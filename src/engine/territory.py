"""
territory.py — La lectura pública del territorio.

El mapa proyectado dice seis cosas de cada punto y las mismas seis de cada
región. Este módulo es el único sitio donde se calculan.

    LA ARITMÉTICA DEL MAPA VIVE EN EL MOTOR, NO EN LA PANTALLA.

No es una preferencia de estilo. `PENDIENTES.md · B9` documenta el fallo que lo
justifica: una línea de la capa de presentación vació las vistas privadas y
las 163 pruebas pasaron enteras, porque **nada de lo que la interfaz calcula por
su cuenta está cubierto por una prueba.** Un promedio por región calculado en
JavaScript es un promedio que nadie verifica nunca. Aquí sí.

QUÉ SALE Y QUÉ NO
-----------------
Salen los seis hechos observables de un punto de cierre:

    caudal ............ cuánto pasa
    dureza ............ cuánto costaría abrirlo por la fuerza
    masa_presente ..... cuánta gente hay
    dias_sostenido .... desde cuándo
    apoyo_local ....... cuánto lo respalda el barrio
    control_voceria ... cuánto controla la vocería reconocida

NO sale `composicion_real`, ni por promedio, ni por diferencia, ni por la puerta
de atrás de una banda. Es la invariante de la capa pública y hay una prueba que
la vigila.

Y NINGUNO SALE COMO NÚMERO CRUDO
--------------------------------
Los cuatro que viven en [0,1] salen como banda —«duro», «vocería parcial»—; la
masa sale redondeada con un «≈» delante; los días son el único entero exacto,
porque contar días que lleva un bloqueo es un hecho de calendario que cualquiera
puede verificar y no un índice que se pueda optimizar. La misma frontera que
separa «Legitimidad: alta» de «Muertes evitables: 3» en el tablero.

Los cortes, en `parameters.py`. Aquí solo se aplican.

Y DOS LECTURAS MÁS, QUE NO SON DE GRADO SINO DE ACTO
----------------------------------------------------
Las seis de arriba describen CÓMO ESTÁ un punto. Faltaban las dos que describen
QUÉ SE ESTÁ HACIENDO CON ÉL, y sin ellas el mapa daba la misma forma y el mismo
color a un punto que acaba de recibir al ESMAD, a uno con mesa instalada y a uno
que nadie ha tocado en cinco jornadas:

    intervencion ...... fuerza · negociacion · ninguna
    mesa .............. si hay mesa instalada, y si ha sesionado HOY

Ninguna de las dos abre una puerta de atrás a la capa 1: que en un punto haya
mesa no dice nada de su mezcla real, y que se haya operado tampoco.
"""

from __future__ import annotations

import math

from src.engine import parameters as P
from src.engine.state import Estado, Nodo, Region


# ---------------------------------------------------------------------------
# La banda
# ---------------------------------------------------------------------------

def banda(valor: float, bandas: tuple) -> str:
    """
    El primer tramo cuyo tope alcanza al valor. **El tope entra en su tramo.**

    Que sea `<=` y no `<` no es un detalle de implementación: el motor decide que
    un punto está abierto con `caudal > 0,05`, así que un caudal de exactamente
    0,05 está cerrado. Con el tope exclusivo, ese punto salía rotulado «goteo» en
    el mapa y «cerrado» en su chip, y la sala se pone a discutir sobre la
    interfaz en vez de sobre el país.
    """
    for tope, palabra in bandas:
        if valor <= tope:
            return palabra
    return bandas[-1][1]


def peldano(valor: float, bandas: tuple) -> int:
    """El índice de la banda. La pantalla lo usa para el color y para la escala."""
    for i, (tope, _) in enumerate(bandas):
        if valor <= tope:
            return i
    return len(bandas) - 1


def aprox_personas(n: float) -> int:
    """
    Redondea una multitud a **dos cifras significativas**.

    337 se dice «unas 340»; 1.687, «unas 1.700». Nadie cuenta 337 personas en una
    glorieta, y el error de una estimación de aforo crece con el aforo: dos
    cifras significativas es exactamente eso —un error relativo constante, del 5 %
    en el peor caso— con una regla que se puede enunciar en una frase.

    **Redondear aquí es más honesto que la cifra exacta, no menos**: la cifra
    exacta afirmaría una precisión que ningún puesto de mando tiene sobre una
    calle. Por debajo de veinte se cuenta entero, porque ahí ya no es una
    multitud sino un grupo, y redondear treinta personas a cero sería mentir.
    """
    n = max(0, int(n))
    if n < P.MASA_SE_CUENTA_ENTERA:
        return n
    magnitud = 10 ** (math.floor(math.log10(n)) - (P.CIFRAS_MASA - 1))
    return int(round(n / magnitud) * magnitud)


# ---------------------------------------------------------------------------
# QUÉ SE ESTÁ HACIENDO EN UN PUNTO
# ---------------------------------------------------------------------------
#
# Tres estados, y el mapa tiene que decirlos sin que nadie los explique:
#
#     fuerza       se intervino a la fuerza — cedió o no cedió
#     negociacion  hay mesa instalada, o el punto está abierto porque se pactó
#     ninguna      no se está haciendo nada en absoluto
#
# NO ES `modo_apertura`, y confundirlos era el defecto. `modo_apertura` responde
# CÓMO SE ABRIÓ, así que de los puntos cerrados —que son la mayoría durante casi
# todo el ejercicio— no dice nada: un punto operado con ESMAD que no cedió y un
# punto que nadie ha tocado salían los dos como «cerrado», con la misma forma y
# el mismo color. Son dos conversaciones completamente distintas en la sala, y
# la pantalla las estaba dando por la misma.
#
# LA PRECEDENCIA, y por qué es esta:
#
#   1 · la fuerza empleada HOY manda sobre todo lo demás. Si esta jornada entró
#       el ESMAD en un punto donde había mesa, lo que la sala tiene que ver es
#       que entró el ESMAD.
#   2 · una mesa viva manda sobre una fuerza de hace tres jornadas: lo que se
#       está haciendo ahí ahora es negociar.
#   3 · un punto abierto lo dice su modo de apertura.
#   4 · y una fuerza empleada alguna vez, aunque no cediera, sigue siendo una
#       intervención a la fuerza. Es un hecho sobre el punto, no un estado que
#       caduque: la calle lo recuerda y el debriefing también.


def intervencion_nodo(nodo: Nodo, jornada: int) -> str:
    """
    `fuerza` · `negociacion` · `ninguna`. Ver la precedencia de arriba.

    `jornada` es la que la sala está VIVIENDO (`Estado.jornada_visible`), no la
    última resuelta. Mientras se delibera la jornada 2 el motor todavía va por
    la 1, y con `turno_decision` una operación de ayer seguía leyéndose como
    «hoy» durante los trece minutos de hoy.
    """
    if nodo.intervencion_fuerza_turno == jornada:
        return "fuerza"
    if nodo.mesa_abierta:
        return "negociacion"
    if nodo.modo_apertura == "concertacion":
        return "negociacion"
    if nodo.modo_apertura == "fuerza":
        return "fuerza"
    if nodo.intervencion_fuerza_turno is not None:
        return "fuerza"
    return "ninguna"


def mesa_nodo(nodo: Nodo, jornada: int) -> dict | None:
    """
    La mesa de este punto, o `None` si no hay ninguna instalada.

    **`sesionada_hoy` es el dato que faltaba.** Una mesa instalada y una mesa
    instalada HOY no son la misma cosa: la primera existe, la segunda avanza. Sin
    esta distinción proyectada, una sala podía instalar una mesa la jornada 1 y
    dar por hecho que seguía trabajando sola hasta la 5 — que es exactamente lo
    que no pasa.

    `jornada` es la que la sala está VIVIENDO. Con la última resuelta, la mesa
    que sesionó ayer seguía diciendo «instalada hoy» durante toda la
    deliberación de hoy, y la pregunta del comienzo del día no aparecía nunca.
    """
    if not nodo.mesa_abierta:
        return None
    return {
        "instalada": True,
        "sesionada_hoy": nodo.mesa_sesion_turno == jornada,
        "ultima_sesion": nodo.mesa_sesion_turno,
        "jornadas_congelada": nodo.jornadas_mesa_congelada,
        # Cuánto le falta, EN PALABRAS. «1 de 2 sesiones» sería la cifra interna
        # del motor puesta en la pared, y con ella la sala cuenta sesiones en vez
        # de decidir dónde instalar mesa.
        "avance": ("a punto de rendir" if nodo.turnos_en_negociacion
                   >= P.TURNOS_APERTURA["concertacion"] - 1 else "recién instalada"),
        "congelada": (nodo.mesa_sesion_turno != jornada
                      and nodo.jornadas_mesa_congelada > 0),
    }


# ---------------------------------------------------------------------------
# Un punto
# ---------------------------------------------------------------------------

def lectura_nodo(nodo: Nodo) -> dict:
    """
    Las seis lecturas de un punto de cierre, tal como se proyectan.

    Cada una lleva su `banda` (la palabra), su `peldano` (para el color y la
    escala de la pantalla) y, cuando la cifra es un hecho de calendario o de
    aforo, su valor aproximado. **Nunca el número interno.**
    """
    return {
        "caudal": {
            "banda": banda(nodo.caudal, P.BANDAS_CAUDAL),
            "peldano": peldano(nodo.caudal, P.BANDAS_CAUDAL),
            "de": len(P.BANDAS_CAUDAL),
            "sentido": "arriba_mejor",
        },
        "dureza": {
            "banda": banda(nodo.dureza, P.BANDAS_DUREZA),
            "peldano": peldano(nodo.dureza, P.BANDAS_DUREZA),
            "de": len(P.BANDAS_DUREZA),
            "sentido": "arriba_peor",
        },
        "masa_presente": {
            "banda": banda(nodo.masa_presente, P.BANDAS_MASA),
            "peldano": peldano(nodo.masa_presente, P.BANDAS_MASA),
            "de": len(P.BANDAS_MASA),
            "aprox": aprox_personas(nodo.masa_presente),
            "sentido": "arriba_peor",
        },
        "dias_sostenido": {
            "banda": banda(nodo.dias_sostenido, P.BANDAS_DIAS_SOSTENIDO),
            "peldano": peldano(nodo.dias_sostenido, P.BANDAS_DIAS_SOSTENIDO),
            "de": len(P.BANDAS_DIAS_SOSTENIDO),
            # EL ÚNICO ENTERO EXACTO. Los días que lleva un bloqueo son de
            # calendario: los sabe el barrio, los sabe la prensa y no hay nada
            # que optimizar sobre ellos.
            "dias": int(nodo.dias_sostenido),
            "sentido": "arriba_peor",
        },
        "apoyo_local": {
            "banda": banda(nodo.apoyo_local, P.BANDAS_APOYO),
            "peldano": peldano(nodo.apoyo_local, P.BANDAS_APOYO),
            "de": len(P.BANDAS_APOYO),
            "sentido": "arriba_peor",
        },
        "control_voceria": {
            "banda": banda(nodo.control_voceria, P.BANDAS_VOCERIA),
            "peldano": peldano(nodo.control_voceria, P.BANDAS_VOCERIA),
            "de": len(P.BANDAS_VOCERIA),
            "sentido": "arriba_mejor",
            # `constatado` SE RETIRÓ. Comparaba `verificado_por` con
            # «dupla_defensoria», un valor que **nadie escribe desde que salió la
            # Defensoría del Pueblo**: las cuatro fuentes que marcan un punto
            # ponen «equipo_terreno», «parte_municipal», «inteligencia_defensa» o
            # «mapa_transporte». Salía `false` siempre, en el mapa y en las
            # vistas, y un dato que siempre dice lo mismo no dice nada.
            #
            # Quién miró y cuándo sigue estando, y ahí sí es verdad: el punto
            # lleva `verificado_por` y `ultima_verificacion_turno`, y el tablero
            # los sirve en `verificado_turno`.
        },
    }


# ---------------------------------------------------------------------------
# Una región
# ---------------------------------------------------------------------------

def lectura_region(region: Region, nodos: list[Nodo],
                   jornada: int = 0) -> dict:
    """
    Las mismas seis, promediadas sobre los puntos modelados de la región.

    ### El promedio es simple, y hay que decirlo

    Media aritmética sin ponderar: **cada punto modelado cuenta uno.** Podría
    ponderarse por masa presente —un bloqueo de mil pesa más que uno de cien— y
    sería defendible, pero entonces la cifra de la pantalla dejaría de ser
    comprobable a ojo por quien la lee, y una cifra proyectada que nadie puede
    reconstruir es una autoridad prestada. Se prefiere la que se puede rehacer
    mentalmente.

    ### Salvo la masa, donde la suma ES la magnitud

    «Un promedio de 340 personas por punto» no es lo que un puesto de mando
    necesita saber; «unas 2.000 personas en la calle en esta región» sí. Se dan
    las dos: `aprox` es el total y `aprox_por_punto` el promedio.

    ### Y la región cuenta lo que el promedio esconde

    Un promedio de caudal 0,5 puede ser dos puntos a la mitad o uno abierto y
    otro cerrado, y no son la misma región. Por eso va aparte `cerrados` — el
    recuento de puntos que no dejan pasar nada — y de ahí sale el estado de
    bloqueo que colorea el mapa.
    """
    n = len(nodos)
    if n == 0:
        # Una región sin puntos modelados no es una región en calma: es una
        # región de la que este ejercicio no modela ningún cierre. Decirlo así
        # evita que la pantalla la pinte verde y afirme algo que no sabe.
        return {"puntos": 0, "sin_puntos_modelados": True}

    def media(f) -> float:
        return sum(f(x) for x in nodos) / n

    cerrados = sum(1 for x in nodos if not x.abierto)
    fraccion_cerrada = cerrados / n

    masa_total = sum(x.masa_presente for x in nodos)

    # QUÉ SE ESTÁ HACIENDO EN ESTA REGIÓN, contado. Un promedio de caudal no lo
    # dice: cuatro puntos cerrados sobre los que nadie hace nada y cuatro puntos
    # cerrados con mesa instalada dan exactamente el mismo promedio, y son dos
    # regiones distintas.
    intervencion = {"fuerza": 0, "negociacion": 0, "ninguna": 0}
    for x in nodos:
        intervencion[intervencion_nodo(x, jornada)] += 1
    con_mesa = [x for x in nodos if x.mesa_abierta]

    return {
        "puntos": n,
        "cerrados": cerrados,
        "intervencion": intervencion,
        "mesas": {
            "instaladas": len(con_mesa),
            "sesionadas_hoy": sum(1 for x in con_mesa
                                  if x.mesa_sesion_turno == jornada),
            "congeladas": sum(1 for x in con_mesa
                              if x.mesa_sesion_turno != jornada
                              and x.jornadas_mesa_congelada > 0),
        },
        "bloqueo": {
            "banda": banda(fraccion_cerrada, P.BANDAS_BLOQUEO),
            "peldano": peldano(fraccion_cerrada, P.BANDAS_BLOQUEO),
            "de": len(P.BANDAS_BLOQUEO),
            "cerrados": cerrados,
            "puntos": n,
        },
        "caudal": {
            "banda": banda(media(lambda x: x.caudal), P.BANDAS_CAUDAL),
            "peldano": peldano(media(lambda x: x.caudal), P.BANDAS_CAUDAL),
            "de": len(P.BANDAS_CAUDAL),
            "sentido": "arriba_mejor",
        },
        "dureza": {
            "banda": banda(media(lambda x: x.dureza), P.BANDAS_DUREZA),
            "peldano": peldano(media(lambda x: x.dureza), P.BANDAS_DUREZA),
            "de": len(P.BANDAS_DUREZA),
            "sentido": "arriba_peor",
        },
        "masa_presente": {
            "banda": banda(masa_total / n, P.BANDAS_MASA),
            "peldano": peldano(masa_total / n, P.BANDAS_MASA),
            "de": len(P.BANDAS_MASA),
            "aprox": aprox_personas(masa_total),
            "aprox_por_punto": aprox_personas(masa_total / n),
            "sentido": "arriba_peor",
        },
        "dias_sostenido": {
            "banda": banda(media(lambda x: x.dias_sostenido), P.BANDAS_DIAS_SOSTENIDO),
            "peldano": peldano(media(lambda x: x.dias_sostenido),
                               P.BANDAS_DIAS_SOSTENIDO),
            "de": len(P.BANDAS_DIAS_SOSTENIDO),
            "dias": round(media(lambda x: x.dias_sostenido)),
            # El más antiguo, además del promedio: es el que fija el relato
            # público de la región —«llevan quince días»— y un promedio lo
            # diluye justo cuando más dice.
            "dias_max": max(x.dias_sostenido for x in nodos),
            "sentido": "arriba_peor",
        },
        "apoyo_local": {
            "banda": banda(media(lambda x: x.apoyo_local), P.BANDAS_APOYO),
            "peldano": peldano(media(lambda x: x.apoyo_local), P.BANDAS_APOYO),
            "de": len(P.BANDAS_APOYO),
            "sentido": "arriba_peor",
        },
        "control_voceria": {
            "banda": banda(media(lambda x: x.control_voceria), P.BANDAS_VOCERIA),
            "peldano": peldano(media(lambda x: x.control_voceria), P.BANDAS_VOCERIA),
            "de": len(P.BANDAS_VOCERIA),
            "sentido": "arriba_mejor",
        },
    }


def lecturas_por_region(estado: Estado) -> dict[str, dict]:
    return {
        r.region_id: lectura_region(
            r, [n for n in estado.nodos.values() if n.region_id == r.region_id],
            estado.jornada_visible)
        for r in estado.regiones.values()
    }


# ---------------------------------------------------------------------------
# LAS MESAS INSTALADAS
# ---------------------------------------------------------------------------

def mesas_instaladas(estado: Estado, region_id: str | None = None) -> list[dict]:
    """
    Dónde hay mesa hoy, y cuáles siguen sin sesionar en esta jornada.

    Es la fuente de la pregunta que reciben el Ministro del Interior y el
    Alcalde al abrir el día (`views.py`). Se calcula aquí y no en la vista
    porque la usan tres sitios —las dos vistas y el tablero— y un recuento en
    tres sitios se desincroniza.

    **Ordenadas por lo que apremia**: primero las que llevan más jornadas
    congeladas, y a igualdad, las que están más cerca de rendir.
    """
    fuera = []
    for n in estado.nodos.values():
        if not n.mesa_abierta:
            continue
        if region_id is not None and n.region_id != region_id:
            continue
        m = mesa_nodo(n, estado.jornada_visible)
        if m is None:
            continue
        fuera.append({
            "nodo_id": n.nodo_id,
            "punto": n.nombre,
            "region_id": n.region_id,
            "epicentro": n.region_id == estado.region_epicentro,
            **m,
        })
    return sorted(fuera, key=lambda x: (-x["jornadas_congelada"],
                                        x["sesionada_hoy"]))


def mesas_sin_sesionar(estado: Estado, region_id: str | None = None) -> list[dict]:
    """Las que hoy todavía no han sesionado. Son las que se van a congelar."""
    return [m for m in mesas_instaladas(estado, region_id)
            if not m["sesionada_hoy"]]


# ---------------------------------------------------------------------------
# La geometría — el guardarraíl que impide que el mapa mienta
# ---------------------------------------------------------------------------
#
# El mapa dejó de ser un esquema de líneas y pasó a ser un país con sus costas y
# sus regiones dibujadas. Eso trae una obligación que el esquema no tenía:
#
#     un punto de la región de Bellaflor tiene que caer DENTRO de Bellaflor.
#
# No es cosmético. Si un punto cae fuera de su polígono, el mapa afirma en una
# pared que ese bloqueo está en otra región — y el reparto territorial es
# exactamente lo que la sala está mirando ahí. Peor: el motor genera cierres
# nuevos por su cuenta (`mobilization._generar_nodo`), así que la comprobación
# no puede ser «lo revisó alguien al dibujarlo».
#
#     Una regla que el software garantiza vale más que una que el software
#     recomienda.
#
# El loader la exige sobre el escenario, y la movilización la usa para colocar
# los cierres nuevos.


def dentro(x: float, y: float, poligono: list[list[float]]) -> bool:
    """Lanzamiento de rayo. `poligono` es una lista de pares [x, y] cerrada o no."""
    dentro_ = False
    n = len(poligono)
    for i in range(n):
        x1, y1 = poligono[i]
        x2, y2 = poligono[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            corte = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < corte:
                dentro_ = not dentro_
    return dentro_


def centroide(poligono: list[list[float]]) -> tuple[float, float]:
    return (sum(p[0] for p in poligono) / len(poligono),
            sum(p[1] for p in poligono) / len(poligono))


def caja(poligono: list[list[float]]) -> tuple[float, float, float, float]:
    """`(x, y, ancho, alto)`. Es lo que la pantalla necesita para hacer zoom."""
    xs = [p[0] for p in poligono]
    ys = [p[1] for p in poligono]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
