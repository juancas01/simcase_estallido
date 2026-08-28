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
import re
from dataclasses import dataclass, field

from src.engine import force
from src.engine.state import Estado
from src.agents import herramientas, resolver
from src.agents.config import cliente, config

TOPE_ACCIONES = 12

# Cómo se dice cada argumento en voz alta. Solo los que la sala puede contrastar
# con lo que acaba de decir: si pidió militares y oye «con ESMAD», corrige.
#
# Los booleanos solo se dicen cuando son ciertos: «sin dupla» en cada línea sería
# ruido, y lo que hace falta señalar —los mitigadores que faltan— ya lo dice la
# banda de riesgo con su lista.
ARGUMENTOS_EN_CLARO: dict = {
    "dupla_presente": lambda v: "con dupla de la Defensoría" if v else "",
    "concertado_con_alcaldia": lambda v: "concertado con la Alcaldía" if v else "",
    "de_noche": lambda v: "de noche" if v else "",
    "responsable_nominado": lambda v: f"responsable: {v}" if v else "",
    "clase_carga": lambda v: f"carga: {v}",
    "modo": lambda v: f"modo: {v}",
    "n_escuadrones": lambda v: f"{v} escuadrón(es)",
    "n_unidades": lambda v: f"{v} unidad(es)",
    # También en los dos sentidos, y por la misma razón que `con_alcaldia`: la
    # firma sin delimitar cuesta −22 de respaldo internacional y −15 de
    # legitimidad frente a −8 y −5, entrega el encuadre de represión y dispara
    # «militares en control de multitudes». Es el valor por defecto más caro del
    # repertorio, y era el que no se decía.
    "delimitada": lambda v: ("con límites escritos" if v else
                             "SIN límites: sin territorio, plazo, reglas ni "
                             "criterio de terminación"),
    "tema": lambda v: f"tema: {v}",
    # Los cinco que faltaban. Cada uno cambia lo que el motor hace y ninguno se
    # decía: la sala confirmaba una mesa «con la Alcaldía» que nadie había
    # pedido, o unas líneas rojas con un margen que nadie había fijado.
    #
    # `con_alcaldia` se dice en los DOS sentidos —a diferencia del resto de
    # booleanos— porque en el epicentro su ausencia es lo que hace inviable la
    # acción, y eso la sala tiene que oírlo antes de confirmar, no después.
    "con_alcaldia": lambda v: ("con la Alcaldía" if v else
                               "SIN la Alcaldía"),
    "ofrece_compensacion": lambda v: ("ofreciendo compensación" if v else
                                      "sin ofrecer compensación"),
    "margen": lambda v: f"margen negociable: {v}",
    "orden": lambda v: f"orden de prioridad: {' > '.join(v)}" if v else "",
    # Los cinco de las ocho acciones que hasta ahora no se podían pedir. Los
    # tres booleanos se leen EN LOS DOS SENTIDOS, porque en las tres el valor
    # por defecto es el que la sala no dijo y tiene que poder corregir.
    "concede_prioridad": lambda v: ("concediendo prioridad de fuerza al "
                                    "epicentro" if v else
                                    "SIN conceder prioridad de fuerza"),
    "acompana": lambda v: {"mesa": "acompañando la mesa",
                           "operacion": "acompañando la operación"}.get(
                               str(v), "sin acompañar la mesa ni la operación"),
    "disputa_cifra": lambda v: ("disputando la cifra nacional" if v else
                                "sin disputar la cifra nacional"),
    "declara_solidez": lambda v: ("declarando qué casos no se sostienen ante "
                                  "un juez" if v else
                                  "SIN declarar qué casos no se sostienen"),
}

UNIDADES_EN_CLARO = {"esmad": "ESMAD", "policia": "policía", "militar": "militares"}

# Cómo se llama cada campo cuando hay que pedirlo. «No se entendió el punto de
# cierre» sirve; «falta nodo_id» no.
# Cómo se lee cada tema en voz alta. «Consulta del estado, sin ordenar nada ·
# fuerza» es correcto y no lo dice nadie así.
TEMA_EN_CLARO = {
    "fuerza": "la capacidad de fuerza disponible",
    "corredores": "el estado de los corredores",
    "abastecimiento": "el abastecimiento de las cuatro regiones",
    "mesa": "el estado de la mesa y sus reservas",
}

_NOMBRE_CAMPO = {
    "nodo_id": "sobre qué punto de cierre",
    "corredor_id": "por qué corredor",
    "region_id": "de qué región",
    "puntos": "qué puntos verificar",
    "tema": "sobre qué se pregunta",
}


def _en_claro_argumento(campo: str, valor) -> str:
    if campo in ("nodo_id", "corredor_id", "region_id", "puntos", "denuncias",
                 "instalaciones"):
        return ""            # las entidades ya salen resueltas, con su nombre
    if campo == "tipo_unidad":
        return f"con {UNIDADES_EN_CLARO.get(str(valor), valor)}"
    fn = ARGUMENTOS_EN_CLARO.get(campo)
    if fn is None or valor in (None, "", [], {}):
        return ""
    return fn(valor)

# Herramientas que NUNCA llegan al motor. Se calcula del repertorio para que no
# haya que acordarse de mantener dos listas.
SOLO_LECTURA = frozenset(
    n for n, e in herramientas.HERRAMIENTAS.items() if e.get("solo_lectura"))


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

    # Lo que el canal QUITÓ de la interpretación, y por qué. Nunca lo que
    # añadió: añadir sería el canal concediendo. Se lee en voz alta con el resto.
    correcciones: list[str] = field(default_factory=list)

    # La hoja de datos, cuando la acción es una CONSULTA y no una orden. Se
    # extrae del motor y viaja con el plan para que se lea en la misma pantalla.
    datos: dict | None = None

    def en_claro(self) -> str:
        """
        Sobre qué actúa y con qué, en una línea, para leerlo en voz alta.

        Solo argumentos que la sala pueda contrastar con lo que dijo. Nada de
        identificadores sueltos: `N003` no le suena a nadie, «Puente Amarillo»
        sí — pero se dan los dos, porque el eco con identificador es lo que hace
        auditable la resolución.
        """
        resueltas = [e for e in self.entidades if e.estado == "ok"]
        if len(resueltas) > 1:
            # UNA CUENTA, y no tres «Sobre:» seguidos. Si la sala nombró tres
            # puntos y oye dos, la resta la hace ella sola — y ese es el único
            # aviso posible cuando el tercero ni siquiera se reconoció como
            # nombre, que es lo que pasa en la rama sin modelo.
            partes = [f"Sobre {len(resueltas)}: " + ", ".join(
                f"{e.nombre} ({e.entidad_id})" for e in resueltas)]
        else:
            partes = [f"Sobre: {e.nombre} ({e.entidad_id})" for e in resueltas]
        for campo, valor in self.argumentos.items():
            trozo = _en_claro_argumento(campo, valor)
            if trozo:
                partes.append(trozo)
        return " · ".join(partes)

    def a_dict(self) -> dict:
        return {
            "herramienta": self.herramienta,
            "rol": self.rol,
            "descripcion": self.descripcion,
            "argumentos": self.argumentos,
            "entidades": [
                {"crudo": e.crudo, "estado": e.estado, "id": e.entidad_id,
                 "nombre": e.nombre, "candidatos": e.candidatos, "eco": e.eco(),
                 "campo": e.campo}
                for e in self.entidades
            ],
            "estado": self.estado,
            "motivo": self.motivo,
            "requisitos_faltantes": self.requisitos_faltantes,
            "habilitada_por": self.habilitada_por,
            "correcciones": self.correcciones,
            "riesgo": self.riesgo,
            "en_claro": self.en_claro(),
            "datos": self.datos,
            "solo_lectura": self.herramienta in SOLO_LECTURA,
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
        ordenes = [a for a in self.acciones if a.herramienta not in SOLO_LECTURA]
        consultas = [a for a in self.acciones if a.herramienta in SOLO_LECTURA]

        if not self.acciones:
            # El diagnóstico ya viene en los avisos y es específico: no se
            # repite aquí una frase genérica que lo tape.
            return "\n".join(self.avisos) or (
                "No se reconoció ninguna orden en ese texto.")

        lineas = []
        for a in consultas:
            lineas.append(
                f"Se pregunta por "
                f"{TEMA_EN_CLARO.get(a.argumentos.get('tema', ''), 'el estado')}. "
                f"La respuesta sale del motor y no se ejecuta nada.")
        if consultas and not ordenes:
            lineas.append("No hay ninguna orden que ejecutar en ese texto.")
            return "\n".join(lineas)
        if consultas:
            lineas.append("")

        lineas.append(f"Entiendo que se ordena lo siguiente ({len(ordenes)}):")
        for i, a in enumerate(ordenes, 1):
            marca = {"lista": "·", "falta_dato": "?", "ambigua": "?",
                     "no_viable": "×"}[a.estado]
            # DE QUIÉN ES LA ACCIÓN. Sin esto, «instalar mesa con voceros»
            # —del Alcalde— y «mesa local de concertación» —del Interior— se
            # leían con la misma frase, y la sala no podía oír que la palanca
            # había cambiado de dueño. En un ejercicio cuyo objeto es quién
            # tiene qué palanca, eso es el dato, no un adorno.
            lineas.append(f"  {marca} {i}. [{a.rol}] {a.descripcion}")
            # SOBRE QUÉ y CON QUÉ. Sin esta línea la sala confirmaba «operación
            # de desbloqueo sobre un punto de cierre» sin oír sobre cuál — y el
            # paso 5 existe justamente para que oiga lo que va a ordenar.
            detalle = a.en_claro()
            if detalle:
                lineas.append(f"       {detalle}")
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
            for c in a.correcciones:
                lineas.append(f"       ! {c}")
            ecos = {e.eco() for e in a.entidades if e.estado != "ok"}
            if a.motivo and a.motivo not in ecos:
                lineas.append(f"       {a.motivo}")
            if a.habilitada_por:
                lineas.append(f"       Lo habilita: {', '.join(a.habilitada_por)}.")
        for av in self.avisos:
            lineas.append(f"  ! {av}")
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
- UN LUGAR AMBIGUO O DESCONOCIDO NO ES MOTIVO PARA NO LLAMAR. Si la acción está
  clara y el sitio no —«operen el puente», habiendo tres puentes—, llama igual a
  la herramienta y copia el texto del sitio tal cual. El sistema determinista
  repregunta después con la lista de candidatos, que es la respuesta correcta.
  Si en cambio no llamas a nada, la sala recibe «esa acción no existe», que es
  falso y la manda a corregir donde no estaba el problema.
- Lo único que justifica no llamar a ninguna herramienta es que la ACCIÓN pedida
  no exista en el repertorio. Y entonces no fuerces la más parecida.
- Una orden puede contener varias acciones. Emite una llamada por cada una.
- Si la persona pregunta algo en vez de ordenar, usa `consultar`.

SOBRE QUÉ UNIDAD SE EMPLEA, y esto importa mucho:
`tipo_unidad` es SIEMPRE "esmad" salvo que el texto diga explícitamente
militares, ejército, tropa o asistencia militar. Que la orden venga del
Ministerio de Defensa NO significa que se empleen militares: el Ministerio
también ordena operaciones con ESMAD, y de hecho es lo normal. Emplear tropa
multiplica por cinco el riesgo y requiere una firma que puede no existir, así
que no se infiere: se dice o no se dice.

LO QUE CONCEDE ALGO NO SE INFIERE NUNCA. `con_alcaldia`,
`concertado_con_alcaldia`, `dupla_presente` y `delimitada` no describen la orden:
conceden un requisito o rebajan un riesgo. Que la Alcaldía esté en la mesa es lo
que hace viable concertar en el epicentro; que la firma vaya delimitada cuesta la
cuarta parte en respaldo internacional. Ponlos SOLO si el texto los dice con sus
palabras. Que la orden suene razonable sin ellos no es decirlos.

El texto viene de una deliberación real: es coloquial, incompleto y a veces
contradictorio. Traduce lo que se pidió, no lo que crees que deberían haber
pedido."""


def interpretar(estado: Estado, texto: str, plan_id: str) -> Plan:
    """Los nueve pasos. Solo el primero usa el modelo, y solo si hay llave."""
    plan = Plan(plan_id=plan_id, texto_original=texto)

    llamadas, quien = _traducir(estado, texto)
    plan.interpretado_por = quien

    if not llamadas:
        plan.avisos.append(_diagnostico_sin_acciones(estado, texto))
        return plan

    # 3 · EXPANSOR. Un criterio —«todos los puntos», «los cerrados»— produce
    #     UNA acción por punto. Antes se quedaba con el primero y la sala creía
    #     haber ordenado veinticuatro operaciones cuando ordenaba una.
    llamadas = _expandir_selectores(estado, llamadas, plan)

    if len(llamadas) > TOPE_ACCIONES:
        plan.avisos.append(
            f"La orden expande a {len(llamadas)} acciones y el tope es "
            f"{TOPE_ACCIONES}. Se muestran las primeras; confirme o acote."
        )
        llamadas = llamadas[:TOPE_ACCIONES]

    # 4 · VALIDADOR — recorre TODAS. Prohibido `break` al primer problema: una
    #     orden compuesta no puede morir entera porque a una parte le falte un dato.
    for llamada in llamadas:
        plan.acciones.append(_a_accion_plan(estado, llamada, texto))

    # Lo que el canal NO traduce y hay que decir en voz alta antes de confirmar.
    plan.avisos.extend(_avisos_de_lectura(texto))
    return plan


def _expandir_selectores(estado: Estado, llamadas: list[dict],
                         plan: Plan) -> list[dict]:
    """
    Un criterio no es un lugar: es N lugares. Aquí se convierte en N llamadas.

    Solo se expanden las entidades SIMPLES. Las de lista —los puntos de
    `asignar_duplas`— ya se expanden dentro de la acción, porque ahí la lista
    entera es un solo acto: tres duplas para tres puntos, no tres acciones.
    """
    salida: list[dict] = []
    for ll in llamadas:
        spec = herramientas.HERRAMIENTAS.get(ll["nombre"])
        if spec is None:
            salida.append(ll)
            continue

        expandida = False
        for campo, tipo in spec.get("entidades", {}).items():
            crudo = (ll.get("argumentos") or {}).get(campo)
            if not crudo:
                continue
            r = resolver.resolver(estado, str(crudo), tipo)
            if r.estado != "selector":
                continue

            ids = resolver.expandir_selector(estado, r.selector or "")
            if not ids:
                break        # sin resultados: que lo marque el validador
            plan.avisos.append(
                f"«{crudo}» es un criterio, no un lugar: son {len(ids)} "
                f"{'punto' if len(ids) == 1 else 'puntos'}. Se ordena uno por cada uno."
            )
            for i in ids:
                salida.append({"nombre": ll["nombre"],
                               "argumentos": {**ll["argumentos"], campo: i}})
            expandida = True
            break

        if not expandida:
            salida.append(ll)
    return salida


# Lo que la gente escribe y el canal NO sabe traducir. No se adivina: se dice.
#
# Van por PALABRA COMPLETA y no por trozo: con «si » a secas, «casi todos los
# puntos siguen cerrados, operen el Puente Amarillo» disparaba el aviso de
# condicional. Un aviso que salta cuando no toca se deja de leer, y entonces
# tampoco se lee el que sí importa.
CONDICIONALES = (r"\bsi\b", r"\bcuando\b", r"\ben cuanto\b",
                 r"\buna vez que\b", r"\bsiempre que\b")
NEGACIONES = (r"\bno\s+oper", r"\bno\s+se\s+opere", r"\bno\s+intervenir",
              r"\bno\s+intervengan", r"\bnada\s+de\b", r"\bning[uú]n\s+punto\b",
              r"\beviten\b", r"\babstenerse\b")


def _avisos_de_lectura(texto: str) -> list[str]:
    """
    Dos cosas que el canal no traduce y que, calladas, cambian la orden entera.

    **No se suprime ni se adivina nada.** El plan se lee en voz alta antes de
    ejecutar precisamente para que una persona atrape esto; el canal solo tiene
    que señalarlo. Suprimir la acción sería el canal decidiendo, que es lo único
    que esta capa no puede hacer.
    """
    t = texto.lower()
    avisos = []
    if any(re.search(c, t) for c in CONDICIONALES):
        avisos.append(
            "Se leyó una condición en el texto y el canal NO la traduce: lo que "
            "sigue queda como orden inmediata. Si debía esperar a que ocurriera "
            "algo, no la confirmen todavía."
        )
    if any(re.search(nn, t) for nn in NEGACIONES):
        avisos.append(
            "Se leyó una negación en el texto y el canal NO la traduce: las "
            "acciones de abajo están en afirmativo. Comprueben que es lo que se "
            "quiso pedir."
        )
    return avisos


def _diagnostico_sin_acciones(estado: Estado, texto: str) -> str:
    """
    Por qué no se reconoció nada. **Cuatro respuestas distintas, no una.**

    Antes, un texto vacío, un galimatías, un saludo, una pregunta y «declaren el
    estado de sitio» daban el mismo párrafo. La sala no podía saber si había
    escrito mal el nombre, si le faltaba el verbo, o si eso sencillamente no
    existe en este mundo — y son tres correcciones distintas.
    """
    if not texto or not texto.strip():
        return "No se escribió ninguna orden."

    citados = resolver.nombres_citados(estado, texto)
    if citados:
        return (
            f"Se menciona {', '.join('«' + c + '»' for c in citados[:3])}, pero no "
            f"qué hacer con {'ellos' if len(citados) > 1 else 'eso'}. Diga la "
            f"acción: operar, concertar, escoltar, verificar, declarar…"
        )

    if "?" in texto or "¿" in texto:
        return (
            "Eso parece una pregunta y no una orden. El canal responde sobre "
            f"{', '.join(herramientas.TEMAS_CONSULTA)}; para lo demás, el dato "
            "está en la vista privada de algún rol."
        )

    # ¿Se entendió la ACCIÓN pero no sobre qué? Es un quinto diagnóstico, y hace
    # falta porque el modelo a veces no llama a nada cuando el sitio es
    # ambiguo: «operen el puente» acababa respondiendo «esa acción no existe»,
    # que es falso y manda a corregir donde no estaba el problema. La regla del
    # sistema ya le pide que llame igual; esto es la red por debajo.
    verbo = herramientas.verbo_reconocido(texto)
    if verbo:
        return (
            f"Se entiende la acción —{verbo}— pero no sobre qué. Diga el punto, "
            f"el corredor o la región por su nombre, o un criterio: «los "
            f"cerrados», «el más duro», «sin verificar»."
        )

    return (
        "Ninguna acción del repertorio corresponde a eso, y el canal no fuerza la "
        "más parecida. Se puede pedir: operar un punto, concertar una mesa, "
        "escoltar un corredor, asignar duplas de verificación, o adoptar una "
        "acción constitutiva. El repertorio completo está en la vista de cada rol."
    )


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
            **cfg.extra_nlu(),
        )
    except Exception as exc:                                  # pragma: no cover
        # Un error del proveedor no puede dejar a nueve personas mirando la
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

def _a_accion_plan(estado: Estado, llamada: dict, texto: str = "") -> AccionPlan:
    nombre = llamada["nombre"]
    args = dict(llamada.get("argumentos") or {})
    spec = herramientas.HERRAMIENTAS.get(nombre)

    if spec is None:
        return AccionPlan(herramienta=nombre, rol="?",
                          descripcion=f"Herramienta desconocida: {nombre}",
                          estado="no_viable",
                          motivo="No existe esa acción en el repertorio.")

    # Rama de solo lectura: preguntar no es ordenar. No construye acción, no
    # toca el motor y no se puede ejecutar — `SOLO_LECTURA` lo garantiza aguas
    # abajo, en la consola.
    if spec.get("solo_lectura"):
        tema = str(args.get("tema", "")).strip().lower()
        if tema not in herramientas.TEMAS_CONSULTA:
            return AccionPlan(
                herramienta=nombre, rol=spec["rol"],
                descripcion=spec["descripcion"], argumentos=args,
                estado="falta_dato",
                motivo=(f"«{tema or 'sin tema'}» no es un tema de consulta. "
                        f"Los que hay: {', '.join(herramientas.TEMAS_CONSULTA)}."))
        return AccionPlan(
            herramienta=nombre, rol=spec["rol"],
            descripcion=f"Consulta: {TEMA_EN_CLARO.get(tema, tema)}",
            argumentos={"tema": tema}, estado="lista",
            datos=hoja_de_datos(estado, tema))

    # Normalizar enumeraciones ANTES de tocar el motor. El modelo dice
    # «militares» donde el motor espera «militar», y eso no puede reventar nada.
    args, avisos_tipo = herramientas.coercionar_tipos(spec, args)
    args, avisos_enum = herramientas.normalizar_enums(args)
    avisos_enum = avisos_tipo + avisos_enum

    # LOS VALORES POR DEFECTO SE PONEN EN EL PLAN, no dentro del constructor.
    #
    # Estaban escondidos en las lambdas de `construir`: la acción se ejecutaba
    # con ESMAD, con seis escuadrones o con la Alcaldía presente, y como el
    # argumento no estaba en `argumentos`, la lectura en voz alta no lo decía.
    # La sala confirmaba una cosa y el motor hacía otra, sin que nadie mintiera.
    #
    # Puestos aquí, viajan con el plan, se dicen en `en_claro()` y se pueden
    # corregir con una elección tipada como cualquier otro argumento.
    for campo, valor in spec.get("por_defecto", {}).items():
        args.setdefault(campo, valor)

    # LO QUE NADIE DIJO NO SE DA POR PUESTO. Aquí se contrasta contra el texto
    # que escribió la sala, no contra lo que devolvió el modelo — que es quien
    # se lo inventa. Medido: «concertar en un punto del epicentro» volvía con
    # `con_alcaldia: true` sin que nadie hubiera nombrado a la Alcaldía, y eso
    # abre la única puerta que obliga al Interior a traer al Alcalde.
    #
    # Solo BAJA concesiones. Si la sala lo dijo y el modelo no lo puso, no se
    # añade: añadir también sería el canal decidiendo. Se queda en su valor
    # declarado, se dice en voz alta, y la sala lo corrige con un botón.
    correcciones: list[str] = []
    if texto:
        args, correcciones = herramientas.corregir_lo_que_no_se_infiere(
            spec, args, texto)

    ap = AccionPlan(herramienta=nombre, rol=spec["rol"],
                    descripcion=spec["descripcion"], argumentos=args,
                    correcciones=correcciones)
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
        r.campo = campo
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
            r.campo = campo
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

    # ¿Falta algo obligatorio? Se dice CUÁL. Antes esto llegaba al motor y volvía
    # como «No existe el punto .» — un mensaje que no le dice a nadie qué
    # escribir para arreglarlo.
    faltan = [c for c in spec.get("requeridos", []) if not args.get(c)]
    if faltan:
        ap.estado = "falta_dato"
        ap.requisitos_faltantes = faltan
        ap.motivo = (
            f"No se entendió {' ni '.join(_NOMBRE_CAMPO.get(c, c) for c in faltan)}. "
            f"Repita la orden nombrándolo."
        )
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
            "ambito": "los corredores del pais",
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
