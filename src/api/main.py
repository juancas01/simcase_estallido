"""
main.py — API del ejercicio.

Sirve las dos proyecciones y la consola del moderador. Deliberadamente delgada:
toda la lógica vive en `src/engine`, que no sabe que esta capa existe.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

ESTADO: esqueleto funcional. El canal de órdenes en lenguaje natural (capa 4)
todavía no está conectado; `/api/plan/interpretar` devuelve por ahora una
interpretación determinista de prueba. El motor sí está completo y se puede
conducir por API.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.engine import parameters as P
from src.engine.loader import cargar_estado, catalogo_para_agente
from src.engine.simulation import MotorCrisis
from src.engine import force

app = FastAPI(title="SIMCASE · Estallido Social")

# --- estado global del ejercicio -------------------------------------------
_estado = cargar_estado()
motor = MotorCrisis(_estado)

sala = {
    "fase": "instalacion",     # instalacion|deliberacion|ordenes|resolucion
    "congelado": True,         # el tablero no se mueve durante la deliberación
    "planes": {},              # planes interpretados pendientes de confirmación
}


# ===========================================================================
# Proyección 1 · Tablero de situación
# ===========================================================================

@app.get("/api/estado")
def estado_publico():
    """
    Vista de la CAPA 2, nunca de la capa 1.

    `vista_publica()` no serializa `composicion_real`. Si algún día lo hiciera,
    el motor de información se anularía y el dilema central del caso
    desaparecería. Es la invariante más importante de esta capa.
    """
    d = _estado.vista_publica()
    d["congelado"] = sala["congelado"]
    d["fase"] = sala["fase"]
    d["registro"] = [asdict(x) for x in _estado.registro[-12:]]
    return d


# ===========================================================================
# Proyección 2 · Esfera pública
# ===========================================================================

@app.get("/api/esfera")
def esfera_publica():
    """Lo que se dice. La distancia con el tablero es el caso."""
    return {
        "encuadre_dominante": _estado.encuadre_dominante,
        "exposicion_internacional": round(_estado.reservas.exposicion_internacional, 1),
        "cifras": _cifras_en_disputa(),
        "publicaciones": _publicaciones_recientes(),
        "denuncias": [],   # las llena la capa 3 cuando esté conectada
    }


def _cifras_en_disputa() -> dict:
    """
    Las tres cifras. Divergen porque las fuentes tienen sesgos opuestos, no
    porque alguien mienta — que es justamente lo que hace difícil el problema.

    PENDIENTE(B3): la divergencia sale hoy de aritmética cableada y no del motor
    de información. Debe salir de `information.estimar_nodo()`, que ya existe y
    ya produce la dispersión real. Ver PENDIENTES.md.
    """
    verificada = sum(1 for n in _estado.nodos.values() if not n.abierto)
    return {
        "oficial": max(0, verificada - 3),      # el parte subestima
        "municipal": verificada + 2,            # el parte municipal sobreestima
        "verificada": verificada,
    }


def _publicaciones_recientes() -> list[dict]:
    """
    PENDIENTE(B2): plantilla hasta conectar los seis agentes de entorno de la
    capa 3 (§9) — Comité del Paro, prensa, redes, gremios, internacional y
    alcaldes. Ver PENDIENTES.md.
    """
    out = []
    for r in motor.historial[-2:]:
        for ev in r.eventos:
            if ev.get("evento") == "incidente_mortal":
                out.append({
                    "fuente": "prensa_nacional", "turno": r.turno,
                    "texto": "Reportan víctima en operación de desbloqueo.",
                    "sin_verificar": False,
                })
            elif ev.get("tipo") == "reapertura":
                out.append({
                    "fuente": "redes", "turno": r.turno,
                    "texto": f"El punto {ev['nodo']} volvió a cerrarse durante la noche.",
                    "sin_verificar": True,
                })
    return out


# ===========================================================================
# Consola del moderador
# ===========================================================================

class TextoOrden(BaseModel):
    texto: str


@app.post("/api/plan/interpretar")
def interpretar(orden: TextoOrden):
    """
    Devuelve el plan para que el moderador LO LEA DE VUELTA a la sala, con su
    banda de riesgo, antes de ejecutarlo.

    Ese momento no es un trámite: la sala oye su propia decisión reformulada,
    con su riesgo, y con frecuencia la cambia.

    PENDIENTE(B1): aquí entra el NLU con herramientas tipadas de la capa 4. Por
    ahora la interpretación ignora el texto y es determinista y de prueba. Ver
    PENDIENTES.md.
    """
    plan_id = f"plan-{len(sala['planes']) + 1}"
    acciones = []

    cerrados = [n for n in _estado.nodos.values() if not n.abierto]
    if cerrados:
        nodo = max(cerrados, key=lambda n: n.dureza)
        ev = force.evaluar_riesgo(_estado, nodo, "esmad")
        acciones.append({
            "rol": "Ministro de Defensa",
            "descripcion": f"Operación de desbloqueo sobre {nodo.nombre}",
            "requisitos_faltantes": [],
            "habilitada_por": [],
            "riesgo": {
                "banda": ev.banda,
                "p_incidente": round(ev.p_incidente, 3),
                "mitigadores_ausentes": ev.mitigadores_ausentes,
            },
        })

    sala["planes"][plan_id] = acciones
    return {"plan_id": plan_id, "acciones": acciones, "texto_original": orden.texto}


class Confirmacion(BaseModel):
    plan_id: str


@app.post("/api/plan/ejecutar")
def ejecutar(c: Confirmacion):
    if c.plan_id not in sala["planes"]:
        raise HTTPException(404, "Ese plan ya se consumió o no existe.")
    sala["planes"].pop(c.plan_id)   # se consume: reanudar dos veces ejecutaría dos veces
    r = motor.paso(franja="dia")
    sala["fase"] = "resolucion"
    sala["congelado"] = False
    return {"turno": r.turno, "resumen": r.resumen,
            "resultados": [{"accion": n, "ok": x.ok, "mensaje": x.mensaje}
                           for n, x in r.resultados]}


@app.post("/api/turno/noche")
def interludio_nocturno():
    """El interludio nocturno: no se delibera, se resuelve. Tres minutos."""
    r = motor.paso(franja="noche")
    return {"turno": r.turno, "resumen": r.resumen, "eventos": r.eventos}


@app.post("/api/sala/fase/{fase}")
def cambiar_fase(fase: str):
    if fase not in ("instalacion", "deliberacion", "ordenes", "resolucion"):
        raise HTTPException(400, f"Fase desconocida: {fase}")
    sala["fase"] = fase
    # El tablero se congela durante la deliberación. Si la pantalla se mueve
    # mientras la gente habla, la gente mira la pantalla.
    sala["congelado"] = fase in ("instalacion", "deliberacion")
    return {"fase": fase, "congelado": sala["congelado"]}


@app.get("/api/catalogo")
def catalogo():
    """Se GENERA desde el estado. Nunca se escribe a mano en un prompt."""
    return catalogo_para_agente(_estado)


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
