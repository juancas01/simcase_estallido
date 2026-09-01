"""
supply.py — El reloj de la crisis.

Los días de autonomía son el driver del caso y, a diferencia de la lluvia de
Macondo, son ENDÓGENOS: bajan solos y solo suben si alguien abre un corredor que
sirva a esa región.

EL OXÍGENO MEDICINAL
--------------------
Es la única variable del motor que convierte logística en muertes, y no es
independiente: es el extremo de una cadena que empieza en una decisión de la sala.

    corredor abierto → entra combustible → hay diésel para carrotanques
                                         → y para plantas de emergencia
                                         → las plantas sostienen producción
                                           y cadena de frío
                                         → hay oxígeno en la UCI
                                         → no se muere quien no tenía que morirse

Cortar la cadena en cualquier punto la rompe entera. Por eso el oxígeno vive
aquí y no en un módulo sanitario: **no modela salud, modela el alcance de una
decisión logística.** Y por eso ninguna cartera lo resuelve sola.

DOS ENTRADAS, NO UNA
--------------------
Hasta la v2 el reloj solo se movía abriendo corredores humanitarios, y por eso
las muertes salían idénticas en cuatro de cinco estrategias: no era mala
calibración, era que el reloj tenía **una sola entrada**. Ahora tiene tres:

    1 · abrir un corredor que sirva a esa región
    2 · escoltar un carrotanque o una misión médica hasta allá
    3 · que Minas asigne el combustible por prioridad de uso

ADVERTENCIA DE CALIBRACIÓN: es la variable más fácil de convertir en chantaje
moral. Si estalla en el turno 2 pase lo que pase, la sala aprende que el diseño
la castigaba, no que decidió mal. **Debe existir SIEMPRE al menos una vía viable
de atenderla**, y esa vía debe costar algo que a alguien le duela.
"""

from __future__ import annotations

from src.engine import parameters as P
from src.engine.state import Estado, Region


def _pesos(orden: list[str]) -> dict[str, float]:
    """El primero de la lista pesa el doble que el tercero. No hay orden correcto."""
    total = sum(range(1, len(orden) + 1))
    return {uso: (len(orden) - i) / total for i, uso in enumerate(orden)}


def _ingreso_por_corredores(estado: Estado, region: Region, clase: str) -> float:
    """
    Cuánto entra a una región, por día, por los corredores que la sirven.

    Solo cuentan los corredores que TOCAN la región: uno abierto en Alto Verde no
    abastece a Puerto Espejo. Sin este filtro, abrir cualquier corredor salvaba a
    todo el país y priorizar dejaba de tener sentido.
    """
    total = 0.0
    for c in estado.corredores_que_sirven(region.region_id, clase):
        total += c.caudal_efectivo(estado.nodos) * P.CAPACIDAD_CORREDOR_DIARIA
    return total


def step(estado: Estado, horas: float) -> dict:
    """
    Avanza el reloj de abastecimiento. Devuelve las regiones en crisis.

    Suma cero: cada asignación que Minas defiende se la está negando a alguien
    más en la misma sala.
    """
    dias = horas / 24.0
    criticas: list[str] = []
    muertes_nuevas = 0

    for region in estado.regiones.values():
        # El pánico es endógeno: si el calendario se difunde, el consumo sube y
        # el agotamiento llega antes. Entregar el reloj cambia el reloj.
        consumo = P.CONSUMO_BASE_DIARIO * (1.0 + region.panico) * dias

        ing_comb = _ingreso_por_corredores(estado, region, "combustible") * dias
        ing_alim = _ingreso_por_corredores(estado, region, "alimentario") * dias
        ing_oxi = _ingreso_por_corredores(estado, region, "humanitario") * dias

        region.dias_autonomia_combustible += ing_comb - consumo
        region.dias_autonomia_alimentos += ing_alim - consumo
        region.dias_autonomia_oxigeno += ing_oxi - consumo

        # El criterio de prioridad de Minas, si está fijado, se aplica CADA PASO.
        # Es la segunda entrada del reloj: la única que no depende de abrir un
        # corredor. Y es suma cero — lo que entra a misión médica sale del
        # transporte de alimentos.
        if estado.prioridad_combustible:
            pesos = _pesos(estado.prioridad_combustible)
            region.dias_autonomia_oxigeno += (
                pesos["mision_medica"] * P.EFECTO_ASIGNACION_COMBUSTIBLE * dias
            )
            region.dias_autonomia_alimentos += (
                pesos["transporte_alimentos"] * P.EFECTO_ASIGNACION_COMBUSTIBLE * dias
            )

        # El oxígeno depende del combustible: sin diésel no hay plantas de
        # emergencia ni cadena de frío. Es el eslabón que hace sistémica la crisis.
        if region.dias_autonomia_combustible < P.UMBRAL_AUTONOMIA_DEGRADA_FUERZA:
            region.dias_autonomia_oxigeno -= 0.25 * dias

        for attr in ("dias_autonomia_combustible", "dias_autonomia_alimentos"):
            setattr(region, attr, max(-1.0, getattr(region, attr)))

        # EL TECHO, que no existía. Sin él los contadores solo tenían suelo: una
        # región con dos corredores abiertos ganaba cuatro días netos por
        # jornada y terminaba el ejercicio con veintiún días de oxígeno, con el
        # semáforo clavado en verde y el reloj de la crisis apagado. El tope es
        # el estado inicial (`Region.techo_autonomia`): abrir corredores sirve
        # para dejar de perder y recuperar lo perdido, no para acumular reserva
        # estratégica en cinco días de paro.
        for clase, attr in (("combustible", "dias_autonomia_combustible"),
                            ("alimentos", "dias_autonomia_alimentos"),
                            ("oxigeno", "dias_autonomia_oxigeno")):
            techo = region.techo_autonomia.get(clase)
            if techo is not None:
                setattr(region, attr, min(techo, getattr(region, attr)))

        # Por debajo de cero, el oxígeno no produce escasez: produce un contador
        # que ninguna deliberación discute.
        if region.dias_autonomia_oxigeno < 0:
            horas_sin = min(horas, abs(region.dias_autonomia_oxigeno) * 24.0)
            # La presión hospitalaria modula el contador: una red al 92 % de
            # ocupación no absorbe lo mismo que una al 74 %. Es el dato del
            # escenario que hasta la v2 se cargaba y nadie leía.
            presion = (region.presion_hospitalaria
                       if P.PRESION_HOSPITALARIA_MODULA_MUERTES else 1.0)
            muertes = int(
                P.PACIENTES_EN_SOPORTE_POR_REGION
                * horas_sin
                * P.TASA_MUERTE_POR_HORA_SIN_OXIGENO
                * presion
            )
            if muertes > 0:
                region.muertes_evitables += muertes
                muertes_nuevas += muertes
                estado.eventos_turno.append({
                    "tipo": "muertes_evitables",
                    "region": region.region_id,
                    "n": muertes,
                })
            region.dias_autonomia_oxigeno = max(-2.0, region.dias_autonomia_oxigeno)

        if region.dias_autonomia_oxigeno < 1.0 or region.dias_autonomia_combustible < 1.0:
            criticas.append(region.region_id)

        if region.dias_autonomia_alimentos < 3.0:
            region.indice_precios += 0.06 * dias

    return {"regiones_criticas": criticas, "muertes_nuevas": muertes_nuevas}


def difundir_calendario(estado: Estado) -> dict:
    """
    Entregar a la mesa el calendario de agotamiento como fecha límite.

    Convierte la deliberación en un plazo — y acelera aquello que mide. La ficha
    del rol lo advierte: entrega a quienes sostienen los cierres la medida exacta
    de su palanca.

    **Decirlo en voz alta es gratis. Entregarlo formalmente cuesta.** La sala se
    entera igual en los dos casos; la diferencia es que esto se filtra.
    """
    for region in estado.regiones.values():
        region.panico = min(1.0, region.panico + P.FACTOR_PANICO_POR_DIFUSION)
    estado.eventos_turno.append({"tipo": "calendario_difundido"})
    return {
        "calendario": {
            r.nombre: {
                "combustible": round(r.dias_autonomia_combustible, 2),
                "oxigeno": round(r.dias_autonomia_oxigeno, 2),
                "alimentos": round(r.dias_autonomia_alimentos, 2),
            }
            for r in estado.regiones.values()
        },
        "efecto": "pánico +35 %: el consumo se acelera en todas las regiones",
    }


def asignar_combustible(estado: Estado, orden: list[str]) -> dict:
    """
    Minas asigna por prioridad de uso: misión médica, fuerza pública, transporte
    de alimentos, consumo general.

    **No hay orden correcto.** Hay un orden que se defiende ante siete personas
    que pierden algo — y ahí está el punto: cada galón que se asigna a la misión
    médica se le quita al transporte de alimentos, y las dos cosas tienen quien
    las reclame en esta mesa.

    Es la segunda entrada del reloj, y hasta la v2 estaba escrita y desconectada:
    ningún rol podía invocarla.
    """
    validos = set(P.ORDEN_PRIORIDAD_COMBUSTIBLE)
    if set(orden) != validos:
        return {"ok": False, "motivo": (
            f"La asignación debe ordenar exactamente estos cuatro usos: "
            f"{', '.join(sorted(validos))}."
        )}

    pesos = _pesos(orden)
    # Queda como criterio PERMANENTE: `supply.step()` lo aplica en cada paso
    # mientras esté puesto. Fijarlo una vez evita pelearlo cada turno.
    estado.prioridad_combustible = list(orden)

    # Si la fuerza pública queda al final, la escolta se degrada: los escuadrones
    # no tienen con qué desplazarse. La crisis logística se vuelve de contención.
    degrada_fuerza = orden.index("fuerza_publica") >= 2
    if degrada_fuerza:
        estado.eventos_turno.append({"tipo": "escolta_degradada"})

    estado.eventos_turno.append({"tipo": "combustible_asignado", "orden": orden})
    return {
        "ok": True,
        "orden": orden,
        "pesos": {k: round(v, 2) for k, v in pesos.items()},
        "escolta_degradada": degrada_fuerza,
    }


def reponer_por_escolta(estado: Estado, regiones: list[str], cantidad: float,
                        clase: str) -> None:
    """
    Lo que entrega una escolta que llegó. Es la tercera entrada del reloj, y la
    única que la Policía controla.
    """
    for rid in regiones:
        r = estado.regiones.get(rid)
        if r is None:
            continue
        if clase == "humanitario":
            r.dias_autonomia_oxigeno += cantidad
        elif clase == "combustible":
            r.dias_autonomia_combustible += cantidad
        elif clase == "alimentario":
            r.dias_autonomia_alimentos += cantidad
