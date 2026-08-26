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

FASES = ("parte_privado", "apertura", "deliberacion", "ordenes",
         "resolucion", "consecuencias", "registro")

sala = {
    "fase": "parte_privado",
    # Las pantallas se congelan durante la deliberación. Si algo cambia mientras
    # la gente habla, la gente mira la pantalla.
    "congelado": True,
    "planes": {},
    "esfera": {"publicaciones": [], "generado_por": "aún no hay hechos"},
}


def _congelado_en(fase: str) -> bool:
    return fase in ("parte_privado", "apertura", "deliberacion")


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
    d["congelado"] = sala["congelado"]
    d["fase"] = sala["fase"]
    d["registro"] = [asdict(x) for x in _estado.registro[-12:]]
    # Qué se movió desde la última vez que la sala miró. Un delta no revela nada
    # que el valor actual no revelara ya: se calcula sobre las mismas magnitudes
    # que `vista_publica()` serializa, ni una más.
    d["deltas"] = motor.deltas()
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
        v = views.vista(_estado, rol, motor.rng)
    except KeyError:
        raise HTTPException(404, f"Rol desconocido: {rol}. Los ocho son {views.ROLES}")
    v["congelado"] = sala["congelado"]
    v["acciones"] = catalogo_por_rol().get(rol, [])
    return v


@app.get("/api/vistas")
def todas_las_vistas():
    """Solo para revisar el contenido al montar. No es una superficie del ejercicio."""
    return views.todas(_estado, motor.rng)


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
    plan_id = f"plan-{len(sala['planes']) + 1}"
    plan = nlu.interpretar(_estado, orden.texto, plan_id)
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
    plan = sala["planes"].pop(c.plan_id, None)
    if plan is None:
        raise HTTPException(404, "Ese plan ya se consumió o no existe.")

    encoladas = 0
    for a in plan.acciones:
        if a.estado in ("no_viable", "ambigua"):
            continue
        spec = nlu.herramientas.HERRAMIENTAS.get(a.herramienta)
        if spec is None:
            continue
        try:
            motor.encolar(spec["construir"](a.argumentos))
            encoladas += 1
        except Exception:
            continue

    r = motor.paso(franja="dia")
    _refrescar_esfera(r.eventos)
    sala["fase"] = "consecuencias"
    sala["congelado"] = False
    return {"turno": r.turno, "resumen": r.resumen, "eventos": r.eventos,
            "acciones_encoladas": encoladas,
            "resultados": [{"accion": n, "ok": x.ok, "mensaje": x.mensaje,
                            "datos": x.datos}
                           for n, x in r.resultados]}


@app.post("/api/consola/noche")
def interludio_nocturno():
    """El interludio nocturno: no se delibera, se sufre. Tres minutos."""
    r = motor.paso(franja="noche")
    _refrescar_esfera(r.eventos)
    return {"turno": r.turno, "resumen": r.resumen, "eventos": r.eventos}


@app.post("/api/consola/fase/{fase}")
def cambiar_fase(fase: str):
    if fase not in FASES:
        raise HTTPException(400, f"Fase desconocida: {fase}. Las siete son {FASES}")
    sala["fase"] = fase
    sala["congelado"] = _congelado_en(fase)
    return {"fase": fase, "congelado": sala["congelado"],
            "minutos": _minutos_de(fase)}


def _minutos_de(fase: str) -> float:
    return {"parte_privado": P.MIN_PARTE_PRIVADO, "apertura": 1.0,
            "deliberacion": 6.0, "ordenes": 2.5, "resolucion": 1.0,
            "consecuencias": 1.0, "registro": 0.5}.get(fase, 0.0)


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
