"""
state.py — Las estructuras de estado del mundo.

De qué está hecho el país dentro del ejercicio. Tres niveles espaciales, porque
los siete roles no deciden sobre lo mismo:

    PUNTO DE CIERRE   un bloqueo concreto            24    Policía · Interior · Alcalde
    CORREDOR          una secuencia de puntos         5    Transporte · Defensa
    REGIÓN            un departamento o área          4    Agricultura · Interior

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
    (`docs/COMO_FUNCIONA.md` §8):

      1 · operar sobre un punto mayoritariamente de protesta legítima cuesta más
      2 · concertar donde hay estructura organizada produce un acuerdo que se rompe

    Sigue sin salir jamás del motor: `vista_publica()` y las nueve vistas por rol
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

    # CUANTA GENTE SOSTIENE ESTE CIERRE, y cuanta hay ahora mismo.
    #
    # `masa_base` es el tamano propio del punto: lo que reune cuando la
    # movilizacion esta en el nivel de referencia. `masa_presente` es lo que hay
    # hoy, y sale de escalar la base por la intensidad de la region y por la
    # franja (`mobilization.recalcular`).
    #
    # La base FALTABA, y el mapa lo dejo a la vista en cuanto empezo a dibujar
    # esta cifra: la masa se calculaba solo desde la intensidad de la region, asi
    # que los seis puntos de Bellaflor tenian siempre la misma cifra exacta de
    # personas. Un peaje de carretera y una glorieta del centro no reunen la
    # misma gente, y el termino de masa del riesgo de incidente (`force.py`)
    # llevaba todo este tiempo sin poder distinguirlos.
    masa_base: int = 200
    masa_presente: int = 200
    apoyo_local: float = 0.7            # [0,1] respaldo del barrio al cierre
    control_voceria: float = 0.5        # [0,1] cuánto controla la vocería reconocida
    proximidad_infra_critica: bool = False

    modo_apertura: ModoApertura = "cerrado"
    turnos_desde_apertura: int = 0
    turnos_en_negociacion: int = 0      # progreso hacia una apertura concertada
    turnos_apoyo_bajo: int = 0

    # LA MESA DE DIÁLOGO INSTALADA EN ESTE PUNTO
    # -----------------------------------------
    # Una mesa local **hay que instalarla cada jornada para que surta efecto**, y
    # eso no estaba dicho en ninguna parte. El progreso hacia una apertura
    # concertada vive en `turnos_en_negociacion`, que sube UNA sola vez por
    # sesión: si un día no se sesiona, no baja —no se pierde lo andado— pero
    # tampoco sube. **No instalar una mesa un día equivale a congelar las
    # negociaciones**, y hasta ahora eso solo lo sabía quien hubiera leído
    # `aperture.avanzar_concertacion`.
    #
    # Estos tres campos son lo que hace visible esa regla: el mapa marca dónde
    # hay mesa, el motor cuenta las jornadas congeladas, y el Ministro del
    # Interior y el Alcalde reciben la pregunta al abrir el día.
    mesa_abierta: bool = False              # hay mesa instalada en este punto
    mesa_sesion_turno: int | None = None    # última JORNADA en que se sesionó
    jornadas_mesa_congelada: int = 0        # jornadas seguidas sin sesión

    # LA FUERZA APLICADA SOBRE ESTE PUNTO
    # -----------------------------------
    # `modo_apertura` solo dice CÓMO se abrió, y por tanto no dice nada de los
    # puntos que siguen cerrados: un punto operado con ESMAD que no cedió y un
    # punto que nadie ha tocado se leían exactamente igual en el mapa. Esta
    # marca es la que permite distinguirlos (`territory.intervencion_nodo`).
    intervencion_fuerza_turno: int | None = None

    # Posición en el mapa (`docs/propuesta.md` §3.2). No es geografía a escala:
    # sitúa el punto dentro del polígono de su región, y el cargador lo exige.
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
        self.masa_base = max(0, int(self.masa_base))


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
# Infraestructura relevante
# ---------------------------------------------------------------------------

@dataclass
class Infraestructura:
    """
    Una instalación que el país necesita en pie, con nombre y con sitio.

    **Existía la acción y no existía el objeto.** `DeclararInfraestructuraCritica`
    recibía una lista de cadenas libres —«refineria»— que nadie validaba contra
    nada: se podía declarar crítica una instalación inventada, y el Ministro de
    Minas no tenía en ninguna pantalla la lista de lo que le toca proteger. Una
    acción cuyo objeto no está en los datos es una acción que se pide a ciegas.

    NO HAY ACCIONES EN CONTRA DE ESTO, y es deliberado. El ejercicio no modela un
    ataque a la refinería: modela la decisión de inmovilizar fuerza para
    custodiarla, que es la que enfrenta a Minas con Defensa. Lo que sí queda es
    **el riesgo asumido**, que el debriefing puede cobrar
    (`MotorCrisis.metricas()['infraestructura']`).

    LA CRITICIDAD ES CUALITATIVA. «Vital», «alta», «media» — nunca un índice de
    0 a 1. Es la misma frontera del resto del tablero: un nivel se interpreta, un
    número se optimiza, y una sala que vea «criticidad 0,87» ordenará proteger
    por orden descendente sin discutir de qué depende cada cosa.
    """
    infra_id: str
    nombre: str
    tipo: str                  # energia|salud|agua|alimentos|logistica|telecom
    region_id: str
    x: float = 0.0
    y: float = 0.0
    criticidad: str = "alta"           # vital | alta | media — CUALITATIVA
    de_que_depende: str = ""           # qué se cae con ella, en una frase
    nodos_contiguos: list[str] = field(default_factory=list)

    protegida: bool = False
    protegida_desde_turno: int | None = None
    jornadas_sin_proteger: int = 0

    def vista_publica(self) -> dict:
        return {
            "infra_id": self.infra_id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "region_id": self.region_id,
            "x": self.x,
            "y": self.y,
            "criticidad": self.criticidad,
            "de_que_depende": self.de_que_depende,
            "nodos_contiguos": list(self.nodos_contiguos),
            "protegida": self.protegida,
            "protegida_desde": self.protegida_desde_turno,
            "jornadas_sin_proteger": self.jornadas_sin_proteger,
        }


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
    clase_alimentaria: bool = False          # Agricultura fijó la clase agroalimentaria

    asistencia_militar_firmada: bool = False
    asistencia_militar_delimitada: bool = False

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
    enseña a nueve futuros funcionarios que las denuncias graves suelen serlo — y
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
    turno_decision: int = 0   # jornadas RESUELTAS; solo las de día
    franja: Franja = "dia"

    # La jornada que la sala está viviendo, que durante los trece minutos de
    # deliberación va una por delante de `turno_decision`: el motor todavía no
    # ha dado el paso. La levanta `MotorCrisis.abrir_jornada()`; ver
    # `jornada_visible`.
    jornada_abierta: int = 0

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
    # SUSPENDER NO ES RETIRARSE, y hacían lo mismo.
    #
    # `comite_disponible` era un pestillo de un solo sentido: se ponía en False
    # al bajar de 30 y **nada en todo el motor lo volvía a poner en True**. Una
    # sala podía recuperar la credibilidad hasta 95 —tres veces el umbral— y el
    # Comité no volvía. El propio mensaje de rechazo prometía lo contrario:
    # «por debajo del umbral EN QUE VUELVE A SENTARSE».
    #
    # Esta bandera es la que sí es definitiva. Por debajo de 15 se levanta y ya
    # no se baja: ahí el umbral `credibilidad_comite_definitivo`, que hasta
    # ahora no producía ningún comportamiento distinto del de 30, empieza a
    # significar algo.
    comite_retirado_definitivo: bool = False
    encuadre_dominante: str = "desorden"  # represion|desorden|negociacion|abandono

    # LAS INSTALACIONES DECLARADAS CRÍTICAS, por su nombre. Es la lista que
    # inmoviliza fuerza (`force.capacidad_inmovilizada_por_custodia`) y la que
    # cuenta el tablero. El REGISTRO de qué infraestructura existe en el país es
    # `infraestructura`, más abajo: una cosa es lo que hay y otra lo que la mesa
    # decidió custodiar.
    instalaciones_criticas: list[str] = field(default_factory=list)
    frentes_rurales_descubiertos: int = 0

    # --- el frente agroalimentario ---------------------------------------
    #
    # LOS PUNTOS RURALES DONDE AGRICULTURA SE SENTÓ. No basta con `mesa_abierta`
    # en el nodo: eso dice que HAY mesa, no de quién es. Y de quién es importa,
    # porque el Ministro del Interior tiene que poder ver cuántos canales
    # paralelos al suyo hay abiertos — que es exactamente lo que la ficha del
    # rol anuncia como su fricción principal.
    mesas_tecnicas_agro: list[str] = field(default_factory=list)

    # Cuántos paquetes de alivio ha activado cada región. El segundo rinde la
    # mitad que el primero: los instrumentos de la cartera no alcanzan a la
    # escala del daño, y repetirlos no los hace alcanzar.
    instrumentos_sectoriales: dict[str, int] = field(default_factory=dict)

    # EL RIESGO SANITARIO ASUMIDO, hermano del riesgo de infraestructura: no
    # produce ningún daño dentro del episodio y se cobra entero en el
    # debriefing. Cada autorización excepcional de movilizar animales por rutas
    # alternas mueve ganado sin control sanitario pleno, y eso se paga meses
    # después y contra esta misma cartera.
    riesgo_sanitario_asumido: int = 0

    # LA INFRAESTRUCTURA RELEVANTE DEL PAÍS, con nombre y con sitio. Se carga del
    # escenario y no se crea en la corrida: es la guía de lo que hay que
    # proteger, y sin ella `DeclararInfraestructuraCritica` se pedía a ciegas
    # sobre una cadena de texto que nadie validaba contra nada.
    infraestructura: dict[str, Infraestructura] = field(default_factory=dict)

    # H1 del paquete detonante, tal como llega en el parte heredado. Es texto
    # para la sala, no una variable: el motor ya aplicó sus efectos al cargar.
    hecho_h1: dict = field(default_factory=dict)

    # UN SOLO BOLSILLO DE TRES: verificar un punto, verificar una denuncia o
    # acompañar una operación salen de aquí. Se repone al empezar cada turno.
    equipos_disponibles: int = P.EQUIPOS_TERRENO_TOTALES
    equipos_usados_en: list[str] = field(default_factory=list)

    denuncias: list[Denuncia] = field(default_factory=list)
    acuerdos: list[Acuerdo] = field(default_factory=list)

    # Región epicentro: la jurisdicción del Alcalde de la mesa
    region_epicentro: str = ""

    # LA GEOGRAFÍA DEL PAÍS: costa, frontera, un polígono por región y los sitios
    # con nombre. Se carga del escenario y no se toca en toda la corrida.
    #
    # Vive aquí y no en la pantalla porque el mapa dejó de ser un esquema y pasó
    # a afirmar en qué región está cada bloqueo. Con el polígono en el estado, el
    # loader puede EXIGIR que cada punto caiga dentro del suyo y la movilización
    # puede colocar ahí dentro los cierres que genera sola. Dibujado a mano en el
    # frontend, ninguna de las dos cosas sería posible.
    geografia: dict = field(default_factory=dict)

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

    @property
    def jornada_visible(self) -> int:
        """
        Qué jornada está viviendo la sala AHORA MISMO.

        No es lo mismo que `turno_decision`, y confundirlas se ve en la pared.
        `turno_decision` cuenta jornadas RESUELTAS: sube cuando el motor da el
        paso, esto es, al final del día. Mientras la sala delibera la jornada 2,
        el motor todavía va por la 1 — y el tablero tiene que decir 2, porque es
        lo que se está jugando.

        `jornada_abierta` la levanta `MotorCrisis.abrir_jornada()` cuando empieza
        el día; el máximo cubre a quien corre el motor sin reloj de sala, como
        hacen las pruebas y el corredor sin interfaz.
        """
        return max(self.turno_decision, self.jornada_abierta)

    def reloj(self) -> dict:
        """
        Qué día es dentro del ejercicio, y cuántos quedan. Nada más.

        **Es un indicador de plazo, no un calendario.** La hora exacta de cada
        ventana estuvo aquí y se retiró: nadie decide distinto por saber que la
        ventana va de 06:00 a 18:00, y esa línea le quitaba sitio en la cabecera
        a lo único del reloj que sí cambia una decisión —cuántas jornadas
        quedan—. Queda la fecha ficticia como ancla («11 de mayo»), la jornada
        sobre el total, y si es de día o de noche.

        VIVE EN EL MOTOR, no en la interfaz. Diez pantallas calculando cada una
        su propia fecha son diez relojes, y la discrepancia se ve el primer turno.

        Y el plazo no es adorno: una concertación tarda dos jornadas en rendir,
        de modo que abrirla en la jornada 5 es no abrirla.
        """
        jornada = self.jornada_visible
        arranque = datetime.fromisoformat(P.FECHA_INICIO)
        hoy = arranque + timedelta(days=max(0, jornada - 1))

        return {
            "jornada": jornada,                  # 0 antes de la apertura
            "jornadas_totales": P.TURNOS_DECISION,
            "jornadas_restantes": max(0, P.TURNOS_DECISION - jornada),
            "franja": self.franja,
            "fecha": _fecha_larga(hoy),
            "ventana": self.turno,               # 1..9; 0 antes de empezar
            "ventanas_totales": P.VENTANAS_TOTALES,
            # Para pintar la barra de jornadas sin que la interfaz reconstruya
            # el calendario por su cuenta. Una marca por jornada y ninguna más:
            # la de día y la de noche por separado eran diez marcas para decir lo
            # que dicen cinco.
            "linea": [
                {
                    "jornada": j,
                    "fecha": _fecha_corta(arranque + timedelta(days=j - 1)),
                    "estado": ("pendiente" if jornada == 0
                               else "cumplida" if j < jornada
                               else "actual" if j == jornada else "pendiente"),
                }
                for j in range(1, P.TURNOS_DECISION + 1)
            ],
            # Redundante con `jornada` y `franja`, pero es la línea que se lee en
            # voz alta y no conviene que cada pantalla la componga a su manera.
            "etiqueta": (
                "antes de la apertura" if jornada == 0
                else f"jornada {jornada} de {P.TURNOS_DECISION} · "
                     f"{'día' if self.franja == 'dia' else 'noche'}"
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
        cuándo son las nueve vistas privadas (`views.py`).

        NUNCA incluye `composicion_real` ni la veracidad de una denuncia. Si eso
        se filtrara, el dilema central del caso desaparecería.

        LA `lectura` DE CADA PUNTO Y DE CADA REGIÓN
        -------------------------------------------
        Desde que el mapa es interactivo, cada punto trae sus seis hechos
        observables —caudal, dureza, masa, días, apoyo del barrio, control de la
        vocería— y cada región los mismos seis promediados sobre sus puntos. Los
        calcula `territory.py`, que es el único sitio donde se calculan.

        **Salen en banda y no en número.** Es la misma frontera que separa
        «Legitimidad: alta» de «Muertes evitables: 3» en el resto del tablero: un
        índice se interpreta, un entero de personas o de días se cuenta. Y no
        abren ninguna puerta de atrás a la capa 1: la mezcla real de un punto no
        se deriva de ninguna de las seis, ni sola ni combinada.
        """
        # Import local: `territory` importa de aquí, y al revés sería un ciclo.
        from src.engine import territory

        lecturas = territory.lecturas_por_region(self)

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
                    # Las seis lecturas promediadas, más el estado de bloqueo.
                    # NO es el semáforo: una región puede estar despejada y
                    # quedarse sin oxígeno porque su corredor empieza en otra.
                    "lectura": lecturas.get(r.region_id, {}),
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
                    # QUÉ SE ESTÁ HACIENDO AQUÍ, que no es lo mismo que cómo se
                    # abrió. `modo_apertura` solo habla de los puntos abiertos:
                    # un punto operado con ESMAD que no cedió y un punto que
                    # nadie ha tocado salían los dos como «cerrado», y son dos
                    # conversaciones distintas en la sala.
                    "intervencion": territory.intervencion_nodo(
                        n, self.jornada_visible),
                    "mesa": territory.mesa_nodo(n, self.jornada_visible),
                    "verificado_turno": n.ultima_verificacion_turno,
                    "x": n.x,
                    "y": n.y,
                    "lectura": territory.lectura_nodo(n),
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
            # LA INFRAESTRUCTURA RELEVANTE, con su estado de protección. Es
            # pública: dónde está la refinería no es un secreto de Estado, y el
            # objeto del ejercicio no es esconderla sino que la mesa decida si
            # gasta fuerza en custodiarla. Su criticidad sale en palabra y no en
            # índice, por la misma razón que el resto del tablero.
            "infraestructura": [
                i.vista_publica() for i in self.infraestructura.values()
            ],
            # El país: costa, frontera, un polígono por región y los sitios con
            # nombre. Es constante durante toda la corrida y va aquí igualmente:
            # una segunda ruta para servirlo obligaría a la pantalla a componer
            # dos respuestas que pueden llegar en cualquier orden, y el mapa se
            # dibujaría a medias en el arranque de la sesión, que es justo cuando
            # todo el mundo está mirando.
            "geografia": self.geografia,
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
