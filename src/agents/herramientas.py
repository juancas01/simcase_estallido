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
        "por_defecto": {"tipo_unidad": "esmad"},
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
        "por_defecto": {"n_escuadrones": 6},
        "esquema": {"n_escuadrones": ("integer", "cuántos escuadrones concentrar")},
        "requeridos": [],
    },
    "escoltar": {
        "rol": "Director de Policía",
        "descripcion": "Escoltar una caravana, carrotanque o misión médica",
        "para_el_modelo": ("Pone la escolta policial. Es el requisito PREVIO "
                           "de organizar_caravana, no lo mismo: si el texto "
                           "pide escolta o protección, es esta."),
        "entidades": {"corredor_id": "corredor"},
        "construir": lambda a: A.Escoltar(
            corredor_id=a.get("corredor_id", ""),
            clase_carga=a.get("clase_carga", "humanitario")),
        "por_defecto": {"clase_carga": "humanitario"},
        "esquema": {
            "corredor_id": ("string", "El corredor, TAL CUAL lo dijo la persona"),
            "clase_carga": ("string", "humanitario, combustible, alimentario o general"),
        },
        "requeridos": ["corredor_id"],
    },
    "relevar_unidades": {
        "rol": "Director de Policía",
        "descripcion": "Relevo y rotación de unidades agotadas",
        "para_el_modelo": ("Rota unidades de POLICÍA agotadas por unidades "
                           "descansadas. Es descanso, no movimiento de tropa: "
                           "si el texto dice militares o ejército, no es esta."),
        "entidades": {},
        "construir": lambda a: A.SolicitarRelevo(
            n_unidades=int(a.get("n_unidades", 6))),
        "por_defecto": {"n_unidades": 6},
        "esquema": {"n_unidades": ("integer", "cuántas unidades relevar")},
        "requeridos": [],
    },
    "redesplegar_militares": {
        "rol": "Ministro de Defensa",
        "descripcion": "Redespliegue militar a infraestructura, o proyección aérea",
        "para_el_modelo": ("Mueve unidades MILITARES —ejército, tropa— a "
                           "custodiar instalaciones, o las proyecta por aire. "
                           "«Redesplegar/mover militares» es esta, no un relevo."),
        "entidades": {},
        "construir": lambda a: A.RedesplegarMilitares(
            modo=a.get("modo", "infraestructura"),
            n_unidades=int(a.get("n_unidades", 4))),
        "por_defecto": {"modo": "infraestructura", "n_unidades": 4},
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
        "por_defecto": {"delimitada": False},
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
        "para_el_modelo": ("La mesa del MINISTRO DEL INTERIOR, válida en todo "
                           "el país. Si el texto dice «voceros del punto» o la "
                           "pide el Alcalde para su ciudad, es mesa_con_voceros."),
        "entidades": {"nodo_id": "punto"},
        "construir": lambda a: A.AbrirMesaLocal(
            nodo_id=a.get("nodo_id", ""),
            con_alcaldia=bool(a.get("con_alcaldia", False))),
        # POR DEFECTO **NO** ESTÁ LA ALCALDÍA, y esto no es un detalle.
        #
        # El constructor ponía `True` cuando nadie lo había dicho. En la
        # jurisdicción del epicentro `AbrirMesaLocal.validar()` exige a la
        # Alcaldía —es la única puerta que obliga al Interior a traer al Alcalde
        # a la mesa— y con el valor puesto a `True` esa puerta **nunca se cerró
        # por el canal**: la orden salía `lista` sin que nadie hubiera dicho que
        # la Alcaldía estaba. Una concesión que el canal se daba a sí mismo.
        "por_defecto": {"con_alcaldia": False},
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
        "para_el_modelo": ("La mesa del ALCALDE, solo en su propia ciudad. "
                           "Con los voceros del punto, sin pasar por el "
                           "Ministerio del Interior."),
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
        "para_el_modelo": ("Junta a los conductores y arma la caravana. "
                           "Necesita una escolta ya dispuesta: si lo que se "
                           "pide es la escolta, es escoltar."),
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
        "por_defecto": {"ofrece_compensacion": True},
        "esquema": {"ofrece_compensacion": ("boolean", "si se ofrece compensación")},
        "requeridos": [],
    },
    "declarar_infraestructura_critica": {
        "rol": "Ministro de Minas",
        "descripcion": "Declaratoria de infraestructura crítica",
        "entidades": {},
        "construir": lambda a: A.DeclararInfraestructuraCritica(
            instalaciones=list(a.get("instalaciones") or ["refineria"])),
        "por_defecto": {"instalaciones": ["refineria"]},
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
        "por_defecto": {"margen": 0.5},
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
                # La nota de desambiguación es SOLO para el modelo. La sala
                # oye `descripcion`, que es corta y se lee en voz alta; el
                # modelo necesita además qué la distingue de su vecina, que es
                # donde se equivocaba: «redesplegar cuatro unidades militares»
                # salía unas veces como el relevo del Director de Policía.
                "description": " · ".join(
                    x for x in (f"[{spec['rol']}] {spec['descripcion']}",
                                spec.get("para_el_modelo")) if x),
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


# Cómo se nombra a la Alcaldía. Va con marca —«con», «concertado con»— porque
# «la Alcaldía se opone» no es concertar con ella.
MARCAS_ALCALDIA = ("con la alcaldia", "con el alcalde", "con la alcaldesa",
                   "junto a la alcaldia", "junto al alcalde",
                   "participa la alcaldia", "participa el alcalde")


# ---------------------------------------------------------------------------
# LO QUE NO SE INFIERE — la contraparte determinista de una regla del prompt
#
# Hay booleanos que no describen la orden: **conceden un requisito o un
# mitigador**. Que la Alcaldía esté en la mesa es lo que hace viable concertar
# en el epicentro; que la firma vaya delimitada cuesta −8 de respaldo en vez de
# −22; que haya dupla divide el riesgo. Ninguno se deduce de que la orden suene
# razonable: se dice o no se dice.
#
# El sistema ya se lo pide al modelo, y aun así lo hace: medido, «concertar en
# la Glorieta La Ceiba» volvía con `con_alcaldia: true` sin que nadie hubiera
# nombrado a la Alcaldía. Es la misma lección que ENUMS, escrita en el mismo
# archivo: **restringir el espacio de salida no impide que el modelo se salga.**
# Por eso la comprobación vive aquí, en una capa determinista y auditable, y no
# solo en una frase del prompt.
#
# La marca se busca en el texto ORIGINAL de la sala, no en lo que devolvió el
# modelo. Lo que no la tiene vuelve a su valor declarado y **se dice**.
NO_SE_INFIERE: dict[str, tuple[str, ...]] = {
    "con_alcaldia": MARCAS_ALCALDIA + ("alcaldia", "alcalde", "alcaldesa"),
    "concertado_con_alcaldia": MARCAS_ALCALDIA + ("alcaldia", "alcalde",
                                                  "alcaldesa"),
    "dupla_presente": ("dupla", "defensoria acompan", "acompanamiento"),
    "delimitada": ("delimit", "con limites", "con reglas escritas", "acotad"),
}


# Lo que cuenta como sí y como no cuando llega en texto. `bool("false")` es
# `True`, y esa línea sola bastaría para firmar sin delimitar una orden que dijo
# lo contrario.
_VERDADEROS = {"true", "1", "si", "sí", "yes", "verdadero", "on"}
_FALSOS = {"false", "0", "no", "falso", "off", "none", "null", ""}


def coercionar_tipos(spec: dict, args: dict) -> tuple[dict, list[str]]:
    """
    Cada campo, en el tipo que su esquema declara. Determinista y auditable.

    Dos vías traen texto donde el esquema dice booleano o número: el modelo, que
    devuelve `"8"` o `"true"` cuando le apetece, y la elección tipada de la
    consola, cuyo `valor` viaja **siempre** como cadena. Por la segunda, un
    `"false"` se convertía en `True` —`bool("false")` lo es— y la orden salía
    con lo contrario de lo que se eligió.

    Lo que no se puede convertir se deja como está y se avisa, igual que en
    `normalizar_enums`: sustituirlo por un valor por defecto sería el canal
    decidiendo.
    """
    out, avisos = dict(args), []
    for campo, decl in spec.get("esquema", {}).items():
        if campo not in out or out[campo] is None:
            continue
        tipo, valor = decl[0], out[campo]

        if tipo == "boolean" and isinstance(valor, str):
            clave = _sin_tildes(valor).strip()
            if clave in _VERDADEROS:
                out[campo] = True
            elif clave in _FALSOS:
                out[campo] = False
            else:
                avisos.append(f"«{valor}» no es sí ni no, para {campo}.")
        elif tipo in ("integer", "number") and isinstance(valor, str):
            try:
                num = float(valor.replace(",", "."))
                out[campo] = int(num) if tipo == "integer" else num
            except ValueError:
                avisos.append(f"«{valor}» no es un número, para {campo}.")
        elif tipo == "array" and isinstance(valor, str):
            # Una lista de uno, escrita sin corchetes. No es un error de la sala.
            out[campo] = [valor]
    return out, avisos


def corregir_lo_que_no_se_infiere(spec: dict, args: dict,
                                  texto: str) -> tuple[dict, list[str]]:
    """
    Devuelve `(argumentos, correcciones)`. Solo baja concesiones, nunca las sube.

    Si la sala lo dijo y el modelo no lo puso, eso NO se corrige aquí: ponerlo
    sería el canal concediendo, que es exactamente lo que esto impide. Se queda
    en el valor declarado, se dice en voz alta y la sala lo corrige con un
    botón.
    """
    t = _sin_tildes(texto)
    out, correcciones = dict(args), []
    for campo, marcas in NO_SE_INFIERE.items():
        if campo not in spec.get("esquema", {}):
            continue
        if not out.get(campo):
            continue
        if any(m in t for m in marcas):
            continue
        out[campo] = spec.get("por_defecto", {}).get(campo, False)
        correcciones.append(
            f"Nadie dijo «{campo.replace('_', ' ')}» en la orden: no se da por "
            f"puesto. Si lo hubo, dígalo y vuelva a interpretar."
        )
    return out, correcciones


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
                          "negociar el punto"],
     ["mesa nacional", "mesa con voceros", "concertacion previa", "condiciona"]),
    # La mesa del ALCALDE, que no es la del Interior: la suya solo vale en el
    # epicentro y no le pide permiso a nadie. Sin disparador propio, «instalar
    # mesa con voceros en X» caía en `abrir_mesa_local` —la del Ministro del
    # Interior— y la sala nunca se enteraba de que había cambiado de dueño.
    ("mesa_con_voceros", ["mesa con voceros", "mesa con los voceros",
                          "voceros del punto"], []),
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
    # Sin esta entrada, «redesplegar militares a la refinería» respondía que
    # ninguna acción del repertorio correspondía a eso — y sí corresponde: es la
    # del Ministro de Defensa. El canal no se equivocaba de acción: negaba tener
    # una que tiene.
    ("redesplegar_militares", ["redespleg", "redespliegue", "proyeccion aerea",
                               "proyeccion area"], []),
    ("fijar_registro_escrito", ["registro escrito", "responsable nominado",
                                "nodo unico"], []),
    ("fijar_lineas_rojas", ["lineas rojas", "linea roja"], []),
    ("exigir_protocolo_voceria", ["protocolo de voceria", "plazo suspensivo"], []),
    ("adoptar_criterio_priorizacion", ["criterio de priorizacion",
                                       "priorizar corredores", "priorizacion de corredores"], []),
    ("clasificar_parte", ["clasificar el parte", "parte clasificado",
                          "confirmado estimado"], []),
    ("condicionar_empleo_fuerza", ["condiciona", "concertacion previa"], []),
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


def verbo_reconocido(texto: str) -> str | None:
    """
    Qué acción del repertorio nombra un texto, aunque no diga sobre qué.

    Sirve para diagnosticar el silencio con precisión: «operen el puente» no es
    «esa acción no existe» —existe— sino «no se entendió sobre qué punto». Son
    dos correcciones distintas y la sala tiene 2,5 minutos de fase de órdenes.
    """
    t = _sin_tildes(texto)
    for nombre, raices, excluye in DISPARADORES:
        if any(x in t for x in excluye):
            continue
        if any(r in t for r in raices):
            return HERRAMIENTAS[nombre]["descripcion"].lower()
    return None


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

        # Las cantidades que la cláusula nombra. Sin esto, «concentrar 8
        # escuadrones» se ejecutaba con SEIS —el valor por defecto del motor— y
        # la lectura en voz alta no decía ningún número, así que la sala no
        # tenía dónde notarlo. Es la sustitución silenciosa de N4 otra vez, con
        # una cifra en lugar de una unidad.
        args.update(_numeros_de_la_clausula(spec, t_clausula))

        if "dupla" in t_clausula and nombre == "operar_punto":
            args["dupla_presente"] = True
        if "de noche" in t_clausula or "nocturn" in t_clausula:
            args["de_noche"] = True
        if "delimit" in t or "con limites" in t:
            args["delimitada"] = True

        # La Alcaldía, cuando la sala la nombra. Son DOS campos distintos con la
        # misma frase detrás: en una operación es un mitigador de riesgo, y en
        # una mesa del epicentro es el requisito de jurisdicción sin el cual la
        # acción no es viable. Ninguno de los dos se infiere: se dice o no.
        if _con_la_alcaldia(t_clausula):
            if nombre == "operar_punto":
                args["concertado_con_alcaldia"] = True
            elif nombre == "abrir_mesa_local":
                args["con_alcaldia"] = True

        responsable = _responsable_de_la_clausula(crudo_clausula)
        if responsable and "responsable_nominado" in spec.get("esquema", {}):
            args["responsable_nominado"] = responsable

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


def _con_la_alcaldia(t_clausula: str) -> bool:
    return any(m in t_clausula for m in MARCAS_ALCALDIA)


# Quién firma. `responsable_nominado` no es adorno: con el registro escrito
# adoptado, es lo que hace ATRIBUIBLE un incidente, y la vista privada muestra
# «— SIN NOMBRE —» cuando falta. Sin extraerlo, esa mecánica entera quedaba
# muerta en cuanto el ejercicio corría sin llave.
_RESPONSABLE = re.compile(
    r"responsab\w*\s*(?:es|:|,)?\s*(?:el|la)?\s*"
    r"([A-Za-zÀ-ÿ][\wÀ-ÿ]*(?:\s+(?:de|del|la|el)?\s*[A-Za-zÀ-ÿ][\wÀ-ÿ]*){0,3})",
    re.IGNORECASE)


def _responsable_de_la_clausula(crudo_clausula: str) -> str | None:
    m = _RESPONSABLE.search(crudo_clausula)
    if not m:
        return None
    nombre = " ".join(m.group(1).split()).strip(" ,.;")
    return nombre or None


def _numeros_de_la_clausula(spec: dict, t_clausula: str) -> dict:
    """
    Las cantidades que la cláusula nombra, para los campos numéricos declarados.

    Se toma el PRIMER número de la cláusula y solo si la herramienta declara un
    campo numérico: no se reparten cifras entre campos, porque adivinar cuál es
    cuál sería el canal decidiendo. Con una sola cifra por cláusula —que es como
    se habla— basta.
    """
    campos = [c for c, decl in spec.get("esquema", {}).items()
              if decl[0] in ("integer", "number")]
    if len(campos) != 1:
        return {}
    m = re.search(r"\b(\d+(?:[.,]\d+)?)\b", t_clausula)
    if m is None:
        n = _numero_en_letras(t_clausula)
        return {campos[0]: n} if n is not None else {}
    crudo = m.group(1).replace(",", ".")
    return {campos[0]: float(crudo) if spec["esquema"][campos[0]][0] == "number"
            else int(float(crudo))}


# La sala dicta en voz alta y quien transcribe escribe lo que oye. «Ocho
# escuadrones» es tan común como «8».
NUMEROS_EN_LETRAS = {
    "un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11,
    "doce": 12,
}


def _numero_en_letras(t_clausula: str) -> int | None:
    for palabra in t_clausula.split():
        limpia = palabra.strip(" ,.;:()")
        if limpia in NUMEROS_EN_LETRAS:
            return NUMEROS_EN_LETRAS[limpia]
    return None


# Frases que PARECEN el principio de otra orden y son un parámetro de la
# anterior. «Operen el Puente Amarillo concertado con la Alcaldía» no son dos
# acciones: es una operación con su mitigador puesto. Sin esto, la raíz
# «concert» abría una mesa de concertación que nadie pidió —y, peor, se llevaba
# consigo el resto de la frase, así que la operación se quedaba sin el mitigador
# Y sin el responsable que venían detrás.
FRASES_PARAMETRO = (
    "concertado con", "concertada con", "concertados con", "concertadas con",
    "concertado previamente", "previa concertacion", "sin concertar",
)


def _tramos_parametro(t: str) -> list[tuple[int, int]]:
    tramos = []
    for f in FRASES_PARAMETRO:
        i = t.find(f)
        while i != -1:
            tramos.append((i, i + len(f)))
            i = t.find(f, i + 1)
    return tramos


def _clausulas(t: str) -> list[tuple[str, list[str], list[str], int, int]]:
    """
    Reparte el texto entre los disparadores que aparecen, por posición.

    Cada disparador se queda con el tramo que va desde donde aparece su raíz
    hasta donde empieza el siguiente. Es una heurística tosca —no analiza
    sintaxis— pero resuelve el caso que importa: que el complemento de una orden
    no se lo lleve otra.
    """
    tramos = _tramos_parametro(t)

    def _primera_posicion(raiz: str) -> int:
        """La primera aparición que NO esté dentro de un parámetro de otra."""
        i = t.find(raiz)
        while i != -1:
            if not any(a <= i < b for a, b in tramos):
                return i
            i = t.find(raiz, i + 1)
        return -1

    encontrados = []
    for nombre, raices, excluye in DISPARADORES:
        posiciones = [i for i in (_primera_posicion(r) for r in raices) if i >= 0]
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
