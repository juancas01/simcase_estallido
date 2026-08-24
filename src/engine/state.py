"""
state.py — Las estructuras de estado del mundo.

DESVIACIÓN DELIBERADA RESPECTO DE MACONDO
-----------------------------------------
La guía de arquitectura recomienda arrays paralelos de NumPy sobre unidades
espaciales, porque un paso de la inundación era una operación vectorizada sobre
657 manzanas y con objetos el ejercicio no corría en tiempo real.

Aquí se usan objetos, a propósito:

  * N = 24 nodos, no 657. El coste de un bucle Python es irrelevante.
  * La lógica por nodo es ramificada (¿tiene contraparte? ¿cómo se abrió?
    ¿está contiguo a infraestructura crítica?), no aritmética uniforme.
    Vectorizar ramas es más lento de escribir y más difícil de leer.
  * El motor avanza 5 veces por ejercicio, no 288.

La regla que SÍ se conserva: identificador estable y opaco (`nodo_id`), y los
nombres legibles fuera del motor, en la capa de resolución de entidades.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal

from src.engine import parameters as P

ModoApertura = Literal["cerrado", "fuerza", "concertacion", "desgaste"]
TipoUnidad = Literal["esmad", "policia", "militar"]
Franja = Literal["dia", "noche"]


# ---------------------------------------------------------------------------
# Nodo de cierre
# ---------------------------------------------------------------------------

@dataclass
class Composicion:
    """Qué hay realmente en un punto de cierre. El Estado NUNCA ve esto."""
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
    turnos_apoyo_bajo: int = 0          # cuántos turnos lleva el apoyo por el suelo

    # --- capa 1: la verdad. No se serializa hacia la interfaz. ---
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

    def caudal_efectivo(self, nodos: dict[str, Nodo]) -> float:
        """Un corredor es tan bueno como su peor punto."""
        if not self.nodos:
            return 1.0
        return min(nodos[n].caudal for n in self.nodos if n in nodos)


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
    legitimidad: float = P.RESERVAS_T0["legitimidad"]
    credibilidad_mesa: float = P.RESERVAS_T0["credibilidad_mesa"]
    exposicion_internacional: float = P.RESERVAS_T0["exposicion_internacional"]
    cohesion_mesa: float = P.RESERVAS_T0["cohesion_mesa"]

    def aplicar(self, deltas: dict[str, float]) -> None:
        for k, v in deltas.items():
            if not hasattr(self, k):
                raise KeyError(f"reserva desconocida: {k}")
            setattr(self, k, min(100.0, max(0.0, getattr(self, k) + v)))

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
        if self.exposicion_internacional > U["exposicion_pronunciamientos"]:
            out.append("pronunciamientos_internacionales")
        if self.cohesion_mesa < U["cohesion_contradicciones"]:
            out.append("contradicciones_publicas")
        return out


# ---------------------------------------------------------------------------
# Banderas constitutivas (§5.5)
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

    asistencia_militar_firmada: bool = False
    asistencia_militar_delimitada: bool = False   # con territorio, plazo y reglas
    defensoria_presente: bool = True

    # turno en que se activó cada bandera, para medir si llegó antes o después
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
        return {
            "reglas_escritas": self.reglas_escritas,
            "identificacion_agentes": self.identificacion_agentes,
            "registro_av": self.registro_av,
        }


# ---------------------------------------------------------------------------
# Registro de decisiones (el pliego físico, §10.5)
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

    nodos: dict[str, Nodo] = field(default_factory=dict)
    corredores: dict[str, Corredor] = field(default_factory=dict)
    regiones: dict[str, Region] = field(default_factory=dict)
    unidades: list[Unidad] = field(default_factory=list)

    reservas: Reservas = field(default_factory=Reservas)
    banderas: Banderas = field(default_factory=Banderas)

    intensidad_nacional: float = P.INTENSIDAD_NACIONAL_T0
    posicion_gremios: str = "fuera"      # fuera|evaluando|sumados
    comite_disponible: bool = True
    encuadre_dominante: str = "desorden"  # represion|desorden|negociacion|abandono

    instalaciones_criticas: list[str] = field(default_factory=list)
    frentes_rurales_descubiertos: int = 0

    registro: list[Decision] = field(default_factory=list)
    eventos_turno: list[dict] = field(default_factory=list)

    # contadores para rendimientos decrecientes
    _conteo_eventos: dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Consultas agregadas
    # ------------------------------------------------------------------

    def unidades_por_tipo(self, tipo: TipoUnidad) -> list[Unidad]:
        return [u for u in self.unidades if u.tipo == tipo]

    def esmad_disponible(self) -> list[Unidad]:
        """Redesplegables a una operación: incluye las que hoy hacen contención.

        Sacarlas de la contención estática es legítimo —es lo que significa
        «concentrar el ESMAD»— pero deja sin cubrir los puntos que sostenían,
        que es el precio de la acción A1 del Director de la Policía.
        """
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

    def muertes_evitables_total(self) -> int:
        return sum(r.muertes_evitables for r in self.regiones.values())

    def dias_autonomia_minimos(self) -> tuple[str, float]:
        peor = min(
            self.regiones.values(),
            key=lambda r: min(r.dias_autonomia_oxigeno, r.dias_autonomia_combustible),
        )
        return peor.nombre, min(peor.dias_autonomia_oxigeno, peor.dias_autonomia_combustible)

    # ------------------------------------------------------------------
    # Serialización — la capa 2, nunca la capa 1
    # ------------------------------------------------------------------

    def vista_publica(self) -> dict:
        """
        Lo que puede salir hacia la interfaz.

        NUNCA incluye `composicion_real`. Si esto se filtra, el motor de
        información (§4.4) se anula y el dilema central del caso desaparece.
        """
        return {
            "turno": self.turno,
            "franja": self.franja,
            "reservas": asdict(self.reservas),
            "intensidad_nacional": round(self.intensidad_nacional, 1),
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
                    "dias_oxigeno": round(r.dias_autonomia_oxigeno, 2),
                    "dias_combustible": round(r.dias_autonomia_combustible, 2),
                    "dias_alimentos": round(r.dias_autonomia_alimentos, 2),
                    "intensidad": round(r.intensidad_movilizacion, 1),
                    "muertes_evitables": r.muertes_evitables,
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
                }
                for c in self.corredores.values()
            ],
            "fuerza": {
                "esmad_total": len(self.unidades_por_tipo("esmad")),
                "esmad_disponible": len(self.esmad_disponible()),
                "fatiga_media_esmad": round(self.fatiga_media("esmad"), 2),
                "instalaciones_criticas": len(self.instalaciones_criticas),
                "frentes_rurales_descubiertos": self.frentes_rurales_descubiertos,
            },
        }
