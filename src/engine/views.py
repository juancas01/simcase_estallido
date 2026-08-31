"""
views.py — Las siete vistas privadas.

    El tablero general responde QUÉ ESTÁ PASANDO.
    La vista privada responde CUÁNTO, DÓNDE EXACTAMENTE Y DESDE CUÁNDO.

RESOLUCIÓN, NO SECRETO
----------------------
Nadie tiene información que los demás no puedan pedir. Lo que cada uno tiene es
**su cartera en alta resolución**, y el resto del país en grano grueso. El
tablero dice «Las Cumbres · abastecimiento ROJO»; solo Agricultura sabe que son
1,8 días y que mañana serán 0,4.

La vista es **personal, no confidencial**: el sistema solo se la muestra a su
titular, pero nadie está obligado a callársela y el ejercicio quiere que se
comparta. Lo que la hace valiosa no es que esté oculta — es que **hay una sola
persona que la tiene actualizada**.

EL DETALLE NO MIGRA
-------------------
Aunque un rol diga su número en voz alta, el número NO se escribe en el tablero.
La mesa lo oyó y ahí queda. Si el dato se fijara en el tablero, el rol se
consultaría una vez y después sobraría; al quedarse aquí, **cada turno cada rol
vuelve a ser necesario**, porque el número cambió y solo él tiene el nuevo.

DOS BLOQUES Y NADA MÁS
----------------------
    detalle   tres o cuatro datos de su cartera. Cabe en una pantalla sin scroll.
    alerta    una línea: qué señala ese detalle como más urgente AHORA.

**Las nueve alertas de cada turno no caben en la capacidad disponible.** Ese es
el diseño: nueve personas con nueve urgencias legítimas y una escolta.

INVARIANTE
----------
Ninguna vista revela `composicion_real` ni la veracidad de una denuncia. Lo que
sale de aquí son estimaciones con el sesgo de su fuente — y los sesgos van en
direcciones opuestas a propósito, para que dos roles honestos vean números
distintos y tengan que hablar.
"""

from __future__ import annotations

from src.engine import parameters as P
from src.engine import information
from src.engine.state import Estado


# LOS SIETE, EN EL ORDEN DE LOS TRES FRENTES: estrategia, seguridad, logística.
# El orden no es decorativo — la portada y el acceso desde el tablero agrupan
# por frente leyendo esta lista.
#
# Eran nueve y los frentes eran tres bloques de tres. Con la salida de la
# Defensoría del Pueblo y del Ministerio de Minas quedan 3 · 2 · 2, y la rejilla
# de la portada deja de ser cuadrada. Es la consecuencia visible de que el
# ejercicio ya no tiene un tercero que vigile ni una cartera que lleve el reloj.
ROLES = [
    "Presidente", "Interior", "Alcalde",
    "Defensa", "Policía",
    "Transporte", "Agricultura",
]


def _dias(valor: float) -> float:
    """
    Días de autonomía, sin negativos.

    Por debajo de cero el motor deja de contar existencias y empieza a contar
    horas sin oxígeno — el contador de muertes evitables. Enseñar «−2,0 días»
    era enseñar la variable interna en vez del hecho: por debajo de cero no
    quedan dos días de nada, no queda nada. Cero es el número correcto, y lo que
    pasa a partir de ahí lo dice el contador de muertes.
    """
    return round(max(0.0, valor), 1)


# ---------------------------------------------------------------------------
# LO QUE ENSEÑABAN LAS DOS VISTAS QUE YA NO EXISTEN
#
# Cuando salieron la Defensoría del Pueblo y el Ministerio de Minas, sus dos
# pantallas se repartieron entre las que quedan. Vive aquí, en funciones, y no
# copiado dentro de cada vista: un bloque copiado en dos sitios se desincroniza
# en el primer cambio, y ninguna prueba mira lo que la interfaz dibuja
# (`PENDIENTES.md · B9`).
# ---------------------------------------------------------------------------

def _bloque_equipos(estado: Estado) -> dict:
    """
    Los equipos de terreno, que ahora son del Ministerio de Defensa.

    **Mismo bolsillo escaso, otro dueño.** Eran la veeduría de un tercero y son
    inteligencia de una parte: lo que se pierde no es la capacidad de mirar, es
    que quien mira no responda ante el que opera.
    """
    sin_verificar = [n for n in estado.nodos.values()
                     if n.ultima_verificacion_turno is None]
    abiertas = [d for d in estado.denuncias if not d.verificada and not d.estallo]

    constatado = []
    for n in estado.nodos.values():
        if n.verificado_por != "equipo_terreno":
            continue
        # El turno de la LECTURA, no el actual: lo que el equipo constató en el
        # turno 2 tiene que seguir diciendo lo mismo en el turno 5. Con
        # `estado.turno` la lectura se volvía a tirar cada vez que alguien abría
        # la vista, que es lo contrario de «constatado».
        cuando = n.ultima_verificacion_turno
        if cuando is None:
            cuando = estado.turno
        est = information.estimar_nodo(
            n, "equipo_terreno", cuando, estado.semilla)
        constatado.append({
            "punto": n.nombre,
            "estructura_organizada": round(est.estructura_organizada, 2),
            "turno": n.ultima_verificacion_turno,
        })

    return {
        "equipos_disponibles": estado.equipos_disponibles,
        "equipos_usados_este_turno": list(estado.equipos_usados_en),
        "denuncias_en_ventanilla": [d.vista_publica() for d in abiertas],
        "puntos_sin_mirar": len(sin_verificar),
        "lo_que_han_constatado": constatado[-5:],
        "_nota_equipos": ("cada equipo hace UNA cosa por turno: verificar un "
                          "punto o verificar una denuncia"),
    }


def _bloque_infraestructura(estado: Estado) -> tuple[list, list]:
    """
    El registro de infraestructura relevante, que ahora es del Interior.

    Devuelve `(filas, vitales_sin_custodia)`. Declarar a ciegas era la
    consecuencia de no tener la lista: la vista decía cuántas instalaciones se
    habían declarado —un número— y no cuáles existen ni qué queda sin custodiar.
    """
    infra = sorted(
        estado.infraestructura.values(),
        key=lambda i: (i.protegida, {"vital": 0, "alta": 1}.get(i.criticidad, 2)),
    )
    filas = [
        {
            "instalacion": i.nombre,
            "region": estado.regiones[i.region_id].nombre
            if i.region_id in estado.regiones else i.region_id,
            "criticidad": i.criticidad,
            "custodia": "puesta" if i.protegida else "sin proteger",
            "de_que_depende": i.de_que_depende,
        }
        for i in infra
    ]
    vitales_solas = [i for i in infra
                     if not i.protegida and i.criticidad == "vital"]
    return filas, vitales_solas


def _calendario_por_region(estado: Estado) -> list[dict]:
    """
    El reloj, región por región. Era el dato exclusivo del Ministerio de Minas.

    Sigue habiendo un reloj y sigue sin verlo la mesa entera: lo lleva
    Agricultura, que es la cartera cuyo daño ya ocurrió. El tablero general
    sigue diciendo «ROJO» y no los días.
    """
    filas = []
    for r in estado.regiones.values():
        entra_oxi = any(
            c.caudal_efectivo(estado.nodos) > 0.05
            for c in estado.corredores_que_sirven(r.region_id, "humanitario")
        )
        manana = r.dias_autonomia_oxigeno - (0.0 if entra_oxi else 1.0 * (1 + r.panico))
        filas.append({
            "region": r.nombre,
            "region_id": r.region_id,
            "oxigeno_dias": _dias(r.dias_autonomia_oxigeno),
            "oxigeno_manana": _dias(manana),
            "combustible_dias": _dias(r.dias_autonomia_combustible),
            "alimentos_dias": _dias(r.dias_autonomia_alimentos),
            "entra_humanitario": entra_oxi,
            "muertes_evitables": r.muertes_evitables,
        })
    return sorted(filas, key=lambda x: x["oxigeno_dias"])



# Las once decisiones constitutivas que la mesa puede tomar, y qué bandera
# levanta cada una. Es el cuadro de mando del Presidente: quién ha constituido
# qué, y qué sigue sin constituirse. Se lee del estado y no se escribe a mano.
CONSTITUTIVAS = (
    ("registro_escrito", "Registro escrito de decisiones", "Presidente"),
    ("lineas_rojas_fijadas", "Líneas rojas del Ejecutivo", "Presidente"),
    ("protocolo_voceria", "Protocolo de vocería única", "Interior"),
    ("concertacion_previa_cali", "Fuerza concertada con la Alcaldía", "Alcalde"),
    ("reglas_escritas", "Reglas de empleo escritas", "Defensa"),
    ("identificacion_agentes", "Identificación de agentes", "Defensa"),
    ("registro_av", "Registro audiovisual", "Defensa"),
    ("protocolo_verificacion", "Protocolo de verificación", "Policía"),
    ("criterio_priorizacion", "Criterio de priorización", "Transporte"),
    ("prioridad_combustible_fijada", "Prioridad del combustible", "Transporte"),
    ("clase_alimentaria", "Clase de prioridad agroalimentaria", "Agricultura"),
)


# ---------------------------------------------------------------------------
# LA PREGUNTA DEL COMIENZO DEL DÍA
# ---------------------------------------------------------------------------
#
# **Una mesa local hay que instalarla cada jornada para que surta efecto.** El
# progreso hacia una apertura concertada sube una vez por sesión y solo por
# sesión: si un día no se sesiona, no se pierde lo andado, pero tampoco se
# avanza — y el reloj del ejercicio corre igual. Abrir una mesa en la jornada 4
# y no volver a ella es no haberla abierto.
#
# Eso ya era cierto y no lo sabía nadie. Vivía dentro de
# `aperture.avanzar_concertacion` y no salía a ninguna pantalla, de modo que una
# sala podía instalar tres mesas la primera jornada y dar por hecho que seguían
# trabajando solas hasta el final.
#
# Los dos que pueden convocarlas —el Ministro del Interior en todo el país, el
# Alcalde en su jurisdicción— reciben la pregunta al abrir el día, con los
# puntos donde hoy todavía no se ha sesionado. **Es una pregunta, no una
# instrucción**: dice dónde hay mesa y cuál lleva jornadas parada; qué hacer con
# eso es de la sala. La distancia entre las dos cosas es la distancia entre un
# ejercicio y un tutorial.


def _notificacion_mesas(estado: Estado, region_id: str | None = None,
                        solo_nodos: list[str] | None = None) -> dict | None:
    """
    Las mesas de este rol que hoy no han sesionado, y la pregunta.

    Devuelve `None` cuando no hay ninguna instalada o cuando ya se sesionó en
    todas: una notificación que aparece siempre deja de leerse a la segunda
    jornada.

    DOS FILTROS, PORQUE HAY DOS FORMAS DE «SUS MESAS». El Alcalde tiene las de
    su jurisdicción —un territorio— y el Ministro de Agricultura las suyas, que
    son las que instaló él y pueden estar repartidas por tres regiones. Un rol
    no puede recibir la pregunta por una mesa que no puede convocar.
    """
    from src.engine import territory

    instaladas = territory.mesas_instaladas(estado, region_id)
    if solo_nodos is not None:
        instaladas = [m for m in instaladas if m["nodo_id"] in solo_nodos]
    if not instaladas:
        return None
    pendientes = [m for m in instaladas if not m["sesionada_hoy"]]
    if not pendientes:
        return None

    congeladas = [m for m in pendientes if m["jornadas_congelada"] > 0]
    if congeladas:
        peor = max(congeladas, key=lambda m: m["jornadas_congelada"])
        detalle = (f"{peor['punto']} lleva {peor['jornadas_congelada']} "
                   f"jornada{'s' if peor['jornadas_congelada'] != 1 else ''} "
                   f"sin sesionar.")
    else:
        detalle = "Ninguna ha sesionado todavía en esta jornada."

    return {
        "tipo": "mesas_sin_sesionar",
        "pregunta": (
            f"¿Avanza hoy en {'la mesa' if len(pendientes) == 1 else 'las mesas'} "
            f"de {', '.join(m['punto'] for m in pendientes)}?"),
        "porque": (
            "Una mesa local hay que instalarla cada jornada para que surta "
            "efecto. No instalarla hoy no pierde lo andado, pero congela la "
            "negociación — y quedan jornadas contadas. " + detalle),
        "mesas": [
            {"punto": m["punto"], "nodo_id": m["nodo_id"],
             "jornadas_congelada": m["jornadas_congelada"],
             "avance": m["avance"]}
            for m in pendientes
        ],
    }


def vista(estado: Estado, rol: str) -> dict:
    """
    Devuelve la vista privada de un rol: `{rol, detalle, alerta}`.

    **Mirar no cambia nada y no gasta azar.** Una vista es una proyección
    determinista del estado: con el mismo estado sale el mismo texto y los
    mismos números, se pida una vez o cincuenta.

    Antes esta función recibía el dado del motor, y eso tenía dos precios que no
    se veían: refrescar la pantalla movía los números, y refrescar la pantalla
    movía la corrida. El ruido de las lecturas sesgadas ahora se deriva de la
    semilla, en `information.estimar_nodo`.
    """
    fn = _VISTAS.get(rol)
    if fn is None:
        raise KeyError(f"rol desconocido: {rol}. Los siete son {ROLES}")
    detalle, alerta = fn(estado)

    # SOLO DE DÍA. De noche no se instala nada, y una pregunta sobre lo que hay
    # que hacer hoy leída durante los dos minutos de consecuencias es ruido.
    notificacion = None
    if estado.franja == "dia":
        if rol == "Interior":
            notificacion = _notificacion_mesas(estado)
        elif rol == "Alcalde":
            notificacion = _notificacion_mesas(estado, estado.region_epicentro)
        elif rol == "Agricultura":
            # Las suyas y solo las suyas: las mesas técnicas rurales que instaló
            # esta cartera. Las del Interior no las puede convocar ella.
            notificacion = _notificacion_mesas(
                estado, solo_nodos=estado.mesas_tecnicas_agro)

    return {
        "rol": rol,
        "notificacion": notificacion,
        # La que se está jugando, no la que se resolvió: mientras la sala
        # delibera la jornada 2, el motor todavía va por la 1.
        "turno": estado.jornada_visible,
        "franja": estado.franja,
        "detalle": detalle,
        "alerta": alerta,
    }


def todas(estado: Estado) -> dict[str, dict]:
    return {r: vista(estado, r) for r in ROLES}


# ===========================================================================
# 01 · Presidente — la contabilidad de la propia mesa
# ===========================================================================

def _presidente(estado: Estado):
    """
    Es el único que ve el desorden del PMU **antes de que produzca un daño**, y
    el único que tiene delante el cuadro completo de lo que la mesa constituyó.

    LA VISTA MÁS VACÍA DEL EJERCICIO ERA ESTA, y era un defecto de diseño y no
    del rol. Traía el pliego de decisiones —que en la jornada 1 está vacío—, la
    temperatura de la coalición y si hay escolta: tres líneas, dos de ellas
    invariantes durante la primera media hora. Su titular abría su dispositivo,
    veía cuatro palabras y lo cerraba.

    Lo que faltaba es justamente su cartera: **qué ha constituido la mesa y qué
    no.** Nadie más lo tiene reunido, cambia cada jornada, y en la jornada 1 —la
    peor de la vista anterior— es cuando más dice, porque no hay nada adoptado y
    esa es exactamente la primera decisión del ejercicio.
    """
    ultimas = estado.registro[-8:]
    sin_responsable = [d for d in ultimas if not d.atribuible]

    coalicion = _temperatura_coalicion(estado)
    escolta = len(estado.esmad_en_reserva()) >= 2

    puestas = [(n, quien) for b, n, quien in CONSTITUTIVAS
               if getattr(estado.banderas, b, False)]
    faltan = [{"decision": n, "quien_la_adopta": quien}
              for b, n, quien in CONSTITUTIVAS
              if not getattr(estado.banderas, b, False)]

    detalle = {
        "la_mesa_ha_constituido": f"{len(puestas)} de {len(CONSTITUTIVAS)}",
        "sin_adoptar_todavia": faltan,
        "pliego_de_decisiones": [
            {
                "jornada": d.turno, "rol": d.rol, "accion": d.descripcion,
                "responsable": d.responsable_nominado or "— SIN NOMBRE —",
                "marcado": not d.atribuible,
            }
            for d in ultimas
        ],
        "temperatura_coalicion": coalicion,
        "puede_desplazarse": escolta,
    }

    if not puestas:
        alerta = (f"La mesa no ha constituido nada: {len(CONSTITUTIVAS)} decisiones "
                  f"que rigen todo lo demás siguen sin adoptarse, y ninguna cuesta "
                  f"un escuadrón.")
    elif sin_responsable:
        alerta = (f"{len(sin_responsable)} de las últimas {len(ultimas)} decisiones "
                  f"salieron sin responsable nominado.")
    elif coalicion == "exige mano dura":
        alerta = ("La coalición está exigiendo escalamiento y el respaldo "
                  "internacional no da para más.")
    elif not escolta:
        alerta = "No hay escolta disponible: no puede desplazarse esta jornada."
    else:
        alerta = (f"El pliego está al día. Quedan {len(faltan)} decisiones "
                  f"constitutivas sin adoptar.")
    return detalle, alerta


def _temperatura_coalicion(estado: Estado) -> str:
    if estado.intensidad_nacional > 75 and estado.reservas.legitimidad < 45:
        return "exige mano dura"
    if estado.reservas.respaldo_internacional < 40:
        return "presionada por fuera"
    return "sostenida"


# ===========================================================================
# 02 · Interior — el canal sesgado hacia arriba, y lo que hay que proteger
# ===========================================================================

def _interior(estado: Estado):
    """
    Su lectura sesgada es la trampa central del caso: **cree que puede pactar un
    punto entero cuando su interlocutor controla la mitad.** Su interlocutor le
    asegura que controla más de lo que controla.

    Y ahí está la sinergia con el Alcalde, que ve la vocería de su jurisdicción
    bien. Si los dos comparan lecturas antes de negociar, el error se evita. Los
    dos están diciendo la verdad; uno de los dos mira desde más cerca.

    Y LLEVA EL REGISTRO DE INFRAESTRUCTURA RELEVANTE, que era del Ministerio de
    Minas. La aritmética no cambió al cambiar de dueño y es la única que hace
    escasa la fuerza por una razón que no es operar: **lo que se pone a
    proteger sale de lo que desbloquea.** Que la lleve quien no opera es lo que
    mantiene ese pulso entre dos personas y no dentro de una.
    """
    cerrados = [n for n in estado.nodos.values() if not n.abierto]
    lecturas = []
    for n in sorted(cerrados, key=lambda x: -x.control_voceria)[:6]:
        est = information.estimar_nodo(
            n, "parte_operacional", estado.turno, estado.semilla)
        lecturas.append({
            "punto": n.nombre,
            "nodo_id": n.nodo_id,
            "control_voceria_estimado": round(est.control_voceria, 2),
            "region": estado.regiones[n.region_id].nombre,
            "jurisdiccion_epicentro": n.region_id == estado.region_epicentro,
        })

    acuerdos_vivos = [a for a in estado.acuerdos if not a.roto and not a.cumplido]

    detalle = {
        "comite_se_sentaria_hoy": estado.comite_disponible,
        "credibilidad_del_canal": round(estado.reservas.credibilidad_mesa, 1),
        "con_quien_se_puede_hablar": lecturas,
        "acuerdos_vigentes": [
            {"id": a.acuerdo_id, "puntos": len(a.nodos), "vence_turno": a.turno_limite}
            for a in acuerdos_vivos
        ],
        "contraprestacion_legislativa": "disponible" if estado.banderas.lineas_rojas_fijadas
        else "disponible, pero sin líneas rojas se renegociará en la sala",
        # EL OTRO CANAL. Las mesas técnicas rurales de Agricultura negocian
        # tránsito de carga y no pliego, pero se sientan con las mismas
        # organizaciones — y él tiene que poder verlas para decidir si eso le
        # sirve o le rompe la exigencia de interlocutor único. Sin este dato la
        # fricción central entre las dos carteras ocurría a ciegas.
        "mesas_tecnicas_rurales": [
            estado.nodos[nid].nombre for nid in estado.mesas_tecnicas_agro
            if nid in estado.nodos
        ],
        "_nota_sesgo": "su interlocutor le asegura que controla más de lo que controla",
    }

    infra, vitales_solas = _bloque_infraestructura(estado)
    detalle["infraestructura_relevante"] = infra
    detalle["puntos_contiguos_a_infraestructura"] = [
        n.nombre for n in estado.nodos.values() if n.proximidad_infra_critica
    ]

    if estado.comite_retirado_definitivo:
        # Las dos situaciones se leían con la misma frase, y no son la misma:
        # de una se vuelve subiendo la credibilidad y de la otra no se vuelve.
        # Para el rol que vive de la mesa, esa es LA diferencia.
        alerta = ("El Comité se retiró en definitiva. No hay mesa nacional en lo "
                  "que queda del episodio, suba lo que suba la credibilidad.")
    elif not estado.comite_disponible:
        falta = round(P.UMBRALES["credibilidad_comite_suspende"]
                      - estado.reservas.credibilidad_mesa, 1)
        alerta = (f"El Comité suspendió. Hoy no hay mesa nacional posible: "
                  f"vuelve a sentarse con {falta} puntos más de credibilidad.")
    elif acuerdos_vivos:
        a = acuerdos_vivos[0]
        alerta = (f"El acuerdo {a.acuerdo_id} vence en el turno {a.turno_limite}. "
                  f"Operar sobre sus puntos lo rompe.")
    elif estado.reservas.credibilidad_mesa < 35:
        alerta = ("La credibilidad del canal está a un paso del umbral en que el "
                  "Comité se levanta.")
    elif vitales_solas:
        # Nunca dice «protéjala»: dice qué está sin custodiar y de qué depende.
        # Custodiar inmoviliza fuerza que Defensa necesita, y esa es la
        # conversación que tiene que ocurrir en la mesa y no en la pantalla.
        nombres = ", ".join(i.nombre for i in vitales_solas[:2])
        resto = len(vitales_solas) - 2
        alerta = (f"{len(vitales_solas)} instalación(es) de criticidad vital sin "
                  f"custodia: {nombres}"
                  f"{f' y {resto} más' if resto > 0 else ''}. "
                  f"Custodiarlas inmoviliza fuerza que hoy desbloquea.")
    else:
        alerta = "Hay ventana para una sesión de mesa. Una operación hoy la cierra."
    return detalle, alerta


# ===========================================================================
# 03 · Alcalde — su ciudad en alta resolución
# ===========================================================================

def _alcalde(estado: Estado):
    """
    Es el único que puede decir, punto por punto, **si hay alguien con quien
    negociar** en su jurisdicción. Y su sesgo va en dirección contraria al de
    Defensa: ve protesta donde hay estructura.
    """
    mios = estado.nodos_de_region(estado.region_epicentro)
    region = estado.regiones.get(estado.region_epicentro)

    puntos = []
    for n in sorted(mios, key=lambda x: -x.dureza)[:8]:
        est = information.estimar_nodo(
            n, "parte_municipal", estado.turno, estado.semilla)
        puntos.append({
            "punto": n.nombre,
            "nodo_id": n.nodo_id,
            "hay_con_quien_hablar": round(est.control_voceria, 2),
            "estructura_organizada_estimada": round(est.estructura_organizada, 2),
            "apoyo_del_barrio_al_cierre": round(n.apoyo_local, 2),
            "abierto": n.abierto,
        })

    barrios_sin_alimentos = sum(
        1 for n in mios if n.apoyo_local < 0.5 and not n.abierto
    )

    detalle = {
        "mi_jurisdiccion": region.nombre if region else "—",
        "puntos_de_mi_ciudad": puntos,
        "abastecimiento_local": {
            "alimentos_dias": _dias(region.dias_autonomia_alimentos) if region else None,
            "oxigeno_dias": _dias(region.dias_autonomia_oxigeno) if region else None,
            "presion_hospitalaria": round(region.presion_hospitalaria, 2) if region else None,
        },
        "concertacion_previa_exigida": estado.banderas.concertacion_previa_cali,
        "_nota_sesgo": "el parte municipal cuenta más víctimas civiles que el operacional",
    }

    if region and region.dias_autonomia_oxigeno <= 0:
        alerta = (f"{region.nombre} se quedó sin oxígeno y la red hospitalaria está "
                  f"al {region.presion_hospitalaria:.0%}. Cada hora que pasa tiene "
                  f"contador de víctimas.")
    elif region and region.dias_autonomia_oxigeno < 1.5:
        alerta = (f"{region.nombre}: menos de {_dias(region.dias_autonomia_oxigeno):.1f} "
                  f"días de oxígeno y la red hospitalaria al "
                  f"{region.presion_hospitalaria:.0%}.")
    elif barrios_sin_alimentos:
        alerta = (f"{barrios_sin_alimentos} punto(s) con el apoyo del barrio ya "
                  f"cayendo: el esquema humanitario los deshace sin fuerza.")
    elif not estado.banderas.concertacion_previa_cali:
        alerta = ("Nadie ha acordado que la fuerza en esta ciudad se concierte con "
                  "la Alcaldía. La próxima operación entra sin avisar.")
    else:
        alerta = "Hay puntos de la ciudad con vocería fuerte: se pueden pactar."
    return detalle, alerta


# ===========================================================================
# 04 · Defensa — la inteligencia, su propia solidez y sus equipos
# ===========================================================================

def _defensa(estado: Estado):
    """
    Su lectura es el argumento más potente para escalar **y la más sesgada**: ve
    casi el doble de estructura organizada de la que hay, y la mesa tiende a
    creerle porque viene de inteligencia.

    Su tercer dato es un freno a su propio argumento: sabe cuáles de sus casos no
    aguantarían ante un juez. Compartirlo debilita su posición hoy; callarlo
    significa que si un caso se cae, arrastra a todos los demás.

    Y AHORA TIENE LOS EQUIPOS DE TERRENO, que eran las duplas de la Defensoría
    del Pueblo. Es el cambio que más pesa de esta versión: **el que opera es el
    que va a constatar qué pasó.** No pierde capacidad de mirar; lo que se
    perdió es que quien mira no responda ante quien operó.
    """
    cerrados = [n for n in estado.nodos.values() if not n.abierto]
    inteligencia = []
    for n in sorted(cerrados,
                    key=lambda x: -x.composicion_real.estructura_organizada)[:5]:
        est = information.estimar_nodo(
            n, "inteligencia_defensa", estado.turno, estado.semilla)
        # La solidez judicial es su propio juicio sobre su propia evidencia: alta
        # donde la lectura coincide con la realidad, baja donde su sesgo la infló.
        real = n.composicion_real.normalizada().estructura_organizada
        solidez = "se sostiene" if est.estructura_organizada - real < 0.20 else "no se sostiene"
        inteligencia.append({
            "punto": n.nombre,
            "nodo_id": n.nodo_id,
            "financiacion_estimada": round(est.estructura_organizada, 2),
            "solidez_judicial": solidez,
        })

    militares_libres = len([u for u in estado.unidades
                            if u.tipo == "militar" and u.asignacion == "reserva"])
    fragiles = [i for i in inteligencia if i["solidez_judicial"] == "no se sostiene"]

    detalle = {
        "inteligencia_por_punto": inteligencia,
        "capacidad_militar_sin_comprometer": militares_libres,
        "frentes_rurales_que_quedarian_descubiertos": estado.frentes_rurales_descubiertos,
        "asistencia_militar": (
            "firmada con límites" if estado.banderas.asistencia_militar_delimitada
            else "firmada sin límites" if estado.banderas.asistencia_militar_firmada
            else "no firmada"
        ),
        "_nota_sesgo": "la inteligencia sobreestima la estructura organizada",
    }
    detalle.update(_bloque_equipos(estado))

    abiertas = detalle["denuncias_en_ventanilla"]
    if len(abiertas) >= 2 and detalle["equipos_disponibles"] < len(abiertas):
        alerta = (f"{len(abiertas)} denuncias graves sin verificar y "
                  f"{detalle['equipos_disponibles']} equipo(s). No alcanzan: hay "
                  f"que elegir, y declarar públicamente que la otra está en "
                  f"verificación.")
    elif fragiles:
        alerta = (f"{len(fragiles)} de {len(inteligencia)} casos de financiación "
                  f"no aguantarían ante un juez. Si uno se cae, arrastra al resto.")
    elif not estado.banderas.reglas_escritas:
        alerta = ("No hay reglas de empleo escritas. La próxima operación corre "
                  "sin ningún descuento de riesgo.")
    else:
        alerta = (f"{len(inteligencia)} punto(s) con financiación documentada que "
                  f"la mesa está tratando como protesta.")
    return detalle, alerta


# ===========================================================================
# 05 · Policía — el que más ve
# ===========================================================================

def _policia(estado: Estado):
    """
    Es el que más ve, y **el único que puede convertir «hay 6 escuadrones libres»
    en «hay 2 que llegan a tiempo»** — que es una decisión completamente distinta.

    La fatiga es el dato más subestimado del ejercicio: no cuesta nada mirarlo y
    es el principal factor de error.
    """
    esmad = estado.unidades_por_tipo("esmad")
    por_estado: dict[str, int] = {}
    for u in esmad:
        por_estado[u.asignacion] = por_estado.get(u.asignacion, 0) + 1

    fatiga = estado.fatiga_media("esmad")
    agotadas = sum(1 for u in esmad if u.fatiga > 0.75)

    denuncias_abiertas = [d for d in estado.denuncias
                          if not d.verificada and not d.estallo]

    detalle = {
        "esmad_por_estado": por_estado,
        "fatiga_media": round(fatiga, 2),
        "escuadrones_agotados": agotadas,
        "descansados_para_el_mitigador": fatiga < P.UMBRAL_FATIGA_DESCANSADA,
        "denuncias_contra_mis_unidades": [
            {"id": d.denuncia_id, "punto": d.nodo_id, "desde_turno": d.turno_aparicion,
             "declarada_en_verificacion": d.declarada_en_verificacion}
            for d in denuncias_abiertas
        ],
        "parte_clasificado": estado.banderas.protocolo_verificacion,
        "_nota_sesgo": "el parte operacional subestima las víctimas civiles",
    }

    if denuncias_abiertas:
        alerta = (f"{len(denuncias_abiertas)} denuncia(s) sin verificar contra "
                  f"unidades. Si estallan afuera primero, la corrección se leerá "
                  f"como encubrimiento.")
    elif agotadas >= 6:
        alerta = (f"{agotadas} escuadrones por encima de 0,75 de fatiga. A partir "
                  f"de aquí la probabilidad de incidente sube sola.")
    elif len(estado.esmad_en_reserva()) < 2:
        alerta = "No queda ni un escuadrón sin comprometer para una escolta."
    else:
        alerta = (f"{len(estado.esmad_en_reserva())} escuadrones sin comprometer, "
                  f"fatiga media {fatiga:.2f}.")
    return detalle, alerta


# ===========================================================================
# 06 · Transporte — el mapa vivo, y el reparto del combustible
# ===========================================================================

def _transporte(estado: Estado):
    """
    Sin él, la mesa discute «el corredor al puerto» como si fuera una cosa. **Él
    sabe que son cuatro puntos, que tres están abiertos y que todo depende de
    uno** — y esa es la información que evita gastar una operación en el punto
    equivocado.

    Y REPARTE EL COMBUSTIBLE, que era del Ministerio de Minas. Por eso ve los
    días que le quedan a cada región: **quien asigna tiene que ver lo que
    asigna.** Es el único número de esta pantalla que también está en otra —la
    de Agricultura, que lleva el reloj entero—, y está en las dos a propósito.
    """
    corredores = []
    for c in estado.corredores.values():
        bloqueo = c.punto_que_bloquea(estado.nodos)
        corredores.append({
            "corredor": c.nombre,
            "corredor_id": c.corredor_id,
            "flujo": round(c.caudal_efectivo(estado.nodos), 2),
            "bloqueado_en": estado.nodos[bloqueo].nombre if bloqueo else None,
            "nodo_bloqueo": bloqueo,
            "poblacion": c.poblacion_aguas_abajo,
            "costo_diario_mm": c.costo_diario_mm_cop,
            "clases": sorted(c.clases_prioridad),
            "puntos_abiertos": sum(1 for n in c.nodos
                                   if n in estado.nodos and estado.nodos[n].abierto),
            "puntos_totales": len(c.nodos),
        })

    cerrados = [c for c in corredores if c["flujo"] <= 0.05]
    costo_total = sum(c["costo_diario_mm"] for c in cerrados)

    detalle = {
        "mapa_vivo": sorted(corredores, key=lambda c: -c["poblacion"]),
        "costo_diario_de_lo_cerrado_mm_cop": costo_total,
        "gremios": estado.posicion_gremios,
        "ultimatum_vence_turno": estado.ultimatum_gremios_turno,
        "criterio_de_priorizacion_adoptado": estado.banderas.criterio_priorizacion,
        # LA DEMANDA DEL TERCERO. La clase agroalimentaria dejó de ser un
        # criterio suyo: la define el Ministro de Agricultura y él la integra
        # como lo que es, la petición de alguien que también tiene asiento. Verla
        # aquí es lo que le permite defender su orden o cederlo a sabiendas.
        "clase_agroalimentaria_exigida": estado.banderas.clase_alimentaria,
        "combustible_por_region": [
            {"region": f["region"], "combustible_dias": f["combustible_dias"]}
            for f in sorted(_calendario_por_region(estado),
                            key=lambda x: x["combustible_dias"])
        ],
        "prioridad_de_combustible_fijada": estado.banderas.prioridad_combustible_fijada,
    }

    seco = [f for f in detalle["combustible_por_region"]
            if f["combustible_dias"] <= 0]

    if seco:
        alerta = (f"{', '.join(f['region'] for f in seco)} sin combustible. Sin "
                  f"él no se mueve ninguna caravana, escolte quien escolte.")
    elif not estado.banderas.prioridad_combustible_fijada:
        alerta = ("El combustible se está asignando sin criterio: cada turno se "
                  "pelea de nuevo y nadie defiende el orden.")
    elif estado.posicion_gremios == "evaluando":
        alerta = ("Los gremios camioneros están evaluando sumarse. Si lo hacen, "
                  "esto deja de ser orden público y pasa a ser cierre logístico "
                  "nacional.")
    else:
        casi = [c for c in corredores
                if c["puntos_abiertos"] == c["puntos_totales"] - 1 and c["flujo"] <= 0.05]
        if casi:
            c = max(casi, key=lambda x: x["poblacion"])
            alerta = (f"{c['corredor']} depende de un solo punto: {c['bloqueado_en']}. "
                      f"Abrirlo abre {c['poblacion']:,} personas.".replace(",", "."))
        else:
            alerta = (f"{len(cerrados)} corredor(es) cerrados, "
                      f"{costo_total:,} MM COP al día.".replace(",", "."))
    return detalle, alerta


# ===========================================================================
# 07 · Agricultura — el reloj que ya sonó, y el que sigue corriendo
# ===========================================================================

def _agricultura(estado: Estado):
    """
    **Es la única cartera cuyo daño no está por venir: ya ocurrió.** Mientras la
    mesa delibera si abre por fuerza o por concertación, hay granjas
    sacrificando animales porque no les llegó el alimento, y eso no se recupera
    abriendo el corredor mañana. Su número no es un pronóstico, es una pérdida.

    SU SESGO VA CONTRA ELLA Y ES EL MÁS RAZONABLE DE LA MESA. Lee la vocería
    rural mejor que nadie —lleva años tratando con esas organizaciones— y por lo
    mismo **subestima la estructura armada detrás**: donde la inteligencia de
    Defensa ve 0,55 ella ve 0,09. Ninguno de los dos miente. Si comparan
    lecturas antes de que ella instale una mesa, el error se evita; si no, el
    Estado le reconoce interlocución a quien el frente de seguridad está
    documentando como financiador del cierre.

    Y LLEVA EL RELOJ, que era del Ministerio de Minas: los días de oxígeno, de
    combustible y de comida de cada región. Sigue sin verlo la mesa entera —el
    tablero general dice «ROJO» y no los días—, y lo lleva la cartera cuyo daño
    ya ocurrió. **Entregarlo formalmente acelera lo que mide.**
    """
    filas = []
    for r in estado.regiones.values():
        entra = any(
            c.caudal_efectivo(estado.nodos) > 0.05
            for c in estado.corredores_que_sirven(r.region_id, "alimentario")
        )
        filas.append({
            "region": r.nombre,
            "region_id": r.region_id,
            "alimentos_dias": _dias(r.dias_autonomia_alimentos),
            # El índice de precios es SU dato y de nadie más: es el que traduce
            # el bloqueo a lo que paga un hogar, y hasta ahora el motor lo movía
            # sin que ninguna pantalla lo leyera.
            "indice_precios": round(r.indice_precios, 2),
            "entra_alimento": entra,
            "alivios_activados": estado.instrumentos_sectoriales.get(r.region_id, 0),
        })

    # Los puntos RURALES cerrados, leídos por su propia interlocución. No los
    # del epicentro: ahí no tiene mandato y enseñárselos sería invitarla a
    # pedir lo que su acción va a rechazar.
    rurales = [n for n in estado.nodos.values()
               if not n.abierto and n.region_id != estado.region_epicentro]
    lecturas = []
    for n in sorted(rurales, key=lambda x: -x.control_voceria)[:5]:
        est = information.estimar_nodo(
            n, "interlocucion_rural", estado.turno, estado.semilla)
        lecturas.append({
            "punto": n.nombre,
            "nodo_id": n.nodo_id,
            "control_voceria_estimado": round(est.control_voceria, 2),
            "estructura_organizada_estimada": round(est.estructura_organizada, 2),
            "region": estado.regiones[n.region_id].nombre,
            "mesa_tecnica": n.nodo_id in estado.mesas_tecnicas_agro,
        })

    calendario = _calendario_por_region(estado)

    detalle = {
        "tablero_agroalimentario": sorted(filas, key=lambda f: f["alimentos_dias"]),
        "calendario_por_region": calendario,
        "con_quien_hablar_en_el_campo": lecturas,
        "clase_agroalimentaria_fijada": estado.banderas.clase_alimentaria,
        "corredores_de_alimentos": sorted(
            c.nombre for c in estado.corredores.values()
            if "alimentario" in c.clases_prioridad
        ),
        # No cuesta nada hoy y se cobra entero en el debriefing, igual que las
        # instalaciones que Minas dejó sin custodia.
        "excepciones_sanitarias_autorizadas": estado.riesgo_sanitario_asumido,
        "_nota_sesgo": ("lee de menos la estructura armada del campo; la lectura "
                        "contraria, y mucho más alta, la tiene la inteligencia "
                        "del Ministerio de Defensa sobre estos mismos puntos"),
    }

    sin_comida = [f for f in filas if f["alimentos_dias"] <= 0]
    apretadas = [f for f in filas if f["alimentos_dias"] < 1.5]
    sin_oxigeno = [x for x in calendario if x["oxigeno_dias"] <= 0]
    criticas = [x for x in calendario if x["oxigeno_dias"] < 1.5]

    # EL OXÍGENO VA PRIMERO Y LA COMIDA DESPUÉS, aunque la comida sea su
    # cartera. Por debajo de cero días de oxígeno lo que corre es el contador de
    # muertes evitables, y no hay nada en esta pantalla que sea más urgente.
    if sin_oxigeno:
        alerta = (f"{', '.join(x['region'] for x in sin_oxigeno)} sin oxígeno. "
                  f"Ahí ya no queda margen: lo que corre es el contador de "
                  f"muertes evitables.")
    elif criticas:
        peor = min(criticas, key=lambda x: x["oxigeno_dias"])
        alerta = (f"{peor['region']}: {peor['oxigeno_dias']} días de oxígeno. "
                  f"Si mañana no entra nada, {peor['oxigeno_manana']}.")
    elif sin_comida:
        alerta = (f"{', '.join(f['region'] for f in sin_comida)} sin días de "
                  f"comida. Lo que se pierde ahí no vuelve abriendo el corredor "
                  f"mañana: son animales sacrificados y cosecha podrida.")
    elif apretadas:
        peor = min(apretadas, key=lambda f: f["alimentos_dias"])
        cerrado = "" if peor["entra_alimento"] else " Hoy no entra nada."
        alerta = (f"{peor['region']}: {peor['alimentos_dias']} días de comida."
                  f"{cerrado} La ventana de los perecederos se mide en horas.")
    elif not estado.banderas.clase_alimentaria:
        alerta = ("Los alimentos no tienen turno propio en el reparto de "
                  "corredores: van detrás de todo, y lo que llega tarde ya no "
                  "sirve.")
    elif estado.riesgo_sanitario_asumido >= 2:
        alerta = (f"{estado.riesgo_sanitario_asumido} autorizaciones sanitarias "
                  f"excepcionales en curso. El ganado se mueve sin control pleno "
                  f"y de eso responde esta cartera después del episodio.")
    else:
        peor = min(filas, key=lambda f: f["alimentos_dias"])
        alerta = (f"{peor['region']} es la más apretada de comida: "
                  f"{peor['alimentos_dias']} días.")
    return detalle, alerta


_VISTAS = {
    "Presidente": _presidente,
    "Interior": _interior,
    "Alcalde": _alcalde,
    "Defensa": _defensa,
    "Policía": _policia,
    "Transporte": _transporte,
    "Agricultura": _agricultura,
}
