"""
aperture.py — Apertura y reapertura de nodos (§4.3).

El corazón pedagógico del caso. Tres vías de abrir un corredor con economías
radicalmente distintas:

    Fuerza        rápida    reabre en 1-2 turnos     consume tres reservas
    Concertación  lenta     se sostiene              caudal = 0,9 × control_voceria
    Desgaste      lentísima no reabre                no consume nada

    «Un corredor pactado se sostiene y uno abierto por la fuerza vuelve a
     cerrarse esa misma noche.» — el motor debe hacerla cierta, no citarla.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.engine import parameters as P
from src.engine.state import Estado, Nodo


@dataclass
class ResultadoApertura:
    nodo_id: str
    via: str
    abierto: bool
    caudal: float
    mensaje: str


def abrir_por_fuerza(nodo: Nodo, rng: random.Random, turno: int) -> ResultadoApertura:
    lo, hi = P.CAUDAL_APERTURA_FUERZA
    nodo.caudal = rng.uniform(lo, hi)
    nodo.modo_apertura = "fuerza"
    nodo.turnos_desde_apertura = 0
    return ResultadoApertura(
        nodo.nodo_id, "fuerza", True, nodo.caudal,
        f"{nodo.nombre} abierto por la fuerza (caudal {nodo.caudal:.0%}). "
        f"Reabrirá si la movilización lo sostiene.",
    )


def avanzar_concertacion(nodo: Nodo, turno: int) -> ResultadoApertura | None:
    """
    La concertación tarda 2 turnos. Devuelve None mientras está en curso.

    LA TRAMPA, y es la mejor del caso: el caudal logrado es proporcional a
    `control_voceria`. Negociar con un vocero que controla el 40 % del nodo
    produce una apertura del 36 % que se anuncia como éxito y se desmiente sola.
    """
    nodo.turnos_en_negociacion += 1
    if nodo.turnos_en_negociacion < P.TURNOS_APERTURA["concertacion"]:
        return None

    caudal = P.CAUDAL_APERTURA_CONCERTACION * nodo.control_voceria
    nodo.caudal = caudal
    nodo.modo_apertura = "concertacion"
    nodo.turnos_desde_apertura = 0
    nodo.turnos_en_negociacion = 0

    aviso = ""
    if nodo.control_voceria < 0.6:
        aviso = (
            f" ATENCIÓN: la vocería solo controla el {nodo.control_voceria:.0%} "
            f"del punto. El acuerdo no cubre el resto."
        )
    return ResultadoApertura(
        nodo.nodo_id, "concertacion", caudal > 0.05, caudal,
        f"{nodo.nombre} abierto por concertación (caudal {caudal:.0%}).{aviso}",
    )


def revisar_desgaste(nodo: Nodo, rng: random.Random) -> ResultadoApertura | None:
    """
    Si el apoyo local cae lo suficiente Y SE SOSTIENE, el cierre se deshace solo.
    Es la única vía que no consume ninguna reserva — y la que el esquema
    humanitario municipal del Alcalde de Cali habilita.

    Tiene que ser LENTA. Si el desgaste es barato y rápido domina a las otras dos
    vías, y entonces ni la fuerza ni la concertación importan: la sala descubre
    que basta con esperar. Requiere apoyo bajo sostenido varios turnos y aun así
    no es automático.
    """
    if nodo.abierto:
        nodo.turnos_apoyo_bajo = 0
        return None
    if nodo.apoyo_local > P.UMBRAL_APOYO_DESGASTE:
        nodo.turnos_apoyo_bajo = 0
        return None

    nodo.turnos_apoyo_bajo += 1
    if nodo.turnos_apoyo_bajo < P.TURNOS_APOYO_BAJO_PARA_DESGASTE:
        return None
    if rng.random() > P.P_DESGASTE_POR_TURNO:
        return None
    lo, hi = P.CAUDAL_APERTURA_DESGASTE
    nodo.caudal = rng.uniform(lo, hi)
    nodo.modo_apertura = "desgaste"
    nodo.turnos_desde_apertura = 0
    return ResultadoApertura(
        nodo.nodo_id, "desgaste", True, nodo.caudal,
        f"{nodo.nombre} se levantó solo: el apoyo del barrio al cierre se agotó.",
    )


def step(estado: Estado, rng: random.Random) -> dict:
    """
    Avanza aperturas, reaperturas y desgastes.

    La reapertura de los nodos abiertos por la fuerza ocurre DE NOCHE. Es lo que
    da su sentido literal a la frase del caso, y lo que la sala ve pasar sin
    poder intervenir durante el interludio nocturno.
    """
    reaperturas: list[str] = []
    desgastes: list[str] = []

    for nodo in estado.nodos.values():
        nodo.dias_sostenido += 1 if not nodo.abierto else 0

        if nodo.abierto and nodo.modo_apertura == "fuerza":
            nodo.turnos_desde_apertura += 1
            if estado.franja == "noche":
                # Cuanto mayor la intensidad y el apoyo local, antes reabre
                region = estado.regiones.get(nodo.region_id)
                intensidad = region.intensidad_movilizacion if region else 60.0
                p_reabre = min(0.95, (intensidad / 100.0) * (0.4 + nodo.apoyo_local))
                if nodo.turnos_desde_apertura >= 1 and rng.random() < p_reabre:
                    nodo.caudal = 0.0
                    nodo.modo_apertura = "cerrado"
                    nodo.turnos_desde_apertura = 0
                    nodo.dureza = min(1.0, nodo.dureza + 0.08)
                    reaperturas.append(nodo.nodo_id)

        elif nodo.abierto and nodo.modo_apertura == "concertacion":
            # Se sostiene mientras el acuerdo se cumpla. Si la credibilidad de
            # la mesa se hunde, el acuerdo se rompe.
            if estado.reservas.credibilidad_mesa < P.UMBRALES["credibilidad_comite_suspende"]:
                if rng.random() < 0.35:
                    nodo.caudal = 0.0
                    nodo.modo_apertura = "cerrado"
                    reaperturas.append(nodo.nodo_id)

        else:
            r = revisar_desgaste(nodo, rng)
            if r:
                desgastes.append(nodo.nodo_id)

        nodo.clamp()

    for nid in reaperturas:
        estado.eventos_turno.append({"tipo": "reapertura", "nodo": nid})
    for nid in desgastes:
        estado.eventos_turno.append({"tipo": "desgaste", "nodo": nid})

    return {"reaperturas": len(reaperturas), "desgastes": len(desgastes)}


def aperturas_netas(estado: Estado) -> int:
    """Aperturas − reaperturas. La métrica que resume el ejercicio."""
    ap = sum(1 for e in estado.eventos_turno if e.get("tipo") == "apertura")
    re = sum(1 for e in estado.eventos_turno if e.get("tipo") == "reapertura")
    return ap - re
