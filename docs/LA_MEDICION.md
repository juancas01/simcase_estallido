# La medición — el cómo y el qué

**Implementado.** Este documento es el diseño —y sigue siendo el sitio donde
está el *porqué* de cada pieza— de la lectura que se hace de una corrida cuando
el ejercicio terminó: **cómo destrabaron el país** y **a quién atendieron
mientras lo hacían.**

> **YA ESTÁ CONSTRUIDO, y esto es dónde vive cada parte:**
>
> | De este documento | En el código |
> |---|---|
> | §2 el cómo · §3 el qué · §5 el residuo · §6 el cruce | [`src/engine/lectura.py`](../src/engine/lectura.py) — `calcular(motor) -> dict`, pura y solo al cierre |
> | §4 qué decisión imputa a quién | dos atributos de clase en cada `Accion` (`via`, `atiende`) y un método `imputacion(estado)` para las que se imputan por su objeto, en [`actions.py`](../src/engine/actions.py) |
> | §7 cómo se garantiza que no lo vean | `GET /api/lectura`, `/api/metricas` y `/api/debriefing` responden **409 mientras la sala no haya cerrado**, en [`main.py`](../src/api/main.py) |
> | §8 cómo se presenta al final | la pestaña 2 de [`Debriefing.jsx`](../web_ui/src/components/Debriefing.jsx) |
> | de dónde salen los datos | el archivo de la corrida, [`bitacora.py`](../src/engine/bitacora.py) (**B1**) |
>
> **Cuatro decisiones que la §10 dejaba abiertas se tomaron.** Están escritas en
> `PENDIENTES.md · B14` y son revisables sin tocar el diseño:
>
> 1. **La capa 1 no se revela en el debriefing** — decisión del equipo docente.
>    La puerta no se construye, así que no hay que recordar no abrirla.
> 2. **Las bandas del saldo son provisionales**: normalizadas al peor caso del
>    escenario y **marcadas «sin calibrar» en la propia salida**. Calibrarlas es
>    tocar cuatro constantes de `lectura.py` y nada más.
> 3. **Imputación doble = una entera a cada público.** Ponderar por mitades o por
>    costo cambia todos los repartos, así que la regla vive en una sola línea y
>    **viaja declarada dentro de la respuesta**.
> 4. **La comparación contra las siete salas ficticias queda fuera** — necesita
>    corridas reales (**C5**). Lo que sí hay para no volar a ciegas:
>    `scripts/correr_ejercicio.py --lectura --todas`, que imprime las siete
>    firmas y **falla si dos se leen igual**.
>
> **Una cosa que el diseño no preveía y el código tuvo que resolver:** dónde
> guardar la imputación. No cabe en `Estado` ni en `Decision`, porque
> `/api/tablero` serializa el registro con `asdict` y el vocabulario de la §2
> se habría publicado solo, en mitad de la jornada 2. Vive en una lista
> paralela del motor (`motor.imputaciones`), y hay pruebas que barren todas las
> respuestas en vivo buscando estas palabras.

> **Ninguna de estas cifras se ve durante la sesión.** No es una preferencia de
> presentación: es la condición para que midan algo. Un marcador visible deja de
> medir la conducta y pasa a producirla, y entonces lo que se lleva la sala al
> final no es un retrato suyo sino la puntuación de un videojuego. La §7 dice
> cómo se garantiza eso con el servidor y no con un rótulo.

| | |
|---|---|
| **Qué mide** | dos preguntas: por qué vía se abrió el país, y a quién se atendió |
| **Cuándo se calcula** | al cierre, leyendo el pliego y la traza. **No es una variable del mundo** |
| **Quién lo ve** | el equipo docente, en el debriefing. Nunca los participantes durante la corrida |
| **De qué depende** | de **B1** (el archivo de la corrida) y se presenta dentro de **B7** (el debriefing) — **los tres, hechos** |
| **Qué NO es** | un puntaje, un ranking, ni una respuesta correcta |

---

## 1 · Dos preguntas, dos instrumentos, y por qué no son el mismo

La pregunta del ejercicio no es «¿lo hicieron bien?». Es **«¿qué clase de
gobierno fueron?»**, y eso tiene dos ejes que no se pueden mezclar en un número:

|  | La pregunta | El instrumento | De dónde sale |
|---|---|---|---|
| **EL CÓMO** | ¿Por qué vía destrabaron? | **seis vías en dos familias** + tres calificadores | el pliego de decisiones y los eventos |
| **EL QUÉ** | ¿A quién atendieron? | **cuatro públicos**, con dos columnas | la imputación de cada decisión, y el mundo al cierre |

Y el QUÉ tiene dos columnas porque son dos cosas distintas y la sala las va a
confundir si se las damos juntas:

> **ATENCIÓN** es dónde gastaron sus decisiones. **SALDO** es cómo terminó cada
> público. **No es lo mismo atender a alguien que servirle**, y el cruce de las
> dos columnas es el material más útil del debriefing (§6).

Las cuatro reservas del tablero —legitimidad, credibilidad, respaldo, cohesión—
**no sirven para esto y no hay que reutilizarlas.** Miden cómo le fue al
Gobierno. Una sala puede terminar con la legitimidad alta sin haber atendido
nunca a la ciudadanía: le fue bien por otra vía. Además son visibles, y cualquier
cosa que se derive de ellas sería un marcador que la sala puede perseguir.

---

## 2 · EL CÓMO — seis vías, en dos familias

### De dónde salen las tres primeras: un cierre se acaba por tres razones

Un punto de cierre existe porque hay gente sosteniéndolo. **Deja de existir
cuando esa gente deja de sostenerlo, y eso pasa exactamente por tres motivos.**
No son una taxonomía que yo proponga: es el campo `modo_apertura` del motor, y la
sala ya lee esas tres palabras en el mapa cada jornada.

| Vía | Qué pasó en el punto | El motor lo llama | Cuánto tarda |
|---|---|---|---|
| **DESPEJAR** | los quitaron de en medio | `fuerza` | **1 paso** |
| **CONCERTAR** | lo levantó quien lo sostenía | `concertacion` | **2 jornadas** |
| **DESGASTAR** | se quedó sin quien lo sostuviera | `desgaste` | **3 jornadas y suerte** |

**Los tres plazos son el diseño entero del subsistema.** Despejar es lo único
inmediato, y por eso es lo que se pide cuando ya no queda tiempo — y lo que
menos aguanta: un punto abierto por la fuerza puede volver a cerrarse **esa
misma noche** (`PASOS_ANTES_DE_REABRIR = 1`). Concertar tarda dos jornadas, de
modo que **abrir una mesa en la jornada 5 es no abrirla**, y aguanta. Desgastar
no se ordena: se espera.

### Desgastar tiene dos caras y son moralmente opuestas

Es la vía que peor se entiende y la que más falta hace explicar. **No es
esperar.** Un cierre se desgasta cuando `apoyo_local` cae por debajo de 0,25 y
**se sostiene ahí tres jornadas**; solo entonces hay una tirada del 20 % por
turno. Es lenta a propósito: *«si el desgaste es barato y rápido, la sala
descubre que basta con esperar»*, y ni la fuerza ni la mesa importarían.

Lo que hace que el barrio deje de respaldar el cierre son **cuatro cosas, y tres
son decisiones de la sala**:

| Qué baja el apoyo | Cuánto | Quién |
|---|---|---|
| esquema humanitario municipal | **−0,12** | Alcalde |
| paso humanitario permanente requerido | −0,06 | Interior |
| instrumentos sectoriales | −0,06 y decreciente | Agricultura |
| **la región lleva menos de dos días de comida** | −0,05 por turno | **nadie: el hambre** |

> **Y ahí está la incomodidad.** Las tres decisiones que más atienden al barrio
> son las tres que le disuelven el bloqueo. El motor lo dice en voz alta —*«reduce
> el incentivo material del cierre sin alimentar la movilización»*— y es
> exactamente lo que hace un gobierno que atiende: **atender es también
> desmovilizar.** La cuarta fila es la misma apertura conseguida por hambre.
>
> **Mecánicamente son idénticas. En el debriefing no pueden serlo**, y por eso la
> lectura las separa: por cada punto abierto por desgaste, si en su región había
> alguna de las tres decisiones vigentes → *lo desgastaron*; si no la había y el
> semáforo estaba en rojo → **se les cayó de hambre**.

### Y las otras tres no abren ningún punto

Aquí está lo que la taxonomía del motor no puede ver, porque `modo_apertura`
solo habla de puntos que se abrieron. **Una sala destraba el país de tres
maneras más, y ninguna aparece en ese campo.**

| Vía | Qué le hace a la crisis | Cómo se reconoce |
|---|---|---|
| **SORTEAR** | el cierre **sigue en pie** y lo que bloqueaba pasa igual | escoltas, caravanas, pasos seguros, corredor humanitario, prioridad de combustible, acopio concentrado |
| **CONSTITUIR** | no toca ningún punto: **cambia lo que cuesta todo lo demás** | las banderas — reglas escritas, protocolos, líneas rojas, criterios de priorización |
| **ENCUADRAR** | cambia **lo que el país cree que está pasando** | publicar el parte, el mapa, el balance, el calendario · presentar inteligencia · ir a mirar |

**SORTEAR es la vía que el tablero no nombra y la sala sí usa.** Sacar el oxígeno
de Las Cumbres por un corredor escoltado no abre un solo punto de cierre y
resuelve lo único irreversible del caso. Sin esta categoría, una sala que hizo
exactamente lo que había que hacer sale medida como pasiva — y ese sería un error
del instrumento, no un retrato de la sala.

**CONSTITUIR no destraba nada y es lo que decide el precio de destrabar.** Los
cinco mitigadores juntos dividen el riesgo de incidente por tres y medio. Una
sala que constituye el primer día y opera el tercero está jugando otro juego que
una que opera el primero. Es la vía que **no se ve rendir**: su efecto es todo lo
que no pasó.

**ENCUADRAR es real y el motor ya la modela**, aunque no lo parezca:
`encuadre_dominante` toma cuatro valores —`represion | desorden | negociacion |
abandono`—, el calendario de agotamiento sube el `panico` de la región, y anunciar
abierto un corredor que no deja pasar se desmiente solo y **sube la intensidad
cuatro puntos**. Ir a mirar entra aquí porque es lo que le da valor a decir: en
este ejercicio, verificar no abre nada, autoriza a hablar.

### Los nombres, y por qué estos

**Las seis son verbos**, siguiendo la regla que este repositorio ya se dio para
nombrar acciones —*«el nombre es un verbo y cabe en un renglón»*—. Miden **actos
de la sala**, no estados del mundo, y un sustantivo los volvería categorías.

| Verbo | Y el motor / la pantalla lo llaman | Por qué no lo llamé de otra manera |
|---|---|---|
| **Despejar** | `fuerza` · «Fuerza» | es el verbo operativo real: se despeja una vía |
| **Concertar** | `concertacion` · «Concertación» | palabra del motor, sin cambiarla |
| **Desgastar** | `desgaste` · «Desgaste» | ídem, en activa, porque a veces se hace y a veces se sufre |
| **Sortear** | — | descartado **«rodeo»**: *andarse con rodeos* lo vuelve una acusación, y esta vía es a menudo la respuesta correcta |
| **Constituir** | — | descartado **«regla»**: choca de frente con `reglas_escritas` y con las reglas de empleo de la fuerza, que son **una** bandera de trece |
| **Encuadrar** | — | descartado **«información»**: es el nombre de una de las tres clases de acción en pantalla, y serían dos cosas con un nombre |

> **Las tres primeras conservan la palabra del motor a propósito.** La sala ya lee
> «Fuerza», «Concertación» y «Desgaste» en el mapa en cada jornada
> (`etiquetas.jsx`). Inventar un segundo vocabulario para las mismas tres cosas
> es la deriva contra la que este repositorio ya tiene pruebas.

### Una acción puede llevar dos vías, y esas son las interesantes

`via` se declara como tupla, igual que `atiende`. No es una concesión: las
acciones de doble vía son las que mejor enseñan.

| Acción | Vías | Por qué las dos |
|---|---|---|
| Abrir paso a lo humanitario | **sortear + desgastar** | mete la ayuda por encima del cierre **y** le quita al cierre su razón de ser |
| Exigir un paso humanitario permanente | **sortear + desgastar** | ídem, y además se cobra afuera |
| Aliviar a los productores | **sortear + desgastar** | ídem, en el campo y con rendimientos decrecientes |
| Acordar ventanas de paso | **concertar + sortear** | se pacta con quien cierra, y lo que se pacta no es abrir |

**Ninguna acción es solo desgastar, y conviene verlo:** la sala **no puede
ordenar** un desgaste. Le llega como consecuencia de haber atendido, o como
consecuencia del hambre. Es la única de las seis que no se pide.

### Los tres calificadores

Una cuenta de vías no dice todavía qué clase de gobierno fue. Tres cortes que los
datos ya permiten y que valen más que el reparto mismo:

**C1 · ¿Anticiparon o reaccionaron?** Por cada bandera,
`banderas.activada_en_turno` contra la ventana del primer incidente. El motor ya
tiene opinión sobre esto —`COSTO_RESERVAS["constitutiva_reactiva"] = 0.5`, el
rédito se parte por dos si la regla llega después— pero **la sala nunca ve que
llegó tarde**, solo ve que rindió poco.

**C2 · ¿Aguantó lo que abrieron?** Aperturas contra reaperturas, **por vía**. Es
lo que separa «abrimos cuatro» de «abrimos cuatro y tres se volvieron a cerrar
esa noche». Hoy `metricas()` da `aperturas_netas` y `reaperturas` en total, sin
repartir por vía — hay que repartirlos.

**C3 · ¿Miraron antes de mover?** De los puntos intervenidos por la fuerza,
cuántos habían sido verificados antes. `Nodo.ultima_verificacion_turno` contra
`Nodo.intervencion_fuerza_turno`: los dos campos existen y nadie los cruza.

> **C3 es la salida más barata de todo este documento** y la que más se va a
> sentir en la sala: *«de los seis puntos que operaron, uno estaba mirado»*. No
> hace falta ninguna teoría para entender qué significa.

### Lo que se entrega del CÓMO

No un puntaje: **una firma**. La vía dominante, la secundaria, la que no usaron
nunca, y los tres calificadores. Una línea que se lee en voz alta:

> *«Despejaron y sortearon. No concertaron ni una vez. Constituyeron después del
> primer incidente, tres de cinco aperturas se revirtieron esa misma noche, y
> operaron cinco puntos habiendo mirado uno.»*

---

## 3 · EL QUÉ — cuatro públicos

Cuatro, tal como los pediste, con una definición que los separa de verdad:

| Público | Qué quiere | Qué lo enfurece |
|---|---|---|
| **EMPRESA** | el país **abierto y previsible** | el bloqueo largo, y la regla que cambia sin avisar |
| **GREMIOS** | que a **ellos** les pase algo: escolta, cupo, alivio, ventana | el ultimátum sin respuesta y la promesa incumplida |
| **CIUDADANÍA** | seguir **viva**, comer, y no ser reprimida | el muerto evitable y el hospital sin oxígeno |
| **INTERNACIONAL** | **proporcionalidad y verificación** | la tropa en la multitud y la denuncia que nadie miró |

**Empresa y gremios no son lo mismo y la diferencia es el punto.** La empresa
quiere que el país funcione —le da igual quién abra el corredor—. Los gremios
quieren que el corredor sea **el suyo**: son los camioneros que pueden sumarse al
paro (`posicion_gremios`) y los productores del campo que esperan cupos y
alivios. Una sala puede tener a la empresa contenta y a los gremios en la calle.

### Columna A · ATENCIÓN — dónde gastaron las decisiones

Cada decisión ejecutada imputa a cero, uno o dos públicos. El reparto **suma
100 % y por eso mide una prioridad**: atender a uno es no atender a otro, que es
la aritmética de todo el resto del ejercicio.

**Hay un residuo y hay que nombrarlo.** Las decisiones que no atienden a nadie
—fijar el registro escrito, exigir el protocolo de vocería, reunir a los
alcaldes— son **el gobierno de sí mismo**: la mesa ordenándose. Casi todas son de
vía **constituir**, y por eso las dos lecturas se leen juntas. No es tiempo
perdido; abarata todo lo demás. Pero una sala que gastó el 40 % de sus decisiones
ahí tiene una conversación pendiente, y hoy nadie se la puede plantear porque
nadie lo cuenta.

### Columna B · SALDO — cómo terminó cada público

**No sale de las decisiones: sale del mundo.** Si el saldo se dedujera de lo que
la sala ordenó, la medición sería circular —atender mucho daría buen saldo por
construcción— y no habría nada que aprender.

| Público | Los hechos que lo componen |
|---|---|
| **EMPRESA** | pérdida acumulada = Σ por ventana de `costo_diario_mm_cop × (1 − caudal)` de cada corredor · exposición de infraestructura (`riesgo_infraestructura`) · **previsibilidad**: acuerdos rotos + reaperturas |
| **GREMIOS** | `posicion_gremios` al cierre · **jornadas entre el ultimátum y la primera decisión dirigida a ellos** · escoltas logradas contra atacadas · alivios por región · `riesgo_sanitario_asumido` |
| **CIUDADANÍA** | **muertes evitables** · jornadas-región en rojo ponderadas por población aguas abajo · incidentes con víctima e imágenes virales · apoyo local medio al cierre |
| **INTERNACIONAL** | `respaldo_internacional` al cierre · corredores humanitarios requeridos contra negados · denuncias verificadas contra estalladas · **mitigadores encendidos en el momento de operar** · ventanas con militares en multitudes |

**El saldo se entrega en banda y con sus hechos debajo**, no como índice suelto:
«**Empresa: mal** — 41 200 MM COP de pérdida, dos instalaciones vitales sin
custodiar cinco jornadas, tres aperturas revertidas». La cifra sola no abre
ninguna conversación; la lista de hechos sí. Debajo puede vivir un 0–100 para
comparar salas entre sesiones, y ese número **es del equipo docente, no de la
sala**.

---

## 4 · Qué decisión imputa a quién

La imputación va **declarada en cada acción**, como ya van `codigo`, `rol` y
`clase` — no en una tabla aparte que se desincroniza. Dos atributos nuevos en
`Accion`:

```python
via: tuple        # 1 o 2 de: despejar | concertar | desgastar | sortear | constituir | encuadrar
atiende: tuple    # 0, 1 o 2 de: empresa | gremios | ciudadania | internacional
```

Y una prueba que exige que **las 37 los declaren**, del mismo estilo que las que
ya impiden que una acción se quede sin ejemplo de consola.

> **La regla de imputación es una sola pregunta, y conviene que sea literal:**
> *si esta decisión sale bien, ¿quién duerme mejor esa noche?* No «a quién
> beneficia en abstracto» ni «qué valores expresa». Una pregunta con respuesta.

### Las 37

| Rol | Acción | Vía | Atiende |
|---|---|---|---|
| Presidente | Dejar todo por escrito | constituir | — |
| Presidente | Decir qué no se negocia | constituir | empresa |
| Presidente | Autorizar al Ejército | despejar | empresa |
| Presidente | Reunir a los alcaldes | constituir | — |
| Presidente | Ir al epicentro en persona | encuadrar | ciudadanía |
| Interior | Poner un solo vocero | constituir | — |
| Interior | Sentar al Comité del Paro | concertar | ciudadanía |
| Interior | Abrir una mesa en un punto | concertar | ciudadanía |
| Interior | Ofrecer algo a cambio | concertar | ciudadanía |
| Interior | Exigir un paso humanitario permanente | **sortear + desgastar** | ciudadanía · internacional |
| Interior | Poner custodia a una instalación | despejar | empresa |
| Alcalde | Exigir que le consulten la fuerza | constituir | ciudadanía |
| Alcalde | Sentarse con los voceros del punto | concertar | ciudadanía |
| Alcalde | Abrir paso a lo humanitario | **sortear + desgastar** | ciudadanía |
| Alcalde | Publicar el conteo de la ciudad | encuadrar | internacional |
| Defensa | Poner reglas a sus unidades | constituir | internacional |
| Defensa | Desbloquear un punto por la fuerza | despejar | empresa |
| Defensa | Mover tropa a donde haga falta | despejar | empresa |
| Defensa | Mostrar quién financia los cierres | encuadrar | — |
| Defensa | Mandar equipos al terreno | encuadrar | internacional |
| Policía | Separar lo confirmado de lo estimado | constituir | internacional |
| Policía | Acordar una sola forma de verificar | constituir | internacional |
| Policía | Concentrar el ESMAD | despejar | empresa |
| Policía | Escoltar una caravana o misión médica | sortear | **según la carga** |
| Policía | Relevar a las unidades cansadas | despejar | — |
| Transporte | Fijar el orden de los corredores | constituir | **según el orden** |
| Transporte | Decidir a qué va el combustible | constituir | **según el orden** |
| Transporte | Organizar una caravana | sortear | empresa · gremios |
| Transporte | Hablar con los camioneros | concertar | gremios |
| Transporte | Acordar ventanas de paso | **concertar + sortear** | empresa · gremios |
| Transporte | Publicar el mapa de cierres | encuadrar | empresa |
| Agricultura | Poner los alimentos en la prioridad | constituir | ciudadanía |
| Agricultura | Sentarse con el campo | concertar | gremios |
| Agricultura | Aliviar a los productores | **sortear + desgastar** | gremios |
| Agricultura | Publicar lo que se está perdiendo | encuadrar | gremios |
| Agricultura | Concentrar el despacho de alimentos | sortear | gremios · ciudadanía |
| Agricultura | Decir cuántos días quedan | encuadrar | ciudadanía |

**El reparto que sale de aquí, y lo que dice del caso** —contando las dos vías
de las acciones dobles—: constituir **11**, encuadrar **7**, concertar **7**,
sortear **7**, despejar **6**, desgastar **3 y ninguna propia**. Tres lecturas:

- **Casi un tercio del repertorio no destraba nada por sí solo.** Constituir es
  la vía más numerosa y la única cuyo efecto es enteramente aquello que no llegó
  a pasar. Una sala que la ignora no lo nota en ninguna pantalla.
- **Despejar es la más corta del repertorio y la que la sala más pide.** Seis
  acciones, y son las que se ordenan cuando el reloj aprieta.
- **Desgastar aparece tres veces y nunca sola** (§2). No se ordena: llega
  pegada a las tres acciones humanitarias, o de que la región pase hambre.

### Las cuatro que se imputan por su objeto, y son las mejores

**La imputación lee los argumentos de la acción ejecutada, no solo su clase.**
Cuatro filas dicen «según» arriba, y son justamente donde la sala declara una
prioridad con todas las letras:

| Acción | Cómo se imputa |
|---|---|
| **Decidir a qué va el combustible** | por el orden que fijaron: `mision_medica` → ciudadanía · `transporte_alimentos` → ciudadanía + gremios · `fuerza_publica` → — · `consumo_general` → **empresa** |
| **Fijar el orden de los corredores** | por la clase que encabeza el criterio |
| **Escoltar** | misión médica → ciudadanía · caravana de carga → gremios + empresa |
| **Abrir una mesa / operar un punto** | por la **región** del punto: la epicentro, la que tiene el reloj de oxígeno más corto, o una rural |
| **Abrir paso a lo humanitario** | por la región donde cae: la vía `desgastar` solo se imputa si allí había un cierre que efectivamente se deshizo |

> **`FijarPrioridadCombustible` es, literalmente, la pregunta que hiciste.**
> «¿Priorizaron el dinero o la vida de las personas?» tiene ahí una respuesta
> escrita por la propia sala, ordenada de primero a cuarto, con hora y con
> responsable. No hay que inferirla de nada.

---

## 5 · El problema honesto: los dos ejes no son independientes

**Hay que decirlo antes de construir nada.** En el repertorio actual, de las diez
acciones que atienden a la empresa, **seis son por vía de fuerza** y ninguna la
atiende sin gastar capacidad de la fuerza pública. Consecuencia:

> «Priorizaron a la empresa» y «abrieron por la fuerza» van a salir
> correlacionados casi siempre. **No porque la sala piense así, sino porque el
> repertorio está hecho así.**

Tres salidas, y la elección es del equipo docente:

| | Qué se hace | Qué cuesta |
|---|---|---|
| **A · Aceptarlo y decirlo** | se reporta la correlación **como hallazgo del caso**, no de la sala: *«en este país, atender a la empresa es casi siempre mandar al ESMAD»* | nada, y es una conversación excelente |
| **B · Medir el residuo** | la celda que importa: **de las decisiones que atendieron a la empresa, cuántas fueron por una vía distinta de la fuerza** | nada. Es la que distingue una sala imaginativa de una obediente |
| **C · Añadir repertorio** | una acción que atienda a la empresa sin fuerza —reapertura económica concertada, ventanas comerciales pactadas | toca el diseño del juego y hay que recalibrar |

**Recomiendo A + B, y dejar C fuera de esta versión.** Cambiar el repertorio para
que la medición salga más bonita es medir el instrumento.

> **Y el mismo cuidado al revés, que es el que se nos puede escapar:** atender a
> la ciudadanía por la vía humanitaria **desgasta el bloqueo** (§2). Una sala
> puede atender de buena fe y estar desmovilizando, y otra puede desmovilizar a
> sabiendas usando el mismo instrumento. **La lectura no puede distinguirlas y no
> debe intentarlo**: enseña las dos cosas juntas y deja que lo discuta la sala.

---

## 6 · El cruce que vale el debriefing entero

Atención contra saldo, por público. Cuatro celdas y las cuatro son una
conversación distinta:

|  | **Saldo bueno** | **Saldo malo** |
|---|---|---|
| **Atención alta** | *Lo atendieron y funcionó.* Lo único que se puede llamar acierto | **«Lo atendieron y no le sirvió.»** Es un problema de **cómo**, no de a quién. La celda más útil del cuadro |
| **Atención baja** | *Le fue bien sin ustedes.* Suerte, o el trabajo de otro. Conviene no cobrárselo | **«Nadie lo miró.»** El resultado más duro y el más frecuente |

Y la salida de una sola línea, que es la que se recuerda:

> **EL PÚBLICO QUE NADIE MIRÓ** — *«Ninguna de sus 41 decisiones atendió a los
> gremios. Se sumaron al paro en la jornada 3.»*

**Contra qué se compara.** El repositorio ya tiene siete salas ficticias
(`scripts/correr_ejercicio.py --comparar`: `solo_fuerza`, `solo_mesa`,
`constituida`, `humanitaria`, `logistica`, `agroalimentaria`, `pasiva`). Cada una
tiene un perfil de vías y de atención que se calcula una vez y se guarda. Así la
sala no se compara con un ideal inventado sino **con lo que habría pasado si
hubiera jugado en una sola dirección** — y ver que su perfil se parece al de
`solo_fuerza` dice más que cualquier nota.

---

## 7 · Cómo se garantiza que no lo vean

Cinco medidas, y **ninguna consiste en no dibujarlo en la pantalla**:

**1 · No hay campo nuevo en `Estado`.** Es lo que más protege. Todo se calcula al
cierre desde `registro`, `historial` y los eventos. Lo que no existe como
variable del mundo no puede colarse en `vista_publica()` ni en ninguna de las
siete vistas por un descuido de serialización.

**2 · Vive en un módulo que la ruta de juego no importa.** `src/engine/lectura.py`,
y una prueba que comprueba que ni `views.py` ni los endpoints en vivo lo
importan. Es la misma forma de guardarraíl que ya usa el repositorio para la capa 1.

**3 · El servidor rechaza, no la pantalla esconde.** `GET /api/lectura` devuelve
**409 mientras `sala["cerrado"]` sea falso.** El pestillo ya existe y ya se usa
para las órdenes. *Una regla que el software garantiza vale más que una que el
software recomienda* — está escrito en `main.py` a propósito de la noche, y vale
igual aquí.

**4 · Ni el vocabulario sale antes.** Si la palabra «público empresarial» aparece
una sola vez en una respuesta del servidor durante la corrida, la sala empieza a
jugar contra ella. Una prueba que barre todas las respuestas en vivo buscando los
términos nuevos — es exactamente el tipo de prueba que falta y que **B9** pide.

**5 · `/api/metricas` hay que cerrarlo también.** Hoy está abierto, sin llave, y
aunque ninguna pantalla lo consulte, un participante con la URL ve
`ratio_fuerza_concertacion` en mitad de la jornada 2. **Es un agujero que ya
existe**, independiente de esta propuesta, y esta propuesta lo agranda.

> **Y esto no se llama «métricas».** El tablero ya tiene una tarjeta con ese
> rótulo —las cuatro reservas y la presión en la calle—, que es pública, se mira
> cada jornada y está pensada para mirarse. Reutilizar la palabra garantiza que
> alguien acabe pintando lo uno donde va lo otro. **Se llama la lectura**, y vive
> en `lectura.py`, `/api/lectura` y el panel del debriefing.

---

## 8 · Cómo se presenta al final

Dentro del debriefing (**B7**), después del panel del país recibido y entregado,
y antes del pliego. Cinco piezas, en este orden:

| | Pieza | Qué se proyecta |
|---|---|---|
| **1** | **La firma de la sala** | una frase, la de §2. Se lee en voz alta y se deja en pantalla |
| **2** | **Las seis vías** | barra apilada en dos bloques —las tres que abren un punto y las tres que no—, y debajo los tres calificadores |
| **3** | **La rosa de atención** | cuatro ejes, el reparto de decisiones, y el residuo de «gobierno de sí mismo» aparte |
| **4** | **Atención × saldo** | el cuadro 2×2 de §6, con los hechos de cada público desplegables |
| **5** | **El público que nadie miró** | una línea, y su consecuencia con jornada y hora |

**Y una decisión de contenido que no es mía:** ¿se revela la capa 1 en este
punto? Que la denuncia que estalló era falsa, que el punto que operaron tenía
91 % de protesta legítima. **Es el remate pedagógico del caso entero** y también
la única salida que tendría la verdad del motor. Si se hace, hay que hacerlo por
una sola función, después del cierre, y extender la prueba que hoy garantiza que
la capa 1 no sale nunca para que permita esa única puerta y ninguna otra.

> **RESUELTA: no se revela.** Decisión del equipo docente. La puerta **no se
> construye**, que es más fuerte que construirla y acordar no usarla: la prueba
> que garantiza que la capa 1 no sale nunca sigue sin excepciones, y el
> debriefing implementado no la toca. Si algún día se decide lo contrario, el
> párrafo de arriba sigue siendo la forma correcta de hacerlo.

**Lo implementado son estas cinco piezas más el país recibido/entregado, la
línea declarada contra la ejecutada, el pliego por ventanas y los tres
momentos**, en cinco pestañas — la lectura es la segunda, en el sitio que este
apartado le da.

---

## 9 · Lo que esto no mide, dicho antes de que alguien lo suponga

- **No mide si acertaron.** No hay respuesta correcta en el caso y esto no la
  introduce por la puerta de atrás.
- **No atribuye consecuencias a decisiones.** Varias caen en la misma ventana y
  el mundo además se mueve solo. Eso ya se decidió y se decidió bien.
- **No mide quién habló en la sala.** Ni quién compartió su vista privada. Eso se
  observa mirando la sala (**P2**, **P4**), y la corrección al respecto ya está
  en **B3**.
- **No mide intención.** Una sala puede priorizar a la ciudadanía por convicción
  o porque el reloj del oxígeno era lo único urgente. La medición no las
  distingue y **no debe fingir que sí**.
- **Con cinco jornadas y cuatro regiones, los agregados pequeños son ruido.** Un
  reparto de 38 %/31 % no distingue nada. Se presenta en bandas y con la cautela
  escrita en la propia pantalla, igual que se hizo en B3.

---

## 10 · Lo que hay que decidir y lo que hay que medir

**Del equipo docente** (van a la Parte 3 de `PENDIENTES.md`):

| | Decisión |
|---|---|
| **1** | ¿Se les anuncia en el briefing que habrá una lectura? **Anunciar los ejes los hace jugables**; no anunciar nada puede sentirse como una trampa. Mi recomendación: anunciar que la habrá, no cuáles son |
| **2** | ~~¿Se revela la capa 1 en el debriefing? (§8)~~ · **DECIDIDO: no.** La puerta no se construye |
| **3** | ¿La celda «le fue bien sin ustedes» se dice en voz alta? Es la más incómoda |
| **4** | ¿Se guarda el perfil entre cohortes para comparar promociones? Cambia el consentimiento que hay que pedir |

**Sin calibrar** (van con **C5** y **B13**). Los tres están **puestos con un
valor provisional y declarado**, no en blanco: el instrumento corre, y lo que
falta es medirlo contra corridas reales.

| | Qué hay que fijar | Qué hace hoy el código |
|---|---|---|
| **1** | Si una decisión que atiende a dos públicos imputa media a cada uno o una entera a los dos. Cambia todos los repartos | **una entera a cada uno.** Vive en una sola línea de `_atencion()` y **viaja declarada en la respuesta** (`"regla"`), así que la pantalla dice bajo qué convención está leyendo |
| **2** | Los cortes de banda de cada saldo. Hoy no hay ninguna corrida real contra la que ponerlos | **normalizados al peor caso del escenario** y marcados `"provisional · sin calibrar"` en la propia salida. Son cuatro constantes al principio de `lectura.py` |
| **3** | Si la atención se cuenta por decisión o se pondera por lo que costó. Doce decisiones baratas no deberían pesar como una cara — y ponderar por costo mete las reservas por la ventana | **por decisión.** Ponderar por costo se descartó por lo que dice esta misma celda; queda abierto para C5 |

**Y una cautela que el código añade y este documento no pedía:**
`scripts/correr_ejercicio.py --lectura --todas` corre las siete estrategias
puras y **sale con error si dos firmas se leen igual**. No calibra nada, pero
detecta lo peor que puede pasarle a este instrumento: que describa el escenario
en vez de a la sala.

**Y un defecto que apareció mirando el catálogo para escribir esto**, ajeno a la
medición pero que la estorba: **`codigo` dejó de ser único dentro de un rol** tras
el reparto de las dos carteras. Interior tiene dos `A1` y dos `A4`; Policía, dos
`A2`; Transporte, dos `A2` y dos `A3`; Agricultura, dos `A4`. Cada acción heredada
se trajo el código de su rol anterior. No rompe nada hoy —nada indexa por
`(rol, codigo)`— pero cualquier informe que cite acciones por código va a
confundir dos filas, y este es exactamente ese informe.
