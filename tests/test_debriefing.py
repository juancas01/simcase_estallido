"""
test_debriefing.py — El cierre: la lectura y el debriefing por la API.

Tres cosas, y las tres son la §7 de docs/LA_MEDICION.md:

  · EL SERVIDOR RECHAZA, NO LA PANTALLA ESCONDE. `/api/lectura` y
    `/api/metricas` devuelven 409 mientras la sala no haya cerrado. Que la
    lectura no se vea durante la sesión no es una preferencia de presentación:
    es la condición para que mida algo.
  · NI EL VOCABULARIO SALE ANTES. Si la palabra «empresa» o «sortear»
    aparece una sola vez en una respuesta en vivo, la sala empieza a jugar
    contra ella. Se barre cada superficie con el ejercicio a mitad de camino.
  · LA LECTURA VIVE FUERA DE LA RUTA DE JUEGO. `views.py` no la importa, y
    ninguna superficie la necesita para dibujar la jornada.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# El vocabulario que solo existe después del cierre. No se barre «despejar»,
# «constituir» ni «atiende»: son palabras españolas que las consolas y los
# en_claro ya usan («no se logró despejar», «en qué orden se atienden los
# corredores») y no delatan la taxonomía. Estas sí: son los nombres de las
# vías nuevas y de los públicos, y no estaban antes.
VOCABULARIO_NUEVO = ("sortear", "encuadrar", "empresa", "ciudadania",
                     "nadie miró")


@pytest.fixture
def consola(tmp_path, monkeypatch):
    """La API recargada, con la bitácora dirigida a `tmp_path`."""
    monkeypatch.setenv("SIMCASE_BITACORA", "on")
    monkeypatch.setenv("SIMCASE_CORRIDAS", str(tmp_path))
    from src.api import main

    importlib.reload(main)
    with TestClient(main.app) as cliente:
        yield cliente, main
    importlib.reload(main)     # devolver el módulo a la bitácora apagada


def _cerrar_ejercicio(cliente):
    cliente.post("/api/consola/reloj/iniciar")
    for _ in range(5):
        cliente.post("/api/consola/reloj/noche")
        cliente.post("/api/consola/reloj/jornada")


# ---------------------------------------------------------------------------
# El pestillo: 409 antes del cierre, contenido después
# ---------------------------------------------------------------------------

def test_la_lectura_no_se_sirve_antes_del_cierre(consola):
    cliente, _ = consola
    r = cliente.get("/api/lectura")
    assert r.status_code == 409
    assert "no ha terminado" in r.json()["detail"]


def test_las_metricas_tampoco(consola):
    """El agujero viejo: `ratio_fuerza_concertacion` en mitad de la jornada 2."""
    cliente, _ = consola
    assert cliente.get("/api/metricas").status_code == 409


def test_tras_el_cierre_la_lectura_y_el_debriefing_se_sirven(consola):
    cliente, _ = consola
    _cerrar_ejercicio(cliente)
    assert cliente.get("/api/lectura").status_code == 200
    d = cliente.get("/api/debriefing").json()
    for k in ("recibido", "entregado", "proyeccion", "lineas_vs_ejecutada",
              "pliego_por_jornada", "momentos", "lectura"):
        assert k in d, f"al debriefing le falta {k}"
    # El pestillo de las métricas se abre con el cierre, no se retira.
    assert cliente.get("/api/metricas").status_code == 200


def test_el_cierre_no_mueve_el_mundo_que_la_sala_entrega(consola):
    """La proyección va sobre una copia: el tablero de la última noche es el
    país que dejaron, no el que viene."""
    cliente, _ = consola
    cliente.post("/api/consola/reloj/iniciar")
    for _ in range(5):
        cliente.post("/api/consola/reloj/noche")
        cliente.post("/api/consola/reloj/jornada")
    t = cliente.get("/api/tablero").json()
    assert t["cronometro"]["cerrado"] is True
    assert t["cronometro"]["jornada"] == 5
    # Y la proyección es idempotente: pedirla dos veces no la corre dos veces.
    a = cliente.get("/api/proyeccion").json()
    b = cliente.get("/api/proyeccion").json()
    assert a == b


def test_el_debriefing_escribe_el_archivo_de_la_corrida(consola, tmp_path):
    """La corrida tiene que quedar en disco aunque el proceso muera después."""
    cliente, _ = consola
    _cerrar_ejercicio(cliente)
    archivos = list(Path(tmp_path).rglob("corrida.jsonl"))
    assert archivos, "el cierre no escribió el archivo de la corrida"
    lineas = [json.loads(x) for x in
              archivos[0].read_text(encoding="utf-8").splitlines() if x.strip()]
    tipos = {x["t"] for x in lineas}
    assert {"apertura", "ventana", "cierre"} <= tipos
    cierre = next(x for x in lineas if x["t"] == "cierre")
    assert "firma" in cierre["lectura"]


# ---------------------------------------------------------------------------
# Ni el vocabulario sale antes
# ---------------------------------------------------------------------------

def test_ninguna_superficie_en_viva_dice_la_lectura(consola):
    cliente, _ = consola
    cliente.post("/api/consola/reloj/iniciar")
    cliente.post("/api/consola/interpretar",
                 json={"texto": "concentrar el ESMAD"})
    cliente.post("/api/consola/interpretar",
                 json={"texto": "convocar la mesa nacional con el Comite"})
    cliente.post("/api/consola/reloj/noche")

    respuestas = [
        cliente.get("/api/tablero").json(),
        cliente.get("/api/esfera").json(),
        cliente.get("/api/catalogo").json(),
        cliente.get("/api/consulta/gremios").json(),
    ]
    from src.engine import views

    for rol in views.ROLES:
        respuestas.append(cliente.get(f"/api/vista/{rol}").json())
    respuestas.append(cliente.post(
        "/api/consola/interpretar",
        json={"texto": "escoltar una mision medica"}).json())

    for respuesta in respuestas:
        texto = json.dumps(respuesta, ensure_ascii=False).lower()
        for palabra in VOCABULARIO_NUEVO:
            assert palabra not in texto, (
                f"«{palabra}» salió en vivo en {texto[:120]}")


def test_el_registro_del_tablero_no_lleva_la_imputacion(consola):
    """El tablero serializa el registro con `asdict`: la imputación viaja en
    el motor y en la bitácora, jamás en `Decision`."""
    cliente, _ = consola
    cliente.post("/api/consola/reloj/iniciar")
    cliente.post("/api/consola/interpretar", json={"texto": "concentrar el ESMAD"})
    r = cliente.post("/api/consola/ejecutar", json={"plan_id": "plan-1"})
    assert r.status_code == 200
    for fila in cliente.get("/api/tablero").json()["registro"]:
        assert "via" not in fila and "atiende" not in fila


def test_views_y_estado_no_importan_la_lectura():
    """
    La lectura vive fuera de la ruta de juego.

    Se comprueba el IMPORT y no la palabra: «lectura» es también una palabra
    española legítima en la prosa del motor («la lectura en voz alta del
    plan»), y prohibirla castigaría los comentarios sin proteger nada.
    """
    for modulo in ("src/engine/views.py", "src/engine/state.py",
                   "src/engine/territory.py", "src/engine/bitacora.py"):
        fuente = Path(modulo).read_text(encoding="utf-8")
        for prohibido in ("from src.engine import lectura",
                          "from src.engine.lectura",
                          "engine.lectura import"):
            assert prohibido not in fuente, f"{modulo} importa la lectura"


# ---------------------------------------------------------------------------
# Y las 37 acciones declaran cómo y a quién (LA_MEDICION §4)
# ---------------------------------------------------------------------------

def test_las_treinta_y_siete_declaran_via_y_publico():
    from src.engine.actions import CATALOGO
    from src.engine.loader import cargar_estado

    estado = cargar_estado()
    vias = {"despejar", "concertar", "desgastar", "sortear",
            "constituir", "encuadrar"}
    publicos = {"empresa", "gremios", "ciudadania", "internacional"}
    for cls in CATALOGO:
        via, atiende = cls().imputacion(estado)
        assert via and set(via) <= vias, (
            f"{cls.__name__} no declara una vía válida: {via}")
        assert set(atiende) <= publicos, (
            f"{cls.__name__} declara un público inválido: {atiende}")


def test_el_catalogo_por_rol_no_filtra_la_imputacion():
    """La imputación no viaja al repertorio que ve cada rol en su pantalla."""
    from src.engine.actions import catalogo_por_rol
    from src.engine.loader import cargar_estado

    texto = json.dumps(catalogo_por_rol(cargar_estado()),
                       ensure_ascii=False).lower()
    for palabra in VOCABULARIO_NUEVO:
        assert palabra not in texto
    # Y las claves de la imputación, ni como campos.
    assert '"via"' not in texto and '"atiende"' not in texto
