# Guía de acciones

Las **treinta y nueve** cosas que se pueden pedir en este ejercicio, una
por una y en lenguaje corriente: cómo se llama cada una, qué hace, qué
tiene que existir antes, y una frase que funciona tal cual dicha en voz
alta delante de la consola.

**Es la misma guía que cada titular tiene en su tablero**, con las nueve
carteras a la vez. En pantalla cada quien ve la suya y además el semáforo
de hoy —si hoy sale o qué falta—; eso cambia cada jornada y por eso no
está aquí. Lo de aquí no cambia nunca.

> **Se genera desde el código y no se edita a mano.**
> `uv run python scripts/repertorio.py`. Si una acción cambia, cambia aquí
> en la siguiente corrida — no hay una segunda versión de la verdad.

> **Sin una sola cifra, a propósito.** Cuánto cuesta cada cosa está en
> [`LAS_ACCIONES.md`](LAS_ACCIONES.md), que es el documento del equipo
> docente. Este es el de la sala, y **un nivel se interpreta; un número se
> optimiza**.

---

## Los tres tipos de acción

| Tipo | Qué cambia | Cuándo se nota |
|---|---|---|
| **Protocolo** | cómo trabaja la mesa: quién habla, quién firma, con qué reglas | no se ve en el mapa · rinde en todo lo que venga después |
| **Operación** | el mundo: el territorio, la fuerza, el abastecimiento | de inmediato |
| **Información** | lo que el país tiene por cierto | en la esfera pública |

**Ninguna está bloqueada y todas están tarifadas.** El ejercicio no obliga
a nadie a empezar por los protocolos: permite saltárselos y cobra la
diferencia después.

## Cómo se pide una acción

**No hay comandos.** Se escribe en la consola lo que se quiere hacer, con
las palabras de siempre, y el canal de órdenes lo traduce. Los ejemplos de
la última columna son el esqueleto mínimo: funcionan tal cual, y se pueden
decir de otras maneras y con otros datos.

**La orden la puede escribir cualquiera que esté sentado a la consola**, no
necesariamente quien tiene el rol. Decir en voz alta de parte de quién va
es lo que mantiene la trazabilidad de quién decidió qué — y eso no lo
comprueba el sistema, lo sostiene la sala.

**Lo que no se dice, no se da por puesto.** Una operación en la que nadie
dijo «militares» se ejecuta con ESMAD; una mesa en la que nadie dijo «con
la Alcaldía» se abre sin ella. Si hace falta un dato —qué unidad, con quién,
delimitada, de noche—, hay que decirlo con esas mismas palabras.

Los nombres de puntos, corredores y regiones son los del escenario, y están
en el mapa del tablero general.

---

## 01 · Presidente de la República

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Dejar todo por escrito** | Protocolo | Deja por escrito cada decisión y quién responde por ella. Sin registro, al cierre nadie puede decir quién ordenó qué. | Ninguno. Es de las que se adoptan el primer día y abaratan todo lo demás. | `fijar el registro escrito de decisiones` |
| **Decir qué no se negocia** | Protocolo | Anuncia qué está y qué no está sobre la mesa. Fija el terreno de lo negociable antes de que lo fije otro. | Ninguno. Conviene antes de que Interior lleve nada a la mesa. | `fijar las lineas rojas del Ejecutivo` |
| **Autorizar al Ejército** | Operación | Autoriza que el Ejército apoye a la Policía. Da más fuerza disponible, y militares frente a multitudes suben la tensión en la calle. | Ninguno. Es ella la que habilita a Defensa a emplear tropa. | `firmar la asistencia militar con limites` |
| **Reunir a los alcaldes** | Operación | Reúne a los alcaldes de las ciudades más golpeadas. Sirve para llegar a la mesa con una sola posición en vez de varias. | Ninguno. | `reunir a los alcaldes de las ciudades criticas` |
| **Ir al epicentro en persona** | Información | Viaja en persona a la ciudad más afectada. Es un gesto público de que el Gobierno da la cara. | Escuadrones sin comprometer para la escolta presidencial. | `ir al epicentro en persona` |

## 02 · Ministro del Interior

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Poner un solo vocero** | Protocolo | Establece que una sola persona habla por el Gobierno. Evita que dos carteras digan cosas distintas el mismo día. | Ninguno. | `exigir el protocolo de voceria` |
| **Sentar al Comité del Paro** | Operación | Sienta al Gobierno con el Comité del Paro. Es la vía más rápida para bajar la tensión, y operar por la fuerza ese mismo día es lo que más caro le sale a la mesa. | Que el Comité del Paro siga sentado a la mesa. | `convocar la mesa nacional con el Comite del Paro` |
| **Abrir una mesa en un punto** | Operación | Negocia un punto concreto para que lo desbloqueen sus propios voceros. Tarda dos turnos, y lo que se abre así aguanta mientras se cumpla lo pactado. | Un punto todavía cerrado, con vocería con quien hablar. En la jurisdicción del epicentro, además, la Alcaldía en la mesa. HAY QUE INSTALARLA CADA JORNADA: la mesa que no sesiona no avanza. | `concertar en el Puente Amarillo con la Alcaldia` |
| **Ofrecer algo a cambio** | Información | Ofrece algo concreto a cambio de levantar los cierres. Funciona donde hay con quién negociar; no donde nadie manda. | Ninguno, pero sin líneas rojas fijadas lo ofrecido se renegocia en la sala. | `ofrecer una contraprestacion legislativa` |

## 03 · Alcalde de la ciudad epicentro

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Exigir que le consulten la fuerza** | Protocolo | Exige que cualquier operación en su ciudad se acuerde antes con la Alcaldía. Baja el riesgo de que salga mal, y le quita velocidad a Defensa. | Ninguno. | `condicionar el empleo de la fuerza en la ciudad` |
| **Sentarse con los voceros del punto** | Operación | Sienta a hablar a los voceros de un punto de su ciudad. Es la vía pactada, hecha desde el municipio. | Un punto de su propia jurisdicción, todavía cerrado. HAY QUE INSTALARLA CADA JORNADA: la mesa que no sesiona no avanza. | `instalar mesa con voceros en el Puente Amarillo` |
| **Abrir paso a lo humanitario** | Operación | Monta un paso para ambulancias, oxígeno y alimentos en su jurisdicción. No abre el punto: abre una ventana. | Su propia jurisdicción. No cubre el resto del país. | `montar el esquema humanitario municipal` |
| **Publicar el conteo de la ciudad** | Información | Publica su propio conteo de lo que pasó en la ciudad. Si contradice la cifra nacional, uno de los dos queda desmentido. | Ninguno, pero sin protocolo común de verificación la cifra se disputa. | `publicar el parte municipal de la ciudad` |

## 04 · Ministro de Defensa

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Poner reglas a sus unidades** | Protocolo | Ordena que sus unidades vayan identificadas, con reglas escritas y grabando. Baja mucho la probabilidad de que una operación termine mal. | Ninguno. | `fijar las reglas de empleo del sector` |
| **Desbloquear un punto por la fuerza** | Operación | Manda a la fuerza pública a abrir un punto. Es lo más rápido que existe y lo más caro: el punto suele volver a cerrarse esa misma noche. | Un punto todavía cerrado y unidades disponibles del tipo que se pida. Con tropa, la asistencia militar firmada; en el epicentro, la concertación con la Alcaldía si la Alcaldía la exigió. | `operar el Puente Amarillo con ESMAD, con dupla de la Defensoria` |
| **Mover tropa a donde haga falta** | Operación | Mueve tropa a proteger instalaciones críticas. Libera policía para otras tareas e inmoviliza esas unidades donde las puso. | Unidades militares en reserva. | `redesplegar militares a infraestructura` |
| **Mostrar quién financia los cierres** | Información | Presenta lo que Inteligencia tiene sobre quién financia los cierres. Vale según lo sólido que sea; si no se sostiene, se vuelve en contra. | Ninguno. | `presentar la evidencia de inteligencia` |

## 05 · Director General de la Policía

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Separar lo confirmado de lo estimado** | Protocolo | Separa en su parte lo confirmado, lo estimado y lo que está en verificación. Evita que una estimación se lea en la mesa como un hecho. | Ninguno. | `clasificar el parte operacional` |
| **Concentrar el ESMAD** | Operación | Concentra escuadrones en los puntos que decida. Gana fuerza donde la lleva y deja descubierto lo que abandona. | Escuadrones todavía en contención estática de donde traerlos. | `concentrar el ESMAD` |
| **Escoltar una caravana o misión médica** | Operación | Escolta una caravana, un carrotanque o una misión médica. Hace llegar el suministro sin abrir el punto, y ocupa escuadrones todo el turno. | Escuadrones sin comprometer. Si el corredor sigue bloqueado la escolta sale, pero la carga no pasa. | `escoltar una mision medica por el Corredor hospitalario` |
| **Relevar a las unidades cansadas** | Operación | Releva a las unidades más agotadas. Un escuadrón cansado es el principal factor de que una operación salga mal. | Unidades desplegadas con fatiga que relevar. | `relevar las unidades agotadas` |

## 06 · Delegado de la Defensoría del Pueblo

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Exigir reglas, identificación y cámaras** | Protocolo | Exige que la fuerza actúe con reglas escritas, identificada y grabando. Es lo que hace que después se pueda saber qué pasó de verdad. | Ninguno. Es la de mayor rendimiento del ejercicio y no cuesta un escuadrón. | `exigir los estandares de empleo de la fuerza` |
| **Acordar una sola forma de verificar** | Protocolo | Establece una sola manera de verificar cifras y denuncias, igual para todos. Evita que cada cartera traiga su propio número. | Ninguno. | `adoptar el protocolo unico de verificacion` |
| **Mandar a sus verificadores** | Operación | Manda a sus verificadores a mirar puntos concretos. Solo tiene tres por turno, y también hacen falta para comprobar denuncias y acompañar operaciones. | Duplas libres esta jornada, y decir qué mirar. Salen del mismo bolsillo que el acompañamiento de operaciones. | `verificar el Puente Amarillo y el Peaje del Puerto` |
| **Exigir un paso humanitario permanente** | Operación | Exige que haya un paso permanente para lo humanitario. Negarlo es lo que más caro cuesta de cara al exterior. | Ninguno. | `requerir un corredor humanitario permanente` |
| **Poner en duda su permanencia** | Información | Dice en público que se está planteando si tiene sentido seguir en la mesa. Es su palanca más fuerte y se gasta: la segunda vez pesa menos que la primera. | Ninguno, pero se gasta: cada pronunciamiento pesa menos que el anterior. | `manifestar duda sobre la permanencia en la mesa` |

## 07 · Ministro de Transporte

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Fijar el orden de los corredores** | Protocolo | Fija en qué orden se atienden los corredores y por qué. Sin criterio, cada turno se discute lo mismo desde cero. | Ninguno. | `adoptar el criterio de priorizacion de corredores` |
| **Organizar una caravana** | Operación | Junta la carga en una caravana por un corredor prioritario. Necesita escolta para poder pasar. | Escolta ya dispuesta por la Policía, y el corredor sin ningún punto que lo bloquee. | `organizar una caravana por el Corredor del Sur` |
| **Hablar con los camioneros** | Operación | Habla con los camioneros antes de que decidan sumarse al paro. Si se suman, se cierra lo que hoy todavía circula. | Que los gremios no se hayan sumado ya al paro. | `negociar con los gremios camioneros` |
| **Publicar el mapa de cierres** | Información | Publica dónde está cerrado y qué se ha abierto. Anunciar una apertura que no se sostiene cuesta credibilidad. | Ninguno. Anunciar abierto lo que no deja pasar se desmiente solo. | `publicar el mapa de cierres` |

## 08 · Ministro de Minas y Energía

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Decidir a qué va el combustible** | Protocolo | Decide a qué va primero el combustible que queda: hospitales, transporte o industria. Es un criterio permanente, no una entrega puntual. | Ordenar los cuatro usos, todos y sin repetir. | `fijar la prioridad de combustible` |
| **Poner custodia a una instalación** | Operación | Pone bajo custodia una instalación del registro de infraestructura relevante. Queda protegida, e inmoviliza fuerza que hace falta en otra parte. | Decir CUÁL, de las del registro de infraestructura relevante, y que quede capacidad libre para custodiarla: lo que se protege sale de lo que desbloquea. | `declarar infraestructura critica el Acopio de combustible de Puerto Espejo` |
| **Acordar ventanas de paso** | Operación | Acuerda ventanas horarias para que pasen carrotanques por un punto. Pasa el suministro sin abrir el bloqueo. | Un punto donde la vocería reconocida controle algo. Donde no manda nadie no hay con quién acordar. | `acordar pasos seguros en la Porteria de la refineria` |
| **Decir cuántos días quedan** | Información | Dice cuántos días de oxígeno, combustible y comida le quedan a cada región. Es el dato que solo usted tiene, y difundirlo también genera pánico. | Ninguno. Difundirlo acelera lo que mide. | `entregar el calendario de agotamiento` |

## 09 · Ministro de Agricultura y Desarrollo Rural

| Acción | Tipo | Qué hace | Qué hace falta antes | Cómo pedirla en la consola |
|---|---|---|---|---|
| **Poner los alimentos en la prioridad** | Protocolo | Consigue que los alimentos y el alimento de las granjas tengan turno propio en el reparto de corredores. Lo que va detrás de todo llega tarde, y lo que llega tarde ya no sirve. | Ninguno. Si Transporte ya fijó su criterio, esto lo reordena delante de la mesa y se nota. | `fijar la clase de prioridad agroalimentaria` |
| **Sentarse con el campo** | Operación | Se sienta con las organizaciones campesinas de un punto rural para acordar el paso de alimentos e insumos. Avanza igual que una mesa local, y sigue en pie aunque el Comité del Paro se levante. | Un punto rural todavía cerrado —fuera del epicentro— con organización con quien hablar. No necesita al Comité del Paro. HAY QUE INSTALARLA CADA JORNADA: la mesa que no sesiona no avanza. | `instalar mesa tecnica agropecuaria en el Cruce de San Isidro` |
| **Aliviar a los productores** | Operación | Da crédito y alivios a los productores con pérdida, y autoriza mover animales y su alimento por rutas alternas. Alivia sin resolver, y la excepción sanitaria deja un riesgo que se paga después. | Ninguno, y es la única suya que no depende de nadie. Cada paquete en la misma región rinde menos que el anterior. | `activar los instrumentos sectoriales en Las Cumbres` |
| **Publicar lo que se está perdiendo** | Información | Publica con los gremios cuántos animales se están sacrificando y cuánto ha subido la comida. Le quita respaldo ciudadano al cierre, y le entrega el argumento de la urgencia a quien pide mano dura. | Ninguno, pero sin protocolo común de verificación la cifra se disputa. | `publicar el balance de perdida del eslabon pecuario` |
| **Concentrar el despacho de alimentos** | Operación | Junta la producción en pocos despachos grandes y los manda por la ventana escoltada que ya existe. Llega mucha más comida con la misma escolta, y quien queda fuera del cupo lo nota. | Escolta ya dispuesta por la Policía, y un corredor de clase alimentaria sin ningún punto que lo bloquee. | `acordar el esquema de acopio por el Corredor del Sur` |

---

## Apéndice · el nombre formal de cada acto

El nombre corriente es el que se usa hablando. El **nombre formal** es el
que queda escrito en el pliego de la sesión, y es el que hay que citar
cuando se reconstruye después quién ordenó qué. El tercero es el nombre en
el código, para quien tenga que buscarlo en
[`actions.py`](../src/engine/actions.py).

| Se dice | Se escribe en el pliego | En el código |
|---|---|---|
| Dejar todo por escrito | Nodo único de coordinación y registro escrito de decisiones | `FijarRegistroEscrito` |
| Decir qué no se negocia | Líneas rojas del Ejecutivo y marco de lo negociable | `FijarLineasRojas` |
| Autorizar al Ejército | Acto administrativo de asistencia militar | `FirmarAsistenciaMilitar` |
| Reunir a los alcaldes | Convocatoria a los alcaldes de las ciudades críticas | `ConvocarAlcaldes` |
| Ir al epicentro en persona | Desplazamiento presidencial al epicentro | `DesplazarseAlEpicentro` |
| Poner un solo vocero | Protocolo de vocería y plazo suspensivo de 24 h | `ExigirProtocoloVoceria` |
| Sentar al Comité del Paro | Sesión de la mesa nacional con el Comité del Paro | `ConvocarMesaNacional` |
| Abrir una mesa en un punto | Mesa local de concertación, corredor por corredor | `AbrirMesaLocal` |
| Ofrecer algo a cambio | Contraprestación legislativa por el levantamiento de cierres | `OfrecerContraprestacion` |
| Exigir que le consulten la fuerza | Concertación previa del empleo de la fuerza en su jurisdicción | `CondicionarEmpleoFuerza` |
| Sentarse con los voceros del punto | Mesa local de desbloqueo con voceros del punto | `InstalarMesaConVoceros` |
| Abrir paso a lo humanitario | Esquema humanitario municipal | `EsquemaHumanitarioMunicipal` |
| Publicar el conteo de la ciudad | Parte municipal verificado y disputa de la cifra nacional | `PublicarParteMunicipal` |
| Poner reglas a sus unidades | Reglas de empleo del sector y registro audiovisual obligatorio | `FijarReglasEmpleoSector` |
| Desbloquear un punto por la fuerza | Operación de desbloqueo sobre un punto | `OperarNodo` |
| Mover tropa a donde haga falta | Redespliegue militar a infraestructura o proyección aérea | `RedesplegarMilitares` |
| Mostrar quién financia los cierres | Evidencia de financiación de cierres y su solidez judicial | `PresentarEvidenciaInteligencia` |
| Separar lo confirmado de lo estimado | Parte operacional clasificado en confirmado, estimado y en verificación | `ClasificarParteOperacional` |
| Concentrar el ESMAD | Concentración del ESMAD en puntos priorizados | `DisponerESMAD` |
| Escoltar una caravana o misión médica | Escolta de caravana, carrotanque o misión médica | `Escoltar` |
| Relevar a las unidades cansadas | Relevo y rotación de unidades agotadas | `SolicitarRelevo` |
| Exigir reglas, identificación y cámaras | Estándar de empleo de la fuerza: reglas, identificación, registro | `ExigirEstandaresEmpleo` |
| Acordar una sola forma de verificar | Protocolo único de verificación de cifras y denuncias | `AdoptarProtocoloVerificacion` |
| Mandar a sus verificadores | Asignación de las duplas de verificación | `AsignarDuplas` |
| Exigir un paso humanitario permanente | Requerimiento de corredores humanitarios permanentes | `RequerirCorredoresHumanitarios` |
| Poner en duda su permanencia | Manifestación pública de duda sobre su permanencia | `ManifestarDudaPermanencia` |
| Fijar el orden de los corredores | Criterio único de priorización de corredores | `AdoptarCriterioPriorizacion` |
| Organizar una caravana | Caravana escoltada en un corredor priorizado | `OrganizarCaravana` |
| Hablar con los camioneros | Negociación con los gremios camioneros | `NegociarConGremios` |
| Publicar el mapa de cierres | Mapa de cierres y anuncio verificado de aperturas | `PublicarMapaCierres` |
| Decidir a qué va el combustible | Orden de prioridad del combustible entre usos | `FijarPrioridadCombustible` |
| Poner custodia a una instalación | Declaratoria de infraestructura crítica | `DeclararInfraestructuraCritica` |
| Acordar ventanas de paso | Pasos seguros y ventanas de despacho concertadas | `AcordarPasosSeguros` |
| Decir cuántos días quedan | Calendario de agotamiento por región | `EntregarCalendarioAgotamiento` |
| Poner los alimentos en la prioridad | Clase de prioridad agroalimentaria con ventana crítica en horas | `FijarClasePrioridadAlimentaria` |
| Sentarse con el campo | Mesa técnica agropecuaria de tránsito de carga, corredor por corredor | `InstalarMesaTecnicaAgropecuaria` |
| Aliviar a los productores | Instrumentos financieros y autorización sanitaria excepcional | `ActivarInstrumentosSectoriales` |
| Publicar lo que se está perdiendo | Balance público de la pérdida pecuaria y del deterioro de precios | `PublicarBalancePerdida` |
| Concentrar el despacho de alimentos | Acopio, cupos y despacho concentrado en ventanas escoltadas | `AcordarAcopioYVentanas` |
