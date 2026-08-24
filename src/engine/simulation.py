"""
simulation.py — El motor. Único dueño del estado.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

Este módulo no importa nada de `src.agents` ni llama a ningún modelo de lenguaje.
Debe poder correr de principio a fin sin clave de API. Si algún día no puede, la
arquitectura está mal.

EL CICLO (§5)
-------------
    turno 0        instalación y declaración de línea — el motor no avanza
    turnos 1..5    decisión (día, 13 min) → el motor avanza 12 h
    interludios    noche (3 min, sin deliberación) → el motor avanza 12 h
    proyección     3 turnos más sin órdenes: el país que la sala entrega
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.engine import parameters as P
from src.engine import mobilization, force, aperture, supply
from src.engine.actions import Accion, Resultado, Validacion
from src.engine.state import Estado, Decision, Franja


@dataclass
class ResultadoTurno:
    turno: int
    franja: Franja
    resultados: list[tuple[str, Resultado]] = field(default_factory=list)
    eventos: list[dict] = field(default_factory=list)
    reservas: dict = field(default_factory=dict)
    umbrales_cruzados: list[str] = field(default_factory=list)
    resumen: str = ""


class MotorCrisis:
    """
    El motor de la simulación del estallido social.

    Uso:
        motor = MotorCrisis(estado_inicial, semilla=20210511)
        motor.encolar(OperarNodo(nodo_id="N07", tipo_unidad="esmad"))
        r = motor.paso()
    """

    def __init__(self, estado: Estado, semilla: int = P.SEMILLA_POR_DEFECTO):
        self.estado = estado
        self.semilla = semilla
        self.rng = random.Random(semilla)

        # Tres colas, igual que en Macondo. La condicional es aquí más necesaria.
        self.cola_inmediata: list[Accion] = []
        self.eventos_programados: list[dict] = []
        self.acciones_condicionales: list[dict] = []

        self.historial: list[ResultadoTurno] = []

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
        """«En cuanto la Defensoría verifique ese nodo, opérenlo.»"""
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
        if e.franja == "dia":
            e.turno_decision += 1

        res = ResultadoTurno(turno=e.turno_decision, franja=e.franja)

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
        if not hubo_ordenes:
            self._turno_sin_decision()

        # 4 · Costos por no haberse constituido
        self._cobrar_ausencia_de_banderas()

        # 5 · Motores de subsistema
        aperture.step(e, self.rng)
        supply.step(e, horas=P.HORAS_POR_TURNO)
        mobilization.presion_por_escasez(e)
        mobilization.step(e, self.rng)
        force.paso_fatiga(e)

        # 6 · Umbrales y encuadre
        res.umbrales_cruzados = e.reservas.umbrales_cruzados()
        self._aplicar_umbrales(res.umbrales_cruzados)
        self._recalcular_encuadre()

        res.eventos = list(e.eventos_turno)
        res.reservas = {
            "legitimidad": round(e.reservas.legitimidad, 1),
            "credibilidad_mesa": round(e.reservas.credibilidad_mesa, 1),
            "exposicion_internacional": round(e.reservas.exposicion_internacional, 1),
            "cohesion_mesa": round(e.reservas.cohesion_mesa, 1),
        }
        res.resumen = self._resumen(res)
        self.historial.append(res)
        return res

    # ------------------------------------------------------------------

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
                # Una condición que lanza excepción descarta esa orden,
                # no tumba el paso.
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

        if victimas or viral:
            e.encuadre_dominante = "represion"
        elif aperturas and e.comite_disponible:
            e.encuadre_dominante = "negociacion"
        elif nuevos:
            e.encuadre_dominante = "desorden"

    def _registrar(self, accion: Accion, r: Resultado) -> None:
        self.estado.registro.append(Decision(
            turno=self.estado.turno,
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
            f"T{e.turno_decision} ({res.franja}) · nodos abiertos {abiertos}/{len(e.nodos)} · "
            f"intensidad {e.intensidad_nacional:.0f} · "
            f"legitimidad {e.reservas.legitimidad:.0f} · "
            f"autonomía mínima {dias:.1f} d ({region}) · "
            f"muertes evitables {e.muertes_evitables_total()}"
        )

    # ------------------------------------------------------------------
    # Proyección final (§5.11) — cierra el incentivo del último turno
    # ------------------------------------------------------------------

    def proyectar_sin_mando(self, turnos: int = P.TURNOS_PROYECCION_FINAL) -> dict:
        """
        Corre N turnos sin órdenes y devuelve el estado proyectado.

        No es un marcador: es el país que la sala entrega. Y responde la pregunta
        con la que conviene abrir el debriefing: ¿esto se sostiene sin ustedes?
        """
        e = self.estado
        antes = {
            "nodos_abiertos": len(e.nodos_abiertos()),
            "intensidad": round(e.intensidad_nacional, 1),
            "legitimidad": round(e.reservas.legitimidad, 1),
            "muertes_evitables": e.muertes_evitables_total(),
        }
        for i in range(turnos):
            self.paso(franja="noche" if i % 2 else "dia")
        region, dias = e.dias_autonomia_minimos()
        return {
            "antes": antes,
            "despues": {
                "nodos_abiertos": len(e.nodos_abiertos()),
                "intensidad": round(e.intensidad_nacional, 1),
                "legitimidad": round(e.reservas.legitimidad, 1),
                "muertes_evitables": e.muertes_evitables_total(),
                "autonomia_minima": f"{dias:.1f} d ({region})",
            },
            "reservas_finales": {
                "legitimidad": round(e.reservas.legitimidad, 1),
                "credibilidad_mesa": round(e.reservas.credibilidad_mesa, 1),
                "exposicion_internacional": round(e.reservas.exposicion_internacional, 1),
                "cohesion_mesa": round(e.reservas.cohesion_mesa, 1),
            },
        }

    # ------------------------------------------------------------------
    # Métricas del debriefing (§8)
    # ------------------------------------------------------------------

    def metricas(self) -> dict:
        e = self.estado
        eventos = [ev for r in self.historial for ev in r.eventos]

        ap_fuerza = sum(1 for x in eventos if x.get("tipo") == "apertura" and x.get("via") == "fuerza")
        ap_conc = sum(1 for x in eventos if x.get("tipo") == "apertura" and x.get("via") == "concertacion")
        ap_desg = sum(1 for x in eventos if x.get("tipo") == "desgaste")
        reap = sum(1 for x in eventos if x.get("tipo") == "reapertura")

        primer_registro = e.banderas.activada_en_turno.get("registro_escrito")
        mitigadores = sum(1 for v in e.banderas.mitigadores_activos().values() if v)

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
            "reservas": {
                "legitimidad": round(e.reservas.legitimidad, 1),
                "credibilidad_mesa": round(e.reservas.credibilidad_mesa, 1),
                "exposicion_internacional": round(e.reservas.exposicion_internacional, 1),
                "cohesion_mesa": round(e.reservas.cohesion_mesa, 1),
            },
            "posicion_gremios": e.posicion_gremios,
            "comite_disponible": e.comite_disponible,
        }
