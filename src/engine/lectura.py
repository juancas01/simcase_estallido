"""
lectura.py — La lectura de la corrida (`B14`, docs/LA_MEDICION.md).

Lo que se lee de una corrida cuando el ejercicio terminó: **cómo destrabaron
el país** y **a quién atendieron mientras lo hacían**. No es un puntaje, no es
un ranking y no introduce una respuesta correcta por la puerta de atrás: es
una FIRMA —una frase que se lee en voz alta— y los hechos que la sostienen.

LA CONDICIÓN QUE ESTE MÓDULO RESPETA, Y QUE NO ES DE ESTILO
----------------------------------------------------------
**Ninguna de estas cifras se ve durante la sesión.** Un marcador visible deja
de medir la conducta y pasa a producirla, y lo que se llevaría la sala al
final no sería un retrato suyo sino la puntuación de un videojuego. Por eso:

  1 · No hay campo nuevo en `Estado`. Todo se calcula al cierre, desde el
      `registro` con su imputación (`motor.imputaciones`), el `historial` y
      los eventos. Lo que no existe como variable del mundo no puede colarse
      en `vista_publica()` ni en ninguna vista por un descuido.
  2 · Este módulo no lo importa ni `views.py` ni ninguna superficie en vivo;
      hay una prueba que lo comprueba.
  3 · El servidor lo sirve con `GET /api/lectura`, que devuelve **409 mientras
      la sala no haya cerrado**. Una regla que el software garantiza vale más
      que una que el software recomienda.

Y NO SE LLAMA «MÉTRICAS». El tablero ya tiene una tarjeta con ese rótulo —las
cuatro reservas y la presión en la calle—, que es pública y está pensada para
mirarse. Esta cosa es otra: se llama la lectura, y vive aquí.

QUÉ NO MIDE, DICHO ANTES DE QUE ALGUIEN LO SUPONGA (§9)
------------------------------------------------------
No mide si acertaron. No atribuye consecuencias a decisiones: varias caen en
la misma ventana y el mundo además se mueve solo. No mide quién habló ni quién
compartió su vista. No mide intención: priorizar la ciudadanía por convicción
o por el reloj del oxígeno es indistinguible aquí, y no debe fingirse que sí.
Con cinco jornadas y cuatro regiones, los agregados pequeños son ruido: los
repartos se presentan en bandas y con la cautela escrita en la propia
pantalla.
"""

from __future__ import annotations

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# El vocabulario de la lectura, en un solo sitio
# ---------------------------------------------------------------------------

# Las seis vías, en sus dos familias. Las tres primeras conservan la palabra
# del motor (`fuerza`/`concertacion`/`desgaste` en `modo_apertura`), que la
# sala ya lee en el mapa cada jornada.
VIAS_QUE_ABREN = ("despejar", "concertar", "desgastar")
VIAS_QUE_NO_ABREN = ("sortear", "constituir", "encuadrar")
VIAS = VIAS_QUE_ABREN + VIAS_QUE_NO_ABREN

PUBLICOS = ("empresa", "gremios", "ciudadania", "internacional")

# La forma verbal de cada vía, para la firma que se lee en voz alta.
_VERBO = {
    "despejar": "Despejaron",
    "concertar": "Concertaron",
    "desgastar": "Desgastaron",
    "sortear": "Sortearon",
    "constituir": "Constituyeron",
    "encuadrar": "Encuadraron",
}

# LAS BANDAS SON PROVISIONALES Y ESTÁN MARCADAS COMO TAL EN LA SALIDA.
# No hay ninguna corrida real contra la que calibrarlas (docs/LA_MEDICION.md
# §10); lo que sí hay es el peor caso del escenario, y contra él se normaliza.
# Cuando existan corridas reales, estos cortes son lo único que hay que tocar.
BASE_DE_BANDAS = "provisional · normalizada al peor caso del escenario, sin calibrar"

# Atención: qué proporción de las decisiones con público fue a cada uno.
_ATENCION_ALTA = 0.35
_ATENCION_MEDIA = 0.15

# Saldo de empresa: pérdida como fracción de la pérdida máxima posible
# (todos los corredores cerrados las cinco jornadas).
_PERDIDA_BIEN = 0.33
_PERDIDA_MAL = 0.66


# ---------------------------------------------------------------------------
# La lectura
# ---------------------------------------------------------------------------

def calcular(motor) -> dict:
    """
    La lectura completa de una corrida, al cierre.

    Recibe el MOTOR —no el estado— porque lee el registro con su imputación,
    el historial con sus ventanas y las líneas declaradas. Es una función
    pura: no muta nada, y dos llamadas devuelven lo mismo.
    """
    e = motor.estado
    imputaciones = motor.imputaciones
    pasos = motor.historial

    como = _el_como(motor, imputaciones, pasos)
    que = _el_que(motor, imputaciones, pasos)
    return {
        "firma": _la_firma(como, que, imputaciones),
        "como": como,
        "que": que,
        "cautelas": [
            "Los repartos pequeños son ruido: con cinco jornadas, un 38 %/31 % "
            "no distingue nada. Las bandas son provisionales y están sin "
            "calibrar.",
            "Atender no es servir: la atención dice dónde gastaron sus "
            "decisiones, y el saldo cómo terminó cada público. El cruce de las "
            "dos es el material del debriefing, no ninguna de las dos solas.",
            "La lectura no distingue intención de urgencia, ni buena fe de "
            "desmovilización: esas conversaciones son de la sala, no del "
            "instrumento.",
        ],
    }


# ---------------------------------------------------------------------------
# EL CÓMO — por qué vía destrabaron
# ---------------------------------------------------------------------------

def _el_como(motor, imputaciones, pasos) -> dict:
    e = motor.estado

    # El reparto de vías. Cada decisión suma UNO a cada vía de su tupla: las
    # acciones de doble vía son las que mejor enseñan y se cuentan en las dos.
    por_via = {v: 0 for v in VIAS}
    for im in imputaciones:
        for v in im["via"]:
            por_via[v] += 1

    # Aperturas y reaperturas POR VÍA, de los eventos. Es lo que separa
    # «abrimos cuatro» de «abrimos cuatro y tres se volvieron a cerrar».
    aperturas = {v: 0 for v in ("fuerza", "concertacion", "desgaste")}
    reaperturas = {v: 0 for v in ("fuerza", "concertacion", "desgaste")}
    apertura_de_nodo: dict[str, tuple[int, str]] = {}   # nodo -> (jornada, vía)
    revertidas_misma_jornada = {v: 0 for v in aperturas}
    for paso in pasos:
        for ev in paso.eventos:
            if ev.get("tipo") == "apertura":
                via = ev.get("via", "")
                aperturas[via] = aperturas.get(via, 0) + 1
                apertura_de_nodo[ev.get("nodo", "")] = (paso.turno, via)
            elif ev.get("tipo") == "desgaste":
                aperturas["desgaste"] += 1
                apertura_de_nodo[ev.get("nodo", "")] = (paso.turno, "desgaste")
            elif ev.get("tipo") == "reapertura":
                via = ev.get("via", "")
                reaperturas[via] = reaperturas.get(via, 0) + 1
                previa = apertura_de_nodo.get(ev.get("nodo", ""))
                if previa and previa[0] == paso.turno:
                    revertidas_misma_jornada[previa[1]] += 1

    usadas = [v for v in VIAS if por_via[v] > 0]
    ordenadas = sorted(usadas, key=lambda v: -por_via[v])
    sin_usar = [v for v in VIAS if por_via[v] == 0]

    return {
        # El reparto de decisiones por vía, con su proporción sobre el total
        # de vías contadas (las dobles cuentan en las dos, §4).
        "vias": {
            v: {"decisiones": por_via[v], "proporcion": _prop(por_via[v], sum(por_via.values()))}
            for v in VIAS
        },
        "bloques": [list(VIAS_QUE_ABREN), list(VIAS_QUE_NO_ABREN)],
        "dominante": ordenadas[0] if ordenadas else None,
        "secundaria": ordenadas[1] if len(ordenadas) > 1 else None,
        "sin_usar": sin_usar,
        "aperturas": aperturas,
        "reaperturas": reaperturas,
        "desgaste": _partir_el_desgaste(motor, imputaciones, pasos),
        "calificadores": {
            "c1_anticiparon": _c1_anticiparon(motor, pasos),
            "c2_aguantaron": {
                "aperturas": aperturas,
                "reaperturas": reaperturas,
                "revertidas_misma_jornada": revertidas_misma_jornada,
            },
            "c3_miraron": _c3_miraron(motor, pasos),
        },
    }


def _partir_el_desgaste(motor, imputaciones, pasos) -> dict:
    """
    La incomodidad de la vía desgastar, partida en dos (§2).

    Mecánicamente, un punto que se abre por desgaste es siempre lo mismo. En
    el debriefing no pueden serlo: por cada punto abierto por desgaste, si en
    su región había alguna de las tres decisiones que disuelven el cierre —
    esquema humanitario, paso humanitario exigido, instrumentos sectoriales—
    lo DESGASTARON ellos; si no la había y el semáforo estaba en rojo, se les
    CAYÓ DE HAMBRE.
    """
    e = motor.estado
    por_region: dict[str, list[dict]] = {}
    # Las tres decisiones que disuelven el cierre, por región y jornada, de
    # las decisiones mismas: el esquema es siempre del epicentro, el
    # requerimiento cae sobre los puntos de su corredor, y los alivios sobre
    # la región que los pidió (o la peor, si la orden no la nombró: para esa
    # queda el recuento acumulado del estado, que nunca baja).
    esquema_en = set()
    instrumentos_en = set()
    requerimiento_en: dict[int, set[str]] = {}
    for im in imputaciones:
        if im["accion"] == "EsquemaHumanitarioMunicipal":
            esquema_en.add(e.region_epicentro)
        elif im["accion"] == "ActivarInstrumentosSectoriales":
            rid = im.get("objeto") or ""
            if rid in e.regiones:
                instrumentos_en.add(rid)
    for paso in pasos:
        for ev in paso.eventos:
            if ev.get("tipo") == "corredor_humanitario_requerido":
                c = e.corredores.get(ev.get("corredor", ""))
                if c:
                    regiones = {e.nodos[n].region_id for n in c.nodos
                                if n in e.nodos}
                    requerimiento_en.setdefault(paso.turno, set()).update(regiones)

    desgastaron, hambre = [], []
    for paso in pasos:
        for ev in paso.eventos:
            if ev.get("tipo") != "desgaste":
                continue
            nodo = e.nodos.get(ev.get("nodo", ""))
            if nodo is None:
                continue
            rid = nodo.region_id
            fila = {
                "nodo": nodo.nombre,
                "region": e.regiones[rid].nombre if rid in e.regiones else rid,
                "jornada": paso.turno,
            }
            atendieron = (
                rid in esquema_en
                or rid in instrumentos_en
                or rid in e.instrumentos_sectoriales
                or any(rid in rs for j, rs in requerimiento_en.items()
                       if j <= paso.turno)
            )
            if atendieron:
                desgastaron.append(fila)
            elif paso.regiones.get(rid, {}).get("semaforo") == "rojo":
                hambre.append(fila)
            else:
                # Ni decisión ni rojo: el cierre se quedó solo sin apoyo.
                # No es hambre y no es atención: se cuenta como desgaste
                # llano y se nombra, para no inflar ninguna de las dos.
                desgastaron.append({**fila, "sin_causa_marcada": True})

    return {
        "lo_desgastaron": desgastaron,
        "se_les_cayo_de_hambre": hambre,
        "nota": (
            "Las tres decisiones que más atienden al barrio son las tres que "
            "le disuelven el bloqueo: atender es también desmovilizar. La "
            "cuarta vía es la misma apertura conseguida por hambre, y en el "
            "debriefing no pueden leerse igual."),
    }


def _c1_anticiparon(motor, pasos) -> dict:
    """
    ¿Anticiparon o reaccionaron? Cada bandera contra la ventana del primer
    incidente (§2, C1).

    El motor ya tiene opinión sobre esto —el rédito de una constitutiva que
    llega tarde se parte por dos— pero la sala nunca ve que llegó tarde: solo
    ve que rindió poco. Esta es la primera vez que se lo dice.
    """
    e = motor.estado
    primer = None
    for paso in pasos:
        if any(x.get("evento") in ("incidente_mortal", "imagen_viral")
               for x in paso.eventos):
            primer = paso.turno
            break

    banderas = []
    for nombre, turno in sorted(e.banderas.activada_en_turno.items(),
                                key=lambda kv: kv[1]):
        jornada = max(1, (turno + 1) // 2)   # `estado.turno` cuenta pasos
        banderas.append({
            "bandera": nombre,
            "jornada": jornada,
            "anticipo": True if primer is None else jornada <= primer,
        })
    anticipadas = sum(1 for b in banderas if b["anticipo"])
    return {
        "primer_incidente": primer,
        "banderas": banderas,
        "anticipadas": f"{anticipadas}/{len(banderas)}" if banderas else "0/0",
    }


def _c3_miraron(motor, pasos) -> dict:
    """
    ¿Miraron antes de mover? De los puntos intervenidos por la fuerza, cuántos
    habían sido verificados antes (§2, C3).

    Es la salida más barata de toda la lectura y la que más se va a sentir en
    la sala: «de los seis puntos que operaron, uno estaba mirado». No hace
    falta ninguna teoría para entender qué significa.
    """
    verificados: dict[str, int] = {}
    detalle = []
    operados = 0
    for paso in pasos:
        for ev in paso.eventos:
            if ev.get("tipo") == "punto_verificado":
                nid = ev.get("nodo", "")
                verificados[nid] = min(verificados.get(nid, 10**9), paso.turno)
        for ev in paso.eventos:
            if ev.get("tipo") != "operacion":
                continue
            operados += 1
            nid = ev.get("nodo", "")
            t_ver = verificados.get(nid)
            detalle.append({
                "nodo": motor.estado.nodos[nid].nombre if nid in motor.estado.nodos else nid,
                "jornada": paso.turno,
                "verificado_en": t_ver if t_ver is not None and t_ver <= paso.turno else None,
            })
    con_mirror = sum(1 for d in detalle if d["verificado_en"] is not None)
    return {
        "puntos_operados": operados,
        "verificados_antes": con_mirror,
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# EL QUÉ — a quién atendieron, y cómo terminó cada público
# ---------------------------------------------------------------------------

def _el_que(motor, imputaciones, pasos) -> dict:
    atencion = _atencion(imputaciones)
    saldo = _saldo(motor, imputaciones, pasos)
    cruce, nadie = _cruce_y_el_nadie(atencion, saldo, motor, pasos)
    return {
        "atencion": atencion,
        "saldo": saldo,
        "cruce": cruce,
        "publico_que_nadie_miro": nadie,
        # §5 B, la celda que distingue una sala imaginativa de una obediente:
        # de las decisiones que atendieron a la empresa, cuántas por una vía
        # distinta de la fuerza. El repertorio correlaciona las dos cosas «no
        # porque la sala piense así, sino porque el repertorio está hecho
        # así», y esta cuenta es la que lo desenreda.
        "empresa_sin_fuerza": _empresa_sin_fuerza(imputaciones),
    }


def _atencion(imputaciones) -> dict:
    """
    Dónde gastaron sus decisiones (columna A). El reparto mide una prioridad
    porque atender a uno es no atender a otro.

    REGLA DE IMPUTACIÓN DOBLE (§10, sin calibrar): una decisión que atiende a
    dos públicos le suma UNO ENTERO a cada uno. Ponderarla por la mitad o por
    el costo cambia todos los repartos y es una decisión del equipo docente;
    la regla vive en esta única línea y se declara en la salida.
    """
    por_publico = {p: 0 for p in PUBLICOS}
    residuo = 0
    for im in imputaciones:
        if im["atiende"]:
            for p in im["atiende"]:
                por_publico[p] += 1
        else:
            residuo += 1
    con_publico = sum(por_publico.values())
    total = len(imputaciones)
    return {
        "por_publico": {
            p: {"decisiones": por_publico[p],
                "proporcion": _prop(por_publico[p], con_publico)}
            for p in PUBLICOS
        },
        "gobierno_de_si_mismo": {
            "decisiones": residuo,
            "proporcion": _prop(residuo, total),
        },
        "decisiones": total,
        "regla": "una entera a cada público de la tupla",
    }


def _saldo(motor, imputaciones, pasos) -> dict:
    """
    Cómo terminó cada público (columna B). NO sale de las decisiones: sale del
    mundo — si se dedujera de lo que la sala ordenó, la medición sería
    circular y no habría nada que aprender.

    Cada público sale en banda y con sus hechos debajo. La cifra sola no abre
    ninguna conversación; la lista de hechos sí.
    """
    e = motor.estado
    m = motor.metricas()

    # EMPRESA · la pérdida acumulada: Σ por jornada de lo que cada corredor
    # dejó de entregar. De los indicadores de cada paso, que ya traen el
    # caudal de los cuatro.
    perdida = 0.0
    peor_caso = 0.0
    for paso in pasos:
        if paso.franja != "dia":
            continue
        for c in e.corredores.values():
            caudal = paso.indicadores.get(f"caudal:{c.corredor_id}", 1.0)
            perdida += c.costo_diario_mm_cop * (1.0 - caudal)
            peor_caso += c.costo_diario_mm_cop
    frac = (perdida / peor_caso) if peor_caso else 0.0
    infra = m["infraestructura"]
    empresa_hechos = [
        f"{perdida:,.0f} MM COP de pérdida por corredores cerrados en cinco jornadas.",
        f"Exposición de infraestructura {infra['exposicion_total']}"
        + (f", con {len(infra['vitales_sin_proteger'])} instalación(es) vital(es) "
           f"sin custodia." if infra["vitales_sin_proteger"] else "."),
        f"{m['acuerdos_rotos']} acuerdo(s) roto(s) y {m['reaperturas']} "
        f"apertura(s) revertida(s): el país no pudo prever.",
    ]
    empresa_banda = _banda_normalizada(frac)

    # GREMIOS · el ultimátum y su respuesta. La primera decisión dirigida a
    # ellos DESPUÉS del ultimátum, contada en jornadas de silencio.
    turno_ultimatum = None
    for paso in pasos:
        if any(ev.get("tipo") == "ultimatum_gremios" for ev in paso.eventos):
            turno_ultimatum = paso.turno
            break
    primera_a_gremios = None
    if turno_ultimatum is not None:
        for im in imputaciones:
            if "gremios" in im["atiende"] and im["ventana"] >= turno_ultimatum:
                primera_a_gremios = im["ventana"]
                break
    silencio = (None if turno_ultimatum is None or primera_a_gremios is None
                else primera_a_gremios - turno_ultimatum)
    alivios = sorted(e.instrumentos_sectoriales)
    gremios_hechos = [
        f"Posición al cierre: {m['posicion_gremios']}.",
        (f"El ultimátum cayó en la jornada {turno_ultimatum} y la primera "
         f"decisión dirigida a ellos llegó "
         + (f"en la {primera_a_gremios}: {silencio} jornada(s) de silencio."
            if primera_a_gremios is not None else "nunca.")
        ) if turno_ultimatum is not None else "No hubo ultimátum en la corrida.",
        f"{m['escoltas_logradas']} escolta(s) lograda(s) y "
        f"{m['escoltas_atacadas']} atacada(s).",
        f"Alivios sectoriales en {len(alivios)} región(es)"
        + (f" ({', '.join(e.regiones[r].nombre for r in alivios if r in e.regiones)})."
           if alivios else "."),
        f"{e.riesgo_sanitario_asumido} autorización(es) sanitaria(s) excepcional(es): "
        f"el riesgo que se asumió y no se vio.",
    ]
    if m["posicion_gremios"] == "sumados":
        banda_gremios = "mal"
    elif silencio is not None and silencio >= 2:
        banda_gremios = "mal"
    elif m["posicion_gremios"] == "evaluando":
        banda_gremios = "regular"
    else:
        banda_gremios = "bien"

    # CIUDADANÍA · muertes, hambre y represión.
    rojas = {}
    incidentes = sum(1 for paso in pasos for ev in paso.eventos
                     if ev.get("evento") == "incidente_mortal")
    virales = sum(1 for paso in pasos for ev in paso.eventos
                  if ev.get("evento") == "imagen_viral")
    for paso in pasos:
        if paso.franja != "dia":
            continue
        for rid, r in paso.regiones.items():
            if r.get("semaforo") == "rojo":
                rojas[rid] = rojas.get(rid, 0) + 1
    regiones_rojas = [(e.regiones[rid].nombre, n)
                      for rid, n in rojas.items() if rid in e.regiones]
    apoyo_medio = (sum(n.apoyo_local for n in e.nodos.values()) / len(e.nodos)
                   if e.nodos else 0.0)
    ciudadania_hechos = [
        f"{m['muertes_evitables']} muerte(s) evitable(s).",
        (f"{sum(n for _, n in regiones_rojas)} jornada(s)-región en rojo: "
         + ", ".join(f"{nom} ({n})" for nom, n in regiones_rojas) + "."
         if regiones_rojas else "Ninguna región pasó el semáforo a rojo."),
        f"{incidentes} incidente(s) con víctima y {virales} con imagen viral.",
        f"Apoyo local medio al cierre: {apoyo_medio:.0%}.",
    ]
    if m["muertes_evitables"] > 0 or sum(n for _, n in regiones_rojas) >= 3:
        banda_ciudadania = "mal"
    elif regiones_rojas or incidentes:
        banda_ciudadania = "regular"
    else:
        banda_ciudadania = "bien"

    # INTERNACIONAL · proporcionalidad y verificación.
    requeridos = sum(1 for paso in pasos for ev in paso.eventos
                     if ev.get("tipo") == "corredor_humanitario_requerido")
    negados = sum(1 for paso in pasos for ev in paso.eventos
                  if ev.get("tipo") == "corredor_humanitario_negado")
    militares_multitud = sum(1 for paso in pasos for ev in paso.eventos
                             if ev.get("evento") == "militares_en_multitudes")
    ops_mitigadores = []
    for paso in pasos:
        if any(ev.get("tipo") == "operacion" for ev in paso.eventos):
            ops_mitigadores.append(len(paso.mitigadores))
    respaldo = e.reservas.respaldo_internacional
    internacional_hechos = [
        f"Respaldo internacional al cierre: {respaldo:.0f}.",
        f"{requeridos} corredor(es) humanitario(s) requerido(s), {negados} "
        f"negado(s) con fecha.",
        f"{m['denuncias_verificadas']} denuncia(s) verificada(s) y "
        f"{m['denuncias_estalladas']} estallada(s) sin que nadie mirara.",
        ("Con una media de "
         f"{sum(ops_mitigadores) / len(ops_mitigadores):.1f} mitigador(es) "
         f"encendido(s) en las {len(ops_mitigadores)} operación(es)."
         if ops_mitigadores else "No hubo operaciones de fuerza."),
        f"{militares_multitud} ventana(s) con militares en multitudes.",
    ]
    if respaldo < 40 or negados >= 2 or m["denuncias_estalladas"] >= 2:
        banda_internacional = "mal"
    elif respaldo < 60 or negados or militares_multitud:
        banda_internacional = "regular"
    else:
        banda_internacional = "bien"

    return {
        "base": BASE_DE_BANDAS,
        "empresa": {"banda": empresa_banda, "hechos": empresa_hechos,
                    "perdida_mm_cop": round(perdida),
                    "perdida_sobre_peor_caso": round(frac, 3),
                    "exposicion_infraestructura": infra["exposicion_total"],
                    "vitales_sin_proteger": infra["vitales_sin_proteger"]},
        "gremios": {"banda": banda_gremios, "hechos": gremios_hechos,
                    "posicion": m["posicion_gremios"],
                    "jornadas_de_silencio": silencio},
        "ciudadania": {"banda": banda_ciudadania, "hechos": ciudadania_hechos,
                       "muertes_evitables": m["muertes_evitables"],
                       "jornadas_region_en_rojo": sum(n for _, n in regiones_rojas)},
        "internacional": {"banda": banda_internacional,
                          "hechos": internacional_hechos,
                          "respaldo": round(respaldo, 1),
                          "corredores_requeridos": requeridos,
                          "corredores_negados": negados},
    }


def _cruce_y_el_nadie(atencion, saldo, motor, pasos) -> tuple[dict, dict]:
    """
    El cruce que vale el debriefing entero (§6): atención contra saldo, cuatro
    celdas y las cuatro son una conversación distinta. Y la salida de una sola
    línea: EL PÚBLICO QUE NADIE MIRÓ, con su consecuencia.
    """
    CELDA = {
        ("alta", "bien"): "Lo atendieron y funcionó. Lo único que se puede llamar acierto.",
        ("alta", "regular"): "Lo atendieron y rindió a medias.",
        ("alta", "mal"): "Lo atendieron y no le sirvió. Es un problema de cómo, no de a quién.",
        ("media", "bien"): "Le fue bien con atención parcial. Conviene no cobrárselo.",
        ("media", "regular"): "Atención parcial, resultado a medias.",
        ("media", "mal"): "Lo miraron a medias y no alcanzó.",
        ("baja", "bien"): "Le fue bien sin ustedes. Suerte, o el trabajo de otro.",
        ("baja", "regular"): "Apenas lo miraron y terminó a medias.",
        ("baja", "mal"): "Nadie lo miró. El resultado más duro y el más frecuente.",
    }
    cruce = {}
    for p in PUBLICOS:
        prop = atencion["por_publico"][p]["proporcion"]
        nivel = ("alta" if prop >= _ATENCION_ALTA
                 else "media" if prop >= _ATENCION_MEDIA else "baja")
        banda = saldo[p]["banda"]
        cruce[p] = {"atencion": nivel, "saldo": banda,
                    "celda": CELDA[(nivel, banda)]}

    # El público que nadie miró: el de atención CERO — y si hay varios, el que
    # peor terminó, que es la conversación que no se puede esquivar.
    ceros = [p for p in PUBLICOS if atencion["por_publico"][p]["decisiones"] == 0]
    if atencion["decisiones"] == 0:
        nadie = {"publico": None, "linea": "No hubo decisiones: no hay un "
                 "reparto de atención que leer, y eso es la lectura.",
                 "consecuencia": ""}
    elif not ceros:
        nadie = {"publico": None, "linea": "Todos los públicos recibieron al "
                 "menos una decisión. La conversación no es a quién dejaron "
                 "fuera, sino qué obtuvo cada uno.", "consecuencia": ""}
    else:
        orden_mal = {"mal": 0, "regular": 1, "bien": 2}
        peor = sorted(ceros, key=lambda p: orden_mal[saldo[p]["banda"]])[0]
        consecuencia = _consecuencia_del_nadie(peor, saldo, motor, pasos)
        nadie = {
            "publico": peor,
            "linea": (f"Ninguna de sus {atencion['decisiones']} decisiones "
                      f"atendió a {peor}."),
            "consecuencia": consecuencia,
        }
    return cruce, nadie


def _consecuencia_del_nadie(publico, saldo, motor, pasos) -> str:
    """La consecuencia concreta del público ignorado, con jornada."""
    e = motor.estado
    if publico == "gremios":
        for paso in pasos:
            if any(ev.get("tipo") == "gremios_se_suman" for ev in paso.eventos):
                return f"Se sumaron al paro en la jornada {paso.turno}."
        return "Terminaron evaluando sumarse."
    if publico == "ciudadania":
        m = saldo["ciudadania"]
        if m["muertes_evitables"]:
            return f"{m['muertes_evitables']} muertes evitables."
        return (f"{m['jornadas_region_en_rojo']} jornada(s)-región en rojo."
                if m["jornadas_region_en_rojo"] else "La calle siguió cerrada.")
    if publico == "empresa":
        return (f"{saldo['empresa']['perdida_mm_cop']:,.0f} MM COP de pérdida.")
    return (f"Respaldo internacional {saldo['internacional']['respaldo']:.0f} "
            f"al cierre.")


def _empresa_sin_fuerza(imputaciones) -> dict:
    """
    §5 B: de las decisiones que atendieron a la empresa, cuántas por una vía
    distinta de la fuerza. En este repertorio casi todo lo que atiende a la
    empresa gasta capacidad de la fuerza pública —«priorizaron a la empresa»
    y «abrieron por la fuerza» salen correlacionados no porque la sala piense
    así, sino porque el repertorio está hecho así— y esta cuenta es la que
    distingue una sala imaginativa de una obediente.
    """
    a_empresa = [im for im in imputaciones if "empresa" in im["atiende"]]
    sin_fuerza = [im for im in a_empresa
                  if not ({"despejar", "desgastar"} & set(im["via"]))]
    return {
        "atendieron": len(a_empresa),
        "sin_fuerza": len(sin_fuerza),
        "ejemplos": [im["nombre"] for im in sin_fuerza[:5]],
    }


# ---------------------------------------------------------------------------
# La firma — una frase que se lee en voz alta y se deja en pantalla
# ---------------------------------------------------------------------------

def _la_firma(como, que, imputaciones) -> str:
    if not imputaciones:
        base = ("La sala no tomó ninguna decisión en cinco jornadas. "
                "El país que entrega es el que el desorden dejó.")
        hambre = como["desgaste"]["se_les_cayo_de_hambre"]
        if hambre:
            base += f" {len(hambre)} punto(s) se les cayó de hambre."
        return base

    ordenadas = sorted((v for v in VIAS if como["vias"][v]["decisiones"] > 0),
                       key=lambda v: -como["vias"][v]["decisiones"])
    partes = []
    if len(ordenadas) == 1:
        partes.append(f"Solo {_VERBO[ordenadas[0]].lower()}.")
    elif len(ordenadas) == 2:
        a, b = (_VERBO[v] for v in ordenadas)
        partes.append(f"{a} y {b.lower()}.")
    else:
        a, b = (_VERBO[v] for v in ordenadas[:2])
        partes.append(f"{a} y {b.lower()}, sobre todo.")
    if como["sin_usar"]:
        muertas = [_VERBO[v].lower() for v in como["sin_usar"]]
        if len(muertas) == 1:
            partes.append(f"No {muertas[0]} ni una vez.")
        else:
            partes.append(f"No {', '.join(muertas[:-1])} ni {muertas[-1]}.")

    c1 = como["calificadores"]["c1_anticiparon"]
    if c1["primer_incidente"] is not None and c1["banderas"]:
        anticipadas, totales = c1["anticipadas"].split("/")
        partes.append("Se constituyeron antes del primer incidente"
                      if anticipadas == totales else
                      "Constituyeron después del primer incidente")

    c2 = como["calificadores"]["c2_aguantaron"]["revertidas_misma_jornada"]
    if c2.get("fuerza"):
        abiertas = como["aperturas"]["fuerza"]
        partes.append(f"{c2['fuerza']} de {abiertas} aperturas por fuerza se "
                      f"revirtieron esa misma jornada")

    hambre = como["desgaste"]["se_les_cayo_de_hambre"]
    if hambre:
        partes.append(f"{len(hambre)} punto(s) se les cayó de hambre")

    c3 = como["calificadores"]["c3_miraron"]
    if c3["puntos_operados"]:
        partes.append(f"Operaron {c3['puntos_operados']} puntos habiendo "
                      f"mirado {c3['verificados_antes']}")

    nadie = que["publico_que_nadie_miro"]
    if nadie["publico"]:
        partes.append(f"Ninguna decisión atendió a {nadie['publico']}")

    partes[0] = partes[0][0].upper() + partes[0][1:]
    frase = ". ".join(p.rstrip(".") for p in partes).strip()
    return frase + ("." if not frase.endswith(".") else "")


# ---------------------------------------------------------------------------
# Ayudantes
# ---------------------------------------------------------------------------

def _prop(n: int, total: int) -> float:
    return round(n / total, 3) if total else 0.0


def _banda_normalizada(frac: float) -> str:
    if frac < _PERDIDA_BIEN:
        return "bien"
    if frac < _PERDIDA_MAL:
        return "regular"
    return "mal"


def cierre_desde_archivo(ruta: Path) -> dict:
    """
    La línea de cierre de un archivo de corrida (`B1`), para contar la corrida
    con el proceso ya muerto: el debriefing no debería depender de que el
    servidor siga vivo.

    Devuelve la línea `cierre` completa —métricas, proyección y lectura— o
    `{}` si el archivo no la tiene (una corrida caída antes del cierre).
    """
    ruta = Path(ruta)
    if not ruta.exists():
        return {}
    with ruta.open(encoding="utf-8") as f:
        for linea in f:
            try:
                reg = json.loads(linea)
            except ValueError:
                continue
            if reg.get("t") == "cierre":
                return reg
    return {}
