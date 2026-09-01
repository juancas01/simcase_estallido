"""
information.py — La verdad, las estimaciones y la versión.

Tres capas distintas, y el ejercicio vive en la distancia entre ellas:

    CAPA 1 · verdad         solo el motor la conoce; NUNCA sale al ejercicio
    CAPA 2 · estimaciones   el tablero (grano grueso) + siete vistas (grano fino)
    CAPA 3 · versión        lo que cada actor afirma públicamente

EL ERROR DOBLE
--------------
Actuar sobre una estimación equivocada se castiga en las dos direcciones:

  * Tratar como organizado un punto mayoritariamente de protesta legítima
    → fuerza sobre población civil → costo máximo de legitimidad y respaldo.
  * Tratar como protesta legítima un punto con estructura organizada
    → se pacta con quien no controla nada → el acuerdo se incumple visiblemente.

No hay opción segura. Hay una decisión sobre cuánta evidencia se exige, y
resolverla cuesta un equipo que no se tiene.

LOS EQUIPOS SALEN DE UN SOLO BOLSILLO DE TRES
---------------------------------------------
Verificar un punto y verificar una denuncia compiten por el mismo presupuesto, y
cada equipo hace UNA sola cosa por turno.

**Y EL BOLSILLO ES DEL MINISTERIO DE DEFENSA.** Eran las duplas de la Defensoría
del Pueblo, que miraba sin ser parte; ahora los despliega el mismo ministerio que
ordena las operaciones. La capacidad de mirar no se perdió: se perdió que quien
mira no responda ante quien operó, y eso tiene dos consecuencias escritas en
este archivo —el grado «confirmado» ya no lo concede nadie, y desmentir la
denuncia propia solo cuenta si hay protocolo común adoptado.
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
    "equipo_terreno": {
        "dueno": "Ministro de Defensa", "cobertura": "3 puntos por turno",
        "latencia": 1,
        "sesga": "sobreestima, bastante menos que desde el escritorio",
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
    | **Lo constatado se queda quieto** | pasando el turno en que el equipo fue, una verificación del turno 2 sigue diciendo lo mismo en el turno 5 |

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

    # SIN `.get(..., 0.0)`, Y ES EL ARREGLO. Mientras hubo un valor por defecto,
    # una clave mal escrita —`defensoria` por `defensa`— apagaba el sesgo de dos
    # fuentes enteras sin producir ningún síntoma: el motor devolvía un número
    # plausible y nadie tenía motivo para sospechar. Ahora falta una clave y el
    # motor lo dice.
    rol = _rol_de(fuente)
    if rol not in P.SESGO_CONTROL_VOCERIA:
        raise KeyError(
            f"la fuente «{fuente}» se resuelve al rol «{rol}», que no tiene "
            f"sesgo de vocería declarado en SESGO_CONTROL_VOCERIA."
        )
    sesgo_voc = P.SESGO_CONTROL_VOCERIA[rol]
    voc = min(1.0, max(0.0, nodo.control_voceria + sesgo_voc + rng.gauss(0, 0.04)))

    # NINGUNA FUENTE VUELVE A SER «CONFIRMADA». El grado lo concedía el equipo de
    # la Defensoría del Pueblo, que era el único que miraba sin ser parte. Sin
    # tercero no hay quién lo conceda, y un grado que nadie puede otorgar es una
    # promesa que el ejercicio no puede cumplir. Todo se lee estimado, y lo que
    # separa una lectura de otra es de quién viene y cuánto se le descuenta.
    grado = "estimado"
    return Estimacion(nodo.nodo_id, fuente, est, voc, grado, turno)


def _rol_de(fuente: str) -> str:
    return {
        "inteligencia_defensa": "defensa",
        "parte_municipal": "alcalde_cali",
        "equipo_terreno": "defensa",
        "interlocucion_rural": "agricultura",
    }.get(fuente, "interior")


# ---------------------------------------------------------------------------
# Los equipos de terreno — un solo bolsillo de tres
# ---------------------------------------------------------------------------

def equipos_libres(estado: Estado) -> int:
    return max(0, estado.equipos_disponibles)


def consumir_equipo(estado: Estado, para: str) -> bool:
    """
    Gasta un equipo. Devuelve False si no quedan.

    Mirar aquí es no mirar allá: es la restricción que convierte la verificación
    en un recurso que hay que ASIGNAR, no consultar.
    """
    if estado.equipos_disponibles <= 0:
        return False
    estado.equipos_disponibles -= 1
    estado.equipos_usados_en.append(para)
    return True


def reponer_equipos(estado: Estado) -> None:
    estado.equipos_disponibles = P.EQUIPOS_TERRENO_TOTALES
    estado.equipos_usados_en = []


def marcar_verificado(estado: Estado, nodo, por: str, turno: int) -> None:
    """
    Registra que alguien miró este punto — y lo deja visible en el tablero.

    Las cuatro fuentes de observación (equipo de terreno, parte municipal,
    inteligencia de Defensa, mapa de Transporte) pasaban por aquí poniendo los
    mismos dos campos a mano, y ninguna dejaba rastro. Que un punto **haya sido
    mirado en la última ventana** es un hecho público y es justo lo que la sala
    necesita ver para saber si su decisión de gastar un equipo surtió efecto.

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
    Manda equipos a constatar qué hay en unos puntos. Un equipo por punto.

    Devuelve lo verificado y lo que no alcanzó — y lo segundo importa tanto como
    lo primero: es lo que hay que informar a la mesa como «esto no lo he podido
    mirar».
    """
    verificados, no_alcanzados = [], []
    for nid in nodos_ids:
        nodo = estado.nodos.get(nid)
        if nodo is None:
            continue
        if not consumir_equipo(estado, f"verificar:{nid}"):
            no_alcanzados.append(nid)
            continue
        marcar_verificado(estado, nodo, "equipo_terreno", turno)
        verificados.append(
            estimar_nodo(nodo, "equipo_terreno", turno, estado.semilla))

    aviso = None
    if no_alcanzados:
        aviso = (f"No alcanzaron los equipos para {len(no_alcanzados)} punto(s). "
                 f"Quedan sin verificar y hay que decirlo en la mesa.")
    return {"ok": True, "verificados": verificados,
            "no_alcanzados": no_alcanzados, "aviso": aviso}


# ---------------------------------------------------------------------------
# Denuncias sin verificar
# ---------------------------------------------------------------------------

def verificar_denuncia(estado: Estado, denuncia_id: str) -> dict:
    """
    Gastar un equipo en establecer si un hecho grave ocurrió o no.

    Las dos salidas son valiosas y ninguna es gratis:
      * si era cierta, queda documentada — y el costo llega, pero llega con el
        Estado enterado en vez de sorprendido;
      * si era falsa, se desmiente antes de que consuma fuerza y de que el
        Estado pierda legitimidad al reaccionar a algo que no pasó.

    PERO EL QUE VERIFICA ES AHORA EL QUE PODRÍA ESTAR SEÑALADO. Las denuncias de
    este ejercicio son sobre conducta de la fuerza, y desde que los equipos son
    del Ministerio de Defensa, verificarlas es la parte acusada resolviendo sobre
    sí misma. Eso no se prohíbe —prohibirlo dejaría las denuncias sin salida— y
    tampoco se cobra igual:

        **la palabra del que verifica solo cuenta si hay un protocolo común de
        verificación adoptado.**

    Sin él, documentar la propia falta no ahorra nada y el desmentido no da
    credibilidad: la mesa está oyendo a una parte hablar de su propia conducta.
    Con él —lo adopta el Director de la Policía— hay una regla previa que la
    sala pactó antes de saber qué iba a decir, y por eso vale.

    Es la sustitución funcional del tercero que ya no está sentado.
    """
    d = next((x for x in estado.denuncias if x.denuncia_id == denuncia_id), None)
    if d is None:
        return {"ok": False, "motivo": f"no existe la denuncia {denuncia_id}"}
    if d.verificada:
        return {"ok": False, "motivo": "esa denuncia ya está verificada"}
    if not consumir_equipo(estado, f"denuncia:{denuncia_id}"):
        return {"ok": False, "motivo": "no quedan equipos este turno"}

    d.verificada = True
    con_protocolo = estado.banderas.protocolo_verificacion

    if d.veraz and con_protocolo:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_veraz_confirmada"])
        msg = ("La denuncia se confirma. El hecho es cierto y queda documentado "
               "dentro del protocolo común, no por la prensa.")
    elif d.veraz:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_veraz_sin_protocolo"])
        msg = ("La denuncia se confirma, y la constata el mismo sector del que "
               "se denuncia. Sin protocolo común de verificación, documentarla "
               "no ahorra nada: el hecho es cierto y además parece administrado.")
    elif con_protocolo:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_falsa_desmentida"])
        from src.engine import mobilization
        mobilization.registrar_evento(estado, "denuncia_desmentida")
        msg = ("La denuncia se desmiente en terreno, dentro del protocolo común. "
               "El desmentido se sostiene y no se desplazó fuerza a una "
               "situación inexistente.")
    else:
        estado.reservas.aplicar(P.COSTO_RESERVAS["denuncia_falsa_sin_protocolo"])
        msg = ("La denuncia se desmiente en terreno, pero la desmiente el propio "
               "sector señalado y sin protocolo común: se lee como una parte "
               "absolviéndose. No se desplazó fuerza, y el desmentido no cuenta.")

    estado.eventos_turno.append(
        {"tipo": "denuncia_verificada", "id": denuncia_id,
         "veraz": d.veraz, "con_protocolo": con_protocolo}
    )
    return {"ok": True, "veraz": d.veraz, "mensaje": msg}


def declarar_en_verificacion(estado: Estado, denuncia_id: str) -> dict:
    """
    La cuarta conducta del cuadro del paquete detonante, y la mejor disponible:
    no afirmar lo que no se sabe.

    No cuesta un equipo. Cuando la denuncia estalle, el costo se aplica con
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
    estado.eventos_turno.append({"tipo": "denuncias_nuevas", "n": n})


# ---------------------------------------------------------------------------
# La cifra oficial
# ---------------------------------------------------------------------------

def costo_de_no_clasificar(estado: Estado) -> None:
    """
    La distancia entre lo afirmado y lo verificado se cobra en legitimidad, CON
    DESCUENTO si la Policía clasificó su parte en confirmado, estimado y en
    verificación.

    Es lo que hace racional la acción del Director de Policía de publicar el
    parte clasificado, que en el papel parece transparencia sin recompensa.

    LEE `parte_clasificado` Y NO `protocolo_verificacion`, y es la mitad del
    reparto que separó las dos acciones gemelas de Policía. Que la propia cifra
    de quien publica no se dispute es efecto de clasificarla — un acto
    unilateral de la Policía sobre lo suyo. El protocolo único es otra cosa: un
    acto de mesa que obliga a todos, y lo que habilita es la palabra del que
    verifica una denuncia (`verificar_denuncia`). Antes las dos acciones
    encendían las dos cosas, y por eso una sobraba.
    """
    if estado.banderas.parte_clasificado:
        return
    estado.reservas.aplicar(P.COSTO_RESERVAS["cifra_desmentida"])
    estado.eventos_turno.append({"tipo": "cifra_desmentida"})
