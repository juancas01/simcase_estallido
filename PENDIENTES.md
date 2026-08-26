# Pendientes

Lo que falta para correr esto con ocho personas en una sala. **Este es el único
sitio donde se lleva la cuenta**: si algo está pendiente y no está aquí, es que
se me pasó.

Va ordenado por lo que bloquea. Hay cuatro clases y no se resuelven igual:

| Clase | Quién lo resuelve | Sección |
|---|---|---|
| **Probar** — lo que se puede hacer ya, sin decidir nada | cualquiera, hoy | [P](#p--lo-que-se-puede-probar-ya) |
| **Decisiones** — no son técnicas y no son mías | el equipo docente | [A](#a--decisiones-que-no-son-mías) |
| **Código** — está diseñado y no escrito | yo | [B](#b--código-que-falta) |
| **Calibración** — solo se resuelve midiendo | la primera corrida | [C](#c--calibración) |

---

## En una mirada

| | Pendiente | Bloquea | Estado |
|---|---|---|---|
| **P1–P4** | las cuatro pruebas, en orden | nada — se pueden hacer hoy | listas para correr |
| **A1** | cuántos dispositivos, o papel | el montaje de la sala | esperando |
| **A2** | quién opera la consola | el guion de la sesión | esperando |
| **A3** | ¿con llave o sin llave la primera vez? | qué se está midiendo | esperando |
| **A4** | el contenido exacto de las ocho vistas | la versión definitiva | se decide probando |
| **A5** | cerrar el territorio ficticio | las fichas impresas | nombres provisionales puestos |
| **B1** | persistencia de la corrida | el debriefing | no existe |
| **B2** | las ocho fichas de rol, en datos | imprimir los sobres | `data/roles/` vacío |
| **B3** | telemetría por turno | medir el ejercicio | no existe |
| **B4** | el hecho H1 del paquete detonante | el turno 1 completo | falta 1 de 4 |
| **B5** | presupuesto de latencia medido | la fase de consecuencias | hay timeout, falta medirlo |
| **C1–C3** | tres cosas que solo se ven con personas | la primera corrida real | esperando |

Lo que **sí** funciona está en el README, sección «Estado actual», y en
[`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md).

---

## Cómo verlos desde el código

```bash
grep -rn "PENDIENTE\|TODO" src/
```

Cada marca lleva el identificador de esta lista (`PENDIENTE(B1)`), así que se
puede ir en las dos direcciones: del código a la explicación y de la explicación
al código.

---

## P · Lo que se puede probar ya

**Nada de esto depende de ninguna decisión pendiente.** Cuatro pruebas, cada una
responde una pregunta distinta, y ninguna necesita la siguiente para ser útil.

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

### P2 · Las pantallas — 30 min, dos personas

**¿Se entienden sin explicación?**

```bash
cd web_ui
npm install
npm run build
cd ..
uv run python -m src.api.main        # http://localhost:8000
```

**Con dos proyectores:** uno con `/tablero`, otro con `/esfera`, un portátil con
`/consola` y otro con una vista privada.

**Con una sola pantalla o un portátil:** `/tablero` ya lleva la esfera pública
como **barra lateral plegable** —el botón está arriba a la derecha— y con eso
basta. Cuando está plegada, el botón sigue mostrando cuántas denuncias hay sin
verificar, que es lo que hace que alguien la abra.

> **Barra y no pestaña.** La distancia entre lo que el Estado tiene por cierto y
> lo que se dice solo se percibe **simultánea**. Una barra abierta se ve junto al
> tablero; una pestaña sustituye una cosa por la otra y elimina justamente lo que
> hay que enseñar.

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
turno en que la mesa dejó de ser una mesa · las agendas reservadas, que se
revelan y no se puntúan.

Y una comprobación nueva de la v2: **en el minuto 4 de la deliberación, mire
cuántas personas están mirando su pantalla.** Si hay alguna, una de las cinco
reglas de §6.3 de la propuesta se rompió.

---

## A · Decisiones que no son mías

Van con recomendación porque tener una es más útil que no tenerla, pero las cinco
son del equipo docente.

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

## B · Código que falta

### B1 · Persistencia de la corrida

**Dónde:** [`src/engine/simulation.py`](src/engine/simulation.py), en el
constructor de `MotorCrisis`.

El motor guarda `historial` en memoria y la semilla en el objeto. Al cerrar el
proceso se pierde todo — y el debriefing dura veinte minutos, más que cualquier
turno.

Hace falta escribir a disco la semilla, el estado inicial, el log de acciones y
los resultados por turno. Con eso **la corrida se repite con una decisión
cambiada**, que es la mejor herramienta que este diseño ofrece y ahora mismo no
se puede usar.

### B2 · Las ocho fichas de rol, en datos

**Dónde:** [`data/roles/`](data/roles/) (vacío)

Las fichas del Manual y sus RADs viven hoy fuera del repositorio. Deben entrar
como datos, no como código, por la misma razón que el escenario: **lo que se
duplique entre los datos y el prompt de un modelo se desincroniza. Siempre.**

Incluye la **agenda reservada** de cada rol —el apartado 11 del Manual—, que va
en sobre sellado y en papel: se juega, no se enuncia.

Depende de **A5** (nombres).

### B3 · Telemetría por turno

**Dónde:** no existe

Un evento canónico por turno, en JSONL. Sin eso, medir el ejercicio es
arqueología: cruzar a mano dos archivos que nunca se diseñaron para cruzarse.

Con la v2 hay dos métricas nuevas que solo existen si esto existe: **en qué turno
cada rol compartió por primera vez algo de su vista**, y **cuántas decisiones se
tomaron habiendo en la sala un dato que las desaconsejaba**.

> **Cuidado:** anotar el dato en el código no basta. Hay que comprobar que
> **llega al archivo**. En la simulación anterior, dos campos se perdían en la
> serialización sin que ninguna prueba lo detectara, porque las pruebas miraban
> el código y no el dato de salida.

### B4 · El hecho H1 del paquete detonante

**Dónde:** [`src/engine/loader.py`](src/engine/loader.py) ·
`proximidad_infra_critica` en el escenario

De los cuatro hechos que abren el turno 1, tres están: **H2** (las dos denuncias,
una cierta y una falsa), **H3** (el ultimátum gremial de 48 horas) y **H4** (la
región que cruza los dos días de oxígeno).

Falta **H1**: el incidente nocturno junto a una instalación de combustible, con
un herido grave de la fuerza pública. Los tres puntos contiguos a infraestructura
crítica ya están marcados en los datos; falta el evento que los active.

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

## C · Calibración

**Ningún coeficiente está medido.** Son convenciones declaradas, elegidas para
que ninguna estrategia pura gane. El criterio es **por comportamiento, no por
realismo**: no hay respuesta empírica a cuánta legitimidad cuesta un muerto, y no
la va a haber.

Medición actual con `--comparar`:

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
75 % y lo paga en cohesión y en caminos. `constituida` tiene la mejor mesa y
gasta legitimidad al operar. `solo_fuerza` se queda sin nada.

**Los dos problemas que estaban medidos ya no lo están** — y no eran de
coeficientes, eran piezas que faltaban. Ver «Lo que ya NO está pendiente».

Quedan **tres cosas que solo se ven con personas dentro**:

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

## D · Fuera del código

- **El protocolo de los sobres.** La agenda reservada en papel depende de que
  nadie pase la hoja. Con ocho personas y un facilitador es sostenible; no
  escalaría a treinta.
- **La declaración del turno 0** sobre el alcance del ejercicio: el motor no
  cuantifica culpa ni produce veredictos sobre hechos históricos.
- **Qué se dice sobre el azar.** *«El azar nunca decide si algo era buena idea;
  decide si esta vez salió mal, y la probabilidad se muestra antes.»*

---

## Lo que ya NO está pendiente

Anotado aquí para que nadie lo vuelva a levantar.

### De la propuesta original

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

### Del diagnóstico del motor anterior

Los siete problemas de [`docs/historial/mapa_de_palancas.md`](docs/historial/mapa_de_palancas.md):

| | Era | Cómo quedó |
|---|---|---|
| **D1** | La mezcla real de los puntos no cambiaba **nada** | Conectada por dos vías. `test_la_mezcla_real_cambia_el_resultado_de_la_corrida` falla si se desconecta |
| **D2** | El polo de negociación no podía negociar | Interior tiene 4 acciones, incluida la mesa nacional. Los dos mayores movimientos hacia abajo de la movilización ya se disparan |
| **D3** | El dueño del ESMAD no podía asignarlo | `DisponerESMAD` y `Escoltar` |
| **D4** | El frente logístico no podía mover carga | Escolta, caravana, gremios, y la prioridad de combustible como criterio permanente |
| **D5** | La cohesión era una rampa determinista | Solo se cobra de día, y ahora se puede reponer. Va de 0 a 74 según lo que la sala haga |
| **D6** | El paquete detonante no existía | H2, H3 y H4 en el motor; la jornada nacional en el calendario. Falta H1 (**B4**) |
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
| **—** | tres superficies contra la API antigua | Cuatro: `/tablero`, `/esfera`, `/vista/{rol}` ×8 y `/consola` |
| **—** | el mapa no existía | [`MapaEsquematico.jsx`](web_ui/src/components/MapaEsquematico.jsx) · esquema de líneas, con la forma del nodo diciendo cómo se abrió y un `?` en lo que nadie ha mirado |
| **—** | el reloj lo llevaba el moderador | Lo lleva el sistema, fase por fase |

---

*Última revisión: 2026-08-26 · 49 pruebas en verde · capas de lenguaje natural
activas con `gpt-5-nano`.*
