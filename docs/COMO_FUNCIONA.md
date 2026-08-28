# Cómo funciona — del juego al motor

Cómo está construido el simulador de la [propuesta](propuesta.md), leído
siempre en el mismo orden: **primero lo que pasa en la sala, después el cálculo
que lo produce.**

No hace falta saber programar para leerlo. Cada sección tiene la misma forma:

> **En la sala** · qué viven las nueve personas
> **En el motor** · qué cálculo lo produce, con los números reales
> **En el código** · qué archivo y qué función, para poder ir a mirar

**Si lo que busca es el código** —cómo está organizado el repositorio, cómo
añadir una acción, qué convenciones hay—, ese es
[`EL_CODIGO.md`](EL_CODIGO.md).

Este documento describe **el motor que corre hoy**. El anterior está en
[`historial/como_funciona_motor_v1.md`](historial/como_funciona_motor_v1.md), y
el diagnóstico del que salió esta versión, en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).

---

## Índice

**A · La sala**

1. [Qué se está simulando, y qué no](#1-qué-se-está-simulando-y-qué-no)
2. [Un turno completo, de principio a fin](#2-un-turno-completo-de-principio-a-fin)
3. [Las cuatro superficies, en tres rutas](#3-las-cuatro-superficies-en-tres-rutas)

**B · Los seis motores, desde la sala**

4. [El adversario reflexivo](#4-el-adversario-reflexivo)
5. [La fuerza y el riesgo](#5-la-fuerza-y-el-riesgo)
6. [Las tres vías de abrir un camino](#6-las-tres-vías-de-abrir-un-camino)
7. [El reloj y el oxígeno](#7-el-reloj-y-el-oxígeno)
7 bis. [La infraestructura relevante](#7-bis-la-infraestructura-relevante)
8. [La información: verdad, vistas y denuncias](#8-la-información-verdad-vistas-y-denuncias)
9. [La mesa: reservas, banderas y acuerdos](#9-la-mesa-reservas-banderas-y-acuerdos)

**C · Lo que la sala puede hacer**

10. [Las treinta y nueve acciones](#10-las-treinta-y-nueve-acciones)
11. [Las nueve vistas privadas, por dentro](#11-las-nueve-vistas-privadas-por-dentro)
12. [Los siete arreglos, medidos](#12-los-siete-arreglos-medidos)
13. [Cómo comprobarlo uno mismo](#13-cómo-comprobarlo-uno-mismo)

---
---

# A · La sala

## 1. Qué se está simulando, y qué no

Nueve personas, dos horas, y **un país que responde a lo que deciden**. No hay
marcador, no hay respuesta correcta y no hay una jugada que gane.

### Lo que el ejercicio pone a prueba

No es si la sala sabe de orden público. Es si **nueve mandatos legítimos que
miran cosas distintas pueden producir una sola línea de acción** en cinco
turnos, con información incompleta y repartida.

De ahí salen las tres tensiones que el motor está construido para sostener:

| | La tensión | Cómo se siente en la sala |
|---|---|---|
| **1** | abrir el país **o** salvar a la gente | los caminos y el oxígeno se piden fuerza mutuamente |
| **2** | actuar rápido **o** actuar bien | la fuerza abre en un turno y reabre esa noche; concertar tarda dos y aguanta |
| **3** | decidir con lo que se sabe **o** gastar en saber | verificar cuesta una dupla que hace falta en otro sitio |

**Ninguna se resuelve. Se administran**, y el debriefing trata de cómo cada sala
las administró.

### Lo que el motor sí modela

```
el territorio ......... 10 puntos de cierre, 4 corredores, 4 regiones
la fuerza ............. escuadrones, fatiga, riesgo de incidente
el abastecimiento ..... oxígeno, combustible, alimentos — con su reloj
la calle .............. una movilización que REACCIONA a lo que se decide
la información ....... una verdad oculta y cuatro estimaciones sesgadas
la mesa ............... cuatro reservas que se gastan y se recomponen
```

### Lo que NO modela, y por qué

Esto importa tanto como lo anterior. La regla que gobierna el alcance:

> **Se modela lo que la sala puede cambiar con una decisión en cinco turnos.**
> Todo lo demás es contexto y va en la ficha, no en el motor.

Por eso no hay economía nacional, ni opinión pública individual, ni
procedimientos judiciales, ni geografía real. **El país del mapa está
inventado** —Valcanto, con sus dos mares y su puerto— y no tiene escala: la
geometría sitúa, no mide. No hay distancias ni tiempos de desplazamiento porque
el motor no los tiene.

> **La silueta y la red vial, en cambio, son reales.** Salen de datos
> cartográficos abiertos de una costa de verdad —su línea de costa y sus
> carreteras principales—, normalizadas al lienzo y simplificadas. **Qué costa
> es no se registra en ninguna parte**, y es deliberado: el territorio del
> ejercicio es ficticio, y saber a qué se parece el dibujo no aporta nada al
> material —solo invita a buscarle correspondencias que no existen. Es el mismo
> trato que Macondo tuvo con Mocoa: lo prestado es el trazo, no el lugar.
>
> Se usan datos reales por una razón práctica: **un país inventado a mano se
> nota.** Las costas de verdad tienen estuarios, cabos y entrantes, y las redes
> viales de verdad tienen troncales que concentran y comarcales que rodean —
> cosas que nadie dibuja por intuición. Y lo que hace falta es que la sala mire
> un país, no un diagrama.

> **El mapa era un esquema de líneas y ya no lo es.** Aquel decía la verdad
> sobre la topología —un corredor ES una secuencia ordenada de puntos— y no
> decía nada sobre el país: diez motas sobre un lienzo vacío, sin costa, sin
> puerto y sin forma. Una sala que mira eso durante trece minutos no llega a
> preguntarse dónde está. La topología sigue siendo la información; lo que ha
> cambiado es que ahora hay un sitio donde ponerla.

> **La red vial va casi transparente, y eso es el diseño.** Las carreteras no
> son la información: son el suelo sobre el que se lee la información. Tienen
> que estar —un bloqueo flotando sobre un polígono de color no se lee como una
> carretera cortada— y tienen que callarse. Lo que resalta son los corredores y
> los puntos de cierre.
>
> Y **cada corredor se dibuja por el camino que existe**: su trazado se rutea
> con Dijkstra sobre la red real y se guarda en el escenario. Antes se unían sus
> puntos con una curva suave, y esa curva afirmaba algo falso —que entre un
> bloqueo y el siguiente la vía pasa por ahí—. Ahora dos puntos que en línea
> recta parecen vecinos pueden estar a media vuelta por carretera, y el mapa lo
> enseña en vez de esconderlo.
>
> **Los diez puntos de cierre están sobre vértices reales de esa red**, no en un
> descampado: un bloqueo está en una carretera. Se siembran a lo largo del
> trazado ya ruteado de su corredor, y no al revés — colocarlos primero a ojo y
> rutear después convertía cada hueco del grafo en media vuelta al país dibujada
> como si fuera el corredor.

Y por eso mismo **no hay un rol de «la protesta»**. La movilización es un
adversario reflexivo del motor, no una persona en la mesa: el ejercicio es sobre
la coordinación del Estado, y sentar a alguien a jugar la protesta lo convertiría
en otra cosa.

### La regla que ordena la construcción

> **El LLM traduce. El motor decide, valida, ejecuta y reporta.**

El ejercicio **corre entero sin llave de API**. Las nueve vistas son proyecciones
deterministas del estado, no texto generado. Esa degradación no es una comodidad
de desarrollo: es la prueba operativa de que ninguna decisión de la simulación
está delegada a un modelo.

> Dónde vive cada cosa en el repositorio, y cómo añadirle algo, está en
> [`EL_CODIGO.md`](EL_CODIGO.md).

---

## 2. Un turno completo, de principio a fin

### En la sala

La jornada dura **quince minutos de mundo real** y se parte en dos tramos con
reglas opuestas —trece de día en que se ordena y dos de noche en que no—, sin más
divisiones. **Cómo se juega ese tramo está en
[`propuesta.md` §6.2](propuesta.md#62-la-jornada-dos-tramos-no-siete-fases);**
aquí está lo que hace que la frontera sea real y no un rótulo.

**La garantiza el servidor.** De noche el cuadro de
órdenes se atenúa y sus botones se desactivan; una orden que llegue igualmente
—una pestaña vieja, un doble clic tardío— recibe un 409. Una regla que el
software garantiza vale más que una que el software recomienda.

**El ritmo lo lleva el sistema.** Se pulsa «Iniciar» una vez y a partir de ahí la
jornada se cierra sola al minuto trece y la siguiente se abre sola dos minutos
después. Quedan cuatro mandos, y son para lo que el reloj no puede prever:

| Mando | Para qué |
|---|---|
| **Pausar** | una interrupción real. El tiempo del ejercicio no corre mientras la sala no está en el ejercicio, y el número se congela en las diez pantallas a la vez |
| **Cerrar el día** | la sala terminó antes de los trece minutos |
| **Empezar la jornada siguiente** | ya leyeron las consecuencias y no hace falta esperar |
| **Reiniciar el reloj** | deja la cuenta a cero. **No rebobina el mundo** |

**No hay moderador como figura aparte.** Quien opera la consola —puede ser uno de
los nueve— solo transcribe.

### En el motor

Los seis bloques de `paso()`, en orden fijo. **Ese orden es lo que hace la corrida
reproducible.**

```
0 · CALENDARIO     lo que ocurre sin que nadie lo decida
                   (la jornada nacional del turno 3)

1 · CONDICIONALES  «en cuanto la Defensoría verifique ese punto, opérenlo»
                   caducan a los 3 turnos; una condición que revienta descarta
                   esa orden y NO tumba el turno

2 · ACCIONES       validar() → ejecutar() por cada acción de la cola
                   PROHIBIDO break al primer problema

3 · NO DECIDIR     si la cola venía vacía: intensidad +1,5 · legitimidad −3
                   dureza +0,03 en TODOS los puntos · encuadre → abandono

4 · BANDERAS       lo que cuesta no haberse constituido.
                   SOLO EN TURNOS DE DÍA (ver §12)

5 · SUBSISTEMAS    aperture.step()          aperturas, reaperturas, desgastes
                   aperture.revisar_acuerdos()  ¿se cumplió lo pactado?
                   supply.step()            el reloj y las muertes
                   presion_por_escasez()    hambre → apoyo local, intensidad
                   information.paso_denuncias()  las que nadie miró, estallan
                   mobilization.step()      decaimiento y realimentación
                   force.paso_fatiga()      la fatiga de las unidades

6 · UMBRALES       los seis umbrales duros, el ultimátum gremial y el encuadre
```

**El turno de día y el interludio de noche llaman al mismo `paso()`.** Lo que
cambia de noche: no se encolan órdenes, el riesgo se multiplica por 1,6, las
reaperturas por fuerza ocurren ahí, y **no se cobra la ausencia de banderas**
—porque la sala no está decidiendo—.

Un ejercicio completo son **nueve pasos** (5 días y 4 noches) más **tres de
proyección**.

### En el código

[`simulation.py:114`](../src/engine/simulation.py) · `MotorCrisis.paso()`

> **Dos propiedades no negociables.** `paso()` es la única forma de que el tiempo
> avance —no hay temporizadores paralelos que muten el estado— y una acción que
> lanza una excepción se convierte en un resultado fallido, no en un turno roto.

---

## 3. Las cuatro superficies, en tres rutas

### En la sala

| Superficie | Quién la ve | Qué responde |
|---|---|---|
| **Tablero general** | proyectado, toda la sala | **qué está pasando** |
| **Esfera pública** | barra lateral del tablero | **qué se dice** |
| **Vista privada** ×8 | cada uno en su dispositivo | **cuánto, dónde exactamente, desde cuándo** |
| **Consola** | quien transcribe | dónde entran las órdenes |

**La distancia entre el tablero y la esfera pública es el caso**, y solo se
percibe si se ven a la vez. Nunca en pestañas.

> **Por eso la esfera no tiene ruta propia.** La tuvo, para montajes de dos
> proyectores. Mientras la tuvo, la doctrina dependía de que quien monta la sala
> hiciera lo correcto: bastaba proyectar una de las dos sola para perder lo que
> hay que enseñar. Al vivir dentro del tablero, el montaje incorrecto deja de ser
> posible — **una regla que el software garantiza vale más que una que el
> software recomienda.**

### En el motor

**El tablero da grano grueso; la vista privada da grano fino, y no se repiten.**

```
EL TABLERO dice:        Las Cumbres · abastecimiento ● ROJO
LA VISTA DE MINAS dice: Las Cumbres · oxígeno 1,8 d  ↓ 0,4 sin ingreso mañana
                                      combustible 2,8 d · alimentos 2,5 d
```

Esto está garantizado por construcción: `vista_publica()` devuelve
`region.semaforo` —un texto de tres valores— y **nunca los días**. Los días solo
existen en la vista de Minas.

**Y el detalle no migra.** Aunque Minas diga el número en voz alta, el número
sigue viviendo en su vista. Si se fijara en el tablero, el rol se consultaría una
vez y después sobraría; al quedarse ahí, **cada turno vuelve a ser necesario**,
porque el número cambió y solo él tiene el nuevo.

### En el código

| Superficie | Endpoint | Función |
|---|---|---|
| Tablero | `GET /api/tablero` | [`state.py:441`](../src/engine/state.py) · `Estado.vista_publica()` |
| Esfera pública | `GET /api/esfera` | [`api/main.py`](../src/api/main.py) · la sirve el mismo tablero |
| Vista privada | `GET /api/vista/{rol}` | [`views.py`](../src/engine/views.py) · `vista()` |
| Consola | `POST /api/consola/*` | [`api/main.py`](../src/api/main.py) |

**Tres cosas están garantizadas por construcción y no por disciplina:** la vista
pública jamás expone la mezcla real de un punto, las nueve vistas privadas tampoco
la exponen, y **solo Minas ve los días exactos**.

### Cómo el tablero señala un problema sin decir qué hacer

Es la tensión que gobierna el diseño de la superficie 1, y no tiene término
medio posible:

| Si el tablero… | Lo que pasa |
|---|---|
| dice «abra el corredor hospitalario» | el ejercicio se acabó: el tablero pensó por la sala |
| es un muro de números iguales | nadie se entera de nada en trece minutos de deliberación |

La salida no es un punto intermedio: es **cambiar de mecanismo**.

> **SALIENCIA, NO INSTRUCCIÓN.**

Cuatro palancas, y las cuatro enuncian hechos. Ninguna nombra un remedio.

**1 · El cambio, no el nivel.** `Legitimidad 41` no le dice nada a quien no
memorizó el punto de partida. `41 ▼9` le dice que algo de anoche costó nueve
puntos. Es la señal más barata del tablero y la que más apunta.

`MotorCrisis.deltas()` compara contra el paso **anterior**, no contra el arranque:
si acumulara, dejaría de señalar en el turno 3.

**2 · El plazo.** «Turno 3» es neutro. «Jornada 3 de 5» es una presión — y una
concertación que tarda dos turnos en rendir no cabe en la jornada 5. El reloj
dice cuánto queda; qué hacer con eso es de la sala.

`Estado.reloj()` vive en el motor y no en la interfaz. Cuatro superficies
calculando cada una su propia hora son cuatro relojes, y con el tablero
proyectado junto a nueve dispositivos la discrepancia se ve el primer turno.

**3 · El orden.** Corredores y regiones van **peor primero**. El ojo aterriza
arriba a la izquierda y ahí está el problema, sin que nadie lo señale. La
memoria espacial que se pierde la devuelve el mapa.

**4 · Lo que falta, contado.** Puntos que nadie ha verificado, denuncias
abiertas, decisiones sin responsable — en fracción, porque `24` no dice si la
sala avanza y `9/24` tres turnos después sí.

> **La distancia entre «3 puntos sin verificar» y «verifique P7» es la distancia
> entre un ejercicio y un tutorial.**

**5 · Dos niveles, y seis lecturas en cada uno.** El mapa del país tiñe cada
región de su **estado de bloqueo** —cuántos de sus puntos no dejan pasar nada— y
al posarse encima entrega el promedio de sus puntos. Un clic acerca la región y
enseña sus puntos con nombre y los corredores que la cruzan.

| | Punto | Región |
|---|---|---|
| **Paso** | banda del caudal | media de sus puntos |
| **Dureza** | cinco peldaños | media |
| **Gente en la calle** | ≈420 personas | total ≈1.600 · ≈260 por punto |
| **Días de cierre** | 15 días | 11 de media · el más antiguo, 15 |
| **Apoyo del barrio** | cinco peldaños | media |
| **Vocería reconocida** | tres bandas | media |

Las cifras las calcula el motor (`territory.py`), no la pantalla. **Un promedio
por región calculado en JavaScript es un promedio que nadie verifica nunca** —y
`PENDIENTES.md · B9` documenta lo que cuesta eso.

Y **ninguna sale como el número interno.** Un nivel se interpreta; un número se
optimiza. Las dos únicas que llevan cifra son las dos que se cuentan de verdad:
personas y días. La misma frontera que en el resto del tablero separa
«Legitimidad: alta» de «Muertes evitables: 3».

> **La vocería lleva tres bandas y no cinco, y es deliberado.** Es el dato
> exclusivo de Interior y del Alcalde, y la lectura de Interior va sesgada +0,20:
> con cinco bandas de 0,20 el sesgo sería exactamente un peldaño y el tablero lo
> desmentiría solo. Con tres, la banda gruesa coincide casi siempre y **la
> discrepancia sigue siendo cosa de la mesa**, que es donde tiene que resolverse.

**6 · Lo que pasó en cada punto.** El mapa dibuja un anillo sobre los puntos
donde ocurrió algo en la última ventana, y se apaga en la siguiente. Es la misma
regla del delta aplicada al territorio: *un punto rojo dice que está cerrado; un
punto rojo con anillo dice que se cerró anoche, que es otra conversación.*

| Anillo | Qué ocurrió |
|---|---|
| rojo | volvió a cerrarse de noche · se operó con incidente · se incumplió un acuerdo |
| ámbar | se operó, sin incidente |
| verde | se abrió, o se acordó paso seguro |
| azul | alguien lo verificó en campo |

> **El mapa cuenta lo que se hizo; no dónde está la fuerza.**
>
> Que se operó en un punto es público: sale en las noticias esa misma tarde, y
> la sala necesita verlo para saber si su decisión surtió efecto. La
> **ubicación, la asignación y la fatiga** de cada escuadrón existen en el motor
> y viven en la vista de la Dirección General de la Policía. Si aparecieran en
> el tablero, uno de los nueve roles dejaría de hacer falta.

Las dos reglas —que el mapa no diga dónde está la fuerza, y que el anillo no se
acumule de una ventana a la siguiente— son invariantes del motor, no del
componente que dibuja.

**Y el delta no abre una puerta trasera.** `_indicadores()` se restringe a lo que
`vista_publica()` ya serializa: un delta calculado sobre la mezcla real de un
punto la filtraría igual de bien que mostrarla.

Los hechos del mapa llevan **lista blanca de campos** por la misma razón: un
evento del motor puede llevar dentro cualquier cosa —`veraz`, por ejemplo— y
basta añadir un campo nuevo para abrir una filtración sin darse cuenta. Lo que no
esté en `CAMPOS_DE_HECHO` no sale.

---
---

# B · Los seis motores, desde la sala

## 4. El adversario reflexivo

### En la sala

> **La lluvia no reacciona a lo que usted decide. Una movilización sí.**

Cada operación de fuerza, cada cifra desmentida y cada sesión de mesa modifica la
intensidad de aquello que se intenta contener. La sala no puede discutir esto —
solo verlo ocurrir.

### En el motor

Una sola variable, `intensidad_movilizacion`, nacional y por región, con **dos
reglas que evitan que se rompa**:

```
SUBE (con rendimientos decrecientes: base × 0,6^(n−1))
  incidente mortal        +20     militares en multitudes  +8
  imagen viral             +8     jornada nacional        +10
  acuerdo incumplido       +6     escolta atacada          +7
  cifra desmentida         +4     turno sin acuerdo       +1,5

BAJA (sin rendimientos decrecientes: un acuerdo no vale menos por ser el segundo)
  acuerdo verificable      −8     contraprestación tramitada −6
  apertura concertada      −4     denuncia desmentida        −3
  turno sin incidentes     −2

DECAIMIENTO cada paso:  ×0,96   (proporcional al nivel, no constante)
```

**Por qué los rendimientos decrecientes.** Arranca en 61 y un incidente mortal
suma 20: con dos incidentes quedaría clavada en 100, y a partir de ahí toda
decisión daría igual — lo peor que le puede pasar a la variable central.

**Por qué el decaimiento proporcional.** Uno fijo de −2 no alcanza a bajar de 100.

**Y la intensidad realimenta el mundo**, que es el bucle que el caso necesita:

| Efecto | Fórmula | En la sala |
|---|---|---|
| endurece los puntos cerrados | `dureza += (I − 50) × 0,0035` | la próxima vez cuesta más |
| engorda la masa presente | `masa = base + (I − 50) × 4` | sube el riesgo de operar |
| genera puntos nuevos | si `I > 75`, con `p = (I − 50)/200` | aparecen cierres en otras ciudades |
| engorda la presión de fondo | `secundarios += (I − 50) × 0,04 − 2` | los más de mil cierres reales |

```
        operación de fuerza
                ↓
      probabilidad de incidente
                ↓
           imagen que circula
                ↓
        la movilización sube
                ↓
   aparecen puntos nuevos en otras ciudades
                ↓
         hace falta más fuerza
                ↓
    pero la fuerza disponible es la misma
```

> **Abrir un camino por la fuerza puede cerrar dos**, y no está escrito en ningún
> guion: sale de la aritmética.

**Un matiz que el motor separa a propósito:** la intensidad **sube** con el uso de
la fuerza —es rabia contra el Estado— mientras `apoyo_local` **baja** con la
escasez —la gente quiere comer—. No son la misma variable con signo contrario, y
por eso el esquema humanitario del Alcalde es la única vía de apertura que no
consume ninguna reserva.

### En el código

[`mobilization.py`](../src/engine/mobilization.py) · `registrar_evento()` aplica
un delta con su decaimiento; `step()` hace el decaimiento y la realimentación;
`presion_por_escasez()` aplica el hambre.

---

## 5. La fuerza y el riesgo

### En la sala

La sala ordena operar un punto. **Antes de ejecutar nada**, la pantalla devuelve:

> *«Operación sobre Loma del Oriente con ESMAD, de noche. Riesgo de incidente:
> **alto**, 32 %. Mitigadores ausentes: los seis. Responsable: sin nominar.»*

La sala lee eso junta y **con frecuencia cambia la orden**. Es el mejor punto
pedagógico del montaje, y ahora no depende de ninguna persona.

### En el motor

```
riesgo = base(tipo_unidad)
       × (1 + fatiga_media)
       × (1 + dureza_del_punto)
       × (1 + masa_presente / 300)
       × factor_nocturno            (×1,6 de noche)
       × Π(mitigadores)

P(incidente) = min(0,98 ; 1 − e^(−riesgo))
```

**Base por tipo de unidad:** ESMAD 0,08 · Policía 0,22 · Militar 0,45. La tropa
de combate en una multitud es cinco veces más peligrosa que la unidad entrenada.

**Los seis mitigadores, y quién los habilita:**

| Mitigador | Factor | Quién |
|---|---:|---|
| reglas de empleo escritas | ×0,70 | Defensoría, Defensa, o el Presidente al firmar con límites |
| identificación de agentes | ×0,85 | Defensoría |
| registro audiovisual | ×0,80 | Defensoría o Defensa |
| **dupla presente** | ×0,75 | Defensoría — **y gasta una de sus tres** |
| concertado con la alcaldía | ×0,80 | Alcalde |
| unidades con fatiga < 0,30 | ×0,75 | Policía (relevo) |

Producto de los seis: **×0,214**. Dividen el riesgo por casi cinco.

**Por qué la saturación exponencial y no el producto directo.** El producto crudo
no está acotado: militares fatigados, de noche, en un punto duro y concurrido dan
`0,45 × 2,0 × 2,0 × 3,0 × 1,6 = 8,6`, que no es una probabilidad. La
transformación mapea `[0, ∞) → [0, 1)`, conserva el orden y conserva el efecto
multiplicativo de los mitigadores **en la zona baja**, que es donde una sala bien
organizada opera.

Y comunica una asimetría deliberada:

```
ESMAD en un punto duro, sin mitigadores        P = 0,32   ALTA
los mismos, con cinco mitigadores puestos      P = 0,10   MEDIA
militares fatigados de noche, con los seis     P = 0,70   la curva saturó
```

> **El estándar protege a quien ya venía operando con cuidado y no rescata a quien
> no.** Es consecuencia directa de la curva, no una regla añadida.

**Dos cosas se resuelven aparte del incidente**, y esto importa:

```
éxito de la apertura   p = max(0,15 ; 1 − dureza × 0,6)     tirada independiente
atribuible             responsable_nominado AND registro_escrito
```

Se puede **abrir el punto y producir una catástrofe reputacional al mismo
tiempo**. Son dos tiradas distintas, y eso es correcto.

**La mezcla real del punto NO entra en el riesgo.** Si entrara, la banda filtraría
la verdad que nadie debe ver. Lo que cambia es **cuánto cuesta** cuando sale mal
(ver §8).

### Dos acciones que el dueño del ESMAD no tenía

**Concentrar.** Traer escuadrones de la contención estática a la reserva. El
precio es material: los puntos que se sueltan se endurecen `+0,06` y se
consolidan, y el mandatario local que los pierde lo lee como abandono.

**Escoltar.** Sin escolta no hay caravana ni carrotanque. Una escolta lograda
repone `1,1 × caudal` días de autonomía en las regiones que el corredor toca; una
atacada —con probabilidad que sube con la intensidad regional— convierte el
corredor humanitario en escenario de confrontación.

### En el código

[`force.py:56`](../src/engine/force.py) · `evaluar_riesgo()` — el cálculo más
importante del motor
[`force.py:153`](../src/engine/force.py) · `ejecutar_operacion()` — las tiradas
[`force.py:231`](../src/engine/force.py) · `concentrar_esmad()`
[`force.py:263`](../src/engine/force.py) · `escoltar()`

---

## 6. Las tres vías de abrir un camino

### En la sala

**Es la mecánica central del caso**, y la elección entre las tres es lo que el
ejercicio enseña.

| Vía | Tarda | Cuánto abre | ¿Se sostiene? | Qué consume |
|---|---|---|---|---|
| **Fuerza** | 1 turno | 70–100 % | **no — se cierra esa misma noche** | legitimidad, credibilidad, respaldo |
| **Concertación** | 2 turnos | `0,9 × control_voceria` | sí, mientras se cumpla | nada, si se cumple |
| **Desgaste** | 4+ turnos | 50–80 % | sí | **nada** |

### En el motor

**La reapertura nocturna**, que es lo que hace cierta la frase del caso:

```
p_reabre = min(0,95 ; (intensidad / 100) × (0,4 + apoyo_local))
y al reabrir:  dureza += 0,08
```

**Un corredor vale lo que su peor punto:** `caudal_efectivo = min(caudal de sus
puntos)`. Combinado con la reapertura nocturna, esto produce el resultado más
contraintuitivo del ejercicio: **con cinco turnos, la fuerza casi nunca alcanza a
sostener un corredor entero.** No se diseñó a mano — sale de la aritmética.

**La trampa de la concertación.** Lo que se abre es proporcional a cuánto controla
el vocero. Pactar con quien controla el 40 % abre el 36 %, que se anuncia como
éxito y se desmiente solo.

**Y hay una segunda trampa, invisible.** Si el punto tiene estructura organizada
alta, el acuerdo se rompe aunque la vocería fuera buena — porque quien firmó no
manda sobre quien sostiene el cierre:

```
P(el acuerdo es frágil) = estructura_organizada × 1,5
```

La sala no puede saberlo sin haber gastado una dupla ahí. **Es la segunda de las
dos vías por las que la mezcla real de un punto tiene consecuencia.**

**El desgaste es lento a propósito**: exige `apoyo_local < 0,25` sostenido **3
turnos** y aun así solo se dispara con `p = 0,20` por turno. Si fuera barato y
rápido dominaría a las otras dos y la sala descubriría que basta con esperar.

### Una mesa local hay que instalarla CADA JORNADA

La concertación tarda **dos sesiones, no dos días**. `turnos_en_negociacion` sube
una vez por sesión y solo por sesión, de modo que:

> **No instalar una mesa un día equivale a congelar las negociaciones.** No se
> pierde lo andado, pero tampoco se avanza — y el reloj del ejercicio corre
> igual. Abrir una mesa en la jornada 4 y no volver a ella es no haberla abierto.

Eso ya era cierto y no lo sabía nadie: vivía dentro de `avanzar_concertacion()` y
no salía a ninguna pantalla. Ahora hay tres sitios donde se ve, y ninguno cambia
la aritmética:

| Dónde | Qué se ve |
|---|---|
| **El mapa** | un anillo verde en los puntos con mesa que ha sesionado hoy; ámbar a trazos en la instalada que hoy nadie ha convocado |
| **Las consecuencias de la noche** | el hecho `mesa_congelada`, con cuántas jornadas lleva parada |
| **La vista privada** | una **pregunta al abrir el día** para los dos que pueden convocarla |

La pregunta le llega al **Ministro del Interior** (todo el país) y al **Alcalde**
(su jurisdicción), y a nadie más: una notificación que le llega a quien no puede
hacer nada con ella es ruido en una pantalla que tiene que caber sin
desplazamiento. Y es una pregunta, no una instrucción — dice qué hay instalado y
qué lleva parado; qué hacer con eso es de la sala.

```
Estado.jornada_visible ← el reloj de la lectura, no el del motor
```

`sesionada_hoy` se compara contra la jornada **que la sala está viviendo** y no
contra la última resuelta. Mientras se delibera la jornada 2 el motor todavía va
por la 1, y con `turno_decision` la mesa de ayer seguía diciendo «instalada hoy»
durante toda la deliberación de hoy: la pregunta no aparecía nunca.

### Y el mapa dice qué se está haciendo en cada punto

`modo_apertura` responde **cómo se abrió**, así que de los puntos cerrados —la
mayoría durante casi todo el ejercicio— no dice nada. Un punto operado con ESMAD
que no cedió y un punto que nadie ha tocado salían con la misma forma y el mismo
color, y son dos conversaciones distintas. `territory.intervencion_nodo()` añade
la lectura que faltaba:

| | Estado | Cuándo |
|---|---|---|
| ◆ | **fuerza** | se empleó fuerza aquí, cediera o no cediera |
| ■ | **negociación** | hay mesa instalada, o está abierto porque se pactó |
| ● | **ninguna** | no se está haciendo nada en absoluto |

La precedencia: la fuerza empleada **hoy** manda sobre todo; una mesa viva manda
sobre una fuerza de hace tres jornadas; y una fuerza empleada alguna vez, aunque
no cediera, sigue siendo una intervención a la fuerza — es un hecho sobre el
punto, no un estado que caduque.

**Los acuerdos de la mesa nacional** valen mientras se cumplan, y cumplirlos
significa **no operar sobre lo pactado**. Si alguien opera, el acuerdo se marca
roto, los puntos vuelven a cerrarse, cae la credibilidad y sube la movilización.

### En el código

[`aperture.py`](../src/engine/aperture.py) · `abrir_por_fuerza()`
[`aperture.py`](../src/engine/aperture.py) · `avanzar_concertacion()` — con la trampa
[`aperture.py`](../src/engine/aperture.py) · `instalar_mesa()` · `cerrar_mesa()` · `revisar_mesas()`
[`aperture.py`](../src/engine/aperture.py) · `revisar_desgaste()`
[`aperture.py`](../src/engine/aperture.py) · `step()` — reaperturas nocturnas
[`aperture.py`](../src/engine/aperture.py) · `revisar_acuerdos()`
[`territory.py`](../src/engine/territory.py) · `intervencion_nodo()` · `mesa_nodo()` · `mesas_instaladas()`
[`views.py`](../src/engine/views.py) · `_notificacion_mesas()`

---

## 7. El reloj y el oxígeno

### En la sala

Cada región tiene días de autonomía de combustible, alimentos y oxígeno
medicinal. **Bajan solos y solo suben si alguien hace algo.** La más apretada
arranca con menos de dos días de oxígeno.

El oxígeno es el único que **convierte logística en muertes**, y no es una
variable sanitaria sino el extremo de una cadena:

```
camino abierto → entra combustible → hay diésel para los carrotanques
                                   → y para las plantas de emergencia
                                   → las plantas sostienen producción y frío
                                   → hay oxígeno en la UCI
                                   → no se muere quien no tenía que morirse
```

**Cortar la cadena en cualquier punto la rompe entera**, y por eso ninguna cartera
lo resuelve sola: hacen falta cuatro.

### En el motor

```
consumo(región)  = 1,0 × (1 + pánico) × días
ingreso(región)  = Σ caudal(corredor) × 2,6 × días
                   solo corredores de la clase pedida QUE TOQUEN la región
```

**El filtro por región es real:** un corredor abierto en Alto Verde no abastece a
Puerto Espejo. Sin él, abrir cualquier cosa salvaba a todo el país y priorizar
dejaba de significar nada.

**El eslabón que hace sistémica la crisis:** si el combustible baja de 1 día, el
oxígeno pierde `0,25` días adicionales por día. Sin diésel no hay plantas.

**Y por debajo de cero no hay escasez: hay un contador.**

```
muertes = 180 pacientes × horas_sin_oxígeno × 0,0022 × presión_hospitalaria
```

La presión hospitalaria (0,74–0,92 según la región) modula el contador: una red al
92 % de ocupación no absorbe lo mismo que una al 74 %.

### El reloj tiene TRES entradas, no una

Esto es lo que v2 arregló, y es la corrección más importante del motor:

| Entrada | Quién la controla |
|---|---|
| **1 · abrir un corredor** que sirva a esa región | Interior, Defensa, el Alcalde |
| **2 · escoltar** un carrotanque o una misión médica hasta allá | **Policía** |
| **3 · la prioridad de combustible**, aplicada cada paso | **Minas** |

La tercera es un **criterio permanente**: mientras esté fijado se aplica en cada
paso, no una sola vez. Fijarlo es exactamente lo que significa «no pelearlo cada
turno» — y es suma cero:

```
pesos según el orden:  1º 0,40   2º 0,30   3º 0,20   4º 0,10
lo que entra a misión médica sale del transporte de alimentos
```

> **No hay orden correcto.** Hay un orden que alguien tiene que defender ante
> siete personas que pierden algo.

**Y una regla que se hace cumplir a la fuerza:** toda región debe tener al menos
un corredor humanitario que la sirva. Sin eso, sus muertes son inevitables haga lo
que haga la sala — y eso no es un dilema, **es un guion que castiga**.
[`loader.py:135`](../src/engine/loader.py) falla ruidosamente si alguien lo rompe.

### En el código

[`supply.py:66`](../src/engine/supply.py) · `step()` — el reloj y el contador
[`supply.py:172`](../src/engine/supply.py) · `asignar_combustible()` — fija el criterio
[`supply.py:145`](../src/engine/supply.py) · `difundir_calendario()` — entregar el reloj lo acelera

---

## 7 bis. La infraestructura relevante

### En la sala

El escenario trae **una base de doce instalaciones con nombre, sitio y región**:
la refinería, dos hospitales, dos plantas de agua, el terminal marítimo, el
acopio de combustible, el aeropuerto, una subestación, una estación de bombeo, un
terminal de transporte y un centro de acopio. Cada una dice **de qué depende** en
una frase, y lleva su criticidad **en palabra y no en índice** — vital, alta,
media.

> **No hay ninguna acción en contra de esta infraestructura, y es deliberado.**
> El ejercicio no simula un ataque a la refinería. Simula la decisión de
> **inmovilizar fuerza para custodiarla**, que es la que enfrenta a Minas con
> Defensa: lo que se protege sale exactamente de lo que desbloquea.

Antes existía la acción y no existía el objeto: `DeclararInfraestructuraCritica`
recibía una cadena de texto libre que nadie comprobaba contra nada. Se podía
declarar crítica una instalación inventada, la orden salía ejecutada con éxito, e
inmovilizaba fuerza igual. Y el Ministro de Minas no tenía en ninguna pantalla la
lista de lo que le toca proteger, así que declaraba a ciegas.

### En el motor

La acción **resuelve contra el registro** —por identificador, por nombre exacto o
por nombre contenido, sin coincidencia difusa— y rechaza lo que no está,
enumerando lo que sí. Al proteger, marca la instalación, consume custodia y
levanta `proximidad_infra_critica` en los puntos contiguos, que es exactamente lo
que se está comprando.

**El riesgo se acumula callado y se cobra al final:**

```
exposicion = Σ  peso(criticidad) × jornadas_sin_custodia
             peso: vital 3,0 · alta 2,0 · media 1,0
```

No produce **ningún** evento durante la corrida y no toca ninguna reserva. Si lo
hiciera, la sala vería moverse el número y jugaría contra él — y lo que este
contador mide no es un daño que ocurrió, sino un riesgo que se asumió.

> Un riesgo que se materializa es un guion. Un riesgo que se nombra al final es
> una conversación sobre lo que se decidió no hacer.

Sale entero en `MotorCrisis.metricas()['infraestructura']`, con el detalle por
instalación: cuántas jornadas pasó sin custodia, de qué depende, y cuáles de
criticidad **vital** se quedaron solas. El número solo no abre ninguna
conversación; lo que la abre es la lista de nombres.

### En el código

[`state.py`](../src/engine/state.py) · `Infraestructura`
[`loader.py`](../src/engine/loader.py) · carga y exige que cada una caiga dentro de su región
[`actions.py`](../src/engine/actions.py) · `DeclararInfraestructuraCritica.resolver()`
[`simulation.py`](../src/engine/simulation.py) · `_acumular_riesgo_infraestructura()` · `riesgo_infraestructura()`
[`views.py`](../src/engine/views.py) · la cartera de Minas, con nombre y estado de custodia

---

## 8. La información: verdad, vistas y denuncias

### En la sala

**El Estado no observa el mundo: lo estima.** Cada punto tiene una mezcla real
—protesta legítima, vandalismo, estructura organizada— que **nadie ve**, ni la
interfaz ni quien opera la consola. Se revela en el debriefing.

Lo que cada rol ve es una lectura sesgada, y **los sesgos van en direcciones
opuestas a propósito**:

| Quién estima | Cómo se equivoca | Qué alcanza a ver |
|---|---|---|
| Inteligencia de Defensa | **+0,28** sobreestima la estructura | media |
| Parte operacional de la Policía | +0,10 · subestima víctimas civiles | todos los puntos |
| Parte municipal del Alcalde | **−0,22** subestima la estructura | solo su jurisdicción |
| Duplas de la Defensoría | +0,02 · casi no se equivoca | **3 puntos por turno** |

**La fuente más precisa es la que menos alcanza a ver.**

### En el motor: la mezcla real ahora TIENE consecuencia

Hasta v2 estaba protegida por una invariante y **no entraba en ningún cálculo**:
daba exactamente igual operar sobre protesta pura o sobre estructura organizada.
Se conectó por **dos vías y solo dos**:

**1 · Operar sobre población civil cuesta más.**

```
multiplicador = 1,0 + max(0 ; protesta_legítima − 0,50) × 2,0
```

Un punto que es 95 % protesta legítima multiplica el costo del incidente por
**1,9**. Uno mitad y mitad, por 1,0. La sala no puede saberlo antes de operar —
puede *averiguarlo* gastando una dupla, y esa es la decisión que el ejercicio
quiere producir.

**2 · Pactar donde hay estructura produce un acuerdo que se rompe** (§6).

Nada más. **La verdad sigue sin salir jamás del motor.**

### Las duplas: un solo bolsillo de tres

Una **dupla** es una pareja de funcionarios de la Defensoría que va al terreno a
constatar qué pasa. Van de a dos porque protege a los verificadores y porque dos
testigos producen una constancia difícil de desestimar.

**Hay tres, y cada una hace UNA sola cosa por turno:**

- verificar un punto — medir qué hay realmente ahí
- verificar una denuncia — establecer si un hecho grave ocurrió
- **acompañar una operación** — baja el riesgo un 25 %

Antes acompañar era una casilla gratis: la sala podía marcarla en todas las
operaciones mientras la Defensoría verificaba aparte. **Ahora compiten**, y por eso
la asignación de la Defensoría es una decisión y no un trámite.

### Las denuncias: nunca una sola

```
D-001  «Reportan personas trasladadas sin registro...»     nodo N003   veraz = True
D-002  «Circula que hubo una desaparición durante el...»   nodo N022   veraz = False
```

**Desde fuera son idénticas.** El campo `veraz` nunca sale del motor.

Un ejercicio sobre el paro de 2021 en el que la única denuncia grave resulta
inventada le enseña a nueve futuros funcionarios que las denuncias graves suelen
serlo — y eso, sobre hechos con responsabilidad judicial viva, **es tomar
partido**. Por eso [`loader.py`](../src/engine/loader.py) exige al menos dos, con
veracidad distinta, y falla ruidosamente si no.

**Las cuatro conductas y su precio:**

| Conducta | Resultado |
|---|---|
| Reaccionar con fuerza a ambas | gasta capacidad en la falsa, agrava la cierta |
| Desestimar ambas | la cierta estalla sin respuesta preparada |
| Verificar una | acierta a medias — **es el resultado realista** |
| Verificar una y **declarar la otra en verificación** | el mejor disponible: el estallido cuesta la mitad |

La cuarta no gasta dupla. Es la mejor conducta disponible, y **no es acertar: es
no afirmar lo que no se sabe.**

Las denuncias sin mirar **estallan** a los dos turnos, con o sin razón.

### En el código

[`information.py:71`](../src/engine/information.py) · `estimar_nodo()` — las lecturas sesgadas
[`information.py:109`](../src/engine/information.py) · `consumir_dupla()` — el bolsillo único
[`information.py:165`](../src/engine/information.py) · `verificar_denuncia()`
[`information.py:202`](../src/engine/information.py) · `declarar_en_verificacion()`
[`information.py:221`](../src/engine/information.py) · `paso_denuncias()` — las que estallan
[`force.py:123`](../src/engine/force.py) · `multiplicador_costo_civil()`

---

## 9. La mesa: reservas, banderas y acuerdos

### En la sala

Cuatro reservas, **y las cuatro se leen igual: arriba es mejor**.

| Reserva | t=0 | Qué es |
|---|---:|---|
| Legitimidad | 52 | el respaldo ciudadano a la respuesta |
| Credibilidad de la mesa | 45 | si el canal de diálogo sirve para algo |
| Respaldo internacional | 55 | cuánto margen queda antes de que el mundo se pronuncie |
| **Cohesión del PMU** | 68 | si estos nueve actúan como uno o como nueve |

> **Cambio de v2:** la «exposición internacional» iba invertida —arriba era peor—
> y obligaba a explicar el tablero. Ahora es **respaldo**, y solo la presión en la
> calle va al revés, que es intuitivo porque es el adversario.

**Tres se heredan dañadas y una no.** La sala no rompió las tres primeras. **La
cohesión empieza alta y es enteramente suya**: en el debriefing es la única serie
de la que los nueve no pueden desentenderse.

### En el motor

**Los seis umbrales son duros**, no efectos suaves. Un deterioro gradual no
produce decisiones; un umbral sí.

| Reserva | Umbral | Qué se activa |
|---|---:|---|
| legitimidad | < 40 | los gremios pasan a `evaluando` |
| legitimidad | < 25 | los gremios se **suman**: cierre logístico nacional |
| credibilidad | < 30 | el Comité suspende su participación |
| credibilidad | < 15 | no vuelve a sentarse |
| respaldo internacional | < 30 | pronunciamientos de organismos |
| cohesión | < 35 | los agentes citan contradicciones entre roles |

**Las banderas constitutivas: ninguna bloqueada, todas tarifadas.**

| Se opera sin… | Precio |
|---|---|
| reglas escritas | riesgo sin descuento |
| registro escrito | el costo se reparte sobre los nueve · cohesión −8 |
| protocolo de vocería | cohesión −5 **por turno de decisión** |
| criterio de priorización | cohesión −3 **por turno de decisión** |
| protocolo de verificación | cada desmentido cuesta 4 de legitimidad |

**El valor de una constitutiva es proporcional a los turnos que le quedan
delante.** No hace falta ninguna penalización artificial por adoptarla tarde: un
protocolo en el turno 5 solo cubre un turno y no borra lo ya desmentido.

**Y la cohesión ahora se puede reponer**, que antes no:

```
decisión con responsable nominado    +2
acuerdo verificable cumplido         +3
calendario entregado a la mesa       +3
evidencia presentada con su solidez  +3
```

### El ultimátum gremial

Los gremios arrancan **fuera**, no evaluando — aunque la legitimidad esté por
encima del umbral. Lo que los activa en el turno 1 es **el ultimátum de 48 horas
del paquete detonante**, que es un disparador independiente.

> Los dos caminos hacia `evaluando` deben coexistir, porque son cosas distintas:
> una es que el país deje de respaldar al Gobierno, y otra que **un gremio
> concreto pida algo concreto con plazo**.

### En el código

[`state.py:197`](../src/engine/state.py) · `Reservas` y `umbrales_cruzados()`
[`state.py:240`](../src/engine/state.py) · `Banderas`
[`simulation.py:274`](../src/engine/simulation.py) · `_cobrar_ausencia_de_banderas()`
[`simulation.py:209`](../src/engine/simulation.py) · `_resolver_ultimatum_gremios()`

---
---

# C · Lo que la sala puede hacer

## 10. Las treinta y nueve acciones

### En la sala

Treinta y nueve acciones repartidas en tres tipos —**protocolo**, **operación**,
**información**— entre cuatro y cinco por rol. **El reparto exacto, con la
razón de por qué unos tienen cinco y otros cuatro, está en
[`propuesta.md` §5.1](propuesta.md#51-cuántas-y-por-qué-no-son-iguales);** cada
acción por separado, con sus números, en [`LAS_ACCIONES.md`](LAS_ACCIONES.md).

Lo que importa aquí es cómo las ejecuta el motor.

### En el motor

El patrón, heredado de Macondo y ampliado:

```python
validar(estado)  -> Validacion   ¿es viable AHORA? NO muta nada
ejecutar(estado, rng) -> Resultado   aplica el efecto. SIEMPRE estructurado
```

**Cuando falta un requisito, `validar()` devuelve quién puede habilitarlo**, no un
rechazo seco. Eso empuja la conversación de vuelta a la sala:

```python
Validacion(
    ok=False,
    motivo="Concertar en la jurisdicción del epicentro requiere a la Alcaldía.",
    requisitos_faltantes=["concertación con la Alcaldía"],
    habilitada_por=["Alcalde de la ciudad epicentro"],
)
```

**Las cinco dependencias duras** —quién necesita a quién, y las cuatro sumas
cero que las acompañan— están en
[`propuesta.md` §5.3](propuesta.md#53-quién-habilita-a-quién). El motor las
comprueba en `validar()`, y por eso el rechazo puede nombrar al habilitante.

### Tres correcciones que reequilibran el ejercicio

**La concertación vuelve a Interior.** Antes vivía en la ficha del Alcalde y no
comprobaba jurisdicción: un alcalde municipal acababa pactando cierres en dos
regiones ajenas. Ahora `AbrirMesaLocal` es de Interior y **exige al Alcalde en el
epicentro**; `InstalarMesaConVoceros` es del Alcalde y **solo funciona en su
jurisdicción**.

**La Policía recupera el ESMAD y la escolta.** El dueño del activo más escaso no
podía asignarlo: los escuadrones se movían solos cuando alguien ordenaba una
operación.

**Minas puede asignar el combustible.** La función existía escrita y desconectada:
ningún rol podía invocarla, y por eso el reloj tenía una sola entrada.

### En el código

[`actions.py`](../src/engine/actions.py) · las 39, agrupadas por rol
[`actions.py:1497`](../src/engine/actions.py) · `catalogo_por_rol()` — se genera
desde el código, no se escribe a mano en ningún prompt

---

## 11. Las nueve vistas privadas, por dentro

### En la sala

Cada vista tiene **tres bloques y nada más**: *su alerta* (una línea), *su
detalle* (3–4 datos de su cartera) y *su repertorio* (qué puede pedir). Cabe en
una pantalla sin desplazamiento.

**Las nueve alertas de un turno real, medidas:**

```
PRESIDENTE   La mesa no ha constituido nada: 11 decisiones que rigen todo lo
             demás siguen sin adoptarse, y ninguna cuesta un escuadrón.
INTERIOR     Hay ventana para una sesión de mesa. Una operación hoy la cierra.
ALCALDE      1 punto con el apoyo del barrio ya cayendo: el esquema humanitario
             los deshace sin fuerza.
DEFENSA      4 de 5 casos de financiación no aguantarían ante un juez. Si uno se
             cae, arrastra al resto.
POLICÍA      2 denuncias sin verificar contra unidades. Si estallan afuera
             primero, la corrección se leerá como encubrimiento.
DEFENSORÍA   Ningún mitigador está activo. El estándar completo divide la
             probabilidad de incidente por casi cinco y no cuesta un escuadrón.
TRANSPORTE   Los gremios camioneros están evaluando sumarse. Si lo hacen, esto
             deja de ser orden público y pasa a ser cierre logístico nacional.
MINAS        Las Cumbres: 0,8 días de oxígeno. Si mañana no entra nada, 0,0.
AGRICULTURA  Puerto Espejo: 1,2 días de comida. Hoy no entra nada. La ventana de
             los perecederos se mide en horas.
```

> **Nueve urgencias legítimas y una escolta.** Ninguna es falsa, ninguna es
> caprichosa, y no caben todas. Eso es el diseño.
>
> Y la última cambia la conversación: **la de Agricultura no es un pronóstico.**
> Las otras dicen lo que va a pasar si no se decide; la suya dice lo que ya
> pasó mientras se decidía.

### El repertorio lleva semáforo

Cada acción dice si se puede pedir **hoy** y, si no, qué falta:

```
Se puede pedir · Operación
   Desbloquear un punto por la fuerza
   Manda a la fuerza pública a abrir un punto.

Aún no · Operación
   Organizar una caravana
   Junta la carga en una caravana por un corredor prioritario.
   Falta escolta policial.
   Lo habilita: Director General de la Policía Nacional (escoltar)

Ya vigente · Protocolo
   Exigir reglas, identificación y cámaras
   Exige que la fuerza actúe con reglas escritas, identificada y grabando.
```

**El problema que resuelve.** El repertorio era una lista plana, y de sus cuatro
o cinco líneas dos podían llevar tres jornadas bloqueadas sin que su titular
tuviera forma de saberlo: lo descubría dictándolas en voz alta y recibiendo el
rechazo delante de la mesa. Eso no es información incompleta —que es el objeto
del ejercicio—, es una interfaz escondiendo una regla que ya conoce.

**Y el requisito se enuncia en general.** «Requiere que el Presidente firme la
asistencia militar» es un hecho sobre el mundo; «pida al Presidente que firme y
opere el Puente Amarillo» sería la pantalla decidiendo por la sala. Es la misma
línea que el tablero no cruza, aplicada aquí.

**Lo que hace es empujar la conversación a la mesa**, no ahorrarla: quien lee
«falta escolta · Director General de la Policía» sabe a quién tiene que
pedírselo, y eso pasa en voz alta.

**No es una segunda copia de las reglas.** `disponibilidad()` LLAMA a
`validar()`, que es la misma función que decide si una orden entra. Lo único que
cada acción aporta es una **sonda** —un ejemplar con el objetivo más favorable
que hoy exista— para poder preguntar sin haber elegido todavía sobre qué punto.
Que la sonda busque el objetivo más favorable es deliberado: la pregunta que
contesta el semáforo es «¿esto se puede pedir hoy?», y «Aún no» significa
entonces que **no hay ningún objetivo para el que salga.**

### En el motor

Cada vista es una **proyección determinista del estado** — no texto generado. Se
construye leyendo el estado y aplicando el sesgo de la fuente de ese rol.

```python
def vista(estado, rol)        -> {"rol", "turno", "detalle", "alerta"}
def catalogo_por_rol(estado)  -> cada acción, con su `disponibilidad`
```

**Tres invariantes, garantizadas por construcción:**

- ninguna vista revela la mezcla real de un punto
- ninguna vista revela si una denuncia es cierta
- **ninguna vista repite lo que ya está en el tablero** — si un dato estuviera en
  los dos, la vista privada sobraría y el participante aprendería a ignorarla

### En el código

[`views.py`](../src/engine/views.py) · una función por rol, más `vista()` y
`todas()`. Verlas con:

```bash
uv run python scripts/correr_ejercicio.py --vistas
```

---

## 12. Los siete arreglos, medidos

El [diagnóstico del motor anterior](historial/mapa_de_palancas.md) encontró siete
problemas (D1–D7). **Qué era cada uno y cómo se cerró está en
[`historial/resueltos.md` §2](historial/resueltos.md#2--del-diagnóstico-del-motor-anterior).**
Aquí está lo otro, que es lo que no se puede afirmar sin medirlo: **cuánto
cambiaron las corridas.**

Dos de los siete eran los graves, porque no eran de coeficientes sino piezas que
faltaban: **la cohesión era una rampa que no respondía a nada** (D5) y **el reloj
tenía una sola entrada, así que las muertes salían idénticas** (el conjunto de
D3, D4 y la prioridad de combustible).

### La cohesión, antes y después

**Antes** era exactamente `−5,0` por paso, nueve peajes en cinco decisiones, y la
serie no respondía a nada:

```
T1d  T1n  T2d  T2n  T3d  T3n  T4d  T4n  T5d
 63   58   53   48   43   38   33   28   23
```

**Ahora** depende de lo que la sala haga:

```
  estrategia      cohesión al cierre
  solo_fuerza              0
  pasiva                  28
  humanitaria             28
  logistica               40
  solo_mesa               56
  constituida             74      ← constituirse paga
```

### El reloj, antes y después

**Antes** las muertes eran idénticas en cuatro de cinco estrategias, porque el
reloj tenía **una sola entrada**. **Ahora** tiene tres:

```
                        antes    ahora
  solo_fuerza             147       64
  pasiva                  147       64
  constituida             147       48
  solo_mesa               147       31
  logistica                 —       28
  humanitaria              70       13
```

**Y la tercera entrada es la que separó a `solo_mesa` de `pasiva`.** Antes las
dos dejaban morir a los mismos: el reloj no distinguía entre una sala que
negociaba y una que no hacía nada, porque ninguna de las dos abría un corredor
por la fuerza y esa era la única entrada que existía.

### La medición completa

**Esta tabla es el criterio de aceptación del proyecto**, y se reproduce con
`uv run python scripts/correr_ejercicio.py --comparar`:

```
  estrategia      netas  reap  muert  legit  cohes  credib   resp
  ---------------------------------------------------------------------
  solo_fuerza         0     3     64     16      0      21     26
  solo_mesa           9     0     31     62     56      39     49
  constituida         3     1     48     47     74      21     59
  humanitaria         2     0     13     51     28      45     58
  logistica           0     2     28     48     40      26     43
  pasiva              0     0     64     30     28      45     49
```

**Ninguna domina, y el reparto es el que debe ser.**

| Estrategia | Lo que consigue | Lo que paga |
|---|---|---|
| `solo_mesa` | **abre nueve caminos** —más que ninguna— y conserva las cuatro reservas | deja morir a **31**: más del doble que las dos logísticas |
| `humanitaria` | **salva 51 de las 64 muertes**, el mejor resultado del cuadro | abre dos caminos. El país queda cerrado |
| `logistica` | salva 36 muertes por la vía del abastecimiento | no abre ninguno neto |
| `constituida` | la **mejor mesa** (cohesión 74) y salva 16 muertes sin dejar de operar | lo paga en credibilidad — es lo que cuesta operar con la mesa puesta |
| `solo_fuerza` | — | se queda sin nada: cero caminos netos, las 64 muertes, y la cohesión en 0 |
| `pasiva` | — | las 64 muertes, sin haber gastado nada |

El dilema central del caso está en el contraste entre las dos primeras líneas:
**abrir el país y dejar morir a la gente, o salvarla y entregar el país cerrado.**

> **Se lee por las columnas que no bailan.** `netas` y `reap` son tiradas y
> cambian con la semilla; `cohes` y `muert` no, porque dependen de qué banderas
> se adoptaron y qué corredores se abrieron. Si esas dos empezaran a moverse con
> la semilla, algo se rompió.

> **Si en el debriefing una opción resulta haber sido obviamente correcta desde el
> turno 1, el ejercicio está mal calibrado.** Hoy no la hay.

**Y una advertencia que sigue en pie:** ningún coeficiente está medido. Son
convenciones declaradas, elegidas para que ninguna estrategia pura gane. **La
primera corrida con personas es una medición, no un ejercicio.**

---

## 13. Cómo comprobarlo uno mismo

Todo lo de este documento se puede verificar en un rato, sin montar la sala y
**sin llave de API**:

```bash
# Un ejercicio completo, turno a turno, con la cadena causal
uv run python scripts/correr_ejercicio.py --detalle

# Las nueve vistas privadas de un turno real — el diseño en una pantalla
uv run python scripts/correr_ejercicio.py --vistas

# Las seis estrategias: el criterio es que NINGUNA domine
uv run python scripts/correr_ejercicio.py --comparar

# Otra semilla, para separar el ruido de la señal
uv run python scripts/correr_ejercicio.py --comparar --semilla 99
```

**La más reveladora es `--vistas`.** Las nueve alertas de un mismo turno, una
debajo de otra: se ve de golpe que los nueve están mirando la misma crisis y
ninguno la misma parte.

> Puesta en marcha completa y el resto de comandos, en
> [`EL_CODIGO.md`](EL_CODIGO.md#12-puesta-en-marcha).

### Qué falta todavía

**La cuenta se lleva en un solo sitio: [`PENDIENTES.md`](../PENDIENTES.md).** Lo
que conviene saber al terminar de leer este documento es que lo que falta se
parte en dos, y que la segunda mitad no la puede cerrar ninguna línea de código:

- **Sin convocar a nadie** — el archivo de la corrida (**B1**), el debriefing que
  depende de él (**B7**), la identidad de los nueve roles en datos (**B2**) y la
  medida de si la asimetría produjo conversación (**B3**).
- **Con personas en una sala** — las tres corridas (**P2–P4**) y las cuatro
  calibraciones (**C1–C4**). *El motor puede estar perfecto y el ejercicio no
  funcionar.*

Los stubs están marcados donde viven: `grep -rn "PENDIENTE" src/`

---

*Motor v2 · semilla `20210511`. Diseño del juego en
[`propuesta.md`](propuesta.md); cada acción por separado en
[`LAS_ACCIONES.md`](LAS_ACCIONES.md); diagnóstico del motor anterior en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).*

*Escuela de Gobierno · Universidad de La Sabana.*
