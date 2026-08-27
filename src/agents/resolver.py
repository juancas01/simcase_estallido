"""
resolver.py — Resolución de entidades, DETERMINISTA y sin modelo.

Traduce lo que la gente escribe —«el puente amarillo», «anillo hospitalario»,
«las cumbres»— a identificadores del motor, **sin modelo y sin adivinar**.

    Es la mejor relación esfuerzo/impacto de todo el sistema, y no toca ni el
    motor ni el modelo.

LOS CUATRO ESTADOS
------------------
    ok             una coincidencia clara            → se ejecuta
    ambiguo        varias candidatas, o parecido dudoso → SE PREGUNTA
    selector       no es un lugar sino un criterio   → lo resuelve el motor
    no_encontrado  nada se parece lo bastante        → se informa

LA REGLA CENTRAL
----------------
**Si un escalón produce más de una candidata, el resultado es `ambiguo`. Nunca se
toma la primera.**

Quedarse con la primera coincidencia parcial produce el peor fallo posible: la
orden **se ejecuta en el lugar equivocado y nadie se entera**. En la simulación
anterior eso mandaba ayuda al barrio equivocado. Aquí manda **ESMAD al punto
equivocado**.

UN MATIZ QUE COSTÓ DESCUBRIR
----------------------------
Si el texto es el nombre oficial completo, gana — aunque sea prefijo de otro. La
salvaguarda de ambigüedad es para formas derivadas, no para el nombre exacto.
Sin esto, un desplegable de nombres oficiales ofrece opciones que el sistema
luego repregunta.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Literal

from src.engine.state import Estado

Estado4 = Literal["ok", "ambiguo", "selector", "no_encontrado"]

UMBRAL_ACEPTAR = 0.90
UMBRAL_PREGUNTAR = 0.75

# Por debajo de esto no se sugiere nada: tres nombres al azar porque son los
# menos malos de veinticuatro no son una ayuda, son ruido con forma de ayuda.
UMBRAL_SUGERIR = 0.40

# Si el catálogo del tipo es corto, se enumera entero en vez de sugerir. Con
# cuatro regiones o cinco corredores, la lista completa resuelve la duda de una.
CATALOGO_CORTO = 6

# Prefijos que la gente escribe y que no distinguen nada
PREFIJOS = (
    "el ", "la ", "los ", "las ", "punto ", "punto de ", "nodo ", "cierre ",
    "corredor ", "corredor de ", "region ", "región ", "bloqueo ", "bloqueo de ",
)

# Selectores: no son lugares, son criterios. Los resuelve el motor.
#
# OJO: las claves se normalizan al final del modulo con `normalizar()`, que quita
# el articulo. Sin eso, «el mas duro» llegaba aqui como «mas duro» y CUATRO
# criterios documentados no funcionaban nunca. Escribalos en lenguaje natural; la
# normalizacion los deja como toca.
_SELECTORES_CRUDOS = {
    "todos": "todos los puntos",
    "todos los puntos": "todos los puntos",
    "los cerrados": "puntos cerrados",
    "cerrados": "puntos cerrados",
    "el mas duro": "el punto más duro",
    "el más duro": "el punto más duro",
    "el mas critico": "el punto más crítico",
    "el más crítico": "el punto más crítico",
    "el que bloquea": "el punto que bloquea el corredor",
    "sin verificar": "puntos sin verificar",
}


@dataclass
class Resolucion:
    crudo: str
    estado: Estado4
    entidad_id: str | None = None
    nombre: str | None = None
    tipo: str | None = None            # punto | corredor | region
    candidatos: list[dict] = field(default_factory=list)
    selector: str | None = None
    puntaje: float = 0.0

    # De qué argumento de la herramienta salió. Viaja hasta la pantalla para que
    # el botón de corregir sepa qué campo está corrigiendo. Antes lo adivinaba
    # el frontend buscando el valor crudo entre los argumentos, y para los
    # campos de lista —los tres puntos de `asignar_duplas`— no lo encontraba
    # nunca: caía en `nodo_id`, que esa herramienta no declara, y la corrección
    # moría en un 400.
    campo: str | None = None

    # Por que no se encontro, cuando se puede saber. Un «no existe» a secas
    # obliga a la sala a adivinar que escribio mal; una pista la deja corregir
    # en un segundo, sin que el sistema decida nada por ella.
    pista: str | None = None

    def eco(self) -> str:
        """
        Lo que se le lee de vuelta a la sala. **Siempre con el nombre completo.**

        Acertar mal en silencio aquí no manda ayuda al barrio equivocado: manda
        ESMAD al punto equivocado.
        """
        if self.estado == "ok":
            return f"«{self.crudo}» → {self.nombre} ({self.entidad_id})"
        if self.estado == "selector":
            return f"«{self.crudo}» → criterio: {self.selector}"
        if self.estado == "ambiguo":
            opciones = ", ".join(c["nombre"] for c in self.candidatos[:4])
            return f"«{self.crudo}» es ambiguo. ¿Cuál de estos?: {opciones}"
        return (self.pista or
                f"«{self.crudo}» no corresponde a ningún punto, corredor ni región.")


def normalizar(texto: str) -> str:
    t = texto.strip().lower()
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if unicodedata.category(c) != "Mn")
    for p in PREFIJOS:
        pn = "".join(c for c in unicodedata.normalize("NFD", p)
                     if unicodedata.category(c) != "Mn")
        if t.startswith(pn):
            t = t[len(pn):]
            break
    return " ".join(t.split())


def _catalogo(estado: Estado) -> list[dict]:
    out = []
    for n in estado.nodos.values():
        out.append({"id": n.nodo_id, "nombre": n.nombre, "tipo": "punto"})
    for c in estado.corredores.values():
        out.append({"id": c.corredor_id, "nombre": c.nombre, "tipo": "corredor"})
    for r in estado.regiones.values():
        out.append({"id": r.region_id, "nombre": r.nombre, "tipo": "region"})
    return out


def resolver(estado: Estado, crudo: str, tipo: str | None = None) -> Resolucion:
    """
    Cinco escalones, en orden. El primero que produce una única candidata gana.

    `tipo` acota la búsqueda cuando la herramienta ya sabe qué espera —un
    corredor, por ejemplo—, y evita ambigüedades que no lo eran.
    """
    if not crudo or not crudo.strip():
        return Resolucion(crudo=crudo, estado="no_encontrado")

    n = normalizar(crudo)
    completo = _catalogo(estado)
    catalogo = [x for x in completo if tipo is None or x["tipo"] == tipo]

    # 0 · ¿es un selector y no un lugar?
    if n in SELECTORES:
        return Resolucion(crudo=crudo, estado="selector", selector=SELECTORES[n])

    # 1 · identificador literal (N003, C-HOS, R-CUM)
    directo = [x for x in catalogo if x["id"].lower() == n]
    if len(directo) == 1:
        return _ok(crudo, directo[0], 1.0)

    # 2 · nombre oficial exacto. GANA aunque sea prefijo de otro.
    exactos = [x for x in catalogo if normalizar(x["nombre"]) == n]
    if len(exactos) == 1:
        return _ok(crudo, exactos[0], 1.0)
    if len(exactos) > 1:
        return _ambiguo(crudo, exactos)

    # 3 · todas las palabras del texto aparecen en el nombre
    tokens = set(n.split())
    por_tokens = [x for x in catalogo
                  if tokens and tokens <= set(normalizar(x["nombre"]).split())]
    if len(por_tokens) == 1:
        return _ok(crudo, por_tokens[0], 0.95)
    if len(por_tokens) > 1:
        return _ambiguo(crudo, por_tokens)

    # 4 · difuso, con DOS umbrales
    puntuados = sorted(
        ((SequenceMatcher(None, n, normalizar(x["nombre"])).ratio(), x)
         for x in catalogo),
        key=lambda p: -p[0],
    )
    if not puntuados:
        return Resolucion(crudo=crudo, estado="no_encontrado")

    mejor, cand = puntuados[0]
    empatados = [x for s, x in puntuados if abs(s - mejor) < 0.02]

    if mejor >= UMBRAL_ACEPTAR and len(empatados) == 1:
        return _ok(crudo, cand, mejor)
    if mejor >= UMBRAL_PREGUNTAR:
        cercanos = [x for s, x in puntuados if s >= UMBRAL_PREGUNTAR][:5]
        return _ambiguo(crudo, cercanos, mejor)

    return _no_encontrado(estado, crudo, n, completo, puntuados, tipo, mejor)


def _no_encontrado(estado, crudo, n, completo, puntuados, tipo, mejor):
    """
    No se encontro **en el tipo que la herramienta esperaba**. Antes de decir que
    no existe, dos comprobaciones que ahorran una repregunta a ciegas.
    """
    # 1 · ¿Existe, pero es de otra clase? «operen el Anillo hospitalario» decía
    #     «no corresponde a ningún punto, corredor ni región» — y es un corredor.
    #     El filtro por tipo tapaba la única respuesta útil.
    if tipo is not None:
        otros = [x for x in completo if x["tipo"] != tipo
                 and (normalizar(x["nombre"]) == n or x["id"].lower() == n)]
        if len(otros) == 1:
            return Resolucion(
                crudo=crudo, estado="no_encontrado",
                pista=f"«{crudo}» no sirve aquí. "
                      f"{_pista_de_tipo(estado, otros[0], tipo)}")

    # 2 · ¿Se parece a algo de verdad? Se ofrecen para que la sala corrija de un
    #     vistazo. No se elige ninguna: eso sería adivinar.
    catalogo = [x for _, x in puntuados]
    cerca = [x for pu, x in puntuados if pu >= UMBRAL_SUGERIR][:3]
    if cerca:
        opciones = ", ".join(x["nombre"] for x in cerca)
        return Resolucion(
            crudo=crudo, estado="no_encontrado", candidatos=cerca, puntaje=mejor,
            pista=f"«{crudo}» no existe en el mapa. "
                  f"¿Quiso decir alguno de estos?: {opciones}")

    # 3 · No se parece a nada. Si el catálogo del tipo es corto, se enumera; si
    #     no, al menos se dice QUÉ CLASE de cosa se esperaba, que es lo que la
    #     versión anterior no decía.
    esperado = NOMBRE_TIPO.get(tipo or "", "punto, corredor ni región")
    if catalogo and len(catalogo) <= CATALOGO_CORTO:
        opciones = ", ".join(x["nombre"] for x in catalogo)
        return Resolucion(
            crudo=crudo, estado="no_encontrado", candidatos=catalogo, puntaje=mejor,
            pista=f"«{crudo}» no existe. Los que hay son: {opciones}.")
    return Resolucion(
        crudo=crudo, estado="no_encontrado", puntaje=mejor,
        pista=f"«{crudo}» no corresponde a ningún {esperado} del mapa.")


NOMBRE_TIPO = {"punto": "punto de cierre", "corredor": "corredor",
               "region": "región"}


def _pista_de_tipo(estado: Estado, x: dict, esperado: str) -> str:
    """
    «X es un corredor, no un punto» — y, si se puede, qué pedir en su lugar.

    Para un corredor se enumeran sus puntos, que son **públicos** (el tablero ya
    los trae). Nunca cuál de ellos lo bloquea: ese es el dato exclusivo del
    Ministro de Transporte y no puede salir por la consola.
    """
    soy = NOMBRE_TIPO.get(x["tipo"], x["tipo"])
    esp = NOMBRE_TIPO.get(esperado, esperado)
    base = f"{x['nombre']} es un {soy}, no un {esp}."

    if x["tipo"] == "corredor" and esperado == "punto":
        c = estado.corredores.get(x["id"])
        if c:
            nombres = [estado.nodos[i].nombre for i in c.nodos if i in estado.nodos]
            if nombres:
                return (f"{base} Un corredor se abre abriendo sus puntos: "
                        f"{', '.join(nombres)}.")
    if x["tipo"] == "punto" and esperado == "corredor":
        nodo = estado.nodos.get(x["id"])
        if nodo and nodo.corredor_id in estado.corredores:
            return (f"{base} Pertenece al corredor "
                    f"{estado.corredores[nodo.corredor_id].nombre}.")
    return base


def _ok(crudo: str, x: dict, puntaje: float) -> Resolucion:
    return Resolucion(crudo=crudo, estado="ok", entidad_id=x["id"],
                      nombre=x["nombre"], tipo=x["tipo"], puntaje=puntaje)


def _ambiguo(crudo: str, candidatos: list[dict], puntaje: float = 0.0) -> Resolucion:
    return Resolucion(crudo=crudo, estado="ambiguo", candidatos=candidatos,
                      puntaje=puntaje)


def nombres_citados(estado: Estado, texto: str) -> list[str]:
    """
    Qué nombres del mapa aparecen en un texto, aunque no se haya entendido nada.

    Sirve para diagnosticar el silencio: si alguien escribe «el Puente Amarillo,
    a ver qué hacemos» el canal no reconoce ninguna acción, y la respuesta útil no
    es «no se reconoció nada» sino **«se menciona el Puente Amarillo pero no qué
    hacer con él»**. Son dos correcciones distintas.
    """
    t = normalizar(texto)
    return [x["nombre"] for x in _catalogo(estado)
            if normalizar(x["nombre"]) in t]


# Las frases que son criterio y no lugar, tal como se escriben. El intérprete de
# reserva las necesita en crudo para reconocerlas dentro de una frase larga.
FRASES_SELECTOR = tuple(_SELECTORES_CRUDOS)


def expandir_selector(estado: Estado, selector: str) -> list[str]:
    """
    Un selector no es un lugar: es un criterio, y lo resuelve el motor.

    Devuelve identificadores. Con tope implícito: quien lo llama decide cuántos
    usar, porque el expansor de plan tiene su propio límite.
    """
    cerrados = [n for n in estado.nodos.values() if not n.abierto]
    if selector == "puntos cerrados":
        return [n.nodo_id for n in cerrados]
    if selector == "todos los puntos":
        return list(estado.nodos)
    if selector == "el punto más duro":
        return [max(cerrados, key=lambda n: n.dureza).nodo_id] if cerrados else []
    if selector == "el punto más crítico":
        peor = min(estado.regiones.values(), key=lambda r: r.dias_autonomia_oxigeno)
        de_region = [n for n in cerrados if n.region_id == peor.region_id]
        return [max(de_region, key=lambda n: n.dureza).nodo_id] if de_region else []
    if selector == "puntos sin verificar":
        return [n.nodo_id for n in estado.nodos.values()
                if n.ultima_verificacion_turno is None]
    if selector == "el punto que bloquea el corredor":
        out = []
        for c in estado.corredores.values():
            b = c.punto_que_bloquea(estado.nodos)
            if b:
                out.append(b)
        return out
    return []


# Las claves, ya normalizadas. Va al final porque `normalizar()` se define
# arriba. Una clave que no sobreviva a la normalización es una clave muerta, y
# durante varias versiones hubo cuatro.
SELECTORES = {normalizar(k): v for k, v in _SELECTORES_CRUDOS.items()}
