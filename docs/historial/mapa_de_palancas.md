# Mapa de palancas

Cómo funciona el ejercicio **como juego**: qué puede hacer cada uno de los ocho
participantes, cómo se afectan entre sí, y qué tan bien lo sostiene el motor.

Está escrito para decidir el diseño del ejercicio, no para leer código. Va en
tres partes y el orden es deliberado:

| Parte | Qué contiene | Para quién |
|---|---|---|
| **I** | [El ejercicio](#parte-i--el-ejercicio) — qué pasa en la sala y cuáles son las reglas del juego | equipo docente y moderación |
| **II** | [Los ocho jugadores](#parte-ii--los-ocho-jugadores) — qué puede hacer cada uno y cómo se afectan | equipo docente |
| **III** | [El motor](#parte-iii--el-motor) — qué de todo esto sostiene el código hoy | quien vaya a construir |

**Las partes I y II describen el ejercicio que el caso propone**, tomado del
Manual de Roles y la Matriz Operativa del GovLab. La parte III lo contrasta con
lo que está construido. Si solo se leen las dos primeras, se entiende el juego
entero.

Una convención: en las fichas de la parte II cada acción lleva **●** si el motor
ya la sostiene y **○** si todavía no. La parte III explica qué cuesta cada
ausencia.

---

## Índice

**Parte I · El ejercicio**

1. [Qué pasa en la sala](#1-qué-pasa-en-la-sala)
2. [Qué tiene que descubrir la sala](#2-qué-tiene-que-descubrir-la-sala)
3. [Las reglas del juego](#3-las-reglas-del-juego)

**Parte II · Los ocho jugadores**

4. [El tablero de los ocho](#4-el-tablero-de-los-ocho)
5. [Ficha por ficha](#5-ficha-por-ficha)
6. [Cómo se afectan entre sí](#6-cómo-se-afectan-entre-sí)
7. [Los seis dilemas que el diseño garantiza](#7-los-seis-dilemas-que-el-diseño-garantiza)

**Parte III · El motor**

8. [Qué promete el diseño y qué entrega el motor](#8-qué-promete-el-diseño-y-qué-entrega-el-motor)
9. [Dónde la traducción está incompleta](#9-dónde-la-traducción-está-incompleta)
10. [Las cuatro decisiones abiertas](#10-las-cuatro-decisiones-abiertas)

---
---

# PARTE I · El ejercicio

## 1. Qué pasa en la sala

Ocho personas, un moderador, **dos horas exactas**. La mesa no lleva pantallas:
hay dos proyecciones para toda la sala y un solo teclado, el del moderador.

El paro lleva quince días cuando los ocho entran. El Puesto de Mando ya está
convocado, la mesa de diálogo ya se instaló y ya se rompió una vez, y la fuerza
ya está desplegada y cansada. **No existe una acción que dé inicio al ejercicio:**
lo que da inicio es un estado heredado y una exigencia con plazo. La primera
decisión no es *empezar* sino *elegir qué atender primero*.

| Bloque | Minutos | Qué ocurre |
|---|---:|---|
| Instalación y turno 0 | 12 | Fichas y sobres sellados. El moderador lee el parte heredado. Cada rol declara en 60 segundos dónde se ubica: fuerza, negociación o secuencia |
| **5 turnos de decisión** | **65** | 13 minutos cada uno |
| **4 interludios nocturnos** | **12** | 3 minutos cada uno, **sin deliberación** |
| Debriefing | 20 | Incluye la proyección a 72 horas |
| Holgura | 11 | Los turnos se pasan. Siempre |

### El turno de día

```
1 · APERTURA        1,5 min   el moderador lee qué cambió y qué se rompió
2 · DELIBERACIÓN    6,0 min   el tablero NO se mueve. La sala discute
3 · ÓRDENES         2,5 min   el moderador transcribe y LEE EL PLAN DE VUELTA,
                              con su banda de riesgo. La sala confirma o corrige
4 · RESOLUCIÓN      1,0 min   el motor ejecuta
5 · CONSECUENCIAS   1,0 min   prensa, redes, gremios, internacional
6 · REGISTRO        1,0 min   la decisión al pliego, con responsable nominado
```

Seis minutos de deliberación es poco **a propósito**. Ocho personas no alcanzan a
discutirlo todo, así que tienen que elegir qué discutir — y esa es la competencia
que el ejercicio entrena. El paquete que abre cada turno trae cuatro hechos
precisamente para que no quepan.

El paso 3 es la mejor pieza del montaje. Cuando el moderador lee de vuelta
*«entiendo que ordenan concentrar el ESMAD en estos tres puntos, replegando los
otros dos; riesgo de incidente en el segundo: alto — ¿confirman?»*, la sala oye
su propia decisión reformulada con su precio, **y con frecuencia la cambia**.

### El interludio de noche

**La noche no se delibera: se sufre.** El moderador no pide órdenes; resuelve lo
que se ordenó de día, y la sala mira cómo un camino abierto por la fuerza se
cierra otra vez, cómo entra un titular, cómo baja el reloj de abastecimiento.
Tres minutos.

No elimina la decisión nocturna: de día se puede *ordenar* operar de noche, y se
resuelve en el interludio con el riesgo multiplicado. Lo que se elimina es el
costo en minutos de sala. Y hay un beneficio de diseño: **la pérdida de control
se representa quitándoles el turno.**

### Las dos proyecciones

- **El tablero de situación** — lo que el Estado tiene por cierto, con la
  procedencia de cada dato y su grado: confirmado, estimado, o sin verificar.
- **La esfera pública** — lo que se dice: prensa, redes, pronunciamientos
  internacionales, y las cifras en disputa.

**La distancia entre las dos es el caso.** Van simultáneas y nunca en pestañas,
porque la divergencia solo se percibe si se ven a la vez.

### La información reservada va en papel

Sin pantallas por rol, la asimetría de información deja de ser un filtro de
software y pasa a ser un **calendario de entregas físicas**: una nota en mano a
un solo participante, en mitad de la deliberación. Los otros siete ven que
alguien recibió algo y no saben qué. Eso produce más tensión de sala que
cualquier notificación en pantalla — y es exactamente el problema de información
que el caso quiere enseñar.

## 2. Qué tiene que descubrir la sala

El ejercicio existe para producir **dos hallazgos en el debriefing**. Todo lo
demás está al servicio de eso.

### Primer hallazgo · la distancia entre lo que se declaró y lo que se hizo

En el turno 0 cada rol declara en 60 segundos si su línea es la fuerza, la
negociación, o una secuencia entre ambas — y **qué condición concreta lo movería
de posición**. El moderador lo registra.

Casi todas las salas declaran una secuencia —«primero la mesa, fuerza solo si
falla»— y casi ninguna la cumple, porque los hechos del turno 1 empujan hacia la
operación y nadie vuelve a mirar lo que dijo al entrar. **Esa distancia es la
métrica principal del ejercicio**, y sin el turno 0 no existe.

La segunda mitad de la pregunta importa tanto como la primera: obliga a cada rol
a nombrar por adelantado su propia condición de cambio, y en el debriefing se
contrasta con si esa condición se cumplió y si el rol se movió o no.

### Segundo hallazgo · la primera decisión no era sobre el territorio

Hay seis acciones que **no abren ningún camino, no aparecen en el tablero y
parecen burocracia mientras el país arde**: poner por escrito quién decide qué,
fijar el estándar de empleo de la fuerza, acordar quién habla, adoptar una sola
forma de verificar cifras, fijar el criterio de priorización, y declarar las
líneas rojas.

Ninguna está prohibida y ninguna es obligatoria. **El diseño no fuerza a la sala
a constituirse: le permite saltárselo y le cobra la diferencia.**

La mayoría de las salas se las salta y lo paga hacia la mitad del ejercicio,
cuando hay tres cifras en disputa, dos operaciones que el ministro del diálogo no
conocía y ningún renglón del pliego con un nombre escrito.

> Que la primera decisión no era sobre el territorio sino sobre la propia mesa es
> el segundo hallazgo del caso. **El ejercicio no debe enseñarlo: debe hacer que
> cueste no haberlo resuelto.**

### El principio que ordena el diseño

> **La lluvia no reacciona a lo que usted decide. Una movilización sí.**

En el ejercicio anterior —una inundación— el fenómeno estaba precalculado: llovía
lo mismo hicieran lo que hicieran. Aquí no. Cada operación de fuerza, cada cifra
desmentida y cada sesión de mesa **modifica la intensidad de aquello que se
intenta contener**.

## 3. Las reglas del juego

### 3.1 Lo que es escaso

Nada en esta mesa es gratis, y hay cuatro clases de escasez distintas.

**La fuerza.** Hay 40 escuadrones de la unidad entrenada para control de
multitudes. **34 ya están desplegados y cansados; quedan 6 libres.** Sobre 24
puntos de cierre modelados —que representan más de mil reales—. Cada punto que se
atiende es un punto que se descubre.

**La credibilidad, en cuatro reservas.** Se consumen rápido, se recuperan
despacio, y a diferencia del dinero **no se pueden pedir prestadas**:

| Reserva | Qué es | Cómo llega |
|---|---|---|
| Legitimidad interna | El respaldo ciudadano a la respuesta | ya deteriorada |
| Credibilidad de la mesa | La viabilidad del canal de diálogo | ya deteriorada |
| Exposición internacional | Cuánto observa el mundo *(al revés: arriba es peor)* | ya deteriorada |
| **Cohesión de la mesa** | Si el PMU actúa como uno o como ocho | **empieza alta** |

**Tres se heredan dañadas y una no**, y es deliberado. La sala no rompió las tres
primeras y no puede culpar a nadie presente: hereda un pasivo. **La cohesión es
enteramente suya** — todo lo que le pase entre el turno 1 y el 5 lo hicieron los
ocho. En el debriefing es la única serie de la que no pueden desentenderse.

**Las reservas tienen umbrales duros, no efectos suaves.** Un deterioro gradual
no produce decisiones; un umbral sí. Cuando la legitimidad cae lo suficiente, los
gremios camioneros evalúan sumarse al paro, y si cae más, se suman: el bloqueo
pasa a ser cierre logístico nacional. Cuando la credibilidad de la mesa cae, el
Comité del Paro suspende su participación, y si cae más, no vuelve a sentarse.

**El tiempo.** Cada región tiene días de autonomía de combustible, alimentos y
oxígeno medicinal. **Bajan solos y solo suben si alguien abre un camino.** La más
apretada arranca con menos de dos días de oxígeno.

**La verdad.** Solo hay duplas de verificación para **tres puntos por turno**, de
veinticuatro. Verificar aquí es no verificar allá.

### 3.2 Las tres formas de abrir un camino

**Esta es la mecánica central del caso.** Tres vías con economías radicalmente
distintas, y la elección entre ellas es lo que el ejercicio enseña.

| Vía | Tarda | Cuánto abre | ¿Se sostiene? | Qué consume |
|---|---|---|---|---|
| **Fuerza** | 1 turno | mucho | **no — vuelve a cerrarse esa misma noche** | legitimidad, credibilidad de la mesa y exposición |
| **Concertación** | 2 turnos | *tanto como controle el vocero con quien se pactó* | sí, mientras el acuerdo se cumpla | nada, si se cumple |
| **Desgaste** | 4 turnos o más | medio | sí | **nada** |

Tres consecuencias que la sala descubre en distinto momento:

**Un camino vale lo que su peor punto.** No basta con abrir un cierre: hay que
abrir todos los del corredor a la vez. Y como lo abierto por la fuerza se cierra
de noche, con cinco turnos **la fuerza casi nunca alcanza a sostener un corredor
entero**. Es el resultado más contraintuitivo del ejercicio y no se diseñó a
mano: sale de la aritmética.

**La trampa de la concertación.** Lo que se logra abrir es proporcional a cuánto
controla realmente el vocero con quien se pactó. Negociar con alguien que controla
el 40 % del punto produce una apertura del 40 % que se anuncia como éxito y **se
desmiente sola en veinticuatro horas**.

**Los puntos duros son justamente aquellos donde no hay con quién hablar.** El
escenario lo reparte así a propósito: los cierres fáciles de pactar son blandos y
los difíciles no tienen vocería reconocida. No existe una respuesta que sirva
para todos.

### 3.3 El riesgo, y lo único que lo baja sin gastar capacidad

Cuando la sala ordena una operación, el sistema calcula **antes de ejecutarla**
qué probabilidad hay de que termine mal, y el moderador la lee en voz alta como
banda —baja, media, alta, crítica—. La sala gestiona riesgo, no sorpresa.

Ese riesgo sube con cosas que la sala no eligió —cuán duro es el punto, cuánta
gente hay, si es de noche— y con una que sí: **qué unidad se manda**. La unidad
entrenada para multitudes es varias veces más segura que la policía regular, y
esta varias veces más segura que tropa de combate.

Y baja con **seis decisiones que no cuestan un solo escuadrón ni un solo peso**:

| Lo que baja el riesgo | Quién lo habilita |
|---|---|
| Reglas de empleo de la fuerza escritas y vigentes | Defensoría, o el Presidente al firmar con límites |
| Identificación individual de los agentes | Defensoría |
| Registro audiovisual obligatorio | Defensoría |
| Una dupla de verificación presente en el punto | Defensoría |
| Operación concertada con la alcaldía | Alcalde |
| Unidades descansadas | Director de la Policía |

**Juntas dividen la probabilidad de un mal resultado por casi cinco.**

> Es el hallazgo positivo del diseño: **el rol sin voto y sin fuerza resulta ser
> el que más reduce la probabilidad del peor resultado.** El Delegado de la
> Defensoría no está en la sala para moralizar; está para bajar una probabilidad.
> Y se descubre haciendo la cuenta, no leyéndolo en la ficha.

Hay una asimetría deliberada y conviene que la moderación la sepa explicar: **el
estándar protege a quien ya venía operando con cuidado y no rescata a quien no.**
Una operación bien hecha pasa de riesgo alto a riesgo bajo; una operación
temeraria —tropa de combate, cansada, de noche, en un punto duro— sigue siendo
temeraria aunque se apliquen los seis. En t=0 **no hay ninguno activo**: la
primera operación que la sala ordene, si la ordena antes de constituir nada,
corre sin ningún descuento. Eso no se les dice. Se descubre.

### 3.4 Lo que la sala no puede saber

**El Estado no observa el mundo: lo estima.** Cada punto de cierre tiene una
composición real —cuánto es protesta legítima, cuánto vandalismo oportunista y
cuánto estructura organizada— que **nadie ve**, ni la interfaz, ni el moderador.
Se revela en el debriefing y no antes.

Lo que cada rol ve es una estimación, y **los sesgos van en direcciones opuestas
a propósito**:

| Quién estima | Cómo se equivoca | Qué alcanza a ver |
|---|---|---|
| Inteligencia del Ministerio de Defensa | **sobreestima** la estructura organizada | media cobertura |
| Parte operacional de la Policía | subestima víctimas civiles | todos los puntos |
| Parte municipal de la Alcaldía | **subestima** la estructura organizada | solo su ciudad |
| Duplas de la Defensoría | casi no se equivoca | **tres puntos por turno** |

**La fuente más precisa es la que menos alcanza a ver.** Eso convierte a la
Defensoría en un recurso que hay que *asignar*, no consultar.

De ahí sale el error doble, y **ninguna de las dos salidas es segura**:

- Tratar como violencia organizada un punto que es sobre todo protesta legítima →
  fuerza sobre población civil → el costo máximo en legitimidad y exposición.
- Tratar como protesta legítima un punto con estructura organizada → se negocia
  con quien no controla nada → el acuerdo se incumple visiblemente → cae la
  credibilidad de la mesa y los partidarios del escalamiento ganan el argumento.

> No hay opción segura. Hay una decisión sobre **cuánta evidencia se exige antes
> de tratar un punto de una u otra forma** — que es exactamente la casilla
> Seguridad × Información de la matriz del Manual.

### 3.5 Los dos relojes

**El reloj de la crisis.** Los días de autonomía bajan solos. El oxígeno
medicinal es el único que **convierte logística en muertes**, y no es una variable
independiente sino el extremo de una cadena que empieza en una decisión de la
sala:

```
camino abierto → entra combustible → hay diésel para los carrotanques
                                   → y para las plantas de emergencia del hospital
                                   → las plantas sostienen la producción y el frío
                                   → hay oxígeno en la UCI
                                   → no se muere quien no tenía que morirse
```

Cortar la cadena en cualquier punto la rompe entera. **Por eso el oxígeno no
modela salud: modela el alcance de una decisión logística.** Y por eso ninguna
cartera lo resuelve sola — hacen falta cuatro.

Una regla de diseño que hubo que hacer cumplir a la fuerza: **toda región debe
tener al menos un camino humanitario que la sirva**. Sin eso, sus muertes son
inevitables haga lo que haga la sala, y eso no es un dilema: es un guion que
castiga.

**El reloj de la sala.** Dos horas, y no todos los turnos necesitan deliberación.
Con cinco turnos de decisión, **toda mecánica que tarde tres turnos en rendir es
inviable** — por eso la concertación tarda dos y no tres, y por eso constituirse
temprano vale mucho más que en un diseño de diez turnos. El ejercicio se vuelve
más denso y menos indulgente, que para dos horas es lo correcto.

### 3.6 El ejercicio no termina en el turno 5

En el último turno la fuerza saldría gratis: lo que se abre por la fuerza reabre
en uno o dos turnos, y ya no quedan turnos. Una sala que lo advierta —y alguna lo
advertirá— podría desatar al final todo lo que evitó antes y salir con mejores
números.

**El antídoto:** terminado el turno 5, el sistema corre tres turnos más **sin
nadie al mando** y proyecta el estado a 72 horas. Se lee en voz alta.

> No es un marcador: **es el país que la sala entrega.** Y es la pregunta con la
> que conviene abrir el debriefing: *¿esto se sostiene sin ustedes?*

---
---

# PARTE II · Los ocho jugadores

## 4. El tablero de los ocho

Tres frentes, y ninguno puede ejecutar su objetivo sin los otros dos.

| | Rol | Frente | Lo que aporta que nadie más aporta |
|---|---|---|---|
| 01 | Presidente de la República | Estrategia | La única firma que activa los instrumentos excepcionales |
| 02 | Ministro del Interior | Estrategia | El canal de diálogo. **Es la alternativa institucional a la fuerza** |
| 03 | Alcalde de Cali | Estrategia | El epicentro: interlocución con quienes sostienen los cierres |
| 04 | Ministro de Defensa | Seguridad | La conducción política de la fuerza y la inteligencia |
| 05 | Director General de la Policía | Seguridad | El ESMAD, y la fuente primaria de la cifra oficial |
| 06 | Delegado de la Defensoría | Seguridad | El estándar de derechos y la verificación creíble. **Sin voto** |
| 07 | Ministro de Transporte | Logística | El mapa de cierres y el criterio de priorización |
| 08 | Ministro de Minas y Energía | Logística | Los días de autonomía y la dependencia sistémica |

Y tres ejes que cruzan los tres frentes, cuyas nueve casillas **son la
arquitectura que la mesa tiene que acordar**:

| | **Mando** | **Información** | **Vocería** |
|---|---|---|---|
| **Estrategia** | ¿Quién fija las líneas rojas y quién puede moverlas? | ¿Qué se reconoce como cierto ante la contraparte y ante el mundo? | ¿Quién habla por el Gobierno y hasta dónde se desplaza? |
| **Seguridad** | ¿Quién autoriza el escalamiento y qué reglas se delegan? | ¿Qué evidencia se exige para tratar un punto como violencia organizada? | ¿Quién explica cada operación, con qué antelación? |
| **Logística** | ¿Quién prioriza cuando la capacidad alcanza para uno? | ¿Quién consolida bloqueos e inventarios, y con qué ciclo? | ¿Qué se anuncia como abierto y quién responde si vuelve a cerrarse? |

## 5. Ficha por ficha

**●** el motor ya lo sostiene · **○** todavía no

### 01 · Presidente de la República

> **Lo que quiere:** recuperar el control del orden público sin adoptar el
> instrumento que le daría a la narrativa de represión su mejor argumento, y sin
> perder la conducción frente a frentes que reclaman autonomía.

**Controla:** la firma exclusiva de la asistencia militar y de la conmoción
interior · la orden preferente sobre alcaldes y gobernadores en orden público ·
la vocería máxima del Estado · la agenda del Puesto de Mando y el poder de
delegar · su propia presencia en el territorio, limitada por alertas de atentado.

**Puede hacer:**

- **●** Firmar o negar la asistencia militar — **y con qué límites**: territorio,
  plazo, reglas escritas y criterio de terminación
- **●** Fijar qué se decide en el centro y qué se delega, con responsable
  nominado y registro escrito de cada decisión
- **●** Fijar públicamente las líneas rojas y el marco de lo negociable
- **○** Convocar a los alcaldes de las ciudades críticas para pactar reglas de
  empleo de la fuerza y de vocería
- **○** Ir o no ir al epicentro, y si acompaña una operación o una mesa

**Cómo afecta al juego.** Su firma es la bisagra de todo el frente de seguridad:
sin ella no hay capacidad militar. Pero **firmarla le cuesta la mesa a Interior
en el mismo turno**, y firmarla sin límites multiplica por tres el costo
internacional. Su decisión de poner las cosas por escrito es la que determina si
el costo de un error cae sobre quien firmó o se reparte sobre los ocho.

> **Su dilema:** concentrar decisiones lo hace responsable de cada error
> operativo; delegarlas lo deja sin control sobre la coherencia de la respuesta.

### 02 · Ministro del Interior

> **Lo que quiere:** producir un resultado verificable en la mesa antes de que la
> línea de negociación pierda vigencia, y evitar que la conducción de la crisis la
> absorba el frente de seguridad.

**Controla:** el canal de diálogo con el Comité Nacional del Paro y con las
vocerías locales · la relación con el Congreso y los partidos, y la capacidad de
ofrecer trámite legislativo como contraprestación · la articulación con alcaldías
y gobernaciones · el protocolo de vocería del Gobierno.

**Puede hacer:**

- **○** Convocar una sesión de la mesa nacional con agenda acotada, excluyendo lo
  que el Presidente declaró línea roja
- **○** Abrir mesas locales de concertación **camino por camino**, sin reconocer a
  esas vocerías como interlocutor nacional
- **○** Ofrecer el trámite de una medida social ante el Congreso como
  contraprestación verificable por el levantamiento de un conjunto de cierres
- **●** Exigir un protocolo que obligue a informar a la mesa toda operación con
  efecto sobre el diálogo, con plazo suspensivo de 24 horas
- **○** Convocar a los alcaldes de las ciudades no representadas

**Cómo afecta al juego.** Es el único que puede bajar la temperatura sin gastar
un escuadrón: un acuerdo cumplido es el movimiento que más desinfla la
movilización en todo el sistema. Su plazo suspensivo protege el canal y a la vez
**impide intervenciones que el terreno exige**, lo que el frente de seguridad lee
como subordinación política de decisiones operativas.

> **Su dilema:** su capital es el canal abierto, y ese capital se agota cuando el
> Gobierno negocia y despliega fuerza en la misma jornada. Reconocer denuncias de
> abuso destruye su posición ante el sector de seguridad; negarlas destruye el canal.
>
> **Su pregunta estratégica:** *¿con quién se negocia cuando quien tiene vocería
> no controla el bloqueo, y quien controla el bloqueo no puede ser reconocido
> como interlocutor?*

### 03 · Alcalde de Cali

> **Lo que quiere:** reabrir la ciudad y el camino al puerto sin que la fuerza
> caiga sobre los barrios donde está su base social, y sin quedar como el alcalde
> que perdió la ciudad ni como el que la entregó a la militarización.

**Controla:** la autoridad municipal sobre movilidad, espacio público y atención
humanitaria local · la interlocución directa con quienes sostienen los puntos de
resistencia · la verificación de hechos en su territorio · vocería propia con
alcance nacional e internacional.

**Puede hacer:**

- **●** Instalar una mesa local de desbloqueo con los voceros de un punto, para
  acordar apertura por franjas horarias
- **○** Publicar el parte municipal verificado y **disputar públicamente la cifra
  oficial nacional**
- **○** Condicionar públicamente su respaldo al empleo de fuerza en su
  jurisdicción a que se concierten los puntos con la Alcaldía
- **●** Activar un esquema humanitario municipal —abastecimiento a barrios
  aislados, ollas comunitarias— que reduzca el incentivo material del cierre
- **○** Exigir formalmente prioridad de fuerza y de caminos para su ciudad, con
  atribución escrita de responsabilidad si se le niega

**Cómo afecta al juego.** Es el único que puede abrir un camino **sin consumir
ninguna reserva**: su esquema humanitario baja el respaldo del barrio al cierre
sin alimentar la movilización, y el cierre acaba deshaciéndose solo. Es lento y
es gratis. Y su condicionamiento público encarece cada operación que el nivel
nacional quiera hacer en su ciudad.

> **Su dilema:** necesita las dos cosas y no puede pedir ninguna sin costo:
> reclama despliegue y simultáneamente rechaza que su territorio sea tratado como
> escenario de operación. Necesita que el deterioro sea atribuible al abandono
> nacional y no a su administración.

### 04 · Ministro de Defensa

> **Lo que quiere:** recuperar caminos y control territorial con una fuerza
> materialmente insuficiente, obteniendo autorización para escalar **sin que la
> decisión se lea como militarización de la protesta social**.

**Controla:** la conducción política del sector · la capacidad militar disponible,
al costo de retirarla de erradicación y frentes rurales · la inteligencia sobre
financiación e infiltración de los cierres · la doctrina y las reglas de empleo
de la fuerza · la vocería sectorial.

**Puede hacer:**

- **○** Presentar al Presidente la solicitud de asistencia militar, con
  delimitación, plazo, reglas escritas y criterio de terminación
- **○** Redesplegar unidades militares desde el campo a proteger instalaciones,
  para **liberar policías de la custodia y concentrar ESMAD**
- **○** Presentar en la mesa y ante la opinión la evidencia de financiación de
  cierres, como criterio para tratar cada punto de forma distinta
- **●** Ordenar una operación de desbloqueo, con reglas escritas y registro
  audiovisual obligatorio
- **○** Ejecutar la proyección aérea de más de mil policías al epicentro

**Cómo afecta al juego.** Es quien tiene la acción que más mueve el tablero, y
por eso el ejercicio tiende a la fuerza si nadie lo frena. **Cada operación con
víctimas consume la legitimidad de la que depende la mesa de Interior**, que no
la ordenó. Su redespliegue es la única forma de aumentar la capacidad disponible
sin la firma presidencial, y abre un frente rural desatendido.

> **Su dilema:** cada operación de desbloqueo puede producir exactamente la imagen
> que alimenta la movilización que intenta contener. Y le preocupa que **el sector
> cargue en solitario el costo de decisiones tomadas colectivamente en esta sala**
> — por eso quiere las órdenes por escrito y con responsable identificado.

### 05 · Director General de la Policía Nacional

> **Lo que quiere:** sostener la contención en más de mil puntos con la única
> fuerza entrenada para hacerlo, **sin que un solo error individual destruya la
> legitimidad de toda la operación**.

**Controla:** el mando operacional sobre el ESMAD y los comandos metropolitanos ·
el parte operacional diario, que es la fuente primaria de la cifra oficial · la
inteligencia policial para individualizar casos · la capacidad de escoltar
caravanas de carga y de misión médica · el registro audiovisual propio.

**Puede hacer:**

- **○** **Concentrar el ESMAD** en un número acotado de puntos, replegando la
  contención en el resto
- **○** **Escoltar caravanas** de carga y de misión médica en los caminos
  priorizados, con ventanas horarias acordadas
- **○** Publicar el parte distinguiendo **lo confirmado, lo estimado y lo que está
  en verificación**, y sostener esa clasificación
- **○** Individualizar y documentar casos para judicialización, en vez de capturas
  masivas
- **●** Solicitar relevo de las unidades agotadas, aceptando reducir la cobertura
  simultánea

**Cómo afecta al juego.** Es el cuello de botella físico de todo el sistema. **Su
escolta es la condición material de la logística**: sin escolta no hay caravana ni
carrotanque, por más que Transporte priorice y Minas asigne. Y su repliegue de un
punto secundario para concentrar en uno crítico se lee como abandono territorial
por el alcalde que lo pierde.

> **Su dilema:** cada intervención pone en riesgo la vida de sus hombres y cada
> abstención los deja como blanco fijo. La fatiga es su principal factor de error,
> y pedir relevo significa aceptar menos cobertura hoy para bajar la probabilidad
> de una catástrofe mañana.

### 06 · Delegado de la Defensoría del Pueblo

> **Lo que quiere:** elevar el estándar de derechos de la respuesta estatal
> **desde adentro de la sala y antes de que ocurra el hecho**, sin que su
> presencia se lea como aval del Gobierno.

**No forma parte del Gobierno ni de la línea de mando. Asiste sin voto y sin
capacidad de decisión operativa.**

**Controla:** el requerimiento formal y la alerta temprana con registro
documental de la fecha en que advirtió · credibilidad simultánea ante el Gobierno
y ante quienes protestan · la ventanilla única de denuncias de todos los actores
· duplas de verificación en terreno · la capacidad de hacer público lo que
constate — **y de retirarse de la mesa como señal institucional**.

**Puede hacer:**

- **●** Condicionar su permanencia a que todo escalamiento incorpore reglas
  escritas, identificación de agentes, registro de actuaciones y ruta de atención
  a víctimas
- **●** Asumir el protocolo único de verificación de cifras y denuncias, a cambio
  de acceso a la información de los tres frentes
- **●** Desplegar duplas en los puntos priorizados, para desmentir alertas falsas
  y documentar hechos antes de que se consoliden como versión
- **○** Requerir corredores humanitarios permanentes, exigibles **tanto al Estado
  como a quienes sostienen los cierres**
- **○** Hacer público un pronunciamiento sobre una decisión concreta de la mesa,
  nombrando la decisión y no al funcionario

**Cómo afecta al juego.** Es el mayor multiplicador del ejercicio y el que menos
lo parece: **sus condiciones bajan el riesgo de toda operación posterior sin
consumir un solo escuadrón.** Sus duplas son el único instrumento que puede
distinguir una denuncia falsa de una cierta antes de que el Estado reaccione — y
reaccionar a una falsa consume capacidad y cuesta legitimidad cuando se desmiente.

> **Su dilema:** su presencia legitima lo que allí se decida y su retiro la
> dejaría sin capacidad de influir sobre lo que ocurra después. **Si exige todo
> sin priorizar, la mesa lo aísla y su palanca desaparece** justo cuando se decide
> el escalamiento. Y la utilidad de una alerta se mide por su oportunidad:
> advertir tarde equivale a no advertir.

### 07 · Ministro de Transporte

> **Lo que quiere:** reabrir caminos que solo se abren con una fuerza que no
> controla, mantener a los gremios transportadores fuera del paro, y no exponer a
> conductores civiles a un riesgo que no puede cubrir.

**Controla:** el mapa vivo de cierres y el estado de la red vial · la
interlocución con los gremios de carga · las concesiones, peajes y puestos de
control · la capacidad de organizar caravanas y movilizar conductores · el costo
económico de los cierres por camino y por día.

**Puede hacer:**

- **●** Presentar una priorización de caminos críticos ordenada por población
  afectada, días de autonomía y costo diario, **como criterio único de asignación
  de fuerza**
- **○** Negociar con los gremios camioneros condiciones verificables y
  compensación, para mantenerlos fuera del paro
- **○** Organizar caravanas escoltadas con conductores voluntarios y ventanas
  horarias acordadas
- **○** Instalar una instancia técnica única de priorización, con mapa común
- **○** Anunciar la reapertura de un camino **únicamente como hecho verificado**

**Cómo afecta al juego.** No tiene fuerza propia y **depende por completo de que
otro despeje**: es el rol que más empuja la conversación de vuelta a la mesa. Su
criterio de priorización es lo que convierte una disputa política de asignación
en una secuencia defendible — y al hacerlo, expone a un ministro concreto como el
que decidió qué ciudad se aplaza.

> **Su dilema:** es indiferente al método y exigente con el resultado. Donde hay
> contraparte prefiere lo concertado, porque **un camino pactado se sostiene y uno
> abierto por la fuerza vuelve a cerrarse esa misma noche**. Y no puede presentar
> como normalización una docena de camiones donde antes circulaban miles: se
> desmiente solo.
>
> **Su pregunta estratégica:** *¿con qué criterio se decide cuál camino se abre y
> cuál se aplaza, cuando la capacidad alcanza para uno y el aplazamiento tiene
> nombre de ciudad?*

### 08 · Ministro de Minas y Energía

> **Lo que quiere:** asegurar la continuidad de un sistema del que dependen todos
> los demás frentes, sin absorber la fuerza escasa que se necesita para
> desbloquear y sin convertir sus instalaciones en escenario de enfrentamiento.

**Controla:** los inventarios y días de autonomía por región · la autoridad para
priorizar el combustible entre usos y entre regiones · la interlocución con
refinerías y centros de acopio · la sustentación técnica de qué es infraestructura
crítica · la habilitación de rutas alternas, dentro de límites acotados.

**Puede hacer:**

- **●** Presentar la lista de instalaciones que requieren protección permanente y
  pedir su declaratoria como infraestructura crítica, **con la inmovilización de
  fuerza que ello implica**
- **○** **Asignar el combustible por prioridad de uso** — misión médica, fuerza
  pública, transporte de alimentos, consumo general — con cifra por región
- **○** Acordar con transportadores y centros de acopio pasos seguros y ventanas
  de despacho concertadas
- **●** Entregar a la mesa el calendario de agotamiento **como fecha límite de la
  decisión**
- **○** Sostener con las empresas del sector un acuerdo de continuidad de operación

**Cómo afecta al juego.** Es quien pone el plazo: su calendario convierte la
deliberación en una cuenta atrás y obliga a la mesa a decidir dentro de la ventana
disponible. Pero **entregarlo acelera aquello que mide** —se difunde, hay compra
por pánico, el consumo sube— y le entrega a quienes sostienen los cierres la
medida exacta de su palanca. Y su declaratoria de infraestructura crítica
inmoviliza exactamente la fuerza que Defensa necesita para desbloquear.

> **Su dilema:** en infraestructura energética un incidente no produce un costo
> político sino un **daño irreversible**. No puede pedir protección para todo
> porque inmovilizaría la capacidad de los demás, y no puede desviar combustible
> hacia un uso sin quitárselo a otro que está sentado en la misma mesa.

## 6. Cómo se afectan entre sí

Esta es la parte del diseño que hace que sea un ejercicio de arquitectura de
decisión y no ocho problemas en paralelo. Hay tres formas distintas en que un rol
afecta a otro, y conviene no confundirlas.

### 6.1 Las cadenas de habilitación — *nadie puede solo*

**Trece de las cuarenta acciones no se pueden ejecutar solas.** Cuando falta el
requisito, el sistema no rechaza: devuelve **quién puede habilitarlo**, y eso
empuja la conversación de vuelta a la sala.

**Cadena logística — tres roles antes de que se mueva un camión**

```
Transporte quiere abrir un camino
        ↓ necesita que alguien despeje
   Defensa (operación)  o  Interior/Alcalde (concertación)
        ↓ y necesita que la carga pase con seguridad
   Policía (escolta)  ← sin esto, no hay caravana. Es material, no político
```

**Cadena de la fuerza — la firma cuesta la mesa**

```
Defensa quiere usar capacidad militar
        ↓ necesita el acto administrativo
   Presidente (firma)
        ↓ y la firma, en el mismo turno
   Interior pierde credibilidad del canal que él no movió
```

**Cadena del oxígeno — cinco carteras y ninguna lo resuelve sola**

```
Minas prioriza misión médica → Transporte le da clase humanitaria al camino
  → alguien lo abre → Policía escolta el carrotanque
  → la Defensoría lo exige como derecho → Defensa decide si vale una operación
```

Es la prueba más limpia del segundo hallazgo del caso: **es imposible atender el
oxígeno sin coordinar cuatro carteras**, y por eso está en el diseño.

**Cadena del estándar — el que no manda a nadie**

```
La Defensoría no ordena nada
        ↓ pero si la mesa acepta sus condiciones
   TODA operación posterior, de cualquier rol, es varias veces menos peligrosa
```

### 6.2 Los circuitos que se realimentan — *lo que vuelve*

**El circuito de la fuerza.** Es el que define el caso:

```
        operación de fuerza
                ↓
      probabilidad de incidente
                ↓
           imagen viral
                ↓
        la movilización sube
                ↓
   aparecen cierres nuevos en otras ciudades
                ↓
         hace falta más fuerza
                ↓
    pero la fuerza disponible es la misma
```

> **Abrir un camino por la fuerza puede cerrar dos.** Y eso no está escrito en
> ningún guion: sale de la aritmética, lo que significa que la sala no puede
> discutirlo — solo verlo ocurrir.

**El circuito del hambre.** Corre en paralelo y en dirección contraria: el cierre
sostenido produce escasez, la escasez baja el respaldo del barrio al cierre, y el
cierre acaba deshaciéndose solo. Es lento, es gratis, y **mientras tanto hay un
contador de muertes corriendo**. Por eso dejar correr la escasez es una tentación
real y un error.

> Estas dos no son la misma variable con signo cambiado: **la intensidad sube con
> el uso de la fuerza —es rabia contra el Estado— y el apoyo al cierre baja con la
> escasez —la gente quiere comer.** Modelarlas por separado es lo que le da
> contenido al esquema humanitario del Alcalde.

**El circuito del reloj.** Minas entrega el calendario de agotamiento; la mesa por
fin sabe cuánto le queda y decide con plazo. Pero el calendario se difunde, hay
compra por pánico, el consumo se acelera y el agotamiento llega antes.
**Entregar el reloj cambia el reloj.**

### 6.3 Las sumas cero — *lo que uno gana, otro lo pierde*

Cuatro, y las cuatro enfrentan a dos roles concretos sentados en la misma mesa.

| Recurso | Quién tira de un lado | Quién tira del otro |
|---|---|---|
| **Escuadrones** | Minas: proteger instalaciones donde un incidente sería irreversible | Defensa: desbloquear caminos |
| **Caminos** | Transporte: el criterio técnico | Alcalde: la exigencia política de su ciudad |
| **Duplas de verificación** | Verificar este punto | No verificar aquel |
| **Combustible** | Misión médica y fuerza pública | Transporte de alimentos y consumo general |

**No hay orden correcto.** Hay un orden que alguien tiene que defender ante siete
personas que pierden algo — y eso es lo que se está entrenando.

### 6.4 El mapa completo, en una tabla

Quién habilita y quién restringe a quién. Los marcados **Alta** son los que sin
ellos el caso no funciona.

| Origen | Al hacer… | Afecta a | Cómo | |
|---|---|---|---|---|
| Presidente | firmar la asistencia | Defensa | **habilita** capacidad militar y libera policías de custodia | Alta |
| Presidente | firmar la asistencia | Interior | **restringe**: endurece a la contraparte en la misma jornada | Alta |
| Presidente | fijar líneas rojas | Interior | **restringe**: sin margen, todo acuerdo es capitulación | Alta |
| Interior | abrir mesas locales | Transporte | **habilita** aperturas que se sostienen sin consumir fuerza | Alta |
| Interior | plazo suspensivo | Defensa | **restringe**: difiere operaciones que el terreno exige | Alta |
| Alcalde | mesa local | Policía | **habilita**: libera ESMAD del camino pactado | Alta |
| Alcalde | condicionar respaldo | Defensa | **restringe**: encarece operar sin concertar | Alta |
| Defensa | redesplegar militares | Policía | **habilita** concentrar ESMAD; abre un frente rural | Alta |
| Defensa | operación de desbloqueo | Interior | **restringe**: cada víctima consume la legitimidad de la mesa | Alta |
| Policía | concentrar ESMAD | Alcalde | **restringe**: el repliegue se lee como abandono territorial | Alta |
| Policía | escoltar | Transporte y Minas | **habilita**: condición material de toda la logística | Alta |
| Policía | pedir relevo | Defensa | **restringe**: menos cobertura adelanta el escalamiento | Media |
| Defensoría | condicionar el escalamiento | Presidente | **restringe**: eleva el requisito formal de la firma | Alta |
| Defensoría | duplas en terreno | *todos* | **habilita**: desmiente alertas falsas antes de que consuman fuerza | Alta |
| Defensoría | corredores humanitarios | Policía | **restringe**: obliga a garantizar paso sin operación autorizada | Alta |
| Transporte | priorización | Defensa | **habilita** un criterio defendible frente a la presión política | Alta |
| Transporte | priorización | Alcalde | **restringe**: todo orden aplaza, y el aplazado tiene nombre | Alta |
| Minas | infraestructura crítica | Defensa | **restringe**: inmoviliza la fuerza del desbloqueo | Alta |
| Minas | asignar combustible | Transporte | **restringe**: suma cero, cada uso se le quita a otro | Alta |
| Minas | calendario de agotamiento | **todos** | **restringe**: convierte el tiempo en variable dura | Alta |

## 7. Los seis dilemas que el diseño garantiza

Un dilema que depende de que los participantes lo descubran no es un dilema del
diseño: es suerte. **Estos seis tienen que aparecer en toda corrida.**

**D1 · La fuerza que abre un camino le resta credibilidad a la mesa que negocia
el siguiente.** El Ministro del Interior ve caer su reserva por decisiones que no
tomó.

**D2 · Cada camino priorizado es un camino aplazado, y el aplazamiento tiene
nombre de ciudad.** El criterio técnico de Transporte y la exigencia política del
Alcalde no pueden satisfacerse a la vez.

**D3 · La verdad es un recurso escaso, y las duplas que la producen son tres por
turno.** Verificar aquí es no verificar allá, y el error tiene dos direcciones,
ambas caras.

**D4 · El estándar de derechos es la única palanca que baja el riesgo sin
consumir capacidad.** Es el dilema *positivo*: el rol sin voto y sin fuerza es el
que más reduce la probabilidad del peor resultado.

**D5 · Entregar el reloj cambia el reloj.** El calendario de Minas es a la vez el
instrumento que obliga a la mesa a decidir y el que acelera aquello que mide.

**D6 · Concentrar hace responsable de cada error; delegar deja sin control sobre
la coherencia.** Sin decisión escrita con responsable nominado, el costo de cada
incidente se reparte sobre los ocho y erosiona la cohesión.

> **La forma general del caso:** las ocho posiciones son defendibles y ninguna es
> suficiente. **Si en el debriefing una opción resulta haber sido obviamente
> correcta desde el turno 1, el ejercicio está mal calibrado.**

---
---

# PARTE III · El motor

Las dos partes anteriores describen el ejercicio que el caso propone. Esta
contrasta cada compromiso de ese diseño con lo que el código sostiene hoy.

## 8. Qué promete el diseño y qué entrega el motor

| Compromiso del diseño | Cómo lo resuelve el motor | ¿Se cumple? |
|---|---|---|
| La movilización reacciona a lo que la sala decide | Un subsistema propio: los incidentes suben la intensidad, la intensidad endurece los puntos, engorda las multitudes y genera cierres nuevos | **Sí** |
| Tres vías de abrir, con economías distintas | Las tres implementadas, con sus tiempos y sus reaperturas | **Sí** |
| Un camino vale lo que su peor punto | El caudal del corredor es el mínimo de sus puntos | **Sí** |
| La fuerza casi nunca alcanza a sostener un corredor en cinco turnos | Sale de la aritmética, no de una regla | **Sí** |
| El estándar de derechos divide el riesgo por casi cinco | Seis multiplicadores, con saturación que no rescata a quien opera mal | **Sí** |
| El riesgo se muestra **antes** de decidir, como banda | Se calcula y se devuelve para que el moderador lo lea | **Sí** |
| Constituirse no está bloqueado: está tarifado | Las seis banderas y sus peajes por turno | **Sí** |
| El costo cae sobre quien firmó, o sobre los ocho | Depende de si hay responsable nominado y registro escrito | **Sí** |
| La corrida se repite en el debriefing con una decisión cambiada | Semilla fija registrada | **Parcial** — no se guarda a disco |
| El oxígeno convierte logística en muertes | Cadena completa: combustible → plantas → oxígeno → contador | **Sí, pero con una sola entrada** |
| Toda región tiene una vía viable de atender el oxígeno | Se verifica al cargar y falla ruidosamente | **Sí** |
| Nadie ve la composición real de un punto | Nunca sale del motor; dos pruebas lo verifican | **Sí — pero tampoco hace nada** |
| Cuatro fuentes estiman con sesgos opuestos | Los cuatro sesgos están calibrados | **No** — solo se produce una |
| La cohesión mide si la mesa se rompió | Solo tiene términos negativos | **No** — es la misma recta siempre |
| Interior puede producir un acuerdo verificable | — | **No** — no tiene con qué |
| La Policía asigna el ESMAD y escolta caravanas | — | **No** |
| Minas asigna el combustible en suma cero | La función existe, sin acción que la invoque | **No** |
| El turno 1 abre con cuatro hechos que no caben | Uno de los cuatro | **No** |
| El encuadre público cambia lo que cuesta cada hecho | Se calcula y se muestra | **No** — nada lo consulta |

**El balance.** Lo que está construido está bien construido: **el corazón del
caso —las tres vías, el bucle reflexivo, el estándar como multiplicador— funciona
y está probado.** Lo que falta se concentra en dos sitios, y no es casual: el
**polo de negociación** y el **frente de logística**.

## 9. Dónde la traducción está incompleta

Siete diagnósticos, ordenados por lo que le cuestan al objetivo didáctico.
Descritos por lo que se ve en la sala, no por lo que se lee en el código.

### 9.1 · El ministro del diálogo no puede dialogar

De las cinco acciones del Ministro del Interior está implementada una, y es la
que sirve para **decir que no**: exigir que le avisen antes de operar.

En la sala se ve así. Un participante declara en el turno 0 que su línea es la
negociación —que es lo que su ficha le pide—, pasa cinco turnos defendiéndola, y
descubre hacia el turno 2 que no tiene una sola forma de traer un resultado. No
puede convocar la mesa nacional, no puede abrir mesas locales, no puede ofrecer
una contraprestación legislativa. **Su papel se reduce a estorbar operaciones
ajenas.**

Y hay una consecuencia sobre el sistema entero: **el movimiento que más desinfla
la movilización en todo el diseño es un acuerdo verificable cumplido, y hoy es
inalcanzable.** El caso queda con un solo polo activo — la fuerza —, que es
exactamente lo que la Matriz advirtió al justificar por qué este rol no se podía
eliminar.

Hay además un desplazamiento que conviene corregir aparte: **la única vía de
concertación implementada está en la ficha del Alcalde de Cali, y no comprueba
jurisdicción.** Un alcalde municipal pacta cierres en Cauca y Nariño. La
competencia que la Matriz asigna a Interior —mesas locales camino por camino—
vive hoy bajo otro nombre y sin límite territorial.

**Severidad: crítica.** Es el diagnóstico que más barato sale de arreglar y más
cambia el ejercicio.

### 9.2 · El dueño del ESMAD no puede asignar el ESMAD

El Director de la Policía es, según el Manual, el titular del *«único instrumento
entrenado para control de multitudes»* y del activo más escaso del ejercicio. De
sus cinco acciones está implementada una: pedir relevo.

**No puede concentrar sus escuadrones ni puede escoltar.** Los escuadrones se
mueven solos cuando alguien ordena una operación.

Eso apaga dos cosas que la Matriz clasifica como imprescindibles. La primera es
un conflicto: concentrar en un punto crítico significa replegar en otro, y el
alcalde que pierde su punto lo lee como abandono — es una de las discusiones más
vivas que el caso puede producir, y hoy no puede ocurrir. La segunda es peor
porque es material: **sin escolta no hay caravana ni carrotanque**, así que todo
el frente de logística queda sin condición de posibilidad. Es la causa directa
del diagnóstico siguiente.

Hay un detalle que además invierte el sentido de un rol: el registro audiovisual
de las operaciones —que es un recurso propio del Director de la Policía, y el que
más reduce la probabilidad de que una imagen circule— **hoy lo enciende la
Defensoría**.

**Severidad: crítica.**

### 9.3 · El frente de logística no tiene con qué mover carga

Transporte y Minas suman tres acciones entre los dos y **ninguna mueve un camión**.

Transporte puede presentar su criterio de priorización, que es un acto de mesa, y
nada más: no puede organizar caravanas, no puede negociar con los gremios, no
puede anunciar una reapertura como hecho verificado. Su pregunta estratégica es de
las mejores del caso y **no puede ejecutar ninguna consecuencia de la respuesta**.

Minas está peor de lo que parece: de sus dos acciones, una inmoviliza fuerza y la
otra acelera el consumo. **Las dos empeoran la situación de alguien.** El rol que
trae el reloj a la mesa no tiene ninguna forma de mejorarlo, porque la acción que
la tendría —asignar el combustible por prioridad de uso, la suma cero que enfrenta
a cuatro roles— no está disponible para él, aunque la mecánica ya esté escrita.

**Y eso explica un problema de calibración que ya estaba medido:** las muertes por
falta de oxígeno son idénticas en cuatro de las cinco estrategias de prueba. No es
que el reloj esté mal calibrado. Es que **solo tiene una entrada**: abrir un camino
humanitario. La segunda vía prevista en el diseño no está conectada a ningún rol.

**Severidad: alta.**

### 9.4 · La composición real de los puntos no cambia nada

Es la decisión de diseño número uno del caso: cada punto de cierre tiene una
mezcla real de protesta legítima, vandalismo y estructura organizada que nadie ve,
y sobre la que hay que decidir con estimaciones sesgadas. De ahí sale el error
doble, el oficio de la Defensoría y la casilla Seguridad × Información entera.

**Hoy esa composición no tiene ninguna consecuencia.** Está celosamente
protegida —no sale del motor, hay dos pruebas que lo verifican— y no entra en
ningún cálculo: ni en el riesgo de operar, ni en si el acuerdo se sostiene, ni en
el costo de equivocarse.

Se puede comprobar: **si se convierten los veinticuatro puntos en estructura
organizada pura y se corre el ejercicio, todos los resultados son idénticos.** Un
punto que es 100 % protesta legítima y uno que es 100 % estructura organizada
producen exactamente lo mismo.

Y va con un segundo hueco: de las cuatro fuentes de estimación **solo se produce
la de la Defensoría**. Los sesgos opuestos de la inteligencia de Defensa y del
parte municipal —que son los que hacen que dos roles miren el mismo punto y vean
cosas distintas— están calibrados y nunca se generan. En la sala eso significa que
**no hay cifras en conflicto**: la esfera pública muestra números que divergen por
aritmética, no porque dos instituciones estén viendo el país de forma distinta.

**Severidad: crítica**, porque es lo que sostiene la mitad del valor pedagógico
del caso — pero ver [P1](#p1--la-composición-real-tiene-consecuencias-o-se-elimina),
porque tiene dos salidas honestas y una es eliminarla.

### 9.5 · La cohesión de la mesa no mide nada

Está diagnosticado como un problema de calibración: la cohesión se hunde a cero y
deja de discriminar. No lo es. Son tres cosas de diseño:

**No hay forma de reponerla.** El Manual dice que se recupera con decisiones
escritas con responsable nominado y con el protocolo de vocería respetado. En el
motor, adoptar esas cosas solo **deja de cobrar el peaje** — nunca devuelve nada.
La variable solo puede bajar.

**El peaje se cobra también cuando la sala no está decidiendo:** en los cuatro
interludios nocturnos, donde por diseño no se delibera ni se ordena, y en los tres
turnos de la proyección final, donde ya no hay nadie al mando. Un ejercicio de
cinco decisiones paga doce peajes.

**Y el evento que debería hundirla por una decisión concreta** —una operación que
la mesa no conocía— nunca se dispara.

El resultado es que la serie de cohesión es **la misma recta descendente en toda
corrida**, independientemente de lo que la sala haga. En el debriefing es una de
las tres lecturas y la única de la que los ocho no pueden desentenderse; hoy no
les dice nada.

**Severidad: alta.**

### 9.6 · El turno 1 no abre con el paquete detonante

El diseño dedica una sección entera a los cuatro hechos que llegan juntos en las
primeras doce horas y que **no caben en la capacidad disponible**, para que la sala
descubra la escasez en su primer minuto y no en el cuarto turno. Está implementado
uno de los cuatro.

| | El hecho | Estado |
|---|---|---|
| **H1** | Incidente nocturno junto a una instalación de combustible, con un herido grave de la fuerza pública | falta |
| **H2** | **Dos denuncias graves sin verificar: una falsa y otra cierta, y nada las distingue** | falta |
| **H3** | Ultimátum de los gremios camioneros: 48 horas o evalúan sumarse | falta |
| **H4** | Una región cruza por debajo de dos días de oxígeno | **existe** |

Falta también la jornada nacional de movilización programada para el turno 3, que
es un empujón exógeno que el calendario debía traer.

**H2 merece atención aparte porque es una decisión ética, no técnica.** La regla
que el diseño subraya es: *nunca una sola denuncia sin verificar; siempre al menos
dos, con veracidad distinta y sin ninguna señal que las distinga*. Un ejercicio
sobre el paro de 2021 en el que la única denuncia grave resulta inventada le
enseña a ocho futuros funcionarios que las denuncias graves suelen ser inventadas
— y eso, sobre hechos con responsabilidad judicial viva, es tomar partido. La
lección correcta no es «desconfíe» sino **«usted no puede saberlo sin verificar, y
verificar cuesta una dupla que no tiene»**.

Sin H2, las duplas de la Defensoría verifican puntos que no tenían nada que
verificar, y la mejor conducta posible del caso —verificar una y declarar
públicamente que la otra está en verificación— no existe.

**Severidad: alta.**

### 9.7 · El eje de Vocería no tiene mecánica

De las nueve casillas de la matriz del Manual, la columna de **Mando** está bien
cubierta y la de **Información** está diseñada pero desconectada. La de **Vocería**
no tiene soporte:

- El encuadre público —si lo que domina es «represión», «desorden»,
  «negociación» o «abandono»— se calcula y se proyecta, pero **no cambia lo que
  cuesta cada hecho**. La idea de que el mismo hecho se paga distinto según el
  encuadre vigente, y de que el encuadre se puede disputar con vocería, no está.
- Que los gremios se sumen al paro **no produce ningún efecto**. El paro logístico
  nacional es hoy una etiqueta en el tablero.
- Anunciar un camino como abierto cuando apenas pasa un hilo de tráfico —la
  mecánica de *«una docena de camiones presentada como normalización se desmiente
  sola»*— no es posible.

**Severidad: media**, y con una salida distinta de las anteriores: buena parte de
esto es trabajo de los agentes de entorno, que ya está en la lista de pendientes.

## 10. Las cuatro decisiones abiertas

De los siete diagnósticos salen cuatro decisiones **de diseño, no de código**.
Ninguna es técnica y ninguna es mía. Van con recomendación porque tener una es más
útil que no tenerla.

### P1 · ¿La composición real tiene consecuencias, o se elimina?

Dos salidas honestas, y son muy distintas.

**Conectarla.** Que operar sobre un punto que es sobre todo protesta legítima
cueste mucho más en legitimidad y exposición, y que pactar con un punto donde hay
estructura organizada produzca un acuerdo que se incumple visiblemente. Con eso el
error doble se vuelve real, las cuatro fuentes con sesgo tienen razón de ser, y la
Defensoría pasa a administrar el recurso más valioso del ejercicio.

**Eliminarla.** Aceptar que con cinco turnos no da tiempo a construir una
hipótesis sobre veinticuatro puntos, y quedarse con una sola incertidumbre: cuánto
controla realmente cada vocero. Esa ya produce un dilema, ya está sesgada por
fuente y ya funciona.

> **Recomendación:** conectarla, pero solo por esas dos vías. Nada más. Es la
> decisión de diseño número uno del caso y hoy es la única que no toca el motor.
> Si se decide eliminarla, hay que decirlo explícitamente y quitar las pruebas que
> la protegen, porque hoy dan la impresión de que sostiene algo.

### P2 · ¿Cuántas acciones por rol, y repartidas cómo?

Hoy hay 14 de las 40, repartidas 3·3·2·2·1·1·1·1. Las 40 no caben en cinco turnos
y no hacen falta. **El problema no es el número: es que dos roles no tienen
ninguna acción que toque el mundo**, y son precisamente el polo de negociación y
el titular de la priorización.

> **Recomendación:** subir a unas 24, con **piso de dos por rol y al menos una que
> toque el mundo para cada uno**. Las siete que más rinden, por orden:
>
> 1. **Interior · sesión de la mesa nacional** — devuelve el segundo polo al caso
> 2. **Policía · escolta** — condición material de todo el frente logístico
> 3. **Minas · asignar combustible** — da al reloj su segunda entrada
> 4. **Policía · concentrar ESMAD** — devuelve la asignación a quien manda
> 5. **Transporte · caravanas escoltadas** — le da un acto operativo
> 6. **Defensoría · corredores humanitarios permanentes**
> 7. **Defensa · presentar la evidencia de inteligencia** — activa la fuente sesgada

### P3 · ¿La cohesión mide la constitución de la mesa, o su desgaste?

El propio diseño se anticipó a esto: *«aceptar que un ejercicio de dos horas mide
la constitución de la mesa y no su desgaste, que también es un objeto legítimo»*.
La decisión cambia el arreglo entero.

- Si mide **constitución**, basta con dejar de cobrar el peaje cuando la sala no
  está decidiendo. La serie pasa a leerse como *cuándo* se constituyó la mesa, que
  es exactamente el segundo hallazgo del caso.
- Si mide **desgaste**, hace falta poder reponerla, y hacen falta los eventos que
  la hunden por una decisión concreta: la operación no informada, la
  desautorización pública, las vocerías contradictorias.

> **Recomendación:** constitución, para la primera corrida. Es el arreglo más
> barato, es coherente con lo que el caso quiere enseñar, y no exige inventar
> eventos que los agentes de entorno todavía no pueden producir.

### P4 · ¿El paquete detonante lo resuelve el sistema o lo inyecta el moderador?

Los cuatro hechos podrían vivir como eventos de guion que la consola inyecta en el
turno 1, sin tocar el motor. Es más rápido y es defendible para dos de ellos.

Pero **H2 necesita que el sistema sepa cuál de las dos denuncias es cierta**, para
poder resolver la verificación cuando la Defensoría gaste una dupla en ella. Y
**H3 necesita un disparador de gremios independiente del deterioro de la
legitimidad**: que un gremio concreto pida algo concreto con plazo es una cosa
distinta de que el país deje de respaldar al Gobierno, y las dos tienen que
coexistir.

> **Recomendación:** H2 y H3 al motor; H1 y H4 por guion. Y conviene decidir ya si
> el paquete es fijo o se sortea —punto **A5** de [`PENDIENTES.md`](../../PENDIENTES.md)—,
> porque cambia dónde vive el dato.

---

## Una nota sobre la calibración

**Ningún coeficiente de este ejercicio está medido.** Son convenciones
declaradas, elegidas para que ninguna estrategia pura gane. El criterio es **por
comportamiento y no por realismo**: no hay respuesta empírica a cuánta legitimidad
cuesta un muerto, y no la va a haber.

Varios de los problemas de calibración que ya estaban medidos —las muertes
idénticas, la cohesión saturada— **no son problemas de coeficientes**, como se ve
en 9.3 y 9.5. Conviene arreglar el diseño antes de tocar los números, o se
calibrará contra un sistema al que le faltan piezas.

> **La primera corrida con personas es una medición, no un ejercicio**, y conviene
> decirlo antes de empezar.

---

*Fuentes: Manual de Roles con RADs (8 roles) y Matriz Operativa (8 roles) del
GovLab · la [propuesta de simulación](propuesta_inicial.md) ·
el motor en el commit `510d903`. Las afirmaciones de 9.4 y 9.5 se comprobaron
ejecutando el motor, no leyéndolo.*

*Escuela de Gobierno · Universidad de La Sabana.*
