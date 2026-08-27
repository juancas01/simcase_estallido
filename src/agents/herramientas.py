"""
herramientas.py — Las herramientas tipadas de la capa 4.

El modelo solo puede llamar a estas. Ninguna prosa, ningún JSON en texto plano
parseado a mano: si el modelo responde en prosa, un `except` acaba mostrando esa
prosa a la sala como si fuera la interpretación oficial.

DOS REGLAS DEL ESQUEMA
----------------------
1. **Los nombres de lugar viajan como texto crudo.** El modelo NO los normaliza:
   esa responsabilidad es de `resolver.py`, que es determinista y auditable.
2. **El catálogo se genera desde los datos**, no se escribe en el prompt. En la
   simulación anterior, un paquete que faltaba en el prompt escrito a mano fue
   invisible para el agente durante todo un ejercicio.

Y una tercera que se aprendió midiendo: **restringir el espacio de salida no
impide que el modelo se salga; lo empuja a forzar la orden dentro de lo
disponible.** Y eso es peor, porque es silencioso. Por eso el sistema le dice
explícitamente que si nada encaja, no llame a nada.
"""

from __future__ import annotations

import re
import unicodedata

from src.engine import actions as A
from src.engine.state import Estado
from src.agents import resolver


def _sin_tildes(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# El repertorio expuesto al modelo
#
# No son las 34 acciones: son las que la sala puede pedir en lenguaje natural.
# Las constitutivas se piden por su nombre y no llevan entidades; las operativas
# llevan el punto o el corredor sobre el que actúan.
# ---------------------------------------------------------------------------

# Los temas de la hoja de datos. Viven aquí porque los usan el esquema de la
# herramienta, el intérprete de reserva y `nlu.hoja_de_datos`. Un dato en dos
# sitios se desincroniza.
TEMAS_CONSULTA = ["fuerza", "corredores", "abastecimiento", "mesa"]


HERRAMIENTAS: dict[str, dict] = {
    # --- Seguridad ---
    "operar_punto": {
        "rol": "Ministro de Defensa",
        "descripcion": "Operación de desbloqueo sobre un punto de cierre",
        "entidades": {"nodo_id": "punto"},
        "muestra_riesgo": True,
        "construir": lambda a: A.OperarNodo(
            nodo_id=a.get("nodo_id", ""),
            tipo_unidad=a.get("tipo_unidad", "esmad"),
            dupla_presente=bool(a.get("dupla_presente")),
            concertado_con_alcaldia=bool(a.get("concertado_con_alcaldia")),
            responsable_nominado=a.get("responsable_nominado"),
            de_noche=bool(a.get("de_noche")),
        ),
        "esquema": {
            "nodo_id": ("string", "El punto de cierre, TAL CUAL lo dijo la persona"),
            "tipo_unidad": ("string", "esmad, policia o militar"),
            "dupla_presente": ("boolean", "si acompaña una dupla de la Defensoría (gasta una de las tres)"),
            "concertado_con_alcaldia": ("boolean", "si se concertó con la Alcaldía"),
            "responsable_nominado": ("string", "quién firma la orden"),
            "de_noche": ("boolean", "si se ordena operar de noche"),
        },
        "requeridos": ["nodo_id"],
    },
    "disponer_esmad": {
        "rol": "Director de Policía",
        "descripcion": "Concentrar el ESMAD replegando la contención estática",
        "entidades": {},
        "construir": lambda a: A.DisponerESMAD(
            n_escuadrones=int(a.get("n_escuadrones", 6))),
        "esquema": {"n_escuadrones": ("integer", "cuántos escuadrones concentrar")},
        "requeridos": [],
    },
    "escoltar": {
        "rol": "Director de Policía",
        "descripcion": "Escoltar una caravana, carrotanque o misión médica",
        "entidades": {"corredor_id": "corredor"},
        "construir": lambda a: A.Escoltar(
            corredor_id=a.get("corredor_id", ""),
            clase_carga=a.get("clase_carga", "humanitario")),
        "esquema": {
            "corredor_id": ("string", "El corredor, TAL CUAL lo dijo la persona"),
            "clase_carga": ("string", "humanitario, combustible, alimentario o general"),
        },
        "requeridos": ["corredor_id"],
    },
    "relevar_unidades": {
        "rol": "Director de Policía",
        "descripcion": "Relevo y rotación de unidades agotadas",
        "entidades": {},
        "construir": lambda a: A.SolicitarRelevo(
            n_unidades=int(a.get("n_unidades", 6))),
        "esquema": {"n_unidades": ("integer", "cuántas unidades relevar")},
        "requeridos": [],
    },
    "redesplegar_militares": {
        "rol": "Ministro de Defensa",
        "descripcion": "Redespliegue militar a infraestructura, o proyección aérea",
        "entidades": {},
        "construir": lambda a: A.RedesplegarMilitares(
            modo=a.get("modo", "infraestructura"),
            n_unidades=int(a.get("n_unidades", 4))),
        "esquema": {
            "modo": ("string", "infraestructura o proyeccion_aerea"),
            "n_unidades": ("integer", "cuántas unidades militares"),
        },
        "requeridos": [],
    },
    # --- Estrategia ---
    "firmar_asistencia_militar": {
        "rol": "Presidente",
        "descripcion": "Acto administrativo de asistencia militar",
        "entidades": {},
        "construir": lambda a: A.FirmarAsistenciaMilitar(
            delimitada=bool(a.get("delimitada", False))),
        "esquema": {"delimitada": ("boolean",
                                   "si lleva territorio, plazo, reglas escritas y "
                                   "criterio de terminación")},
        "requeridos": [],
    },
    "convocar_mesa_nacional": {
        "rol": "Ministro del Interior",
        "descripcion": "Sesión de la mesa nacional con el Comité del Paro",
        "entidades": {},
        "construir": lambda a: A.ConvocarMesaNacional(),
        "esquema": {},
        "requeridos": [],
    },
    "abrir_mesa_local": {
        "rol": "Ministro del Interior",
        "descripcion": "Mesa de concertación sobre un punto",
        "entidades": {"nodo_id": "punto"},
        "construir": lambda a: A.AbrirMesaLocal(
            nodo_id=a.get("nodo_id", ""),
            con_alcaldia=bool(a.get("con_alcaldia", True))),
        "esquema": {
            "nodo_id": ("string", "El punto, TAL CUAL lo dijo la persona"),
            "con_alcaldia": ("boolean", "si la Alcaldía participa (obligatorio en el epicentro)"),
        },
        "requeridos": ["nodo_id"],
    },
    "ofrecer_contraprestacion": {
        "rol": "Ministro del Interior",
        "descripcion": "Contraprestación legislativa por el levantamiento de cierres",
        "entidades": {},
        "construir": lambda a: A.OfrecerContraprestacion(),
        "esquema": {},
        "requeridos": [],
    },
    "esquema_humanitario": {
        "rol": "Alcalde",
        "descripcion": "Esquema humanitario municipal en su jurisdicción",
        "entidades": {},
        "construir": lambda a: A.EsquemaHumanitarioMunicipal(),
        "esquema": {},
        "requeridos": [],
    },
    "mesa_con_voceros": {
        "rol": "Alcalde",
        "descripcion": "Mesa local con los voceros de un punto de su ciudad",
        "entidades": {"nodo_id": "punto"},
        "construir": lambda a: A.InstalarMesaConVoceros(nodo_id=a.get("nodo_id", "")),
        "esquema": {"nodo_id": ("string", "El punto, TAL CUAL lo dijo la persona")},
        "requeridos": ["nodo_id"],
    },
    # --- Defensoría ---
    "asignar_duplas": {
        "rol": "Defensoría",
        "descripcion": "Asignar las tres duplas de verificación",
        "entidades": {},
        "entidades_lista": {"puntos": "punto"},
        "construir": lambda a: A.AsignarDuplas(
            nodos=list(a.get("puntos") or []),
            denuncias=list(a.get("denuncias") or [])),
        "esquema": {
            "puntos": ("array", "puntos a verificar, TAL CUAL los dijo la persona"),
            "denuncias": ("array", "identificadores de denuncias a verificar"),
        },
        "requeridos": [],
    },
    "exigir_estandares": {
        "rol": "Defensoría",
        "descripcion": "Estándar de empleo: reglas escritas, identificación, registro",
        "entidades": {},
        "construir": lambda a: A.ExigirEstandaresEmpleo(),
        "esquema": {},
        "requeridos": [],
    },
    "requerir_corredor_humanitario": {
        "rol": "Defensoría",
        "descripcion": "Requerimiento de paso humanitario permanente",
        "entidades": {"corredor_id": "corredor"},
        "construir": lambda a: A.RequerirCorredoresHumanitarios(
            corredor_id=a.get("corredor_id", "")),
        "esquema": {"corredor_id": ("string", "El corredor, o vacío para el más cerrado")},
        "requeridos": [],
    },
    "manifestar_duda_permanencia": {
        "rol": "Defensoría",
        "descripcion": "Manifestar públicamente que su permanencia está en cuestión",
        "entidades": {},
        "construir": lambda a: A.ManifestarDudaPermanencia(),
        "esquema": {},
        "requeridos": [],
    },
    # --- Logística ---
    "organizar_caravana": {
        "rol": "Ministro de Transporte",
        "descripcion": "Caravana escoltada por un corredor priorizado",
        "entidades": {"corredor_id": "corredor"},
        "construir": lambda a: A.OrganizarCaravana(corredor_id=a.get("corredor_id", "")),
        "esquema": {"corredor_id": ("string", "El corredor, TAL CUAL lo dijo la persona")},
        "requeridos": ["corredor_id"],
    },
    "negociar_con_gremios": {
        "rol": "Ministro de Transporte",
        "descripcion": "Negociación con los gremios camioneros",
        "entidades": {},
        "construir": lambda a: A.NegociarConGremios(
            ofrece_compensacion=bool(a.get("ofrece_compensacion", True))),
        "esquema": {"ofrece_compensacion": ("boolean", "si se ofrece compensación")},
        "requeridos": [],
    },
    "declarar_infraestructura_critica": {
        "rol": "Ministro de Minas",
        "descripcion": "Declaratoria de infraestructura crítica",
        "entidades": {},
        "construir": lambda a: A.DeclararInfraestructuraCritica(
            instalaciones=list(a.get("instalaciones") or ["refineria"])),
        "esquema": {"instalaciones": ("array", "las instalaciones a proteger")},
        "requeridos": [],
    },
    "fijar_prioridad_combustible": {
        "rol": "Ministro de Minas",
        "descripcion": "Orden de prioridad del combustible entre usos",
        "entidades": {},
        "construir": lambda a: A.FijarPrioridadCombustible(
            orden=list(a.get("orden") or A.P.ORDEN_PRIORIDAD_COMBUSTIBLE)),
        "esquema": {"orden": ("array",
                              "los cuatro usos ordenados: mision_medica, "
                              "fuerza_publica, transporte_alimentos, consumo_general")},
        "requeridos": [],
    },
    "entregar_calendario": {
        "rol": "Ministro de Minas",
        "descripcion": "Entregar el calendario de agotamiento a la mesa",
        "entidades": {},
        "construir": lambda a: A.EntregarCalendarioAgotamiento(),
        "esquema": {},
        "requeridos": [],
    },
    # --- Constitutivas de la mesa ---
    "fijar_registro_escrito": {
        "rol": "Presidente",
        "descripcion": "Nodo único y registro escrito con responsable nominado",
        "entidades": {},
        "construir": lambda a: A.FijarRegistroEscrito(),
        "esquema": {},
        "requeridos": [],
    },
    "fijar_lineas_rojas": {
        "rol": "Presidente",
        "descripcion": "Líneas rojas del Ejecutivo y marco de lo negociable",
        "entidades": {},
        "construir": lambda a: A.FijarLineasRojas(
            margen=float(a.get("margen", 0.5))),
        "esquema": {"margen": ("number", "0 = sin margen, 1 = todo negociable")},
        "requeridos": [],
    },
    "exigir_protocolo_voceria": {
        "rol": "Ministro del Interior",
        "descripcion": "Protocolo de vocería y plazo suspensivo de 24 h",
        "entidades": {},
        "construir": lambda a: A.ExigirProtocoloVoceria(),
        "esquema": {},
        "requeridos": [],
    },
    "adoptar_criterio_priorizacion": {
        "rol": "Ministro de Transporte",
        "descripcion": "Criterio único de priorización de corredores",
        "entidades": {},
        "construir": lambda a: A.AdoptarCriterioPriorizacion(),
        "esquema": {},
        "requeridos": [],
    },
    "clasificar_parte": {
        "rol": "Director de Policía",
        "descripcion": "Parte clasificado en confirmado, estimado y en verificación",
        "entidades": {},
        "construir": lambda a: A.ClasificarParteOperacional(),
        "esquema": {},
        "requeridos": [],
    },
    "condicionar_empleo_fuerza": {
        "rol": "Alcalde",
        "descripcion": "Concertación previa del empleo de la fuerza en su jurisdicción",
        "entidades": {},
        "construir": lambda a: A.CondicionarEmpleoFuerza(),
        "esquema": {},
        "requeridos": [],
    },

    # --- La rama de solo lectura ---
    #
    # Preguntar NO es ordenar, y el sistema no puede obligar a elegir entre las
    # dos: un mensaje puede ser orden Y consulta a la vez. Por eso consultar es
    # una herramienta más y no un clasificador previo — un clasificador que se
    # equivoca manda una orden que nadie dio, y eso es irreversible.
    #
    # `solo_lectura` es lo que impide que llegue al motor. Nunca construye una
    # acción: no tiene `construir`.
    "consultar": {
        "rol": "cualquiera",
        "descripcion": "Consulta del estado, sin ordenar nada",
        "entidades": {},
        "solo_lectura": True,
        "esquema": {"tema": ("string", "sobre qué se pregunta",
                             TEMAS_CONSULTA)},
        "requeridos": ["tema"],
    },
}

TIPOS_JSON = {"string": "string", "integer": "integer",
              "boolean": "boolean", "number": "number", "array": "array"}


def esquemas() -> list[dict]:
    """Los esquemas en el formato de tool calling. Se generan, no se escriben."""
    out = []
    for nombre, spec in HERRAMIENTAS.items():
        props = {}
        for campo, decl in spec["esquema"].items():
            tipo, desc = decl[0], decl[1]
            opciones = decl[2] if len(decl) > 2 else None
            if tipo == "array":
                props[campo] = {"type": "array", "items": {"type": "string"},
                                "description": desc}
            else:
                props[campo] = {"type": TIPOS_JSON[tipo], "description": desc}
            if opciones:
                props[campo]["enum"] = list(opciones)
        out.append({
            "type": "function",
            "function": {
                "name": nombre,
                "description": f"[{spec['rol']}] {spec['descripcion']}",
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": spec["requeridos"],
                },
            },
        })
    return out


# ---------------------------------------------------------------------------
# Normalización de enumeraciones — determinista, y hace falta
#
# El modelo devuelve «militares» donde el motor espera «militar», o «humanitaria»
# donde espera «humanitario». Con un esquema tipado eso sigue pasando: el tipo es
# `string`, no un enum cerrado, y aunque lo fuera el modelo puede salirse.
#
# **Restringir el espacio de salida no impide que el modelo se salga: lo empuja a
# forzar el valor dentro de lo disponible.** Y eso es peor, porque es silencioso.
# Aquí se normaliza en una capa determinista y auditable, y lo que no encaja se
# rechaza en `validar()` con un motivo legible — nunca revienta el turno.
# ---------------------------------------------------------------------------

ENUMS: dict[str, dict[str, str]] = {
    "tipo_unidad": {
        "esmad": "esmad", "escuadron movil": "esmad", "antidisturbios": "esmad",
        "policia": "policia", "policia regular": "policia", "policias": "policia",
        "militar": "militar", "militares": "militar", "ejercito": "militar",
        "tropa": "militar", "fuerzas militares": "militar",
    },
    "clase_carga": {
        "humanitario": "humanitario", "humanitaria": "humanitario",
        "mision medica": "humanitario", "oxigeno": "humanitario",
        "combustible": "combustible", "carrotanque": "combustible",
        "alimentario": "alimentario", "alimentos": "alimentario",
        "alimenticio": "alimentario", "general": "general", "carga": "general",
    },
    "modo": {
        "infraestructura": "infraestructura", "estatica": "infraestructura",
        "proteccion estatica": "infraestructura",
        "proyeccion_aerea": "proyeccion_aerea", "proyeccion aerea": "proyeccion_aerea",
        "aerea": "proyeccion_aerea",
    },
}


def normalizar_enums(argumentos: dict) -> tuple[dict, list[str]]:
    """
    Devuelve `(argumentos_normalizados, avisos)`.

    Lo que no encaja se DEJA COMO ESTÁ y se avisa, para que `validar()` lo
    rechace con un motivo que la sala pueda leer. Silenciarlo o sustituirlo por
    un valor por defecto produciría el peor fallo posible: la orden se ejecuta
    con una unidad que nadie pidió y nadie se entera.
    """
    out, avisos = dict(argumentos), []
    for campo, tabla in ENUMS.items():
        crudo = out.get(campo)
        if not isinstance(crudo, str):
            continue
        clave = _sin_tildes(crudo).strip()
        if clave in tabla:
            out[campo] = tabla[clave]
        else:
            avisos.append(
                f"«{crudo}» no es un valor válido para {campo}. "
                f"Los que hay: {', '.join(sorted(set(tabla.values())))}."
            )
    return out, avisos


def catalogo_compacto(estado: Estado) -> dict:
    """
    Lo que el modelo necesita saber del mundo para traducir. **Generado desde el
    estado**, nunca escrito a mano en el prompt.
    """
    return {
        "puntos": [{"id": n.nodo_id, "nombre": n.nombre} for n in estado.nodos.values()],
        "corredores": [{"id": c.corredor_id, "nombre": c.nombre}
                       for c in estado.corredores.values()],
        "regiones": [{"id": r.region_id, "nombre": r.nombre}
                     for r in estado.regiones.values()],
        "denuncias_abiertas": [d.denuncia_id for d in estado.denuncias
                               if not d.verificada],
    }


# ---------------------------------------------------------------------------
# El intérprete de reserva — sin modelo
# ---------------------------------------------------------------------------

# Raíces que disparan cada herramienta. Se usan RAÍCES y no palabras completas
# porque la gente conjuga: «operen», «operar», «operación» y «operativo» son la
# misma orden. Con palabras completas, «Operen el Puente Amarillo» no disparaba
# nada — y eso es exactamente el fallo silencioso que hay que evitar.
#
# `excluye` evita que una raíz secundaria robe la orden: «con dupla de la
# Defensoría» dentro de una operación es un PARÁMETRO, no una acción aparte.
DISPARADORES: list[tuple[str, list[str], list[str]]] = [
    ("operar_punto", ["oper", "desbloque", "despej", "intervenir", "esmad en"], []),
    ("escoltar", ["escolt", "carrotanque", "mision medica", "misión medica"], []),
    ("disponer_esmad", ["concentr", "replegar", "repliegue", "disponer del esmad"], []),
    ("relevar_unidades", ["relev", "rotar", "rotacion"], []),
    ("convocar_mesa_nacional", ["mesa nacional", "comite del paro", "comité del paro",
                                "convocar la mesa"], []),
    ("abrir_mesa_local", ["concert", "mesa local", "pactar", "pacto",
                          "negociar el punto"], ["mesa nacional"]),
    ("ofrecer_contraprestacion", ["contraprestacion", "congreso",
                                  "tramite legislativo"], []),
    ("esquema_humanitario", ["esquema humanitario", "ollas comunitarias",
                             "barrios aislados"], []),
    ("asignar_duplas", ["dupla", "verific"], ["oper", "acompan", "acompañ"]),
    ("exigir_estandares", ["estandar", "reglas de empleo",
                           "identificacion de agentes"], []),
    ("requerir_corredor_humanitario", ["corredor humanitario", "paso humanitario"], []),
    ("manifestar_duda_permanencia", ["retirarme", "permanencia", "no puedo avalar"], []),
    ("organizar_caravana", ["caravana", "conductores"], ["escolt"]),
    ("negociar_con_gremios", ["gremio", "camionero"], []),
    ("declarar_infraestructura_critica", ["infraestructura critica",
                                          "proteger la refineria"], []),
    ("fijar_prioridad_combustible", ["prioridad de combustible",
                                     "asignar combustible", "asignacion de combustible"], []),
    ("entregar_calendario", ["calendario", "agotamiento",
                             "cuanto tiempo queda"], []),
    ("firmar_asistencia_militar", ["asistencia militar", "ley 1801"], []),
    ("fijar_registro_escrito", ["registro escrito", "responsable nominado",
                                "nodo unico"], []),
    ("fijar_lineas_rojas", ["lineas rojas", "linea roja"], []),
    ("exigir_protocolo_voceria", ["protocolo de voceria", "plazo suspensivo"], []),
    ("adoptar_criterio_priorizacion", ["criterio de priorizacion",
                                       "priorizar corredores", "priorizacion de corredores"], []),
    ("clasificar_parte", ["clasificar el parte", "parte clasificado",
                          "confirmado estimado"], []),
    ("condicionar_empleo_fuerza", ["condicionar", "concertacion previa"], []),
]


# Interrogativos que convierten un texto en consulta y no en orden, con el tema
# al que corresponde cada uno. Preguntar no es ordenar.
PREGUNTAS: list[tuple[str, list[str]]] = [
    ("fuerza", ["cuantos escuadrones", "cuanta fuerza", "esmad disponible",
                "unidades disponibles", "cuantas unidades", "como esta la fuerza"]),
    ("corredores", ["que corredores", "como estan los corredores",
                    "esta abierto", "estan abiertos", "que esta bloqueado"]),
    ("abastecimiento", ["cuanto oxigeno", "cuanto combustible", "abastecimiento",
                        "cuanto tiempo queda", "dias de autonomia"]),
    ("mesa", ["como esta la mesa", "que legitimidad", "credibilidad",
              "estado de la mesa", "que reservas"]),
]


def interpretar_sin_modelo(estado: Estado, texto: str) -> list[dict]:
    """
    Reserva determinista para cuando no hay llave o el proveedor falla.

    **Cada disparador solo mira SU cláusula.** Antes miraba el texto entero, y
    eso producía el peor fallo del sistema: en «operen el puente y concertar el
    Alto del Mirador», el nombre de la segunda cláusula se colaba en la primera y
    salían dos acciones sobre el Alto del Mirador. La ambigüedad de «el puente»
    —que era la respuesta correcta, una repregunta— desaparecía sin que nadie lo
    notara.

    Extrae el nombre citándolo **tal cual**, para que el resolutor haga su
    trabajo igual que con el modelo. El cauce posterior es idéntico.
    """
    t = _sin_tildes(texto)
    llamadas: list[dict] = []

    # Una consulta no compite con las órdenes: se emite además.
    for tema, marcas in PREGUNTAS:
        if any(m in t for m in marcas):
            llamadas.append({"nombre": "consultar", "argumentos": {"tema": tema}})
            break

    for nombre, raices, excluye, ini, fin in _clausulas(t):
        spec = HERRAMIENTAS[nombre]
        # La cláusula, en el texto original y en el normalizado. Si las
        # longitudes no coinciden —alguna descomposición rara— se usa el texto
        # entero: peor precisión, pero nunca un recorte a destiempo.
        crudo_clausula = texto[ini:fin] if len(t) == len(texto) else texto
        t_clausula = t[ini:fin]

        args: dict = {}
        for campo, tipo in spec.get("entidades", {}).items():
            crudo = _extraer_entidad(estado, crudo_clausula, tipo)
            if crudo:
                args[campo] = crudo
        for campo, tipo in spec.get("entidades_lista", {}).items():
            encontrados = _extraer_entidades(estado, crudo_clausula, tipo)
            if encontrados:
                args[campo] = encontrados

        # Las enumeraciones que la cláusula nombra. Sin esto, «operen X con
        # militares» salía como ESMAD por defecto: una substitución silenciosa de
        # la unidad, que es el fallo más caro del canal. Lo que no reconozca
        # queda sin poner y la lectura en voz alta dice «con ESMAD», que es lo
        # que la sala tiene que oír para corregir.
        args.update(_enums_de_la_clausula(spec, t_clausula))

        if "dupla" in t_clausula and nombre == "operar_punto":
            args["dupla_presente"] = True
        if "de noche" in t_clausula or "nocturn" in t_clausula:
            args["de_noche"] = True
        if "delimit" in t or "con limites" in t:
            args["delimitada"] = True

        # Falta un dato obligatorio: se emite igual, para que el validador lo
        # marque y la sala lo complete. No se descarta en silencio.
        llamadas.append({"nombre": nombre, "argumentos": args})

    return llamadas[:12]


# Para `tipo_unidad` hace falta una marca: sin ella, «responsable el Director de
# Policía» pondría la unidad en policía. Con la marca, solo cuenta «con policía».
MARCAS_UNIDAD = ("con ", "usando ", "empleando ", "mediante ")


def _enums_de_la_clausula(spec: dict, t_clausula: str) -> dict:
    """Los valores de enumeración que la cláusula nombra explícitamente."""
    puestos = {}
    for campo in spec.get("esquema", {}):
        tabla = ENUMS.get(campo)
        if tabla is None:
            continue
        # De más largo a más corto: «escuadron movil» antes que «movil».
        for clave in sorted(tabla, key=len, reverse=True):
            if clave not in t_clausula:
                continue
            if campo == "tipo_unidad" and not any(
                    m + clave in t_clausula for m in MARCAS_UNIDAD):
                continue
            puestos[campo] = tabla[clave]
            break
    return puestos


def _clausulas(t: str) -> list[tuple[str, list[str], list[str], int, int]]:
    """
    Reparte el texto entre los disparadores que aparecen, por posición.

    Cada disparador se queda con el tramo que va desde donde aparece su raíz
    hasta donde empieza el siguiente. Es una heurística tosca —no analiza
    sintaxis— pero resuelve el caso que importa: que el complemento de una orden
    no se lo lleve otra.
    """
    encontrados = []
    for nombre, raices, excluye in DISPARADORES:
        posiciones = [t.find(r) for r in raices if r in t]
        if not posiciones:
            continue
        if any(x in t for x in excluye):
            continue
        encontrados.append((min(posiciones), nombre, raices, excluye))

    encontrados.sort()
    salida = []
    for i, (pos, nombre, raices, excluye) in enumerate(encontrados):
        fin = encontrados[i + 1][0] if i + 1 < len(encontrados) else len(t)
        salida.append((nombre, raices, excluye, pos, fin))
    return salida


def _extraer_entidades(estado: Estado, texto: str, tipo: str) -> list[str]:
    """Todos los nombres del catálogo que aparecen en el texto, no solo el primero."""
    t = _sin_tildes(texto)
    if tipo == "punto":
        candidatos = [n.nombre for n in estado.nodos.values()]
    elif tipo == "corredor":
        candidatos = [c.nombre for c in estado.corredores.values()]
    else:
        candidatos = [r.nombre for r in estado.regiones.values()]
    encontrados = [c for c in candidatos if _sin_tildes(c) in t]
    if encontrados:
        return encontrados

    # Ningún nombre propio: ¿había un criterio? «verificar los cerrados» producía
    # una lista VACÍA que el plan daba por buena — se ordenaba verificar y no se
    # verificaba nada. El criterio se pasa en crudo y lo expande el resolutor.
    for frase in resolver.FRASES_SELECTOR:
        if _sin_tildes(frase) in t:
            return [frase]
    return []


def _extraer_entidad(estado: Estado, texto: str, tipo: str) -> str | None:
    """Busca el nombre más largo del catálogo que aparezca en el texto."""
    t = _sin_tildes(texto)
    candidatos: list[str] = []
    if tipo == "punto":
        candidatos = [n.nombre for n in estado.nodos.values()]
        candidatos += list(estado.nodos)
    elif tipo == "corredor":
        candidatos = [c.nombre for c in estado.corredores.values()]
        candidatos += list(estado.corredores)
    elif tipo == "region":
        candidatos = [r.nombre for r in estado.regiones.values()]

    encontrados = [c for c in candidatos if _sin_tildes(c) in t]
    if encontrados:
        return max(encontrados, key=len)

    # Un identificador suelto: N003, C-HOS
    m = re.search(r"\b([NCR]-?\d{2,3}|[NC]-[A-Z]{3})\b", texto, re.IGNORECASE)
    if m:
        return m.group(1)

    # Último recurso: el sintagma que sigue al verbo, tal cual, para que el
    # resolutor determinista decida si es claro, ambiguo o desconocido.
    #
    # Es deliberado que esto pueda devolver algo ambiguo —«el peaje», habiendo
    # dos peajes—: la respuesta correcta a «el peaje» ES una repregunta, no una
    # adivinanza. Quedarse con la primera coincidencia produce el peor fallo
    # posible: la orden se ejecuta en el punto equivocado y nadie se entera.
    m = re.search(
        r"(?:oper\w*|desbloque\w*|despej\w*|concert\w*|escolt\w*|verific\w*|"
        r"pact\w*|intervenir)\s+(?:en\s+|sobre\s+|el\s+|la\s+|los\s+|las\s+|"
        r"al\s+|del\s+)*([\wà-ÿ\s]{3,40}?)"
        r"(?:\s+(?:con|y|para|desde)\b|[,.]|$)",
        texto, re.IGNORECASE)
    if m:
        candidato = " ".join(m.group(1).split())
        if candidato and len(candidato.split()) <= 6:
            return candidato
    return None
