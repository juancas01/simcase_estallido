"""
conftest.py — La suite no sale a la red. Nunca, desde ningún archivo.

`test_canal_ordenes.py` traía su propio accesorio `sin_modelo`, y decía en su
cabecera que ninguna prueba llamaba a un modelo. **Era falso a medias, y por el
peor sitio: el que nadie miró.** El accesorio silenciaba `nlu`, pero las cinco
pruebas que pasan por `/api/consola/ejecutar` y `/api/consola/noche` disparan
después `_refrescar_esfera()`, que llama a la CAPA 3 —`entorno.py`— con el
cliente real.

Medido: la suite tardaba **176 s**, hacía llamadas facturadas contra la llave del
`.env` en cada corrida, y no corría sin conexión. Con las dos capas silenciadas,
`test_canal_ordenes.py` pasa en **0,9 s**.

Se silencian aquí, en `conftest.py` y con `autouse`, y no en cada archivo: un
accesorio por archivo es exactamente lo que dejó la mitad del agujero abierto.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """
    Las DOS capas de lenguaje natural, en su rama determinista.

    Además de hacer la suite reproducible y gratuita, esto prueba algo del
    diseño: **el ejercicio entero funciona sin llave.** Si alguna prueba dejara
    de pasar al quitar el modelo, la degradación sería decorativa.
    """
    from src.agents import entorno, nlu

    monkeypatch.setattr(nlu, "cliente", lambda: None)
    monkeypatch.setattr(entorno, "cliente", lambda: None)


@pytest.fixture(autouse=True)
def sin_bitacora(monkeypatch):
    """
    La suite no escribe corridas en el repositorio.

    El archivo de la corrida (`B1`) va ENCENDIDO en producción — su condición
    es que lo escrito sobreviva al proceso—, pero cada `reload` del módulo de
    la API crearía una carpeta nueva por prueba. La comprobación de que el
    dato llega al archivo está en `test_bitacora.py`, que construye su bitácora
    apuntando a `tmp_path` y usa el motor directamente, sin pasar por aquí.
    """
    monkeypatch.setenv("SIMCASE_BITACORA", "off")
