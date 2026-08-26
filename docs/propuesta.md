# Propuesta v2 — El ejercicio como decisión compartida

**Qué cambia:** cada rol ve su propia cartera **con más resolución que nadie**.
No para guardarse nada, sino para que su criterio pese en decisiones que no
tienen respuesta obvia.

**Alcance:** el modo de juego y el modelo del mundo. Qué se simula y hasta dónde,
qué ve cada uno, qué puede hacer, y cómo eso afecta a los demás. **No propone
código** — eso viene después, cuando el modo de juego esté cerrado.

**Versión:** 2.1 · incorpora las decisiones del equipo sobre vistas, consola y
alcance de lo compartido

> Los términos propios del caso —punto de cierre, corredor, dupla, escuadrón,
> mitigador— se explican al usarlos por primera vez, y están todos reunidos en el
> [glosario](#glosario) al final.

---

## La idea, en una escena

Turno 2. Hay **una escolta disponible** y tres corredores la piden. Los ocho
tienen la misma pantalla común delante y todos están diciendo la verdad:

> **Transporte:** *«El Corredor Norte mueve los alimentos de 780 mil personas.
> Llevo el costo diario y es el más caro de todos.»*
>
> **Minas:** *«El Anillo Hospitalario es el único camino humanitario que sirve a
> Cauca, y Cauca tiene oxígeno para menos de dos días.»*
>
> **Policía:** *«El punto que bloquea el corredor al puerto es el más caliente
> del país. Si no se atiende hoy, mañana no es un punto: son tres.»*
>
> **Alcalde de Cali:** *«Ese puerto es el que alimenta a mi ciudad, y llevo nueve
> días con el comercio paralizado.»*
>
> **Defensoría:** *«En ese punto hay una denuncia grave que no he podido
> verificar. Operar ahí antes de verificarla es el peor escenario posible.»*

**Cinco criterios legítimos, una escolta, ninguna respuesta correcta.** Nadie
ocultó nada, nadie mintió, y la decisión sigue siendo difícil — porque lo es.

> **Eso es lo que la vista privada existe para producir.** No un juego de
> secretos: **una deliberación donde cada uno aporta el pedazo del país que
> solo él ve con nitidez, y donde el desacuerdo sobrevive a la transparencia.**

---

## Los cuatro cambios respecto de la versión actual

| | Cambio | Por qué |
|---|---|---|
| **1** | **Cada rol tiene una vista privada** con su cartera en alta resolución, en su propio dispositivo | Para que su criterio tenga peso propio y las decisiones tengan más consideraciones |
| **2** | **El tablero general lleva el grueso de la información** | La simulación se sigue desde ahí. La vista privada es un complemento fino, no un sustituto |
| **3** | **Entre 4 y 5 acciones por rol**, no todas iguales | El Presidente decide más que el Ministro de Minas. Lo que importa es que ninguno se quede corto y que todas sirvan para manejar la crisis |
| **4** | **No hay moderador como figura aparte** | Quien opera la consola puede ser un participante. El sistema conduce el turno |

---

## ¿Va esto contra el input del GovLab?

Se revisó el *Manual de Roles con RADs* y la *Matriz Operativa*. **No, y en dos
puntos esta versión completa algo que el propio GovLab ya había dejado
planteado.**

**Sobre la transparencia entre roles.** El Manual enmarca el ejercicio así:
*«Ninguno puede resolver la crisis desde su frente: el resultado depende de una
línea y de un diseño que solo existen si esta mesa los acuerda.»* Los apartados
10 de cada ficha —«actores con los que puede entrar en conflicto»— describen
**fricciones institucionales entre mandatos legítimos**, no antagonismo personal:
Minas contra Defensa por la fuerza que la custodia inmoviliza, Transporte contra
el Alcalde por el orden de los corredores. Son exactamente las tensiones que
sobreviven a la transparencia total. **Alineado.**

**Sobre las agendas reservadas.** El Manual sí guarda algo: *«el apartado 11
contiene información reservada del rol: describe lo que ese actor persigue y no
declara en la mesa. Se juega, no se enuncia.»* No hay contradicción, y la
distinción es la que ordena esta versión:

> **Transparencia sobre los hechos. Reserva sobre los motivos.**
>
> Los datos se comparten. Lo que cada uno persigue con ellos, no. Y así es más
> interesante: **los ocho pueden estar de acuerdo en los hechos y seguir sin
> estar de acuerdo en qué hacer** — porque sus objetivos son distintos, no porque
> alguien esconda un número.

**Sobre el moderador.** El Manual elimina al Director del DAPRE con este
argumento: *«sus funciones de secretaría técnica, tablero de situación, ciclo de
actualización y bitácora de decisiones las ejecuta el motor de simulación»*. Y
más adelante: *«el concepto militar de viabilidad se entrega como documento
inyectado por el simulador, no como agente»*. **El GovLab ya había decidido que
la conducción del ejercicio es del sistema.** Quitar al moderador como figura
aparte no contradice el input: lo lleva hasta el final.

**Sobre el número de acciones.** El Manual dice: *«cada rol queda descrito con
exactamente cinco recursos, cinco acciones y cinco efectos»*. Aquí sí hay una
desviación consciente: se implementan entre 4 y 5 por rol, no 5 exactas, porque
con cinco turnos algunas no alcanzan a rendir. **Cada omisión se justifica una
por una en la sección 5.**

---

## Índice

1. [El principio: resolución, no secreto](#1-el-principio-resolución-no-secreto)
2. [El mundo: qué se modela y hasta dónde](#2-el-mundo-qué-se-modela-y-hasta-dónde)
3. [El tablero general](#3-el-tablero-general)
4. [Las ocho vistas privadas](#4-las-ocho-vistas-privadas)
5. [Las acciones](#5-las-acciones)
6. [Cómo se juega un turno](#6-cómo-se-juega-un-turno)
7. [Los dilemas que esto garantiza](#7-los-dilemas-que-esto-garantiza)
8. [Las decisiones del equipo](#8-las-decisiones-del-equipo)
9. [Qué le pide esto al motor](#9-qué-le-pide-esto-al-motor)
· [Glosario](#glosario)

---

## 1. El principio: resolución, no secreto

### 1.1 La misma foto, distinta nitidez

**Nadie tiene información que los demás no puedan pedir.** Lo que cada uno tiene
es **su cartera en alta resolución**, y el resto del país en grano grueso.

```
EL TABLERO GENERAL dice:      Cauca · abastecimiento ● ROJO

LA VISTA DE MINAS dice:       Cauca
                                oxígeno       1,8 días  ↓ 0,4 sin ingreso mañana
                                combustible   2,8 días
                                alimentos     2,5 días
```

La mesa entera sabe que Cauca está mal. **Solo Minas sabe cuánto tiempo queda**,
y hasta que lo diga la sala no puede ponerle fecha a nada. No es un secreto: es
que nadie más tiene ese instrumento.

Lo mismo con los demás. El tablero dice que el corredor al puerto está cerrado;
Transporte sabe **cuál de sus cuatro puntos** lo bloquea. El tablero dice que hay
6 escuadrones libres; la Policía sabe **cuán cansados están y cuánto tardan en
llegar**. El tablero muestra las cifras que circulan; la Defensoría sabe **cuál
de las denuncias alcanzó a verificar y cuál no**.

> **La regla que ordena todo el reparto:**
>
> El tablero general responde **qué está pasando**.
> La vista privada responde **cuánto, dónde exactamente, y desde cuándo**.

### 1.2 Personal, no confidencial

Una precisión importante sobre qué significa «privada».

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

Esto es deliberado y tiene una consecuencia que vale la pena entender:

> **Consultar a un rol una vez no lo agota.** Si Minas dijo en el turno 2 que
> quedaban 1,8 días, en el turno 3 ese número cambió — y sigue siendo el único
> que tiene el nuevo. La mesa tiene que volver a preguntarle. **Cada turno, cada
> rol vuelve a ser necesario.**

Si el dato se fijara en el tablero, el rol se consultaría una vez y después
sobraría. Es exactamente lo que se quiere evitar.

**Hablar es gratis; hacerlo oficial tiene consecuencia.** Decir *«nos quedan como
dos días»* en la deliberación no cuesta nada. **Entregar formalmente el calendario
de agotamiento** —que es una acción— sí: queda en el registro, obliga a la mesa a
decidir con plazo, y se filtra hacia afuera, donde produce compra por pánico y
acelera el agotamiento que mide. Lo mismo con la cifra oficial: contar en voz alta
es gratis; publicar el parte y sostenerlo es un acto que después se contrasta con
la verdad.

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
> tiene tres, y con ellas tiene que cubrir veinticuatro puntos.**

**Ninguna de estas seis decisiones tiene una respuesta que un participante pueda
deducir solo.** Y todas salen mejor si los ocho hablaron antes — que es
exactamente lo que se quiere entrenar.

---

## 2. El mundo: qué se modela y hasta dónde

Esta sección describe **de qué está hecho el país** dentro del ejercicio. Es la
parte que hay que cerrar antes de construir nada, porque define qué puede tocar
una decisión y qué es solo contexto.

### 2.1 Tres niveles, porque las decisiones se toman en tres niveles

El ejercicio anterior —una inundación— tenía una sola unidad de territorio: la
manzana. Aquí hacen falta tres, **porque los ocho roles no deciden sobre lo
mismo**.

| Nivel | Qué es | Cuántos | Quién decide sobre él |
| --- | --- | ---: | --- |
| **Punto de cierre** | Un bloqueo concreto, con nombre y ubicación | **24** | La Policía (dónde va la fuerza) · Interior y el Alcalde (con quién se habla) |
| **Corredor** | Una secuencia ordenada de puntos entre un origen y un destino | **5** | Transporte (cuál se prioriza) · Defensa (cuál se opera) |
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
> veinticuatro.

**La trampa de con quién se habla.** Lo que se logra abrir por concertación es
proporcional a cuánto controla realmente el vocero con quien se pactó. Negociar
con alguien que controla la mitad del punto produce una apertura a media máquina
que se anuncia como éxito y **se desmiente sola en veinticuatro horas**. Y el
escenario reparte los puntos a propósito: **los cierres fáciles de pactar son
blandos, y los duros son justamente aquellos donde no hay con quién hablar.**

### 2.3 Por qué 24 puntos y no mil

En el paro real había más de mil puntos de cierre activos. **Mil no caben en una
deliberación de ocho personas.**

Se modelan los **veinticuatro que deciden un corredor**: los que tienen nombre,
ubicación, contraparte propia y consecuencia si se abren. No son una muestra
representativa — **son los que importan**.

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

### 2.4 El corredor — y por qué vale lo que su peor punto

Un corredor es una **secuencia ordenada de puntos entre un origen y un destino**:
la ciudad y el puerto, la refinería y los centros de acopio, el anillo de
hospitales.

Lo que pasa por él está limitado por su punto más cerrado. Un camión que atraviesa
tres bloqueos y se queda en el cuarto **no llegó**.

Tres consecuencias que la sala descubre en momentos distintos:

**Abrir un punto no es abrir un corredor.** Hay que sostener todos sus puntos a la
vez. Con cinco turnos y con lo que se abre por la fuerza cerrándose de noche,
**la fuerza casi nunca alcanza a sostener un corredor entero.** Es el resultado
más contraintuitivo del ejercicio.

**No todos los corredores sirven para lo mismo.** Cada uno tiene sus clases:
combustible, alimentario, humanitario, general. El anillo hospitalario es *solo*
humanitario; el de la refinería es *solo* combustible. Por eso «abrir un
corredor» no es una frase genérica: **importa cuál**, y el que salva a Cauca no
es el que alimenta a Cali.

**Un corredor abierto solo sirve a las regiones que toca.** Uno abierto en Nariño
no abastece a Buenaventura. Sin ese filtro, abrir cualquier cosa salvaba a todo el
país y priorizar dejaba de significar nada.

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

**En t=0 hay 34 desplegados y 6 en reserva.** La sala no hereda una fuerza fresca:
hereda una fuerza cansada.

**El cansancio es el principal factor de error**, y esto es lo que lo convierte en
una decisión y no en un dato: sube con cada turno desplegado, baja solo en relevo,
y **relevar significa aceptar menos cobertura hoy para bajar la probabilidad de
una catástrofe mañana.**

**Tres tipos de unidad, con riesgos muy distintos.** El ESMAD está entrenado y
equipado para control de multitudes; la policía regular no —no es su función—; y
la tropa militar es **tropa de combate**, varias veces más peligrosa en una
multitud que cualquiera de las otras dos. Usar militares además requiere una
firma que solo el Presidente puede dar.

> **Decisión de alcance:** no se modelan agentes individuales. La unidad mínima es
> el escuadrón. Los «veinte mil policías y treinta mil militares menos» del caso
> real entran como una **restricción sobre el total disponible**, no como un
> conteo de personas.

### 2.7 El tiempo — cinco días en turnos de doce horas

El ejercicio cubre **cinco jornadas**, del 11 al 15 de mayo, en turnos de doce
horas que alternan día y noche.

| | **Turno de día** | **Interludio de noche** |
|---|---|---|
| Deliberación | sí, 6 minutos | **no** |
| Órdenes nuevas | sí | **no** |
| Mesa de diálogo | disponible | no |
| Gente en los puntos | más | menos, pero más dura |
| Riesgo de que algo salga mal | normal | **multiplicado por 1,6** |
| Reaperturas | — | **ocurren aquí** |

**La noche no se delibera: se sufre.** La sala mira cómo un camino abierto por la
fuerza vuelve a cerrarse, cómo entra un titular, cómo baja el reloj. Tres
minutos, sin poder intervenir. **La pérdida de control se representa quitándoles
el turno.**

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
| **Personas individuales** | No hay manifestantes ni agentes con nombre. Los únicos individuos del ejercicio son los ocho de la mesa |
| **Geografía a escala** | No hay kilómetros ni tiempos de desplazamiento. Un punto pertenece a un corredor y a una región, y eso basta para decidir. *Sí hay una representación visual —un esquema de líneas, §3.2— pero es un diagrama de relaciones, no un mapa* |
| **El proceso judicial** | La judicialización aparece como *cuán sólido es un caso*, no como un sistema con fiscales y jueces |
| **La economía** | Solo el costo diario de cada corredor cerrado y un índice de precios. No hay inflación, empleo ni mercados |
| **La salud, más allá del oxígeno** | No se modela la pandemia, ni camas de UCI, ni vacunación. El oxígeno está porque convierte logística en muertes; lo demás no tocaría ninguna decisión |
| **Otras instituciones del Estado** | No hay Fiscalía ni jueces como agentes. El Congreso existe como una posibilidad que Interior puede invocar, no como actor |
| **El resto del país** | Bogotá, Medellín y las demás ciudades existen como **voces en la esfera pública**, no como territorio gestionable |

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
el debriefing **con una sola decisión cambiada**. Es la mejor herramienta que este
diseño ofrece para cerrar el ejercicio.

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
                              + ocho vistas privadas (grano fino, cada uno la suya)
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
| **Cohesión del PMU** | Si estos ocho actúan como uno o como ocho | **alta** |

**Tres se heredan dañadas y una no.** La sala no rompió las tres primeras y no
puede culpar a nadie presente: hereda un pasivo. **La cohesión empieza alta y es
enteramente suya** — todo lo que le pase entre el turno 1 y el 5 lo hicieron los
ocho. En el debriefing es la única serie de la que no pueden desentenderse.

**Cada indicador tiene un umbral duro**, no un deterioro suave: cuando la
legitimidad cae lo suficiente los gremios camioneros evalúan sumarse al paro, y
si cae más se suman y el bloqueo pasa a ser cierre logístico nacional. Cuando cae
la credibilidad de la mesa, el Comité del Paro suspende, y si cae más no vuelve a
sentarse. **Un deterioro gradual no produce decisiones; un umbral sí.**

> **Corrección de legibilidad respecto de la versión actual:** la exposición
> internacional estaba invertida —arriba era peor— y obligaba a explicar el
> tablero. Se le da la vuelta y pasa a ser **respaldo internacional**: las cuatro
> reservas se leen igual, y solo la presión en la calle va al revés, que es
> intuitivo porque es el adversario.

### 3.2 El mapa — un esquema, no un mapa real

Aunque el ejercicio no modela geografía a escala, **sí conviene una
representación visual del territorio**: es lo que convierte una tabla de estados
en algo que ocho personas pueden señalar con el dedo mientras discuten.

**La forma correcta es un esquema de líneas, no un mapa geográfico** — un plano
de metro antes que un mapa de carreteras. Y la razón no es estética: **es que el
modelo del mundo tiene exactamente esa forma.** Un corredor *es* una secuencia
ordenada de puntos entre un origen y un destino, igual que una línea de metro es
una secuencia ordenada de estaciones. **La topología es la información; la
geometría es decoración.**

```
  ┌─ REGIÓN CENTRAL ────────────────────────── abastecimiento ▲ ÁMBAR ─┐
  │                                                                     │
  │  CIUDAD — PUERTO       ○───○───●───○      2,4 M · combustible,      │
  │                        P1  P2  P3  P4            alimentos, humanit. │
  │                                ↑                                     │
  │                    un punto cerrado = el corredor entero no pasa     │
  │                                                                      │
  │  ANILLO HOSPITALARIO   ◐───◐───◐          900 mil · humanitario      │
  │                        P10 P11 P12                                   │
  └──────────────────────────────────────────────────────────────────────┘

  ┌─ REGIÓN DEL SUR ───────────────────────────  abastecimiento ▲ ROJO ─┐
  │                                                                      │
  │  CORREDOR SUR          ○───?───?───○───○   1,65 M · alimentos,       │
  │                        P5  P6  P7  P8  P9         humanitario        │
  │                            ↑   ↑                                     │
  │                    nadie los ha mirado desde el turno 1              │
  └──────────────────────────────────────────────────────────────────────┘

     ○ abierto      ◐ parcial      ● cerrado      ? sin verificar
```

**Tres cosas que el esquema hace y una tabla no:**

**Enseña sin palabras la mecánica central del caso.** *«Un corredor vale lo que su
peor punto»* deja de ser una regla que hay que explicar: se ve. Tres estaciones
verdes y una roja, y la línea entera está rota.

**Hace visibles los huecos.** Un punto marcado `?` proyectado en la pared es una
petición de decisión con destinatario: hay alguien en la mesa que puede
resolverlo gastando una dupla, y todos lo están viendo.

**Da algo que señalar.** Ocho personas discutiendo sobre «el corredor al puerto»
sin nada delante es una conversación abstracta. Con el esquema proyectado, la
discusión pasa a ser sobre P3 — que es la conversación correcta.

#### El mismo mapa, ocho niveles de detalle

Aquí está la mejor propiedad del esquema: **no hace falta un mapa por rol, sino
el mismo mapa con distinta resolución.** Es la traducción visual del principio de
§1.1.

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

**No hay distancias, ni escala, ni tiempos de desplazamiento.** El esquema debe
*parecer* esquemático precisamente para que nadie lea distancia en él. Si alguien
pregunta «¿cuánto se tarda de P3 a P17?», el mapa está prometiendo algo que el
modelo no tiene.

**El mapa no muestra lo que el tablero no muestra.** Ni la mezcla real de un
punto, ni si una denuncia es cierta. Vale la regla de §3.6 sin excepciones.

**Se congela durante la deliberación**, igual que todo lo demás.

#### Sobre la disposición espacial

El esquema puede organizarse **libremente pero con intuición**: un puerto al
extremo de una línea, un anillo cerrado alrededor de la ciudad, un corredor largo
bajando hacia el sur. Eso da orientación sin afirmar geografía.

Y con **nombres ficticios** (decisión A1) el esquema es la solución más honesta
disponible: un mapa real con nombres inventados sería una contradicción visible
—todo el mundo reconoce dónde queda Cali—, mientras que **un esquema inventado
con nombres inventados no finge ser nada.**

> **Es barato.** La topología ya existe en los datos: cada corredor lista sus
> puntos en orden, y cada punto sabe a qué región pertenece. Lo único que hace
> falta añadir es **una posición por punto en el diagrama** —veinticuatro pares de
> coordenadas, escritos una vez— y dibujar líneas y círculos. **No requiere
> ninguna lógica nueva en el motor:** es una vista sobre datos que ya están.

### 3.3 Las cuatro regiones

Un semáforo de abastecimiento por región —verde, ámbar, rojo— **sin números**, y
el contador de muertes evitables, que solo crece y no se compensa con nada.

**Los días exactos los tiene Minas.** Antes de que los diga, la mesa sabe que hay
un problema y no sabe cuánto tiempo tiene.

### 3.4 La fuerza disponible

Cuántos escuadrones quedan sin comprometer, sobre el total: **6 de 40**. Dónde
está cada uno y cuán agotados están es la vista del Director de la Policía.

### 3.5 La esfera pública

Titulares, redes, pronunciamientos internacionales, posición de los gremios. Y
**las cifras que circulan, juntas**, cuando hay más de una.

> **Dos superficies y no una.** El tablero muestra lo que el Estado tiene por
> cierto; la esfera pública muestra lo que se dice. **La distancia entre las dos
> es el caso**, y solo se percibe si se ven a la vez. Nunca en pestañas.

### 3.6 Lo que el tablero nunca muestra

- **La mezcla real de ningún punto.** Se revela en el debriefing.
- **Si una denuncia sin verificar es cierta o falsa.**
- **El detalle fino de ninguna cartera** — ni siquiera después de que su titular
  lo diga en voz alta.

---

## 4. Las ocho vistas privadas

### 4.1 El principio

Cada vista tiene **dos bloques y nada más**. Cabe en una pantalla sin
desplazamiento y se lee en menos de un minuto.

| | Qué es | Para qué sirve |
|---|---|---|
| **Su detalle** | Tres o cuatro datos de su cartera, con la resolución que nadie más tiene | Le da algo concreto que aportar en cada turno |
| **Su alerta** | Una línea: qué señala ese detalle como más urgente **ahora** | Es lo que pone sobre la mesa, y compite con las otras siete alertas |

**Las ocho alertas de cada turno no caben en la capacidad disponible.** Ese es el
diseño: ocho personas con ocho urgencias legítimas y una escolta.

### 4.2 Las ocho vistas

---

#### 01 · Presidente de la República

**Su detalle**

- **El pliego de decisiones**: qué se decidió cada turno, quién lo pidió y quién
  quedó como responsable. **Los renglones sin nombre aparecen marcados**
- **La temperatura de la coalición**: cuánta mano dura le exigen el Congreso y su
  partido
- **Su propia disponibilidad**: si las alertas de seguridad le permiten
  desplazarse al epicentro este turno
- **Las líneas que cada rol declaró al empezar** — es el único que las tiene
  delante

**Su alerta.** *«Tres de las cinco decisiones del turno pasado salieron sin
responsable nominado.»*

**Por qué importa.** Es el único que ve la contabilidad de la propia mesa. El
desorden del PMU aparece en su pantalla **antes de que produzca un daño**, y
puede corregirlo — que es literalmente la potestad que absorbió del DAPRE.

Y tiene el único instrumento puramente social del ejercicio: puede recordarle a
un ministro, en el turno 4, lo que declaró en el turno 0. No cuesta nada y puede
cambiar una decisión. Es lo que un jefe de Estado hace: **arbitrar sobre
información que no seleccionó**.

---

#### 02 · Ministro del Interior

**Su detalle**

- **El estado del canal**: si el Comité del Paro se sentaría hoy, qué pide y cuán
  fragmentado está
- **Con quién se puede hablar en cada punto**, y cuánto controla ese
  interlocutor — *su interlocutor le asegura que controla el punto entero;
  **lo sobreestima***
- **La viabilidad legislativa**: qué medida concreta podría ofrecer y si el
  Congreso respondería en plazo

**Su alerta.** *«Hay ventana para una sesión de mesa hoy. Si se opera antes de
las 6, no la hay.»*

**Por qué importa.** Es el único que puede decir si negociar es una opción real
hoy o una ilusión — y el único que puede traer una moneda que no es la fuerza.

Su lectura sesgada es la trampa central del caso: **cree que puede pactar un
punto entero cuando su interlocutor controla la mitad.** Si pacta con esa
creencia, el acuerdo se anuncia como éxito y se desmiente solo.

**Y ahí está la sinergia con el Alcalde**, que ve la vocería de su jurisdicción
bien. Si los dos comparan sus lecturas antes de negociar en Cali, el error se
evita. Los dos están diciendo la verdad; **solo que uno de los dos está mirando
desde más cerca**.

---

#### 03 · Alcalde de Cali

**Su detalle**

- **El parte municipal verificado**: hechos, víctimas y cierres de su ciudad, con
  detalle que nadie más tiene — *cuenta más víctimas civiles que el parte
  operacional*
- **Quién es quién en cada punto de su jurisdicción**: con qué liderazgo barrial
  se puede hablar de verdad
- **El abastecimiento barrio por barrio** y el estado de la red hospitalaria local
- *Subestima cuánta estructura organizada hay en sus puntos*

**Su alerta.** *«Dos barrios llevan cuatro días sin entrada de alimentos. El
apoyo al cierre está cayendo solo.»*

**Por qué importa.** Es el único que puede decir, punto por punto, **si hay
alguien con quien negociar**. Sin eso, la mesa ordena operaciones sobre puntos
donde había un acuerdo posible.

Y es el único que puede abrir un camino **sin consumir ninguna reserva**: su
esquema humanitario reduce el incentivo material del cierre sin alimentar la
movilización. Es lento y es gratis.

---

#### 04 · Ministro de Defensa

**Su detalle**

- **La capacidad real disponible**, y **qué frente rural queda descubierto** si
  mueve tropa a las ciudades
- **La inteligencia sobre financiación e infiltración** de cada punto — *ve casi
  el doble de estructura organizada de la que hay*
- **La solidez judicial de esa inteligencia**: cuántos de esos casos aguantarían
  ante un juez

**Su alerta.** *«Dos de los puntos que la mesa trata como protesta tienen
financiación documentada. Y uno de mis tres casos no se sostiene.»*

**Por qué importa.** Su lectura es el argumento más potente que existe para
escalar, **y la mesa tiende a creerle porque viene de inteligencia**. Que él mismo
vea la solidez judicial de sus propios casos es lo que le permite decir *«esto lo
sostengo»* y *«esto no»* — y esa distinción, hecha a tiempo, es lo que evita que
un caso caído en los estrados destruya la credibilidad de todos los demás.

**Su sesgo va en dirección contraria al del Alcalde.** Defensa ve estructura donde
hay protesta; el Alcalde ve protesta donde hay estructura. **Ninguno miente.** Si
los dos ponen sus números sobre la mesa, la verdad queda entre los dos y se
resuelve gastando una dupla. Si solo habla uno, la mesa decide con la mitad de la
foto.

---

#### 05 · Director General de la Policía Nacional

**Su detalle**

- **El parte operacional**: el estado de todos los puntos, con la cobertura más
  amplia de la mesa — *subestima las víctimas civiles*
- **Dónde está cada escuadrón, cuán cansado y cuánto tarda en llegar** a otro
  punto
- **Las denuncias contra sus unidades**, con su estado de verificación

**Su alerta.** *«Los escuadrones del anillo llevan cuatro turnos sin relevo. A
partir de aquí, la probabilidad de incidente sube sola.»*

**Por qué importa.** Es el que más ve, y **el único que puede convertir "hay 6
escuadrones libres" en "hay 2 que llegan a tiempo"** — que es una decisión
completamente distinta.

La fatiga es el dato más subestimado del ejercicio: no cuesta nada mirarlo y es
el principal factor de error. Y sus denuncias son el termómetro que dice si el
problema del sector es un incidente o un patrón.

---

#### 06 · Delegado de la Defensoría del Pueblo

**Su detalle**

- **La ventanilla de denuncias**: lo que llega de manifestantes, de ciudadanos
  afectados por los cierres y de uniformados heridos, con su estado de
  verificación. **Algunas son ciertas y otras no, y nada las distingue a simple
  vista**
- **Sus tres duplas**: dónde está cada una y qué constató
- **El contraste entre lo afirmado públicamente y lo verificado**

**Su alerta.** *«Dos denuncias graves sin verificar, en puntos distintos. Tengo
tres duplas y esta noche hay una operación que también las pide.»*

**Por qué importa.** Es la única fuente que casi no se equivoca, y la que menos
alcanza a ver. **Verificar aquí es no verificar allá**, y esa elección es suya
cada turno — lo que la convierte en un recurso que la mesa tiene que **asignar**,
no consultar.

**Las tres duplas salen del mismo bolsillo**, y esto es lo que hace dura su
decisión. Cada una puede hacer **una sola cosa por turno**:

- **verificar un punto** — medir qué hay realmente ahí
- **verificar una denuncia** — establecer si un hecho grave ocurrió o no
- **acompañar una operación** — su sola presencia baja el riesgo de que termine
  mal en un 25 %

Tres duplas, veinticuatro puntos, y una operación que también las pide. **No
puede hacer las tres cosas**, y ninguna de las tres es obviamente la correcta.

Y produce el dilema más limpio del ejercicio: cuando llegan dos denuncias graves
y solo alcanza a verificar una, **no hay forma de saber cuál primero**. La mejor
conducta disponible no es acertar: es verificar una y **declarar públicamente que
la otra está en verificación** — no afirmar lo que no se sabe.

---

#### 07 · Ministro de Transporte

**Su detalle**

- **El mapa vivo**: qué punto exacto bloquea cada corredor, y qué haría falta
  para abrirlo
- **El costo diario** de cada corredor cerrado y cuánta población depende de él
- **La posición de los gremios camioneros**: cuán cerca están de sumarse y qué
  piden para no hacerlo

**Su alerta.** *«El corredor al puerto depende de un solo punto. Abrir ese punto
abre 2,4 millones de personas.»*

**Por qué importa.** Sin él, la mesa discute «el corredor al puerto» como si
fuera una cosa. **Él sabe que son cuatro puntos, que tres están abiertos, y que
todo depende de uno.** Es la información que convierte una discusión política de
asignación en una secuencia defendible — y la que evita gastar una operación en
el punto equivocado.

Su alerta de gremios es una cuenta atrás que solo él ve: si un gremio se suma, el
bloqueo deja de ser un problema de orden público y pasa a ser **cierre logístico
nacional**.

---

#### 08 · Ministro de Minas y Energía

**Su detalle**

- **Los días de autonomía reales** por región: combustible, alimentos y oxígeno
  medicinal — y **hacia dónde van mañana**
- **Qué instalaciones son de verdad críticas**: dónde un incidente produce daño
  irreversible y no solo costo político
- **A qué se está destinando el combustible** hoy, y qué se le está quitando a qué

**Su alerta.** *«Cauca: 1,8 días de oxígeno. Si mañana no entra nada, 0,4.»*

**Por qué importa.** **Es quien tiene el reloj.** Mientras no lo diga, la mesa
sabe que hay un problema de abastecimiento y no sabe cuánto tiempo tiene. Y es el
único que puede explicar por qué el oxígeno no es un asunto sanitario sino
logístico — la cadena de §2.5.

> **El costo de su acción más importante.** Decir *«nos quedan como dos días»* es
> gratis. **Entregar formalmente el calendario** convierte el tiempo en variable
> dura y obliga a decidir — pero se filtra, hay compra por pánico, el consumo se
> acelera y el agotamiento llega antes. **Entregar el reloj cambia el reloj.** No
> es un dilema sobre si compartir: es que el instrumento que mide el problema
> también lo agrava.

---

### 4.3 Cuando dos roles miran lo mismo

| El mismo hecho | Lo ve así… | Y así… | Quién lo resuelve |
|---|---|---|---|
| Cuánta estructura organizada hay en un punto | **Defensa**: más de la que hay | **Alcalde**: menos | la Defensoría, si gasta una dupla ahí |
| Cuánto controla el vocero con quien se negocia | **Interior**: más | **Alcalde**: bien, pero solo en su ciudad | hablando entre ellos |
| Cuántas víctimas hubo | **Policía**: menos | **Alcalde**: más | la Defensoría, si verificó |
| Cuánto tiempo queda | **Minas**: exacto | *nadie más lo sabe* | Minas, al decirlo |

**Ninguno miente.** Cada uno mira desde donde está parado, con la cobertura y los
incentivos de su institución. Y esa es la lección: la guerra de cifras del caso
real no fue —solo— mala fe; fue cuatro instituciones con cuatro coberturas.

> **Regla de diseño:** cuando dos roles ven el mismo hecho, sus sesgos van en
> **direcciones opuestas**. Si fueran en la misma, compartir no aportaría nada y
> la vista privada sería decoración.

---

## 5. Las acciones

### 5.1 Cuántas, y por qué no son iguales

**Treinta y cuatro acciones, entre cuatro y cinco por rol.** El Presidente tiene
cinco porque decide más: es el único con instrumentos excepcionales y con
potestad sobre la propia mesa. La Defensoría también, porque es el único rol que
cruza dos ejes —el estándar de empleo de la fuerza y el protocolo de
información— sin mandar sobre nadie.

| Rol | Acciones | Constituye | Toca el mundo | Informa |
| --- | ---: | :---: | :---: | :---: |
| Presidente | **5** | 2 | 2 | 1 |
| Ministro del Interior | **4** | 1 | 2 | 1 |
| Alcalde de Cali | **4** | 1 | 2 | 1 |
| Ministro de Defensa | **4** | 1 | 2 | 1 |
| Director de Policía | **4** | 1 | 3 | — |
| Delegado de la Defensoría | **5** | 2 | 2 | 1 |
| Ministro de Transporte | **4** | 1 | 2 | 1 |
| Ministro de Minas | **4** | 1 | 2 | 1 |

**Cada rol tiene al menos una acción de cada clase**, que es lo que garantiza que
nadie pase el ejercicio sin nada que hacer:

| Clase | Qué cambia | Se ve en el tablero |
|---|---|---|
| **Constituye** | cómo funciona la mesa · rinde en todo lo que venga después | no |
| **Toca el mundo** | el territorio, la fuerza, el abastecimiento | de inmediato |
| **Informa** | lo que el país tiene por cierto | en la esfera pública |

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

### 5.2 Las treinta y cuatro

---

**PRESIDENTE DE LA REPÚBLICA · 5**

- *Constituye* — **Fijar el nodo único y el registro escrito.** Cada decisión
  queda con responsable nominado; el costo de un error cae sobre quien firmó y no
  sobre los ocho.
- *Constituye* — **Fijar las líneas rojas** del Ejecutivo y el marco de lo
  negociable. *Sin margen, cualquier acuerdo posterior será una capitulación.*
- *Toca el mundo* — **Firmar o negar la asistencia militar**, con delimitación
  territorial, plazo, reglas escritas y criterio de terminación — o sin ellos.
- *Toca el mundo* — **Convocar a los alcaldes de las ciudades críticas** para
  pactar reglas de empleo de la fuerza y de vocería.
- *Informa* — **Ir o no ir al epicentro**, y si acompaña una operación, una mesa,
  o ninguna. *Consume escolta y lo expone.*

**MINISTRO DEL INTERIOR · 4**

- *Constituye* — **Protocolo de vocería y plazo suspensivo de 24 h.** Ninguna
  operación con efecto sobre el diálogo se ejecuta sin que la mesa lo sepa antes.
- *Toca el mundo* — **Convocar la mesa nacional** con el Comité del Paro, con
  agenda acotada y excluyendo lo que el Presidente declaró línea roja.
- *Toca el mundo* — **Abrir mesas locales de concertación, corredor por
  corredor.** *En Cali requiere al Alcalde; en el resto del país no.*
- *Informa* — **Poner sobre la mesa la contraprestación legislativa** disponible
  y su plazo real.

> **Corrección importante.** Hoy la concertación es una acción del Alcalde de
> Cali sin límite de jurisdicción, y acaba pactando cierres en Cauca y Nariño.
> La Matriz asigna esa competencia a Interior. **Devolvérsela es el cambio que
> más reequilibra el ejercicio**, porque le da al polo de negociación algo que
> hacer.

**ALCALDE DE CALI · 4**

- *Constituye* — **Condicionar el empleo de la fuerza en su jurisdicción** a que
  los puntos y el mando local se concierten con la Alcaldía.
- *Toca el mundo* — **Instalar una mesa local con los voceros de un punto** de su
  ciudad, para acordar apertura por franjas horarias.
- *Toca el mundo* — **Activar el esquema humanitario municipal**: abastecimiento
  a barrios aislados, atención a heridos, ollas comunitarias. *La única vía que
  no consume ninguna reserva.*
- *Informa* — **Publicar el parte municipal verificado**, y disputar la cifra
  nacional si difiere.

**MINISTRO DE DEFENSA · 4**

- *Constituye* — **Fijar las reglas de empleo de la fuerza del sector**, con
  registro audiovisual obligatorio.
- *Toca el mundo* — **Ordenar una operación de desbloqueo**: punto, unidad,
  franja horaria y responsable nominado.
- *Toca el mundo* — **Redesplegar capacidad militar** a protección de
  infraestructura, o proyectarla por aire al epicentro. *Libera policías de la
  custodia y abre un frente rural desatendido.*
- *Informa* — **Presentar la evidencia de financiación e infiltración**, con su
  grado de solidez judicial.

**DIRECTOR GENERAL DE LA POLICÍA NACIONAL · 4**

- *Constituye* — **Clasificar el parte operacional** en confirmado, estimado y en
  verificación, y sostener esa clasificación frente a las cifras que circulan.
- *Toca el mundo* — **Disponer del ESMAD**: concentrarlo en puntos priorizados
  replegando la contención en el resto.
- *Toca el mundo* — **Escoltar** una caravana de carga, un carrotanque o una
  misión médica. *Sin esto no hay logística posible.*
- *Toca el mundo* — **Relevar unidades agotadas**, aceptando reducir la cobertura
  simultánea.

> **Corrección importante.** Hoy el dueño del ESMAD no puede asignarlo —los
> escuadrones se mueven solos cuando alguien ordena una operación— y no puede
> escoltar. **Sin escolta no hay caravana ni carrotanque**, así que todo el frente
> logístico queda hoy sin condición de posibilidad.

**DELEGADO DE LA DEFENSORÍA DEL PUEBLO · 5**

- *Constituye* — **Requerir formalmente el estándar de empleo de la fuerza**:
  reglas escritas, identificación de agentes, registro de actuaciones y ruta de
  atención a víctimas. *Si exige todo sin priorizar, la mesa lo aísla.*
- *Constituye* — **Asumir el protocolo único de verificación** de cifras y
  denuncias, a cambio de acceso a la información de los tres frentes.
- *Toca el mundo* — **Asignar sus tres duplas**: verificar un punto, verificar
  una denuncia, o acompañar una operación. *Cada dupla hace una sola cosa por
  turno.*
- *Toca el mundo* — **Requerir corredores humanitarios permanentes**, exigibles
  tanto al Estado como a quienes sostienen los cierres.
- *Informa* — **Manifestar públicamente que su permanencia está en cuestión.**
  No se retira —no puede—, pero deja constancia pública de que no está segura de
  poder seguir avalando con su presencia lo que la mesa decide.

> **Su palanca no es irse: es decir en voz alta que se lo está pensando.** El
> Delegado nunca abandona la mesa (decisión A3), pero puede **poner en duda
> públicamente su propia permanencia**, y eso cuesta: **legitimidad**, porque el
> Ministerio Público dudando de la respuesta del Estado es una señal que la
> opinión lee de inmediato, y **respaldo internacional**, porque los organismos
> que observan el caso miran su postura antes que la del Gobierno.
>
> **Y le cuesta a él.** Su credibilidad ante ambas partes es un activo que se
> consume con cada uso: la primera vez pesa, la tercera es ruido — y si el
> pronunciamiento se lee como denuncia general, el Gobierno le restringe el
> acceso y **pierde la única medida de su utilidad, que es la oportunidad**.
>
> Es mejor que la amenaza de retirarse por tres razones: **se puede usar varias
> veces** a lo largo del ejercicio en vez de una sola; **es graduada**, así que la
> mesa puede responder y él puede escalar; y **nunca saca sus mitigadores del
> juego**, que era el problema de dejarlo marchar de verdad. Además es lo que hacen
> los defensores del pueblo reales: no se van, emiten pronunciamientos.

**MINISTRO DE TRANSPORTE · 4**

- *Constituye* — **Adoptar el criterio único de priorización** de corredores: por
  población afectada, días de autonomía y costo diario.
- *Toca el mundo* — **Organizar una caravana** en un corredor priorizado, con
  conductores voluntarios y ventanas horarias. *Requiere escolta.*
- *Toca el mundo* — **Negociar con los gremios camioneros** condiciones
  verificables y compensación, para mantenerlos fuera del paro.
- *Informa* — **Publicar el mapa de cierres y anunciar aperturas solo como hecho
  verificado**, con criterio explícito de qué cuenta como corredor abierto.

**MINISTRO DE MINAS Y ENERGÍA · 4**

- *Constituye* — **Fijar el orden de prioridad del combustible** —misión médica,
  fuerza pública, transporte de alimentos, consumo general— como criterio
  permanente y no como decisión de cada turno.
- *Toca el mundo* — **Declarar infraestructura crítica**, con la inmovilización de
  fuerza que implica.
- *Toca el mundo* — **Acordar pasos seguros y ventanas de despacho** con
  transportadores y centros de acopio. *Supone reconocer de hecho una contraparte
  en el cierre.*
- *Informa* — **Entregar el calendario de agotamiento** por región.

---

### 5.3 Quién habilita a quién

Cinco dependencias duras. Cuando falta el requisito, el sistema no rechaza:
**dice quién puede habilitarlo**, y eso devuelve la conversación a la mesa.

```
Transporte quiere mover carga        → necesita ESCOLTA de la Policía
Interior quiere pactar en Cali       → necesita al ALCALDE
Defensa quiere usar militares        → necesita la FIRMA del Presidente
Minas quiere proteger instalaciones  → CONSUME los escuadrones del desbloqueo
La Defensoría acompaña una operación → esa dupla NO verifica nada más ese turno
```

Y cuatro sumas cero, cada una enfrentando dos criterios legítimos:

| Recurso escaso | Un criterio | El otro |
|---|---|---|
| **Escuadrones** | Minas: evitar el daño irreversible | Defensa: abrir caminos |
| **Corredores** | Transporte: el criterio técnico | Alcalde: la urgencia de su ciudad |
| **Duplas** | verificar lo que pasó | acompañar lo que va a pasar |
| **Combustible** | misión médica y fuerza pública | alimentos y consumo general |

**No hay orden correcto.** Hay un orden que alguien tiene que defender ante siete
personas que pierden algo — y eso es lo que se está entrenando.

---

## 6. Cómo se juega un turno

### 6.1 Quién opera la consola

**No hay moderador como figura aparte del ejercicio.** Hay una **consola** —una
superficie más, junto al tablero y las ocho vistas— y alguien la opera.

**Quién la opera queda abierto**, y las dos formas funcionan:

- **Alguien externo**, en una pantalla independiente, que solo transcribe. Deja a
  los ocho libres para deliberar.
- **Un participante designado**, que además de su rol tiene acceso a la vista de
  órdenes. El Presidente es el candidato natural, porque el registro escrito de
  decisiones es competencia suya.

Su función es una sola: **traducir a órdenes lo que la mesa deliberó**. No
conduce, no reparte información, no decide el ritmo, **y no sabe nada que los
demás no sepan**.

> Esto no es una concesión: **es lo que el propio Manual ya había decidido** al
> eliminar al Director del DAPRE — *«sus funciones de secretaría técnica, tablero
> de situación, ciclo de actualización y bitácora de decisiones las ejecuta el
> motor de simulación»*.

Tres consecuencias de diseño, y las tres mejoran el ejercicio:

**La información reservada la reparte el sistema, no una persona.** Es
precisamente lo que hacen las ocho vistas privadas. Sin ellas haría falta alguien
repartiendo sobres — y ese alguien sabría lo que hay en todos.

**El ritmo lo lleva el sistema.** El reloj de cada fase es visible para toda la
sala y suena solo. No lo administra el criterio de nadie, que siempre concede «un
minuto más».

**El parte lo muestra la pantalla.** Al abrir cada turno el tablero dice qué
cambió y qué se rompió. Cualquiera puede leerlo en voz alta; nadie tiene que
prepararlo.

### 6.2 El turno, autoconducido

```
0 · PARTE PRIVADO    1,0 min   Cada rol lee su vista. NADIE HABLA.
1 · APERTURA         1,0 min   El tablero muestra qué cambió. Se lee en voz alta
2 · DELIBERACIÓN     6,0 min   Las pantallas se congelan. Se habla
3 · ÓRDENES          2,5 min   Se transcriben. El sistema devuelve el plan
                               interpretado CON SU BANDA DE RIESGO, y la mesa
                               confirma o corrige
4 · RESOLUCIÓN       1,0 min   El sistema ejecuta
5 · CONSECUENCIAS    1,0 min   Prensa, redes, gremios, internacional
6 · REGISTRO         0,5 min   La decisión al pliego, con responsable nominado
                    ─────────
                    13,0 min
```

**Cinco turnos de decisión y cuatro interludios nocturnos de 3 minutos**, más
turno 0 y debriefing: dos horas exactas.

**El minuto 0 es indispensable.** Un minuto de silencio absoluto en el que los
ocho leen su pantalla. Si no se les da ese minuto, lo van a tomar durante la
deliberación — y ahí sí tendremos ocho personas mirando ocho pantallas.

**El paso 3 sigue siendo el mejor punto pedagógico del montaje**, y ahora no
depende de nadie. La pantalla devuelve:

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

**Al cerrar el turno 5**, el sistema corre tres turnos más sin nadie al mando y
proyecta el estado a 72 horas. No es un marcador: **es el país que la sala
entrega**, y es la pregunta con la que conviene abrir el debriefing — *¿esto se
sostiene sin ustedes?*

### 6.3 Las cinco reglas que impiden que la sala mire pantallas

El hallazgo del primer ejercicio fue exactamente este: **una pantalla por
participante produce ocho personas mirando ocho pantallas y ninguna mirando a las
otras siete.** Estas cinco reglas son la condición de que v2 funcione.

**1 · La vista privada cabe en una pantalla y no tiene desplazamiento.** Dos
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

> **Prueba para la primera corrida:** si en el minuto 4 de la deliberación alguien
> está mirando su pantalla, una de estas cinco se rompió.

---

## 7. Los dilemas que esto garantiza

Un dilema que depende de que los participantes lo descubran no es un dilema del
diseño: es suerte. **Estos ocho tienen que aparecer en toda corrida.**

**D1 · La fuerza que abre un camino le resta credibilidad a la mesa que negocia
el siguiente.** El Ministro del Interior ve caer su reserva por decisiones que no
tomó.

**D2 · Cada corredor priorizado es un corredor aplazado, y el aplazamiento tiene
nombre de ciudad.** El criterio técnico de Transporte y la urgencia del Alcalde
no pueden satisfacerse a la vez.

**D3 · La verdad es un recurso escaso: tres duplas para veinticuatro puntos.**
Verificar aquí es no verificar allá, y el error tiene dos direcciones, ambas
caras.

**D4 · El estándar de derechos es la única palanca que baja el riesgo sin
consumir capacidad.** Es el dilema *positivo*: el rol sin voto y sin fuerza es el
que más reduce la probabilidad del peor resultado.

**D5 · Entregar el reloj cambia el reloj.** El calendario de Minas es a la vez lo
que obliga a la mesa a decidir y lo que acelera aquello que mide.

**D6 · Concentrar hace responsable de cada error; delegar deja sin control sobre
la coherencia.** Sin decisión escrita con responsable nominado, el costo de cada
incidente se reparte sobre los ocho.

**D7 · Ocho urgencias legítimas y una escolta.** Cada turno, las ocho alertas
privadas apuntan a sitios distintos y todas tienen razón. No hay criterio superior
que las ordene: hay una mesa que tiene que elegir.

**D8 · Dos personas honestas, el mismo hecho, dos números.** Desde dentro de
ninguna de las dos vistas se puede saber cuál es correcto. La salida es hablar, y
si no basta, gastar una dupla que entonces no hace otra cosa.

> **La forma general del caso:** las ocho posiciones son defendibles y ninguna es
> suficiente. **Si en el debriefing una opción resulta haber sido obviamente
> correcta desde el turno 1, el ejercicio está mal calibrado.**

---

## 8. Las decisiones del equipo

### 8.1 Resueltas

| # | Decisión | Resolución |
|---|---|---|
| **V1** | ¿La vista privada es un dispositivo por persona o papel impreso? | **Un dispositivo por rol.** Cada participante accede desde su propio computador — página web, servidor local o lo que determine la implementación final. Sujeto a las cinco reglas de §6.3 |
| **V2** | ¿Quién opera la consola? | **Abierto, y las dos formas valen.** Una persona externa con pantalla independiente, o un participante designado con acceso a la vista de órdenes. En ningún caso sabe algo que los demás no sepan |
| **V3** | ¿Se puede afirmar un dato distinto del que se ve? | **No.** Con agendas reservadas ya hay tensión suficiente, y permitir el dato falso convierte esto en un juego de engaño en vez de uno de criterios en conflicto |
| **V4** | ¿El detalle de las vistas puede pasar al tablero general? | **No.** Las cifras se comparten hablando y los jugadores pueden anotarlas donde quieran, pero **el dato vive en la vista de su rol y no migra.** Así cada rol vuelve a ser necesario cada turno |
| **V5** | ¿Cuántas acciones? | **34**, entre cuatro y cinco por rol. La dinámica es lo que importa ahora; el número se puede replantear después |
| **V6** | ¿Las duplas de verificación y el acompañamiento de operaciones salen del mismo presupuesto? | **Sí, un solo bolsillo de tres.** Cada dupla hace una sola cosa por turno. Es lo que convierte la asignación de la Defensoría en una decisión real |

### 8.2 Resueltas — las que venían de la propuesta original

| # | Decisión | Resolución |
|---|---|---|
| **A1** | ¿Nombres reales o ficticios? | **Ficticios.** Ciudades, regiones y puntos de cierre. Protege de convertir el ejercicio en un juicio sobre hechos con responsabilidad judicial viva, y hace coherente el mapa esquemático de §3.2 |
| **A2** | ¿Se puntúa? ¿Las agendas suman? | **No hay marcador.** Las agendas reservadas se revelan al final, no se puntúan |
| **A3** | ¿La Defensoría puede retirarse? | **No se retira** — pero puede **manifestar públicamente que su permanencia está en cuestión**, y eso cuesta legitimidad y respaldo internacional |
| **A5** | ¿Los hechos que abren el turno 1 son fijos o se sortean? | **Fijos, siempre.** Permite comparar salas entre sí |
| **A6** | ¿Se acepta el azar? | **Sí, con semilla fija para reproducibilidad.** La semilla no es un elemento visible de la interfaz |

Dos de estas cinco tienen consecuencia de diseño y conviene dejarlas anotadas:

**A3 · La duda pública sustituye a la amenaza de irse.** La acción A1 de su ficha
es literalmente *«condicionar su permanencia»*, y una amenaza que el diseño nunca
deja consumar no sería una palanca. La sustitución —**decir en voz alta que se lo
está pensando**— es mejor que el retiro por tres razones: se puede usar varias
veces en vez de una sola, es graduada, y nunca saca sus mitigadores del juego.
Está desarrollada en su ficha de acciones (§5.2).

**A1 · Los nombres ficticios son trabajo pendiente.** Los puntos de cierre ya
tienen nombres inventados —Peaje del Puerto, Glorieta La Ceiba, Puente Amarillo—
**pero las regiones y varios puntos siguen siendo reales**. La tabla de §8.4 fija
un juego provisional para poder avanzar.

### 8.3 Lo único que queda abierto

**Quién opera la consola** (V2), que se decide al montar cada corrida y no antes:
alguien externo con pantalla independiente, o un participante designado.

### 8.4 El territorio ficticio — juego provisional

**Nombres de trabajo, para poder avanzar.** No están cerrados: son un
marcador de posición que se puede sustituir entero sin tocar nada del diseño,
porque el motor identifica los puntos por código y no por nombre.

**Las cuatro regiones y la ciudad epicentro:**

| Nombre | Qué papel cumple |
|---|---|
| **Bellaflor** | La ciudad epicentro: donde está el alcalde de la mesa, y donde la crisis es más aguda |
| **Región de Bellaflor** | La región central. Concentra la mayor parte de los puntos de cierre |
| **Puerto Espejo** | La región portuaria. Por ahí entra el combustible del país |
| **Las Cumbres** | Región montañosa del sur. **El reloj de oxígeno más apretado** |
| **Alto Verde** | Región del sur, agrícola y con presencia de comunidades organizadas |

**Los cinco corredores:**

| Nombre | Qué conecta |
|---|---|
| **Bellaflor – Puerto Espejo** | La ciudad con el puerto. Combustible, alimentos y humanitario. El más poblado |
| **Corredor del Sur** | Baja de Bellaflor hacia Las Cumbres y Alto Verde. Alimentos y humanitario |
| **Anillo hospitalario** | Rodea Bellaflor. **Solo humanitario** — es el único que sirve a Las Cumbres |
| **Refinería – Acopios** | De la refinería a los centros de distribución. **Solo combustible** |
| **Corredor Norte** | Salida norte de Bellaflor. Alimentos y general |

**Los puntos que hay que renombrar.** De los 24, la mayoría ya son inventados. Estos
cuatro conservan referencias reales y deben cambiar:

| Actual | Por qué | Sustituto propuesto |
|---|---|---|
| Km 18 vía al mar | Vía real de Cali | **Alto del Mirador** |
| Cruce de Villarrica | Municipio real del Cauca | **Cruce de San Isidro** |
| Retén de Pasto Norte | Ciudad real | **Retén del Alto Norte** |
| Corredor Sur (Panamericana) | Carretera real | **Corredor del Sur** |

> **El criterio, para cuando se cierren de verdad:** que **no sean alias
> transparentes**. «Valle Alto» por «Valle» no protege de nada. La convención
> heredada de la simulación anterior —Macondo sobre Mocoa— es un nombre que
> **declara su propia ficción** y que aun así permite reconocer la estructura del
> caso.
>
> Y una nota de operación: **la correspondencia entre lo ficticio y lo real es
> información del equipo docente, no del material de los participantes.** En las
> fichas y en las pantallas solo aparecen los nombres inventados.

---

## 9. Qué le pide esto al motor

Se anota para dimensionar, no para diseñarlo. **La buena noticia: v2 casi no
añade variables nuevas.** Casi todo lo que hace falta ya existe en el estado del
mundo; lo que falta es **proyectarlo ocho veces** y escribir las acciones que
faltan.

| Lo que hace falta | Tamaño | Ya existe |
|---|---|---|
| Ocho proyecciones del estado, una por rol, con su sesgo y su cobertura | **medio** | los cuatro sesgos están calibrados; falta producir las lecturas |
| Veinte acciones que hoy no existen | **grande** | el patrón de acción está resuelto y probado |
| Un solo presupuesto de tres duplas, compartido entre verificar y acompañar | **pequeño** | hoy son dos cosas independientes y acompañar sale gratis |
| Que la mezcla real de un punto tenga consecuencias | **pequeño** | la variable existe y hoy no entra en ningún cálculo |
| Denuncias con veracidad oculta, para la ventanilla de la Defensoría | **pequeño** | la estructura está escrita y nada la usa |
| Conducción del turno por el sistema: reloj por fase, parte de apertura, plan de vuelta | **medio** | el cálculo de riesgo y el plan interpretado ya existen |
| **El mapa esquemático**, con sus ocho niveles de detalle | **pequeño** | la topología está en los datos; solo falta una posición por punto y dibujar |
| Renombrar regiones y ciudades a nombres ficticios | **pequeño** | los puntos ya los tienen; las regiones y el epicentro no |
| Que la cohesión se pueda reponer y no solo perder | **pequeño** | hoy solo baja, y siempre igual |
| Persistir la corrida para repetirla con una decisión cambiada | **pequeño** | la semilla ya está registrada |

Y una regla que no se toca: **el motor debe seguir corriendo entero sin llamar a
ningún modelo de lenguaje.** Las ocho vistas son proyecciones deterministas del
estado, no texto generado. Si algún día una vista privada necesita un modelo para
existir, la arquitectura está mal.

---

## Lo que sigue

Este documento cierra el **modo de juego y el alcance del mundo**. El orden de
trabajo desde aquí:

1. **Cerrar el contenido exacto de las ocho vistas** — los tres o cuatro datos de
   cada una y la línea de alerta. Es una decisión de contenido, no de software, y
   **se puede probar en papel antes de escribir una línea de código.**
2. **Nombrar el territorio ficticio** —cuatro regiones y la ciudad epicentro— y
   **dibujar el esquema**: la disposición de los 24 puntos sobre sus cinco
   líneas. También es trabajo de papel, y de él sale el mapa que después se
   dibuja en pantalla.
3. **Escribir las acciones que faltan**, empezando por las cuatro que reequilibran
   el ejercicio: la mesa de concertación de Interior, la escolta y la disposición
   del ESMAD de la Policía, y la asignación de combustible de Minas.
4. **Unificar el presupuesto de duplas** y **conectar la mezcla real** de los
   puntos, para que el error doble tenga consecuencia.
5. **Recalibrar**, que solo se puede hacer después y con personas dentro.

**La primera corrida con personas es una medición, no un ejercicio**, y conviene
decirlo antes de empezar. Ningún coeficiente de este diseño está medido: son
convenciones declaradas, elegidas para que ninguna estrategia pura gane.

---

## Glosario

Términos propios del caso, en orden de aparición en el ejercicio.

**PMU · Puesto de Mando Unificado.** La instancia donde los ocho se sientan. En
el caso real, la mesa de coordinación de la respuesta del Estado a la crisis.

**Punto de cierre** *(o «punto»)*. Un bloqueo concreto con nombre y ubicación: un
peaje, una glorieta, un puente, la entrada de una refinería. Se modelan 24 de los
más de mil que hubo.

**Corredor.** Una secuencia ordenada de puntos entre un origen y un destino. Vale
lo que su peor punto: un camión que atraviesa tres bloqueos y se queda en el
cuarto no llegó.

**Clase de corredor.** Para qué sirve: combustible, alimentario, humanitario,
general. Un corredor puede tener varias, y el que salva a una región no es
necesariamente el que alimenta a otra.

**Días de autonomía.** Cuánto le queda a una región de combustible, alimentos u
oxígeno medicinal. Bajan solos; solo suben si se abre un corredor que sirva a esa
región.

**Escuadrón.** La unidad mínima de fuerza. Hay 40 del ESMAD, y cada uno está en
un sitio, haciendo algo, y cansado en algún grado.

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
desestimar. **Hay tres**, y con ellas hay que cubrir 24 puntos.

**Mitigador.** Una decisión que baja la probabilidad de que una operación termine
mal **sin consumir capacidad**: reglas de empleo escritas, identificación de los
agentes, registro audiovisual, una dupla presente, concertación con la alcaldía,
unidades descansadas. Los seis juntos dividen el riesgo por casi cinco.

**Banda de riesgo.** Cómo se le muestra a la sala la probabilidad de que una
operación termine mal, **antes de ordenarla**: baja, media, alta o crítica. Sirve
para que la sala gestione riesgo y no sorpresa.

**Vocería · control de vocería.** Quién habla por un punto de cierre, y sobre todo
**cuánto de ese punto controla realmente**. Lo que se logra abrir por
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

**Acción constitutiva.** Una que no abre ningún camino, no aparece en el tablero
y **modifica todo lo que venga después**: poner las decisiones por escrito, fijar
el estándar de empleo de la fuerza, acordar quién habla. Ninguna es obligatoria y
todas están tarifadas.

**Interludio nocturno.** Los tres minutos entre dos turnos de decisión. No se
delibera ni se ordena: se resuelve lo que se ordenó de día y la sala mira.

**Proyección a 72 horas.** Al cerrar el turno 5, el sistema corre tres turnos más
sin nadie al mando. No es un marcador: es el país que la sala entrega.

**Mapa esquemático.** La representación visual del territorio: líneas y
estaciones, como un plano de metro. Muestra relaciones —qué punto pertenece a qué
corredor y a qué región— y deliberadamente **no** muestra distancias, porque el
modelo no las tiene.

**Semilla.** El número que fija el azar de una corrida, de modo que se pueda
repetir exactamente igual. Queda registrada y **no es un elemento visible de la
interfaz**; se usa en el debriefing para volver a correr la jornada con una
decisión cambiada.

---

*Propuesta derivada del Manual de Roles con RADs (8 roles) y de la Matriz
Operativa del GovLab, y del diagnóstico del motor actual recogido en
[`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md).*

*Escuela de Gobierno · Universidad de La Sabana.*
