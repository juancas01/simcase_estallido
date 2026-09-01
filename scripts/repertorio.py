# -*- coding: utf-8 -*-
"""
Escribe `docs/GUIA_DE_ACCIONES.md` leyendo el catálogo del motor.

ES EL MISMO CONTENIDO QUE LA PANTALLA, EN PAPEL. La guía de acciones vive en el
tablero individual de cada titular y ahí se ve una sola cartera, la propia. Este
documento es la vista de arriba: las nueve a la vez, para preparar la sesión,
para repartirla impresa, y para que quien facilita pueda contestar «¿y esto qué
hace?» sin abrir nueve pestañas.

POR QUÉ SE GENERA Y NO SE ESCRIBE. Un cuarto documento con las treinta y nueve
acciones copiadas a mano es un cuarto documento que se desincroniza. Este lee
`actions.catalogo_por_rol()`, que es la misma llamada que sirve la API a la
pantalla: si una acción cambia de nombre, de requisito o de ejemplo, cambia
aquí en la siguiente corrida y no hay una segunda versión de la verdad.

    uv run python scripts/repertorio.py

Lo que NO trae, y es deliberado: ni una cifra del motor. Cuánto cuesta cada cosa
está en `parameters.py` y en el comentario de cada acción, en el código. Este es
el de la sala, y en la sala un número es algo que se optimiza.
"""

from __future__ import annotations

import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from src.engine import actions          # noqa: E402
from src.engine.views import ROLES      # noqa: E402

# El título con el que cada rol se presenta en la sala. Es el mismo de
# `web_ui/src/comun.jsx`; el motor solo conoce el identificador corto, porque
# para él un rol es una clave y no una persona.
TITULOS = {
    "Presidente": "Presidente de la República",
    "Interior": "Ministro del Interior",
    "Alcalde": "Alcalde de la ciudad epicentro",
    "Defensa": "Ministro de Defensa",
    "Policía": "Director General de la Policía",
    "Transporte": "Ministro de Transporte",
    "Agricultura": "Ministro de Agricultura y Desarrollo Rural",
}

# Las tres categorías, con el nombre que se usa delante de la sala. El motor las
# llama `constitutiva`, `operativa` e `informativa` —vocabulario de diseño, y
# ahí se queda—; lo que se lee es la palabra corriente.
TIPOS = {
    "constitutiva": "Protocolo",
    "operativa": "Operación",
    "informativa": "Información",
}

def celda(texto: str) -> str:
    """Un párrafo del código metido en una celda de tabla, sin romperla."""
    return re.sub(r"\s+", " ", texto or "").strip().replace("|", "\\|")

def documento() -> str:
    cat = actions.catalogo_por_rol()

    L: list[str] = []
    w = L.append

    w("# Guía de acciones")
    w("")
    w("Las **treinta y nueve** cosas que se pueden pedir en este ejercicio, una")
    w("por una y en lenguaje corriente: cómo se llama cada una, qué hace, qué")
    w("tiene que existir antes, y una frase que funciona tal cual dicha en voz")
    w("alta delante de la consola.")
    w("")
    w("**Es la misma guía que cada titular tiene en su tablero**, con las nueve")
    w("carteras a la vez. En pantalla cada quien ve la suya y además el semáforo")
    w("de hoy —si hoy sale o qué falta—; eso cambia cada jornada y por eso no")
    w("está aquí. Lo de aquí no cambia nunca.")
    w("")
    w("> **Se genera desde el código y no se edita a mano.**")
    w("> `uv run python scripts/repertorio.py`. Si una acción cambia, cambia aquí")
    w("> en la siguiente corrida — no hay una segunda versión de la verdad.")
    w("")
    w("> **Sin una sola cifra, a propósito.** Cuánto cuesta cada cosa está en")
    w("> el código: `parameters.py` y el comentario de cada acción. Este es el de")
    w("> la sala, y **un nivel se interpreta; un número se")
    w("> optimiza**.")
    w("")
    w("---")
    w("")
    w("## Los tres tipos de acción")
    w("")
    w("| Tipo | Qué cambia | Cuándo se nota |")
    w("|---|---|---|")
    w("| **Protocolo** | cómo trabaja la mesa: quién habla, quién firma, con qué "
      "reglas | no se ve en el mapa · rinde en todo lo que venga después |")
    w("| **Operación** | el mundo: el territorio, la fuerza, el abastecimiento | "
      "de inmediato |")
    w("| **Información** | lo que el país tiene por cierto | en la esfera pública |")
    w("")
    w("**Ninguna está bloqueada y todas están tarifadas.** El ejercicio no obliga")
    w("a nadie a empezar por los protocolos: permite saltárselos y cobra la")
    w("diferencia después.")
    w("")
    w("## Cómo se pide una acción")
    w("")
    w("**No hay comandos.** Se escribe en la consola lo que se quiere hacer, con")
    w("las palabras de siempre, y el canal de órdenes lo traduce. Los ejemplos de")
    w("la última columna son el esqueleto mínimo: funcionan tal cual, y se pueden")
    w("decir de otras maneras y con otros datos.")
    w("")
    w("**La orden la puede escribir cualquiera que esté sentado a la consola**, no")
    w("necesariamente quien tiene el rol. Decir en voz alta de parte de quién va")
    w("es lo que mantiene la trazabilidad de quién decidió qué — y eso no lo")
    w("comprueba el sistema, lo sostiene la sala.")
    w("")
    w("**Lo que no se dice, no se da por puesto.** Una operación en la que nadie")
    w("dijo «militares» se ejecuta con ESMAD; una mesa en la que nadie dijo «con")
    w("la Alcaldía» se abre sin ella. Si hace falta un dato —qué unidad, con quién,")
    w("delimitada, de noche—, hay que decirlo con esas mismas palabras.")
    w("")
    w("Los nombres de puntos, corredores y regiones son los del escenario, y están")
    w("en el mapa del tablero general.")
    w("")
    w("---")
    w("")

    for i, rol in enumerate(ROLES, start=1):
        fichas = cat.get(rol, [])
        w("## %02d · %s" % (i, TITULOS.get(rol, rol)))
        w("")
        w("| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |")
        w("|---|---|---|---|---|")
        for f in fichas:
            # Ninguna ficha llega sin ejemplo: hay una prueba que lo exige.
            ejemplo = "`%s`" % celda(f["ejemplo_consola"])
            w("| **%s** | %s | %s | %s | %s |" % (
                celda(f["nombre"]),
                TIPOS.get(f["clase"], f["clase"]),
                celda(f["en_claro"]),
                celda(f["requisitos_previos"]) or "—",
                ejemplo,
            ))
        w("")

    w("---")
    w("")
    w("## Apéndice · el nombre formal de cada acto")
    w("")
    w("El nombre corriente es el que se usa hablando. El **nombre formal** es el")
    w("que queda escrito en el pliego de la sesión, y es el que hay que citar")
    w("cuando se reconstruye después quién ordenó qué. El tercero es el nombre en")
    w("el código, para quien tenga que buscarlo en")
    w("[`actions.py`](../src/engine/actions.py).")
    w("")
    w("| Se dice | Se escribe en el pliego | En el código |")
    w("|---|---|---|")
    for rol in ROLES:
        for f in cat.get(rol, []):
            w("| %s | %s | `%s` |" % (
                celda(f["nombre"]), celda(f["descripcion"]), f["accion"]))
    w("")
    return "\n".join(L)

if __name__ == "__main__":
    destino = os.path.join(RAIZ, "docs", "GUIA_DE_ACCIONES.md")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(documento())
    print("escrito: docs/GUIA_DE_ACCIONES.md")
