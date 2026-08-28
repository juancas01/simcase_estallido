# SIMCASE · El Estado frente al Estallido Social

Simulación de conducción de crisis sobre el Paro Nacional de 2021. Un Puesto de
Mando Unificado de nueve roles, dos horas de mundo real, y un motor que calcula
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

---

## Los documentos

**Cinco vigentes, uno de referencia y una carpeta de historial.** Cada hecho vive
en un solo sitio; los demás documentos apuntan a él.

### Por dónde empezar

Los tres primeros no piden saber programar.

| | Lea | Para qué |
|---|---|---|
| **1** | [`docs/propuesta.md`](docs/propuesta.md) | **El diseño del juego.** Qué se simula y hasta dónde, qué ve cada uno de los nueve, qué puede hacer y cómo se afectan entre sí. Incluye el modelo del mundo y un glosario. **Empiece por aquí si no conoce el caso** |
| **2** | [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) | **Del juego al motor.** Cada sección tiene la misma forma: qué pasa en la sala, qué cálculo lo produce, y en qué archivo está. **Es el documento central**, y el hogar de todos los números |
| **3** | [`PENDIENTES.md`](PENDIENTES.md) | **Qué falta.** Separado por lo que se hace sin convocar a nadie, lo que necesita personas en una sala, y lo que decide el equipo docente. **Es el único sitio donde se lleva la cuenta** |
| **4** | [`docs/EL_CODIGO.md`](docs/EL_CODIGO.md) | **Cómo está organizado el repositorio.** Dónde vive cada cosa, cómo añadir una acción o un punto, qué convenciones hay. Este sí pide saber programar |

Y dos **de consulta, que no se leen seguidos**:

| Lea | Para qué |
|---|---|
| [`docs/GUIA_DE_ACCIONES.md`](docs/GUIA_DE_ACCIONES.md) | **Las 39 acciones en lenguaje corriente y sin una sola cifra.** Cómo se llama cada una, qué hace, qué hace falta antes y la frase que la pide. Es la guía que cada titular tiene en pantalla, con las nueve carteras a la vez: **esto es lo que se imprime y se reparte en la sala** |
| [`docs/LAS_ACCIONES.md`](docs/LAS_ACCIONES.md) | **Las mismas 39, con los números.** Qué escribe cada una en el estado y cuánto cobra. Se abre por el rol o por la acción que se está discutiendo |

### Y dos más, según lo que busque

| Lea | Para qué |
|---|---|
| [`docs/guia_arquitectura_simulaciones.md`](docs/guia_arquitectura_simulaciones.md) | Montar **otro** caso con esta arquitectura. Describe la forma, no el caso: sirve igual para un sismo, un brote o una falla de infraestructura. De aquí sale el principio que ordena todo el repositorio — *el LLM traduce; el motor decide, valida, ejecuta y reporta* — y los ocho modos de falla del canal de órdenes |
| [`docs/historial/`](docs/historial/) | De dónde salieron las decisiones actuales. **No está obsoleto: está superado.** La [propuesta inicial](docs/historial/propuesta_inicial.md) con sus razonamientos largos, [cómo funcionaba el primer motor](docs/historial/como_funciona_motor_v1.md), el [diagnóstico](docs/historial/mapa_de_palancas.md) del que salió esta versión, y [lo que ya no está pendiente](docs/historial/resueltos.md) |

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

# 4 · Las nueve vistas privadas de un turno real
uv run python scripts/correr_ejercicio.py --vistas

# 5 · Las superficies
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
plantillas. Comprobar con `/api/config`, que dice además cuánto se espera como
máximo por cada capa.

**El presupuesto de latencia está medido** (`PENDIENTES.md` B5) y los valores por
defecto de `.env.example` salen de esa medición: el canal responde en **2,4 s de
mediana** y la esfera pública en **6 s**, contra presupuestos de 12 y 20. Los dos
ajustes que lo consiguen —`REINTENTOS_LLM=0` y `ESFUERZO_*=low`— están
comentados ahí, porque sin ellos la esfera pública **no llegaba a usar el modelo
ni una vez**.

---

## Cómo está organizado

```
src/engine/          EL MOTOR. Único dueño del estado. Sin IA, determinista salvo
                     por una semilla registrada.
  parameters.py        todas las constantes, con nombre y unidad
  state.py             nodos, corredores, regiones, reservas, banderas
  loader.py            construye el estado heredado (t=0) desde data/
  mobilization.py      el adversario reflexivo
  force.py             capacidad, fatiga e incidentes
  aperture.py          las tres vías de abrir un corredor
  information.py       la verdad, las estimaciones y la versión
  supply.py            el reloj y el oxígeno medicinal
  territory.py         las lecturas del mapa, qué se hace en cada punto, geometría
  views.py             LAS NUEVE VISTAS PRIVADAS
  actions.py           las 39 acciones de los nueve roles
  simulation.py        el bucle de turnos

src/api/             capa delgada · sirve las superficies
src/agents/          capas 3 y 4 · agentes y órdenes en LN (sin escribir estado)
data/escenario/      el caso, en datos y no en código
web_ui/              las superficies · React + Vite
scripts/             corredor sin interfaz, y la guía que se reparte
tests/               los verificadores · ninguno llama a un modelo
```

El detalle —tamaños, por qué cada cosa está donde está, y cómo añadirle algo—
está en [`docs/EL_CODIGO.md`](docs/EL_CODIGO.md).

---

## Las seis decisiones de diseño

| | Decisión | Dónde vive |
|---|---|---|
| **1** | **El Estado no observa el mundo: lo estima.** Cada nodo tiene una `composicion_real` oculta, y cuatro fuentes la estiman con sesgos opuestos | `information.py` |
| **2** | **Tres vías de abrir un corredor, con economías distintas.** La fuerza reabre esa misma noche; la concertación se sostiene —y **hay que sentarse cada jornada**, o se congela—; el desgaste es gratis y lento | `aperture.py` |
| **3** | **El estándar de derechos es un multiplicador de riesgo**, no un discurso. Seis mitigadores dividen la probabilidad de incidente por casi cinco | `force.py` |
| **4** | **Lo primero no es el territorio: es la mesa.** Diez acciones de protocolo no abren ningún corredor y modifican todo lo posterior. Nada está bloqueado; todo está tarifado | `actions.py` |
| **5** | **Cada rol ve su cartera en alta resolución** y el resto del país en grano grueso. Resolución, no secreto: lo que hace valiosa una vista no es que esté oculta, sino que hay una sola persona que la tiene actualizada | `views.py` |
| **6** | **No hay moderador como figura aparte.** El sistema conduce el turno; quien opera la consola puede ser uno de los nueve | `simulation.py` |

## Tres invariantes que no se pueden romper

Las tres se verifican solas. Si fallan, el ejercicio pierde su objeto sin que
nada reviente ruidosamente — que es la peor clase de fallo.

**1 · La mezcla real de un punto nunca sale del motor** — ni al tablero, ni a
ninguna de las nueve vistas privadas. Si la verdad se proyecta, las cinco fuentes
con sesgo sobran, el error doble desaparece y la Defensoría se queda sin oficio.
Y esa mezcla **sí tiene consecuencia**: operar sobre población mayoritariamente
civil cuesta casi el doble, y pactar donde hay estructura organizada produce un
acuerdo que se rompe.

**2 · Toda región debe tener un corredor humanitario.** Sin vía de reposición de
oxígeno, una región acumula muertes evitables *haga lo que haga la sala*. Eso no
es un dilema: es un guion que castiga. Se detectó midiendo —las estrategias daban
todas las mismas 147 muertes— y hoy `loader.py` falla ruidosamente si alguien lo
rompe.

**3 · Nunca una sola denuncia sin verificar.** Siempre al menos dos, con
veracidad distinta y sin ninguna señal que las distinga. Un ejercicio en el que
la única denuncia grave resulta inventada enseña que las denuncias graves suelen
serlo — y eso, sobre hechos con responsabilidad judicial viva, es tomar partido.

---

## Estado actual

**Funciona y está medido:**

- motor v2 completo: seis subsistemas, bucle día/noche, proyección T+72 h
- **la jornada de quince minutos, en dos tramos** — trece de día en que se ordena
  y dos de noche en que no, y el reloj las encadena solo
- 10 puntos de cierre —cinco en la ciudad epicentro—, 4 corredores, 4
  regiones, 40 escuadrones con fatiga
- **el frente agroalimentario**: el Ministro de Agricultura, la única cartera
  cuyo daño **ya ocurrió** mientras la mesa delibera, con la única mesa de
  negociación que sobrevive a la salida del Comité del Paro
- **39 acciones** de los nueve roles — de protocolo, de operación y de
  información —, cada una con su **guía**: cómo se llama en la sala, qué hace,
  qué hace falta antes (en cualitativo, nunca una cifra) y una frase que
  funciona tal cual en la consola
- **las nueve vistas privadas**, con sus sesgos opuestos y su alerta por turno
- **las mesas de diálogo se instalan cada jornada o se congelan**, y eso se ve:
  en el mapa, en las consecuencias de la noche, y en una pregunta que reciben al
  abrir el día los dos que pueden convocarlas
- **el mapa dice qué se está haciendo en cada punto** — intervenido a la fuerza,
  en negociación, o nada en absoluto
- **doce instalaciones de infraestructura relevante** con nombre y sitio, y el
  riesgo de dejarlas sin custodia se cobra en el debriefing
- tres duplas en un solo bolsillo: verificar un punto, una denuncia, o acompañar
- denuncias con veracidad oculta, y el ultimátum gremial del turno 1
- territorio ficticio sobre **geografía real**: la silueta y la red vial salen
  de datos cartográficos abiertos de un sitio que no consta, y **cada corredor
  se dibuja por el camino que existe**, ruteado sobre esa red
- corredor sin interfaz con **seis estrategias** comparables

**Falta** — la lista completa está en [`PENDIENTES.md`](PENDIENTES.md):

- **la primera corrida con nueve personas.** Nada de lo de arriba está probado con
  gente: es la única prueba que no se puede sustituir por código
- **verificación de lo que la interfaz dibuja** (B9). Todo lo que se comprueba
  hoy mira el motor y el canal; nada mira la pantalla, y un fallo de una línea
  vació las nueve vistas privadas sin que nada avisara
- **persistencia** de la corrida, para repetirla con una decisión cambiada
- **telemetría por turno**, para saber dónde se fue el tiempo
- cinco decisiones que esperan al equipo docente (A1–A7 en `PENDIENTES.md`)

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
  solo_fuerza         4     3     64      3      0      21     14
  solo_mesa           9     0     15     65     56      49     49
  constituida         0     3     48     49     74      21     59
  humanitaria         2     0     13     35     28      45     48
  logistica           2     0     13     52     40      36     45
  pasiva              1     0     64     23     28      45     43
```

> ⚠️ **Esta medición es de un tablero recién cambiado y hay que rehacerla.** El
> escenario pasó de once puntos a diez —cinco en la ciudad y cinco fuera— sobre
> una geografía nueva, y ocho de los diez estrenan `masa_base`. Con eso,
> **`solo_mesa` se acerca a dominar**: abre nueve caminos, deja quince muertes y
> termina arriba en las cuatro reservas. El criterio de calibración del caso es
> que **ninguna estrategia pura gane**, así que esto es un hallazgo abierto y no
> un resultado. Está anotado en [`PENDIENTES.md`](PENDIENTES.md) · C5.

El dilema del caso sigue siendo el mismo y se lee en las dos filas de abajo:
**abrir el país y dejar morir a la gente, o salvarla y entregar el país
cerrado.** Lo que hay que volver a ajustar es cuánto cuesta la mesa.

La lectura completa, con el antes y el después de los dos problemas que estaban
medidos —la cohesión saturada en 0 y las muertes idénticas en cuatro de cinco
estrategias—, está en
[`docs/COMO_FUNCIONA.md` §12](docs/COMO_FUNCIONA.md#12-los-siete-arreglos-medidos).

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
sobre Mocoa. Si se decide usar nombres reales (decisión **A5** de
`PENDIENTES.md`), conviene además una declaración expresa en el turno 0.
