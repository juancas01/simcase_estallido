"""
information.py — La verdad, las estimaciones y la versión.

Tres capas distintas, y el ejercicio vive en la distancia entre ellas:

    CAPA 1 · verdad         solo el motor la conoce; NUNCA sale al ejercicio
    CAPA 2 · estimaciones   el tablero (grano grueso) + nueve vistas (grano fino)
    CAPA 3 · versión        lo que cada actor afirma públicamente

EL ERROR DOBLE
--------------
Actuar sobre una estimación equivocada se castiga en las dos direcciones:

  * Tratar como organizado un punto mayoritariamente de protesta legítima
    → fuerza sobre población civil → costo máximo de legitimidad y respaldo.
  * Tratar como protesta legítima un punto con estructura organizada
    → se pacta con quien no controla nada → el acuerdo se incumple visiblemente.

No hay opción segura. Hay una decisión sobre cuánta evidencia se exige, y
resolverla cuesta una dupla que no se tiene.

LAS DUPLAS SALEN DE UN SOLO BOLSILLO DE TRES
--------------------------------------------
Verificar un punto, verificar una denuncia y acompañar una operación compiten
por el mismo presupuesto, y cada dupla hace UNA sola cosa por turno. Antes
acompañar salía gratis y la asignación de la Defensoría no era una decisión.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.engine import parameters as P
from src.engine.state import Estado, Nodo, Denuncia


FUENTES = {
    "parte_operacional": {
        "dueno": "Director de Policía", "cobertura": "todos los puntos", "latencia": 1,
        "sesga": "subestima las víctimas civiles",
    },
    "inteligencia_defensa": {
        "dueno": "Ministro de Defensa", "cobertura": "media", "latencia": 2,
        "sesga": "sobreestima la estructura organizada",
    },
    "parte_municipal": {
        "dueno": "Alcalde de la ciudad epicentro", "cobertura": "solo su jurisdicción",
        "latencia": 0, "sesga": "subestima la estructura organizada",
    },
    "dupla_defensoria": {
        "dueno": "Defensoría", "cobertura": "3 puntos por turno", "latencia": 1,
        "sesga": "casi no se equivoca",
    },
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


def estimar_nodo(nodo: Nodo, fuente: str, turno: int, semilla: int) -> Estimacion:
    """
    Produce la lectura sesgada de una fuente sobre un punto.

    Nadie ve `composicion_real`. Cada rol ve esto, y los sesgos van en
    direcciones opuestas a propósito: la inteligencia de Defensa sobreestima la
    estructura organizada, el parte municipal la subestima. **Ninguno miente**:
    cada uno mira desde donde está parado.

    ### La lectura es un hecho del turno, no del momento en que se mira

    El ruido no sale de un dado compartido: sale de una semilla derivada de
    **(corrida, turno, fuente, punto)**. Con las mismas cuatro cosas sale
    siempre el mismo número, y con cualquiera distinta sale otro.

    Esto no es una optimización, corrige tres cosas a la vez:

    | | |
    |---|---|
    | **Mirar dos veces da lo mismo** | antes cada F5 volvía a tirar el dado, y el parte de Interior cambiaba solo por refrescar la pantalla |
    | **Mirar no gasta azar de la corrida** | antes la API pasaba aquí el `rng` del motor: el resultado de la simulación dependía de cuántas veces alguien refrescó, que es justo lo que una semilla existe para impedir |
    | **Lo constatado se queda quieto** | pasando el turno en que la dupla fue, una verificación del turno 2 sigue diciendo lo mismo en el turno 5 |

    Por eso `turno` es el turno **de la lectura**, no el turno actual. Quien
    consulta algo verificado antes pasa `nodo.ultima_verificacion_turno`.
    """
    real = nodo.composicion_real.normalizada()
    sesgo = P.SESGO_FUENTE.get(fuente, 0.0)

    # Semilla derivada, no dado compartido. `random.Random` con cadena usa
    # sha512: es estable entre procesos y no depende de PYTHONHASHSEED.
    rng = random.Random(f"{semilla}|{turno}|{fuente}|{nodo.nodo_id}")
    ruido = rng.gauss(0.0, 0.05)

    est = min(1.0, max(0.0, real.estructura_organizada + sesgo + ruido))

    sesgo_voc = P.SESGO_CONTROL_VOCERIA.get(_rol_de(fuente), 0.0)
    voc = min(1.0, max(0.0, nodo.control_voceria + sesgo_voc + rng.gauss(0, 0.04)))

    grado = "confirmado" if fuente == "dupla_defensoria" else "estimado"
    return Estimacion(nodo.nodo_id, fuente, est, voc, grado, turno)


def _rol_de(fuente: str) -> str:
    return {
        "inteligencia_defensa": "defensa",
        "parte_municipal": "alcalde_cali",
        "dupla_defensoria": "defensoria",
        "interlocucion_rural": "agricultura",
    }.get(fuente, "interior")


# ---------------------------------------------------------------------------
# Las duplas — un solo bolsillo de tres
# ---------------------------------------------------------------------------

def duplas_libres(estado: Estado) -> int:
    return max(0, estado.duplas_disponibles)


def consumir_dupla(estado: Estado, para: str) -> bool:
    """
    Gasta una dupla. Devuelve False si no quedan.

    Verificar aquí es no verificar allá: es la restricción que convierte a la
    Defensoría en un recurso que hay que ASIGNAR, no consultar.
    """
    if estado.duplas_disponibles <= 0:
        return False
    estado.duplas_disponibles -= 1
    estado.duplas_usadas_en.append(para)
    return True


def reponer_duplas(estado: Estado) -> None:
    estado.duplas_disponibles = P.DUPLAS_TOTALES
    estado.duplas_usadas_en = []


def marcar_verificado(estado: Estado, nodo, por: str, turno: int) -> None:
    """
    Registra que alguien miró este punto — y lo deja visible en el tablero.

    Las cuatro fuentes de observación (dupla, parte municipal, inteligencia de
    Defensa, mapa de Transporte) pasaban por aquí poniendo los mismos dos campos
    a mano, y ninguna dejaba rastro. Que un punto **haya sido mirado en la última
    ventana** es un hecho público y es justo lo que la sala necesita ver para
    saber si su decisión de gastar una dupla surtió efecto.

    Lo que NO sale de aquí es qué vio: la estimación, con su sesgo, es de quien
    la encargó.
    """
    nodo.ultima_verificacion_turno = turno
    nodo.verificado_por = por
    estado.eventos_turno.append(
        {"tipo": "punto_verificado", "nodo": nodo.nodo_id, "por": por}
    )


def verificar_puntos(
    estado: Estado, nodos_ids: list[str], turno: int
) -> dict:
    """
    Manda duplas a constatar qué hay en unos puntos. Una dupla por punto.

    Devuelve lo verificado y lo que no alcanzó — y lo segundo importa tanto como
    lo primero: es lo que la Defensoría tiene que informar a la mesa como «esto
    no lo he podido mirar».
    """
    if not estado.banderas.defensoria_presente:
        return {"ok": False, "motivo": "la Defensoría no está en la mesa"}

    verificados, no_alcanzados = [], []
    for nid in nodos_ids:
        nodo = estado.nodos.get(nid)
        if nodo is None:
            continue
        if not consumir_dupla(estado, f"verificar:{nid}"):
            no_alcanzados.append(nid)
            continue
        marcar_verificado(estado, nodo, "dupla_defensoria", turno)
        verificados.append(
            estimar_nodo(nodo, "dupla_defensoria", turno, estado.semilla))

    aviso = None
    if no_alcanzados:
        aviso = (f"No alcanzaron las duplas para {len(no_alcanzados)} punto(s). "
                 f"Quedan sin verificar y hay que decirlo en la mesa.")
    return {"ok": True, "verificados": verificados,
            "no_alcanzados": no_alcanzados, "aviso": aviso}


# ---------------------------------------------------------------------------
# Denuncias sin verificar
# ---------------------------------------------------------------------------

def verificar_denuncia(estado: Estado, denuncia_id: str) -> dict:
    """
    Gastar una dupla en establecer si un hecho grave ocurrió o no.

    Las dos salidas son valiosas y ninguna es gratis:
      * si era cierta, queda documentada por la Defensoría — y el costo llega,
        pero llega con el Estado enterado en vez de sorprendido;
      * si era falsa, se desmiente antes de que consuma fuerza y de que el
        Estado pierda legitimidad al reaccionar a algo que no pasó.
    """
    d = next((x for x in estado.denuncias if x.denuncia_id == denuncia_id), None)
    if d is None:
        return {"ok": False, "motivo": f"no existe la denuncia {denuncia_id}"}
    if d.verificada:
        return {"ok": False, "motivo": "esa denuncia ya está verificada"}
    if not consumir_dupla(estado, f"denuncia:{denuncia_id}"):
        return {"ok": False, "motivo": "no quedan duplas este turno"}

    d.verificada = True
    if d.veraz:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_veraz_confirmada"])
        msg = ("La denuncia se confirma. El hecho es cierto y ahora está "
               "documentado por la Defensoría, no por la prensa.")
    else:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_falsa_desmentida"])
        from src.engine import mobilization
        mobilization.registrar_evento(estado, "denuncia_desmentida")
        msg = ("La denuncia se desmiente en terreno. La Defensoría gana "
               "credibilidad ante ambas partes y no se desplazó fuerza a una "
               "situación inexistente.")

    estado.eventos_turno.append(
        {"tipo": "denuncia_verificada", "id": denuncia_id, "veraz": d.veraz}
    )
    return {"ok": True, "veraz": d.veraz, "mensaje": msg}


def declarar_en_verificacion(estado: Estado, denuncia_id: str) -> dict:
    """
    La cuarta conducta del cuadro del paquete detonante, y la mejor disponible:
    no afirmar lo que no se sabe.

    No cuesta una dupla. Cuando la denuncia estalle, el costo se aplica con
    descuento — porque el Estado no la negó ni la afirmó: dijo que la estaba
    mirando.
    """
    d = next((x for x in estado.denuncias if x.denuncia_id == denuncia_id), None)
    if d is None:
        return {"ok": False, "motivo": f"no existe la denuncia {denuncia_id}"}
    d.declarada_en_verificacion = True
    return {"ok": True, "mensaje": (
        f"La denuncia {denuncia_id} queda declarada públicamente en verificación. "
        f"No se afirma ni se niega."
    )}


def paso_denuncias(estado: Estado, rng: random.Random) -> dict:
    """
    Las denuncias sin verificar no esperan indefinidamente: estallan.

    Si una denuncia CIERTA lleva dos turnos sin que nadie la mire, sale en la
    esfera pública sin que el Estado tenga respuesta preparada. Si una FALSA
    hace lo mismo, consume legitimidad cuando el Estado reacciona a algo que no
    ocurrió — salvo que se haya declarado en verificación.
    """
    estallidos = []
    for d in estado.denuncias:
        if d.verificada or d.estallo:
            continue
        edad = estado.turno_decision - d.turno_aparicion
        if edad < P.TURNOS_DENUNCIA_SIN_VERIFICAR_ESTALLA:
            continue

        d.estallo = True
        # Declararla en verificación no la resuelve, pero abarata el golpe: el
        # Estado no afirmó lo que no sabía.
        escala = 0.5 if d.declarada_en_verificacion else 1.0
        if d.veraz:
            estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_veraz_confirmada"], escala)
            from src.engine import mobilization
            mobilization.registrar_evento(estado, "cifra_desmentida", d.nodo_id and
                                          estado.nodos[d.nodo_id].region_id)
        else:
            estado.reservas.aplicar(P.COSTO_RESERVAS["cifra_desmentida"], escala)
        estallidos.append(d.denuncia_id)
        estado.eventos_turno.append({
            "tipo": "denuncia_estallo", "id": d.denuncia_id,
            "veraz": d.veraz, "declarada": d.declarada_en_verificacion,
        })

    # Aparecen paquetes nuevos, y NUNCA de a uno.
    exceso = max(0.0, estado.intensidad_nacional - 50.0)
    if rng.random() < P.P_PAQUETE_DENUNCIAS_BASE + exceso / 400.0:
        _generar_paquete(estado, rng)

    return {"estallidos": estallidos}


def _generar_paquete(estado: Estado, rng: random.Random) -> None:
    """
    Siempre al menos dos, con veracidad distinta y sin ninguna señal que las
    distinga.

    EL TAMAÑO SALE DE `parameters.py` Y NO DE AQUÍ. Estaba escrito a mano en
    tres sitios de esta función mientras `DENUNCIAS_POR_PAQUETE` existía sin que
    nadie la leyera: un parámetro documentado, calibrable y desconectado.
    """
    n = max(2, P.DENUNCIAS_POR_PAQUETE)
    cerrados = [x for x in estado.nodos.values() if not x.abierto]
    if len(cerrados) < n:
        return
    elegidos = rng.sample(cerrados, n)
    base = len(estado.denuncias)
    # La mitad ciertas y la mitad falsas, barajadas: lo que hace indistinguible
    # un paquete no es que sean dos, es que no se sepa cuál es cuál.
    veracidades = [i % 2 == 0 for i in range(n)]
    rng.shuffle(veracidades)
    for i, (nodo, veraz) in enumerate(zip(elegidos, veracidades)):
        estado.denuncias.append(Denuncia(
            denuncia_id=f"D-{base + i + 1:03d}",
            texto=(f"Denuncia grave sin verificar sobre hechos en {nodo.nombre} "
                   f"durante las últimas doce horas."),
            nodo_id=nodo.nodo_id,
            veraz=veraz,
            turno_aparicion=estado.turno_decision,
        ))
    estado.eventos_turno.append({"tipo": "denuncias_nuevas", "n": 2})


# ---------------------------------------------------------------------------
# La cifra oficial
# ---------------------------------------------------------------------------

def costo_de_no_clasificar(estado: Estado) -> None:
    """
    La distancia entre lo afirmado y lo verificado se cobra en legitimidad, CON
    DESCUENTO si el actor clasificó su dato como confirmado, estimado o en
    verificación.

    Es lo que hace racional la acción del Director de Policía de publicar el
    parte clasificado, que en el papel parece transparencia sin recompensa.
    """
    if estado.banderas.protocolo_verificacion:
        return
    estado.reservas.aplicar(P.COSTO_RESERVAS["cifra_desmentida"])
    estado.eventos_turno.append({"tipo": "cifra_desmentida"})
