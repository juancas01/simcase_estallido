"""
test_invariantes.py — Verificadores SIN modelo.

Heredado de Macondo (§6.4 de la guía): dos niveles de pruebas, y el primero es
el que se usa a diario. Estas comprueban propiedades estructurales y de
comportamiento sin consumir un solo token, corren en menos de un segundo y se
ejecutan en cada cambio.

Las dos primeras son las que más valen: protegen las invariantes que, si se
rompen, vacían el ejercicio de sentido sin que nada falle ruidosamente.
"""

from __future__ import annotations

import json
import random

import pytest

from src.engine import parameters as P
from src.engine import force
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis
from src.engine.state import Composicion
from src.engine.actions import (
    ExigirEstandaresEmpleo, FijarRegistroEscrito, OperarNodo, AbrirMesaLocal,
)


@pytest.fixture
def estado():
    return cargar_estado()


@pytest.fixture
def motor(estado):
    return MotorCrisis(estado, semilla=P.SEMILLA_POR_DEFECTO)


# ===========================================================================
# INVARIANTE 1 · La capa 1 nunca sale
# ===========================================================================

def test_la_vista_publica_jamas_expone_composicion_real(estado):
    """
    Si `composicion_real` se filtra a la interfaz, las cuatro fuentes con sesgo
    sobran, el error doble desaparece y la Defensoría se queda sin oficio. Es la
    invariante más importante del sistema.
    """
    blob = json.dumps(estado.vista_publica(), default=str)
    assert "composicion_real" not in blob
    assert "protesta_legitima" not in blob
    assert "estructura_organizada" not in blob
    assert "vandalismo_oportunista" not in blob


def test_la_vista_publica_sigue_limpia_tras_varios_turnos(motor):
    for i in range(6):
        motor.paso(franja="noche" if i % 2 else "dia")
    blob = json.dumps(motor.estado.vista_publica(), default=str)
    assert "composicion_real" not in blob
    assert "estructura_organizada" not in blob


# ===========================================================================
# INVARIANTE 2 · Toda región puede ser salvada
# ===========================================================================

def test_toda_region_tiene_corredor_humanitario(estado):
    """
    Sin vía de reposición de oxígeno, una región acumula muertes evitables HAGA
    LO QUE HAGA la sala. Eso no es un dilema: es un guion que castiga.

    Se detectó midiendo: las cuatro estrategias daban las mismas 147 muertes
    porque Buenaventura no tenía ningún corredor humanitario.
    """
    for r in estado.regiones.values():
        sirven = [
            c for c in estado.corredores.values()
            if "humanitario" in c.clases_prioridad
            and any(estado.nodos[n].region_id == r.region_id
                    for n in c.nodos if n in estado.nodos)
        ]
        assert sirven, f"{r.nombre} no tiene corredor humanitario"


def test_las_muertes_dependen_de_las_decisiones():
    """
    Si dos estrategias distintas producen el mismo número de muertes, el oxígeno
    está desacoplado de las decisiones y el reloj dejó de ser un dilema.
    """
    def correr(abrir_humanitario: bool) -> int:
        e = cargar_estado()
        m = MotorCrisis(e, semilla=P.SEMILLA_POR_DEFECTO)
        objetivo = e.corredores["C-HOS"].nodos
        for t in range(P.TURNOS_DECISION):
            if abrir_humanitario:
                for nid in objetivo:
                    if not e.nodos[nid].abierto:
                        m.encolar(AbrirMesaLocal(nodo_id=nid))
            m.paso(franja="dia")
            m.paso(franja="noche")
        return e.muertes_evitables_total()

    con = correr(True)
    sin = correr(False)
    assert con < sin, f"atender el corredor humanitario no cambió nada ({con} vs {sin})"


# ===========================================================================
# El motor de fuerza
# ===========================================================================

def test_la_probabilidad_de_incidente_nunca_excede_uno(estado):
    """
    El producto crudo de base × amplificadores llegaba a 8,6 para militares
    fatigados de noche en un nodo duro. La saturación exponencial lo acota.
    """
    estado.franja = "noche"
    for u in estado.unidades:
        u.fatiga = 1.0
        u.asignacion = "operacion"
    for nodo in estado.nodos.values():
        nodo.dureza = 1.0
        nodo.masa_presente = 5000
        for tipo in ("esmad", "policia", "militar"):
            ev = force.evaluar_riesgo(estado, nodo, tipo)
            assert 0.0 <= ev.p_incidente < 1.0


def test_los_mitigadores_reducen_el_riesgo(estado):
    nodo = next(iter(estado.nodos.values()))
    sin = force.evaluar_riesgo(estado, nodo, "esmad")

    estado.banderas.activar("reglas_escritas", 1)
    estado.banderas.activar("identificacion_agentes", 1)
    estado.banderas.activar("registro_av", 1)
    con = force.evaluar_riesgo(estado, nodo, "esmad",
                               dupla_presente=True, concertado_con_alcaldia=True)

    assert con.p_incidente < sin.p_incidente
    assert con.factor_mitigacion < sin.factor_mitigacion


def test_el_estandar_no_rescata_a_quien_opera_sin_cuidado(estado):
    """
    En la zona alta la curva ya saturó: el estándar protege a quien venía
    operando con cuidado y no salva una operación temeraria.
    """
    estado.franja = "noche"
    for u in estado.unidades:
        u.fatiga = 1.0
        u.asignacion = "operacion"
    nodo = next(iter(estado.nodos.values()))
    nodo.dureza, nodo.masa_presente = 1.0, 3000

    for b in ("reglas_escritas", "identificacion_agentes", "registro_av"):
        estado.banderas.activar(b, 1)
    ev = force.evaluar_riesgo(estado, nodo, "militar",
                              dupla_presente=True, concertado_con_alcaldia=True)
    assert ev.p_incidente > 0.5


# ===========================================================================
# Las tres vías de apertura
# ===========================================================================

def test_la_concertacion_da_caudal_proporcional_al_control(estado):
    """La trampa de la concertación: negociar con quien no controla no abre."""
    from src.engine import aperture
    nodo = estado.nodos["N010"]
    nodo.control_voceria = 0.4
    aperture.avanzar_concertacion(nodo, 1)
    r = aperture.avanzar_concertacion(nodo, 2)
    assert r is not None
    assert abs(r.caudal - P.CAUDAL_APERTURA_CONCERTACION * 0.4) < 1e-6


def test_un_corredor_vale_lo_que_su_peor_nodo(estado):
    c = estado.corredores["C-HOS"]
    for nid in c.nodos:
        estado.nodos[nid].caudal = 0.9
    estado.nodos[c.nodos[-1]].caudal = 0.1
    assert abs(c.caudal_efectivo(estado.nodos) - 0.1) < 1e-9


# ===========================================================================
# El motor de movilización
# ===========================================================================

def test_la_intensidad_no_se_clava_en_el_techo(estado):
    """
    Con incrementos planos y decaimiento constante, dos incidentes la dejaban en
    100 y a partir de ahí todas las decisiones daban igual. Rendimientos
    decrecientes + decaimiento proporcional lo evitan.
    """
    from src.engine import mobilization
    for _ in range(8):
        mobilization.registrar_evento(estado, "incidente_mortal")
    assert estado.intensidad_nacional <= P.INTENSIDAD_MAX

    rng = random.Random(1)
    antes = estado.intensidad_nacional
    for _ in range(6):
        mobilization.step(estado, rng)
    assert estado.intensidad_nacional < antes, "la intensidad debe poder bajar"


def test_rendimientos_decrecientes(estado):
    from src.engine import mobilization
    d1 = mobilization.registrar_evento(estado, "incidente_mortal")
    d2 = mobilization.registrar_evento(estado, "incidente_mortal")
    assert d2 < d1


# ===========================================================================
# El ciclo y las acciones
# ===========================================================================

def test_una_accion_invalida_no_tumba_el_resto(motor):
    """PROHIBIDO `break` al primer problema (F2 de la guía)."""
    motor.encolar(FijarRegistroEscrito())
    motor.cola_inmediata.append(OperarNodo(nodo_id="NO-EXISTE"))
    motor.encolar(ExigirEstandaresEmpleo())
    r = motor.paso(franja="dia")
    assert len(r.resultados) == 3
    assert sum(1 for _, x in r.resultados if x.ok) == 2


def test_el_turno_de_decision_solo_avanza_de_dia(motor):
    motor.paso(franja="dia")
    assert motor.estado.turno_decision == 1
    motor.paso(franja="noche")
    assert motor.estado.turno_decision == 1
    motor.paso(franja="dia")
    assert motor.estado.turno_decision == 2


def test_no_decidir_cuesta(motor):
    antes = motor.estado.reservas.legitimidad
    motor.paso(franja="dia")
    assert motor.estado.reservas.legitimidad < antes


def test_las_condicionales_caducan(motor):
    motor.encolar_condicional(
        FijarRegistroEscrito(), lambda e: False, "nunca se cumple"
    )
    for _ in range(P.CADUCIDAD_ORDEN_CONDICIONAL + 2):
        motor.paso(franja="dia")
    assert not motor.acciones_condicionales


def test_una_condicion_que_revienta_no_tumba_el_turno(motor):
    def explota(_estado):
        raise RuntimeError("boom")

    motor.encolar_condicional(FijarRegistroEscrito(), explota, "condición rota")
    r = motor.paso(franja="dia")     # no debe lanzar
    assert r.turno == 1
    assert not motor.acciones_condicionales


# ===========================================================================
# Reproducibilidad
# ===========================================================================

def test_la_misma_semilla_da_la_misma_corrida():
    """Sin esto no se puede reproducir la corrida en el debriefing."""
    def correr():
        e = cargar_estado()
        m = MotorCrisis(e, semilla=1234)
        for t in range(4):
            cerrados = [n for n in e.nodos.values() if not n.abierto]
            if cerrados:
                m.encolar(OperarNodo(nodo_id=cerrados[0].nodo_id, tipo_unidad="esmad"))
            m.paso(franja="dia" if t % 2 == 0 else "noche")
        return m.metricas()

    assert correr() == correr()


def test_el_estado_inicial_cumple_sus_invariantes():
    e = cargar_estado()
    assert len(e.nodos) == 24
    assert len(e.esmad_en_reserva()) == P.ESMAD_ESCUADRONES_TOTALES - P.ESMAD_DESPLEGADOS_T0
    # En t=0 no hay ningún mitigador puesto: la primera operación corre sin descuento.
    assert sum(e.banderas.mitigadores_activos().values()) == 0
    assert e.posicion_gremios == "fuera"
    for n in e.nodos.values():
        c = n.composicion_real
        s = c.protesta_legitima + c.vandalismo_oportunista + c.estructura_organizada
        assert abs(s - 1.0) < 1e-6
