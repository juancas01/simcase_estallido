"""
information.py — La verdad, las estimaciones y la versión (§4.4).

Tres capas distintas, y el ejercicio vive en la distancia entre ellas:

    CAPA 1 · verdad         solo el motor la conoce; NUNCA sale al ejercicio
    CAPA 2 · estimaciones   una por fuente, con sesgo y cobertura propios
    CAPA 3 · versión        lo que cada actor afirma públicamente

EL ERROR DOBLE
--------------
Actuar sobre una estimación equivocada se castiga en las dos direcciones:

  * Tratar como organizado un nodo mayoritariamente de protesta legítima
    → fuerza sobre población civil → costo máximo de legitimidad y exposición.
  * Tratar como protesta legítima un nodo con estructura organizada
    → se negocia con quien no controla nada → el acuerdo se incumple
      visiblemente → costo de credibilidad y argumento para escalar.

No hay opción segura. Hay una decisión sobre cuánta evidencia se exige.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.engine import parameters as P
from src.engine.state import Estado, Nodo


FUENTES = {
    "parte_operacional": {"dueno": "Director de Policía", "cobertura": "alta", "latencia": 1},
    "inteligencia_defensa": {"dueno": "Ministro de Defensa", "cobertura": "media", "latencia": 2},
    "parte_municipal": {"dueno": "Alcalde de Cali", "cobertura": "solo Cali", "latencia": 0},
    "dupla_defensoria": {"dueno": "Defensoría", "cobertura": "2-3 nodos/turno", "latencia": 1},
}


@dataclass
class Estimacion:
    nodo_id: str
    fuente: str
    estructura_organizada: float
    control_voceria: float
    grado: str          # confirmado | estimado | en_verificacion
    turno: int

    def etiqueta(self) -> str:
        return f"[{self.grado} · {self.fuente} · turno {self.turno}]"


def estimar_nodo(nodo: Nodo, fuente: str, turno: int, rng: random.Random) -> Estimacion:
    """
    Produce la lectura sesgada de una fuente sobre un nodo.

    Nadie ve `composicion_real`. Cada rol ve esto, y los sesgos van en
    direcciones opuestas a propósito: la inteligencia de Defensa sobreestima la
    estructura organizada, el parte municipal la subestima.
    """
    real = nodo.composicion_real.normalizada()
    sesgo = P.SESGO_FUENTE.get(fuente, 0.0)
    ruido = rng.gauss(0.0, 0.05)

    est = min(1.0, max(0.0, real.estructura_organizada + sesgo + ruido))

    sesgo_voc = P.SESGO_CONTROL_VOCERIA.get(_rol_de(fuente), 0.0)
    voc = min(1.0, max(0.0, nodo.control_voceria + sesgo_voc + rng.gauss(0, 0.04)))

    if fuente == "dupla_defensoria":
        grado = "confirmado"
    elif fuente == "parte_municipal":
        grado = "estimado"
    else:
        grado = "estimado"

    return Estimacion(nodo.nodo_id, fuente, est, voc, grado, turno)


def _rol_de(fuente: str) -> str:
    return {
        "inteligencia_defensa": "defensa",
        "parte_municipal": "alcalde_cali",
        "dupla_defensoria": "defensoria",
    }.get(fuente, "interior")


def desplegar_duplas(
    estado: Estado, nodos_ids: list[str], turno: int, rng: random.Random
) -> dict:
    """
    Acción A3 de la Defensoría. Cobertura: 2-3 nodos por turno.

    Verificar aquí es no verificar allá. Es la restricción que convierte a la
    Defensoría en un recurso que hay que ASIGNAR, no consultar.
    """
    if not estado.banderas.defensoria_presente:
        return {"ok": False, "motivo": "la Defensoría no está en la mesa"}

    limite = P.COBERTURA_DUPLAS_POR_TURNO
    seleccionados = nodos_ids[:limite]
    sobrantes = nodos_ids[limite:]

    verificados = []
    for nid in seleccionados:
        nodo = estado.nodos.get(nid)
        if not nodo:
            continue
        nodo.ultima_verificacion_turno = turno
        nodo.verificado_por = "dupla_defensoria"
        est = estimar_nodo(nodo, "dupla_defensoria", turno, rng)
        verificados.append(est)

    return {
        "ok": True,
        "verificados": verificados,
        "no_alcanzados": sobrantes,
        "aviso": (
            f"Se verificaron {len(verificados)} de {len(nodos_ids)} nodos pedidos. "
            f"La cobertura son {limite} por turno."
            if sobrantes else None
        ),
    }


# ---------------------------------------------------------------------------
# Denuncias sin verificar
# ---------------------------------------------------------------------------

@dataclass
class Denuncia:
    denuncia_id: str
    texto: str
    nodo_id: str | None
    veraz: bool                 # capa 1 — el motor lo sabe, nadie más
    verificada: bool = False
    desmentida_publicamente: bool = False
    turno_aparicion: int = 0

    def vista_publica(self) -> dict:
        """Sale sin `veraz`. Si se filtra, el diseño entero pierde sentido."""
        return {
            "denuncia_id": self.denuncia_id,
            "texto": self.texto,
            "nodo_id": self.nodo_id,
            "estado": ("verificada" if self.verificada else "sin verificar"),
            "turno": self.turno_aparicion,
        }


def verificar_denuncia(estado: Estado, denuncias: list[Denuncia], did: str) -> dict:
    """
    Verificar una denuncia consume la dupla que no verificará otra cosa.

    REGLA DE DISEÑO: nunca una sola denuncia sin verificar. Siempre al menos dos,
    con veracidad distinta y sin ninguna señal que las distinga. Así la lección
    no es «desconfíe» sino «usted no puede saberlo sin verificar, y verificar
    cuesta una dupla que no tiene».
    """
    d = next((x for x in denuncias if x.denuncia_id == did), None)
    if d is None:
        return {"ok": False, "motivo": f"no existe la denuncia {did}"}

    d.verificada = True
    if d.veraz:
        estado.reservas.aplicar({"exposicion_internacional": 6.0, "legitimidad": -3.0})
        msg = ("La denuncia se confirma. El hecho es cierto y ahora está "
               "documentado por la Defensoría.")
    else:
        estado.reservas.aplicar({"legitimidad": 3.0, "credibilidad_mesa": 2.0})
        msg = ("La denuncia se desmiente en terreno. La Defensoría gana "
               "credibilidad ante ambas partes.")

    estado.eventos_turno.append(
        {"tipo": "denuncia_verificada", "id": did, "veraz": d.veraz}
    )
    return {"ok": True, "veraz": d.veraz, "mensaje": msg}


def costo_de_no_clasificar(estado: Estado, afirmo_sin_clasificar: bool) -> None:
    """
    La distancia entre lo afirmado y lo verificado se cobra en legitimidad, CON
    DESCUENTO si el actor clasificó su dato como confirmado, estimado o en
    verificación. Es lo que hace racional la acción A3 del Director de Policía,
    que en el papel parece transparencia sin recompensa.
    """
    if afirmo_sin_clasificar and not estado.banderas.protocolo_verificacion:
        estado.reservas.aplicar(P.COSTO_RESERVAS["cifra_desmentida"])
        estado.eventos_turno.append({"tipo": "cifra_desmentida"})
