"""
state.py — Las estructuras de estado del mundo.

De qué está hecho el país dentro del ejercicio. Tres niveles espaciales, porque
los ocho roles no deciden sobre lo mismo:

    PUNTO DE CIERRE   un bloqueo concreto            24    Policía · Interior · Alcalde
    CORREDOR          una secuencia de puntos         5    Transporte · Defensa
    REGIÓN            un departamento o área          4    Minas · Interior

DESVIACIÓN DELIBERADA RESPECTO DE MACONDO
-----------------------------------------
La guía de arquitectura recomienda arrays paralelos de NumPy. Aquí se usan
objetos, a propósito: 24 nodos y no 657, lógica ramificada y no aritmética
uniforme, y 12 pasos por ejercicio y no 288.

La regla que SÍ se conserva: identificador estable y opaco (`nodo_id`), y los
nombres legibles fuera del motor.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Literal

from src.engine import parameters as P

ModoApertura = Literal["cerrado", "fuerza", "concertacion", "desgaste"]
TipoUnidad = Literal["esmad", "policia", "militar"]
Franja = Literal["dia", "noche"]


# ---------------------------------------------------------------------------
# Punto de cierre
# ---------------------------------------------------------------------------

@dataclass
class Composicion:
    """
    Qué hay realmente en un punto de cierre. El Estado NUNCA lo ve.

    Desde la v2 esta mezcla SÍ tiene consecuencias, por dos vías y solo dos
    (§P1 de `docs/propuesta.md`):

      1 · operar sobre un punto mayoritariamente de protesta legítima cuesta más
      2 · concertar donde hay estructura organizada produce un acuerdo que se rompe

    Sigue sin salir jamás del motor: `vista_publica()` y las ocho vistas por rol
    solo entregan estimaciones sesgadas.
    """
    protesta_legitima: float
    vandalismo_oportunista: float
    estructura_organizada: float

    def normalizada(self) -> "Composicion":
        t = self.protesta_legitima + self.vandalismo_oportunista + self.estructura_organizada
        if t <= 0:
            return Composicion(1.0, 0.0, 0.0)
        return Composicion(
            self.protesta_legitima / t,
            self.vandalismo_oportunista / t,
            self.estructura_organizada / t,
        )


@dataclass
class Nodo:
    nodo_id: str
    nombre: str
    region_id: str
    corredor_id: str | None = None

    dureza: float = 0.5                 # [0,1] cuánto cuesta abrirlo por fuerza
    caudal: float = 0.0                 # [0,1] fracción de flujo que deja pasar
    dias_sostenido: int = 0
    masa_presente: int = 200
    apoyo_local: float = 0.7            # [0,1] respaldo del barrio al cierre
    control_voceria: float = 0.5        # [0,1] cuánto controla la vocería reconocida
    proximidad_infra_critica: bool = False

    modo_apertura: ModoApertura = "cerrado"
    turnos_desde_apertura: int = 0
    turnos_en_negociacion: int = 0      # progreso hacia una apertura concertada
    turnos_apoyo_bajo: int = 0

    # Posición en el mapa esquemático (§3.2 de la v2). No es geografía: es la
    # disposición del diagrama de líneas, como un plano de metro.
    x: float = 0.0
    y: float = 0.0

    # --- capa 1: la verdad. No se serializa hacia ninguna interfaz. ---
    composicion_real: Composicion = field(
        default_factory=lambda: Composicion(0.75, 0.15, 0.10)
    )

    # --- trazabilidad de la observación ---
    ultima_verificacion_turno: int | None = None
    verificado_por: str | None = None

    @property
    def abierto(self) -> bool:
        return self.caudal > 0.05

    def clamp(self) -> None:
        self.dureza = min(1.0, max(0.0, self.dureza))
        self.caudal = min(1.0, max(0.0, self.caudal))
        self.apoyo_local = min(1.0, max(0.0, self.apoyo_local))
        self.control_voceria = min(1.0, max(0.0, self.control_voceria))
        self.masa_presente = max(0, int(self.masa_presente))


# ---------------------------------------------------------------------------
# Corredor
# ---------------------------------------------------------------------------

@dataclass
class Corredor:
    corredor_id: str
    nombre: str
    nodos: list[str]                       # ids, en orden
    poblacion_aguas_abajo: int
    costo_diario_mm_cop: float
    clases_prioridad: set[str] = field(default_factory=set)
    anunciado_abierto: bool = False
    anunciado_en_turno: int | None = None
    anunciado_verificado: bool = False      # si se anunció como hecho verificado

    def caudal_efectivo(self, nodos: dict[str, Nodo]) -> float:
        """Un corredor es tan bueno como su peor punto."""
        if not self.nodos:
            return 1.0
        return min(nodos[n].caudal for n in self.nodos if n in nodos)

    def punto_que_bloquea(self, nodos: dict[str, Nodo]) -> str | None:
        """Cuál de sus puntos lo está cerrando. Es el dato fino de Transporte."""
        candidatos = [nodos[n] for n in self.nodos if n in nodos]
        if not candidatos:
            return None
        peor = min(candidatos, key=lambda n: n.caudal)
        return peor.nodo_id if not peor.abierto else None


# ---------------------------------------------------------------------------
# Región
# ---------------------------------------------------------------------------

@dataclass
class Region:
    region_id: str
    nombre: str
    dias_autonomia_combustible: float
    dias_autonomia_alimentos: float
    dias_autonomia_oxigeno: float
    presion_hospitalaria: float = 0.7
    indice_precios: float = 1.0
    intensidad_movilizacion: float = P.INTENSIDAD_NACIONAL_T0
    nodos_secundarios_activos: int = 100
    muertes_evitables: int = 0          # acumulador; solo crece
    panico: float = 0.0                 # sube si se difunde el calendario

    @property
    def semaforo(self) -> str:
        """El grano grueso que ve toda la sala. Los días exactos son de Minas."""
        peor = min(self.dias_autonomia_oxigeno,
                   self.dias_autonomia_combustible,
                   self.dias_autonomia_alimentos)
        if peor < 1.0:
            return "rojo"
        if peor < 2.5:
            return "ambar"
        return "verde"


# ---------------------------------------------------------------------------
# Unidades de fuerza
# ---------------------------------------------------------------------------

@dataclass
class Unidad:
    unidad_id: str
    tipo: TipoUnidad
    asignacion: str = "reserva"   # reserva|contencion|operacion|escolta|custodia|relevo
    ubicacion: str | None = None  # nodo_id o instalacion_id
    fatiga: float = 0.0
    turnos_continuos: int = 0

    @property
    def disponible(self) -> bool:
        return self.asignacion in ("reserva", "contencion")


# ---------------------------------------------------------------------------
# Reservas sistémicas
# ---------------------------------------------------------------------------

@dataclass
class Reservas:
    """
    Las cuatro reservas. Se consumen rápido y se recuperan despacio, y a
    diferencia del dinero NO se pueden pedir prestadas.

    Las cuatro se leen igual: arriba es mejor. En la versión anterior la
    exposición internacional iba invertida y obligaba a explicar el tablero.
    """
    legitimidad: float = P.RESERVAS_T0["legitimidad"]
    credibilidad_mesa: float = P.RESERVAS_T0["credibilidad_mesa"]
    respaldo_internacional: float = P.RESERVAS_T0["respaldo_internacional"]
    cohesion_mesa: float = P.RESERVAS_T0["cohesion_mesa"]

    def aplicar(self, deltas: dict[str, float], escala: float = 1.0) -> None:
        for k, v in deltas.items():
            if not hasattr(self, k):
                raise KeyError(f"reserva desconocida: {k}")
            setattr(self, k, min(100.0, max(0.0, getattr(self, k) + v * escala)))

    def umbrales_cruzados(self) -> list[str]:
        """Los umbrales son duros: un deterioro gradual no produce decisiones."""
        out = []
        U = P.UMBRALES
        if self.legitimidad < U["legitimidad_gremios_se_suman"]:
            out.append("gremios_se_suman")
        elif self.legitimidad < U["legitimidad_gremios_evaluan"]:
            out.append("gremios_evaluan")
        if self.credibilidad_mesa < U["credibilidad_comite_definitivo"]:
            out.append("comite_se_retira_definitivo")
        elif self.credibilidad_mesa < U["credibilidad_comite_suspende"]:
            out.append("comite_suspende")
        if self.respaldo_internacional < U["respaldo_pronunciamientos"]:
            out.append("pronunciamientos_internacionales")
        if self.cohesion_mesa < U["cohesion_contradicciones"]:
            out.append("contradicciones_publicas")
        return out


# ---------------------------------------------------------------------------
# Banderas constitutivas
# ---------------------------------------------------------------------------

@dataclass
class Banderas:
    """Lo que la mesa constituyó. Ninguna es obligatoria; todas están tarifadas."""
    reglas_escritas: bool = False
    identificacion_agentes: bool = False
    registro_av: bool = False
    registro_escrito: bool = False
    protocolo_voceria: bool = False
    protocolo_verificacion: bool = False
    criterio_priorizacion: bool = False
    lineas_rojas_fijadas: bool = False
    plazo_suspensivo: bool = False
    nodo_unico: bool = False
    concertacion_previa_cali: bool = False   # el Alcalde condicionó el empleo de la fuerza
    prioridad_combustible_fijada: bool = False

    asistencia_militar_firmada: bool = False
    asistencia_militar_delimitada: bool = False
    defensoria_presente: bool = True         # decisión A3: no se retira nunca

    activada_en_turno: dict[str, int] = field(default_factory=dict)

    def activar(self, nombre: str, turno: int) -> bool:
        if not hasattr(self, nombre):
            raise KeyError(f"bandera desconocida: {nombre}")
        if getattr(self, nombre):
            return False
        setattr(self, nombre, True)
        self.activada_en_turno[nombre] = turno
        return True

    def mitigadores_activos(self) -> dict[str, bool]:
        """Los tres persistentes. Los otros tres son parámetros de cada operación."""
        return {
            "reglas_escritas": self.reglas_escritas,
            "identificacion_agentes": self.identificacion_agentes,
            "registro_av": self.registro_av,
        }


# ---------------------------------------------------------------------------
# Denuncias sin verificar
# ---------------------------------------------------------------------------

@dataclass
class Denuncia:
    """
    El hecho H2 del paquete detonante, hecho mecánica.

    REGLA DE DISEÑO: nunca una sola denuncia sin verificar. Siempre al menos dos,
    con veracidad distinta y sin ninguna señal que las distinga. Un ejercicio
    sobre el paro de 2021 en el que la única denuncia grave resulta inventada le
    enseña a ocho futuros funcionarios que las denuncias graves suelen serlo — y
    eso, sobre hechos con responsabilidad judicial viva, es tomar partido.

    La lección correcta no es «desconfíe» sino «usted no puede saberlo sin
    verificar, y verificar cuesta una dupla que no tiene».
    """
    denuncia_id: str
    texto: str
    nodo_id: str | None
    veraz: bool                    # capa 1 — el motor lo sabe, nadie más
    turno_aparicion: int = 0
    verificada: bool = False
    declarada_en_verificacion: bool = False
    estallo: bool = False

    def vista_publica(self) -> dict:
        """Sale sin `veraz`. Si se filtra, el diseño entero pierde sentido."""
        estado = "sin verificar"
        if self.verificada:
            estado = "verificada"
        elif self.declarada_en_verificacion:
            estado = "declarada en verificación"
        return {
            "denuncia_id": self.denuncia_id,
            "texto": self.texto,
            "nodo_id": self.nodo_id,
            "estado": estado,
            "turno": self.turno_aparicion,
        }


# ---------------------------------------------------------------------------
# Acuerdos de la mesa
# ---------------------------------------------------------------------------

@dataclass
class Acuerdo:
    """
    Lo que Interior trae de la mesa. Vale mientras se cumpla — y cumplirlo
    significa no operar sobre los puntos pactados mientras esté vigente.
    """
    acuerdo_id: str
    nodos: list[str]
    turno_firmado: int
    turno_limite: int
    cumplido: bool = False
    roto: bool = False
    motivo_ruptura: str | None = None


# ---------------------------------------------------------------------------
# Registro de decisiones (el pliego)
# ---------------------------------------------------------------------------

@dataclass
class Decision:
    turno: int
    franja: Franja
    rol: str
    accion: str
    descripcion: str
    responsable_nominado: str | None
    resultado: str

    @property
    def atribuible(self) -> bool:
        return self.responsable_nominado is not None


# ---------------------------------------------------------------------------
# Estado completo
# ---------------------------------------------------------------------------

@dataclass
class Estado:
    turno: int = 0            # pasos del motor (día y noche cuentan)
    turno_decision: int = 0   # turnos de sala; solo los de día
    franja: Franja = "dia"

    # La semilla de la corrida. No es una variable del caso: es lo que permite
    # que una LECTURA sea reproducible sin gastar el azar del motor. La pone
    # `MotorCrisis.__init__`; ver `information.estimar_nodo`.
    semilla: int = P.SEMILLA_POR_DEFECTO

    nodos: dict[str, Nodo] = field(default_factory=dict)
    corredores: dict[str, Corredor] = field(default_factory=dict)
    regiones: dict[str, Region] = field(default_factory=dict)
    unidades: list[Unidad] = field(default_factory=list)

    reservas: Reservas = field(default_factory=Reservas)
    banderas: Banderas = field(default_factory=Banderas)

    intensidad_nacional: float = P.INTENSIDAD_NACIONAL_T0
    posicion_gremios: str = "fuera"      # fuera|evaluando|sumados
    ultimatum_gremios_turno: int | None = None
    comite_disponible: bool = True
    encuadre_dominante: str = "desorden"  # represion|desorden|negociacion|abandono

    instalaciones_criticas: list[str] = field(default_factory=list)
    frentes_rurales_descubiertos: int = 0

    # H1 del paquete detonante, tal como llega en el parte heredado. Es texto
    # para la sala, no una variable: el motor ya aplicó sus efectos al cargar.
    hecho_h1: dict = field(default_factory=dict)

    # UN SOLO BOLSILLO DE TRES: verificar un punto, verificar una denuncia o
    # acompañar una operación salen de aquí. Se repone al empezar cada turno.
    duplas_disponibles: int = P.DUPLAS_TOTALES
    duplas_usadas_en: list[str] = field(default_factory=list)
    dudas_permanencia: int = 0           # cuántas veces la Defensoría lo ha dicho

    denuncias: list[Denuncia] = field(default_factory=list)
    acuerdos: list[Acuerdo] = field(default_factory=list)

    # Región epicentro: la jurisdicción del Alcalde de la mesa
    region_epicentro: str = ""

    # El orden de prioridad del combustible, cuando Minas lo fija. Es un criterio
    # PERMANENTE: mientras esté puesto se aplica en cada paso, no una sola vez.
    prioridad_combustible: list[str] = field(default_factory=list)

    registro: list[Decision] = field(default_factory=list)
    eventos_turno: list[dict] = field(default_factory=list)

    _conteo_eventos: dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Consultas agregadas
    # ------------------------------------------------------------------

    def unidades_por_tipo(self, tipo: TipoUnidad) -> list[Unidad]:
        return [u for u in self.unidades if u.tipo == tipo]

    def esmad_disponible(self) -> list[Unidad]:
        """Redesplegables: incluye las que hoy hacen contención estática."""
        return [u for u in self.unidades if u.tipo == "esmad" and u.disponible]

    def esmad_en_reserva(self) -> list[Unidad]:
        """Libres de verdad. En t=0 son 6 de 40."""
        return [u for u in self.unidades
                if u.tipo == "esmad" and u.asignacion == "reserva"]

    def fatiga_media(self, tipo: TipoUnidad | None = None) -> float:
        pool = self.unidades if tipo is None else self.unidades_por_tipo(tipo)
        desplegadas = [u for u in pool if u.asignacion != "reserva"]
        if not desplegadas:
            return 0.0
        return sum(u.fatiga for u in desplegadas) / len(desplegadas)

    def nodos_abiertos(self) -> list[Nodo]:
        return [n for n in self.nodos.values() if n.abierto]

    def nodos_de_region(self, region_id: str) -> list[Nodo]:
        return [n for n in self.nodos.values() if n.region_id == region_id]

    # ---------------------------------------------------------------- reloj

    def reloj(self) -> dict:
        """
        Qué hora es dentro del ejercicio.

        Cinco jornadas del 11 al 15 de mayo en turnos de doce horas que alternan
        día y noche. La noche cruza la medianoche: la de la jornada 2 va del 12 a
        las 18:00 al 13 a las 06:00.

        VIVE EN EL MOTOR, no en la interfaz. Cuatro superficies calculando cada
        una su propia hora son cuatro relojes, y en una sala con dos proyectores
        la discrepancia se ve el primer turno.

        Y no es adorno. Con cinco jornadas, **saber cuántas quedan cambia lo que
        se decide**: una concertación tarda dos turnos, de modo que abrirla en la
        jornada 5 es no abrirla. El reloj dice el plazo; qué hacer con él es de
        la sala.
        """
        de_dia = self.franja == "dia"
        jornada = max(1, self.turno_decision)

        # Ventana actual: turno 1 = día 1, turno 2 = noche 1, turno 3 = día 2…
        horas = max(0, self.turno - 1) * P.HORAS_POR_TURNO
        inicio = datetime.fromisoformat(P.FECHA_INICIO) + timedelta(hours=horas)
        fin = inicio + timedelta(hours=P.HORAS_POR_TURNO)

        return {
            "jornada": self.turno_decision,      # 0 antes de empezar
            "jornadas_totales": P.TURNOS_DECISION,
            "jornadas_restantes": max(0, P.TURNOS_DECISION - self.turno_decision),
            "franja": self.franja,
            "fecha": _fecha_larga(inicio),
            "fecha_fin": _fecha_larga(fin),
            "cruza_medianoche": inicio.day != fin.day,
            "hora_inicio": inicio.strftime("%H:%M"),
            "hora_fin": fin.strftime("%H:%M"),
            "horas_transcurridas": horas,
            "ventana": self.turno,               # 1..9; 0 antes de empezar
            "ventanas_totales": P.VENTANAS_TOTALES,
            # Para pintar la barra de jornadas sin que la interfaz reconstruya
            # el calendario por su cuenta.
            "linea": [
                {
                    "jornada": j,
                    "fecha": _fecha_corta(
                        datetime.fromisoformat(P.FECHA_INICIO) + timedelta(days=j - 1)),
                    "dia": _estado_ventana(self.turno, 2 * j - 1),
                    "noche": (_estado_ventana(self.turno, 2 * j)
                              if j < P.TURNOS_DECISION else None),
                }
                for j in range(1, P.TURNOS_DECISION + 1)
            ],
            # Redundante con `jornada` y `franja`, pero es la línea que se lee en
            # voz alta y no conviene que cada pantalla la componga a su manera.
            "etiqueta": (
                "antes de la apertura" if self.turno_decision == 0
                else f"jornada {jornada} · {'día' if de_dia else 'noche'}"
            ),
        }

    def muertes_evitables_total(self) -> int:
        return sum(r.muertes_evitables for r in self.regiones.values())

    def dias_autonomia_minimos(self) -> tuple[str, float]:
        peor = min(
            self.regiones.values(),
            key=lambda r: min(r.dias_autonomia_oxigeno, r.dias_autonomia_combustible),
        )
        return peor.nombre, min(peor.dias_autonomia_oxigeno, peor.dias_autonomia_combustible)

    def acuerdo_vigente_sobre(self, nodo_id: str) -> Acuerdo | None:
        for a in self.acuerdos:
            if not a.roto and not a.cumplido and nodo_id in a.nodos:
                return a
        return None

    def corredores_que_sirven(self, region_id: str, clase: str) -> list[Corredor]:
        out = []
        for c in self.corredores.values():
            if clase not in c.clases_prioridad:
                continue
            if any(self.nodos[n].region_id == region_id
                   for n in c.nodos if n in self.nodos):
                out.append(c)
        return out

    # ------------------------------------------------------------------
    # Serialización — la capa 2 (grano grueso), nunca la capa 1
    # ------------------------------------------------------------------

    def vista_publica(self) -> dict:
        """
        El TABLERO GENERAL: lo que ve toda la sala.

        Responde QUÉ ESTÁ PASANDO. El cuánto, el dónde exactamente y el desde
        cuándo son las ocho vistas privadas (`views.py`).

        NUNCA incluye `composicion_real` ni la veracidad de una denuncia. Si eso
        se filtrara, el dilema central del caso desaparecería.
        """
        return {
            "turno": self.turno,
            "turno_decision": self.turno_decision,
            "franja": self.franja,
            "reloj": self.reloj(),
            "reservas": asdict(self.reservas),
            "presion_calle": round(self.intensidad_nacional, 1),
            "posicion_gremios": self.posicion_gremios,
            "comite_disponible": self.comite_disponible,
            "encuadre_dominante": self.encuadre_dominante,
            "banderas": {
                k: v for k, v in asdict(self.banderas).items()
                if isinstance(v, bool)
            },
            "muertes_evitables": self.muertes_evitables_total(),
            "regiones": [
                {
                    "region_id": r.region_id,
                    "nombre": r.nombre,
                    "semaforo": r.semaforo,          # grano grueso: los días son de Minas
                    "muertes_evitables": r.muertes_evitables,
                    "epicentro": r.region_id == self.region_epicentro,
                }
                for r in self.regiones.values()
            ],
            "corredores": [
                {
                    "corredor_id": c.corredor_id,
                    "nombre": c.nombre,
                    "caudal": round(c.caudal_efectivo(self.nodos), 2),
                    "poblacion": c.poblacion_aguas_abajo,
                    "clases": sorted(c.clases_prioridad),
                    "anunciado_abierto": c.anunciado_abierto,
                    "nodos": list(c.nodos),
                }
                for c in self.corredores.values()
            ],
            "puntos": [
                {
                    "nodo_id": n.nodo_id,
                    "nombre": n.nombre,
                    "region_id": n.region_id,
                    "corredor_id": n.corredor_id,
                    "estado": self._estado_punto(n),
                    "modo_apertura": n.modo_apertura,
                    "verificado_turno": n.ultima_verificacion_turno,
                    "x": n.x,
                    "y": n.y,
                }
                for n in self.nodos.values()
            ],
            "fuerza": {
                "esmad_total": len(self.unidades_por_tipo("esmad")),
                "esmad_sin_comprometer": len(self.esmad_en_reserva()),
                "esmad_disponible": len(self.esmad_disponible()),
                "instalaciones_criticas": len(self.instalaciones_criticas),
                "frentes_rurales_descubiertos": self.frentes_rurales_descubiertos,
            },
            "denuncias": [d.vista_publica() for d in self.denuncias],
        }

    def _estado_punto(self, n: Nodo) -> str:
        """Abierto, parcial, cerrado — o sin verificar, que es una petición de decisión."""
        if n.ultima_verificacion_turno is None and self.turno > 1:
            return "sin_verificar"
        if n.caudal > 0.6:
            return "abierto"
        if n.caudal > 0.05:
            return "parcial"
        return "cerrado"


# ---------------------------------------------------------------------------
# Formato de fechas
# ---------------------------------------------------------------------------
#
# Sin año y sin día de la semana, a propósito. El año anclaría un territorio
# ficticio a un expediente real; el día de la semana sería una señal falsa,
# porque el motor no distingue un martes de un domingo.

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def _fecha_larga(t: datetime) -> str:
    return f"{t.day} de {MESES[t.month - 1]}"


def _fecha_corta(t: datetime) -> str:
    return f"{t.day}"


def _estado_ventana(actual: int, ventana: int) -> str:
    """`cumplida`, `actual` o `pendiente`. Es lo que hace legible el plazo."""
    if actual == 0:
        return "pendiente"
    if ventana < actual:
        return "cumplida"
    return "actual" if ventana == actual else "pendiente"
