"""
views.py — Las nueve vistas privadas.

    El tablero general responde QUÉ ESTÁ PASANDO.
    La vista privada responde CUÁNTO, DÓNDE EXACTAMENTE Y DESDE CUÁNDO.

RESOLUCIÓN, NO SECRETO
----------------------
Nadie tiene información que los demás no puedan pedir. Lo que cada uno tiene es
**su cartera en alta resolución**, y el resto del país en grano grueso. El
tablero dice «Las Cumbres · abastecimiento ROJO»; solo Minas sabe que son 1,8
días y que mañana serán 0,4.

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


# LOS NUEVE, EN EL ORDEN DE LOS TRES FRENTES: estrategia, seguridad, logística.
# El orden no es decorativo — la portada y el acceso desde el tablero agrupan
# por frente leyendo esta lista, y tres bloques de tres es lo que hace que la
# rejilla se lea de un vistazo.
ROLES = [
    "Presidente", "Interior", "Alcalde",
    "Defensa", "Policía", "Defensoría",
    "Transporte", "Minas", "Agricultura",
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


# Las once decisiones constitutivas que la mesa puede tomar, y qué bandera
# levanta cada una. Es el cuadro de mando del Presidente: quién ha constituido
# qué, y qué sigue sin constituirse. Se lee del estado y no se escribe a mano.
CONSTITUTIVAS = (
    ("registro_escrito", "Registro escrito de decisiones", "Presidente"),
    ("lineas_rojas_fijadas", "Líneas rojas del Ejecutivo", "Presidente"),
    ("protocolo_voceria", "Protocolo de vocería única", "Interior"),
    ("concertacion_previa_cali", "Fuerza concertada con la Alcaldía", "Alcalde"),
    ("reglas_escritas", "Reglas de empleo escritas", "Defensa · Defensoría"),
    ("identificacion_agentes", "Identificación de agentes", "Defensoría"),
    ("registro_av", "Registro audiovisual", "Defensoría · Defensa"),
    ("protocolo_verificacion", "Protocolo de verificación", "Policía · Defensoría"),
    ("criterio_priorizacion", "Criterio de priorización", "Transporte"),
    ("prioridad_combustible_fijada", "Prioridad del combustible", "Minas"),
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
        raise KeyError(f"rol desconocido: {rol}. Los nueve son {ROLES}")
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
# 02 · Interior — el estado del canal, sesgado hacia arriba
# ===========================================================================

def _interior(estado: Estado):
    """
    Su lectura sesgada es la trampa central del caso: **cree que puede pactar un
    punto entero cuando su interlocutor controla la mitad.** Su interlocutor le
    asegura que controla más de lo que controla.

    Y ahí está la sinergia con el Alcalde, que ve la vocería de su jurisdicción
    bien. Si los dos comparan lecturas antes de negociar, el error se evita. Los
    dos están diciendo la verdad; uno de los dos mira desde más cerca.
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
# 04 · Defensa — la inteligencia, y su propia solidez
# ===========================================================================

def _defensa(estado: Estado):
    """
    Su lectura es el argumento más potente para escalar **y la más sesgada**: ve
    casi el doble de estructura organizada de la que hay, y la mesa tiende a
    creerle porque viene de inteligencia.

    Su tercer dato es un freno a su propio argumento: sabe cuáles de sus casos no
    aguantarían ante un juez. Compartirlo debilita su posición hoy; callarlo
    significa que si un caso se cae, arrastra a todos los demás.
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

    if fragiles:
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
# 06 · Defensoría — tres duplas y veinticuatro puntos
# ===========================================================================

def _defensoria(estado: Estado):
    """
    Es la única fuente que casi no se equivoca, y la que menos alcanza a ver.
    **Verificar aquí es no verificar allá**, y esa elección es suya cada turno.

    Las tres duplas salen del mismo bolsillo que el acompañamiento de
    operaciones: no puede hacer las tres cosas.
    """
    sin_verificar = [n for n in estado.nodos.values()
                     if n.ultima_verificacion_turno is None]
    abiertas = [d for d in estado.denuncias if not d.verificada and not d.estallo]

    verificados = []
    for n in estado.nodos.values():
        if n.verificado_por == "dupla_defensoria":
            # El turno de la LECTURA, no el actual: lo que la dupla constató en
            # el turno 2 tiene que seguir diciendo lo mismo en el turno 5. Con
            # `estado.turno` la verificación se volvía a tirar cada vez que
            # alguien abría la vista, que es lo contrario de «constatado».
            cuando = n.ultima_verificacion_turno
            if cuando is None:
                cuando = estado.turno
            est = information.estimar_nodo(
                n, "dupla_defensoria", cuando, estado.semilla)
            verificados.append({
                "punto": n.nombre,
                "estructura_organizada": round(est.estructura_organizada, 2),
                "turno": n.ultima_verificacion_turno,
            })

    detalle = {
        "duplas_disponibles": estado.duplas_disponibles,
        "duplas_usadas_este_turno": list(estado.duplas_usadas_en),
        "denuncias_en_ventanilla": [d.vista_publica() for d in abiertas],
        "puntos_sin_mirar": len(sin_verificar),
        "lo_que_han_constatado": verificados[-5:],
        "_nota": ("cada dupla hace UNA cosa por turno: verificar un punto, "
                  "verificar una denuncia, o acompañar una operación"),
    }

    if len(abiertas) >= 2 and estado.duplas_disponibles < len(abiertas):
        alerta = (f"{len(abiertas)} denuncias graves sin verificar y "
                  f"{estado.duplas_disponibles} dupla(s). No alcanzan: hay que "
                  f"elegir, y declarar públicamente que la otra está en verificación.")
    elif estado.duplas_disponibles == 0:
        alerta = "No quedan duplas este turno. Lo que no se miró, no se miró."
    elif not estado.banderas.reglas_escritas:
        alerta = ("Ningún mitigador está activo. El estándar completo divide la "
                  "probabilidad de incidente por casi cinco y no cuesta un escuadrón.")
    else:
        alerta = (f"{len(sin_verificar)} punto(s) que nadie ha mirado y "
                  f"{estado.duplas_disponibles} dupla(s) disponibles.")
    return detalle, alerta


# ===========================================================================
# 07 · Transporte — el mapa vivo
# ===========================================================================

def _transporte(estado: Estado):
    """
    Sin él, la mesa discute «el corredor al puerto» como si fuera una cosa. **Él
    sabe que son cuatro puntos, que tres están abiertos y que todo depende de
    uno** — y esa es la información que evita gastar una operación en el punto
    equivocado.
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
    }

    if estado.posicion_gremios == "evaluando":
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
# 08 · Minas — el reloj
# ===========================================================================

def _minas(estado: Estado):
    """
    **Es quien tiene el reloj.** Mientras no lo diga, la mesa sabe que hay un
    problema de abastecimiento y no sabe cuánto tiempo tiene.

    Su proyección a mañana es lo que convierte la deliberación en una cuenta
    atrás — y entregarla formalmente la acelera.
    """
    regiones = []
    for r in estado.regiones.values():
        entra_oxi = any(
            c.caudal_efectivo(estado.nodos) > 0.05
            for c in estado.corredores_que_sirven(r.region_id, "humanitario")
        )
        manana = r.dias_autonomia_oxigeno - (0.0 if entra_oxi else 1.0 * (1 + r.panico))
        regiones.append({
            "region": r.nombre,
            "region_id": r.region_id,
            "oxigeno_dias": _dias(r.dias_autonomia_oxigeno),
            "oxigeno_manana": _dias(manana),
            "combustible_dias": _dias(r.dias_autonomia_combustible),
            "alimentos_dias": _dias(r.dias_autonomia_alimentos),
            "entra_humanitario": entra_oxi,
            "muertes_evitables": r.muertes_evitables,
        })

    criticas = [x for x in regiones if x["oxigeno_dias"] < 1.5]

    # LA INFRAESTRUCTURA QUE LE TOCA PROTEGER, con nombre y con estado. Es su
    # cartera y no la tenía: hasta ahora su vista decía cuántas instalaciones
    # había declarado —un número— y no cuáles existen ni qué queda sin custodiar.
    # Declarar a ciegas era la consecuencia.
    infra = sorted(
        estado.infraestructura.values(),
        key=lambda i: (i.protegida, {"vital": 0, "alta": 1}.get(i.criticidad, 2)),
    )
    sin_custodia = [i for i in infra if not i.protegida]
    vitales_solas = [i for i in sin_custodia if i.criticidad == "vital"]

    detalle = {
        "calendario_por_region": sorted(regiones, key=lambda x: x["oxigeno_dias"]),
        "infraestructura_relevante": [
            {
                "instalacion": i.nombre,
                "region": estado.regiones[i.region_id].nombre
                if i.region_id in estado.regiones else i.region_id,
                "criticidad": i.criticidad,
                "custodia": "puesta" if i.protegida else "sin proteger",
                "de_que_depende": i.de_que_depende,
            }
            for i in infra
        ],
        "puntos_contiguos_a_infraestructura": [
            n.nombre for n in estado.nodos.values() if n.proximidad_infra_critica
        ],
        "prioridad_de_combustible_fijada": estado.banderas.prioridad_combustible_fijada,
        "panico_por_difusion": round(
            max((r.panico for r in estado.regiones.values()), default=0.0), 2
        ),
    }

    agotadas = [x for x in regiones if x["oxigeno_dias"] <= 0]
    if agotadas:
        alerta = (f"{', '.join(x['region'] for x in agotadas)} sin oxígeno. "
                  f"Ahí ya no queda margen: lo que corre es el contador de "
                  f"muertes evitables.")
    elif criticas:
        peor = min(criticas, key=lambda x: x["oxigeno_dias"])
        alerta = (f"{peor['region']}: {peor['oxigeno_dias']} días de oxígeno. "
                  f"Si mañana no entra nada, {peor['oxigeno_manana']}.")
    elif vitales_solas:
        # Nunca dice «protéjala»: dice qué está sin custodiar y de qué depende.
        # Custodiar inmoviliza fuerza que Defensa necesita, y esa es la
        # conversación que tiene que ocurrir en la mesa y no en la pantalla.
        #
        # DOS NOMBRES Y EL RECUENTO, no la lista entera: con cinco instalaciones
        # sin custodia la línea pasaba de 260 caracteres y la vista dejaba de
        # caber en una pantalla, que es la regla que hace que la sala se mire
        # entre sí en vez de mirar el dispositivo. La lista completa está en el
        # detalle, dos centímetros más abajo.
        nombres = ", ".join(i.nombre for i in vitales_solas[:2])
        resto = len(vitales_solas) - 2
        alerta = (f"{len(vitales_solas)} instalación(es) de criticidad vital sin "
                  f"custodia: {nombres}"
                  f"{f' y {resto} más' if resto > 0 else ''}. "
                  f"Custodiarlas inmoviliza fuerza que hoy desbloquea.")
    elif not estado.banderas.prioridad_combustible_fijada:
        alerta = ("El combustible se está asignando sin criterio: cada turno se "
                  "pelea de nuevo y nadie defiende el orden.")
    else:
        peor = min(regiones, key=lambda x: x["oxigeno_dias"])
        alerta = f"{peor['region']} es la más apretada: {peor['oxigeno_dias']} días."
    return detalle, alerta


# ===========================================================================
# 09 · Agricultura — el reloj que ya sonó
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

    detalle = {
        "tablero_agroalimentario": sorted(filas, key=lambda f: f["alimentos_dias"]),
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

    if sin_comida:
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
    "Defensoría": _defensoria,
    "Transporte": _transporte,
    "Minas": _minas,
    "Agricultura": _agricultura,
}
