"""
correr_ejercicio.py — Corre un ejercicio completo sin interfaz y sin LLM.

El motor de principio a fin en milisegundos, para calibrar sin gastar tokens ni
montar la sala.

    uv run python scripts/correr_ejercicio.py
    uv run python scripts/correr_ejercicio.py --estrategia constituida
    uv run python scripts/correr_ejercicio.py --comparar
    uv run python scripts/correr_ejercicio.py --vistas
    uv run python scripts/correr_ejercicio.py --lectura

Las estrategias existen para el criterio de calibración: ajustar hasta que
NINGUNA pura gane. Si `solo_fuerza` domina, el modelo está mal calibrado; si
`constituida` gana siempre y sin costo, también.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

# Las consolas Windows son cp1252 e imprimir acentos revienta. Se fuerza UTF-8 al
# arranque, como manda el anexo de la guía de arquitectura.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine import parameters as P                      # noqa: E402
from src.engine import views                                # noqa: E402
from src.engine import lectura as modulo_lectura            # noqa: E402
from src.engine.loader import cargar_estado                 # noqa: E402
from src.engine.simulation import MotorCrisis               # noqa: E402
from src.engine.actions import (                            # noqa: E402
    FijarRegistroEscrito, FijarLineasRojas, FirmarAsistenciaMilitar,
    ExigirProtocoloVoceria, ConvocarMesaNacional, AbrirMesaLocal,
    OfrecerContraprestacion,
    CondicionarEmpleoFuerza, InstalarMesaConVoceros, EsquemaHumanitarioMunicipal,
    FijarReglasEmpleoSector, OperarNodo, RedesplegarMilitares,
    ClasificarParteOperacional, DisponerESMAD, Escoltar, SolicitarRelevo,
    FijarReglasEmpleoSector, AdoptarProtocoloVerificacion, DesplegarEquiposTerreno,
    RequerirCorredoresHumanitarios,
    AdoptarCriterioPriorizacion, OrganizarCaravana, NegociarConGremios,
    FijarPrioridadCombustible, DeclararInfraestructuraCritica,
    EntregarCalendarioAgotamiento,
    FijarClasePrioridadAlimentaria, InstalarMesaTecnicaAgropecuaria,
    ActivarInstrumentosSectoriales, AcordarAcopioYVentanas,
)

SEP = "=" * 78


def _cerrados(motor):
    return [n for n in motor.estado.nodos.values() if not n.abierto]


def _corredor_humanitario_mas_corto(estado):
    hum = [c for c in estado.corredores.values() if "humanitario" in c.clases_prioridad]
    return min(hum, key=lambda c: len(c.nodos))


# ---------------------------------------------------------------------------
# Estrategias
# ---------------------------------------------------------------------------

def plan_solo_fuerza(motor, turno: int) -> None:
    """La sala se salta la constitución y opera desde el turno 1."""
    if turno == 1:
        motor.encolar(DisponerESMAD(n_escuadrones=8))
    duros = sorted(_cerrados(motor), key=lambda n: -n.dureza)
    for nodo in duros[:2]:
        motor.encolar(OperarNodo(nodo_id=nodo.nodo_id, tipo_unidad="esmad"))


def plan_solo_mesa(motor, turno: int) -> None:
    """
    La sala solo negocia. Nunca usa la fuerza.

    Desde la v2 la concertación es competencia de INTERIOR y comprueba
    jurisdicción: en el epicentro necesita al Alcalde.
    """
    e = motor.estado
    if turno == 1:
        motor.encolar(ExigirProtocoloVoceria())
        motor.encolar(ConvocarMesaNacional())
        return
    if turno == 2:
        motor.encolar(OfrecerContraprestacion())

    concertables = sorted(_cerrados(motor), key=lambda n: -n.control_voceria)[:3]
    for nodo in concertables:
        en_epicentro = nodo.region_id == e.region_epicentro
        motor.encolar(AbrirMesaLocal(nodo_id=nodo.nodo_id, con_alcaldia=en_epicentro))


def plan_constituida(motor, turno: int) -> None:
    """La sala se constituye primero y después opera con los mitigadores puestos."""
    e = motor.estado
    if turno == 1:
        motor.encolar(FijarRegistroEscrito())
        motor.encolar(FijarReglasEmpleoSector())
        motor.encolar(AdoptarCriterioPriorizacion())
        motor.encolar(ExigirProtocoloVoceria())
        motor.encolar(DesplegarEquiposTerreno(nodos=["N003", "N013", "N022"]))
        return
    if turno == 2:
        motor.encolar(ClasificarParteOperacional())
        motor.encolar(FijarPrioridadCombustible())
        motor.encolar(SolicitarRelevo(n_unidades=8))
        motor.encolar(EsquemaHumanitarioMunicipal())
        return

    concertables = sorted(
        [n for n in _cerrados(motor) if n.control_voceria > 0.6],
        key=lambda n: -n.control_voceria,
    )
    for nodo in concertables[:2]:
        en_epicentro = nodo.region_id == e.region_epicentro
        motor.encolar(AbrirMesaLocal(nodo_id=nodo.nodo_id, con_alcaldia=en_epicentro))

    duros = sorted([n for n in _cerrados(motor) if n.control_voceria <= 0.4],
                   key=lambda n: -n.dureza)
    if duros:
        motor.encolar(OperarNodo(
            nodo_id=duros[0].nodo_id, tipo_unidad="esmad",
            concertado_con_alcaldia=True,
            responsable_nominado="Ministro de Defensa",
        ))


def plan_humanitaria(motor, turno: int) -> None:
    """
    Prioriza el anillo hospitalario y los corredores humanitarios.

    Existe para comprobar que las muertes evitables SON evitables. Si esta
    estrategia da el mismo número de muertes que las demás, el oxígeno está
    desacoplado de las decisiones y el modelo está roto.
    """
    e = motor.estado
    if turno == 1:
        motor.encolar(FijarReglasEmpleoSector())
        motor.encolar(RequerirCorredoresHumanitarios())
        motor.encolar(FijarPrioridadCombustible())

    # CONCENTRAR, no dispersar. Un corredor es tan bueno como su peor punto, así
    # que abrir un punto de cada corredor no abre ninguno.
    objetivo = _corredor_humanitario_mas_corto(e)
    for nid in objetivo.nodos:
        nodo = e.nodos.get(nid)
        if nodo is None or nodo.abierto:
            continue
        en_epicentro = nodo.region_id == e.region_epicentro
        motor.encolar(AbrirMesaLocal(nodo_id=nid, con_alcaldia=en_epicentro))

    # Y escoltar lo que se logre abrir: la segunda entrada del reloj.
    if objetivo.caudal_efectivo(e.nodos) > 0.05:
        motor.encolar(Escoltar(corredor_id=objetivo.corredor_id,
                               clase_carga="humanitario"))


def plan_logistica(motor, turno: int) -> None:
    """
    La sala juega el frente logístico entero: escolta, combustible y caravanas.

    Existe desde la v2 para comprobar que el reloj tiene TRES entradas y no una.
    """
    e = motor.estado
    if turno == 1:
        motor.encolar(AdoptarCriterioPriorizacion())
        motor.encolar(FijarPrioridadCombustible())
        motor.encolar(DisponerESMAD(n_escuadrones=6))
        return

    hum = _corredor_humanitario_mas_corto(e)
    for nid in hum.nodos:
        nodo = e.nodos.get(nid)
        if nodo is None or nodo.abierto:
            continue
        motor.encolar(AbrirMesaLocal(
            nodo_id=nid, con_alcaldia=nodo.region_id == e.region_epicentro))

    for c in e.corredores.values():
        if c.caudal_efectivo(e.nodos) > 0.05:
            clase = "humanitario" if "humanitario" in c.clases_prioridad else \
                sorted(c.clases_prioridad)[0]
            motor.encolar(Escoltar(corredor_id=c.corredor_id, clase_carga=clase))
            break

    if turno >= 3:
        motor.encolar(NegociarConGremios())


def plan_agroalimentaria(motor, turno: int) -> None:
    """
    La sala juega el frente rural: clase alimentaria, mesas técnicas y acopio.

    Existe por la misma razón que `humanitaria` existe para el oxígeno: **para
    comprobar que el hambre es evitable y que se evita con estas decisiones y no
    con cualquiera.** Si su columna de muertes y su índice de precios salieran
    iguales que los de `pasiva`, el frente agroalimentario estaría desacoplado y
    el noveno rol sería decoración.

    Y para lo contrario, que importa igual: si esta estrategia domina, el rol
    resuelve solo lo que el caso quiere que se negocie, y hay que abaratarla.
    """
    e = motor.estado
    if turno == 1:
        motor.encolar(FijarClasePrioridadAlimentaria())
        motor.encolar(DisponerESMAD(n_escuadrones=6))
        return

    # Las mesas técnicas se instalan CADA JORNADA o se congelan. Es la regla que
    # más se olvida en la sala, y una estrategia de referencia que la olvidara
    # mediría otra cosa.
    for nodo in sorted(e.nodos.values(), key=lambda n: -n.control_voceria):
        if nodo.abierto or nodo.region_id == e.region_epicentro:
            continue
        if nodo.control_voceria < 0.25:
            continue
        motor.encolar(InstalarMesaTecnicaAgropecuaria(nodo_id=nodo.nodo_id))

    peor = min(e.regiones.values(), key=lambda r: r.dias_autonomia_alimentos)
    motor.encolar(ActivarInstrumentosSectoriales(region_id=peor.region_id))

    # Escolta primero, acopio después: el despacho concentrado no pide escolta,
    # hace rendir la que ya está puesta.
    for c in e.corredores.values():
        if "alimentario" not in c.clases_prioridad:
            continue
        if c.punto_que_bloquea(e.nodos):
            continue
        motor.encolar(Escoltar(corredor_id=c.corredor_id, clase_carga="alimentario"))
        motor.encolar(AcordarAcopioYVentanas(corredor_id=c.corredor_id))
        break


def plan_pasiva(motor, turno: int) -> None:
    """La sala no decide. Para medir el costo de no decidir."""
    return


ESTRATEGIAS = {
    "solo_fuerza": plan_solo_fuerza,
    "solo_mesa": plan_solo_mesa,
    "constituida": plan_constituida,
    "humanitaria": plan_humanitaria,
    "logistica": plan_logistica,
    "agroalimentaria": plan_agroalimentaria,
    "pasiva": plan_pasiva,
}


# ---------------------------------------------------------------------------

def correr(estrategia: str, semilla: int, verboso: bool = True) -> dict:
    estado = cargar_estado()
    motor = MotorCrisis(estado, semilla=semilla)
    plan = ESTRATEGIAS[estrategia]

    # La traza: qué se ordenó cada turno y qué produjo. Sin esto, la tabla de
    # `--comparar` da un resultado sin explicación — y un número sin su cadena
    # causal no sirve para calibrar: no dice QUÉ tocar.
    traza: list[dict] = []
    # Y esto: si un corredor humanitario que sirve a una región llegó a estar
    # abierto alguna vez. Es lo que separa «la sala no pudo» de «la sala no lo
    # atendió», que en el debriefing son dos conversaciones distintas.
    sirvio_humanitario = {rid: False for rid in estado.regiones}

    if verboso:
        region, dias = estado.dias_autonomia_minimos()
        print(SEP)
        print(f"  ESTRATEGIA: {estrategia}   ·   semilla {semilla}")
        print(SEP)
        print(f"  t=0 · {len(estado.nodos)} puntos · presión en la calle "
              f"{estado.intensidad_nacional:.0f} · autonomía mínima {dias:.1f} d ({region})")
        print(f"  ESMAD sin comprometer: {len(estado.esmad_en_reserva())}/"
              f"{len(estado.unidades_por_tipo('esmad'))} · "
              f"fatiga media {estado.fatiga_media('esmad'):.2f}")
        print(f"  Mitigadores activos: 0/6 — nada se ha constituido")
        print(f"  Denuncias sin verificar: {len(estado.denuncias)}")

    for turno in range(1, P.TURNOS_DECISION + 1):
        plan(motor, turno)
        r = motor.paso(franja="dia")

        for rid in sirvio_humanitario:
            if any(c.caudal_efectivo(estado.nodos) > 0.05
                   for c in estado.corredores_que_sirven(rid, "humanitario")):
                sirvio_humanitario[rid] = True

        traza.append({
            "turno": turno,
            "ordenes": [(n, res.ok, res.mensaje, res.datos) for n, res in r.resultados],
            "eventos": list(r.eventos),
            "puntos_abiertos": len(estado.nodos_abiertos()),
            "presion": round(estado.intensidad_nacional, 1),
            "muertes": estado.muertes_evitables_total(),
            "reservas": dict(r.reservas),
        })

        if verboso:
            print()
            print(f"── TURNO {turno} (día) " + "─" * 44)
            for nombre, res in r.resultados:
                marca = "ok" if res.ok else "..."
                print(f"  {marca} {nombre}: {res.mensaje}")
                if res.requisitos_faltantes:
                    print(f"       faltan: {', '.join(res.requisitos_faltantes)}")
                if "p_incidente" in res.datos:
                    print(f"       riesgo mostrado P={res.datos['p_incidente']:.0%} · "
                          f"tirada {res.datos['tirada']:.3f} · "
                          f"atribuible={res.datos['atribuible']}")
            print(f"   {r.resumen}")

        if turno < P.TURNOS_DECISION:
            rn = motor.paso(franja="noche")
            traza[-1]["noche"] = list(rn.eventos)
            traza[-1]["muertes_tras_noche"] = estado.muertes_evitables_total()
            if verboso:
                eventos = [e for e in rn.eventos
                           if e.get("tipo") in ("reapertura", "muertes_evitables")]
                if eventos:
                    reap = sum(1 for e in eventos if e["tipo"] == "reapertura")
                    muertes = sum(e.get("n", 0) for e in eventos
                                  if e["tipo"] == "muertes_evitables")
                    partes = []
                    if reap:
                        partes.append(f"{reap} punto(s) volvieron a cerrarse")
                    if muertes:
                        partes.append(f"{muertes} muertes evitables")
                    print(f"   · noche: {'; '.join(partes)}")
                else:
                    print("   · noche: sin novedad")

    m = motor.metricas()
    # El desglose por región se congela AQUÍ, en el mismo instante que las
    # métricas: al cerrar el turno 5 y antes de la proyección. Leerlo después
    # daba un total distinto del de la tabla, que es la peor clase de error en
    # una herramienta de calibración — dos números verdaderos que no cuadran.
    regiones_al_cierre = {
        r.region_id: {"nombre": r.nombre, "muertes": r.muertes_evitables}
        for r in estado.regiones.values()
    }
    banderas_al_cierre = dict(estado.banderas.activada_en_turno)
    # LA PROYECCIÓN VA SOBRE UNA COPIA. `proyectar_sin_mando()` corre turnos de
    # verdad sobre el motor que se le pasa: hacerlo aquí sobre el motor real
    # dejaba, después de la tabla, un motor con tres turnos de más — y la
    # lectura de `--lectura` salía describiendo un país que la sala nunca
    # entregó. Es la misma copia que hace `_proyeccion_final()` en la API.
    proy = copy.deepcopy(motor).proyectar_sin_mando()

    if verboso:
        print()
        print(SEP)
        print("  MÉTRICAS DEL DEBRIEFING")
        print(SEP)
        print(f"  Aperturas netas ............ {m['aperturas_netas']}")
        print(f"    por fuerza ............... {m['aperturas']['fuerza']}")
        print(f"    por concertación ......... {m['aperturas']['concertacion']}")
        print(f"    por desgaste ............. {m['aperturas']['desgaste']}")
        print(f"  Reaperturas ................ {m['reaperturas']}")
        print(f"  Acuerdos cumplidos/rotos ... {m['acuerdos_cumplidos']}/{m['acuerdos_rotos']}")
        print(f"  Escoltas logradas/atacadas . {m['escoltas_logradas']}/{m['escoltas_atacadas']}")
        print(f"  Denuncias verif./estalladas  {m['denuncias_verificadas']}/{m['denuncias_estalladas']}")
        print(f"  Muertes evitables .......... {m['muertes_evitables']}")
        print(f"  Mitigadores al cierre ...... {m['mitigadores_al_cierre']}")
        print(f"  Decisiones con responsable . {m['decisiones_atribuibles']}/{m['decisiones_totales']}")
        print(f"  Reservas ................... {m['reservas']}")
        print()
        print("  PROYECCIÓN T+72 h — el país que la sala entrega")
        for k, v in proy["despues"].items():
            print(f"    {k:.<26} {v}")

    return {"motor": motor, "metricas": m, "proyeccion": proy, "traza": traza,
            "sirvio_humanitario": sirvio_humanitario,
            "regiones": regiones_al_cierre,
            "banderas": banderas_al_cierre}


# ---------------------------------------------------------------------------
# La traza: de qué decisiones salió el resultado
#
# Un número sin su cadena causal no sirve para calibrar, porque no dice QUÉ
# tocar. Estas dos funciones responden «¿por qué salió así?» leyendo la corrida,
# no interpretándola.
# ---------------------------------------------------------------------------

ABREVIA = {
    "FijarRegistroEscrito": "registro escrito",
    "FijarLineasRojas": "líneas rojas",
    "FirmarAsistenciaMilitar": "FIRMA asistencia militar",
    "ConvocarAlcaldes": "convoca alcaldes",
    "DesplazarseAlEpicentro": "va al epicentro",
    "ExigirProtocoloVoceria": "protocolo de vocería",
    "ConvocarMesaNacional": "MESA NACIONAL",
    "AbrirMesaLocal": "concierta",
    "OfrecerContraprestacion": "contraprestación",
    "CondicionarEmpleoFuerza": "condiciona la fuerza",
    "InstalarMesaConVoceros": "mesa con voceros",
    "EsquemaHumanitarioMunicipal": "esquema humanitario",
    "PublicarParteMunicipal": "parte municipal",
    "FijarReglasEmpleoSector": "reglas del sector",
    "OperarNodo": "OPERA",
    "RedesplegarMilitares": "redespliega militares",
    "PresentarEvidenciaInteligencia": "evidencia de inteligencia",
    "ClasificarParteOperacional": "parte clasificado",
    "DisponerESMAD": "concentra ESMAD",
    "Escoltar": "ESCOLTA",
    "SolicitarRelevo": "relevo",
    "AdoptarProtocoloVerificacion": "protocolo de verificación",
    "DesplegarEquiposTerreno": "equipos al terreno",
    "RequerirCorredoresHumanitarios": "requiere corredor humanitario",
    "AdoptarCriterioPriorizacion": "criterio de priorización",
    "OrganizarCaravana": "caravana",
    "NegociarConGremios": "negocia gremios",
    "PublicarMapaCierres": "publica el mapa",
    "FijarPrioridadCombustible": "prioridad de combustible",
    "DeclararInfraestructuraCritica": "infraestructura crítica",
    "AcordarPasosSeguros": "pasos seguros",
    "EntregarCalendarioAgotamiento": "entrega el calendario",
}


def imprimir_traza(nombre, r):
    """Qué se ordenó cada turno y qué produjo. La cadena causal, no el resultado."""
    m = r["metricas"]
    res = m["reservas"]
    print()
    print("-- " + nombre.upper() + " " + "-" * max(4, 56 - len(nombre)))
    print(f"   {m['aperturas_netas']} netas · {m['reaperturas']} reaperturas · "
          f"{m['muertes_evitables']} muertes · legit {res['legitimidad']:.0f} · "
          f"cohes {res['cohesion_mesa']:.0f}")
    print()

    for t in r["traza"]:
        ordenes = []
        for accion, ok, _msg, datos in t["ordenes"]:
            etiqueta = ABREVIA.get(accion, accion)
            if not ok:
                etiqueta = etiqueta + " (falló)"
            elif "p_incidente" in datos:
                etiqueta += f" P={datos['p_incidente']:.0%}"
                if datos.get("victimas"):
                    etiqueta += f" ¡{datos['victimas']} VÍCTIMA(S)!"
            ordenes.append(etiqueta)
        texto = " · ".join(ordenes) if ordenes else "— sin órdenes —"

        # Solo los eventos que explican algo. El ruido no ayuda a calibrar.
        consecuencias = []
        ap = sum(1 for e in t["eventos"] if e.get("tipo") == "apertura")
        if ap:
            consecuencias.append(f"+{ap} abierto(s)")
        reap = sum(1 for e in (t["eventos"] + t.get("noche", []))
                   if e.get("tipo") == "reapertura")
        if reap:
            consecuencias.append(f"-{reap} reabierto(s)")
        muertes = t.get("muertes_tras_noche", t["muertes"])
        if muertes:
            consecuencias.append(f"{muertes} muertes acumuladas")

        print(f"   T{t['turno']}  {texto}")
        if consecuencias:
            print("        -> " + " · ".join(consecuencias) +
                  f" · presión {t['presion']:.0f}")


def diagnosticar(nombre, r):
    """
    Por qué salió así. Se LEE de la corrida, no se interpreta.

    Es lo que convierte la tabla de `--comparar` en algo con lo que se puede
    calibrar: dice qué pieza produjo cada número.
    """
    m = r["metricas"]
    print()
    print("   POR QUÉ SALIÓ ASÍ")

    # --- las muertes ---
    muertas = {rid: d for rid, d in r["regiones"].items() if d["muertes"] > 0}
    if not muertas:
        print("   · Muertes 0: todas las regiones tuvieron reposición a tiempo.")
    else:
        print(f"   · {m['muertes_evitables']} muertes, repartidas así:")
        for rid, d in sorted(muertas.items(), key=lambda x: -x[1]["muertes"]):
            servida = r["sirvio_humanitario"][rid]
            causa = ("tuvo camino humanitario abierto, pero tarde o insuficiente"
                     if servida else
                     "NUNCA tuvo un camino humanitario abierto que la sirviera")
            print(f"       {d['nombre']:<24} {d['muertes']:>4} — {causa}")

    # --- las aperturas ---
    a = m["aperturas"]
    print(f"   · {a['fuerza']} por fuerza, {a['concertacion']} por concertación, "
          f"{a['desgaste']} por desgaste · {m['reaperturas']} volvieron a cerrarse")
    if a["fuerza"] and m["reaperturas"] >= a["fuerza"]:
        print("       Lo abierto por la fuerza se cerró de noche: es la aritmética")
        print("       del caso, no mala suerte.")

    # --- la cohesión ---
    banderas = r["banderas"]
    voceria = banderas.get("protocolo_voceria")
    criterio = banderas.get("criterio_priorizacion")
    peajes = []
    if not voceria:
        peajes.append("-5/turno por no tener protocolo de vocería")
    if not criterio:
        peajes.append("-3/turno por no tener criterio de priorización")
    if peajes:
        print("   · Cohesión: " + "; ".join(peajes))
    else:
        print(f"   · Cohesión: las dos banderas puestas pronto (vocería T{voceria}, "
              f"criterio T{criterio}); el peaje se cortó.")

    # --- la mesa ---
    if m["acuerdos_cumplidos"] or m["acuerdos_rotos"]:
        print(f"   · Acuerdos: {m['acuerdos_cumplidos']} cumplidos, "
              f"{m['acuerdos_rotos']} rotos")
    if m["escoltas_logradas"] or m["escoltas_atacadas"]:
        print(f"   · Escoltas: {m['escoltas_logradas']} llegaron, "
              f"{m['escoltas_atacadas']} atacadas")
    if m["denuncias_estalladas"]:
        print(f"   · {m['denuncias_estalladas']} denuncia(s) estallaron sin verificar; "
              f"{m['denuncias_verificadas']} se verificaron")

    print(f"   · Mitigadores persistentes al cierre: {m['mitigadores_al_cierre']} · "
          f"decisiones con responsable: "
          f"{m['decisiones_atribuibles']}/{m['decisiones_totales']}")


def comparar(semilla: int, detalle: bool = False) -> None:
    print(SEP)
    print("  COMPARACIÓN DE ESTRATEGIAS — ninguna debería dominar")
    print(SEP)
    print(f"  {'estrategia':<17}{'netas':>7}{'reap':>6}{'muert':>7}"
          f"{'legit':>7}{'cohes':>7}{'credib':>8}{'resp':>7}")
    print("  " + "-" * 69)
    resultados = {}
    for nombre in ESTRATEGIAS:
        r = correr(nombre, semilla, verboso=False)
        resultados[nombre] = r
        m = r["metricas"]
        res = m["reservas"]
        print(f"  {nombre:<17}{m['aperturas_netas']:>7}{m['reaperturas']:>6}"
              f"{m['muertes_evitables']:>7}{res['legitimidad']:>7.0f}"
              f"{res['cohesion_mesa']:>7.0f}{res['credibilidad_mesa']:>8.0f}"
              f"{res['respaldo_internacional']:>7.0f}")

    if not detalle:
        print()
        print("  Con --detalle se ve qué se ordenó cada turno y por qué salió así.")
        return

    print()
    print(SEP)
    print("  QUÉ SE ORDENÓ, Y POR QUÉ SALIÓ ASÍ")
    print(SEP)
    for nombre, r in resultados.items():
        imprimir_traza(nombre, r)
        diagnosticar(nombre, r)


def mostrar_vistas(semilla: int, turnos: int = 2) -> None:
    """Las nueve vistas privadas después de N turnos, para revisar su contenido."""
    estado = cargar_estado()
    motor = MotorCrisis(estado, semilla=semilla)
    for t in range(1, turnos + 1):
        plan_constituida(motor, t)
        motor.paso(franja="dia")
        if t < turnos:
            motor.paso(franja="noche")

    print(SEP)
    print(f"  LAS OCHO VISTAS PRIVADAS — turno {estado.turno_decision}")
    print(SEP)
    for rol, v in views.todas(estado).items():
        print()
        print(f"── {rol.upper()} " + "─" * (60 - len(rol)))
        print(f"  ALERTA: {v['alerta']}")
        print("  detalle:")
        print("    " + json.dumps(v["detalle"], ensure_ascii=False,
                                  indent=2).replace("\n", "\n    ")[:1400])


# ---------------------------------------------------------------------------
# La lectura (`B14`, docs/LA_MEDICION.md)
#
# El mismo material que el equipo docente ve en el debriefing, impreso desde la
# terminal y sin montar la sala. Existe por dos razones distintas:
#
#   · PARA LEERLA. La firma y los repartos de una estrategia pura son la única
#     forma barata de comprobar que la lectura DICE ALGO — que `solo_fuerza` y
#     `solo_mesa` no salen descritas igual. Si salieran, el instrumento no
#     estaría midiendo la conducta sino el escenario.
#   · PARA VALIDARLA. La lectura viaja como JSON a una pantalla, y una lectura
#     que no cierra sus cuentas es peor que ninguna: da una cifra falsa con
#     cara de verdadera. Las comprobaciones de abajo son las mismas que hacen
#     las pruebas, corriendo aquí sobre CUALQUIER estrategia.
#
# La comparación contra las siete salas ficticias NO va aquí: es `C5`, y exige
# corridas reales contra las que calibrar las bandas (§10).
# ---------------------------------------------------------------------------

def validar_lectura(L: dict, motor) -> list[str]:
    """
    Las cuentas de la lectura, comprobadas. Devuelve la lista de fallas —
    vacía si todo cierra.

    No lanza: imprimir la lectura y DESPUÉS decir qué no cuadra es más útil
    para calibrar que morirse en la primera resta que no da.
    """
    fallas: list[str] = []

    def cerca(a: float, b: float, tol: float = 0.01) -> bool:
        return abs(a - b) <= tol

    # 1 · El vocabulario. Ninguna acción puede inventarse una vía o un público.
    for im in motor.imputaciones:
        for v in im["via"]:
            if v not in modulo_lectura.VIAS:
                fallas.append(f"{im['accion']} declara la vía inexistente «{v}»")
        for pub in im["atiende"]:
            if pub not in modulo_lectura.PUBLICOS:
                fallas.append(f"{im['accion']} declara el público inexistente «{pub}»")

    # 2 · El reparto de vías suma uno (las dobles cuentan en las dos, §4).
    vias = L["como"]["vias"]
    total_vias = sum(v["decisiones"] for v in vias.values())
    if total_vias:
        suma = sum(v["proporcion"] for v in vias.values())
        if not cerca(suma, 1.0):
            fallas.append(f"las proporciones de vía suman {suma:.3f}, no 1")
        contadas = sum(len(im["via"]) for im in motor.imputaciones)
        if total_vias != contadas:
            fallas.append(f"el reparto de vías cuenta {total_vias} y las "
                          f"decisiones declaran {contadas}")

    # 3 · La atención suma uno SOBRE LAS DECISIONES CON PÚBLICO, y el residuo
    #     —el gobierno de sí mismo— sobre el total. Son dos denominadores
    #     distintos a propósito, y es justo donde se cuela el error.
    at = L["que"]["atencion"]
    con_publico = sum(pu["decisiones"] for pu in at["por_publico"].values())
    if con_publico:
        suma = sum(pu["proporcion"] for pu in at["por_publico"].values())
        if not cerca(suma, 1.0):
            fallas.append(f"las proporciones de atención suman {suma:.3f}, no 1")
    if at["decisiones"] != len(motor.imputaciones):
        fallas.append(f"la atención dice {at['decisiones']} decisiones y el "
                      f"motor registró {len(motor.imputaciones)}")
    sin_publico = sum(1 for im in motor.imputaciones if not im["atiende"])
    if at["gobierno_de_si_mismo"]["decisiones"] != sin_publico:
        fallas.append(f"el residuo dice {at['gobierno_de_si_mismo']['decisiones']} "
                      f"y hay {sin_publico} decisiones sin público")

    # 4 · Los cuatro públicos tienen saldo y celda en el 2×2. Un público que se
    #     cae del cruce es exactamente el que nadie miraría en el debriefing.
    for pub in modulo_lectura.PUBLICOS:
        if pub not in L["que"]["saldo"]:
            fallas.append(f"«{pub}» no tiene saldo")
        if pub not in L["que"]["cruce"]:
            fallas.append(f"«{pub}» no tiene celda en el cruce")

    # 5 · Viaja como JSON, que es la única forma en que la pantalla la recibe.
    try:
        json.dumps(L, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        fallas.append(f"la lectura no es serializable: {exc}")

    # 6 · Y es pura: calcularla no mueve el mundo ni consume la semilla.
    if modulo_lectura.calcular(motor) != L:
        fallas.append("dos lecturas del mismo cierre salieron distintas")

    return fallas


def imprimir_lectura(estrategia: str, motor) -> bool:
    """La lectura de una corrida, impresa y comprobada. `True` si cuadra."""
    L = modulo_lectura.calcular(motor)
    como, que = L["como"], L["que"]

    print()
    print(SEP)
    print(f"  LA LECTURA — {estrategia}")
    print(SEP)
    print(f"  «{L['firma']}»")

    print()
    print("  EL CÓMO — las seis vías")
    abren, no_abren = como["bloques"]
    for titulo, bloque_vias in (("    las que abren el punto", abren),
                                ("    las que no lo abren", no_abren)):
        print(titulo)
        for v in bloque_vias:
            d = como["vias"][v]
            barra = "#" * int(round(d["proporcion"] * 30))
            print(f"      {v:<12}{d['decisiones']:>3}  {d['proporcion']:>5.0%} {barra}")
    if como["sin_usar"]:
        print(f"    sin usar: {', '.join(como['sin_usar'])}")

    print(f"    aperturas {como['aperturas']} · reaperturas {como['reaperturas']}")
    des = como["desgaste"]
    print(f"    desgaste · lo desgastaron: {len(des['lo_desgastaron'])} · "
          f"se les cayó de hambre: {len(des['se_les_cayo_de_hambre'])}")

    c = como["calificadores"]
    c1, c3 = c["c1_anticiparon"], c["c3_miraron"]
    print(f"    C1 ¿anticiparon? .... {c1['anticipadas']} banderas antes del "
          f"primer incidente (jornada {c1['primer_incidente'] or '—'})")
    print(f"    C2 ¿aguantó? ........ revertidas la misma jornada: "
          f"{c['c2_aguantaron']['revertidas_misma_jornada']}")
    print(f"    C3 ¿miraron antes? .. {c3['verificados_antes']}/"
          f"{c3['puntos_operados']} puntos operados estaban verificados")

    print()
    print("  EL QUÉ — a quién atendieron, y cómo terminó cada uno")
    at = que["atencion"]
    for pub in modulo_lectura.PUBLICOS:
        d = at["por_publico"][pub]
        cruce = que["cruce"][pub]
        print(f"    {pub:<15}{d['decisiones']:>3}  {d['proporcion']:>5.0%}  "
              f"atención {cruce['atencion']:<7} saldo {cruce['saldo']}")
    r = at["gobierno_de_si_mismo"]
    print(f"    {'(de sí mismo)':<15}{r['decisiones']:>3}  {r['proporcion']:>5.0%}"
          f"  — sobre {at['decisiones']} decisiones")
    print(f"    bandas: {que['saldo']['base']}")

    print()
    print("  LOS HECHOS DEL SALDO")
    for pub in modulo_lectura.PUBLICOS:
        s_pub = que["saldo"][pub]
        print(f"    {pub} [{s_pub['banda']}]")
        for hecho in s_pub["hechos"]:
            print(f"       · {hecho}")

    nadie = que["publico_que_nadie_miro"]
    print()
    if nadie:
        print(f"  EL PÚBLICO QUE NADIE MIRÓ — {nadie['publico']}")
        print(f"    {nadie['linea']}")
        print(f"    {nadie['consecuencia']}")
    else:
        print("  EL PÚBLICO QUE NADIE MIRÓ — ninguno se quedó sin una decisión.")

    sf = que["empresa_sin_fuerza"]
    print(f"  Residuo §5B: de {sf['atendieron']} decisión(es) que atendieron a "
          f"la empresa, {sf['sin_fuerza']} sin fuerza.")

    print()
    fallas = validar_lectura(L, motor)
    if fallas:
        print("  LA LECTURA NO CIERRA SUS CUENTAS:")
        for f in fallas:
            print(f"    ! {f}")
    else:
        print("  Las cuentas de la lectura cierran.")
    return not fallas


def leer(estrategia: str, semilla: int, verboso: bool = False) -> bool:
    """Corre una estrategia y lee su corrida. `True` si la lectura cuadra."""
    r = correr(estrategia, semilla, verboso=verboso)
    return imprimir_lectura(estrategia, r["motor"])


def leer_todas(semilla: int) -> bool:
    """
    La lectura de las siete estrategias puras, seguidas.

    El criterio no es que ninguna gane —eso lo mira `--comparar`— sino que
    ninguna se LEA IGUAL que otra. Dos firmas idénticas para dos conductas
    opuestas serían el instrumento describiendo el escenario y no a la sala.
    """
    ok = True
    firmas: dict[str, str] = {}
    for nombre in ESTRATEGIAS:
        r = correr(nombre, semilla, verboso=False)
        ok = imprimir_lectura(nombre, r["motor"]) and ok
        firmas[nombre] = modulo_lectura.calcular(r["motor"])["firma"]

    print()
    print(SEP)
    print("  LAS SIETE FIRMAS — ninguna debería leerse igual que otra")
    print(SEP)
    for nombre, firma in firmas.items():
        print(f"  {nombre:<17}«{firma}»")
    repetidas = len(firmas) - len(set(firmas.values()))
    if repetidas:
        print(f"  ! {repetidas} firma(s) repetida(s): la lectura no está "
              f"distinguiendo conductas distintas.")
        ok = False
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="SIMCASE · Estallido Social")
    ap.add_argument("--estrategia", default="constituida", choices=list(ESTRATEGIAS))
    ap.add_argument("--semilla", type=int, default=P.SEMILLA_POR_DEFECTO)
    ap.add_argument("--comparar", action="store_true")
    ap.add_argument("--detalle", action="store_true",
                    help="con --comparar: la traza de órdenes y el diagnóstico")
    ap.add_argument("--vistas", action="store_true")
    ap.add_argument("--lectura", action="store_true",
                    help="imprime y valida la lectura del cierre (B14)")
    ap.add_argument("--todas", action="store_true",
                    help="con --lectura: las siete estrategias y sus firmas")
    args = ap.parse_args()

    if args.comparar:
        comparar(args.semilla, detalle=args.detalle)
    elif args.vistas:
        mostrar_vistas(args.semilla)
    elif args.lectura:
        # Sale con 1 si la lectura no cierra sus cuentas: así vale como
        # comprobación de un script y no solo como algo que se mira.
        ok = (leer_todas(args.semilla) if args.todas
              else leer(args.estrategia, args.semilla))
        sys.exit(0 if ok else 1)
    else:
        correr(args.estrategia, args.semilla)


if __name__ == "__main__":
    main()
