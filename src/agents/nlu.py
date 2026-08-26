"""
nlu.py — CAPA 4 · el canal de órdenes en lenguaje natural.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

Alguien escribe en la consola *«concentrar el ESMAD en el anillo hospitalario,
con dupla de la Defensoría, responsable el Ministro de Defensa»* y el sistema
devuelve un **plan tipado** —acciones, requisitos que faltan, banda de riesgo—
para que **la sala lo lea junta antes de ejecutarlo**.

Ese momento no es un trámite: la sala oye su propia decisión reformulada, con su
riesgo, y con frecuencia la cambia.

EL CAUCE — NUEVE PASOS, Y SOLO EL PRIMERO USA EL MODELO
-------------------------------------------------------
    1 · NLU          tool calling con herramientas tipadas   ← 1 llamada
    2 · RESOLUTOR    entidades, determinista
    3 · EXPANSOR     llamadas → acciones atómicas, con tope
    4 · VALIDADOR    dry-run por acción, SIN break
    5 · PREVISUALIZAR si falta un dato: el plan entero espera
    6 · EJECUTAR
    7 · REPORTAR     plantilla determinista, DESPUÉS de ejecutar
    8 · SUGERIR      solo si hubo fallo
    9 · CONSULTAR    rama de solo lectura

LOS OCHO MODOS DE FALLA QUE ESTO EVITA
--------------------------------------
    F1 la confirmación se redacta antes de ejecutar → reporte determinista después
    F2 una parte incompleta mata la orden entera    → validación por acción, sin break
    F3 resolución que acierta mal en silencio       → resolutor de 4 estados
    F4 explosión combinatoria origen × destino      → acción atómica + tope
    F5 el modelo fuerza la acción más parecida      → herramientas tipadas
    F6 el historial contamina el turno siguiente    → plan en sesión, elección tipada
    F7 clasificador orden/consulta irreversible     → consultar es una herramienta más
    F8 el canal de consultas sin fuente de verdad   → hoja de datos desde el motor

**Si no hay llave, el paso 1 lo hace un intérprete determinista de reserva.** El
resto del cauce es idéntico. Ver `src/agents/config.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from src.engine import force
from src.engine.state import Estado
from src.agents import herramientas, resolver
from src.agents.config import cliente, config

TOPE_ACCIONES = 12


@dataclass
class AccionPlan:
    herramienta: str
    rol: str
    descripcion: str
    argumentos: dict = field(default_factory=dict)
    entidades: list[resolver.Resolucion] = field(default_factory=list)
    estado: str = "lista"        # lista | falta_dato | ambigua | no_viable
    motivo: str | None = None
    requisitos_faltantes: list[str] = field(default_factory=list)
    habilitada_por: list[str] = field(default_factory=list)
    riesgo: dict | None = None

    def a_dict(self) -> dict:
        return {
            "herramienta": self.herramienta,
            "rol": self.rol,
            "descripcion": self.descripcion,
            "argumentos": self.argumentos,
            "entidades": [
                {"crudo": e.crudo, "estado": e.estado, "id": e.entidad_id,
                 "nombre": e.nombre, "candidatos": e.candidatos, "eco": e.eco()}
                for e in self.entidades
            ],
            "estado": self.estado,
            "motivo": self.motivo,
            "requisitos_faltantes": self.requisitos_faltantes,
            "habilitada_por": self.habilitada_por,
            "riesgo": self.riesgo,
        }


@dataclass
class Plan:
    plan_id: str
    texto_original: str
    acciones: list[AccionPlan] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    interpretado_por: str = "determinista"

    @property
    def necesita_confirmacion(self) -> bool:
        return any(a.estado in ("falta_dato", "ambigua") for a in self.acciones)

    def a_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "texto_original": self.texto_original,
            "interpretado_por": self.interpretado_por,
            "acciones": [a.a_dict() for a in self.acciones],
            "avisos": self.avisos,
            "necesita_confirmacion": self.necesita_confirmacion,
            "lectura_en_voz_alta": self.lectura(),
        }

    def lectura(self) -> str:
        """
        Lo que la sala lee junta antes de ejecutar. **Determinista, siempre.**

        Nunca lo escribe el modelo: si lo escribiera, podría afirmar un éxito que
        todavía no ocurrió — que es el primero de los ocho modos de falla.
        """
        if not self.acciones:
            return ("No se reconoció ninguna orden en ese texto. Puede pedir una "
                    "operación, una mesa de concertación, una escolta, duplas de "
                    "verificación o una acción constitutiva.")
        lineas = [f"Entiendo que se ordena lo siguiente ({len(self.acciones)}):"]
        for i, a in enumerate(self.acciones, 1):
            marca = {"lista": "·", "falta_dato": "?", "ambigua": "?",
                     "no_viable": "×"}[a.estado]
            lineas.append(f"  {marca} {i}. {a.descripcion}")
            for e in a.entidades:
                if e.estado != "ok":
                    lineas.append(f"       {e.eco()}")
            if a.riesgo:
                r = a.riesgo
                faltan = ", ".join(r["mitigadores_ausentes"]) or "ninguno"
                lineas.append(
                    f"       Riesgo de incidente: {r['banda'].upper()}, "
                    f"{r['p_incidente']:.0%}. Mitigadores ausentes: {faltan}."
                )
            ecos = {e.eco() for e in a.entidades if e.estado != "ok"}
            if a.motivo and a.motivo not in ecos:
                lineas.append(f"       {a.motivo}")
            if a.habilitada_por:
                lineas.append(f"       Lo habilita: {', '.join(a.habilitada_por)}.")
        lineas.append("¿Confirman?")
        return "\n".join(lineas)


# ===========================================================================
# 1 · NLU
# ===========================================================================

SISTEMA = """Eres el canal de órdenes de un simulador de crisis. Tu ÚNICA función
es traducir a llamadas de herramienta lo que un Puesto de Mando acaba de decidir
en voz alta.

REGLAS QUE NO PUEDES ROMPER:
- NO decides nada. NO validas. NO estimas riesgos. NO afirmas resultados.
- NO normalices los nombres de lugar: cópialos TAL CUAL los escribió la persona.
  Un sistema determinista los resuelve después, y es auditable.
- Si la orden no encaja en ninguna herramienta, no fuerces la más parecida:
  no llames a ninguna.
- Una orden puede contener varias acciones. Emite una llamada por cada una.
- Si la persona pregunta algo en vez de ordenar, usa `consultar`.

SOBRE QUÉ UNIDAD SE EMPLEA, y esto importa mucho:
`tipo_unidad` es SIEMPRE "esmad" salvo que el texto diga explícitamente
militares, ejército, tropa o asistencia militar. Que la orden venga del
Ministerio de Defensa NO significa que se empleen militares: el Ministerio
también ordena operaciones con ESMAD, y de hecho es lo normal. Emplear tropa
multiplica por cinco el riesgo y requiere una firma que puede no existir, así
que no se infiere: se dice o no se dice.

El texto viene de una deliberación real: es coloquial, incompleto y a veces
contradictorio. Traduce lo que se pidió, no lo que crees que deberían haber
pedido."""


def interpretar(estado: Estado, texto: str, plan_id: str) -> Plan:
    """Los nueve pasos. Solo el primero usa el modelo, y solo si hay llave."""
    plan = Plan(plan_id=plan_id, texto_original=texto)

    llamadas, quien = _traducir(estado, texto)
    plan.interpretado_por = quien

    if not llamadas:
        plan.avisos.append(
            "No se reconoció ninguna acción. Se puede pedir: operar un punto, "
            "abrir una mesa, escoltar un corredor, asignar duplas, o adoptar una "
            "acción constitutiva."
        )
        return plan

    # 3 · EXPANSOR, con tope de seguridad
    if len(llamadas) > TOPE_ACCIONES:
        plan.avisos.append(
            f"La orden expande a {len(llamadas)} acciones y el tope es "
            f"{TOPE_ACCIONES}. Se muestran las primeras; confirme o acote."
        )
        llamadas = llamadas[:TOPE_ACCIONES]

    # 4 · VALIDADOR — recorre TODAS. Prohibido `break` al primer problema: una
    #     orden compuesta no puede morir entera porque a una parte le falte un dato.
    for llamada in llamadas:
        plan.acciones.append(_a_accion_plan(estado, llamada))

    return plan


def _traducir(estado: Estado, texto: str) -> tuple[list[dict], str]:
    """
    Paso 1. Devuelve `(llamadas, quién_lo_hizo)`.

    Si no hay llave, si el SDK no está o si el proveedor tarda, cae al
    intérprete determinista de reserva **sin romper nada**.
    """
    c = cliente()
    if c is None:
        return herramientas.interpretar_sin_modelo(estado, texto), "determinista"

    cfg = config()
    try:
        respuesta = c.chat.completions.create(
            model=cfg.modelo_nlu,
            messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "system", "content":
                    "Catálogo del mundo (generado desde el estado, no escrito a "
                    "mano):\n" + json.dumps(herramientas.catalogo_compacto(estado),
                                            ensure_ascii=False)},
                {"role": "user", "content": texto},
            ],
            tools=herramientas.esquemas(),
            tool_choice="auto",
            parallel_tool_calls=True,
            timeout=cfg.timeout_nlu,
        )
    except Exception as exc:                                  # pragma: no cover
        # Un error del proveedor no puede dejar a ocho personas mirando la
        # pantalla. Se degrada y se dice que se degradó.
        return (herramientas.interpretar_sin_modelo(estado, texto),
                f"determinista (el modelo falló: {type(exc).__name__})")

    mensaje = respuesta.choices[0].message
    llamadas = []
    for tc in (mensaje.tool_calls or []):
        try:
            args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            # NUNCA parsear prosa a mano. Si el modelo no devolvió JSON válido,
            # esa llamada se descarta y las demás siguen.
            continue
        llamadas.append({"nombre": tc.function.name, "argumentos": args})

    if not llamadas:
        return [], f"{cfg.modelo_nlu} (no reconoció ninguna acción)"
    return llamadas, cfg.modelo_nlu


# ===========================================================================
# 2–4 · Resolutor, expansor y validador — todo determinista
# ===========================================================================

def _a_accion_plan(estado: Estado, llamada: dict) -> AccionPlan:
    nombre = llamada["nombre"]
    args = dict(llamada.get("argumentos") or {})
    spec = herramientas.HERRAMIENTAS.get(nombre)

    if spec is None:
        return AccionPlan(herramienta=nombre, rol="?",
                          descripcion=f"Herramienta desconocida: {nombre}",
                          estado="no_viable",
                          motivo="No existe esa acción en el repertorio.")

    # Normalizar enumeraciones ANTES de tocar el motor. El modelo dice
    # «militares» donde el motor espera «militar», y eso no puede reventar nada.
    args, avisos_enum = herramientas.normalizar_enums(args)

    ap = AccionPlan(herramienta=nombre, rol=spec["rol"],
                    descripcion=spec["descripcion"], argumentos=args)
    if avisos_enum:
        ap.estado = "falta_dato"
        ap.motivo = " ".join(avisos_enum)
        return ap

    # 2 · resolver las entidades que la herramienta declara
    for campo, tipo in spec.get("entidades", {}).items():
        crudo = args.get(campo)
        if not crudo:
            continue
        r = resolver.resolver(estado, str(crudo), tipo)
        ap.entidades.append(r)
        if r.estado == "ok":
            args[campo] = r.entidad_id
        elif r.estado == "selector":
            ids = resolver.expandir_selector(estado, r.selector or "")
            args[campo] = ids[0] if ids else None
            if not ids:
                ap.estado = "falta_dato"
                ap.motivo = f"El criterio «{r.selector}» no produjo ningún punto."
        elif r.estado == "ambiguo":
            ap.estado = "ambigua"
            ap.motivo = r.eco()
        else:
            ap.estado = "falta_dato"
            ap.motivo = r.eco()

    # Listas de entidades: cada elemento se resuelve por separado, y los que no
    # resuelven se informan en vez de descartarse en silencio.
    for campo, tipo in spec.get("entidades_lista", {}).items():
        crudos = args.get(campo) or []
        resueltos, perdidos = [], []
        for crudo in crudos:
            r = resolver.resolver(estado, str(crudo), tipo)
            ap.entidades.append(r)
            if r.estado == "ok":
                resueltos.append(r.entidad_id)
            elif r.estado == "selector":
                resueltos.extend(resolver.expandir_selector(estado, r.selector or ""))
            else:
                perdidos.append(str(crudo))
        args[campo] = resueltos
        if perdidos:
            ap.motivo = (f"No se resolvieron: {', '.join(perdidos)}. "
                         f"El resto sigue en el plan.")

    if ap.estado != "lista":
        return ap

    # 4 · dry-run contra el motor. `validar()` NO muta nada.
    try:
        accion = spec["construir"](args)
    except Exception as exc:
        ap.estado = "falta_dato"
        ap.motivo = f"Faltan datos para armar la acción: {exc}"
        return ap

    v = accion.validar(estado)
    ap.requisitos_faltantes = list(v.requisitos_faltantes)
    ap.habilitada_por = list(v.habilitada_por)
    if not v.ok:
        ap.estado = "no_viable"
        ap.motivo = v.motivo
    elif v.parcial:
        ap.motivo = v.motivo

    # La banda de riesgo, si la acción la tiene. Se calcula en el motor, no en el
    # modelo, y se muestra ANTES de decidir.
    nodo_id = args.get("nodo_id")
    if spec.get("muestra_riesgo") and nodo_id in estado.nodos:
        ev = force.evaluar_riesgo(
            estado, estado.nodos[nodo_id],
            args.get("tipo_unidad", "esmad"),
            dupla_presente=bool(args.get("dupla_presente")),
            concertado_con_alcaldia=bool(args.get("concertado_con_alcaldia")),
        )
        ap.riesgo = {
            "banda": ev.banda,
            "p_incidente": round(ev.p_incidente, 3),
            "mitigadores_ausentes": ev.mitigadores_ausentes,
            "mitigadores_activos": ev.mitigadores_activos,
        }
    return ap


# ===========================================================================
# 9 · Consultar — hechos, no párrafos
# ===========================================================================

def hoja_de_datos(estado: Estado, tema: str) -> dict:
    """
    Un canal de consultas que entrega al modelo un párrafo con totales agregados
    lo obliga a inventar en cuanto le preguntan por algo concreto.

    **Regla: se extraen los hechos del motor y se pasan como datos
    estructurados.** Y se compone POR TEMA: un modelo al que se le da de más
    responde de más.

    Nunca se usa `null`: es ambiguo entre «no lo sé» y «no hay», y el modelo lo
    lee como laguna. Se pone un texto explícito.
    """
    if tema == "fuerza":
        return {
            "ambito": "capacidad de fuerza, nacional",
            "esmad_total": len(estado.unidades_por_tipo("esmad")),
            "esmad_sin_comprometer": len(estado.esmad_en_reserva()),
            "fatiga_media": round(estado.fatiga_media("esmad"), 2),
            "instalaciones_bajo_custodia": len(estado.instalaciones_criticas) or
                                           "ninguna declarada",
            "asistencia_militar": (
                "firmada con límites" if estado.banderas.asistencia_militar_delimitada
                else "firmada sin límites" if estado.banderas.asistencia_militar_firmada
                else "no firmada"
            ),
        }
    if tema == "corredores":
        return {
            "ambito": "los cinco corredores",
            "corredores": [
                {"nombre": c.nombre,
                 "flujo": round(c.caudal_efectivo(estado.nodos), 2),
                 "bloqueado_en": (estado.nodos[b].nombre
                                  if (b := c.punto_que_bloquea(estado.nodos))
                                  else "ninguno: pasa"),
                 "poblacion": c.poblacion_aguas_abajo,
                 "clases": sorted(c.clases_prioridad)}
                for c in estado.corredores.values()
            ],
        }
    if tema == "abastecimiento":
        return {
            "ambito": "las cuatro regiones",
            "aviso": "los días exactos son dato del Ministro de Minas",
            "regiones": [
                {"nombre": r.nombre, "semaforo": r.semaforo,
                 "muertes_evitables": r.muertes_evitables}
                for r in estado.regiones.values()
            ],
        }
    if tema == "mesa":
        return {
            "ambito": "el estado de la mesa",
            "reservas": {
                "legitimidad": round(estado.reservas.legitimidad, 1),
                "credibilidad_mesa": round(estado.reservas.credibilidad_mesa, 1),
                "respaldo_internacional": round(estado.reservas.respaldo_internacional, 1),
                "cohesion_mesa": round(estado.reservas.cohesion_mesa, 1),
            },
            "comite_disponible": estado.comite_disponible,
            "posicion_gremios": estado.posicion_gremios,
            "banderas_activas": [k for k, v in vars(estado.banderas).items()
                                 if isinstance(v, bool) and v] or ["ninguna"],
        }
    return {"ambito": tema, "error": (
        "Tema desconocido. Los que hay: fuerza, corredores, abastecimiento, mesa."
    )}
