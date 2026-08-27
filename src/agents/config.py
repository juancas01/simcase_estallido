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
    reintentos: int
    esfuerzo_nlu: str
    esfuerzo_entorno: str

    def extra_nlu(self) -> dict:
        return {"reasoning_effort": self.esfuerzo_nlu} if self.esfuerzo_nlu else {}

    def extra_entorno(self) -> dict:
        return ({"reasoning_effort": self.esfuerzo_entorno}
                if self.esfuerzo_entorno else {})

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
            "reintentos": self.reintentos,
            "esfuerzo_nlu": self.esfuerzo_nlu or "por defecto del modelo",
            "esfuerzo_entorno": self.esfuerzo_entorno or "por defecto del modelo",
            "espera_maxima_nlu_s": self.timeout_nlu * (self.reintentos + 1),
            "espera_maxima_entorno_s": self.timeout_entorno * (self.reintentos + 1),
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
        reintentos=int(os.getenv("REINTENTOS_LLM", "0")),
        # EL ESFUERZO DE RAZONAMIENTO, MEDIDO Y NO SUPUESTO.
        #
        # Con el valor de fábrica de gpt-5-nano, la CAPA 3 tardaba entre 22 y
        # 36 s y **nunca** entraba en su presupuesto de 20: la esfera pública
        # salía de plantilla en el 100 % de los turnos, en un montaje que la
        # anuncia con seis agentes y su sesgo. Y la CAPA 4 tenía una mediana de
        # 8,0 s con la cola pegada al presupuesto de 12.
        #
        # Medido sobre nueve órdenes difíciles y tres turnos de esfera:
        #
        #   esfuerzo    capa 4                       capa 3
        #   ---------------------------------------------------------------
        #   (fábrica)   mediana 8,0 s · 9/9 bien     26–36 s · SIEMPRE fuera
        #   low         mediana 2,2 s · 9/9 bien     7,1–7,5 s · dentro
        #   minimal     mediana 0,8 s · 6/9 bien     3,1–5,1 s · dentro
        #
        # `minimal` queda descartado para la capa 4 y no por poco: con él,
        # «declaren el estado de sitio» llamaba a `firmar_asistencia_militar`
        # —forzar la acción más parecida, que es el modo de falla F5— y una
        # orden compuesta perdía la mitad. Se descarta también para la capa 3
        # por simetría: allí las reglas que importan son «no inventes hechos» y
        # «nombres ficticios», y son instrucciones que conviene que se lean.
        #
        # Vacío = no se manda el parámetro. Hace falta ponerlo así si se apunta
        # `MODELO_*` a un modelo que no razona o a otro proveedor, que lo
        # rechazarían.
        esfuerzo_nlu=os.getenv("ESFUERZO_NLU", "low"),
        esfuerzo_entorno=os.getenv("ESFUERZO_ENTORNO", "low"),
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
    # EL PRESUPUESTO DE LATENCIA TIENE QUE SER DURO, y con el valor por defecto
    # del SDK no lo era. `max_retries` vale 2 de fábrica: un `timeout` de 12 s se
    # convertía en TRES intentos y hasta 36 s de reloj, más la espera entre
    # reintentos. Medido en una sonda real: 35,3 s con el presupuesto puesto en
    # 12. Ocho personas mirando la pantalla durante 35 s es exactamente lo que
    # esta capa promete que no puede pasar.
    #
    # Con `REINTENTOS_LLM=0`, el presupuesto declarado es el que se espera. Quien
    # prefiera pagar un reintento a cambio de menos degradaciones lo sube en
    # `.env`, y `/api/config` dice cuál es la espera máxima resultante.
    kwargs = {"api_key": c.api_key, "max_retries": c.reintentos}
    if c.base_url:
        kwargs["base_url"] = c.base_url
    return OpenAI(**kwargs)
