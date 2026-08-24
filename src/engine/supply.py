"""
supply.py — Abastecimiento y el reloj de la crisis (§4.5).

Los días de autonomía son el driver del caso y, a diferencia de la lluvia de
Macondo, son ENDÓGENOS: bajan solos y solo suben si alguien abre un corredor.

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
aquí y no en un módulo sanitario: no modela salud, modela el alcance de una
decisión logística.

ADVERTENCIA DE CALIBRACIÓN: es la variable más fácil de convertir en chantaje
moral. Si estalla en el turno 2 pase lo que pase, la sala aprende que el diseño
la castigaba, no que decidió mal. Debe existir SIEMPRE al menos una vía viable
de atenderla, y esa vía debe costar algo que a alguien le duela.
"""

from __future__ import annotations

from src.engine import parameters as P
from src.engine.state import Estado, Region


def _ingreso_por_corredores(estado: Estado, region: Region, clase: str) -> float:
    """
    Cuánto entra a una región, por día, por los corredores que la sirven.

    Solo cuentan los corredores que tocan la región: un corredor abierto en
    Nariño no abastece a Buenaventura. Sin este filtro, abrir cualquier corredor
    salvaba a todo el país y la priorización dejaba de tener sentido.
    """
    total = 0.0
    for c in estado.corredores.values():
        if clase not in c.clases_prioridad:
            continue
        toca_region = any(
            estado.nodos[n].region_id == region.region_id
            for n in c.nodos if n in estado.nodos
        )
        if not toca_region:
            continue
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
        # El pánico es endógeno: si el calendario se difunde, el consumo sube
        # y el agotamiento llega antes. Entregar el reloj cambia el reloj.
        consumo = P.CONSUMO_BASE_DIARIO * (1.0 + region.panico) * dias

        ing_comb = _ingreso_por_corredores(estado, region, "combustible") * dias
        ing_alim = _ingreso_por_corredores(estado, region, "alimentario") * dias
        ing_oxi = _ingreso_por_corredores(estado, region, "humanitario") * dias

        region.dias_autonomia_combustible += ing_comb - consumo
        region.dias_autonomia_alimentos += ing_alim - consumo
        region.dias_autonomia_oxigeno += ing_oxi - consumo

        # El oxígeno depende del combustible: sin diésel no hay plantas de
        # emergencia ni cadena de frío. Es el eslabón que hace sistémica la crisis.
        if region.dias_autonomia_combustible < P.UMBRAL_AUTONOMIA_DEGRADA_FUERZA:
            region.dias_autonomia_oxigeno -= 0.25 * dias

        for attr in ("dias_autonomia_combustible", "dias_autonomia_alimentos"):
            setattr(region, attr, max(-1.0, getattr(region, attr)))

        # Por debajo de cero, el oxígeno no produce escasez: produce un contador
        # que ninguna deliberación discute.
        if region.dias_autonomia_oxigeno < 0:
            horas_sin = min(horas, abs(region.dias_autonomia_oxigeno) * 24.0)
            muertes = int(
                P.PACIENTES_EN_SOPORTE_POR_REGION
                * horas_sin
                * P.TASA_MUERTE_POR_HORA_SIN_OXIGENO
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

        # Precios: suben con la escasez de alimentos
        if region.dias_autonomia_alimentos < 3.0:
            region.indice_precios += 0.06 * dias

    return {"regiones_criticas": criticas, "muertes_nuevas": muertes_nuevas}


def difundir_calendario(estado: Estado) -> dict:
    """
    Acción A4 del Ministro de Minas: entregar a la mesa el calendario de
    agotamiento como fecha límite de la decisión.

    Convierte la deliberación en un plazo — y acelera aquello que mide. La ficha
    del rol lo advierte: entrega a quienes sostienen los cierres la medida exacta
    de su palanca.
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
    Acción A2 de Minas: asignar por prioridad de uso.

    No hay orden correcto; hay un orden que se defiende ante siete personas que
    pierden algo. El motor no juzga la elección: aplica sus consecuencias.
    """
    validos = set(P.ORDEN_PRIORIDAD_COMBUSTIBLE)
    if set(orden) != validos:
        return {"ok": False, "motivo": f"la asignación debe ordenar exactamente {sorted(validos)}"}

    pesos = {uso: (len(orden) - i) / sum(range(1, len(orden) + 1))
             for i, uso in enumerate(orden)}

    for region in estado.regiones.values():
        region.dias_autonomia_oxigeno += pesos["mision_medica"] * 0.8
        region.dias_autonomia_alimentos += pesos["transporte_alimentos"] * 0.8

    # Si la fuerza pública queda al final, la escolta se degrada
    degrada_fuerza = orden.index("fuerza_publica") >= 2
    return {
        "ok": True,
        "orden": orden,
        "pesos": {k: round(v, 2) for k, v in pesos.items()},
        "escolta_degradada": degrada_fuerza,
    }
