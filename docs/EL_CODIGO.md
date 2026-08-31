# El código — cómo está organizado el repositorio

Este documento es **para quien va a tocar el código**. Explica dónde vive cada
cosa, por qué está donde está, y cómo añadir algo sin romper lo que ya funciona.

Si lo que busca es entender **el ejercicio** —qué pasa en la sala y qué cálculo
lo produce—, ese es [`COMO_FUNCIONA.md`](COMO_FUNCIONA.md) y conviene leerlo
antes que este.

---

## Índice

1. [La regla que ordena todo](#1-la-regla-que-ordena-todo)
2. [Las cuatro capas](#2-las-cuatro-capas)
3. [El mapa del repositorio](#3-el-mapa-del-repositorio)
4. [El motor por dentro](#4-el-motor-por-dentro)
5. [Los datos: el caso fuera del código](#5-los-datos-el-caso-fuera-del-código)
6. [La API](#6-la-api)
7. [Las capas de lenguaje natural](#7-las-capas-de-lenguaje-natural)
8. [El frontend](#8-el-frontend)
9. [Las propiedades que se verifican](#9-las-propiedades-que-se-verifican)
10. [Cómo añadir cosas](#10-cómo-añadir-cosas)
11. [Convenciones](#11-convenciones)
12. [Puesta en marcha](#12-puesta-en-marcha)

---

## 1. La regla que ordena todo

> **El LLM traduce. El motor decide, valida, ejecuta y reporta.**

De ahí sale la propiedad más importante del repositorio, y la que conviene
comprobar antes de tocar nada:

```bash
uv run pytest -q          # ninguna verificación llama a un modelo
```

**El motor corre entero sin llave de API.** No es una comodidad de desarrollo: es
la prueba operativa de que ninguna decisión de la simulación está delegada al
modelo. Si algún día una parte del ejercicio necesitara un modelo para existir,
la arquitectura estaría mal y habría que arreglarla, no documentarla.

Un corolario práctico: **`src/engine/` no importa nada de `src/agents/`.** La
dependencia va en una sola dirección, siempre.

---

## 2. Las cuatro capas

| | Capa | Qué hace | ¿Usa modelo? |
|---|---|---|---|
| **1** | `src/engine/` | El estado del mundo y toda la lógica | **No, nunca** |
| **2** | `src/api/` | Sirve el estado a las pantallas | No |
| **3** | `src/agents/entorno.py` | Redacta la esfera pública | Sí, una llamada por turno |
| **4** | `src/agents/nlu.py` | Traduce órdenes habladas a acciones tipadas | Sí, una llamada por orden |

Las capas 3 y 4 **degradan solas**: sin llave, o si el proveedor tarda, el
ejercicio sigue con plantillas deterministas y lo dice en el campo
`generado_por`. Esa degradación se prueba, no se supone.

---

## 3. El mapa del repositorio

```
simcase_estallido/
│
├── src/engine/          EL MOTOR · único dueño del estado · sin IA
│   ├── parameters.py       531 l   todas las constantes, con nombre y unidad
│   ├── state.py            853 l   de qué está hecho el país + vista_publica()
│   ├── loader.py           385 l   construye t=0 desde data/ y verifica invariantes
│   │
│   ├── mobilization.py     255 l   el adversario reflexivo
│   ├── force.py            367 l   riesgo, mitigadores, incidentes, ESMAD, escolta
│   ├── aperture.py         293 l   las tres vías de abrir · LAS MESAS · acuerdos
│   ├── supply.py           227 l   el reloj, el oxígeno, la prioridad de combustible
│   ├── information.py      342 l   verdad, estimaciones sesgadas, equipos, denuncias
│   ├── territory.py        473 l   lecturas del mapa · INTERVENCIÓN · geometría
│   │
│   ├── views.py            860 l   LAS NUEVE VISTAS PRIVADAS
│   ├── actions.py        2 744 l   las 37 acciones + la GUÍA de cada una
│   └── simulation.py       692 l   el bucle · paso() es la única puerta
│
├── src/api/main.py     880 l   capa delgada · endpoints y catch-all del SPA
│
├── src/agents/          LAS CAPAS DE LENGUAJE NATURAL · opcionales
│   ├── config.py           159 l   .env, llave, y el presupuesto de latencia duro
│   ├── resolver.py         345 l   entidades → ids, determinista, cuatro estados
│   ├── herramientas.py   1 073 l   esquemas tipados generados del catálogo
│   ├── nlu.py              787 l   el cauce de nueve pasos
│   └── entorno.py          303 l   los seis agentes de entorno
│
├── web_ui/src/          LAS SUPERFICIES · React 19 + Vite
│   ├── App.jsx             241 l   enrutado y portada
│   ├── comun.jsx           262 l   ROLES, api(), useDatos, Medidor, Tendencia
│   ├── definiciones.jsx    784 l   las definiciones formales de los globos
│   ├── etiquetas.jsx       292 l   identificador del motor → rótulo de pantalla
│   ├── index.css         1 660 l   el sistema visual entero
│   └── components/      Tablero · VistaPrivada · Consola · Mapa · Reloj · Ayuda
│                        (`Mapa.jsx`, 1 160 l, DIBUJA; no calcula ni una cifra)
│
├── data/escenario/      EL CASO, en datos y no en código
├── scripts/             el corredor sin interfaz, para calibrar sin sala
│   ├── correr_ejercicio.py  siete estrategias de referencia · --comparar
│   ├── repertorio.py   escribe `docs/GUIA_DE_ACCIONES.md` desde el catálogo
│   └── mapa/           CÓMO SE CONSTRUYE EL MAPA · nueve pasos, desde
│                       datos cartográficos abiertos hasta el escenario
├── tests/               los verificadores · ninguno llama a un modelo
│
├── README.md            por dónde empezar
├── PENDIENTES.md        qué falta · el único sitio donde se lleva la cuenta
└── docs/                este documento y los demás
```

**Los tamaños importan aquí.** `actions.py`, con casi dos mil líneas, es el
archivo más grande y el que más se toca: 39 clases, cada una con su validación y
su ejecución. Si crece mucho más, el corte natural es por frente (seguridad,
estrategia, logística), no por tipo de acción. El segundo es `index.css`, y ahí
el corte natural sería por superficie.

---

## 4. El motor por dentro

### El estado

Todo el mundo vive en un objeto `Estado` ([`state.py`](../src/engine/state.py)),
con **tres niveles espaciales** porque los siete roles no deciden sobre lo mismo:

```
Nodo       un punto de cierre          11    Policía · Interior · Alcalde
Corredor   una secuencia de puntos      4    Transporte · Defensa
Region     un área con su reloj         4    Agricultura · Interior
```

Más `Reservas`, `Banderas`, `Unidad`, `Denuncia`, `Acuerdo` y el registro de
decisiones.

> **Desviación deliberada respecto de la guía de arquitectura.** Esa guía
> recomienda arrays paralelos de NumPy. Aquí se usan objetos, a propósito: once
> nodos y no 657, lógica ramificada y no aritmética uniforme, doce pasos por
> ejercicio y no 288. La regla que **sí** se conserva es el identificador estable
> y opaco (`nodo_id`), con los nombres legibles fuera del motor.

### El paso

`MotorCrisis.paso()` es **la única forma de que el tiempo avance**. Su orden es
fijo y ese orden es parte del diseño:

```
0 · eventos de calendario          (la jornada nacional del turno 3)
1 · condicionales cuya condición ya se cumple
2 · las acciones de la cola        ← PROHIBIDO break al primer fallo
3 · el costo de no decidir
4 · costos por no haberse constituido   (solo en turnos de día)
5 · subsistemas, en orden fijo:
      aperture → acuerdos → supply → escasez → denuncias → movilización → fatiga
6 · umbrales, gremios, encuadre
7 · foto de indicadores y resumen
```

**El paso 2 no puede llevar `break`.** Una orden compuesta no puede morir entera
porque a una de sus partes le falte un dato — es el modo de falla F2, y está
probado.

### Lo que nunca sale del motor

Dos datos, y son los que sostienen el ejercicio entero:

| Dato | Dónde vive | Qué pasaría si saliera |
|---|---|---|
| `Nodo.composicion_real` | capa 1, `state.py` | se acabaría el dilema de operar a ciegas |
| `Denuncia.veraz` | capa 1, `state.py` | verificar dejaría de costar algo |

**Están custodiados en las cuatro superficies**, no solo en `vista_publica()`:
también en las siete vistas privadas, en los deltas y en los hechos del mapa. Cada
vez que se añade una superficie hay que preguntarse si abre una puerta trasera a
estos dos.

---

## 5. Los datos: el caso fuera del código

`data/escenario/estado_inicial.json` contiene **el caso**, y el motor no sabe
nada de él más allá de su forma:

```jsonc
{
  "fecha_inicio": "2021-05-11T06:00",
  "region_epicentro": "R-BEL",
  "regiones":   [ … 4 … ],
  "corredores": [ … 4 … ],
  "nodos":      [ … 10, con x/y sobre un vértice REAL de la red vial y
                    DENTRO del polígono de su región … ],
  "infraestructura": [ … 12 instalaciones con nombre, sitio, criticidad
                    cualitativa y de qué depende cada una … ],
  "mapa":       { … contorno real, tramos de litoral y frontera, agua
                    interior, RED VIAL real, TRAZADOS ruteados de los
                    cuatro corredores, cuatro polígonos de región,
                    rótulos, mares, puerto y ciudad … },
  "denuncias_iniciales": [ … el hecho H2 … ],
  "hecho_h1":   { … el incidente que la sala recibe · apunta a la
                    instalación por su identificador … }
}
```

**El bloque `mapa` no se escribe a mano.** Sale de un proceso de construcción
que parte de datos cartográficos abiertos —línea de costa y carreteras
principales de un sitio real que no consta— y produce: la silueta por
rasterizado y marching squares, las cuatro regiones por reparto de la rejilla
con **fronteras compartidas** (cada una se simplifica una vez y se usa dos, de
modo que la teselación es exacta por construcción), y los trazados de corredor
por Dijkstra sobre el grafo vial. Los diez puntos se siembran **sobre** el
trazado ya ruteado de su corredor, no al revés.

**Por qué en datos y no en código.** Se puede cambiar el escenario, apagar un
hecho detonante o probar otro territorio sin tocar el motor. Y `loader.py`
verifica las invariantes al cargar, **fallando ruidosamente**:

- toda región necesita al menos un corredor humanitario
- nunca una sola denuncia sin verificar (hacen falta ≥2, con veracidad distinta)
- **todo punto cae dentro del polígono de su región**
- **toda instalación cae dentro del polígono de la suya**, y sus puntos
  contiguos existen
- el hecho H1 custodia una instalación **que está en el registro**

La última es nueva y es del mapa interactivo. Mientras el mapa fue un esquema de
líneas, las coordenadas no afirmaban nada. Ahora afirman en qué región está cada
bloqueo, y el reparto territorial es justo lo que la sala está leyendo. No puede
ser «lo revisó alguien al dibujarlo»: el motor genera cierres nuevos por su
cuenta cuando la intensidad sube, y `mobilization._hueco_en` los coloca dentro
del polígono por la misma razón.

Y una más que vigila la suite y no el cargador, porque necesita el contorno:
**nada cae en el agua de dentro.** Es la trampa de este mapa — el contorno
*encierra* el estuario, porque para repartir el territorio entre las cuatro
regiones el agua interior se rellena. De modo que `dentro(contorno)` da `True`
en mitad del agua, y las dos comprobaciones de arriba dejarían pasar un bloqueo
dibujado sobre el estrecho: se dibuja, se puede pinchar, tiene sus seis
lecturas, y está en el agua.

Un escenario que no las cumpla no arranca. Es preferible a arrancar y producir
un ejercicio sin dilema.

---

## 6. La API

[`src/api/main.py`](../src/api/main.py) es deliberadamente delgada: **toda la
lógica vive en el motor, que no sabe que esta capa existe.**

```
GET  /api/tablero              el tablero + deltas + hechos del mapa
GET  /api/vista/{rol}          la vista privada de un rol
GET  /api/vistas               las siete, para el corredor sin interfaz
GET  /api/esfera               lo que se dice
GET  /api/catalogo             las 37 acciones, con su `en_claro`
GET  /api/config               si hay llave de API, y cuál es el archivo .env
GET  /api/metricas             las métricas de cierre
GET  /api/proyeccion           el país a 72 horas
GET  /api/consulta/{tema}      la rama de solo lectura del canal de órdenes

POST /api/consola/interpretar  texto → plan, con su banda de riesgo
POST /api/consola/elegir       resuelve una ambigüedad con elección tipada
POST /api/consola/encolar      confirma una orden sin gastar la jornada
POST /api/consola/ejecutar     encola y cierra el día, en un solo acto
POST /api/consola/resolver     cierra el día con lo que haya en cola
POST /api/consola/declarar_linea   la declaración del turno 0

POST /api/consola/reloj/iniciar    arranca el ejercicio y abre la jornada 1
POST /api/consola/reloj/pausa      detiene el reloj interno · y lo reanuda
POST /api/consola/reloj/noche      cierra el día YA y sirve las consecuencias
POST /api/consola/reloj/jornada    abre el día siguiente YA
POST /api/consola/reloj/reiniciar  la cuenta a cero. NO rebobina el mundo
POST /api/consola/fase/{fase}      pone la sala en un tramo, para depurar

GET  /{full_path}              sirve web_ui/dist (el SPA)
```

**El estado vive en memoria del proceso** (`_estado` y `motor`, globales). Es la
limitación conocida y es el pendiente **B1**: al cerrar el proceso se pierde la
corrida, y el debriefing dura más que cualquier turno.

### El reloj de sala, y por qué vive en la API

La jornada son quince minutos partidos en dos tramos —trece de día en que se
ordena y dos de noche en que no—, y las transiciones las dispara un **latido de
fondo cada segundo** más una comprobación en cada lectura del tablero. Tres
piezas sostienen eso:

| Pieza | Qué hace |
|---|---|
| `sala["reloj"]` | tres instantes: `sesion_desde`, `jornada_desde`, `pausa_desde`. La fase se deriva de ellos |
| `_sincronizar()` | lleva el mundo a donde el reloj dice que está. Idempotente |
| `_cerrojo` | un `RLock` sobre todo lo que mueve el mundo |

**El cerrojo no es defensivo, es necesario.** Los endpoints declarados con `def`
corren en un pool de hilos y encima hay un latido: sin él, dos pantallas
consultando el tablero en el segundo en que expira el día resolvían la jornada
**dos veces**, y no se notaba hasta ver dos noches seguidas en el historial.

Y el motor no sabe nada de esto. Expone dos bisagras —`abrir_jornada()` y
`cerrar_jornada()`— y quién las llama, cuándo y por qué es asunto de esta capa.

---

## 7. Las capas de lenguaje natural

Solo el **paso 1** de nueve usa el modelo:

```
1 · NLU           tool calling con herramientas tipadas   ← la única llamada
2 · RESOLUTOR     entidades → ids, determinista
3 · EXPANSOR      llamadas → acciones atómicas, con tope
4 · VALIDADOR     dry-run por acción, SIN break
5 · PREVISUALIZAR si falta un dato, el plan entero espera
6 · EJECUTAR
7 · REPORTAR      plantilla determinista, DESPUÉS de ejecutar
8 · SUGERIR       solo si hubo fallo
9 · CONSULTAR     rama de solo lectura
```

Cada paso existe por un modo de falla medido en un ejercicio real —los ocho están
listados en la cabecera de [`nlu.py`](../src/agents/nlu.py)—.

### La regla que gobierna toda la capa

> **Si el canal no entiende, PREGUNTA.** Nunca adivina, nunca fuerza la acción
> más parecida, y nunca ejecuta una orden a medias.

El fallo que hay que impedir no es que el canal se equivoque: es que **se
equivoque en silencio**. Una orden rechazada con un motivo legible cuesta veinte
segundos de sala; una orden ejecutada en el punto equivocado no cuesta nada
—hasta el debriefing.

### Cuatro piezas que sostienen esa regla

**El resolutor tiene cuatro estados, no dos.** `ok · ambiguo · selector ·
no_encontrado`. Y lo que lo hace seguro: *si un escalón produce más de un
candidato, el resultado es ambiguo — nunca se toma el primero.*

**Un `no_encontrado` explica y ofrece.** Tres respuestas distintas según el caso:
si el nombre existe pero es de otra clase, lo dice y enumera los puntos del
corredor; si se parece a algo por encima de `UMBRAL_SUGERIR`, ofrece las tres más
cercanas como botones; si no se parece a nada, dice **qué clase de cosa se
esperaba**. Un «no existe» a secas obliga a la sala a adivinar qué escribió mal.

**El expansor expande.** Un criterio —«todos los puntos», «los cerrados»— produce
**una acción por punto**, con tope y con aviso. No es un lugar: son N lugares.

**Solo se ejecuta lo que está `lista`.** `falta_dato` también se queda fuera, y
lo que se queda fuera **se enuncia** en `omitidas`. Ejecutar una acción
incompleta con sus valores por defecto produce una operación que nadie ordenó,
informada como cumplida.

### Y dos que ya estaban

**Las ambigüedades se resuelven con elección tipada**, no con texto libre. Sin
eso, «no», «400» y «sí, confirmo» vuelven a entrar por el canal como si fueran
órdenes nuevas.

`herramientas.py` **genera los esquemas desde el catálogo**, no los escribe a
mano. En la simulación anterior, un paquete que faltaba en un prompt escrito a
mano fue invisible para el agente durante todo un ejercicio.

### El intérprete de reserva trabaja por cláusula

Sin llave, el paso 1 lo hace un intérprete de raíces —`oper`, `escolt`,
`concert`— porque la gente conjuga. **Cada disparador solo mira su cláusula**:
antes miraba el texto entero, y en «operen el puente y concertar el Alto del
Mirador» el nombre de la segunda se colaba en la primera. Salían dos acciones
sobre el Alto del Mirador y la ambigüedad de «el puente» desaparecía sin dejar
rastro.

> **`consultar` es una herramienta más, no un clasificador previo.** Un
> clasificador orden/consulta que se equivoca emite una orden que nadie dio, y
> eso es irreversible. Un mismo texto puede ser orden **y** consulta.

---

## 8. El frontend

React 19 + Vite, sin router: [`App.jsx`](../web_ui/src/App.jsx) mira
`window.location.pathname`. Tres rutas.

### Los cuatro módulos compartidos

| Archivo | Qué guarda | Por qué existe |
|---|---|---|
| `comun.jsx` | `ROLES`, `api()`, `useDatos`, `Medidor`, `Tendencia`, `Cargando` | lo que usan todas las superficies |
| `definiciones.jsx` | las 38 definiciones de los globos de ayuda | **un umbral cambia en un solo párrafo** |
| `etiquetas.jsx` | `sin_verificar` → «Sin verificar» | el identificador es del motor; el rótulo es de la sala |
| `index.css` | el sistema visual entero | tokens, no valores sueltos |

### Dos patrones que conviene respetar

**Una marca de ayuda, un globo.** Dos marcas pegadas obligan a elegir cuál abrir
antes de saber qué hay en cada una. Si una tarjeta necesita explicar dos cosas,
se componen en un solo globo (ver `NOTA_DELTA` en `definiciones.jsx`).

**`rotulo()` degrada bien.** Si el motor gana un enum nuevo que `etiquetas.jsx`
no conoce, sale «Valor nuevo» y no `valor_nuevo`. Nunca hay que pintar un
identificador crudo.

### El sistema visual

Oscuro, porque una sala proyectando en claro a las dos de la tarde no se lee.
Todo el color pasa por tokens (`--bien`, `--medio`, `--mal`, `--acento`), y los
tres semánticos se usan igual en todas partes: verde es que va bien, ámbar es
aviso, rojo es deterioro.

---

## 9. Las propiedades que se verifican

**Lo que se comprueba en cada cambio no es una lista de pruebas: es una lista de
propiedades**, y todas están aquí porque **se rompieron alguna vez** o porque su
ruptura sería silenciosa — que es la peor clase de fallo: el ejercicio pierde su
objeto sin que nada reviente ruidosamente.

```bash
uv run pytest -q
```

Se agrupan en dos frentes, porque custodian dos cosas muy distintas.

### El motor — que el mundo se comporte como dice el diseño

| Propiedad | Por qué importa |
|---|---|
| **Lo que nunca sale** | la mezcla real y la veracidad de una denuncia, en las **cuatro** superficies: tablero, vistas privadas, deltas y hechos del mapa |
| **La mezcla real sí importa** | que `composicion_real` cambie el resultado de una corrida — se desconectó una vez sin que nada avisara |
| **El reloj y el oxígeno** | que las muertes dependan de las decisiones y no del guion |
| **Riesgo y mitigadores** | el techo de 0,98, y que el estándar no rescate a quien opera sin cuidado |
| **Duplas y denuncias** | el bolsillo de tres, y que verificar aquí sea no verificar allá |
| **La mesa y el tiempo** | que la cohesión no vuelva a ser una rampa determinista |
| **Aperturas** | que un corredor valga lo que su peor punto |
| **Jurisdicción y validación** | que una acción inválida no tumbe el resto de la orden |
| **Las siete vistas** | que quepan en una pantalla y que los sesgos vayan en direcciones opuestas |
| **El escenario** | las invariantes del cargador, el territorio ficticio, las posiciones del mapa |
| **Reloj, deltas y hechos** | que el delta mida el último paso y no abra puertas traseras |
| **La documentación** | que cada `PENDIENTE(Xn)` del código apunte a una entrada real |

La última es inusual y se ganó su sitio: **la promesa de navegación en los dos
sentidos de `PENDIENTES.md` ya se había roto en silencio.**

### El canal de órdenes — que se traduzca lo que la sala quiso decir

| Propiedad | Por qué importa |
|---|---|
| **Un recurso que no existe** | que «el Puente de Brooklyn» no se opere en el que más se le parezca |
| **Una orden que no existe** | que no se fuerce la acción más parecida, y que el silencio diga por qué |
| **La ambigüedad** | que se pregunte, y que una orden compuesta no le robe el lugar a la otra |
| **Las enumeraciones** | que la unidad pedida no se cambie por la de por defecto |
| **Los criterios** | que «todos los puntos» sean N acciones y no la primera |
| **Preguntar no es ordenar** | que una consulta no ejecute nada ni gaste una jornada |
| **Lo que la sala oye** | que la lectura en voz alta diga el rol, el punto y los mitigadores |
| **La consola** | que nada se ejecute a medias ni se caiga en silencio |
| **La degradación** | que sin llave, y con el proveedor caído, el canal siga traduciendo |
| **El repertorio, sin llave** | que ninguna herramienta quede sin disparador — el canal no puede negar tener una acción que tiene |
| **Requisitos que no se regalan** | que el canal no se conceda la Alcaldía, ni una cifra, ni un responsable que nadie dijo |
| **Los valores por defecto** | que lo que el motor va a usar se diga en voz alta antes de confirmarlo |
| **El presupuesto y la esfera** | que la espera sea la declarada, y que solo publiquen las seis fuentes |

> **Este frente llegó tarde, y conviene recordar por qué.** Durante varias
> versiones todo lo verificado custodiaba el motor —que nadie toca durante el
> ejercicio— y **nada** custodiaba el canal por el que entran las órdenes de siete
> personas en dos horas. Al sondearlo aparecieron dieciocho fallos, nueve de
> ellos silenciosos. Están contados en
> [`docs/historial/resueltos.md`](historial/resueltos.md#4--primera-revisión-del-canal-de-órdenes).

### Dos reglas del banco de verificación

**Nada sale a la red.** Las dos capas de lenguaje natural se silencian a la vez,
con un accesorio único y automático, y eso también se comprueba. **Un accesorio
por archivo es justo lo que dejó media puerta abierta** durante varias versiones:
se silenciaba la capa 4 y la capa 3 seguía haciendo llamadas facturadas en cada
corrida.

**Se fuerza la rama determinista**, que además es la que corre cuando no hay
llave: si algo dejara de pasar al quitar el modelo, la degradación sería
decorativa.

> **Lo que hoy no se verifica es la interfaz.** Ninguna comprobación mira lo que
> la pantalla dibuja, y un fallo de una línea llegó a vaciar las siete vistas
> privadas con todo lo demás en verde. Es el pendiente **B9** de
> [`PENDIENTES.md`](../PENDIENTES.md).

## 10. Cómo añadir cosas

### Una acción nueva

1. Una clase en [`actions.py`](../src/engine/actions.py) que herede de `Accion`:

```python
class MiAccion(Accion):
    """Qué hace, y por qué existe en el ejercicio."""
    codigo = "X1"
    rol = "Transporte"
    clase: Clase = "operativa"          # constitutiva | operativa | informativa
                                        # en pantalla: Protocolo | Operación |
                                        # Información  (etiquetas.jsx)
    descripcion = "El nombre formal del acto"
    en_claro = ("Qué hace, en una frase. "
                "Qué cuesta o qué habilita, en otra.")

    def validar(self, estado) -> Validacion: ...
    def ejecutar(self, estado, rng) -> Resultado: ...
```

2. Añadirla a `CATALOGO`.
3. Si se puede pedir hablando, un esquema en `herramientas.py`.
4. Una prueba de su validación y otra de su efecto.

**`validar()` no muta nada** — se usa como dry-run en el paso 4 del cauce.

### Un rol nuevo

Tocaría `views.py` (su vista), `actions.py` (su repertorio), `comun.jsx` (su
título) y la ficha impresa. Es el cambio más caro del repositorio: **siete es un
número de diseño**, no una constante.

Y quitar uno cuesta más que añadirlo, porque hay que decidir qué pasa con la
mecánica que sostenía. Está medido: la salida del Delegado de la Defensoría del
Pueblo y del Ministro de Minas y Energía está contada en
[`historial/resueltos.md`](historial/resueltos.md).

### Un punto, un corredor, una región

Solo `data/escenario/estado_inicial.json`. Si rompe una invariante, el cargador
lo dice al arrancar.

### Una definición o un rótulo en pantalla

`definiciones.jsx` o `etiquetas.jsx`. **Nunca en el componente**: un texto en dos
sitios se desincroniza.

---

## 11. Convenciones

**Español en todo.** Nombres de función, variables, comentarios y documentos. Un
repositorio bilingüe obliga a traducir mentalmente en cada lectura.

**Un número que gobierna algo vive en `parameters.py`** y en ningún otro sitio.
Si aparece un literal en la lógica, es un error.

**Las marcas de pendiente llevan su identificador:**

```bash
grep -rn "PENDIENTE" src/
```

`PENDIENTE(B1)` apunta a la entrada B1 de [`PENDIENTES.md`](../PENDIENTES.md).
Una marca sin entrada rompe una prueba.

**Los comentarios explican el porqué, no el qué.** El código ya dice qué hace. Lo
que se pierde al cabo de un mes es por qué se eligió así, y sobre todo **qué se
probó antes y no funcionó**.

**Lo que se duplique se desincroniza. Siempre.** Es la regla más repetida del
repositorio y la que más veces ha salvado algo: el catálogo de acciones se genera
del código, los rótulos viven en un archivo, las definiciones en otro, y el
frontend lee de las mismas fuentes que el motor.

**Mirar no cambia nada y no gasta azar.** Todo lo que sirve una superficie
—`vista_publica()`, `views.vista()`, `deltas()`, `hechos_por_punto()`— es una
proyección determinista del estado: con el mismo estado sale lo mismo, se pida
una vez o cincuenta. Donde hace falta ruido, la semilla se **deriva** de la clave
del dato (`information.estimar_nodo`) en vez de sacarla del `rng` del motor.

> Costó encontrarlo porque el síntoma era cosmético —los números de la vista de
> Interior cambiaban al refrescar— y el daño no: cada refresco consumía azar de
> la corrida, así que el resultado dependía de cuántas veces alguien pulsó F5.
> Una semilla que no reproduce la corrida no sirve para el debriefing.
>
> **La excepción conocida es `/api/proyeccion`**, que sí avanza el mundo:
> `proyectar_sin_mando()` corre turnos de verdad sobre el estado real. Es
> intencionado —es el país que la sala entrega— pero significa que ese endpoint
> **no se puede refrescar**. Hoy ninguna pantalla lo llama.

---

## 12. Puesta en marcha

```bash
# 1 · el motor y su verificación
uv sync
uv run pytest -q

# 2 · una corrida completa sin montar la sala
uv run python scripts/repertorio.py            # la guía que se reparte
uv run python scripts/correr_ejercicio.py --detalle
uv run python scripts/correr_ejercicio.py --comparar
uv run python scripts/correr_ejercicio.py --vistas

# 3 · las pantallas
cd web_ui
npm install
npm run build
cd ..
uv run python -m src.api.main        # http://localhost:8000
```

**Nada de lo anterior necesita llave de API.** Para activar las capas de lenguaje
natural, `OPENAI_API_KEY` en un `.env` en la raíz, a partir de `.env.example`.
`GET /api/config` dice si está.

> En PowerShell, **un comando por línea**: `&&` no es un operador válido.

---

*Escuela de Gobierno · Universidad de La Sabana · AI Lab*
