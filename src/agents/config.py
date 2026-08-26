"""
config.py — De dónde salen la llave y el modelo.

    La llave se escribe en `.env`, en la raíz del repositorio.
    Copie `.env.example` a `.env` y rellene OPENAI_API_KEY.

`.env` está en `.gitignore`: no se sube nunca.

LA REGLA QUE NO SE TOCA
-----------------------
**El motor corre entero sin llamar a ningún modelo de lenguaje.** Este módulo y
todo lo que cuelga de él son opcionales: si la llave falta, si el proveedor
tarda o si la llamada revienta, las dos capas de lenguaje natural degradan a
contenido determinista y el ejercicio sigue.

No es tolerancia a fallos por cortesía: es la prueba operativa de que ninguna
decisión de la simulación se delegó al modelo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:                                   # pragma: no cover
    def load_dotenv(*_a, **_k):                       # type: ignore
        return False


RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")


@dataclass(frozen=True)
class Config:
    api_key: str | None
    base_url: str | None
    modelo_nlu: str
    modelo_entorno: str
    timeout_nlu: float
    timeout_entorno: float

    @property
    def disponible(self) -> bool:
        return bool(self.api_key)

    def diagnostico(self) -> dict:
        """Lo que la consola muestra al montar, para saber si hay modelo o no."""
        return {
            "llave_presente": self.disponible,
            "archivo_env": str(RAIZ / ".env"),
            "existe_env": (RAIZ / ".env").exists(),
            "modelo_nlu": self.modelo_nlu,
            "modelo_entorno": self.modelo_entorno,
            "timeout_nlu_s": self.timeout_nlu,
            "timeout_entorno_s": self.timeout_entorno,
            "sdk_instalado": _sdk_instalado(),
            "mensaje": (
                "Capas de lenguaje natural activas."
                if self.disponible and _sdk_instalado() else
                "Sin llave o sin SDK: la consola interpreta de forma determinista "
                "y la esfera pública usa plantillas. El ejercicio funciona igual."
            ),
        }


def _sdk_instalado() -> bool:
    try:
        import openai   # noqa: F401
        return True
    except ImportError:
        return False


@lru_cache(maxsize=1)
def config() -> Config:
    return Config(
        api_key=os.getenv("OPENAI_API_KEY") or None,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        modelo_nlu=os.getenv("MODELO_NLU", "gpt-5-nano"),
        modelo_entorno=os.getenv("MODELO_ENTORNO", "gpt-5-nano"),
        timeout_nlu=float(os.getenv("TIMEOUT_NLU", "12")),
        timeout_entorno=float(os.getenv("TIMEOUT_ENTORNO", "20")),
    )


@lru_cache(maxsize=1)
def cliente():
    """
    El cliente de OpenAI, o None si no hay llave o no está el SDK.

    Nunca lanza: quien lo llama comprueba `is None` y degrada.
    """
    c = config()
    if not c.disponible or not _sdk_instalado():
        return None
    from openai import OpenAI
    kwargs = {"api_key": c.api_key}
    if c.base_url:
        kwargs["base_url"] = c.base_url
    return OpenAI(**kwargs)
