"""
actions.py — Las acciones de los ocho roles.

Treinta y cuatro acciones, entre cuatro y cinco por rol. El Presidente tiene
cinco porque decide más; la Defensoría también, porque cruza dos ejes sin mandar
sobre nadie.

    Constituye     cambia cómo funciona la mesa. Activa una bandera persistente.
                   Casi no cuesta y modifica TODO lo posterior.
    Toca el mundo  cambia el territorio, la fuerza o el abastecimiento.
                   Efecto inmediato; se agota en su turno.
    Informa        cambia lo que el país tiene por cierto.
                   Hablar es gratis; hacerlo oficial tiene consecuencia.

**Cada rol tiene al menos una de cada clase**, y eso es lo que garantiza que
ningún participante pase el ejercicio sin nada que hacer.

EL PATRÓN
---------
    validar()                    ¿es viable AHORA? NO muta nada.
    ejecutar()                   aplica el efecto. SIEMPRE resultado estructurado.
    requisitos_de_otros_roles    quién más tiene que actuar.

Cuando falta un requisito, `validar()` devuelve **quién puede habilitarlo**, no
un rechazo seco. Eso empuja la conversación de vuelta a la sala, que es donde el
ejercicio la quiere.

NINGUNA CONSTITUTIVA ESTÁ BLOQUEADA Y NINGUNA ES OBLIGATORIA. El diseño no
fuerza a la sala a constituirse: le permite saltárselo y le cobra la diferencia.
Un bloqueo duro se siente como un riel; un precio se siente como una consecuencia.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

from src.engine import parameters as P
from src.engine import force, aperture, supply, information
from src.engine.state import Estado, Acuerdo

Clase = Literal["constitutiva", "operativa", "informativa"]


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

    # DOS DESCRIPCIONES, PARA DOS LECTORES DISTINTOS.
    #
    #   `descripcion`  el nombre formal del acto — «Acto administrativo de
    #                  asistencia militar». Va al pliego, que es un registro, y
    #                  ahí el registro formal es lo correcto.
    #
    #   `en_claro`     qué hace y qué cambia, en dos frases y sin jerga. Es lo
    #                  que lee quien tiene que decidir si pedirlo.
    #
    # No son el mismo dato con dos redacciones: son dos informaciones distintas
    # para dos lectores distintos. Quien lee su repertorio no necesita el nombre
    # del acto administrativo — necesita saber qué puede pedir.
    descripcion: str = ""
    en_claro: str = ""

    def validar(self, estado: Estado) -> Validacion:
        return Validacion(ok=True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        raise NotImplementedError


# ===========================================================================
# 01 · PRESIDENTE DE LA REPÚBLICA — 5
# ===========================================================================

@dataclass
class FijarRegistroEscrito(Accion):
    """Nodo único de coordinación y registro escrito con responsable nominado."""
    codigo = "A2"
    rol = "Presidente"
    clase: Clase = "constitutiva"
    descripcion = "Nodo único de coordinación y registro escrito de decisiones"
    en_claro = (
        "Deja por escrito cada decisión y quién responde por ella. Sin "
        "registro, al cierre nadie puede decir quién ordenó qué.")

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
class FijarLineasRojas(Accion):
    """Las líneas rojas del Ejecutivo y el marco de lo negociable."""
    codigo = "A3"
    rol = "Presidente"
    clase: Clase = "constitutiva"
    descripcion = "Líneas rojas del Ejecutivo y marco de lo negociable"
    en_claro = (
        "Anuncia qué está y qué no está sobre la mesa. Fija el terreno de lo "
        "negociable antes de que lo fije otro.")
    margen: float = 0.5     # 0 = sin margen, 1 = todo negociable

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("lineas_rojas_fijadas", estado.turno)
        if self.margen < 0.25:
            estado.reservas.aplicar({"credibilidad_mesa": -8.0})
            return Resultado(True, (
                "Líneas rojas fijadas SIN MARGEN. Cierran anticipadamente el "
                "espacio del Ministro del Interior: cualquier acuerdo posterior "
                "será una capitulación pública."
            ), {"margen": self.margen})
        return Resultado(True, (
            "Líneas rojas fijadas. La posición del Gobierno queda ordenada y "
            "cada acuerdo que traiga Interior deja de renegociarse en la sala."
        ), {"margen": self.margen})


@dataclass
class FirmarAsistenciaMilitar(Accion):
    """La única firma que habilita capacidad militar (Ley 1801 de 2016)."""
    codigo = "A1"
    rol = "Presidente"
    clase: Clase = "operativa"
    descripcion = "Acto administrativo de asistencia militar"
    en_claro = (
        "Autoriza que el Ejército apoye a la Policía. Da más fuerza "
        "disponible, y militares frente a multitudes suben la tensión en la "
        "calle.")
    delimitada: bool = False    # territorio + plazo + reglas + criterio de terminación

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        estado.banderas.activar("asistencia_militar_firmada", estado.turno)

        if self.delimitada:
            estado.banderas.activar("asistencia_militar_delimitada", estado.turno)
            estado.banderas.activar("reglas_escritas", estado.turno)
            estado.reservas.aplicar(
                {"respaldo_internacional": -8.0, "legitimidad": -5.0}
            )
            liberadas = [u for u in estado.unidades if u.asignacion == "custodia"][:6]
            for u in liberadas:
                u.asignacion = "reserva"
                u.ubicacion = None
            msg = (
                "Asistencia militar firmada CON delimitación territorial, plazo, "
                "reglas escritas y criterio de terminación. Habilita capacidad "
                f"militar y libera {len(liberadas)} unidad(es) de la custodia."
            )
        else:
            estado.reservas.aplicar(
                {"respaldo_internacional": -22.0, "legitimidad": -15.0}
            )
            mobilization.registrar_evento(estado, "militares_en_multitudes")
            estado.encuadre_dominante = "represion"
            msg = (
                "Asistencia militar firmada SIN delimitación ni reglas escritas. "
                "Entrega a la narrativa de represión su mejor argumento."
            )

        estado.reservas.aplicar({"credibilidad_mesa": -12.0})
        return Resultado(True, msg, {"delimitada": self.delimitada})


@dataclass
class ConvocarAlcaldes(Accion):
    """Pactar con los alcaldes de las ciudades críticas reglas de empleo y vocería."""
    codigo = "A4"
    rol = "Presidente"
    clase: Clase = "operativa"
    descripcion = "Convocatoria a los alcaldes de las ciudades críticas"
    en_claro = (
        "Reúne a los alcaldes de las ciudades más golpeadas. Sirve para "
        "llegar a la mesa con una sola posición en vez de varias.")
    concede_prioridad: bool = False   # ¿se le da prioridad de fuerza al epicentro?

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_voceria", estado.turno)
        if self.concede_prioridad:
            estado.banderas.activar("concertacion_previa_cali", estado.turno)
            estado.reservas.aplicar({"cohesion_mesa": 4.0, "legitimidad": 2.0})
            return Resultado(True, (
                "Acuerdo con los alcaldes: corresponsabilidad territorial y "
                "concertación previa del empleo de la fuerza. Baja la disputa de "
                "vocería, al precio de comprometer prioridad de fuerza."
            ))
        estado.reservas.aplicar({"cohesion_mesa": 2.0})
        return Resultado(True, (
            "Convocatoria atendida, sin conceder prioridad. Se alinea el mensaje, "
            "pero el mandatario del epicentro sale con un incumplimiento visible "
            "que hará público."
        ), {"agravio_territorial": True})


@dataclass
class DesplazarseAlEpicentro(Accion):
    """Ir o no ir. Consume escolta y lo expone."""
    codigo = "A5"
    rol = "Presidente"
    clase: Clase = "informativa"
    descripcion = "Desplazamiento presidencial al epicentro"
    en_claro = (
        "Viaja en persona a la ciudad más afectada. Es un gesto público de "
        "que el Gobierno da la cara.")
    acompana: str = "ninguna"    # operacion | mesa | ninguna

    def validar(self, estado: Estado) -> Validacion:
        if len(estado.esmad_en_reserva()) < 2:
            return Validacion(False, (
                "No hay escolta disponible: el desplazamiento presidencial "
                "consume capacidad que hoy no existe."
            ), habilitada_por=["Director de Policía (disponer del ESMAD)"])
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        for u in estado.esmad_en_reserva()[:2]:
            u.asignacion = "escolta"
            u.ubicacion = "presidencia"

        if self.acompana == "mesa":
            estado.reservas.aplicar({"credibilidad_mesa": 6.0, "legitimidad": 3.0})
            msg = ("El Presidente acompaña la mesa en el epicentro. Reduce la "
                   "crítica de lentitud y respalda el canal de diálogo.")
        elif self.acompana == "operacion":
            estado.reservas.aplicar({"legitimidad": -2.0, "cohesion_mesa": 3.0})
            estado.encuadre_dominante = "represion"
            msg = ("El Presidente acompaña la operación. Asume la decisión como "
                   "propia —el sector deja de cargarla solo— y queda identificado "
                   "con ella.")
        else:
            estado.reservas.aplicar({"legitimidad": 1.0})
            msg = ("El Presidente se desplaza sin acompañar ninguna de las dos. "
                   "Hace verificable la prioridad territorial sin comprometerse.")

        return Resultado(True, msg + " Consume 2 escuadrones de escolta.",
                         {"acompana": self.acompana})


# ===========================================================================
# 02 · MINISTRO DEL INTERIOR — 4
# ===========================================================================

@dataclass
class ExigirProtocoloVoceria(Accion):
    """Protocolo de vocería y plazo suspensivo de 24 h sobre las operaciones."""
    codigo = "A4"
    rol = "Interior"
    clase: Clase = "constitutiva"
    descripcion = "Protocolo de vocería y plazo suspensivo de 24 h"
    en_claro = (
        "Establece que una sola persona habla por el Gobierno. Evita que dos "
        "carteras digan cosas distintas el mismo día.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_voceria", estado.turno)
        estado.banderas.activar("plazo_suspensivo", estado.turno)
        return Resultado(True, (
            "Protocolo de vocería vigente y plazo suspensivo de 24 h sobre toda "
            "operación con efecto en el diálogo. Ninguna operación vuelve a "
            "sorprender a la mesa — y cuesta un turno de demora."
        ))


@dataclass
class ConvocarMesaNacional(Accion):
    """
    La sesión con el Comité del Paro.

    **Es la única acción del ejercicio que puede producir un acuerdo verificable**,
    que es el movimiento que más desinfla la movilización de todo el diseño. Sin
    ella el caso queda con un solo polo activo — la fuerza —, que es exactamente
    lo que la Matriz advirtió al justificar por qué este rol no se podía eliminar.
    """
    codigo = "A1"
    rol = "Interior"
    clase: Clase = "operativa"
    descripcion = "Sesión de la mesa nacional con el Comité del Paro"
    en_claro = (
        "Sienta al Gobierno con el Comité del Paro. Es la vía más rápida para "
        "bajar la tensión, y operar por la fuerza ese mismo día es lo que más "
        "caro le sale a la mesa.")
    nodos_pactados: list[str] = field(default_factory=list)

    def validar(self, estado: Estado) -> Validacion:
        if not estado.comite_disponible:
            return Validacion(False, (
                "El Comité del Paro suspendió su participación. La credibilidad "
                "de la mesa está por debajo del umbral en que vuelve a sentarse."
            ))
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization

        candidatos = self.nodos_pactados or [
            n.nodo_id for n in sorted(
                (x for x in estado.nodos.values() if not x.abierto),
                key=lambda x: -x.control_voceria,
            )[:P.NODOS_POR_ACUERDO_NACIONAL]
        ]
        candidatos = candidatos[:P.NODOS_POR_ACUERDO_NACIONAL]

        acuerdo = Acuerdo(
            acuerdo_id=f"AC-{len(estado.acuerdos) + 1:02d}",
            nodos=candidatos,
            turno_firmado=estado.turno_decision,
            turno_limite=estado.turno_decision + P.TURNOS_PARA_CUMPLIR_ACUERDO,
        )
        estado.acuerdos.append(acuerdo)

        abiertos = []
        for nid in candidatos:
            nodo = estado.nodos.get(nid)
            if nodo is None:
                continue
            caudal = P.CAUDAL_ACUERDO_NACIONAL * nodo.control_voceria / 0.6
            nodo.caudal = max(nodo.caudal, min(0.9, caudal))
            nodo.modo_apertura = "concertacion"
            abiertos.append(nid)
            estado.eventos_turno.append(
                {"tipo": "apertura", "nodo": nid, "via": "concertacion"}
            )

        mobilization.registrar_evento(estado, "apertura_concertada")
        estado.reservas.aplicar(P.COSTO_RESERVAS["apertura_concertada"])
        estado.encuadre_dominante = "negociacion"

        return Resultado(True, (
            f"Mesa nacional instalada. Acuerdo {acuerdo.acuerdo_id} sobre "
            f"{len(abiertos)} punto(s). **Vale mientras se cumpla**: si se opera "
            f"sobre cualquiera de ellos antes del turno "
            f"{acuerdo.turno_limite}, el acuerdo se rompe visiblemente."
        ), {"acuerdo": acuerdo.acuerdo_id, "nodos": abiertos,
            "turno_limite": acuerdo.turno_limite})


@dataclass
class AbrirMesaLocal(Accion):
    """
    Concertación corredor por corredor con vocerías territoriales.

    **En la jurisdicción del epicentro requiere al Alcalde**; en el resto del país
    no. Hasta la v2 esta acción vivía en la ficha del Alcalde y no comprobaba
    jurisdicción: un alcalde municipal acababa pactando cierres en dos regiones
    ajenas.
    """
    codigo = "A2"
    rol = "Interior"
    clase: Clase = "operativa"
    descripcion = "Mesa local de concertación, corredor por corredor"
    en_claro = (
        "Negocia un punto concreto para que lo desbloqueen sus propios "
        "voceros. Tarda dos turnos, y lo que se abre así aguanta mientras se "
        "cumpla lo pactado.")
    nodo_id: str = ""
    con_alcaldia: bool = False

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el punto {self.nodo_id}.")
        if nodo.abierto:
            return Validacion(False, f"{nodo.nombre} ya está abierto.")
        if not estado.comite_disponible and nodo.control_voceria > 0.5:
            return Validacion(False, (
                "El Comité del Paro suspendió su participación y la vocería de "
                "este punto responde a él."
            ))
        if nodo.region_id == estado.region_epicentro and not self.con_alcaldia:
            return Validacion(
                False,
                "Concertar en la jurisdicción del epicentro requiere a la Alcaldía.",
                requisitos_faltantes=["concertación con la Alcaldía"],
                habilitada_por=["Alcalde de la ciudad epicentro"],
            )
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        nodo = estado.nodos[self.nodo_id]
        r = aperture.avanzar_concertacion(nodo, estado.turno, rng)
        if r is None:
            return Resultado(True, (
                f"Mesa instalada en {nodo.nombre}. La concertación necesita otro "
                f"turno para producir apertura."
            ), {"en_curso": True})

        estado.eventos_turno.append(
            {"tipo": "apertura", "nodo": nodo.nodo_id, "via": "concertacion"}
        )
        estado.reservas.aplicar(P.COSTO_RESERVAS["apertura_concertada"])
        mobilization.registrar_evento(estado, "apertura_concertada", nodo.region_id)

        msg = r.mensaje
        if r.fragil:
            # La SEGUNDA vía por la que la mezcla real de un punto tiene
            # consecuencia: quien firmó no manda sobre quien sostiene el cierre.
            nodo.caudal *= 0.4
            estado.reservas.aplicar(P.COSTO_RESERVAS["acuerdo_incumplido"])
            mobilization.registrar_evento(estado, "acuerdo_incumplido", nodo.region_id)
            estado.eventos_turno.append(
                {"tipo": "acuerdo_incumplido", "nodo": nodo.nodo_id}
            )
            msg += (" El acuerdo se incumplió en cuestión de horas: quien firmó "
                    "no controla ese punto.")

        return Resultado(True, msg, {"caudal": round(nodo.caudal, 2), "fragil": r.fragil})


@dataclass
class OfrecerContraprestacion(Accion):
    """Trámite legislativo como contraprestación verificable. La moneda no violenta."""
    codigo = "A3"
    rol = "Interior"
    clase: Clase = "informativa"
    descripcion = "Contraprestación legislativa por el levantamiento de cierres"
    en_claro = (
        "Ofrece algo concreto a cambio de levantar los cierres. Funciona "
        "donde hay con quién negociar; no donde nadie manda.")

    def validar(self, estado: Estado) -> Validacion:
        if estado.banderas.lineas_rojas_fijadas is False:
            return Validacion(True, parcial=True, motivo=(
                "Sin líneas rojas fijadas, lo que se ofrezca se renegociará en la "
                "sala. Se puede ofrecer igual."
            ), habilitada_por=["Presidente (fijar líneas rojas)"])
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        if rng.random() < P.P_CONGRESO_RESPONDE:
            mobilization.registrar_evento(estado, "contraprestacion_tramitada")
            estado.reservas.aplicar({"credibilidad_mesa": 6.0, "legitimidad": 4.0})
            return Resultado(True, (
                "El Congreso da trámite a la medida. Es el resultado verificable "
                "que la mesa necesitaba: baja la presión en la calle sin gastar "
                "un solo escuadrón."
            ), {"tramitada": True})
        estado.reservas.aplicar({"credibilidad_mesa": -8.0, "legitimidad": -4.0})
        return Resultado(True, (
            "El Congreso no responde en el plazo ofrecido. El incumplimiento se "
            "imputa al Gobierno entero y refuerza a quienes sostienen que solo la "
            "fuerza produce efectos."
        ), {"tramitada": False})


# ===========================================================================
# 03 · ALCALDE DE LA CIUDAD EPICENTRO — 4
# ===========================================================================

@dataclass
class CondicionarEmpleoFuerza(Accion):
    """Condicionar el empleo de la fuerza en su jurisdicción a concertarla."""
    codigo = "A3"
    rol = "Alcalde"
    clase: Clase = "constitutiva"
    descripcion = "Concertación previa del empleo de la fuerza en su jurisdicción"
    en_claro = (
        "Exige que cualquier operación en su ciudad se acuerde antes con la "
        "Alcaldía. Baja el riesgo de que salga mal, y le quita velocidad a "
        "Defensa.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("concertacion_previa_cali", estado.turno)
        return Resultado(True, (
            "Condicionamiento público: en esta jurisdicción los puntos y el mando "
            "local se concertan con la Alcaldía. Operar sin concertar cuesta "
            "legitimidad adicional — y concertado, baja el riesgo de incidente."
        ))


@dataclass
class InstalarMesaConVoceros(Accion):
    """Mesa local con los voceros de un punto de su ciudad, por franjas horarias."""
    codigo = "A1"
    rol = "Alcalde"
    clase: Clase = "operativa"
    descripcion = "Mesa local de desbloqueo con voceros del punto"
    en_claro = (
        "Sienta a hablar a los voceros de un punto de su ciudad. Es la vía "
        "pactada, hecha desde el municipio.")
    nodo_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el punto {self.nodo_id}.")
        if nodo.region_id != estado.region_epicentro:
            return Validacion(
                False,
                f"{nodo.nombre} está fuera de su jurisdicción.",
                habilitada_por=["Ministro del Interior (mesa local de concertación)"],
            )
        if nodo.abierto:
            return Validacion(False, f"{nodo.nombre} ya está abierto.")
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        nodo = estado.nodos[self.nodo_id]
        r = aperture.avanzar_concertacion(nodo, estado.turno, rng)
        if r is None:
            return Resultado(True, (
                f"Mesa local instalada en {nodo.nombre}. La concertación necesita "
                f"otro turno para producir apertura."
            ), {"en_curso": True})

        estado.eventos_turno.append(
            {"tipo": "apertura", "nodo": nodo.nodo_id, "via": "concertacion"}
        )
        estado.reservas.aplicar(P.COSTO_RESERVAS["apertura_concertada"])
        mobilization.registrar_evento(estado, "apertura_concertada", nodo.region_id)

        msg = r.mensaje
        if r.fragil:
            nodo.caudal *= 0.4
            estado.reservas.aplicar(P.COSTO_RESERVAS["acuerdo_incumplido"])
            mobilization.registrar_evento(estado, "acuerdo_incumplido", nodo.region_id)
            msg += (" El acuerdo se incumplió: los voceros con quienes se pactó "
                    "no controlan ese punto.")
        return Resultado(True, msg, {"caudal": round(nodo.caudal, 2)})


@dataclass
class EsquemaHumanitarioMunicipal(Accion):
    """
    Abastecimiento a barrios aislados, atención a heridos, ollas comunitarias.

    **La única vía de apertura que no consume ninguna reserva**: baja el incentivo
    material del cierre sin alimentar la movilización. Es lenta y es gratis.
    """
    codigo = "A4"
    rol = "Alcalde"
    clase: Clase = "operativa"
    descripcion = "Esquema humanitario municipal"
    en_claro = (
        "Monta un paso para ambulancias, oxígeno y alimentos en su "
        "jurisdicción. No abre el punto: abre una ventana.")
    region_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        rid = self.region_id or estado.region_epicentro
        if rid != estado.region_epicentro:
            return Validacion(False, "El esquema municipal solo cubre su jurisdicción.")
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        rid = self.region_id or estado.region_epicentro
        mobilization.erosionar_apoyo_local(
            estado, rid, P.DESGASTE_POR_ESQUEMA_HUMANITARIO
        )
        return Resultado(True, (
            "Esquema humanitario activado. Baja el incentivo material del cierre "
            "sin alimentar la movilización — y consume recursos distritales que "
            "el Gobierno Nacional puede leer como sostenimiento del bloqueo."
        ), {"region": rid})


@dataclass
class PublicarParteMunicipal(Accion):
    """
    El parte verificado de su ciudad, y la disputa de la cifra nacional.

    Mejora la calidad de la información del sistema — pero si contradice al parte
    operacional sin protocolo común, profundiza la guerra de cifras.
    """
    codigo = "A2"
    rol = "Alcalde"
    clase: Clase = "informativa"
    descripcion = "Parte municipal verificado y disputa de la cifra nacional"
    en_claro = (
        "Publica su propio conteo de lo que pasó en la ciudad. Si contradice "
        "la cifra nacional, uno de los dos queda desmentido.")
    disputa_cifra: bool = True

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        nodos = estado.nodos_de_region(estado.region_epicentro)
        for n in nodos:
            if n.ultima_verificacion_turno is None:
                information.marcar_verificado(estado, n, "parte_municipal", estado.turno)

        if self.disputa_cifra and not estado.banderas.protocolo_verificacion:
            information.costo_de_no_clasificar(estado)
            return Resultado(True, (
                f"Parte municipal publicado sobre {len(nodos)} puntos. Al disputar "
                f"la cifra nacional SIN protocolo común, la guerra de números se "
                f"profundiza y el desmentido cuesta legitimidad."
            ), {"puntos": len(nodos)})

        estado.reservas.aplicar({"legitimidad": 2.0, "respaldo_internacional": 3.0})
        return Resultado(True, (
            f"Parte municipal publicado sobre {len(nodos)} puntos, dentro del "
            f"protocolo común. Mejora la información de la mesa y reduce el "
            f"desplazamiento de fuerza a situaciones inexistentes."
        ), {"puntos": len(nodos)})


# ===========================================================================
# 04 · MINISTRO DE DEFENSA — 4
# ===========================================================================

@dataclass
class FijarReglasEmpleoSector(Accion):
    """Reglas de empleo de la fuerza del sector, con registro audiovisual."""
    codigo = "A1"
    rol = "Defensa"
    clase: Clase = "constitutiva"
    descripcion = "Reglas de empleo del sector y registro audiovisual obligatorio"
    en_claro = (
        "Ordena que sus unidades vayan identificadas, con reglas escritas y "
        "grabando. Baja mucho la probabilidad de que una operación termine "
        "mal.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("reglas_escritas", estado.turno)
        estado.banderas.activar("registro_av", estado.turno)
        return Resultado(True, (
            "Reglas de empleo escritas y registro audiovisual obligatorio. Dos "
            "mitigadores activos, y la probabilidad de que una imagen circule "
            "baja del 55 % al 25 %."
        ), {"mitigadores": ["reglas_escritas", "registro_av"]})


@dataclass
class OperarNodo(Accion):
    """
    Aplicar fuerza sobre un punto de cierre.

    Es la acción que más mueve el tablero, y por eso el ejercicio tiende a la
    fuerza si nadie lo frena. Cada operación con víctimas consume la legitimidad
    de la que depende la mesa de Interior, que no la ordenó.
    """
    codigo = "A4"
    rol = "Defensa"
    clase: Clase = "operativa"
    descripcion = "Operación de desbloqueo sobre un punto"
    en_claro = (
        "Manda a la fuerza pública a abrir un punto. Es lo más rápido que "
        "existe y lo más caro: el punto suele volver a cerrarse esa misma "
        "noche.")

    nodo_id: str = ""
    tipo_unidad: str = "esmad"
    dupla_presente: bool = False
    concertado_con_alcaldia: bool = False
    responsable_nominado: str | None = None
    de_noche: bool = False

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el punto {self.nodo_id}.")
        if nodo.abierto:
            return Validacion(False, f"{nodo.nombre} ya está abierto.")
        # Un tipo de unidad desconocido se rechaza con un motivo legible. Antes
        # reventaba el cálculo de riesgo con un KeyError, y una acción que falla
        # de forma ruidosa a mitad de turno es peor que una que se rechaza.
        if self.tipo_unidad not in P.BASE_INCIDENTE:
            return Validacion(False, (
                f"«{self.tipo_unidad}» no es un tipo de unidad. Los que hay: "
                f"{', '.join(sorted(P.BASE_INCIDENTE))}."
            ))

        faltan, habilita = [], []
        if self.tipo_unidad == "esmad" and not estado.esmad_disponible():
            faltan.append("ESMAD disponible")
            habilita.append("Director de Policía (disponer del ESMAD)")
        if self.tipo_unidad == "militar" and not estado.banderas.asistencia_militar_firmada:
            faltan.append("asistencia militar firmada")
            habilita.append("Presidente (firmar la asistencia militar)")
        if faltan:
            return Validacion(False, "Faltan requisitos.", faltan, habilita)

        if (estado.banderas.concertacion_previa_cali
                and nodo.region_id == estado.region_epicentro
                and not self.concertado_con_alcaldia):
            return Validacion(True, parcial=True, motivo=(
                "La Alcaldía condicionó el empleo de la fuerza en su jurisdicción. "
                "Operar sin concertar es posible y cuesta legitimidad adicional."
            ), habilitada_por=["Alcalde de la ciudad epicentro"])

        if estado.banderas.plazo_suspensivo and not self.concertado_con_alcaldia:
            return Validacion(True, parcial=True, motivo=(
                "Plazo suspensivo vigente: la operación se difiere un turno."
            ), habilitada_por=["Ministro del Interior"])
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        nodo = estado.nodos[self.nodo_id]

        # Acompañar con una dupla GASTA una dupla del bolsillo de tres. Antes era
        # una casilla gratis y la asignación de la Defensoría no era una decisión.
        dupla_real = False
        if self.dupla_presente:
            dupla_real = information.consumir_dupla(estado, f"acompanar:{self.nodo_id}")

        unidades = (estado.esmad_disponible()[:2] if self.tipo_unidad == "esmad"
                    else [u for u in estado.unidades if u.tipo == self.tipo_unidad][:2])

        res = force.ejecutar_operacion(
            estado, nodo, self.tipo_unidad, unidades, rng,
            dupla_presente=dupla_real,
            concertado_con_alcaldia=self.concertado_con_alcaldia,
            responsable_nominado=self.responsable_nominado,
        )

        # QUE SE OPERÓ AQUÍ ES UN HECHO PÚBLICO, con éxito o sin él. Sale en las
        # noticias esa misma tarde. Antes solo se registraba la apertura cuando
        # salía bien, de modo que una operación fallida no dejaba ninguna huella
        # en el tablero y la sala no podía ver dónde había intervenido.
        #
        # Lo que NO se registra aquí es dónde está la fuerza AHORA. Eso es de la
        # Dirección General de la Policía, y si se filtrara al tablero uno de los
        # ocho roles dejaría de hacer falta.
        estado.eventos_turno.append({
            "tipo": "operacion",
            "nodo": nodo.nodo_id,
            "unidad": self.tipo_unidad,
            "dupla": dupla_real,
            "incidente": res.hubo_incidente,
        })

        # ¿Se operó sobre un punto pactado? El acuerdo se rompe.
        acuerdo = estado.acuerdo_vigente_sobre(self.nodo_id)
        if acuerdo is not None:
            acuerdo.motivo_ruptura = (
                f"se operó sobre {nodo.nombre}, que estaba pactado"
            )

        if res.exito:
            aperture.abrir_por_fuerza(nodo, rng, estado.turno)
            estado.eventos_turno.append(
                {"tipo": "apertura", "nodo": nodo.nodo_id, "via": "fuerza"}
            )

        if res.hubo_incidente:
            # PRIMERA vía por la que la mezcla real de un punto tiene consecuencia:
            # un incidente sobre población mayoritariamente civil cuesta el doble.
            escala = res.multiplicador_civil
            if res.victimas > 0:
                estado.reservas.aplicar(P.COSTO_RESERVAS["incidente_con_victima"], escala)
                mobilization.registrar_evento(estado, "incidente_mortal", nodo.region_id)
            if res.imagen_viral:
                estado.reservas.aplicar(P.COSTO_RESERVAS["imagen_viral"], escala)
                mobilization.registrar_evento(estado, "imagen_viral", nodo.region_id)
            if not res.atribuible:
                estado.reservas.aplicar(P.COSTO_RESERVAS["sin_registro_escrito"])

        if self.tipo_unidad == "militar":
            mobilization.registrar_evento(estado, "militares_en_multitudes", nodo.region_id)

        if (estado.banderas.concertacion_previa_cali
                and nodo.region_id == estado.region_epicentro
                and not self.concertado_con_alcaldia):
            estado.reservas.aplicar({"legitimidad": -8.0, "cohesion_mesa": -4.0})

        if not estado.banderas.plazo_suspensivo:
            estado.reservas.aplicar(P.COSTO_RESERVAS["operacion_no_informada"])

        if estado.comite_disponible and estado.franja == "dia":
            estado.reservas.aplicar(P.COSTO_RESERVAS["operacion_dia_de_mesa"])

        if self.responsable_nominado and estado.banderas.registro_escrito:
            estado.reservas.aplicar(P.COSTO_RESERVAS["decision_con_responsable"])

        return Resultado(res.exito, res.mensaje, {
            "p_incidente": round(res.p_usada, 3),
            "tirada": round(res.tirada, 3),
            "victimas": res.victimas,
            "viral": res.imagen_viral,
            "atribuible": res.atribuible,
            "dupla_presente": dupla_real,
        })


@dataclass
class RedesplegarMilitares(Accion):
    """
    Traer capacidad militar a proteger infraestructura, o proyectarla por aire.

    Libera policías de la custodia y **abre un frente rural desatendido**, que el
    motor contabiliza y que produce sus propios eventos.
    """
    codigo = "A2"
    rol = "Defensa"
    clase: Clase = "operativa"
    descripcion = "Redespliegue militar a infraestructura o proyección aérea"
    en_claro = (
        "Mueve tropa a proteger instalaciones críticas. Libera policía para "
        "otras tareas e inmoviliza esas unidades donde las puso.")
    modo: str = "infraestructura"   # infraestructura | proyeccion_aerea
    n_unidades: int = 4

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        militares = [u for u in estado.unidades
                     if u.tipo == "militar" and u.asignacion == "reserva"]
        usados = militares[:self.n_unidades]

        if self.modo == "infraestructura":
            for u in usados:
                u.asignacion = "custodia"
                u.ubicacion = "infraestructura"
            liberados = [u for u in estado.unidades
                         if u.tipo == "esmad" and u.asignacion == "custodia"][:len(usados)]
            for u in liberados:
                u.asignacion = "reserva"
                u.ubicacion = None
            estado.frentes_rurales_descubiertos += len(usados)
            return Resultado(True, (
                f"{len(usados)} unidad(es) militares a protección estática. Libera "
                f"{len(liberados)} escuadrón(es) de la custodia y deja "
                f"{estado.frentes_rurales_descubiertos} frente(s) rural(es) "
                f"descubierto(s)."
            ), {"liberados": len(liberados),
                "frentes_descubiertos": estado.frentes_rurales_descubiertos})

        # Proyección aérea: concentra capacidad policial en el epicentro en horas
        traidos = force.concentrar_esmad(estado, 6)
        mobilization.registrar_evento(estado, "militares_en_multitudes")
        estado.frentes_rurales_descubiertos += len(usados)
        return Resultado(True, (
            f"Proyección aérea al epicentro: {traidos['concentrados']} escuadrón(es) "
            f"concentrados en horas, a costa de la cobertura de otras ciudades. "
            f"Los mandatarios de esas ciudades reclamarán el mismo trato."
        ), traidos)


@dataclass
class PresentarEvidenciaInteligencia(Accion):
    """
    La evidencia de financiación e infiltración, con su grado de solidez judicial.

    Justifica respuestas diferenciadas — pero si un solo caso no se sostiene ante
    los jueces, se destruye la credibilidad de todos los demás.
    """
    codigo = "A3"
    rol = "Defensa"
    clase: Clase = "informativa"
    descripcion = "Evidencia de financiación de cierres y su solidez judicial"
    en_claro = (
        "Presenta lo que Inteligencia tiene sobre quién financia los cierres. "
        "Vale según lo sólido que sea; si no se sostiene, se vuelve en "
        "contra.")
    nodos: list[str] = field(default_factory=list)
    declara_solidez: bool = True    # ¿dice cuáles de sus casos no aguantan?

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        objetivo = self.nodos or [
            n.nodo_id for n in sorted(
                estado.nodos.values(),
                key=lambda x: -x.composicion_real.estructura_organizada,
            )[:3]
        ]
        for nid in objetivo:
            n = estado.nodos.get(nid)
            if n and n.ultima_verificacion_turno is None:
                information.marcar_verificado(
                    estado, n, "inteligencia_defensa", estado.turno)

        if self.declara_solidez:
            estado.reservas.aplicar({"cohesion_mesa": 3.0, "credibilidad_mesa": 2.0})
            return Resultado(True, (
                f"Evidencia presentada sobre {len(objetivo)} punto(s), diciendo "
                f"cuáles de los casos se sostienen ante un juez y cuáles no. "
                f"Debilita su propia posición hoy y protege la credibilidad del "
                f"sector para el resto del episodio."
            ), {"nodos": objetivo, "solidez_declarada": True})

        estado.reservas.aplicar({"legitimidad": -3.0, "credibilidad_mesa": -5.0})
        estado.encuadre_dominante = "represion"
        return Resultado(True, (
            f"Evidencia presentada sobre {len(objetivo)} punto(s) sin declarar su "
            f"solidez. Justifica el escalamiento — y si un caso se cae en los "
            f"estrados, arrastra a todos los demás."
        ), {"nodos": objetivo, "solidez_declarada": False})


# ===========================================================================
# 05 · DIRECTOR GENERAL DE LA POLICÍA — 4
# ===========================================================================

@dataclass
class ClasificarParteOperacional(Accion):
    """
    Publicar el parte distinguiendo confirmado, estimado y en verificación.

    En el papel parece transparencia sin recompensa. Lo que hace es que cada
    desmentido posterior cueste la mitad — y da al Gobierno una cifra defendible.
    """
    codigo = "A3"
    rol = "Policía"
    clase: Clase = "constitutiva"
    descripcion = "Parte operacional clasificado en confirmado, estimado y en verificación"
    en_claro = (
        "Separa en su parte lo confirmado, lo estimado y lo que está en "
        "verificación. Evita que una estimación se lea en la mesa como un "
        "hecho.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_verificacion", estado.turno)
        return Resultado(True, (
            "Parte operacional clasificado y sostenido públicamente. La mesa pasa "
            "a tener una sola cifra oficial con su grado, y el desmentido deja de "
            "costar legitimidad cada vez."
        ))


@dataclass
class DisponerESMAD(Accion):
    """
    Concentrar el ESMAD en puntos priorizados, replegando la contención estática.

    **El precio tiene nombre de ciudad:** los puntos que se sueltan se consolidan,
    y el mandatario local que los pierde lo lee como abandono territorial.
    """
    codigo = "A1"
    rol = "Policía"
    clase: Clase = "operativa"
    descripcion = "Concentración del ESMAD en puntos priorizados"
    en_claro = (
        "Concentra escuadrones en los puntos que decida. Gana fuerza donde la "
        "lleva y deja descubierto lo que abandona.")
    n_escuadrones: int = 6

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        r = force.concentrar_esmad(estado, self.n_escuadrones)
        if r["concentrados"] == 0:
            return Resultado(False, (
                "No quedan escuadrones en contención estática que traer: la fuerza "
                "ya está toda comprometida."
            ))
        estado.reservas.aplicar({"cohesion_mesa": -3.0})
        return Resultado(True, (
            f"{r['concentrados']} escuadrón(es) concentrados y disponibles. Se "
            f"replegó la contención en {len(r['consolidados'])} punto(s), que se "
            f"consolidan — y el mandatario local lo leerá como abandono."
        ), r)


@dataclass
class Escoltar(Accion):
    """
    Acompañar una caravana de carga, un carrotanque o una misión médica.

    **Es la condición material de todo el frente logístico.** Sin escolta no hay
    caravana ni carrotanque, por más que Transporte priorice y Minas asigne.
    """
    codigo = "A2"
    rol = "Policía"
    clase: Clase = "operativa"
    descripcion = "Escolta de caravana, carrotanque o misión médica"
    en_claro = (
        "Escolta una caravana, un carrotanque o una misión médica. Hace "
        "llegar el suministro sin abrir el punto, y ocupa escuadrones todo el "
        "turno.")
    corredor_id: str = ""
    clase_carga: str = "humanitario"

    def validar(self, estado: Estado) -> Validacion:
        c = estado.corredores.get(self.corredor_id)
        if c is None:
            return Validacion(False, f"No existe el corredor {self.corredor_id}.")
        if len(estado.esmad_en_reserva()) < P.ESCUADRONES_POR_ESCOLTA:
            return Validacion(
                False,
                f"Hacen falta {P.ESCUADRONES_POR_ESCOLTA} escuadrones sin comprometer.",
                requisitos_faltantes=["escuadrones en reserva"],
                habilitada_por=["Director de Policía (concentrar el ESMAD)",
                                "Ministro de Defensa (redesplegar militares)"],
            )
        bloqueo = c.punto_que_bloquea(estado.nodos)
        if bloqueo:
            return Validacion(True, parcial=True, motivo=(
                f"{c.nombre} sigue bloqueado en {estado.nodos[bloqueo].nombre}. "
                f"La escolta puede salir, pero la carga no pasará."
            ), habilitada_por=["Ministro de Defensa (operar el punto)",
                               "Ministro del Interior (concertar el punto)"])
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        from src.engine import mobilization
        r = force.escoltar(estado, self.corredor_id, self.clase_carga, rng)
        if not r["ok"]:
            return Resultado(False, r["motivo"])
        if not r.get("paso") and not r.get("atacada"):
            return Resultado(False, r["mensaje"])

        if r["atacada"]:
            estado.reservas.aplicar(P.COSTO_RESERVAS["escolta_atacada"])
            mobilization.registrar_evento(estado, "escolta_atacada")
            estado.eventos_turno.append({"tipo": "escolta_atacada",
                                         "corredor": self.corredor_id})
            return Resultado(False, (
                "La caravana fue atacada en ruta. El corredor humanitario se "
                "convierte en escenario de confrontación, se destruye la "
                "neutralidad de la misión, y los escuadrones quedan inmovilizados."
            ), {"atacada": True})

        supply.reponer_por_escolta(
            estado, r["regiones"], r["reposicion"], self.clase_carga
        )
        estado.reservas.aplicar(P.COSTO_RESERVAS["escolta_lograda"])
        estado.eventos_turno.append({"tipo": "escolta_lograda",
                                     "corredor": self.corredor_id,
                                     "clase": self.clase_carga})
        return Resultado(True, (
            f"Caravana escoltada por {estado.corredores[self.corredor_id].nombre}. "
            f"Repone {r['reposicion']:.1f} días de autonomía en "
            f"{len(r['regiones'])} región(es), y hace verificable la reapertura."
        ), {"regiones": r["regiones"], "reposicion": round(r["reposicion"], 2)})


@dataclass
class SolicitarRelevo(Accion):
    """Menos fatiga a cambio de menos cobertura simultánea."""
    codigo = "A5"
    rol = "Policía"
    clase: Clase = "operativa"
    descripcion = "Relevo y rotación de unidades agotadas"
    en_claro = (
        "Releva a las unidades más agotadas. Un escuadrón cansado es el "
        "principal factor de que una operación salga mal.")
    n_unidades: int = 6

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        n = force.solicitar_relevo(estado, self.n_unidades)
        return Resultado(True, (
            f"{n} unidad(es) en relevo. Baja la fatiga —el principal factor de "
            f"error— a costa de reducir la cobertura simultánea de puntos."
        ), {"relevadas": n})


# ===========================================================================
# 06 · DELEGADO DE LA DEFENSORÍA DEL PUEBLO — 5
# ===========================================================================

@dataclass
class ExigirEstandaresEmpleo(Accion):
    """
    Reglas escritas, identificación de agentes, registro audiovisual y ruta de
    atención a víctimas.

    Enciende TRES mitigadores de golpe. Es la acción de mayor rendimiento del
    ejercicio y la que menos se parece a una acción.
    """
    codigo = "A1"
    rol = "Defensoría"
    clase: Clase = "constitutiva"
    descripcion = "Estándar de empleo de la fuerza: reglas, identificación, registro"
    en_claro = (
        "Exige que la fuerza actúe con reglas escritas, identificada y "
        "grabando. Es lo que hace que después se pueda saber qué pasó de "
        "verdad.")
    exigencias: int = 3     # >3 simultáneas y la mesa lo aísla

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        if self.exigencias > 3:
            estado.eventos_turno.append({"tipo": "defensoria_aislada"})
            return Resultado(False, (
                "Condicionó sin priorizar: la mesa lo aísla. Pierde acceso y su "
                "palanca desaparece justo cuando se decide el escalamiento."
            ))
        for b in ("reglas_escritas", "identificacion_agentes", "registro_av"):
            estado.banderas.activar(b, estado.turno)
        estado.reservas.aplicar({"respaldo_internacional": 10.0})
        return Resultado(True, (
            "Estándar adoptado. Tres mitigadores activos: la probabilidad de "
            "incidente en toda operación futura cae a poco más de la mitad, sin "
            "consumir un solo escuadrón."
        ), {"mitigadores": ["reglas_escritas", "identificacion_agentes", "registro_av"]})


@dataclass
class AdoptarProtocoloVerificacion(Accion):
    """Protocolo único de verificación de cifras y denuncias."""
    codigo = "A2"
    rol = "Defensoría"
    clase: Clase = "constitutiva"
    descripcion = "Protocolo único de verificación de cifras y denuncias"
    en_claro = (
        "Establece una sola manera de verificar cifras y denuncias, igual "
        "para todos. Evita que cada cartera traiga su propio número.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.banderas.activar("protocolo_verificacion", estado.turno)
        return Resultado(True, (
            "Protocolo único de verificación vigente. Una sola cifra oficial, "
            "clasificada — y el Gobierno acepta que un tercero la fije."
        ))


@dataclass
class AsignarDuplas(Accion):
    """
    Las tres duplas del turno.

    Una **dupla** es una pareja de funcionarios de la Defensoría que va al terreno
    a constatar qué pasa en un punto, un hospital o un sitio de detención. Van de
    a dos porque protege a los verificadores y porque dos testigos producen una
    constancia difícil de desestimar.

    **Hay tres, y salen del mismo bolsillo que el acompañamiento de operaciones.**
    Cada una hace UNA sola cosa por turno: verificar un punto, verificar una
    denuncia, o acompañar una operación. No puede hacer las tres.
    """
    codigo = "A3"
    rol = "Defensoría"
    clase: Clase = "operativa"
    descripcion = "Asignación de las duplas de verificación"
    en_claro = (
        "Manda a sus verificadores a mirar puntos concretos. Solo tiene tres "
        "por turno, y también hacen falta para comprobar denuncias y "
        "acompañar operaciones.")
    nodos: list[str] = field(default_factory=list)
    denuncias: list[str] = field(default_factory=list)

    def validar(self, estado: Estado) -> Validacion:
        if not estado.banderas.defensoria_presente:
            return Validacion(False, "La Defensoría no está en la mesa.")
        if information.duplas_libres(estado) == 0:
            return Validacion(False, (
                "No quedan duplas este turno. Verificar aquí era no verificar allá."
            ))
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        partes, datos = [], {}

        for did in self.denuncias:
            r = information.verificar_denuncia(estado, did)
            partes.append(r.get("mensaje") or r.get("motivo", ""))
            datos.setdefault("denuncias", []).append(
                {"id": did, "ok": r["ok"], "veraz": r.get("veraz")}
            )

        if self.nodos:
            r = information.verificar_puntos(estado, self.nodos, estado.turno)
            if r["ok"]:
                partes.append(f"Verificados {len(r['verificados'])} punto(s).")
                if r.get("aviso"):
                    partes.append(r["aviso"])
                datos["verificados"] = [e.nodo_id for e in r["verificados"]]
                datos["no_alcanzados"] = r["no_alcanzados"]

        if not partes:
            return Resultado(False, "No se asignó ninguna dupla.")
        datos["duplas_restantes"] = information.duplas_libres(estado)
        return Resultado(True, " ".join(partes), datos)


@dataclass
class RequerirCorredoresHumanitarios(Accion):
    """
    Corredores humanitarios permanentes, exigibles **tanto al Estado como a
    quienes sostienen los cierres**.

    Sin oxígeno modelado sería una declaración de principios. Con él, negarlo
    tiene contador de víctimas — y obliga a elegir entre abrirlo por la fuerza,
    que es el peor escenario posible, o aceptar públicamente el incumplimiento.
    """
    codigo = "A4"
    rol = "Defensoría"
    clase: Clase = "operativa"
    descripcion = "Requerimiento de corredores humanitarios permanentes"
    en_claro = (
        "Exige que haya un paso permanente para lo humanitario. Negarlo es lo "
        "que más caro cuesta de cara al exterior.")
    corredor_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        if self.corredor_id and self.corredor_id not in estado.corredores:
            return Validacion(False, f"No existe el corredor {self.corredor_id}.")
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        humanitarios = [c for c in estado.corredores.values()
                        if "humanitario" in c.clases_prioridad]
        objetivo = (estado.corredores[self.corredor_id] if self.corredor_id
                    else min(humanitarios,
                             key=lambda c: c.caudal_efectivo(estado.nodos)))

        # Requerir baja el apoyo al cierre en sus puntos: la misión médica se
        # vuelve línea roja también para quienes sostienen el bloqueo.
        for nid in objetivo.nodos:
            n = estado.nodos.get(nid)
            if n:
                n.apoyo_local = max(0.0, n.apoyo_local - 0.06)

        estado.reservas.aplicar({"respaldo_internacional": 5.0})
        estado.eventos_turno.append({"tipo": "corredor_humanitario_requerido",
                                     "corredor": objetivo.corredor_id})
        return Resultado(True, (
            f"Requerimiento formal de paso humanitario permanente por "
            f"{objetivo.nombre}, exigible al Estado y a quienes sostienen los "
            f"cierres. Si se niega, el incumplimiento queda con fecha."
        ), {"corredor": objetivo.corredor_id})


@dataclass
class ManifestarDudaPermanencia(Accion):
    """
    Decir en voz alta que su permanencia está en cuestión.

    **No se retira** —el Delegado nunca abandona la mesa— pero puede poner en duda
    públicamente si puede seguir avalando con su presencia lo que la mesa decide.

    Es mejor que la amenaza de irse por tres razones: se puede usar varias veces,
    es graduada, y **nunca saca sus mitigadores del juego**. Y es lo que hacen los
    defensores del pueblo reales: no se van, emiten pronunciamientos.

    Su credibilidad ante ambas partes es un activo que se consume: **la primera
    vez pesa, la tercera es ruido.**
    """
    codigo = "A5"
    rol = "Defensoría"
    clase: Clase = "informativa"
    descripcion = "Manifestación pública de duda sobre su permanencia"
    en_claro = (
        "Dice en público que se está planteando si tiene sentido seguir en la "
        "mesa. Es su palanca más fuerte y se gasta: la segunda vez pesa menos "
        "que la primera.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        n = estado.dudas_permanencia
        estado.dudas_permanencia += 1
        escala = P.DECAIMIENTO_DUDA_PERMANENCIA ** n

        estado.reservas.aplicar(P.COSTO_RESERVAS["defensoria_duda_permanencia"], escala)
        estado.eventos_turno.append({"tipo": "duda_permanencia", "n": n + 1})

        if n == 0:
            msg = ("El Delegado manifiesta públicamente que no está seguro de "
                   "poder seguir avalando con su presencia lo que aquí se decide. "
                   "La señal se lee de inmediato dentro y fuera del país.")
        elif n == 1:
            msg = ("Segundo pronunciamiento sobre su permanencia. Sigue pesando, "
                   "pero menos: la mesa empieza a leerlo como una posición y no "
                   "como una advertencia.")
        else:
            msg = ("Otro pronunciamiento más. A esta altura se lee como denuncia "
                   "general: el Gobierno restringe su acceso y la advertencia "
                   "pierde la única medida de su utilidad, que es la oportunidad.")
            estado.reservas.aplicar({"credibilidad_mesa": -3.0})

        return Resultado(True, msg, {"pronunciamiento_n": n + 1,
                                     "escala_aplicada": round(escala, 2)})


# ===========================================================================
# 07 · MINISTRO DE TRANSPORTE — 4
# ===========================================================================

@dataclass
class AdoptarCriterioPriorizacion(Accion):
    """
    El criterio único de asignación: población, días de autonomía y costo diario.

    Convierte la disputa política de asignación en una secuencia defendible — y
    expone a un ministro concreto como el que decidió qué ciudad se aplaza.
    """
    codigo = "A1"
    rol = "Transporte"
    clase: Clase = "constitutiva"
    descripcion = "Criterio único de priorización de corredores"
    en_claro = (
        "Fija en qué orden se atienden los corredores y por qué. Sin "
        "criterio, cada turno se discute lo mismo desde cero.")

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
class OrganizarCaravana(Accion):
    """
    Caravana con conductores voluntarios y ventanas horarias. **Requiere escolta.**

    Sin fuerza propia, depende por completo de que otro despeje y otro acompañe:
    es el rol que más empuja la conversación de vuelta a la mesa.
    """
    codigo = "A3"
    rol = "Transporte"
    clase: Clase = "operativa"
    descripcion = "Caravana escoltada en un corredor priorizado"
    en_claro = (
        "Junta la carga en una caravana por un corredor prioritario. Necesita "
        "escolta para poder pasar.")
    corredor_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        c = estado.corredores.get(self.corredor_id)
        if c is None:
            return Validacion(False, f"No existe el corredor {self.corredor_id}.")
        escoltas = [u for u in estado.unidades if u.asignacion == "escolta"]
        if not escoltas:
            return Validacion(
                False,
                "La caravana requiere escolta.",
                requisitos_faltantes=["escolta policial"],
                habilitada_por=["Director General de la Policía Nacional (escoltar)"],
            )
        bloqueo = c.punto_que_bloquea(estado.nodos)
        if bloqueo:
            return Validacion(
                False,
                f"{c.nombre} está bloqueado en {estado.nodos[bloqueo].nombre}.",
                requisitos_faltantes=[f"abrir {estado.nodos[bloqueo].nombre}"],
                habilitada_por=["Ministro de Defensa (operar)",
                                "Ministro del Interior (concertar)"],
            )
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        c = estado.corredores[self.corredor_id]
        caudal = c.caudal_efectivo(estado.nodos)
        regiones = sorted({estado.nodos[n].region_id for n in c.nodos
                           if n in estado.nodos})
        for clase in c.clases_prioridad:
            supply.reponer_por_escolta(estado, regiones, 0.6 * caudal, clase)
        estado.reservas.aplicar({"legitimidad": 3.0})
        estado.eventos_turno.append({"tipo": "caravana", "corredor": self.corredor_id})
        return Resultado(True, (
            f"Caravana en marcha por {c.nombre}, con {caudal:.0%} de flujo. "
            f"Repone abastecimiento en {len(regiones)} región(es) y produce la "
            f"señal de que el corredor funciona."
        ), {"regiones": regiones, "caudal": round(caudal, 2)})


@dataclass
class NegociarConGremios(Accion):
    """
    Condiciones verificables y compensación para que los camioneros no se sumen.

    Un solo gremio que se sume convierte el bloqueo en cierre logístico nacional.
    """
    codigo = "A2"
    rol = "Transporte"
    clase: Clase = "operativa"
    descripcion = "Negociación con los gremios camioneros"
    en_claro = (
        "Habla con los camioneros antes de que decidan sumarse al paro. Si se "
        "suman, se cierra lo que hoy todavía circula.")
    ofrece_compensacion: bool = True

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        if estado.posicion_gremios == "sumados":
            return Resultado(False, (
                "Los gremios ya se sumaron al paro. La negociación llega tarde: "
                "el bloqueo es ahora cierre logístico nacional."
            ))
        if self.ofrece_compensacion:
            estado.posicion_gremios = "fuera"
            estado.ultimatum_gremios_turno = None
            estado.reservas.aplicar({"legitimidad": 2.0, "credibilidad_mesa": -3.0})
            return Resultado(True, (
                "Acuerdo con los gremios: quedan fuera del paro a cambio de "
                "compensación por días de inmovilización y esquema de escolta. "
                "Crea un precedente fiscal y el Comité del Paro lo leerá como "
                "trato preferente."
            ), {"posicion": "fuera"})
        estado.posicion_gremios = "evaluando"
        return Resultado(True, (
            "Negociación sin compensación: los gremios siguen evaluando. La "
            "presión se aplaza, no se resuelve."
        ), {"posicion": "evaluando"})


@dataclass
class PublicarMapaCierres(Accion):
    """
    El mapa de cierres, y el anuncio de aperturas **solo como hecho verificado**.

    Anunciar un corredor abierto con un hilo de tráfico se desmiente solo: una
    docena de camiones presentada como normalización cuesta más de lo que aporta.
    """
    codigo = "A5"
    rol = "Transporte"
    clase: Clase = "informativa"
    descripcion = "Mapa de cierres y anuncio verificado de aperturas"
    en_claro = (
        "Publica dónde está cerrado y qué se ha abierto. Anunciar una "
        "apertura que no se sostiene cuesta credibilidad.")
    anunciar: str = ""      # corredor_id que se quiere anunciar como abierto

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        # Publicar el mapa hace visible qué punto bloquea cada corredor
        bloqueos = {}
        for c in estado.corredores.values():
            b = c.punto_que_bloquea(estado.nodos)
            if b:
                bloqueos[c.corredor_id] = estado.nodos[b].nombre
                information.marcar_verificado(
                    estado, estado.nodos[b], "mapa_transporte", estado.turno)

        if not self.anunciar:
            return Resultado(True, (
                f"Mapa de cierres publicado. {len(bloqueos)} corredor(es) con su "
                f"punto de bloqueo identificado, que hasta ahora la mesa no tenía."
            ), {"bloqueos": bloqueos})

        c = estado.corredores.get(self.anunciar)
        if c is None:
            return Resultado(False, f"No existe el corredor {self.anunciar}.")
        caudal = c.caudal_efectivo(estado.nodos)
        c.anunciado_abierto = True
        c.anunciado_en_turno = estado.turno_decision

        if caudal < 0.3:
            c.anunciado_verificado = False
            information.costo_de_no_clasificar(estado)
            estado.reservas.aplicar({"legitimidad": -4.0})
            return Resultado(True, (
                f"Se anunció {c.nombre} como abierto con {caudal:.0%} de flujo. "
                f"Una docena de camiones presentada como normalización **se "
                f"desmiente sola**, y el desmentido cuesta."
            ), {"caudal": round(caudal, 2), "verificado": False})

        c.anunciado_verificado = True
        estado.reservas.aplicar({"legitimidad": 3.0, "credibilidad_mesa": 2.0})
        return Resultado(True, (
            f"{c.nombre} anunciado como abierto, con {caudal:.0%} de flujo "
            f"verificado. El dato es utilizable por los demás frentes."
        ), {"caudal": round(caudal, 2), "verificado": True})


# ===========================================================================
# 08 · MINISTRO DE MINAS Y ENERGÍA — 4
# ===========================================================================

@dataclass
class FijarPrioridadCombustible(Accion):
    """
    El orden de prioridad del combustible como criterio permanente.

    **No hay orden correcto.** Hay un orden que se defiende ante siete personas
    que pierden algo — y fijarlo como criterio evita pelearlo cada turno.
    """
    codigo = "A2"
    rol = "Minas"
    clase: Clase = "constitutiva"
    descripcion = "Orden de prioridad del combustible entre usos"
    en_claro = (
        "Decide a qué va primero el combustible que queda: hospitales, "
        "transporte o industria. Es un criterio permanente, no una entrega "
        "puntual.")
    orden: list[str] = field(default_factory=lambda: list(P.ORDEN_PRIORIDAD_COMBUSTIBLE))

    def validar(self, estado: Estado) -> Validacion:
        if set(self.orden) != set(P.ORDEN_PRIORIDAD_COMBUSTIBLE):
            return Validacion(False, (
                f"La asignación debe ordenar exactamente: "
                f"{', '.join(sorted(P.ORDEN_PRIORIDAD_COMBUSTIBLE))}."
            ))
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        r = supply.asignar_combustible(estado, self.orden)
        if not r["ok"]:
            return Resultado(False, r["motivo"])
        estado.banderas.activar("prioridad_combustible_fijada", estado.turno)
        aviso = ""
        if r["escolta_degradada"]:
            aviso = (" La fuerza pública queda por debajo del segundo lugar: la "
                     "escolta se degrada y la crisis logística empieza a volverse "
                     "crisis de contención.")
        return Resultado(True, (
            f"Prioridad de combustible fijada: {' > '.join(self.orden)}."
            + aviso
        ), r)


@dataclass
class DeclararInfraestructuraCritica(Accion):
    """
    Protección permanente, con la inmovilización de fuerza que implica.

    **Es la aritmética que enfrenta a Minas con Defensa**: la protección
    permanente resta exactamente de la capacidad de desbloqueo.
    """
    codigo = "A1"
    rol = "Minas"
    clase: Clase = "operativa"
    descripcion = "Declaratoria de infraestructura crítica"
    en_claro = (
        "Declara una instalación como crítica para que la custodien. Queda "
        "protegida, e inmoviliza fuerza que hace falta en otra parte.")
    instalaciones: list[str] = field(default_factory=list)

    def validar(self, estado: Estado) -> Validacion:
        cupo = len(estado.esmad_disponible())
        necesita = len(self.instalaciones) * P.CUSTODIA_POLICIAS_POR_INSTALACION
        if necesita > cupo:
            return Validacion(True, parcial=True, motivo=(
                f"Inmovilizaría {necesita} unidades y la capacidad libre no "
                f"alcanza. Se protegerá lo que se pueda."
            ), habilitada_por=["Ministro de Defensa (redesplegar militares)"])
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        estado.instalaciones_criticas.extend(self.instalaciones)
        for u in estado.esmad_disponible()[: len(self.instalaciones)]:
            u.asignacion = "custodia"
            u.ubicacion = "infraestructura"
        inmovilizadas = force.capacidad_inmovilizada_por_custodia(estado)

        # Los puntos contiguos a infraestructura crítica dejan de poder producir
        # el hecho irreversible: es exactamente lo que se está comprando.
        protegidos = [n.nodo_id for n in estado.nodos.values()
                      if n.proximidad_infra_critica]
        return Resultado(True, (
            f"{len(self.instalaciones)} instalación(es) bajo protección "
            f"permanente. Inmoviliza {inmovilizadas} unidades que Seguridad "
            f"necesitaba para desbloquear: la mesa tendrá que aplazar corredores, "
            f"y el aplazamiento tiene nombre de ciudad."
        ), {"inmovilizadas": inmovilizadas, "puntos_protegidos": protegidos})


@dataclass
class AcordarPasosSeguros(Accion):
    """
    Pasos seguros y ventanas de despacho concertadas con transportadores.

    Permite despachos sin operación de fuerza — pero **supone reconocer de hecho
    una contraparte en el cierre**, lo que puede contradecir la línea roja fijada
    por el Presidente.
    """
    codigo = "A3"
    rol = "Minas"
    clase: Clase = "operativa"
    descripcion = "Pasos seguros y ventanas de despacho concertadas"
    en_claro = (
        "Acuerda ventanas horarias para que pasen carrotanques por un punto. "
        "Pasa el suministro sin abrir el bloqueo.")
    nodo_id: str = ""

    def validar(self, estado: Estado) -> Validacion:
        nodo = estado.nodos.get(self.nodo_id)
        if nodo is None:
            return Validacion(False, f"No existe el punto {self.nodo_id}.")
        if nodo.control_voceria < 0.25:
            return Validacion(False, (
                f"En {nodo.nombre} no hay con quién acordar un paso seguro: la "
                f"vocería reconocida no controla el punto."
            ))
        return Validacion(True)

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        nodo = estado.nodos[self.nodo_id]
        # Un paso seguro no abre el punto: abre una ventana de despacho
        nodo.caudal = max(nodo.caudal, 0.25 * nodo.control_voceria)
        nodo.modo_apertura = "concertacion" if nodo.abierto else nodo.modo_apertura

        aviso = ""
        if estado.banderas.lineas_rojas_fijadas:
            estado.reservas.aplicar({"cohesion_mesa": -4.0})
            aviso = (" Contradice la línea roja fijada por el Presidente: se leerá "
                     "como negociación paralela por fuera de la mesa.")
        estado.eventos_turno.append({"tipo": "paso_seguro", "nodo": nodo.nodo_id})
        return Resultado(True, (
            f"Ventana de despacho concertada en {nodo.nombre} "
            f"({nodo.caudal:.0%} de flujo) sin operación de fuerza."
            + aviso
        ), {"caudal": round(nodo.caudal, 2)})


@dataclass
class EntregarCalendarioAgotamiento(Accion):
    """
    El reloj de la crisis, con su efecto sobre el reloj.

    Decir «nos quedan como dos días» en la deliberación es gratis. **Entregarlo
    formalmente** convierte el tiempo en variable dura y obliga a decidir — pero
    se filtra, hay compra por pánico y el agotamiento llega antes.
    """
    codigo = "A4"
    rol = "Minas"
    clase: Clase = "informativa"
    descripcion = "Calendario de agotamiento por región"
    en_claro = (
        "Dice cuántos días de oxígeno, combustible y comida le quedan a cada "
        "región. Es el dato que solo usted tiene, y difundirlo también genera "
        "pánico.")

    def ejecutar(self, estado: Estado, rng: random.Random) -> Resultado:
        r = supply.difundir_calendario(estado)
        estado.reservas.aplicar({"cohesion_mesa": 3.0})
        return Resultado(True, (
            "Calendario entregado a la mesa. La deliberación pasa a tener fecha "
            "límite — y acelera aquello que mide: el pánico sube y el consumo con "
            "él. Entregar el reloj cambia el reloj."
        ), r)


# ===========================================================================

CATALOGO = [
    # Presidente
    FijarRegistroEscrito, FijarLineasRojas, FirmarAsistenciaMilitar,
    ConvocarAlcaldes, DesplazarseAlEpicentro,
    # Interior
    ExigirProtocoloVoceria, ConvocarMesaNacional, AbrirMesaLocal,
    OfrecerContraprestacion,
    # Alcalde
    CondicionarEmpleoFuerza, InstalarMesaConVoceros, EsquemaHumanitarioMunicipal,
    PublicarParteMunicipal,
    # Defensa
    FijarReglasEmpleoSector, OperarNodo, RedesplegarMilitares,
    PresentarEvidenciaInteligencia,
    # Policía
    ClasificarParteOperacional, DisponerESMAD, Escoltar, SolicitarRelevo,
    # Defensoría
    ExigirEstandaresEmpleo, AdoptarProtocoloVerificacion, AsignarDuplas,
    RequerirCorredoresHumanitarios, ManifestarDudaPermanencia,
    # Transporte
    AdoptarCriterioPriorizacion, OrganizarCaravana, NegociarConGremios,
    PublicarMapaCierres,
    # Minas
    FijarPrioridadCombustible, DeclararInfraestructuraCritica,
    AcordarPasosSeguros, EntregarCalendarioAgotamiento,
]


def catalogo_por_rol() -> dict[str, list[dict]]:
    """El repertorio de cada rol, generado desde el código y no escrito a mano."""
    out: dict[str, list[dict]] = {}
    for cls in CATALOGO:
        out.setdefault(cls.rol, []).append({
            "codigo": cls.codigo,
            "accion": cls.__name__,
            "clase": cls.clase,
            "descripcion": cls.descripcion,
            "en_claro": cls.en_claro,
        })
    return out
