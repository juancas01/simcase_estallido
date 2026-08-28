# El diseño del juego — el ejercicio como decisión compartida

**Qué es esto.** El modo de juego y el modelo del mundo: qué se simula y hasta
dónde, qué ve cada uno de los nueve, qué puede hacer, y cómo eso afecta a los
demás. **No hay que saber programar para leerlo.**

**Qué NO es esto.** Ni el detalle de cada acción —eso es
[`LAS_ACCIONES.md`](LAS_ACCIONES.md)—, ni el cálculo que produce cada efecto
—eso es [`COMO_FUNCIONA.md`](COMO_FUNCIONA.md)—, ni dónde vive cada cosa en el
repositorio —eso es [`EL_CODIGO.md`](EL_CODIGO.md)—.

> Los términos propios del caso —punto de cierre, corredor, dupla, escuadrón,
> mitigador— se explican al usarlos por primera vez, y están todos reunidos en el
> [glosario](#glosario) al final.

---

## La idea, en una escena

Turno 2. Hay **una escolta disponible** y tres corredores la piden. Los nueve
tienen la misma pantalla común delante y todos están diciendo la verdad:

> **Transporte:** *«El corredor al puerto mueve los alimentos de 780 mil
> personas. Llevo el costo diario y es el más caro de todos.»*
>
> **Minas:** *«El corredor hospitalario es el único camino humanitario que sirve
> a Las Cumbres, y Las Cumbres tiene oxígeno para menos de dos días.»*
>
> **Policía:** *«El punto que bloquea el corredor al puerto es el más caliente
> del país. Si no se atiende hoy, mañana no es un punto: son tres.»*
>
> **Alcalde:** *«Ese puerto es el que alimenta a mi ciudad, y llevo nueve días
> con el comercio paralizado.»*
>
> **Defensoría:** *«En ese punto hay una denuncia grave que no he podido
> verificar. Operar ahí antes de verificarla es el peor escenario posible.»*

**Cinco criterios legítimos, una escolta, ninguna respuesta correcta.** Nadie
ocultó nada, nadie mintió, y la decisión sigue siendo difícil — porque lo es.

> **Eso es lo que la vista privada existe para producir.** No un juego de
> secretos: **una deliberación donde cada uno aporta el pedazo del país que solo
> él ve con nitidez, y donde el desacuerdo sobrevive a la transparencia.**

---

## Los cuatro cambios que ordenan el diseño

| | Cambio | Por qué |
|---|---|---|
| **1** | **Cada rol tiene una vista privada** con su cartera en alta resolución, en su propio dispositivo | Para que su criterio tenga peso propio y las decisiones tengan más consideraciones |
| **2** | **El tablero general lleva el grueso de la información** | La simulación se sigue desde ahí. La vista privada es un complemento fino, no un sustituto |
| **3** | **Entre 4 y 5 acciones por rol**, no todas iguales | El Presidente decide más que el Ministro de Minas. Lo que importa es que ninguno se quede corto |
| **4** | **No hay moderador como figura aparte** | Quien opera la consola puede ser un participante. El sistema conduce el turno |

### Sobre el input del GovLab

Se revisó el *Manual de Roles con RADs* y la *Matriz Operativa*. **No hay
contradicción, y en dos puntos esta versión completa algo que el propio GovLab ya
había dejado planteado.**

| Punto | Qué dice el Manual | Cómo queda |
|---|---|---|
| **Transparencia entre roles** | los apartados 10 describen **fricciones entre mandatos legítimos**, no antagonismo personal | Alineado: son exactamente las tensiones que sobreviven a la transparencia total |
| **Agendas reservadas** | *«el apartado 11 contiene información reservada del rol… se juega, no se enuncia»* | **Transparencia sobre los hechos, reserva sobre los motivos.** Los nueve pueden estar de acuerdo en los hechos y seguir sin estar de acuerdo en qué hacer |
| **Moderador** | elimina al Director del DAPRE porque *«sus funciones… las ejecuta el motor de simulación»* | El GovLab ya había decidido que la conducción es del sistema. Quitarlo como figura aparte lo lleva hasta el final |
| **Número de acciones** | *«cada rol queda descrito con exactamente cinco recursos, cinco acciones y cinco efectos»* | **Desviación consciente:** entre 4 y 5, porque con cinco turnos algunas no alcanzan a rendir. Cada omisión se justifica en §5 |

---

## Índice

1. [El principio: resolución, no secreto](#1-el-principio-resolución-no-secreto)
2. [El mundo: qué se modela y hasta dónde](#2-el-mundo-qué-se-modela-y-hasta-dónde)
3. [El tablero general](#3-el-tablero-general)
4. [Las nueve vistas privadas](#4-las-nueve-vistas-privadas)
5. [Las acciones](#5-las-acciones)
6. [Cómo se juega un turno](#6-cómo-se-juega-un-turno)
7. [Los dilemas que esto garantiza](#7-los-dilemas-que-esto-garantiza)
8. [Las decisiones del equipo](#8-las-decisiones-del-equipo)
· [Glosario](#glosario)

---

## 1. El principio: resolución, no secreto

### 1.1 La misma foto, distinta nitidez

**Nadie tiene información que los demás no puedan pedir.** Lo que cada uno tiene
es **su cartera en alta resolución**, y el resto del país en grano grueso.

```
EL TABLERO GENERAL dice:      Las Cumbres · abastecimiento ● ROJO

LA VISTA DE MINAS dice:       Las Cumbres
                                oxígeno       1,8 días  ↓ 0,4 sin ingreso mañana
                                combustible   2,8 días
                                alimentos     2,5 días
```

La mesa entera sabe que Las Cumbres está mal. **Solo Minas sabe cuánto tiempo
queda**, y hasta que lo diga la sala no puede ponerle fecha a nada. No es un
secreto: es que nadie más tiene ese instrumento.

Lo mismo con los demás. El tablero dice que el corredor al puerto está cerrado;
Transporte sabe **cuál de sus puntos** lo bloquea. El tablero dice cuántos
escuadrones quedan libres; la Policía sabe **cuán cansados están y cuánto tardan
en llegar**. El tablero muestra las cifras que circulan; la Defensoría sabe
**cuál de las denuncias alcanzó a verificar y cuál no**.

> **La regla que ordena todo el reparto:**
>
> El tablero general responde **qué está pasando**.
> La vista privada responde **cuánto, dónde exactamente, y desde cuándo**.

### 1.2 Personal, no confidencial

**La vista es personal porque el sistema solo se la muestra a su titular. No es
un secreto y nadie está obligado a callársela.** Un participante puede leerla en
voz alta, girar su pantalla hacia el vecino, o anotar su número en una hoja
común. No hay ninguna regla que lo prohíba, y de hecho el ejercicio quiere que se
comparta.

Lo que la hace valiosa no es que esté oculta: **es que hay una sola persona que
la tiene actualizada.**

### 1.3 El detalle no migra al tablero

**Aunque un rol diga su número en voz alta, el número no se escribe en el tablero
general.** La mesa lo oyó, alguien puede anotarlo, y ahí queda.

> **Consultar a un rol una vez no lo agota.** Si Minas dijo en el turno 2 que
> quedaban 1,8 días, en el turno 3 ese número cambió — y sigue siendo el único
> que tiene el nuevo. La mesa tiene que volver a preguntarle. **Cada turno, cada
> rol vuelve a ser necesario.**

Si el dato se fijara en el tablero, el rol se consultaría una vez y después
sobraría. Es exactamente lo que se quiere evitar.

**Hablar es gratis; hacerlo oficial tiene consecuencia.** Decir *«nos quedan como
dos días»* en la deliberación no cuesta nada. **Entregar formalmente el
calendario de agotamiento** —que es una acción— sí: queda en el registro, obliga
a la mesa a decidir con plazo, y se filtra hacia afuera, donde produce compra por
pánico y acelera el agotamiento que mide. Lo mismo con la cifra oficial: contar
en voz alta es gratis; publicar el parte y sostenerlo es un acto que después se
contrasta con la verdad.

### 1.4 Lo que esto produce: decisiones sin respuesta correcta

La escena de arriba no es una ilustración: **es el patrón que el diseño repite
turno a turno**. Cada decisión importante enfrenta criterios que son todos
legítimos y que apuntan a sitios distintos.

| La decisión | Los criterios que compiten |
|---|---|
| **Qué corredor se abre primero** | población afectada · días de autonomía · costo económico · calor del punto · qué ciudad reclama |
| **Cómo se abre** | rápido y se cierra esa noche · lento y se sostiene · gratis y tarda cuatro turnos |
| **Dónde va la escolta** | carga de alimentos · carrotanques de combustible · misión médica |
| **Dónde van las tres duplas** de la Defensoría | verificar la denuncia grave · acompañar la operación · medir un punto que nadie ha mirado |
| **Qué se declara infraestructura crítica** | evitar un daño irreversible · no inmovilizar la fuerza que abre caminos |
| **Cuánta evidencia se exige** antes de tratar un punto como violencia organizada | actuar tarde · actuar sobre población civil |

> **Una dupla** es una pareja de funcionarios de la Defensoría del Pueblo que va
> al terreno a constatar qué está pasando en un punto, un hospital o un sitio de
> detención. Van de a dos porque protege a los verificadores y porque dos
> testigos producen una constancia mucho más difícil de desestimar. Es el término
> que usa el Manual de Roles y es la práctica institucional real. **La Defensoría
> tiene tres, y con ellas tiene que cubrir diez puntos.**

**Ninguna de estas seis decisiones tiene una respuesta que un participante pueda
deducir solo.** Y todas salen mejor si los nueve hablaron antes — que es
exactamente lo que se quiere entrenar.

---

## 2. El mundo: qué se modela y hasta dónde

### 2.1 Tres niveles, porque las decisiones se toman en tres niveles

El ejercicio anterior —una inundación— tenía una sola unidad de territorio: la
manzana. Aquí hacen falta tres, **porque los nueve roles no deciden sobre lo
mismo**.

| Nivel | Qué es | Cuántos | Quién decide sobre él |
| --- | --- | ---: | --- |
| **Punto de cierre** | Un bloqueo concreto, con nombre y ubicación | **11** | La Policía (dónde va la fuerza) · Interior y el Alcalde (con quién se habla) |
| **Corredor** | Una secuencia ordenada de puntos entre un origen y un destino | **4** | Transporte (cuál se prioriza) · Defensa (cuál se opera) |
| **Región** | Un departamento o área metropolitana | **4** | Minas (dónde va el combustible) · Interior (dónde se concerta) |

Un mismo hecho se lee distinto en cada nivel, y eso es lo que produce
conversación: **abrir un punto** es una operación; **abrir un corredor** es una
campaña; **salvar una región** es una cadena que cruza cuatro carteras.

### 2.2 El punto de cierre — la unidad mínima

Es un bloqueo concreto: un peaje, una glorieta, la entrada de una refinería, un
puente. Cada uno tiene seis cosas que se pueden estimar y **una que no se ve
nunca**.

**Lo que se estima:**

- **Qué tan duro es.** Cuánto cuesta abrirlo por la fuerza. Un peaje con
  retroexcavadoras cruzadas y quince días de trincheras no es lo mismo que una
  calle con tres carpas.
- **Cuánto deja pasar.** Un punto no está abierto o cerrado: deja pasar una
  fracción del tráfico normal. Puede dejar pasar ambulancias y no camiones.
- **Cuánta gente hay.** Cambia entre el día y la noche, y crece cuando sube la
  movilización.
- **Cuánto lo respalda el barrio.** Es lo que determina si el cierre se sostiene
  solo. Cuando el barrio se cansa —porque lleva días sin abastecimiento— el
  cierre se deshace sin que nadie lo desaloje.
- **Con quién se puede hablar**, y sobre todo **cuánto controla esa persona**.
- **Cuántos días lleva.** Los cierres viejos están consolidados; los nuevos no.

**Lo que no se ve nunca:**

Cada punto tiene una mezcla real de tres cosas: **gente que protesta
legítimamente, gente que aprovecha para delinquir, y estructura organizada con
financiación y mando.** Esa mezcla no aparece en ninguna pantalla, ni en la del
Presidente, ni en la de quien opera la consola. Se revela en el debriefing.

> **Es lo que hace que la pregunta «¿esto es protesta o es otra cosa?» tenga
> contenido.** Si el sistema repartiera la respuesta, no habría nada que decidir.
> Lo único que existe son cuatro lecturas parciales que se equivocan en
> direcciones distintas — y tres duplas para resolver la duda en tres puntos de
> once.

**La trampa de con quién se habla.** Lo que se logra abrir por concertación es
proporcional a cuánto controla realmente el vocero con quien se pactó. Negociar
con alguien que controla la mitad del punto produce una apertura a media máquina
que se anuncia como éxito y **se desmiente sola en veinticuatro horas**. Y el
escenario reparte los puntos a propósito: **los cierres fáciles de pactar son
blandos, y los duros son justamente aquellos donde no hay con quién hablar.**

### 2.3 Por qué diez puntos y no mil

En el paro real había más de mil puntos de cierre activos. **Mil no caben en una
deliberación de nueve personas.**

Se modelan los **once que deciden un corredor**: los que tienen nombre,
ubicación, contraparte propia y consecuencia si se abren. No son una muestra
representativa — **son los que importan**.

> **Eran veinticuatro.** Con cinco decisiones, veinticuatro producían un tablero
> que ninguna sala recorría entera: se tocaban ocho o nueve y los quince
> restantes eran decorado con nombre propio, ocupando sitio en el mapa y en la
> cuenta de «puntos sin verificar» sin que nadie fuera a mirarlos nunca. **Un
> punto que ninguna sala va a tocar no añade dificultad: añade ruido.**
>
> Y **cinco de los diez están en la ciudad epicentro**, cinco fuera. Esa
> proporción es la tensión territorial del caso —lo que se ve por la ventana
> contra lo que solo existe en el tablero— y con veinticuatro se diluía. Uno de
> los seis, además, no pertenece a ningún corredor: abrirlo por la fuerza no
> compra un solo día de autonomía a nadie.
>
> Que once sea el número correcto no está medido. Es la apuesta contraria a la
> anterior, y la primera corrida con gente la mide (**C1** de
> [`PENDIENTES.md`](../PENDIENTES.md)).

El resto entra como **presión de fondo por región**: un número agregado que crece
cuando sube la movilización y decrece cuando baja, y que la sala no gestiona uno
por uno. Es lo que impide que el ejercicio se sienta pequeño sin volverlo
inmanejable.

**Y el número puede crecer.** Si la movilización sube lo suficiente, **aparecen
puntos nuevos** que antes no existían — cierres espontáneos, sin vocería
reconocida, en sitios donde no había nada. Es la forma más visible del bucle
central del caso:

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

> **Abrir un camino por la fuerza puede cerrar dos.** Y no está escrito en ningún
> guion: sale de la aritmética. La sala no puede discutirlo — solo verlo ocurrir.
>
> Los números de ese bucle están en
> [`COMO_FUNCIONA.md` §4](COMO_FUNCIONA.md#4-el-adversario-reflexivo).

### 2.4 El corredor — y por qué vale lo que su peor punto

Un corredor es una **secuencia ordenada de puntos entre un origen y un destino**:
la ciudad y el puerto, la refinería y los centros de acopio, el anillo de
hospitales.

Lo que pasa por él está limitado por su punto más cerrado. Un camión que
atraviesa tres bloqueos y se queda en el cuarto **no llegó**.

Tres consecuencias que la sala descubre en momentos distintos:

**Abrir un punto no es abrir un corredor.** Hay que sostener todos sus puntos a
la vez. Con cinco turnos y con lo que se abre por la fuerza cerrándose de noche,
**la fuerza casi nunca alcanza a sostener un corredor entero.** Es el resultado
más contraintuitivo del ejercicio.

**No todos los corredores sirven para lo mismo.** Cada uno tiene sus clases:
combustible, alimentario, humanitario, general. El corredor hospitalario es
*solo* humanitario; el de la refinería es *solo* combustible. Por eso «abrir un
corredor» no es una frase genérica: **importa cuál**, y el que salva a Las
Cumbres no es el que alimenta al epicentro.

**Un corredor abierto solo sirve a las regiones que toca.** Uno abierto en Alto
Verde no abastece a Puerto Espejo. Sin ese filtro, abrir cualquier cosa salvaba a
todo el país y priorizar dejaba de significar nada.

### 2.5 La región — donde vive el reloj

Cuatro regiones. Cada una lleva **días de autonomía** de tres cosas: combustible,
alimentos y oxígeno medicinal.

**Bajan solas y solo suben si alguien abre un corredor que sirva a esa región.**
A diferencia de la lluvia del ejercicio anterior, el reloj no es un dato de
guion: es la consecuencia acumulada de lo que la sala hizo y dejó de hacer.

**El oxígeno es el único que convierte logística en muertes**, y no es una
variable independiente sino el extremo de una cadena:

```
camino abierto → entra combustible → hay diésel para los carrotanques
                                   → y para las plantas de emergencia del hospital
                                   → las plantas sostienen la producción y el frío
                                   → hay oxígeno en la UCI
                                   → no se muere quien no tenía que morirse
```

**Cortar la cadena en cualquier punto la rompe entera.** Por eso el oxígeno no
modela salud: modela **el alcance de una decisión logística**. Y por eso ninguna
cartera lo resuelve sola — hacen falta cuatro: Minas prioriza el suministro,
Transporte le da clase humanitaria al corredor, la Policía escolta el
carrotanque, la Defensoría lo exige como derecho.

**Y hay una regla de diseño que hay que hacer cumplir a la fuerza:** toda región
debe tener **al menos una vía viable** de atender su oxígeno. Si una región no
tiene ningún corredor humanitario que la sirva, sus muertes son inevitables haga
lo que haga la sala — y eso no es un dilema, **es un guion que castiga**.

### 2.6 La fuerza — un inventario, no un número

La capacidad de contención se modela como **cuarenta escuadrones**, cada uno con
tres cosas: dónde está, qué está haciendo, y cuán cansado está.

**Seis estados posibles**, y solo dos cuentan como disponibles:

| Estado | Qué significa | ¿Disponible? |
|---|---|---|
| Reserva | Sin comprometer | **sí** |
| Contención | Sosteniendo un punto sin operar | **sí, pero sacarlo lo descubre** |
| Operación | Abriendo un punto ahora | no |
| Escolta | Acompañando una caravana o misión médica | no |
| Custodia | Protegiendo una instalación crítica | no |
| Relevo | Descansando | no |

**En t=0 hay 34 desplegados y 6 en reserva.** La sala no hereda una fuerza
fresca: hereda una fuerza cansada.

**El cansancio es el principal factor de error**, y esto es lo que lo convierte
en una decisión y no en un dato: sube con cada turno desplegado, baja solo en
relevo, y **relevar significa aceptar menos cobertura hoy para bajar la
probabilidad de una catástrofe mañana.**

**Tres tipos de unidad, con riesgos muy distintos.** El ESMAD está entrenado y
equipado para control de multitudes; la policía regular no —no es su función—; y
la tropa militar es **tropa de combate**, varias veces más peligrosa en una
multitud que cualquiera de las otras dos. Usar militares además requiere una
firma que solo el Presidente puede dar.

> **Decisión de alcance:** no se modelan agentes individuales. La unidad mínima
> es el escuadrón. Los «veinte mil policías y treinta mil militares menos» del
> caso real entran como una **restricción sobre el total disponible**, no como un
> conteo de personas.

### 2.7 El tiempo — cinco días en turnos de doce horas

El ejercicio cubre **cinco jornadas**, del 11 al 15 de mayo, en turnos de doce
horas que alternan día y noche.

| | **Turno de día** | **Interludio de noche** |
|---|---|---|
| Deliberación | sí | **no** |
| Órdenes nuevas | sí | **no** |
| Mesa de diálogo | disponible | no |
| Gente en los puntos | más | menos, pero más dura |
| Riesgo de que algo salga mal | normal | **multiplicado por 1,6** |
| Reaperturas | — | **ocurren aquí** |

**La noche no se delibera: se sufre.** La sala mira cómo un camino abierto por la
fuerza vuelve a cerrarse, cómo entra un titular, cómo baja el reloj, sin poder
intervenir. **La pérdida de control se representa quitándoles el turno.**

Y no elimina la decisión nocturna: de día se puede *ordenar* operar de noche, y
se resuelve en el interludio con el riesgo multiplicado.

> **Consecuencia de alcance que hay que aceptar:** con cinco turnos de decisión,
> **toda mecánica que tarde tres turnos en rendir es inviable.** Por eso la
> concertación tarda dos y no tres, y por eso constituir la mesa temprano vale
> mucho más que en un diseño de diez turnos.

### 2.8 Lo que no se modela, y por qué

Esto importa tanto como lo anterior. **La regla que gobierna el alcance:**

> **Se modela lo que una decisión de la sala puede tocar.** Si ningún rol puede
> actuar sobre algo, ese algo es contexto y no variable.

| Lo que queda fuera | Por qué |
|---|---|
| **Personas individuales** | No hay manifestantes ni agentes con nombre. Los únicos individuos del ejercicio son los nueve de la mesa |
| **Geografía a escala** | No hay kilómetros ni tiempos de desplazamiento. Un punto pertenece a un corredor y a una región, y eso basta para decidir. *Sí hay un mapa —§3.2— de un país inventado, y sitúa sin medir* |
| **El proceso judicial** | La judicialización aparece como *cuán sólido es un caso*, no como un sistema con fiscales y jueces |
| **La economía** | Solo el costo diario de cada corredor cerrado y un índice de precios. No hay inflación, empleo ni mercados |
| **La salud, más allá del oxígeno** | No se modela la pandemia, ni camas de UCI, ni vacunación. El oxígeno está porque convierte logística en muertes; lo demás no tocaría ninguna decisión |
| **Otras instituciones del Estado** | No hay Fiscalía ni jueces como agentes. El Congreso existe como una posibilidad que Interior puede invocar, no como actor |
| **El resto del país** | Las demás ciudades existen como **voces en la esfera pública**, no como territorio gestionable |
| **Un rol de «la protesta»** | La movilización es un adversario del motor, no una persona en la mesa: el ejercicio es sobre la coordinación del Estado, y sentar a alguien a jugar la protesta lo convertiría en otra cosa |

**Y algo que sí está y conviene nombrar:** la esfera pública —prensa nacional e
internacional, redes sociales, gremios, el Comité del Paro, los alcaldes de
entorno— produce **contenido y solo contenido**. Reacciona a lo que la sala hizo
y lo narra desde su sesgo. **Nunca decide nada**: no abre un corredor, no provoca
un incidente, no cambia una cifra. El sistema ya calculó lo que pasó; ellos lo
cuentan.

### 2.9 Qué es azar y qué no

Importa para que la sala confíe en el ejercicio, y para el debriefing.

**Se calcula, no se sortea:**

- El riesgo de que una operación termine mal — **y se muestra antes de decidir**
- Cuánto abre una concertación
- Cómo avanza el reloj de abastecimiento
- Qué corredor abastece a qué región
- Cuánto se endurece un punto y cuánta gente hay en él

**Se sortea:**

- Si el incidente efectivamente ocurre, contra la probabilidad que se mostró
- Cuántas víctimas hay
- Si la imagen circula
- Si un punto abierto por la fuerza reabre esta noche
- Si un cierre desgastado finalmente se levanta

**Y la semilla queda registrada**, así que la corrida entera se puede repetir en
el debriefing **con una sola decisión cambiada**. Es la mejor herramienta que
este diseño ofrece para cerrar el ejercicio.

> **El azar nunca decide si algo era buena idea.** Decide si esta vez salió mal.
> La probabilidad se muestra antes, como banda —baja, media, alta, crítica—, para
> que la sala gestione riesgo y no sorpresa. *«Hicimos todo bien y salió mal»* es
> una lección real y difícil de recibir, y conviene decirlo en el turno 0.

### 2.10 Las tres capas de conocimiento

Todo lo anterior existe en el sistema. **Lo que llega a las personas pasa por
tres filtros:**

```
CAPA 1 · LO QUE PASA          El estado real del país. Solo el sistema.
                              No se muestra jamás — se revela en el debriefing.
                                        ↓  filtrado por competencia y sesgo
CAPA 2 · LO QUE EL ESTADO VE  El tablero general (grano grueso, para todos)
                              + nueve vistas privadas (grano fino, cada uno la suya)
                                        ↓  solo pasa lo que alguien AFIRMA en público
CAPA 3 · LO QUE SE DICE       Prensa, redes, gremios, comunidad internacional.
                              Puede contradecir a las dos anteriores, y lo hace.
```

**Compartir dentro de la capa 2 es hablar**, y no requiere ningún mecanismo: si
Minas dice cuántos días quedan, los otros siete lo oyeron. El sistema no lleva la
contabilidad de quién le dijo qué a quién, **y el dato no se escribe en el
tablero** (§1.3).

**Pasar de la capa 2 a la capa 3 sí es un acto con consecuencia**, porque lo que
se afirma en público después se contrasta con lo que resultó cierto — y la
distancia se paga en legitimidad, con descuento si el dato salió clasificado como
confirmado, estimado o en verificación.

---

## 3. El tablero general

**Aquí vive la simulación.** Es lo que la sala mira para seguir el ejercicio, y
tiene que bastar para jugar. Se proyecta para todos.

### 3.1 Los cinco indicadores del país

| Indicador | Qué significa en la sala | Arranca |
|---|---|---|
| **Presión en la calle** | Cuánta movilización hay. Sube con la fuerza mal usada; baja con acuerdos que se cumplen | alta |
| **Legitimidad** | El respaldo ciudadano a la respuesta del Estado | deteriorada |
| **Credibilidad de la mesa** | Si el canal de diálogo sirve para algo | deteriorada |
| **Respaldo internacional** | Cuánto margen queda antes de que el mundo se pronuncie | deteriorado |
| **Cohesión del PMU** | Si estos nueve actúan como uno o como nueve | **alta** |

**Tres se heredan dañadas y una no.** La sala no rompió las tres primeras y no
puede culpar a nadie presente: hereda un pasivo. **La cohesión empieza alta y es
enteramente suya** — todo lo que le pase entre el turno 1 y el 5 lo hicieron los
nueve. En el debriefing es la única serie de la que no pueden desentenderse.

**Cada indicador tiene un umbral duro**, no un deterioro suave: cuando la
legitimidad cae lo suficiente los gremios camioneros evalúan sumarse al paro, y
si cae más se suman y el bloqueo pasa a ser cierre logístico nacional. Cuando cae
la credibilidad de la mesa, el Comité del Paro suspende, y si cae más no vuelve a
sentarse. **Un deterioro gradual no produce decisiones; un umbral sí.**

> Los valores de arranque y los seis umbrales exactos están en
> [`COMO_FUNCIONA.md` §9](COMO_FUNCIONA.md#9-la-mesa-reservas-banderas-y-acuerdos).

### 3.2 El mapa — un país inventado, en dos niveles

Aunque el ejercicio no modela geografía a escala, **sí conviene una
representación visual del territorio**: es lo que convierte una tabla de estados
en algo que nueve personas pueden señalar con el dedo mientras discuten.

**La topología es la información**: un corredor *es* una secuencia ordenada de
puntos entre un origen y un destino, igual que una línea de metro es una
secuencia ordenada de estaciones.

**La primera versión fue un esquema de líneas puro, y se quedó corta por una
razón que no se ve hasta proyectarlo**: diez motas sobre un lienzo vacío, sin
costa, sin puerto y sin forma, no son un país. Una sala que mira eso durante
trece minutos no llega a preguntarse dónde está, y la tensión territorial del
caso no aparece por ninguna parte.

La versión que quedó dibuja **Valcanto**, un país inventado, con dos mares, un
puerto, una frontera terrestre, un estuario que parte la ciudad epicentro, y
cuatro regiones que lo cubren entero.

**La silueta y la red vial son reales** —una costa de verdad y sus carreteras
principales, de datos cartográficos abiertos, sin que quede registrado en
ninguna parte cuál es— porque un país dibujado a mano se nota: las costas tienen
estuarios, cabos y entrantes, y las redes viales tienen troncales que concentran
y comarcales que rodean. Nadie inventa eso por intuición. Es el mismo trato que
Macondo tuvo con Mocoa: **lo prestado es el trazo, no el lugar.**

> **Las carreteras van casi transparentes, y eso es el diseño.** No son la
> información: son el suelo sobre el que se lee la información. Tienen que estar
> —un bloqueo flotando sobre un polígono de color no se lee como una carretera
> cortada— y tienen que callarse. Lo que resalta son los corredores y los puntos.
>
> Y **cada corredor va por el camino que existe**, ruteado sobre esa red. Antes
> se unían sus puntos con una curva suave, y la curva afirmaba algo falso: que
> entre un bloqueo y el siguiente la vía pasa por ahí. Dos puntos que en línea
> recta parecen vecinos pueden estar a media vuelta por carretera — y eso, en un
> caso sobre logística, es exactamente lo que hay que ver.
>
> **Los diez puntos están sobre vértices reales de la red.** Un bloqueo está en
> una carretera, no en un descampado.

| | Qué muestra | Para qué |
|---|---|---|
| **Nivel país** | las cuatro regiones teñidas de su **estado de bloqueo**, la costa, el puerto y la mancha de la ciudad epicentro | dónde está el problema, de un vistazo desde el fondo de la sala |
| **Nivel región** | sus puntos con nombre y los corredores que la cruzan | qué decidir, cuando la mesa ya sabe dónde mirar |

```
  ┌─ REGIÓN DE BELLAFLOR ─────────────────────  abastecimiento ▲ ÁMBAR ─┐
  │                                                                      │
  │  CIUDAD — PUERTO       ○───○───●───○      2,4 M · combustible,       │
  │                        P1  P2  P3  P4            alimentos, humanit. │
  │                                ↑                                     │
  │                    un punto cerrado = el corredor entero no pasa     │
  │                                                                      │
  │  CORREDOR HOSPITALARIO ◐───◐───◐          900 mil · humanitario      │
  │                        P10 P11 P12                                   │
  └──────────────────────────────────────────────────────────────────────┘

  ┌─ LAS CUMBRES ─────────────────────────────  abastecimiento ▲ ROJO ──┐
  │                                                                      │
  │  CORREDOR DEL SUR      ○───?───?───○───○   1,65 M · alimentos,       │
  │                        P5  P6  P7  P8  P9         humanitario        │
  │                            ↑   ↑                                     │
  │                    nadie los ha mirado desde el turno 1              │
  └──────────────────────────────────────────────────────────────────────┘

     ○ abierto      ◐ parcial      ● cerrado      ? sin verificar
```

**Tres cosas que el mapa hace y una tabla no:**

**Enseña sin palabras la mecánica central del caso.** *«Un corredor vale lo que
su peor punto»* deja de ser una regla que hay que explicar: se ve.

**Hace visibles los huecos.** Un punto marcado `?` proyectado en la pared es una
petición de decisión con destinatario: hay alguien en la mesa que puede
resolverlo gastando una dupla, y todos lo están viendo.

**Da algo que señalar.** Nueve personas discutiendo sobre «el corredor al puerto»
sin nada delante es una conversación abstracta. Con el mapa proyectado, la
discusión pasa a ser sobre P3 — que es la conversación correcta.

#### El mismo mapa, nueve niveles de detalle

**No hace falta un mapa por rol, sino el mismo mapa con distinta resolución.** Es
la traducción visual del principio de §1.1.

| Quién lo mira | Qué ve encima |
|---|---|
| **Todos** (tablero) | Estado de cada punto, líneas y regiones con su semáforo |
| **Transporte** | Cuánto cuesta cada corredor por día y cuánta población depende de él |
| **Minas** | Los días exactos de cada región, y hacia dónde van mañana |
| **Policía** | Dónde está cada escuadrón, cuán cansado, y a qué punto alcanza a llegar |
| **Defensoría** | Cuándo se verificó cada punto por última vez y qué se constató |
| **Alcalde** | Su jurisdicción ampliada: con quién se puede hablar en cada punto |
| **Interior** | Dónde hay vocería reconocida y cuánto controla — *con su sesgo* |
| **Defensa** | Dónde señala financiación su inteligencia — *con su sesgo* |

#### Tres guardarraíles

**No hay distancias, ni escala, ni tiempos de desplazamiento.** Si alguien
pregunta «¿cuánto se tarda de P3 a P7?», el mapa está prometiendo algo que el
modelo no tiene. La geometría **sitúa, no mide**: lo único que afirma es en qué
región está cada bloqueo.

**El mapa no muestra lo que el tablero no muestra.** Ni la mezcla real de un
punto, ni si una denuncia es cierta. Vale la regla de §3.5 sin excepciones.

**Las cuatro regiones teselan el país.** Cada una es un trozo del contorno más
una frontera interior, y **cada frontera se simplifica UNA sola vez y se usa dos
veces**, en sentidos opuestos: no hay huecos ni solapes por construcción, y hay
una prueba que lo comprueba muestreando el país entero.

> Simplificar cada polígono por su cuenta no vale, y costó una pasada
> descubrirlo: la costa de Bellaflor y la costa del país quedaban a un cuarto de
> unidad la una de la otra, y entre las dos aparecía una cuchilla de tierra que
> no pertenecía a ninguna región. Medido: 265 muestras de tierra huérfanas. Un
> hueco es un trozo de país que el mapa pinta sin color y del que la ficha no
> sabe decir nada.

**El agua de dentro se rellena para repartir y se dibuja aparte.** El estuario es
un agujero dentro de la tierra, y un agujero rompe la teselación: el contorno lo
encierra pero ninguna región lo cubre. Se rellena para el reparto —así
`dentro()` sigue siendo una prueba de rayo sobre un polígono simple— y se pinta
encima con el color del mar. El estrecho se sigue viendo, que es lo que hace de
esa ciudad un cuello de botella.

> **Es barato.** La topología ya existe en los datos: cada corredor lista sus
> puntos en orden, y cada punto sabe a qué región pertenece. **No requiere
> ninguna lógica nueva en el motor:** es una vista sobre datos que ya están.
>
> Lo que el mapa señala turno a turno —las seis lecturas, los anillos de lo que
> cambió anoche— está en
> [`COMO_FUNCIONA.md` §3](COMO_FUNCIONA.md#3-las-cuatro-superficies-en-tres-rutas).

### 3.3 Las regiones, la fuerza y la esfera pública

**Las cuatro regiones.** Un semáforo de abastecimiento —verde, ámbar, rojo—
**sin números**, y el contador de muertes evitables, que solo crece y no se
compensa con nada. **Los días exactos los tiene Minas.** Antes de que los diga,
la mesa sabe que hay un problema y no sabe cuánto tiempo tiene.

**La fuerza disponible.** Cuántos escuadrones quedan sin comprometer, sobre el
total: **6 de 40**. Dónde está cada uno y cuán agotados están es la vista del
Director de la Policía.

**La esfera pública.** Titulares, redes, pronunciamientos internacionales,
posición de los gremios. Y **las cifras que circulan, juntas**, cuando hay más de
una.

> **Dos superficies y no una.** El tablero muestra lo que el Estado tiene por
> cierto; la esfera pública muestra lo que se dice. **La distancia entre las dos
> es el caso**, y solo se percibe si se ven a la vez. Nunca en pestañas — por eso
> la esfera vive dentro del tablero y no tiene ruta propia.

### 3.5 Lo que el tablero nunca muestra

- **La mezcla real de ningún punto.** Se revela en el debriefing.
- **Si una denuncia sin verificar es cierta o falsa.**
- **El detalle fino de ninguna cartera** — ni siquiera después de que su titular
  lo diga en voz alta.

---

## 4. Las nueve vistas privadas

### 4.1 El principio

Cada vista tiene **tres bloques y nada más**. Cabe en una pantalla sin
desplazamiento y se lee en menos de un minuto.

| | Qué es | Para qué sirve |
|---|---|---|
| **Su alerta** | Una línea: qué señala su detalle como más urgente **ahora** | Es lo que pone sobre la mesa, y compite con las otras siete alertas |
| **Su detalle** | Tres o cuatro datos de su cartera, con la resolución que nadie más tiene | Le da algo concreto que aportar en cada turno |
| **Su repertorio** | Qué puede pedir hoy, y si no puede, qué falta y quién lo habilita | Empuja la petición a la mesa en voz alta |

**Las nueve alertas de cada turno no caben en la capacidad disponible.** Ese es
el diseño: nueve personas con nueve urgencias legítimas y una escolta.

> **Las nueve vistas, con sus alertas medidas de un turno real, están en
> [`COMO_FUNCIONA.md` §11](COMO_FUNCIONA.md#11-las-nueve-vistas-privadas-por-dentro).**
> Se pueden ver todas de golpe con
> `uv run python scripts/correr_ejercicio.py --vistas`, que es la forma más
> rápida de entender el diseño entero.

### 4.2 Cuando dos roles miran lo mismo

Esta es la pieza que hace que compartir valga la pena, y la regla que la produce:

| El mismo hecho | Lo ve así… | Y así… | Quién lo resuelve |
|---|---|---|---|
| Cuánta estructura organizada hay en un punto | **Defensa**: más de la que hay | **Alcalde**: menos | la Defensoría, si gasta una dupla ahí |
| Lo mismo, pero en un punto **rural** | **Defensa**: 0,33–0,42 | **Agricultura**: 0,00–0,14 | la Defensoría · y ahí lo real es 0,04–0,12 |
| Cuánto controla el vocero con quien se negocia | **Interior**: más | **Alcalde**: bien, pero solo en su ciudad | hablando entre ellos |
| Cuántas víctimas hubo | **Policía**: menos | **Alcalde**: más | la Defensoría, si verificó |
| Cuánto tiempo queda | **Minas**: exacto | *nadie más lo sabe* | Minas, al decirlo |

**Ninguno miente.** Cada uno mira desde donde está parado, con la cobertura y los
incentivos de su institución. Y esa es la lección: la guerra de cifras del caso
real no fue —solo— mala fe; fue cinco instituciones con cinco coberturas.

> **La segunda fila es incómoda a propósito.** En el campo la estructura armada
> real es baja y **el que se equivoca de largo es el frente de seguridad**. El
> Ministro de Agricultura lo sabe porque trata con esas organizaciones, y no
> tiene con qué demostrarlo: la única lectura sin sesgo es la de una dupla, y
> hay tres por jornada. Su exposición no es equivocarse en general — es el punto
> concreto donde sí se equivoca, y sentarse ahí le reconoce interlocución a
> quien sostiene el cierre con otra cosa.

> **Regla de diseño:** cuando dos roles ven el mismo hecho, sus sesgos van en
> **direcciones opuestas**. Si fueran en la misma, compartir no aportaría nada y
> la vista privada sería decoración.

---

## 5. Las acciones

### 5.1 Cuántas, y por qué no son iguales

**Treinta y nueve acciones, entre cuatro y cinco por rol.** El Presidente tiene
cinco porque decide más: es el único con instrumentos excepcionales y con
potestad sobre la propia mesa. La Defensoría también, porque es el único rol que
cruza dos ejes —el estándar de empleo de la fuerza y el protocolo de
información— sin mandar sobre nadie. Y el Ministro de Agricultura, por la razón
contraria: **ninguna de las suyas se ejecuta sin la concurrencia de otro**, así
que necesita margen para elegir por dónde entrar.

| Tipo | Qué cambia | Se ve en el tablero |
|---|---|---|
| **Protocolo** | cómo trabaja la mesa: quién habla, quién firma, con qué reglas · rinde en todo lo que venga después | no |
| **Operación** | el territorio, la fuerza, el abastecimiento | de inmediato |
| **Información** | lo que el país tiene por cierto | en la esfera pública |

| Rol | Acciones | Protocolo | Operación | Información |
| --- | ---: | :---: | :---: | :---: |
| Presidente | **5** | 2 | 2 | 1 |
| Ministro del Interior | **4** | 1 | 2 | 1 |
| Alcalde de la ciudad epicentro | **4** | 1 | 2 | 1 |
| Ministro de Defensa | **4** | 1 | 2 | 1 |
| Director de Policía | **4** | 1 | **3** | **—** |
| Delegado de la Defensoría | **5** | 2 | 2 | 1 |
| Ministro de Transporte | **4** | 1 | 2 | 1 |
| Ministro de Minas | **4** | 1 | 2 | 1 |
| Ministro de Agricultura | **5** | 1 | **3** | 1 |

> **La Policía es la excepción, y está anotada como pendiente de decisión.** Es
> el único rol sin acción informativa. O se corrige la regla —«cada rol tiene al
> menos una de cada clase»— o se añade la acción, y eso lo decide el equipo
> docente. Está en
> [`LAS_ACCIONES.md`](LAS_ACCIONES.md#1--la-policía-no-tiene-acción-informativa).

> **Las treinta y nueve, en lenguaje corriente y sin una sola cifra, están en
> [`GUIA_DE_ACCIONES.md`](GUIA_DE_ACCIONES.md)** — cómo se llama cada una, qué
> hace, qué hace falta antes y la frase que la pide. Es la misma guía que cada
> titular tiene en su tablero, con las nueve carteras a la vez, y se genera desde
> el código.
>
> **Las mismas treinta y nueve con los números —qué escribe cada una en el
> estado y cuánto cobra— están en [`LAS_ACCIONES.md`](LAS_ACCIONES.md)**, que es
> el documento del equipo docente.

### 5.2 Las seis que la Matriz define y no entran

**La Matriz Operativa define cinco por rol, cuarenta en total.** Se dejan fuera
seis, y cada omisión tiene su razón:

| Acción de la Matriz | Por qué no entra |
|---|---|
| Policía A4 · individualizar casos para judicialización | La propia Matriz lo dice: *«es lento frente al ritmo de la crisis y no produce efecto visible dentro de la ventana de decisión de esta semana»* |
| Defensa A5 · proyección aérea al epicentro | Es una modalidad del redespliegue, no una decisión distinta. Entra como opción dentro de él |
| Interior A5 · convocar alcaldes no representados | Se solapa con la convocatoria del Presidente a los alcaldes de ciudades críticas |
| Alcalde A5 · exigir prioridad con atribución escrita | Es lo que hace hablando en la deliberación. No necesita ser una acción |
| Defensoría A5 · pronunciamiento público | **Sí entra**, reformulada: es su acción de manifestar que su permanencia está en cuestión |
| Transporte A4 · instancia técnica única | Se solapa con su criterio de priorización |
| Minas A5 · acuerdo de continuidad con las empresas | No tiene efecto dentro de cinco turnos |

### 5.3 Quién habilita a quién

Cinco dependencias duras. Cuando falta el requisito, el sistema no rechaza:
**dice quién puede habilitarlo**, y eso devuelve la conversación a la mesa.

```
Transporte quiere mover carga          → necesita ESCOLTA de la Policía
Interior quiere pactar en el epicentro → necesita al ALCALDE
Defensa quiere usar militares          → necesita la FIRMA del Presidente
Minas quiere proteger instalaciones    → CONSUME los escuadrones del desbloqueo
La Defensoría acompaña una operación   → esa dupla NO verifica nada más ese turno
Agricultura quiere despachar comida    → necesita una ESCOLTA ya puesta, y que
                                         el corredor lleve CLASE ALIMENTARIA
```

> **Ninguna de las cinco acciones de Agricultura abre un camino por sí sola**, y
> es la única cartera de la que eso es cierto entera. No tiene fuerza ni
> corredores: cada cosa que hace pasa por lo que otro despeja, prioriza o
> acompaña. Es el rol que más empuja la conversación de vuelta a la mesa.

Y cuatro sumas cero, cada una enfrentando dos criterios legítimos:

| Recurso escaso | Un criterio | El otro |
|---|---|---|
| **Escuadrones** | Minas: evitar el daño irreversible | Defensa: abrir caminos |
| **Corredores** | Transporte: el criterio técnico | Alcalde: la urgencia de su ciudad |
| **Duplas** | verificar lo que pasó | acompañar lo que va a pasar |
| **Combustible** | misión médica y fuerza pública | alimentos y consumo general |
| **La ventana escoltada** | Transporte: carga general | Agricultura: perecederos e insumos pecuarios |
| **El canal con el territorio** | Interior: interlocutor único y pliego | Agricultura: mesa técnica rural y tránsito de carga |

**No hay orden correcto.** Hay un orden que alguien tiene que defender ante siete
personas que pierden algo — y eso es lo que se está entrenando.

---

## 6. Cómo se juega un turno

### 6.1 Quién opera la consola

**No hay moderador como figura aparte del ejercicio.** Hay una **consola** —una
superficie más, junto al tablero y las nueve vistas— y alguien la opera.

**Quién la opera queda abierto**, y las dos formas funcionan:

- **Alguien externo**, en una pantalla independiente, que solo transcribe. Deja a
  los nueve libres para deliberar.
- **Un participante designado**, que además de su rol tiene acceso a la vista de
  órdenes. El Presidente es el candidato natural, porque el registro escrito de
  decisiones es competencia suya.

Su función es una sola: **traducir a órdenes lo que la mesa deliberó**. No
conduce, no reparte información, no decide el ritmo, **y no sabe nada que los
demás no sepan**.

Tres consecuencias de diseño, y las tres mejoran el ejercicio:

**La información reservada la reparte el sistema, no una persona.** Es
precisamente lo que hacen las nueve vistas privadas. Sin ellas haría falta alguien
repartiendo sobres — y ese alguien sabría lo que hay en todos.

**El ritmo lo lleva el sistema.** El reloj de cada tramo es visible para toda la
sala y suena solo. No lo administra el criterio de nadie, que siempre concede «un
minuto más».

**El parte lo muestra la pantalla.** Al abrir cada turno el tablero dice qué
cambió y qué se rompió. Cualquiera puede leerlo en voz alta; nadie tiene que
prepararlo.

### 6.2 La jornada: dos tramos, no siete fases

```
DÍA     13 min   Se leen los tableros y se delibera. LA CONSOLA ACEPTA ÓRDENES
                 EN CUALQUIER MOMENTO: se dictan de una en una y se acumulan.
                 Cada plan vuelve CON SU BANDA DE RIESGO antes de confirmarse.

NOCHE    2 min   El motor resuelve el día y pasa la noche. Se miran las
                 consecuencias y se interpretan. NO SE RECIBEN ÓRDENES.
```

**Había siete fases y ahora hay dos.** Las siete describían bien la coreografía
de una sala ideal y mal la de una sala real: obligaban a saber en qué minuto se
estaba antes de poder decir nada, y la única frontera que cambia lo que se puede
hacer —¿se ordena o no se ordena?— quedaba escondida entre otras seis.

**Cinco jornadas de decisión**, más turno 0 y debriefing: dos horas exactas.

**El paso que devuelve el plan es el mejor punto pedagógico del montaje**, y no
depende de nadie. La pantalla contesta:

> *«Se ordena operar el punto Loma del Oriente con ESMAD, de noche. Riesgo de
> incidente: **alto**, 32 %. Mitigadores ausentes: los seis. Responsable: sin
> nominar.»*

La sala lee eso junta, y **con frecuencia cambia la orden**. Que salga de la
pantalla y no de una persona lo hace incluso más difícil de discutir.

**El turno 0.** Fichas y agendas reservadas en papel, el parte heredado en
pantalla, y **60 segundos por rol** para declarar dónde se ubica —fuerza,
negociación o secuencia— y qué condición lo movería de posición. El sistema lo
registra. **La distancia entre esa línea y la que de hecho se ejecutó es la
métrica principal del debriefing.**

**Al cerrar la última jornada**, el sistema corre tres turnos más sin nadie al
mando y proyecta el estado a 72 horas. No es un marcador: **es el país que la
sala entrega**, y es la pregunta con la que conviene abrir el debriefing —
*¿esto se sostiene sin ustedes?*

### 6.3 Las cinco reglas que impiden que la sala mire pantallas

El hallazgo del primer ejercicio fue exactamente este: **una pantalla por
participante produce nueve personas mirando nueve pantallas y ninguna mirando a las
otras siete.** Estas cinco reglas son la condición de que el diseño funcione.

**1 · La vista privada cabe en una pantalla y no tiene desplazamiento.** Tres
bloques, tres o cuatro datos. Si hay que hacer scroll, está mal diseñada.

**2 · Las pantallas se congelan durante la deliberación.** Nada cambia mientras
la gente habla, así que no hay ninguna razón para volver a mirarlas.

**3 · Nadie ordena desde su pantalla.** Las vistas son de solo lectura. Las
órdenes entran por la consola y se leen de vuelta antes de ejecutarse. **La
pantalla informa; la mesa decide.**

**4 · Papel para lo que no cambia.** La ficha de rol y la agenda reservada se
entregan impresas. A pantalla va solo lo que se mueve turno a turno.

**5 · El tablero general no repite lo que está en una vista privada.** Si un dato
está en los dos, la vista privada sobra y el participante aprende a ignorarla.

> **Prueba para la primera corrida:** si en el minuto 4 de la deliberación
> alguien está mirando su pantalla, una de estas cinco se rompió.

---

## 7. Los dilemas que esto garantiza

Un dilema que depende de que los participantes lo descubran no es un dilema del
diseño: es suerte. **Estos ocho dilemas tienen que aparecer en toda corrida.**

**D1 · La fuerza que abre un camino le resta credibilidad a la mesa que negocia
el siguiente.** El Ministro del Interior ve caer su reserva por decisiones que no
tomó.

**D2 · Cada corredor priorizado es un corredor aplazado, y el aplazamiento tiene
nombre de ciudad.** El criterio técnico de Transporte y la urgencia del Alcalde
no pueden satisfacerse a la vez.

**D3 · La verdad es un recurso escaso: tres duplas para diez puntos.** Verificar
aquí es no verificar allá, y el error tiene dos direcciones, ambas caras.

**D4 · El estándar de derechos es la única palanca que baja el riesgo sin
consumir capacidad.** Es el dilema *positivo*: el rol sin voto y sin fuerza es el
que más reduce la probabilidad del peor resultado.

**D5 · Entregar el reloj cambia el reloj.** El calendario de Minas es a la vez lo
que obliga a la mesa a decidir y lo que acelera aquello que mide.

**D6 · Concentrar hace responsable de cada error; delegar deja sin control sobre
la coherencia.** Sin decisión escrita con responsable nominado, el costo de cada
incidente se reparte sobre los nueve.

**D7 · Nueve urgencias legítimas y una escolta.** Cada turno, las nueve alertas
privadas apuntan a sitios distintos y todas tienen razón. No hay criterio
superior que las ordene: hay una mesa que tiene que elegir.

**D8 · Dos personas honestas, el mismo hecho, dos números.** Desde dentro de
ninguna de las dos vistas se puede saber cuál es correcto. La salida es hablar, y
si no basta, gastar una dupla que entonces no hace otra cosa.

> **La forma general del caso:** las nueve posiciones son defendibles y ninguna es
> suficiente. **Si en el debriefing una opción resulta haber sido obviamente
> correcta desde el turno 1, el ejercicio está mal calibrado.**

---

## 8. Las decisiones del equipo

### 8.1 Resueltas

| # | Decisión | Resolución |
|---|---|---|
| **V1** | ¿La vista privada es un dispositivo por persona o papel impreso? | **Un dispositivo por rol**, desde su propio computador. Sujeto a las cinco reglas de §6.3 |
| **V3** | ¿Se puede afirmar un dato distinto del que se ve? | **No.** Con agendas reservadas ya hay tensión suficiente, y permitir el dato falso convierte esto en un juego de engaño en vez de uno de criterios en conflicto |
| **V4** | ¿El detalle de las vistas puede pasar al tablero general? | **No.** Las cifras se comparten hablando y los jugadores pueden anotarlas donde quieran, pero **el dato vive en la vista de su rol y no migra** |
| **V5** | ¿Cuántas acciones? | **39**, entre cuatro y cinco por rol |
| **V6** | ¿Las duplas de verificación y el acompañamiento salen del mismo presupuesto? | **Sí, un solo bolsillo de tres.** Cada dupla hace una sola cosa por turno. Es lo que convierte la asignación de la Defensoría en una decisión real |
| **A1** | ¿Nombres reales o ficticios? | **Ficticios.** El país entero: Valcanto, sus dos mares, sus cuatro regiones y sus diez puntos. Protege de convertir el ejercicio en un juicio sobre hechos con responsabilidad judicial viva, y permite dibujar un mapa de verdad (§3.2) |
| **A2** | ¿Se puntúa? ¿Las agendas suman? | **No hay marcador.** Las agendas reservadas se revelan al final, no se puntúan |
| **A3** | ¿La Defensoría puede retirarse? | **No se retira** — pero puede **manifestar públicamente que su permanencia está en cuestión**, y eso cuesta legitimidad y respaldo internacional |
| **A5** | ¿Los hechos que abren el turno 1 son fijos o se sortean? | **Fijos, siempre.** Permite comparar salas entre sí |
| **A6** | ¿Se acepta el azar? | **Sí, con semilla fija.** La semilla no es un elemento visible de la interfaz |

**A3 merece una nota, porque tiene consecuencia de diseño.** La acción A1 de la
ficha de la Defensoría es literalmente *«condicionar su permanencia»*, y una
amenaza que el diseño nunca deja consumar no sería una palanca. La sustitución
—**decir en voz alta que se lo está pensando**— es mejor que el retiro por tres
razones: **se puede usar varias veces** a lo largo del ejercicio en vez de una
sola; **es graduada**, así que la mesa puede responder y él puede escalar; y
**nunca saca sus mitigadores del juego**, que era el problema de dejarlo marchar
de verdad. Además es lo que hacen los defensores del pueblo reales: no se van,
emiten pronunciamientos.

### 8.2 Lo que sigue abierto

Está todo en [`PENDIENTES.md`](../PENDIENTES.md) · Parte 3, que es donde se lleva
la cuenta. En resumen: cuántos dispositivos, quién opera la consola, si la
primera corrida va con llave de API o sin ella, el contenido exacto de las nueve
vistas, si se cierra el territorio ficticio, si el mapa muestra dónde está la
fuerza, y si la consola puede decir qué punto bloquea un corredor.

### 8.3 El territorio ficticio — juego provisional

**Nombres de trabajo, para poder avanzar.** No están cerrados: son un marcador de
posición que se puede sustituir entero sin tocar nada del diseño, porque el motor
identifica los puntos por código y no por nombre.

| Nombre | Qué papel cumple |
|---|---|
| **Bellaflor** | La ciudad epicentro: donde está el alcalde de la mesa, y donde la crisis es más aguda |
| **Región de Bellaflor** | La región central. Concentra la mayor parte de los puntos de cierre |
| **Puerto Espejo** | La región portuaria. Por ahí entra el combustible del país |
| **Las Cumbres** | Región montañosa del sur. **El reloj de oxígeno más apretado** |
| **Alto Verde** | Región del sur, agrícola y con presencia de comunidades organizadas |

**Los cuatro corredores:**

| Nombre | Qué conecta |
|---|---|
| **Bellaflor – Puerto Espejo** | La ciudad con el puerto. Combustible, alimentos y humanitario. Cuatro puntos, tres de ellos en la ciudad: es el más largo y el más poblado |
| **Refinería – Acopios** | De la refinería a los centros de distribución. **Solo combustible**, y su primer punto es donde ocurrió H1 |
| **Corredor hospitalario** | Del hospital de Bellaflor hacia Las Cumbres. **Solo humanitario** — es el que decide el reloj de oxígeno más apretado |
| **Corredor del Sur** | Las Cumbres y Alto Verde. Alimentos y humanitario. **Ninguno de sus dos puntos está en la ciudad**: es el corredor que la sala olvida |

> **Eran cinco.** El Corredor Norte se retiró con la bajada a diez puntos: sus
> cuatro puntos no decidían nada que los otros no decidieran ya, y una salida más
> de la ciudad diluía la única distinción territorial que importa —lo que está en
> la ciudad epicentro contra lo que no.

> **El criterio, para cuando se cierren de verdad:** que **no sean alias
> transparentes**. La convención heredada de la simulación anterior —Macondo
> sobre Mocoa— es un nombre que **declara su propia ficción** y que aun así
> permite reconocer la estructura del caso.
>
> Y una nota de operación: **la correspondencia entre lo ficticio y lo real es
> información del equipo docente, no del material de los participantes.** En las
> fichas y en las pantallas solo aparecen los nombres inventados.

---

## Glosario

Términos propios del caso, en orden de aparición en el ejercicio.

**PMU · Puesto de Mando Unificado.** La instancia donde los nueve se sientan. En
el caso real, la mesa de coordinación de la respuesta del Estado a la crisis.

**Punto de cierre** *(o «punto»)*. Un bloqueo concreto con nombre y ubicación: un
peaje, una glorieta, un puente, la entrada de una refinería. Se modelan once de
los más de mil que hubo, y seis de ellos están en la ciudad epicentro.

**Corredor.** Una secuencia ordenada de puntos entre un origen y un destino. Vale
lo que su peor punto: un camión que atraviesa tres bloqueos y se queda en el
cuarto no llegó.

**Clase de corredor.** Para qué sirve: combustible, alimentario, humanitario,
general. Un corredor puede tener varias, y el que salva a una región no es
necesariamente el que alimenta a otra.

**Días de autonomía.** Cuánto le queda a una región de combustible, alimentos u
oxígeno medicinal. Bajan solos; solo suben si se abre un corredor que sirva a esa
región.

**Escuadrón.** La unidad mínima de fuerza. Hay 40, y cada uno está en un sitio,
haciendo algo, y cansado en algún grado.

**ESMAD.** El Escuadrón Móvil Antidisturbios: la única unidad del Estado
entrenada y equipada para control de multitudes. Por eso es el activo más escaso
del ejercicio.

**Asistencia militar.** La figura de la Ley 1801 de 2016 que permite emplear
capacidad militar en orden público interno. **Requiere la firma del Presidente**,
y su costo depende enteramente de si se firma con límites —territorio, plazo,
reglas escritas, criterio de terminación— o sin ellos.

**Dupla.** Una pareja de funcionarios de la Defensoría del Pueblo que va al
terreno a constatar qué está pasando. Van de a dos porque protege a los
verificadores y porque dos testigos producen una constancia difícil de
desestimar. **Hay tres**, y con ellas hay que cubrir diez puntos.

**Mitigador.** Una decisión que baja la probabilidad de que una operación termine
mal **sin consumir capacidad**: reglas de empleo escritas, identificación de los
agentes, registro audiovisual, una dupla presente, concertación con la alcaldía,
unidades descansadas. Los seis juntos dividen el riesgo por casi cinco.

**Banda de riesgo.** Cómo se le muestra a la sala la probabilidad de que una
operación termine mal, **antes de ordenarla**: baja, media, alta o crítica. Sirve
para que la sala gestione riesgo y no sorpresa.

**Vocería · control de vocería.** Quién habla por un punto de cierre, y sobre
todo **cuánto de ese punto controla realmente**. Lo que se logra abrir por
concertación es proporcional a ese control — pactar con quien controla la mitad
abre la mitad.

**Apoyo local.** Cuánto respalda el barrio al cierre. Cuando cae —porque la gente
lleva días sin abastecimiento— el cierre se deshace sin que nadie lo desaloje.

**Concertación · desgaste · fuerza.** Las tres vías de abrir un camino. La fuerza
es rápida y se cierra esa misma noche; la concertación tarda dos turnos y se
sostiene; el desgaste tarda cuatro o más, no reabre y no cuesta nada.

**Reapertura.** Que un punto abierto por la fuerza vuelva a cerrarse. Ocurre de
noche, y es lo que hace que la fuerza casi nunca alcance a sostener un corredor
entero en cinco turnos.

**Acción de protocolo** *(constitutiva, en el motor)*. Una que no abre ningún camino, no aparece en el tablero
y **modifica todo lo que venga después**: poner las decisiones por escrito, fijar
el estándar de empleo de la fuerza, acordar quién habla. Ninguna es obligatoria y
todas están tarifadas.

**Interludio nocturno.** Los dos minutos entre dos jornadas de decisión. No se
delibera ni se ordena: se resuelve lo que se ordenó de día y la sala mira.

**Proyección a 72 horas.** Al cerrar la última jornada, el sistema corre tres
turnos más sin nadie al mando. No es un marcador: es el país que la sala entrega.

**Mapa.** La representación visual del territorio, en dos niveles: el país
—Valcanto, inventado— con sus cuatro regiones teñidas de su estado de bloqueo, y
la región ampliada con sus puntos y sus corredores. Muestra relaciones —qué punto
pertenece a qué corredor y a qué región— y deliberadamente **no** muestra
distancias, porque el modelo no las tiene.

**Semilla.** El número que fija el azar de una corrida, de modo que se pueda
repetir exactamente igual. Queda registrada y **no es un elemento visible de la
interfaz**; se usa en el debriefing para volver a correr la jornada con una
decisión cambiada.

---

*Derivado del Manual de Roles con RADs (8 roles) y de la Matriz Operativa del
GovLab, y del diagnóstico del motor anterior recogido en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).*

*Escuela de Gobierno · Universidad de La Sabana.*
