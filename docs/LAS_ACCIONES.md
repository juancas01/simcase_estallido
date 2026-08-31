# Las 37 acciones, una por una

Qué puede pedir cada uno de los siete, qué significa eso en la sala, y qué hace
exactamente el motor cuando se ejecuta.

**Este documento es el puente entre las dos lecturas.**
[`propuesta.md`](propuesta.md) dice qué puede hacer cada rol;
[`COMO_FUNCIONA.md`](COMO_FUNCIONA.md) dice cómo está construido cada subsistema.
Falta el cruce: *para esta acción concreta, qué cambia en el estado y cuánto*.
Eso es lo que hay aquí.

> **Todo lo que sigue está leído del código, no de la propuesta.** Cuando el
> número de este documento y el de otro no coincidan, gana
> [`actions.py`](../src/engine/actions.py) — y hay que corregir el documento.

---

## Cómo se lee cada ficha

Cada acción se llama de tres maneras, porque tiene tres lectores:

| | Qué es | Quién lo lee |
|---|---|---|
| `nombre` | cómo se llama en la sala, en verbo y en un renglón — «Autorizar al Ejército» | quien busca su fila en la guía y la dice en voz alta |
| `descripcion` | el nombre formal del acto — «Acto administrativo de asistencia militar» | el pliego, que es un registro |
| `en_claro` | qué hace y qué cambia, sin jerga | quien tiene que decidir si pedirlo |

Y desde la guía de acciones hay dos más, que viven en `GUIA`, al final de
[`actions.py`](../src/engine/actions.py), y salen en el tablero individual de su
titular:

| | Qué es | Regla |
|---|---|---|
| `requisitos_previos` | qué tiene que existir antes | **cualitativo siempre, nunca una cifra** — hay una prueba que lo vigila |
| `ejemplo_consola` | una frase que produce esta acción | **tiene que funcionar de verdad** — hay una prueba que las pasa todas por el intérprete |

> **`nombre` vive también en `GUIA`**, con los otros dos, y por la misma razón:
> treinta y siete rótulos escritos a dos mil líneas de distancia no se pueden
> redactar con el mismo rasero, y un rótulo que no es comparable con el de al
> lado no sirve de rótulo.

> **Las tres categorías se llaman en la sala Protocolo, Operación e
> Información.** En el código siguen siendo `constitutiva`, `operativa` e
> `informativa` —es vocabulario de diseño y ahí se queda—, y este documento usa
> las de la sala porque es el que se lee al lado de la pantalla. La traducción
> está en un solo sitio, [`etiquetas.jsx`](../web_ui/src/etiquetas.jsx).

Y aquí se añade la última, que no está en ningún sitio:

**En el motor** — qué valida, qué escribe en el estado, qué cobra en reservas,
qué evento de movilización registra. Con los números.

---

## El vocabulario común

Las fichas de abajo son tersas porque **los números compartidos viven en un solo
sitio**, y ese sitio es [`COMO_FUNCIONA.md`](COMO_FUNCIONA.md). Lo que hay que
tener a mano para leer una ficha:

| Qué | Dónde está, con sus números |
|---|---|
| **Las cuatro reservas** y sus seis umbrales duros | [§9 · La mesa](COMO_FUNCIONA.md#9-la-mesa-reservas-banderas-y-acuerdos) |
| **Los cinco mitigadores** y su factor | [§5 · La fuerza y el riesgo](COMO_FUNCIONA.md#5-la-fuerza-y-el-riesgo) |
| **La intensidad de movilización** y su tabla de eventos | [§4 · El adversario reflexivo](COMO_FUNCIONA.md#4-el-adversario-reflexivo) |
| **Las tres vías de abrir un punto** | [§6 · Las tres vías](COMO_FUNCIONA.md#6-las-tres-vías-de-abrir-un-camino) |
| **Los equipos de terreno** — un solo bolsillo de tres | [§8 · La información](COMO_FUNCIONA.md#8-la-información-verdad-vistas-y-denuncias) |

Y las cuatro cosas que hay que saber de memoria, porque aparecen en casi todas
las fichas:

- **Las reservas van de 0 a 100 y arriba siempre es mejor.** Legitimidad,
  credibilidad de la mesa, respaldo internacional y cohesión del PMU.
- **Las banderas son persistentes.** Se activan una vez y modifican todo lo
  posterior. **Ninguna es obligatoria y todas están tarifadas** — el diseño no
  fuerza a la sala a constituirse, le permite saltárselo y le cobra la
  diferencia.
- **Tres banderas son además mitigadores de riesgo**, y ahí está la decisión de
  diseño de fondo: el estándar de derechos no es un discurso, es un
  multiplicador.
- **Los equipos de terreno son tres por turno de decisión**, y verificar un
  punto y verificar una denuncia salen del mismo bolsillo. Mirar aquí es no
  mirar allá — y desde que los despliega el Ministerio de Defensa, **el que
  mira es parte**.

## En una mirada

**P** Protocolo · **O** Operación · **I** Información

**Las treinta y siete se piden por la consola, en lenguaje corriente.** Hubo una
columna que decía cuáles sí y cuáles no; se fue con las ocho que decían que no.

La primera columna de cada acción es **cómo se llama en la sala**; la segunda,
cómo se llama en el código. La guía entera en lenguaje corriente, con lo que
hace falta antes y cómo se pide, está en
[`GUIA_DE_ACCIONES.md`](GUIA_DE_ACCIONES.md).

| Rol | | Acción | | |
|---|---|---|---|---|
| **Presidente** | P | **Dejar todo por escrito** | `FijarRegistroEscrito` | registro escrito y responsable nominado |
|  | P | **Decir qué no se negocia** | `FijarLineasRojas` | el marco de lo negociable |
|  | O | **Autorizar al Ejército** | `FirmarAsistenciaMilitar` | la única firma que habilita tropa |
|  | O | **Reunir a los alcaldes** | `ConvocarAlcaldes` | corresponsabilidad territorial |
|  | I | **Ir al epicentro en persona** | `DesplazarseAlEpicentro` | ir en persona |
| **Interior** | P | **Poner un solo vocero** | `ExigirProtocoloVoceria` | una sola voz y plazo suspensivo |
|  | O | **Sentar al Comité del Paro** | `ConvocarMesaNacional` | **la única que produce un acuerdo verificable** |
|  | O | **Abrir una mesa en un punto** | `AbrirMesaLocal` | concertar un punto · **hay que instalarla cada jornada** |
|  | I | **Ofrecer algo a cambio** | `OfrecerContraprestacion` | la moneda no violenta |
|  | O | **Exigir un paso humanitario permanente** | `RequerirCorredoresHumanitarios` | paso permanente, exigible a las dos partes |
|  | O | **Poner custodia a una instalación** | `DeclararInfraestructuraCritica` | proteger, inmovilizando · **lo que se protege sale de lo que desbloquea** |
| **Alcalde** | P | **Exigir que le consulten la fuerza** | `CondicionarEmpleoFuerza` | concertación previa en su ciudad |
|  | O | **Sentarse con los voceros del punto** | `InstalarMesaConVoceros` | la mesa municipal · **cada jornada** |
|  | O | **Abrir paso a lo humanitario** | `EsquemaHumanitarioMunicipal` | **la única vía que no cuesta ninguna reserva** |
|  | I | **Publicar el conteo de la ciudad** | `PublicarParteMunicipal` | su propio conteo |
| **Defensa** | P | **Poner reglas a sus unidades** | `FijarReglasEmpleoSector` | **los tres mitigadores, y ya no se los exige nadie** |
|  | O | **Desbloquear un punto por la fuerza** | `OperarNodo` | **la que más mueve el tablero** |
|  | O | **Mover tropa a donde haga falta** | `RedesplegarMilitares` | tropa a infraestructura, o aire |
|  | I | **Mostrar quién financia los cierres** | `PresentarEvidenciaInteligencia` | quién financia los cierres |
|  | O | **Mandar equipos al terreno** | `DesplegarEquiposTerreno` | los tres del turno, y ya no son de un tercero |
| **Policía** | P | **Separar lo confirmado de lo estimado** | `ClasificarParteOperacional` | confirmado, estimado, en verificación |
|  | P | **Acordar una sola forma de verificar** | `AdoptarProtocoloVerificacion` | una sola cifra oficial · **lo que hace que valga la palabra del que verifica** |
|  | O | **Concentrar el ESMAD** | `DisponerESMAD` | concentrar fuerza |
|  | O | **Escoltar una caravana o misión médica** | `Escoltar` | **la condición material de todo lo logístico** |
|  | O | **Relevar a las unidades cansadas** | `SolicitarRelevo` | bajar la fatiga |
| **Transporte** | P | **Fijar el orden de los corredores** | `AdoptarCriterioPriorizacion` | en qué orden se atiende |
|  | P | **Decidir a qué va el combustible** | `FijarPrioridadCombustible` | **la segunda entrada del reloj** |
|  | O | **Organizar una caravana** | `OrganizarCaravana` | mover carga |
|  | O | **Hablar con los camioneros** | `NegociarConGremios` | que no se sumen |
|  | O | **Acordar ventanas de paso** | `AcordarPasosSeguros` | pasar sin abrir y sin gastar escolta |
|  | I | **Publicar el mapa de cierres** | `PublicarMapaCierres` | dónde está cerrado |
| **Agricultura** | P | **Poner los alimentos en la prioridad** | `FijarClasePrioridadAlimentaria` | reordena corredores, no añade ninguno |
|  | O | **Sentarse con el campo** | `InstalarMesaTecnicaAgropecuaria` | **la única mesa que sobrevive a la salida del Comité** |
|  | O | **Aliviar a los productores** | `ActivarInstrumentosSectoriales` | la única suya que no depende de nadie |
|  | I | **Publicar lo que se está perdiendo** | `PublicarBalancePerdida` | el costo del cierre, en lo que paga un hogar |
|  | O | **Concentrar el despacho de alimentos** | `AcordarAcopioYVentanas` | hace rendir la escolta que ya hay |
|  | I | **Decir cuántos días quedan** | `EntregarCalendarioAgotamiento` | el reloj, y lo que difundirlo hace |

---
---

---

# 01 · Presidente de la República

Cinco acciones, porque decide más. Dos de ellas constituyen la mesa y
casi no cuestan; una sola —la firma— puede reordenar el episodio entero.

### `FijarRegistroEscrito`
**Dejar todo por escrito** · Protocolo · [`actions.py:219`](../src/engine/actions.py#L219)

> *Deja por escrito cada decisión y quién responde por ella. Sin registro, al
> cierre nadie puede decir quién ordenó qué.*

**En la sala.** Parece burocracia y es la pieza que decide sobre quién cae el
costo de lo que salga mal. Sin ella, un incidente se reparte sobre los siete y
golpea la cohesión; con ella, cae sobre quien firmó. Es la acción que el
Ministro de Defensa quiere que exista antes de operar y la que, una vez existe,
lo deja expuesto.

**En el motor.**
- **Escribe** las banderas `registro_escrito` y `nodo_unico`.
- **Habilita** el campo `atribuible` de toda operación posterior: es
  `bool(responsable_nominado) and registro_escrito`. Sin las dos cosas a la vez,
  no hay atribución.
- **Con ella**, operar nombrando responsable cobra `decision_con_responsable`:
  **cohesión +2**.
- **Sin ella**, cada incidente cobra además `sin_registro_escrito`:
  **cohesión −8**.
- Es idempotente: repetirla devuelve «ya estaba vigente» y no cobra nada.

### `FijarLineasRojas`
**Decir qué no se negocia** · Protocolo · [`actions.py:243`](../src/engine/actions.py#L243)

> *Anuncia qué está y qué no está sobre la mesa. Fija el terreno de lo negociable
> antes de que lo fije otro.*

**En la sala.** Ordena la posición del Gobierno para que lo que traiga Interior
no se renegocie delante de todos. Y tiene un filo: fijarlas demasiado estrechas
cierra por anticipado el espacio de su propio Ministro del Interior.

**El único parámetro: `margen`.** Es **un número entre 0 y 1**, y no un
porcentaje: **0 = nada es negociable**, **1 = todo lo es**. Por defecto vale
**0,5**. Es cuánto espacio se le deja al Ministro del Interior para pactar.

**En el motor.**
- **Escribe** la bandera `lineas_rojas_fijadas`.
- **`margen` < 0,25** → **credibilidad −8**. Cualquier acuerdo posterior será una
  capitulación pública.
- **Y eso es todo lo que hace el número.** El motor lo lee como un interruptor,
  no como un dial: **0,25 y 1,0 se comportan exactamente igual**. Lo demás
  —habilitar la contraprestación, encarecer los pasos seguros— depende de la
  bandera, que se activa con cualquier margen.
- **Habilita** `OfrecerContraprestacion`, que sin esta bandera se valida como
  *parcial* con el aviso de que lo ofrecido se renegociará.
- **Efecto cruzado que sorprende:** con la bandera puesta, los pasos seguros de
  Transporte pasan a costar **cohesión −4**, porque se leen como negociación
  paralela.

> **Cuidado con esta acción: hoy el número no se comprueba.** Ver el punto 3 de
> [«lo que este recuento deja a la vista»](#3--el-margen-de-las-líneas-rojas-no-se-comprueba).

### `FirmarAsistenciaMilitar`
**Autorizar al Ejército** · Operación · [`actions.py:272`](../src/engine/actions.py#L272)

> *Autoriza que el Ejército apoye a la Policía. Da más fuerza disponible, y
> militares frente a multitudes suben la tensión en la calle.*

**En la sala.** Es la única llave que abre el empleo de tropa, y el ejercicio la
pone donde debe estar: en el Presidente, no en Defensa. La decisión no es
firmar o no firmar — es **firmar delimitando o firmar sin delimitar**, y la
diferencia entre las dos es casi tres veces el costo.

**En el motor.**
- **Escribe** siempre `asistencia_militar_firmada`. **Habilita** `OperarNodo` con
  `tipo_unidad="militar"`, que sin esta bandera no valida.
- **Siempre**: credibilidad **−12**.

| | Delimitada | Sin delimitar |
|---|---|---|
| Reservas | respaldo **−8**, legitimidad **−5** | respaldo **−22**, legitimidad **−15** |
| Banderas | `asistencia_militar_delimitada` **y `reglas_escritas`** —el mitigador ×0,70 gratis | ninguna |
| Fuerza | **libera hasta 6 unidades** de custodia a reserva | nada |
| Movilización | — | `militares_en_multitudes` **+8** |
| Encuadre | — | pasa a **represión** |

> Delimitar significa territorio, plazo, reglas escritas y criterio de
> terminación. Cuesta la cuarta parte en respaldo internacional, activa un
> mitigador y devuelve seis unidades. **No hay lectura en la que salga peor.**

### `ConvocarAlcaldes`
**Reunir a los alcaldes** · Operación · [`actions.py:321`](../src/engine/actions.py#L321)

> *Reúne a los alcaldes de las ciudades más golpeadas. Sirve para llegar a la
> mesa con una sola posición en vez de varias.*

**En la sala.** Llegar a la mesa nacional con los territorios alineados, o llegar
con un mandatario local dispuesto a hacer público su desacuerdo. El precio de
alinearlos es comprometer prioridad de fuerza que Defensa quería libre.

**En el motor.**
- **Escribe** siempre `protocolo_voceria` — la misma bandera que la constitutiva
  de Interior, con lo cual **también retira el peaje de cohesión −5 por turno**.
- **`concede_prioridad=True`** → escribe además `concertacion_previa_cali`;
  cohesión **+4**, legitimidad **+2**.
- **`False`** → cohesión **+2** y devuelve `agravio_territorial: True`.

> Ojo con la segunda bandera: `concertacion_previa_cali` es la misma que activa
> la constitutiva del Alcalde, y a partir de ahí **operar en el epicentro sin
> concertar cuesta legitimidad −8 y cohesión −4**. El Presidente puede activarle
> a Defensa ese peaje sin que Defensa esté en la conversación.

### `DesplazarseAlEpicentro`
**Ir al epicentro en persona** · Información · [`actions.py:351`](../src/engine/actions.py#L351)

> *Viaja en persona a la ciudad más afectada. Es un gesto público de que el
> Gobierno da la cara.*

**En la sala.** Ir es barato de decir y caro de hacer: consume escolta que hoy no
sobra. Y lo que decide su signo no es ir, sino **a qué se acompaña al llegar**.

**En el motor.**
- **Valida** que haya **≥2 escuadrones ESMAD en reserva**. Si no los hay, se
  rechaza y devuelve *habilitada por: Director de Policía*.
- **Consume 2 escuadrones**: pasan a `escolta`, ubicación `presidencia`.

| `acompana` | Reservas | Además |
|---|---|---|
| `mesa` | credibilidad **+6**, legitimidad **+3** | respalda el canal de diálogo |
| `operacion` | legitimidad **−2**, cohesión **+3** | encuadre pasa a **represión**. El sector deja de cargar solo la decisión |
| `ninguna` | legitimidad **+1** | hace verificable la prioridad sin comprometerse |

---

---

# 02 · Ministro del Interior

Seis, y dos son heredadas. **Es el rol que más creció al salir la
Defensoría del Pueblo y el Ministerio de Minas**: se quedó con el paso
humanitario permanente y con el registro de infraestructura, que es la
única aritmética que hace escasa la fuerza por una razón que no es operar.

### `ExigirProtocoloVoceria`
**Poner un solo vocero** · Protocolo · [`actions.py:399`](../src/engine/actions.py#L399)

> *Establece que una sola persona habla por el Gobierno. Evita que dos carteras
> digan cosas distintas el mismo día.*

**En la sala.** Ninguna operación vuelve a sorprender a la mesa — y cuesta un
turno de demora en todas. Es el intercambio explícito entre coordinación y
velocidad, y quien paga la demora es Defensa.

**En el motor.**
- **Escribe** `protocolo_voceria` **y** `plazo_suspensivo`.
- `protocolo_voceria` **retira un peaje que se cobra cada turno de día**:
  `sin_protocolo_voceria`, **cohesión −5**.
- `plazo_suspensivo` hace que `OperarNodo` sin concertar valide como **parcial**
  con el aviso «la operación se difiere un turno».
- Y **retira el otro peaje**: sin `plazo_suspensivo`, cada operación cobra
  `operacion_no_informada`, **cohesión −8**.

> Sumando los dos, en un turno con una operación esta acción ahorra **13 puntos
> de cohesión** —y 8 más por cada operación adicional—. Es la constitutiva con
> mejor relación costo-beneficio después del estándar de empleo, y la que más
> ruido causa en la sala, porque su costo lo paga otro.

### `ConvocarMesaNacional`
**Sentar al Comité del Paro** · Operación · [`actions.py:422`](../src/engine/actions.py#L422)

> *Sienta al Gobierno con el Comité del Paro. Es la vía más rápida para bajar la
> tensión, y operar por la fuerza ese mismo día es lo que más caro le sale a la
> mesa.*

**En la sala.** **Es la única acción del ejercicio que puede producir un acuerdo
verificable**, que es el movimiento que más desinfla la movilización de todo el
diseño. Sin ella el caso queda con un solo polo activo, la fuerza.

**En el motor.**
- **Valida** que `comite_disponible` sea cierto. Si la credibilidad bajó de 30,
  el Comité suspendió y esta acción **no se puede ejecutar** — hasta que la
  credibilidad vuelva a subir de 30, momento en el que el Comité se sienta otra
  vez y se registra el evento `comite_vuelve`. **Salvo que en algún momento
  haya bajado de 15**: eso es retirada definitiva y no se deshace.
- **Crea un `Acuerdo`** sobre hasta **3 puntos** —los cerrados con mayor
  `control_voceria`, si no se nombran—, con **`turno_limite` = turno actual + 2**.
- Por cada punto: `caudal = max(caudal, min(0.9, 0.35 × control_voceria / 0.6))`,
  modo de apertura **concertación**, evento de apertura.
- **Movilización** `apertura_concertada`: **−4**. **Reservas**: legitimidad **+2**.
  **Encuadre** pasa a *negociación*.

**Y entonces empieza lo que importa**, que se resuelve dos turnos después en
`aperture.revisar_acuerdos()`:

| Al llegar el turno límite | Reservas | Movilización | Territorio |
|---|---|---|---|
| **Se cumplió** —nadie operó sobre lo pactado | legitimidad **+5**, credibilidad **+8**, cohesión **+3** | `acuerdo_verificable` **−8** · *el mayor movimiento a la baja del diseño* | los puntos siguen abiertos |
| **Se rompió** —se operó sobre un punto pactado | credibilidad **−10**, legitimidad **−3** | `acuerdo_incumplido` **+6** | **los puntos pactados vuelven a cerrarse** |

> La ruptura no la decide Interior: la decide Defensa operando. Basta una
> operación sobre uno de los tres puntos para que `motivo_ruptura` quede escrito,
> y dos turnos después se cobra entero.

### `AbrirMesaLocal`
**Abrir una mesa en un punto** · Operación · [`actions.py:495`](../src/engine/actions.py#L495)

> *Negocia un punto concreto para que lo desbloqueen sus propios voceros. Tarda
> dos turnos, y lo que se abre así aguanta mientras se cumpla lo pactado.*

**En la sala.** La vía pactada punto por punto. Lenta, sostenible, y con dos
trampas que la sala no puede ver sin haber gastado un equipo de terreno ahí.

**En el motor.**
- **Valida**: que el punto exista y no esté abierto; que el Comité esté
  disponible si el punto tiene `control_voceria > 0,5`; y **en la jurisdicción
  del epicentro exige `con_alcaldia`** — si no, se rechaza señalando al Alcalde.
- **Tarda 2 turnos.** El primero devuelve «la concertación necesita otro turno».
- Al cumplirse: **`caudal = 0,90 × control_voceria`**.
- **Reservas**: `apertura_concertada`, legitimidad **+2**. **Movilización** −4.

**Las dos trampas, y son el corazón pedagógico del caso:**

1. **La visible.** Pactar con quien controla el 40 % del punto abre el 36 %. Se
   anuncia como éxito y se desmiente solo. El motor avisa por debajo de 0,6:
   *«la vocería solo controla el X %; el acuerdo no cubre el resto»*.
2. **La invisible.** Con probabilidad **`estructura_organizada × 1,5`** el
   acuerdo es **frágil**: quien firmó no manda sobre quien sostiene el cierre.
   Entonces el caudal se multiplica por **0,4**, se cobra `acuerdo_incumplido`
   —credibilidad **−10**, legitimidad **−3**— y la movilización sube **+6**.

> Esta es una de las dos vías por las que la mezcla real de un punto tiene
> consecuencia. La otra está en `OperarNodo`. **Ninguna de las dos deja ver la
> verdad**: solo se paga.

### `OfrecerContraprestacion`
**Ofrecer algo a cambio** · Información · [`actions.py:595`](../src/engine/actions.py#L595)

> *Ofrece algo concreto a cambio de levantar los cierres. Funciona donde hay con
> quién negociar; no donde nadie manda.*

**En la sala.** La moneda no violenta: bajar la presión en la calle sin gastar un
escuadrón. Y es una apuesta — el Congreso responde seis de cada diez veces.

**En el motor.**
- **Valida como parcial** si no hay `lineas_rojas_fijadas`, con el aviso de que
  lo ofrecido se renegociará. **Se puede ofrecer igual.**
- Tirada contra `P_CONGRESO_RESPONDE = 0,6`.

| | Reservas | Movilización |
|---|---|---|
| **Tramitada** (60 %) | credibilidad **+6**, legitimidad **+4** | `contraprestacion_tramitada` **−6** |
| **No responde** (40 %) | credibilidad **−8**, legitimidad **−4** | — |

> El incumplimiento se imputa al Gobierno entero y refuerza a quienes sostienen
> que solo la fuerza produce efectos. Es la acción con mayor varianza del
> repertorio.

---

### `RequerirCorredoresHumanitarios`
**Exigir un paso humanitario permanente** · Operación · [`actions.py:632`](../src/engine/actions.py#L632)

> *Exige que haya un paso permanente para lo humanitario. Negarlo es lo que más
> caro cuesta de cara al exterior.*

**En la sala.** Exigible **tanto al Estado como a quienes sostienen los cierres**.
Sin oxígeno modelado sería una declaración de principios; con él, negarlo tiene
contador de víctimas.

**En el motor.**
- Elige el corredor humanitario **de menor caudal efectivo**, si no se nombra
  otro.
- **Baja el apoyo al cierre −0,06** en todos sus puntos: la misión médica se
  vuelve línea roja también para quienes bloquean.
- **Respaldo internacional +5.**

### `DeclararInfraestructuraCritica`
**Poner custodia a una instalación** · Operación · [`actions.py:680`](../src/engine/actions.py#L680)

> *Declara una instalación como crítica para que la custodien. Queda protegida, e
> inmoviliza fuerza que hace falta en otra parte.*

**En la sala.** **Es la aritmética que enfrenta al Interior con Defensa**: la
protección permanente resta exactamente de la capacidad de desbloqueo.

**En el motor.**
- **Valida como parcial** si no alcanza el cupo —**2 unidades por instalación**—
  con el aviso de que se protegerá lo que se pueda y señalando a Defensa.
- Manda a `custodia` tantos escuadrones ESMAD disponibles como instalaciones.
- Devuelve cuántas unidades quedan **inmovilizadas** y qué puntos contiguos a
  infraestructura crítica dejan de poder producir el hecho irreversible: *es
  exactamente lo que se está comprando*.

---

# 03 · Alcalde de la ciudad epicentro

Cuatro, y es el único que no heredó nada. No es un descuido: su mandato
acaba en el borde de su ciudad, y las carteras que se fueron eran
nacionales.

### `CondicionarEmpleoFuerza`
**Exigir que le consulten la fuerza** · Protocolo · [`actions.py:825`](../src/engine/actions.py#L825)

> *Exige que cualquier operación en su ciudad se acuerde antes con la Alcaldía.
> Baja el riesgo de que salga mal, y le quita velocidad a Defensa.*

**En la sala.** Es la acción que convierte al Alcalde en alguien a quien hay que
llamar. No bloquea nada: pone precio.

**En el motor.**
- **Escribe** `concertacion_previa_cali`.
- A partir de ahí, `OperarNodo` en el epicentro **sin** `concertado_con_alcaldia`:
  valida como **parcial** y cobra **legitimidad −8, cohesión −4**.
- Y **con** concertación, activa el mitigador `concertado_con_alcaldia`: **×0,80**
  sobre la probabilidad de incidente.

> Las dos mitades importan. La sanción hace que llamarlo tenga sentido; el
> mitigador hace que llamarlo sirva.

### `InstalarMesaConVoceros`
**Sentarse con los voceros del punto** · Operación · [`actions.py:848`](../src/engine/actions.py#L848)

> *Sienta a hablar a los voceros de un punto de su ciudad. Es la vía pactada,
> hecha desde el municipio.*

**En la sala.** La misma vía que la mesa local de Interior, hecha desde el
municipio y sin pedirle permiso a nadie. La diferencia está en la jurisdicción,
y es exactamente inversa.

**En el motor.**
- **Valida** que el punto esté **en la región epicentro**. Fuera de ella se
  rechaza y devuelve *habilitada por: Ministro del Interior*.
- La mecánica es **idéntica** a `AbrirMesaLocal`: dos turnos, caudal
  `0,90 × control_voceria`, fragilidad por estructura organizada, legitimidad +2,
  movilización −4.

> Interior puede concertar en todo el país pero en el epicentro necesita al
> Alcalde; el Alcalde solo puede en el epicentro y ahí no necesita a nadie. Es la
> misma frontera vista desde los dos lados.

### `EsquemaHumanitarioMunicipal`
**Abrir paso a lo humanitario** · Operación · [`actions.py:912`](../src/engine/actions.py#L912)

> *Monta un paso para ambulancias, oxígeno y alimentos en su jurisdicción. No
> abre el punto: abre una ventana.*

**En la sala.** **La única vía de apertura que no consume ninguna reserva.** Baja
el incentivo material del cierre sin alimentar la movilización. Es lenta y es
gratis — y el Gobierno Nacional puede leerla como sostenimiento del bloqueo.

**En el motor.**
- **Valida** que sea su jurisdicción.
- **Erosiona el apoyo local** en **todos** los puntos de la región:
  **−0,12** (`DESGASTE_POR_ESQUEMA_HUMANITARIO`).
- **No toca ninguna reserva. No registra ningún evento de movilización.**
- **Habilita la tercera vía de apertura:** cuando `apoyo_local` cae por debajo de
  **0,25** y se sostiene **3 turnos**, cada turno hay un **20 %** de que el punto
  **se levante solo**, con caudal 0,50–0,80 — y el desgaste **no reabre**.

> Dos aplicaciones bajan el apoyo 0,24. Es la acción más lenta del repertorio y
> la única cuyo resultado no aparece el turno en que se ordena.

### `PublicarParteMunicipal`
**Publicar el conteo de la ciudad** · Información · [`actions.py:948`](../src/engine/actions.py#L948)

> *Publica su propio conteo de lo que pasó en la ciudad. Si contradice la cifra
> nacional, uno de los dos queda desmentido.*

**En la sala.** Mejora la información del sistema, y disputar la cifra nacional
sin protocolo común profundiza la guerra de números. El mismo acto, con y sin
protocolo, cambia de signo.

**En el motor.**
- **Marca verificados** todos los puntos de su región que nadie hubiera mirado,
  con fuente `parte_municipal` — cuyo sesgo es **−0,22 sobre la estructura
  organizada**: *la subestima*.

| | Reservas |
|---|---|
| Disputa la cifra **sin** `protocolo_verificacion` | `cifra_desmentida`: **legitimidad −4** y evento público |
| Dentro del protocolo, o sin disputar | legitimidad **+2**, respaldo **+3** |

> El signo lo decide una bandera que el Alcalde no controla: la pone el Director
> General de la Policía.

---

---

# 04 · Ministro de Defensa

Cinco. La quinta son **los equipos de verificación en terreno**, que eran
las duplas del Delegado de la Defensoría del Pueblo. Es el cambio que más
pesa de esta versión del ejercicio: el que opera es ahora el que va a
constatar qué pasó.

### `FijarReglasEmpleoSector`
**Poner reglas a sus unidades** · Protocolo · [`actions.py:991`](../src/engine/actions.py#L991)

> *Ordena que sus unidades vayan identificadas, con reglas escritas y grabando.
> Baja mucho la probabilidad de que una operación termine mal.*

**En la sala.** **Esta acción absorbió la del Delegado de la Defensoría del
Pueblo**, que exigía lo mismo desde fuera. Los tres mitigadores son ahora una
sola decisión y la toma quien tiene que cumplirlos: ya no es «un tercero pide
más de lo que el sector concede», es **«el sector se autolimita, o no lo hace
nadie»**. Y atarse las manos delante de la mesa tiene precio en cohesión, que es
lo que antes no costaba porque lo pedía otro.

**En el motor.**
- **Escribe** `reglas_escritas` **(×0,70)** y `registro_av` **(×0,80)**. Juntos:
  **×0,56** sobre la probabilidad de incidente.
- `registro_av` además **baja la probabilidad de que la imagen circule del 55 %
  al 25 %** cuando hay incidente.

### `OperarNodo`
**Desbloquear un punto por la fuerza** · Operación · [`actions.py:1032`](../src/engine/actions.py#L1032)

> *Manda a la fuerza pública a abrir un punto. Es lo más rápido que existe y lo
> más caro: el punto suele volver a cerrarse esa misma noche.*

**En la sala.** La acción central del caso. Cada operación con víctimas consume
la legitimidad de la que depende la mesa de Interior, que no la ordenó.

**Lo que valida.**

| | |
|---|---|
| El punto existe y **no está abierto** | si no, se rechaza |
| `tipo_unidad` ∈ `esmad`, `policia`, `militar` | un valor desconocido se rechaza con motivo legible |
| ESMAD → tiene que haber **ESMAD disponible** | *habilitada por: Director de Policía* |
| Militar → **`asistencia_militar_firmada`** | *habilitada por: Presidente* |
| Epicentro con `concertacion_previa_cali` y sin concertar | **parcial**: se puede, cuesta más |
| `plazo_suspensivo` vigente y sin concertar | **parcial**: se difiere un turno |

**Cómo se calcula el riesgo** — en [`force.py`](../src/engine/force.py), y se le
muestra a la sala **antes** de decidir:

```
riesgo = base[unidad] × (1 + fatiga) × (1 + dureza) × (1 + masa/300)
         × 1,6 si es de noche
         × el producto de los mitigadores activos

P = 1 − e^(−riesgo)        con techo en 0,98
```

| Unidad | Base | Víctimas esperadas si hay incidente |
|---|---|---|
| `esmad` | **0,08** — entrenado para control de multitudes | 0,4 |
| `policia` | **0,22** — no es su función | 0,9 |
| `militar` | **0,45** — tropa de combate frente a civiles | **2,1** |

> **`composicion_real` no entra en el riesgo.** La mezcla de un punto no cambia
> la probabilidad de que algo salga mal: cambia **lo que cuesta** cuando sale
> mal. Si entrara aquí, la banda de riesgo filtraría la verdad que nadie debe
> ver.

**Qué hace al ejecutarse.**
- **El acompañamiento ya no existe.** Era el sexto mitigador y descontaba porque
  miraba una dupla de la Defensoría del Pueblo; con los equipos de terreno en
  manos del mismo ministerio que ordena la operación, acompañarse a sí mismo no
  cambia la probabilidad de que una imagen circule.
- **El éxito de la apertura es independiente del incidente**:
  `P = max(0,15, 1 − dureza × 0,6)`. Se puede abrir el punto y producir una
  catástrofe reputacional a la vez.
- Si abre: caudal **0,70–1,00**, modo `fuerza` — y **de noche vuelve a cerrarse**
  con `P = intensidad/100 × (0,4 + apoyo_local)`, endureciendo el punto **+0,08**.
- **Registra siempre el hecho público de que se operó ahí**, con éxito o sin él.
  Lo que nunca sale es dónde está la fuerza ahora: eso es de la Policía.
- **Si el punto estaba pactado, marca el acuerdo para ruptura.**

**Lo que cobra.**

| Condición | Reservas | Movilización |
|---|---|---|
| Incidente con víctimas | legitimidad **−9**, respaldo **−7** · **× multiplicador civil** | `incidente_mortal` **+20** |
| La imagen circula | legitimidad **−6**, respaldo **−5** · **× multiplicador civil** | `imagen_viral` **+8** |
| Incidente **no atribuible** | cohesión **−8** | — |
| Unidad militar | — | `militares_en_multitudes` **+8** |
| Epicentro sin concertar, con la bandera | legitimidad **−8**, cohesión **−4** | — |
| **Sin** `plazo_suspensivo` | cohesión **−8** | — |
| Comité disponible **y de día** | **credibilidad −12** | — |
| Con responsable **y** registro escrito | cohesión **+2** | — |

**El multiplicador civil**, que es la primera de las dos vías por las que la
mezcla real tiene consecuencia:

```
multiplicador = 1 + max(0, protesta_legítima − 0,50) × 2,0
```

Un punto que es **90 % protesta legítima** cuesta **1,8 veces** lo que uno que es
mitad y mitad. **La sala no puede saberlo antes de operar.** Puede averiguarlo
gastando un equipo — y esa es exactamente la decisión que el ejercicio quiere
producir.

> **Cuidado con el nombre del parámetro: `operacion_dia_de_mesa` no significa
> «el día que hubo sesión».** La condición real es
> `comite_disponible and franja == "dia"`, así que **toda operación de un turno
> de decisión cuesta −12 mientras el Comité siga en la mesa**, haya habido sesión
> o no. Y como los cinco turnos de decisión son de día, son **todas**.
>
> Son 12 puntos, empatados con la firma de asistencia militar como el mayor
> golpe individual a esa reserva. Se empieza con 45 y el Comité suspende por
> debajo de 30: **dos operaciones cualesquiera bastan para cerrar el polo de
> negociación** —45 → 33 → 21— y hoy lo cierran **para siempre**. Ver el punto 4
> de [«lo que este recuento deja a la vista»](#4--el-comité-del-paro-no-volvía-nunca--corregido).
>
> Y hay un efecto perverso, medido: **una vez el Comité se va, operar deja de
> costar esos 12 puntos**, porque la condición exige que esté. El motor abarata
> la acción justo después de que ella haya destruido lo que la encarecía.

### `RedesplegarMilitares`
**Mover tropa a donde haga falta** · Operación · [`actions.py:1197`](../src/engine/actions.py#L1197)

> *Mueve tropa a proteger instalaciones críticas. Libera policía para otras
> tareas e inmoviliza esas unidades donde las puso.*

**En la sala.** Cambiar tropa por policía disponible. Y abrir un frente rural
desatendido que el motor contabiliza.

**En el motor.**
- **Valida** que `modo` sea `infraestructura` o `proyeccion_aerea`. Un modo
  desconocido **se rechaza**; antes caía por el `else` y hacía proyección aérea.

| Modo | Qué hace |
|---|---|
| `infraestructura` | N militares de reserva → custodia; **libera el mismo número de escuadrones ESMAD** de custodia a reserva; `frentes_rurales_descubiertos` **+N** |
| `proyeccion_aerea` | **concentra 6 escuadrones** en horas —con el mismo precio que `DisponerESMAD`—, registra `militares_en_multitudes` **+8** y suma **+N** frentes descubiertos |

### `PresentarEvidenciaInteligencia`
**Mostrar quién financia los cierres** · Información · [`actions.py:1264`](../src/engine/actions.py#L1264)

> *Presenta lo que Inteligencia tiene sobre quién financia los cierres. Vale
> según lo sólido que sea; si no se sostiene, se vuelve en contra.*

**En la sala.** Justifica respuestas diferenciadas. Y si un solo caso no aguanta
ante los jueces, arrastra la credibilidad de todos los demás.

**En el motor.**
- **Marca verificados** hasta 3 puntos —los de mayor estructura organizada real,
  si no se nombran— con fuente `inteligencia_defensa`, cuyo sesgo es **+0,28**:
  *sobreestima la estructura organizada*, que es el sesgo más grande de las
  cuatro fuentes.

| | Reservas | Además |
|---|---|---|
| **Declara la solidez** | cohesión **+3**, credibilidad **+2** | debilita su posición hoy, protege la credibilidad del sector |
| **No la declara** | legitimidad **−3**, credibilidad **−5** | encuadre pasa a **represión** |

---

### `DesplegarEquiposTerreno`
**Mandar a sus verificadores** · Operación · [`actions.py:1314`](../src/engine/actions.py#L1314)

> *Manda equipos suyos a constatar en el sitio qué pasa en un punto o si una
> denuncia es cierta. Solo tiene tres por turno, y son los mismos para las dos
> cosas.*

**En la sala.** Un **equipo de terreno** es una pareja de funcionarios que va al
sitio a constatar qué pasa. Van de a dos porque protege a quien verifica y porque
dos testigos producen una constancia difícil de desestimar. **Hay tres, y cada
uno hace una sola cosa por turno.**

**ERA LA VEEDURÍA DE UN TERCERO Y ES INTELIGENCIA DE UNA PARTE.** Cuando esto lo
hacía el Delegado de la Defensoría del Pueblo, su lectura era la única del
ejercicio sin sesgo apreciable y la única que producía el grado `confirmado`.
Ahora lo hace el mismo ministerio que ordena las operaciones, y eso cambia tres
cosas a la vez.

**En el motor.**
- **Valida**: **queda al menos un equipo**; y **se dijo qué verificar** — sin
  punto ni denuncia se rechaza, porque antes esto se ejecutaba y se reportaba
  como correcto.
- **Verificar un punto** gasta un equipo, lo marca como mirado —hecho público— y
  produce una estimación con fuente `equipo_terreno`, **sesgo +0,12**. Ir al
  terreno corrige más de la mitad del `+0,28` que tiene la inteligencia desde el
  escritorio, y sigue tirando hacia arriba: hacia el lado que justifica escalar.
- **Ninguna fuente concede ya el grado `confirmado`.** Un grado que solo podía
  otorgar quien no era parte es una promesa que este ejercicio ya no puede
  cumplir, así que se retiró. Todo se lee `estimado`.
- Lo que no alcanza sale en `no_alcanzados`, y eso **importa tanto como lo
  verificado**: es lo que hay que informar a la mesa como «esto no lo he podido
  mirar».

**Verificar una denuncia** también gasta un equipo — y **lo que vale el resultado
depende de si hay protocolo común de verificación adoptado**, porque las
denuncias son sobre conducta de la fuerza y quien las resuelve es la fuerza:

| | Con `protocolo_verificacion` | Sin él |
|---|---|---|
| Era **cierta** | respaldo **−6**, legitimidad **−3** · el costo llega con el Estado enterado en vez de sorprendido | respaldo **−11**, legitimidad **−7** · el hecho es cierto y además parece administrado |
| Era **falsa** | legitimidad **+3**, credibilidad **+2** · `denuncia_desmentida` **−3** | legitimidad **+1** y nada más · se lee como una parte absolviéndose |

> **El protocolo es la sustitución funcional del tercero que se fue.** No es una
> formalidad: es una regla que la sala pacta ANTES de saber qué va a decir, y por
> eso su palabra cuenta después. La adopta el Director General de la Policía.

> **Nunca hay una sola denuncia sin verificar: siempre al menos dos, con
> veracidad distinta y sin ninguna señal que las distinga.** Y no esperan: a los
> **2 turnos estallan** solas. Declararlas públicamente *en verificación* no
> cuesta dupla y **abarata el golpe a la mitad** — el Estado no afirmó lo que no
> sabía.

---

# 05 · Director General de la Policía Nacional

Cinco, y la que llega es el **protocolo único de verificación**. No es un
relleno: desde que quien verifica es parte, ese protocolo es lo único que
hace que su palabra cuente.

### `ClasificarParteOperacional`
**Separar lo confirmado de lo estimado** · Protocolo · [`actions.py:1410`](../src/engine/actions.py#L1410)

> *Separa en su parte lo confirmado, lo estimado y lo que está en verificación.
> Evita que una estimación se lea en la mesa como un hecho.*

**En la sala.** En el papel parece transparencia sin recompensa. Lo que hace es
que cada desmentido posterior deje de costar.

**En el motor.**
- **Escribe** `protocolo_verificacion`.
- Con la bandera puesta, `costo_de_no_clasificar()` **no cobra nada**. Sin ella,
  cobra **legitimidad −4** cada vez que se dispute una cifra — lo que ocurre al
  publicar el parte municipal disputando, y al anunciar un corredor abierto que
  no lo está.

### `AdoptarProtocoloVerificacion`
**Acordar una sola forma de verificar** · Protocolo · [`actions.py:1438`](../src/engine/actions.py#L1438)

> *Establece una sola manera de verificar cifras y denuncias, igual para todos.
> Evita que cada cartera traiga su propio número.*

**En el motor.** Escribe `protocolo_verificacion`, **la misma bandera** que la
constitutiva del Director de Policía y con el mismo efecto: retira el
**legitimidad −4** de cada cifra desmentida. Que dos roles distintos puedan
ponerla es deliberado — el Gobierno acepta que un tercero fije la cifra, o la fija
él.

### `DisponerESMAD`
**Concentrar el ESMAD** · Operación · [`actions.py:1459`](../src/engine/actions.py#L1459)

> *Concentra escuadrones en los puntos que decida. Gana fuerza donde la lleva y
> deja descubierto lo que abandona.*

**En la sala.** Es la acción que su dueño no tenía hasta la v2. **El precio tiene
nombre de ciudad**: los puntos que se sueltan se consolidan, y el mandatario
local que los pierde lo lee como abandono territorial.

**En el motor.**
- Trae escuadrones de `contencion` a `reserva`, con tope de **8 por turno**.
- **Consolida los 2 puntos cerrados más blandos**: dureza **+0,06** y un día más
  sostenidos.
- **Cohesión −3.**
- Si no queda nada en contención estática, devuelve **fallo**: la fuerza ya está
  toda comprometida.

### `Escoltar`
**Escoltar una caravana o misión médica** · Operación · [`actions.py:1503`](../src/engine/actions.py#L1503)

> *Escolta una caravana, un carrotanque o una misión médica. Hace llegar el
> suministro sin abrir el punto, y ocupa escuadrones todo el turno.*

**En la sala.** **Sin escolta no hay caravana ni carrotanque**, por más que
Transporte priorice y asigne. Es el cuello de botella de todo el frente
logístico, y está en manos de un rol que no responde por él.

**En el motor.**
- **Valida**: el corredor existe; hay **≥2 escuadrones sin comprometer**; y la
  clase de carga tiene que estar entre las del corredor. Si el corredor está
  bloqueado valida como **parcial**: *la escolta puede salir, pero la carga no
  pasará*.
- **Inmoviliza 2 escuadrones** durante el turno.
- Si el caudal efectivo es **≤ 0,05**, la caravana no pasa y los escuadrones
  quedan gastados igual.
- **Riesgo de ataque**: `P = min(0,55, 0,12 × (1 + intensidad/100))` — sube donde
  la movilización está más caliente.

| | Reservas | Movilización | Abastecimiento |
|---|---|---|---|
| **Lograda** | legitimidad **+3** | — | **repone `1,1 × caudal` días** de autonomía en las regiones del corredor |
| **Atacada** | legitimidad **−6**, respaldo **−4** | `escolta_atacada` **+7** | nada, y el corredor humanitario se vuelve escenario de confrontación |

### `SolicitarRelevo`
**Relevar a las unidades cansadas** · Operación · [`actions.py:1586`](../src/engine/actions.py#L1586)

> *Releva a las unidades más agotadas. Un escuadrón cansado es el principal
> factor de que una operación salga mal.*

**En la sala.** Menos probabilidad de catástrofe reputacional a cambio de menos
cobertura simultánea. Es el intercambio más limpio del repertorio.

**En el motor.**
- Manda a `relevo` las **N unidades más fatigadas** de contención u operación.
- En relevo recuperan **0,30 de fatiga por turno**, y al bajar de 0,05 vuelven
  solas a reserva.
- La fatiga entra en el riesgo como **×(1 + fatiga)** y además activa el
  mitigador **`unidades_descansadas` ×0,75** cuando la media baja de **0,30**.

> Se empieza con fatiga media **0,55** y 34 de 40 escuadrones desplegados. Llegar
> a 0,30 exige varios turnos de relevo seguidos, y cada uno de esos turnos es un
> turno con menos cobertura.

---

---

# 06 · Ministro de Transporte

Seis. Hereda del Ministerio de Minas el reparto del combustible y las
ventanas de paso, que son las dos cosas que ya negociaba con los mismos
transportadores.

### `AdoptarCriterioPriorizacion`
**Fijar el orden de los corredores** · Protocolo · [`actions.py:1621`](../src/engine/actions.py#L1621)

> *Fija en qué orden se atienden los corredores y por qué. Sin criterio, cada
> turno se discute lo mismo desde cero.*

**En la sala.** Convierte la disputa política de asignación en una secuencia
defendible — y expone a un ministro concreto como el que decidió qué ciudad se
aplaza.

**En el motor.**
- **Escribe** `criterio_priorizacion`, que **retira un peaje que se cobra cada
  turno de día**: `sin_criterio_priorizacion`, **cohesión −3**.
- Devuelve el orden calculado por población aguas abajo y costo diario.

### `FijarPrioridadCombustible`
**Decidir a qué va el combustible** · Protocolo · [`actions.py:1664`](../src/engine/actions.py#L1664)

> *Decide a qué va primero el combustible que queda: hospitales, transporte o
> industria. Es un criterio permanente, no una entrega puntual.*

**En la sala.** **No hay orden correcto.** Hay un orden que se defiende ante
siete personas que pierden algo. Cada galón que va a la misión médica se le quita
al transporte de alimentos, y las dos cosas tienen quien las reclame en esta mesa.

**En el motor.**
- **Valida** que el orden contenga **exactamente** los cuatro usos:
  `mision_medica`, `fuerza_publica`, `transporte_alimentos`, `consumo_general`.
- Queda como **criterio permanente**: `supply.step()` lo aplica **en cada paso**
  mientras esté puesto. Es **la segunda entrada del reloj** y la única que no
  depende de abrir un corredor.
- Pesos por posición: **4/10, 3/10, 2/10, 1/10**.
- Cada día: `oxígeno += peso(misión_médica) × 0,85` y
  `alimentos += peso(transporte_alimentos) × 0,85`.
- **Si `fuerza_publica` queda tercera o cuarta**, se registra `escolta_degradada`:
  los escuadrones no tienen con qué desplazarse y **la crisis logística empieza a
  volverse crisis de contención**.

> Poner misión médica primera entrega **+0,34 días de oxígeno al día** a cada
> región; ponerla cuarta, **+0,085**. Cuatro veces, cada día, en las cuatro
> regiones — y sin depender de que nadie abra nada. Es la única palanca del
> reloj que no pasa por el territorio.

### `OrganizarCaravana`
**Organizar una caravana** · Operación · [`actions.py:1706`](../src/engine/actions.py#L1706)

> *Junta la carga en una caravana por un corredor prioritario. Necesita escolta
> para poder pasar.*

**En el motor.**
- **Valida** tres cosas, y las tres son de otros: el corredor existe; **hay al
  menos una unidad en escolta** —*habilitada por: Director de Policía*—; y el
  corredor **no está bloqueado** —*habilitada por: Defensa (operar) o Interior
  (concertar)*.
- Repone **`0,6 × caudal`** días de autonomía **por cada clase de prioridad** del
  corredor, en todas las regiones que toca.
- **Legitimidad +3.**

> Es la acción con más requisitos ajenos del repertorio. Sin los otros dos roles,
> no se puede ni intentar.

### `NegociarConGremios`
**Hablar con los camioneros** · Operación · [`actions.py:1771`](../src/engine/actions.py#L1771)

> *Habla con los camioneros antes de que decidan sumarse al paro. Si se suman, se
> cierra lo que hoy todavía circula.*

**En la sala.** Un solo gremio que se sume convierte el bloqueo en cierre
logístico nacional. En el turno 1 llega un **ultimátum de 48 horas**, y hay
**2 turnos** para responderlo.

**En el motor.**
- Si los gremios ya están **sumados**, devuelve **fallo**: la negociación llega
  tarde.
- **Con compensación** → posición **`fuera`**, se cancela el ultimátum;
  legitimidad **+2**, **credibilidad −3** — el Comité lo leerá como trato
  preferente.
- **Sin compensación** → posición **`evaluando`**. La presión se aplaza, no se
  resuelve.

> Los gremios también se mueven solos por umbral: con **legitimidad < 40** pasan
> a evaluando, y con **legitimidad < 25 se suman**, se haya negociado o no.

### `AcordarPasosSeguros`
**Acordar ventanas de paso** · Operación · [`actions.py:1821`](../src/engine/actions.py#L1821)

> *Acuerda ventanas horarias para que pasen carrotanques por un punto. Pasa el
> suministro sin abrir el bloqueo.*

**En la sala.** Despachar sin operación de fuerza — pero **supone reconocer de
hecho una contraparte en el cierre**.

**En el motor.**
- **Valida** que el punto tenga **`control_voceria ≥ 0,25`**: donde nadie manda,
  no hay con quién acordar.
- **`caudal = max(caudal, 0,25 × control_voceria)`**. No abre el punto: abre una
  ventana.
- **Si el Presidente fijó líneas rojas → cohesión −4**: se leerá como negociación
  paralela por fuera de la mesa.

### `PublicarMapaCierres`
**Publicar el mapa de cierres** · Información · [`actions.py:1879`](../src/engine/actions.py#L1879)

> *Publica dónde está cerrado y qué se ha abierto. Anunciar una apertura que no
> se sostiene cuesta credibilidad.*

**En la sala.** Publicar el mapa **le da a la mesa un dato que hasta entonces no
tenía**: qué punto concreto bloquea cada corredor. Es el dato exclusivo de este
rol.

**En el motor.**
- Marca verificado el punto que bloquea cada corredor, con fuente
  `mapa_transporte`.
- Si además **se anuncia un corredor como abierto**:

| Caudal efectivo | Qué pasa |
|---|---|
| **< 0,30** | `costo_de_no_clasificar` **+ legitimidad −4**. *Una docena de camiones presentada como normalización se desmiente sola* |
| **≥ 0,30** | legitimidad **+3**, credibilidad **+2**, y el dato queda utilizable por los demás frentes |

---

---

# 07 · Ministro de Agricultura y Desarrollo Rural

Seis. La que llega es el **calendario de agotamiento**: el reloj de las
cuatro regiones, que era el dato exclusivo del Ministerio de Minas y que
se queda en la cartera cuyo daño ya ocurrió.

### `FijarClasePrioridadAlimentaria`
**Poner los alimentos en la prioridad** · Protocolo · [`actions.py:1957`](../src/engine/actions.py#L1957)

> *Consigue que los alimentos y el alimento de las granjas tengan turno propio en
> el reparto de corredores. Lo que va detrás de todo llega tarde, y lo que llega
> tarde ya no sirve.*

**En la sala.** No pide capacidad nueva: **reordena la que hay**, y se la quita a
un criterio que otro ministro ya defendió. Es la acción que obliga al Presidente
a arbitrar entre dos priorizaciones legítimas dentro de la misma sesión.

**En el motor.**
- **Escribe** la bandera `clase_alimentaria`, que es la **undécima** constitutiva
  del cuadro del Presidente.
- **Añade `"alimentario"`** a las clases del corredor con más población que sirva
  a la región con menos días de comida y todavía no cuente como alimentario. A
  partir de ahí ese corredor alimenta el reloj de la comida en `supply.step()`.
- **Cuesta cohesión −2**, o **−5 si Transporte ya adoptó su criterio único**. La
  diferencia es la fricción declarada entre las dos carteras: entrar en un orden
  que no existe no es deshacer el que un ministro defendió delante de todos.
- Es idempotente por bandera: pedirla dos veces sale «ya vigente».

### `InstalarMesaTecnicaAgropecuaria`
**Sentarse con el campo** · Operación · [`actions.py:2026`](../src/engine/actions.py#L2026)

> *Se sienta con las organizaciones campesinas de un punto rural para acordar el
> paso de alimentos e insumos. Avanza igual que una mesa local, y sigue en pie
> aunque el Comité del Paro se levante.*

**En la sala.** Es **la razón por la que el rol vale un asiento.** Cuando la
credibilidad cae y el Comité suspende, las mesas locales del Interior se quedan
sin los puntos de mejor vocería —justo los que responden a él— y el frente de
estrategia se queda sin canal. Esta no pasa por el Comité: su contraparte son
organizaciones rurales.

Su mandato es **el tránsito de carga y nada más**. El pliego es del Interior, y
desbordar esa frontera rompe la línea roja del Presidente desde dentro del
gabinete.

**En el motor.**
- **Valida jurisdicción al revés que las otras dos mesas:** rechaza los puntos
  del epicentro y nombra al Alcalde y al Interior como quienes sí pueden ahí.
- **No mira `comite_disponible`.** `AbrirMesaLocal` sí, y por eso las dos
  divergen exactamente en el peor día del episodio.
- **Instala mesa** (`aperture.instalar_mesa`) y **avanza la concertación** con la
  misma mecánica de dos sesiones. Se apunta en `estado.mesas_tecnicas_agro`, que
  es lo que el Interior ve en su vista.
- **Cohesión −4** cuando hay protocolo de vocería fijado o un acuerdo nacional
  vivo: es entonces cuando abrir un segundo canal le quita algo a alguien.
- **Respaldo internacional −6** con probabilidad `estructura_organizada × 1,5`.
  Medido sobre el escenario, eso es una cola del **6 % al 18 %** en los puntos
  rurales — un riesgo que se corre, no un peaje que se paga.

### `ActivarInstrumentosSectoriales`
**Aliviar a los productores** · Operación · [`actions.py:2152`](../src/engine/actions.py#L2152)

> *Da crédito y alivios a los productores con pérdida, y autoriza mover animales
> y su alimento por rutas alternas. Alivia sin resolver, y la excepción sanitaria
> deja un riesgo que se paga después.*

**En la sala.** La única suya que no depende de nadie, y por eso la que más se va
a pedir. Mitiga y **no compensa a la escala del daño** — que es lo que la ficha
del rol declara y lo que el segundo paquete demuestra.

**En el motor.**
- **Suma +0,5 días de comida** a la región y **baja `indice_precios`**, que es el
  dato que solo esta cartera lee.
- **Erosiona el apoyo al cierre** en 0,06 — menos que el esquema humanitario
  municipal (0,12), porque el alivio llega al productor y no al barrio.
- **Cada paquete siguiente en la misma región rinde la mitad**
  (`DECAIMIENTO_ALIVIO_SECTORIAL`). Sin esto, repetir la acción cinco jornadas
  apagaba el frente rural entero.
- **Suma uno a `riesgo_sanitario_asumido`**, que **no toca ninguna reserva** y
  sale entero en `metricas()`. Hermano del riesgo de infraestructura, y por la
  misma razón: si moviera un número, la sala jugaría contra el número.

### `PublicarBalancePerdida`
**Publicar lo que se está perdiendo** · Información · [`actions.py:2230`](../src/engine/actions.py#L2230)

> *Publica con los gremios cuántos animales se están sacrificando y cuánto ha
> subido la comida. Le quita respaldo ciudadano al cierre, y le entrega el
> argumento de la urgencia a quien pide mano dura.*

**En la sala.** **La más peligrosa del rol para su propio titular.** Traslada el
costo del cierre al plano de la población, y el mismo argumento lo hereda quien
pide decisión inmediata — lo que puede convertirlo en vocero sectorial del
escalamiento y cerrarle la interlocución rural de la que vive todo lo demás.

**En el motor.**
- **Erosiona el apoyo al cierre en 0,04 en TODAS las regiones**: la cifra circula
  por el país entero, no solo donde hay pérdida.
- **Legitimidad +2, cohesión −3.**
- **Con `protocolo_verificacion`**: respaldo internacional **+2**, la cifra se
  sostiene.
  **Sin él**: credibilidad **−5** y evento `cifra_sectorial_disputada`. Es el
  enlace con el frente de seguridad, y el que decide si esta acción cierra la guerra de
  números o la alimenta.

### `AcordarAcopioYVentanas`
**Concentrar el despacho de alimentos** · Operación · [`actions.py:2286`](../src/engine/actions.py#L2286)

> *Junta la producción en pocos despachos grandes y los manda por la ventana
> escoltada que ya existe. Llega mucha más comida con la misma escolta, y quien
> queda fuera del cupo lo nota.*

**En la sala.** **No pide escolta: hace rendir la que ya está puesta.** Es su
aporte cooperativo al frente logístico, y el único caso del ejercicio en que una
cartera mejora el rendimiento de un recurso de otra sin consumirlo.

**En el motor.**
- **Requiere tres cosas a la vez**: corredor de clase `alimentario`, escolta ya
  dispuesta y ningún punto que lo bloquee. Cada rechazo nombra a quien lo
  habilita — la propia Agricultura para la clase, la Policía para la escolta,
  Defensa o Interior para el punto.
- **Repone `ACOPIO_CONCENTRADO` (1,1) × caudal** en clase alimentaria, contra el
  **0,6** de una caravana normal.
- **Baja `indice_precios`** en las regiones que el corredor sirve.
- **Legitimidad −2, cohesión +2**: los cupos dejan fuera a productores, y la
  escolta rinde más para todos.

### `EntregarCalendarioAgotamiento`
**Decir cuántos días quedan** · Información · [`actions.py:2371`](../src/engine/actions.py#L2371)

> *Dice cuántos días de oxígeno, combustible y comida le quedan a cada región. Es
> el dato que solo usted tiene, y difundirlo también genera pánico.*

**En la sala.** Decir «nos quedan como dos días» en la deliberación es gratis.
**Entregarlo formalmente** convierte el tiempo en variable dura y obliga a
decidir — pero se filtra, hay compra por pánico, y el agotamiento llega antes.

**En el motor.**
- **Sube el pánico +0,35** en **todas** las regiones, con tope en 1,0.
- El consumo diario es `1,0 × (1 + pánico)`: con el calendario entregado una vez,
  **el consumo sube un 35 %** hasta el final del ejercicio.
- **Cohesión +3.**

> **Entregar el reloj cambia el reloj.** Es la única acción del repertorio cuyo
> efecto colateral acelera exactamente aquello que mide.

---
---

---

# Lo que se cobra sin que nadie lo ordene

Tres cosas pasan cada turno de decisión al margen de lo que la sala pida. Están
en [`simulation.py`](../src/engine/simulation.py) y explican por qué las reservas
bajan aunque nadie haga nada mal.

| | Cuándo | Qué cuesta |
|---|---|---|
| **Turno sin órdenes** | ninguna acción se encoló | legitimidad **−3**, movilización `turno_sin_acuerdo` **+1,5**, **todos** los puntos se endurecen **+0,03**, encuadre pasa a *abandono* |
| **Sin protocolo de vocería** | cada turno de día | cohesión **−5** |
| **Sin criterio de priorización** | cada turno de día | cohesión **−3** |

> **Los peajes se cobran solo de día, y eso es una corrección medida.** Cobrarlos
> también en las noches y en la proyección convertía la cohesión en una rampa
> determinista: doce peajes en cinco decisiones, y la serie bajaba igual hiciera
> lo que hiciera la sala. **Una variable que no responde no mide nada.**

Un turno sin órdenes, sin ninguna de las dos banderas puestas, cuesta
**legitimidad −3 y cohesión −8**, más el endurecimiento de los diez puntos. Pero el
castigo real no es la penalización: **es el reloj**, que corre igual.

---

---

# Cinco cosas que este recuento deja a la vista

Salieron de escribir el documento, no de leerlo, y todas son verificables desde
el código. **Tres siguen abiertas; la segunda y la cuarta ya están corregidas**
y se dejan anotadas porque la clase de fallo que ilustran es fácil de repetir.

### 1 · La Policía no tiene acción informativa

La cabecera de [`actions.py`](../src/engine/actions.py) afirma:

> *«Cada rol tiene al menos una de cada clase, y eso es lo que garantiza que
> ningún participante pase el ejercicio sin nada que hacer.»*

**No es cierto para el Director General de la Policía**, que tiene dos
constitutivas —la segunda le llegó con el reparto— y **tres** operativas:

| Rol | P | O | I |
|---|---|---|---|
| Presidente | 2 | 2 | 1 |
| Interior | 1 | 4 | 1 |
| Alcalde | 1 | 2 | 1 |
| Defensa | 1 | 3 | 1 |
| **Policía** | **2** | **3** | **0** |
| Transporte | 2 | 3 | 1 |
| Agricultura | 1 | 3 | 2 |

No es un error de código: es una decisión de diseño que la cabecera describe mal,
o una acción que falta. **Se corrige la frase o se añade la acción**, y esa es una
decisión del equipo docente, no del repositorio.

### 2 · Ocho acciones no se podían pedir en lenguaje natural — **corregido**

**Ya está arreglado.** El canal expone las **39**, y la historia —qué eran, por
qué faltaban, y qué hizo falta para que las ocho llaves nuevas no le robaran la
orden a su vecina— está en
[`historial/resueltos.md` §10](historial/resueltos.md#10--las-ocho-que-no-se-podían-pedir).

Se deja anotado por lo que enseña, que sigue valiendo: **cuatro de las ocho eran
informativas.** La clase «informa» —cambiar lo que el país tiene por cierto— era
la peor servida por el canal, y es justamente la que la sala pide con palabras y
no con un formulario. Una acción que el motor tiene y la consola no alcanza
existe en el código y no existe en el ejercicio.

### 3 · El margen de las líneas rojas no se comprueba

`FijarLineasRojas` es la única acción con un parámetro **numérico continuo**, y
es la única que **no valida su rango**. No sobreescribe `validar()`, así que
acepta cualquier número:

| `margen` | ¿Valida? | ¿Cobra los −8? |
|---|---|---|
| 0,0 · 0,2 | sí | **sí** — correcto |
| 0,25 · 0,5 · 1,0 | sí | no — correcto |
| **20,0** | **sí** | **no** |
| **−3,0** | **sí** | sí, por accidente |

El problema no es teórico: **la escala 0–1 es exactamente lo que se confunde con
un porcentaje**, y falla igual con llave y sin ella.

| La sala dice | Sin llave | Con modelo | Lo que debería pasar |
|---|---|---|---|
| «margen 0.2» | `0,2` ✓ | — | cobra −8 |
| «un margen del **20 por ciento**» | **`20,0`** ✗ | **`20`** ✗ | cobra −8 |
| «**sin ningún** margen» | **`0,5`** ✗ | `0` ✓ | cobra −8 |
| «nada es negociable» | **`0,5`** ✗ | `0` ✓ | cobra −8 |

Pedir un margen del 20 % —que es *estrecho*— produce hoy el resultado del margen
más amplio posible, **sin que nada lo diga**. Y sin llave, las dos formas más
naturales de decir «sin margen» dejan el valor por defecto de 0,5.

Son tres arreglos distintos y ninguno está hecho:

| | Qué | Dónde |
|---|---|---|
| **1** | `validar()` rechaza fuera de `[0, 1]` con un motivo legible, como ya hace `RedesplegarMilitares` con su `modo` | `actions.py` |
| **2** | el intérprete de reserva reconoce «sin margen», «nada negociable», «margen amplio» | `herramientas.py` |
| **3** | el esquema dice que es 0–1 **y que no es un porcentaje** | `herramientas.py` |

> **Lo que no hay que hacer es dividir entre cien cuando el número pasa de 1.**
> Eso sería el canal adivinando qué quiso decir la sala, que es lo único que esta
> capa no puede hacer. Un 20 se rechaza y se repregunta; no se reinterpreta.

### 4 · El Comité del Paro no volvía nunca — **corregido**

**Ya está arreglado**, y la historia completa —qué era, por qué sobrevivió tanto,
y qué se cae con el Comité— está en
[`historial/resueltos.md` §6](historial/resueltos.md#6--el-comité-del-paro-que-no-volvía-nunca).

Se menciona aquí solo por lo que sigue afectando a estas fichas:

| | Cómo funciona hoy |
|---|---|
| **Suspensión** | credibilidad por debajo de **30**: se cae `ConvocarMesaNacional` y `AbrirMesaLocal` en los puntos con vocería > 0,5. **Vuelve** en cuanto la credibilidad remonta los 30 |
| **Retirada definitiva** | si en algún momento bajó de **15**, no vuelve, suba lo que suba después |
| Lo que sobrevive | `InstalarMesaConVoceros` del Alcalde, que no comprueba el Comité, y `AbrirMesaLocal` en puntos con vocería baja |

> **Y una cosa de calibración que sigue abierta:** el costo de −12 por operar
> exige que el Comité esté sentado, así que **en cuanto el Comité se va, operar
> deja de costarlo**. Es un cambio de equilibrio, no una corrección, y se decide
> con gente dentro.
### 5 · Dos pares de acciones escriben la misma bandera

No es un defecto —es deliberado— pero conviene saberlo antes de una corrida,
porque cambia quién se apunta el tanto:

| Bandera | La escriben |
|---|---|
| `protocolo_voceria` | `ExigirProtocoloVoceria` (Interior) y `ConvocarAlcaldes` (Presidente) |
| `protocolo_verificacion` | `ClasificarParteOperacional` y `AdoptarProtocoloVerificacion`, las dos del Director General de la Policía |
| `concertacion_previa_cali` | `CondicionarEmpleoFuerza` (Alcalde) y `ConvocarAlcaldes` con prioridad (Presidente) |

El último es el más consecuente: **el Presidente puede activarle a Defensa el
peaje de −8 legitimidad por operar sin concertar, sin que ni Defensa ni el
Alcalde estén en esa conversación.**

---

*Leído de [`actions.py`](../src/engine/actions.py),
[`parameters.py`](../src/engine/parameters.py),
[`force.py`](../src/engine/force.py),
[`aperture.py`](../src/engine/aperture.py),
[`information.py`](../src/engine/information.py),
[`supply.py`](../src/engine/supply.py),
[`mobilization.py`](../src/engine/mobilization.py) y
[`simulation.py`](../src/engine/simulation.py) · Escuela de Gobierno · Universidad
de La Sabana*


---
---
