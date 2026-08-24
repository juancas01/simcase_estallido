"""
loader.py — Construye el estado heredado (t=0) desde datos.

Regla de oro heredada de Macondo: si un dato aparece a la vez en un archivo y en
el prompt de un modelo, se desincronizará. Siempre. Todo lo que define el caso
vive en `data/`, y el catálogo que ve el modelo se GENERA desde aquí.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.engine import parameters as P
from src.engine.state import (
    Estado, Nodo, Corredor, Region, Unidad, Composicion, Reservas, Banderas,
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
            masa_presente=n.get("masa_presente", 200),
            apoyo_local=n.get("apoyo_local", 0.7),
            control_voceria=n.get("control_voceria", 0.5),
            proximidad_infra_critica=n.get("proximidad_infra_critica", False),
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

    estado.unidades = _construir_fuerza()
    estado.reservas = Reservas(**P.RESERVAS_T0)
    estado.banderas = Banderas()          # ningún mitigador activo en t=0
    estado.intensidad_nacional = P.INTENSIDAD_NACIONAL_T0
    estado.posicion_gremios = "fuera"     # el ultimátum de H3 los activa, no el umbral

    _verificar_invariantes(estado)
    return estado


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
    """Comprobaciones que deben cumplirse SIEMPRE al cargar."""
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
    # castiga. Se detectó exactamente así en la primera corrida —Buenaventura no
    # tenía ninguno y las cuatro estrategias daban las mismas 147 muertes—, y por
    # eso la comprobación vive aquí y falla ruidosamente.
    for r in estado.regiones.values():
        tiene = any(
            "humanitario" in c.clases_prioridad
            and any(estado.nodos[n].region_id == r.region_id
                    for n in c.nodos if n in estado.nodos)
            for c in estado.corredores.values()
        )
        if not tiene:
            raise ValueError(
                f"La región {r.nombre} no tiene ningún corredor de clase "
                f"'humanitario'. Sus muertes evitables serían inevitables por "
                f"construcción. Ver §4.5 de la propuesta."
            )


def catalogo_para_agente(estado: Estado) -> dict:
    """
    El catálogo que ve el modelo se GENERA desde el estado, no se escribe a mano
    en el prompt. En Macondo, un paquete que faltaba en el prompt escrito a mano
    fue invisible para el agente durante todo un ejercicio.
    """
    return {
        "nodos": [
            {"id": n.nodo_id, "nombre": n.nombre, "region": estado.regiones[n.region_id].nombre,
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
    }
