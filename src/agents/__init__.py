"""
src/agents — Las dos capas de lenguaje natural.

    CAPA 4 · nlu.py       traduce lo que la sala dijo a acciones tipadas
    CAPA 3 · entorno.py   los seis agentes que pueblan el mundo

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

**Nada de esto es obligatorio.** El motor corre entero sin llamar a ningún modelo
de lenguaje; si falta la llave o el proveedor falla, las dos capas degradan a
contenido determinista y el ejercicio sigue. Esa degradación es la prueba
operativa de que ninguna decisión de la simulación se delegó al modelo.

DÓNDE SE ESCRIBE LA LLAVE
-------------------------
En `.env`, en la raíz del repositorio. Copie `.env.example` y rellene
`OPENAI_API_KEY`. Ver `config.py`.
"""

from src.agents.config import config, cliente          # noqa: F401
