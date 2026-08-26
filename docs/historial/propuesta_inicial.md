# Propuesta de simulación — El Estado frente al Estallido Social

**Caso:** Paro Nacional de 2021 · Puesto de Mando Unificado · Casa de Nariño, segunda semana de mayo
**Alcance de este documento:** el motor de simulación y su lógica. No propone código.
**Versión:** 1.0 · Documento de diseño para discusión del equipo

Este documento propone **qué debe modelar el motor**: con qué variables, qué reglas
acoplan unas decisiones con otras y qué dilemas quedan garantizados por
construcción. Sigue la arquitectura de cuatro capas de
[`../guia_arquitectura_simulaciones.md`](../guia_arquitectura_simulaciones.md) y toma
los ocho roles, sus recursos y sus acciones del Manual de Roles y de la Matriz
Operativa ya elaborados.

---

## Resumen

**Una sola diferencia con Macondo ordena todo el diseño: la lluvia no reacciona a
lo que usted decide, una movilización sí.** El motor deja de simular daños y pasa
a simular retroalimentación. Abrir un corredor por la fuerza puede cerrar dos, y
eso tiene que salir de la aritmética del motor, no de un guion.

**Cinco decisiones de diseño definen la propuesta:**

| | Decisión | Por qué |
|---|---|---|
| **1** | **El Estado no observa el mundo: lo estima.** Cada nodo tiene una composición real oculta, y cuatro fuentes la estiman con sesgos opuestos. | Sin esto, la pregunta del frente de seguridad —qué evidencia se exige antes de tratar un punto como violencia organizada— no tiene contenido. |
| **2** | **Tres vías de abrir un corredor con economías distintas.** La fuerza es rápida y reabre esa misma noche; la concertación es lenta y se sostiene; el desgaste es gratis y tarda. | Es el corazón pedagógico. Convierte una frase del caso en una cuenta. |
| **3** | **El estándar de derechos es un multiplicador de riesgo.** Reglas escritas, identificación, registro, dupla presente: seis mitigadores que dividen la probabilidad de incidente por casi cinco. | El rol sin voto y sin fuerza resulta ser el que más reduce la probabilidad del peor resultado, y se descubre haciendo la cuenta. |
| **4** | **Lo primero no es el territorio: es la mesa.** Seis acciones «constitutivas» no aparecen en el tablero, no abren ningún corredor y modifican todo lo posterior. Nada está bloqueado; todo está tarifado. | La mayoría de las salas se las salta y paga entre el turno 4 y el 6. Ese descubrimiento es la segunda pregunta del caso. |
| **5** | **Una sola sala, un solo teclado, ninguna pantalla individual.** Dos proyecciones comunes; la información reservada se entrega en papel, en mano. | Responde al hallazgo del ejercicio anterior: una pantalla por participante produce ocho personas mirando ocho pantallas. |

**Lo que cuesta montar:** 8 participantes · 1 moderador · **2 horas exactas**
(12 min de instalación + 5 turnos de decisión de 13 min + 4 interludios nocturnos
de 3 min + 20 min de debriefing + holgura) · dos proyectores · fichas y sobres
impresos. El motor físico de Macondo no se reutiliza; **todo lo demás de su
arquitectura sí** (§13).

**Lo que necesito de ti:** las seis decisiones de [§12.1](#121-lo-que-hay-que-decidir-antes-de-construir),
en particular si los nombres van reales o ficticios y si el ejercicio lleva
marcador. Los ajustes técnicos de §12.2 los recomiendo yo y solo necesitan visto
bueno.

**Lo que no está resuelto:** ningún coeficiente está calibrado y no hay forma de
calibrarlo en el escritorio. La primera corrida es una medición, no un ejercicio.

> Si tienes veinte minutos y no dos horas: §1 (qué cambia), §4.1–4.3 (los tres
> motores que importan), §7 (los dilemas) y §12 (lo que hay que decidir).

---

## Índice

1. [Lo que cambia respecto de Macondo](#1-lo-que-cambia-respecto-de-macondo)
2. [El sustrato: qué se modela](#2-el-sustrato-qué-se-modela)
3. [Variables de estado](#3-variables-de-estado)
4. [Los seis motores](#4-los-seis-motores)
5. [El arranque y el ciclo](#5-el-arranque-y-el-ciclo)
6. [Acciones, efectos y acoplamientos](#6-acciones-efectos-y-acoplamientos)
7. [Los dilemas que el motor vuelve inevitables](#7-los-dilemas-que-el-motor-vuelve-inevitables)
8. [Métricas y debriefing](#8-métricas-y-debriefing)
9. [Roles de IA: quién puebla el mundo](#9-roles-de-ia-quién-puebla-el-mundo)
10. [La interfaz: una sala sin pantallas individuales](#10-la-interfaz-una-sala-sin-pantallas-individuales)
11. [Qué NO debe hacer el motor](#11-qué-no-debe-hacer-el-motor)
12. [Decisiones abiertas](#12-decisiones-abiertas)
13. [Qué se reutiliza de Macondo](#13-qué-se-reutiliza-de-macondo)

---

## 1. Lo que cambia respecto de Macondo

En Macondo el fenómeno era exógeno y precalculado: el perfil de lluvia estaba en
un CSV y los participantes gestionaban sus consecuencias. Aquí es **reflexivo**:
cada operación de fuerza, cada cifra desmentida y cada sesión de mesa modifica la
intensidad y la forma de aquello que se intenta contener.

De ahí, cuatro cambios estructurales:

| | **Macondo (inundación)** | **Estallido social** |
|---|---|---|
| **Driver** | exógeno, precalculado, indiferente | endógeno y reflexivo; responde a las decisiones |
| **Sustrato** | físico (agua, daño, heridos) | político-social (legitimidad, control, abastecimiento) |
| **Recurso crítico** | presupuesto y paquetes logísticos | capacidad de fuerza **y** legitimidad, ambas finitas |
| **Reloj** | 24 h en pasos de 5 min | 5 días en turnos de 12 h; el reloj lo fija el agotamiento |
| **Error grave** | desplegar tarde | abrir un corredor y cerrar dos |
| **Verdad** | el motor la conoce y la reparte filtrada | **nadie la conoce**; hay estimaciones en conflicto |

Ese último punto es el más importante y el que más trabajo pide. En Macondo el
estado del mundo era verdadero y el filtrado por rol solo ocultaba partes. Aquí
**el Estado no observa el mundo: lo estima**, y estima mal de maneras
sistemáticas y distintas según quién estime. La guerra de cifras del caso real no
es ambientación: es una variable de estado.

---

## 2. El sustrato: qué se modela

### 2.1 Tres niveles espaciales, no uno

Macondo tenía una sola unidad espacial (la manzana). Aquí hacen falta tres,
porque las decisiones se toman en niveles distintos:

| Nivel | Qué es | Cardinalidad propuesta | Quién decide sobre él |
|---|---|---|---|
| **Nodo** | un punto de cierre concreto | **24 modelados**, que representan >1.000 reales | Policía (ESMAD), Alcalde (mesa local) |
| **Corredor** | secuencia ordenada de nodos entre origen y destino | ~12 | Transporte (prioriza), Defensa (opera) |
| **Región** | departamento o área metropolitana | 6 (Valle, Cauca, Nariño, Buenaventura, Bogotá, Antioquia) | Minas (asigna), Interior (concerta) |

**Por qué 24 nodos y no 1.000.** Mil puntos no caben en una deliberación de sala.
Se modelan los nodos que **deciden un corredor**: el resto entra como presión
agregada por región (`nodos_secundarios_activos`), que crece o decrece pero no se
gestiona uno a uno. Un nodo modelado representa un cierre con nombre, ubicación,
composición y contraparte propia.

> **Regla heredada:** identificador estable y opaco por nodo (`nodo_id`); los
> nombres legibles viven en la capa de resolución de entidades, nunca en el motor.

### 2.2 Un corredor no está abierto o cerrado

Tiene un **caudal** ∈ [0, 1]: la fracción del flujo normal que pasa. Se calcula
como el mínimo de los caudales de sus nodos —un corredor es tan bueno como su
peor punto— y determina cuánto abastecimiento llega aguas abajo.

Esto habilita una mecánica del caso: *«una docena de camiones presentada como
normalización se desmiente sola»*. Anunciar un corredor abierto con caudal 0,08
es verificablemente falso y cuesta legitimidad. La acción A5 del Ministro de
Transporte —anunciar solo hechos verificados— existe precisamente para eso.

---

## 3. Variables de estado

### 3.1 Por nodo de cierre

```
nodo_id                     identificador opaco
corredor_id                 a qué corredor pertenece (o ninguno: cierre urbano)
region_id
dureza                 [0,1]  cuánto cuesta abrirlo por fuerza
caudal                 [0,1]  fracción de flujo que deja pasar
dias_sostenido           int  antigüedad del cierre
masa_presente            int  personas en el punto (varía día/noche)
apoyo_local            [0,1]  respaldo del barrio o vereda al cierre
control_voceria        [0,1]  fracción del nodo que la vocería reconocida controla
proximidad_infra_critica bool  contiguo a instalación energética o refinería
modo_apertura           enum  {cerrado, fuerza, concertacion, desgaste}
turnos_desde_apertura    int  para el modelo de reapertura
```

**Y la variable que no se observa:**

```
composicion_real       vector de 3, suma 1
  ├─ protesta_legitima
  ├─ vandalismo_oportunista
  └─ estructura_organizada     ← financiada, con mando, con propósito
```

Ningún rol ve `composicion_real`. Cada uno ve una **estimación con sesgo propio**
(§4.4). Esto es deliberado: la pregunta central del frente de seguridad —*qué
evidencia se exige para tratar un punto como violencia organizada y no como
protesta*— no tiene contenido si el motor reparte la verdad.

### 3.2 Por corredor

```
caudal_efectivo        [0,1]  mínimo de los caudales de sus nodos
poblacion_aguas_abajo    int  cuánta gente depende de él
costo_diario_mm_cop    float  pérdida económica por día cerrado
clase_prioridad         set   {alimentario, humanitario, combustible, general}
anunciado_abierto       bool  si el Gobierno lo declaró abierto
```

`clase_prioridad` es un conjunto, no un valor: un corredor puede ser a la vez
alimentario y humanitario, y eso multiplica el costo de aplazarlo. Las clases
alimentaria y humanitaria son las que absorbieron Transporte y Minas de los
ministerios de Agricultura y Salud eliminados.

### 3.3 Por región — el reloj de la crisis

```
dias_autonomia_combustible  float   decrece con consumo, crece si entra caudal
dias_autonomia_alimentos    float
dias_autonomia_oxigeno      float   el más corto y el más grave — ver §4.5
presion_hospitalaria        [0,1]
muertes_evitables           int     acumulador; solo crece; no se compensa
indice_precios              float   1.0 = normal
intensidad_movilizacion     [0,100] regional
nodos_secundarios_activos   int     los no modelados
```

**Los días de autonomía son el driver del caso**, y a diferencia de la lluvia son
**endógenos**: bajan solos y solo suben si alguien abre un corredor. La acción A4
del Ministro de Minas —entregar a la mesa el calendario de agotamiento— convierte
la deliberación en un plazo. Que sea el propio motor quien calcula ese calendario,
y no un dato de guion, es lo que hace que la presión sea real.

> **Efecto de segundo orden que hay que modelar:** el oxígeno medicinal y las
> plantas de emergencia hospitalarias dependen del combustible. Y la fuerza
> pública también. Un desabastecimiento de combustible degrada simultáneamente la
> capacidad de contención y la red hospitalaria. Es la dependencia sistémica que
> justifica el rol de Minas.

### 3.4 Las cuatro reservas sistémicas

Son variables globales, escalares, en [0, 100]. Se consumen rápido y se
recuperan despacio. **Tres son reservas y una no**: la exposición internacional
funciona al revés —crece con el daño y es mala arriba— y solo se agrupa aquí
porque comparte escala y umbrales. Conviene mostrarla en el tablero con el eje
invertido para que la sala lea siempre «arriba es peor» en las cuatro. **Son el equivalente al presupuesto de Macondo**, pero a
diferencia del dinero no se pueden pedir prestadas.

| Reserva | Qué representa | Qué la consume | Qué la repone |
|---|---|---|---|
| **Legitimidad interna** | respaldo ciudadano a la respuesta estatal | incidentes con víctimas, imágenes virales, cifras desmentidas | acuerdos verificables cumplidos, aperturas concertadas, constataciones favorables de la Defensoría |
| **Credibilidad de la mesa** | viabilidad del canal de diálogo | operar el día de una sesión, incumplir una contraprestación ofrecida, reconocer y luego desconocer a un interlocutor | sesiones con acuerdo verificable, notificación previa cumplida |
| **Exposición internacional** | *invertida:* cuánto observa el mundo | víctimas, corredor humanitario negado, uso de militares en control de multitudes | reglas escritas publicadas, acceso concedido a verificación, visita atendida |
| **Cohesión de la mesa** | si el PMU actúa como uno o como ocho | desautorizaciones públicas, operaciones no informadas, vocerías contradictorias | decisiones escritas con responsable nominado, protocolo de vocería respetado |

**Las reservas tienen umbrales duros**, no efectos continuos suaves. Esto importa:
un deterioro gradual no produce decisiones, un umbral sí.

| Reserva | Umbral | Qué se activa al cruzarlo hacia abajo |
|---|---|---|
| Legitimidad interna | < 40 | los gremios camioneros evalúan sumarse al paro cada turno |
| Legitimidad interna | < 25 | se suman: el cierre pasa a ser paro logístico nacional |
| Credibilidad de la mesa | < 30 | el Comité Nacional del Paro suspende su participación |
| Credibilidad de la mesa | < 15 | no vuelve a sentarse en lo que resta del ejercicio |
| Exposición internacional | > 70 | pronunciamientos de organismos; la conmoción interior queda políticamente cerrada |
| Cohesión de la mesa | < 35 | los agentes de entorno empiezan a citar contradicciones entre roles |

### 3.5 Capacidad de fuerza

```
ESMAD:      escuadrones_totales   40      (el activo escaso del ejercicio)
Policía:    unidades_disponibles  ~déficit de 20.000 efectivos para control urbano
Militar:    unidades_disponibles  ~déficit de 30.000; solo protección estática
                                  salvo asistencia militar firmada
```

Por unidad:

```
asignacion       enum {reserva, contencion_estatica, operacion, escolta, custodia, relevo}
nodo_asignado    o instalacion_asignada
fatiga           [0,1]   +0,15 por turno desplegada · −0,30 por turno en relevo
turnos_continuos int
```

**La fatiga es el factor de error, y el error individual es el riesgo sistémico.**
`fatiga` entra directamente en la probabilidad de incidente (§4.2). La acción A5
del Director de la Policía —solicitar relevo aceptando reducir cobertura— es un
intercambio explícito entre exposición inmediata y probabilidad de catástrofe
reputacional.

**Custodia de infraestructura crítica.** Cada instalación declarada crítica
inmoviliza 2 unidades de policía **o** 3 militares por turno. El redespliegue
militar del Ministro de Defensa (A2) libera policías para ESMAD, al precio de
abrir un frente rural desatendido, que el motor contabiliza como
`frentes_rurales_descubiertos` y que produce sus propios eventos.

### 3.6 Por rol

```
capital_politico   [0,100]   capacidad de sostener una posición contra la sala
objetivo_publico   texto     el del §4 de su ficha
agenda_reservada   estructura con condición de logro (el §11, oculto)
acciones_usadas    registro  A1..A5 y en qué turno
```

El capital político **no es un puntaje de victoria**: es una restricción. Un rol
por debajo de 20 no puede sostener una posición contra tres roles opuestos; su
acción se ejecuta degradada o se bloquea. Es lo que impide que un participante
elocuente gane todas las discusiones sin costo acumulado.

---

## 4. Los seis motores

Cada uno con su propio `step()`, invocado por el motor principal en orden fijo.
Sustituibles de forma independiente.

### 4.1 Motor de movilización — el adversario reflexivo

**Es el motor que define el caso.** Si solo se implementa uno, es este.

```
intensidad_movilizacion  [0,100] nacional, con multiplicador regional
```

**Sube con:**

| Fuente | Magnitud | Nota |
|---|---|---|
| incidente con víctima mortal | +12 a +25 | según difusión de la imagen |
| imagen viral sin víctima | +5 a +10 | uso desproporcionado, agente sin identificar |
| militares en control de multitudes | +8 | independiente del resultado |
| jornada nacional programada | +10 | exógena, en el calendario |
| turno sin acuerdo verificable | +1,5 | acumulativo: la indefinición cuesta |
| cifra oficial desmentida públicamente | +4 | |

**Baja con:**

| Fuente | Magnitud |
|---|---|
| acuerdo verificable anunciado y cumplido | −8 |
| turno sin incidentes | −2 |
| apertura concertada de un corredor priorizado | −4 |
| contraprestación legislativa efectivamente tramitada | −6 |

**Y la intensidad realimenta el mundo:**

```
tasa_regeneracion_nodos  = f(intensidad)      nodos nuevos por turno
dureza de nodos abiertos = g(intensidad)      cuánto cuesta la próxima vez
masa_presente por nodo   = h(intensidad)      cuánta gente hay
```

> **El bucle central del ejercicio:** operación de fuerza → probabilidad de
> incidente → imagen viral → intensidad sube → aparecen nodos nuevos en otras
> ciudades → hace falta más fuerza → la fuerza disponible es la misma.
>
> **Abrir un corredor por la fuerza puede cerrar dos.** El motor debe producir
> ese resultado sin que nadie lo escriba en un guion.

#### Dos variables que se mueven en direcciones opuestas

Un matiz que cuesta ver y que hace falta modelar por separado:

- `intensidad_movilizacion` **sube** con el uso de la fuerza — es rabia contra el Estado.
- `apoyo_local` al cierre **baja** con la escasez prolongada — la gente quiere comer.

No son la misma variable con signo contrario. Esto es lo que da contenido a la
acción A4 del Alcalde de Cali: un esquema humanitario municipal **reduce el
incentivo material del cierre** (baja `apoyo_local`) sin alimentar la
movilización. Es la única vía de apertura que no consume ninguna reserva.

También explica por qué la escasez no es unívocamente mala para el Gobierno y por
qué dejarla correr es una tentación real y un error: baja `apoyo_local`, pero
sube `intensidad` en toda la región y consume el reloj de la autonomía.

### 4.2 Motor de fuerza e incidentes

Cuando se aplica fuerza sobre un nodo, el motor calcula una **exposición al
riesgo** y después la satura:

```
riesgo = base(tipo_unidad)
       × (1 + fatiga_media)
       × (1 + dureza_nodo)
       × (1 + masa_presente / masa_referencia)
       × factor_nocturno
       × Π (mitigadores)

P(incidente) = 1 − e^(−riesgo)        ← saturación exponencial
```

> **Por qué la saturación y no el producto directo.** El producto crudo no está
> acotado: militares fatigados, de noche, en un nodo duro y concurrido dan
> `0,45 × 2,0 × 2,0 × 3,0 × 1,6 = 8,6`, que no es una probabilidad. La
> transformación exponencial
> mapea `[0, ∞) → [0, 1)`, conserva el orden y —lo que importa— **conserva el
> efecto multiplicativo de los mitigadores en la zona baja**, que es donde una
> sala bien organizada opera. En `riesgo = 0,1` la reducción es casi
> proporcional; en `riesgo = 8,6` ya no salva a nadie, que es exactamente lo que
> debe comunicar.

**Base por tipo de unidad:**

| Unidad | Base | Comentario |
|---|---|---|
| ESMAD | 0,08 | entrenado y equipado para esto |
| Policía regular | 0,22 | no es su función |
| Militar | 0,45 | tropa de combate en control de multitudes |

**Mitigadores** — cada uno multiplica la probabilidad, y **todos son decisiones
que alguien en la sala tiene que tomar**:

| Mitigador | Factor | Quién lo habilita |
|---|---|---|
| reglas de empleo escritas y vigentes | ×0,70 | Presidente (A1) o Defensa (A1/A4) |
| identificación individual de agentes | ×0,85 | Defensoría (A1) |
| registro audiovisual obligatorio | ×0,80 | Defensa (A4), Policía (A3/A5) |
| dupla de verificación presente en el nodo | ×0,75 | Defensoría (A3) |
| operación concertada previamente con la Alcaldía | ×0,80 | Alcalde (A3) |
| unidades con fatiga < 0,3 | ×0,75 | Policía (A5) |

> **El estándar de derechos deja de ser un discurso y pasa a ser un instrumento
> de reducción de riesgo.** El Delegado de la Defensoría no está en la sala para
> moralizar: está para bajar una probabilidad. Con los seis mitigadores activos,
> los seis mitigadores juntos multiplican el riesgo por **0,21**: lo dividen
> por casi cinco, sea cual sea el punto de partida. Un ESMAD descansado en un
> nodo blando de día pasa de P≈0,08 a P≈0,02; militares fatigados de noche sin
> reglas escritas se quedan por encima de 0,80 aunque se apliquen todos, porque
> a esa altura la curva ya saturó. **El estándar protege a quien ya venía
> operando con cuidado y no rescata a quien no.**
>
> Convierte en una cuenta que la sala puede hacer una discusión que en un aula
> se vuelve retórica.

**Si el incidente ocurre**, el motor determina:

```
victimas          ~ f(tipo_unidad, masa_presente)
imagen_viral      ~ P(difusión | ausencia de registro propio, presencia de terceros)
atribuible        ¿hay agente identificable? ¿hay orden escrita? ¿con nombre?
```

`atribuible` importa porque decide **sobre quién cae el costo**: sin orden escrita
con responsable nominado, el costo se reparte sobre toda la mesa y golpea la
cohesión. Con ella, cae sobre quien firmó. Es exactamente la tensión del Ministro
de Defensa: *«le preocupa que el sector cargue en solitario el costo de decisiones
tomadas colectivamente en esta sala»*.

**Sobre el azar.** El incidente es estocástico pero con **semilla fija y
registrada**: una corrida se puede reproducir íntegra en el debriefing. La
probabilidad se muestra **antes** de decidir, como banda (baja / media / alta /
crítica), de modo que la sala gestione riesgo y no sorpresa. La consola del
moderador permite forzar o suprimir un resultado por razón pedagógica, y queda
registrado que se hizo.

### 4.3 Motor de apertura y reapertura

Tres vías de abrir un nodo, con economías radicalmente distintas. **Esta tabla es
el corazón pedagógico del caso.**

| Vía | Requiere | Velocidad | Caudal logrado | Reapertura | Reservas que consume |
|---|---|---|---|---|---|
| **Fuerza** | ESMAD u orden de asistencia militar | 1 turno | 0,7–1,0 | **1–2 turnos**, escalado con `intensidad` | legitimidad, credibilidad de la mesa, exposición |
| **Concertación** | contraparte con `control_voceria` alto | **2 turnos** | `0,9 × control_voceria` | mientras el acuerdo se cumpla | credibilidad si se incumple |
| **Desgaste** | `apoyo_local` < 0,3 sostenido | 4+ turnos | 0,5–0,8 | no reabre | ninguna |

> *«Un corredor pactado se sostiene y uno abierto por la fuerza vuelve a cerrarse
> esa misma noche.»* La cita es del Ministro de Transporte en su ficha. El motor
> debe hacerla cierta, no citarla.

**La trampa de la concertación.** El caudal logrado es
proporcional a `control_voceria`. Negociar con un vocero que controla el 40 % del
nodo produce una apertura del 36 % que se anuncia como éxito y se desmiente sola
en veinticuatro horas. La pregunta estratégica del Ministro del Interior —*con
quién se negocia cuando quien tiene vocería no controla el bloqueo*— tiene aquí
una respuesta numérica que el participante puede descubrir y pagar.

### 4.4 Motor de información — la verdad, las estimaciones y la versión

Tres capas distintas, y el ejercicio vive en la distancia entre ellas.

```
CAPA 1 · verdad         solo el motor la conoce; nunca se muestra en el ejercicio
CAPA 2 · estimaciones   una por fuente, con sesgo y cobertura propios
CAPA 3 · versión        lo que cada actor afirma públicamente
```

**Las cuatro fuentes de estimación:**

| Fuente | Dueño | Sesgo | Cobertura | Latencia |
|---|---|---|---|---|
| Parte operacional | Director de Policía | subestima víctimas civiles | alta (todos los nodos) | 1 turno |
| Inteligencia estratégica | Ministro de Defensa | **sobreestima `estructura_organizada`** | media | 1–2 turnos |
| Parte municipal verificado | Alcalde de Cali | **subestima `estructura_organizada`** | solo su jurisdicción | inmediata |
| Duplas de verificación | Defensoría | sesgo mínimo | **muy baja: 2–3 nodos por turno** | 1 turno |

El sesgo de la Defensoría es el menor y su cobertura la más pequeña. Eso la
convierte en un recurso que hay que **asignar**, no consultar: verificar aquí es
no verificar allá.

**El error doble.** Actuar sobre una estimación equivocada se castiga en las dos
direcciones, y de forma distinta:

- **Tratar como organizado un nodo mayoritariamente de protesta legítima** →
  operación de fuerza sobre población civil → costo máximo de legitimidad y
  exposición internacional.
- **Tratar como protesta legítima un nodo con estructura organizada** → se
  negocia con quien no controla nada → el acuerdo se incumple visiblemente →
  costo de credibilidad de la mesa y argumento a los gremios para exigir
  escalamiento.

No hay opción segura. Hay una decisión sobre **cuánta evidencia se exige antes de
tratar un punto de una u otra forma**, que es la casilla Seguridad × Información
de la matriz de la arquitectura.

**Las alertas falsas.** El motor genera, con probabilidad creciente en
`intensidad_movilizacion`, afirmaciones falsas de extrema gravedad que circulan en
la esfera pública. Si el Estado reacciona a una alerta falsa:

- consume capacidad de fuerza desplazándola a una situación inexistente,
- y pierde legitimidad cuando se desmiente.

Si una dupla de la Defensoría la verifica antes, se neutraliza y la Defensoría
**gana** credibilidad ante ambas partes. Esto da contenido mecánico a su recurso
R2, que en la ficha aparece como un hecho biográfico y aquí se vuelve un activo
que se usa y se agota.

**La cifra oficial.** El motor rastrea qué cifra afirmó públicamente cada actor y
en qué turno. Cuando la realidad se revela —por verificación, por prensa
internacional o por el cierre del ejercicio— cada afirmación se contrasta. La
distancia entre lo afirmado y lo verificado se cobra en legitimidad, **con
descuento si el actor clasificó explícitamente su dato** como confirmado, estimado
o en verificación. Es lo que hace racional la acción A3 del Director de la
Policía, que en el papel parece un gesto de transparencia sin recompensa.

### 4.5 Motor de abastecimiento

```
consumo_region(t)  = consumo_base × (1 + panico) × (1 − racionamiento)
ingreso_region(t)  = Σ caudal(corredor) × capacidad(corredor) × prioridad_asignada
dias_autonomia(t+1) = (inventario + ingreso − consumo) / consumo_diario
```

#### El oxígeno medicinal: qué es y por qué existe esta variable

Merece explicación aparte porque es la única variable del motor que **convierte
logística en muertes**, y porque no es una variable independiente sino el
extremo de una cadena.

**Qué mide.** `dias_autonomia_oxigeno` es, por región, cuántos días puede sostener
la red hospitalaria el consumo de oxígeno medicinal con lo que tiene almacenado
más lo que logra reponer. No es un inventario: es un **plazo**. Y por debajo de
cero no produce escasez sino un contador que ninguna deliberación discute:

```
muertes_evitables += pacientes_en_soporte × horas_sin_suministro × tasa
```

**Por qué no es independiente.** Es el último eslabón de una cadena que empieza en
una decisión de la sala:

```
corredor abierto → entra combustible → hay diésel para carrotanques
                                     → y para plantas de emergencia del hospital
                                     → las plantas sostienen la producción
                                       y la cadena de frío
                                     → hay oxígeno en la UCI
                                     → no se muere quien no tenía que morirse
```

Cortar el corredor en cualquier punto rompe la cadena entera. Por eso el oxígeno
está en el motor de abastecimiento y no en un módulo sanitario: **no modela salud,
modela el alcance de una decisión logística**.

**Qué me llevó a crearla.** Cuatro razones, en orden de peso:

1. **Sin ella, cuatro roles heredaron funciones sin objeto.** El Anexo A del
   Manual reparte al Ministro de Salud eliminado entre cuatro receptores: Minas
   (prioridad de oxígeno y plantas de emergencia), Transporte (clase de corredor
   humanitario), Policía (escolta de misión médica) y Defensoría (exigencia
   normativa de corredores humanitarios permanentes). Si el oxígeno no está en el
   motor, **esos cuatro traspasos son decorativos**: cuatro roles tienen una
   competencia escrita en su ficha que no puede actuar sobre nada. La variable
   existe para que la eliminación del Ministro de Salud sea una reasignación real
   y no un recorte disimulado.
2. **Es históricamente cierto y no es presión inventada.** Mayo de 2021 fue el
   peor mes de la pandemia en Colombia. Las UCI del Valle estaban en capacidad o
   por encima, y el suministro de oxígeno medicinal dependía materialmente de las
   vías que estaban cerradas. La tensión entre el bloqueo y la red hospitalaria
   no hay que fabricarla: estaba ahí.
3. **Es el único reloj cuyo vencimiento es irreversible y con nombre.** El
   desabastecimiento de alimentos encarece y duele; el de combustible paraliza;
   ambos se compensan después. El de oxígeno **mata a alguien esta noche en un
   hospital concreto**, y ninguna decisión posterior lo deshace. Un ejercicio
   sobre uso de la fuerza necesita al menos una consecuencia que no admita
   discusión retórica en el debriefing.
4. **No pertenece a ningún frente y los cruza todos.** Minas prioriza el
   suministro, Transporte le asigna clase de corredor, la Policía escolta,
   la Defensoría lo exige como derecho, Defensa decide si vale una operación,
   el Alcalde reclama por su ciudad. **Ninguno lo resuelve solo.** Es la prueba
   más limpia de la segunda pregunta del caso —con qué arquitectura se ejecuta—
   porque es imposible atenderlo sin coordinar cuatro carteras.

**Y le da filo a una acción que en el papel parece retórica.** La A4 de la
Defensoría —requerir corredores humanitarios permanentes exigibles al Estado *y*
a quienes sostienen los cierres— es, sin oxígeno modelado, una declaración de
principios. Con oxígeno modelado, negar un corredor humanitario tiene contador de
víctimas, y la ficha lo dice sin ambages: obliga a elegir entre abrirlo por la
fuerza, *que es el peor escenario posible*, o aceptar públicamente el
incumplimiento.

> **Una advertencia de calibración.** Es la variable más fácil de convertir en
> chantaje moral. Si el motor la hace explotar en el turno 2 pase lo que pase, la
> sala aprende que el diseño la castigaba, no que decidió mal. Debe existir
> **siempre al menos una vía viable** de atenderla —corredor humanitario
> concertado, escolta, o reasignación de combustible— y esa vía debe costar algo
> que a alguien le duela. Si no hay salida, no es un dilema: es un guion.

#### Tres mecánicas más que hay que respetar

1. **La asignación es de suma cero.** Cada galón que Minas asigna a misión médica
   se lo quita al transporte de alimentos. La acción A2 del Ministro de Minas
   obliga a ordenar cuatro usos: misión médica, fuerza pública, transporte de
   alimentos, consumo general. **No hay orden correcto**; hay un orden que se
   defiende ante siete personas que pierden algo.
2. **El pánico es endógeno.** Si el calendario de agotamiento se difunde —acción
   A4 de Minas, que la mesa suele pedir— `panico` sube, el consumo se acelera y
   el agotamiento llega antes. Entregar el reloj cambia el reloj. Y además, en
   palabras de su propia ficha, *entrega a quienes sostienen los cierres la medida
   exacta de su palanca*.
3. **El combustible realimenta la fuerza.** Por debajo de un umbral de autonomía,
   la capacidad de escolta y de desplazamiento de unidades se degrada. La crisis
   logística se convierte en crisis de contención.

### 4.6 Motor de esfera pública

Consolida lo que producen los agentes de IA (§9) y calcula su efecto agregado:

```
saliencia_nacional      [0,1]   cuánto ocupa la crisis el espacio público
encuadre_dominante      enum    {represion, desorden, negociacion, abandono}
presion_internacional   [0,100]
posicion_gremios        enum    {fuera, evaluando, sumados}
```

`encuadre_dominante` es la variable que traduce hechos en política. Se calcula de
los eventos del turno: víctimas y militares empujan hacia `represion`; nodos
nuevos y desabastecimiento hacia `desorden`; sesiones con acuerdo hacia
`negociacion`; aplazamientos de corredores hacia `abandono`. **El mismo hecho
cuesta distinto según el encuadre vigente**, y el encuadre se puede disputar con
vocería —que es lo que hace de la casilla Vocería algo más que un adorno.

---

## 5. El arranque y el ciclo

### 5.1 Aquí no hay minuto cero

En Macondo el instante inicial era el mundo normal —no había llovido, los heridos
eran cero— y el Alcalde activando el PMU **creaba** la gestión de la crisis. Aquí
el paro lleva quince días cuando los ocho entran a la sala: el PMU ya está
convocado, la mesa ya se instaló y ya se rompió una vez, y la fuerza ya está
desplegada y cansada.

> **No existe una «acción que da inicio». Lo que da inicio es un estado heredado
> más una exigencia con plazo.** El motor arranca a mitad de camino,
> deteriorándose solo, y la primera decisión de la sala no es *empezar* sino
> *elegir qué atender primero*.

Hay que modelar entonces tres cosas: **qué se hereda**, **qué obliga a sesionar
hoy** y **qué tipo de acción inicia de verdad la gestión** —que no es la que la
mayoría de las salas escoge.

### 5.2 El estado heredado (t = 0)

El motor se inicializa con un archivo de estado inicial, no con ceros. Estos son
valores de partida propuestos, para calibrar.

| Variable | Valor en t=0 | Por qué así |
|---|---|---|
| **Nodos modelados** | 24 activos sobre 5 corredores | de ellos, 6 con `dias_sostenido > 10`: están consolidados |
| **`nodos_secundarios_activos`** | ~1.000 agregados por región | la presión de fondo que no se gestiona uno a uno |
| **ESMAD** | 34 de 40 escuadrones desplegados | **`fatiga` media 0,55** |
| **Policía** | déficit de 20.000 para control urbano | ya contabilizado |
| **Militar** | déficit de 30.000 · sin habilitación para control de multitudes | la asistencia militar **no** está firmada |
| **Legitimidad interna** | 52 | ya deteriorada por las dos primeras semanas |
| **Credibilidad de la mesa** | 45 | la mesa ya se instaló y ya se suspendió una vez |
| **Exposición internacional** | 45 | ya hubo pronunciamientos |
| **Cohesión de la mesa** | 68 | — |
| **`intensidad_movilizacion`** | 61 nacional · 84 en Valle | |
| **Autonomía combustible** | Buenaventura 2,1 d · Cali 3,4 d | |
| **Autonomía oxígeno** | Cauca **1,8 d** | el más corto: presión inmediata |
| **`posicion_gremios`** | `fuera`, con ultimátum vivo | ver nota abajo |
| **Mitigadores activos** | **ninguno** | no hay reglas escritas, ni protocolo, ni registro |

**La asimetría deliberada de las reservas.** Tres se heredan dañadas y una no:

- Legitimidad, credibilidad de la mesa y exposición **vienen así**. La sala no las
  rompió y no puede culpar a nadie presente. Hereda un pasivo.
- **Cohesión empieza alta y es enteramente suya.** Todo lo que le pase entre el
  turno 1 y el 10 lo hicieron los ocho. En el debriefing es la única serie de la
  que no pueden desentenderse.

**Nota sobre los gremios.** El umbral de §3.4 los pone a evaluar por debajo de
40 de legitimidad, y en t=0 la legitimidad está en 52. Por eso arrancan **fuera**
y no evaluando: lo que los activa en el turno 1 no es el umbral sino el ultimátum
de 48 horas del paquete detonante (H3), que es un disparador independiente. Los
dos caminos hacia `evaluando` —deterioro lento por umbral y exigencia puntual con
plazo— deben coexistir en el motor, porque son dos cosas distintas: una es que el
país deje de respaldar al Gobierno y otra es que un gremio concreto pida algo
concreto.

Y el dato que más rinde: **ningún mitigador está activo en t=0**. La primera
operación de fuerza que la sala ordene, si la ordena antes de constituir nada,
corre con probabilidad de incidente sin descuento y con `atribuible = false`.
Esto no se les dice; se descubre.

### 5.3 Turno 0 — instalación y declaración de línea

No es un turno de juego: no se dan órdenes y el motor no avanza. Dura unos ocho
minutos y produce el insumo central del debriefing.

```
1 · Entrega de fichas y sobres sellados con la agenda reservada
2 · El moderador lee el parte heredado (§5.2), en voz alta, para toda la sala
3 · DECLARACIÓN DE LÍNEA — 60 segundos por rol, en ronda, sin debate:
       ¿fuerza, negociación, o secuencia entre ambas?
       ¿y qué condición concreta lo movería de posición?
4 · El moderador lo registra: posicion_declarada_t0 por rol
```

**Por qué vale la pena gastar ocho minutos en esto.** La métrica más reveladora
del ejercicio es la distancia entre **la línea que la sala declaró** y **la línea
que de hecho ejecutó**. Casi todas las salas declaran una secuencia —«primero la
mesa, fuerza solo si falla»— y casi ninguna la cumple, porque el hecho detonante
del turno 1 empuja hacia la operación y nadie vuelve a mirar lo que dijo al
entrar. Sin el turno 0 esa comparación no existe y el hallazgo se pierde.

La segunda parte de la pregunta —*qué lo movería de posición*— importa tanto como
la primera: obliga a cada rol a nombrar por adelantado su propia condición de
cambio, y en el debriefing se contrasta con si esa condición efectivamente se
cumplió y si el rol se movió o no.

### 5.4 El hecho detonante: qué obliga a sesionar hoy

El turno 1 no abre con un tablero en calma. Abre con un **paquete detonante**:
varios hechos de las últimas doce horas que llegan juntos y que **no caben en la
capacidad disponible**. La sala descubre la escasez en su primer minuto, no en el
cuarto turno.

Composición propuesta del paquete —cuatro hechos, cuatro frentes, un solo ESMAD:

| # | Hecho | Frente que interpela | Qué exige |
|---|---|---|---|
| **H1** | Incidente nocturno en un nodo contiguo a una instalación de combustible. Un herido grave de la fuerza pública. | Seguridad · Logística | ¿se opera el nodo, se protege la instalación, o ninguna? |
| **H2** | **Dos** denuncias de extrema gravedad sobre hechos en puntos de resistencia distintos. Ambas sin verificar. Una es falsa y la otra cierta; nada las distingue. | Información · Estrategia | ¿cuál se verifica, con la única dupla disponible? |
| **H3** | Ultimátum de los gremios camioneros: 48 horas o evalúan sumarse al paro. | Logística · Estrategia | ¿se negocia, se ignora, con qué se paga? |
| **H4** | Cauca cruza por debajo de 2 días de autonomía de oxígeno medicinal. | Logística · Seguridad | ¿corredor humanitario? ¿con qué escolta? |

**Tres reglas de construcción del paquete detonante**, que valen para cualquier
turno posterior pero sobre todo para este:

1. **La suma excede la capacidad.** Atender los cuatro es imposible: hay 6
   escuadrones de ESMAD sin desplegar y cada hecho pide al menos dos. Priorizar no
   es una virtud recomendada, es la única salida.
2. **Hay dos denuncias graves sin verificar: una es falsa y la otra es cierta.**
   Y no están marcadas.

   > **Por qué dos y no una.** Un ejercicio sobre el paro de 2021 en el que la
   > única denuncia grave resulta inventada le enseña a ocho futuros funcionarios
   > que las denuncias graves suelen ser inventadas. Hubo denuncias falsas —la
   > Defensoría desmintió varias— y hubo hechos ciertos y documentados. Un diseño
   > que solo modela las primeras no es neutral: toma partido, y lo hace sobre
   > hechos que todavía están en discusión judicial.
   >
   > **La regla correcta: nunca una sola denuncia sin verificar.** Siempre al
   > menos dos, con veracidad distinta y sin ninguna señal que las distinga. Así
   > la lección no es «desconfíe» sino **«usted no puede saberlo sin verificar, y
   > verificar cuesta una dupla que no tiene»**, que es el problema real.

   Las cuatro conductas posibles y su precio:

   | Conducta ante las dos denuncias | Resultado |
   |---|---|
   | Reacciona con fuerza a ambas | gasta capacidad en la falsa, agrava la cierta |
   | Desestima ambas | la cierta estalla en la esfera pública sin respuesta preparada |
   | Verifica una (solo hay duplas para una) | acierta a medias; **es el resultado realista** |
   | Verifica una y **declara públicamente que la otra está en verificación** | el mejor disponible: no afirma lo que no sabe |

   La cuarta fila es la que la acción A3 del Director de la Policía —clasificar en
   confirmado, estimado y en verificación— hace posible, y que sin ella no existe.
3. **Cada hecho toca al menos dos frentes.** Ninguno se resuelve dentro de una
   sola cartera. Si un rol puede despachar un hecho solo, el hecho está mal
   diseñado.

> Los turnos siguientes se arman con la misma receta, salvo que a partir del turno
> 2 el paquete ya no es de guion: **lo produce el motor** a partir de las
> consecuencias del turno anterior y de la esfera pública. El único paquete
> escrito a mano es el del turno 1.

### 5.5 Lo que de verdad inicia la gestión: acciones constitutivas

Aquí está la respuesta a *cuáles son las acciones primeras*. Las cuarenta
acciones de la Matriz Operativa se parten en dos clases que el motor trata de
forma distinta:

| | **Constitutivas** | **Operativas** |
|---|---|---|
| Qué cambian | cómo funciona la mesa | el territorio |
| Efecto | activan una bandera persistente | mueven caudal, fuerza, reservas |
| Visibilidad | nula en el tablero | inmediata |
| Costo directo | casi ninguno | alto |
| Valor | **modifican todas las acciones posteriores** | se agotan en su turno |

**Las seis constitutivas, y la bandera que activa cada una:**

| Acción | Rol | Bandera que activa | Efecto sobre el resto del ejercicio |
|---|---|---|---|
| **A2** | Presidente | `registro_escrito`, `nodo_unico` | `atribuible = true` en cada incidente: el costo cae sobre quien firmó, no sobre los ocho |
| **A3** | Presidente | `lineas_rojas_fijadas` | acota el margen de Interior; sin ellas, cada acuerdo se renegocia en la sala |
| **A4** | Interior | `protocolo_voceria`, `plazo_suspensivo` | ninguna operación sorprende a la mesa; cuesta un turno de demora |
| **A2** | Defensoría | `protocolo_verificacion` | una sola cifra oficial clasificada; desactiva la guerra de números |
| **A1** | Defensoría | `reglas_escritas`, `identificacion`, `registro_av` | **tres mitigadores de golpe: P(incidente) ×0,48** |
| **A1/A4** | Transporte | `criterio_priorizacion` | convierte la disputa política de asignación en una secuencia defendible |

**Ninguna está bloqueada y ninguna es obligatoria.** El diseño no fuerza a la sala
a constituirse: le permite saltárselo y le cobra la diferencia. Es la decisión de
diseño más importante de esta sección — un bloqueo duro se siente como un riel;
un precio se siente como una consecuencia.

**Lo que cuesta operar sin haberlas tomado:**

| Se opera sin… | Precio |
|---|---|
| `reglas_escritas` | P(incidente) sin descuento · `exposicion += 22` en vez de `+= 8` al firmar |
| `registro_escrito` | `atribuible = false`: el costo del incidente se reparte y `cohesion −= 8` |
| `protocolo_verificacion` | cada rol afirma su propia cifra; el desmentido cuesta `legitimidad −= 4` cada vez |
| `protocolo_voceria` | vocerías contradictorias: los agentes de entorno las citan, `cohesion −= 5` por turno |
| `criterio_priorizacion` | la asignación se pelea políticamente cada turno: `cohesion −= 3` por turno |
| `lineas_rojas_fijadas` | cualquier acuerdo que Interior traiga se discute de nuevo en la sala |

**El valor de una constitutiva es proporcional a los turnos que le quedan por
delante.** No hace falta ninguna penalización artificial por adoptarla tarde: un
protocolo de verificación en el turno 8 solo cubre dos turnos y no borra las
cuatro cifras ya desmentidas. El daño acumulado no se revierte. Eso basta —y es
verdad— para que la adopción temprana valga más.

Un solo matiz que sí conviene modelar aparte: **adoptar una constitutiva justo
después de un incidente se lee como reacción, no como diseño.** El efecto hacia
adelante es idéntico, pero el rédito en legitimidad es la mitad. La prensa
distingue perfectamente entre prevenir y responder.

> **La trampa:** el paquete detonante grita por acciones operativas, y las
> constitutivas no aparecen en el tablero, no abren ningún corredor y parecen
> burocracia mientras el país arde. **La mayoría de las salas se las salta y paga
> entre el turno 4 y el 6**, cuando hay tres cifras en disputa, dos operaciones
> que Interior no conocía y ningún renglón del pliego con un nombre escrito.
>
> Que la primera decisión no era sobre el territorio sino sobre la propia mesa es
> la segunda pregunta del caso. El motor no debe enseñarla: debe hacer que cueste
> no haberla resuelto.

### 5.6 El costo de no decidir

Un turno sin órdenes es una opción legítima y tiene consecuencias propias:

```
intensidad_movilizacion  += 1,5     la indefinición acumula
dias_autonomia           −= consumo del turno, sin ingreso
dureza de todos los nodos += 0,03   se consolidan
encuadre_dominante       → empuje hacia 'abandono'
legitimidad_interna      −= 3
cohesion_mesa             sin cambio   (no discutieron: no se rompieron)
```

No es catastrófico en un turno y es insostenible en tres. **El castigo real no es
la penalización: es el reloj**, que corre igual. Es la traducción mecánica de la
frase de la ficha del Presidente sobre el costo que ya se está pagando por la
indefinición.

### 5.7 El orden de la palabra en el turno 1

Detalle de moderación con efecto de diseño. **Solo en el turno 1**, la palabra va
en orden fijo:

```
1 · Seguridad informa estado      (Policía, luego Defensa)
2 · Logística informa estado      (Transporte, luego Minas)
3 · Defensoría informa lo verificado y lo que NO ha podido verificar
4 · Estrategia responde           (Cali, Interior, Presidente al final)
5 · Deliberación abierta
```

**Por qué el Presidente habla último.** Si abre, encuadra el problema antes de
que los hechos estén sobre la mesa y los siete restantes discuten su marco en vez
del caso. Que hable al final lo obliga a arbitrar sobre información que no
seleccionó, que es precisamente su trabajo.

**Por qué la Defensoría informa también lo que no pudo verificar.** Instala desde
el primer minuto la distinción entre confirmado, estimado y en verificación —y
hace visible que su cobertura es de dos o tres nodos por turno, que es el hecho
que la sala necesita entender antes de pedirle que verifique todo.

A partir del turno 2 no hay orden fijo. Quién toma la palabra primero pasa a ser
un dato del ejercicio.

### 5.8 El presupuesto de 120 minutos

**Restricción dura: el ejercicio completo dura dos horas de mundo real**, menos
la instalación y el debriefing. Diez turnos deliberativos no caben, y diez turnos
de seis minutos no son un Puesto de Mando sino un concurso de rapidez. La salida
no es acortar los turnos sino **reconocer que no todos necesitan deliberación**.

| Bloque | Minutos | Qué pasa |
|---|---:|---|
| Instalación y turno 0 | 12 | fichas, sobres, parte heredado, declaración de línea |
| **5 turnos de decisión (día)** | **65** | 13 min cada uno |
| **4 interludios nocturnos** | **12** | 3 min cada uno · **sin deliberación** |
| Debriefing | 20 | §8.3 |
| Holgura | 11 | los turnos se pasan; siempre |
| **Total** | **120** | |

**Los interludios nocturnos son lo que hace que esto quepa.** La noche
no se delibera: se sufre. El moderador no pide órdenes; resuelve lo que se ordenó
de día, y la sala **mira** cómo un corredor abierto por la fuerza se cierra otra
vez, cómo entra un titular, cómo baja el reloj de autonomía. Tres minutos.

Esto no es solo una economía de tiempo: **es mejor diseño**. La frase del caso
—*un corredor abierto por la fuerza vuelve a cerrarse esa misma noche*— deja de
ser una regla en una tabla y pasa a ser algo que la sala ve ocurrir sin poder
intervenir. La pérdida de control se representa quitándoles el turno.

Y no elimina la decisión nocturna: **de día se puede ordenar operar de noche**,
que se resuelve en el interludio con `factor_nocturno = 1,6`. El intercambio
día/noche se conserva íntegro; lo que se elimina es el costo en minutos de sala.

**Cobertura temporal:** D–N–D–N–D–N–D–N–D = 5 jornadas, del 11 al 15 de mayo de
2021, con una jornada nacional de movilización programada en el turno 3.

> **Consecuencia de calibración que hay que aceptar:** con 5 turnos de decisión,
> toda mecánica que tarde 3 turnos en rendir es prácticamente inviable. Por eso
> la concertación baja a **2 turnos** (§4.3) y las constitutivas del turno 1
> valen mucho más que en un diseño de 10 turnos. El ejercicio se vuelve más
> denso y menos indulgente, que para dos horas es lo correcto.

### 5.9 Turnos de día y turnos de noche no son iguales

| | **Turno de día (13 min)** | **Interludio de noche (3 min)** |
|---|---|---|
| Deliberación | sí, 6 min | **no** |
| Órdenes nuevas | sí | **no** |
| Mesa de diálogo | disponible | no |
| Vocería pública | alto alcance | bajo |
| `masa_presente` en nodos | alta | media, pero más dura |
| `factor_nocturno` en incidentes | ×1,0 | **×1,6** |
| Reapertura de nodos abiertos por fuerza | — | **aquí ocurre** |
| Operaciones | se ordenan | **se resuelven** las ordenadas para la noche |

### 5.10 Estructura de los dos tipos de turno

**Turno de decisión — 13 minutos**

```
1 · APERTURA        1,5 min   el moderador lee el parte: qué cambió, qué se rompió
2 · DELIBERACIÓN    6,0 min   el tablero NO se actualiza. La sala discute.
3 · ÓRDENES         2,5 min   se transcribe; se lee de vuelta el plan CON SU BANDA
                              DE RIESGO; la sala confirma o corrige
4 · RESOLUCIÓN      1,0 min   el motor ejecuta
5 · CONSECUENCIAS   1,0 min   prensa, redes, gremios, internacional
6 · REGISTRO        1,0 min   la decisión al pliego, con responsable nominado
```

**Interludio nocturno — 3 minutos**

```
1 · RESOLUCIÓN      1,5 min   se ejecuta lo ordenado para la noche
2 · CONSECUENCIAS   1,5 min   reaperturas, incidentes, titulares, el reloj
                              — la sala mira, no interviene
```

**Sobre los 6 minutos de deliberación.** Es poco y es deliberado. Ocho personas
con seis minutos no alcanzan a discutirlo todo: **tienen que elegir qué discutir**,
que es la competencia que el ejercicio quiere entrenar. El paquete detonante
(§5.4) trae cuatro hechos precisamente para que no quepan.

**Dos reglas de moderación sin las cuales el presupuesto no se cumple:**

1. **El reloj de deliberación es visible y suena.** No lo administra el criterio
   del moderador, que siempre concede «un minuto más».
2. **Si no hay orden al terminar los 6 minutos, no hay orden.** El turno se
   resuelve como turno sin decisión (§5.6). Esto ocurre una vez por ejercicio,
   nunca dos: la primera vez enseña más que cualquier instrucción previa.

**Que el tablero se congele durante la deliberación es una decisión de diseño, no
una limitación técnica** (§10). Si la pantalla se mueve mientras la gente habla,
la gente mira la pantalla.

### 5.11 El problema del último turno

**En el turno 5 la fuerza sale gratis.** Un nodo abierto por la fuerza reabre en
1–2 turnos y no quedan turnos; la imagen viral sube la movilización y no queda
quién la sufra. Una sala que lo advierta —y alguna lo advertirá— puede desatar en
el último turno todo lo que evitó en los cuatro anteriores y salir con mejores
números.

**El antídoto: el ejercicio no termina en el turno 5.** Terminado el último turno,
antes del debriefing, el motor corre **tres turnos más sin órdenes** y proyecta el
estado a 72 horas:

```
PROYECCIÓN T+72h  ·  sin nadie al mando
  nodos reabiertos:            +N
  intensidad_movilizacion:     61 → X
  reservas al cierre proyectado
  días de autonomía restantes por región
  muertes evitables acumuladas
```

Se proyecta en pantalla y se lee en voz alta. **No es un marcador: es el país que
la sala entrega.** Cierra el incentivo del último turno y, sobre todo, instala la
pregunta con la que conviene abrir el debriefing: *¿esto se sostiene sin ustedes?*

### 5.11 Tres colas, igual que en Macondo

La cola condicional es aquí todavía más necesaria que en la inundación:

- **Inmediata** — se aplica en la resolución de este turno.
- **Por tiempo** — «la sesión de la mesa es mañana a las 10».
- **Por condición** — *«en cuanto la Defensoría verifique ese nodo, opérenlo»*,
  *«si los gremios se suman, firmo la asistencia militar»*. Nadie sabe cuándo se
  cumplirá.

Con las mismas tres salvaguardas: caducidad con constancia en el registro,
ejecución inmediata si la condición ya se cumple, y una condición que lanza
excepción descarta esa orden sin tumbar el turno.

---

## 6. Acciones, efectos y acoplamientos

Las cuarenta acciones (8 roles × 5) ya están definidas en la Matriz Operativa. Lo
que falta —y es lo que este documento aporta— es **su traducción a operaciones
sobre las variables**.

### 6.1 Forma de una acción

Igual que en Macondo: `validar()` que no muta y devuelve motivo, `ejecutar()` que
devuelve resultado estructurado, y una tabla de efectos que el motor aplica. Con
una adición propia de este caso:

```
requisitos_de_otros_roles : lista
```

**Trece de las cuarenta acciones no se pueden ejecutar solas.** El Ministro de
Transporte no puede desbloquear: necesita que Defensa opere o que Interior
concerte. El Alcalde no puede desplegar fuerza. Minas no puede proteger sus
instalaciones. Cuando falta el requisito, `validar()` debe devolver **quién puede
habilitarlo**, no un rechazo:

> *«La caravana requiere escolta. Corresponde al Director General de la Policía
> Nacional (acción A2). Sin escolta la acción queda en espera condicional.»*

Eso empuja la conversación de vuelta a la sala, que es donde el ejercicio quiere
que ocurra. Es la versión de este caso del principio de Macondo sobre rechazar en
código determinista con un motivo accionable.

### 6.2 Efectos: cuatro ejemplos completos

**Presidente · A1 — Firmar la asistencia militar**

```
SI delimitacion Y plazo Y reglas_escritas Y criterio_terminacion:
    militar.control_multitudes      ← habilitado en territorio delimitado
    policia.liberados_de_custodia   += 2 por instalación bajo custodia militar
    esmad.concentrable              ← true
    exposicion_internacional        += 8
    legitimidad_interna             −= 5
    reglas_de_empleo_vigentes       ← true   (mitigador ×0,70 activo)
SI NO:
    ídem, pero:
    exposicion_internacional        += 22
    legitimidad_interna             −= 15
    intensidad_movilizacion         += 8
    encuadre_dominante              → represion (fuerte empuje)
    reglas_de_empleo_vigentes       ← false
SI SE NIEGA:
    capacidad_fuerza                sin cambio (insuficiente para >1.000 puntos)
    credibilidad_mesa               += 6
    cohesion_mesa                   −= 5   (Defensa queda expuesto sin instrumento)
```

**Defensoría · A1 — Condicionar su permanencia a estándares escritos**

```
SI la mesa acepta:
    mitigadores {reglas, identificacion, registro, ruta_victimas} ← activos
    P(incidente) global                    ×0,45 aproximadamente
    exposicion_internacional               −= 10
    defensoria.presente                    ← true
SI la mesa rechaza:
    defensoria.presente                    ← false
    cobertura_verificacion                 ← 0   (se pierde la mejor fuente)
    exposicion_internacional               += 15
    alertas_falsas_no_desmentidas          ← se acumulan sin filtro
SI condiciona sin priorizar (>3 exigencias simultáneas):
    la mesa lo aísla; capital_politico −= 25; acceso restringido
```

La tercera rama es importante: la ficha advierte que *si exige todo sin
priorizar, la mesa lo aísla y su palanca desaparece*. El motor debe hacerlo
posible, incluyendo el resultado en que el rol correcto pierde por exceso.

**Minas · A1 — Declarar infraestructura crítica**

```
POR CADA instalación en la lista:
    fuerza_inmovilizada     += 2 policías o 3 militares por turno
    P(incidente_irreversible en esa instalación) ← ~0
Y COMO CONSECUENCIA:
    esmad_disponible_desbloqueo −= equivalente
    corredores_aplazados        += según la priorización de Transporte
    → y el aplazamiento tiene nombre de ciudad, y esa ciudad tiene un alcalde
```

**Transporte · A1 — Priorización de corredores**

```
criterio ← ordenar por (poblacion_aguas_abajo, dias_autonomia, costo_diario)
SI la mesa lo adopta como criterio único:
    disputa_politica_asignacion  −= mucho
    defensa.criterio_defendible  ← true
    cali.agravio_si_desplazado   ← registrado con atribución
SI NO se adopta:
    cada asignación de fuerza se decide políticamente turno a turno
    cohesion_mesa −= 3 por turno
```

### 6.3 La tabla de acoplamientos

Todo acoplamiento **habilita** o **restringe**. La Matriz Operativa ya identificó
treinta y cuatro; estos son los que el motor debe implementar primero porque sin
ellos el caso no funciona.

| Origen | Acción | Destino | Tipo | Mecanismo en el motor |
|---|---|---|---|---|
| Presidente | A1 firma | Defensa | habilita | `militar.control_multitudes ← true`; libera policías de custodia |
| Presidente | A1 firma | Interior | restringe | `credibilidad_mesa −= 12` en el mismo turno |
| Presidente | A3 líneas rojas | Interior | restringe | acota el espacio negociable; sin margen, todo acuerdo es capitulación |
| Interior | A4 plazo suspensivo | Defensa | restringe | las operaciones se difieren 1 turno; nodos se endurecen entretanto |
| Interior | A2 mesas locales | Transporte | habilita | apertura por concertación sin consumir ESMAD |
| Cali | A1 mesa local | Policía | habilita | libera ESMAD del corredor pactado |
| Cali | A3 condicionamiento | Defensa | restringe | operar sin concertar: `legitimidad −= 8` adicional |
| Cali | A4 esquema humanitario | *nodos de su jurisdicción* | habilita | baja `apoyo_local`: abre por desgaste sin consumir reservas |
| Defensa | A2 redespliegue | Policía | habilita | +N policías a ESMAD; abre `frentes_rurales_descubiertos` |
| Defensa | A4 operación nacional | Interior | restringe | cada víctima consume la legitimidad de la que depende la mesa |
| Policía | A1 concentración ESMAD | Cali y alcaldes de entorno | restringe | el repliegue consolida nodos secundarios: `+2 nodos/turno` |
| Policía | A2 escolta | Transporte y Minas | habilita | **condición material**: sin escolta no hay caravana ni carrotanque |
| Policía | A5 relevo | Defensa | restringe | menor cobertura → adelanta la solicitud de escalamiento |
| Defensoría | A1 condicionamiento | Presidente | restringe | eleva el requisito formal de la firma |
| Defensoría | A3 duplas | *todos* | habilita | desmiente alertas falsas antes de que consuman fuerza |
| Defensoría | A4 corredores humanitarios | Policía | restringe | obliga a garantizar paso donde no hay operación autorizada |
| Transporte | A1 priorización | Defensa | habilita | criterio técnico defendible frente a la presión política |
| Transporte | A1 priorización | Cali | restringe | todo orden aplaza corredores y produce agravio atribuible |
| Minas | A1 infraestructura crítica | Defensa | restringe | **inmoviliza la fuerza del desbloqueo** |
| Minas | A2 asignación combustible | Transporte | restringe | suma cero: cada uso se le quita a otro |
| Minas | A4 calendario | **todos** | restringe | fija la fecha límite; convierte el tiempo en variable dura |

---

## 7. Los dilemas que el motor vuelve inevitables

Un dilema que depende de que los participantes lo descubran no es un dilema del
diseño: es suerte. Estos seis deben ser **consecuencia aritmética** del motor, de
modo que aparezcan en toda corrida.

### D1 · La fuerza que abre resta credibilidad a la mesa que negocia el siguiente

Garantizado por el acoplamiento Presidente A1 → Interior y Defensa A4 → Interior.
El Ministro del Interior ve caer su reserva por decisiones que no tomó.

### D2 · Cada corredor priorizado es un corredor aplazado, y el aplazamiento tiene nombre de ciudad

Garantizado por la escasez de ESMAD (40 escuadrones, de los que solo 6 quedan sin
desplegar en t=0, sobre 24 nodos modelados) y por
la inmovilización que produce la custodia de infraestructura. El criterio técnico
de Transporte y la exigencia política del Alcalde **no pueden satisfacerse
simultáneamente**.

### D3 · La verdad es un recurso escaso y las duplas que la producen son tres por turno

Garantizado por la cobertura limitada de la Defensoría frente al sesgo sistemático
de las otras tres fuentes. Verificar aquí es no verificar allá, y el error tiene
dos direcciones, ambas caras.

### D4 · El estándar de derechos es la única palanca que baja el riesgo sin consumir capacidad

Garantizado por los mitigadores multiplicativos. Es el dilema **positivo** del
diseño: el rol sin voto y sin fuerza es el que más reduce la probabilidad del peor
resultado. Se descubre haciendo la cuenta, y por eso hay que mostrar la banda de
riesgo antes de decidir.

### D5 · Entregar el reloj cambia el reloj

Garantizado por el pánico endógeno. El calendario de agotamiento de Minas es a la
vez el instrumento que obliga a la mesa a decidir y el que acelera aquello que
mide.

### D6 · Concentrar hace responsable de cada error; delegar deja sin control sobre la coherencia

Garantizado por la variable `atribuible` y por la reserva de cohesión. Sin
decisión escrita con responsable nominado, el costo de cada incidente se reparte
sobre los ocho y erosiona la cohesión. Con ella, cae íntegro sobre quien firmó.

> **La forma general del caso:** las ocho posiciones son defendibles y ninguna es
> suficiente. Si en el debriefing una opción resulta haber sido obviamente
> correcta desde el turno 1, el motor está mal calibrado.

---

## 8. Métricas y debriefing

### 8.1 Lo que se instrumenta desde el primer turno

Un evento canónico por turno, en JSONL, con la misma disciplina de Macondo:
anotar el dato en el código no basta, hay que comprobar que **llega al archivo**.

```json
{"turno": 4, "franja": "noche", "t_sim": "2021-05-12T20:00",
 "ordenes": [{"rol": "...", "accion": "A4", "requisitos_faltantes": [...],
              "estado_final": "ejecutada|encolada|bloqueada", "habilitada_por": "..."}],
 "riesgo_mostrado": {"nodo_17": "alta", "p_calculada": 0.34, "semilla": 88213},
 "incidentes": [{"nodo": 17, "victimas": 1, "viral": true, "atribuible": false}],
 "reservas": {"legitimidad": 41, "credibilidad_mesa": 28, "exposicion": 63, "cohesion": 44},
 "aperturas": {"fuerza": 2, "concertacion": 0, "desgaste": 1, "reaperturas": 2},
 "reloj": {"dias_autonomia_min": 1.8, "region": "Buenaventura"},
 "cifras": {"afirmada_gobierno": 12, "verificada": 19, "clasificada": false}}
```

### 8.2 Las métricas que importan

| Métrica | Qué revela | Meta |
|---|---|---|
| **Aperturas netas** | aperturas − reaperturas | > 0 al cierre |
| **Ratio fuerza/concertación** | qué línea de respuesta se ejecutó *de hecho*, más allá de lo que se declaró | contrastar con la línea declarada en el turno 1 |
| **Supervivencia por vía de apertura** | valida D1 y la tabla de §4.3 | la concertada debe sobrevivir 3× |
| **Turno de la primera decisión escrita con responsable** | si la mesa se organizó o improvisó | ≤ turno 3 |
| **Mitigadores activos al primer uso de fuerza** | si el estándar llegó antes o después del hecho | ≥ 4 de 6 |
| **Distancia cifra afirmada / verificada** | la guerra de cifras, cuantificada | ↓ y clasificada |
| **Días de autonomía mínimos alcanzados** | qué tan cerca del hecho irreversible se pasó | > 1,0 |
| **Alertas falsas no desmentidas que movieron fuerza** | costo de no haber asignado duplas | 0 |
| **Reservas al cierre** | el estado en que se entrega el país | ninguna bajo umbral crítico |

### 8.3 El entregable del debriefing

**La cronología reconstruida**, turno a turno, con cuatro columnas: qué se
decidió, quién lo pidió, qué produjo el motor, y **qué habría producido la vía
alternativa** —esto último es posible porque la corrida está sembrada y se puede
reproducir con una decisión cambiada.

Y sobre esa cronología, tres lecturas:

1. **La línea declarada contra la línea ejecutada.** La sala casi siempre declara
   una secuencia —«primero negociación, fuerza solo si falla»— y casi nunca la
   ejecuta. La distancia es el hallazgo.
2. **El momento en que la mesa dejó de ser una mesa.** Localizable en la serie de
   `cohesion_mesa`: el turno de la primera operación no informada o la primera
   desautorización pública.
3. **Las agendas reservadas.** Se revelan al final. Qué persiguió cada uno sin
   declararlo, y si lo consiguió a costa de qué reserva colectiva.

---

## 9. Roles de IA: quién puebla el mundo

Producen contenido; **nunca mutan el estado**. Seis arquetipos, cada uno un grafo
de uno o dos nodos, con cadencia propia y bandera de no reentrada.

| Agente | Cadencia | Patrón | Presión que genera |
|---|---|---|---|
| **Comité Nacional del Paro** | cada turno | evaluar → responder | la contraparte: endurece, se fragmenta o acepta |
| **Prensa nacional** | cada turno | ¿hay noticia? → publicar | obliga a comunicar; fija el encuadre |
| **Prensa internacional** | cada 2 turnos | ídem, con umbral más alto | traduce hechos en exposición internacional |
| **Redes sociales** | cada turno | reunir contexto → publicar | **incluye el generador de alertas falsas** |
| **Gremios** | cada 2 turnos | evaluar → posicionarse | camioneros, comercio: la amenaza del paro logístico |
| **Alcaldes de entorno** | cada 2 turnos | reaccionar públicamente | Bogotá y Medellín, ya previstos como actores de entorno |

Dos precisiones sobre el Comité del Paro, que es el más delicado:

- **Es el único agente con estado propio persistente**: su disposición a sentarse,
  su fragmentación interna y el pliego que sostiene evolucionan turno a turno y
  dependen de lo que la mesa haya hecho.
- **No decide si un nodo se abre.** Eso lo calcula el motor a partir de
  `control_voceria` y del cumplimiento del acuerdo. El agente redacta la posición;
  la aritmética la hace el código. Si el modelo pudiera abrir corredores, el
  ejercicio dejaría de ser reproducible y sería imposible atribuir un resultado a
  las decisiones de los participantes.

---

## 10. La interfaz: una sala sin pantallas individuales

El hallazgo del ejercicio anterior —**una pantalla por participante produce ocho
personas mirando ocho pantallas y ninguna mirando a las otras siete**— es un
resultado de diseño, no un accidente. En un caso cuyo objeto es *la arquitectura
de decisión de un cuerpo colegiado*, retirar las pantallas individuales no es una
concesión: es lo que hace que el objeto exista.

### 10.1 Tres superficies, un solo teclado

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  TABLERO DE SITUACIÓN        │  │  ESFERA PÚBLICA              │
│  proyectado · toda la sala   │  │  proyectado · toda la sala   │
│                              │  │                              │
│  · mapa de nodos CON su      │  │  · titulares de prensa       │
│    procedencia y grado       │  │  · redes sociales            │
│  · las 4 reservas            │  │  · pronunciamientos int.     │
│  · reloj de autonomía        │  │  · LAS TRES CIFRAS, juntas   │
│  · asignación de fuerza      │  │                              │
│  · turno y franja            │  │                              │
└──────────────────────────────┘  └──────────────────────────────┘
                    ▲                          ▲
                    └────────────┬─────────────┘
                    ┌────────────┴─────────────┐
                    │  CONSOLA DEL MODERADOR   │
                    │  el único teclado        │
                    │  no proyectada           │
                    └──────────────────────────┘

        LA MESA: ocho personas, papel, y nada más.
```

**Por qué dos proyecciones y no una.** El tablero muestra **lo que el Estado
tiene por cierto**; la esfera pública muestra **lo que se dice**. La distancia
entre ambas es el caso. Verlas separadas y verlas divergir —la cifra oficial en
una pantalla y la cifra que circula en la otra— convierte la guerra de cifras en
algo que la sala ve ocurrir en lugar de algo que se le explica.

> **Regla dura sobre qué puede mostrar el tablero.** No puede mostrar los hechos
> que el motor conoce. Si la pantalla común muestra el caudal verdadero de cada
> nodo y su composición real, **el motor de información se anula entero** (§4.4):
> las cuatro fuentes con sesgo sobran, el error doble desaparece y la Defensoría
> se queda sin oficio.
>
> **El tablero es una vista de la capa 2, nunca de la capa 1.** Muestra el estado
> **según la fuente que la mesa haya adoptado como oficial** —y si no ha adoptado
> ninguna, muestra la del parte operacional, con su sesgo, sin avisar. Cada dato
> va con su procedencia y su grado:

```
Nodo 17 · caudal 0,3  [estimado · parte operacional · turno 3]
Nodo 12 · caudal 0,0  [confirmado · dupla Defensoría · turno 4]
Nodo 23 · caudal  ?   [sin verificar desde el turno 1]
```

> La tercera línea es la más valiosa del tablero. **Un signo de interrogación
> proyectado sobre la pared es una petición de decisión**: alguien tiene que
> gastar una dupla ahí, o alguien va a operar a ciegas. La ignorancia del Estado
> debe ser visible para que sea gestionable.

Si solo hay un proyector, se divide vertical: tablero arriba, esfera pública
abajo. Nunca en pestañas: la divergencia solo se percibe simultánea.

### 10.2 El moderador conduce; no juega

Su consola es el único punto de entrada de decisiones. Hace cuatro cosas:

1. **Transcribe** lo que la mesa acordó, en lenguaje natural.
2. **Lee de vuelta el plan interpretado** antes de ejecutar. Este momento es una
   pieza de diseño, no un trámite: *«Entiendo que ordenan concentrar ESMAD en los
   nodos 12, 17 y 23, replegando el 31 y el 44. Riesgo de incidente en el 17:
   alto. ¿Confirman?»* — la sala oye su propia decisión reformulada, con su
   riesgo, y con frecuencia la cambia. **Es el mejor punto de intervención
   pedagógica de todo el montaje.**
3. **Entrega información privada en papel** (§10.3).
4. **Inyecta** eventos de guion y, si hace falta, corrige un resultado
   estocástico — quedando registrado.

### 10.3 La asimetría de información se resuelve en papel

Sin pantallas por rol, la matriz de información deja de ser un filtro de software
y pasa a ser un **calendario de entregas físicas**. Esto es mejor, no peor:

| Momento | Qué se entrega | A quién |
|---|---|---|
| Antes de empezar | ficha del rol + sobre sellado con la agenda reservada | cada uno |
| Turno 1 | lectura de inteligencia sobre financiación de cierres | solo Defensa |
| Turno 2 | alerta de atentado contra el mandatario | solo Presidente |
| Cada turno | parte operacional con su sesgo | solo Policía |
| Cada turno | verificaciones de las duplas asignadas | solo Defensoría |
| Bajo umbral | calendario de agotamiento por región | solo Minas |

Una nota entregada en mano a un solo participante, en mitad de la deliberación,
produce **más tensión de sala que cualquier notificación en pantalla**: los otros
siete ven que alguien recibió algo y no saben qué. Ese es exactamente el problema
de información que el caso quiere enseñar.

### 10.4 El tablero se congela durante la deliberación

Regla dura: **entre la apertura del turno y la entrada de órdenes, ninguna
pantalla cambia.** Si el tablero se actualiza mientras la gente habla, la gente
mira el tablero.

Se descongela en la fase de resolución, y ahí sí conviene que el cambio sea
visible y con ritmo: las reservas se mueven, un nodo cambia de color, un titular
entra. La resolución es el único momento en que las pantallas compiten por la
atención, y debe durar poco.

### 10.5 El registro de decisiones es físico

Un pliego visible donde el moderador escribe, cada turno: **la decisión, el
responsable nominado y la hora.** Es la potestad que el Presidente absorbió del
Director del DAPRE, y ponerla en papel a la vista de todos tiene dos efectos:

- hace **visible la ausencia** cuando la mesa decide sin nominar a nadie —el
  renglón vacío es más elocuente que cualquier advertencia—;
- y produce el insumo del debriefing con la letra de los propios participantes.

### 10.6 Qué se pierde y qué se hace en su lugar

| Se pierde | Sustituto |
|---|---|
| Trazabilidad automática de quién pidió qué | el moderador etiqueta cada orden con el rol proponente al transcribir |
| Consulta individual al asistente | consulta en voz alta; la respuesta la oye toda la sala, que es mejor |
| Filtrado por rol verificable en código | entrega física + honestidad; el caso tiene ocho personas, no doscientas |
| Simultaneidad de acciones | secuenciación por turno, que además obliga a priorizar |

La tercera fila merece una advertencia honesta: **la confidencialidad en papel
depende de que los participantes no se pasen las hojas.** Con ocho personas
sentadas a una mesa y un facilitador presente es sostenible. No escalaría a un
ejercicio de treinta.

---

## 11. Qué NO debe hacer el motor

Lo mismo que en Macondo, más tres reglas propias de este caso.

- **No decide si la respuesta fue correcta.** Calcula consecuencias. El juicio es
  del debriefing, y es de las personas.
- **No llama a ningún modelo de lenguaje.** Debe correr entero sin clave de API.
- **No conoce nombres legibles ni roles**: eso es la capa 4 y la capa 2.

Y las tres nuevas:

- **Ningún incidente se narra a la existencia.** La probabilidad se calcula en
  código desde el estado, se muestra antes de decidir y se resuelve con semilla
  registrada. Un modelo no puede decidir que hubo un muerto.
- **Ninguna apertura de corredor la determina un agente de IA.** El Comité del
  Paro redacta su posición; el caudal lo calcula el motor.
- **El motor no revela `composicion_real`.** Ni en la interfaz, ni en los logs
  que el facilitador proyecta, ni en un mensaje de depuración. Se revela en el
  debriefing y no antes. Si se filtra, el dilema central desaparece.

---

## 12. Decisiones abiertas

Reúne lo que este diseño **no** resuelve. Va ordenado por lo que bloquea: primero
lo que necesito decidido antes de construir, después lo que solo se resuelve
corriendo el ejercicio, y al final los riesgos que asumo a sabiendas.

### 12.1 Lo que hay que decidir antes de construir

| # | Decisión | Mi recomendación |
|---|---|---|
| **D1** | **¿Nombres reales o ficticios?** El Manual de Roles usa Cali, Cauca y Buenaventura. Ficcionalizar protege de convertir el ejercicio en un juicio sobre hechos con responsabilidad judicial viva; cuesta el reconocimiento inmediato que hace que el caso muerda. | Mantener los reales por coherencia con el Manual, y añadir al turno 0 una declaración expresa de que el ejercicio no juzga hechos ni personas. |
| **D2** | **¿Se puntúa?** Y en particular: ¿las agendas reservadas suman? Si los participantes concluyen que ganar es cumplir su §11 a costa de la sala, se pierde el objeto. | Sin marcador. Las agendas se revelan, no se puntúan. Se evalúa el resultado colectivo y la calidad del proceso. |
| **D3** | **¿La Defensoría puede retirarse de verdad**, dejando el ejercicio sin sus mitigadores, o es una amenaza que el diseño nunca deja consumar? | Que pueda. Un condicionamiento que no se puede cumplir no es una palanca, y el resultado en que el rol correcto pierde por exceso es pedagógicamente valioso. |
| **D4** | **¿`capital_politico` se queda?** Tal como está en §3.6 **no es implementable**: el motor no sabe quién se opone a quién, porque la deliberación ocurre en voz alta y no entra al sistema. | Eliminarlo. Con ocho personas en una sala, el capital político lo administra la sala sola; modelarlo duplica algo que funciona mejor sin motor. |
| **D5** | **¿El paquete detonante del turno 1 es fijo o se sortea** entre varias versiones? Fijo permite comparar salas; sorteado evita que el facilitador que ya lo vio lo anticipe. | Fijo las primeras corridas —hacen falta para calibrar—, sorteado después. |
| **D6** | **¿Se acepta el estocástico?** «Hicimos todo bien y salió mal» es una lección real y difícil de recibir. Mitigado con la banda de riesgo visible antes de decidir y la corrida reproducible, pero no resuelto. | Decisión del equipo docente, no mía. |

### 12.2 Ajustes técnicos pendientes

Los recomiendo yo y solo necesitan visto bueno.

| # | Problema | Ajuste |
|---|---|---|
| **T1** | **`intensidad_movilizacion` satura y deja de discriminar.** Arranca en 61, un incidente mortal suma hasta +25 y el decaimiento es de −2 por turno: con dos incidentes queda clavada en 100 y a partir de ahí toda decisión da igual. Es lo peor que le puede pasar a la variable central del motor. | Incrementos con rendimientos decrecientes —el segundo muerto de la semana mueve menos que el primero— y decaimiento proporcional al nivel. **Es la calibración más urgente del modelo.** |
| **T2** | **`control_voceria` no está en la capa de estimación.** §4.3 lo usa para calcular el caudal de una apertura concertada, pero nada dice cómo lo observa Interior. Si lo ve, elige siempre el nodo con vocería fuerte y el dilema desaparece. | Entra a la tabla de fuentes con sesgo propio: Interior lo **sobreestima** —su interlocutor le asegura que controla más de lo que controla—; Cali lo estima bien en su jurisdicción y en ninguna otra. Vuelve necesaria la relación Interior–Cali. |
| **T3** | **`dureza` la escriben dos mecanismos sin precedencia declarada:** `g(intensidad)` en §4.1 y `+0,03` por turno sin decisión en §5.6. | Declarar el orden. Menor, pero sin definir produce corridas irreproducibles. |
| **T4** | **El presupuesto de latencia no está calculado.** Seis agentes, cinco turnos y cuatro interludios: 40–50 invocaciones de modelo. La fase de consecuencias dura 60 segundos con ocho personas mirando la pantalla. | Ejecución en paralelo con presupuesto de tiempo duro, degradando a contenido de plantilla si el proveedor tarda. |

### 12.3 Lo que solo se resuelve corriendo el ejercicio

**Ningún coeficiente de este documento está calibrado, y no hay forma de
calibrarlo en el escritorio.** La inundación se podía contrastar con literatura de
desastres; aquí no hay respuesta empírica a cuánta legitimidad cuesta un muerto.

**Criterio propuesto: calibrar por comportamiento, no por realismo.** Ajustar hasta
que ninguna estrategia pura —solo fuerza, solo mesa— gane, y documentar los
coeficientes como convenciones declaradas y no como hallazgos. **La primera corrida
es una medición, no un ejercicio**, y conviene decirlo antes de empezar.

Tres cosas concretas que mirar en esa primera corrida:

- **¿24 nodos son demasiados para 5 decisiones?** Si la sala toca menos de diez,
  bajar a 16.
- **¿Da tiempo a que la mesa se rompa?** El deterioro de la cohesión es una de las
  tres lecturas del debriefing, y con cinco decisiones puede no aparecer. Si la
  cohesión termina por encima de 55 casi siempre, subir la sensibilidad —o aceptar
  que un ejercicio de dos horas mide la constitución de la mesa y no su desgaste,
  que también es un objeto legítimo.
- **¿Se cumplen los 13 minutos?** Si no, el problema es de moderación y se corrige
  con guion, no con diseño.

### 12.4 Riesgos asumidos

**El moderador es el punto único de fallo.** Sin pantallas individuales, el ritmo
entero depende de una persona. Requiere ensayo completo y un guion de moderación,
no solo un manual de roles.

**La confidencialidad en papel depende de que nadie pase la hoja.** Con ocho
personas y un facilitador presente es sostenible. No escalaría a treinta.

**El caso es reciente y tiene víctimas reales.** El motor no cuantifica culpa ni
produce veredictos sobre hechos históricos: calcula consecuencias de decisiones
tomadas en la sala. Conviene que eso se diga en voz alta en el turno 0, decida lo
que se decida sobre D1.

---

## 13. Qué se reutiliza de Macondo

La arquitectura de cuatro capas se sostiene entera. Lo que se sustituye es la capa 1.

| Componente | Estado |
|---|---|
| Arquitectura de 4 capas · «el LLM traduce, el motor decide» | **íntegra** |
| Patrón `Accion` con `validar()`/`ejecutar()` | íntegro, más `requisitos_de_otros_roles` |
| Tres colas (inmediata, tiempo, condición) | íntegro; la condicional pesa más aquí |
| Reporte determinista tras ejecutar · la invariante | íntegro |
| Plan aparcado con elección tipada | íntegro, y más útil: el moderador lo lee a la sala |
| Resolutor determinista de entidades | reutilizable; cambia el catálogo a nodos y corredores |
| Expansor de plan con tope | reutilizable; mismo riesgo de producto cartesiano |
| Telemetría por turno | reutilizable; cambian los campos, no la disciplina |
| Consola del facilitador | se amplía: pasa de observar a conducir |
| **Motor físico** (lluvia, daño, heridos) | **no aplica** — lo sustituyen los seis motores de §4 |
| **Matriz de información por rol** | **cambia de medio**: de filtro de software a calendario de entregas en papel |
| **Pantallas por rol** | **se eliminan** (§10) |

Los ocho modos de falla de la guía siguen siendo los mismos ocho. Dos son peores
aquí:

- **F3 — resolución de entidades que acierta mal en silencio.** En Macondo enviaba
  ayuda al barrio equivocado. Aquí envía **ESMAD** al nodo equivocado.
- **F1 — la confirmación se redacta antes de ejecutar.** Aquí la lee un moderador
  en voz alta a ocho personas que van a creerle.

---

*Documento de diseño derivado del Manual de Roles con RADs (8 roles) y de la
Matriz Operativa del caso Estallido Social, sobre la arquitectura de
[`../guia_arquitectura_simulaciones.md`](../guia_arquitectura_simulaciones.md). Los
coeficientes son propuestas de partida para calibrar, no valores medidos.*
