"""
loader.py — Construye el estado heredado (t=0) desde datos.

Regla de oro heredada de Macondo: si un dato aparece a la vez en un archivo y en
el prompt de un modelo, se desincronizará. Siempre. Todo lo que define el caso
vive en `data/`, y el catálogo que ve el modelo se GENERA desde aquí.

AQUÍ NO ARRANCA EN CERO. El paro lleva quince días cuando los nueve entran a la
sala: el PMU ya está convocado, la mesa ya se instaló y ya se rompió una vez, y
la fuerza ya está desplegada y cansada. Lo que da inicio al ejercicio no es una
acción: es un estado heredado más una exigencia con plazo.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.engine import parameters as P
from src.engine import territory
from src.engine.state import (
    Estado, Nodo, Corredor, Region, Unidad, Composicion, Reservas, Banderas,
    Denuncia, Infraestructura,
)


def _ruta_por_defecto() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "escenario" / "estado_inicial.json"


def cargar_estado(ruta: str | Path | None = None) -> Estado:
    ruta = Path(ruta) if ruta else _ruta_por_defecto()
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el escenario: {ruta}")

    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)

    estado = Estado(turno=0, franja="dia")
    estado.region_epicentro = d.get("region_epicentro", "")
    estado.geografia = d.get("mapa", {})

    for r in d["regiones"]:
        estado.regiones[r["region_id"]] = Region(
            region_id=r["region_id"],
            nombre=r["nombre"],
            dias_autonomia_combustible=r["dias_autonomia_combustible"],
            dias_autonomia_alimentos=r["dias_autonomia_alimentos"],
            dias_autonomia_oxigeno=r["dias_autonomia_oxigeno"],
            presion_hospitalaria=r.get("presion_hospitalaria", 0.7),
            intensidad_movilizacion=r.get("intensidad_movilizacion", P.INTENSIDAD_NACIONAL_T0),
            nodos_secundarios_activos=r.get("nodos_secundarios_activos", 100),
        )

    for n in d["nodos"]:
        comp = n.get("composicion_real", [0.75, 0.15, 0.10])
        estado.nodos[n["nodo_id"]] = Nodo(
            nodo_id=n["nodo_id"],
            nombre=n["nombre"],
            region_id=n["region_id"],
            corredor_id=n.get("corredor_id"),
            dureza=n.get("dureza", 0.5),
            caudal=0.0,
            dias_sostenido=n.get("dias_sostenido", 0),
            masa_base=n.get("masa_base", 200),
            # En t=0 hay la gente que hay: la base. `mobilization.recalcular` la
            # escala por la intensidad de la región en cuanto empieza el turno 1.
            masa_presente=n.get("masa_base", 200),
            apoyo_local=n.get("apoyo_local", 0.7),
            control_voceria=n.get("control_voceria", 0.5),
            proximidad_infra_critica=n.get("proximidad_infra_critica", False),
            x=n.get("x", 0.0),
            y=n.get("y", 0.0),
            composicion_real=Composicion(*comp).normalizada(),
        )

    for c in d["corredores"]:
        estado.corredores[c["corredor_id"]] = Corredor(
            corredor_id=c["corredor_id"],
            nombre=c["nombre"],
            nodos=c["nodos"],
            poblacion_aguas_abajo=c["poblacion_aguas_abajo"],
            costo_diario_mm_cop=c["costo_diario_mm_cop"],
            clases_prioridad=set(c.get("clases_prioridad", [])),
        )

    # LA INFRAESTRUCTURA RELEVANTE. Es una guia, no un adversario: no hay
    # acciones en contra de ella. Lo que hace es que declarar critica una
    # instalacion deje de ser una cadena de texto libre y pase a apuntar a algo
    # que existe, con su region, su sitio y de que depende.
    for x in d.get("infraestructura", []):
        estado.infraestructura[x["infra_id"]] = Infraestructura(
            infra_id=x["infra_id"],
            nombre=x["nombre"],
            tipo=x.get("tipo", "logistica"),
            region_id=x["region_id"],
            x=x.get("x", 0.0),
            y=x.get("y", 0.0),
            criticidad=x.get("criticidad", "alta"),
            de_que_depende=x.get("de_que_depende", ""),
            nodos_contiguos=list(x.get("nodos_contiguos", [])),
        )

    # El hecho H2 del paquete detonante: dos denuncias graves sin verificar, una
    # cierta y otra falsa, y nada las distingue.
    for x in d.get("denuncias_iniciales", []):
        estado.denuncias.append(Denuncia(
            denuncia_id=x["denuncia_id"],
            texto=x["texto"],
            nodo_id=x.get("nodo_id"),
            veraz=x["veraz"],
            turno_aparicion=1,
        ))

    estado.unidades = _construir_fuerza()
    estado.reservas = Reservas(**P.RESERVAS_T0)
    estado.banderas = Banderas()          # ningún mitigador activo en t=0
    estado.intensidad_nacional = P.INTENSIDAD_NACIONAL_T0
    estado.duplas_disponibles = P.DUPLAS_TOTALES

    # Los gremios arrancan FUERA y no evaluando: lo que los activa en el turno 1
    # no es el umbral de legitimidad sino el ultimátum de 48 horas del paquete
    # detonante, que es un disparador independiente. Los dos caminos hacia
    # `evaluando` deben coexistir, porque son cosas distintas: una es que el país
    # deje de respaldar al Gobierno y otra es que un gremio pida algo concreto.
    estado.posicion_gremios = "fuera"
    estado.ultimatum_gremios_turno = P.TURNO_ULTIMATUM_GREMIOS

    _aplicar_hecho_h1(estado, d.get("hecho_h1"))

    _verificar_invariantes(estado)
    return estado


def _aplicar_hecho_h1(estado: Estado, h: dict | None) -> None:
    """
    H1 del paquete detonante: el incidente nocturno junto a la refinería.

    **Ya ocurrió.** La sala lo recibe en el parte heredado, no lo provoca, y esa
    diferencia es el punto: el turno 1 no empieza en calma sino con un herido
    grave de la fuerza pública y una instalación crítica bajo presión.

    POR QUÉ `N013` Y NO OTRO. El punto ya trae la trampa en los datos:

        dureza 0,77 .............. el más duro de los tres junto a infraestructura
        control_voceria 0,28 ..... casi no hay con quién concertar
        51 % protesta legítima ... apenas sobre el umbral de 0,50, así que
                                   operar ahí cuesta el doble
        región epicentro, corredor de la refinería — el que Minas necesita

    Responder con fuerza es la jugada evidente y es la más cara, en el punto
    donde menos se puede negociar, sobre el corredor que otra cartera necesita
    intacto. Y la mesa todavía no se ha constituido: sin registro escrito, sin
    protocolo de vocería y sin criterio de priorización, los mitigadores están
    al mínimo.

    LO QUE H1 NO HACE: matar a nadie ni abrir el punto. Es una condición
    inicial, no un resultado. Si el hecho detonante ya resolviera algo, el turno
    1 empezaría con menos decisiones y no con más.

    La intensidad se asigna DIRECTAMENTE y no vía `registrar_evento()`: ese
    camino lleva la cuenta de repeticiones para los rendimientos decrecientes, y
    gastar ahí un turno que aún no ha empezado descontaría el primer incidente
    de verdad.
    """
    if not h:
        return

    nodo = estado.nodos.get(h["nodo"])
    if nodo is None:
        raise ValueError(
            f"El hecho H1 apunta a «{h['nodo']}», que no existe en el escenario."
        )

    nodo.dureza = min(1.0, nodo.dureza + h.get("dureza_extra", 0.0))

    region = estado.regiones[nodo.region_id]
    region.intensidad_movilizacion = min(
        100.0, region.intensidad_movilizacion + h.get("intensidad_region", 0.0))
    estado.intensidad_nacional = min(
        100.0, estado.intensidad_nacional + h.get("intensidad_nacional", 0.0))

    # La custodia inmoviliza fuerza: es la colisión entre lo que Minas necesita
    # proteger y lo que Defensa necesita disponible. Sale de la reserva, para que
    # se note en el contador del tablero desde el primer minuto.
    # LA INSTALACIÓN VIENE POR IDENTIFICADOR, no por nombre. Queda marcada como
    # custodiada desde el primer minuto —esa custodia la puso el hecho heredado,
    # no una decisión de la mesa— y el debriefing no le imputa a la sala un
    # riesgo que no asumió.
    instalacion = h.get("instalacion")
    if instalacion:
        infra = estado.infraestructura.get(instalacion)
        if infra is None:
            raise ValueError(
                f"El hecho H1 custodia «{instalacion}», que no está en el "
                f"registro de infraestructura del escenario."
            )
        estado.instalaciones_criticas.append(infra.nombre)
        infra.protegida = True
        infra.protegida_desde_turno = 0
    cuantas = h.get("custodia_inmovilizada", 0)
    for u in estado.unidades:
        if cuantas <= 0:
            break
        if u.tipo == "policia" and u.asignacion != "custodia":
            u.asignacion = "custodia"
            u.ubicacion = nodo.nodo_id
            cuantas -= 1

    estado.hecho_h1 = {
        "nodo": nodo.nodo_id,
        "nombre": nodo.nombre,
        "region": region.nombre,
        "texto": h.get("texto", ""),
        "publicacion": h.get("publicacion"),
    }


def _construir_fuerza() -> list[Unidad]:
    """
    34 de 40 escuadrones de ESMAD ya desplegados y con fatiga media 0,55.

    La sala no hereda una fuerza fresca: hereda una fuerza cansada. La decisión
    de relevo está viva desde el turno 1.
    """
    unidades: list[Unidad] = []
    for i in range(P.ESMAD_ESCUADRONES_TOTALES):
        desplegada = i < P.ESMAD_DESPLEGADOS_T0
        unidades.append(Unidad(
            unidad_id=f"ESMAD-{i+1:02d}",
            tipo="esmad",
            asignacion="contencion" if desplegada else "reserva",
            fatiga=P.FATIGA_MEDIA_T0 if desplegada else 0.0,
            turnos_continuos=4 if desplegada else 0,
        ))
    for i in range(20):
        unidades.append(Unidad(f"POL-{i+1:02d}", "policia", "contencion", fatiga=0.45))
    for i in range(12):
        unidades.append(Unidad(f"MIL-{i+1:02d}", "militar", "reserva", fatiga=0.10))
    return unidades


def _verificar_invariantes(estado: Estado) -> None:
    """
    Comprobaciones que deben cumplirse SIEMPRE al cargar, y que fallan
    ruidosamente. Cada una se descubrió rompiéndose.
    """
    for c in estado.corredores.values():
        faltan = [n for n in c.nodos if n not in estado.nodos]
        if faltan:
            raise ValueError(f"Corredor {c.corredor_id} referencia nodos inexistentes: {faltan}")

    for n in estado.nodos.values():
        if n.region_id not in estado.regiones:
            raise ValueError(f"Nodo {n.nodo_id} referencia región inexistente: {n.region_id}")
        s = (n.composicion_real.protesta_legitima
             + n.composicion_real.vandalismo_oportunista
             + n.composicion_real.estructura_organizada)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"Nodo {n.nodo_id}: composicion_real no suma 1 ({s})")

    if any(v for k, v in vars(estado.banderas).items()
           if isinstance(v, bool) and k not in ("defensoria_presente",)):
        raise ValueError("En t=0 no debe haber ninguna bandera activa salvo defensoria_presente")

    # INVARIANTE CRÍTICA: toda región debe tener al menos un corredor humanitario.
    #
    # Sin ella, una región sin vía de reposición de oxígeno acumula muertes
    # evitables HAGA LO QUE HAGA la sala. Eso no es un dilema: es un guion que
    # castiga. Se detectó midiendo —una región no tenía ninguno y las cinco
    # estrategias daban exactamente las mismas 147 muertes—, y por eso la
    # comprobación vive aquí.
    for r in estado.regiones.values():
        if not estado.corredores_que_sirven(r.region_id, "humanitario"):
            raise ValueError(
                f"La región {r.nombre} no tiene ningún corredor de clase "
                f"'humanitario'. Sus muertes evitables serían inevitables por "
                f"construcción."
            )

    # INVARIANTE DEL PAQUETE DETONANTE: nunca una sola denuncia sin verificar.
    # Siempre al menos dos, con veracidad DISTINTA. Un ejercicio en el que la
    # única denuncia grave resulta inventada enseña que las denuncias graves
    # suelen serlo — y eso, sobre hechos con responsabilidad judicial viva, es
    # tomar partido.
    if estado.denuncias:
        if len(estado.denuncias) < 2:
            raise ValueError(
                "Nunca una sola denuncia sin verificar: hacen falta al menos dos."
            )
        veracidades = {d.veraz for d in estado.denuncias}
        if len(veracidades) < 2:
            raise ValueError(
                "Las denuncias iniciales deben tener veracidad DISTINTA: al menos "
                "una cierta y una falsa, sin ninguna señal que las distinga."
            )

    if estado.region_epicentro and estado.region_epicentro not in estado.regiones:
        raise ValueError(f"region_epicentro desconocida: {estado.region_epicentro}")

    _verificar_geografia(estado)


def _verificar_geografia(estado: Estado) -> None:
    """
    Cada punto tiene que caer DENTRO del polígono de su región.

    Mientras el mapa fue un esquema de líneas, las coordenadas no afirmaban nada:
    eran la disposición de un plano de metro y podían estar en cualquier sitio.
    Desde que el mapa dibuja el país, un punto fuera de su polígono es la pantalla
    **afirmando en una pared que ese bloqueo está en otra región** — y el reparto
    territorial es justo lo que la sala está leyendo ahí.

    No puede ser «lo revisó alguien al dibujarlo», porque el motor genera cierres
    nuevos por su cuenta cuando la intensidad sube (`mobilization._generar_nodo`).

        Una regla que el software garantiza vale más que una que el software
        recomienda.

    Sin bloque `mapa` en el escenario no hay nada que comprobar y no pasa nada:
    un escenario sin geografía es válido, solo que su mapa no se dibuja.
    """
    poligonos = (estado.geografia or {}).get("regiones") or {}
    if not poligonos:
        return

    faltan = [r for r in estado.regiones if r not in poligonos]
    if faltan:
        raise ValueError(
            f"El mapa no tiene polígono para {faltan}. Sus puntos no se podrían "
            f"dibujar en ninguna parte."
        )

    fuera = [
        f"{n.nodo_id} ({n.nombre}) en ({n.x}, {n.y}) no cae dentro de {n.region_id}"
        for n in estado.nodos.values()
        if not territory.dentro(n.x, n.y, poligonos[n.region_id])
    ]
    if fuera:
        raise ValueError("Puntos fuera de su región en el mapa: " + "; ".join(fuera))

    # Y lo mismo para la infraestructura, por la misma razón: el mapa la dibuja
    # con nombre, y una refinería pintada en la región equivocada es la pantalla
    # afirmando en una pared algo que el motor no dice.
    mal = [
        f"{i.infra_id} ({i.nombre}) en ({i.x}, {i.y}) no cae dentro de {i.region_id}"
        for i in estado.infraestructura.values()
        if i.region_id in poligonos
        and not territory.dentro(i.x, i.y, poligonos[i.region_id])
    ]
    if mal:
        raise ValueError("Infraestructura fuera de su región: " + "; ".join(mal))

    huerfanas = [
        f"{i.infra_id} apunta a {n}"
        for i in estado.infraestructura.values()
        for n in i.nodos_contiguos if n not in estado.nodos
    ]
    if huerfanas:
        raise ValueError(
            "Infraestructura contigua a puntos inexistentes: " + "; ".join(huerfanas))


def catalogo_para_agente(estado: Estado) -> dict:
    """
    El catálogo que ve el modelo se GENERA desde el estado, no se escribe a mano
    en el prompt. En Macondo, un paquete que faltaba en el prompt escrito a mano
    fue invisible para el agente durante todo un ejercicio.
    """
    return {
        "puntos": [
            {"id": n.nodo_id, "nombre": n.nombre,
             "region": estado.regiones[n.region_id].nombre,
             "corredor": n.corredor_id, "abierto": n.abierto}
            for n in estado.nodos.values()
        ],
        "corredores": [
            {"id": c.corredor_id, "nombre": c.nombre, "clases": sorted(c.clases_prioridad)}
            for c in estado.corredores.values()
        ],
        "regiones": [
            {"id": r.region_id, "nombre": r.nombre} for r in estado.regiones.values()
        ],
        "denuncias": [d.vista_publica() for d in estado.denuncias],
    }
