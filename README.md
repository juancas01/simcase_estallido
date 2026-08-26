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

**Tres documentos, en este orden.** No hace falta saber programar para ninguno.

| | Lee | Para qué |
|---|---|---|
| **1** | [`docs/propuesta.md`](docs/propuesta.md) | **El diseño del juego.** Qué ve cada uno de los ocho, qué puede hacer y cómo se afectan. Incluye el modelo del mundo y un glosario |
| **2** | [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) | **Cómo está construido.** Del juego al código: qué pasa en la sala, qué cálculo lo produce, y en qué archivo está |
| **3** | [`PENDIENTES.md`](PENDIENTES.md) | **Qué falta y cómo probarlo.** Las cuatro pruebas en orden y las decisiones que esperan al equipo docente |

Y dos más, según lo que busques:

| Lee | Para qué |
|---|---|
| [`docs/guia_arquitectura_simulaciones.md`](docs/guia_arquitectura_simulaciones.md) | Montar **otro** caso con esta arquitectura. Describe la forma, no el caso |
| [`docs/historial/`](docs/historial/) | De dónde salieron las decisiones actuales: la propuesta inicial, el primer motor, y el diagnóstico que produjo esta versión |

---|---|
| **entender cómo funciona el motor v2** | [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) — del juego al código: qué pasa en la sala, qué cálculo lo produce y en qué archivo está |
| entender el motor **anterior** | [`docs/historial/como_funciona_motor_v1.md`](docs/historial/como_funciona_motor_v1.md) — la versión previa, con sus números |
| saber **por qué** está diseñado así | [`docs/historial/propuesta_inicial.md`](docs/historial/propuesta_inicial.md) — el documento de diseño completo |
| entender **el diseño del juego v2** | [`docs/propuesta.md`](docs/propuesta.md) — vista privada por rol, el modelo del mundo, 34 acciones y el turno sin moderador |
| montar **otro** caso con esta arquitectura | [`docs/guia_arquitectura_simulaciones.md`](docs/guia_arquitectura_simulaciones.md) |
| entender **el ejercicio como juego** — qué puede hacer cada rol y cómo se afectan | [`docs/historial/mapa_de_palancas.md`](docs/historial/mapa_de_palancas.md) — las reglas, las ocho fichas, el mapa de interdependencias, y qué de todo eso sostiene el motor |
| **empezar a probar**, y saber qué falta | [`PENDIENTES.md`](PENDIENTES.md) — las cuatro pruebas en orden, las decisiones abiertas, el código sin escribir y la calibración, en un solo sitio |

---

## Arranque rápido

> **En Windows PowerShell**, los comandos van **uno por línea**: PowerShell 5.1
> no admite `&&` como separador y da un `ParserError`. Todo lo de abajo funciona
> tal cual en PowerShell, cmd y bash.

```bash
# 1 · Dependencias (Python 3.13+)
uv sync --extra dev

# 2 · Correr un ejercicio completo, sin interfaz y sin LLM
uv run python scripts/correr_ejercicio.py

# 3 · Comparar estrategias — el criterio de calibración
uv run python scripts/correr_ejercicio.py --comparar

# 4 · Pruebas (sin modelo, < 1 s)
uv run pytest -q

# 5 · Las ocho vistas privadas de un turno real
uv run python scripts/correr_ejercicio.py --vistas

# 6 · Las cuatro superficies
cd web_ui
npm install
npm run build
cd ..
uv run python -m src.api.main        # http://localhost:8000
```

| Superficie | Ruta | Para quién |
|---|---|---|
| Tablero de situación | `/tablero` | **proyectar** — con la esfera pública en su barra lateral |
| Vista privada | `/vista/Minas`, `/vista/Defensoría`… | el dispositivo de cada uno |
| Consola | `/consola` | quien transcribe · no proyectar |

> **La esfera pública no tiene ruta propia, y es a propósito.** La distancia
> entre lo que el Estado tiene por cierto y lo que se dice solo se percibe
> **simultánea**. Mientras tuvo pantalla aparte, esa doctrina dependía de que
> quien monta la sala hiciera lo correcto; ahora el montaje incorrecto no es
> posible.

No hace falta clave de API para nada de lo anterior. **El motor corre entero sin
llamar a ningún modelo de lenguaje.** Si algún día no puede, la arquitectura está
mal.

### Con lenguaje natural (opcional)

Las dos capas de LN —el canal de órdenes y los agentes de entorno— se activan con
una llave. Va en un archivo `.env` en la raíz:

```bash
cp .env.example .env      # y dentro: OPENAI_API_KEY=sk-...
uv sync --extra agents
```

Sin llave, la consola interpreta de forma determinista y la esfera pública usa
plantillas. Comprobar con `/api/config`.

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
  views.py             LAS OCHO VISTAS PRIVADAS · la pieza central de la v2
  actions.py           las 34 acciones de los ocho roles
  simulation.py        el bucle de turnos

src/api/             capa delgada · sirve las cuatro superficies
src/agents/          capas 3 y 4 · agentes y órdenes en LN (sin escribir)
data/escenario/      el caso, en datos y no en código
web_ui/              las cuatro superficies · React + Vite
scripts/             corredor sin interfaz, para calibrar
tests/               verificadores sin modelo
```

---

## Las seis decisiones de diseño

| | Decisión | Dónde vive |
|---|---|---|
| **1** | **El Estado no observa el mundo: lo estima.** Cada nodo tiene una `composicion_real` oculta, y cuatro fuentes la estiman con sesgos opuestos. | `information.py` |
| **2** | **Tres vías de abrir un corredor, con economías distintas.** La fuerza reabre esa misma noche; la concertación se sostiene; el desgaste es gratis y lento. | `aperture.py` |
| **3** | **El estándar de derechos es un multiplicador de riesgo**, no un discurso. Seis mitigadores dividen la probabilidad de incidente por casi cinco. | `force.py` |
| **4** | **Lo primero no es el territorio: es la mesa.** Seis acciones constitutivas no abren ningún corredor y modifican todo lo posterior. Nada está bloqueado; todo está tarifado. | `actions.py` |
| **5** | **Cada rol ve su cartera en alta resolución** y el resto del país en grano grueso. Resolución, no secreto: lo que hace valiosa una vista no es que esté oculta, sino que hay una sola persona que la tiene actualizada. | `views.py` |
| **6** | **No hay moderador como figura aparte.** El sistema conduce el turno; quien opera la consola puede ser uno de los ocho. | `simulation.py` |

---

## Tres invariantes que no se pueden romper

Ambas tienen prueba automática. Si fallan, el ejercicio pierde su objeto sin que
nada reviente ruidosamente — que es la peor clase de fallo.

**1 · La mezcla real de un punto nunca sale del motor** — ni al tablero, ni a
ninguna de las ocho vistas privadas. Si la verdad se proyecta, las cuatro fuentes
con sesgo sobran, el error doble desaparece y la Defensoría se queda sin oficio.
Y desde la v2 esa mezcla **sí tiene consecuencia**: operar sobre población
mayoritariamente civil cuesta casi el doble, y pactar donde hay estructura
organizada produce un acuerdo que se rompe.

**2 · Toda región debe tener un corredor humanitario.** Sin vía de reposición de
oxígeno, una región acumula muertes evitables *haga lo que haga la sala*. Eso no
es un dilema: es un guion que castiga. Se detectó midiendo —las estrategias
daban todas las mismas 147 muertes— y hoy `loader.py` falla ruidosamente si
alguien lo rompe.

**3 · Nunca una sola denuncia sin verificar.** Siempre al menos dos, con
veracidad distinta y sin ninguna señal que las distinga. Un ejercicio en el que
la única denuncia grave resulta inventada enseña que las denuncias graves suelen
serlo — y eso, sobre hechos con responsabilidad judicial viva, es tomar partido.

---

## Estado actual

**Funciona y está medido:**

- motor v2 completo: seis subsistemas, bucle día/noche, proyección T+72 h
- 24 puntos de cierre, 5 corredores, 4 regiones, 40 escuadrones con fatiga
- **34 acciones** de los ocho roles — constitutivas, operativas e informativas
- **las ocho vistas privadas**, con sus sesgos opuestos y su alerta por turno
- tres duplas en un solo bolsillo: verificar un punto, una denuncia, o acompañar
- denuncias con veracidad oculta, y el ultimátum gremial del turno 1
- territorio ficticio, con posiciones para el mapa esquemático
- corredor sin interfaz con **seis estrategias** comparables
- **49 pruebas sin modelo, en 0,2 s**

**Falta** — la lista completa está en [`PENDIENTES.md`](PENDIENTES.md):

- **la primera corrida con ocho personas.** Nada de lo de arriba está probado
  con gente: es la única prueba que no se puede sustituir por código
- **persistencia** de la corrida, para repetirla con una decisión cambiada
- **telemetría por turno**, para saber dónde se fue el tiempo
- cinco decisiones que esperan al equipo docente (A1–A5 en `PENDIENTES.md`)

Los stubs están marcados donde viven: `grep -rn "PENDIENTE" src/`

---

## Sobre la calibración

**Ningún coeficiente está medido.** Son convenciones declaradas. La primera
corrida con personas es una medición, no un ejercicio, y conviene decirlo antes
de empezar.

El criterio es **por comportamiento, no por realismo**: ajustar hasta que ninguna
estrategia pura gane. `scripts/correr_ejercicio.py --comparar` lo mide.

```
  estrategia      netas  reap  muert  legit  cohes  credib   resp
  ---------------------------------------------------------------------
  solo_fuerza         1     2     64     15      0      21     24
  solo_mesa           5     4     64     59     56      29     49
  constituida         3     1     48     24     74      21     38
  humanitaria         3     0     16     32     28      35     50
  logistica           3     1     24     41     40      26     39
  pasiva              0     0     64     23     28      45     43
```

**Ninguna domina.** `solo_mesa` abre más caminos y conserva las reservas — y deja
morir a la misma gente que `pasiva`. `humanitaria` salva al 75 % y lo paga en
cohesión y en caminos. `constituida` tiene la mejor mesa y gasta legitimidad al
operar. `solo_fuerza` se queda sin nada.

Los dos problemas que estaban medidos —la cohesión saturada en 0 y las muertes
idénticas en cuatro de cinco estrategias— **no eran de coeficientes: eran piezas
que faltaban.** El antes y el después está en
[`docs/COMO_FUNCIONA.md` §12](docs/COMO_FUNCIONA.md).

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
