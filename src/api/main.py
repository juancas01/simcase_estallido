"""
main.py — API del ejercicio.

Sirve las tres clases de superficie del montaje v2 y nada más. Deliberadamente
delgada: toda la lógica vive en `src/engine`, que no sabe que esta capa existe.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

LAS SUPERFICIES
---------------
    /api/tablero          el TABLERO GENERAL, proyectado para toda la sala
    /api/vista/{rol}      la VISTA PRIVADA de un rol, en su propio dispositivo
    /api/esfera           la ESFERA PÚBLICA, proyectada junto al tablero
    /api/consola/*        la CONSOLA, donde se transcriben las órdenes

NO HAY MODERADOR COMO FIGURA APARTE. La consola es una superficie más y quien la
opera —puede ser uno de los nueve— solo transcribe: no conduce, no reparte
información, no decide el ritmo y no sabe nada que los demás no sepan.
"""

from __future__ import annotations

import argparse
import asyncio
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.agents import entorno, nlu
from src.agents.config import config as cfg_llm
from src.engine import parameters as P
from src.engine import views
from src.engine.actions import catalogo_por_rol
from src.engine.loader import cargar_estado, catalogo_para_agente
from src.engine.simulation import MotorCrisis

app = FastAPI(title="SIMCASE · Estallido Social")

# --- estado global del ejercicio -------------------------------------------
_estado = cargar_estado()
motor = MotorCrisis(_estado)

# ---------------------------------------------------------------------------
# EL RELOJ DE SALA — dos mitades por jornada, y solo dos
#
# La jornada dura quince minutos de mundo real y se parte en dos tramos con
# reglas OPUESTAS:
#
#     DÍA    13 min   se leen los tableros, se discute y SE ORDENA. En cualquier
#                     momento: no hay que esperar a que llegue el turno de las
#                     órdenes, porque ya no existe tal turno.
#     NOCHE   2 min   el motor resolvió. Se miran las consecuencias y se
#                     interpretan. NO SE RECIBEN ÓRDENES.
#
# HABÍA SIETE FASES Y AHORA HAY DOS. Las siete describían bien la coreografía de
# una sala ideal y mal la de una sala real: obligaban a saber en qué minuto se
# estaba antes de poder decir nada, y la única frontera que cambia lo que se
# puede hacer —¿se ordena o no se ordena?— quedaba escondida entre otras seis.
#
# Y ESA FRONTERA LA GARANTIZA EL SERVIDOR, no un rótulo. De noche la consola se
# apaga sola y lo que llegue igualmente se rechaza con un 409. Una regla que el
# software garantiza vale más que una que el software recomienda.
#
# VIVE AQUÍ Y NO EN EL NAVEGADOR, y no es un detalle de implementación: hay diez
# pantallas mirando a la vez —el tablero, la consola y las siete vistas—, y un
# cronómetro por pantalla es un cronómetro distinto por pantalla en cuanto una se
# recarga. El servidor guarda TRES INSTANTES y cada superficie deriva de ellos lo
# que muestra:
#
#     sesion_desde    cuándo se pulsó «Iniciar». Solo se corre al reanudar.
#     jornada_desde   cuándo empezó el día de la jornada en curso.
#     pausa_desde     desde cuándo está detenido el reloj, o None.
#
# Las transiciones —resolver el día, abrir el siguiente— las dispara
# `_sincronizar()`, y solo él. La tabla de fases se sirve a las pantallas en cada
# respuesta: la interfaz tuvo su propia copia, y un dato en dos sitios se
# desincroniza.
# ---------------------------------------------------------------------------

# `guia` es qué debería estar pasando en la sala mientras corre ese tramo. Viaja
# con la tabla hasta la consola, de modo que quien la opera no tiene que
# acordarse.
FASES_TURNO = (
    {"id": "dia", "nombre": "Día", "minutos": P.MIN_DIA, "admite_ordenes": True,
     "guia": "Se leen los tableros y se delibera. La consola acepta órdenes en "
             "cualquier momento de estos minutos: se pueden dictar de una en "
             "una y se acumulan hasta que caiga la noche."},
    {"id": "noche", "nombre": "Noche", "minutos": P.MIN_NOCHE,
     "admite_ordenes": False,
     "guia": "El motor ya resolvió. Se miran las consecuencias y se interpretan. "
             "No se reciben órdenes: la consola está apagada."},
)

FASES = tuple(f["id"] for f in FASES_TURNO)

# Si alguien cambia un tramo sin cambiar el presupuesto, esto lo dice en el
# arranque y no en mitad de la sala.
assert abs(sum(f["minutos"] for f in FASES_TURNO) - P.MIN_JORNADA) < 1e-9

SEGUNDOS_DIA = P.MIN_DIA * 60.0
SEGUNDOS_JORNADA = P.MIN_JORNADA * 60.0

# Cuántos planes sin ejecutar se guardan. Con trece minutos de día, más de un
# puñado significa que algo se quedó a medias.
PLANES_EN_MEMORIA = 8

# Contador MONOTÓNICO de planes. Antes el identificador salía de
# `len(sala["planes"]) + 1`, y `ejecutar` saca el plan del diccionario: con dos
# planes abiertos, ejecutar el primero hacía que el siguiente `interpretar`
# reutilizara un identificador vivo y sobrescribiera aquel plan sin avisar.
_planes_emitidos = 0

# UN SOLO CERROJO PARA TODO LO QUE MUEVE EL MUNDO.
#
# Los endpoints de FastAPI declarados con `def` corren en un pool de hilos, y
# encima hay un latido de fondo que también dispara transiciones. Sin esto, dos
# pantallas consultando el tablero en el segundo en que expira el día podían
# resolver la jornada DOS VECES, y nadie se enteraría hasta ver dos noches
# seguidas en el historial.
_cerrojo = threading.RLock()

sala = {
    # La fase de reserva: la que rige mientras el reloj no corre. En cuanto
    # alguien pulsa «Iniciar» manda la fase calculada, y esta deja de leerse.
    "fase": "dia",
    # Los tres instantes del reloj de sala. Todos `None` = sin empezar.
    "reloj": {"sesion_desde": None, "jornada_desde": None, "pausa_desde": None},
    # Se levanta al resolver la última jornada. A partir de ahí no se abre otra.
    "cerrado": False,
    "planes": {},
    "esfera": {"publicaciones": [], "generado_por": "aún no hay hechos"},
    # Lo que produjo el último cierre de jornada, para que la consola lo enseñe
    # durante los dos minutos de noche sin que nadie tenga que pedirlo.
    "consecuencias": None,
}


def _fase_de(fase_id: str) -> dict:
    for f in FASES_TURNO:
        if f["id"] == fase_id:
            return f
    return FASES_TURNO[0]


def _transcurrido(ahora: float | None = None) -> float | None:
    """
    Segundos de jornada corridos, descontando lo que estuvo en pausa.

    Devuelve `None` si el reloj no ha empezado, que es lo que permite montar y
    depurar sin cronometrar nada.
    """
    r = sala["reloj"]
    if r["jornada_desde"] is None:
        return None
    fin = r["pausa_desde"] if r["pausa_desde"] is not None else (
        time.time() if ahora is None else ahora)
    return max(0.0, fin - r["jornada_desde"])


def _admite_ordenes() -> bool:
    return bool(_fase_de(sala["fase"])["admite_ordenes"]) and not sala["cerrado"]


def _exigir_ventana_de_ordenes() -> None:
    """
    De noche no se ordena, y no es un rótulo: es un 409.

    Con el reloj parado no se exige nada — un montaje que nunca pulse «Iniciar»
    se comporta como antes, y así se puede probar el canal sin cronometrar.
    """
    if sala["reloj"]["jornada_desde"] is None:
        return
    if sala["cerrado"]:
        raise HTTPException(409, (
            "El ejercicio terminó. Lo que queda es la proyección y el "
            "debriefing, no más órdenes."))
    if not _admite_ordenes():
        raise HTTPException(409, (
            "Es de noche: las consecuencias ya están resueltas y no se reciben "
            "órdenes. La consola vuelve a abrir con la jornada siguiente."))


# ---------------------------------------------------------------------------
# LAS DOS BISAGRAS
# ---------------------------------------------------------------------------

def _abrir_jornada() -> dict:
    """Empieza el día de la jornada siguiente. **No avanza el mundo.**"""
    with _cerrojo:
        if sala["cerrado"]:
            return _cronometro()
        _reanudar_si_estaba_en_pausa()
        motor.abrir_jornada()
        sala["fase"] = "dia"
        sala["consecuencias"] = None
        ahora = time.time()
        if sala["reloj"]["sesion_desde"] is None:
            sala["reloj"]["sesion_desde"] = ahora
        sala["reloj"]["jornada_desde"] = ahora
        return _cronometro()


def _cerrar_jornada() -> dict:
    """
    Resuelve el día con lo que la mesa dejó en cola, pasa la noche y planta el
    reloj al comienzo de los dos minutos de consecuencias.

    **Solo hacia adelante.** Si la jornada se cierra porque se agotó el tiempo,
    el reloj ya está dentro de la noche y no se rebobina; si se cierra a mano
    antes de tiempo, la noche empieza ahora.
    """
    with _cerrojo:
        pasos = motor.cerrar_jornada()
        eventos = [ev for pa in pasos for ev in pa.eventos]
        _refrescar_esfera(eventos)

        sala["fase"] = "noche"
        r = sala["reloj"]
        if r["jornada_desde"] is not None:
            _reanudar_si_estaba_en_pausa()
            r["jornada_desde"] = min(r["jornada_desde"],
                                     time.time() - SEGUNDOS_DIA)

        dia = pasos[0]
        sala["consecuencias"] = {
            "jornada": dia.turno,
            "resumen": dia.resumen,
            "resultados": [{"accion": n, "ok": x.ok, "mensaje": x.mensaje,
                            "datos": x.datos}
                           for n, x in dia.resultados],
            "eventos": eventos,
            "umbrales": dia.umbrales_cruzados,
            "ultima": _estado.turno_decision >= P.TURNOS_DECISION,
        }
        if _estado.turno_decision >= P.TURNOS_DECISION:
            sala["cerrado"] = True
        return sala["consecuencias"]


def _reanudar_si_estaba_en_pausa() -> None:
    """
    Mover el mundo reanuda el reloj.

    Dejarlo detenido mientras el ejercicio avanza sería un cronómetro que
    miente, y el cronómetro es lo único que las diez pantallas comparten.
    """
    r = sala["reloj"]
    if r["pausa_desde"] is None:
        return
    detenido = time.time() - r["pausa_desde"]
    for k in ("sesion_desde", "jornada_desde"):
        if r[k] is not None:
            r[k] += detenido
    r["pausa_desde"] = None


def _sincronizar() -> None:
    """
    Lleva el mundo al punto donde el reloj dice que está.

    Lo llama el latido de fondo cada segundo y, por si el latido faltara,
    también cada lectura del tablero. Es idempotente: dos llamadas en el mismo
    instante hacen exactamente una transición, porque el cerrojo las serializa y
    la condición mira `sala["fase"]`, que la primera ya cambió.
    """
    with _cerrojo:
        t = _transcurrido()
        if t is None:
            return
        if sala["fase"] == "dia" and t >= SEGUNDOS_DIA:
            _cerrar_jornada()
        elif (sala["fase"] == "noche" and t >= SEGUNDOS_JORNADA
                and not sala["cerrado"]):
            _abrir_jornada()


async def _latido() -> None:
    """
    Un segundo. Es lo que hace que la consola se apague sola en el minuto trece
    aunque en ese momento no haya ninguna pantalla preguntando.
    """
    while True:
        try:
            await asyncio.sleep(1.0)
            _sincronizar()
        except asyncio.CancelledError:
            raise
        except Exception:      # un latido roto no puede tumbar el servidor
            pass


@asynccontextmanager
async def _ciclo_de_vida(_app: FastAPI):
    tarea = asyncio.create_task(_latido())
    try:
        yield
    finally:
        tarea.cancel()


app.router.lifespan_context = _ciclo_de_vida


def _cronometro() -> dict:
    """
    Lo que necesita una pantalla para dibujar el cronómetro **sin preguntar dos
    veces**: los tres instantes, la tabla de fases y el reloj del servidor.

    `ahora` es la pieza que las mantiene de acuerdo. Cada superficie compara su
    reloj con este y guarda el desfase, así que las diez cuentan sobre el mismo
    instante aunque los relojes de sus máquinas no coincidan — y siguen contando
    entre respuesta y respuesta, sin esperar a la siguiente.
    """
    r = sala["reloj"]
    return {
        "corriendo": r["jornada_desde"] is not None,
        "pausado": r["pausa_desde"] is not None,
        "cerrado": sala["cerrado"],
        "ahora": time.time(),
        "sesion_desde": r["sesion_desde"],
        "jornada_desde": r["jornada_desde"],
        "pausa_desde": r["pausa_desde"],
        "fase": sala["fase"],
        "admite_ordenes": _admite_ordenes(),
        "jornada": _estado.jornada_visible,
        "jornadas_totales": P.TURNOS_DECISION,
        "fases": [dict(f) for f in FASES_TURNO],
    }


# ===========================================================================
# Superficie 1 · El tablero general
# ===========================================================================

@app.get("/api/tablero")
def tablero():
    """
    Lo que ve toda la sala. Responde QUÉ ESTÁ PASANDO, en grano grueso.

    `vista_publica()` no serializa la mezcla real de ningún punto ni la veracidad
    de ninguna denuncia. Es la invariante más importante de esta capa: si eso se
    filtrara, el dilema central del caso desaparecería.
    """
    # Red de seguridad del latido: si por lo que sea no estuviera corriendo, el
    # mundo avanza igual en cuanto alguien mira el tablero.
    _sincronizar()
    d = _estado.vista_publica()
    d["cronometro"] = _cronometro()
    # Lo que la mesa ya confirmó y todavía no se ha resuelto. La consola lo lee
    # de aquí, así que sobrevive a que alguien recargue la pantalla.
    d["en_cola"] = len(motor.cola_inmediata)
    d["fase"] = d["cronometro"]["fase"]
    d["admite_ordenes"] = d["cronometro"]["admite_ordenes"]
    # Lo que produjo el último cierre de jornada. Va aquí y no solo en la
    # consola porque los dos minutos de noche son para leerlo.
    d["consecuencias"] = sala["consecuencias"]
    d["registro"] = [asdict(x) for x in _estado.registro[-12:]]
    # Qué se movió desde la última vez que la sala miró. Un delta no revela nada
    # que el valor actual no revelara ya: se calcula sobre las mismas magnitudes
    # que `vista_publica()` serializa, ni una más.
    d["deltas"] = motor.deltas()
    # Qué le pasó a cada punto en la última ventana. Solo hechos públicos y
    # ya ocurridos: nunca dónde está la fuerza ahora, que es de la Policía.
    d["hechos"] = motor.hechos_por_punto()
    return d


# ===========================================================================
# Superficie 2 · Las siete vistas privadas
# ===========================================================================

@app.get("/api/vista/{rol}")
def vista_privada(rol: str):
    """
    La cartera de un rol en alta resolución. Es **personal, no confidencial**: el
    sistema solo se la muestra a su titular, pero nadie está obligado a
    callársela y el ejercicio quiere que se comparta.

    Lo que la hace valiosa no es que esté oculta — es que hay una sola persona
    que la tiene actualizada. Y el detalle **no migra al tablero**: aunque se diga
    en voz alta, el número sigue viviendo aquí, así que cada turno el rol vuelve
    a ser necesario.
    """
    try:
        v = views.vista(_estado, rol)
    except KeyError:
        raise HTTPException(404, f"Rol desconocido: {rol}. Los siete son {views.ROLES}")
    v["cronometro"] = _cronometro()
    v["admite_ordenes"] = v["cronometro"]["admite_ordenes"]
    # EL REPERTORIO VIENE CON SU SEMÁFORO. Cada acción dice si se puede pedir
    # AHORA y, si no, qué falta — en general y sin nombrar el remedio concreto.
    # Sin eso, la vista enumeraba cinco acciones de las que dos llevaban tres
    # turnos bloqueadas y su titular no tenía forma de saberlo hasta que la
    # consola le devolvía un rechazo delante de la mesa.
    v["acciones"] = catalogo_por_rol(_estado).get(rol, [])
    return v


@app.get("/api/vistas")
def todas_las_vistas():
    """Solo para revisar el contenido al montar. No es una superficie del ejercicio."""
    return views.todas(_estado)


# ===========================================================================
# Superficie 3 · La esfera pública
# ===========================================================================

@app.get("/api/esfera")
def esfera_publica():
    """
    Lo que se dice. La distancia con el tablero es el caso, y solo se percibe si
    las dos se ven a la vez.

    Las publicaciones las produce la CAPA 3 —los seis agentes de entorno— que
    generan **contenido y solo contenido**: reaccionan a lo que el motor ya
    calculó y lo narran desde su sesgo. Nunca deciden nada.

    Sin llave de API, degradan a plantilla y el campo `generado_por` lo dice.
    """
    return {
        "encuadre_dominante": _estado.encuadre_dominante,
        "respaldo_internacional": round(_estado.reservas.respaldo_internacional, 1),
        "posicion_gremios": _estado.posicion_gremios,
        "comite_disponible": _estado.comite_disponible,
        "denuncias": [d.vista_publica() for d in _estado.denuncias],
        **sala["esfera"],
    }


def _refrescar_esfera(eventos: list[dict]) -> None:
    """Se llama después de cada paso, con los hechos que el motor produjo."""
    previas = [p["texto"] for p in sala["esfera"].get("publicaciones", [])][-4:]
    nuevas = entorno.publicaciones(_estado, eventos, previas)
    sala["esfera"] = {
        "publicaciones": (nuevas["publicaciones"] +
                          sala["esfera"].get("publicaciones", []))[:20],
        "generado_por": nuevas["generado_por"],
    }


# ===========================================================================
# Superficie 4 · La consola
# ===========================================================================

class TextoOrden(BaseModel):
    texto: str


@app.post("/api/consola/interpretar")
def interpretar(orden: TextoOrden):
    """
    CAPA 4 · traduce lo que la sala dijo a un plan tipado, y lo devuelve **para
    que la sala lo lea junta antes de ejecutarlo**.

    Ese momento no es un trámite: es el mejor punto pedagógico del montaje. La
    sala oye su propia decisión reformulada, con su riesgo, y con frecuencia la
    cambia.

        El LLM traduce. El motor decide, valida, ejecuta y reporta.

    El modelo solo hace el primer paso —texto a llamadas de herramienta—. La
    resolución de entidades, la validación y la banda de riesgo son
    deterministas, y el texto que se lee en voz alta también.
    """
    _exigir_ventana_de_ordenes()
    global _planes_emitidos
    _planes_emitidos += 1
    plan_id = f"plan-{_planes_emitidos}"
    plan = nlu.interpretar(_estado, orden.texto, plan_id)

    # Los planes que nadie ejecutó no se acumulan toda la sesión.
    for viejo in list(sala["planes"])[:-PLANES_EN_MEMORIA]:
        sala["planes"].pop(viejo, None)
    sala["planes"][plan_id] = plan
    return plan.a_dict()


class Eleccion(BaseModel):
    plan_id: str
    indice: int
    campo: str
    valor: str


@app.post("/api/consola/elegir")
def elegir(e: Eleccion):
    """
    Resolver una ambigüedad **con una elección tipada, no con texto libre**.

    Sin esto aparecen las ejecuciones fantasma: la respuesta corta a una
    repregunta —«no», «400», «sí, confirmo»— entra de nuevo por el canal como si
    fuera una orden nueva. En la simulación anterior esas tres palabras
    produjeron cada una una evacuación.
    """
    plan = sala["planes"].get(e.plan_id)
    if plan is None:
        raise HTTPException(404, "Ese plan ya se consumió o no existe.")
    if not (0 <= e.indice < len(plan.acciones)):
        raise HTTPException(400, "No existe esa acción en el plan.")

    accion = plan.acciones[e.indice]
    spec = nlu.herramientas.HERRAMIENTAS.get(accion.herramienta, {})
    # Las elecciones solo pueden tocar campos DECLARADOS, o la reanudación sería
    # una vía para inyectar argumentos arbitrarios.
    if e.campo not in spec.get("esquema", {}):
        raise HTTPException(400, f"Campo no declarado: {e.campo}")

    # LOS CAMPOS DE LISTA SE COMPLETAN, NO SE SUSTITUYEN. `asignar_duplas` lleva
    # tres puntos en un solo acto: si el tercero no se resolvió, elegirlo tenía
    # que añadirlo a los dos que sí, no borrarlos. Con la asignación plana, la
    # pantalla mandaba un texto donde el motor espera una lista y el botón de
    # corregir dejaba la orden peor que antes.
    if e.campo in spec.get("entidades_lista", {}):
        actuales = list(accion.argumentos.get(e.campo) or [])
        if e.valor not in actuales:
            actuales.append(e.valor)
        accion.argumentos[e.campo] = actuales
    else:
        accion.argumentos[e.campo] = e.valor

    plan.acciones[e.indice] = nlu._a_accion_plan(
        _estado, {"nombre": accion.herramienta, "argumentos": accion.argumentos})
    return plan.a_dict()


class Confirmacion(BaseModel):
    plan_id: str


@app.post("/api/consola/ejecutar")
def ejecutar(c: Confirmacion):
    """
    Ejecuta el plan y **reporta después**, desde resultados reales.

    Ninguna frase que la sala lea sobre el resultado de una orden puede haber
    sido escrita antes de que la orden se ejecutara. Es el primero de los ocho
    modos de falla, y el más difícil de detectar.
    """
    _exigir_ventana_de_ordenes()
    plan = _sacar_plan(c.plan_id)
    if _solo_consultas(plan):
        return _respuesta_consulta()

    encoladas, omitidas = _encolar_plan(plan)
    return _resolver_turno(encoladas, omitidas)


# ---------------------------------------------------------------------------
# ENCOLAR Y RESOLVER SON DOS COSAS, Y ANTES ERAN UNA
#
# `/ejecutar` metía las acciones en la cola del motor y daba el paso del turno
# en la misma llamada. De ahí salían dos cosas incómodas:
#
#   1 · varias órdenes en un turno solo cabían **en un mismo texto**. Dictar una,
#       ejecutar, dictar otra y ejecutar gastaba DOS de las cinco ventanas del
#       ejercicio, y nadie avisaba.
#   2 · confirmar la primera orden cortaba en seco los 2,5 minutos de la fase de
#       órdenes, porque el reloj se plantaba en las consecuencias.
#
# Ahora hay dos verbos. `/encolar` acumula y no gasta turno —la mesa puede ir de
# una en una durante toda la fase— y `/resolver` da el paso con lo que haya.
# `/ejecutar` se queda como los dos seguidos, que es lo que hace falta cuando la
# orden viene entera en una sola frase.
# ---------------------------------------------------------------------------

def _sacar_plan(plan_id: str):
    plan = sala["planes"].pop(plan_id, None)
    if plan is None:
        raise HTTPException(404, "Ese plan ya se consumió o no existe.")
    return plan


def _solo_consultas(plan) -> bool:
    """
    PREGUNTAR NO GASTA UN TURNO. Un plan que solo tiene consultas corría
    `motor.paso()` igual: la sala preguntaba cuánto oxígeno quedaba, pulsaba el
    botón grande, y se le iba una de las cinco ventanas del ejercicio. La hoja
    de datos ya viaja dentro del plan y se lee sin ejecutar nada.
    """
    return bool(plan.acciones) and all(a.herramienta in nlu.SOLO_LECTURA
                                       for a in plan.acciones)


def _respuesta_consulta() -> dict:
    return {"turno": _estado.turno_decision, "resumen": (
        "Consulta resuelta. No se ordenó nada y el turno no avanzó: la "
        "respuesta ya estaba en el plan."),
        "eventos": [], "acciones_encoladas": 0, "omitidas": [],
        "resultados": [], "turno_avanzado": False,
        "en_cola": len(motor.cola_inmediata)}


def _encolar_plan(plan) -> tuple[int, list[dict]]:
    """Mete en la cola del motor lo que esté listo. **No da el paso.**"""
    encoladas = 0
    omitidas: list[dict] = []

    for a in plan.acciones:
        # SOLO SE ENCOLA LO QUE ESTÁ LISTO. `falta_dato` también se queda fuera:
        # una acción con un enum inválido o un punto sin resolver llegaba al
        # motor y se ejecutaba con lo que hubiera — que es cómo un redespliegue
        # con un modo desconocido terminaba siendo proyección aérea.
        if a.estado != "lista":
            omitidas.append({"herramienta": a.herramienta, "estado": a.estado,
                             "motivo": a.motivo or "No estaba lista."})
            continue

        # Preguntar no es ordenar: la consulta ya trae su respuesta en el plan.
        if a.herramienta in nlu.SOLO_LECTURA:
            continue

        spec = nlu.herramientas.HERRAMIENTAS.get(a.herramienta)
        if spec is None or not spec.get("construir"):
            omitidas.append({"herramienta": a.herramienta, "estado": a.estado,
                             "motivo": "No corresponde a ninguna acción del motor."})
            continue
        try:
            v = motor.encolar(spec["construir"](a.argumentos))
        except Exception as exc:
            # Antes esto era `continue` a secas. Una acción confirmada en voz
            # alta desaparecía sin dejar rastro, y el hueco no salía por ningún
            # sitio hasta el debriefing —si es que salía.
            omitidas.append({"herramienta": a.herramienta, "estado": a.estado,
                             "motivo": f"No se pudo armar: {type(exc).__name__}"})
            continue

        # `encolar` VALIDA, y si no valida no encola. Contarla igual decía a la
        # sala que su orden estaba en cola cuando no lo estaba — y al dictar de
        # una en una, ese hueco no salía hasta resolver el turno.
        #
        # EL CAMPO ES `motivo` Y AQUÍ DECÍA `mensaje`. `Validacion` no tiene
        # `mensaje` —lo tiene `Resultado`, que es la otra mitad del patrón— así
        # que esta línea no omitía la orden: lanzaba `AttributeError` y la
        # consola devolvía un 500. Se alcanzaba siempre que `validar()` cambiaba
        # de opinión entre interpretar y confirmar, y de forma segura al dictar
        # la orden que pasa el tope de la cola, donde `encolar` rechaza sin que
        # ninguna capa anterior lo haya visto venir.
        if not v.ok:
            omitidas.append({"herramienta": a.herramienta, "estado": "no_viable",
                             "motivo": v.motivo or "El motor no la admitió."})
            continue
        encoladas += 1

    return encoladas, omitidas


def _resolver_turno(encoladas: int = 0, omitidas: list[dict] | None = None) -> dict:
    """
    Cierra la jornada con lo que haya en cola, y reporta desde resultados reales.

    **Resolver el día ES pasar a la noche.** No son dos actos: en cuanto el motor
    da el paso, lo que la sala tiene delante son consecuencias, y la consola deja
    de admitir órdenes hasta que se abra la jornada siguiente.
    """
    c = _cerrar_jornada()
    return {"turno": c["jornada"], "resumen": c["resumen"], "eventos": c["eventos"],
            "acciones_encoladas": encoladas,
            "omitidas": omitidas or [],
            "turno_avanzado": True,
            "en_cola": len(motor.cola_inmediata),
            "resultados": c["resultados"]}


@app.post("/api/consola/encolar")
def encolar_orden(c: Confirmacion):
    """
    Confirma una orden y la deja en cola **sin gastar el turno**.

    Es lo que permite dictar de una en una durante los 2,5 minutos completos de
    la fase de órdenes, en vez de tener que meterlas todas en un mismo texto. El
    reloj no se mueve: la fase corre entera.
    """
    _exigir_ventana_de_ordenes()
    plan = _sacar_plan(c.plan_id)
    if _solo_consultas(plan):
        return _respuesta_consulta()

    encoladas, omitidas = _encolar_plan(plan)
    return {"turno": _estado.jornada_visible,
            "resumen": (f"{encoladas} en cola para este turno. "
                        "El turno no ha avanzado."),
            "eventos": [], "acciones_encoladas": encoladas,
            "omitidas": omitidas, "resultados": [],
            "turno_avanzado": False,
            "en_cola": len(motor.cola_inmediata)}


@app.post("/api/consola/resolver")
def resolver():
    """Cierra el día con todo lo que la mesa dejó en cola y pasa a la noche."""
    _exigir_ventana_de_ordenes()
    return _resolver_turno()


# ---------------------------------------------------------------------------
# LOS MANDOS DEL RELOJ
#
# El ritmo normal lo lleva el sistema: trece minutos de día, dos de noche, y la
# jornada siguiente. Estos mandos existen para lo OTRO — la sala que termina
# antes, la que se interrumpe de verdad, el proyector que se cae. Son cuatro y
# ninguno decide nada del caso:
#
#     iniciar     arranca el ejercicio y abre la jornada 1
#     pausa       detiene el reloj interno · lo reanuda el mismo botón
#     noche       cierra el día YA y enseña las consecuencias
#     jornada     abre el día siguiente YA
#     reiniciar   deja el reloj a cero y parado. NO rebobina el mundo
# ---------------------------------------------------------------------------

@app.post("/api/consola/reloj/iniciar")
def reloj_iniciar():
    """
    **El único sitio desde el que arranca el ejercicio.** Se pulsa en la consola
    y a partir de ese instante las diez pantallas cuentan lo mismo.

    `sesion_desde` solo se fija la primera vez: es cuánto lleva la sala reunida,
    y eso no se reinicia al empezar una jornada nueva.
    """
    with _cerrojo:
        if sala["reloj"]["sesion_desde"] is None:
            sala["reloj"]["sesion_desde"] = time.time()
        _abrir_jornada()
    return _cronometro()


@app.post("/api/consola/reloj/pausa")
def reloj_pausa():
    """
    Detiene el reloj interno del ejercicio, o lo reanuda.

    Es el mando de las interrupciones reales: una pregunta que se alarga, alguien
    que entra, un proyector que se apaga. **El tiempo del ejercicio no corre
    mientras la sala no está en el ejercicio**, y el cronómetro de las diez
    pantallas se detiene a la vez.
    """
    with _cerrojo:
        r = sala["reloj"]
        if r["jornada_desde"] is None:
            raise HTTPException(409, "El reloj no ha empezado. Pulse «Iniciar».")
        if r["pausa_desde"] is None:
            r["pausa_desde"] = time.time()
        else:
            _reanudar_si_estaba_en_pausa()
    return _cronometro()


@app.post("/api/consola/reloj/noche")
def reloj_pasar_a_la_noche():
    """Cierra el día ahora mismo: resuelve lo que haya en cola y enseña las
    consecuencias. Para cuando la sala terminó antes de los trece minutos."""
    with _cerrojo:
        if sala["cerrado"]:
            raise HTTPException(409, "El ejercicio ya terminó.")
        if sala["fase"] != "dia":
            raise HTTPException(409, "Ya es de noche: las consecuencias están servidas.")
        _cerrar_jornada()
    return _cronometro()


@app.post("/api/consola/reloj/jornada")
def reloj_jornada_siguiente():
    """
    Abre el día siguiente ahora mismo.

    Si todavía es de día, primero lo cierra: saltar a la jornada siguiente sin
    resolver la actual dejaría en cola órdenes que la mesa dio en voz alta y
    nadie ejecutó jamás.
    """
    with _cerrojo:
        if sala["cerrado"]:
            raise HTTPException(409, "El ejercicio ya terminó.")
        # CON EL RELOJ PARADO ESTO ADELANTABA LA JORNADA SIN RESOLVER NADA. La
        # condición de arriba solo cierra el día si el reloj corre, así que
        # pulsarlo antes de «Iniciar» —montando, que es cuando se pulsa todo—
        # subía `jornada_abierta` una vez por pulsación mientras
        # `turno_decision` seguía en cero: el tablero decía «jornada 4 de 5» con
        # el ejercicio sin empezar.
        if sala["reloj"]["jornada_desde"] is None:
            raise HTTPException(409, (
                "El ejercicio no ha empezado. La jornada 1 se abre con "
                "«Iniciar», no saltando a la siguiente."))
        if sala["fase"] == "dia":
            _cerrar_jornada()
        if sala["cerrado"]:
            return _cronometro()
        _abrir_jornada()
    return _cronometro()


@app.post("/api/consola/reloj/reiniciar")
def reloj_reiniciar():
    """
    Deja el reloj a cero y parado. Vuelve a mandar la fase de reserva.

    **No rebobina el mundo**: lo que el motor ya resolvió, resuelto está. Esto
    solo detiene la cuenta.
    """
    with _cerrojo:
        sala["reloj"] = {"sesion_desde": None, "jornada_desde": None,
                         "pausa_desde": None}
        # Y VUELVE A LA FASE DE RESERVA, que es lo que este docstring prometía y
        # no hacía. Sin esta línea, reiniciar durante la noche dejaba la sala
        # rotulada «noche» para siempre —nada la volvía a mover, porque
        # `_sincronizar` se retira en cuanto el reloj está parado— mientras el
        # canal SÍ aceptaba órdenes. La pantalla decía una cosa y el servidor
        # hacía otra.
        sala["fase"] = "dia"
    return _cronometro()


@app.post("/api/consola/fase/{fase}")
def cambiar_fase(fase: str):
    """Poner la sala en una fase concreta sin cronometrar. Para montar y depurar:
    el ritmo normal lo lleva el reloj."""
    if fase not in FASES:
        raise HTTPException(400, f"Fase desconocida: {fase}. Las dos son {FASES}")
    with _cerrojo:
        sala["fase"] = fase
    return _cronometro()


class Linea(BaseModel):
    rol: str
    linea: str
    condicion: str = ""


@app.post("/api/consola/declarar_linea")
def declarar_linea(d: Linea):
    """
    El turno 0: 60 segundos por rol, sin debate.

    La métrica más reveladora del ejercicio es la distancia entre la línea que la
    sala declaró y la que de hecho ejecutó.
    """
    motor.declarar_linea(d.rol, d.linea, d.condicion)
    return {"declaradas": motor.lineas_declaradas}


# ===========================================================================
# Consultas
# ===========================================================================

@app.get("/api/catalogo")
def catalogo():
    """Se GENERA desde el estado. Nunca se escribe a mano en un prompt."""
    return {"mundo": catalogo_para_agente(_estado), "acciones": catalogo_por_rol()}


@app.get("/api/config")
def diagnostico():
    """
    Si hay modelo o no, y dónde se escribe la llave. La consola lo muestra al
    montar, para que nadie descubra a mitad del ejercicio que estaba degradado.
    """
    return cfg_llm().diagnostico()


@app.get("/api/consulta/{tema}")
def consulta(tema: str):
    """Hechos, no párrafos. Extraídos del motor y por tema."""
    return nlu.hoja_de_datos(_estado, tema)


@app.get("/api/metricas")
def metricas():
    return motor.metricas()


@app.get("/api/proyeccion")
def proyeccion():
    """T+72h sin nadie al mando: el país que la sala entrega."""
    return motor.proyectar_sin_mando()


# ===========================================================================
# Frontend construido
# ===========================================================================

@app.get("/{full_path:path}")
def servir_frontend(full_path: str):
    dist = Path(__file__).resolve().parents[2] / "web_ui" / "dist"
    archivo = dist / full_path
    if full_path and archivo.is_file():
        return FileResponse(archivo)
    index = dist / "index.html"
    if not index.exists():
        raise HTTPException(503, "El frontend no está construido. Corra `npm run build` en web_ui/.")
    return FileResponse(index)


if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser(description="SIMCASE · Estallido Social")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=args.port)
