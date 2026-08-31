"""
force.py — Capacidad de fuerza, fatiga e incidentes.

Aquí vive la pieza de diseño que convierte el estándar de derechos en un
instrumento de reducción de riesgo en vez de un discurso: los seis mitigadores
son decisiones que alguien en la sala tiene que tomar, y multiplican la
probabilidad de que una operación termine mal.

    El estándar de derechos no está en el motor para moralizar:
    está para bajar una probabilidad.

QUEDAN CINCO Y ERAN SEIS. El sexto era «va acompañada por una dupla de la
Defensoría del Pueblo», y mitigaba porque miraba alguien de fuera. Desde que los
equipos de terreno son del mismo ministerio que ordena la operación, que sus
propios funcionarios la acompañen no cambia la probabilidad de que una imagen
circule: cambia quién la graba. **El acompañamiento no se prohíbe, deja de
descontar** — y esa es la parte del estándar que se fue con el tercero.

Y desde la v2, el módulo hace algo más: **le da consecuencia a la mezcla real de
un punto**. Operar sobre población mayoritariamente civil cuesta más que operar
donde hay estructura organizada — aunque la sala no pueda saber cuál es cuál sin
gastar un equipo. Es la mitad del error doble.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src.engine import parameters as P
from src.engine.state import Estado, Nodo, Unidad, TipoUnidad


@dataclass
class EvaluacionRiesgo:
    """Lo que se le muestra a la sala ANTES de decidir."""
    p_incidente: float
    riesgo_bruto: float
    banda: str                      # baja | media | alta | crítica
    mitigadores_activos: list[str]
    mitigadores_ausentes: list[str]
    factor_mitigacion: float

    def resumen(self) -> str:
        faltan = ", ".join(self.mitigadores_ausentes) or "ninguno"
        return (
            f"riesgo {self.banda.upper()} (P={self.p_incidente:.0%}) · "
            f"mitigadores ausentes: {faltan}"
        )


def _banda(p: float) -> str:
    if p < 0.10:
        return "baja"
    if p < 0.25:
        return "media"
    if p < 0.50:
        return "alta"
    return "critica"


def evaluar_riesgo(
    estado: Estado,
    nodo: Nodo,
    tipo_unidad: TipoUnidad,
    *,
    concertado_con_alcaldia: bool = False,
) -> EvaluacionRiesgo:
    """
    Calcula la exposición al riesgo y la satura a una probabilidad.

    SOBRE LA SATURACIÓN
    -------------------
    El producto crudo no está acotado: militares fatigados, de noche, en un punto
    duro y concurrido dan 0,45 × 2,0 × 2,0 × 3,0 × 1,6 = 8,6, que no es una
    probabilidad. La transformación P = 1 − e^(−riesgo) mapea [0,∞) → [0,1),
    conserva el orden y conserva el efecto multiplicativo de los mitigadores en
    la zona baja, que es donde una sala bien organizada opera.

    Consecuencia que el motor debe comunicar: **el estándar protege a quien ya
    venía operando con cuidado y no rescata a quien no.**

    Nótese que `composicion_real` NO entra aquí. La mezcla de un punto no cambia
    la probabilidad de que algo salga mal; cambia lo que cuesta cuando sale mal
    (ver `ejecutar_operacion`). Si entrara aquí, la banda de riesgo filtraría la
    verdad que nadie debe ver.
    """
    fatiga = estado.fatiga_media(tipo_unidad)

    riesgo = P.BASE_INCIDENTE[tipo_unidad]
    riesgo *= (1.0 + fatiga)
    riesgo *= (1.0 + nodo.dureza)
    riesgo *= (1.0 + nodo.masa_presente / P.MASA_REFERENCIA)
    if estado.franja == "noche":
        riesgo *= P.FACTOR_NOCTURNO

    b = estado.banderas
    disponibles = {
        "reglas_escritas": b.reglas_escritas,
        "identificacion_agentes": b.identificacion_agentes,
        "registro_av": b.registro_av,
        "concertado_con_alcaldia": concertado_con_alcaldia,
        "unidades_descansadas": fatiga < P.UMBRAL_FATIGA_DESCANSADA,
    }

    factor = 1.0
    activos, ausentes = [], []
    for nombre, activo in disponibles.items():
        if activo:
            factor *= P.MITIGADORES[nombre]
            activos.append(nombre)
        else:
            ausentes.append(nombre)

    p = min(P.P_INCIDENTE_MAX, 1.0 - math.exp(-riesgo * factor))

    return EvaluacionRiesgo(
        p_incidente=p,
        riesgo_bruto=riesgo,
        banda=_banda(p),
        mitigadores_activos=activos,
        mitigadores_ausentes=ausentes,
        factor_mitigacion=factor,
    )


def multiplicador_costo_civil(nodo: Nodo) -> float:
    """
    Cuánto más cuesta un incidente según a quién se le hizo.

    **Es la primera de las dos vías por las que la mezcla real de un punto tiene
    consecuencia** (`docs/COMO_FUNCIONA.md` §8). Un incidente en un punto que es 90 %
    protesta legítima cuesta casi el doble que uno donde la mitad es otra cosa:
    es fuerza sobre población civil, y se paga como tal.

    La sala no puede saber esto antes de operar. Puede *averiguarlo* gastando un
    equipo — y esa es exactamente la decisión que el ejercicio quiere producir.
    """
    legit = nodo.composicion_real.normalizada().protesta_legitima
    exceso = max(0.0, legit - P.UMBRAL_PROTESTA_CIVIL)
    return 1.0 + exceso * P.MULTIPLICADOR_COSTO_PROTESTA


@dataclass
class ResultadoOperacion:
    exito: bool
    hubo_incidente: bool
    victimas: int
    imagen_viral: bool
    atribuible: bool
    p_usada: float
    tirada: float
    multiplicador_civil: float
    mensaje: str


def ejecutar_operacion(
    estado: Estado,
    nodo: Nodo,
    tipo_unidad: TipoUnidad,
    unidades: list[Unidad],
    rng: random.Random,
    *,
    concertado_con_alcaldia: bool = False,
    responsable_nominado: str | None = None,
) -> ResultadoOperacion:
    """
    Aplica fuerza sobre un punto. Resuelve el incidente con la semilla del motor.

    El azar es estocástico pero reproducible: la corrida entera se puede repetir
    en el debriefing con una decisión cambiada. **El azar nunca decide si algo era
    buena idea: decide si esta vez salió mal.** La probabilidad se mostró antes.
    """
    ev = evaluar_riesgo(
        estado, nodo, tipo_unidad,
        concertado_con_alcaldia=concertado_con_alcaldia,
    )

    tirada = rng.random()
    hubo_incidente = tirada < ev.p_incidente

    victimas = 0
    viral = False
    if hubo_incidente:
        esperadas = P.VICTIMAS_ESPERADAS[tipo_unidad]
        victimas = max(0, int(rng.gauss(esperadas, esperadas * 0.6) + 0.5))
        p_viral = (P.P_VIRAL_CON_REGISTRO if estado.banderas.registro_av
                   else P.P_VIRAL_SIN_REGISTRO)
        viral = rng.random() < p_viral

    # `atribuible` decide SOBRE QUIÉN cae el costo. Sin orden escrita con
    # responsable nominado, el costo se reparte sobre los nueve y golpea la
    # cohesión — que es exactamente la tensión del Ministro de Defensa.
    atribuible = bool(responsable_nominado) and estado.banderas.registro_escrito

    for u in unidades:
        u.fatiga = min(P.FATIGA_MAX, u.fatiga + P.FATIGA_POR_TURNO_DESPLEGADO)
        u.turnos_continuos += 1
        u.asignacion = "operacion"
        u.ubicacion = nodo.nodo_id

    # El éxito de la apertura no depende del incidente: se puede abrir el punto y
    # producir una catástrofe reputacional al mismo tiempo.
    prob_exito = max(0.15, 1.0 - nodo.dureza * 0.6)
    exito = rng.random() < prob_exito

    msg = f"Operación sobre {nodo.nombre}: "
    msg += "punto despejado. " if exito else "no se logró despejar. "
    if hubo_incidente:
        msg += f"INCIDENTE con {victimas} víctima(s)."
        if viral:
            msg += " La imagen circula."
    else:
        msg += "Sin incidentes."

    return ResultadoOperacion(
        exito=exito,
        hubo_incidente=hubo_incidente,
        victimas=victimas,
        imagen_viral=viral,
        atribuible=atribuible,
        p_usada=ev.p_incidente,
        tirada=tirada,
        multiplicador_civil=multiplicador_costo_civil(nodo),
        mensaje=msg,
    )


# ---------------------------------------------------------------------------
# Disposición del ESMAD — la acción que su dueño no tenía
# ---------------------------------------------------------------------------

def concentrar_esmad(estado: Estado, n_escuadrones: int) -> dict:
    """
    Traer escuadrones de la contención estática a la reserva, para poder
    emplearlos donde la mesa decida.

    **El precio es material y tiene nombre de ciudad:** los puntos que sostenían
    quedan descubiertos y se consolidan, y el mandatario local que los pierde lo
    lee como abandono territorial. Es la interdependencia que la Matriz
    Operativa clasifica como de intensidad Alta y que hasta ahora no existía.
    """
    tope = min(n_escuadrones, P.ESMAD_CONCENTRABLE_POR_TURNO)
    candidatas = [u for u in estado.unidades
                  if u.tipo == "esmad" and u.asignacion == "contencion"][:tope]
    for u in candidatas:
        u.asignacion = "reserva"
        u.ubicacion = None

    # El repliegue consolida puntos secundarios
    consolidados = []
    if candidatas:
        cerrados = sorted(
            [n for n in estado.nodos.values() if not n.abierto],
            key=lambda n: n.dureza,
        )[:P.NODOS_CONSOLIDADOS_POR_REPLIEGUE]
        for n in cerrados:
            n.dureza = min(1.0, n.dureza + 0.06)
            n.dias_sostenido += 1
            consolidados.append(n.nodo_id)

    return {"concentrados": len(candidatas), "consolidados": consolidados}


def escoltar(
    estado: Estado, corredor_id: str, clase: str, rng: random.Random
) -> dict:
    """
    Acompañar una caravana de carga, un carrotanque o una misión médica.

    **Es la condición material de todo el frente logístico**: sin escolta no hay
    caravana ni carrotanque, por más que Transporte priorice y asigne. La
    Matriz lo dice con esas palabras, y hasta ahora no existía en el motor.

    Una escolta lograda repone autonomía en las regiones que el corredor sirve.
    Una escolta atacada convierte el corredor humanitario en escenario de
    confrontación, destruye la neutralidad de la misión médica e inmoviliza
    escuadrones que se necesitaban en otro punto.
    """
    corredor = estado.corredores.get(corredor_id)
    if corredor is None:
        return {"ok": False, "motivo": f"no existe el corredor {corredor_id}"}
    if clase not in corredor.clases_prioridad:
        return {"ok": False, "motivo": (
            f"{corredor.nombre} no es corredor de clase '{clase}'. "
            f"Sus clases son: {', '.join(sorted(corredor.clases_prioridad))}."
        )}

    disponibles = estado.esmad_en_reserva()
    if len(disponibles) < P.ESCUADRONES_POR_ESCOLTA:
        return {"ok": False, "motivo": (
            f"Hacen falta {P.ESCUADRONES_POR_ESCOLTA} escuadrones sin comprometer "
            f"y hay {len(disponibles)}."
        )}

    for u in disponibles[:P.ESCUADRONES_POR_ESCOLTA]:
        u.asignacion = "escolta"
        u.ubicacion = corredor_id

    caudal = corredor.caudal_efectivo(estado.nodos)
    if caudal <= 0.05:
        return {"ok": True, "paso": False, "atacada": False, "mensaje": (
            f"La escolta salió pero {corredor.nombre} sigue cerrado en su peor "
            f"punto: la caravana no pasó. Los escuadrones quedan inmovilizados."
        )}

    # Riesgo de ataque, mayor donde la movilización está más caliente
    regiones = {estado.nodos[n].region_id for n in corredor.nodos if n in estado.nodos}
    intensidad = max(
        (estado.regiones[r].intensidad_movilizacion for r in regiones
         if r in estado.regiones),
        default=60.0,
    )
    p_ataque = min(0.55, P.P_ESCOLTA_ATACADA_BASE * (1.0 + intensidad / 100.0))
    atacada = rng.random() < p_ataque

    return {
        "ok": True, "paso": not atacada, "atacada": atacada,
        "regiones": sorted(regiones), "caudal": caudal,
        "reposicion": P.REPOSICION_POR_ESCOLTA * caudal,
    }


# ---------------------------------------------------------------------------
# Fatiga y custodia
# ---------------------------------------------------------------------------

def paso_fatiga(estado: Estado) -> None:
    """La fatiga es el factor de error, y el error individual es el riesgo sistémico."""
    for u in estado.unidades:
        if u.asignacion == "relevo":
            u.fatiga = max(0.0, u.fatiga - P.FATIGA_RECUPERADA_EN_RELEVO)
            u.turnos_continuos = 0
            if u.fatiga <= 0.05:
                u.asignacion = "reserva"
                u.ubicacion = None
        elif u.asignacion == "escolta":
            # La escolta dura un turno: después vuelve a estar disponible
            u.fatiga = min(P.FATIGA_MAX, u.fatiga + P.FATIGA_POR_TURNO_DESPLEGADO * 0.5)
            u.asignacion = "reserva"
            u.ubicacion = None
        elif u.asignacion in ("contencion", "operacion", "custodia"):
            u.fatiga = min(P.FATIGA_MAX, u.fatiga + P.FATIGA_POR_TURNO_DESPLEGADO * 0.5)
            u.turnos_continuos += 1


def capacidad_inmovilizada_por_custodia(estado: Estado) -> int:
    """
    Cada instalación declarada crítica inmoviliza fuerza.

    Es la aritmética que enfrenta al Interior con Defensa: la protección permanente
    resta exactamente de la capacidad de desbloqueo.
    """
    return len(estado.instalaciones_criticas) * P.CUSTODIA_POLICIAS_POR_INSTALACION


def solicitar_relevo(estado: Estado, n_unidades: int) -> int:
    """
    Intercambio explícito: menor probabilidad de catástrofe reputacional a cambio
    de menor cobertura simultánea.
    """
    candidatas = sorted(
        [u for u in estado.unidades if u.asignacion in ("contencion", "operacion")],
        key=lambda u: -u.fatiga,
    )[:n_unidades]
    for u in candidatas:
        u.asignacion = "relevo"
        u.ubicacion = None
    return len(candidatas)
