# Pendientes

Lo que falta para correr esto con ocho personas en una sala. **Este es el único
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
> citados desde el código (`PENDIENTE(B1)`), desde `COMO_FUNCIONA.md` y desde
> aquí mismo. Renumerarlos por estética rompería la navegación en los dos
> sentidos que este documento promete — y ya se rompió una vez.

---

## En una mirada

| | Pendiente | ¿Necesita gente? | Estado |
|---|---|---|---|
| **B1** | el archivo de la corrida — persistencia y telemetría | no | **no existe** · bloquea B7 |
| **B2** | la identidad de los ocho roles, en datos | no | `data/roles/` vacío · hoy duplicada en el frontend |
| **B7** | el debriefing, la superficie que falta | no | **no existe** · depende de B1 |
| **B5** | presupuesto de latencia medido | se mide en P2 | hay timeout, falta medirlo |
| **B6** | el guion de la sesión | no | fuera del código |
| **P1** | correr el motor solo y leer la traza | **no** — una persona, 20 min | listo para correr |
| **P2** | las pantallas | **sí** — dos personas, 30 min | listo |
| **P3** | en seco, tres roles | **sí** — tres personas, 45 min | listo |
| **P4** | la corrida completa | **sí** — ocho personas, 2 h | listo |
| **B3** | decisiones alineadas con información privada | no | derivado del motor · sale en B1, se lee en B7 |
| **C1–C4** | cuatro calibraciones | **sí** | esperando P3/P4 · **C4 es nueva** |
| **A1** | cuántos dispositivos, o papel | — | esperando |
| **A2** | quién opera la consola | — | esperando |
| **A3** | ¿con llave o sin llave la primera vez? | — | esperando |
| **A4** | el contenido exacto de las ocho vistas | se decide probando | esperando |
| **A5** | cerrar el territorio ficticio | — | nombres provisionales puestos |
| **A6** | ¿el mapa muestra dónde está la fuerza? | se decide tras P3 | esperando |

Lo que **sí** funciona está en el README, sección «Estado actual», y en
[`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md).

---

## Cómo verlos desde el código

```bash
grep -rn "PENDIENTE" src/
```

Cada marca lleva el identificador de esta lista (`PENDIENTE(B1)`), así que se
puede ir en las dos direcciones: del código a la explicación y de la explicación
al código. Lo custodia
`test_cada_marca_del_codigo_apunta_a_un_pendiente_que_existe`.

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


### B2 · La identidad de los ocho roles, en datos

**Dónde:** [`data/roles/`](data/roles/) (vacío) ·
[`web_ui/src/comun.jsx`](web_ui/src/comun.jsx) tiene hoy la lista duplicada

**Esta entrada era más grande de lo que debía.** Decía «las ocho fichas de rol,
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
pantalla diga qué causó qué, sino que ocho personas lo discutan mirando el
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
| **Necesita un observador dedicado** | y con ocho participantes ya hay alguien en la consola |

**Compartir información no se anota: se evidencia en lo que la sala decide.** Si
la asimetría funciona, se nota en que el Puesto de Mando prioriza donde solo un
rol sabía que había que priorizar. Y eso el motor **sí** lo puede calcular,
porque conoce las dos mitades: el dato privado y la decisión.

**Decisiones alineadas con información que solo tenía un rol.** Para cada
decisión del pliego, el motor comprueba si aprovecha algo que no estaba en el
tablero:

| Decisión | El dato privado que la respalda | De quién |
|---|---|---|
| Prioridad de combustible a una región | ¿es la del reloj de oxígeno más corto? El tablero solo da el semáforo | **Minas** |
| Verificar un punto y no otro | ¿es el que bloquea un corredor? | **Transporte** |
| Escoltar por un corredor | ¿sirve a la región peor abastecida? | **Minas + Transporte** |
| Operar con dupla presente | el mitigador que solo la Defensoría puede aportar | **Defensoría** |
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

### B5 · Presupuesto de latencia, medido

**Dónde:** [`src/agents/entorno.py`](src/agents/entorno.py) y
[`src/agents/nlu.py`](src/agents/nlu.py)

Hay timeout duro y degradación a plantilla, que es lo importante. Lo que falta es
**medir cuánto tarda de verdad** con el modelo puesto: la fase de consecuencias
dura sesenta segundos con ocho personas mirando la pantalla.

Se mide en la prueba **P2**, cronómetro en mano.


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
perfecto y el ejercicio no funcionar: lo que se mide aquí es si ocho personas
discuten, no si el código calcula.

Van en orden. Cada una responde una pregunta distinta y ninguna necesita la
siguiente para ser útil.

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

> Las 30 definiciones viven en un solo archivo,
> [`definiciones.jsx`](web_ui/src/definiciones.jsx). Si un umbral cambia en
> `parameters.py`, hay exactamente un párrafo que corregir.

**Es la prueba más barata y la que más va a cambiar el diseño.**

### P3 · En seco, con tres personas — 45 min

**¿La asimetría de información produce conversación?**

Tres roles, uno por frente: **Interior**, **Defensa** y **Minas**. Tres turnos,
sin turno 0 ni debriefing. Y una sola cosa que mirar:

- ¿Alguien dice un dato de su vista privada **sin que se lo pregunten**?
- ¿Alguien **pregunta** a otro por un dato que no tiene?
- ¿Aparece un desacuerdo entre dos personas que están las dos diciendo la verdad?

> Si las tres respuestas son «no», la asimetría es decoración y hay que revisar
> el contenido de las vistas (**A4**) antes de convocar a ocho.

### P4 · La corrida completa — 2 horas, ocho personas

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

Medición actual con `--comparar`:

```
  estrategia      netas  reap  muert  legit  cohes  credib   resp
  ---------------------------------------------------------------------
  solo_fuerza         1     2     64     11      0      21     20
  solo_mesa           9     0     64     65     56      49     49
  constituida         3     1     48     24     74      21     38
  humanitaria         3     0     14     41     28      35     54
  logistica           3     1     24     41     40      26     39
  pasiva              1     0     64     23     28      45     43
```

**Ninguna domina, y el reparto es el que debe ser.** `solo_mesa` abre nueve
caminos y conserva las reservas — **y deja morir exactamente a la misma gente que
`pasiva`**. `humanitaria` salva 50 de las 64 muertes y abre un tercio de los
caminos. `constituida` tiene la mejor mesa y gasta legitimidad al operar.
`solo_fuerza` se queda sin nada.

El dilema central del caso está en esa primera línea: **abrir el país y dejar
morir a la gente, o salvarla y entregar el país cerrado.**

**Los dos problemas que estaban medidos ya no lo están** — y no eran de
coeficientes, eran piezas que faltaban. Ver «Lo que ya NO está pendiente».

Quedan **tres cosas que solo se ven con personas dentro**:

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

### C1 · ¿24 puntos son demasiados para 5 decisiones?

Si la sala toca menos de diez, bajar a 16. El mapa esquemático puede cambiar esto
en las dos direcciones: hace los 24 más manejables, o hace evidente que sobran.

### C2 · ¿Da tiempo a que la mesa se rompa?

Si la cohesión termina por encima de 55 casi siempre, subir la sensibilidad — o
aceptar que un ejercicio de dos horas **mide la constitución de la mesa y no su
desgaste**, que también es un objeto legítimo.

### C3 · ¿Se cumplen los 13 minutos por turno?

Con el minuto 0 de parte privado añadido, el turno es más apretado. Si no
cuadra, el problema es de conducción y se corrige con guion, no con diseño.

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
| Portátil o tableta por persona | ocho equipos en la red del servidor |
| **Papel por turno** | alguien imprime ocho hojas desde `/api/vistas` |

> **Recomendación:** portátil o tableta. Y si el equipo no está seguro de poder
> sostener las cinco reglas —vista sin scroll, pantallas congeladas en la
> deliberación, nadie ordena desde su pantalla, ficha en papel, el tablero no
> repite lo privado—, **papel**: el ejercicio funciona igual y el riesgo de ocho
> personas mirando ocho pantallas desaparece.

### A2 · ¿Quién opera la consola?

**Bloquea:** el guion de la sesión.

**No es un moderador**: no conduce, no reparte información y no sabe nada que los
demás no sepan.

> **Recomendación:** un externo si lo hay —deja a los ocho libres para
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

### A4 · ¿Cuál es el contenido exacto de las ocho vistas?

**Bloquea:** la versión definitiva. No bloquea probar.

Las ocho están construidas con un contenido que **es una propuesta, no una
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
> sean alias transparentes**. Hay una prueba automática
> (`test_el_territorio_es_ficticio`) que falla si vuelve a aparecer un nombre real.

---

### A6 · ¿El mapa muestra dónde está la fuerza?

**Quién decide:** el equipo docente. **Bloquea:** el papel de la Policía en la
mesa.

El mapa ya dibuja **lo que se hizo**: un anillo sobre cada punto donde ocurrió
algo en la última ventana — se operó, con qué unidad y si llevaba dupla; se
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

> **Está puesto del lado que preserva los ocho roles**, que es el que sostiene el
> diseño. Cambiarlo es media hora: `vista_publica()` ya tiene el dato y solo
> habría que dejarlo salir.

Se decide mejor **después de P3**: si con tres personas nadie le pregunta nunca a
la Policía dónde tiene los escuadrones, la asimetría no está funcionando y da
igual mostrarla.


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
---

## Lo que ya NO está pendiente

Anotado aquí para que nadie lo vuelva a levantar.

### De la propuesta original

> **Ojo con los identificadores de esta tabla:** son los de la propuesta
> original, no los de la lista de arriba. El `A6` de aquí («¿se acepta el
> azar?») no tiene nada que ver con el `A6` vigente («¿el mapa muestra dónde
> está la fuerza?»). Los dos numeraron cosas distintas en momentos distintos.

| | Era | Cómo quedó |
|---|---|---|
| **T1** | `intensidad_movilizacion` satura en 100 y deja de discriminar | Rendimientos decrecientes (×0,6 por repetición) y decaimiento proporcional (×0,96) |
| **T2** | `control_voceria` no está en la capa de estimación | Entró con sesgo por fuente: Interior lo sobreestima +0,20; el Alcalde lo ve bien en su jurisdicción |
| **T3** | `dureza` la escriben dos mecanismos sin precedencia | Tres, con orden fijo en `paso()`. Determinista y reproducible |
| **—** | Toda región sin corredor humanitario acumula muertes inevitables | Invariante con fallo ruidoso en `loader.py` y prueba automática |
| **—** | `P(incidente)` alcanzaba 1,0 y volvía la tirada irrelevante | Techo en 0,98 |
| **A2** | ¿Se puntúa? ¿Las agendas suman? | **No hay marcador.** Las agendas se revelan, no se puntúan |
| **A3** | ¿La Defensoría puede retirarse? | **No se retira.** Su palanca es manifestar públicamente que su permanencia está en cuestión — se puede usar varias veces, es graduada, y nunca saca sus mitigadores del juego |
| **A4** | `capital_politico` no es implementable | Eliminado. Con ocho personas en una sala, el capital político lo administra la sala sola |
| **A6** | ¿Se acepta el azar? | Sí, con semilla fija. **La semilla no es un elemento visible de la interfaz** |

### El paquete detonante, completo

**B4** era el último de los cuatro hechos que abren el turno 1. Ya está.

| | Qué | Dónde |
|---|---|---|
| **H1** | el incidente nocturno junto a la refinería, con un herido grave de la fuerza pública | `hecho_h1` en [`estado_inicial.json`](data/escenario/estado_inicial.json), aplicado por `_aplicar_hecho_h1()` |
| **H2** | dos denuncias graves sin verificar, una cierta y una falsa | `denuncias_iniciales` |
| **H3** | el ultimátum gremial de 48 horas | `ultimatum_gremios_turno` |
| **H4** | la región que cruza los dos días de oxígeno | autonomías del escenario |

**H1 cae en `N013`, la Portería de la refinería**, y no es una elección
arbitraria: el punto ya traía la trampa en los datos.

| Dato | Valor | Qué produce |
|---|---|---|
| `dureza` | **0,77** → 0,83 tras el incidente | el más duro de los tres junto a infraestructura |
| `control_voceria` | **0,28** | casi no hay con quién concertar |
| `composicion_real` | **51 % protesta legítima** | apenas sobre el umbral de 0,50 → **operar cuesta el doble** |
| región y corredor | epicentro · `C-REF` | el corredor que Minas necesita |

Responder con fuerza es la jugada evidente —hay un herido de la fuerza
pública— y es la más cara, donde menos se puede negociar, sobre el corredor que
otra cartera necesita intacto. Y la mesa aún no se ha constituido: los
mitigadores están al mínimo.

> **H1 no mata a nadie ni abre el punto.** Es una condición inicial, no un
> resultado: el turno 1 empieza con más decisiones sobre la mesa, no con menos.
> Lo custodian `test_h1_llega_aplicado_y_no_resuelve_nada` y
> `test_h1_cae_donde_la_via_pactada_casi_no_existe`.

Al implementarlo se descubrió **C4**, que sigue abierto.

### Del diagnóstico del motor anterior

Los siete problemas de [`docs/historial/mapa_de_palancas.md`](docs/historial/mapa_de_palancas.md):

| | Era | Cómo quedó |
|---|---|---|
| **D1** | La mezcla real de los puntos no cambiaba **nada** | Conectada por dos vías. `test_la_mezcla_real_cambia_el_resultado_de_la_corrida` falla si se desconecta |
| **D2** | El polo de negociación no podía negociar | Interior tiene 4 acciones, incluida la mesa nacional. Los dos mayores movimientos hacia abajo de la movilización ya se disparan |
| **D3** | El dueño del ESMAD no podía asignarlo | `DisponerESMAD` y `Escoltar` |
| **D4** | El frente logístico no podía mover carga | Escolta, caravana, gremios, y la prioridad de combustible como criterio permanente |
| **D5** | La cohesión era una rampa determinista | Solo se cobra de día, y ahora se puede reponer. Va de 0 a 74 según lo que la sala haga |
| **D6** | El paquete detonante no existía | **Los cuatro hechos**, más la jornada nacional en el calendario |
| **D7** | El eje de Vocería no tenía mecánica | Parcial: el anuncio verificado y el parte clasificado sí; el encuadre sigue pendiente |

### Las dos capas de lenguaje natural

Eran **B1** y **B2** de la lista anterior. **Están construidas y probadas con el
modelo puesto.**

| | Era | Cómo quedó |
|---|---|---|
| **capa 4** | el canal de órdenes era un stub que ignoraba el texto | [`src/agents/nlu.py`](src/agents/nlu.py) · los nueve pasos, y **solo el primero usa el modelo**. Resolutor determinista de cuatro estados, validación sin `break`, tope de expansión, elección tipada para las ambigüedades y lectura de vuelta determinista |
| **capa 3** | la esfera pública emitía dos frases fijas | [`src/agents/entorno.py`](src/agents/entorno.py) · seis agentes con su sesgo y su cadencia, una llamada por turno con presupuesto duro |
| **—** | las tres cifras salían cableadas | Salen de las vistas por rol, con los sesgos calibrados |
| **—** | no había dónde poner la llave | `.env` en la raíz, a partir de `.env.example`. `/api/config` dice si está |

**Las dos degradan solas si falta la llave o si el proveedor tarda**, y lo dicen
en el campo `generado_por`. Esa degradación es la prueba operativa de que ninguna
decisión de la simulación se delegó al modelo.

### Las superficies

| | Era | Cómo quedó |
|---|---|---|
| **—** | tres superficies contra la API antigua | Tres: `/tablero` —con la esfera dentro—, `/vista/{rol}` ×8 y `/consola` |
| **—** | el mapa no existía | [`MapaEsquematico.jsx`](web_ui/src/components/MapaEsquematico.jsx) · esquema de líneas, con la forma del nodo diciendo cómo se abrió, un `?` en lo que nadie ha mirado y **un anillo sobre lo que cambió en la última ventana** |
| **—** | el tablero no decía qué hora era | `Estado.reloj()` · cinco jornadas del 11 al 15 de mayo, nueve ventanas, y la noche se ve distinta |
| **—** | un número solo no decía si iba a mejor | `MotorCrisis.deltas()` · ▲▼ contra la ventana anterior, no contra el arranque |
| **—** | cada cifra llevaba su glosa impresa debajo | Marca **(?)** y 30 definiciones formales en [`definiciones.jsx`](web_ui/src/definiciones.jsx) |
| **—** | el reloj de fases lo llevaba el moderador | Lo lleva el sistema, fase por fase |

---

*Última revisión: 2026-08-26 · 59 pruebas en verde · capas de lenguaje natural
activas con `gpt-5-nano`.*
