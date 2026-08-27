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
9. [Las pruebas](#9-las-pruebas)
10. [Cómo añadir cosas](#10-cómo-añadir-cosas)
11. [Convenciones](#11-convenciones)
12. [Puesta en marcha](#12-puesta-en-marcha)

---

## 1. La regla que ordena todo

> **El LLM traduce. El motor decide, valida, ejecuta y reporta.**

De ahí sale la propiedad más importante del repositorio, y la que conviene
comprobar antes de tocar nada:

```bash
uv run pytest -q          # 150 pruebas, ninguna llama a un modelo
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
│   ├── parameters.py    328 l   todas las constantes, con nombre y unidad
│   ├── state.py         646 l   de qué está hecho el país + vista_publica()
│   ├── loader.py        289 l   construye t=0 desde data/ y verifica invariantes
│   │
│   ├── mobilization.py  183 l   el adversario reflexivo
│   ├── force.py         367 l   riesgo, mitigadores, incidentes, ESMAD, escolta
│   ├── aperture.py      224 l   las tres vías de abrir, reaperturas, acuerdos
│   ├── supply.py        227 l   el reloj, el oxígeno, la prioridad de combustible
│   ├── information.py   341 l   verdad, estimaciones sesgadas, duplas, denuncias
│   │
│   ├── views.py         539 l   LAS OCHO VISTAS PRIVADAS
│   ├── actions.py     1 692 l   las 34 acciones de los ocho roles
│   └── simulation.py    502 l   el bucle de turnos · paso() es la única puerta
│
├── src/api/main.py      400 l   capa delgada · 15 endpoints y el catch-all del SPA
│
├── src/agents/          LAS CAPAS DE LENGUAJE NATURAL · opcionales
│   ├── config.py        159 l   .env, llave, y el presupuesto de latencia duro
│   ├── resolver.py      345 l   entidades → ids, determinista, cuatro estados
│   ├── herramientas.py  835 l   esquemas tipados generados del catálogo
│   ├── nlu.py           736 l   el cauce de nueve pasos
│   └── entorno.py       294 l   los seis agentes de entorno
│
├── web_ui/src/          LAS SUPERFICIES · React 19 + Vite
│   ├── App.jsx          174 l   enrutado y portada
│   ├── comun.jsx        161 l   ROLES, FASES, api(), useDatos, Barra, Delta
│   ├── definiciones.jsx 612 l   las 38 definiciones formales de los globos
│   ├── etiquetas.jsx    146 l   identificador del motor → rótulo de pantalla
│   ├── index.css        787 l   el sistema visual entero
│   └── components/      Tablero · VistaPrivada · Consola · Mapa · Reloj · Ayuda
│
├── data/escenario/      EL CASO, en datos y no en código
├── scripts/             el corredor sin interfaz, para calibrar sin sala
├── tests/             2 106 l   150 verificadores sin modelo, en 2,3 s
│   ├── conftest.py              —   silencia LAS DOS capas: nada sale a la red
│   ├── test_invariantes.py     63   el motor
│   └── test_canal_ordenes.py   87   las capas que hablan con personas
│
├── README.md            por dónde empezar
├── PENDIENTES.md        qué falta · el único sitio donde se lleva la cuenta
└── docs/                este documento y los demás
```

**Los tamaños importan aquí.** `actions.py` con 1 692 líneas es el archivo más
grande y es el que más se toca: 34 clases, cada una con su validación y su
ejecución. Si crece mucho más, el corte natural es por frente (seguridad,
estrategia, logística), no por tipo de acción.

---

## 4. El motor por dentro

### El estado

Todo el mundo vive en un objeto `Estado` ([`state.py`](../src/engine/state.py)),
con **tres niveles espaciales** porque los ocho roles no deciden sobre lo mismo:

```
Nodo       un punto de cierre          24    Policía · Interior · Alcalde
Corredor   una secuencia de puntos      5    Transporte · Defensa
Region     un área con su reloj         4    Minas · Interior
```

Más `Reservas`, `Banderas`, `Unidad`, `Denuncia`, `Acuerdo` y el registro de
decisiones.

> **Desviación deliberada respecto de la guía de arquitectura.** Esa guía
> recomienda arrays paralelos de NumPy. Aquí se usan objetos, a propósito: 24
> nodos y no 657, lógica ramificada y no aritmética uniforme, 12 pasos por
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

**Cuatro pruebas los custodian**, y no solo en `vista_publica()`: también en las
ocho vistas privadas, en los deltas y en los hechos del mapa. Cada vez que se
añade una superficie hay que preguntarse si abre una puerta trasera a estos dos.

---

## 5. Los datos: el caso fuera del código

`data/escenario/estado_inicial.json` contiene **el caso**, y el motor no sabe
nada de él más allá de su forma:

```jsonc
{
  "fecha_inicio": "2021-05-11T06:00",
  "region_epicentro": "R-BEL",
  "regiones":   [ … 4 … ],
  "corredores": [ … 5 … ],
  "nodos":      [ … 24, con x/y para el mapa esquemático … ],
  "denuncias_iniciales": [ … el hecho H2 … ],
  "hecho_h1":   { … el incidente que la sala recibe … }
}
```

**Por qué en datos y no en código.** Se puede cambiar el escenario, apagar un
hecho detonante o probar otro territorio sin tocar el motor. Y `loader.py`
verifica las invariantes al cargar, **fallando ruidosamente**:

- toda región necesita al menos un corredor humanitario
- nunca una sola denuncia sin verificar (hacen falta ≥2, con veracidad distinta)
- todo punto necesita posición en el mapa

Un escenario que no las cumpla no arranca. Es preferible a arrancar y producir
un ejercicio sin dilema.

---

## 6. La API

[`src/api/main.py`](../src/api/main.py) es deliberadamente delgada: **toda la
lógica vive en el motor, que no sabe que esta capa existe.**

```
GET  /api/tablero              el tablero + deltas + hechos del mapa
GET  /api/vista/{rol}          la vista privada de un rol
GET  /api/vistas               las ocho, para el corredor sin interfaz
GET  /api/esfera               lo que se dice
GET  /api/catalogo             las 34 acciones, con su `en_claro`
GET  /api/config               si hay llave de API, y cuál es el archivo .env
GET  /api/metricas             las métricas de cierre
GET  /api/proyeccion           el país a 72 horas
GET  /api/consulta/{tema}      la rama de solo lectura del canal de órdenes

POST /api/consola/interpretar  texto → plan, con su banda de riesgo
POST /api/consola/elegir       resuelve una ambigüedad con elección tipada
POST /api/consola/ejecutar     ejecuta un plan ya leído en voz alta
POST /api/consola/noche        resuelve el interludio nocturno
POST /api/consola/fase/{fase}  mueve el reloj de fases
POST /api/consola/declarar_linea   la declaración del turno 0

GET  /{full_path}              sirve web_ui/dist (el SPA)
```

**El estado vive en memoria del proceso** (`_estado` y `motor`, globales). Es la
limitación conocida y es el pendiente **B1**: al cerrar el proceso se pierde la
corrida, y el debriefing dura más que cualquier turno.

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
| `comun.jsx` | `ROLES`, `FASES`, `api()`, `useDatos`, `Barra`, `Delta` | lo que usan todas las superficies |
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

## 9. Las pruebas

**150, sin modelo, en poco más de dos segundos.** Corren en cada cambio.

> **Que no salgan a la red no se hereda: se comprueba.** La cabecera de
> `test_canal_ordenes.py` decía que ninguna prueba llamaba a un modelo, y era
> verdad a medias. Su accesorio silenciaba la capa 4, pero las cinco pruebas que
> pasan por `/api/consola/ejecutar` disparan después la **capa 3** —la esfera
> pública— con el cliente real: **176 s por corrida y llamadas facturadas**, en
> la suite que se corre en cada cambio. Hoy las silencia
> [`tests/conftest.py`](../tests/conftest.py) con `autouse`, las dos, y
> `test_las_dos_capas_estan_silenciadas_en_las_pruebas` lo custodia.

```bash
uv run pytest -q
uv run pytest -q tests/test_canal_ordenes.py   # las capas 3 y 4
uv run pytest -q -k "delta or mapa"            # un subconjunto
```

Cada prueba existe porque **su propiedad se rompió alguna vez** o porque su
ruptura sería silenciosa — que es la peor clase de fallo: el ejercicio pierde su
objeto sin que nada reviente.

Van en dos archivos porque custodian dos cosas distintas:

| Archivo | Cuántas | Qué custodia |
|---|---|---|
| `test_invariantes.py` | 63 | **el motor** — que el mundo se comporte como dice el diseño |
| `test_canal_ordenes.py` | 87 | **las capas 3 y 4** — que lo que ocho personas dicen en voz alta se traduzca a lo que quisieron decir, o se repregunte |

> **El segundo archivo llegó tarde.** Durante varias versiones, sesenta y tres
> verificadores custodiaban el motor —que nadie toca durante el ejercicio— y
> **cero** custodiaban el canal por el que entran las órdenes de ocho personas en
> dos horas. Al sondearlo aparecieron nueve fallos, cuatro de ellos silenciosos.

Las del motor, agrupadas por lo que protegen:

| Grupo | Cuántas | Qué protegen |
|---|---|---|
| **Lo que nunca sale** | 4 | la mezcla real y la veracidad, en las cuatro superficies |
| **La mezcla real sí importa** | 3 | que `composicion_real` cambie el resultado — se rompió una vez |
| **El reloj y el oxígeno** | 4 | que las muertes dependan de las decisiones |
| **Riesgo y mitigadores** | 4 | el techo de 0,98 y que el estándar no rescate al descuidado |
| **Duplas y denuncias** | 6 | el bolsillo de tres, y que verificar aquí sea no verificar allá |
| **La mesa y el tiempo** | 8 | que la cohesión no sea una rampa determinista |
| **Aperturas** | 6 | que un corredor valga lo que su peor punto |
| **Jurisdicción y validación** | 5 | que una acción inválida no tumbe el resto |
| **Las ocho vistas** | 7 | que quepan en una pantalla y que los sesgos vayan en direcciones opuestas |
| **El escenario** | 4 | invariantes, territorio ficticio, posiciones del mapa |
| **Reloj, deltas y hechos** | 6 | que el delta mida el último paso y no abra puertas traseras |
| **La documentación** | 2 | que `PENDIENTE(Xn)` apunte a una entrada real |

Las dos últimas son inusuales y se ganaron su sitio: **la promesa de navegación
en los dos sentidos de `PENDIENTES.md` ya se había roto en silencio.**

Y las del canal de órdenes:

| Grupo | Cuántas | Qué protegen |
|---|---|---|
| **Un recurso que no existe** | 6 | que «el Puente de Brooklyn» no se opere en el que más se le parezca |
| **Una orden que no existe** | 5 | que no se fuerce la acción más parecida, y que el silencio diga por qué |
| **La ambigüedad** | 3 | que se pregunte, y que una orden compuesta no le robe el lugar a la otra |
| **Las enumeraciones** | 5 | que la unidad pedida no se cambie por la de por defecto |
| **Los criterios** | 4 | que «todos los puntos» sean N acciones y no la primera |
| **Preguntar no es ordenar** | 5 | que una consulta no ejecute nada |
| **Lo que la sala oye** | 6 | que la lectura diga sobre qué punto se actúa |
| **La consola** | 8 | que nada se ejecute a medias ni se caiga en silencio |
| **La degradación** | 3 | que sin llave, y con el proveedor caído, el canal siga traduciendo |
| **Lo que no puede salir** | 2 | la mezcla real y la veracidad, también por esta superficie |
| **El repertorio, sin llave** | 4 | que ninguna herramienta quede sin disparador — el canal no puede negar tener una acción que tiene |
| **Requisitos que no se regalan** | 5 | que el canal no se conceda la Alcaldía, ni una cifra, ni un responsable que nadie dijo |
| **Los valores por defecto** | 5 | que lo que el motor va a usar se diga en voz alta antes de confirmarlo |
| **El presupuesto y la esfera** | 6 | que la espera sea la declarada, y que solo publiquen las seis fuentes |
| **La consola, segunda tanda** | 4 | que preguntar no gaste un turno y que corregir una lista no la borre |

**Ninguna llama a un modelo.** El accesorio `sin_modelo` fuerza la rama
determinista, que además es la que corre cuando no hay llave: si alguna dejara de
pasar al quitar el modelo, la degradación sería decorativa.

---

## 10. Cómo añadir cosas

### Una acción nueva

1. Una clase en [`actions.py`](../src/engine/actions.py) que herede de `Accion`:

```python
class MiAccion(Accion):
    """Qué hace, y por qué existe en el ejercicio."""
    codigo = "X1"
    rol = "Minas"
    clase: Clase = "operativa"          # constitutiva | operativa | informativa
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
título) y la ficha impresa. Es el cambio más caro del repositorio: **ocho es un
número de diseño**, no una constante.

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
# 1 · el motor y las pruebas
uv sync
uv run pytest -q

# 2 · una corrida completa sin montar la sala
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
