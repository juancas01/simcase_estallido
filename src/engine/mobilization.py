"""
mobilization.py — El adversario reflexivo (§4.1).

Es el motor que define el caso. Si solo se implementa uno, es este.

    La lluvia no reacciona a lo que usted decide. Una movilización sí.

El bucle central que este módulo tiene que producir SIN que nadie lo escriba en
un guion:

    operación de fuerza → probabilidad de incidente → imagen viral
    → intensidad sube → aparecen nodos nuevos en otras ciudades
    → hace falta más fuerza → la fuerza disponible es la misma

Es decir: **abrir un corredor por la fuerza puede cerrar dos.**
"""

from __future__ import annotations

import random

from src.engine import parameters as P
from src.engine.state import Estado, Nodo


def _delta_con_rendimientos_decrecientes(estado: Estado, evento: str, base: float) -> float:
    """
    El segundo muerto de la semana mueve menos que el primero.

    Sin esto la variable satura: arranca en 61, un incidente mortal suma +20 y
    con dos incidentes queda clavada en 100, momento en el cual todas las
    decisiones posteriores dan igual — lo peor que le puede pasar a la variable
    central del motor.
    """
    n = estado._conteo_eventos.get(evento, 0)
    estado._conteo_eventos[evento] = n + 1
    return base * (P.DECAIMIENTO_REPETICION ** n)


def registrar_evento(estado: Estado, evento: str, region_id: str | None = None) -> float:
    """
    Aplica el efecto de un evento sobre la intensidad. Devuelve el delta aplicado.

    Los eventos positivos (que suben la movilización) llevan rendimientos
    decrecientes; los negativos no, porque un acuerdo verificable no vale menos
    por ser el segundo.
    """
    if evento in P.DELTA_INTENSIDAD:
        delta = _delta_con_rendimientos_decrecientes(
            estado, evento, P.DELTA_INTENSIDAD[evento]
        )
    elif evento in P.DELTA_INTENSIDAD_NEGATIVO:
        delta = P.DELTA_INTENSIDAD_NEGATIVO[evento]
    else:
        raise KeyError(f"evento de movilización desconocido: {evento}")

    estado.intensidad_nacional = _clamp(estado.intensidad_nacional + delta)

    # Regional: el efecto es mayor donde ocurrió
    for r in estado.regiones.values():
        peso = 1.6 if (region_id and r.region_id == region_id) else 0.5
        r.intensidad_movilizacion = _clamp(r.intensidad_movilizacion + delta * peso)

    estado.eventos_turno.append(
        {"tipo": "movilizacion", "evento": evento, "delta": round(delta, 2),
         "region": region_id}
    )
    return delta


def step(estado: Estado, rng: random.Random) -> dict:
    """
    Avanza la movilización un turno y aplica su realimentación sobre el mundo.

    Se ejecuta DESPUÉS de resolver las acciones del turno, para que los eventos
    que produjeron ya estén registrados.
    """
    # 1 · Decaimiento proporcional al nivel, no constante.
    #     Un decaimiento fijo de -2 no alcanza a bajar de 100 y la variable
    #     se queda pegada al techo.
    estado.intensidad_nacional = _clamp(
        estado.intensidad_nacional * (1.0 - P.TASA_DECAIMIENTO_PROPORCIONAL)
    )
    for r in estado.regiones.values():
        r.intensidad_movilizacion = _clamp(
            r.intensidad_movilizacion * (1.0 - P.TASA_DECAIMIENTO_PROPORCIONAL)
        )

    # 2 · Realimentación sobre los nodos existentes
    nodos_nuevos = 0
    for region in estado.regiones.values():
        exceso = max(0.0, region.intensidad_movilizacion - 50.0)

        # Los nodos secundarios (los no modelados) crecen como presión de fondo
        crecimiento = exceso * P.NODOS_NUEVOS_POR_INTENSIDAD
        region.nodos_secundarios_activos = max(
            0, int(region.nodos_secundarios_activos + crecimiento - 2)
        )

        for nodo in _nodos_de(estado, region.region_id):
            # Los nodos cerrados se endurecen con la intensidad
            if not nodo.abierto:
                nodo.dureza += exceso * P.DUREZA_POR_INTENSIDAD
            # La masa presente sigue a la intensidad
            base = 120 if estado.franja == "noche" else 200
            nodo.masa_presente = int(base + exceso * P.MASA_POR_INTENSIDAD)
            nodo.clamp()

        # Nodos nuevos: solo si la intensidad es alta y hay dónde
        if exceso > 25 and rng.random() < (exceso / 200.0):
            nuevo = _generar_nodo(estado, region.region_id, rng)
            if nuevo:
                estado.nodos[nuevo.nodo_id] = nuevo
                nodos_nuevos += 1
                estado.eventos_turno.append(
                    {"tipo": "nodo_nuevo", "nodo": nuevo.nodo_id,
                     "region": region.region_id}
                )

    return {
        "intensidad_nacional": round(estado.intensidad_nacional, 1),
        "nodos_nuevos": nodos_nuevos,
    }


def erosionar_apoyo_local(estado: Estado, region_id: str, delta: float) -> None:
    """
    La escasez prolongada y el esquema humanitario municipal BAJAN el apoyo al
    cierre, mientras el uso de la fuerza SUBE la intensidad.

    Son dos variables distintas moviéndose en direcciones opuestas, y es lo que
    da contenido a la acción A4 del Alcalde de Cali: reduce el incentivo
    material del cierre sin alimentar la movilización. Es la única vía de
    apertura que no consume ninguna reserva.
    """
    for nodo in _nodos_de(estado, region_id):
        nodo.apoyo_local = max(0.0, nodo.apoyo_local - delta)


def presion_por_escasez(estado: Estado) -> None:
    """
    La escasez tiene dos efectos opuestos y hay que aplicar los dos:
      * baja `apoyo_local`  — la gente quiere comer
      * sube `intensidad`   — la gente está furiosa
    """
    for region in estado.regiones.values():
        if region.dias_autonomia_alimentos < 2.0:
            erosionar_apoyo_local(estado, region.region_id, 0.05)
            region.intensidad_movilizacion = _clamp(
                region.intensidad_movilizacion + 2.0
            )


# ---------------------------------------------------------------------------

def _clamp(v: float) -> float:
    return min(P.INTENSIDAD_MAX, max(0.0, v))


def _nodos_de(estado: Estado, region_id: str) -> list[Nodo]:
    return [n for n in estado.nodos.values() if n.region_id == region_id]


def _generar_nodo(estado: Estado, region_id: str, rng: random.Random) -> Nodo | None:
    idx = len(estado.nodos) + 1
    nodo_id = f"N{idx:03d}"
    if nodo_id in estado.nodos:
        return None
    from src.engine.state import Composicion
    return Nodo(
        nodo_id=nodo_id,
        nombre=f"Cierre espontáneo {idx}",
        region_id=region_id,
        corredor_id=None,
        dureza=rng.uniform(0.25, 0.5),
        caudal=0.0,
        masa_presente=150,
        apoyo_local=rng.uniform(0.5, 0.85),
        control_voceria=rng.uniform(0.1, 0.4),   # los nuevos no tienen vocería
        composicion_real=Composicion(
            rng.uniform(0.6, 0.9), rng.uniform(0.05, 0.25), rng.uniform(0.0, 0.15)
        ).normalizada(),
    )
