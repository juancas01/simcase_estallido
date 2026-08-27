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
      <strong>Las flechas ▲▼</strong> dicen cuánto se movió la magnitud desde
      la última vez que la sala miró, es decir, en la última ventana resuelta.
    </p>
    <p>
      Una magnitud sin flecha no se movió. El color indica si el movimiento fue a
      favor o en contra, no si la decisión que lo produjo fue acertada.
    </p>
  </>
)

export const D = {

  reservas: (
    <>
      <p>
        <strong>Las cuatro se leen igual: arriba es mejor.</strong> Cada una lleva
        su propia definición en su marca de ayuda.
      </p>
      <p>
        Se agotan y se recomponen con las decisiones de la mesa, no con el paso
        del tiempo. Ninguna se recupera sola.
      </p>
      {NOTA_DELTA}
    </>
  ),


  // --- el reloj y el plazo --------------------------------------------------

  reloj: (
    <>
      <p>
        <strong>Cinco jornadas, del 11 al 15 de mayo</strong>, en turnos de doce
        horas que alternan día y noche. Nueve ventanas en total: cinco de
        deliberación y cuatro interludios nocturnos.
      </p>
      <dl>
        <dt>Día</dt>
        <dd>06:00 – 18:00 · se delibera, se ordena, la mesa está disponible</dd>
        <dt>Noche</dt>
        <dd>
          18:00 – 06:00 · no se delibera. Lo abierto por la fuerza vuelve a
          cerrarse y el riesgo de incidente se multiplica por 1,6
        </dd>
      </dl>
      <p>
        El plazo condiciona la jugada tanto como el dato: una concertación tarda
        dos turnos en rendir, de modo que abrirla en la jornada 5 es no abrirla.
      </p>
    </>
  ),

  linea_jornadas: (
    <>
      <p>
        <strong>Las nueve ventanas del ejercicio.</strong> La barra superior de
        cada columna es el día; la inferior, la noche que le sigue.
      </p>
      <dl>
        <dt>Llena</dt><dd>ventana ya resuelta</dd>
        <dt>Azul</dt><dd>la ventana en curso</dd>
        <dt>Vacía</dt><dd>pendiente</dd>
      </dl>
      <p>La quinta jornada no tiene noche: el ejercicio cierra con ella.</p>
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
        hacer con cada uno —y si vale la pena— es de la mesa.
      </p>
    </>
  ),

  coste_humano: (
    <>
      <p>
        <strong>Las dos magnitudes que no perdonan.</strong>
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
        deterioro. Responde a las decisiones del Puesto de Mando con rendimientos
        decrecientes —cada repetición de una misma medida conserva el 60 % del
        efecto de la anterior— y decae de forma proporcional a razón del 4 % por
        turno en ausencia de nuevos estímulos.
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
        <strong>Esquema topológico.</strong> Representa el orden de los puntos de
        cierre dentro de cada corredor y nada más.
      </p>
      <p>
        No representa distancias, escala geográfica ni tiempos de desplazamiento.
        Ninguna medida tomada sobre este esquema tiene significado.
      </p>
    </>
  ),

  formas_mapa: (
    <>
      <p>
        La forma del punto indica <strong>por qué vía se abrió</strong>, que no
        es un dato accesorio: determina cuánto dura la apertura.
      </p>
      <dl>
        <dt>◆</dt><dd>Fuerza — se revierte en el interludio nocturno</dd>
        <dt>■</dt><dd>Pactado — se sostiene mientras el acuerdo se cumpla</dd>
        <dt>●</dt><dd>Cerrado, o abierto por desgaste</dd>
        <dt>?</dt><dd>Sin verificar — su estado real se desconoce</dd>
      </dl>
    </>
  ),

  hechos_mapa: (
    <>
      <p>
        <strong>Un anillo dice que en ese punto pasó algo</strong> desde la última
        vez que la sala miró, es decir, en la última ventana resuelta. Se apaga
        solo en la siguiente.
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
        Una decisión sin responsable se consigna igualmente, y así consta. Cada
        decisión con responsable aporta 2 puntos de cohesión; la ausencia de
        registro escrito descuenta 8.
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
        Las dos superficies se muestran de forma simultánea y no alternada: la
        divergencia entre ambas es objeto del ejercicio y solo se percibe cuando
        se ven a la vez.
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
        Cada verificación consume una dupla del bolsillo de la Defensoría del
        Pueblo, que es de tres y se comparte con la verificación de puntos y el
        acompañamiento de operaciones.
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
        La Defensoría del Pueblo puede verificarlo con una dupla. El bolsillo
        disponible es de tres y se comparte con la verificación de denuncias y el
        acompañamiento de operaciones: emplear una aquí es no emplearla en otro
        sitio.
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
        El tablero general responde qué está pasando; esta vista responde cuánto,
        dónde exactamente y desde cuándo. El detalle no migra al tablero: por eso
        el titular sigue siendo necesario en todos los turnos y no solo en el
        primero.
      </p>
    </>
  ),

  repertorio: (
    <>
      <p>
        <strong>Acciones que esta cartera puede solicitar.</strong> Se enuncian
        ante la mesa y se transcriben en la consola.
      </p>
      <p>
        Esta vista es de solo lectura: no se ordena desde ella. Una orden que no
        se dijo en voz alta no la oyó nadie, y el ejercicio trata precisamente de
        lo que se dice en voz alta.
      </p>
    </>
  ),

  clases_accion: (
    <dl>
      <dt>Constituye</dt>
      <dd>establece una figura o una regla que rige los turnos siguientes</dd>
      <dt>Toca el mundo</dt>
      <dd>modifica el estado del territorio, de la fuerza o del abastecimiento</dd>
      <dt>Informa</dt>
      <dd>obtiene o difunde información sin alterar el estado del mundo</dd>
    </dl>
  ),

  vista_personal: (
    <>
      <p>
        <strong>Personal, no confidencial.</strong> El sistema la muestra
        únicamente a su titular, pero nada impide comunicar su contenido a la
        mesa, y el ejercicio busca que se comunique.
      </p>
      <p>
        Lo consignado aquí no se traslada al tablero general. En el turno
        siguiente el valor habrá cambiado y solo el titular tendrá el nuevo.
      </p>
    </>
  ),

  // --- la consola -----------------------------------------------------------

  fases: (
    <>
      <p>
        <strong>Secuencia de fases del turno y su duración prevista</strong>, en
        minutos.
      </p>
      <p>
        El reloj lo lleva el sistema. No hay moderador como figura aparte: quien
        opera esta consola puede ser cualquiera de los ocho, y se limita a
        transcribir.
      </p>
    </>
  ),

  congelado: (
    <>
      <p>
        <strong>Pantallas congeladas.</strong> Durante el parte privado, la
        apertura y la deliberación ninguna superficie se actualiza.
      </p>
      <p>
        Los valores mostrados corresponden al último cierre. Mientras la sala
        delibera no hay ninguna razón para volver a mirar una pantalla.
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
        <strong>Interpretación de la orden dictada</strong>, con las entidades
        resueltas y la banda de riesgo de cada acción.
      </p>
      <p>
        Ninguna consecuencia se enuncia antes de la ejecución: el modelo traduce;
        el motor decide, valida, ejecuta y reporta.
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
        La consulta es una acción más del plan, no un modo aparte: un mismo texto
        puede contener una pregunta y una orden. Un sistema que tuviera que
        clasificar entre las dos antes de leerlas emitiría, cuando se
        equivocase, una orden que nadie dio.
      </p>
      <p>
        Los datos se entregan estructurados y por tema. Un canal que devolviera
        un párrafo con totales agregados obligaría a inventar en cuanto se
        preguntara por algo concreto.
      </p>
    </>
  ),

  omitidas: (
    <>
      <p>
        <strong>Órdenes que constaban en el plan y no llegaron al motor.</strong>
      </p>
      <p>
        Solo se ejecuta lo que está enteramente resuelto. Una acción con un lugar
        sin identificar, una ambigüedad sin dirimir o un valor fuera de la
        enumeración se queda fuera y se enuncia con su motivo.
      </p>
      <p>
        La alternativa —ejecutarla con los valores por defecto— produciría una
        operación que nadie ordenó, informada como cumplida.
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
