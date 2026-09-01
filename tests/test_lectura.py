"""
test_lectura.py — La lectura del cierre (`B14`, docs/LA_MEDICION.md).

Dos preguntas y ningún puntaje: por qué vía destrabaron (el cómo) y a quién
atendieron (el qué). Las pruebas se leen igual que la lectura: un perfil de
sala que solo usó la fuerza tiene que salir como «solo despejaron», una sala
sin decisiones tiene que decirlo, y el desgaste tiene que partirse entre «lo
desgastaron» y «se les cayó de hambre».
"""

from __future__ import annotations

import json

import pytest

from src.engine import lectura
from src.engine.actions import (AbrirMesaLocal, ConvocarMesaNacional,
                                DisponerESMAD, Escoltar, ExigirProtocoloVoceria,
                                FijarPrioridadCombustible, OperarNodo)
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis, ResultadoTurno

SEMILLA = 20210511


@pytest.fixture
def motor():
    return MotorCrisis(cargar_estado(), semilla=SEMILLA)


def _correr(motor, colas):
    """Cinco jornadas; `colas(t)` devuelve la lista de órdenes del día t."""
    for t in range(1, 6):
        for accion in colas(t):
            motor.encolar(accion)
        motor.paso(franja="dia")
        motor.paso(franja="noche")


# ---------------------------------------------------------------------------
# El cómo — la firma y el reparto de vías
# ---------------------------------------------------------------------------

def test_la_sala_que_solo_uso_fuerza_sale_como_tal(motor):
    def colas(t):
        out = [DisponerESMAD()]
        cerrados = [n for n in motor.estado.nodos.values() if not n.abierto]
        for n in cerrados[:2]:
            out.append(OperarNodo(nodo_id=n.nodo_id, tipo_unidad="esmad"))
        return out

    _correr(motor, colas)
    l = lectura.calcular(motor)
    assert l["como"]["dominante"] == "despejar"
    assert "concertar" in l["como"]["sin_usar"]
    assert "solo despejaron" in l["firma"].lower()
    # Y operó puntos: el calificador C3 tiene material.
    assert l["como"]["calificadores"]["c3_miraron"]["puntos_operados"] > 0


def test_la_sala_de_la_mesa_sale_concertando(motor):
    def colas(t):
        out = [ConvocarMesaNacional()]
        cerrados = [n for n in motor.estado.nodos.values() if not n.abierto]
        for n in cerrados[:3]:
            out.append(AbrirMesaLocal(nodo_id=n.nodo_id, con_alcaldia=True))
        return out

    _correr(motor, colas)
    l = lectura.calcular(motor)
    assert l["como"]["dominante"] == "concertar"
    assert "despejar" in l["como"]["sin_usar"]
    assert "concertaron" in l["firma"].lower()


def test_la_sala_pasiva_dice_que_no_decidio(motor):
    _correr(motor, lambda t: [])
    l = lectura.calcular(motor)
    assert l["que"]["atencion"]["decisiones"] == 0
    assert "ninguna decisión" in l["firma"]
    assert l["que"]["publico_que_nadie_miro"]["publico"] is None


def test_las_aperturas_y_reaperturas_se_reparten_por_via(motor):
    """«Abrimos cuatro» no es «abrimos cuatro y tres se volvieron a cerrar»."""
    # Una apertura por fuerza en la jornada 1 y su reapertura esa misma noche.
    n = next(iter(motor.estado.nodos.values()))
    motor.paso(franja="dia")   # t=1 sin órdenes: el mundo arranca
    # Se inyecta la secuencia mínima como historial sintético: la lectura es
    # una función de los eventos, y aquí se prueban sus reglas y no el azar.
    motor.historial.append(ResultadoTurno(
        turno=2, franja="dia",
        eventos=[{"tipo": "apertura", "nodo": n.nodo_id, "via": "fuerza"}],
        regiones={}))
    motor.historial.append(ResultadoTurno(
        turno=2, franja="noche",
        eventos=[{"tipo": "reapertura", "nodo": n.nodo_id, "via": "fuerza"}],
        regiones={}))
    c2 = lectura.calcular(motor)["como"]["calificadores"]["c2_aguantaron"]
    assert c2["aperturas"]["fuerza"] == 1
    assert c2["reaperturas"]["fuerza"] == 1
    assert c2["revertidas_misma_jornada"]["fuerza"] == 1


# ---------------------------------------------------------------------------
# El qué — atención, saldo y el cruce
# ---------------------------------------------------------------------------

def test_la_atencion_suma_con_su_residuo(motor):
    motor.encolar(DisponerESMAD())            # empresa
    motor.encolar(ExigirProtocoloVoceria())   # gobierno de sí mismo
    motor.encolar(ConvocarMesaNacional())     # ciudadanía
    motor.paso(franja="dia")
    motor.paso(franja="noche")

    a = lectura.calcular(motor)["que"]["atencion"]
    assert a["decisiones"] == 3
    assert a["por_publico"]["empresa"]["decisiones"] == 1
    assert a["por_publico"]["ciudadania"]["decisiones"] == 1
    # El residuo se nombra: la mesa ordenándose no atiende a nadie en particular.
    assert a["gobierno_de_si_mismo"]["decisiones"] == 1


def test_el_publico_que_nadie_miro_lleva_su_consecuencia(motor):
    motor.encolar(ConvocarMesaNacional())     # solo ciudadanía
    motor.paso(franja="dia")
    motor.paso(franja="noche")
    q = lectura.calcular(motor)["que"]
    assert q["publico_que_nadie_miro"]["publico"] is not None
    assert q["publico_que_nadie_miro"]["consecuencia"]


def test_el_saldo_sale_en_banda_y_con_sus_hechos(motor):
    _correr(motor, lambda t: [])
    s = lectura.calcular(motor)["que"]["saldo"]
    for p in ("empresa", "gremios", "ciudadania", "internacional"):
        assert s[p]["banda"] in ("bien", "regular", "mal")
        assert s[p]["hechos"], f"la banda de {p} salió sin hechos debajo"
    # La pérdida de la empresa es reconstruible desde los indicadores.
    assert s["empresa"]["perdida_mm_cop"] > 0


def test_el_residuo_de_atender_a_la_empresa_sin_fuerza(motor):
    """§5 B: la celda que distingue una sala imaginativa de una obediente."""
    motor.encolar(DisponerESMAD())       # empresa, por fuerza
    motor.paso(franja="dia")
    motor.paso(franja="noche")
    r = lectura.calcular(motor)["que"]["empresa_sin_fuerza"]
    assert r["atendieron"] == 1 and r["sin_fuerza"] == 0


# ---------------------------------------------------------------------------
# Las imputaciones que se resuelven por su objeto
# ---------------------------------------------------------------------------

def test_el_orden_del_combustible_es_la_respuesta_escrita_de_la_sala(motor):
    e = motor.estado
    vida = FijarPrioridadCombustible(orden=["mision_medica", "transporte_alimentos",
                                            "fuerza_publica", "consumo_general"])
    dinero = FijarPrioridadCombustible(orden=["consumo_general", "fuerza_publica",
                                              "transporte_alimentos", "mision_medica"])
    assert vida.imputacion(e)[1] == ("ciudadania",)
    assert dinero.imputacion(e)[1] == ("empresa",)


def test_la_escolta_se_imputa_por_la_carga(motor):
    e = motor.estado
    medica = Escoltar(corredor_id="C-HOS", clase_carga="humanitario")
    carga = Escoltar(corredor_id="C-SUR", clase_carga="general")
    assert medica.imputacion(e)[1] == ("ciudadania",)
    assert set(carga.imputacion(e)[1]) == {"gremios", "empresa"}


def test_el_desgastar_solo_cuenta_donde_habia_cierre(motor):
    e = motor.estado
    from src.engine.actions import ActivarInstrumentosSectoriales, EsquemaHumanitarioMunicipal
    # El epicentro arranca con puntos cerrados; el esquema muerde ahí.
    esquema = EsquemaHumanitarioMunicipal(region_id=e.region_epicentro)
    assert "desgastar" in esquema.imputacion(e)[0]
    # Pero donde todo está abierto, atender no desgasta nada.
    for n in e.nodos.values():
        n.caudal = 1.0
    assert "desgastar" not in esquema.imputacion(e)[0]


# ---------------------------------------------------------------------------
# El desgaste partido: atender no es lo mismo que dejar pasar hambre
# ---------------------------------------------------------------------------

def _historial_con_desgaste(motor, nodo, semaforo):
    rid = nodo.region_id
    motor.historial.append(ResultadoTurno(
        turno=3, franja="dia",
        eventos=[{"tipo": "desgaste", "nodo": nodo.nodo_id}],
        regiones={rid: {"semaforo": semaforo}}))


def test_un_desgaste_en_region_atendida_es_un_desgaste(motor):
    nodo = next(iter(motor.estado.nodos.values()))
    motor.estado.instrumentos_sectoriales[nodo.region_id] = 1
    _historial_con_desgaste(motor, nodo, "ambar")
    d = lectura.calcular(motor)["como"]["desgaste"]
    assert len(d["lo_desgastaron"]) == 1
    assert not d["se_les_cayo_de_hambre"]


def test_un_desgaste_en_region_en_rojo_sin_decisiones_es_hambre(motor):
    nodo = next(iter(motor.estado.nodos.values()))
    _historial_con_desgaste(motor, nodo, "rojo")
    d = lectura.calcular(motor)["como"]["desgaste"]
    assert not d["lo_desgastaron"]
    assert len(d["se_les_cayo_de_hambre"]) == 1


def test_la_firma_menciona_la_hambre(motor):
    nodo = next(iter(motor.estado.nodos.values()))
    _historial_con_desgaste(motor, nodo, "rojo")
    assert "hambre" in lectura.calcular(motor)["firma"].lower()


# ---------------------------------------------------------------------------
# Condición de servicio: serializable, pura, y sin campos en Estado
# ---------------------------------------------------------------------------

def test_la_lectura_entera_es_serializable(motor):
    _correr(motor, lambda t: [ConvocarMesaNacional()])
    json.dumps(lectura.calcular(motor), ensure_ascii=False)


def test_la_lectura_es_pura(motor):
    _correr(motor, lambda t: [ConvocarMesaNacional()])
    a, b = lectura.calcular(motor), lectura.calcular(motor)
    assert a == b
    assert not any(hasattr(motor.estado, k) for k in ("via", "atiende", "lectura"))
