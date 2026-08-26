# Cómo funciona — del juego al motor

Cómo está construido el simulador de la [propuesta](propuesta.md), leído
siempre en el mismo orden: **primero lo que pasa en la sala, después cómo el
motor lo produce, y al final dónde está el código.**

No hace falta saber programar para leerlo. Cada sección tiene la misma forma:

> **En la sala** · qué viven las ocho personas
> **En el motor** · qué cálculo lo produce, con los números reales
> **En el código** · qué archivo y qué función, para poder ir a mirar

Describe **el motor que corre hoy**. El anterior está en
[`historial/como_funciona_motor_v1.md`](historial/como_funciona_motor_v1.md),
y el diagnóstico del que salió esta versión, en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).

---

## Índice

**A · El mapa**

1. [Qué archivo hace qué](#1-qué-archivo-hace-qué)
2. [Un turno completo, de principio a fin](#2-un-turno-completo-de-principio-a-fin)
3. [Las cuatro superficies, en tres rutas](#3-las-cuatro-superficies-en-tres-rutas)

**B · Los seis motores, desde la sala**

4. [El adversario reflexivo](#4-el-adversario-reflexivo)
5. [La fuerza y el riesgo](#5-la-fuerza-y-el-riesgo)
6. [Las tres vías de abrir un camino](#6-las-tres-vías-de-abrir-un-camino)
7. [El reloj y el oxígeno](#7-el-reloj-y-el-oxígeno)
8. [La información: verdad, vistas y denuncias](#8-la-información-verdad-vistas-y-denuncias)
9. [La mesa: reservas, banderas y acuerdos](#9-la-mesa-reservas-banderas-y-acuerdos)

**C · Lo que v2 cambió**

10. [Las treinta y cuatro acciones](#10-las-treinta-y-cuatro-acciones)
11. [Las ocho vistas privadas, por dentro](#11-las-ocho-vistas-privadas-por-dentro)
12. [Los siete arreglos, medidos](#12-los-siete-arreglos-medidos)
13. [Cómo comprobarlo uno mismo](#13-cómo-comprobarlo-uno-mismo)

---
---

# A · El mapa

## 1. Qué archivo hace qué

```
src/engine/                EL MOTOR. Único dueño del estado.
                           Sin IA, determinista salvo por una semilla registrada.

  parameters.py    319 l   Todas las constantes, con nombre y unidad.
                           Si un número gobierna algo, vive aquí y en ningún otro sitio.

  state.py         545 l   De qué está hecho el país: puntos, corredores,
                           regiones, unidades, reservas, banderas, denuncias,
                           acuerdos — y `vista_publica()`, el tablero general.

  loader.py        215 l   Construye el estado heredado (t=0) desde `data/` y
                           verifica las invariantes que fallan ruidosamente.

  mobilization.py  183 l   El adversario reflexivo. Si solo se implementa uno, es este.
  force.py         367 l   Riesgo, mitigadores, incidentes, ESMAD y escolta.
  aperture.py      224 l   Las tres vías de abrir, las reaperturas y los acuerdos.
  supply.py        202 l   El reloj, el oxígeno y la prioridad de combustible.
  information.py   300 l   Verdad, estimaciones sesgadas, duplas y denuncias.

  views.py         421 l   LAS OCHO VISTAS PRIVADAS. La pieza central de la v2.
  actions.py     1 516 l   Las 34 acciones de los ocho roles.
  simulation.py    416 l   El bucle de turnos. `paso()` es la única forma de que
                           el tiempo avance.

src/api/main.py            Capa delgada: sirve las superficies.
data/escenario/            El caso, en datos y no en código.
scripts/                   El corredor sin interfaz, para calibrar sin montar la sala.
tests/                     49 verificadores sin modelo, en 0,2 s.
```

**La regla que ordena todo esto:** el motor **corre entero sin llamar a ningún
modelo de lenguaje**. Las ocho vistas son proyecciones deterministas del estado,
no texto generado. Si algún día una vista necesitara un modelo para existir, la
arquitectura estaría mal.

### Para entenderlo por dentro, en este orden

1. **`scripts/correr_ejercicio.py --vistas`** — mira las ocho alertas de un turno
   real. Es la v2 en una pantalla.
2. **[`state.py`](../src/engine/state.py)** — de qué está hecho el mundo.
3. **[`force.py`](../src/engine/force.py)**, la función `evaluar_riesgo` — el
   cálculo más importante del motor.
4. **[`simulation.py`](../src/engine/simulation.py)**, el método `paso()` — el que
   ordena todo lo demás.

---

## 2. Un turno completo, de principio a fin

### En la sala

```
0 · PARTE PRIVADO    1,0 min   Cada rol lee su vista. NADIE HABLA.
1 · APERTURA         1,0 min   El tablero muestra qué cambió. Se lee en voz alta
2 · DELIBERACIÓN     6,0 min   Las pantallas se congelan. Se habla
3 · ÓRDENES          2,5 min   Se transcriben; el sistema devuelve el plan
                               CON SU BANDA DE RIESGO y la mesa confirma
4 · RESOLUCIÓN       1,0 min   El sistema ejecuta
5 · CONSECUENCIAS    1,0 min   Prensa, redes, gremios, internacional
6 · REGISTRO         0,5 min   La decisión al pliego, con responsable nominado
```

**No hay moderador como figura aparte.** Quien opera la consola —puede ser uno de
los ocho— solo transcribe. El reloj de cada fase lo lleva el sistema, el parte de
apertura lo muestra la pantalla, y el plan de vuelta sale del motor.

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

**Tres pruebas custodian la separación** y están en
[`tests/test_invariantes.py`](../tests/test_invariantes.py):

- `test_la_vista_publica_jamas_expone_la_mezcla_real`
- `test_las_ocho_vistas_privadas_tampoco_la_exponen`
- `test_solo_minas_ve_los_dias_exactos`

### Cómo el tablero señala un problema sin decir qué hacer

Es la tensión que gobierna el diseño de la superficie 1, y no tiene término
medio posible:

| Si el tablero… | Lo que pasa |
|---|---|
| dice «abra el corredor hospitalario» | el ejercicio se acabó: el tablero pensó por la sala |
| es un muro de números iguales | nadie se entera de nada en seis minutos de deliberación |

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
proyectado junto a ocho dispositivos la discrepancia se ve el primer turno.

**3 · El orden.** Corredores y regiones van **peor primero**. El ojo aterriza
arriba a la izquierda y ahí está el problema, sin que nadie lo señale. La
memoria espacial que se pierde la devuelve el mapa.

**4 · Lo que falta, contado.** Puntos que nadie ha verificado, denuncias
abiertas, decisiones sin responsable — en fracción, porque `24` no dice si la
sala avanza y `9/24` tres turnos después sí.

> **La distancia entre «3 puntos sin verificar» y «verifique P7» es la distancia
> entre un ejercicio y un tutorial.**

**5 · Lo que pasó en cada punto.** El mapa dibuja un anillo sobre los puntos
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
> el tablero, uno de los ocho roles dejaría de hacer falta.

Lo custodia `test_el_mapa_cuenta_lo_que_se_hizo_y_no_donde_esta_la_fuerza`, y que
el anillo no se acumule,
`test_el_anillo_del_mapa_se_apaga_a_la_ventana_siguiente`.

**Y el delta no abre una puerta trasera.** `_indicadores()` se restringe a lo que
`vista_publica()` ya serializa: un delta calculado sobre la mezcla real de un
punto la filtraría igual de bien que mostrarla. Lo custodia
`test_el_delta_no_abre_una_puerta_trasera_a_lo_oculto`.

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
> no.** Hay una prueba que lo verifica: `test_el_estandar_no_rescata_a_quien_opera_sin_cuidado`.

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

**Los acuerdos de la mesa nacional** valen mientras se cumplan, y cumplirlos
significa **no operar sobre lo pactado**. Si alguien opera, el acuerdo se marca
roto, los puntos vuelven a cerrarse, cae la credibilidad y sube la movilización.

### En el código

[`aperture.py:38`](../src/engine/aperture.py) · `abrir_por_fuerza()`
[`aperture.py:50`](../src/engine/aperture.py) · `avanzar_concertacion()` — con la trampa
[`aperture.py:91`](../src/engine/aperture.py) · `revisar_desgaste()`
[`aperture.py:124`](../src/engine/aperture.py) · `step()` — reaperturas nocturnas
[`aperture.py:174`](../src/engine/aperture.py) · `revisar_acuerdos()`

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

**Desde fuera son idénticas.** El campo `veraz` nunca sale del motor, y hay una
prueba que lo verifica.

Un ejercicio sobre el paro de 2021 en el que la única denuncia grave resulta
inventada le enseña a ocho futuros funcionarios que las denuncias graves suelen
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
| **Cohesión del PMU** | 68 | si estos ocho actúan como uno o como ocho |

> **Cambio de v2:** la «exposición internacional» iba invertida —arriba era peor—
> y obligaba a explicar el tablero. Ahora es **respaldo**, y solo la presión en la
> calle va al revés, que es intuitivo porque es el adversario.

**Tres se heredan dañadas y una no.** La sala no rompió las tres primeras. **La
cohesión empieza alta y es enteramente suya**: en el debriefing es la única serie
de la que los ocho no pueden desentenderse.

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
| registro escrito | el costo se reparte sobre los ocho · cohesión −8 |
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

# C · Lo que v2 cambió

## 10. Las treinta y cuatro acciones

### En la sala

> **Cada rol tiene al menos una acción de cada clase**, y eso es lo que garantiza
> que ningún participante pase el ejercicio sin nada que hacer.

| Clase | Qué cambia | Se ve en el tablero |
|---|---|---|
| **Constituye** | cómo funciona la mesa · rinde en todo lo que venga después | no |
| **Toca el mundo** | el territorio, la fuerza, el abastecimiento | de inmediato |
| **Informa** | lo que el país tiene por cierto | en la esfera pública |

| Rol | Acciones | | Rol | Acciones |
|---|---:|---|---|---:|
| Presidente | 5 | | Policía | 4 |
| Defensoría | 5 | | Transporte | 4 |
| Interior | 4 | | Minas | 4 |
| Alcalde | 4 | | Defensa | 4 |

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

**Las cinco dependencias duras:**

```
Transporte quiere mover carga        → necesita ESCOLTA de la Policía
Interior quiere pactar en el epicentro → necesita al ALCALDE
Defensa quiere usar militares        → necesita la FIRMA del Presidente
Minas quiere proteger instalaciones  → CONSUME los escuadrones del desbloqueo
La Defensoría acompaña una operación → esa dupla NO verifica nada más
```

### Tres correcciones que reequilibran el ejercicio

**La concertación vuelve a Interior.** Antes vivía en la ficha del Alcalde y no
comprobaba jurisdicción: un alcalde municipal acababa pactando cierres en dos
regiones ajenas. Ahora `AbrirMesaLocal` es de Interior y **exige al Alcalde en el
epicentro**; `InstalarMesaConVoceros` es del Alcalde y **solo funciona en su
jurisdicción**. Dos pruebas lo custodian.

**La Policía recupera el ESMAD y la escolta.** El dueño del activo más escaso no
podía asignarlo: los escuadrones se movían solos cuando alguien ordenaba una
operación.

**Minas puede asignar el combustible.** La función existía escrita y desconectada:
ningún rol podía invocarla, y por eso el reloj tenía una sola entrada.

### En el código

[`actions.py`](../src/engine/actions.py) · las 34, agrupadas por rol
[`actions.py:1497`](../src/engine/actions.py) · `catalogo_por_rol()` — se genera
desde el código, no se escribe a mano en ningún prompt

---

## 11. Las ocho vistas privadas, por dentro

### En la sala

Cada vista tiene **dos bloques y nada más**: *su detalle* (3–4 datos de su
cartera) y *su alerta* (una línea). Cabe en una pantalla sin desplazamiento.

**Las ocho alertas de un turno real, medidas:**

```
PRESIDENTE   8 de las últimas 8 decisiones salieron sin responsable nominado.
INTERIOR     Hay ventana para una sesión de mesa. Una operación hoy la cierra.
ALCALDE      Bellaflor: menos de 1,3 días de oxígeno y la red hospitalaria al 92 %.
DEFENSA      3 de 5 casos de financiación no aguantarían ante un juez.
POLICÍA      6 denuncias sin verificar contra unidades. Si estallan afuera
             primero, la corrección se leerá como encubrimiento.
DEFENSORÍA   6 denuncias graves sin verificar y 3 duplas. No alcanzan: hay que
             elegir, y declarar públicamente que la otra está en verificación.
TRANSPORTE   Los gremios están evaluando sumarse. Si lo hacen, esto deja de ser
             orden público y pasa a ser cierre logístico nacional.
MINAS        Las Cumbres: 0,5 días de oxígeno. Si mañana no entra nada, −0,5.
```

> **Ocho urgencias legítimas y una escolta.** Ninguna es falsa, ninguna es
> caprichosa, y no caben todas. Eso es el diseño.

### En el motor

Cada vista es una **proyección determinista del estado** — no texto generado. Se
construye leyendo el estado y aplicando el sesgo de la fuente de ese rol.

```python
def vista(estado, rol, rng) -> {"rol", "turno", "detalle", "alerta"}
```

**Tres invariantes que las custodian**, con prueba cada una:

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
problemas. Esto es lo que pasó con cada uno.

| # | El problema | Cómo quedó |
|---|---|---|
| **D1** | La mezcla real de los puntos no cambiaba **nada** | Conectada por dos vías. `test_la_mezcla_real_cambia_el_resultado_de_la_corrida` falla si se desconecta |
| **D2** | El polo de negociación no podía negociar | Interior tiene 4 acciones, incluida la mesa nacional. `acuerdo_verificable` (−8) y `contraprestacion_tramitada` (−6) ya se disparan |
| **D3** | El dueño del ESMAD no podía asignarlo | `DisponerESMAD` y `Escoltar` |
| **D4** | El frente logístico no podía mover carga | Escolta, caravana, gremios, y la prioridad de combustible como criterio permanente |
| **D5** | La cohesión era una rampa determinista | Solo se cobra de día, y ahora se puede reponer |
| **D6** | El paquete detonante no existía | H2 y H3 en el motor; la jornada nacional en el calendario |
| **D7** | El eje de Vocería no tenía mecánica | Parcial: el anuncio verificado y el parte clasificado sí; el encuadre sigue pendiente de la capa 3 |

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
  solo_mesa               147       64
  pasiva                  147       64
  constituida             147       48
  logistica                 —       24
  humanitaria              70       16
```

### La medición completa

```
  estrategia      netas  reap  muert  legit  cohes  credib   resp
  ---------------------------------------------------------------------
  solo_fuerza         1     2     64     15      0      21     24
  solo_mesa           5     4     64     59     56      29     49
  constituida         3     1     48     24     74      21     38
  humanitaria         3     0     16     32     28      35     50
  logistica           3     1     24     41     40      26     39
  pasiva              0     0     64     23     28      45     43
```

**Ninguna domina, que es el criterio.** `solo_mesa` abre más caminos y conserva
las reservas — y deja morir a la misma gente que `pasiva`. `humanitaria` salva al
75 % y lo paga en cohesión y en caminos. `constituida` tiene la mejor mesa y opera
lo justo para gastar legitimidad. `solo_fuerza` se queda sin nada.

> **Si en el debriefing una opción resulta haber sido obviamente correcta desde el
> turno 1, el ejercicio está mal calibrado.** Hoy no la hay.

**Y una advertencia que sigue en pie:** ningún coeficiente está medido. Son
convenciones declaradas, elegidas para que ninguna estrategia pura gane. **La
primera corrida con personas es una medición, no un ejercicio.**

---

## 13. Cómo comprobarlo uno mismo

```bash
# Un ejercicio completo, turno a turno
uv run python scripts/correr_ejercicio.py --estrategia constituida

# Las ocho vistas privadas de un turno real — la v2 en una pantalla
uv run python scripts/correr_ejercicio.py --vistas

# Comparar las seis estrategias: el criterio de calibración
uv run python scripts/correr_ejercicio.py --comparar

# Cambiar la semilla y ver cuánto es ruido y cuánto es señal
uv run python scripts/correr_ejercicio.py --semilla 7 --comparar

# Las 57 pruebas, sin modelo, en dos décimas de segundo
uv run pytest -q

# La API con sus superficies
uv run python -m src.api.main       # http://localhost:8000/api/tablero
                                    #                      /api/vista/Minas
```

**Ninguno de estos comandos necesita clave de API.** El motor corre entero sin
llamar a ningún modelo de lenguaje, y esa es la prueba operativa de que la
arquitectura de cuatro capas se respeta.

### Qué falta todavía

| | Qué | Dónde |
|---|---|---|
| **B1** | Persistencia de la corrida | el historial vive en memoria; reiniciar el servidor la borra |
| **B2** | Las ocho fichas de rol como dato | hoy van en papel, fuera del motor |
| **B3** | Telemetría por turno | no se mide dónde se va el tiempo de la sala |
| **P1–P4** | **La primera corrida con ocho personas** | ninguna prueba de código la sustituye |

Los stubs están marcados donde viven: `grep -rn "PENDIENTE" src/`

---

*Motor v2 · 57 pruebas en verde · semilla `20210511`. Diseño en
[`propuesta.md`](propuesta.md); diagnóstico del motor anterior en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).*

*Escuela de Gobierno · Universidad de La Sabana.*
