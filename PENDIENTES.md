# Pendientes

Lo que falta para correr esto con siete personas en una sala. **Este es el único
sitio donde se lleva la cuenta**: si algo está pendiente y no está aquí, es que
se me pasó.

La división que manda es una sola, porque es la que decide qué se puede hacer el
lunes por la mañana:

| Parte | Qué es | Quién |
|---|---|---|
| **[1 · Sin convocar a nadie](#parte-1--sin-convocar-a-nadie)** | código y verificación · se puede hacer hoy | yo |
| **[2 · Con personas en una sala](#parte-2--con-personas-en-una-sala)** | lo que **ninguna prueba de código sustituye** | el equipo, con gente |
| **[3 · Decisiones que no son mías](#parte-3--decisiones-que-no-son-mías)** | no son técnicas | el equipo docente |

> **Los identificadores no cambian aunque el documento se reordene.** Están
> citados desde el código (`PENDIENTE(B1)`), desde `CONTEXTO.md` y desde
> aquí mismo. Renumerarlos por estética rompería la navegación en los dos
> sentidos que este documento promete — y ya se rompió una vez.

---

## En una mirada

| | Pendiente | ¿Necesita gente? | Estado |
|---|---|---|---|
| **B1** | el archivo de la corrida — persistencia y telemetría | no | **no existe** · bloquea B7 |
| **B2** | la identidad de los siete roles, en datos | no | `data/roles/` vacío · hoy duplicada en el frontend · **ahora son nueve** |
| **B7** | el debriefing, la superficie que falta | no | **no existe** · depende de B1 |
| **B5** | presupuesto de latencia medido | el reloj de la fase, en P2 | **medido** · el timeout ya es duro y las dos capas caben dentro |
| **B6** | el guion de la sesión | no | fuera del código |
| **P1** | correr el motor solo y leer la traza | **no** — una persona, 20 min | listo para correr |
| **P2** | las pantallas | **sí** — dos personas, 30 min | listo |
| **P3** | en seco, tres roles | **sí** — tres personas, 45 min | listo |
| **P4** | la corrida completa | **sí** — nueve personas, 2 h | listo |
| **B3** | decisiones alineadas con información privada | no | derivado del motor · sale en B1, se lee en B7 |
| **C1–C5** | cinco calibraciones | **sí** | esperando P3/P4 · **C5 es nueva y bloquea la tabla** |
| **A1** | cuántos dispositivos, o papel | — | esperando |
| **A2** | quién opera la consola | — | esperando |
| **A3** | ¿con llave o sin llave la primera vez? | — | esperando |
| **A4** | el contenido exacto de las siete vistas | se decide probando | esperando |
| **A5** | cerrar el territorio ficticio | — | nombres provisionales puestos |
| **A6** | ¿el mapa muestra dónde está la fuerza? | se decide tras P3 | esperando |
| **B8** | órdenes condicionales en el canal | no | el motor sabe; el canal no lee «si…» · hoy se avisa |
| **A7** | ¿la consola puede decir qué punto bloquea un corredor? | — | esperando · es el dato exclusivo de Transporte |
| **B9** | **ninguna prueba mira lo que la interfaz dibuja** | no | **no existe** · un fallo de una línea vació las siete vistas y la suite pasó entera |
| **B11** | la lista agroalimentaria no se comprueba después | no | se concede la clase y nadie mira si se cumplió |
| **B12** | tres constantes y tres campos que nadie lee | no | **cerrado por la simplificación del motor (S1–S11, ya aplicadas)** · retirados; quedó una huérfana declarada |
| **B13** | dos números del reparto de carteras sin calibrar | no | provisionales y declarados · van con **C5** |
| **B14** | **la lectura de la corrida — el cómo y el qué** | no | **propuesta escrita**, sin implementar · depende de **B1**, se presenta en **B7** |

Lo que **sí** funciona está en el README, sección «Estado actual»; y dónde
mirar según la pregunta —el mapa del código y las claves del motor—, en
[`CONTEXTO.md`](CONTEXTO.md), que es el punto de entrada del repositorio.

---

## Cómo verlos desde el código

```bash
grep -rn "PENDIENTE" src/
```

Cada marca lleva el identificador de esta lista (`PENDIENTE(B1)`), así que se
puede ir en las dos direcciones: del código a la explicación y de la explicación
al código. Una marca sin entrada es un error y se detecta sola.

---
---

# PARTE 1 · Sin convocar a nadie

Todo esto se puede hacer hoy, solo, sin reservar una sala. **Nada de ello depende
de ninguna decisión pendiente.**

## La verificación que corre hoy

### P1 · El motor, solo — 20 min, una persona

**¿El motor produce dilemas o produce un guion?**

```bash
# La tabla: seis salas ficticias, mismo escenario, seis formas de jugar
uv run python scripts/correr_ejercicio.py --comparar

# Y la cadena causal: qué se ordenó cada turno y por qué salió así
uv run python scripts/correr_ejercicio.py --comparar --detalle

# Con otras semillas, para separar el ruido de la señal
uv run python scripts/correr_ejercicio.py --semilla 7 --comparar
uv run python scripts/correr_ejercicio.py --semilla 99 --comparar
```

Mirar que **ninguna estrategia domine con las tres semillas**. Si `solo_fuerza`
gana alguna vez, hay que recalibrar antes de convocar a nadie.

**`--detalle` es lo que hace la prueba útil para calibrar**, porque un número sin
su cadena causal no dice qué tocar. Por cada estrategia imprime las órdenes de
los cinco turnos con su consecuencia, y después un diagnóstico leído de la
corrida: **en qué región murió cada quien y si esa región llegó a tener alguna
vez un camino humanitario abierto que la sirviera** — que es la diferencia entre
«la sala no pudo» y «la sala no lo atendió», dos conversaciones muy distintas en
el debriefing.

**Lo que debe cambiar con la semilla y lo que no.** Cambian `netas`, `reap` y las
reservas: son las tiradas. **No cambian `cohes` ni `muert`**, porque la cohesión
depende de qué banderas se adoptaron y el reloj de qué corredores se abrieron —
no del azar. Si algún día empezaran a bailar, algo se rompió.


---

## El código que falta

### B1 · El archivo de la corrida — persistencia y telemetría, un solo archivo

**Dónde:** `src/engine/bitacora.py` (por escribir) ·
[`simulation.py`](src/engine/simulation.py) lleva la marca `PENDIENTE(B1)`

**Estaban separados y por eso no se movió ninguno.** B1 quería que la corrida
sobreviviera al proceso; B3 quería poder medirla. Son **el mismo artefacto visto
desde dos lados**, y escribirlo dos veces garantiza que se desincronicen.

Un archivo por corrida, **JSONL y solo de anexado**:

```
corridas/2026-08-26-1430/corrida.jsonl
```

```jsonc
{"t":"apertura",  "semilla":20210511, "reloj":{...}, "indicadores":{...}}
{"t":"linea",     "rol":"Defensa", "linea":"..."}          // turno 0
{"t":"orden",     "ventana":3, "dictado":"...", "interpretado_por":"...", "acciones":[...]}
{"t":"decision",  "ventana":3, "rol":"...", "accion":"...", "responsable":"..."}
{"t":"ventana",   "n":3, "franja":"dia", "indicadores":{...}, "deltas":{...}, "eventos":[...]}
{"t":"cierre",    "metricas":{...}, "proyeccion":{...}}
```

**Por qué de anexado y no un volcado al final.** Si el proceso se cae a mitad del
ejercicio, sobrevive todo lo anterior. Un volcado final lo pierde todo — y una
caída durante la corrida es exactamente cuando más falta hace el registro.

**Lo que esto habilita, y que hoy es imposible:**

| | Cómo |
|---|---|
| Debriefing con el proceso cerrado | se lee el archivo, no la memoria |
| **Repetir la corrida cambiando una decisión** | el motor es determinista dada la semilla: se reproducen las órdenes del archivo con una editada, y todo lo demás sale igual |
| Comparar dos salas con el mismo escenario | dos archivos, mismas claves |
| Medir dónde se fue el tiempo | cada línea lleva su marca temporal |

> **Ojo, y es la trampa de la simulación anterior:** que el código anote el dato
> no basta. Hay que comprobar que **llega al archivo**. Allí dos campos se
> perdían en la serialización y ninguna prueba lo detectó, porque las pruebas
> miraban el código y no el archivo de salida. La prueba tiene que leer el
> `.jsonl` escrito.

**Nota de alcance:** esto permite **volver a contar** la corrida, no
*reanudarla*. Reanudar exigiría serializar el estado entero. Y no hace falta: con
la semilla y las órdenes, reproducirla es exacto.


### B2 · La identidad de los siete roles, en datos

**Dónde:** [`data/roles/`](data/roles/) (vacío) ·
[`web_ui/src/comun.jsx`](web_ui/src/comun.jsx) tiene hoy la lista duplicada

**Esta entrada era más grande de lo que debía.** Decía «las nueve fichas de rol,
en datos», y eso no hace falta: las fichas del *Manual de Roles con RADs* son un
entregable del GovLab, se entregan **impresas** por decisión de diseño
(`propuesta.md` §6, regla 4: *papel para lo que no cambia*), y **nadie calcula
con su texto biográfico**. Meterlo en el motor sería duplicar el documento del
GovLab dentro del repositorio, con el problema de sincronización que eso trae.

Lo que sí falta es pequeño y sí es necesario:

| | Qué | Por qué |
|---|---|---|
| **1** | `id`, título completo y frente de cada rol | hoy viven **solo** en `comun.jsx`, o sea duplicados fuera del motor. `views.py` tiene los `id` y no los títulos |
| **2** | el nombre ficticio que aparece en la ficha impresa | tiene que coincidir con el de las pantallas, o la sala ve dos mundos (**A5**) |
| **3** | un puntero al apartado de la ficha del GovLab | para ir del rol al documento sin buscarlo |

La **agenda reservada** (apartado 11 del Manual) tampoco entra, y por una razón
más simple de la que yo le atribuía: **es contexto fijo del rol, no una pieza
secreta del juego.** Describe desde dónde llega cada uno a la mesa. El motor no
la lee, no la puntúa y no la necesita — vive en la ficha del GovLab y ahí se
queda.

Depende de **A5** (nombres).


### B7 · El debriefing — la superficie que falta

**Dónde:** `/debriefing` en [`App.jsx`](web_ui/src/App.jsx) y
`GET /api/debriefing` · **depende de B1**

Veinte minutos, más que cualquier turno, y hoy no hay nada que proyectar. El
motor ya tiene los datos; lo que falta es **el relato**.

**El criterio: hechos y contraste, no un volcado de variables.** Nadie aprende
mirando veinte números. Se aprende viendo qué se decidió y qué pasó después.

Cinco paneles, en el orden en que se conduce un debriefing:

**1 · El país que se recibió y el que se entrega.** Seis magnitudes, lado a lado,
apertura contra cierre, más la proyección a 72 horas. No las veinte: las seis que
significan algo.

**2 · La línea declarada contra la ejecutada.** Por cada rol, lo que dijo en el
turno 0 y lo que el pliego dice que hizo. Los datos ya existen
(`lineas_declaradas` + `registro` filtrado por rol). **Es el panel más cargado
del ejercicio** y ya está nombrado como una de las tres lecturas del debriefing.

**3 · Las decisiones y la ventana en que cayeron.** El pliego completo, y al lado
lo que se movió en esa ventana.

> **El motor no atribuye una consecuencia a una decisión, y no va a hacerlo.**
> Varias caen en la misma ventana y el mundo además se mueve solo. Se muestra
> *«en la ventana en que se ordenó esto, la legitimidad bajó 9»* y se dice que
> es lo que es.

**Llegó a estar en el plan hacer que el motor rastreara el porqué** —un `motivo`
en cada cargo a las reservas, un libro de cargos— para poder afirmar *«esta
operación costó 9 por incidente con víctima»*. **Se descartó por decisión del
equipo docente, y con razón:** el porqué de una decisión es material de
conversación, no de instrumentación. Lo interesante en la sala no es que la
pantalla diga qué causó qué, sino que nueve personas lo discutan mirando el
pliego. Aparejar el motor para eso habría sido complicarlo para sustituir la
parte que no conviene sustituir.

**4 · Los tres momentos.** El turno en que la mesa dejó de ser una mesa
(credibilidad bajo 30), el turno del primer registro escrito, y el turno en que
una región cruzó el reloj de oxígeno. Los cruces de umbral ya se calculan en
`umbrales_cruzados`.

> **Lo que NO va en el debriefing: las agendas reservadas.** Son contexto fijo
> del rol —de dónde viene cada uno—, no una jugada oculta que haya que destapar
> al final. Revelarlas como cierre las convertiría en un marcador encubierto, que
> es justo lo que este ejercicio no tiene.


### B3 · Que la información se comparta, evidenciado en las decisiones

**Dónde:** [`simulation.py`](src/engine/simulation.py) · sale en el archivo de
**B1** y se lee en **B7**

**Esta entrada estaba mal planteada y la corrección viene del equipo docente.**
Yo proponía una hoja de observación: alguien con un papel anotando quién habló
primero de su vista privada. Dos problemas:

| | |
|---|---|
| **Convierte la conversación en un marcador** | anotar quién compartió invita a compartir para que quede anotado, que no es lo que se quiere medir |
| **Necesita un observador dedicado** | y con nueve participantes ya hay alguien en la consola |

**Compartir información no se anota: se evidencia en lo que la sala decide.** Si
la asimetría funciona, se nota en que el Puesto de Mando prioriza donde solo un
rol sabía que había que priorizar. Y eso el motor **sí** lo puede calcular,
porque conoce las dos mitades: el dato privado y la decisión.

**Decisiones alineadas con información que solo tenía un rol.** Para cada
decisión del pliego, el motor comprueba si aprovecha algo que no estaba en el
tablero:

| Decisión | El dato privado que la respalda | De quién |
|---|---|---|
| Prioridad de combustible a una región | ¿es la del reloj de oxígeno más corto? El tablero solo da el semáforo | **Transporte + Agricultura** |
| Verificar un punto y no otro | ¿es el que bloquea un corredor? | **Transporte** |
| Escoltar por un corredor | ¿sirve a la región peor abastecida? | **Agricultura + Transporte** |
| Verificar una denuncia contra la fuerza | solo cuenta con protocolo común adoptado | **Policía + Defensa** |
| Concertar en vez de operar | ¿tiene el punto vocería con quién hablar? | **Interior + Alcalde** |

Cada una da *alineada · no alineada · no aplica*. El agregado —«N de M
decisiones aprovecharon información que solo tenía un rol»— es la medida de si
la asimetría produjo conversación.

> **Con la cautela dicha en voz alta:** con cuatro regiones, acertar por azar
> pasa una de cada cuatro veces. El número es indicio a lo largo de cinco
> turnos, no prueba de una decisión concreta. Se dice así en la pantalla.

**Lo que esto NO mide** —y conviene no fingir que sí— es si alguien miró su
pantalla durante la deliberación. Eso se observa en **P2** y **P4** mirando la
sala, no leyendo un archivo.

### B5 · Presupuesto de latencia — medido, y no era lo que decía

**Dónde:** [`config.py`](src/agents/config.py) · medido el 26-08-2026 contra
`gpt-5-nano`, 12 órdenes y 3 turnos de esfera

Esta entrada decía «hay timeout duro y degradación a plantilla, que es lo
importante». **Al medirlo, ninguna de las dos cosas era cierta.**

| | Lo que decía | Lo que medía |
|---|---|---|
| El presupuesto es duro | `timeout=12` en la llamada | El SDK reintenta **dos veces** de fábrica: 12 s eran hasta 36 s de reloj. Cronometrado: **35,3 s** |
| La esfera degrada si el proveedor tarda | excepcional | Tardaba **26–36 s** contra un presupuesto de 20: degradaba **siempre**. La esfera pública no había usado el modelo ni una vez |

Lo segundo es lo grave, y es del tipo que este documento llama silencioso: el
montaje anuncia seis agentes con su sesgo, el campo `generado_por` decía
`plantilla (el modelo falló: APITimeoutError)` en todos los turnos, y nadie
miraba ese campo porque no había motivo para sospechar.

**Las dos correcciones y lo que dan:**

```
REINTENTOS_LLM=0     el presupuesto declarado es el que se espera
ESFUERZO_NLU=low     el esfuerzo de razonamiento, medido y no supuesto
ESFUERZO_ENTORNO=low
```

| | Antes | Ahora | Presupuesto |
|---|---|---|---|
| **capa 4** · canal de órdenes | mediana 8,0 s · máx 35,3 s | **mediana 2,4 s · máx 4,4 s** | 12 s |
| **capa 3** · esfera pública | 26–36 s · fuera **siempre** | **5,5–6,3 s** | 20 s |

`minimal` está descartado para el canal y no por poco: con él, «declaren el
estado de sitio» llamaba a firmar la asistencia militar —forzar la acción más
parecida, que es el modo de falla F5— y una orden compuesta perdía la mitad.
Acierta 6 de 9 casos difíciles donde `low` acierta 9.

**Lo que sigue en P2** es lo que no se puede medir sin sala: el reloj de la fase
de consecuencias **entera** —modelo, red del local y pintado de las pantallas—,
que es lo que dura de verdad para las nueve personas que están mirando.


### B6 · El guion de la sesión

**Dónde:** fuera del código

Qué se dice en el turno 0 —incluida la declaración expresa sobre el alcance del
ejercicio—, cómo se abre el debriefing, y qué se hace si la sala se queda sin
órdenes al terminar los seis minutos.

---



---
---

# PARTE 2 · Con personas en una sala

**Esto es lo que ninguna prueba de código sustituye.** El motor puede estar
perfecto y el ejercicio no funcionar: lo que se mide aquí es si nueve personas
discuten, no si el código calcula.

Van en orden. Cada una responde una pregunta distinta y ninguna necesita la
siguiente para ser útil.

### B8 · Órdenes condicionales, en el canal

**Dónde:** [`nlu.py`](src/agents/nlu.py) · el motor ya está listo

`MotorCrisis.encolar_condicional()` existe y funciona: **«en cuanto Defensa
verifique ese punto, opérenlo»** es una orden que el motor sabe guardar y
disparar sola. El canal no sabe leerla.

Hoy, «si un equipo de terreno verifica el Puente Amarillo, opérenlo» se traduce como
orden **inmediata**, y lo único que impide que eso pase inadvertido es un aviso:

```
! Se leyó una condición en el texto y el canal NO la traduce: lo que sigue
  queda como orden inmediata. Si debía esperar a que ocurriera algo, no la
  confirmen todavía.
```

**Por qué se dejó en un aviso y no en una supresión.** Suprimir la acción sería
el canal decidiendo, que es lo único que esta capa no puede hacer. Y el plan se
lee en voz alta antes de ejecutar precisamente para que una persona atrape esto.

**Qué haría falta:** una herramienta `ordenar_si` con dos campos —la condición y
la acción—, un vocabulario cerrado de condiciones que el motor sepa evaluar
(«cuando X esté verificado», «si la mesa cae por debajo de N»), y una manera de
enseñar en el tablero que hay órdenes esperando. Ese último punto es el que hace
que valga la pena: **una orden condicional invisible es peor que no tenerla.**

> Con cinco turnos puede no hacer falta. Se decide viendo si en **P3** o **P4**
> alguien la pide de viva voz.

---

### P2 · Las pantallas — 30 min, dos personas

**¿Se entienden sin explicación?**

```bash
cd web_ui
npm install
npm run build
cd ..
uv run python -m src.api.main        # http://localhost:8000
```

**El montaje:** un proyector con `/tablero`, un portátil con `/consola` y otro
con una vista privada. Con un segundo proyector, otra vista privada.

`/tablero` lleva la esfera pública como **barra lateral plegable** —el botón
está arriba a la derecha—. Cuando está plegada, el botón sigue mostrando
cuántas denuncias hay sin verificar, que es lo que hace que alguien la abra.

> **La esfera no tiene ruta propia, y es a propósito.** La distancia entre lo que
> el Estado tiene por cierto y lo que se dice solo se percibe **simultánea**.
> Mientras tuvo pantalla aparte, bastaba proyectar una de las dos sola para
> perder justamente lo que hay que enseñar. **Una regla que el software
> garantiza vale más que una que el software recomienda.**

- ¿Se lee el tablero desde el fondo de la sala?
- ¿El mapa enseña por sí solo que un corredor vale lo que su peor punto?
- ¿La alerta de la vista privada se entiende en menos de diez segundos?
- ¿El plan de vuelta de la consola es legible en voz alta?

**Y la que mide la capa de ayuda:** ninguna cifra lleva ya su glosa impresa
debajo. Cada una tiene una marca **(?)** de 14 px y la definición formal
—con sus umbrales y coeficientes, tomados del motor— aparece al pasar por
encima, al llegar con el tabulador o al tocarla.

- ¿Alguien busca una definición y **no** encuentra la marca donde esperaba?
- ¿Alguna definición hace falta **dos veces** en el mismo turno? Si sí, ese dato
  debería estar impreso y no en el globo.
- ¿Alguna marca interrumpe la lectura del número en vez de acompañarla?

**Y la que mide si el tablero apunta sin mandar.** El tablero ordena corredores y
regiones peor primero, marca con ▲▼ cuánto se movió cada magnitud desde la
última ventana, dice en qué jornada va de cinco y cuenta lo que sigue sin cerrar.
Ninguna de las cuatro señales nombra un remedio.

- ¿Alguien mira el tablero y **dice en voz alta cuál es el problema** sin que se
  lo pregunten? Es la señal de que la saliencia funciona.
- ¿Alguien lee el tablero como una **lista de tareas**? Entonces se pasó de
  indicativo a prescriptivo, y hay que quitar señal.
- ¿El delta ▼ de una reserva provoca la pregunta «¿qué hicimos anoche?»? Es
  exactamente para lo que está.
- ¿La franja de noche se distingue de la de día **sin leerla**?
- ¿Se entiende, **sin explicarlo**, que un anillo en el mapa quiere decir que ahí
  pasó algo anoche? Y en particular: ¿se ve el bucle completo —se operó por
  fuerza, se abrió, volvió a cerrarse en el interludio— sin que nadie lo narre?
- ¿Alguien pregunta dónde están los escuadrones? Esa pregunta es **A6**, y la
  respuesta a P3 la decide.

> Las 38 definiciones viven en un solo archivo,
> [`definiciones.jsx`](web_ui/src/definiciones.jsx). Si un umbral cambia en
> `parameters.py`, hay exactamente un párrafo que corregir.

**Es la prueba más barata y la que más va a cambiar el diseño.**

### P3 · En seco, con tres personas — 45 min

**¿La asimetría de información produce conversación?**

Tres roles, uno por frente: **Interior**, **Defensa** y **Transporte**. Tres turnos,
sin turno 0 ni debriefing. Y una sola cosa que mirar:

- ¿Alguien dice un dato de su vista privada **sin que se lo pregunten**?
- ¿Alguien **pregunta** a otro por un dato que no tiene?
- ¿Aparece un desacuerdo entre dos personas que están las dos diciendo la verdad?

> Si las tres respuestas son «no», la asimetría es decoración y hay que revisar
> el contenido de las vistas (**A4**) antes de convocar a nueve.

### P4 · La corrida completa — 2 horas, nueve personas

**¿El ejercicio enseña lo que pretende enseñar?**

**Y es una medición, no un ejercicio.** Conviene decirlo antes de empezar.

Las tres lecturas del debriefing: la línea declarada contra la ejecutada · el
turno en que la mesa dejó de ser una mesa · el país que se recibió contra el que
se entrega.

Y una comprobación nueva de la v2: **en el minuto 4 de la deliberación, mire
cuántas personas están mirando su pantalla.** Si hay alguna, una de las cinco
reglas de §6.3 de la propuesta se rompió.

---


---

## Calibración — lo que solo se ve con gente dentro

**Ningún coeficiente está medido.** Son convenciones declaradas, elegidas para
que ninguna estrategia pura gane. El criterio es **por comportamiento, no por
realismo**: no hay respuesta empírica a cuánta legitimidad cuesta un muerto, y no
la va a haber.

**La medición vive en un solo sitio: la tabla de esta misma entrada (C5)**,
con su lectura. Se reproduce con
`uv run python scripts/correr_ejercicio.py --comparar`.

**Los dos problemas que estaban medidos ya no lo están** —la cohesión saturada en
0 y las muertes idénticas en cuatro de cinco estrategias— y no eran de
coeficientes: eran piezas que faltaban. Ver
la revisión general del motor (histórico en git: `docs/historial/`).

Quedan **cuatro cosas que solo se ven con personas dentro**:

### C4 · `solo_mesa` termina a un punto del acantilado

**Encontrado al implementar H1**, y merece quedar escrito porque es una
fragilidad de la medición, no del diseño.

Un punto abierto por concertación se sostiene **mientras la credibilidad de la
mesa siga por encima de 30**. Por debajo, los acuerdos se caen y con ellos los
caminos. Que haya acantilado está bien: es el punto pedagógico de todo el eje de
negociación.

El problema es dónde aterriza `solo_mesa`:

```
credibilidad al cierre de cada jornada
  sin H1 ....... 45  51  49  49  29      → 4 reaperturas en la última noche
  con H1 ....... 45  51  49  49  49      → ninguna
```

**Veintinueve contra treinta.** Un punto de diferencia decide si cuatro caminos
siguen abiertos, y por eso añadir H1 movió la fila entera de `solo_mesa` de
5 netas a 9. No es azar: pasa igual con las cuatro semillas probadas.

| | Qué significa |
|---|---|
| Para el **ejercicio** | nada. Una sala real no juega `solo_mesa` puro |
| Para la **tabla de calibración** | esa fila es bimodal: cualquier cambio pequeño la voltea, así que **no sirve para detectar regresiones** |

Dos salidas, y la decisión es del equipo:

1. **Aceptarlo y anotarlo** — la tabla compara estrategias caricaturescas, no
   salas; que una fila sea sensible no invalida el resto.
2. **Separar el umbral del final de la corrida** — si el acantilado se cruzara en
   la jornada 3 y no en la 5, la sala tendría dos turnos para reaccionar y el
   mecanismo *enseñaría* en vez de solo puntuar.

La 2 es más interesante pedagógicamente y toca calibración, así que se decide
midiendo con gente dentro.

### C5 · La tabla hay que rehacerla: el tablero cambió debajo

**La medición vigente es de un escenario que ya no es el que corre**, y hasta
que se rehaga no sirve para detectar regresiones. Cambiaron tres cosas a la vez:

| Qué cambió | De | A |
|---|---|---|
| puntos de cierre | 11 (seis en la ciudad) | **10 (cinco en la ciudad)** |
| geografía | esquema sobre una silueta | **red vial real, corredores ruteados** |
| `masa_base` | dos puntos la tenían medida | **ocho la estrenan** |

> **REMEDIDA tras la revisión del motor.** Entraron cuatro reglas que mueven la
> tabla: una orden no se dicta dos veces en la misma jornada, los eventos que
> BAJAN la intensidad decaen igual que los que la suben, la autonomía tiene
> techo, y todo corredor exigido se cobra si no se abre. Semilla `20210511`,
> comprobada con `1`, `7`, `42` y `99999`.

```
  estrategia         netas  reap  muert  legit  cohes  credib   resp
  ---------------------------------------------------------------------
  solo_fuerza            4     3     64     10      0      21     15
  solo_mesa              9     0     15     62     56      38     50
  constituida            0     3     48     50     69      21     58
  humanitaria            2     0     13     34     23      45     38
  logistica              2     0     13     54     40      36     47
  agroalimentaria        5     0     33     68     27      45     50
  pasiva                 1     0     64     25     28      45     45
```

> **LA NOTA ANTERIOR AFIRMABA DOS COSAS QUE NO SE SOSTIENEN, y las dos eran el
> criterio con el que esta tabla detecta regresiones.** Quedan escritas aquí
> porque lo que hay que decidir es qué hacer con ellas, no volver a descubrirlas.
>
> 1 · **«`cohes` y `muert` no se movieron con la semilla».** Sí se mueven, y con
> semillas que la nota no probó: `solo_mesa` pasa de 15 muertes a **29** con la
> semilla `42`; `agroalimentaria`, de 33 a **64**; `logistica`, de 13 a **28**
> con `99999`. Mientras `muert` dependa del dado, esta columna no puede servir
> de detector de regresiones — y es la columna que más pesa en el debriefing.
>
> 2 · **«ninguna estrategia domina».** `solo_mesa` domina en las cinco semillas
> probadas: primera en aperturas netas, mínimo de muertes, primera o segunda en
> las cuatro reservas. Las reglas nuevas no la tocaron —la sala que negocia pide
> mesas sobre puntos DISTINTOS, que es exactamente lo que la llave de jornada
> permite— y no debían tocarla: cerrar el exploit de repetir la misma orden y
> calibrar el peso de la vía de concertación son dos problemas distintos.
>
> El segundo sigue siendo la entrada `C4` de más abajo, y se decide midiendo con
> gente dentro.

> **La estrategia agroalimentaria es nueva y NO domina**, que es lo que había
> que comprobar al añadir el noveno rol: abre cinco caminos, deja treinta y tres
> muertes —el doble que la mesa— y paga su legitimidad en cohesión, porque
> reordena el criterio de Transporte y abre un canal paralelo al del Interior.
> Lo que no arregla es lo de abajo.

**`solo_mesa` se acerca a dominar.** Abre nueve caminos, deja quince muertes
—casi lo mismo que las dos estrategias logísticas, que antes le sacaban el
doble— y termina primera o segunda en las cuatro reservas. El criterio de
calibración del caso es explícito y es este:

> Ajustar hasta que **ninguna estrategia pura gane**.

Si una sala puede sentarse a hablar cinco jornadas y ganar en todo, el dilema
del caso —abrir el país o salvar a la gente— se deshace.

> **El noveno rol no empeora esto y tampoco lo arregla.** `agroalimentaria` no
> domina —abre cinco caminos, deja treinta y tres muertes y paga su legitimidad
> en cohesión—, pero se mide por primera vez y no hay serie histórica contra la
> que compararla. Cuando se rehaga la tabla, hay que rehacer las siete filas.

**Dónde mirar primero**, por orden de sospecha:

1. **`masa_base` de los ocho puntos nuevos.** El término de masa entra en el
   riesgo de incidente, así que unas cifras generosas abaratan la fuerza y unas
   cortas la encarecen; pero lo que se movió a favor de la mesa fue el
   *resultado humanitario*, y ahí manda el abastecimiento.
2. **Qué punto se retiró.** Salió `N002`, la Glorieta La Ceiba: dureza media y
   **vocería 0,68**, el punto pactable de la arteria. Quitarlo debería haber
   hecho la mesa *más* difícil, no menos — conviene entender por qué no.
3. **La longitud de los corredores.** Ahora son caminos reales y `C-HOS` da un
   rodeo de 1,77 sobre la línea recta. La reposición no depende de la distancia
   —el motor no tiene tiempos de desplazamiento— así que **esto no debería
   influir**, y si influye es que algo lee la geometría que no debería.

Es una medición, no un ejercicio, y se hace con
`uv run python scripts/correr_ejercicio.py --comparar`.

### C1 · ¿Diez puntos son los que caben en cinco decisiones?

**Eran veinticuatro y se bajó a once**, sin haberlo medido con gente: veinticuatro
producían un tablero que ninguna sala recorría entera, y quince de ellos eran
decorado con nombre propio. Once es la apuesta contraria y también es una
apuesta. Lo que hay que mirar en la primera corrida:

- si la sala toca **ocho o más**, el número está bien
- si toca **cuatro o cinco**, sobran igual y hay que bajar a ocho
- si se queja de que no hay dónde elegir, subir a catorce

Cinco de los diez están en la ciudad epicentro y cinco fuera. Esa proporción es
la que hace que el Alcalde tenga cartera sin que las otras tres regiones sean
decorado, y es lo segundo que conviene mirar.

### C2 · ¿Da tiempo a que la mesa se rompa?

Si la cohesión termina por encima de 55 casi siempre, subir la sensibilidad — o
aceptar que un ejercicio de dos horas **mide la constitución de la mesa y no su
desgaste**, que también es un objeto legítimo.

### C3 · ¿Se cumplen los 13 minutos de día?

La jornada son quince minutos: trece de día y dos de noche. Las siete fases se
retiraron —eran una coreografía de sala ideal— y el día es ahora un solo tramo
continuo en el que se puede ordenar en cualquier momento.

Lo que hay que medir: **si los dos minutos de noche alcanzan** para leer las
consecuencias. Si la sala se queda con la boca abierta y el reloj ya abrió la
jornada siguiente, el reparto correcto es 12/3 y no 13/2. Se cambia en
`parameters.py` (`MIN_DIA`, `MIN_NOCHE`) y en ningún otro sitio.

### B13 · Dos números del paso de nueve roles a siete, sin calibrar

De «De nueve roles a siete» (histórico en git: `docs/historial/`).
Los dos están puestos, funcionan y **son provisionales**: se eligieron por
coherencia con lo que había, no midiendo. Van con `C5`, que este cambio obliga a
rehacer de todos modos.

| | Qué hay que fijar | Hoy |
|---|---|---|
| **1** | El precio de `FijarReglasEmpleoSector`, que ahora enciende los **tres** mitigadores en una sola acción · antes el tercero lo traía la Defensoría | `estandar_autoimpuesto`: respaldo **+8**, cohesión **−6** |
| **2** | Cuánto cambian los costos de verificar una denuncia **sin** protocolo común adoptado, ahora que quien verifica es el sector señalado | veraz: respaldo **−11**, legitimidad **−7** · falsa: legitimidad **+1** |

**Por qué importa el primero.** Encender tres mitigadores el primer día sin
ningún costo divide el riesgo por tres y medio a cambio de nada, y eso vacía la
decisión que el subsistema de fuerza existe para producir. El número tiene que
salir de medir cuántas salas lo adoptan en la jornada 1 y qué pasa con las que
no.

> Medido tras el cambio, la tabla de estrategias se movió poco: `constituida`
> baja de 74 a 68 de cohesión y `humanitaria` de 28 a 22. Ninguna estrategia
> pasó a dominar, que era el riesgo.

### B14 · La lectura de la corrida — cómo destrabaron y a quién atendieron

**Dónde:** [`docs/LA_MEDICION.md`](docs/LA_MEDICION.md) es la propuesta completa ·
`src/engine/lectura.py` y `GET /api/lectura` están **por escribir** · depende de
**B1** y se presenta dentro de **B7**

Dos preguntas que el ejercicio hoy no responde y que son el material del
debriefing: **por qué vía se destrabó el país** y **a quién se atendió**
mientras tanto.

Seis vías en dos familias. **Tres abren el punto** y son las tres del campo
`modo_apertura`, que la sala ya lee en el mapa: **despejar**, **concertar**,
**desgastar**. **Tres no abren ninguno** y el motor no las nombra en ningún
sitio: **sortear** —el cierre sigue en pie y lo bloqueado pasa igual—,
**constituir** —cambia lo que cuesta todo lo demás— y **encuadrar** —cambia lo
que el país cree que está pasando—. Y cuatro públicos: empresa, gremios,
ciudadanía y comunidad internacional.

**Nada de esto se ve durante la sesión, y esa es la condición de que mida algo.**
Un marcador visible deja de medir la conducta y pasa a producirla. Se calcula al
cierre desde el pliego y la traza, **sin ningún campo nuevo en `Estado`**, que es
lo que impide que se cuele en una vista por un descuido de serialización.

Lo que hay que decidir antes de escribir una línea está en §10 de la propuesta.
Dos cosas de ahí no son técnicas y son del equipo docente: **si se les anuncia en
el briefing que habrá una lectura** (anunciar los ejes los hace jugables) y **si
se revela la capa 1 en el debriefing**.

> **Y un hallazgo del propio diseño, dicho en la propuesta y no escondido:** en
> el repertorio actual, atender a la empresa es casi siempre operar por la
> fuerza —seis de las diez acciones que la atienden—. Los dos ejes **no son
> independientes**, y eso hay que reportarlo como hallazgo del caso en vez de
> tocar el repertorio para que la medición salga más limpia.

**Estorba, y es de esta misma revisión:** `codigo` dejó de ser único dentro de un
rol tras el reparto de las dos carteras —Interior tiene dos `A1` y dos `A4`;
Policía dos `A2`; Transporte dos `A2` y dos `A3`; Agricultura dos `A4`—, porque
cada acción heredada se trajo el código de su rol anterior. No rompe nada hoy
—nada indexa por `(rol, codigo)`— pero cualquier informe que cite acciones por
código confunde dos filas.

### B12 · Lo que quedó escrito y nadie lee

De la revisión general del motor (histórico en git: `docs/historial/`).
Cuatro defectos se corrigieron ahí; esto es lo que se decidió **no** tocar,
porque tocarlo sería cambiar el diseño y no arreglar un error.

> **CERRADO por la simplificación del motor (S1–S11).** Las tres
> constantes y los tres campos se retiraron: los minutos de instalación y de
> debriefing se fueron a la guía del facilitador, la custodia militar por
> instalación dejó de existir hasta que alguien decida que la aritmética
> Interior–Defensa debe cambiar, y `nodo_unico`, `turno_firmado` y `resultado`
> ya no se escriben. Quedó **una huérfana declarada** —
> `MULTIPLICADOR_CONSTITUTIVA_REACTIVA`, que siempre estuvo escondida DENTRO de
> `COSTO_RESERVAS`— y la prueba que vigilaba la lista original sigue vigilando
> esa. Lo de abajo se deja como estaba, porque describe el problema que la
> decisión original tenía delante.

**Tres constantes de `parameters.py`:**

| | Qué pasa | Qué habría que decidir |
|---|---|---|
| `MIN_INSTALACION` · `MIN_DEBRIEFING` | 12 y 20 minutos del cuadro de tiempos de la sesión. El reloj del ejercicio solo conduce las cinco jornadas | O el reloj cubre la sesión entera —instalación, jornadas, debriefing— o estos dos se van a la guía del facilitador. Hoy están en el sitio donde nadie los va a mirar |
| `CUSTODIA_MILITARES_POR_INSTALACION = 3` | Su gemela policial (`= 2`) sí se usa. El redespliegue militar inmoviliza **por unidad**, no por instalación, así que esta nunca entra | Que la custodia militar cueste por instalación como la policial, o quitar la constante. Lo primero **cambia la aritmética** que enfrenta al Interior con Defensa, y esa es la decisión |

**Tres campos del estado que se escriben y nadie lee:**

| Campo | Se escribe en | Nadie lo lee |
|---|---|---|
| `Banderas.nodo_unico` | `FijarRegistroEscrito` | no está en `CONSTITUTIVAS`, no tiene rótulo, y **el bloque `banderas` que el tablero sirve no lo pinta ninguna superficie** |
| `Acuerdo.turno_firmado` | `ConvocarMesaNacional` | el vencimiento se calcula con `turno_limite` |
| `Decision.resultado` | `_registrar()` | el pliego del Presidente muestra rol, acción y responsable |

Ninguno es un error: son campos que se dejaron puestos para algo que todavía no
existe. **Lo que sí conviene decidir es el primero**, porque el nodo único de
coordinación es una de las diez decisiones que la mesa puede tomar y hoy no
aparece en el cuadro del Presidente ni en ningún otro sitio: se adopta, se cobra
en el registro escrito, y **el ejercicio no lo enseña nunca**.

> Hay una prueba —`test_ninguna_constante_de_parameters_queda_sin_leer`— que
> lleva la lista de las tres constantes. No prohíbe las huérfanas: obliga a que
> aparecer en ella sea una decisión escrita y no un descuido.

### B11 · Se concede la clase agroalimentaria y nadie comprueba si se cumplió

La ficha del Ministro de Agricultura declara un efecto que **el motor no modela**:

> *«Si la lista se aprueba y no se cumple, queda documentado públicamente un
> incumplimiento del Gobierno que los gremios usarán en su contra.»*

Hoy `FijarClasePrioridadAlimentaria` reetiqueta un corredor y ahí termina. Si ese
corredor sigue bloqueado las cinco jornadas, **no pasa nada**: la mesa concedió
una prioridad que no entregó y el ejercicio no se lo cobra.

Es el mismo modo de falla que el anuncio de aperturas de Transporte
(`anunciado_abierto` / `anunciado_verificado`), y **ya existe la maquinaria para
resolverlo**: una revisión nocturna que mire si el corredor con clase
agroalimentaria dejó pasar algo, y cobre credibilidad si no. Media hora.

Se deja anotado y no hecho por una razón de método: es el **tercer** cobro
nocturno que se añadiría —mesas congeladas, riesgo de infraestructura, y este— y
conviene ver una corrida con personas antes de seguir apilando consecuencias que
la sala no ve venir. Va con **P4**.

### B9 · Ninguna prueba mira lo que la interfaz dibuja

**El fallo que lo hizo necesario.** `rotulo()` traduce el identificador del motor
al rótulo de pantalla, y admite un solo argumento: `rotulo('Puente Amarillo')`
tenía que capitalizar y devolver el texto. Devolvía **un guion**, porque la
primera guarda miraba `valor` —que con un solo argumento es `undefined`— antes de
darse cuenta de que el argumento único era el valor.

Así se formatea **cada celda de texto de las siete vistas privadas**. El resultado:
el nombre de cada punto, cada corredor, cada región y cada estado salía como
«—» en la pantalla de su titular. Nueve tablas llenas de guiones, que desde el
otro lado de la sala se ve exactamente como una pantalla en blanco.

> **Y la verificación automática pasaba entera.** El motor entregaba bien los
> nombres; era la última capa la que los borraba. No hubo excepción, ni traza, ni
> error de consola: la interfaz hizo su trabajo con diligencia sobre un dato
> equivocado.

**Lo que falta.** Un verificador que renderice las cuatro superficies con un
estado de referencia y falle si algo no cuadra. No hace falta un navegador:
`react-dom/server` las pinta en memoria en milisegundos. Tres comprobaciones
bastarían para haber cazado esto:

- ninguna celda de una tabla es un guion cuando el motor entregó un texto
- las cuatro superficies renderizan sin lanzar, con estado de t=0 y de t=5
- el mapa dibuja un rótulo por punto, y las zonas de región no se solapan

**Coste**: `esbuild` ya está en `web_ui` como dependencia de Vite, y el corredor
cabe en un `npm run verificar`. **Sin esto, la única prueba de la interfaz es
mirarla** — y mirarla es justo lo que no ocurre entre una corrida y la siguiente.

---


---
---

# PARTE 3 · Decisiones que no son mías

No son técnicas y no me corresponden. Cada una tiene consecuencias sobre el
diseño, así que van con lo que se gana y lo que se pierde.

### A1 · ¿Cuántos dispositivos, o papel?

**Bloquea:** el montaje físico de la sala. No bloquea código.

| Montaje | Qué hace falta |
|---|---|
| Portátil o tableta por persona | nueve equipos en la red del servidor |
| **Papel por turno** | alguien imprime nueve hojas desde `/api/vistas` |

> **Recomendación:** portátil o tableta. Y si el equipo no está seguro de poder
> sostener las cinco reglas —vista sin scroll, pantallas congeladas en la
> deliberación, nadie ordena desde su pantalla, ficha en papel, el tablero no
> repite lo privado—, **papel**: el ejercicio funciona igual y el riesgo de nueve
> personas mirando nueve pantallas desaparece.

### A2 · ¿Quién opera la consola?

**Bloquea:** el guion de la sesión.

**No es un moderador**: no conduce, no reparte información y no sabe nada que los
demás no sepan.

> **Recomendación:** un externo si lo hay —deja a los nueve libres para
> deliberar—; el Presidente si no, porque el registro escrito de decisiones ya es
> competencia suya.

### A3 · ¿Con llave o sin llave la primera vez?

**Bloquea:** qué se está midiendo.

La llave ya está puesta y las dos capas funcionan. Con llave, la consola entiende
lenguaje coloquial y la esfera pública produce titulares reales; sin ella, ambas
degradan y el ejercicio corre igual.

> **Recomendación:** **la primera corrida sin llave** —basta con vaciar
> `OPENAI_API_KEY` en `.env`—, para medir el motor y no el modelo. Cuando el
> motor esté calibrado, se enciende y se mide qué añade, que es una medición
> distinta y también interesante.

### A4 · ¿Cuál es el contenido exacto de las siete vistas?

**Bloquea:** la versión definitiva. No bloquea probar.

Las nueve están construidas con un contenido que **es una propuesta, no una
decisión**. Verlas de un vistazo:

```bash
uv run python scripts/correr_ejercicio.py --vistas
```

La pregunta, vista por vista: **¿este dato le sirve a su titular para decir algo
que nadie más puede decir?** Si no, sobra.

> **Recomendación:** probarlas tal como están y ajustar después. Es una decisión
> que se resuelve mejor viendo a tres personas usarlas 45 minutos que
> discutiéndola en una mesa.

### A5 · ¿Se cierra el territorio ficticio?

**Bloquea:** las fichas impresas y el material de los participantes.

Los nombres provisionales están puestos y funcionando: **Bellaflor** (ciudad
epicentro), **Región de Bellaflor**, **Puerto Espejo**, **Las Cumbres**, **Alto
Verde**. Se sustituyen enteros editando solo
[`data/escenario/estado_inicial.json`](data/escenario/estado_inicial.json),
porque el motor identifica por código y no por nombre.

> **Recomendación:** dejarlos para las primeras corridas y decidirlos después,
> cuando se vea si el caso muerde con nombres inventados. El criterio: que **no
> sean alias transparentes**. El repositorio falla solo si vuelve a aparecer un
> nombre real.

---

### A6 · ¿El mapa muestra dónde está la fuerza?

**Quién decide:** el equipo docente. **Bloquea:** el papel de la Policía en la
mesa.

El mapa ya dibuja **lo que se hizo**: un anillo sobre cada punto donde ocurrió
algo en la última ventana — se operó y con qué unidad; se
volvió a cerrar de noche; alguien lo verificó. Eso es público: sale en las
noticias esa misma tarde.

Lo que **no** dibuja es dónde está la fuerza ahora. La ubicación, la asignación
y la fatiga de cada escuadrón existen en el motor (`Unidad.ubicacion`) y viven
solo en la vista de la Dirección General de la Policía.

| | Si se muestra | Si no se muestra |
|---|---|---|
| **La sala** | lee el tablero sin preguntar | tiene que preguntarle a alguien |
| **La Policía** | pierde su razón de estar | es la única que convierte «hay 6 escuadrones libres» en «hay 2 que llegan a tiempo» |
| **El ejercicio** | más fácil de seguir | siete roles siguen necesitando al octavo |

> **Está puesto del lado que preserva los siete roles**, que es el que sostiene el
> diseño. Cambiarlo es media hora: `vista_publica()` ya tiene el dato y solo
> habría que dejarlo salir.

Se decide mejor **después de P3**: si con tres personas nadie le pregunta nunca a
la Policía dónde tiene los escuadrones, la asimetría no está funcionando y da
igual mostrarla.

---

### A7 · ¿La consola puede decir qué punto bloquea un corredor?

**Encontrado revisando el canal de órdenes.** Cuando alguien ordena una escolta,
`Escoltar.validar()` responde:

```
Corredor del Sur sigue bloqueado en Cruce de San Isidro.
La escolta puede salir, pero la carga no pasará.
```

**Qué punto bloquea cada corredor es el dato exclusivo del Ministro de
Transporte**, y esa exclusividad está garantizada por construcción. Y el plan se
lee en voz alta: cualquiera que pida una escolta se lo destapa a toda la sala.

| | A favor de dejarlo | A favor de quitarlo |
|---|---|---|
| **Es consecuencia, no consulta** | el dato aparece porque alguien gastó una orden; no se puede pedir a discreción | pero se destapa igual, y basta con una escolta |
| **El valor de Transporte** | está en saberlo **antes**, para que la sala no gaste el turno | si se destapa en el turno 1, en el turno 2 ya lo sabe todo el mundo |

Al explicar un corredor, el resolutor **sí** se contiene: enumera sus puntos —que
son públicos— y nunca dice cuál lo bloquea. Esa asimetría entre las dos
superficies es la que hay que resolver en un sentido o en el otro.

> Cambiarlo es una línea. La pregunta no es técnica: es **cuánto vale que
> Transporte sea necesario el segundo turno y no solo el primero.**

Se decide con **P3**, mirando si alguien le pregunta a Transporte antes de pedir
una escolta.

---

## Fuera del código

- **Las fichas y sus agendas** se entregan en papel. Son contexto del rol, no
  una jugada oculta: no hace falta protocolo de custodia, hace falta que cada
  uno lea la suya antes de empezar.
- **La declaración del turno 0** sobre el alcance del ejercicio: el motor no
  cuantifica culpa ni produce veredictos sobre hechos históricos.
- **Qué se dice sobre el azar.** *«El azar nunca decide si algo era buena idea;
  decide si esta vez salió mal, y la probabilidad se muestra antes.»*

---
## Lo que ya no está pendiente

**Se movió entero al historial** (en git: `docs/historial/resueltos.md`).
Un documento que lleva la cuenta de lo que falta no puede tener dentro
doscientas líneas de lo que ya no falta.

Lo que hay allí, por si hace falta ir a buscarlo:

| | Qué se cerró |
|---|---|
| **1** | Las decisiones de la propuesta original — marcador, retiro de la Defensoría, azar |
| **2** | Los siete problemas del diagnóstico del motor anterior (D1–D7) |
| **3** | Las dos capas de lenguaje natural, con su degradación sin llave |
| **4–5** | Las dos revisiones del canal de órdenes — dieciocho fallos, nueve de ellos silenciosos |
| **6** | El Comité del Paro, que no volvía nunca |
| **7** | El paquete detonante (H1–H4) |
| **8** | Las superficies — mapa, reloj, deltas, semáforo del repertorio |

**Y una cosa de ahí sigue abierta**, porque es de equilibrio y no de corrección:
el costo de −12 por operar exige que el Comité esté sentado, así que **en cuanto
el Comité se va, operar deja de costarlo**. Con la vuelta ya implementada eso
pasa a ser un estado que la sala puede administrar, y cambiarlo mueve la tabla de
calibración. Se decide con gente dentro.

---

*Última revisión: 2026-08-27 · semilla `20210511` · capas de lenguaje natural
activas con `gpt-5-nano`, con su latencia medida (B5).*
