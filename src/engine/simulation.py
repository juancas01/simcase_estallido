"""
simulation.py — El motor. Único dueño del estado.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

Este módulo no importa nada de `src.agents` ni llama a ningún modelo de lenguaje.
Debe poder correr de principio a fin sin clave de API. Si algún día no puede, la
arquitectura está mal.

EL CICLO
--------
    turno 0        instalación y declaración de línea — el motor no avanza
    turnos 1..5    decisión (día, 13 min) → el motor avanza 12 h
    interludios    noche (3 min, sin deliberación) → el motor avanza 12 h
    proyección     3 turnos más sin órdenes: el país que la sala entrega

NO HAY MODERADOR COMO FIGURA APARTE (v2). El sistema conduce el turno: lleva el
reloj de cada fase, produce el parte de apertura y devuelve el plan interpretado
con su banda de riesgo. Quien opera la consola solo transcribe, y puede ser uno
de los nueve.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.engine import parameters as P
from src.engine import mobilization, force, aperture, supply, information
from src.engine.actions import Accion, Resultado, Validacion
from src.engine.bitacora import Bitacora
from src.engine.state import Estado, Decision, Franja


@dataclass
class ResultadoTurno:
    turno: int
    franja: Franja
    resultados: list[tuple[str, Resultado]] = field(default_factory=list)
    eventos: list[dict] = field(default_factory=list)
    reservas: dict = field(default_factory=dict)
    # Foto de TODAS las magnitudes del tablero al cerrar el paso. Es lo que
    # permite decir qué cambió, y un número solo nunca dice eso.
    indicadores: dict = field(default_factory=dict)
    umbrales_cruzados: list[str] = field(default_factory=list)
    resumen: str = ""
    # Semáforo y autonomías por región al cerrar el paso. Es la serie que la
    # lectura necesita («jornadas-región en rojo», «se les cayó de hambre») y
    # es exactamente lo que no puede dibujarse en vivo sin volverlo marcador:
    # vive en el historial del motor y en el archivo de la corrida (`B1`),
    # nunca en `Estado`.
    regiones: dict = field(default_factory=dict)
    # Los mitigadores persistentes encendidos al cerrar el paso. Es lo que
    # permite decir, en el cierre, con cuánta red se operó cada punto.
    mitigadores: list[str] = field(default_factory=list)


class MotorCrisis:
    """
    El motor de la simulación del estallido social.

    Uso:
        motor = MotorCrisis(estado_inicial, semilla=20210511)
        motor.encolar(OperarNodo(nodo_id="N003", tipo_unidad="esmad"))
        r = motor.paso()
    """

    def __init__(self, estado: Estado, semilla: int = P.SEMILLA_POR_DEFECTO,
                 bitacora: Bitacora | None = None):
        self.estado = estado
        # La semilla queda registrada para repetir la corrida en el debriefing con
        # una decisión cambiada. NO es un elemento visible de la interfaz (A6).
        self.semilla = semilla
        self.rng = random.Random(semilla)

        # El estado la lleva encima para que una LECTURA pueda ser reproducible
        # sin tocar `self.rng`. Mirar no mueve el dado: si lo moviera, el
        # resultado de la corrida dependeria de cuantas veces se refresco una
        # pantalla, y la semilla no serviria para nada.
        estado.semilla = semilla

        # Tres colas, igual que en Macondo. La condicional es aquí más necesaria.
        self.cola_inmediata: list[Accion] = []
        self.eventos_programados: list[dict] = []
        self.acciones_condicionales: list[dict] = []

        # EL ARCHIVO DE LA CORRIDA (`B1`). De solo anexado, para que lo escrito
        # sobreviva a una caída del proceso. Nadie la pidió → `inactiva()`: el
        # motor corre entero sin escribir nada, como siempre pudo.
        self.bitacora = bitacora or Bitacora.inactiva()

        # La memoria de las decisiones con su imputación resuelta (`via`,
        # `atiende`, ver docs/LA_MEDICION.md §4). Va AQUÍ y no en `Estado` ni en
        # `Decision` a propósito: el tablero serializa el registro tal cual, y
        # el vocabulario de la lectura no puede salir antes del cierre (§7).
        self.imputaciones: list[dict] = []

        # El historial sigue siendo la memoria en vivo de los pasos; la bitácora
        # es la copia que sobrevive al proceso.
        self.historial: list[ResultadoTurno] = []
        self.lineas_declaradas: dict[str, str] = {}

        # La foto de partida. Sin ella el primer turno no tendría contra qué
        # compararse, y el primer turno es justo donde la sala aún no sabe qué
        # es normal en este tablero.
        self._indicadores_t0 = self._indicadores()
        self.bitacora.fijar_apertura(semilla, self._indicadores_t0)

    # ------------------------------------------------------------------
    # Turno 0 — instalación
    # ------------------------------------------------------------------

    def declarar_linea(self, rol: str, linea: str, condicion: str = "") -> None:
        """
        La declaración de línea del turno 0: 60 segundos por rol, sin debate.

        La métrica más reveladora del ejercicio es la distancia entre la línea que
        la sala DECLARÓ y la que de hecho EJECUTÓ. Casi todas declaran una
        secuencia —«primero la mesa, fuerza solo si falla»— y casi ninguna la
        cumple. Sin el turno 0 esa comparación no existe.
        """
        self.lineas_declaradas[rol] = f"{linea}" + (f" · se movería si: {condicion}"
                                                    if condicion else "")
        self.bitacora.linea(rol, self.lineas_declaradas[rol])

    # ------------------------------------------------------------------
    # Encolar
    # ------------------------------------------------------------------

    def encolar(self, accion: Accion) -> Validacion:
        """
        LA PRIMERA DE LAS DOS VALIDACIONES, contra el estado de la ventana
        ANTERIOR. La segunda ocurre al ejecutar, dentro de `paso()`, contra el
        estado a mitad de plan — con todo lo que las acciones anteriores del
        mismo plan ya hicieron.

        Esa distancia es un contrato y no un accidente:

          · Lo que OTRO DÍA pudo habilitar (una bandera, un acuerdo) tiene que
            haber ocurrido ya: aquí es requisito duro y la acción no entra.
          · Lo que ESTE MISMO PLAN puede habilitar (la escolta que `Escoltar`
            pone una línea antes, el ESMAD que se concentra, el punto que se
            abre) no se exige aquí: se AVISA (`parcial`) y se comprueba al
            ejecutar. Exigirlo aquí hacía inalcanzables a las que dependían de
            algo que solo existe dentro de un plan — la escolta se libera al
            cerrar cada paso, así que en el momento de encolar nunca hay una.

        El orden del dictado es el orden de ejecución: la cola es FIFO y no se
        reordena jamás. Quien habilita va antes en la frase, igual que en la
        mesa.

        Y UNA ORDEN NO SE DICTA DOS VECES EN LA MISMA JORNADA. No había nada que
        lo impidiera: la cola era una lista y esto solo miraba el tope de doce,
        de modo que seis sesiones de la mesa nacional en un día eran seis
        sesiones — con sus seis acuerdos y sus seis descuentos de intensidad. Una
        acción repetida ganaba el ejercicio. Lo que distingue una orden de otra
        es `Accion.llave()`: el acto, y su objetivo cuando el acto tiene uno.
        """
        v = accion.validar(self.estado)
        if not v.ok:
            return v

        llave = accion.llave()
        ya = next((a for a in self.cola_inmediata if a.llave() == llave), None)
        if ya is not None:
            return Validacion(False, (
                "Esa orden ya está dictada en esta jornada y sigue en cola. "
                "Repetirla no la hace valer más: para hacer otra cosa, dígala "
                "sobre otro objetivo."
            ))

        if len(self.cola_inmediata) >= P.TOPE_ACCIONES_POR_PLAN:
            return Validacion(False, f"Tope de {P.TOPE_ACCIONES_POR_PLAN} acciones por plan.")
        self.cola_inmediata.append(accion)
        return v

    def encolar_condicional(self, accion: Accion, condicion, descripcion: str) -> None:
        """«En cuanto la Defensoría verifique ese punto, opérenlo.»"""
        self.acciones_condicionales.append({
            "accion": accion,
            "condicion": condicion,
            "descripcion": descripcion,
            "turno_encolada": self.estado.turno,
        })

    # ------------------------------------------------------------------
    # LA JORNADA — las dos mitades que la sala vive
    # ------------------------------------------------------------------
    #
    # El reloj de sala parte la jornada en dos tramos con reglas opuestas:
    # trece minutos de día en los que se ordena, y dos de noche en los que se
    # mira lo que salió. Estos dos métodos son las bisagras, y existen porque
    # abrir el día y resolverlo NO son el mismo acto:
    #
    #     abrir_jornada()    no avanza el mundo. Pone la mesa: es de día, hay
    #                        tres equipos otra vez, y la fecha de la pared sube.
    #     cerrar_jornada()   avanza el mundo. Resuelve el día con lo que haya en
    #                        cola y a continuación pasa la noche.
    #
    # La noche va DENTRO de cerrar_jornada y no en un botón aparte, porque los
    # dos minutos de consecuencias tienen que enseñar las dos cosas a la vez: lo
    # que produjo la orden y lo que produjo la noche. Separarlas obligaba a la
    # sala a leer media consecuencia, empezar a deliberar, y recibir la otra
    # mitad a mitad de la conversación siguiente.
    # ------------------------------------------------------------------

    def abrir_jornada(self) -> int:
        """
        Empieza el día de la jornada siguiente. **No avanza el mundo.**

        Reponer aquí los equipos y no dentro del paso no es cosmético: el
        Ministro de Defensa tiene que ver sus tres equipos MIENTRAS decide a
        dónde mandarlos. Si se repusieran al resolver, su propia pantalla le
        diría durante los trece minutos que no le queda ninguno.
        """
        self.estado.jornada_abierta = max(
            self.estado.turno_decision, self.estado.jornada_abierta) + 1
        self.estado.franja = "dia"
        information.reponer_equipos(self.estado)
        return self.estado.jornada_abierta

    def cerrar_jornada(self) -> list[ResultadoTurno]:
        """
        Resuelve el día con lo que la mesa dejó en cola, y pasa la noche.

        Devuelve los pasos dados, en orden. Después de la última jornada no hay
        noche que sufrir: el país que la sala entrega lo dice la proyección.
        """
        pasos = [self.paso(franja="dia")]
        if self.estado.turno_decision < P.TURNOS_DECISION:
            pasos.append(self.paso(franja="noche"))
        else:
            # No hay noche que sufrir, pero la sala SÍ tiene sus dos minutos de
            # consecuencias — y durante ellos el tablero no puede decir «día».
            # La franja es lo que la sala está viviendo; el motor ya no avanza.
            self.estado.franja = "noche"
        return pasos

    # ------------------------------------------------------------------
    # El paso
    # ------------------------------------------------------------------

    def paso(self, franja: Franja | None = None) -> ResultadoTurno:
        e = self.estado
        e.eventos_turno = []

        if franja is not None:
            e.franja = franja
        e.turno += 1
        es_dia = e.franja == "dia"
        if es_dia:
            e.turno_decision += 1
            # La jornada abierta nunca puede quedarse por detrás de la resuelta:
            # quien corre el motor sin reloj de sala —las pruebas, el corredor
            # sin interfaz— no llama a `abrir_jornada()` nunca.
            e.jornada_abierta = max(e.jornada_abierta, e.turno_decision)
            # Los tres equipos se reponen al empezar cada turno de decisión. Con
            # reloj de sala ya las repuso `abrir_jornada()`, y volver a hacerlo
            # aquí no quita nada: entre una cosa y la otra no se gasta ninguna,
            # porque las acciones se ejecutan más abajo.
            information.reponer_equipos(e)

        res = ResultadoTurno(turno=e.turno_decision, franja=e.franja)

        # 0 · Eventos del calendario (la jornada nacional del turno 3)
        if es_dia:
            self._eventos_de_calendario()

        # 1 · Condicionales cuya condición ya se cumple
        self._resolver_condicionales()

        # 2 · Acciones del turno. PROHIBIDO `break` al primer problema: una orden
        #     compuesta no puede morir entera porque a una parte le falte un dato.
        hubo_ordenes = bool(self.cola_inmediata)
        for accion in self.cola_inmediata:
            v = accion.validar(e)
            if not v.ok:
                res.resultados.append((accion.__class__.__name__, Resultado(
                    False, v.motivo or "No viable.",
                    requisitos_faltantes=v.requisitos_faltantes,
                )))
                continue
            try:
                r = accion.ejecutar(e, self.rng)
            except Exception as exc:   # una acción rota no tumba el turno
                r = Resultado(False, f"Error interno en {accion.__class__.__name__}: {exc}")
            res.resultados.append((accion.__class__.__name__, r))
            self._registrar(accion)
        self.cola_inmediata = []

        # 3 · El costo de no decidir
        if not hubo_ordenes and es_dia:
            self._turno_sin_decision()

        # 4 · Costos por no haberse constituido.
        #     SOLO EN TURNOS DE DECISIÓN. Cobrarlos también de noche y en la
        #     proyección convertía la cohesión en una rampa determinista: doce
        #     peajes en cinco decisiones, y la serie bajaba igual hiciera lo que
        #     hiciera la sala. Una variable que no responde no mide nada.
        if es_dia or not P.COBRAR_BANDERAS_SOLO_DE_DIA:
            self._cobrar_ausencia_de_banderas()

        # 4b · El riesgo de infraestructura, que se acumula sin avisar.
        #      Solo de día: la exposición se cuenta por JORNADAS sin custodia, y
        #      contarla también de noche la duplicaría sin que nada cambie.
        if es_dia:
            self._acumular_riesgo_infraestructura()
            self._cobrar_corredores_negados()

        # 5 · Motores de subsistema, en orden fijo
        #
        # Las mesas se revisan ANTES que nada y solo de día: hay que mirar la
        # jornada tal como la dejaron las órdenes, y una mesa que no sesionó hoy
        # es un hecho de la jornada, no de la noche. De noche no se instala nada
        # y no hay nada que reprochar.
        if es_dia:
            aperture.revisar_mesas(e)
        aperture.step(e, self.rng)
        aperture.revisar_acuerdos(e, self.rng)
        supply.step(e, horas=P.HORAS_POR_TURNO)
        mobilization.presion_por_escasez(e)
        if es_dia:
            information.paso_denuncias(e, self.rng)
        mobilization.step(e, self.rng)
        force.paso_fatiga(e)

        # 6 · Umbrales y encuadre
        res.umbrales_cruzados = e.reservas.umbrales_cruzados()
        self._aplicar_umbrales(res.umbrales_cruzados)
        self._resolver_ultimatum_gremios()
        self._recalcular_encuadre()

        res.eventos = list(e.eventos_turno)
        res.reservas = self._reservas_dict()
        res.indicadores = self._indicadores()
        res.regiones = self._regiones_dict()
        res.mitigadores = [k for k, v in e.banderas.mitigadores_activos().items()
                           if v]
        res.resumen = self._resumen(res)
        self.historial.append(res)
        self.bitacora.ventana(
            n=e.turno_decision, franja=e.franja,
            indicadores=res.indicadores, deltas=self.deltas(),
            eventos=res.eventos, regiones=res.regiones,
            mitigadores=res.mitigadores,
        )
        return res

    # ------------------------------------------------------------------

    # Qué clases de hecho se dibujan sobre un punto del mapa, y qué campos de
    # cada uno viajan a la interfaz. La lista de campos es BLANCA a propósito: un
    # evento del motor puede llevar dentro cualquier cosa —`veraz`, por ejemplo—
    # y basta con que alguien añada un campo nuevo para abrir una filtración sin
    # darse cuenta. Aquí no pasa nada por olvidarse: lo que no esté en la lista
    # no sale.
    HECHOS_DE_PUNTO = frozenset({
        "operacion", "punto_verificado", "apertura", "reapertura",
        "desgaste", "paso_seguro", "acuerdo_incumplido", "mesa_congelada",
    })
    CAMPOS_DE_HECHO = frozenset({"tipo", "via", "unidad", "incidente",
                                 "por", "jornadas"})

    def hechos_por_punto(self) -> dict[str, list[dict]]:
        """
        Qué le pasó a cada punto en la última ventana resuelta.

        Es el mismo principio que los deltas, aplicado al mapa: **el cambio, no
        el nivel.** Un punto rojo dice que está cerrado; un punto rojo con anillo
        dice que se cerró anoche, que es otra conversación.

        LA LÍNEA QUE NO SE CRUZA: aquí va lo que YA OCURRIÓ y es público —se
        operó en este punto, un equipo lo miró, el acuerdo se rompió— y nunca
        dónde está la fuerza AHORA. Lo primero sale en las noticias esa misma
        tarde; lo segundo es de la Dirección General de la Policía, y en el
        tablero dejaría sin oficio a uno de los siete.
        """
        if not self.historial:
            return {}
        fuera: dict[str, list[dict]] = {}
        for ev in self.historial[-1].eventos:
            nid = ev.get("nodo")
            if not nid or ev.get("tipo") not in self.HECHOS_DE_PUNTO:
                continue
            fuera.setdefault(nid, []).append(
                {k: v for k, v in ev.items() if k in self.CAMPOS_DE_HECHO}
            )
        return fuera

    def _indicadores(self) -> dict:
        """
        Foto de las magnitudes que ve la sala, para poder restarlas después.

        No incluye nada que el tablero no muestre: sin mezcla real de un punto y
        sin veracidad de ninguna denuncia. Un delta también filtra.
        """
        e = self.estado
        d = self._reservas_dict()
        d["presion_calle"] = round(e.intensidad_nacional, 1)
        d["muertes_evitables"] = float(e.muertes_evitables_total())
        d["esmad_sin_comprometer"] = float(len(e.esmad_en_reserva()))
        d["puntos_abiertos"] = float(len(e.nodos_abiertos()))
        for c in e.corredores.values():
            d[f"caudal:{c.corredor_id}"] = round(c.caudal_efectivo(e.nodos), 3)
        return d

    def deltas(self) -> dict:
        """
        Cuánto se movió cada magnitud en el último paso.

        Es la señal más barata del tablero y la que más señala. `Legitimidad 41`
        no le dice nada a quien no memorizó el punto de partida; `41 ▼9` le dice
        que algo de lo que hizo anoche costó nueve puntos. **Apunta al problema
        sin nombrar el remedio**, que es exactamente lo que el tablero debe hacer.
        """
        if not self.historial:
            return {}
        ahora = self.historial[-1].indicadores
        antes = (self.historial[-2].indicadores if len(self.historial) >= 2
                 else self._indicadores_t0)
        return {k: round(v - antes[k], 2) for k, v in ahora.items() if k in antes}

    def _reservas_dict(self) -> dict:
        r = self.estado.reservas
        return {
            "legitimidad": round(r.legitimidad, 1),
            "credibilidad_mesa": round(r.credibilidad_mesa, 1),
            "respaldo_internacional": round(r.respaldo_internacional, 1),
            "cohesion_mesa": round(r.cohesion_mesa, 1),
        }

    def _regiones_dict(self) -> dict:
        """
        Semáforo y autonomías de cada región, para el historial y la bitácora.

        No es un dato nuevo: es el mismo `Region.semaforo` que el tablero
        publica, congelado por paso. La serie completa —qué región pasó cuántas
        jornadas en rojo— solo la necesita la lectura del cierre, y por eso no
        existe como campo de `Estado`.
        """
        return {
            rid: {
                "nombre": r.nombre,
                "semaforo": r.semaforo,
                "dias_autonomia_alimentos": round(r.dias_autonomia_alimentos, 2),
                "dias_autonomia_combustible": round(r.dias_autonomia_combustible, 2),
                "dias_autonomia_oxigeno": round(r.dias_autonomia_oxigeno, 2),
            }
            for rid, r in self.estado.regiones.items()
        }

    def _eventos_de_calendario(self) -> None:
        """
        Lo que ocurre sin que nadie lo decida. Va en el calendario y no se
        genera al vuelo, para que el escenario sea reproducible.
        """
        if self.estado.turno_decision == P.TURNO_JORNADA_NACIONAL:
            mobilization.registrar_evento(self.estado, "jornada_nacional")
            self.estado.eventos_turno.append({"tipo": "jornada_nacional"})

    def _resolver_ultimatum_gremios(self) -> None:
        """
        El ultimátum de 48 horas del paquete detonante.

        Es un disparador INDEPENDIENTE del umbral de legitimidad, y los dos
        caminos hacia `evaluando` deben coexistir: una cosa es que el país deje de
        respaldar al Gobierno y otra que un gremio concreto pida algo concreto.
        """
        e = self.estado
        if e.ultimatum_gremios_turno is None:
            return
        if e.turno_decision < e.ultimatum_gremios_turno:
            return
        vencido = e.turno_decision >= e.ultimatum_gremios_turno + P.TURNOS_PLAZO_ULTIMATUM
        if e.posicion_gremios == "fuera":
            e.posicion_gremios = "evaluando"
            e.eventos_turno.append({"tipo": "ultimatum_gremios"})
        elif e.posicion_gremios == "evaluando" and vencido:
            e.posicion_gremios = "sumados"
            e.ultimatum_gremios_turno = None
            e.eventos_turno.append({"tipo": "gremios_se_suman"})
            # El bloqueo pasa a ser cierre logístico nacional
            for r in e.regiones.values():
                r.dias_autonomia_alimentos -= 0.4
                r.dias_autonomia_combustible -= 0.4

    def _resolver_condicionales(self) -> None:
        pendientes = []
        for item in self.acciones_condicionales:
            edad = self.estado.turno - item["turno_encolada"]
            if edad > P.CADUCIDAD_ORDEN_CONDICIONAL:
                # Una orden en espera indefinida es una orden olvidada.
                self.estado.eventos_turno.append({
                    "tipo": "condicional_caducada", "descripcion": item["descripcion"],
                })
                continue
            try:
                cumple = bool(item["condicion"](self.estado))
            except Exception:
                # Una condición que lanza excepción descarta esa orden, no tumba
                # el paso.
                self.estado.eventos_turno.append({
                    "tipo": "condicional_descartada", "descripcion": item["descripcion"],
                })
                continue
            if cumple:
                self.cola_inmediata.append(item["accion"])
            else:
                pendientes.append(item)
        self.acciones_condicionales = pendientes

    def _turno_sin_decision(self) -> None:
        """
        Un turno sin órdenes es una opción legítima con consecuencias propias.

        El castigo real no es la penalización: **es el reloj**, que corre igual.
        """
        e = self.estado
        e.reservas.aplicar(P.COSTO_RESERVAS["turno_sin_decision"])
        mobilization.registrar_evento(e, "turno_sin_acuerdo")
        for nodo in e.nodos.values():
            nodo.dureza = min(1.0, nodo.dureza + 0.03)
        e.encuadre_dominante = "abandono"
        e.eventos_turno.append({"tipo": "turno_sin_decision"})

    def _cobrar_ausencia_de_banderas(self) -> None:
        """
        Lo que cuesta operar sin haberse constituido. Ninguna bandera es
        obligatoria; todas están tarifadas.
        """
        e, b = self.estado, self.estado.banderas
        if not b.protocolo_voceria:
            e.reservas.aplicar(P.COSTO_RESERVAS["sin_protocolo_voceria"])
        if not b.criterio_priorizacion:
            e.reservas.aplicar(P.COSTO_RESERVAS["sin_criterio_priorizacion"])

    def _acumular_riesgo_infraestructura(self) -> None:
        """
        Una jornada más sin custodia, por cada instalación que la sala no protegió.

        **No produce ningún evento y no toca ninguna reserva.** Si lo hiciera, la
        sala vería moverse el número y jugaría contra él — y lo que este contador
        mide no es un daño que ocurrió, sino un riesgo que se asumió. Se cobra
        entero en el debriefing, que es donde se responde de esa clase de cosa.
        """
        for i in self.estado.infraestructura.values():
            if not i.protegida:
                i.jornadas_sin_proteger += 1

    def _cobrar_corredores_negados(self) -> None:
        """
        El paso humanitario que se exigió y sigue cerrado. **Con fecha.**

        `COSTO_RESERVAS["corredor_humanitario_negado"]` era la huérfana más cara
        del archivo: −12 de respaldo internacional y −5 de legitimidad
        declarados, calibrados, documentados **y jamás aplicados**. Sin esto,
        `RequerirCorredoresHumanitarios` era +5 de respaldo a cambio de nada, y
        la ficha del rol prometía lo contrario —«si se niega, el incumplimiento
        queda con fecha»—.

        La regla es la de la acción, sin machinery nueva: el requerimiento vence
        al cerrar la jornada siguiente. Si el corredor está abierto para
        entonces, se cumplió y no cuesta; si no, se cobra UNA vez y el plazo se
        apaga. Nadie tiene que acordarse de nada: el plazo vive en el corredor.
        """
        e = self.estado
        for c in e.corredores.values():
            if c.requerido_en_turno is None:
                continue
            if e.turno_decision <= c.requerido_en_turno:
                continue
            c.requerido_en_turno = None
            if c.caudal_efectivo(e.nodos) > P.CAUDAL_MINIMO_PARA_ANUNCIAR:
                e.eventos_turno.append({
                    "tipo": "corredor_humanitario_cumplido",
                    "corredor": c.corredor_id,
                })
                continue
            e.reservas.aplicar(P.COSTO_RESERVAS["corredor_humanitario_negado"])
            e.eventos_turno.append({
                "tipo": "corredor_humanitario_negado",
                "corredor": c.corredor_id,
            })

    def riesgo_infraestructura(self) -> dict:
        """
        Lo que la sala dejó sin proteger, y durante cuánto. **Para el cierre.**

        La exposición pondera las jornadas sin custodia por lo que depende de
        cada instalación: dejar una refinería vital cinco jornadas no es lo mismo
        que dejar un centro de acopio. Sale con el detalle, porque el número solo
        no abre ninguna conversación — lo que la abre es la lista de nombres.
        """
        e = self.estado
        filas = []
        for i in sorted(e.infraestructura.values(),
                        key=lambda x: (-P.PESO_CRITICIDAD.get(x.criticidad, 1.0),
                                       -x.jornadas_sin_proteger)):
            peso = P.PESO_CRITICIDAD.get(i.criticidad, 1.0)
            filas.append({
                "instalacion": i.nombre,
                "region": e.regiones[i.region_id].nombre
                if i.region_id in e.regiones else i.region_id,
                "criticidad": i.criticidad,
                "protegida": i.protegida,
                "jornadas_sin_proteger": i.jornadas_sin_proteger,
                "de_que_depende": i.de_que_depende,
                "exposicion": round(peso * i.jornadas_sin_proteger, 1),
            })
        total = round(sum(f["exposicion"] for f in filas), 1)
        vitales = [f for f in filas
                   if f["criticidad"] == "vital" and not f["protegida"]]
        return {
            "exposicion_total": total,
            "grave": total >= P.EXPOSICION_INFRA_GRAVE,
            "protegidas": sum(1 for f in filas if f["protegida"]),
            "total": len(filas),
            "vitales_sin_proteger": [f["instalacion"] for f in vitales],
            "detalle": filas,
        }

    def _aplicar_umbrales(self, cruzados: list[str]) -> None:
        """
        Los umbrales duros, y **la única puerta de esta clase que se abre en los
        dos sentidos**.

        Las dos ramas del Comité estaban colapsadas en una: suspender por bajar
        de 30 y retirarse por bajar de 15 hacían exactamente lo mismo, y lo
        hacían para siempre. El umbral de 15 era código muerto y la sala que
        reparaba su credibilidad no recibía nada a cambio.
        """
        e = self.estado
        for u in cruzados:
            if u == "gremios_se_suman":
                e.posicion_gremios = "sumados"
            elif u == "gremios_evaluan" and e.posicion_gremios == "fuera":
                e.posicion_gremios = "evaluando"
            elif u == "comite_se_retira_definitivo":
                if e.comite_disponible or not e.comite_retirado_definitivo:
                    e.eventos_turno.append({"tipo": "comite_se_retira_definitivo"})
                e.comite_disponible = False
                e.comite_retirado_definitivo = True
            elif u == "comite_suspende":
                if e.comite_disponible:
                    e.eventos_turno.append({"tipo": "comite_suspende"})
                e.comite_disponible = False

        self._revisar_vuelta_del_comite()

    def _revisar_vuelta_del_comite(self) -> None:
        """
        El Comité se vuelve a sentar cuando la credibilidad remonta el umbral.

        No lo puede decir `umbrales_cruzados()`, que informa de lo que está
        cruzado AHORA y calla en cuanto se deja de estar por debajo. Por eso la
        vuelta necesita su propia comprobación y por eso no existía.

        **Salvo que se haya ido en definitiva.** Por debajo de 15 la retirada no
        se deshace: es la diferencia entre los dos umbrales que el modelo
        declaraba y no aplicaba.
        """
        e = self.estado
        if e.comite_disponible or e.comite_retirado_definitivo:
            return
        if e.reservas.credibilidad_mesa < P.UMBRALES["credibilidad_comite_suspende"]:
            return
        e.comite_disponible = True
        e.eventos_turno.append({
            "tipo": "comite_vuelve",
            "credibilidad": round(e.reservas.credibilidad_mesa, 1),
        })

    def _recalcular_encuadre(self) -> None:
        """El mismo hecho cuesta distinto según el encuadre vigente."""
        e = self.estado
        ev = e.eventos_turno
        victimas = any(x.get("evento") == "incidente_mortal" for x in ev)
        viral = any(x.get("evento") == "imagen_viral" for x in ev)
        aperturas = sum(1 for x in ev if x.get("tipo") == "apertura")
        nuevos = sum(1 for x in ev if x.get("tipo") == "nodo_nuevo")
        acuerdos = sum(1 for x in ev if x.get("tipo") == "acuerdo_cumplido")

        if victimas or viral:
            e.encuadre_dominante = "represion"
        elif acuerdos or (aperturas and e.comite_disponible):
            e.encuadre_dominante = "negociacion"
        elif nuevos:
            e.encuadre_dominante = "desorden"

    def _registrar(self, accion: Accion) -> None:
        """
        El pliego: quién ordenó qué y bajo la responsabilidad de quién.

        YA NO RECIBE EL RESULTADO. Se guardaba como «ok»/«falló» en
        `Decision.resultado` y no lo leía ninguna superficie. El desenlace de
        cada orden vive en `ResultadoTurno.resultados`, que es lo que la consola
        lee de vuelta, y el que hará falta en el debriefing es el archivo de la
        corrida (`B1`), con su ventana y sus deltas.

        Aquí se resuelve además la IMPUTACIÓN de la decisión —su vía y su
        público— que cada acción declara (`Accion.imputacion`). Se guarda en
        `self.imputaciones` y en la bitácora, JAMÁS en `Decision`: el tablero
        serializa el registro tal cual, y estas dos palabras son el vocabulario
        de la lectura del cierre.
        """
        e = self.estado
        rol = getattr(accion, "rol", "?")
        nombre = getattr(accion, "nombre", "") or accion.__class__.__name__
        descripcion = getattr(accion, "descripcion", "")
        responsable = getattr(accion, "responsable_nominado", None)

        e.registro.append(Decision(
            turno=e.turno_decision,
            franja=e.franja,
            rol=rol,
            accion=accion.__class__.__name__,
            descripcion=descripcion,
            responsable_nominado=responsable,
        ))

        via, atiende = accion.imputacion(e)
        # EL OBJETO de la orden —dónde cayó—, para la lectura del cierre. Se
        # deriva de los campos que la acción ya declara; no hace falta lógica
        # nueva por acción.
        objeto = (getattr(accion, "region_id", "")
                  or getattr(accion, "nodo_id", "")
                  or getattr(accion, "corredor_id", ""))
        self.imputaciones.append({
            "ventana": e.turno_decision,
            "franja": e.franja,
            "rol": rol,
            "accion": accion.__class__.__name__,
            "nombre": nombre,
            "descripcion": descripcion,
            "responsable": responsable,
            "via": list(via),
            "atiende": list(atiende),
            "objeto": objeto,
        })
        self.bitacora.decision(
            ventana=e.turno_decision, rol=rol,
            accion=accion.__class__.__name__, nombre=nombre,
            descripcion=descripcion, responsable=responsable,
            via=list(via), atiende=list(atiende),
        )

    def _resumen(self, res: ResultadoTurno) -> str:
        e = self.estado
        region, dias = e.dias_autonomia_minimos()
        # Por debajo de cero no quedan «−2,0 días» de nada: no queda nada, y lo
        # que corre a partir de ahí es el contador de muertes evitables.
        dias = max(0.0, dias)
        abiertos = len(e.nodos_abiertos())
        return (
            f"T{e.turno_decision} ({res.franja}) · puntos abiertos {abiertos}/{len(e.nodos)} · "
            f"presión en la calle {e.intensidad_nacional:.0f} · "
            f"legitimidad {e.reservas.legitimidad:.0f} · "
            f"autonomía mínima {dias:.1f} d ({region}) · "
            f"muertes evitables {e.muertes_evitables_total()}"
        )

    # ------------------------------------------------------------------
    # Proyección final — cierra el incentivo del último turno
    # ------------------------------------------------------------------

    def proyectar_sin_mando(self, turnos: int = P.TURNOS_PROYECCION_FINAL) -> dict:
        """
        Corre N turnos sin órdenes y devuelve el estado proyectado.

        Existe porque en el turno 5 la fuerza saldría gratis: lo que se abre por
        la fuerza reabre en uno o dos turnos y ya no quedan turnos. Una sala que
        lo advierta podría desatar al final todo lo que evitó antes.

        **No es un marcador: es el país que la sala entrega.** Y es la pregunta
        con la que conviene abrir el debriefing: ¿esto se sostiene sin ustedes?
        """
        e = self.estado
        antes = {
            "puntos_abiertos": len(e.nodos_abiertos()),
            "presion_calle": round(e.intensidad_nacional, 1),
            "legitimidad": round(e.reservas.legitimidad, 1),
            "muertes_evitables": e.muertes_evitables_total(),
        }
        for i in range(turnos):
            self.paso(franja="noche" if i % 2 else "dia")
        region, dias = e.dias_autonomia_minimos()
        dias = max(0.0, dias)     # por debajo de cero no queda nada, no «−2 días»
        return {
            "antes": antes,
            "despues": {
                "puntos_abiertos": len(e.nodos_abiertos()),
                "presion_calle": round(e.intensidad_nacional, 1),
                "legitimidad": round(e.reservas.legitimidad, 1),
                "muertes_evitables": e.muertes_evitables_total(),
                "autonomia_minima": f"{dias:.1f} d ({region})",
            },
            "reservas_finales": self._reservas_dict(),
        }

    # ------------------------------------------------------------------
    # Métricas del debriefing
    # ------------------------------------------------------------------

    def metricas(self) -> dict:
        e = self.estado
        eventos = [ev for r in self.historial for ev in r.eventos]

        ap_fuerza = sum(1 for x in eventos
                        if x.get("tipo") == "apertura" and x.get("via") == "fuerza")
        ap_conc = sum(1 for x in eventos
                      if x.get("tipo") == "apertura" and x.get("via") == "concertacion")
        ap_desg = sum(1 for x in eventos if x.get("tipo") == "desgaste")
        reap = sum(1 for x in eventos if x.get("tipo") == "reapertura")

        primer_registro = e.banderas.activada_en_turno.get("registro_escrito")
        mitigadores = sum(1 for v in e.banderas.mitigadores_activos().values() if v)

        denuncias_verificadas = sum(1 for d in e.denuncias if d.verificada)
        denuncias_estalladas = sum(1 for d in e.denuncias if d.estallo)

        return {
            "aperturas_netas": (ap_fuerza + ap_conc + ap_desg) - reap,
            "aperturas": {"fuerza": ap_fuerza, "concertacion": ap_conc, "desgaste": ap_desg},
            "reaperturas": reap,
            # NUNCA `inf`, y no es un detalle de estilo: `float("inf")` no es
            # JSON válido, así que una sala que hubiera abierto por la fuerza y
            # ni una vez por concertación —que es justo la corrida sobre la que
            # más hay que hablar— **tumbaba el endpoint de métricas con un 500
            # en mitad del debriefing.** `None` se lee «no hubo ninguna
            # concertación con la que comparar», que es lo que pasa.
            "ratio_fuerza_concertacion": (
                round(ap_fuerza / ap_conc, 2) if ap_conc
                else (None if ap_fuerza else 0)
            ),
            "turno_primer_registro_escrito": primer_registro,
            "mitigadores_al_cierre": f"{mitigadores}/3",
            "muertes_evitables": e.muertes_evitables_total(),
            "decisiones_atribuibles": sum(1 for d in e.registro if d.atribuible),
            "decisiones_totales": len(e.registro),
            "acuerdos_cumplidos": sum(1 for a in e.acuerdos if a.cumplido),
            "acuerdos_rotos": sum(1 for a in e.acuerdos if a.roto),
            "denuncias_verificadas": denuncias_verificadas,
            "denuncias_estalladas": denuncias_estalladas,
            "escoltas_logradas": sum(1 for x in eventos if x.get("tipo") == "escolta_lograda"),
            "escoltas_atacadas": sum(1 for x in eventos if x.get("tipo") == "escolta_atacada"),
            "reservas": self._reservas_dict(),
            # EL RIESGO QUE SE ASUMIÓ, no el daño que ocurrió. No hay acciones
            # en contra de la infraestructura: lo que el cierre cobra es lo que
            # se dejó sin custodiar, y durante cuántas jornadas.
            "infraestructura": self.riesgo_infraestructura(),
            # EL OTRO RIESGO QUE SE ASUMIÓ Y NO SE VIO. Cada autorización
            # sanitaria excepcional movió animales y alimento balanceado por
            # rutas alternas sin control pleno. Dentro del episodio no cuesta
            # nada —igual que la infraestructura sin custodia—, y por eso está
            # aquí: para que en el debriefing haya un número contra el que
            # preguntar de quién fue la decisión y qué se compró con ella.
            "riesgo_sanitario": {
                "excepciones_autorizadas": e.riesgo_sanitario_asumido,
                "regiones_con_alivios": dict(e.instrumentos_sectoriales),
            },
            "posicion_gremios": e.posicion_gremios,
            "comite_disponible": e.comite_disponible,
            "lineas_declaradas": dict(self.lineas_declaradas),
        }
