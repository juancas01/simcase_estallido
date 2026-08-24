# Cómo funciona la simulación

Guía de lectura del motor. Explica **qué pasa en la sala**, **qué calcula el
motor** y **por qué una decisión produce una consecuencia y no otra**, con los
números que el código usa de verdad.

No hace falta leer código para entender este documento, ni leer los 1.500
renglones de la propuesta de diseño. Si después quieres el porqué de cada
decisión de diseño, ese está en
[`propuesta_simulacion_estallido_social.md`](propuesta_simulacion_estallido_social.md).

Todas las cifras que aparecen aquí salen de ejecutar el motor. Se pueden
reproducir con los comandos que se indican.

---

## Índice

1. [La idea en una frase](#1-la-idea-en-una-frase)
2. [Qué pasa en la sala, minuto a minuto](#2-qué-pasa-en-la-sala-minuto-a-minuto)
3. [De qué está hecho el mundo](#3-de-qué-está-hecho-el-mundo)
4. [Qué pasa cuando la sala ordena algo](#4-qué-pasa-cuando-la-sala-ordena-algo)
5. [Los seis motores](#5-los-seis-motores)
6. [Un turno completo, de verdad](#6-un-turno-completo-de-verdad)
7. [Las tres cadenas que hacen que decidir importe](#7-las-tres-cadenas-que-hacen-que-decidir-importe)
8. [Qué NO hace el motor](#8-qué-no-hace-el-motor)
9. [Dónde está cada cosa en el código](#9-dónde-está-cada-cosa-en-el-código)

---

## 1. La idea en una frase

> **La lluvia no reacciona a lo que usted decide. Una movilización sí.**

En la simulación anterior —la inundación de Macondo— el fenómeno estaba
precalculado en un archivo: llovía lo mismo hicieras lo que hicieras, y los
participantes gestionaban las consecuencias.

Aquí no. Cada operación de fuerza, cada cifra desmentida y cada sesión de mesa
**modifica la intensidad de aquello que se intenta contener**. El resultado que
el motor tiene que producir, sin que nadie lo escriba en un guion:

```
        operación de fuerza
                ↓
     probabilidad de incidente
                ↓
          imagen viral
                ↓
       la movilización sube
                ↓
   aparecen nodos nuevos en otras ciudades
                ↓
        hace falta más fuerza
                ↓
   pero la fuerza disponible es la misma
```

**Abrir un corredor por la fuerza puede cerrar dos.** Eso sale de la aritmética,
no de una regla escrita a mano.

---

## 2. Qué pasa en la sala, minuto a minuto

Ocho personas, un moderador, dos horas exactas. **La mesa no lleva pantallas.**

| Bloque | Min | Qué pasa |
|---|---:|---|
| Instalación · turno 0 | 12 | Fichas y sobres sellados. El moderador lee el parte heredado. Cada rol declara en 60 s dónde se ubica: fuerza, negociación o secuencia. |
| **5 turnos de decisión** | 65 | 13 min cada uno |
| **4 interludios nocturnos** | 12 | 3 min cada uno · **sin deliberación** |
| Debriefing | 20 | Incluye la proyección a 72 h |
| Holgura | 11 | Los turnos se pasan. Siempre. |

### El turno de decisión (13 min)

```
1 · APERTURA        1,5 min   el moderador lee qué cambió y qué se rompió
2 · DELIBERACIÓN    6,0 min   el tablero NO se mueve. La sala discute.
3 · ÓRDENES         2,5 min   el moderador transcribe y LEE EL PLAN DE VUELTA
                              con su banda de riesgo. La sala confirma o corrige.
4 · RESOLUCIÓN      1,0 min   el motor ejecuta
5 · CONSECUENCIAS   1,0 min   prensa, redes, gremios, internacional
6 · REGISTRO        1,0 min   la decisión al pliego, con responsable nominado
```

Seis minutos de deliberación es poco **a propósito**: ocho personas no alcanzan a
discutirlo todo, así que tienen que elegir qué discutir. Esa es la competencia
que el ejercicio entrena.

### El interludio nocturno (3 min)

**La noche no se delibera: se sufre.** El moderador no pide órdenes; resuelve lo
que se ordenó de día, y la sala **mira** cómo un corredor abierto por la fuerza se
cierra otra vez, cómo entra un titular, cómo baja el reloj de autonomía.

De día sí se puede *ordenar* operar de noche: se resuelve en el interludio con la
probabilidad de incidente multiplicada por 1,6.

### Las tres pantallas

Ninguna es individual. Dos se proyectan a toda la sala y una es del moderador:

- **`/tablero`** — lo que el Estado tiene por cierto, con la procedencia de cada dato.
- **`/esfera`** — lo que se dice: prensa, redes, internacional, y las tres cifras juntas.
- **`/consola`** — el único teclado. No se proyecta.

La distancia entre las dos proyecciones **es el caso**. Por eso van simultáneas y
nunca en pestañas: la divergencia solo se percibe si se ven a la vez.

---

## 3. De qué está hecho el mundo

Tres niveles espaciales, porque las decisiones se toman en niveles distintos.

### El nodo — un punto de cierre concreto

24 modelados, que representan más de mil reales. Cada uno tiene:

| Variable | Qué es | ¿La ve la sala? |
|---|---|---|
| `dureza` | cuánto cuesta abrirlo por la fuerza [0-1] | estimada |
| `caudal` | fracción de flujo que deja pasar [0-1] | estimada |
| `apoyo_local` | respaldo del barrio al cierre [0-1] | estimada |
| `control_voceria` | **cuánto del punto controla la vocería reconocida** | estimada, con sesgo |
| `masa_presente` | personas en el punto | estimada |
| `modo_apertura` | cerrado, fuerza, concertación, desgaste | sí |
| **`composicion_real`** | **qué hay realmente ahí** | **NUNCA** |

`composicion_real` reparte el punto en tres: protesta legítima, vandalismo
oportunista y estructura organizada. **Nadie la ve** — ni la interfaz, ni los
logs, ni un mensaje de depuración. Se revela en el debriefing y no antes.

### El corredor — una secuencia de nodos

**Un corredor vale lo que su peor nodo.** Su caudal es el mínimo de los caudales
de todos sus puntos. Cinco corredores, de 3 a 5 nodos cada uno.

Esto tiene una consecuencia grande que se explica en §7.

### La región — el reloj

Cuatro regiones. Cada una lleva días de autonomía de combustible, alimentos y
**oxígeno medicinal**, más un contador de `muertes_evitables` que solo crece.

### Las cuatro reservas

Escalares de 0 a 100. Son el equivalente al presupuesto de Macondo, pero **no se
pueden pedir prestadas**.

| Reserva | t=0 | Qué la consume |
|---|---:|---|
| Legitimidad interna | 52 | incidentes con víctimas, imágenes virales, cifras desmentidas |
| Credibilidad de la mesa | 45 | operar el día de una sesión, incumplir lo ofrecido |
| Exposición internacional | 45 | víctimas, corredor humanitario negado, militares en multitudes |
| Cohesión de la mesa | 68 | desautorizaciones, operaciones no informadas |

**Tres se heredan dañadas y una no.** Legitimidad, credibilidad y exposición
vienen así: la sala no las rompió. **Cohesión empieza alta y es enteramente
suya** — todo lo que le pase entre el turno 1 y el 5 lo hicieron los ocho. En el
debriefing es la única serie de la que no pueden desentenderse.

La exposición internacional funciona **al revés**: crece con el daño y arriba es
peor.

### El estado heredado

El motor **no arranca en cero**. El paro lleva quince días cuando la sala entra:

```
24 nodos activos · ~1.000 secundarios agregados por región
ESMAD: 34 de 40 escuadrones ya desplegados · fatiga media 0,55
       solo 6 en reserva
Cauca: 1,8 días de oxígeno
Intensidad de movilización: 61 nacional · 84 en Valle
Mitigadores activos: NINGUNO
```

Esa última línea es la que más rinde: **la primera operación de fuerza que la
sala ordene, si la ordena antes de constituir nada, corre sin ningún descuento**.
Eso no se les dice. Se descubre.

---

## 4. Qué pasa cuando la sala ordena algo

Sigamos una orden real de principio a fin.

> *«Operen el Puente Amarillo con ESMAD.»*

### Paso 1 · El moderador transcribe y el sistema calcula el riesgo

El motor evalúa el riesgo **antes** de que nadie confirme nada:

```
riesgo = base(tipo_unidad)
       × (1 + fatiga_media)
       × (1 + dureza_nodo)
       × (1 + masa_presente / 300)
       × factor_nocturno
       × Π(mitigadores)

P(incidente) = 1 − e^(−riesgo)        ← saturación
```

Con los valores reales del Puente Amarillo (`dureza` 0,84, `masa` 200, fatiga del
ESMAD 0,55) y **ningún mitigador puesto**:

```
riesgo = 0,08 × 1,55 × 1,84 × 1,67 × 1,0 × 1,0 = 0,380
P      = 1 − e^(−0,380)                        = 0,316   →  banda ALTA
```

**Esto es lo que el moderador lee en voz alta a la sala**, antes de ejecutar:

> «Riesgo **alto**, probabilidad 32 %. Mitigadores ausentes: los seis. ¿Confirman?»

Ese momento no es un trámite. Es el punto donde la sala oye su propia decisión
con su precio, y con frecuencia la cambia.

### Paso 2 · Si la sala hubiera constituido primero

Con reglas escritas, identificación de agentes, registro audiovisual, dupla de la
Defensoría presente y concertación con la Alcaldía:

```
factor de mitigación = 0,70 × 0,85 × 0,80 × 0,75 × 0,80 = 0,286
P = 1 − e^(−0,380 × 0,286)                              = 0,103   →  banda MEDIA
```

**De 32 % a 10 %.** Ninguno de esos cinco mitigadores cuesta un escuadrón ni un
peso: son decisiones que alguien tenía que tomar en el turno 1.

> Esto es lo que convierte el estándar de derechos en un instrumento y no en un
> discurso. El rol sin voto y sin fuerza —la Defensoría— es el que más reduce la
> probabilidad del peor resultado. Se descubre haciendo la cuenta.

### Paso 3 · Pero el estándar no rescata a quien no lo necesitaba

Misma orden, con militares fatigados, de noche:

```
riesgo bruto = 4,20        P = 0,98   (el techo)
con TODOS los mitigadores  P = 0,70
```

A esa altura la curva ya saturó. **El estándar protege a quien ya venía operando
con cuidado y no rescata a quien no.** Esa asimetría es deliberada.

### Paso 4 · Se resuelve la tirada

El motor saca un número con la semilla registrada. Si cae por debajo de P, hubo
incidente: se calculan víctimas, y si la imagen circula (55 % sin registro
audiovisual propio, 25 % con él).

La corrida entera se puede repetir en el debriefing cambiando una sola decisión,
porque la semilla queda anotada.

### Paso 5 · ¿Sobre quién cae el costo?

```python
atribuible = bool(responsable_nominado) and banderas.registro_escrito
```

- **Con** registro escrito y un nombre → el costo cae sobre quien firmó.
- **Sin** él → se reparte sobre los ocho y **la cohesión baja 8 puntos**.

Es exactamente la tensión del Ministro de Defensa: *le preocupa que el sector
cargue en solitario el costo de decisiones tomadas colectivamente en esta sala*.

### Paso 6 · El mundo reacciona

Si hubo víctima, la movilización sube. Si la imagen circuló, sube más. Si la
operación ocurrió el día de una sesión de mesa, la credibilidad del canal cae 12
puntos — y eso lo paga el Ministro del Interior, que no ordenó nada.

---

## 5. Los seis motores

Cada uno con su propio paso, invocados en orden fijo.

### 5.1 Movilización — el adversario reflexivo

**Si solo se implementa uno, es este.** Lleva la `intensidad_movilizacion` de 0 a
100 y la realimenta sobre el mundo.

Sube con: incidente mortal (+20), imagen viral (+8), militares en control de
multitudes (+8), jornada nacional (+10), turno sin acuerdo (+1,5).
Baja con: acuerdo verificable (−8), apertura concertada (−4), turno sin
incidentes (−2).

Dos reglas que evitan que la variable se rompa:

- **Rendimientos decrecientes.** El n-ésimo evento del mismo tipo vale
  `base × 0,6^(n−1)`. El segundo muerto de la semana mueve menos que el primero.
- **Decaimiento proporcional al nivel**, no constante. Con un decaimiento fijo
  de −2, dos incidentes la dejaban clavada en 100 y a partir de ahí todas las
  decisiones daban igual — lo peor que le puede pasar a la variable central.

Y la intensidad realimenta: nodos nuevos, nodos existentes más duros, más gente
en cada punto.

> **Un matiz que cuesta ver:** `intensidad` **sube** con el uso de la fuerza —es
> rabia contra el Estado—, mientras `apoyo_local` al cierre **baja** con la
> escasez prolongada —la gente quiere comer—. No son la misma variable con signo
> contrario. Por eso el esquema humanitario municipal del Alcalde es la única vía
> de apertura que no consume ninguna reserva.

### 5.2 Fuerza e incidentes

Ya explicado en §4. Lo que hay que retener:

- 40 escuadrones de ESMAD, **6 en reserva** al empezar, fatiga media 0,55.
- La fatiga sube 0,15 por turno desplegado y baja 0,30 en relevo.
- Cada instalación declarada crítica inmoviliza 2 unidades. **Es la aritmética
  que enfrenta a Minas con Defensa**: la protección permanente resta exactamente
  de la capacidad de desbloqueo.

### 5.3 Apertura y reapertura

El corazón pedagógico. Tres vías con economías radicalmente distintas:

| Vía | Tarda | Caudal | ¿Reabre? | Consume |
|---|---|---|---|---|
| **Fuerza** | 1 turno | 0,70–1,00 | **sí, esa misma noche** | legitimidad, credibilidad, exposición |
| **Concertación** | 2 turnos | `0,9 × control_voceria` | no, mientras el acuerdo se cumpla | credibilidad si se incumple |
| **Desgaste** | 4+ turnos | 0,50–0,80 | no | nada |

**La trampa de la concertación.** El caudal es proporcional a `control_voceria`.
En la Glorieta La Ceiba, con vocería de 0,68:

```
caudal = 0,9 × 0,68 = 0,61
```

Negociar con un vocero que controla el 40 % produce una apertura del 36 % que se
anuncia como éxito y se desmiente sola. Es la pregunta estratégica del Ministro
del Interior con respuesta numérica: *con quién se negocia cuando quien tiene
vocería no controla el bloqueo*.

El escenario reparte los nodos a propósito:

```
N010 Acceso Hospital Universitario   vocería 0,82   dureza 0,31   ← fácil de pactar
N005 Cruce de Villarrica             vocería 0,79   dureza 0,48
...
N013 Portería de la refinería        vocería 0,28   dureza 0,77
N003 Puente Amarillo                 vocería 0,22   dureza 0,84   ← ni pactar ni forzar
N022 Loma del Oriente                vocería 0,19   dureza 0,75
```

Los nodos duros son justamente aquellos donde no hay con quién hablar.

### 5.4 Información — verdad, estimaciones y versión

Tres capas, y el ejercicio vive en la distancia entre ellas.

Sobre el Puente Amarillo, cuya composición real tiene **0,33 de estructura
organizada**, así estima cada fuente:

```
VERDAD (nadie la ve)              0,33
  Inteligencia de Defensa         0,60   ← casi el doble
  Dupla de la Defensoría          0,41   ← la más cercana
  Parte operacional               0,42
  Parte municipal de la Alcaldía  0,06   ← casi cero
```

**Los sesgos van en direcciones opuestas a propósito.** Defensa sobreestima la
estructura organizada; la Alcaldía la subestima. Y la Defensoría, que es la más
precisa, **solo cubre 3 nodos por turno**: verificar aquí es no verificar allá.

De ahí el **error doble**, y ninguna de las dos salidas es segura:

- Tratar como organizado un nodo que es sobre todo protesta legítima → fuerza
  sobre población civil → costo máximo de legitimidad y exposición.
- Tratar como protesta legítima un nodo con estructura organizada → se negocia
  con quien no controla nada → el acuerdo se incumple visiblemente.

### 5.5 Abastecimiento — el reloj y el oxígeno

Los días de autonomía **bajan solos y solo suben si alguien abre un corredor**.

El oxígeno medicinal es la única variable que convierte logística en muertes, y
no es independiente: es el extremo de una cadena.

```
corredor abierto → entra combustible → hay diésel para carrotanques
                                     → y para plantas de emergencia del hospital
                                     → las plantas sostienen la producción
                                     → hay oxígeno en la UCI
                                     → no se muere quien no tenía que morirse
```

Cauca empieza con 1,8 días. Si la sala no hace nada:

```
t=0   1,80 d
T1    0,80 d      0 muertes
T2   −0,32 d      5 muertes
T3   −1,57 d     21 muertes
T4   −2,00 d     37 muertes
T5   −2,00 d     53 muertes
```

> **Regla de diseño que hubo que hacer cumplir a la fuerza:** toda región debe
> tener al menos un corredor humanitario que la sirva. Sin eso, sus muertes son
> inevitables **haga lo que haga la sala** — y eso no es un dilema, es un guion
> que castiga. Se detectó midiendo: las cinco estrategias daban exactamente las
> mismas 147 muertes porque Buenaventura no tenía ninguno. Hoy el cargador falla
> ruidosamente si alguien lo rompe.

El pánico es endógeno: si el Ministro de Minas difunde el calendario de
agotamiento —que la mesa suele pedirle—, el consumo sube un 35 % y el agotamiento
llega antes. **Entregar el reloj cambia el reloj.**

### 5.6 Esfera pública

Consolida lo que dicen los agentes de entorno y calcula el `encuadre_dominante`:
víctimas y militares empujan hacia *represión*; nodos nuevos y desabastecimiento
hacia *desorden*; sesiones con acuerdo hacia *negociación*; aplazamientos hacia
*abandono*.

**El mismo hecho cuesta distinto según el encuadre vigente**, y el encuadre se
puede disputar con vocería.

*(Los seis agentes de IA que pueblan esta capa todavía no están conectados.)*

---

## 6. Un turno completo, de verdad

Salida real del motor. Reproducible con:

```bash
uv run python scripts/correr_ejercicio.py --estrategia constituida
```

```
  t=0 · 24 nodos · intensidad 61 · autonomía mínima 1.8 d (Cauca)
  ESMAD en reserva: 6/40 · fatiga media 0.55
  Mitigadores activos: 0/6 — nada se ha constituido

── TURNO 1 (día) ─────────────────────────────────────────────
  ok FijarRegistroEscrito: Registro escrito vigente. A partir de ahora cada
     incidente es ATRIBUIBLE a quien firmó, en vez de repartirse sobre los ocho.
  ok ExigirEstandaresEmpleo: Estándares adoptados. Tres mitigadores activos.
  ok AdoptarCriterioPriorizacion: Criterio único de priorización adoptado.
  ok DesplegarDuplas: Verificados 3 nodos.
   T1 (dia) · nodos abiertos 0/25 · intensidad 59 · legitimidad 52 ·
              autonomía mínima 1.3 d (Cauca) · muertes evitables 0
   · noche: sin novedad

── TURNO 3 (día) ─────────────────────────────────────────────
  ok AbrirMesaLocal: Mesa instalada en Cruce de Villarrica. La concertación
     necesita otro turno para producir apertura.
  ok OperarNodo: Operación sobre Peaje del Puerto: nodo despejado. Sin incidentes.
       riesgo mostrado P=12% · tirada 0.737 · atribuible=True
   · noche: 1 nodo(s) volvieron a cerrarse; 30 muertes evitables
```

Fíjate en tres cosas del turno 1: **no abre ningún nodo** —las cuatro acciones son
constitutivas—, la intensidad **baja** de 61 a 59 porque no hubo incidentes, y sin
embargo el reloj de Cauca cae de 1,8 a 1,3 días. Constituirse cuesta tiempo que
el reloj no perdona.

Y en el turno 3: la operación se ejecuta con P=12 % en vez de 32 %, porque los
mitigadores del turno 1 están puestos, y sale `atribuible=True` porque hay
registro escrito y un nombre.

### La proyección a 72 horas

Terminado el turno 5, el motor corre **tres turnos más sin órdenes** y proyecta el
estado. No es un marcador: es **el país que la sala entrega**.

Existe porque en el turno 5 la fuerza saldría gratis —un nodo abierto por la
fuerza reabre en 1-2 turnos y ya no quedan turnos—, y una sala que lo advierta
podría desatar al final todo lo que evitó antes. La proyección cierra ese
incentivo y, sobre todo, instala la pregunta con la que conviene abrir el
debriefing: **¿esto se sostiene sin ustedes?**

---

## 7. Las tres cadenas que hacen que decidir importe

### Cadena 1 · La fuerza no abre corredores

Un corredor vale lo que su peor nodo, y un nodo abierto por la fuerza reabre de
noche. Combinando ambas: **con cinco turnos, la fuerza casi nunca sostiene todos
los nodos de un corredor a la vez.** Medido sobre el anillo hospitalario:

```
      N010    N011    N012   →  caudal del corredor
T1    0,80    0,72    0,00   →  0,00
T2    0,80    0,00    1,00   →  0,00      (N011 reabrió de noche)
T3    0,99    0,00    1,00   →  0,00
T4    0,99    0,00    1,00   →  0,00
T5    0,99    0,70    1,00   →  0,70      (por fin, en el último turno)
```

La vía concertada abre el mismo corredor **en el turno 2 y lo sostiene**. Este
resultado no se diseñó: salió de la aritmética, y refuerza la tesis del caso.

### Cadena 2 · Constituirse cuesta turnos y los devuelve multiplicados

Las seis acciones constitutivas no abren ningún corredor, no aparecen en el
tablero y parecen burocracia mientras el país arde. **La mayoría de las salas se
las salta y paga entre el turno 4 y el 6**, cuando hay tres cifras en disputa, dos
operaciones que Interior no conocía y ningún renglón del pliego con un nombre.

Lo que cuesta no haberlas tomado:

| Se opera sin… | Precio |
|---|---|
| reglas escritas | P(incidente) sin descuento — 32 % en vez de 10 % |
| registro escrito | el costo del incidente se reparte · cohesión −8 |
| protocolo de verificación | cada desmentido cuesta 4 de legitimidad |
| protocolo de vocería | cohesión −5 **por turno** |
| criterio de priorización | cohesión −3 **por turno** |

Ninguna está bloqueada y ninguna es obligatoria. **Un bloqueo duro se siente como
un riel; un precio se siente como una consecuencia.**

### Cadena 3 · Nadie puede resolver su frente solo

Trece de las acciones no se pueden ejecutar solas. Cuando falta el requisito, el
motor devuelve **quién puede habilitarlo**, no un rechazo seco:

> «La caravana requiere escolta. Corresponde al Director General de la Policía
> Nacional (acción A2). Sin escolta la acción queda en espera condicional.»

Eso empuja la conversación de vuelta a la sala, que es donde el ejercicio la
quiere.

---

## 8. Qué NO hace el motor

- **No decide si la respuesta fue correcta.** Calcula consecuencias. El juicio es
  del debriefing, y es de las personas.
- **No llama a ningún modelo de lenguaje.** Corre entero sin clave de API. Si
  algún día no puede, la arquitectura está mal.
- **No narra incidentes a la existencia.** La probabilidad se calcula en código
  desde el estado, se muestra antes de decidir y se resuelve con semilla
  registrada. Un modelo no puede decidir que hubo un muerto.
- **No revela `composicion_real`** — ni en la interfaz, ni en los logs, ni en un
  mensaje de depuración. Hay una prueba automática que lo verifica.
- **No cuantifica culpa** ni produce veredictos sobre hechos históricos. El paro
  de 2021 tiene víctimas reales y responsabilidades en discusión judicial.

---

## 9. Dónde está cada cosa en el código

```
src/engine/parameters.py     todas las constantes. Si un número gobierna algo,
                             vive aquí y en ningún otro sitio.
src/engine/state.py          nodos, corredores, regiones, reservas, banderas
                             y `vista_publica()`, la única salida autorizada
src/engine/loader.py         construye t=0 desde data/ y verifica invariantes
src/engine/mobilization.py   §5.1 · el adversario reflexivo
src/engine/force.py          §5.2 · riesgo, mitigadores, incidentes
src/engine/aperture.py       §5.3 · las tres vías
src/engine/information.py    §5.4 · verdad, estimaciones, denuncias
src/engine/supply.py         §5.5 · el reloj y el oxígeno
src/engine/actions.py        las acciones de los ocho roles
src/engine/simulation.py     el bucle de turnos

data/escenario/              el caso, en datos y no en código
scripts/correr_ejercicio.py  el motor completo sin interfaz, en milisegundos
tests/test_invariantes.py    18 verificadores sin modelo, en 0,1 s
web_ui/src/components/       las tres superficies
```

### Para entenderlo por dentro, en este orden

1. **`scripts/correr_ejercicio.py`** — corre una estrategia y mira la salida.
2. **`src/engine/state.py`** — de qué está hecho el mundo.
3. **`src/engine/force.py`** — la función `evaluar_riesgo`, que es el cálculo más
   importante del motor.
4. **`src/engine/simulation.py`** — el método `paso()`, que ordena todo lo demás.

### Comandos útiles

```bash
# Un ejercicio completo, con detalle turno a turno
uv run python scripts/correr_ejercicio.py --estrategia constituida

# Comparar las cinco estrategias — el criterio de calibración
uv run python scripts/correr_ejercicio.py --comparar

# Cambiar la semilla y ver cuánto es ruido y cuánto es señal
uv run python scripts/correr_ejercicio.py --semilla 7

# Las pruebas
uv run pytest -q
```

---

## Una advertencia final

**Ningún coeficiente de este motor está medido.** Son convenciones declaradas,
elegidas para que ninguna estrategia pura gane. El criterio de calibración es por
comportamiento y no por realismo, y la herramienta que lo mide es
`--comparar`.

**La primera corrida con personas es una medición, no un ejercicio**, y conviene
decirlo antes de empezar.
