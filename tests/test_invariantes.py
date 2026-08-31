"""
test_invariantes.py — Verificadores sin modelo.

Comprueban propiedades estructurales y de comportamiento sin consumir tokens.
Corren en décimas de segundo y se ejecutan en cada cambio.

Cada prueba de este archivo existe porque su propiedad **se rompió alguna vez** o
porque su ruptura sería silenciosa — que es la peor clase de fallo: el ejercicio
pierde su objeto sin que nada reviente ruidosamente.
"""

from __future__ import annotations

import pathlib
import random

import pytest

from src.engine import parameters as P
from src.engine import actions, aperture, force, information, mobilization, territory, views
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis
from src.engine.state import Composicion
from src.engine.actions import (
    catalogo_por_rol,
    OperarNodo, AbrirMesaLocal, DesplegarEquiposTerreno, FijarReglasEmpleoSector,
    ExigirProtocoloVoceria, AdoptarCriterioPriorizacion, Escoltar,
    FijarPrioridadCombustible, ConvocarMesaNacional,
    InstalarMesaConVoceros, DisponerESMAD, OfrecerContraprestacion,
    DesplazarseAlEpicentro, PresentarEvidenciaInteligencia,
)


@pytest.fixture
def estado():
    return cargar_estado()


@pytest.fixture
def motor(estado):
    return MotorCrisis(estado, semilla=P.SEMILLA_POR_DEFECTO)


def _rng():
    return random.Random(P.SEMILLA_POR_DEFECTO)


# ===========================================================================
# LA VERDAD NO SALE DEL MOTOR
# ===========================================================================

def test_la_vista_publica_jamas_expone_la_mezcla_real(estado):
    """
    Si la verdad se proyecta en la pared, las cuatro fuentes con sesgo sobran, el
    error doble desaparece y los equipos de terreno se quedan sin oficio.
    """
    texto = repr(estado.vista_publica())
    assert "composicion_real" not in texto
    assert "protesta_legitima" not in texto
    assert "estructura_organizada" not in texto


def test_las_nueve_vistas_privadas_tampoco_la_exponen(estado):
    """La vista privada es de alta resolución, no de capa 1."""
    for rol in views.ROLES:
        texto = repr(views.vista(estado, rol))
        assert "composicion_real" not in texto, rol
        assert "protesta_legitima" not in texto, rol


def test_ninguna_vista_revela_la_veracidad_de_una_denuncia(estado):
    """
    Nada distingue una denuncia cierta de una falsa. Si el campo `veraz` se
    filtrara, la decisión de gastar un equipo dejaría de existir.
    """
    assert "veraz" not in repr(estado.vista_publica())
    for rol in views.ROLES:
        assert "'veraz'" not in repr(views.vista(estado, rol)), rol


def test_la_vista_publica_sigue_limpia_tras_varios_turnos(motor):
    for _ in range(4):
        motor.paso()
    texto = repr(motor.estado.vista_publica())
    assert "composicion_real" not in texto
    assert "veraz" not in texto


# ===========================================================================
# LA MEZCLA REAL TIENE CONSECUENCIA — decisión de diseño nº 1
# ===========================================================================

def test_operar_sobre_protesta_legitima_cuesta_mas(estado):
    """
    PRIMERA vía. Un punto que es 90 % protesta legítima cuesta casi el doble que
    uno donde la mitad es otra cosa: es fuerza sobre población civil.
    """
    civil = estado.nodos["N010"]
    civil.composicion_real = Composicion(0.95, 0.04, 0.01)
    mixto = estado.nodos["N003"]
    mixto.composicion_real = Composicion(0.50, 0.20, 0.30)

    assert force.multiplicador_costo_civil(civil) > force.multiplicador_costo_civil(mixto)
    assert force.multiplicador_costo_civil(mixto) == pytest.approx(1.0)


def test_concertar_donde_hay_estructura_produce_acuerdos_que_se_rompen(estado):
    """
    SEGUNDA vía. Quien firmó no manda sobre quien sostiene el cierre — y la sala
    no puede saberlo sin haber gastado un equipo ahí.
    """
    rng = random.Random(7)
    fragiles = 0
    for _ in range(200):
        nodo = estado.nodos["N003"]
        nodo.composicion_real = Composicion(0.20, 0.10, 0.70)
        nodo.turnos_en_negociacion = 1
        r = aperture.avanzar_concertacion(nodo, 1, rng)
        fragiles += bool(r and r.fragil)
    assert fragiles > 100, "con 70 % de estructura organizada casi todo debe romperse"

    limpios = 0
    for _ in range(200):
        nodo = estado.nodos["N010"]
        nodo.composicion_real = Composicion(0.97, 0.02, 0.01)
        nodo.turnos_en_negociacion = 1
        r = aperture.avanzar_concertacion(nodo, 1, rng)
        limpios += bool(r and not r.fragil)
    assert limpios > 180, "con 1 % de estructura organizada casi nada debe romperse"


def test_la_mezcla_real_cambia_el_resultado_de_la_corrida():
    """
    LA PRUEBA QUE ANTES FALLABA EN SILENCIO.

    Hasta la v2, convertir los 24 puntos en estructura organizada pura no cambiaba
    una sola métrica: la decisión de diseño nº 1 estaba protegida por una
    invariante y no entraba en ningún cálculo.
    """
    def correr(mutar):
        e = cargar_estado()
        if mutar:
            for n in e.nodos.values():
                n.composicion_real = Composicion(0.0, 0.0, 1.0)
        m = MotorCrisis(e, semilla=P.SEMILLA_POR_DEFECTO)
        for t in range(1, 4):
            for nodo in sorted(e.nodos.values(), key=lambda x: -x.control_voceria)[:3]:
                if not nodo.abierto:
                    m.encolar(AbrirMesaLocal(
                        nodo_id=nodo.nodo_id,
                        con_alcaldia=nodo.region_id == e.region_epicentro,
                    ))
            m.paso(franja="dia")
            m.paso(franja="noche")
        return m.metricas()

    assert correr(False) != correr(True), (
        "la mezcla real de los puntos no cambia nada: la decisión de diseño nº 1 "
        "está desconectada del motor"
    )


# ===========================================================================
# EL RELOJ ES UN DILEMA, NO UN GUION
# ===========================================================================

def test_toda_region_tiene_corredor_humanitario(estado):
    """
    Sin vía de reposición, una región acumula muertes evitables HAGA LO QUE HAGA
    la sala. Eso no es un dilema: es un guion que castiga.
    """
    for r in estado.regiones.values():
        assert estado.corredores_que_sirven(r.region_id, "humanitario"), r.nombre


def test_las_muertes_dependen_de_las_decisiones():
    """Atender el corredor humanitario tiene que salvar gente. Si no, es un guion."""
    def correr(atender: bool) -> int:
        e = cargar_estado()
        m = MotorCrisis(e, semilla=P.SEMILLA_POR_DEFECTO)
        hum = min((c for c in e.corredores.values()
                   if "humanitario" in c.clases_prioridad), key=lambda c: len(c.nodos))
        for _ in range(5):
            if atender:
                m.encolar(FijarPrioridadCombustible())
                for nid in hum.nodos:
                    if not e.nodos[nid].abierto:
                        m.encolar(AbrirMesaLocal(
                            nodo_id=nid,
                            con_alcaldia=e.nodos[nid].region_id == e.region_epicentro,
                        ))
            m.paso(franja="dia")
            m.paso(franja="noche")
        return e.muertes_evitables_total()

    con, sin = correr(True), correr(False)
    assert con < sin, f"atender el corredor humanitario no cambió nada ({con} vs {sin})"


def test_un_corredor_abierto_repone_mas_de_lo_que_la_region_gasta():
    """Si no, la región se agota pase lo que pase y el reloj deja de ser dilema."""
    assert P.CAPACIDAD_CORREDOR_DIARIA > P.CONSUMO_BASE_DIARIO


def test_la_prioridad_de_combustible_es_un_criterio_permanente(estado):
    """
    Fijarla una vez debe aplicarse en CADA paso. Si fuera un empujón de un solo
    turno, Transporte no tendría ninguna palanca continua sobre el reloj.
    """
    m = MotorCrisis(estado, semilla=P.SEMILLA_POR_DEFECTO)
    m.encolar(FijarPrioridadCombustible())
    m.paso(franja="dia")
    assert estado.prioridad_combustible, "el criterio no quedó fijado"

    antes = {r.region_id: r.dias_autonomia_oxigeno for r in estado.regiones.values()}
    m.paso(franja="noche")
    # Sigue bajando (el consumo manda), pero menos de lo que bajaría sin criterio.
    sin_criterio = cargar_estado()
    m2 = MotorCrisis(sin_criterio, semilla=P.SEMILLA_POR_DEFECTO)
    m2.paso(franja="dia")
    caida_con = antes["R-CUM"] - estado.regiones["R-CUM"].dias_autonomia_oxigeno
    m2.paso(franja="noche")
    assert caida_con < 1.0


# ===========================================================================
# EL ESTÁNDAR DE DERECHOS ES UN INSTRUMENTO
# ===========================================================================

def test_la_probabilidad_de_incidente_nunca_excede_uno(estado):
    """
    Una operación puede ser un disparate y aun así no terminar mal — que es
    precisamente por lo que se repiten los disparates.
    """
    nodo = estado.nodos["N003"]
    nodo.dureza = 1.0
    nodo.masa_presente = 5000
    estado.franja = "noche"
    ev = force.evaluar_riesgo(estado, nodo, "militar")
    assert ev.p_incidente <= P.P_INCIDENTE_MAX < 1.0


def test_los_mitigadores_reducen_el_riesgo(estado):
    nodo = estado.nodos["N003"]
    sin = force.evaluar_riesgo(estado, nodo, "esmad").p_incidente
    for b in ("reglas_escritas", "identificacion_agentes", "registro_av"):
        estado.banderas.activar(b, 1)
    con = force.evaluar_riesgo(
        estado, nodo, "esmad", concertado_con_alcaldia=True
    ).p_incidente
    assert con < sin * 0.6


def test_el_estandar_no_rescata_a_quien_opera_sin_cuidado(estado):
    """
    Asimetría deliberada: protege a quien ya venía operando con cuidado y no
    rescata a quien no. A riesgo alto la curva ya saturó.
    """
    nodo = estado.nodos["N003"]
    nodo.dureza = 0.95
    nodo.masa_presente = 2000
    estado.franja = "noche"
    for b in ("reglas_escritas", "identificacion_agentes", "registro_av"):
        estado.banderas.activar(b, 1)
    ev = force.evaluar_riesgo(
        estado, nodo, "militar", concertado_con_alcaldia=True
    )
    assert ev.p_incidente > 0.55


def test_la_banda_de_riesgo_se_puede_leer_antes_de_decidir(estado):
    """La sala gestiona riesgo, no sorpresa: la banda existe antes de ejecutar."""
    ev = force.evaluar_riesgo(estado, estado.nodos["N003"], "esmad")
    assert ev.banda in ("baja", "media", "alta", "critica")
    assert "mitigadores ausentes" in ev.resumen()


# ===========================================================================
# LOS EQUIPOS DE TERRENO SALEN DE UN SOLO BOLSILLO
# ===========================================================================

def test_los_equipos_son_tres_y_se_reponen_cada_turno(motor):
    e = motor.estado
    motor.paso(franja="dia")
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES
    information.consumir_equipo(e, "prueba")
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES - 1
    motor.paso(franja="noche")
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES - 1, (
        "de noche no se reponen")
    motor.paso(franja="dia")
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES


def test_acompanar_una_operacion_ya_no_gasta_ni_descuenta(motor):
    """
    **El sexto mitigador se fue con el tercero que lo justificaba.**

    Acompañar descontaba riesgo porque miraba una dupla de la Defensoría del
    Pueblo, que no respondía ante quien operaba. Con los equipos en manos del
    mismo ministerio que ordena la operación, que sus propios funcionarios la
    acompañen no cambia la probabilidad de que una imagen circule — así que ni
    gasta bolsillo ni lo ahorra, y el campo no existe.
    """
    import dataclasses
    campos = {f.name for f in dataclasses.fields(OperarNodo)}
    assert "dupla_presente" not in campos
    assert "dupla_presente" not in P.MITIGADORES
    assert len(P.MITIGADORES) == 5

    e = motor.estado
    antes = e.equipos_disponibles
    motor.encolar(OperarNodo(nodo_id="N010", tipo_unidad="esmad"))
    motor.paso(franja="dia")
    assert e.equipos_disponibles == antes


def test_mirar_aqui_es_no_mirar_alla(motor):
    """Tres equipos, cinco puntos. Lo que no alcanza se informa."""
    e = motor.estado
    motor.encolar(DesplegarEquiposTerreno(
        nodos=["N001", "N010", "N003", "N004", "N005"]
    ))
    r = motor.paso(franja="dia")
    _, res = r.resultados[0]
    assert res.ok
    assert len(res.datos["verificados"]) == P.EQUIPOS_TERRENO_TOTALES
    assert len(res.datos["no_alcanzados"]) == 2


def test_una_denuncia_verificada_no_se_puede_verificar_dos_veces(estado):
    did = estado.denuncias[0].denuncia_id
    assert information.verificar_denuncia(estado, did)["ok"]
    assert not information.verificar_denuncia(estado, did)["ok"]


# ===========================================================================
# EL PAQUETE DETONANTE
# ===========================================================================

def test_nunca_una_sola_denuncia_sin_verificar(estado):
    """
    Decisión ética explícita: un ejercicio en el que la única denuncia grave
    resulta inventada enseña que las denuncias graves suelen serlo — y eso, sobre
    hechos con responsabilidad judicial viva, es tomar partido.
    """
    assert len(estado.denuncias) >= 2
    assert len({d.veraz for d in estado.denuncias}) == 2


def test_declarar_en_verificacion_abarata_el_estallido():
    """
    La mejor conducta disponible no es acertar: es no afirmar lo que no se sabe.
    """
    def correr(declara: bool) -> float:
        e = cargar_estado()
        m = MotorCrisis(e, semilla=P.SEMILLA_POR_DEFECTO)
        if declara:
            for d in e.denuncias:
                information.declarar_en_verificacion(e, d.denuncia_id)
        for _ in range(4):
            m.paso(franja="dia")
        return e.reservas.legitimidad

    assert correr(True) > correr(False)


def test_la_jornada_nacional_esta_en_el_calendario(motor):
    """Un empujón exógeno que el calendario trae y nadie decide."""
    for _ in range(P.TURNO_JORNADA_NACIONAL):
        r = motor.paso(franja="dia")
    assert any(e.get("tipo") == "jornada_nacional" for e in r.eventos)


def test_el_ultimatum_gremial_es_independiente_del_umbral(motor):
    """
    Los dos caminos hacia `evaluando` deben coexistir: una cosa es que el país
    deje de respaldar al Gobierno y otra que un gremio pida algo concreto.
    """
    e = motor.estado
    assert e.posicion_gremios == "fuera"
    assert e.reservas.legitimidad > P.UMBRALES["legitimidad_gremios_evaluan"]
    motor.paso(franja="dia")
    assert e.posicion_gremios == "evaluando"


# ===========================================================================
# LA COHESIÓN RESPONDE A LO QUE LA SALA HACE
# ===========================================================================

def test_la_cohesion_no_es_una_rampa_determinista():
    """
    ANTES ERA UNA RECTA. Se cobraba también en los interludios nocturnos —donde
    la sala no delibera ni ordena— y en la proyección, donde ya no hay nadie al
    mando: doce peajes en cinco decisiones, y la serie bajaba igual hiciera lo
    que hiciera la sala.
    """
    def correr(constituye: bool) -> float:
        e = cargar_estado()
        m = MotorCrisis(e, semilla=P.SEMILLA_POR_DEFECTO)
        for t in range(1, 6):
            if constituye and t == 1:
                m.encolar(ExigirProtocoloVoceria())
                m.encolar(AdoptarCriterioPriorizacion())
            m.paso(franja="dia")
            m.paso(franja="noche")
        return e.reservas.cohesion_mesa

    con, sin = correr(True), correr(False)
    assert con > sin + 20, f"constituirse tiene que pagar ({con} vs {sin})"


def test_las_banderas_no_se_cobran_de_noche(motor):
    """De noche la sala no delibera ni ordena: no se le puede cobrar la ausencia."""
    e = motor.estado
    motor.paso(franja="dia")
    antes = e.reservas.cohesion_mesa
    motor.paso(franja="noche")
    assert e.reservas.cohesion_mesa == antes


# ===========================================================================
# LAS TRES VÍAS DE ABRIR
# ===========================================================================

def test_la_concertacion_da_caudal_proporcional_al_control(estado):
    """La trampa: pactar con quien controla el 40 % abre el 36 %."""
    nodo = estado.nodos["N010"]
    nodo.control_voceria = 0.4
    aperture.avanzar_concertacion(nodo, 1, _rng())
    r = aperture.avanzar_concertacion(nodo, 2, _rng())
    assert r is not None
    assert r.caudal == pytest.approx(0.4 * P.CAUDAL_APERTURA_CONCERTACION)


def test_un_corredor_vale_lo_que_su_peor_punto(estado):
    c = estado.corredores["C-HOS"]
    for nid in c.nodos:
        estado.nodos[nid].caudal = 0.9
    estado.nodos[c.nodos[1]].caudal = 0.1
    assert c.caudal_efectivo(estado.nodos) == pytest.approx(0.1)
    assert c.punto_que_bloquea(estado.nodos) is None  # 0.1 > 0.05: pasa algo

    estado.nodos[c.nodos[1]].caudal = 0.0
    assert c.punto_que_bloquea(estado.nodos) == c.nodos[1]


def test_el_desgaste_es_lento_a_proposito():
    """
    Si el desgaste fuera barato y rápido dominaría a las otras dos vías, y la sala
    descubriría que basta con esperar.
    """
    assert P.TURNOS_APOYO_BAJO_PARA_DESGASTE >= 3
    assert P.P_DESGASTE_POR_TURNO <= 0.25


# ===========================================================================
# QUIÉN HABILITA A QUIÉN
# ===========================================================================

def test_la_concertacion_en_el_epicentro_requiere_al_alcalde(estado):
    """
    Antes esta acción vivía en la ficha del Alcalde y no comprobaba jurisdicción:
    un alcalde municipal acababa pactando cierres en dos regiones ajenas.
    """
    epicentro = next(n for n in estado.nodos.values()
                     if n.region_id == estado.region_epicentro and not n.abierto)
    v = AbrirMesaLocal(nodo_id=epicentro.nodo_id).validar(estado)
    assert not v.ok
    assert "Alcalde" in " ".join(v.habilitada_por)

    v2 = AbrirMesaLocal(nodo_id=epicentro.nodo_id, con_alcaldia=True).validar(estado)
    assert v2.ok


def test_el_alcalde_no_puede_pactar_fuera_de_su_jurisdiccion(estado):
    fuera = next(n for n in estado.nodos.values()
                 if n.region_id != estado.region_epicentro)
    v = InstalarMesaConVoceros(nodo_id=fuera.nodo_id).validar(estado)
    assert not v.ok
    assert "Interior" in " ".join(v.habilitada_por)


def test_sin_escolta_no_hay_caravana(estado):
    """Es la condición material de todo el frente logístico."""
    for u in estado.unidades:
        if u.tipo == "esmad":
            u.asignacion = "contencion"
    v = Escoltar(corredor_id="C-HOS").validar(estado)
    assert not v.ok
    assert v.habilitada_por


def test_una_accion_devuelve_quien_puede_habilitarla(estado):
    """Cuando falta el requisito, el motor no rechaza: empuja la conversación."""
    for u in estado.unidades:
        if u.tipo == "esmad":
            u.asignacion = "operacion"
    v = OperarNodo(nodo_id="N003", tipo_unidad="esmad").validar(estado)
    assert not v.ok
    assert v.requisitos_faltantes and v.habilitada_por


# ===========================================================================
# EL BUCLE DE TURNOS
# ===========================================================================

def test_una_accion_invalida_no_tumba_el_resto(motor):
    """PROHIBIDO `break` al primer problema."""
    motor.cola_inmediata.append(OperarNodo(nodo_id="NO-EXISTE"))
    motor.cola_inmediata.append(FijarReglasEmpleoSector())
    r = motor.paso(franja="dia")
    assert len(r.resultados) == 2
    assert not r.resultados[0][1].ok
    assert r.resultados[1][1].ok


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
        FijarReglasEmpleoSector(), lambda e: False, "nunca se cumple"
    )
    for _ in range(P.CADUCIDAD_ORDEN_CONDICIONAL + 2):
        motor.paso()
    assert not motor.acciones_condicionales


def test_una_condicion_que_revienta_no_tumba_el_turno(motor):
    def explota(estado):
        raise RuntimeError("condición rota")

    motor.encolar_condicional(FijarReglasEmpleoSector(), explota, "revienta")
    r = motor.paso(franja="dia")
    assert any(e.get("tipo") == "condicional_descartada" for e in r.eventos)


def test_la_misma_semilla_da_la_misma_corrida():
    """La corrida se repite en el debriefing con una decisión cambiada."""
    def correr():
        e = cargar_estado()
        m = MotorCrisis(e, semilla=4242)
        for t in range(1, 4):
            m.encolar(OperarNodo(nodo_id="N003", tipo_unidad="esmad"))
            m.paso(franja="dia")
            m.paso(franja="noche")
        return m.metricas()

    assert correr() == correr()


# ===========================================================================
# LAS SIETE VISTAS
# ===========================================================================

def test_los_siete_roles_tienen_vista(estado):
    assert len(views.ROLES) == 7
    for rol in views.ROLES:
        v = views.vista(estado, rol)
        assert v["detalle"], rol
        assert v["alerta"], rol


def test_cada_vista_cabe_en_una_pantalla(estado):
    """
    Si hay que hacer scroll, está mal diseñada — y la gente mirará la pantalla
    en vez de a las otras seis personas.

    EL TOPE SUBIÓ DE SIETE A ONCE, y no es una rebaja de la regla: es la cuenta
    de que dos carteras se repartieron entre cinco. El Interior heredó el
    registro de infraestructura y Defensa los equipos de terreno, así que sus
    pantallas llevan hoy lo que antes se repartía en cuatro. Si esto sigue
    subiendo, lo que hay que revisar no es el número: es si el reparto de
    `docs/historial/resueltos.md` dejó a alguien con dos oficios.
    """
    for rol in views.ROLES:
        v = views.vista(estado, rol)
        assert len(v["detalle"]) <= 11, f"{rol} tiene {len(v['detalle'])} bloques"
        assert len(v["alerta"]) < 260, rol


# ---------------------------------------------------------------------------
# Mirar no cambia nada
#
# Las cuatro nacen del mismo fallo: `estimar_nodo` tiraba el dado en el momento
# de MIRAR, y la API le pasaba el dado del motor. Refrescar movía los números y
# —lo grave— movía la corrida.
# ---------------------------------------------------------------------------

def test_mirar_dos_veces_da_lo_mismo(estado, motor):
    """
    Refrescar la pantalla no puede mover un número.

    Es el síntoma por el que se encontró todo esto: el parte de Interior cambiaba
    solo por pulsar F5, y una fuente que se contradice sola es una fuente que
    nadie lleva a la mesa.
    """
    motor.paso(franja="dia")
    assert views.todas(estado) == views.todas(estado) == views.todas(estado)


def test_mirar_no_gasta_azar_de_la_corrida(estado, motor):
    """
    El precio invisible del mismo fallo, y el grave.

    Si una lectura consume el `rng` del motor, el resultado de la corrida pasa a
    depender de cuántas veces alguien refrescó su pantalla — y entonces la
    semilla no sirve para repetir la corrida con una decisión cambiada, que es la
    mejor herramienta del debriefing.
    """
    motor.paso(franja="dia")
    antes = motor.rng.getstate()
    for _ in range(5):
        views.todas(estado)
    assert motor.rng.getstate() == antes


def test_la_lectura_es_un_hecho_del_turno_en_que_se_hizo(estado):
    """
    La misma fuente, el mismo punto y el mismo turno dan siempre lo mismo. Turnos
    distintos dan lecturas distintas, que es lo correcto: cada turno la fuente
    vuelve a mirar.
    """
    n = next(iter(estado.nodos.values()))
    a = information.estimar_nodo(n, "equipo_terreno", 2, estado.semilla)
    b = information.estimar_nodo(n, "equipo_terreno", 2, estado.semilla)
    c = information.estimar_nodo(n, "equipo_terreno", 5, estado.semilla)

    assert a.estructura_organizada == b.estructura_organizada
    assert a.estructura_organizada != c.estructura_organizada


def test_lo_constatado_en_terreno_se_queda_quieto(estado, motor):
    """
    Lo que un equipo constató en el turno 0 tiene que seguir diciendo lo mismo en
    el turno 3. Si se recalcula con el turno actual, «constatado» no significa
    nada.

    Ojo con el turno 0: es un turno, no un `None`. La primera versión del guardia
    usaba `or` y el turno 0 caía por falsy, que es justo el caso de un punto
    verificado antes de empezar.
    """
    nodo = next(iter(estado.nodos.values()))
    information.marcar_verificado(estado, nodo, "equipo_terreno", estado.turno)

    def constatado():
        v = views.vista(estado, "Defensa")
        return v["detalle"]["lo_que_han_constatado"]

    primero = constatado()
    assert primero, "el punto verificado tiene que aparecer"

    motor.paso(franja="dia")
    motor.paso(franja="noche")
    motor.paso(franja="dia")

    assert constatado() == primero


def test_solo_agricultura_ve_los_dias_exactos(estado):
    """
    El tablero muestra un semáforo; los días son de Agricultura desde que el
    Ministerio de Minas salió del ejercicio. Si el dato estuviera en los dos
    sitios, el rol se consultaría una vez y después sobraría.
    """
    publico = estado.vista_publica()
    for r in publico["regiones"]:
        assert "semaforo" in r
        assert "dias_oxigeno" not in r

    agro = views.vista(estado, "Agricultura")
    assert agro["detalle"]["calendario_por_region"][0]["oxigeno_dias"] is not None


def test_solo_transporte_ve_que_punto_bloquea_cada_corredor(estado):
    t = views.vista(estado, "Transporte")
    assert any(c["bloqueado_en"] for c in t["detalle"]["mapa_vivo"])


def test_los_sesgos_van_en_direcciones_opuestas(estado):
    """
    Cuando dos roles ven el mismo hecho, sus sesgos van en direcciones opuestas.
    Si fueran en la misma, compartir no aportaría nada y la vista sería decoración.
    """
    assert P.SESGO_FUENTE["inteligencia_defensa"] > 0
    assert P.SESGO_FUENTE["parte_municipal"] < 0

    # Y LA TERCERA YA NO ES LIMPIA. Cuando la lectura de terreno la hacía la
    # Defensoría del Pueblo su sesgo era 0,02 y arbitraba entre las otras dos.
    # Ahora es del mismo ministerio que ordena las operaciones: corrige más de la
    # mitad del sesgo de escritorio y sigue tirando hacia el mismo lado.
    assert 0 < P.SESGO_FUENTE["equipo_terreno"] < P.SESGO_FUENTE["inteligencia_defensa"] / 2


# ===========================================================================
# SUSPENDER NO ES RETIRARSE
#
# `comite_disponible` era un pestillo de un solo sentido: se ponía en False al
# bajar de 30 y **nada en todo el motor lo volvía a poner en True**. Medido: una
# sala podía subir la credibilidad a 95 —tres veces el umbral— y el Comité no
# volvía. El propio mensaje de rechazo prometía lo contrario.
#
# Y los dos umbrales declarados hacían lo mismo, así que el de 15 era código
# muerto. Ninguna de las seis estrategias baja nunca de 15, y por eso el fallo
# era invisible para `--comparar`: solo aparece con una sala que intenta
# reparar lo que rompió.
# ===========================================================================

def test_el_comite_vuelve_cuando_la_credibilidad_remonta(estado, motor):
    """La promesa que el propio motor hace al rechazar la convocatoria."""
    estado.reservas.credibilidad_mesa = 22.0
    motor.paso(franja="dia")
    assert not estado.comite_disponible

    estado.reservas.credibilidad_mesa = 31.0
    motor.paso(franja="dia")
    assert estado.comite_disponible
    assert ConvocarMesaNacional().validar(estado).ok


def test_el_comite_no_vuelve_antes_de_cruzar_el_umbral(estado, motor):
    """29 no es 30. Los umbrales son duros en los dos sentidos."""
    estado.reservas.credibilidad_mesa = 22.0
    motor.paso(franja="dia")
    estado.reservas.credibilidad_mesa = 29.0
    motor.paso(franja="dia")
    assert not estado.comite_disponible


def test_por_debajo_del_umbral_definitivo_el_comite_no_vuelve(estado, motor):
    """
    La diferencia entre los dos umbrales que el modelo declaraba y no aplicaba.
    Por debajo de 15 la retirada no se deshace, suba lo que suba después.
    """
    estado.reservas.credibilidad_mesa = 12.0
    motor.paso(franja="dia")
    assert estado.comite_retirado_definitivo

    estado.reservas.credibilidad_mesa = 90.0
    motor.paso(franja="dia")
    assert not estado.comite_disponible, "por debajo de 15 no vuelve nunca"
    assert not ConvocarMesaNacional().validar(estado).ok


def test_los_dos_umbrales_del_comite_hacen_cosas_distintas(estado):
    """
    Si volvieran a hacer lo mismo, el segundo parámetro sobra — y esa fue
    exactamente la forma que tomó el fallo durante varias versiones.
    """
    suspendido = cargar_estado()
    m1 = MotorCrisis(suspendido, semilla=P.SEMILLA_POR_DEFECTO)
    suspendido.reservas.credibilidad_mesa = 20.0
    m1.paso(franja="dia")

    retirado = cargar_estado()
    m2 = MotorCrisis(retirado, semilla=P.SEMILLA_POR_DEFECTO)
    retirado.reservas.credibilidad_mesa = 10.0
    m2.paso(franja="dia")

    for e, m in ((suspendido, m1), (retirado, m2)):
        e.reservas.credibilidad_mesa = 80.0
        m.paso(franja="dia")

    assert suspendido.comite_disponible
    assert not retirado.comite_disponible


def test_la_vuelta_del_comite_se_registra_como_evento(estado, motor):
    """
    Un cambio de esta magnitud que no deja rastro no existe para el debriefing —
    ni para la esfera pública, que narra a partir de los eventos del turno.
    """
    estado.reservas.credibilidad_mesa = 20.0
    r = motor.paso(franja="dia")
    assert any(x.get("tipo") == "comite_suspende" for x in r.eventos)

    estado.reservas.credibilidad_mesa = 40.0
    r = motor.paso(franja="dia")
    assert any(x.get("tipo") == "comite_vuelve" for x in r.eventos)


def test_una_sala_que_repara_su_credibilidad_recupera_la_mesa(estado, motor):
    """
    El caso completo, con el mecanismo real y sin tocar reservas a mano: se
    pierde el Comité operando y se recupera negociando. Es la lección que el
    ejercicio quiere enseñar y que hasta ahora no podía.
    """
    for nid in ("N003", "N004"):
        motor.encolar(OperarNodo(nodo_id=nid, tipo_unidad="esmad"))
        motor.paso(franja="dia")
    assert not estado.comite_disponible, "dos operaciones tumban el Comité"

    motor.encolar(OfrecerContraprestacion())
    motor.encolar(DesplazarseAlEpicentro(acompana="mesa"))
    motor.encolar(PresentarEvidenciaInteligencia(declara_solidez=True))
    motor.paso(franja="dia")

    assert estado.reservas.credibilidad_mesa >= 30.0
    assert estado.comite_disponible, "reparar tiene que servir de algo"


def test_la_mesa_local_de_voceria_fuerte_vuelve_con_el_comite(estado, motor):
    """
    No solo se cae la mesa nacional: `AbrirMesaLocal` sobre puntos con vocería
    alta también la comprueba, y son los que más caudal abren.
    """
    fuerte = max((n for n in estado.nodos.values() if not n.abierto),
                 key=lambda n: n.control_voceria)
    assert fuerte.control_voceria > 0.5

    estado.reservas.credibilidad_mesa = 20.0
    motor.paso(franja="dia")
    accion = AbrirMesaLocal(nodo_id=fuerte.nodo_id, con_alcaldia=True)
    assert not accion.validar(estado).ok

    estado.reservas.credibilidad_mesa = 45.0
    motor.paso(franja="dia")
    assert accion.validar(estado).ok


# ===========================================================================
# SIN TERCERO, EL QUE MIRA ES PARTE
#
# Lo que sustituye a la Defensoría del Pueblo no es otro rol: es una regla. El
# protocolo común de verificación —que adopta el Director de la Policía— es lo
# único que hace que la palabra del que verifica valga, ahora que el que
# verifica es el sector del que se denuncia.
# ===========================================================================

def test_ninguna_fuente_concede_ya_el_grado_confirmado(estado):
    """
    **La invariante de esta versión.** El grado «confirmado» lo otorgaba la dupla
    de la Defensoría, que era la única que miraba sin ser parte. Sin ese rol no
    hay quién lo conceda, y un grado que nadie puede otorgar es una promesa que
    el ejercicio no puede cumplir.

    Si esta prueba se cae es porque alguien le devolvió a una parte la potestad
    de declarar algo confirmado sobre su propia conducta.
    """
    nodo = next(iter(estado.nodos.values()))
    for fuente in information.FUENTES:
        est = information.estimar_nodo(nodo, fuente, 1, estado.semilla)
        assert est.grado == "estimado", (fuente, est.grado)


def test_desmentir_la_denuncia_propia_sin_protocolo_no_da_credibilidad(estado):
    """
    **La sustitución funcional del tercero.**

    Los equipos que verifican son del mismo ministerio que ordena las
    operaciones, y las denuncias son sobre conducta de la fuerza. Sin una regla
    pactada ANTES de saber qué iba a decir, la mesa está oyendo a una parte
    hablar de sí misma — y el desmentido no puede valer lo mismo.
    """
    import copy

    falsa = next(d for d in estado.denuncias if not d.veraz)

    sin = copy.deepcopy(estado)
    information.verificar_denuncia(sin, falsa.denuncia_id)

    con = copy.deepcopy(estado)
    con.banderas.activar("protocolo_verificacion", 0)
    information.verificar_denuncia(con, falsa.denuncia_id)

    assert con.reservas.legitimidad > sin.reservas.legitimidad
    assert con.reservas.credibilidad_mesa > sin.reservas.credibilidad_mesa


def test_confirmar_la_denuncia_propia_sin_protocolo_cuesta_mas(estado):
    """La otra mitad: documentar la propia falta fuera del protocolo no ahorra."""
    import copy

    veraz = next(d for d in estado.denuncias if d.veraz)

    sin = copy.deepcopy(estado)
    information.verificar_denuncia(sin, veraz.denuncia_id)

    con = copy.deepcopy(estado)
    con.banderas.activar("protocolo_verificacion", 0)
    information.verificar_denuncia(con, veraz.denuncia_id)

    assert sin.reservas.respaldo_internacional < con.reservas.respaldo_internacional
    assert sin.reservas.legitimidad < con.reservas.legitimidad


def test_el_estandar_completo_lo_adopta_ahora_el_propio_sector(motor):
    """
    **Los tres mitigadores en una sola acción, y es del que tiene que cumplirlos.**

    Los encendía una acción del Delegado de la Defensoría, que se los EXIGÍA al
    Gobierno; sin ese rol no hay quién los exija. La lección cambia y no se
    pierde: era «un tercero pide más de lo que el sector concede», y es «el
    sector se autolimita, o no lo hace nadie».
    """
    e = motor.estado
    motor.encolar(FijarReglasEmpleoSector())
    motor.paso(franja="dia")
    assert all(e.banderas.mitigadores_activos().values())


# ===========================================================================
# EL ESCENARIO
# ===========================================================================

def test_el_estado_inicial_cumple_sus_invariantes():
    e = cargar_estado()
    assert len(e.nodos) == 10
    assert len(e.corredores) == 4
    assert len(e.regiones) == 4
    assert len(e.esmad_en_reserva()) == P.ESMAD_ESCUADRONES_TOTALES - P.ESMAD_DESPLEGADOS_T0
    assert e.region_epicentro in e.regiones
    # NINGUNA, sin excepción. Había una —`defensoria_presente`— que empezaba en
    # verdadero porque el Delegado ya estaba sentado; sin ese rol, la mesa
    # empieza sin haber constituido absolutamente nada.
    assert not any(v for k, v in vars(e.banderas).items() if isinstance(v, bool))


def test_la_mitad_larga_del_tablero_esta_en_la_ciudad_epicentro():
    """
    **Cinco dentro y cinco fuera.** Es la tensión territorial del caso: lo que se
    ve por la ventana contra lo que solo existe en el tablero, y una sala que
    solo atienda su ciudad deja media logística sin abrir.

    Si el epicentro se quedara con dos o tres, el Alcalde dejaría de tener
    cartera; si se quedara con nueve, las otras tres regiones serían decorado.
    """
    e = cargar_estado()
    dentro = e.nodos_de_region(e.region_epicentro)
    fuera = [n for n in e.nodos.values() if n.region_id != e.region_epicentro]
    assert len(dentro) == 5 and len(fuera) == 5

    # Y uno de los de la ciudad no está en ningún corredor: abrirlo por la
    # fuerza no compra un solo día de autonomía a nadie.
    assert sum(1 for n in dentro if n.corredor_id is None) == 1


def test_ningun_corredor_se_resuelve_con_un_solo_punto():
    """
    Un corredor de un punto no enseña que vale lo que su peor punto: enseña que
    vale lo que su único punto, que es otra cosa y no es la del caso.
    """
    e = cargar_estado()
    for c in e.corredores.values():
        assert len(c.nodos) >= 2, c.corredor_id


def test_todos_los_puntos_tienen_posicion_en_el_mapa():
    """
    El mapa esquemático necesita una posición por punto. No es geografía: es la
    disposición del diagrama de líneas.
    """
    e = cargar_estado()
    for n in e.nodos.values():
        assert (n.x, n.y) != (0.0, 0.0), n.nodo_id


def test_el_territorio_es_ficticio():
    """
    Decisión A1. Un ejercicio sobre hechos con responsabilidad judicial viva no
    debe leerse como un juicio sobre lugares reales.
    """
    e = cargar_estado()
    reales = {"cali", "cauca", "nariño", "narino", "buenaventura", "valle",
              "panamericana", "pasto", "villarrica"}
    for r in e.regiones.values():
        assert r.nombre.lower() not in reales, r.nombre
    for n in e.nodos.values():
        for palabra in reales:
            assert palabra not in n.nombre.lower(), n.nombre


def test_los_puntos_duros_no_tienen_con_quien_hablar():
    """
    El escenario lo reparte así a propósito: los cierres fáciles de pactar son
    blandos y los duros son justamente aquellos donde no hay contraparte. Sin eso
    existiría una respuesta que sirve para todos.
    """
    e = cargar_estado()
    duros = sorted(e.nodos.values(), key=lambda n: -n.dureza)[:5]
    blandos = sorted(e.nodos.values(), key=lambda n: n.dureza)[:5]
    voc_duros = sum(n.control_voceria for n in duros) / 5
    voc_blandos = sum(n.control_voceria for n in blandos) / 5
    assert voc_duros < voc_blandos - 0.2


# ===========================================================================
# El reloj y los deltas — las dos señales que orientan el tablero
# ===========================================================================

def test_el_reloj_recorre_las_cinco_jornadas_de_mayo():
    """
    Cinco jornadas, del 11 al 15 de mayo. **Fecha y nada más.**

    La hora exacta de cada ventana estuvo aquí y se retiró: nadie decide
    distinto por saber que la ventana va de 06:00 a 18:00, y esa línea le
    quitaba sitio en la cabecera a lo único del reloj que sí cambia una
    decisión, que es cuántas jornadas quedan.

    Vive en el motor y no en la interfaz porque diez pantallas calculando cada
    una su propia fecha son diez relojes, y la discrepancia se ve el primer
    turno.
    """
    e = cargar_estado()
    m = MotorCrisis(e)

    assert e.reloj()["fecha"] == "11 de mayo"
    assert e.reloj()["jornada"] == 0            # antes de la apertura
    assert e.reloj()["etiqueta"] == "antes de la apertura"

    esperado = [
        ("dia",   1, "11 de mayo"),
        ("noche", 1, "11 de mayo"),
        ("dia",   2, "12 de mayo"),
        ("noche", 2, "12 de mayo"),
        ("dia",   3, "13 de mayo"),
    ]
    for franja, jornada, fecha in esperado:
        m.paso(franja)
        r = e.reloj()
        assert (r["franja"], r["jornada"], r["fecha"]) == (franja, jornada, fecha)
        assert r["jornadas_restantes"] == P.TURNOS_DECISION - jornada


def test_la_jornada_que_se_delibera_va_por_delante_de_la_resuelta():
    """
    **El tablero dice la jornada que se está jugando, no la que se resolvió.**

    `turno_decision` sube cuando el motor da el paso, esto es, al final del día.
    Durante los trece minutos en que la sala delibera la jornada 2, el motor
    todavía va por la 1 — y una pared que dijera «jornada 1» mientras se decide
    la 2 le da a la sala un turno de más que no tiene.
    """
    e = cargar_estado()
    m = MotorCrisis(e)

    m.abrir_jornada()
    assert (e.turno_decision, e.jornada_visible, e.franja) == (0, 1, "dia")
    assert e.reloj()["jornada"] == 1

    m.cerrar_jornada()
    assert (e.turno_decision, e.jornada_visible, e.franja) == (1, 1, "noche")

    m.abrir_jornada()
    assert (e.turno_decision, e.jornada_visible, e.franja) == (1, 2, "dia")
    assert e.reloj()["fecha"] == "12 de mayo"


def test_abrir_la_jornada_repone_los_equipos_antes_de_decidir():
    """
    El Ministro de Defensa tiene que ver sus tres equipos MIENTRAS decide a dónde
    mandarlas. Reponerlas al resolver le decía durante los trece minutos que no
    le quedaba ninguna.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.abrir_jornada()
    information.consumir_equipo(e, "prueba")
    information.consumir_equipo(e, "prueba")
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES - 2

    m.cerrar_jornada()
    m.abrir_jornada()
    assert e.equipos_disponibles == P.EQUIPOS_TERRENO_TOTALES


def test_cerrar_la_jornada_resuelve_el_dia_y_pasa_la_noche():
    """
    Los dos minutos de consecuencias tienen que enseñar las dos cosas a la vez:
    lo que produjo la orden y lo que produjo la noche. Separarlas obligaba a la
    sala a leer media consecuencia, ponerse a deliberar, y recibir la otra mitad
    a mitad de la conversación siguiente.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.abrir_jornada()
    pasos = m.cerrar_jornada()
    assert [x.franja for x in pasos] == ["dia", "noche"]
    assert e.turno == 2


def test_la_ultima_jornada_no_tiene_noche():
    """
    Nueve ventanas y no diez: el ejercicio cierra con la jornada 5. Después de
    esa no hay noche que sufrir — lo que queda es la proyección.
    """
    e = cargar_estado()
    linea = e.reloj()["linea"]
    assert len(linea) == P.TURNOS_DECISION
    assert [j["fecha"] for j in linea] == ["11", "12", "13", "14", "15"]
    assert all(j["estado"] == "pendiente" for j in linea)
    assert e.reloj()["ventanas_totales"] == P.VENTANAS_TOTALES == 9

    m = MotorCrisis(e)
    for _ in range(P.TURNOS_DECISION):
        m.abrir_jornada()
        pasos = m.cerrar_jornada()
    assert [x.franja for x in pasos] == ["dia"], "la quinta jornada cierra sin noche"
    assert e.turno == P.VENTANAS_TOTALES


def test_la_linea_de_jornadas_marca_la_que_se_esta_jugando():
    e = cargar_estado()
    m = MotorCrisis(e)
    m.abrir_jornada()
    m.cerrar_jornada()
    m.abrir_jornada()
    estados = [j["estado"] for j in e.reloj()["linea"]]
    assert estados == ["cumplida", "actual", "pendiente", "pendiente", "pendiente"]


def test_el_delta_mide_el_ultimo_paso_y_no_la_corrida():
    """
    `Legitimidad 41` no le dice nada a quien no memorizó el punto de partida.
    `41 ▼9` le dice que algo de anoche costó nueve puntos.

    La propiedad que importa: el delta es la diferencia contra el paso ANTERIOR,
    no contra el arranque. Si acumulara, dejaría de señalar en el turno 3.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    assert m.deltas() == {}, "sin historial no hay contra qué comparar"

    m.paso("dia")
    antes = e.reservas.cohesion_mesa
    d1 = m.deltas()
    assert d1["cohesion_mesa"] != 0, "el primer turno compara contra la línea base"

    m.paso("dia")
    d2 = m.deltas()
    assert d2["cohesion_mesa"] == pytest.approx(
        e.reservas.cohesion_mesa - antes, abs=0.05)


def test_el_delta_no_abre_una_puerta_trasera_a_lo_oculto():
    """
    **La invariante más importante de esta capa.** El tablero no muestra la
    mezcla real de un punto ni la veracidad de una denuncia; un delta calculado
    sobre esas magnitudes las filtraría igual de bien que mostrarlas.

    Por eso `_indicadores()` se restringe a lo que `vista_publica()` ya serializa.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.paso("dia")
    m.paso("noche")

    prohibido = ("composicion", "veraz", "veracidad", "estructura",
                 "protesta", "infiltra", "dureza")
    for clave in {**m.deltas(), **m.historial[-1].indicadores}:
        assert not any(p in clave.lower() for p in prohibido), clave

    # Y lo que sí lleva es exactamente lo que la sala ya ve.
    publicas = {"legitimidad", "credibilidad_mesa", "respaldo_internacional",
                "cohesion_mesa", "presion_calle", "muertes_evitables",
                "esmad_sin_comprometer", "puntos_abiertos"}
    caudales = {f"caudal:{c}" for c in e.corredores}
    assert set(m.historial[-1].indicadores) == publicas | caudales


def test_el_mapa_cuenta_lo_que_se_hizo_y_no_donde_esta_la_fuerza():
    """
    **La línea que no se cruza en la capa de hechos del mapa.**

    Que se operó en un punto es un hecho público: sale en las noticias esa misma
    tarde, y la sala necesita verlo para saber si su decisión surtió efecto.

    Dónde está la fuerza AHORA —su ubicación, su asignación, su fatiga— es de la
    Dirección General de la Policía. Si apareciera en el tablero, uno de los nueve
    roles dejaría de hacer falta.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.paso("dia")

    nid = next(iter(e.nodos))
    m.cola_inmediata = [OperarNodo(
        nodo_id=nid, tipo_unidad="esmad",
        responsable_nominado="Ministro de Defensa")]
    m.paso("dia")

    hechos = m.hechos_por_punto()
    assert nid in hechos, "operar deja huella aunque no consiga abrir"
    tipos = {h["tipo"] for h in hechos[nid]}
    assert "operacion" in tipos

    # Ni un solo campo que hable de dónde está o cómo está la fuerza.
    prohibido = ("ubicacion", "asignacion", "fatiga", "unidad_id",
                 "escuadron", "turnos_continuos", "veraz", "composicion")
    for lista in hechos.values():
        for h in lista:
            for clave in h:
                assert clave in MotorCrisis.CAMPOS_DE_HECHO, clave
                assert not any(x in clave.lower() for x in prohibido), clave

    # Y la posición sigue existiendo en el motor: no se ha borrado, se ha callado.
    assert any(u.ubicacion is not None for u in e.unidades)


def test_el_anillo_del_mapa_se_apaga_a_la_ventana_siguiente():
    """
    Los hechos son de la ÚLTIMA ventana, igual que los deltas. Si se acumularan,
    a partir del turno 3 el mapa estaría lleno de anillos y dejaría de señalar.

    La noche vale como ventana: lo que se abrió por la fuerza reabre en ella, y
    eso es precisamente lo que la sala tiene que ver ocurrir.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.paso("dia")

    nid = next(iter(e.nodos))
    m.cola_inmediata = [OperarNodo(
        nodo_id=nid, tipo_unidad="esmad",
        responsable_nominado="Ministro de Defensa")]
    m.paso("dia")
    assert "operacion" in {h["tipo"] for h in m.hechos_por_punto().get(nid, [])}

    m.paso("noche")
    despues = {h["tipo"] for h in m.hechos_por_punto().get(nid, [])}
    assert "operacion" not in despues, "el hecho no se arrastra de una ventana a otra"


def test_cada_marca_del_codigo_apunta_a_un_pendiente_que_existe():
    """
    `PENDIENTES.md` promete navegación en los dos sentidos: del código a la
    explicación y de la explicación al código. Esa promesa **ya se rompió una
    vez** —el marcador de la persistencia decía `B5`, que es el presupuesto de
    latencia— y se rompió en silencio, que es lo peor de una promesa de este
    tipo: no falla nada, simplemente se lee mal.

    La lista es la autoridad. Una marca que no corresponde a ninguna entrada es
    un error, y una entrada sin marca es legítima (no todo pendiente vive en un
    archivo).
    """
    import re

    raiz = pathlib.Path(__file__).resolve().parents[1]
    lista = (raiz / "PENDIENTES.md").read_text(encoding="utf-8")
    entradas = set(re.findall(r"^### ([PABC]\d+) ·", lista, re.M))
    assert entradas, "no se encontró ninguna entrada en PENDIENTES.md"

    marcas: list[tuple[str, str]] = []
    for py in (raiz / "src").rglob("*.py"):
        for n, linea in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            for ident in re.findall(r"PENDIENTE\(([PABC]\d+)\)", linea):
                marcas.append((f"{py.relative_to(raiz)}:{n}", ident))

    huerfanas = [(d, i) for d, i in marcas if i not in entradas]
    assert not huerfanas, f"marcas sin entrada en PENDIENTES.md: {huerfanas}"


def test_el_resumen_de_pendientes_no_se_deja_ninguna_entrada():
    """
    La tabla «En una mirada» es lo único que mucha gente va a leer. Si una
    entrada existe abajo y no aparece arriba, para efectos prácticos no existe
    — que es lo que le pasó a **B6**, el guion de la sesión.
    """
    import re

    lista = (pathlib.Path(__file__).resolve().parents[1]
             / "PENDIENTES.md").read_text(encoding="utf-8")
    resumen = lista[lista.index("## En una mirada"):lista.index("## Cómo verlos")]

    detalladas = set(re.findall(r"^### ([PABC]\d+) ·", lista, re.M))
    # El resumen agrupa rangos: «P1–P4», «C1–C3». Se expanden antes de comparar.
    citadas: set[str] = set()
    for letra, ini, fin in re.findall(
            r"\*\*([PABC])(\d+)(?:[–-](?:[PABC])?(\d+))?\*\*", resumen):
        citadas.update(f"{letra}{n}" for n in range(int(ini), int(fin or ini) + 1))

    assert not detalladas - citadas, (
        f"entradas que existen pero no salen en «En una mirada»: "
        f"{sorted(detalladas - citadas)}")


# ===========================================================================
# H1 — el hecho detonante que la sala recibe
# ===========================================================================

def test_h1_llega_aplicado_y_no_resuelve_nada():
    """
    H1 **ya ocurrió**: la sala lo recibe en el parte heredado, no lo provoca.

    Lo que tiene que hacer es dejar el turno 1 más cargado, no menos. Si el
    hecho detonante resolviera algo —abrir el punto, cerrar una denuncia— el
    ejercicio empezaría con menos decisiones sobre la mesa, que es exactamente
    lo contrario de lo que un paquete detonante existe para hacer.
    """
    e = cargar_estado()
    assert e.hecho_h1, "H1 no se aplicó al cargar"

    nodo = e.nodos[e.hecho_h1["nodo"]]
    assert nodo.proximidad_infra_critica, "H1 debe caer junto a infraestructura crítica"

    # No resuelve: el punto sigue cerrado y nadie lo ha mirado.
    assert not nodo.abierto
    assert nodo.ultima_verificacion_turno is None

    # Sí carga: endurece el punto e inmoviliza fuerza en la instalación.
    assert nodo.dureza > 0.77, "el punto se endurece tras el incidente"
    custodia = [u for u in e.unidades if u.asignacion == "custodia"]
    assert len(custodia) == 3
    assert {u.ubicacion for u in custodia} == {nodo.nodo_id}
    assert e.instalaciones_criticas


def test_h1_cae_donde_la_via_pactada_casi_no_existe():
    """
    **Por qué `N013` y no otro.** El punto tiene que hacer cara la respuesta
    evidente. Si H1 cayera donde se puede concertar barato, no ofrecería ningún
    dilema: se pacta y se sigue.

    Las tres condiciones, las tres ya en los datos del escenario.
    """
    e = cargar_estado()
    nodo = e.nodos[e.hecho_h1["nodo"]]

    # 1 · casi no hay con quién concertar
    assert nodo.control_voceria < 0.35

    # 2 · mayoría de protesta legítima → operar cuesta el doble
    assert nodo.composicion_real.protesta_legitima > P.UMBRAL_PROTESTA_CIVIL

    # 3 · en el epicentro, y sobre un corredor que otra cartera necesita
    assert nodo.region_id == e.region_epicentro
    assert nodo.corredor_id is not None

    # Y es el más duro de los puntos junto a infraestructura crítica.
    vecinos = [n for n in e.nodos.values() if n.proximidad_infra_critica]
    assert nodo.dureza == max(n.dureza for n in vecinos)


# ===========================================================================
# EL SEMÁFORO DEL REPERTORIO
#
# Cada acción dice si se puede pedir HOY y, si no, qué falta. Antes el
# repertorio era una lista plana, y de sus cinco líneas dos podían llevar tres
# jornadas bloqueadas sin que su titular tuviera forma de saberlo: lo descubría
# dictándola en voz alta y recibiendo el rechazo delante de la mesa.
# ===========================================================================

def test_cada_accion_dice_si_hoy_se_puede_pedir(estado):
    for rol, acciones in catalogo_por_rol(estado).items():
        for a in acciones:
            d = a["disponibilidad"]
            assert d["estado"] in ("disponible", "condicionada", "bloqueada", "hecha"), a
            if d["estado"] != "disponible":
                assert d["requisito"], f"{rol}·{a['accion']} no dice qué falta"


def test_una_accion_trabada_dice_quien_la_destraba(estado):
    """
    Es lo que empuja la conversación de vuelta a la mesa: quien lee «falta
    escolta · Director General de la Policía» sabe a quién pedírselo, y eso pasa
    en voz alta y no en un menú.
    """
    caravana = next(a for a in catalogo_por_rol(estado)["Transporte"]
                    if a["accion"] == "OrganizarCaravana")
    d = caravana["disponibilidad"]
    assert d["estado"] == "bloqueada"
    assert "escolta" in d["requisito"].lower()
    assert any("Policía" in q for q in d["habilitada_por"])


def test_una_constitutiva_vigente_deja_de_pedirse(estado):
    def semaforo():
        return next(a["disponibilidad"]["estado"]
                    for a in catalogo_por_rol(estado)["Presidente"]
                    if a["accion"] == "FijarRegistroEscrito")

    assert semaforo() == "disponible"
    estado.banderas.activar("registro_escrito", 1)
    assert semaforo() == "hecha"


def test_el_semaforo_sigue_al_estado_del_mundo(estado):
    """
    Sin ESMAD no se opera, y el repertorio del Ministro de Defensa tiene que
    decirlo ANTES de que lo pida. La sonda busca el objetivo más favorable: si ni
    siquiera ese sale, es que no hay capacidad.
    """
    def semaforo():
        return next(a["disponibilidad"]
                    for a in catalogo_por_rol(estado)["Defensa"]
                    if a["accion"] == "OperarNodo")

    assert semaforo()["estado"] == "disponible"
    for u in estado.unidades:
        if u.tipo == "esmad":
            u.asignacion = "operacion"
    d = semaforo()
    assert d["estado"] == "bloqueada"
    assert "ESMAD" in d["requisito"]
    assert d["habilitada_por"]


def test_el_semaforo_no_estorba_si_algo_revienta(estado):
    """
    Un semáforo roto no puede quitarle a nadie su repertorio. Ante la duda se
    muestra disponible y que el canal de órdenes decida, que es quien valida de
    verdad.
    """
    class Rota(OperarNodo):
        @classmethod
        def sonda(cls, estado):
            raise RuntimeError("sonda rota")

    assert Rota.disponibilidad(estado).estado == "disponible"


def test_el_catalogo_sin_estado_no_lleva_semaforo():
    """El catálogo que ve el modelo dice qué existe, no qué se puede: ahí el
    semáforo sobra y además dependería de un estado que esa llamada no tiene."""
    for acciones in catalogo_por_rol().values():
        assert all("disponibilidad" not in a for a in acciones)


# ===========================================================================
# EL MAPA: LAS SEIS LECTURAS, Y LA GEOMETRÍA QUE LAS SOSTIENE
#
# El mapa dejó de ser un esquema de líneas sobre un lienzo vacío y pasó a dibujar
# un país con sus costas y sus cuatro regiones, cada una teñida de su estado de
# bloqueo. Eso trae dos obligaciones nuevas, y las dos se comprueban aquí:
#
#   1 · LAS CIFRAS SE CALCULAN EN EL MOTOR.  Un promedio por región calculado en
#       JavaScript es un promedio que nadie verifica nunca (`PENDIENTES.md · B9`).
#   2 · UN PUNTO CAE DENTRO DE SU REGIÓN.  Si no, el mapa afirma en una pared que
#       ese bloqueo está en otra parte, y el reparto territorial es justo lo que
#       la sala está mirando ahí.
# ===========================================================================

SEIS = ("caudal", "dureza", "masa_presente", "dias_sostenido",
        "apoyo_local", "control_voceria")


def test_cada_punto_y_cada_region_traen_sus_seis_lecturas(estado):
    v = estado.vista_publica()
    for p in v["puntos"]:
        for clave in SEIS:
            assert p["lectura"][clave]["banda"], f"{p['nodo_id']}·{clave}"
    for r in v["regiones"]:
        for clave in SEIS:
            assert r["lectura"][clave]["banda"], f"{r['region_id']}·{clave}"


def test_las_lecturas_no_llevan_el_numero_interno(estado):
    """
    Un nivel se interpreta; un número se optimiza. Es la misma frontera que en el
    tablero separa «Legitimidad: alta» de «Muertes evitables: 3», y las dos
    únicas cifras que la cruzan son las dos que se cuentan de verdad: personas y
    días. «dureza 0,84» proyectado en una pared convierte la deliberación en
    aritmética sobre qué punto tiene el decimal más bajo.
    """
    permitidos = {"peldano", "de", "aprox", "aprox_por_punto", "dias", "dias_max"}
    for p in estado.vista_publica()["puntos"]:
        for clave in SEIS:
            m = p["lectura"][clave]
            numericos = {k for k, x in m.items()
                         if isinstance(x, (int, float)) and not isinstance(x, bool)}
            assert numericos <= permitidos, (clave, numericos)
            assert isinstance(m["banda"], str)


def test_la_banda_del_caudal_no_contradice_al_chip_del_punto(estado):
    """
    Los cortes del caudal son los del motor y no unos propios: 0,05 es el umbral
    de `Nodo.abierto` y 0,60 el de `_estado_punto`. Con cortes propios habría
    puntos rotulados «cerrado» con el chip en «parcial», y la sala discutiría
    sobre la interfaz en vez de sobre el país.
    """
    for caudal in (0.0, 0.04, 0.05, 0.3, 0.59, 0.6, 0.61, 0.9, 1.0):
        for n in estado.nodos.values():
            n.caudal = caudal
        for p in estado.vista_publica()["puntos"]:
            banda = p["lectura"]["caudal"]["banda"]
            if p["estado"] == "cerrado":
                assert banda == "cerrado", caudal
            elif p["estado"] == "abierto":
                assert banda in ("casi normal", "abierto"), caudal
            elif p["estado"] == "parcial":
                assert banda in ("goteo", "paso parcial"), caudal


def test_el_promedio_de_una_region_se_puede_rehacer_a_mano(estado):
    """
    Media aritmética sin ponderar: cada punto modelado cuenta uno. Podría
    ponderarse por masa presente y sería defendible, pero entonces la cifra
    proyectada dejaría de ser comprobable a ojo por quien la lee — y una cifra
    que nadie puede reconstruir es una autoridad prestada.
    """
    r = estado.regiones["R-BEL"]
    nodos = [n for n in estado.nodos.values() if n.region_id == "R-BEL"]
    lectura = territory.lectura_region(r, nodos)

    media = sum(n.dureza for n in nodos) / len(nodos)
    assert lectura["dureza"]["banda"] == territory.banda(media, P.BANDAS_DUREZA)
    assert lectura["puntos"] == len(nodos)
    assert lectura["masa_presente"]["aprox"] == territory.aprox_personas(
        sum(n.masa_presente for n in nodos))


def test_la_region_cuenta_lo_que_el_promedio_esconde(estado):
    """
    Un caudal medio de 0,5 puede ser dos puntos a la mitad o uno abierto y otro
    cerrado, y no son la misma región. Por eso el estado de bloqueo se calcula
    del RECUENTO de puntos cerrados y no de la media.
    """
    nodos = [n for n in estado.nodos.values() if n.region_id == "R-BEL"]
    r = estado.regiones["R-BEL"]

    for n in nodos:
        n.caudal = 0.5
    a = territory.lectura_region(r, nodos)

    for i, n in enumerate(nodos):
        n.caudal = 1.0 if i % 2 else 0.0
    b = territory.lectura_region(r, nodos)

    assert a["caudal"]["banda"] == b["caudal"]["banda"]      # la media, igual
    assert a["bloqueo"]["banda"] != b["bloqueo"]["banda"]    # el bloqueo, no


def test_una_region_sin_puntos_modelados_lo_dice(estado):
    """
    No es una región en calma: es una región de la que este ejercicio no modela
    ningún cierre. Pintarla verde sería afirmar algo que el motor no sabe.
    """
    lectura = territory.lectura_region(estado.regiones["R-VER"], [])
    assert lectura["sin_puntos_modelados"] is True
    assert "bloqueo" not in lectura


def test_la_masa_se_redondea_y_no_se_inventa():
    """
    Nadie cuenta 337 personas en una glorieta. El escalón crece con el tamaño
    porque el error de una estimación de aforo crece con el aforo.
    """
    assert territory.aprox_personas(337) == 340
    assert territory.aprox_personas(1687) == 1700
    assert territory.aprox_personas(12) == 12
    assert territory.aprox_personas(43) == 43     # ya tiene dos cifras
    assert territory.aprox_personas(0) == 0
    for n in range(0, 6000, 7):
        assert abs(territory.aprox_personas(n) - n) <= max(1, n * 0.055)


def test_la_lectura_publica_no_deja_deducir_la_mezcla_real(estado):
    """
    Seis lecturas nuevas por punto son seis puertas nuevas a la capa 1. Ninguna
    de las seis depende de `composicion_real`: cambiarla entera no mueve ni una
    banda.
    """
    antes = [territory.lectura_nodo(n) for n in estado.nodos.values()]
    for n in estado.nodos.values():
        n.composicion_real = Composicion(0.05, 0.05, 0.90).normalizada()
    assert [territory.lectura_nodo(n) for n in estado.nodos.values()] == antes


# --- la geometría ----------------------------------------------------------

def test_cada_punto_del_escenario_cae_dentro_de_su_region(estado):
    poligonos = estado.geografia["regiones"]
    for n in estado.nodos.values():
        assert territory.dentro(n.x, n.y, poligonos[n.region_id]), n.nodo_id


def test_ninguna_region_se_solapa_con_otra(estado):
    """Un punto dentro de dos polígonos es un punto que el mapa sitúa dos veces."""
    poligonos = estado.geografia["regiones"]
    for n in estado.nodos.values():
        ajenas = [r for r, poly in poligonos.items()
                  if r != n.region_id and territory.dentro(n.x, n.y, poly)]
        assert not ajenas, f"{n.nodo_id} también cae en {ajenas}"


def test_los_cierres_que_el_motor_genera_tambien_caen_dentro(motor):
    """
    La comprobación no puede ser «lo revisó alguien al dibujarlo»: la
    movilización crea cierres nuevos por su cuenta cuando la intensidad sube, y
    esos no los coloca nadie. Antes aterrizaban a catorce unidades del centroide,
    que en una región estrecha es al otro lado de la frontera — o en el mar.
    """
    for _ in range(P.TURNOS_DECISION):
        motor.abrir_jornada()
        motor.cerrar_jornada()

    poligonos = motor.estado.geografia["regiones"]
    nuevos = [n for n in motor.estado.nodos.values() if n.nombre.startswith("Cierre")]
    assert nuevos, "el escenario debería generar algún cierre nuevo en cinco jornadas"
    for n in motor.estado.nodos.values():
        assert territory.dentro(n.x, n.y, poligonos[n.region_id]), n.nodo_id


def test_el_escenario_no_carga_con_un_punto_fuera_de_su_region(tmp_path):
    """
    Una regla que el software garantiza vale más que una que el software
    recomienda. Mover un punto en el JSON sin mirar el mapa tiene que reventar al
    cargar, y no aparecer como un bloqueo dibujado en la región de otro.
    """
    import json
    ruta = pathlib.Path("data/escenario/estado_inicial.json")
    d = json.loads(ruta.read_text(encoding="utf-8"))
    d["nodos"][0]["x"], d["nodos"][0]["y"] = 99, 99      # en el mar, y fuera

    copia = tmp_path / "roto.json"
    copia.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="fuera de su región"):
        cargar_estado(copia)


def test_cada_punto_tiene_su_propio_tamano(estado):
    """
    La masa presente salía de la intensidad de la región y de nada más, así que
    los seis puntos de Bellaflor tenían SIEMPRE la misma cifra exacta de
    personas. Un peaje de carretera y una glorieta del centro no reúnen la misma
    gente, y el término de masa del riesgo de incidente llevaba todo este tiempo
    sin poder distinguirlos. No se veía porque nada mostraba la cifra.
    """
    mobilization.step(estado, _rng())
    masas = {n.masa_presente for n in estado.nodos.values() if n.region_id == "R-BEL"}
    assert len(masas) > 1


def test_las_cuatro_regiones_teselan_el_pais(estado):
    """
    Ni huecos ni solapes: cada trozo de tierra pertenece a exactamente una
    región.

    No es una comprobación cosmética. Un hueco es un trozo del país que el mapa
    pinta sin color y del que la ficha no sabe decir nada; un solape es un punto
    que el mapa sitúa dos veces y una región que se cuenta a sí misma de más.

    Y la construcción lo garantiza —cada frontera interior se usa dos veces, en
    sentidos opuestos— pero garantizarlo por construcción y comprobarlo son cosas
    distintas en cuanto alguien mueva un vértice a mano.
    """
    geo = estado.geografia
    pais = geo["contorno"]
    poligonos = geo["regiones"]

    huecos = dobles = dentro_del_pais = 0
    paso = 1.0
    for i in range(int(100 / paso)):
        for j in range(int(100 / paso)):
            x, y = (i + 0.5) * paso, (j + 0.5) * paso
            if not territory.dentro(x, y, pais):
                continue
            dentro_del_pais += 1
            n = sum(territory.dentro(x, y, p) for p in poligonos.values())
            huecos += n == 0
            dobles += n > 1

    assert dentro_del_pais > 2000, "el contorno no cubre casi nada del lienzo"
    assert huecos == 0, f"{huecos} muestras de tierra sin región"
    assert dobles == 0, f"{dobles} muestras en dos regiones a la vez"


def test_el_contorno_distingue_litoral_de_frontera(estado):
    """
    Por el litoral entra el combustible del país; por la frontera terrestre no
    entra nada que el ejercicio modele. Se dibujan distinto porque significan
    cosas distintas, y los tramos tienen que sumar el contorno entero.
    """
    geo = estado.geografia
    tramos = geo["tramos"]
    assert any(t["frontera"] for t in tramos), "no hay ningún tramo de frontera"
    assert any(not t["frontera"] for t in tramos), "no hay ningún tramo de litoral"

    # Los tramos, encadenados, son el contorno: cada uno acaba donde empieza el
    # siguiente, y el último cierra sobre el primero.
    for a, b in zip(tramos, tramos[1:] + tramos[:1]):
        assert a["puntos"][-1] == b["puntos"][0], "los tramos no encadenan"
    unidos = [p for t in tramos for p in t["puntos"][:-1]]
    assert unidos == geo["contorno"]


def test_ningun_punto_ni_sitio_cae_en_el_mar(estado):
    """El contorno es la costa: un bloqueo dibujado en el agua no es un bloqueo."""
    pais = estado.geografia["contorno"]
    for n in estado.nodos.values():
        assert territory.dentro(n.x, n.y, pais), f"{n.nodo_id} en el mar"
    for s in estado.geografia["sitios"]:
        assert territory.dentro(s["x"], s["y"], pais), f"{s['nombre']} en el mar"


def test_nada_cae_en_el_agua_de_dentro(estado):
    """
    Y tampoco en el estuario, que es la trampa de este mapa.

    El contorno del país **encierra el agua interior**: para repartir el
    territorio entre las cuatro regiones el estuario se rellena, porque un
    agujero dentro del país deja trozos que no pertenecen a ninguna región. De
    modo que `dentro(contorno)` da `True` en mitad del agua, y las dos
    comprobaciones anteriores —la del mar y la de la región— dejan pasar un
    bloqueo dibujado sobre el estrecho.

    Es exactamente la clase de fallo que no revienta nada: el punto se dibuja,
    se puede pinchar, tiene sus seis lecturas, y está en el agua.
    """
    aguas = estado.geografia.get("aguas") or []
    if not aguas:
        return
    for n in estado.nodos.values():
        for a in aguas:
            assert not territory.dentro(n.x, n.y, a), f"{n.nodo_id} en el agua"
    for i in estado.infraestructura.values():
        for a in aguas:
            assert not territory.dentro(i.x, i.y, a), f"{i.infra_id} en el agua"
    for s in estado.geografia["sitios"]:
        for a in aguas:
            assert not territory.dentro(s["x"], s["y"], a), f"{s['nombre']} en el agua"


def test_los_nombres_de_los_mares_caen_en_el_agua(estado):
    """
    Un rótulo de mar sobre tierra firme es la clase de error que nadie ve en el
    código y todo el mundo ve proyectado en una pared.
    """
    pais = estado.geografia["contorno"]
    for m in estado.geografia["mares"]:
        assert not territory.dentro(m["x"], m["y"], pais), m["nombre"]


# ===========================================================================
# LA GUÍA DE ACCIONES
#
# La tabla que cada titular tiene en su tablero individual: de qué tipo es la
# acción, cómo se llama, qué hace, qué hace falta antes y cómo se pide. Tres de
# sus columnas son promesas que hay que sostener con pruebas, porque las tres se
# rompen en silencio: un nombre que se alarga hasta volverse un párrafo no
# revienta nada, un requisito con una cifra dentro tampoco, y un ejemplo que no
# funciona solo se descubre dictándolo delante de la mesa.
# ===========================================================================

def test_las_treinta_y_cuatro_acciones_tienen_ficha_de_guia():
    """Una fila vacía en la guía es un rol que no sabe qué puede pedir."""
    for cls in actions.CATALOGO:
        assert cls in actions.GUIA, cls.__name__
        assert cls.nombre, cls.__name__
        assert cls.requisitos_previos, cls.__name__
        assert cls.en_claro, cls.__name__
        assert cls.descripcion, cls.__name__


def test_el_nombre_de_una_accion_cabe_en_un_renglon():
    """
    **El nombre es un rótulo, no una descripción.** Es lo que el ojo recorre
    para encontrar su fila entre cinco, y lo que se dice en voz alta al pedirla.

    Un nombre que crece hasta las dos líneas deja de servir para eso y duplica a
    `en_claro`, que es la celda de al lado. Seis palabras es holgado —«Escoltar
    una caravana o una misión médica» son seis— y cuarenta y cinco caracteres
    caben en la columna de una tableta.

    Tampoco lleva punto final: un rótulo no es una frase.
    """
    for cls in actions.CATALOGO:
        assert len(cls.nombre) <= 45, (cls.__name__, cls.nombre)
        assert len(cls.nombre.split()) <= 6, (cls.__name__, cls.nombre)
        assert not cls.nombre.endswith("."), (cls.__name__, cls.nombre)


def test_dentro_de_un_rol_no_hay_dos_nombres_iguales():
    """
    Dos filas con el mismo rótulo en la misma pantalla es una guía que no guía.

    Entre roles distintos sí puede repetirse —el Alcalde y el Ministro del
    Interior hacen cosas parecidas con las mesas—, porque nadie ve las dos
    tablas a la vez: cada titular ve la suya.
    """
    catalogo = actions.catalogo_por_rol()
    for rol, fichas in catalogo.items():
        nombres = [f["nombre"] for f in fichas]
        assert len(set(nombres)) == len(nombres), (rol, nombres)


def test_el_requisito_previo_nunca_es_numerico():
    """
    **Cualitativo siempre.** «Escuadrones sin comprometer», no «dos
    escuadrones»; «que el Comité siga sentado», no «credibilidad sobre treinta».

    Con la cifra delante, la sala cuenta hasta el umbral y pide la acción justo
    ahí, y la guía deja de enseñar de qué depende cada cosa para enseñar cuánto
    cuesta. Cuánto falta HOY lo dice el semáforo, que es otra columna y sí mira
    el estado real.
    """
    import re
    for cls in actions.CATALOGO:
        assert not re.search(r"\d", cls.requisitos_previos), (
            f"{cls.__name__} tiene una cifra en su requisito: "
            f"{cls.requisitos_previos!r}")


def test_cada_ejemplo_de_la_guia_produce_su_accion(estado):
    """
    **El ejemplo tiene que funcionar de verdad**, no ser una paráfrasis.

    Se pasan todos por el intérprete determinista —el que corre sin llave— y se
    comprueba que cada uno llega a la acción de cuya ficha salió. Un ejemplo que
    no funciona es peor que no dar ninguno: se dicta en voz alta delante de la
    mesa y la consola contesta que no lo entiende.
    """
    from src.agents import herramientas

    for cls in actions.CATALOGO:
        if not cls.ejemplo_consola:
            continue
        llamadas = herramientas.interpretar_sin_modelo(estado, cls.ejemplo_consola)
        construidas = []
        for l in llamadas:
            spec = herramientas.HERRAMIENTAS[l["nombre"]]
            if spec.get("solo_lectura"):
                continue
            construidas.append(type(spec["construir"](l["argumentos"])).__name__)
        assert cls.__name__ in construidas, (
            f"«{cls.ejemplo_consola}» no produce {cls.__name__}, sino {construidas}")


def test_la_guia_viaja_con_el_catalogo_de_cada_rol(estado):
    """La vista privada la lee de aquí; si no viaja, la tabla sale vacía."""
    catalogo = actions.catalogo_por_rol(estado)
    for rol, fichas in catalogo.items():
        for f in fichas:
            assert "nombre" in f, (rol, f["accion"])
            assert "requisitos_previos" in f, (rol, f["accion"])
            assert "ejemplo_consola" in f, (rol, f["accion"])
            assert "clase" in f and "en_claro" in f


def test_la_guia_que_se_reparte_esta_al_dia():
    """
    **`docs/GUIA_DE_ACCIONES.md` se genera y no se escribe**, y esta prueba es
    la que hace que eso signifique algo.

    Es el documento que se imprime y se pone delante de los participantes. Un
    cuarto sitio con las treinta y cuatro acciones copiadas a mano es un cuarto
    sitio que se desincroniza —y este se desincroniza en el peor momento, que es
    cuando alguien pide en voz alta lo que dice el papel y la consola contesta
    otra cosa.

    Si falla, no hay nada que arreglar a mano:

        uv run python scripts/repertorio.py
    """
    import importlib.util
    from pathlib import Path

    raiz = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "repertorio", raiz / "scripts" / "repertorio.py")
    repertorio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(repertorio)

    escrito = (raiz / "docs" / "GUIA_DE_ACCIONES.md").read_text(encoding="utf-8")
    # Se compara por líneas y no por el texto entero: el final de línea
    # depende de con qué se clonó el repositorio, y eso no es una
    # desincronización.
    assert escrito.splitlines() == repertorio.documento().splitlines(), (
        "docs/GUIA_DE_ACCIONES.md no coincide con el catálogo del motor. "
        "Correr: uv run python scripts/repertorio.py")


# ===========================================================================
# LAS MESAS DE DIÁLOGO — hay que instalarlas cada jornada
# ===========================================================================

def test_una_mesa_instalada_queda_marcada_en_el_punto(motor):
    """El mapa no puede señalar lo que el motor no registra."""
    e = motor.estado
    nodo = next(n for n in e.nodos.values()
                if n.region_id != e.region_epicentro and not n.abierto)
    motor.encolar(actions.AbrirMesaLocal(nodo_id=nodo.nodo_id))
    motor.paso(franja="dia")
    assert nodo.mesa_abierta
    assert nodo.mesa_sesion_turno == e.turno_decision
    assert nodo.jornadas_mesa_congelada == 0


def test_no_instalar_la_mesa_un_dia_congela_la_negociacion(motor):
    """
    **No instalar una mesa un día equivale a congelar las negociaciones.**

    No se pierde lo andado —el progreso no baja— pero tampoco sube, y el reloj
    del ejercicio corre igual. Abrir una mesa en la jornada 4 y no volver a ella
    es no haberla abierto.
    """
    e = motor.estado
    nodo = next(n for n in e.nodos.values()
                if n.region_id != e.region_epicentro and not n.abierto)
    motor.encolar(actions.AbrirMesaLocal(nodo_id=nodo.nodo_id))
    motor.paso(franja="dia")
    avance = nodo.turnos_en_negociacion
    assert avance >= 1

    motor.paso(franja="noche")
    motor.paso(franja="dia")          # una jornada entera sin volver a la mesa

    assert nodo.turnos_en_negociacion == avance, "lo andado no se pierde"
    assert nodo.jornadas_mesa_congelada == 1, "pero tampoco avanza"
    assert not nodo.abierto, "y por tanto no se abre"


def test_la_mesa_congelada_se_anuncia_como_hecho(motor):
    """Si no sale del motor, no sale en el mapa ni en las consecuencias."""
    e = motor.estado
    nodo = next(n for n in e.nodos.values()
                if n.region_id != e.region_epicentro and not n.abierto)
    motor.encolar(actions.AbrirMesaLocal(nodo_id=nodo.nodo_id))
    motor.paso(franja="dia")
    motor.paso(franja="noche")
    r = motor.paso(franja="dia")
    assert any(ev.get("tipo") == "mesa_congelada" and ev.get("nodo") == nodo.nodo_id
               for ev in r.eventos)


def test_dos_sesiones_seguidas_si_abren_el_punto(motor):
    """La otra mitad: instalada cada jornada, la concertación sí rinde."""
    e = motor.estado
    nodo = max((n for n in e.nodos.values()
                if n.region_id != e.region_epicentro and not n.abierto),
               key=lambda n: n.control_voceria)
    for _ in range(2):
        motor.encolar(actions.AbrirMesaLocal(nodo_id=nodo.nodo_id))
        motor.paso(franja="dia")
        motor.paso(franja="noche")
    assert nodo.caudal > 0.0, "dos sesiones producen apertura"
    assert not nodo.mesa_abierta, "y la mesa deja de estar instalada"


def test_el_interior_y_el_alcalde_reciben_la_pregunta_al_abrir_el_dia(motor):
    """
    La notificación del comienzo del día, y **solo para quien puede convocar**.

    El Alcalde ve las de su jurisdicción; el Ministro del Interior, todas. Los
    otros cuatro no reciben nada: una notificación que le llega a quien no puede
    hacer nada con ella es ruido en una pantalla que cabe sin desplazamiento.
    """
    e = motor.estado
    epicentro = next(n for n in e.nodos_de_region(e.region_epicentro)
                     if not n.abierto)
    motor.encolar(actions.InstalarMesaConVoceros(nodo_id=epicentro.nodo_id))
    motor.paso(franja="dia")

    # El mismo día en que se sesionó no hay nada que preguntar.
    assert views.vista(e, "Interior")["notificacion"] is None

    motor.paso(franja="noche")
    motor.abrir_jornada()

    for rol in ("Interior", "Alcalde"):
        n = views.vista(e, rol)["notificacion"]
        assert n is not None, rol
        assert epicentro.nombre in n["pregunta"]
        assert "cada jornada" in n["porque"]

    for rol in ("Presidente", "Defensa", "Policía", "Transporte"):
        assert views.vista(e, rol)["notificacion"] is None, rol


def test_el_alcalde_solo_recibe_las_mesas_de_su_jurisdiccion(motor):
    e = motor.estado
    fuera = next(n for n in e.nodos.values()
                 if n.region_id != e.region_epicentro and not n.abierto)
    motor.encolar(actions.AbrirMesaLocal(nodo_id=fuera.nodo_id))
    motor.paso(franja="dia")
    motor.paso(franja="noche")
    motor.abrir_jornada()

    assert views.vista(e, "Interior")["notificacion"] is not None
    assert views.vista(e, "Alcalde")["notificacion"] is None


# ===========================================================================
# QUÉ SE ESTÁ HACIENDO EN CADA PUNTO
# ===========================================================================

def test_el_mapa_distingue_fuerza_negociacion_y_nada(motor):
    """
    Los tres estados del enunciado, y el que no existía.

    `modo_apertura` solo se escribe cuando el punto cede, así que un punto
    operado que no cedió y un punto que nadie ha tocado salían iguales.
    """
    e = motor.estado
    sin_tocar = e.vista_publica()["puntos"]
    assert all(p["intervencion"] == "ninguna" for p in sin_tocar)

    blando = min((n for n in e.nodos.values() if not n.abierto),
                 key=lambda n: n.dureza)
    otro = max((n for n in e.nodos.values()
                if not n.abierto and n.nodo_id != blando.nodo_id
                and n.region_id != e.region_epicentro),
               key=lambda n: n.control_voceria)

    motor.encolar(actions.OperarNodo(nodo_id=blando.nodo_id, tipo_unidad="esmad"))
    motor.encolar(actions.AbrirMesaLocal(nodo_id=otro.nodo_id))
    motor.paso(franja="dia")

    por_id = {p["nodo_id"]: p for p in e.vista_publica()["puntos"]}
    assert por_id[blando.nodo_id]["intervencion"] == "fuerza"
    assert por_id[otro.nodo_id]["intervencion"] == "negociacion"
    assert por_id[otro.nodo_id]["mesa"]["instalada"]


def test_operar_sin_que_el_punto_ceda_deja_marca_igual(estado):
    """
    La marca que faltaba. Se emplea fuerza, cediera o no cediera: para la calle
    y para el debriefing eso ocurrió, y el mapa no puede pintarlo como un punto
    que nadie ha tocado.
    """
    import random
    from src.engine import territory

    nodo = max((n for n in estado.nodos.values() if not n.abierto),
               key=lambda n: n.dureza)
    nodo.dureza = 1.0
    a = actions.OperarNodo(nodo_id=nodo.nodo_id, tipo_unidad="esmad")
    a.ejecutar(estado, random.Random(1))
    assert nodo.intervencion_fuerza_turno is not None
    assert territory.intervencion_nodo(nodo, estado.jornada_visible) == "fuerza"


def test_la_region_cuenta_que_se_esta_haciendo_en_ella(motor):
    """Un promedio de caudal no distingue cuatro puntos abandonados de cuatro
    con mesa instalada, y no son la misma región."""
    e = motor.estado
    nodo = next(n for n in e.nodos.values()
                if n.region_id != e.region_epicentro and not n.abierto)
    motor.encolar(actions.AbrirMesaLocal(nodo_id=nodo.nodo_id))
    motor.paso(franja="dia")

    region = next(r for r in e.vista_publica()["regiones"]
                  if r["region_id"] == nodo.region_id)
    assert region["lectura"]["intervencion"]["negociacion"] >= 1
    assert region["lectura"]["mesas"]["instaladas"] >= 1


def test_las_metricas_del_cierre_siempre_son_serializables(motor):
    """
    **`inf` no es JSON**, y el caso que lo producía era el más importante.

    `ratio_fuerza_concertacion` valía `float("inf")` cuando la sala había abierto
    por la fuerza y ni una sola vez por concertación — que es exactamente la
    corrida sobre la que más hay que hablar en el debriefing. El endpoint
    contestaba 500 y el cierre se quedaba sin métricas.

    No falló nunca en la suite porque las corridas de prueba pactaban algo.
    """
    import json
    import random

    e = motor.estado
    blando = min((n for n in e.nodos.values() if not n.abierto),
                 key=lambda n: n.dureza)
    blando.dureza = 0.0                      # que ceda seguro
    motor.encolar(actions.OperarNodo(nodo_id=blando.nodo_id, tipo_unidad="esmad"))
    motor.paso(franja="dia")

    m = motor.metricas()
    assert m["aperturas"]["fuerza"] >= 1 and m["aperturas"]["concertacion"] == 0
    assert m["ratio_fuerza_concertacion"] is None
    json.dumps(m)            # lo que hacía FastAPI, y lo que reventaba


# ===========================================================================
# 09 · EL FRENTE AGROALIMENTARIO
#
# El rol que no tiene fuerza ni corredores. Lo que hay que vigilar aquí no es
# que sus acciones funcionen —eso lo cubre la guía— sino las cuatro cosas que lo
# distinguen de las otras ocho carteras y que, si se rompen, lo dejan siendo un
# Ministro de Transporte con otro nombre:
#
#   · su mesa es RURAL y no pisa la jurisdicción del epicentro;
#   · su mesa SOBREVIVE a la salida del Comité del Paro, que es la única razón
#     por la que el rol vale un asiento en el peor día del frente de estrategia;
#   · su lectura del campo va CONTRA la de la inteligencia de Defensa;
#   · el riesgo sanitario que asume no cuesta nada hoy y se cobra al cierre.
# ===========================================================================

def test_agricultura_tiene_vista_alerta_y_seis_acciones(estado):
    v = views.vista(estado, "Agricultura")
    assert v["detalle"] and v["alerta"]
    fichas = actions.catalogo_por_rol(estado)["Agricultura"]
    # Cinco propias más el calendario de agotamiento, que era del Ministerio de
    # Minas y Energía y se quedó en la cartera cuyo daño ya ocurrió.
    assert len(fichas) == 6
    clases = {f["clase"] for f in fichas}
    assert clases == {"constitutiva", "operativa", "informativa"}, clases


def test_la_mesa_tecnica_no_entra_en_la_jurisdiccion_del_epicentro(estado):
    """
    **La frontera del mandato es lo que separa esta mesa de las otras dos.**
    Dentro del epicentro la mesa la instala la Alcaldía, o el Interior con ella.
    Sin esta comprobación, el Ministro de Agricultura acaba pactando cierres
    urbanos, que es exactamente el desborde de competencia que la reasignación
    del reparto de carteras existe para impedir.
    """
    dentro = next(n for n in estado.nodos.values()
                  if n.region_id == estado.region_epicentro and not n.abierto)
    v = actions.InstalarMesaTecnicaAgropecuaria(nodo_id=dentro.nodo_id).validar(estado)
    assert not v.ok
    assert "epicentro" in v.motivo
    assert any("Alcalde" in q for q in v.habilitada_por)


def test_la_mesa_rural_sobrevive_a_la_salida_del_comite(estado):
    """
    **Es la razón por la que el rol vale un asiento.** Cuando el Comité del Paro
    suspende, las mesas locales del Interior caen justo en los puntos de mejor
    vocería —los que responden a él— y el frente de estrategia se queda sin
    canal. La interlocución rural no pasa por el Comité y sigue en pie.

    Si esto se rompiera, Agricultura sería otro modo de hacer lo mismo.
    """
    estado.comite_disponible = False
    rural = max(
        (n for n in estado.nodos.values()
         if not n.abierto and n.region_id != estado.region_epicentro),
        key=lambda n: n.control_voceria)
    assert rural.control_voceria > 0.5, "la prueba necesita un punto de buena vocería"

    del_interior = actions.AbrirMesaLocal(nodo_id=rural.nodo_id).validar(estado)
    assert not del_interior.ok, "el Interior debería quedarse sin este punto"

    de_agricultura = actions.InstalarMesaTecnicaAgropecuaria(
        nodo_id=rural.nodo_id).validar(estado)
    assert de_agricultura.ok


def test_agricultura_y_defensa_leen_el_campo_al_reves(estado):
    """
    Dos personas honestas, el mismo punto rural, y una distancia que no se cierra
    hablando: hay que gastar un equipo. Medido sobre el escenario, la estructura
    real de los puntos rurales es baja y **la que se equivoca de largo ahí es la
    inteligencia**, no ella — y ella no tiene con qué demostrarlo.
    """
    rurales = [n for n in estado.nodos.values()
               if n.region_id != estado.region_epicentro]
    assert rurales
    for n in rurales:
        agro = information.estimar_nodo(
            n, "interlocucion_rural", 0, estado.semilla).estructura_organizada
        defensa = information.estimar_nodo(
            n, "inteligencia_defensa", 0, estado.semilla).estructura_organizada
        assert agro < defensa, n.nombre


def test_la_clase_alimentaria_reetiqueta_un_corredor_hacia_la_region_mas_apretada(motor):
    """No añade capacidad: reordena la que hay, y eso se ve en el tablero."""
    e = motor.estado
    peor = min(e.regiones.values(), key=lambda r: r.dias_autonomia_alimentos)
    antes = {c.corredor_id: set(c.clases_prioridad) for c in e.corredores.values()}

    motor.encolar(actions.FijarClasePrioridadAlimentaria())
    motor.paso(franja="dia")

    assert e.banderas.clase_alimentaria
    nuevos = [c for c in e.corredores.values()
              if "alimentario" in c.clases_prioridad
              and "alimentario" not in antes[c.corredor_id]]
    assert len(nuevos) == 1, [c.nombre for c in nuevos]
    assert any(e.nodos[n].region_id == peor.region_id
               for n in nuevos[0].nodos if n in e.nodos)


def test_llegar_despues_del_criterio_de_transporte_cuesta_mas(estado):
    """
    Entrar en un orden que no existe no es lo mismo que deshacer delante de la
    mesa el que un ministro ya defendió. La diferencia es la fricción declarada
    entre las dos carteras, y tiene que estar en el número.
    """
    import copy, random

    def cohesion_tras(con_criterio):
        e = copy.deepcopy(estado)
        e.banderas.criterio_priorizacion = con_criterio
        antes = e.reservas.cohesion_mesa
        actions.FijarClasePrioridadAlimentaria().ejecutar(e, random.Random(0))
        return antes - e.reservas.cohesion_mesa

    assert cohesion_tras(True) > cohesion_tras(False) > 0


def test_el_riesgo_sanitario_no_cuesta_hoy_y_se_cobra_al_cierre(motor):
    """
    Hermano del riesgo de infraestructura, y por la misma razón: si moviera una
    reserva, la sala jugaría contra el número en vez de decidir. Lo que mide no
    es un daño que ocurrió — es un riesgo que alguien asumió por alguien.
    """
    e = motor.estado
    region = min(e.regiones.values(), key=lambda r: r.dias_autonomia_alimentos)
    reservas_antes = e.reservas.respaldo_internacional

    motor.encolar(actions.ActivarInstrumentosSectoriales(region_id=region.region_id))
    motor.paso(franja="dia")

    assert e.riesgo_sanitario_asumido == 1
    assert e.reservas.respaldo_internacional == reservas_antes
    m = motor.metricas()
    assert m["riesgo_sanitario"]["excepciones_autorizadas"] == 1
    assert region.region_id in m["riesgo_sanitario"]["regiones_con_alivios"]


def test_el_segundo_paquete_de_alivios_rinde_la_mitad(estado):
    """
    «Los instrumentos no alcanzan a compensar a la escala del daño» es una frase
    de la ficha del rol, y aquí es un número: repetir la acción en la misma
    región no la hace alcanzar.
    """
    import random
    rng = random.Random(0)
    region = next(iter(estado.regiones.values()))

    def gana():
        antes = region.dias_autonomia_alimentos
        actions.ActivarInstrumentosSectoriales(
            region_id=region.region_id).ejecutar(estado, rng)
        return region.dias_autonomia_alimentos - antes

    primero = gana()
    segundo = gana()
    assert primero > 0
    assert abs(segundo - primero * P.DECAIMIENTO_ALIVIO_SECTORIAL) < 1e-9


def test_la_cifra_del_campo_se_disputa_sin_protocolo_de_verificacion(estado):
    """El enlace con la Defensoría: su protocolo es lo que hace que la cifra
    sectorial cierre la guerra de números en vez de alimentarla."""
    import copy, random

    def credibilidad_tras(con_protocolo):
        e = copy.deepcopy(estado)
        e.banderas.protocolo_verificacion = con_protocolo
        antes = e.reservas.credibilidad_mesa
        actions.PublicarBalancePerdida().ejecutar(e, random.Random(0))
        return e.reservas.credibilidad_mesa - antes

    assert credibilidad_tras(False) < 0
    assert credibilidad_tras(True) == 0


def test_el_despacho_concentrado_necesita_escolta_y_corredor_alimentario(estado):
    """
    No pide escolta: hace rendir la que ya hay. Un rol sin fuerza propia no puede
    tener una acción que se ejecute sola — si la tuviera, dejaría de empujar la
    conversación de vuelta a la mesa, que es para lo que existe.
    """
    alimentario = next(c for c in estado.corredores.values()
                       if "alimentario" in c.clases_prioridad)
    otro = next(c for c in estado.corredores.values()
                if "alimentario" not in c.clases_prioridad)

    v = actions.AcordarAcopioYVentanas(corredor_id=otro.corredor_id).validar(estado)
    assert not v.ok and "alimentaria" in " ".join(v.requisitos_faltantes)

    v = actions.AcordarAcopioYVentanas(
        corredor_id=alimentario.corredor_id).validar(estado)
    assert not v.ok
    assert "escolta policial" in v.requisitos_faltantes
    assert any("Policía" in q for q in v.habilitada_por)


def test_la_pregunta_de_las_mesas_llega_solo_a_quien_puede_convocarlas(motor):
    """
    Tres carteras convocan mesas y cada una recibe la pregunta por LAS SUYAS. La
    de Agricultura no se define por territorio sino por autoría: sus mesas
    técnicas pueden estar repartidas por tres regiones, y las del Interior no las
    puede convocar ella.
    """
    e = motor.estado
    rural = max(
        (n for n in e.nodos.values()
         if not n.abierto and n.region_id != e.region_epicentro),
        key=lambda n: n.control_voceria)
    motor.encolar(actions.InstalarMesaTecnicaAgropecuaria(nodo_id=rural.nodo_id))
    motor.paso(franja="dia")
    motor.paso(franja="noche")
    motor.abrir_jornada()

    for rol in ("Agricultura", "Interior"):
        n = views.vista(e, rol)["notificacion"]
        assert n is not None, rol
        assert rural.nombre in n["pregunta"]

    # El Alcalde no: el punto no está en su jurisdicción.
    assert views.vista(e, "Alcalde")["notificacion"] is None


# ===========================================================================
# LO QUE SALIÓ DE LA REVISIÓN GENERAL DEL MOTOR
#
# Cuatro defectos que la suite no veía porque nadie le había preguntado. Los
# cuatro son de la misma familia: **una unidad que no coincide con su nombre.**
# Días que contaban tramos, un parámetro que decía turnos y contaba pasos, una
# raíz de tres letras dentro de una frase de dos palabras, y un tamaño de
# paquete escrito a mano al lado de la constante que debía fijarlo.
# ===========================================================================

def test_los_dias_de_cierre_avanzan_un_dia_por_jornada(motor):
    """
    **`step()` corre dos veces al día y este contador se incrementaba en las
    dos.** Un punto con quince días de cierre marcaba veinticinco al terminar un
    ejercicio de cinco jornadas, con la palabra «días» al lado en el mapa.

    No lo notaba nadie porque el número no entra en ningún cálculo: solo se
    dibuja. Y por eso es peor — un dato que solo se enseña es un dato que nadie
    va a contrastar contra nada.
    """
    e = motor.estado
    nodo = next(n for n in e.nodos.values() if not n.abierto)
    antes = nodo.dias_sostenido

    for _ in range(3):
        motor.paso(franja="dia")
        motor.paso(franja="noche")

    assert nodo.abierto or nodo.dias_sostenido == antes + 3, (
        f"{nodo.nombre} pasó de {antes} a {nodo.dias_sostenido} en tres jornadas")


def test_la_banda_de_dias_no_satura_en_la_primera_jornada(motor):
    """
    La consecuencia visible del anterior: con dos días por jornada, todo el
    tablero cruzaba el umbral de «crónico» —quince días— antes de la segunda.
    Una lectura que vale lo mismo en todos los puntos no informa de nada.
    """
    e = motor.estado
    for _ in range(2):
        motor.paso(franja="dia")
        motor.paso(franja="noche")

    bandas = {territory.lectura_nodo(n)["dias_sostenido"]["banda"]
              for n in e.nodos.values()}
    assert len(bandas) > 1, f"todos los puntos leen igual: {bandas}"


def test_pedir_un_despacho_concentrado_no_mueve_el_esmad(estado):
    """
    **El canal no puede añadir una acción que nadie pidió.**

    `concentr` es una raíz de `disponer_esmad` y está dentro de «despacho
    concentrado», que es el acopio agroalimentario. La orden salía con dos
    acciones: la que se pidió y una concentración de ESMAD de regalo.
    """
    from src.agents import herramientas

    for frase in ("acordar el despacho concentrado por el Corredor del Sur",
                  "despacho concentrado de alimentos por el Corredor del Sur"):
        nombres = [l["nombre"]
                   for l in herramientas.interpretar_sin_modelo(estado, frase)]
        assert "acordar_acopio" in nombres, (frase, nombres)
        assert "disponer_esmad" not in nombres, (frase, nombres)


def test_el_tamano_del_paquete_de_denuncias_sale_de_parameters(estado):
    """
    Estaba escrito a mano en tres sitios mientras `DENUNCIAS_POR_PAQUETE`
    existía sin que nadie la leyera. Un parámetro documentado y desconectado es
    peor que ninguno: se calibra, y no mueve nada.
    """
    import random
    antes = len(estado.denuncias)
    information._generar_paquete(estado, random.Random(3))
    assert len(estado.denuncias) - antes == P.DENUNCIAS_POR_PAQUETE

    # Y lo que hace indistinguible un paquete no es que sean dos: es que dentro
    # haya de las dos clases y no se sepa cuál es cuál.
    nuevas = estado.denuncias[antes:]
    assert len({d.veraz for d in nuevas}) == 2, [d.veraz for d in nuevas]


def test_ninguna_constante_de_parameters_queda_sin_leer():
    """
    **Una constante que nadie lee se documenta, se calibra y se discute como si
    moviera algo.** Esta prueba no exige que no haya ninguna: exige que las que
    haya estén DECLARADAS, para que aparecer en esta lista sea una decisión y no
    un descuido.
    """
    import pathlib
    import re

    raiz = pathlib.Path(__file__).resolve().parent.parent
    par = (raiz / "src" / "engine" / "parameters.py").read_text(encoding="utf-8")
    resto = "\n".join(
        f.read_text(encoding="utf-8")
        for f in list((raiz / "src").rglob("*.py")) + list((raiz / "scripts").rglob("*.py"))
        if f.name != "parameters.py" and "__pycache__" not in str(f)
    )

    # Las que se sabe que no las lee el motor, y por qué.
    DECLARADAS = {
        # Reparto de la sesión en la sala: los minutos de instalación y de
        # debriefing no los conduce el reloj del ejercicio, que solo corre las
        # cinco jornadas. Viven aquí porque son del mismo cuadro de tiempos.
        "MIN_INSTALACION", "MIN_DEBRIEFING",
        # El redespliegue militar inmoviliza por unidad y no por instalación,
        # así que su gemela policial se usa y esta no. Ver la revisión general.
        "CUSTODIA_MILITARES_POR_INSTALACION",
    }

    huerfanas = {
        c for c in set(re.findall(r"^([A-Z][A-Z0-9_]{2,})\s*[:=]", par, re.M))
        if not re.search(r"\b%s\b" % re.escape(c), resto)
    } - DECLARADAS
    assert not huerfanas, f"constantes sin leer y sin declarar: {sorted(huerfanas)}"


def test_las_treinta_y_nueve_acciones_se_pueden_pedir_por_la_consola():
    """
    **Las 39, sin excepción.** Ocho no se podían hasta que se cerró `B10`.

    La consola es la ÚNICA entrada al motor durante una sesión: una acción sin
    herramienta existe, se ejecuta y está probada, pero con gente en la sala se
    acuerda de palabra y no se transcribe. Que el motor la tenga no significa
    que el ejercicio la tenga.

    Cada una necesita las tres cosas y la prueba mira las tres: una herramienta
    que la construya, un disparador que la alcance sin llave, y un ejemplo en su
    ficha. Añadir la cuarenta sin una de ellas para aquí.
    """
    from src.agents import herramientas

    por_accion = {}
    for nombre, spec in herramientas.HERRAMIENTAS.items():
        if spec.get("solo_lectura"):
            continue
        clase = type(spec["construir"](spec.get("por_defecto", {}))).__name__
        por_accion[clase] = nombre

    sin_canal = sorted(c.__name__ for c in actions.CATALOGO
                       if c.__name__ not in por_accion)
    assert sin_canal == [], f"existen en el motor y no se pueden pedir: {sin_canal}"

    con_disparador = {n for n, _, _ in herramientas.DISPARADORES}
    for cls in actions.CATALOGO:
        assert por_accion[cls.__name__] in con_disparador, cls.__name__
        assert cls.ejemplo_consola, cls.__name__


def test_ningun_ejemplo_de_la_guia_arrastra_una_accion_de_mas(estado):
    """
    **La contraparte de `test_cada_ejemplo_de_la_guia_produce_su_accion`**, que
    solo miraba que la suya estuviera y no que fuera la única.

    Por ahí se colaban dos: «clasificar el parte OPERacional» disparaba además
    una operación de desbloqueo, y «acordar el despacho CONCENTRado» una
    concentración de ESMAD. Una acción de más no es un error de comprensión: es
    una orden que nadie dio, y llega al pliego firmada por su rol.
    """
    from src.agents import herramientas

    for cls in actions.CATALOGO:
        construidas = []
        for l in herramientas.interpretar_sin_modelo(estado, cls.ejemplo_consola):
            spec = herramientas.HERRAMIENTAS[l["nombre"]]
            if spec.get("solo_lectura"):
                continue
            construidas.append(type(spec["construir"](l["argumentos"])).__name__)
        assert construidas == [cls.__name__], (
            f"«{cls.ejemplo_consola}» produce {construidas}")


def test_ningun_ejemplo_de_la_guia_se_rechaza_en_la_primera_jornada(estado):
    """
    **Un ejemplo que se entiende y se rechaza es peor que uno que no se
    entiende**, porque parece que el sistema falla y lo que falla es la ficha.
    Se dicta en voz alta en la primera jornada, delante de la mesa.

    Salieron dos al barrer los treinta y nueve:

    - `DeclararInfraestructuraCritica` traía `["refineria"]` como valor por
      defecto, y **la refinería empieza el escenario custodiada**: la orden
      construía la acción correcta y se rechazaba siempre.
    - `AcordarPasosSeguros` pedía el paso en el punto con MENOS vocería del
      escenario, que es justo donde no hay con quién acordarlo.

    Las dos que quedan no son un defecto de la ficha: son la interdependencia
    del ejercicio. La escolta la pone la Policía, y hasta que la pone, ni la
    caravana de Transporte ni el acopio de Agricultura pueden salir. Por eso
    están declaradas aquí y no silenciadas.
    """
    from src.agents import herramientas, nlu

    NECESITAN_ESCOLTA = {"OrganizarCaravana", "AcordarAcopioYVentanas"}

    rechazadas = {}
    for cls in actions.CATALOGO:
        # Por el cauce entero: el intérprete cita el nombre TAL CUAL y quien lo
        # resuelve es `_a_accion_plan`. Comprobarlo antes de resolver mediría
        # otra cosa —«no existe el punto Puente Amarillo»— y no lo que la sala ve.
        llamada = herramientas.interpretar_sin_modelo(
            estado, cls.ejemplo_consola)[0]
        ap = nlu._a_accion_plan(estado, llamada, cls.ejemplo_consola)
        spec = herramientas.HERRAMIENTAS[ap.herramienta]
        v = spec["construir"](ap.argumentos).validar(estado)
        if not v.ok:
            rechazadas[cls.__name__] = v.motivo

    inesperadas = {k: v for k, v in rechazadas.items()
                   if k not in NECESITAN_ESCOLTA}
    assert not inesperadas, f"ejemplos que se rechazan en t=0: {inesperadas}"
    assert set(rechazadas) == NECESITAN_ESCOLTA, sorted(rechazadas)


def test_las_ocho_llaves_nuevas_no_le_roban_la_orden_a_su_vecina(estado):
    """
    **Cada una de las ocho tiene una vecina cuya raíz lleva dentro**, y ese es
    el modo de falla que ya se cobró dos veces en este archivo.

    Las tres que importan, porque en las tres cambia el ROL que firma:
    adoptar el protocolo de verificación no despliega equipos al terreno;
    acordar pasos seguros no es el acopio agroalimentario; e ir al epicentro
    acompañando la operación no ordena ninguna operación.

    LA CUARTA SE RESOLVIÓ SOLA AL IRSE LA DEFENSORÍA. «Reglas de empleo» tenía
    dos dueños —el sector que las adoptaba y el tercero que las exigía— y la
    regla de la raíz más larga era lo que los separaba. Con la acción del
    tercero retirada, las dos frases van a la misma y única acción, que es
    justo lo que tiene que pasar.
    """
    from src.agents import herramientas

    def nombres(frase):
        return [l["nombre"]
                for l in herramientas.interpretar_sin_modelo(estado, frase)]

    assert nombres("adoptar el protocolo unico de verificacion") == [
        "adoptar_protocolo_verificacion"]
    assert nombres("acordar una sola forma de verificar") == [
        "adoptar_protocolo_verificacion"]
    assert nombres("fijar las reglas de empleo del sector") == [
        "fijar_reglas_sector"]
    assert nombres("ir al epicentro acompanando la operacion") == [
        "ir_al_epicentro"]
    assert nombres("acordar pasos seguros en el Puente Amarillo") == [
        "acordar_pasos_seguros"]

    # Y al revés: la vecina sigue siendo alcanzable, que es lo que una exclusión
    # de texto entero habría roto en cuanto se pidieran las dos en un mensaje.
    assert nombres("desplegar equipos de terreno en el Puente Amarillo") == [
        "desplegar_equipos"]

    # Las dos formas de pedir el estándar llegan ahora a la misma acción: la
    # adopta el sector y ya no se la exige nadie.
    assert nombres("exigir los estandares de empleo de la fuerza") == [
        "fijar_reglas_sector"]
    assert nombres("que los agentes vayan con identificacion de agentes") == [
        "fijar_reglas_sector"]


def test_lo_que_la_sala_oye_de_las_ocho_acciones_nuevas(estado):
    """
    **Tres de las ocho llevan un booleano que cambia lo que el motor cobra**, y
    ninguno se decía. Un valor por defecto que se ejecuta y no se lee en voz
    alta es la sala confirmando una cosa y el motor haciendo otra.
    """
    from src.agents import nlu

    def leer(frase):
        return nlu.interpretar(estado, frase, "p").acciones[0]

    a = leer("reunir a los alcaldes de las ciudades criticas")
    assert a.argumentos["concede_prioridad"] is False
    assert "SIN conceder prioridad" in a.en_claro()

    a = leer("presentar la evidencia de inteligencia")
    assert a.argumentos["declara_solidez"] is False
    assert "SIN declarar" in a.en_claro()

    a = leer("publicar el parte municipal de la ciudad")
    assert a.argumentos["disputa_cifra"] is True
    assert "disputando la cifra nacional" in a.en_claro()

    a = leer("ir al epicentro en persona")
    assert a.argumentos["acompana"] == "ninguna"
    assert "sin acompanar" in a.en_claro().replace("ñ", "n")


def test_validar_no_muta_el_estado(estado):
    """
    **Está escrito en la cabecera de `actions.py` y no lo comprobaba nadie.**

    Importa por el semáforo: `disponibilidad()` llama a `validar()` para las
    treinta y nueve acciones cada vez que alguien abre su tablero. Si una sola
    mutara, mirar la pantalla cambiaría la corrida — y con nueve dispositivos
    refrescando, la partida dependería de quién mira y cuándo.
    """
    import copy

    def huella(e):
        return (
            [(n.nodo_id, round(n.caudal, 6), round(n.dureza, 6), n.modo_apertura,
              n.mesa_abierta, n.turnos_en_negociacion, n.dias_sostenido)
             for n in e.nodos.values()],
            [(u.tipo, u.asignacion, u.ubicacion, round(u.fatiga, 6))
             for u in e.unidades],
            tuple(round(getattr(e.reservas, k), 6) for k in
                  ("legitimidad", "credibilidad_mesa",
                   "respaldo_internacional", "cohesion_mesa")),
            e.equipos_disponibles, len(e.eventos_turno), len(e.acuerdos),
            sorted((c.corredor_id, tuple(sorted(c.clases_prioridad)))
                   for c in e.corredores.values()),
            {k: v for k, v in vars(e.banderas).items() if isinstance(v, bool)},
        )

    for cls in actions.CATALOGO:
        e = copy.deepcopy(estado)
        antes = huella(e)
        (cls.sonda(e) or cls()).validar(e)
        cls.disponibilidad(e)
        assert huella(e) == antes, f"{cls.__name__} muta el estado al validarse"
