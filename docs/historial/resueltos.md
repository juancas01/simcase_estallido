# Lo que ya no está pendiente

Anotado aquí para que nadie lo vuelva a levantar, y separado de
[`PENDIENTES.md`](../../PENDIENTES.md) porque un documento que lleva la cuenta de
lo que falta no puede tener dentro doscientas líneas de lo que ya no falta.

**No está obsoleto: está resuelto.** Se conserva porque cada entrada explica una
clase de fallo fácil de repetir, y porque el porqué de una corrección se pierde
en cuanto se borra el texto que la discutió.

---

## Índice

1. [De la propuesta original](#1--de-la-propuesta-original)
2. [Del diagnóstico del motor anterior](#2--del-diagnóstico-del-motor-anterior)
3. [Las dos capas de lenguaje natural](#3--las-dos-capas-de-lenguaje-natural)
4. [Primera revisión del canal de órdenes](#4--primera-revisión-del-canal-de-órdenes)
5. [Segunda revisión del canal de órdenes](#5--segunda-revisión-del-canal-de-órdenes)
6. [El Comité del Paro, que no volvía nunca](#6--el-comité-del-paro-que-no-volvía-nunca)
7. [El paquete detonante](#7--el-paquete-detonante)
8. [Las superficies](#8--las-superficies)
9. [Revisión general del motor](#9--revisión-general-del-motor)
10. [Las ocho que no se podían pedir](#10--las-ocho-que-no-se-podían-pedir)

---

## 1 · De la propuesta original

> **Ojo con los identificadores de esta tabla:** son los de la propuesta
> original, no los de la lista vigente. El `A6` de aquí —«¿se acepta el azar?»—
> no tiene nada que ver con el `A6` vigente —«¿el mapa muestra dónde está la
> fuerza?»—. Numeraron cosas distintas en momentos distintos.

| | Era | Cómo quedó |
|---|---|---|
| **T1** | `intensidad_movilizacion` satura en 100 y deja de discriminar | Rendimientos decrecientes (×0,6 por repetición) y decaimiento proporcional (×0,96) |
| **T2** | `control_voceria` no está en la capa de estimación | Entró con sesgo por fuente: Interior lo sobreestima +0,20; el Alcalde lo ve bien en su jurisdicción |
| **T3** | `dureza` la escriben dos mecanismos sin precedencia | Tres, con orden fijo en `paso()`. Determinista y reproducible |
| **—** | Toda región sin corredor humanitario acumula muertes inevitables | Invariante con fallo ruidoso en `loader.py` |
| **—** | `P(incidente)` alcanzaba 1,0 y volvía la tirada irrelevante | Techo en 0,98 |
| **A2** | ¿Se puntúa? ¿Las agendas suman? | **No hay marcador.** Las agendas se revelan, no se puntúan |
| **A3** | ¿La Defensoría puede retirarse? | **No se retira.** Su palanca es manifestar públicamente que su permanencia está en cuestión — se puede usar varias veces, es graduada, y nunca saca sus mitigadores del juego |
| **A4** | `capital_politico` no es implementable | Eliminado. Con ocho personas en una sala, el capital político lo administra la sala sola |
| **A6** | ¿Se acepta el azar? | Sí, con semilla fija. **La semilla no es un elemento visible de la interfaz** |

---

## 2 · Del diagnóstico del motor anterior

Los siete problemas que midió [`mapa_de_palancas.md`](mapa_de_palancas.md). El
antes y el después medido está en
[`COMO_FUNCIONA.md` §12](../COMO_FUNCIONA.md#12-los-siete-arreglos-medidos).

| | Era | Cómo quedó |
|---|---|---|
| **D1** | La mezcla real de los puntos no cambiaba **nada** | Conectada por dos vías: operar sobre población civil cuesta más, y pactar donde hay estructura produce un acuerdo que se rompe |
| **D2** | El polo de negociación no podía negociar | Interior tiene cuatro acciones, incluida la mesa nacional. Los dos mayores movimientos hacia abajo de la movilización ya se disparan |
| **D3** | El dueño del ESMAD no podía asignarlo | `DisponerESMAD` y `Escoltar` |
| **D4** | El frente logístico no podía mover carga | Escolta, caravana, gremios, y la prioridad de combustible como criterio permanente |
| **D5** | La cohesión era una rampa determinista | Solo se cobra de día, y ahora se puede reponer. Va de 0 a 74 según lo que la sala haga |
| **D6** | El paquete detonante no existía | Los cuatro hechos, más la jornada nacional en el calendario |
| **D7** | El eje de Vocería no tenía mecánica | **Parcial.** El anuncio verificado y el parte clasificado sí; el encuadre sigue pendiente de la capa 3 |

---

## 3 · Las dos capas de lenguaje natural

Eran `B1` y `B2` de la lista anterior. **Están construidas y probadas con el
modelo puesto.**

| | Era | Cómo quedó |
|---|---|---|
| **capa 4** | el canal de órdenes era un stub que ignoraba el texto | [`src/agents/nlu.py`](../../src/agents/nlu.py) · los nueve pasos, y **solo el primero usa el modelo**. Resolutor determinista de cuatro estados, validación sin `break`, tope de expansión, elección tipada para las ambigüedades y lectura de vuelta determinista |
| **capa 3** | la esfera pública emitía dos frases fijas | [`src/agents/entorno.py`](../../src/agents/entorno.py) · seis agentes con su sesgo y su cadencia, una llamada por turno con presupuesto duro |
| **—** | las tres cifras salían cableadas | Salen de las vistas por rol, con los sesgos calibrados |
| **—** | no había dónde poner la llave | `.env` en la raíz, a partir de `.env.example`. `GET /api/config` dice si está |

**Las dos degradan solas si falta la llave o si el proveedor tarda**, y lo dicen
en el campo `generado_por`. Esa degradación es la prueba operativa de que ninguna
decisión de la simulación se delegó al modelo.

---

## 4 · Primera revisión del canal de órdenes

La capa 4 se sondeó por primera vez con órdenes reales y aparecieron nueve
fallos. **Cuatro eran silenciosos**, que es la peor clase: el canal hacía algo
distinto de lo que la sala pidió y lo informaba como cumplido.

| | Era | Cómo quedó |
|---|---|---|
| **N1** | «Operen el puente **y** concertar el Alto del Mirador» producía DOS acciones sobre el Alto del Mirador: el intérprete buscaba nombres en todo el texto | Cada disparador solo mira **su cláusula**. La ambigüedad de «el puente» sobrevive y se repregunta |
| **N2** | «Operen todos los puntos» ejecutaba **uno**: el expansor se quedaba con `ids[0]` | Un criterio produce **una acción por punto**, con tope y con aviso |
| **N3** | La lectura en voz alta decía «operación de desbloqueo sobre un punto de cierre» — **sin decir sobre cuál** | Dice sobre qué punto, con qué unidad y con qué mitigadores |
| **N4** | «Operen X **con militares**» salía como ESMAD: el intérprete de reserva no leía la unidad | La lee, tras una marca («con», «usando»), para que «responsable el Director de Policía» no cuente |
| **N5** | Cuatro criterios documentados —«el más duro», «el más crítico», «el que bloquea», «el más…»— eran **inalcanzables**: `normalizar()` quita el artículo y la tabla los guardaba con él | Las claves se normalizan al cargar |
| **N6** | «Operen el Anillo hospitalario» respondía «no corresponde a ningún punto, corredor ni región» — y es un corredor | Dice qué es, y enumera sus puntos. Nunca cuál lo bloquea: eso es de Transporte |
| **N7** | Vacío, galimatías, saludo, pregunta y «declaren el estado de sitio» daban **el mismo párrafo** | Cuatro diagnósticos distintos, porque son cuatro correcciones distintas |
| **N8** | `consultar` se le ofrecía al modelo pero **no existía** en el repertorio: al llamarla, «Herramienta desconocida» | Herramienta de solo lectura, con su hoja de datos en el plan y sin llegar al motor |
| **N9** | `/ejecutar` encolaba acciones en `falta_dato`, y un `except: continue` tiraba las que fallaban **sin decirlo** | Solo se ejecuta lo que está `lista`; lo que no, sale en `omitidas` con su motivo |

Y dos del motor, que sostenían por debajo dos de esos fallos:
`RedesplegarMilitares` no validaba su `modo` —un valor desconocido caía por el
`else` y hacía **proyección aérea**— y `AsignarDuplas` daba por buena una
asignación sin ningún punto ni denuncia.

---

## 5 · Segunda revisión del canal de órdenes

Al volver a sondear el canal —esta vez **con el modelo puesto** y no solo la rama
determinista— aparecieron otros nueve. **Cinco eran silenciosos**, y dos llevaban
puesta la etiqueta contraria: el código decía en su propia cabecera que hacía lo
que no hacía.

| | Era | Cómo quedó |
|---|---|---|
| **M1** | El constructor de `abrir_mesa_local` ponía `con_alcaldia=True` **cuando nadie lo había dicho**. En el epicentro esa es la única puerta que obliga al Interior a traer al Alcalde, y por el canal **no se cerró nunca** | Por defecto **no** está la Alcaldía. La orden sale `no_viable` y dice quién la habilita. «Con la Alcaldía» dicho sí cuenta |
| **M2** | Dos de las herramientas —`redesplegar_militares` y `mesa_con_voceros`— **no tenían disparador**: sin llave, el canal respondía «ninguna acción del repertorio corresponde a eso» sobre acciones que sí tiene | Las dos tienen el suyo. **El canal ya no niega tener lo que tiene** |
| **M3** | Los valores por defecto vivían dentro de `construir`: la acción se ejecutaba con ESMAD, con seis escuadrones o con un margen de 0,5, y como el argumento no estaba en `argumentos`, **la lectura en voz alta no lo decía** | `por_defecto` declarado por herramienta. Viaja en el plan, se dice, y se puede corregir con un botón |
| **M4** | El intérprete de reserva no leía **ninguna cifra**: «concentrar 8 escuadrones» concentraba seis | Las lee, en dígitos y en letras. También el margen de las líneas rojas |
| **M5** | Tampoco leía **quién firma**. Con el registro escrito adoptado, `responsable_nominado` es lo que hace atribuible un incidente: esa mecánica entera moría al correr sin llave | Se extrae tras «responsable», y se dice en la lectura |
| **M6** | «Operen X **concertado con la Alcaldía**» abría una mesa que nadie pidió —la raíz `concert`— y se llevaba el resto de la frase: la operación perdía el mitigador **y** el responsable que venían detrás | Hay frases que son parámetro de la orden anterior y no empiezan otra |
| **M7** | `condicionar` es un infinitivo, no una raíz: «el Alcalde **condiciona** el empleo de la fuerza» no disparaba nada | La raíz aguanta la conjugación |
| **M8** | La lectura en voz alta **no decía de qué rol era cada acción**. «Instalar mesa con voceros» —del Alcalde— salía como la mesa del Interior, y la sala no tenía cómo oírlo | Cada línea empieza por su rol. En un ejercicio cuyo objeto es quién tiene qué palanca, eso es el dato |
| **M9** | Preguntar **gastaba un turno**: un plan de solo consultas llegaba a `/ejecutar` y corría `motor.paso()` igual. La sala preguntaba cuánto oxígeno quedaba y se le iba una de las cinco ventanas | El reloj no se mueve, y la respuesta lo dice |

Y cuatro que solo aparecen **con el modelo puesto**. Los tres primeros son la
misma lección escrita tres veces: *restringir el espacio de salida no impide que
el modelo se salga.*

| | Era | Cómo quedó |
|---|---|---|
| **M10** | El modelo **se concedía a sí mismo** lo que M1 le quitó al constructor: «concertar en la Glorieta La Ceiba» volvía con `con_alcaldia: true` sin que nadie hubiera nombrado a la Alcaldía. Lo mismo con la dupla y con la firma delimitada | `NO_SE_INFIERE`: cuatro booleanos que **conceden** un requisito o rebajan un riesgo se contrastan contra el texto que escribió la sala. Solo **bajan** concesiones —añadir sería el canal decidiendo— y lo que se quita **se dice** |
| **M11** | `bool("false")` es `True`. El `valor` de una elección tipada viaja siempre como cadena, así que un «no» pulsado en la pantalla habría entrado como sí | Cada campo se lleva al tipo que declara su esquema antes de tocar el motor. Lo que no se puede convertir se avisa y no se inventa |
| **M12** | Dos parejas de herramientas se confundían: «redesplegar cuatro unidades militares» salía unas veces como el **relevo del Director de Policía**, y la caravana como la escolta | Una nota `para_el_modelo` por herramienta confundible, que **no** se lee en voz alta: la sala oye la descripción corta, el modelo recibe además qué la distingue de su vecina |
| **—** | «Operen eso de allí» respondía «esa acción no existe» — y la acción se había entendido perfectamente | Si se reconoce el verbo pero no el sitio, se dice así, que es otra corrección |

Y tres del cauce, que no son del canal pero lo sostienen:

| | Era | Cómo quedó |
|---|---|---|
| **—** | **La verificación automática salía a la red.** Se silenciaba la capa 4, pero la capa 3 —la esfera pública— seguía disparándose con el cliente real: casi tres minutos por corrida y llamadas facturadas, en lo que se corre en cada cambio | Un accesorio único silencia **las dos**. Un accesorio por archivo es justo lo que dejó media puerta abierta |
| **—** | Con el modelo, un lugar ambiguo hacía que **no llamara a nada**: «operen el puente» respondía «esa acción no existe», y la repregunta con candidatos —para la que existe `resolver.py` entero— no se disparaba nunca | Un sitio ambiguo se copia tal cual y se llama igual. Lo único que justifica no llamar es que la **acción** no exista |
| **—** | La pantalla adivinaba a qué campo pertenecía cada entidad buscando el valor crudo entre los argumentos. Para los de **lista** no aparecía nunca, así que corregir uno de los tres puntos de `asignar_duplas` moría en un 400 | Cada entidad viaja con su campo, y una elección sobre un campo de lista **completa** en vez de sustituir |

**Lo que sigue sin poder hacer la rama sin llave:** un nombre que no está en el
catálogo y que tampoco se parece a nada **no se ve**. «Duplas al Puente Amarillo,
al Puente de Brooklyn y al Alto del Mirador» asigna dos y no puede nombrar el que
perdió, porque nunca lo reconoció como nombre. Por eso la lectura ahora
**cuenta** —«Sobre 2: …»—: si la sala dijo tres y oye dos, la resta la hace ella.
Con el modelo puesto no pasa: el nombre viaja crudo y sale por su nombre.

**Queda un residuo, y es del modelo, no del cauce.** «Concertar en el Alto del
Mirador» sale una de cada tres veces como la mesa del Alcalde. El punto está
fuera de su jurisdicción, así que el motor la rechaza diciendo que la habilita el
Ministro del Interior, y la lectura en voz alta empieza por el rol — la sala lo
oye. Es el diseño funcionando: **el modelo se equivoca y el cauce lo atrapa.**

---

## 6 · El Comité del Paro, que no volvía nunca

> **La clase de fallo que ilustra es fácil de repetir:** *una variable de estado
> que solo se escribe en una dirección.*

**Era así.** `comite_disponible` se asignaba **una sola vez en todo el motor**
—en `_aplicar_umbrales`, y siempre a `False`—. Nada, en ningún archivo, la volvía
a poner en `True`. Medido: se tumbaba el Comité con dos operaciones, se subía la
credibilidad **a 95** —más de tres veces el umbral— y no volvía.

```
T2  credibilidad 21,0  comite_disponible=False   convocar mesa: NO
    [se fuerza la credibilidad a 95,0]
T6  credibilidad 95,0  comite_disponible=False   convocar mesa: NO
```

**Que era un fallo y no una decisión lo decían cuatro fuentes**, y la primera es
el propio motor:

| | Qué dice |
|---|---|
| El mensaje de rechazo de `ConvocarMesaNacional` | *«la credibilidad está por debajo del umbral **en que vuelve a sentarse**»* |
| `parameters.py` | declara **dos** umbrales: `comite_suspende` = 30 y `comite_definitivo` = 15. Si los dos fueran permanentes, el segundo sobra |
| La propuesta | *«el Comité del Paro **suspende**, y si cae más no vuelve a sentarse»* |
| `views.py` | expone el campo como `comite_se_sentaria_hoy` — una lectura viva, turno a turno |

`_aplicar_umbrales` colapsaba las dos ramas en una:

```python
elif u in ("comite_suspende", "comite_se_retira_definitivo"):
    e.comite_disponible = False        # y nadie lo vuelve a poner en True
```

**El umbral de 15 era, de hecho, código muerto:** no producía ningún
comportamiento distinto del de 30.

**Por qué no se detectó.** A tres de las seis estrategias se les cae el Comité
—`solo_fuerza` en el turno 1, `constituida` y `logistica` en el 4— pero **ninguna
intenta recuperarse**, así que ninguna vuelve a cruzar los 30. El fallo era
invisible para el corredor sin interfaz y **solo aparecía con una sala dentro**.
Y aparecía rápido: una sala que pierde el Comité en el turno 2 y dedica el 3 a
recuperarse veía esto —

```
T3  credibilidad 35,0  POR ENCIMA del umbral    comite_disponible=False  convocar: NO
T5  credibilidad 49,0  más alta que al empezar  comite_disponible=False  convocar: NO
```

— es decir, **un turno bastaba para recuperar la credibilidad y no servía de
nada.** Lo que la sala aprendía es que reparar no se premia, que es lo contrario
de lo que el ejercicio quiere enseñar.

**Cómo quedó.** Dos reglas, y las dos estaban ya declaradas en el modelo:

| | |
|---|---|
| **Vuelta simétrica** | el Comité se vuelve a sentar en cuanto la credibilidad remonta los **30**. Se registra el evento `comite_vuelve` y la esfera pública lo narra |
| **Retirada definitiva** | si en algún momento bajó de **15**, no vuelve. La bandera `comite_retirado_definitivo` es la que ahora sí es de un solo sentido |
| La vista de Interior | dice cuántos puntos de credibilidad faltan para que vuelva, o que ya no vuelve |

La vuelta necesitaba su propia comprobación —`_revisar_vuelta_del_comite()`— y
por eso no existía: `umbrales_cruzados()` informa de lo que está cruzado **ahora**
y calla en cuanto se deja de estar por debajo, así que nunca podía anunciar un
regreso.

**No mueve la calibración.** Ninguna de las seis estrategias intenta recuperarse,
así que la puerta nueva no llega a abrirse para ellas. Cambia solo lo que le pasa
a una sala que repara — el caso que las estrategias no cubren y por el que el
fallo sobrevivió tanto.

**Se cae con el Comité más de lo que parece:**

| | ¿Sobrevive? |
|---|---|
| `ConvocarMesaNacional` | **no**, mientras esté suspendido |
| `AbrirMesaLocal` en puntos con vocería > 0,5 | **no** — y son los que más caudal abren |
| `AbrirMesaLocal` en puntos con vocería baja | sí |
| `InstalarMesaConVoceros` del Alcalde | **sí** — no comprueba el Comité |
| El encuadre de *negociación* por aperturas | **no**: `_recalcular_encuadre` lo condiciona a `comite_disponible` |

**Queda una cosa sin resolver, y es de calibración.** El costo de −12 por operar
exige `comite_disponible`. En cuanto el Comité se va, **operar deja de costar
esos 12 puntos**: medido, `+0` en vez de `−12`. El motor abarata la acción justo
después de que haya destruido aquello que la encarecía. Con la vuelta
implementada eso deja de ser una puerta de un solo sentido y pasa a ser un
**estado que la sala puede administrar**: mantenerse por debajo de 30 hace la
fuerza gratis, y subir de 30 solo cuando se quiera una sesión. **No se ha
tocado** — es un cambio de equilibrio, no una corrección, y el criterio de
aceptación del proyecto es la tabla de estrategias.

---

## 7 · El paquete detonante

**B4** era el último de los cuatro hechos que abren el turno 1.

| | Qué | Dónde |
|---|---|---|
| **H1** | el incidente nocturno junto a la refinería, con un herido grave de la fuerza pública | `hecho_h1` en [`estado_inicial.json`](../../data/escenario/estado_inicial.json), aplicado por `_aplicar_hecho_h1()` |
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

Responder con fuerza es la jugada evidente —hay un herido de la fuerza pública— y
es la más cara, donde menos se puede negociar, sobre el corredor que otra cartera
necesita intacto. Y la mesa aún no se ha constituido: los mitigadores están al
mínimo.

> **H1 no mata a nadie ni abre el punto.** Es una condición inicial, no un
> resultado: el turno 1 empieza con más decisiones sobre la mesa, no con menos.

Al implementarlo se descubrió **C4**, que sigue abierto en
[`PENDIENTES.md`](../../PENDIENTES.md).

---

## 8 · Las superficies

| | Era | Cómo quedó |
|---|---|---|
| **—** | tres superficies contra la API antigua | Tres rutas: `/tablero` —con la esfera dentro—, `/vista/{rol}` ×8 y `/consola` |
| **—** | el mapa era un puñado de códigos sobre un lienzo vacío | **Mapa en dos niveles** sobre una **silueta costera real** (sin que conste cuál): el país con su litoral y su puerto, cada región teñida de su estado de bloqueo; un clic acerca la región y enseña sus puntos y sus corredores |
| **—** | del territorio solo se sabía si un punto estaba abierto | **Seis lecturas** por punto y las mismas seis promediadas por región — paso, dureza, gente, días, apoyo del barrio, vocería — en banda y sin el número interno |
| **—** | el mapa no decía qué había cambiado | La forma del punto dice cómo se abrió, un `?` marca lo que nadie ha mirado, y **un anillo señala lo que cambió en la última ventana** |
| **—** | el tablero no decía qué hora era | `Estado.reloj()` · cinco jornadas del 11 al 15 de mayo, y la noche se ve distinta |
| **—** | un número solo no decía si iba a mejor | `MotorCrisis.deltas()` · ▲▼ contra la ventana anterior, no contra el arranque |
| **—** | cada cifra llevaba su glosa impresa debajo | Marca **(?)** y las definiciones formales en [`definiciones.jsx`](../../web_ui/src/definiciones.jsx) |
| **—** | el reloj de fases lo llevaba el moderador | Lo lleva el sistema. **Dos tramos y no siete**: 13 min de día en que se ordena, 2 de noche en que no, y la consola se apaga sola |
| **—** | las reservas eran cuatro cifras proyectadas | **Métricas** en escala de cinco pasos, sin un solo número: un nivel se interpreta, un número se optimiza |
| **—** | el repertorio no decía si una acción era pedible | **Semáforo por acción**, calculado desde `validar()`, con el requisito en general y quién lo habilita |
| **—** | una pantalla sin datos parecía una pantalla muerta | `Cargando` dice qué se pide y desde dónde, y un `Salvavidas` impide que un fallo de render deje la pantalla en blanco |

---

*Escuela de Gobierno · Universidad de La Sabana*

---

## 9 · Revisión general del motor

Salió de una pregunta simple —*¿todas las acciones se pueden pedir y ejecutar?*—
y de auditar el motor entero para contestarla. Las treinta y nueve se ejecutan
sin reventar; **ocho no se pueden pedir**, y eso ya estaba anotado en
[`PENDIENTES.md` · B10](../../PENDIENTES.md). Lo que no estaba anotado es esto.

**Los cuatro son de la misma familia: una unidad que no coincide con su nombre.**
Ninguno tumbaba nada, y por eso ninguno se había visto.

| | Era | Cómo quedó |
|---|---|---|
| **M1** | `dias_sostenido` se incrementaba en los DOS tramos de la jornada. Un punto con quince días de cierre marcaba veinticinco al terminar un ejercicio de cinco días | Se cuenta al cerrar la jornada. Dos pruebas: el avance es 1 por jornada, y la banda del mapa no satura en «crónico» antes de la segunda |
| **M2** | `REAPERTURA_FUERZA_TURNOS_BASE = 2` no la leía nadie: el código comparaba contra un `1` escrito a mano. Quien calibrara moviendo el 2 no habría cambiado nada, y habría creído que sí | Es `PASOS_ANTES_DE_REABRIR = 1`, conectada. El nombre dice ahora en qué unidad cuenta: contaba pasos del motor y decía turnos |
| **M3** | «acordar el **despacho concentrado**» disparaba también `disponer_esmad`: la raíz `concentr` está dentro de la frase. La orden salía con una concentración de ESMAD que nadie pidió | Exclusión en el disparador, con prueba. Es el mismo modo de falla que obligó a separar la mesa del Alcalde de la del Interior |
| **M4** | `DENUNCIAS_POR_PAQUETE = 2` existía sin que nadie la leyera: el `2` estaba escrito a mano en tres sitios de `_generar_paquete` | Conectada, y el reparto de veracidad se deriva del tamaño en vez de ser una lista fija |

**Y dos contratos que el código declaraba y nadie comprobaba**, ahora con prueba:

- **`validar()` no muta el estado.** Importa por el semáforo del repertorio:
  `disponibilidad()` llama a `validar()` para las treinta y nueve acciones cada
  vez que alguien abre su tablero. Si una sola mutara, **mirar la pantalla
  cambiaría la corrida** — y con nueve dispositivos refrescando, la partida
  dependería de quién mira y cuándo. Las treinta y nueve están limpias; lo que
  faltaba era la prueba.
- **Ninguna constante de `parameters.py` queda sin leer sin estar declarada.**
  La prueba no prohíbe las huérfanas: obliga a que aparecer en la lista sea una
  decisión escrita. Quedan tres, y su razón está en `PENDIENTES.md · B12`.

> **Lo que la suite no veía y por qué.** Los cuatro tocan números que **solo se
> dibujan** o que **solo se documentan**. Un dato que no entra en ningún cálculo
> no rompe ninguna prueba de comportamiento, y es justamente el que nadie va a
> contrastar contra nada: sale en la pantalla con la palabra «días» al lado y se
> cree. `PENDIENTES.md · B9` —«ninguna prueba mira lo que la interfaz dibuja»—
> sigue siendo la entrada que más falta hace.

---

## 10 · Las ocho que no se podían pedir

Era [`PENDIENTES.md` · B10](../../PENDIENTES.md), y salió de la pregunta más
simple que se le puede hacer a este repositorio: *¿todas las acciones se pueden
pedir?* **Treinta y una de treinta y nueve.**

Las ocho existían en el motor, estaban probadas y el corredor sin interfaz las
ejecutaba. Lo que no existía era su puerta. **La consola es la ÚNICA entrada al
motor durante una sesión**, así que con gente en la sala esas ocho se acordaban
de palabra y no se transcribían: el Ministro de Defensa no podía adoptar el
estándar de su propio sector, y Minas no tenía cómo hacer pasar suministro sin
abrir el punto ni gastar escolta.

| Rol | Como la ve el participante | Cómo se pide ahora |
|---|---|---|
| Presidente | Reunir a los alcaldes | «reunir a los alcaldes de las ciudades críticas» |
| Presidente | Ir al epicentro en persona | «ir al epicentro en persona» |
| Alcalde | Publicar el conteo de la ciudad | «publicar el parte municipal de la ciudad» |
| Defensa | Poner reglas a sus unidades | «fijar las reglas de empleo del sector» |
| Defensa | Mostrar quién financia los cierres | «presentar la evidencia de inteligencia» |
| Defensoría | Acordar una sola forma de verificar | «adoptar el protocolo único de verificación» |
| Transporte | Publicar el mapa de cierres | «publicar el mapa de cierres» |
| Minas | Acordar ventanas de paso | «acordar pasos seguros en el Puente Amarillo» |

### Lo que no era mecánico

`PENDIENTES.md` decía que el arreglo lo era: una entrada en `HERRAMIENTAS`, un
disparador y una fila en `GUIA`. Lo es hasta que se mira **con qué vecina choca
cada llave nueva** — y las ocho chocan con alguna, porque el intérprete sin
modelo busca raíces dentro del texto:

| La orden | Disparaba además | Y eso es |
|---|---|---|
| «adoptar el protocolo de **verific**ación» | las tres duplas de la Defensoría | el recurso más escaso del rol, gastado sin pedirlo |
| «fijar las **reglas de empleo** del sector» | el estándar que exige la Defensoría | **otro rol firmando** |
| «ir al epicentro acompañando la **oper**ación» | una operación de desbloqueo sin punto | una orden que nadie dio |
| «clasificar el parte **oper**acional» | lo mismo | y esta **ya estaba ahí**, encontrada al barrer los treinta y nueve ejemplos |

La salida fácil era una exclusión de texto entero, que es lo que el archivo ya
usaba dos veces. **Y habría sido peor que el problema**: una exclusión mira el
mensaje completo, de modo que «operen el Puente Amarillo y clasifiquen el parte
operacional» habría perdido la operación **en silencio**. Una acción de más se
ve en la lectura en voz alta; una acción de menos, no.

Así que se separaron con dos reglas, las dos en `_clausulas`:

- **`FRASES_OPACAS`** — tramos donde una raíz no cuenta porque está dentro del
  nombre de otra cosa: «parte operacional», «de verificación», «de verificar».
  «Asignar duplas de verificación» sigue siendo una orden de duplas, porque su
  raíz aparece fuera del tramo.
- **A igualdad de posición, gana la raíz más larga.** «Reglas de empleo del
  sector» y «reglas de empleo» empiezan en la misma letra; la específica se
  queda con la orden. Dos acciones distintas no pueden empezar en el mismo
  carácter, así que esto no pierde ninguna — y evita excluir «del sector» del
  estándar de la Defensoría, que sí la habría perdido en cuanto alguien pidiera
  las dos cosas en el mismo mensaje.

### Dos que se entendían y se rechazaban siempre

Salieron de barrer los treinta y nueve ejemplos, y son de la misma familia que
lo anterior: **la acción se puede pedir y no se puede hacer.**

- **`DeclararInfraestructuraCritica`** traía `["refineria"]` como valor por
  defecto, y la refinería **empieza el escenario custodiada**. La orden se
  entendía, construía la acción correcta y se rechazaba —«esa instalación ya
  está bajo custodia»— en todas las primeras jornadas. Un valor por defecto que
  siempre se rechaza no es un valor por defecto: es una acción que la sala no
  tiene. Ahora la instalación **se dice**, y para eso el registro de
  infraestructura entró en el catálogo del resolutor, que es lo que da la
  repregunta con candidatos. La resolución final la sigue haciendo el motor,
  que no acepta difuso: acertar mal ahí pone la custodia en la instalación
  equivocada y deja sin proteger la que se quiso proteger.
- **`AcordarPasosSeguros`** pedía el paso en el Puente Amarillo, que es el
  punto con **menos vocería reconocida** del escenario — justo donde no hay con
  quién acordarlo.

`test_ningun_ejemplo_de_la_guia_se_rechaza_en_la_primera_jornada` lo vigila.
Deja pasar dos, declaradas: la caravana de Transporte y el acopio de
Agricultura necesitan una escolta que pone la Policía, y eso no es un defecto
de la ficha — es la interdependencia del ejercicio.

### Tres booleanos que había que poder decir

Tres de las ocho llevan un campo que cambia lo que el motor cobra, y ninguno se
deducía de que la orden sonara razonable:

- **`concede_prioridad`** (reunir a los alcaldes) y **`declara_solidez`**
  (evidencia de inteligencia) se piden como `delimitada`: **no se dan por
  puestos.** El primero cede prioridad de fuerza al epicentro; el segundo dice
  qué casos no aguantan ante un juez, cuesta hoy y protege la credibilidad del
  sector el resto del episodio.
- **`disputa_cifra`** (parte municipal) va al revés, y es la excepción: viene
  puesto. No concede nada a quien lo pide —está en el nombre de la acción— así
  que no se contrasta contra el texto; se lee en voz alta antes de confirmar.

### Lo que queda vigilado

- `test_las_treinta_y_nueve_acciones_se_pueden_pedir_por_la_consola` — cada
  acción con **las tres cosas**: herramienta, disparador y ejemplo.
- `test_ningun_ejemplo_de_la_guia_arrastra_una_accion_de_mas` — la contraparte
  que faltaba: la prueba anterior miraba que la suya **estuviera**, no que fuera
  **la única**. Por ahí se colaban las dos de `oper`.
- `test_las_ocho_llaves_nuevas_no_le_roban_la_orden_a_su_vecina` — y, al revés,
  que la vecina siga siendo alcanzable.

> Y se fue una rama muerta: la celda que dibujaba «todavía no se transcribe: se
> acuerda en la mesa» ya no puede ocurrir, y la columna **LN** de
> `LAS_ACCIONES.md` —que decía cuáles sí y cuáles no— tenía las treinta y nueve
> celdas diciendo lo mismo.
