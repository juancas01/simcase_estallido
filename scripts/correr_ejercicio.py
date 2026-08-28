"""
correr_ejercicio.py — Corre un ejercicio completo sin interfaz y sin LLM.

El motor de principio a fin en milisegundos, para calibrar sin gastar tokens ni
montar la sala.

    uv run python scripts/correr_ejercicio.py
    uv run python scripts/correr_ejercicio.py --estrategia constituida
    uv run python scripts/correr_ejercicio.py --comparar
    uv run python scripts/correr_ejercicio.py --vistas

Las estrategias existen para el criterio de calibración: ajustar hasta que
NINGUNA pura gane. Si `solo_fuerza` domina, el modelo está mal calibrado; si
`constituida` gana siempre y sin costo, también.
"""

from __future__ import annotations

import argparse
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
from src.engine.loader import cargar_estado                 # noqa: E402
from src.engine.simulation import MotorCrisis               # noqa: E402
from src.engine.actions import (                            # noqa: E402
    FijarRegistroEscrito, FijarLineasRojas, FirmarAsistenciaMilitar,
    ExigirProtocoloVoceria, ConvocarMesaNacional, AbrirMesaLocal,
    OfrecerContraprestacion,
    CondicionarEmpleoFuerza, InstalarMesaConVoceros, EsquemaHumanitarioMunicipal,
    FijarReglasEmpleoSector, OperarNodo, RedesplegarMilitares,
    ClasificarParteOperacional, DisponerESMAD, Escoltar, SolicitarRelevo,
    ExigirEstandaresEmpleo, AdoptarProtocoloVerificacion, AsignarDuplas,
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
        motor.encolar(ExigirEstandaresEmpleo())
        motor.encolar(AdoptarCriterioPriorizacion())
        motor.encolar(ExigirProtocoloVoceria())
        motor.encolar(AsignarDuplas(nodos=["N003", "N013", "N022"]))
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
            dupla_presente=True, concertado_con_alcaldia=True,
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
        motor.encolar(ExigirEstandaresEmpleo())
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
    proy = motor.proyectar_sin_mando()

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

    return {"metricas": m, "proyeccion": proy, "traza": traza,
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
    "ExigirEstandaresEmpleo": "estándares de empleo",
    "AdoptarProtocoloVerificacion": "protocolo de verificación",
    "AsignarDuplas": "duplas",
    "RequerirCorredoresHumanitarios": "requiere corredor humanitario",
    "ManifestarDudaPermanencia": "duda su permanencia",
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


def main() -> None:
    ap = argparse.ArgumentParser(description="SIMCASE · Estallido Social")
    ap.add_argument("--estrategia", default="constituida", choices=list(ESTRATEGIAS))
    ap.add_argument("--semilla", type=int, default=P.SEMILLA_POR_DEFECTO)
    ap.add_argument("--comparar", action="store_true")
    ap.add_argument("--detalle", action="store_true",
                    help="con --comparar: la traza de órdenes y el diagnóstico")
    ap.add_argument("--vistas", action="store_true")
    args = ap.parse_args()

    if args.comparar:
        comparar(args.semilla, detalle=args.detalle)
    elif args.vistas:
        mostrar_vistas(args.semilla)
    else:
        correr(args.estrategia, args.semilla)


if __name__ == "__main__":
    main()
