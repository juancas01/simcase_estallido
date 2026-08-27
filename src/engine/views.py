"""
views.py — Las ocho vistas privadas.

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

**Las ocho alertas de cada turno no caben en la capacidad disponible.** Ese es el
diseño: ocho personas con ocho urgencias legítimas y una escolta.

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


ROLES = [
    "Presidente", "Interior", "Alcalde", "Defensa",
    "Policía", "Defensoría", "Transporte", "Minas",
]


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
        raise KeyError(f"rol desconocido: {rol}. Los ocho son {ROLES}")
    detalle, alerta = fn(estado)
    return {
        "rol": rol,
        "turno": estado.turno_decision,
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
    el único que tiene delante lo que cada rol declaró al entrar.
    """
    ultimas = estado.registro[-8:]
    sin_responsable = [d for d in ultimas if not d.atribuible]

    coalicion = _temperatura_coalicion(estado)
    escolta = len(estado.esmad_en_reserva()) >= 2

    detalle = {
        "pliego_de_decisiones": [
            {
                "turno": d.turno, "rol": d.rol, "accion": d.descripcion,
                "responsable": d.responsable_nominado or "— SIN NOMBRE —",
                "marcado": not d.atribuible,
            }
            for d in ultimas
        ],
        "temperatura_coalicion": coalicion,
        "puede_desplazarse": escolta,
        "lineas_declaradas_turno_0": "las tiene el sistema; se contrastan al cierre",
    }

    if sin_responsable:
        alerta = (f"{len(sin_responsable)} de las últimas {len(ultimas)} decisiones "
                  f"salieron sin responsable nominado.")
    elif coalicion == "exige mano dura":
        alerta = ("La coalición está exigiendo escalamiento y el respaldo "
                  "internacional no da para más.")
    elif not escolta:
        alerta = "No hay escolta disponible: no puede desplazarse este turno."
    else:
        alerta = "El pliego está al día y cada decisión tiene nombre."
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
        "_nota_sesgo": "su interlocutor le asegura que controla más de lo que controla",
    }

    if not estado.comite_disponible:
        alerta = "El Comité suspendió. Hoy no hay mesa nacional posible."
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
            "alimentos_dias": round(region.dias_autonomia_alimentos, 1) if region else None,
            "oxigeno_dias": round(region.dias_autonomia_oxigeno, 1) if region else None,
            "presion_hospitalaria": round(region.presion_hospitalaria, 2) if region else None,
        },
        "concertacion_previa_exigida": estado.banderas.concertacion_previa_cali,
        "_nota_sesgo": "el parte municipal cuenta más víctimas civiles que el operacional",
    }

    if region and region.dias_autonomia_oxigeno < 1.5:
        alerta = (f"{region.nombre}: menos de {region.dias_autonomia_oxigeno:.1f} días "
                  f"de oxígeno y la red hospitalaria al {region.presion_hospitalaria:.0%}.")
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
            "oxigeno_dias": round(r.dias_autonomia_oxigeno, 1),
            "oxigeno_manana": round(manana, 1),
            "combustible_dias": round(r.dias_autonomia_combustible, 1),
            "alimentos_dias": round(r.dias_autonomia_alimentos, 1),
            "entra_humanitario": entra_oxi,
            "muertes_evitables": r.muertes_evitables,
        })

    criticas = [x for x in regiones if x["oxigeno_dias"] < 1.5]

    detalle = {
        "calendario_por_region": sorted(regiones, key=lambda x: x["oxigeno_dias"]),
        "instalaciones_criticas_declaradas": len(estado.instalaciones_criticas),
        "puntos_contiguos_a_infraestructura": [
            n.nombre for n in estado.nodos.values() if n.proximidad_infra_critica
        ],
        "prioridad_de_combustible_fijada": estado.banderas.prioridad_combustible_fijada,
        "panico_por_difusion": round(
            max((r.panico for r in estado.regiones.values()), default=0.0), 2
        ),
    }

    if criticas:
        peor = min(criticas, key=lambda x: x["oxigeno_dias"])
        alerta = (f"{peor['region']}: {peor['oxigeno_dias']} días de oxígeno. "
                  f"Si mañana no entra nada, {peor['oxigeno_manana']}.")
    elif not estado.banderas.prioridad_combustible_fijada:
        alerta = ("El combustible se está asignando sin criterio: cada turno se "
                  "pelea de nuevo y nadie defiende el orden.")
    else:
        peor = min(regiones, key=lambda x: x["oxigeno_dias"])
        alerta = f"{peor['region']} es la más apretada: {peor['oxigeno_dias']} días."
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
}
