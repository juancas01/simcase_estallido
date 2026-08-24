"""
actions.py — Las acciones de los ocho roles.

Patrón heredado de Macondo, con una adición propia de este caso:

    validar()  → ¿es viable AHORA? NO muta nada.
    ejecutar() → aplica el efecto. Devuelve SIEMPRE resultado estructurado.
    requisitos_de_otros_roles → quién más tiene que actuar

Trece de las cuarenta acciones no se pueden ejecutar solas. Cuando falta el
requisito, validar() devuelve QUIÉN puede habilitarlo, no un rechazo seco. Eso
empuja la conversación de vuelta a la sala, que es donde el ejercicio la quiere.

DOS CLASES DE ACCIÓN
--------------------
    CONSTITUTIVAS  cambian cómo funciona la mesa; activan una bandera
                   persistente; casi no cuestan; modifican TODO lo posterior
    OPERATIVAS     cambian el territorio; efecto inmediato; se agotan en su turno

Ninguna constitutiva está bloqueada y ninguna es obligatoria. El diseño no
fuerza a la sala a constituirse: le permite saltárselo y le cobra la diferencia.
Un bloqueo duro se siente como un riel; un precio se siente como una consecuencia.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

from src.engine import parameters as P
from src.engine import force, aperture, supply, information
from src.engine.state import Estado

Clase = Literal["constitutiva", "operativa"]


@dataclass
class Resultado:
    ok: bool
    mensaje: str
    datos: dict = field(default_factory=dict)
    requisitos_faltantes: list[str] = field(default_factory=list)


@dataclass
class Validacion:
    ok: bool
    motivo: str | None = None
    requisitos_faltantes: list[str] = field(default_factory=list)
    habilitada_por: list[str] = field(default_factory=list)
    parcial: bool = False


class Accion:
    codigo: str = "A0"
    rol: str = ""
    clase: Clase = "operativa"
    descripcion: str = ""

    def validar(self, estado: Estado) -> Validacion:
        return Validacion(ok=True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        raise NotImplementedError


# ===========================================================================
# CONSTITUTIVAS — las que de verdad inician la gestión (§5.5)
# ===========================================================================

@dataclass
class FijarRegistroEscrito(Accion):
    """Presidente · A2 — qué se decide en el centro y qué se delega."""
    codigo = "A2"
    rol = "Presidente"
    clase: Clase = "constitutiva"
    descripcion = "Nodo único de coordinación y registro escrito con responsable nominado"

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        nuevo = estado.banderas.activar("registro_escrito", estado.turno)
        estado.banderas.activar("nodo_unico", estado.turno)
        if not nuevo:
            return Resultado(True, "El registro escrito ya estaba vigente.")
        return Resultado(True, (
            "Registro escrito vigente. A partir de ahora cada incidente es "
            "ATRIBUIBLE a quien firmó, en vez de repartirse sobre los ocho."
        ), {"bandera": "registro_escrito"})


@dataclass
class ExigirEstandaresEmpleo(Accion):
    """
    Defensoría · A1 — condicionar su permanencia a estándares escritos.

    Enciende TRES mitigadores de golpe. Es la acción de mayor rendimiento del
    ejercicio y la que menos se parece a una acción.
    """
    codigo = "A1"
    rol = "Defensoría"
    clase: Clase = "constitutiva"
    descripcion = "Reglas de empleo escritas, identificación de agentes, registro audiovisual"
    exigencias: int = 3     # >3 simultáneas y la mesa lo aísla

    def validar(self, estado: Estado) -> Validacion:
        if not estado.banderas.defensoria_presente:
            return Validacion(False, "La Defensoría se retiró de la mesa.")
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        if self.exigencias > 3:
            estado.eventos_turno.append({"tipo": "defensoria_aislada"})
            return Resultado(False, (
                "Condicionó sin priorizar: la mesa lo aísla. Pierde acceso y su "
                "palanca desaparece justo cuando se decide el escalamiento."
            ))
        for b in ("reglas_escritas", "identificacion_agentes", "registro_av"):
            estado.banderas.activar(b, estado.turno)
        estado.reservas.aplicar({"exposicion_internacional": -10.0})
        return Resultado(True, (
            "Estándares adoptados. Tres mitigadores activos: la probabilidad de "
            "incidente en toda operación futura cae a poco más de la mitad."
        ), {"mitigadores": ["reglas_escritas", "identificacion_agentes", "registro_av"]})


@dataclass
class AdoptarProtocoloVerificacion(Accion):
    """Defensoría · A2 — una sola cifra oficial, clasificada."""
    codigo = "A2"
    rol = "Defensoría"
    clase: Clase = "constitutiva"
    descripcion = "Protocolo único de verificación de cifras y denuncias"

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_verificacion", estado.turno)
        return Resultado(True, (
            "Protocolo único de verificación vigente. Las cifras salen "
            "clasificadas en confirmado, estimado y en verificación."
        ))


@dataclass
class ExigirProtocoloVoceria(Accion):
    """Interior · A4 — plazo suspensivo sobre operaciones con efecto en el diálogo."""
    codigo = "A4"
    rol = "Interior"
    clase: Clase = "constitutiva"
    descripcion = "Protocolo de vocería y plazo suspensivo de 24 h"

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_voceria", estado.turno)
        estado.banderas.activar("plazo_suspensivo", estado.turno)
        return Resultado(True, (
            "Protocolo de vocería vigente y plazo suspensivo de 24 h sobre toda "
            "operación con efecto en el diálogo. Cuesta un turno de demora."
        ))


@dataclass
class AdoptarCriterioPriorizacion(Accion):
    """Transporte · A1 — el criterio único de asignación de fuerza."""
    codigo = "A1"
    rol = "Transporte"
    clase: Clase = "constitutiva"
    descripcion = "Priorización por población, autonomía y costo diario"

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("criterio_priorizacion", estado.turno)
        orden = sorted(
            estado.corredores.values(),
            key=lambda c: (-c.poblacion_aguas_abajo, -c.costo_diario_mm_cop),
        )
        return Resultado(True, (
            "Criterio único de priorización adoptado. La asignación de fuerza "
            "deja de pelearse políticamente cada turno."
        ), {"orden": [c.nombre for c in orden]})


@dataclass
class FijarLineasRojas(Accion):
    """Presidente · A3 — el marco de lo negociable."""
    codigo = "A3"
    rol = "Presidente"
    clase: Clase = "constitutiva"
    descripcion = "Líneas rojas del Ejecutivo y marco de lo negociable"
    margen: float = 0.5     # 0 = sin margen, 1 = todo negociable

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("lineas_rojas_fijadas", estado.turno)
        if self.margen < 0.25:
            estado.reservas.aplicar({"credibilidad_mesa": -8.0})
            return Resultado(True, (
                "Líneas rojas fijadas sin margen. Cierran anticipadamente el "
                "espacio del Ministro del Interior: cualquier acuerdo posterior "
                "será una capitulación pública."
            ))
        return Resultado(True, "Líneas rojas fijadas. La posición del Gobierno queda ordenada.")


# ===========================================================================
# OPERATIVAS
# ===========================================================================

@dataclass
class OperarNodo(Accion):
    """Defensa · A4 / Policía · A1 — aplicar fuerza sobre un punto de cierre."""
    codigo = "A4"
    rol = "Defensa"
    clase: Clase = "operativa"
    descripcion = "Operación de desbloqueo sobre un nodo"

    nodo_id: str = ""
    tipo_unidad: str = "esmad"
    dupla_presente: bool = False
    concertado_con_alcaldia: bool = False
    responsable_nominado: str | None = None
    de_noche: bool = False

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el nodo {self.nodo_id}.")
        if nodo.abierto:
            return Validacion(False, f"{nodo.nombre} ya está abierto.")

        faltan, habilita = [], []
        if self.tipo_unidad == "esmad" and not estado.esmad_disponible():
            faltan.append("ESMAD disponible")
            habilita.append("Director de Policía (A1: concentrar) o Defensa (A2: redesplegar)")
        if self.tipo_unidad == "militar" and not estado.banderas.asistencia_militar_firmada:
            faltan.append("asistencia militar firmada")
            habilita.append("Presidente (A1)")
        if estado.banderas.plazo_suspensivo and not self.concertado_con_alcaldia:
            return Validacion(
                True, parcial=True,
                motivo="Plazo suspensivo vigente: la operación se difiere un turno.",
                habilitada_por=["Ministro del Interior"],
            )
        if faltan:
            return Validacion(False, "Faltan requisitos.", faltan, habilita)
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        nodo = estado.nodos[self.nodo_id]
        unidades = (estado.esmad_disponible()[:2] if self.tipo_unidad == "esmad"
                    else [u for u in estado.unidades if u.tipo == self.tipo_unidad][:2])

        res = force.ejecutar_operacion(
            estado, nodo, self.tipo_unidad, unidades, rng,
            dupla_presente=self.dupla_presente,
            concertado_con_alcaldia=self.concertado_con_alcaldia,
            responsable_nominado=self.responsable_nominado,
        )

        from src.engine import mobilization

        if res.exito:
            aperture.abrir_por_fuerza(nodo, rng, estado.turno)
            estado.eventos_turno.append({"tipo": "apertura", "nodo": nodo.nodo_id, "via": "fuerza"})

        if res.hubo_incidente:
            if res.victimas > 0:
                estado.reservas.aplicar(P.COSTO_RESERVAS["incidente_con_victima"])
                mobilization.registrar_evento(estado, "incidente_mortal", nodo.region_id)
            if res.imagen_viral:
                estado.reservas.aplicar(P.COSTO_RESERVAS["imagen_viral"])
                mobilization.registrar_evento(estado, "imagen_viral", nodo.region_id)
            if not res.atribuible:
                estado.reservas.aplicar(P.COSTO_RESERVAS["sin_registro_escrito"])

        if self.tipo_unidad == "militar":
            mobilization.registrar_evento(estado, "militares_en_multitudes", nodo.region_id)

        if estado.comite_disponible and estado.franja == "dia":
            estado.reservas.aplicar(P.COSTO_RESERVAS["operacion_dia_de_mesa"])

        return Resultado(res.exito, res.mensaje, {
            "p_incidente": round(res.p_usada, 3),
            "tirada": round(res.tirada, 3),
            "victimas": res.victimas,
            "viral": res.imagen_viral,
            "atribuible": res.atribuible,
        })


@dataclass
class AbrirMesaLocal(Accion):
    """Alcalde · A1 / Interior · A2 — concertar la apertura de un nodo."""
    codigo = "A1"
    rol = "Alcalde de Cali"
    clase: Clase = "operativa"
    descripcion = "Mesa local de desbloqueo con voceros del punto de resistencia"
    nodo_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el nodo {self.nodo_id}.")
        if not estado.comite_disponible and nodo.control_voceria > 0.5:
            return Validacion(False, "El Comité del Paro suspendió su participación.")
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        nodo = estado.nodos[self.nodo_id]
        r = aperture.avanzar_concertacion(nodo, estado.turno)
        if r is None:
            return Resultado(True, (
                f"Mesa instalada en {nodo.nombre}. La concertación necesita "
                f"otro turno para producir apertura."
            ), {"en_curso": True})

        from src.engine import mobilization
        estado.eventos_turno.append({"tipo": "apertura", "nodo": nodo.nodo_id, "via": "concertacion"})
        estado.reservas.aplicar(P.COSTO_RESERVAS["apertura_concertada"])
        mobilization.registrar_evento(estado, "apertura_concertada", nodo.region_id)
        return Resultado(True, r.mensaje, {"caudal": round(r.caudal, 2)})


@dataclass
class EsquemaHumanitarioMunicipal(Accion):
    """
    Alcalde · A4 — abastecimiento a barrios aislados y ollas comunitarias.

    La única vía de apertura que no consume ninguna reserva: baja `apoyo_local`
    sin alimentar la movilización.
    """
    codigo = "A4"
    rol = "Alcalde de Cali"
    clase: Clase = "operativa"
    descripcion = "Esquema humanitario municipal"
    region_id: str = ""

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        mobilization.erosionar_apoyo_local(
            estado, self.region_id, P.DESGASTE_POR_ESQUEMA_HUMANITARIO
        )
        return Resultado(True, (
            "Esquema humanitario activado. Baja el incentivo material del cierre "
            "sin alimentar la movilización — pero consume recursos distritales y "
            "el Gobierno Nacional puede leerlo como sostenimiento del bloqueo."
        ))


@dataclass
class DeclararInfraestructuraCritica(Accion):
    """Minas · A1 — protección permanente, con la inmovilización que implica."""
    codigo = "A1"
    rol = "Minas y Energía"
    clase: Clase = "operativa"
    descripcion = "Declaratoria de infraestructura crítica"
    instalaciones: list[str] = field(default_factory=list)

    def validar(self, estado: Estado) -> Validacion:
        cupo = len(estado.esmad_disponible())
        necesita = len(self.instalaciones) * P.CUSTODIA_POLICIAS_POR_INSTALACION
        if necesita > cupo * 2:
            return Validacion(
                True, parcial=True,
                motivo=(f"Inmovilizaría {necesita} unidades y la capacidad libre "
                        f"no alcanza. Se protegerá lo que se pueda."),
                habilitada_por=["Ministro de Defensa (A2: redesplegar militares)"],
            )
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.instalaciones_criticas.extend(self.instalaciones)
        inmovilizadas = force.capacidad_inmovilizada_por_custodia(estado)
        for u in estado.esmad_disponible()[: len(self.instalaciones)]:
            u.asignacion = "custodia"
        return Resultado(True, (
            f"{len(self.instalaciones)} instalación(es) bajo protección permanente. "
            f"Inmoviliza {inmovilizadas} unidades que Seguridad necesitaba para "
            f"desbloquear: la mesa tendrá que aplazar corredores."
        ), {"inmovilizadas": inmovilizadas})


@dataclass
class FirmarAsistenciaMilitar(Accion):
    """Presidente · A1 — la única firma que habilita capacidad militar."""
    codigo = "A1"
    rol = "Presidente"
    clase: Clase = "operativa"
    descripcion = "Acto administrativo de asistencia militar (Ley 1801 de 2016)"
    delimitada: bool = False    # territorio + plazo + reglas + criterio de terminación

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        estado.banderas.activar("asistencia_militar_firmada", estado.turno)

        if self.delimitada:
            estado.banderas.activar("asistencia_militar_delimitada", estado.turno)
            estado.banderas.activar("reglas_escritas", estado.turno)
            estado.reservas.aplicar({"exposicion_internacional": 8.0, "legitimidad": -5.0})
            for u in [u for u in estado.unidades if u.asignacion == "custodia"][:6]:
                u.asignacion = "reserva"
            msg = ("Asistencia militar firmada CON delimitación territorial, plazo, "
                   "reglas escritas y criterio de terminación. Habilita capacidad "
                   "y libera ESMAD de la custodia estática.")
        else:
            estado.reservas.aplicar({"exposicion_internacional": 22.0, "legitimidad": -15.0})
            mobilization.registrar_evento(estado, "militares_en_multitudes")
            estado.encuadre_dominante = "represion"
            msg = ("Asistencia militar firmada SIN delimitación ni reglas escritas. "
                   "Entrega a la narrativa de represión su mejor argumento.")

        return Resultado(True, msg, {"delimitada": self.delimitada})


@dataclass
class SolicitarRelevo(Accion):
    """Policía · A5 — menos fatiga a cambio de menos cobertura."""
    codigo = "A5"
    rol = "Director de Policía"
    clase: Clase = "operativa"
    descripcion = "Relevo y rotación de unidades agotadas"
    n_unidades: int = 6

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        n = force.solicitar_relevo(estado, self.n_unidades)
        return Resultado(True, (
            f"{n} unidad(es) en relevo. Baja la fatiga —el principal factor de "
            f"error— a costa de reducir la cobertura simultánea de puntos."
        ), {"relevadas": n})


@dataclass
class DesplegarDuplas(Accion):
    """Defensoría · A3 — verificar en terreno. Cobertura: 3 nodos por turno."""
    codigo = "A3"
    rol = "Defensoría"
    clase: Clase = "operativa"
    descripcion = "Duplas de verificación en puntos priorizados"
    nodos: list[str] = field(default_factory=list)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        r = information.desplegar_duplas(estado, self.nodos, estado.turno, rng)
        if not r["ok"]:
            return Resultado(False, r["motivo"])
        msg = f"Verificados {len(r['verificados'])} nodos."
        if r.get("aviso"):
            msg += " " + r["aviso"]
        return Resultado(True, msg, {
            "verificados": [e.nodo_id for e in r["verificados"]],
            "no_alcanzados": r["no_alcanzados"],
        })


@dataclass
class EntregarCalendarioAgotamiento(Accion):
    """Minas · A4 — el reloj de la crisis, con su efecto sobre el reloj."""
    codigo = "A4"
    rol = "Minas y Energía"
    clase: Clase = "operativa"
    descripcion = "Calendario de agotamiento por región"

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        r = supply.difundir_calendario(estado)
        return Resultado(True, (
            "Calendario entregado a la mesa. Convierte la deliberación en un "
            "plazo — y acelera aquello que mide: el pánico sube y el consumo "
            "con él."
        ), r)


CATALOGO = [
    FijarRegistroEscrito, FijarLineasRojas, ExigirEstandaresEmpleo,
    AdoptarProtocoloVerificacion, ExigirProtocoloVoceria, AdoptarCriterioPriorizacion,
    OperarNodo, AbrirMesaLocal, EsquemaHumanitarioMunicipal,
    DeclararInfraestructuraCritica, FirmarAsistenciaMilitar, SolicitarRelevo,
    DesplegarDuplas, EntregarCalendarioAgotamiento,
]
