"""
test_invariantes.py — Verificadores sin modelo.

Comprueban propiedades estructurales y de comportamiento sin consumir tokens.
Corren en décimas de segundo y se ejecutan en cada cambio.

Cada prueba de este archivo existe porque su propiedad **se rompió alguna vez** o
porque su ruptura sería silenciosa — que es la peor clase de fallo: el ejercicio
pierde su objeto sin que nada reviente ruidosamente.
"""

from __future__ import annotations

import random

import pytest

from src.engine import parameters as P
from src.engine import aperture, force, information, views
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis
from src.engine.state import Composicion
from src.engine.actions import (
    OperarNodo, AbrirMesaLocal, AsignarDuplas, ExigirEstandaresEmpleo,
    ExigirProtocoloVoceria, AdoptarCriterioPriorizacion, Escoltar,
    FijarPrioridadCombustible, ConvocarMesaNacional, ManifestarDudaPermanencia,
    InstalarMesaConVoceros, DisponerESMAD,
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
    error doble desaparece y la Defensoría se queda sin oficio.
    """
    texto = repr(estado.vista_publica())
    assert "composicion_real" not in texto
    assert "protesta_legitima" not in texto
    assert "estructura_organizada" not in texto


def test_las_ocho_vistas_privadas_tampoco_la_exponen(estado):
    """La vista privada es de alta resolución, no de capa 1."""
    for rol in views.ROLES:
        texto = repr(views.vista(estado, rol, _rng()))
        assert "composicion_real" not in texto, rol
        assert "protesta_legitima" not in texto, rol


def test_ninguna_vista_revela_la_veracidad_de_una_denuncia(estado):
    """
    Nada distingue una denuncia cierta de una falsa. Si el campo `veraz` se
    filtrara, la decisión de gastar una dupla dejaría de existir.
    """
    assert "veraz" not in repr(estado.vista_publica())
    for rol in views.ROLES:
        assert "'veraz'" not in repr(views.vista(estado, rol, _rng())), rol


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
    no puede saberlo sin haber gastado una dupla ahí.
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
    turno, Minas no tendría ninguna palanca continua sobre el reloj.
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
        estado, nodo, "esmad", dupla_presente=True, concertado_con_alcaldia=True
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
        estado, nodo, "militar", dupla_presente=True, concertado_con_alcaldia=True
    )
    assert ev.p_incidente > 0.55


def test_la_banda_de_riesgo_se_puede_leer_antes_de_decidir(estado):
    """La sala gestiona riesgo, no sorpresa: la banda existe antes de ejecutar."""
    ev = force.evaluar_riesgo(estado, estado.nodos["N003"], "esmad")
    assert ev.banda in ("baja", "media", "alta", "critica")
    assert "mitigadores ausentes" in ev.resumen()


# ===========================================================================
# LAS DUPLAS SALEN DE UN SOLO BOLSILLO
# ===========================================================================

def test_las_duplas_son_tres_y_se_reponen_cada_turno(motor):
    e = motor.estado
    motor.paso(franja="dia")
    assert e.duplas_disponibles == P.DUPLAS_TOTALES
    information.consumir_dupla(e, "prueba")
    assert e.duplas_disponibles == P.DUPLAS_TOTALES - 1
    motor.paso(franja="noche")
    assert e.duplas_disponibles == P.DUPLAS_TOTALES - 1, "de noche no se reponen"
    motor.paso(franja="dia")
    assert e.duplas_disponibles == P.DUPLAS_TOTALES


def test_acompanar_una_operacion_gasta_una_dupla(motor):
    """
    LA FUGA QUE ANTES EXISTÍA. Acompañar era una casilla gratis: la sala podía
    marcarla en todas las operaciones mientras la Defensoría verificaba aparte.
    """
    e = motor.estado
    antes = e.duplas_disponibles
    motor.encolar(OperarNodo(nodo_id="N010", tipo_unidad="esmad", dupla_presente=True))
    motor.paso(franja="dia")
    assert e.duplas_disponibles < antes


def test_verificar_aqui_es_no_verificar_alla(motor):
    """Tres duplas, veinticuatro puntos. Lo que no alcanza se informa."""
    e = motor.estado
    motor.encolar(AsignarDuplas(
        nodos=["N001", "N002", "N003", "N004", "N005"]
    ))
    r = motor.paso(franja="dia")
    _, res = r.resultados[0]
    assert res.ok
    assert len(res.datos["verificados"]) == P.DUPLAS_TOTALES
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
    motor.cola_inmediata.append(ExigirEstandaresEmpleo())
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
        ExigirEstandaresEmpleo(), lambda e: False, "nunca se cumple"
    )
    for _ in range(P.CADUCIDAD_ORDEN_CONDICIONAL + 2):
        motor.paso()
    assert not motor.acciones_condicionales


def test_una_condicion_que_revienta_no_tumba_el_turno(motor):
    def explota(estado):
        raise RuntimeError("condición rota")

    motor.encolar_condicional(ExigirEstandaresEmpleo(), explota, "revienta")
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
# LAS OCHO VISTAS
# ===========================================================================

def test_los_ocho_roles_tienen_vista(estado):
    assert len(views.ROLES) == 8
    for rol in views.ROLES:
        v = views.vista(estado, rol, _rng())
        assert v["detalle"], rol
        assert v["alerta"], rol


def test_cada_vista_cabe_en_una_pantalla(estado):
    """
    Dos bloques y nada más. Si hay que hacer scroll, está mal diseñada — y la
    gente mirará la pantalla en vez de a las otras siete personas.
    """
    for rol in views.ROLES:
        v = views.vista(estado, rol, _rng())
        assert len(v["detalle"]) <= 7, f"{rol} tiene {len(v['detalle'])} bloques"
        assert len(v["alerta"]) < 260, rol


def test_solo_minas_ve_los_dias_exactos(estado):
    """
    El tablero muestra un semáforo; los días son de Minas. Si el dato estuviera en
    los dos sitios, el rol se consultaría una vez y después sobraría.
    """
    publico = estado.vista_publica()
    for r in publico["regiones"]:
        assert "semaforo" in r
        assert "dias_oxigeno" not in r

    minas = views.vista(estado, "Minas", _rng())
    assert minas["detalle"]["calendario_por_region"][0]["oxigeno_dias"] is not None


def test_solo_transporte_ve_que_punto_bloquea_cada_corredor(estado):
    t = views.vista(estado, "Transporte", _rng())
    assert any(c["bloqueado_en"] for c in t["detalle"]["mapa_vivo"])


def test_los_sesgos_van_en_direcciones_opuestas(estado):
    """
    Cuando dos roles ven el mismo hecho, sus sesgos van en direcciones opuestas.
    Si fueran en la misma, compartir no aportaría nada y la vista sería decoración.
    """
    assert P.SESGO_FUENTE["inteligencia_defensa"] > 0
    assert P.SESGO_FUENTE["parte_municipal"] < 0
    assert abs(P.SESGO_FUENTE["dupla_defensoria"]) < 0.05


# ===========================================================================
# LA DEFENSORÍA NO SE RETIRA
# ===========================================================================

def test_la_defensoria_no_se_retira_pero_puede_dudar(motor):
    """
    Decisión A3. Su palanca no es irse: es decir en voz alta que se lo está
    pensando — y eso cuesta legitimidad y respaldo internacional.
    """
    e = motor.estado
    antes = (e.reservas.legitimidad, e.reservas.respaldo_internacional)
    motor.encolar(ManifestarDudaPermanencia())
    motor.paso(franja="dia")
    assert e.banderas.defensoria_presente, "la Defensoría no puede retirarse"
    assert e.reservas.legitimidad < antes[0]
    assert e.reservas.respaldo_internacional < antes[1]


def test_la_duda_de_permanencia_se_gasta_con_el_uso(estado):
    """
    La primera vez pesa, la tercera es ruido. Su credibilidad ante ambas partes
    es un activo que se consume con cada uso.

    Se mide la acción aislada, sin avanzar el turno: si se midiera dentro de un
    paso, los demás eventos moverían la misma reserva y la comparación no diría
    nada sobre la acción.
    """
    caidas = []
    for _ in range(3):
        antes = estado.reservas.respaldo_internacional
        ManifestarDudaPermanencia().ejecutar(estado, _rng())
        caidas.append(antes - estado.reservas.respaldo_internacional)
    assert caidas[0] > caidas[1] > caidas[2]
    assert estado.dudas_permanencia == 3


# ===========================================================================
# EL ESCENARIO
# ===========================================================================

def test_el_estado_inicial_cumple_sus_invariantes():
    e = cargar_estado()
    assert len(e.nodos) == 24
    assert len(e.corredores) == 5
    assert len(e.regiones) == 4
    assert len(e.esmad_en_reserva()) == P.ESMAD_ESCUADRONES_TOTALES - P.ESMAD_DESPLEGADOS_T0
    assert e.region_epicentro in e.regiones
    assert not any(v for k, v in vars(e.banderas).items()
                   if isinstance(v, bool) and k != "defensoria_presente")


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
    Cinco jornadas del 11 al 15 de mayo en turnos de doce horas que alternan día
    y noche (docs/propuesta.md § 2.7). La noche cruza la medianoche.

    Vive en el motor y no en la interfaz porque cuatro superficies calculando
    cada una su propia hora son cuatro relojes, y en una sala con dos proyectores
    la discrepancia se ve el primer turno.
    """
    e = cargar_estado()
    m = MotorCrisis(e)

    assert e.reloj()["fecha"] == "11 de mayo"
    assert e.reloj()["jornada"] == 0            # antes de la apertura

    esperado = [
        ("dia",   1, "11 de mayo", "06:00", 0),
        ("noche", 1, "11 de mayo", "18:00", 12),
        ("dia",   2, "12 de mayo", "06:00", 24),
        ("noche", 2, "12 de mayo", "18:00", 36),
        ("dia",   3, "13 de mayo", "06:00", 48),
    ]
    for franja, jornada, fecha, hora, horas in esperado:
        m.paso(franja)
        r = e.reloj()
        assert (r["franja"], r["jornada"], r["fecha"], r["hora_inicio"]) == \
               (franja, jornada, fecha, hora)
        assert r["horas_transcurridas"] == horas

    # La noche cruza la medianoche; el día no.
    m.paso("noche")
    assert e.reloj()["cruza_medianoche"] is True
    assert e.reloj()["fecha_fin"] == "14 de mayo"


def test_la_ultima_jornada_no_tiene_noche():
    """
    Nueve ventanas y no diez: el ejercicio cierra con la jornada 5. Si la línea
    dibujara una décima, la sala contaría con un interludio que no existe.
    """
    e = cargar_estado()
    linea = e.reloj()["linea"]
    assert len(linea) == P.TURNOS_DECISION
    assert linea[-1]["noche"] is None
    assert all(j["noche"] is not None for j in linea[:-1])
    assert e.reloj()["ventanas_totales"] == P.VENTANAS_TOTALES == 9


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
    Dirección General de la Policía. Si apareciera en el tablero, uno de los ocho
    roles dejaría de hacer falta.
    """
    e = cargar_estado()
    m = MotorCrisis(e)
    m.paso("dia")

    nid = next(iter(e.nodos))
    m.cola_inmediata = [OperarNodo(
        nodo_id=nid, tipo_unidad="esmad", dupla_presente=True,
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
