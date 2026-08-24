# Arquitectura de un ejercicio de simulación de crisis

**Guía de referencia para montar casos nuevos**
Versión 1.0 · 2026-08-14

Este documento describe **la forma**, no el caso. Está escrito a partir de la
simulación de inundación de Macondo, pero deliberadamente separa lo que es
estructura de lo que era ese fenómeno concreto: sirve igual para un sismo, un
brote epidemiológico, un incendio forestal, una crisis de orden público o una
falla de infraestructura crítica.

Donde aparece el caso de inundación lo hace **como ilustración**, marcado así:

> *Ejemplo (inundación): …*

---

## Índice

1. [Las cuatro capas](#1-las-cuatro-capas)
2. [Capa 1 — El motor de simulación](#2-capa-1--el-motor-de-simulación)
3. [Capa 2 — Roles humanos](#3-capa-2--roles-humanos)
4. [Capa 3 — Roles de IA (actores autónomos)](#4-capa-3--roles-de-ia-actores-autónomos)
5. [Capa 4 — El agente de órdenes](#5-capa-4--el-agente-de-órdenes)
6. [Observabilidad y evaluación](#6-observabilidad-y-evaluación)
7. [Cómo montar un caso nuevo](#7-cómo-montar-un-caso-nuevo)
8. [Anexo — Errores que costaron tiempo](#8-anexo--errores-que-costaron-tiempo)

---

## 1. Las cuatro capas

Un ejercicio de simulación de crisis con participantes humanos y asistencia de IA
se compone de cuatro capas con responsabilidades **estrictamente separadas**. La
separación no es estética: cada vez que se difumina, aparece un modo de falla
concreto y medible (§5.3).

```
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 4 · AGENTE DE ÓRDENES                                      │
│  Traduce lenguaje natural a acciones tipadas. NO decide.         │
└───────────────────────────┬──────────────────────────────────────┘
                            │ acciones validadas
┌───────────────────────────▼──────────────────────────────────────┐
│  CAPA 1 · MOTOR DE SIMULACIÓN                                    │
│  Único dueño del estado. Decide, valida, ejecuta y reporta.      │
└───────────────────────────┬──────────────────────────────────────┘
                            │ estado
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────────┐  ┌───────────────────────────────────┐
│ CAPA 2 · ROLES HUMANOS   │  │ CAPA 3 · ROLES DE IA              │
│ Deciden. Ven un estado   │  │ Pueblan el mundo: prensa,         │
│ filtrado por competencia │  │ ciudadanía, autoridades técnicas  │
└──────────────────────────┘  └───────────────────────────────────┘
```

**El principio que ordena todo:**

> **El LLM traduce. El motor decide, valida, ejecuta y reporta.**
> Ninguna frase que un participante lea sobre el resultado de una orden puede
> haber sido escrita por un modelo antes de que la orden se ejecutara.

Todo lo demás en este documento es consecuencia de esa frase.

---

## 2. Capa 1 — El motor de simulación

El motor es un programa determinista sin ninguna dependencia de IA. Debe poder
ejecutarse de principio a fin sin clave de API. Si no puede, la arquitectura está
mal: significa que alguna decisión de la simulación se delegó al modelo.

### 2.1 El estado: arrays paralelos sobre unidades espaciales

El estado del mundo es un objeto plano de **arrays de igual longitud**, uno por
variable, indexados por **unidad espacial**. No objetos por entidad.

```python
@dataclass
class EstadoUnidades:
    n_unidades: int

    # Población por estado y grupo
    poblacion_sana_0_19:  np.ndarray
    poblacion_sana_20_60: np.ndarray
    afectados_leves:      np.ndarray
    afectados_graves:     np.ndarray
    fallecidos:           np.ndarray

    # Infraestructura
    dano_acumulado:       np.ndarray
    servicio_agua:        np.ndarray   # 1.0 disponible · 0.0 cortado
    servicio_energia:     np.ndarray

    # Recursos desplegados
    personal_tipo_a:      np.ndarray
    equipamiento_tipo_b:  np.ndarray
```

**Por qué arrays y no objetos:** un paso de simulación es una operación
vectorizada sobre todo el territorio. Con objetos por unidad, cada paso es un
bucle de Python y el ejercicio deja de correr en tiempo real. Además, cualquier
consulta agregada («cuánto personal hay en la zona X») es una suma de índices.

**La unidad espacial** es la granularidad mínima del fenómeno. Elegirla es la
primera decisión de diseño y condiciona todo lo demás.

> *Ejemplo (inundación): la manzana censal, cargada desde un GeoJSON con
> atributos de riesgo, altura y distancias. 657 manzanas agrupadas en 93
> barrios, más 19 sitios singulares (hospitales, colegios, estaciones).*

**Regla:** las unidades tienen un identificador estable y opaco (`ag_code`), y un
diccionario `id → índice` para traducir. Los nombres legibles viven fuera, en la
capa de resolución de entidades (§5.2), nunca en el motor.

### 2.2 El reloj: un único `step()`

```python
def step(self, dt_min: float) -> None:
    # 1. Procesar acciones pendientes (§2.5)
    # 2. Leer los drivers exógenos del instante actual
    # 3. Aplicar umbrales de infraestructura
    # 4. Transiciones de población y daño
    # 5. Avanzar gestores de subsistema (§2.4)
    # 6. Avanzar el reloj y notificar a las interfaces
```

Dos propiedades no negociables:

- **`step()` es la única forma de que pase el tiempo.** No hay temporizadores
  paralelos que modifiquen el estado.
- **`dt` es un parámetro, no una constante implícita.** Permite correr el mismo
  escenario acelerado para pruebas y a ritmo real para el ejercicio.

> *Ejemplo (inundación): `dt = 5` minutos simulados por paso, `DeltaT = 25`
> segundos reales entre pasos, `Ttotal = 1440` minutos (24 h de crisis en ~2 h
> de ejercicio).*

**Los drivers exógenos** —lo que ocurre sin que nadie lo decida— se leen de una
tabla temporal precalculada, no se generan al vuelo. Así el escenario es
reproducible y el facilitador sabe qué va a pasar y cuándo.

> *Ejemplo (inundación): una serie de intensidad de lluvia e inundación
> acumulada por minuto. Los umbrales de 25/30/35 mm disparan la caída de la
> energía, del acueducto y del puente.*

### 2.3 Acciones: el único modo de cambiar el estado

Toda mutación del estado pasa por una clase `Accion`. Sin excepciones.

```python
class Accion:
    def validar(self, motor) -> dict:
        """¿Es viable AHORA? NO muta nada.
        → {"ok": bool, "motivo": str|None, "parcial": bool}"""

    def ejecutar(self, motor) -> dict:
        """Aplica el efecto.
        → {"success": bool, "message": str}"""
```

Tres reglas que valen más que cualquier otra cosa de este documento:

1. **`validar()` es obligatorio y no muta.** Existe para poder decirle al
   participante *antes* si su orden es viable, y para no dejar el estado a
   medias. Una acción sin `validar()` es una acción que fallará en silencio.
2. **`ejecutar()` devuelve siempre un resultado estructurado.** Nunca `None`,
   nunca `print()` como único canal. Un error impreso en la consola del servidor
   es un error que nadie verá.
3. **Ninguna acción deja un array en negativo.** Toda resta se acota con
   `min(disponible, pedido)`.

#### Acciones directas e inversas

Por cada acción que **instala** algo debe existir la que lo **retira**, y ambas
deben vivir pegadas en el código.

| Directa | Inversa |
|---|---|
| desplegar recurso | retirar recurso y devolverlo al inventario |
| movilizar personal a un punto | replegar personal a su base |
| ingresar afectados | dar de alta |

**Comprobación obligatoria — ida y vuelta:** aplicar la directa y después la
inversa debe dejar el estado **numéricamente idéntico** al de partida. Se prueba
comparando arrays, no leyendo mensajes.

**Lo irreversible se declara, no se finge.** Un consumible ya repartido no se
puede recuperar; la inversa debe rechazarlo con su motivo.

> *Ejemplo (inundación): las raciones de comida y el agua distribuida son
> consumibles. `desactivar PL-01` responde «las raciones ya se repartieron y se
> consumieron» en vez de fingir que las retira.*

**Asimetría deliberada:** las inversas piden **menos** parámetros que sus
directas. El repliegue no pregunta destino —el motor sabe dónde está la base—;
retirar un recurso no pregunta lugar —el motor sabe dónde se instaló—.
Preguntarlo invita al participante a escribirlo mal.

### 2.4 Gestores de subsistema

Los procesos que tienen dinámica propia se encapsulan en gestores con su propio
`step()`, invocados por el motor:

| Gestor | Responsabilidad |
|---|---|
| **Adquisiciones** | catálogo, compras, tiempos de entrega, inventario, despliegue |
| **Presupuesto** | CAPEX al comprar, OPEX continuo mientras algo está desplegado |
| **Transporte y capacidad** | traslado de afectados a puntos de atención, ocupación |
| **Movilidad de población** | flujos de evacuación y retorno sobre una red |
| **Orden público / conducta** | reacción de la población al desempeño (malestar, disturbios) |

Cada gestor es sustituible sin tocar los demás. **La reacción de la población es
la que convierte el ejercicio en un ejercicio de gestión** y no en una hoja de
cálculo: si nada empeora cuando las decisiones son malas, no hay presión.

### 2.5 Tres colas, no una

```python
motor.cola_acciones            # inmediata: se aplica en el próximo step
motor.eventos_programados      # por TIEMPO: {"t_disparo": int, "accion": ...}
motor.acciones_condicionales   # por CONDICIÓN: {"condicion": fn(motor)->bool, ...}
```

La tercera es la que suele faltar y la que los participantes piden sin saber
nombrarla: *«en cuanto llegue el recurso X, mándalo a Y»*. Nadie sabe a qué hora
llegará, así que una cola por tiempo no sirve.

Tres salvaguardas imprescindibles en la cola condicional:

- **Caducidad.** Una orden en espera indefinida es una orden olvidada. Se
  descarta pasado un plazo y **queda constancia** en el registro.
- **Si la condición ya se cumple, no se difiere:** se ejecuta en el acto.
- **Una condición que lanza excepción descarta esa orden, no tumba el paso.** Un
  `except` silencioso la dejaría colgada para siempre.

### 2.6 Datos de entrada

Todo lo que define el caso vive **en datos, no en código**:

| Archivo | Contenido |
|---|---|
| `territorio.geojson` | unidades espaciales con sus atributos |
| `red_vial.geojson` | conectividad, si el fenómeno implica movilidad |
| `drivers.csv` | serie temporal del fenómeno exógeno |
| `catalogo_recursos.csv` | recursos: coste, tiempo de entrega, efecto, duración |
| `parametros.py` | constantes del modelo, todas con nombre y unidad |
| `matriz_informacion.csv` | qué ve cada rol (§3.2) |
| `alias.json` | cómo llama la gente a los lugares (§5.2) |

**Regla de oro:** si un dato aparece a la vez en un archivo y en el prompt de un
modelo, se desincronizará. Siempre. El catálogo que ve el modelo debe
**generarse** desde el CSV en el arranque.

> *Ejemplo (inundación): el catálogo estaba escrito a mano en el prompt y le
> faltaba un paquete. Durante todo un ejercicio, PL-08 fue invisible para el
> agente: un participante lo pidió y recibió «no logré identificar una acción
> operativa clara».*

### 2.7 Qué NO debe hacer el motor

- No conoce nombres legibles de lugares (eso es la capa 4).
- No conoce roles ni permisos (eso es la capa 2).
- No llama a ningún modelo de lenguaje. Nunca.
- No redacta texto para el participante más allá de un mensaje factual corto.

---

## 3. Capa 2 — Roles humanos

### 3.1 Competencias

Cada rol tiene un conjunto de acciones que le corresponden. Se declara en datos,
en un solo lugar:

```python
COMPETENCIAS = {
    1: {"acciones": ["DeclararEmergenciaRegional", ...]},
    4: {"acciones": ["MovilizarPersonal", ...], "recursos": ["tipo_a"]},
    ...
}
```

> *Ejemplo (inundación): 10 roles — Gobernador, Alcalde, secretarías sectoriales,
> comandantes de policía y fuerzas militares, jefe de comunicaciones.*

**Lección dura sobre restringir el espacio de salida del modelo.** Es tentador
construir el esquema de herramientas del modelo restringido al rol, con la idea
de que «si no puede movilizar personal militar, la herramienta no existe y no
podrá proponerla». **Se midió y es falso.** Con el enum restringido a un solo
valor, ante *«envía 30 policías y 30 militares»* el modelo no se abstuvo:
**forzó los 30 militares dentro del único valor disponible**, convirtiéndolos en
policías sin que nadie se enterara.

> **Regla:** el esquema por rol es una **pista**, no una garantía. Expón el enum
> completo y **rechaza en código determinista**, con un motivo que el
> participante pueda entender y accionar: *«la movilización del Ejército
> corresponde al Cmdte. FFMM»*.

### 3.2 Matriz de información

Un CSV que cruza **variable de estado × rol**. Alimenta dos cosas:

1. `filtrar_estado_para_rol(estado, rol)` — el filtrado **real y auditable**.
2. Un directorio inverso: qué rol sí tiene ese dato, para poder redirigir.

> **Nunca pidas a un modelo que se autocensure.** Filtrar el estado *antes* de
> construir el contexto es código verificable; pedirle al modelo que no cuente
> algo que tiene delante es una súplica.

### 3.3 La decisión de canal: por rol o canal único

Hay dos diseños de ejercicio, y hay que elegir a conciencia:

| | **Asistente por participante** | **Canal único (operador maestro)** |
|---|---|---|
| Quién escribe | cada rol, en su terminal | un operador transcribe lo ya deliberado |
| Permisos | los comprueba el código | los comprueban las personas en la sala |
| Filtrado | por rol, obligatorio | innecesario |
| Deliberación | ocurre contra la máquina | ocurre entre personas, y se transcribe |
| Complejidad | alta | baja |

**El canal único elimina de golpe media arquitectura** —permisos, filtrado,
autocensura— y desplaza la verificación de competencias a donde el ejercicio
quiere que esté: la conversación entre participantes. El coste es que se pierde
la trazabilidad automática de quién pidió qué.

> *Ejemplo (inundación): el ejercicio migró de asistente-por-rol a canal único a
> mitad del rediseño. La maquinaria de permisos se conservó pero dejó de
> aplicarse en el canal de órdenes.*

---

## 4. Capa 3 — Roles de IA (actores autónomos)

Son agentes que **pueblan el mundo** y generan presión sobre los participantes.
No ejecutan acciones sobre el estado: **producen contenido**. Esa distinción es
lo que los hace seguros.

### 4.1 Arquetipos

Cuatro arquetipos cubren la mayoría de ejercicios:

| Arquetipo | Qué hace | Presión que genera |
|---|---|---|
| **Autoridad técnica** | emite pronósticos y alertas oficiales | obliga a anticipar |
| **Ciudadanía** | publica en redes según cómo le va | vuelve visible el desempeño |
| **Prensa** | decide si publicar, pregunta, publica | obliga a comunicar |
| **Comunidad organizada** | interpela directamente a un rol concreto | obliga a rendir cuentas |

> *Ejemplo (inundación): IDEAM (autoridad meteorológica), población civil, medios
> de prensa, y la Junta de Acción Local, que escribe a la Secretaría de Gobierno.*

### 4.2 Estructura: un grafo pequeño por agente

Cada uno es un grafo de uno o dos nodos:

```
Autoridad técnica:   [analizar] → fin
Ciudadanía:          [reunir contexto] → [generar publicaciones] → fin
Prensa:              [decidir si publica] → [redactar y publicar] → fin
```

El patrón **decidir → ejecutar** de la prensa es el más valioso: separa *«¿hay
noticia?»* de *«escribe la noticia»*, y evita que el agente publique cada vez que
le toca el turno solo porque le toca.

### 4.3 Cadencia y no reentrada

```python
if (motor.t_actual - ultimo_disparo_X) >= INTERVALO_X and not _X_corriendo:
    lanzar_en_segundo_plano(disparar_X())
```

Tres reglas:

- **Cadencias distintas por agente**, en minutos de simulación.
  > *Ejemplo (inundación): autoridad técnica cada 30 min, ciudadanía y prensa
  > cada 60, comunidad cada 120.*
- **Bandera de no reentrada.** Una llamada al modelo puede tardar más que el
  intervalo. Sin la bandera se acumulan ejecuciones solapadas.
- **En segundo plano, siempre.** El bucle de simulación no puede bloquearse
  esperando a un modelo. Si el proveedor cae, el ejercicio sigue.

### 4.4 Contrato de salida

Cada agente devuelve **solo contenido**, en listas tipadas:

```python
{"mensajes_out": [...],      # mensajes dirigidos a un rol
 "publicaciones_out": [...]} # contenido público
```

**Ningún agente autónomo llama a `ejecutar()` sobre el motor.** Si un actor
autónomo pudiera mutar el estado, el ejercicio dejaría de ser reproducible y
sería imposible atribuir un resultado a las decisiones de los participantes.

Lo que sí reciben es **estado filtrado y su propio historial reciente** (las
últimas 2 publicaciones), para no repetirse.

---

## 5. Capa 4 — El agente de órdenes

Es la capa donde se concentra el riesgo, porque es la única donde interviene un
modelo de lenguaje sobre decisiones que mutan el mundo.

### 5.1 El cauce

Nueve pasos. **Solo el primero usa el modelo.**

```
   texto del participante
            │
   ┌────────▼─────────────────────────────────────────────┐
   │ 1 · NLU — tool calling con herramientas tipadas      │ ← 1 llamada
   │     salida: 0..n llamadas validadas por el esquema   │
   └────────┬─────────────────────────────────────────────┘
   ┌────────▼─────────────────────────────────────────────┐
   │ 2 · RESOLUTOR de entidades      (determinista)       │
   │ 3 · EXPANSOR de plan            (determinista)       │
   │ 4 · VALIDADOR / dry-run         (determinista)       │
   └────────┬─────────────────────────────────────────────┘
       ¿ambigüedad o falta un dato?
            │ sí                         │ no
   ┌────────▼──────────────┐    ┌────────▼──────────────┐
   │ 5 · PREVISUALIZAR     │    │ 6 · EJECUTAR          │
   │     plan en sesión    │    │ 7 · REPORTAR          │
   │     + opciones        │    │ 8 · SUGERIR (si falló)│
   └───────────────────────┘    └───────────────────────┘

   9 · CONSULTAR — rama de solo lectura, en paralelo
```

### 5.2 Las piezas, una por una

#### 1 · NLU por herramientas tipadas

Una sola llamada al modelo con `parallel_tool_calls`. Nunca JSON en texto plano
parseado a mano: si el modelo responde en prosa, el `except` acaba mostrando esa
prosa al participante como si fuera la interpretación oficial.

**Dos reglas de diseño del esquema:**

1. **Los nombres de lugar viajan como texto crudo.** El modelo NO los normaliza.
   Esa responsabilidad es de la capa determinista, que es auditable.
2. **El catálogo se genera desde los datos**, no se escribe en el prompt (§2.6).

#### 2 · Resolutor de entidades determinista

Traduce lo que la gente escribe a identificadores del motor, **sin modelo y sin
adivinar**. Termina siempre en uno de cuatro estados:

| Estado | Significado | Qué pasa |
|---|---|---|
| `ok` | una coincidencia clara | se ejecuta |
| `ambiguo` | varias candidatas, o parecido dudoso | **se pregunta** |
| `selector` | no es un lugar sino un criterio | lo resuelve el motor |
| `no_encontrado` | nada se parece lo bastante | se informa |

Escalones, en orden: normalización (minúsculas, sin diacríticos, sin prefijos) →
forma exacta → tokens → difuso con dos umbrales (`≥90` aceptar, `75-89`
preguntar, `<75` no encontrado).

> **La regla central: si un escalón produce más de una candidata, el resultado es
> `ambiguo`. Nunca se toma la primera.**

Quedarse con la primera coincidencia parcial produce el peor fallo posible: la
orden **se ejecuta en el lugar equivocado y nadie se entera**.

> *Ejemplo (inundación): «salud san antonio» resolvía al *barrio* San Antonio en
> vez de al *Centro de Salud* San Antonio. Medido: 6 casos de resolución
> silenciosamente incorrecta, y 53,4 % de acierto global. Con el resolutor
> determinista: 96,8 % y **0** resoluciones a lugar equivocado.*

Dos matices que costaron descubrir:

- **Si el texto es el nombre oficial completo, gana**, aunque sea prefijo de otro.
  La salvaguarda de ambigüedad es para formas derivadas, no para el nombre
  exacto. Sin esto, un desplegable de nombres oficiales ofrece opciones que el
  sistema luego repregunta.
- **Los alias viven en datos y se pueden añadir en caliente** (§6.3).

#### 3 · Expansor de plan

Convierte llamadas en **acciones atómicas**, y es donde se contiene la explosión
combinatoria.

> **Definición de acción atómica: una intención operativa con un destino lógico.**
> La cantidad es un parámetro, no una repetición. Los orígenes y destinos
> múltiples viajan como listas si la acción los admite, y el reparto lo hace el
> motor internamente.

Sin esta regla, un producto cartesiano entre orígenes y destinos genera miles de
acciones desde una sola frase.

> *Ejemplo (inundación): «movilizar todos los pacientes leves a los centros de
> refugio» generaba **1.270** acciones: el cruce completo de las manzanas de
> origen por las de destino. Con la regla: 1 acción con listas.*

**Tope de seguridad.** Si un plan expande por encima de un límite, no se ejecuta:
se devuelve con su desglose para que el operador confirme. No es un rechazo, es
una confirmación obligatoria.

> *Ejemplo (inundación): tope de 25. El plan legítimo más grande de toda la
> jornada fue de 13 acciones.*

#### 4 · Validador

Recorre **todas** las acciones anotando el estado de cada una.

> **Prohibido `break` al primer problema.** Una orden compuesta no puede morir
> entera porque a una de sus partes le falte un dato.

> *Ejemplo (inundación): «enviar 30 policías y 30 militares a Los Pinos»
> ejecutaba **cero** acciones porque faltaba el origen. 11 de 24 órdenes
> multi-recurso ejecutaron de menos por esta causa.*

Esto permite decir, por primera vez: *«de las 6 acciones que pidió, 4 se
ejecutan, 1 requiere que confirme el destino y 1 no está en sus competencias»*.

#### 5 · Previsualización con plan en sesión

Cuando hay ambigüedad o falta un dato obligatorio, **el plan entero espera** en
un objeto de sesión y se le muestra al operador con opciones concretas.

**Por qué el plan entero y no solo la parte dudosa:** resolver la duda y ejecutar
todo de una vez le sale más barato al operador que recibir la mitad ahora y tener
que reformular la otra mitad después.

> **La clave: la respuesta del operador es una elección con identidad de acción y
> de campo, no texto libre.** No vuelve a pasar por el modelo.

Sin esto aparecen las ejecuciones fantasma: la respuesta corta a una repregunta
entra de nuevo por el NLU como si fuera una orden nueva.

> *Ejemplo (inundación): las palabras «No», «400» y «Sí, confirmo» produjeron
> cada una una evacuación.*

Salvaguardas del plan aparcado:

- **Se consume al reanudarlo.** Reanudar dos veces ejecutaría dos veces.
- **Caduca.** Se validó contra un estado que ya cambió.
- **Una orden nueva lo descarta**, en servidor y en pantalla.
- **Las elecciones solo pueden tocar campos declarados**, o la reanudación sería
  una vía para inyectar argumentos arbitrarios.

#### 6, 7, 8 · Ejecutar, reportar, sugerir

```python
def reportar(plan):
    texto = plantilla(plan)     # 100 % determinista, DESPUÉS de ejecutar
```

El reporte distingue explícitamente los estados terminales, porque el
participante no tiene por qué saber qué se aplicó ya y qué está encolado:

```
Sr. Comandante, de su instrucción ejecuté 1 de 2 acciones:
  ✓ 30 unidades tipo A: Base → Zona 4. Aplicado.
  ⏳ Despliegue de recurso B → Zona 7. Se aplica en el próximo paso (t+15 min).
  ✗ 30 unidades tipo C → Zona 4. No está en sus competencias: corresponde a …

Para la próxima, puede darme ambas en un solo mensaje indicando el origen:
  «Envía 30 unidades tipo A desde la base a la Zona 4»
```

El bloque final lo produce el **sugeridor**, activo **solo cuando hubo fallo**,
desde una plantilla asociada al tipo de fallo. Nunca de una generación libre.

#### 9 · Consultas: hechos, no párrafos

Un canal de consultas que entrega al modelo un **párrafo con totales agregados**
lo obliga a inventar en cuanto le preguntan por una zona concreta.

> **Regla: extraiga los hechos pertinentes del motor y páselos como datos
> estructurados. El modelo solo los pone en prosa.**

La hoja de datos se compone **por tema**, no se vuelca entera: un modelo al que
se le da de más responde de más.

**Dos trampas de la forma de los datos**, ambas medidas:

1. **`null` es ambiguo entre «no lo sé» y «no hay».** El modelo lo lee como
   laguna y responde «no tengo ese dato» cuando el dato existe y vale cero. Use
   un texto explícito: `"ninguna fuera de su base"`.
2. **Dos escalas en la misma hoja se confunden.** Con datos globales y de una
   zona juntos, el modelo dio el total del municipio como si fuera el del barrio.
   Nombre los ámbitos de forma imposible de confundir y añada una nota de
   alcance.

**Lo que no se puede calcular se declara.** Si el motor no modela una magnitud,
la respuesta correcta es decirlo, no aproximarla.

### 5.3 Los ocho modos de falla y su antídoto

Esta tabla es el resumen operativo del documento. Cada fila se observó y se midió
en un ejercicio real.

| # | Modo de falla | Antídoto |
|---|---|---|
| **F1** | La confirmación se redacta antes de ejecutar | Reporte determinista **después** de ejecutar, desde resultados reales |
| **F2** | Una parte incompleta mata la orden entera | Validación por acción, **sin `break`** |
| **F3** | Resolución de entidades que acierta mal en silencio | Resolutor determinista de 4 estados; ambigüedad → preguntar |
| **F4** | Explosión combinatoria origen × destino | Acción atómica = intención + destino lógico; tope de seguridad |
| **F5** | El modelo fuerza la acción más parecida y se ejecuta | Herramientas tipadas; si no encaja, se dice qué sí se puede hacer |
| **F6** | El historial contamina el turno siguiente | Plan en sesión; la respuesta es una elección, no texto |
| **F7** | Clasificador orden/consulta con decisión irreversible | Consultar es una herramienta más; un mensaje puede ser ambas |
| **F8** | El canal de consultas no tiene fuente de verdad | Hoja de datos por tema extraída del motor |

### 5.4 La invariante del sistema

> **Toda afirmación de éxito mostrada a un participante debe poder rastrearse a
> un resultado del motor con `success == True` o a un encolado que superó su
> validación, producido en ese mismo turno.**

Es comprobable automáticamente: se recorre la respuesta buscando verbos de
confirmación y se exige que exista una acción en estado terminal exitoso. **Debe
ser una métrica bloqueante.**

Un matiz que solo aparece al medirlo: **los turnos de consulta quedan fuera**. Una
respuesta correcta sobre el estado dice cosas como *«se compró 1 recurso, está en
camino»* —verdadera y respaldada— pero no ejecuta ninguna acción. Contarla como
afirmación sin respaldo llena la métrica de falsas alarmas, y **una alarma que
suena siempre deja de mirarse**.

---

## 6. Observabilidad y evaluación

### 6.1 Instrumentar desde el primer día

**Antes de mejorar nada, mida.** Un evento canónico por turno, en JSONL:

```json
{"turn_id": "...", "ts": "...", "t_sim": 205, "rol": "...",
 "texto_usuario": "...",
 "nlu":       {"modelo": "...", "tool_calls": [...], "tokens": ..., "latencia_ms": ...},
 "entidades": [{"crudo": "...", "estado": "ambiguo", "candidatos": [...]}],
 "plan":      {"n_acciones": 5, "acciones": [{"estado_final": "encolada", ...}]},
 "interaccion": {"hubo_pausa": true, "resuelto_por": "opcion"},
 "resultado": {"n_solicitadas": 5, "n_ejecutadas": 3, "fidelidad": 0.8,
               "afirmaciones_sin_respaldo": 0},
 "coste": {"tokens_total": 1002, "usd_estimado": 0.00031}}
```

Con esto, cualquier métrica del ejercicio es una consulta. Sin esto, es
arqueología: cruzar a mano dos archivos que nunca se diseñaron para cruzarse.

**Cuidado:** anotar el dato en el código no basta. Compruebe que **llega al
archivo**. Dos campos se perdían en la serialización sin que ninguna prueba lo
detectara, porque las pruebas miraban el código y no el dato de salida.

### 6.2 Métricas que importan

| Métrica | Qué revela |
|---|---|
| **Tasa de reintento** | mensajes muy parecidos del mismo equipo en poco tiempo. **La métrica síntesis:** mide cuánto del ejercicio se gasta peleando con la herramienta |
| **Fidelidad de ejecución** | acciones exitosas ÷ solicitadas |
| **Entidades no resueltas** | calidad del resolutor en uso real |
| **Afirmaciones sin respaldo** | 🔒 bloqueante |
| **Latencia p95** | si supera unos segundos, el operador reformula |

> *Ejemplo (inundación): **el 31 % de los mensajes fueron reintentos**. Uno de
> cada tres turnos se gastó peleando con la interfaz, no gestionando la crisis.*

### 6.3 Consola del facilitador

Una vista en vivo sobre esa telemetría, **durante** el ejercicio:

- las métricas de cabecera con su meta al lado;
- **las entidades que están fallando, con alta de alias en caliente** — si tres
  equipos escriben lo mismo y no resuelve, el facilitador lo corrige en el
  momento y deja de fallar para el resto del ejercicio, sin redespliegue;
- los turnos donde el participante pidió más de lo que obtuvo;
- **exportación de la cronología de decisiones** por equipo, ordenada por tiempo
  de simulación: qué se pidió, qué se ejecutó, qué no y por qué. Es el
  entregable del debriefing.

### 6.4 Banco de pruebas

Dos niveles, y el primero es el que se usa a diario:

1. **Verificadores sin modelo.** Comprueban propiedades estructurales y de
   comportamiento sin consumir tokens: que la validación no aborte, que la ida y
   vuelta cuadre, que la previsualización no afirme éxito, que la UI y el agente
   lean de la misma fuente. Corren en segundos y se ejecutan en cada cambio.
2. **Golden set con el modelo.** Los mensajes reales de un ejercicio previo,
   etiquetados, más variantes sintéticas por **mutación controlada** (quitar
   tildes, inyectar typos observados, sustituir por alias, componer órdenes
   múltiples). Las métricas se reportan **siempre separadas por origen**.

> **Cuidado con el criterio de evaluación.** La primera medición dio 73,9 %
> porque contaba las consultas bien contestadas como fallos de ejecución. El
> valor real era 97,3 %. Un criterio mal puesto puede premiar exactamente el
> comportamiento que se quiere eliminar.

---

## 7. Cómo montar un caso nuevo

Orden recomendado. Las tres primeras etapas no requieren ningún modelo.

### Etapa A — Definir el mundo

1. **Unidad espacial** y su fuente geográfica.
2. **Variables de estado**: poblaciones por estado, infraestructura, recursos.
3. **Driver exógeno** y sus umbrales, como serie temporal precalculada.
4. **Parámetros** del modelo, con nombre y unidad, en un solo archivo.

### Etapa B — Definir la mecánica

5. **Catálogo de recursos** en CSV: coste, tiempo de entrega, efecto, duración.
   > Decida explícitamente **si los recursos caducan**. Si `duracion` está en el
   > catálogo pero el motor no la usa, «renovar» no significará nada y hay que
   > decirlo en vez de fingirlo.
6. **Acciones directas**, cada una con `validar()` y resultado estructurado.
7. **Acciones inversas**, con prueba de ida y vuelta.
   > Antes de escribir cada una, **compruebe que no existe ya con otro nombre**.
8. **Gestores de subsistema**, incluido el de reacción de la población.

### Etapa C — Definir el ejercicio

9. **Roles humanos** y sus competencias.
10. **Matriz de información** por rol.
11. **Decidir el canal**: asistente por rol o canal único (§3.3).
12. **Roles de IA**: arquetipos, cadencias, contrato de salida.

### Etapa D — El agente de órdenes

13. **Instrumentación primero.** Evento canónico por turno, antes que nada más.
14. **Resolutor de entidades** con la tabla de alias sembrada.
    > Es la mejor relación esfuerzo/impacto de todo el sistema y no toca ni el
    > motor ni el modelo.
15. **Herramientas tipadas** generadas desde el catálogo.
16. **Validación por acción**, expansor con tope, reporte determinista.
17. **Previsualización** con plan en sesión.
18. **Consultas** por hoja de datos.
19. **Consola del facilitador** y exportación de cronología.
20. **Autocompletado y panel de acciones** en la interfaz.

### Etapa E — Antes del ejercicio real

21. Correr el golden set y **actualizar las cifras**.
22. **Vaciar los logs de pruebas.**
23. Ensayo completo con el facilitador.

---

## 8. Anexo — Errores que costaron tiempo

Reglas transversales, todas aprendidas a base de perder horas.

### Sobre el modelo

1. **La forma de los datos induce la alucinación.** No es solo qué datos le da,
   sino cómo. `null` ambiguo y dos escalas con nombres parecidos reintrodujeron,
   dentro de su propia solución, el fallo que venían a eliminar.
2. **Restringir el espacio de salida no impide que el modelo se salga: lo empuja
   a forzar la orden dentro de lo disponible.** Y eso es peor, porque es
   silencioso.
3. **Cuando el usuario aprende a defenderse de la herramienta, el problema es de
   arquitectura.** Si empiezan a escribir «(es solo consulta)» al final de sus
   preguntas, no lo arregle con prompt.

### Sobre las fuentes de verdad

4. **Un dato en dos sitios se desincroniza.** Catálogos, listas de lugares,
   campos obligatorios: una sola fuente, siempre.
5. **La interfaz debe leer de las mismas fuentes que el agente.** Una lista
   propia en el frontend es un catálogo duplicado con otro nombre.
6. **Antes de añadir una capacidad, compruebe que no existe ya.** Dos de cuatro
   acciones comprometidas no hacían falta: una ya estaba con otro nombre —y mejor
   implementada— y la otra no tenía mecánica que invertir.

### Sobre las pruebas

7. **Una comprobación sobre el código no sustituye a una sobre el dato que
   sale.** Escriba un evento y léalo de vuelta.
8. **Las pruebas estructurales por `grep` se rompen al refactorizar aunque la
   propiedad se mantenga.** Prefiera comprobar comportamiento; cuando no se pueda,
   apunte a la propiedad, no a la forma del código.
9. **Una prueba en la que todo falla no demuestra nada.** Si el escenario deja
   todas las acciones fallando, la invariante se cumple sola.

### Sobre el reporte

10. **Un error impreso en la consola del servidor es un error que nadie verá.**
11. **No añada una pista genérica si el motor ya explicó el motivo.** «El recurso
    no caduca» seguido de «revise disponibilidad de recursos» se contradice.
12. **Distinga ejecutado de encolado.** Los participantes preguntan
    repetidamente por esto cuando el sistema no lo dice.

### Sobre el entorno

13. **Las consolas Windows son cp1252**: imprimir acentos o símbolos revienta.
    Fuerce UTF-8 al arranque de cada script.
14. **`array or []` con NumPy lanza `ValueError`**, y un `try/except` amplio lo
    convierte en un resultado vacío silencioso.
15. **Reemplazar texto por script no avisa cuando no encuentra el ancla.**
    Verifique siempre después de editar.

---

*Documento derivado del rediseño del canal de órdenes de la simulación de crisis
de Macondo (2026). El detalle específico de ese caso está en
`arquitectura_agente_v2.md`.*
