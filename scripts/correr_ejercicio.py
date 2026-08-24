"""
correr_ejercicio.py — Corre un ejercicio completo sin interfaz y sin LLM.

Equivalente al `ajuste_parametros/run_sim.py` de Macondo: el motor de principio
a fin en milisegundos, para calibrar sin gastar tokens ni montar la sala.

    uv run python scripts/correr_ejercicio.py
    uv run python scripts/correr_ejercicio.py --estrategia solo_fuerza
    uv run python scripts/correr_ejercicio.py --estrategia constituida --semilla 7

Las tres estrategias existen para el criterio de calibración de §12.3: ajustar
hasta que NINGUNA estrategia pura gane. Si `solo_fuerza` domina, el modelo está
mal calibrado; si `constituida` gana siempre y sin costo, también.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Las consolas de Windows son cp1252 e imprimir acentos revienta. Se fuerza
# UTF-8 al arranque, como manda el anexo de `guia_arquitectura_simulaciones.md`.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine import parameters as P
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis
from src.engine.actions import (
    FijarRegistroEscrito, FijarLineasRojas, ExigirEstandaresEmpleo,
    AdoptarProtocoloVerificacion, ExigirProtocoloVoceria, AdoptarCriterioPriorizacion,
    OperarNodo, AbrirMesaLocal, EsquemaHumanitarioMunicipal, SolicitarRelevo,
    DesplegarDuplas, EntregarCalendarioAgotamiento,
)

SEP = "=" * 78


def plan_solo_fuerza(motor: MotorCrisis, turno: int) -> None:
    """La sala se salta la constitución y opera desde el turno 1."""
    cerrados = [n for n in motor.estado.nodos.values() if not n.abierto]
    cerrados.sort(key=lambda n: -n.dureza)
    for nodo in cerrados[:2]:
        motor.encolar(OperarNodo(nodo_id=nodo.nodo_id, tipo_unidad="esmad"))


def plan_solo_mesa(motor: MotorCrisis, turno: int) -> None:
    """La sala solo negocia. Nunca usa la fuerza."""
    cerrados = [n for n in motor.estado.nodos.values() if not n.abierto]
    cerrados.sort(key=lambda n: -n.control_voceria)
    for nodo in cerrados[:3]:
        motor.encolar(AbrirMesaLocal(nodo_id=nodo.nodo_id))
    if turno == 1:
        motor.encolar(ExigirProtocoloVoceria())


def plan_constituida(motor: MotorCrisis, turno: int) -> None:
    """La sala se constituye primero y después opera con los mitigadores puestos."""
    e = motor.estado
    if turno == 1:
        motor.encolar(FijarRegistroEscrito())
        motor.encolar(ExigirEstandaresEmpleo())
        motor.encolar(AdoptarCriterioPriorizacion())
        motor.encolar(DesplegarDuplas(nodos=["N003", "N013", "N022"]))
        return
    if turno == 2:
        motor.encolar(AdoptarProtocoloVerificacion())
        motor.encolar(SolicitarRelevo(n_unidades=8))
        motor.encolar(EsquemaHumanitarioMunicipal(region_id="R-VAL"))
        return

    cerrados = [n for n in e.nodos.values() if not n.abierto]
    concertables = sorted(
        [n for n in cerrados if n.control_voceria > 0.6], key=lambda n: -n.control_voceria
    )
    for nodo in concertables[:2]:
        motor.encolar(AbrirMesaLocal(nodo_id=nodo.nodo_id))

    duros = sorted([n for n in cerrados if n.control_voceria <= 0.4], key=lambda n: -n.dureza)
    if duros:
        motor.encolar(OperarNodo(
            nodo_id=duros[0].nodo_id, tipo_unidad="esmad",
            dupla_presente=True, concertado_con_alcaldia=True,
            responsable_nominado="Ministro de Defensa",
        ))


def plan_humanitaria(motor: MotorCrisis, turno: int) -> None:
    """
    Prioriza el anillo hospitalario y los corredores humanitarios.

    Existe para comprobar que las muertes evitables SON evitables. Si esta
    estrategia da el mismo numero de muertes que las demas, el oxigeno esta
    desacoplado de las decisiones y el modelo esta roto (fue el caso en la
    primera corrida).
    """
    e = motor.estado
    if turno == 1:
        motor.encolar(ExigirEstandaresEmpleo())

    # CONCENTRAR, no dispersar. Un corredor es tan bueno como su peor punto, asi
    # que abrir un nodo de cada corredor no abre ninguno. Se elige el corredor
    # humanitario mas corto y se trabaja hasta terminarlo.
    humanitarios = [c for c in e.corredores.values() if "humanitario" in c.clases_prioridad]
    humanitarios.sort(key=lambda c: len(c.nodos))
    objetivo = humanitarios[0]

    for nid in objetivo.nodos:
        nodo = e.nodos.get(nid)
        if nodo is None or nodo.abierto:
            continue
        # La fuerza no sirve para abrir un corredor: lo que abre de noche se
        # cierra, y el minimo vuelve a cero. Solo la concertacion se sostiene.
        motor.encolar(AbrirMesaLocal(nodo_id=nid))


def plan_pasiva(motor: MotorCrisis, turno: int) -> None:
    """La sala no decide. Para medir el costo de no decidir (§5.6)."""
    return


ESTRATEGIAS = {
    "solo_fuerza": plan_solo_fuerza,
    "solo_mesa": plan_solo_mesa,
    "constituida": plan_constituida,
    "humanitaria": plan_humanitaria,
    "pasiva": plan_pasiva,
}


def correr(estrategia: str, semilla: int, verboso: bool = True) -> dict:
    estado = cargar_estado()
    motor = MotorCrisis(estado, semilla=semilla)
    plan = ESTRATEGIAS[estrategia]

    if verboso:
        print(SEP)
        print(f"  SIMCASE · ESTALLIDO SOCIAL — estrategia: {estrategia} · semilla {semilla}")
        print(SEP)
        region, dias = estado.dias_autonomia_minimos()
        print(f"  t=0 · {len(estado.nodos)} nodos · intensidad {estado.intensidad_nacional:.0f} · "
              f"autonomía mínima {dias:.1f} d ({region})")
        print(f"  ESMAD en reserva: {len(estado.esmad_en_reserva())}/{P.ESMAD_ESCUADRONES_TOTALES} · "
              f"fatiga media {estado.fatiga_media('esmad'):.2f}")
        print(f"  Mitigadores activos: 0/6 — nada se ha constituido")
        print()

    for turno in range(1, P.TURNOS_DECISION + 1):
        plan(motor, turno)
        r = motor.paso(franja="dia")
        if verboso:
            print(f"── TURNO {turno} (día) " + "─" * 52)
            for nombre, res in r.resultados:
                marca = "  ok " if res.ok else "  ×  "
                print(f"{marca}{nombre}: {res.mensaje}")
                if res.datos.get("p_incidente") is not None:
                    print(f"       riesgo mostrado P={res.datos['p_incidente']:.0%} · "
                          f"tirada {res.datos['tirada']:.3f} · "
                          f"atribuible={res.datos['atribuible']}")
            if not r.resultados:
                print("   (sin órdenes)")
            print(f"   {r.resumen}")
            if r.umbrales_cruzados:
                print(f"   ⚠ UMBRALES: {', '.join(r.umbrales_cruzados)}")

        if turno < P.TURNOS_DECISION:
            rn = motor.paso(franja="noche")
            if verboso:
                reap = [e for e in rn.eventos if e.get("tipo") == "reapertura"]
                muertes = [e for e in rn.eventos if e.get("tipo") == "muertes_evitables"]
                partes = []
                if reap:
                    partes.append(f"{len(reap)} nodo(s) volvieron a cerrarse")
                if muertes:
                    partes.append(f"{sum(m['n'] for m in muertes)} muertes evitables")
                print(f"   · noche: {'; '.join(partes) if partes else 'sin novedad'}")
                print()

    m = motor.metricas()
    proy = motor.proyectar_sin_mando()

    if verboso:
        print(SEP)
        print("  MÉTRICAS AL CIERRE")
        print(SEP)
        print(f"  Aperturas netas ............ {m['aperturas_netas']}")
        print(f"  Por vía .................... fuerza {m['aperturas']['fuerza']} · "
              f"concertación {m['aperturas']['concertacion']} · desgaste {m['aperturas']['desgaste']}")
        print(f"  Reaperturas ................ {m['reaperturas']}")
        print(f"  Muertes evitables .......... {m['muertes_evitables']}")
        print(f"  Mitigadores al cierre ...... {m['mitigadores_al_cierre']}")
        print(f"  Registro escrito en turno .. {m['turno_primer_registro_escrito'] or 'nunca'}")
        print(f"  Decisiones atribuibles ..... {m['decisiones_atribuibles']}/{m['decisiones_totales']}")
        print(f"  Reservas ................... {m['reservas']}")
        print(f"  Gremios .................... {m['posicion_gremios']} · "
              f"Comité disponible: {m['comite_disponible']}")
        print()
        print(SEP)
        print("  PROYECCIÓN T+72h — el país que la sala entrega")
        print(SEP)
        for k in ("nodos_abiertos", "intensidad", "legitimidad", "muertes_evitables"):
            print(f"  {k:.<28} {proy['antes'][k]}  →  {proy['despues'][k]}")
        print(f"  {'autonomia_minima':.<28} {proy['despues']['autonomia_minima']}")
        print()

    return {"metricas": m, "proyeccion": proy}


def main() -> int:
    ap = argparse.ArgumentParser(description="Corre un ejercicio completo sin interfaz")
    ap.add_argument("--estrategia", choices=list(ESTRATEGIAS), default="constituida")
    ap.add_argument("--semilla", type=int, default=P.SEMILLA_POR_DEFECTO)
    ap.add_argument("--comparar", action="store_true",
                    help="corre las cuatro estrategias y compara (criterio de calibración)")
    args = ap.parse_args()

    if args.comparar:
        print(SEP)
        print("  COMPARACIÓN DE ESTRATEGIAS — ninguna debería dominar (§12.3)")
        print(SEP)
        filas = []
        for nombre in ESTRATEGIAS:
            out = correr(nombre, args.semilla, verboso=False)
            m = out["metricas"]
            filas.append((nombre, m))
        cab = f"  {'estrategia':<14}{'netas':>7}{'reap':>6}{'muertes':>9}{'legit':>7}{'cohes':>7}{'credib':>8}"
        print(cab)
        print("  " + "-" * (len(cab) - 2))
        for nombre, m in filas:
            print(f"  {nombre:<14}{m['aperturas_netas']:>7}{m['reaperturas']:>6}"
                  f"{m['muertes_evitables']:>9}{m['reservas']['legitimidad']:>7.0f}"
                  f"{m['reservas']['cohesion_mesa']:>7.0f}"
                  f"{m['reservas']['credibilidad_mesa']:>8.0f}")
        print()
        return 0

    correr(args.estrategia, args.semilla)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
