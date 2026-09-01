"""
aperture.py — Las tres formas de abrir un camino.

El corazón pedagógico del caso. Tres vías con economías radicalmente distintas:

    Fuerza        1 turno    mucho                 REABRE esa misma noche
    Concertación  2 turnos   0,9 × control_voceria  se sostiene si se cumple
    Desgaste      4+ turnos  medio                  no reabre, y es gratis

    «Un corredor pactado se sostiene y uno abierto por la fuerza vuelve a
     cerrarse esa misma noche.» — el motor debe hacerla cierta, no citarla.

Y desde la v2 hay una cuarta cosa que este módulo resuelve: **la segunda vía por
la que la mezcla real de un punto tiene consecuencia.** Pactar donde hay
estructura organizada produce un acuerdo que se incumple, porque quien firmó no
controla el punto. Es la otra mitad del error doble.

LA MESA HAY QUE INSTALARLA CADA JORNADA
---------------------------------------
La concertación tarda dos sesiones, no dos días. `turnos_en_negociacion` sube
una vez por sesión y solo por sesión, de modo que **no instalar una mesa un día
equivale a congelar las negociaciones**: no se pierde lo andado, pero tampoco se
avanza, y el reloj del ejercicio corre igual.

Eso ya era cierto y no lo sabía nadie. `instalar_mesa`, `cerrar_mesa` y
`revisar_mesas` no cambian la aritmética: la hacen visible en el mapa, en las
consecuencias de la noche y en la pregunta que reciben el Ministro del Interior
y el Alcalde al abrir el día.
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
    fragil: bool = False        # el acuerdo se firmó donde no controlan el punto


def abrir_por_fuerza(nodo: Nodo, rng: random.Random, turno: int) -> ResultadoApertura:
    lo, hi = P.CAUDAL_APERTURA_FUERZA
    nodo.caudal = rng.uniform(lo, hi)
    nodo.modo_apertura = "fuerza"
    nodo.turnos_desde_apertura = 0
    return ResultadoApertura(
        nodo.nodo_id, "fuerza", True, nodo.caudal,
        f"{nodo.nombre} abierto por la fuerza (deja pasar {nodo.caudal:.0%}). "
        f"Volverá a cerrarse si la movilización lo sostiene.",
    )


def instalar_mesa(nodo: Nodo, turno_decision: int) -> None:
    """
    Deja constancia de que hoy hubo sesión en este punto.

    **Es lo que hace que la mesa cuente como instalada esta jornada.** Sin esta
    marca, `revisar_mesas` no puede distinguir una mesa que trabajó de una que
    se dejó de lado, y esa distinción es la regla entera: una mesa local hay que
    instalarla cada jornada para que surta efecto.
    """
    nodo.mesa_abierta = True
    nodo.mesa_sesion_turno = turno_decision
    nodo.jornadas_mesa_congelada = 0


def cerrar_mesa(nodo: Nodo) -> None:
    """La mesa rindió: el punto se abrió por concertación y ya no hay qué negociar."""
    nodo.mesa_abierta = False
    nodo.jornadas_mesa_congelada = 0


def revisar_mesas(estado: Estado) -> dict:
    """
    Al cerrar cada jornada de decisión: qué mesas quedaron sin sesionar.

    **NO INSTALAR UNA MESA UN DÍA EQUIVALE A CONGELAR LAS NEGOCIACIONES**, y esa
    frase es literal en el motor: `turnos_en_negociacion` sube una vez por
    sesión y solo por sesión. Una mesa sin sesionar no pierde lo andado —no se
    castiga el silencio— pero tampoco avanza, y el reloj del ejercicio sí corre.
    Abrir una mesa en la jornada 4 y no volver a ella es no haberla abierto.

    Lo único que hace esta función es **hacerlo visible**: contar las jornadas
    congeladas y emitir el hecho, para que salga en el mapa, en las
    consecuencias de la noche y en la pregunta del día siguiente. La mecánica ya
    estaba; lo que no estaba era la forma de enterarse.

    Solo se llama en las ventanas de DÍA. De noche no se instala nada y no hay
    nada que reprochar.
    """
    congeladas = []
    for nodo in estado.nodos.values():
        if not nodo.mesa_abierta:
            continue
        if nodo.mesa_sesion_turno == estado.turno_decision:
            continue
        nodo.jornadas_mesa_congelada += 1
        congeladas.append(nodo.nodo_id)
        estado.eventos_turno.append({
            "tipo": "mesa_congelada",
            "nodo": nodo.nodo_id,
            "jornadas": nodo.jornadas_mesa_congelada,
        })
    return {"congeladas": len(congeladas), "nodos": congeladas}


def avanzar_concertacion(
    nodo: Nodo, turno: int, rng: random.Random
) -> ResultadoApertura | None:
    """
    La concertación tarda 2 turnos. Devuelve None mientras está en curso.

    LA TRAMPA, y es la mejor del caso: lo que se logra abrir es proporcional a
    `control_voceria`. Pactar con quien controla el 40 % del punto produce una
    apertura del 36 % que se anuncia como éxito y se desmiente sola en
    veinticuatro horas.

    Y hay una segunda trampa, invisible: si el punto tiene estructura organizada
    alta, **el acuerdo se rompe aunque la vocería fuera buena** — porque quien
    firmó no manda sobre quien sostiene el cierre. La sala no puede saberlo sin
    haber gastado un equipo de terreno ahí.
    """
    nodo.turnos_en_negociacion += 1
    if nodo.turnos_en_negociacion < P.TURNOS_APERTURA["concertacion"]:
        return None

    caudal = P.CAUDAL_APERTURA_CONCERTACION * nodo.control_voceria
    nodo.caudal = caudal
    nodo.modo_apertura = "concertacion"
    nodo.turnos_desde_apertura = 0
    nodo.turnos_en_negociacion = 0
    # La mesa rindió: deja de estar instalada, y el punto pasa a leerse por su
    # modo de apertura —pactado— que es lo que ahora lo sostiene.
    cerrar_mesa(nodo)

    organizada = nodo.composicion_real.normalizada().estructura_organizada
    fragil = rng.random() < organizada * P.FACTOR_INCUMPLIMIENTO_POR_ESTRUCTURA

    aviso = ""
    if nodo.control_voceria < 0.6:
        aviso = (f" ATENCIÓN: la vocería solo controla el {nodo.control_voceria:.0%} "
                 f"del punto. El acuerdo no cubre el resto.")

    return ResultadoApertura(
        nodo.nodo_id, "concertacion", caudal > 0.05, caudal,
        f"{nodo.nombre} abierto por concertación (deja pasar {caudal:.0%}).{aviso}",
        fragil=fragil,
    )


def liquidar_concertacion(
    estado: Estado, nodo: Nodo, r: ResultadoApertura, *, nota_fragil: str
) -> str:
    """
    El desenlace de una mesa que rindió: la apertura, lo que cuesta y lo que pasa
    si el acuerdo sale frágil. Devuelve el mensaje para la sala.

    LA FRONTERA, Y ES LO QUE HACE QUE ESTO NO BORRE NINGÚN ROL. Lo que distingue
    una mesa de otra —a quién puede sentar, dónde, con qué requisito previo, qué
    le cuesta abrir un canal paralelo, qué riesgo propio corre— **se queda en su
    acción**. Lo que es una regla del mundo —qué pasa cuando una mesa rinde— vive
    aquí, una sola vez. El Ministro del Interior, el Alcalde y el Ministro de
    Agricultura siguen teniendo cada uno su acción, con su jurisdicción y su
    contraparte.

    ESTABA ESCRITO TRES VECES Y YA HABÍAN DIVERGIDO. La mesa del Alcalde no
    registraba el evento `acuerdo_incumplido` en `eventos_turno`, de modo que un
    incumplimiento que sí ocurría no se dibujaba en el mapa ni salía en las
    consecuencias de la noche. **Nadie decidió esa diferencia**: se perdió al
    copiar el bloque, que es exactamente lo que un bloque copiado tres veces
    acaba haciendo.

    `nota_fragil` la pone cada rol porque es su voz —«los voceros con quienes se
    pactó», «quien firmó no manda sobre quien sostiene el cierre»— y eso sí es
    suyo.
    """
    from src.engine import mobilization

    estado.eventos_turno.append(
        {"tipo": "apertura", "nodo": nodo.nodo_id, "via": "concertacion"}
    )
    estado.reservas.aplicar(P.COSTO_RESERVAS["apertura_concertada"])
    mobilization.registrar_evento(estado, "apertura_concertada", nodo.region_id)

    if not r.fragil:
        return r.mensaje

    # Quien firmó no manda sobre quien sostiene el cierre: el acuerdo se
    # incumple en horas y solo queda una fracción de lo que se abrió.
    nodo.caudal *= P.CAUDAL_RESTANTE_ACUERDO_FRAGIL
    estado.reservas.aplicar(P.COSTO_RESERVAS["acuerdo_incumplido"])
    mobilization.registrar_evento(estado, "acuerdo_incumplido", nodo.region_id)
    estado.eventos_turno.append(
        {"tipo": "acuerdo_incumplido", "nodo": nodo.nodo_id}
    )
    return r.mensaje + nota_fragil


def revisar_desgaste(nodo: Nodo, rng: random.Random) -> ResultadoApertura | None:
    """
    Si el apoyo del barrio cae lo suficiente Y SE SOSTIENE, el cierre se deshace
    solo. Es la única vía que no consume ninguna reserva — y la que el esquema
    humanitario municipal del Alcalde habilita.

    Tiene que ser LENTA. Si el desgaste es barato y rápido domina a las otras dos
    vías, y entonces ni la fuerza ni la concertación importan: la sala descubre
    que basta con esperar.
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

    La reapertura de los puntos abiertos por la fuerza ocurre DE NOCHE. Es lo que
    da su sentido literal a la frase del caso, y lo que la sala ve pasar sin
    poder intervenir durante el interludio nocturno.
    """
    reaperturas: list[str] = []
    desgastes: list[str] = []

    # UN DÍA POR JORNADA, NO UNO POR TRAMO. `step()` corre dos veces al día
    # —día y noche— y este contador se incrementaba en las dos, de modo que un
    # punto que empezaba con quince días de cierre marcaba veinticinco al
    # terminar un ejercicio de cinco jornadas. El número sale en el mapa, con la
    # palabra «días» al lado, y su banda —reciente, asentado, enquistado,
    # crónico— saturaba en la primera jornada.
    #
    # Se cuenta AL CERRAR LA JORNADA, que es cuando el día terminó de verdad.
    if estado.franja == "noche":
        for nodo in estado.nodos.values():
            if not nodo.abierto:
                nodo.dias_sostenido += 1

    for nodo in estado.nodos.values():

        if nodo.abierto and nodo.modo_apertura == "fuerza":
            nodo.turnos_desde_apertura += 1
            if estado.franja == "noche":
                region = estado.regiones.get(nodo.region_id)
                intensidad = region.intensidad_movilizacion if region else 60.0
                p_reabre = min(0.95, (intensidad / 100.0) * (0.4 + nodo.apoyo_local))
                if (nodo.turnos_desde_apertura >= P.PASOS_ANTES_DE_REABRIR
                        and rng.random() < p_reabre):
                    nodo.caudal = 0.0
                    nodo.modo_apertura = "cerrado"
                    nodo.turnos_desde_apertura = 0
                    nodo.dureza = min(1.0, nodo.dureza + 0.08)
                    reaperturas.append(nodo.nodo_id)

        elif nodo.abierto and nodo.modo_apertura == "concertacion":
            # Se sostiene mientras el acuerdo se cumpla. Si la credibilidad de la
            # mesa se hunde, el acuerdo se rompe.
            if estado.reservas.credibilidad_mesa < P.UMBRALES["credibilidad_comite_suspende"]:
                if rng.random() < 0.35:
                    nodo.caudal = 0.0
                    nodo.modo_apertura = "cerrado"
                    reaperturas.append(nodo.nodo_id)

        else:
            if revisar_desgaste(nodo, rng):
                desgastes.append(nodo.nodo_id)

        nodo.clamp()

    for nid in reaperturas:
        estado.eventos_turno.append({"tipo": "reapertura", "nodo": nid})
    for nid in desgastes:
        estado.eventos_turno.append({"tipo": "desgaste", "nodo": nid})

    return {"reaperturas": len(reaperturas), "desgastes": len(desgastes)}


def revisar_acuerdos(estado: Estado, rng: random.Random) -> dict:
    """
    Un acuerdo vale mientras se cumpla, y cumplirlo significa no operar sobre lo
    pactado. Si se rompe, se rompe visiblemente:

      * la credibilidad de la mesa cae y el Comité endurece condiciones;
      * la movilización sube, porque el Gobierno prometió y no cumplió;
      * y los puntos pactados vuelven a cerrarse.
    """
    rotos, cumplidos = [], []
    for a in estado.acuerdos:
        if a.roto or a.cumplido:
            continue
        if estado.turno_decision < a.turno_limite:
            continue

        # ¿Se operó sobre algún punto pactado mientras el acuerdo estaba vigente?
        if a.motivo_ruptura:
            a.roto = True
            rotos.append(a)
        else:
            a.cumplido = True
            cumplidos.append(a)

    for a in rotos:
        from src.engine import mobilization
        for nid in a.nodos:
            n = estado.nodos.get(nid)
            if n and n.modo_apertura == "concertacion":
                n.caudal = 0.0
                n.modo_apertura = "cerrado"
        estado.reservas.aplicar(P.COSTO_RESERVAS["acuerdo_incumplido"])
        mobilization.registrar_evento(estado, "acuerdo_incumplido")
        estado.eventos_turno.append({
            "tipo": "acuerdo_roto", "acuerdo": a.acuerdo_id, "motivo": a.motivo_ruptura,
        })

    for a in cumplidos:
        from src.engine import mobilization
        estado.reservas.aplicar(P.COSTO_RESERVAS["acuerdo_verificable_cumplido"])
        mobilization.registrar_evento(estado, "acuerdo_verificable")
        estado.eventos_turno.append({"tipo": "acuerdo_cumplido", "acuerdo": a.acuerdo_id})

    return {"rotos": len(rotos), "cumplidos": len(cumplidos)}


def aperturas_netas(estado: Estado) -> int:
    """Aperturas − reaperturas. La métrica que resume el ejercicio."""
    ap = sum(1 for e in estado.eventos_turno if e.get("tipo") == "apertura")
    re = sum(1 for e in estado.eventos_turno if e.get("tipo") == "reapertura")
    return ap - re
