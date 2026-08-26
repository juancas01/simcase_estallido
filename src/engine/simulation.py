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
de los ocho.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.engine import parameters as P
from src.engine import mobilization, force, aperture, supply, information
from src.engine.actions import Accion, Resultado, Validacion
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


class MotorCrisis:
    """
    El motor de la simulación del estallido social.

    Uso:
        motor = MotorCrisis(estado_inicial, semilla=20210511)
        motor.encolar(OperarNodo(nodo_id="N003", tipo_unidad="esmad"))
        r = motor.paso()
    """

    def __init__(self, estado: Estado, semilla: int = P.SEMILLA_POR_DEFECTO):
        self.estado = estado
        # La semilla queda registrada para repetir la corrida en el debriefing con
        # una decisión cambiada. NO es un elemento visible de la interfaz (A6).
        self.semilla = semilla
        self.rng = random.Random(semilla)

        # Tres colas, igual que en Macondo. La condicional es aquí más necesaria.
        self.cola_inmediata: list[Accion] = []
        self.eventos_programados: list[dict] = []
        self.acciones_condicionales: list[dict] = []

        # PENDIENTE(B5): el historial vive solo en memoria. Sin volcarlo a disco
        # con la semilla, la corrida no se puede repetir con una decisión
        # cambiada — que es la mejor herramienta del debriefing.
        self.historial: list[ResultadoTurno] = []
        self.lineas_declaradas: dict[str, str] = {}

        # La foto de partida. Sin ella el primer turno no tendría contra qué
        # compararse, y el primer turno es justo donde la sala aún no sabe qué
        # es normal en este tablero.
        self._indicadores_t0 = self._indicadores()

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

    # ------------------------------------------------------------------
    # Encolar
    # ------------------------------------------------------------------

    def encolar(self, accion: Accion) -> Validacion:
        v = accion.validar(self.estado)
        if v.ok:
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
            # Las tres duplas se reponen al empezar cada turno de decisión.
            information.reponer_duplas(e)

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
            self._registrar(accion, r)
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

        # 5 · Motores de subsistema, en orden fijo
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
        res.resumen = self._resumen(res)
        self.historial.append(res)
        return res

    # ------------------------------------------------------------------

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

    def _aplicar_umbrales(self, cruzados: list[str]) -> None:
        e = self.estado
        for u in cruzados:
            if u == "gremios_se_suman":
                e.posicion_gremios = "sumados"
            elif u == "gremios_evaluan" and e.posicion_gremios == "fuera":
                e.posicion_gremios = "evaluando"
            elif u in ("comite_suspende", "comite_se_retira_definitivo"):
                e.comite_disponible = False

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

    def _registrar(self, accion: Accion, r: Resultado) -> None:
        self.estado.registro.append(Decision(
            turno=self.estado.turno_decision,
            franja=self.estado.franja,
            rol=getattr(accion, "rol", "?"),
            accion=accion.__class__.__name__,
            descripcion=getattr(accion, "descripcion", ""),
            responsable_nominado=getattr(accion, "responsable_nominado", None),
            resultado="ok" if r.ok else "falló",
        ))

    def _resumen(self, res: ResultadoTurno) -> str:
        e = self.estado
        region, dias = e.dias_autonomia_minimos()
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
            "ratio_fuerza_concertacion": (
                round(ap_fuerza / ap_conc, 2) if ap_conc else (float("inf") if ap_fuerza else 0)
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
            "dudas_permanencia": e.dudas_permanencia,
            "reservas": self._reservas_dict(),
            "posicion_gremios": e.posicion_gremios,
            "comite_disponible": e.comite_disponible,
            "lineas_declaradas": dict(self.lineas_declaradas),
        }
