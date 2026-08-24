# SIMCASE · El Estado frente al Estallido Social

Simulación de conducción de crisis sobre el Paro Nacional de 2021. Un Puesto de
Mando Unificado de ocho roles, dos horas de mundo real, y un motor que calcula
las consecuencias de lo que la sala decide.

**Escuela de Gobierno · Universidad de La Sabana**

---

## Qué es esto

Segundo caso de la línea de simulaciones aumentadas con IA, después de la
inundación de Macondo. Una sola diferencia ordena todo el diseño:

> **La lluvia no reacciona a lo que usted decide. Una movilización sí.**

El motor deja de simular daños y pasa a simular **retroalimentación**: cada
operación de fuerza, cada cifra desmentida y cada sesión de mesa modifica la
intensidad de aquello que se intenta contener. Abrir un corredor por la fuerza
puede cerrar dos, y eso sale de la aritmética del motor, no de un guion.

### Por dónde empezar

| Si quieres… | Lee |
|---|---|
| **entender cómo funciona la simulación** | [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) — explica el motor con los números reales que usa, sin necesidad de leer código |
| saber **por qué** está diseñado así | [`docs/propuesta_simulacion_estallido_social.md`](docs/propuesta_simulacion_estallido_social.md) — el documento de diseño completo |
| montar **otro** caso con esta arquitectura | [`docs/guia_arquitectura_simulaciones.md`](docs/guia_arquitectura_simulaciones.md) |

---

## Arranque rápido

```bash
# 1 · Dependencias (Python 3.13+)
uv sync --extra dev

# 2 · Correr un ejercicio completo, sin interfaz y sin LLM
uv run python scripts/correr_ejercicio.py

# 3 · Comparar estrategias — el criterio de calibración
uv run python scripts/correr_ejercicio.py --comparar

# 4 · Pruebas (sin modelo, < 1 s)
uv run pytest -q

# 5 · Interfaz
cd web_ui && npm install && npm run build && cd ..
uv run python -m src.api.main        # http://localhost:8000
```

No hace falta clave de API para nada de lo anterior. **El motor corre entero sin
llamar a ningún modelo de lenguaje.** Si algún día no puede, la arquitectura está
mal.

---

## Cómo está organizado

```
src/engine/          EL MOTOR. Único dueño del estado. Sin IA, determinista salvo
                     por una semilla registrada.
  parameters.py        todas las constantes, con nombre y unidad
  state.py             nodos, corredores, regiones, reservas, banderas
  loader.py            construye el estado heredado (t=0) desde data/
  mobilization.py      §4.1 · el adversario reflexivo
  force.py             §4.2 · capacidad, fatiga e incidentes
  aperture.py          §4.3 · las tres vías de abrir un corredor
  information.py       §4.4 · la verdad, las estimaciones y la versión
  supply.py            §4.5 · el reloj y el oxígeno medicinal
  actions.py           las acciones de los ocho roles
  simulation.py        el bucle de turnos

src/api/             capa delgada sobre el motor
src/agents/          capa 4 · canal de órdenes en LN (pendiente)
data/escenario/      el caso, en datos y no en código
web_ui/              las tres superficies
scripts/             corredor sin interfaz, para calibrar
tests/               verificadores sin modelo
```

---

## Las cinco decisiones de diseño

| | Decisión | Dónde vive |
|---|---|---|
| **1** | **El Estado no observa el mundo: lo estima.** Cada nodo tiene una `composicion_real` oculta, y cuatro fuentes la estiman con sesgos opuestos. | `information.py` |
| **2** | **Tres vías de abrir un corredor, con economías distintas.** La fuerza reabre esa misma noche; la concertación se sostiene; el desgaste es gratis y lento. | `aperture.py` |
| **3** | **El estándar de derechos es un multiplicador de riesgo**, no un discurso. Seis mitigadores dividen la probabilidad de incidente por casi cinco. | `force.py` |
| **4** | **Lo primero no es el territorio: es la mesa.** Seis acciones constitutivas no abren ningún corredor y modifican todo lo posterior. Nada está bloqueado; todo está tarifado. | `actions.py` |
| **5** | **Una sala, un teclado, ninguna pantalla individual.** | `web_ui/` |

---

## Dos invariantes que no se pueden romper

Ambas tienen prueba automática. Si fallan, el ejercicio pierde su objeto sin que
nada reviente ruidosamente — que es la peor clase de fallo.

**1 · `composicion_real` nunca sale del motor.** Si la verdad se proyecta en la
pared, las cuatro fuentes con sesgo sobran, el error doble desaparece y la
Defensoría se queda sin oficio. `Estado.vista_publica()` es la única salida
autorizada.

**2 · Toda región debe tener un corredor humanitario.** Sin vía de reposición de
oxígeno, una región acumula muertes evitables *haga lo que haga la sala*. Eso no
es un dilema: es un guion que castiga. Se detectó midiendo —las cuatro
estrategias daban las mismas 147 muertes— y hoy `loader.py` falla ruidosamente
si alguien lo rompe.

---

## Estado actual

**Funciona y está medido:**

- motor completo: seis subsistemas, bucle de turnos día/noche, proyección T+72 h
- 24 nodos, 5 corredores, 4 regiones, 40 escuadrones con fatiga
- 14 acciones de los ocho roles, constitutivas y operativas
- corredor sin interfaz con cinco estrategias comparables
- 18 pruebas sin modelo, en 0,1 s
- las tres superficies de la interfaz, conectadas a la API

**Falta:**

- **capa 4** — el canal de órdenes en lenguaje natural. `/api/plan/interpretar`
  devuelve hoy una interpretación determinista de prueba.
- **capa 3** — los seis agentes de entorno (Comité del Paro, prensa, redes,
  gremios, internacional, alcaldes). La esfera pública se llena con un
  marcador de posición.
- **calibración** — ver abajo.

---

## Sobre la calibración

**Ningún coeficiente está medido.** Son convenciones declaradas. La primera
corrida con personas es una medición, no un ejercicio, y conviene decirlo antes
de empezar.

El criterio es **por comportamiento, no por realismo**: ajustar hasta que
ninguna estrategia pura gane. `scripts/correr_ejercicio.py --comparar` es la
herramienta que lo mide. Medición del 2026-08-24:

```
  estrategia      netas  reap  muertes  legit  cohes  credib
  solo_fuerza         3     3      147     25      0      21
  solo_mesa           6     0      147     52     41      45
  constituida         1     2      147     44     23      21
  humanitaria         3     0       70     37      0      45
  pasiva              1     0      147     25      0      45
```

Ninguna domina —`solo_mesa` conserva las reservas pero no salva a nadie;
`humanitaria` salva la mitad y lo paga en legitimidad y cohesión— pero quedan
dos problemas abiertos: la cohesión se hunde a 0 en tres de las cinco (satura), y
`constituida` rinde por debajo de lo que debería para una sala que hace las cosas
bien. Ver §12.2 de la propuesta.

---

## Qué se hereda de Macondo

La arquitectura de cuatro capas se sostiene entera; lo que se sustituye es la
capa 1. Íntegros: el patrón `Accion` con `validar()`/`ejecutar()`, las tres colas,
el reporte determinista después de ejecutar, el plan aparcado con elección
tipada. Y los ocho modos de falla de la guía siguen siendo los mismos ocho —dos
son peores aquí, porque una resolución de entidades que acierta mal en silencio
ya no manda ayuda al barrio equivocado sino **ESMAD al nodo equivocado**.

---

## Nota sobre el caso

El paro de 2021 es reciente, tiene víctimas reales y responsabilidades todavía en
discusión judicial. **El motor no cuantifica culpa ni produce veredictos sobre
hechos históricos: calcula consecuencias de decisiones tomadas en la sala.**

Los nodos llevan nombres ficticios sobre una estructura real, como Macondo lo fue
sobre Mocoa. Si se decide usar nombres reales (decisión D1 de §12.1), conviene
además una declaración expresa en el turno 0.
