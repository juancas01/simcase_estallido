"""
mobilization.py — El adversario reflexivo.

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
from src.engine import territory
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

    **TODOS decaen, y antes solo decaían los que suben.** La exención de los
    negativos estaba razonada así: «un acuerdo verificable no vale menos por ser
    el segundo». Era el agujero central del motor — repetir la misma buena
    noticia bajaba la intensidad sin límite, y una sola acción repetida seis
    veces por jornada ganaba el ejercicio entero.

    Con la regla simétrica hay una sola frase que aprender —la calle se satura
    de lo que sea que se repita— y este módulo pierde una rama.
    """
    if evento in P.DELTA_INTENSIDAD:
        base = P.DELTA_INTENSIDAD[evento]
    elif evento in P.DELTA_INTENSIDAD_NEGATIVO:
        base = P.DELTA_INTENSIDAD_NEGATIVO[evento]
    else:
        raise KeyError(f"evento de movilización desconocido: {evento}")

    delta = _delta_con_rendimientos_decrecientes(estado, evento, base)

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
            # LA MASA SIGUE A LA INTENSIDAD Y AL TAMAÑO DEL PUNTO.
            #
            # Lo segundo faltaba: la cifra salía de la intensidad de la región y
            # de nada más, así que los seis puntos de Bellaflor tenían siempre la
            # MISMA cifra exacta de personas. Un peaje de carretera y una glorieta
            # del centro no reúnen la misma gente, y el término de masa del riesgo
            # de incidente (`force.py`) llevaba todo este tiempo sin distinguirlos.
            # No se veía porque nada mostraba la cifra; el mapa la muestra.
            factor = P.MASA_FACTOR_NOCTURNO if estado.franja == "noche" else 1.0
            crecida = 1.0 + exceso * P.MASA_POR_INTENSIDAD / P.MASA_BASE_REFERENCIA
            nodo.masa_presente = int(nodo.masa_base * factor * crecida)
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
    """
    Un cierre espontáneo donde antes no había nada.

    EL IDENTIFICADOR SE BUSCA LIBRE, no se deriva del tamaño. Los del escenario
    no son correlativos —son los once que deciden un corredor, de entre más de
    mil— y `len(nodos) + 1` caía encima de uno existente y devolvía `None`: el
    bucle central del caso, el que hace que abrir un corredor por la fuerza
    pueda cerrar dos, se quedaba sin su efecto más visible y en silencio.
    """
    from src.engine.state import Composicion

    nodo_id = next((f"N{i:03d}" for i in range(1, 1000)
                    if f"N{i:03d}" not in estado.nodos), None)
    if nodo_id is None:
        return None

    # LAS TRES PROPORCIONES SE SORTEAN Y SOLO SE GUARDAN DOS.
    #
    # `Composicion` almacena la protesta legítima y la estructura organizada, y
    # deriva el vandalismo como residuo — pero **sortearlo sigue haciendo falta**,
    # porque es lo que fija el peso relativo de las otras dos al repartir el
    # total. Sortear solo dos daría otra distribución: la protesta legítima
    # saldría sistemáticamente más alta, y como es la que multiplica el costo de
    # operar sobre población civil, encarecería en silencio cada operación sobre
    # un cierre espontáneo.
    #
    # Un cierre que aparece a mitad de partida es sobre todo gente que salió esa
    # tarde: mucha protesta y casi ninguna estructura.
    protesta = rng.uniform(0.6, 0.9)
    vandalismo = rng.uniform(0.05, 0.25)
    organizada = rng.uniform(0.0, 0.15)
    total = protesta + vandalismo + organizada

    return Nodo(
        nodo_id=nodo_id,
        # «Cierre espontáneo 006» son veintiún caracteres y en el mapa se parte
        # en dos líneas que se montan sobre los vecinos. Que sea espontáneo no
        # hace falta decirlo en el rótulo: apareció a mitad de partida, lleva
        # cero días sostenido y no pertenece a ningún corredor. Las tres cosas
        # están en su ficha.
        nombre=f"Cierre {nodo_id[1:]}",
        region_id=region_id,
        corredor_id=None,
        dureza=rng.uniform(0.25, 0.5),
        caudal=0.0,
        masa_base=150,
        masa_presente=150,
        apoyo_local=rng.uniform(0.5, 0.85),
        control_voceria=rng.uniform(0.1, 0.4),   # los nuevos no tienen vocería
        composicion_real=Composicion(protesta / total, organizada / total),
        # Y CON SITIO EN EL MAPA. Sin posición aterrizaban todos en el (0,0),
        # amontonados en una esquina del esquema y encima de la línea de otro
        # corredor: un punto nuevo que no se ve no cuenta nada.
        **_hueco_en(estado, region_id, rng),
    )


def _hueco_en(estado: Estado, region_id: str, rng: random.Random) -> dict:
    """
    Un sitio libre DENTRO de la región, y no solo cerca de sus puntos.

    Antes bastaba «cerca del centroide», porque el mapa era un esquema de líneas
    sobre un lienzo vacío y las coordenadas no afirmaban nada. Ahora el mapa
    dibuja el país: un cierre nuevo que aparece a catorce unidades del centroide
    puede caer al otro lado de la frontera de su región —o en el mar— y la
    pantalla lo pintaría en la región equivocada. `loader._verificar_geografia`
    exige lo contrario para el escenario; esto es lo mismo para lo que el motor
    genera solo.
    """
    poligono = (estado.geografia or {}).get("regiones", {}).get(region_id)
    vecinos = _nodos_de(estado, region_id)

    if poligono:
        cx, cy = territory.centroide(poligono)
    elif vecinos:
        cx = sum(n.x for n in vecinos) / len(vecinos)
        cy = sum(n.y for n in vecinos) / len(vecinos)
    else:
        return {"x": rng.uniform(20, 80), "y": rng.uniform(20, 80)}

    # Nueve unidades de separación y no siete. Con el mapa dibujando el nombre de
    # cada punto, dos cierres a siete unidades son dos rótulos superpuestos.
    def libre(x, y):
        return all((n.x - x) ** 2 + (n.y - y) ** 2 > 81 for n in estado.nodos.values())

    for _ in range(60):
        x = min(97.0, max(3.0, cx + rng.uniform(-14, 14)))
        y = min(97.0, max(3.0, cy + rng.uniform(-14, 14)))
        if not libre(x, y):
            continue
        if poligono and not territory.dentro(x, y, poligono):
            continue
        return {"x": round(x, 1), "y": round(y, 1)}

    # Si en sesenta intentos no cupo, el centroide de la región: apretado contra
    # otro punto, pero nunca fuera del territorio que dice ocupar.
    return {"x": round(cx, 1), "y": round(cy, 1)}
