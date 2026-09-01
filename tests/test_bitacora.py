"""
test_bitacora.py — El archivo de la corrida (`B1`).

LA TRAMPA DE LA SIMULACIÓN ANTERIOR, Y POR QUÉ ESTE ARCHIVO EXISTE
------------------------------------------------------------------
Que el código anote el dato no basta: hay que comprobar que **llega al
archivo**. Allí dos campos se perdían en la serialización y ninguna prueba lo
detectó, porque las pruebas miraban el código y no la salida. Aquí cada
prueba abre y lee el `.jsonl` escrito en `tmp_path` — no el objeto, no el
código: el archivo.
"""

from __future__ import annotations

import json

import pytest

from src.engine.bitacora import Bitacora
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis
from src.engine import lectura


@pytest.fixture
def una_corrida(tmp_path):
    """Un motor con bitácora en `tmp_path`, y la ruta del archivo escrito."""
    bitacora = Bitacora(raiz=tmp_path)
    motor = MotorCrisis(cargar_estado(), semilla=20210511, bitacora=bitacora)
    return motor, bitacora


def _lineas(bitacora: Bitacora) -> list[dict]:
    """Lo que de verdad quedó en disco, releyéndolo."""
    assert bitacora.ruta is not None and bitacora.ruta.exists()
    with bitacora.ruta.open(encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]


# ---------------------------------------------------------------------------
# Que el dato llega al archivo
# ---------------------------------------------------------------------------

def test_la_apertura_lleva_la_semilla_y_la_foto_de_partida(una_corrida):
    motor, bitacora = una_corrida
    motor.paso(franja="dia")
    primeras = [x for x in _lineas(bitacora) if x["t"] == "apertura"]
    assert len(primeras) == 1
    assert primeras[0]["semilla"] == 20210511
    # La foto de partida: sin ella no hay contra qué comparar la ventana 1.
    assert primeras[0]["indicadores"]["presion_calle"] > 0


def test_la_decision_lleva_su_via_y_su_publico(una_corrida):
    """La imputación (`via`, `atiende`) tiene que llegar al archivo."""
    from src.engine.actions import DisponerESMAD, OperarNodo

    motor, bitacora = una_corrida
    motor.encolar(DisponerESMAD())
    motor.encolar(OperarNodo(nodo_id="N001", tipo_unidad="esmad"))
    motor.paso(franja="dia")

    decisiones = [x for x in _lineas(bitacora) if x["t"] == "decision"]
    assert decisiones, "las decisiones no llegaron al archivo"
    por_accion = {d["accion"]: d for d in decisiones}
    assert por_accion["DisponerESMAD"]["via"] == ["despejar"]
    assert por_accion["DisponerESMAD"]["atiende"] == ["empresa"]
    # OperarNodo se imputa por su objeto: la región del punto.
    assert por_accion["OperarNodo"]["atiende"]


def test_la_ventana_lleva_el_desarrollo_de_las_metricas(una_corrida):
    motor, bitacora = una_corrida
    motor.paso(franja="dia")
    motor.paso(franja="noche")

    ventanas = [x for x in _lineas(bitacora) if x["t"] == "ventana"]
    assert len(ventanas) == 2
    for v in ventanas:
        assert v["indicadores"]["presion_calle"] >= 0
        assert set(v["regiones"]), "el semáforo por región no llegó"
        for r in v["regiones"].values():
            assert r["semaforo"] in ("rojo", "ambar", "verde")


def test_la_linea_declarada_llega_al_archivo(una_corrida):
    motor, bitacora = una_corrida
    motor.declarar_linea("Defensa", "Primero la mesa, fuerza solo si falla")
    motor.paso(franja="dia")
    lineas = [x for x in _lineas(bitacora) if x["t"] == "linea"]
    assert lineas and lineas[0]["rol"] == "Defensa"


def test_el_cierre_lleva_metricas_proyeccion_y_lectura(una_corrida):
    motor, bitacora = una_corrida
    for _ in range(5):
        motor.paso(franja="dia")
        motor.paso(franja="noche")
    bitacora.cierre(metricas=motor.metricas(),
                    proyeccion=motor.proyectar_sin_mando(),
                    lectura=lectura.calcular(motor))

    cierres = [x for x in _lineas(bitacora) if x["t"] == "cierre"]
    assert len(cierres) == 1
    assert cierres[0]["metricas"]["decisiones_totales"] == 0
    assert "firma" in cierres[0]["lectura"]
    assert "antes" in cierres[0]["proyeccion"]


def test_el_archivo_se_puede_releer_con_el_proceso_muerto(una_corrida):
    """El debriefing no debe depender de que el servidor siga vivo."""
    motor, bitacora = una_corrida
    motor.paso(franja="dia")
    bitacora.cierre(metricas=motor.metricas(), proyeccion={},
                    lectura=lectura.calcular(motor))
    leido = lectura.cierre_desde_archivo(bitacora.ruta)
    assert leido["t"] == "cierre"
    assert "firma" in leido["lectura"]


# ---------------------------------------------------------------------------
# La bitácora no puede tumbar el ejercicio
# ---------------------------------------------------------------------------

def test_un_disco_roto_no_tumba_el_motor(tmp_path):
    """Si el disco falla en plena corrida, lo caro es la corrida."""
    # Una carpeta cuya raíz es un archivo existente: mkdir no puede nada ahí.
    bloqueo = tmp_path / "bloqueo"
    bloqueo.write_text("no soy una carpeta", encoding="utf-8")
    bitacora = Bitacora(raiz=bloqueo)
    motor = MotorCrisis(cargar_estado(), bitacora=bitacora)
    from src.engine.actions import DisponerESMAD
    motor.encolar(DisponerESMAD())
    res = motor.paso(franja="dia")     # no lanza
    assert res.resultados
    assert not bitacora.activa


def test_un_bitacora_inactiva_no_escribe_nada(tmp_path):
    bitacora = Bitacora.inactiva()
    motor = MotorCrisis(cargar_estado(), bitacora=bitacora)
    motor.paso(franja="dia")
    assert bitacora.ruta is None
    assert list(tmp_path.iterdir()) == []


def test_el_entorno_apaga_y_redirige(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMCASE_BITACORA", "off")
    assert not Bitacora.desde_entorno().activa
    monkeypatch.setenv("SIMCASE_BITACORA", "on")
    monkeypatch.setenv("SIMCASE_CORRIDAS", str(tmp_path))
    b = Bitacora.desde_entorno()
    assert b.activa and b.raiz == tmp_path
