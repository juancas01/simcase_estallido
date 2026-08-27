"""
entorno.py — CAPA 3 · los seis agentes que pueblan el mundo.

    Comité del Paro · prensa nacional · prensa internacional · redes ·
    gremios · alcaldes de entorno

**Producen contenido y SOLO contenido.** No mutan el estado, no abren un
corredor, no provocan un incidente y no cambian una cifra. El motor ya calculó
lo que pasó; ellos lo narran desde su sesgo.

    Si un actor autónomo pudiera mutar el estado, el ejercicio dejaría de ser
    reproducible y sería imposible atribuir un resultado a las decisiones de los
    participantes.

PRESUPUESTO DE LATENCIA
-----------------------
Seis agentes, cinco turnos y cuatro interludios dan entre 40 y 50 invocaciones.
La fase de consecuencias dura sesenta segundos con ocho personas mirando la
pantalla. Por eso:

    * una sola llamada por turno, no seis
    * presupuesto de tiempo duro
    * si el proveedor tarda o falla, **contenido de plantilla**, y se dice que
      es de plantilla

El ejercicio nunca se queda esperando a un modelo.
"""

from __future__ import annotations

import json

from src.engine.state import Estado
from src.agents.config import cliente, config


AGENTES = {
    "comite_del_paro": {
        "nombre": "Comité Nacional del Paro",
        "cadencia": 1,
        "sesgo": ("La contraparte. Evalúa si el Gobierno cumple lo que ofrece. "
                  "Endurece cuando se opera el día de una sesión; se fragmenta "
                  "cuando la mesa se prolonga sin resultado."),
    },
    "prensa_nacional": {
        "nombre": "Prensa nacional",
        "cadencia": 1,
        "sesgo": ("Busca la noticia del día y fija el encuadre. Titula sobre lo "
                  "más visible, no sobre lo más importante."),
    },
    "prensa_internacional": {
        "nombre": "Prensa internacional",
        "cadencia": 2,
        "sesgo": ("Umbral más alto: solo cubre víctimas, militares en control de "
                  "multitudes y pronunciamientos de organismos. Traduce hechos en "
                  "exposición."),
    },
    "redes": {
        "nombre": "Redes sociales",
        "cadencia": 1,
        "sesgo": ("Rápidas, emocionales y sin verificar. Amplifican imágenes y "
                  "también rumores que nadie ha confirmado."),
    },
    "gremios": {
        "nombre": "Gremios camioneros y comercio",
        "cadencia": 2,
        "sesgo": ("Miden en días de inmovilización y en pérdidas. Empujan hacia "
                  "el escalamiento y amenazan con sumarse."),
    },
    "alcaldes_entorno": {
        "nombre": "Alcaldes de otras ciudades",
        "cadencia": 2,
        "sesgo": ("Reclaman tratamiento para su ciudad y leen cualquier repliegue "
                  "como abandono territorial."),
    },
}

SISTEMA = """Eres un generador de contenido para la esfera pública de un simulador
de crisis sobre un paro nacional en un país FICTICIO.

REGLAS QUE NO PUEDES ROMPER:
- Solo escribes CONTENIDO: titulares, publicaciones, comunicados y reacciones.
- NO decides nada. No abres corredores, no causas incidentes, no fijas cifras.
- Escribes SOBRE HECHOS QUE YA OCURRIERON y que se te entregan. No inventes
  hechos nuevos: reacciona a los que están en los datos.
- Usa SOLO los nombres de lugar que aparecen en los datos. Son ficticios.
- Nada de nombres de personas reales, partidos reales ni instituciones reales de
  ningún país.
- Cada publicación: una o dos frases. Es un titular o un tuit, no un artículo.
- NO empieces el texto repitiendo el nombre de la fuente: la pantalla ya lo pone
  al lado, y «Prensa nacional: Prensa nacional informa…» es lo que sale si lo
  haces.
- El campo `fuente` es la CLAVE que se te da en `fuentes_que_publican`
  —`prensa_nacional`, `redes`…—, no el nombre para mostrar. Una fuente que no
  esté en esa lista no se publica.
- Respeta el sesgo de cada fuente: es lo que hace visible que el mismo hecho se
  cuenta de cuatro maneras distintas.

Devuelve JSON: {"publicaciones": [{"fuente": "...", "texto": "...",
"sin_verificar": true/false}]}"""


def publicaciones(estado: Estado, eventos: list[dict],
                  historial_reciente: list[str] | None = None) -> dict:
    """
    Lo que la esfera pública dice este turno.

    Devuelve `{"publicaciones": [...], "generado_por": "..."}`. Si no hay llave o
    el proveedor falla, las publicaciones vienen de plantilla y `generado_por` lo
    dice — para que nadie confunda una cosa con la otra.
    """
    hechos = _hechos_del_turno(estado, eventos)
    if not hechos:
        return {"publicaciones": [], "generado_por": "sin hechos que narrar"}

    c = cliente()
    if c is None:
        return {"publicaciones": _plantilla(estado, hechos),
                "generado_por": "plantilla (sin llave de API)"}

    cfg = config()
    activos = [k for k, v in AGENTES.items()
               if estado.turno_decision % v["cadencia"] == 0 or v["cadencia"] == 1]

    try:
        respuesta = c.chat.completions.create(
            model=cfg.modelo_entorno,
            messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": json.dumps({
                    "turno": estado.turno_decision,
                    "franja": estado.franja,
                    "encuadre_dominante": estado.encuadre_dominante,
                    "hechos_del_turno": hechos,
                    "fuentes_que_publican": [
                        {"fuente": k, "nombre": AGENTES[k]["nombre"],
                         "sesgo": AGENTES[k]["sesgo"]}
                        for k in activos
                    ],
                    "no_repetir": historial_reciente or [],
                }, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            timeout=cfg.timeout_entorno,
            **cfg.extra_entorno(),
        )
        datos = json.loads(respuesta.choices[0].message.content or "{}")
        pubs = _de_fuentes_conocidas(datos.get("publicaciones") or [])
        if not pubs:
            raise ValueError("respuesta vacía o sin ninguna fuente reconocible")
        for p in pubs:
            p["turno"] = estado.turno_decision
        return {"publicaciones": pubs[:6], "generado_por": cfg.modelo_entorno}
    except Exception as exc:                                   # pragma: no cover
        # Ocho personas no pueden quedarse mirando la pantalla porque un
        # proveedor tardó. Se degrada y se dice.
        return {"publicaciones": _plantilla(estado, hechos),
                "generado_por": f"plantilla (el modelo falló: {type(exc).__name__})"}


# Cómo se puede nombrar cada una de las seis. El modelo devuelve unas veces la
# clave y otras el nombre para mostrar, y la pantalla rotula por clave.
_ALIAS_FUENTE = {
    **{k: k for k in AGENTES},
    **{v["nombre"].lower(): k for k, v in AGENTES.items()},
}


def _de_fuentes_conocidas(pubs: list) -> list[dict]:
    """
    **Solo publican las seis.** Y con la clave canónica, no con lo que el modelo
    haya escrito esa vez.

    Dos cosas distintas, y las dos importan. La primera es de rótulo: el campo
    volvía unas veces como `comite_del_paro` y otras como «Comité Nacional del
    Paro», y la pantalla rotula por clave. La segunda no es de rótulo: un
    `fuente` inventado es **contenido atribuido a un medio que no existe** en un
    ejercicio cuyo objeto es la distancia entre lo que el Estado tiene por cierto
    y lo que se dice. Atribuirlo mal es peor que no publicarlo.
    """
    salida = []
    for p in pubs:
        if not isinstance(p, dict):
            continue
        clave = _ALIAS_FUENTE.get(str(p.get("fuente", "")).strip().lower())
        if clave is None or not str(p.get("texto", "")).strip():
            continue
        salida.append({**p, "fuente": clave})
    return salida


def _hechos_del_turno(estado: Estado, eventos: list[dict]) -> list[dict]:
    """
    Los hechos que el motor YA calculó, extraídos como datos estructurados.

    Un canal que entrega al modelo un párrafo con totales agregados lo obliga a
    inventar en cuanto le preguntan por algo concreto. Aquí se le dan hechos, y
    su trabajo es solo ponerlos en prosa desde su sesgo.
    """
    hechos = []
    for ev in eventos:
        tipo, evento = ev.get("tipo"), ev.get("evento")
        nodo = estado.nodos.get(ev.get("nodo", ""))
        nombre = nodo.nombre if nodo else None

        if evento == "incidente_mortal":
            hechos.append({"que": "incidente con víctima en una operación de fuerza",
                           "donde": nombre})
        elif evento == "imagen_viral":
            hechos.append({"que": "una imagen del operativo circula ampliamente",
                           "donde": nombre})
        elif evento == "militares_en_multitudes":
            hechos.append({"que": "se emplearon militares en control de multitudes"})
        elif tipo == "reapertura":
            hechos.append({"que": "un punto abierto por la fuerza volvió a cerrarse "
                                  "durante la noche", "donde": nombre})
        elif tipo == "apertura":
            hechos.append({"que": f"un punto se abrió por {ev.get('via')}",
                           "donde": nombre})
        elif tipo == "acuerdo_cumplido":
            hechos.append({"que": "el Gobierno cumplió lo pactado en la mesa"})
        elif tipo == "acuerdo_roto" or tipo == "acuerdo_incumplido":
            hechos.append({"que": "se rompió un acuerdo de la mesa",
                           "detalle": ev.get("motivo")})
        elif tipo == "muertes_evitables":
            r = estado.regiones.get(ev.get("region", ""))
            hechos.append({"que": "muertes por falta de oxígeno medicinal",
                           "donde": r.nombre if r else None, "cuantas": ev.get("n")})
        elif tipo == "escolta_atacada":
            hechos.append({"que": "una caravana escoltada fue atacada en ruta"})
        elif tipo == "escolta_lograda":
            hechos.append({"que": "una caravana llegó a su destino con escolta"})
        elif tipo == "duda_permanencia":
            hechos.append({"que": "la Defensoría puso en duda públicamente su "
                                  "permanencia en la mesa"})
        elif tipo == "gremios_se_suman":
            hechos.append({"que": "los gremios camioneros se sumaron al paro"})
        elif tipo == "ultimatum_gremios":
            hechos.append({"que": "los gremios dieron un ultimátum de 48 horas"})
        elif tipo == "calendario_difundido":
            hechos.append({"que": "se difundió el calendario de agotamiento de "
                                  "combustible y oxígeno"})
        elif tipo == "jornada_nacional":
            hechos.append({"que": "jornada nacional de movilización convocada"})
        elif tipo == "denuncia_estallo":
            hechos.append({"que": "una denuncia grave sin verificar salió a la luz",
                           "declarada_en_verificacion": ev.get("declarada")})
        elif tipo == "nodo_nuevo":
            hechos.append({"que": "apareció un punto de cierre nuevo", "donde": nombre})

    # Las denuncias abiertas son contexto permanente, no un hecho del turno
    abiertas = [d for d in estado.denuncias if not d.verificada and not d.estallo]
    if abiertas:
        hechos.append({"que": f"{len(abiertas)} denuncia(s) grave(s) circulan sin "
                              f"verificar"})
    return hechos[:8]


def _plantilla(estado: Estado, hechos: list[dict]) -> list[dict]:
    """
    Contenido determinista. Menos rico, y suficiente para que el ejercicio corra.

    Es la degradación que hace cierta la regla de la arquitectura: **el motor
    corre entero sin llamar a ningún modelo de lenguaje.**
    """
    out = []
    for h in hechos[:5]:
        que = h["que"]
        donde = f" en {h['donde']}" if h.get("donde") else ""
        if "víctima" in que or "imagen" in que:
            out.append({"fuente": "prensa_nacional",
                        "texto": f"Reportan {que}{donde}.",
                        "sin_verificar": False, "turno": estado.turno_decision})
        elif "cerrarse" in que or "punto de cierre nuevo" in que:
            out.append({"fuente": "redes",
                        "texto": f"Circula que {que}{donde}.",
                        "sin_verificar": True, "turno": estado.turno_decision})
        elif "pactado" in que or "acuerdo" in que:
            out.append({"fuente": "comite_del_paro",
                        "texto": f"El Comité se pronuncia: {que}.",
                        "sin_verificar": False, "turno": estado.turno_decision})
        elif "oxígeno" in que:
            out.append({"fuente": "prensa_internacional",
                        "texto": f"Organismos internacionales advierten por {que}{donde}.",
                        "sin_verificar": False, "turno": estado.turno_decision})
        elif "gremios" in que or "camioneros" in que:
            out.append({"fuente": "gremios",
                        "texto": f"Los gremios informan: {que}.",
                        "sin_verificar": False, "turno": estado.turno_decision})
        else:
            out.append({"fuente": "prensa_nacional",
                        "texto": f"{que.capitalize()}{donde}.",
                        "sin_verificar": False, "turno": estado.turno_decision})
    return out
