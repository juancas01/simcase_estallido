// ---------------------------------------------------------------------------
// LAS DEFINICIONES — el texto que antes estaba impreso bajo cada cifra.
//
// Vive en un solo archivo por la misma razón que el catálogo de acciones vive en
// el motor: **un dato en dos sitios se desincroniza.** Si la fórmula del
// semáforo cambia, hay exactamente un párrafo que corregir.
//
// REGISTRO: formal y verificable. Cada umbral y cada coeficiente que aparece
// aquí está tomado de `src/engine/parameters.py`, no redactado de memoria. Una
// definición que dice «desciende ante incidentes» no explica nada que el lector
// no supusiera; una que dice «−9 puntos por incidente con víctima atribuible»
// permite calcular antes de decidir, que es de lo que trata el ejercicio.
//
// LO QUE NUNCA SE DEFINE AQUÍ: la mezcla real de un punto y la veracidad de una
// denuncia. Ninguna de las dos sale nunca del motor, y una definición locuaz es
// una filtración con otro nombre.
// ---------------------------------------------------------------------------

/**
 * La notación ▲▼. NO es una entrada del catálogo: es un fragmento que se
 * compone dentro de otras definiciones.
 *
 * El motivo es de interfaz, no de organización. Dos marcas de ayuda pegadas la
 * una a la otra obligan a elegir cuál abrir antes de saber qué hay en cada una,
 * y eso es peor que un globo largo. **Una marca, un globo, todo lo que hace
 * falta saber de esa tarjeta.**
 */
const NOTA_DELTA = (
  <>
    <p>
      <strong>Las flechas ▲▼</strong> indican cuánto se movió la magnitud en la
      última ventana resuelta, esto es, desde la anterior vez que la sala miró
      el tablero.
    </p>
    <p>
      Una magnitud sin flecha no se movió. El color indica si el movimiento fue a
      favor o en contra, no si la decisión que lo produjo fue acertada.
    </p>
  </>
)

export const D = {

  metricas: (
    <>
      <p>
        <strong>Cinco magnitudes del episodio, en escala y no en cifra:</strong>
        muy bajo, bajo, medio, alto, muy alto. Cuatro se leen igual —arriba es
        mejor— y la presión en la calle al revés.
      </p>
      <p>
        <strong>Por qué sin número.</strong> Un nivel se interpreta; un número
        se optimiza. Con la cifra proyectada, la deliberación se vuelve
        aritmética —«subimos tres, podemos gastar cuatro»— y el ejercicio pasa
        de tratar sobre conducción a tratar sobre puntuación. Ninguna de estas
        magnitudes es medible en la realidad con dos cifras significativas.
      </p>
      <p>
        Se agotan y se recomponen con las decisiones de la mesa, no con el paso
        del tiempo. Ninguna se recupera sola, y cada una lleva su propia
        definición en su marca de ayuda.
      </p>
      {NOTA_DELTA}
    </>
  ),


  // --- el reloj y el plazo --------------------------------------------------

  reloj: (
    <>
      <p>
        <strong>Cinco jornadas, del 11 al 15 de mayo.</strong> Cada una son
        quince minutos de sala partidos en dos tramos con reglas opuestas.
      </p>
      <dl>
        <dt>Día · 13 min</dt>
        <dd>
          se leen los tableros, se delibera y se ordena. La consola acepta
          órdenes en cualquier momento del tramo
        </dd>
        <dt>Noche · 2 min</dt>
        <dd>
          el motor resuelve lo que quedó en cola y se miran las consecuencias.
          No se reciben órdenes; lo abierto por la fuerza vuelve a cerrarse
        </dd>
      </dl>
      <p>
        La fecha es un indicador de la jornada, no un calendario. Lo que sí
        cambia una decisión es cuántas jornadas quedan: una concertación tarda
        dos en rendir, de modo que iniciarla en la quinta equivale a no
        iniciarla.
      </p>
    </>
  ),

  linea_jornadas: (
    <>
      <p>
        <strong>Las cinco jornadas del ejercicio</strong>, una marca cada una.
      </p>
      <dl>
        <dt>Llena</dt><dd>jornada ya resuelta</dd>
        <dt>Azul</dt><dd>la jornada en curso</dd>
        <dt>Vacía</dt><dd>pendiente</dd>
      </dl>
      <p>
        Si es de día o de noche lo dice la propia caja del reloj, que cambia de
        color.
      </p>
    </>
  ),

  sin_cerrar: (
    <>
      <p>
        <strong>Lo que sigue abierto</strong>, contado. Puntos que nadie ha
        verificado en campo, denuncias graves cuya veracidad no se ha
        establecido, y decisiones registradas sin responsable nominado.
      </p>
      <p>
        Son hechos sobre el estado del expediente, no una lista de tareas. Qué
        hacer con cada uno, y si conviene hacer algo, lo decide la mesa.
      </p>
    </>
  ),

  coste_humano: (
    <>
      <p>
        <strong>Las dos magnitudes del coste humano del ejercicio.</strong>
      </p>
      <p>
        Las muertes evitables son un acumulador irreversible: no descienden
        nunca, hagan lo que hagan los turnos siguientes. La presión en la calle
        sí baja, pero solo con decisiones, y con rendimientos decrecientes.
      </p>
      {NOTA_DELTA}
    </>
  ),

  // --- las cinco magnitudes del tablero ------------------------------------

  presion_calle: (
    <>
      <p><strong>Intensidad de la movilización</strong>, en escala de 0 a 100.</p>
      <p>
        Es la única magnitud del tablero en la que un valor alto indica
        deterioro. Responde a las decisiones del Puesto de Mando con
        rendimientos decrecientes —cada repetición de una misma medida conserva
        el 60 % del efecto de la anterior— y decae un 4 % por turno mientras no
        reciba nuevos estímulos.
      </p>
    </>
  ),

  legitimidad: (
    <>
      <p>
        <strong>Reserva de 0 a 100.</strong> Reconocimiento público de la
        actuación del Estado como ajustada a derecho.
      </p>
      <dl>
        <dt>−9</dt><dd>incidente con víctima atribuible</dd>
        <dt>−7</dt><dd>la Defensoría hace pública su duda de permanencia</dd>
        <dt>−6</dt><dd>imagen viral</dd>
        <dt>−3</dt><dd>turno cerrado sin ninguna decisión</dd>
        <dt>+5</dt><dd>acuerdo verificable cumplido</dd>
        <dt>+3</dt><dd>escolta humanitaria lograda</dd>
        <dt>+2</dt><dd>apertura concertada de un punto</dd>
      </dl>
    </>
  ),

  credibilidad_mesa: (
    <>
      <p>
        <strong>Reserva de 0 a 100.</strong> Disposición de las contrapartes a
        tener por vinculante lo que el Gobierno ofrece.
      </p>
      <dl>
        <dt>−12</dt><dd>operar el mismo día en que hay mesa convocada</dd>
        <dt>−10</dt><dd>acuerdo incumplido</dd>
        <dt>+8</dt><dd>acuerdo verificable cumplido</dd>
      </dl>
      <p>
        Por debajo de 30 el Comité Nacional del Paro suspende su participación;
        por debajo de 15 la retira de forma definitiva.
      </p>
    </>
  ),

  respaldo_internacional: (
    <>
      <p>
        <strong>Reserva de 0 a 100.</strong> Posición de organismos
        multilaterales y gobiernos externos.
      </p>
      <dl>
        <dt>−12</dt><dd>corredor humanitario negado</dd>
        <dt>−9</dt><dd>la Defensoría hace pública su duda de permanencia</dd>
        <dt>−7</dt><dd>incidente con víctima atribuible</dd>
        <dt>−6</dt><dd>denuncia grave confirmada como veraz</dd>
      </dl>
      <p>Por debajo de 30 se producen pronunciamientos públicos.</p>
    </>
  ),

  cohesion_mesa: (
    <>
      <p>
        <strong>Reserva de 0 a 100.</strong> Consistencia interna del Puesto de
        Mando. Se liquida únicamente en los turnos de decisión.
      </p>
      <dl>
        <dt>−8</dt><dd>sin registro escrito de las decisiones</dd>
        <dt>−8</dt><dd>operación ejecutada sin informar a la mesa</dd>
        <dt>−5</dt><dd>sin protocolo de vocería única</dd>
        <dt>−3</dt><dd>sin criterio de priorización declarado</dd>
        <dt>+2</dt><dd>por cada decisión con responsable nominado</dd>
      </dl>
      <p>Por debajo de 35 aparecen contradicciones públicas entre carteras.</p>
    </>
  ),

  fuerza: (
    <>
      <p>
        <strong>Escuadrones antidisturbios no comprometidos</strong> en ninguna
        operación en curso, sobre el total en el teatro.
      </p>
      <p>
        Cada escolta humanitaria inmoviliza 2 escuadrones durante el turno, y
        cada instalación bajo custodia, 2 policías o 3 militares. El tablero no
        indica su ubicación ni su fatiga: ese grado de resolución corresponde a
        la Dirección General de la Policía.
      </p>
    </>
  ),

  // --- el mapa y los corredores --------------------------------------------

  mapa: (
    <>
      <p>
        <strong>Mapa en dos niveles.</strong> El de país dibuja las cuatro
        regiones teñidas de su <em>estado de bloqueo</em> — cuántos de sus puntos
        no dejan pasar nada. Un clic acerca una región y muestra sus puntos y sus
        corredores.
      </p>
      <p>
        Al posarse sobre una región o sobre un punto, la ficha de abajo entrega
        las mismas seis lecturas: paso, dureza, gente en la calle, días de cierre,
        apoyo del barrio y control de la vocería. Las de la región son el promedio
        simple de sus puntos modelados.
      </p>
      <p>
        <strong>Las lecturas van en banda y no en cifra.</strong> Un nivel se
        interpreta; un número se optimiza. Las dos excepciones son las dos cosas
        que se cuentan de verdad: personas y días.
      </p>
      <p>
        <strong>La silueta y la red vial son reales</strong>, tomadas de datos
        abiertos; el país, sus nombres y sus cuatro regiones son inventados. Las
        carreteras van casi transparentes a propósito: son el suelo sobre el que
        se leen los corredores y los bloqueos, no la información.
      </p>
      <p>
        Cada corredor se dibuja <strong>por el camino que existe</strong>, no en
        línea recta entre sus puntos: dos bloqueos que parecen vecinos pueden
        estar a media vuelta por carretera.
      </p>
      <p>
        El territorio es <strong>ficticio</strong>. Sitúa, no mide: no hay
        distancias, ni escala, ni tiempos de desplazamiento, y ninguna medida
        tomada sobre este mapa significa nada.
      </p>
    </>
  ),

  formas_mapa: (
    <>
      <p>
        La forma del punto indica <strong>qué se está haciendo con él</strong>,
        que no es lo mismo que cómo se abrió: de un punto cerrado, el modo de
        apertura no dice nada, y un punto operado que no cedió no es un punto
        que nadie ha tocado.
      </p>
      <dl>
        <dt>◆</dt>
        <dd>Intervenido a la fuerza — cediera o no cediera</dd>
        <dt>■</dt>
        <dd>En negociación — hay mesa instalada, o está abierto porque se pactó</dd>
        <dt>●</dt><dd>No se está haciendo nada en absoluto</dd>
        <dt>?</dt><dd>Sin verificar — su estado real se desconoce</dd>
      </dl>
      <p>
        El anillo verde señala una <strong>mesa que ha sesionado hoy</strong>; el
        ámbar a trazos, una instalada que hoy nadie ha convocado. Una mesa local
        hay que instalarla cada jornada para que surta efecto: no instalarla un
        día equivale a congelar la negociación, y lo andado no se pierde pero
        tampoco avanza.
      </p>
    </>
  ),

  infraestructura_mapa: (
    <>
      <p>
        <strong>Las instalaciones que el país necesita en pie</strong>, con su
        criticidad en palabra — vital, alta, media — y no en índice. Aparecen al
        acercar una región.
      </p>
      <dl>
        <dt>Contorno continuo</dt><dd>bajo custodia</dd>
        <dt>Contorno a trazos</dt><dd>sin proteger</dd>
      </dl>
      <p>
        <strong>No hay acciones en contra de esta infraestructura</strong>, y es
        deliberado: el ejercicio no simula un ataque a la refinería, simula la
        decisión de inmovilizar fuerza para custodiarla — que es la que enfrenta
        a Minas con Defensa. Lo que queda registrado es el riesgo asumido al
        dejarla sola, y de eso se responde en el cierre.
      </p>
    </>
  ),

  hechos_mapa: (
    <>
      <p>
        <strong>Un anillo señala que en ese punto ocurrió algo</strong> durante
        la última ventana resuelta. Se apaga solo en la siguiente.
      </p>
      <dl>
        <dt>Rojo</dt>
        <dd>
          volvió a cerrarse de noche, se operó con incidente, o se incumplió un
          acuerdo
        </dd>
        <dt>Ámbar</dt><dd>se operó, sin incidente</dd>
        <dt>Verde</dt><dd>se abrió, o se acordó paso seguro</dd>
        <dt>Azul</dt><dd>alguien lo verificó en campo</dd>
      </dl>
      <p>
        Al posarse sobre el punto se lee el detalle: qué unidad operó y si llevaba
        dupla de la Defensoría.
      </p>
      <p>
        <strong>El mapa cuenta lo que se hizo, no dónde está la fuerza ahora.</strong>{' '}
        Una operación de anoche es un hecho público; la posición y la fatiga de los
        escuadrones son de la Dirección General de la Policía.
      </p>
    </>
  ),

  corredores: (
    <>
      <p>
        <strong>Flujo:</strong> proporción del tránsito nominal que el corredor
        admite, calculada como el <strong>mínimo</strong> del flujo de sus
        puntos.
      </p>
      <p>
        Un corredor vale lo que su peor punto, con independencia de cuántos de
        los demás estén abiertos. Uno a flujo pleno repone 2,6 días de autonomía
        por día, contra un consumo de 1,0.
      </p>
    </>
  ),

  poblacion_corredor:
    'Población aguas abajo: habitantes cuyo abastecimiento depende de este corredor.',

  clases_corredor:
    'Clases de carga con prioridad declarada sobre este corredor.',

  // --- las regiones ---------------------------------------------------------

  semaforo: (
    <>
      <p>
        <strong>Estado de abastecimiento en grano grueso</strong>, determinado
        por el menor de los tres días de autonomía de la región: oxígeno
        medicinal, combustible y alimentos.
      </p>
      <dl>
        <dt>Verde</dt><dd>2,5 días o más</dd>
        <dt>Ámbar</dt><dd>entre 1 y 2,5 días</dd>
        <dt>Rojo</dt><dd>menos de 1 día</dd>
      </dl>
      <p>
        Las cifras exactas, y cuál de los tres insumos manda, corresponden al
        Ministerio de Minas y Energía.
      </p>
    </>
  ),

  muertes_evitables: (
    <>
      <p>
        <strong>Fallecimientos por interrupción del suministro de oxígeno
        medicinal.</strong> Acumulador irreversible: no descienden nunca.
      </p>
      <p>
        Se aplica una tasa de 0,22 % por hora sin suministro sobre los 180
        pacientes en soporte de la región, modulada por su presión hospitalaria.
        Es la única magnitud del ejercicio que convierte logística en muertes.
      </p>
    </>
  ),

  // --- el pliego ------------------------------------------------------------

  pliego: (
    <>
      <p>
        <strong>Registro de las decisiones adoptadas y de su responsable
        nominado.</strong>
      </p>
      <p>
        Una decisión sin responsable se consigna de todos modos, y queda marcada
        como tal. Cada decisión con responsable aporta 2 puntos de cohesión; la
        ausencia de registro escrito descuenta 8.
      </p>
    </>
  ),

  // --- la esfera pública ----------------------------------------------------

  esfera: (
    <>
      <p>
        <strong>Lo que se publica y se afirma</strong>, con independencia de lo
        que el tablero registra como cierto.
      </p>
      <p>
        Las dos superficies se muestran a la vez y no alternadas: la divergencia
        entre ambas es parte de lo que el ejercicio enseña, y solo se aprecia
        comparándolas.
      </p>
    </>
  ),

  encuadre: (
    <>
      <p>
        <strong>Marco interpretativo predominante</strong> en la cobertura del
        período: represión, desorden, negociación o abandono.
      </p>
      <p>
        Se deriva del estado del mundo y de las decisiones publicadas. La mesa
        puede cambiarlo actuando, no declarándolo.
      </p>
    </>
  ),

  denuncias: (
    <>
      <p>
        <strong>Denuncias graves cuya veracidad no ha sido establecida.</strong>
      </p>
      <p>
        No existe señal observable que distinga una denuncia veraz de una falsa
        antes de verificarla. Confirmar una veraz descuenta 6 puntos de respaldo
        internacional; desmentir una falsa aporta 3 de legitimidad.
      </p>
      <p>
        Cada verificación consume una de las tres duplas de la Defensoría del
        Pueblo, que son también las que verifican puntos y acompañan
        operaciones.
      </p>
    </>
  ),

  punto_sin_verificar: (
    <>
      <p>
        <strong>Punto sin verificación en campo.</strong> Su estado real se
        desconoce, y el tablero no lo supone.
      </p>
      <p>
        La Defensoría del Pueblo puede verificarlo con una dupla. Dispone de
        tres en total, y las mismas tres sirven para verificar denuncias y
        acompañar operaciones: la que se emplea aquí no queda para otro sitio.
      </p>
    </>
  ),

  generado_por: (
    <>
      <p><strong>Origen del texto mostrado.</strong></p>
      <p>
        Un modelo de lenguaje redacta la narración a partir del estado que el
        motor ya calculó. Sin llave de API el motor emplea plantillas
        deterministas y el ejercicio se desarrolla igual: ninguna decisión de la
        simulación está delegada al modelo.
      </p>
    </>
  ),

  // --- la vista privada -----------------------------------------------------

  alerta_privada:
    'Asunto de mayor urgencia en la cartera del titular durante el turno en '
    + 'curso. Se recalcula en cada turno a partir del estado del motor.',

  detalle_privado: (
    <>
      <p>
        <strong>Información disponible con este grado de resolución únicamente
        para esta cartera.</strong>
      </p>
      <p>
        El tablero general responde qué está pasando; esta vista responde
        cuánto, dónde exactamente y desde cuándo. El detalle no sube al tablero:
        si su titular no lo comunica a la mesa, nadie más lo tiene.
      </p>
    </>
  ),

  requisitos_previos: (
    <>
      <p>
        <strong>Qué tiene que existir antes</strong> para que esta acción pueda
        pedirse. Es un hecho sobre la acción: no cambia de una jornada a otra.
      </p>
      <p>
        <strong>Va en cualitativo y nunca en cifra.</strong> «Escuadrones sin
        comprometer», no «dos escuadrones». Con el número delante, la
        deliberación se vuelve aritmética; con el requisito enunciado, hay que
        preguntarle a quien lo tiene — y esa pregunta ocurre en voz alta, que es
        donde el ejercicio la quiere.
      </p>
      <p>
        Cuánto falta <em>hoy</em> lo dice la primera columna, que sí mira el
        estado real.
      </p>
    </>
  ),

  ejemplo_consola: (
    <>
      <p>
        <strong>Una frase que funciona tal cual.</strong> No es una paráfrasis:
        escrita así en la consola, produce esta acción.
      </p>
      <p>
        Se puede decir de otras maneras y con otros datos — el punto, la unidad,
        quién firma, si acompaña una dupla. El ejemplo es el esqueleto mínimo,
        no la única forma admitida.
      </p>
      <p>
        Algunas acciones existen en el motor y <strong>todavía no se
        transcriben</strong> por la consola: se acuerdan en la mesa y quedan en
        el pliego, pero el canal de órdenes aún no las reconoce.
      </p>
    </>
  ),

  mesas_diarias: (
    <>
      <p>
        <strong>Una mesa local hay que instalarla cada jornada para que surta
        efecto.</strong> La concertación avanza por sesiones, no por días
        transcurridos.
      </p>
      <p>
        No instalarla un día <strong>no pierde lo andado</strong>, pero congela
        la negociación: no avanza, y el reloj del ejercicio corre igual. Abrir
        una mesa en la cuarta jornada y no volver a ella es no haberla abierto.
      </p>
      <p>
        La pregunta llega solo a quien puede convocarla — el Ministro del
        Interior en todo el país, el Alcalde en su jurisdicción — y es una
        pregunta: dice qué hay y qué lleva parado, no qué conviene hacer.
      </p>
    </>
  ),

  repertorio: (
    <>
      <p>
        <strong>Acciones que esta cartera puede solicitar</strong>, con lo que
        hace falta antes y cómo se piden.
      </p>
      <dl>
        <dt>Se puede pedir</dt><dd>viable en esta jornada</dd>
        <dt>Con reparos</dt>
        <dd>viable, y con una condición que conviene conocer antes de pedirla</dd>
        <dt>Aún no</dt>
        <dd>falta un requisito; se indica cuál y, si corresponde, qué cartera lo habilita</dd>
        <dt>Ya vigente</dt><dd>en vigor; volver a adoptarla no altera nada</dd>
      </dl>
      <p>
        El requisito se enuncia en general y nunca como instrucción: informa de
        qué falta, no de qué conviene hacer.
      </p>
      <p>
        La columna <em>Requisitos previos</em> enuncia de qué depende cada
        acción, siempre en cualitativo; la columna <em>Hoy</em> dice si eso se
        cumple en esta jornada.
      </p>
      <p>
        Esta vista es de solo lectura. Para que una acción se ejecute hay que
        pedirla ante la mesa y transcribirla en la consola.
      </p>
    </>
  ),

  consecuencias: (
    <>
      <p>
        <strong>Lo que produjo la jornada</strong>, reunido en un solo sitio
        durante los dos minutos de noche: el resultado de cada orden y los
        hechos que el motor generó a continuación.
      </p>
      <p>
        Enumera; no interpreta. Qué significa cada cosa y qué se hace con ella
        corresponde a la mesa, y es para eso que existe este tramo.
      </p>
      <p>Desaparece al abrir la jornada siguiente.</p>
    </>
  ),

  clases_accion: (
    <dl>
      <dt>Protocolo</dt>
      <dd>
        establece una figura o una regla que rige los turnos siguientes: quién
        habla, quién firma, con qué estándar se emplea la fuerza
      </dd>
      <dt>Operación</dt>
      <dd>modifica el estado del territorio, de la fuerza o del abastecimiento</dd>
      <dt>Información</dt>
      <dd>obtiene o difunde información sin alterar el estado del mundo</dd>
    </dl>
  ),

  vista_personal: (
    <>
      <p>
        <strong>Personal, no confidencial.</strong> El sistema la muestra
        únicamente a su titular, pero su contenido puede comunicarse a la mesa,
        y el ejercicio espera que se comunique.
      </p>
      <p>
        Lo consignado aquí no se traslada al tablero general. En el turno
        siguiente el valor habrá cambiado y solo el titular tendrá el nuevo.
      </p>
    </>
  ),

  // --- la consola -----------------------------------------------------------

  cronometro: (
    <>
      <p>
        <strong>Reloj de sala.</strong> Arranca desde la consola y a partir de
        ese momento corre solo: la jornada se cierra sola al minuto trece y la
        siguiente se abre sola dos minutos después.
      </p>
      <p>
        Arriba queda lo que resta del tramo en curso; abajo, lo que lleva la
        sesión entera. Es el mismo número en las diez pantallas: lo calcula el
        servidor y cada superficie corrige el desfase de su propio reloj.
      </p>
      <p>
        Detenido desde la consola, el número se congela en todas a la vez y la
        caja lo indica. El tiempo del ejercicio no corre mientras la sala no
        está en el ejercicio.
      </p>
    </>
  ),

  fases: (
    <>
      <p>
        <strong>Los dos tramos de la jornada y su duración.</strong> Trece
        minutos de día en los que se ordena y dos de noche en los que no.
      </p>
      <p>
        El ritmo lo lleva el sistema: se arranca aquí una sola vez y después las
        jornadas se encadenan solas. Los mandos son para lo imprevisto —pausar
        ante una interrupción real, cerrar el día antes de tiempo, abrir la
        jornada siguiente, poner el reloj a cero.
      </p>
      <p>
        No hay moderador como figura aparte: quien opera esta consola puede ser
        cualquiera de los nueve, y se limita a transcribir.
      </p>
    </>
  ),

  ordenes: (
    <>
      <p><strong>Transcripción literal de lo que la mesa acordó.</strong></p>
      <p>
        Se escribe tal como se dijo. La pantalla devuelve el plan interpretado
        para leerlo en voz alta, y la sala confirma o corrige antes de que nada
        se ejecute.
      </p>
    </>
  ),

  plan_interpretado: (
    <>
      <p>
        <strong>Interpretación de la orden dictada</strong>, con los lugares y
        las unidades ya identificados y la banda de riesgo de cada acción.
      </p>
      <p>
        Ninguna consecuencia se enuncia antes de ejecutar: lo que aparece aquí
        es lo que se va a intentar, no lo que va a ocurrir.
      </p>
    </>
  ),

  riesgo_mostrado: (
    <>
      <p>
        <strong>Probabilidad de incidente</strong> calculada para la operación,
        con techo del 98 %.
      </p>
      <p>
        Seis mitigadores la reducen de forma multiplicativa: reglas escritas
        (×0,70), identificación de agentes (×0,85), registro audiovisual (×0,80),
        dupla presente (×0,75), concertación con la alcaldía (×0,80) y unidades
        descansadas (×0,75). Los seis juntos dividen el riesgo por 4,7
        aproximadamente.
      </p>
      <p>
        <strong>Atribuible</strong> indica si un incidente eventual se imputaría
        al Estado.
      </p>
    </>
  ),

  consulta: (
    <>
      <p>
        <strong>Respuesta de solo lectura, extraída del motor.</strong> Preguntar
        no consume el turno y no ordena nada.
      </p>
      <p>
        No hace falta cambiar de modo para preguntar: un mismo texto puede
        contener una pregunta y una orden, y la consola atiende las dos.
      </p>
      <p>
        Los datos se entregan estructurados y por tema, de modo que una pregunta
        concreta obtiene una cifra concreta y no un resumen.
      </p>
    </>
  ),

  omitidas: (
    <>
      <p>
        <strong>Órdenes que constaban en el plan y no llegaron al motor.</strong>
      </p>
      <p>
        Solo se ejecuta lo que está enteramente resuelto. Una acción con un
        lugar sin identificar, una ambigüedad sin dirimir o un valor que no está
        entre los admitidos se queda fuera.
      </p>
      <p>
        Cada una aparece con su motivo. Para que se ejecute hay que volver a
        dictarla con el dato que le faltaba.
      </p>
    </>
  ),

  interpretado_por: (
    <>
      <p>
        <strong>Capa que tradujo la orden</strong> de lenguaje natural a acciones
        tipadas.
      </p>
      <p>
        Sin llave de API se emplea un intérprete determinista de menor alcance.
        La validación y la ejecución son idénticas en ambos casos.
      </p>
    </>
  ),
}
