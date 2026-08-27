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
opera —puede ser uno de los ocho— solo transcribe: no conduce, no reparte
información, no decide el ritmo y no sabe nada que los demás no sepan.
"""

from __future__ import annotations

import argparse
import time
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
# EL RELOJ DE SALA
#
# Antes la fase se cambiaba a mano, con siete botones en la consola. El ritmo del
# ejercicio dependía entonces de que alguien se acordara de pulsar, y ese alguien
# está además transcribiendo órdenes. Ahora el tiempo corre solo.
#
# VIVE AQUÍ Y NO EN EL NAVEGADOR, y no es un detalle de implementación: hay diez
# pantallas mirando a la vez —el tablero, la consola y las ocho vistas—, y un
# cronómetro por pantalla es un cronómetro distinto por pantalla en cuanto una se
# recarga. El servidor guarda DOS INSTANTES y cada superficie deriva de ellos lo
# que muestra:
#
#     sesion_desde   cuándo se pulsó «Iniciar». No se mueve nunca.
#     turno_desde    cuándo empezó el ciclo de fases del turno en curso.
#
# La fase no se guarda: se CALCULA a partir de `turno_desde` y de esta tabla. Un
# valor derivado no se puede desincronizar de aquello de lo que deriva, y saltar
# de fase se reduce entonces a mover `turno_desde` hacia atrás.
#
# La tabla se sirve a las pantallas en cada respuesta. La interfaz tenía su
# propia copia en `comun.jsx`, y un dato en dos sitios se desincroniza.
# ---------------------------------------------------------------------------

# `guia` es la coreografía de §6.2 de `docs/propuesta.md`, palabra por palabra:
# qué debería estar pasando en la sala mientras corre esa fase. Viaja con la
# tabla hasta la consola, de modo que quien la opera no tiene que acordarse.
FASES_TURNO = (
    {"id": "parte_privado", "nombre": "Parte privado",
     "minutos": float(P.MIN_PARTE_PRIVADO), "congela": True,
     "guia": "Cada rol lee su vista en su dispositivo. Nadie habla."},
    {"id": "apertura", "nombre": "Apertura", "minutos": 1.0, "congela": True,
     "guia": "El tablero muestra qué cambió desde la última ventana. "
             "Se lee en voz alta."},
    {"id": "deliberacion", "nombre": "Deliberación", "minutos": 6.0, "congela": True,
     "guia": "Las pantallas se congelan. Se habla."},
    {"id": "ordenes", "nombre": "Órdenes", "minutos": 2.5, "congela": False,
     "guia": "Se transcribe lo que la mesa acordó. La pantalla devuelve el plan "
             "interpretado con su banda de riesgo, y la mesa confirma o corrige."},
    {"id": "resolucion", "nombre": "Resolución", "minutos": 1.0, "congela": False,
     "guia": "Se resuelve el turno con todo lo que quedó en cola."},
    {"id": "consecuencias", "nombre": "Consecuencias", "minutos": 1.0, "congela": False,
     "guia": "Prensa, redes, gremios y respaldo internacional responden."},
    {"id": "registro", "nombre": "Registro", "minutos": 0.5, "congela": False,
     "guia": "La decisión pasa al pliego, con su responsable nominado."},
)

FASES = tuple(f["id"] for f in FASES_TURNO)

# El ciclo entero es el turno de decisión de §6.2. Si alguien cambia una fase sin
# cambiar el presupuesto, esto lo dice en el arranque y no en mitad de la sala.
assert abs(sum(f["minutos"] for f in FASES_TURNO) - P.MIN_TURNO_DECISION) < 1e-9

# Cuántos planes sin ejecutar se guardan. Con 2,5 minutos de órdenes por turno,
# más de un puñado significa que algo se quedó a medias.
PLANES_EN_MEMORIA = 8

# Contador MONOTÓNICO de planes. Antes el identificador salía de
# `len(sala["planes"]) + 1`, y `ejecutar` saca el plan del diccionario: con dos
# planes abiertos, ejecutar el primero hacía que el siguiente `interpretar`
# reutilizara un identificador vivo y sobrescribiera aquel plan sin avisar.
_planes_emitidos = 0

sala = {
    # La fase de reserva: la que rige mientras el reloj no corre. En cuanto
    # alguien pulsa «Iniciar» manda la fase calculada, y esta deja de leerse.
    "fase": "parte_privado",
    # Los dos instantes del reloj de sala. `None` en los dos = sin empezar.
    "reloj": {"sesion_desde": None, "turno_desde": None},
    # Las pantallas se congelan durante la deliberación. Si algo cambia mientras
    # la gente habla, la gente mira la pantalla.
    "congelado": True,
    "planes": {},
    "esfera": {"publicaciones": [], "generado_por": "aún no hay hechos"},
}


def _congelado_en(fase: str) -> bool:
    return any(f["id"] == fase and f["congela"] for f in FASES_TURNO)


def _segundos_antes_de(fase: str) -> float:
    """Cuánto dura el ciclo hasta el comienzo de `fase`. Es lo que hay que
    restarle al reloj para plantarse justo en ella."""
    acumulado = 0.0
    for f in FASES_TURNO:
        if f["id"] == fase:
            return acumulado
        acumulado += f["minutos"] * 60
    return acumulado


def _fase_ahora(ahora: float | None = None) -> tuple[str, bool]:
    """
    La fase que toca, y si congela. Mientras el reloj no corre manda la fase de
    reserva, de modo que un montaje que nunca pulse «Iniciar» se comporta como
    antes.

    **Agotado el ciclo NO se encadena nada.** Se queda en la última fase y el
    tiempo de más se cuenta como prórroga: nada avanza sin que una persona lo
    decida, que es la regla de la que cuelga todo este ejercicio.
    """
    desde = sala["reloj"]["turno_desde"]
    if desde is None:
        return sala["fase"], _congelado_en(sala["fase"])

    t = (time.time() if ahora is None else ahora) - desde
    acumulado = 0.0
    for f in FASES_TURNO:
        acumulado += f["minutos"] * 60
        if t < acumulado:
            return f["id"], f["congela"]

    ultima = FASES_TURNO[-1]
    return ultima["id"], ultima["congela"]


def _cronometro() -> dict:
    """
    Lo que necesita una pantalla para dibujar el cronómetro **sin preguntar dos
    veces**: los dos instantes, la tabla de fases y el reloj del servidor.

    `ahora` es la pieza que las mantiene de acuerdo. Cada superficie compara su
    reloj con este y guarda el desfase, así que las diez cuentan sobre el mismo
    instante aunque los relojes de sus máquinas no coincidan — y siguen contando
    entre respuesta y respuesta, sin esperar a la siguiente.
    """
    r = sala["reloj"]
    fase, congelado = _fase_ahora()
    return {
        "corriendo": r["turno_desde"] is not None,
        "ahora": time.time(),
        "sesion_desde": r["sesion_desde"],
        "turno_desde": r["turno_desde"],
        "fase": fase,
        "congelado": congelado,
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
    d = _estado.vista_publica()
    d["cronometro"] = _cronometro()
    # Lo que la mesa ya confirmó y todavía no se ha resuelto. La consola lo lee
    # de aquí, así que sobrevive a que alguien recargue la pantalla.
    d["en_cola"] = len(motor.cola_inmediata)
    d["fase"] = d["cronometro"]["fase"]
    d["congelado"] = d["cronometro"]["congelado"]
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
# Superficie 2 · Las ocho vistas privadas
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
        raise HTTPException(404, f"Rol desconocido: {rol}. Los ocho son {views.ROLES}")
    v["cronometro"] = _cronometro()
    v["congelado"] = v["cronometro"]["congelado"]
    v["acciones"] = catalogo_por_rol().get(rol, [])
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
        if not v.ok:
            omitidas.append({"herramienta": a.herramienta, "estado": "no_viable",
                             "motivo": v.mensaje})
            continue
        encoladas += 1

    return encoladas, omitidas


def _resolver_turno(encoladas: int = 0, omitidas: list[dict] | None = None) -> dict:
    """Da el paso del turno con lo que haya en la cola, y reporta desde
    resultados reales."""
    r = motor.paso(franja="dia")
    _refrescar_esfera(r.eventos)
    # Resolver ES la fase de resolución. Si el reloj corre, se planta en las
    # consecuencias en vez de dejar correr los minutos de una fase que la sala
    # acaba de terminar. Solo hacia adelante: rebobinar el reloj de una sala
    # porque alguien resolvió tarde sería peor que no tocarlo.
    _ir_a_fase("consecuencias", solo_adelante=True)
    sala["fase"] = "consecuencias"
    sala["congelado"] = False
    return {"turno": r.turno, "resumen": r.resumen, "eventos": r.eventos,
            "acciones_encoladas": encoladas,
            "omitidas": omitidas or [],
            "turno_avanzado": True,
            "en_cola": len(motor.cola_inmediata),
            "resultados": [{"accion": n, "ok": x.ok, "mensaje": x.mensaje,
                            "datos": x.datos}
                           for n, x in r.resultados]}


@app.post("/api/consola/encolar")
def encolar_orden(c: Confirmacion):
    """
    Confirma una orden y la deja en cola **sin gastar el turno**.

    Es lo que permite dictar de una en una durante los 2,5 minutos completos de
    la fase de órdenes, en vez de tener que meterlas todas en un mismo texto. El
    reloj no se mueve: la fase corre entera.
    """
    plan = _sacar_plan(c.plan_id)
    if _solo_consultas(plan):
        return _respuesta_consulta()

    encoladas, omitidas = _encolar_plan(plan)
    return {"turno": _estado.turno_decision,
            "resumen": (f"{encoladas} en cola para este turno. "
                        "El turno no ha avanzado."),
            "eventos": [], "acciones_encoladas": encoladas,
            "omitidas": omitidas, "resultados": [],
            "turno_avanzado": False,
            "en_cola": len(motor.cola_inmediata)}


@app.post("/api/consola/resolver")
def resolver():
    """Cierra el turno con todo lo que la mesa dejó en cola."""
    return _resolver_turno()


@app.post("/api/consola/noche")
def interludio_nocturno():
    """El interludio nocturno: no se delibera, se sufre. Tres minutos."""
    r = motor.paso(franja="noche")
    _refrescar_esfera(r.eventos)
    return {"turno": r.turno, "resumen": r.resumen, "eventos": r.eventos}


def _ir_a_fase(fase: str, solo_adelante: bool = False) -> None:
    """Planta el reloj al comienzo de `fase`, corriendo `turno_desde` hacia
    atrás. Si el reloj no corre no hace nada: no se salta lo que no empezó."""
    if sala["reloj"]["turno_desde"] is None:
        return
    destino = time.time() - _segundos_antes_de(fase)
    if solo_adelante and destino > sala["reloj"]["turno_desde"]:
        return
    sala["reloj"]["turno_desde"] = destino


@app.post("/api/consola/reloj/iniciar")
def reloj_iniciar():
    """
    **El único sitio desde el que arranca el ejercicio.** Se pulsa en la consola
    y a partir de ese instante las diez pantallas cuentan lo mismo.

    `sesion_desde` solo se fija la primera vez: es cuánto lleva la sala reunida,
    y eso no se reinicia al empezar un turno nuevo.
    """
    ahora = time.time()
    if sala["reloj"]["sesion_desde"] is None:
        sala["reloj"]["sesion_desde"] = ahora
    sala["reloj"]["turno_desde"] = ahora
    return _cronometro()


@app.post("/api/consola/reloj/siguiente")
def reloj_siguiente_fase():
    """Adelanta a la fase siguiente, para cuando la sala termina antes. En la
    última no hace nada: de ahí se sale con un turno nuevo, no con un salto."""
    if sala["reloj"]["turno_desde"] is None:
        raise HTTPException(409, "El reloj no ha empezado. Pulse «Iniciar».")
    actual, _ = _fase_ahora()
    orden = [f["id"] for f in FASES_TURNO]
    i = orden.index(actual)
    if i + 1 < len(orden):
        _ir_a_fase(orden[i + 1])
    return _cronometro()


@app.post("/api/consola/reloj/turno")
def reloj_turno_siguiente():
    """Vuelve el ciclo de fases a su comienzo. El tiempo total de la sesión
    sigue corriendo: lo que empieza de nuevo es el turno, no la reunión."""
    if sala["reloj"]["sesion_desde"] is None:
        raise HTTPException(409, "El reloj no ha empezado. Pulse «Iniciar».")
    sala["reloj"]["turno_desde"] = time.time()
    return _cronometro()


@app.post("/api/consola/reloj/reiniciar")
def reloj_reiniciar():
    """Deja el reloj a cero y parado. Vuelve a mandar la fase de reserva."""
    sala["reloj"] = {"sesion_desde": None, "turno_desde": None}
    return _cronometro()


@app.post("/api/consola/fase/{fase}")
def cambiar_fase(fase: str):
    """Ir a una fase concreta. La consola ya no lo ofrece —el reloj lleva el
    ritmo— pero sigue aquí para montar y depurar sin cronometrar."""
    if fase not in FASES:
        raise HTTPException(400, f"Fase desconocida: {fase}. Las siete son {FASES}")
    _ir_a_fase(fase)
    sala["fase"] = fase
    sala["congelado"] = _congelado_en(fase)
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
