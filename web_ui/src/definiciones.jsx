// ---------------------------------------------------------------------------
// LAS DEFINICIONES — lo que dice cada globo de ayuda.
//
// DOS FRASES Y NINGUNA CIFRA. Esa es toda la regla, y sustituye a la contraria.
//
// Antes esto era un catálogo formal: cada globo traía los umbrales y los
// coeficientes exactos tomados de `src/engine/parameters.py`, con la idea de
// que una definición que dice «−9 puntos por incidente con víctima atribuible»
// permite calcular antes de decidir. El razonamiento tenía un fallo, y es el
// mismo que el tablero lleva defendiendo en todo lo demás:
//
//     UN NIVEL SE INTERPRETA; UN NÚMERO SE OPTIMIZA.
//
// El tablero se cuida de no proyectar cifras —«Legitimidad: alta», nunca «61»—
// justamente para que la deliberación no se vuelva aritmética. Y después las
// ponía todas, con su signo y su magnitud, a un puntero de distancia. La mesa
// que quisiera contar hasta el umbral solo tenía que abrir el globo: «esto nos
// cuesta ocho, aquello nos da cinco, hagamos aquello». La puerta de atrás era
// más ancha que la puerta.
//
// De modo que un globo ya no define: CONTEXTUALIZA. Dice qué es esta cosa y por
// qué importa en el ejercicio, y se calla el resto. Quien quiera saber cuánto
// cuesta exactamente una decisión tiene que preguntárselo a quien lleva esa
// cartera, en voz alta y delante de todos — que es donde el ejercicio quiere
// esa conversación.
//
// SON CADENAS Y NO JSX, y eso es parte de la regla, no un detalle. Con JSX
// cabía una lista de definiciones, una tabla de umbrales y cuatro párrafos; en
// una cadena de dos frases no cabe nada de eso aunque se quiera. El formato
// impide la recaída.
//
// LO QUE SIGUE SIN DEFINIRSE AQUÍ: la mezcla real de un punto y la veracidad de
// una denuncia. Ninguna de las dos sale nunca del motor, y una definición
// locuaz es una filtración con otro nombre.
// ---------------------------------------------------------------------------

export const D = {

  // --- el estado del país ---------------------------------------------------

  metricas:
    'Cinco magnitudes del episodio, en escala y no en cifra. Se agotan y se '
    + 'recomponen con las decisiones de la mesa, nunca con el paso del tiempo.',

  presion_calle:
    'La intensidad de la movilización en la calle. Es la única magnitud del '
    + 'tablero en la que estar arriba es estar peor.',

  legitimidad:
    'El reconocimiento público de que el Estado está actuando conforme a '
    + 'derecho. Se pierde con los incidentes y también con la inacción, y se '
    + 'recompone cumpliendo lo que se acuerda.',

  credibilidad_mesa:
    'Cuánto creen las contrapartes que el Gobierno cumplirá lo que ofrece. Si '
    + 'cae lo suficiente, dejan de sentarse.',

  respaldo_internacional:
    'La posición de los organismos multilaterales y los gobiernos externos ante '
    + 'lo que hace el Puesto de Mando. Cuando se deteriora, aparecen '
    + 'pronunciamientos públicos.',

  cohesion_mesa:
    'Si el Puesto de Mando está actuando como un solo Gobierno o como carteras '
    + 'sueltas. Cuando se erosiona, las contradicciones entre ministerios se '
    + 'vuelven públicas.',

  muertes_evitables:
    'Las muertes causadas por quedarse sin oxígeno medicinal. Es lo único '
    + 'irreversible del ejercicio: no bajan nunca, haga lo que haga la sala '
    + 'después.',

  puntos_abiertos:
    'Cuántos puntos de cierre dejan pasar el tránsito con normalidad, sobre el '
    + 'total del país. Es la tarea del ejercicio, contada.',

  estado_mesa:
    'Con quién se puede negociar hoy y qué quedó pendiente de resolver. No mide '
    + 'el país: mide la conversación que lo está conduciendo.',

  perdida_bloqueos:
    'Lo que la economía deja de mover cada día por los corredores '
    + 'estrangulados. Es la contraparte económica del bloqueo, y cede con cada '
    + 'apertura que la mesa consiga sostener.',

  fuerza:
    'Los escuadrones antidisturbios que hoy no están metidos en ninguna '
    + 'operación. Dónde están y cómo están no lo dice el tablero: eso es de la '
    + 'Dirección General de la Policía.',

  // --- el reloj -------------------------------------------------------------

  reloj:
    'El ejercicio transcurre en jornadas, y cada una tiene un tramo para '
    + 'deliberar y otro para ver lo que resultó. Lo que cambia una decisión no '
    + 'es la fecha, sino cuántas jornadas quedan.',

  cronometro:
    'El reloj de la sala. Arranca una sola vez desde la consola y a partir de '
    + 'ahí las jornadas se encadenan solas, con el mismo número en todas las '
    + 'pantallas.',

  fases:
    'Los dos tramos de cada jornada: uno para deliberar y ordenar, otro para '
    + 'leer las consecuencias. Los mandos de al lado son para lo imprevisto, no '
    + 'para llevar el ritmo.',

  // --- el territorio --------------------------------------------------------

  mapa:
    'Un país ficticio en dos niveles: las regiones teñidas según cuántos de sus '
    + 'puntos no dejan pasar nada, y un clic acerca cualquiera de ellas. Sitúa, '
    + 'no mide: ninguna distancia tomada sobre este mapa significa algo.',

  formas_mapa:
    'La forma de cada punto dice qué se está haciendo con él, que no es lo '
    + 'mismo que cómo llegó a estar así. El aro alrededor distingue una mesa '
    + 'que ha sesionado hoy de una instalada que hoy nadie ha convocado.',

  hechos_mapa:
    'Un anillo avisa de que en ese punto pasó algo desde la última vez que la '
    + 'sala miró, y se apaga solo en la ventana siguiente. Cuenta lo que se '
    + 'hizo, no dónde está la fuerza ahora.',

  corredores:
    'Las rutas por las que se abastece el país y lo que hoy dejan pasar. Un '
    + 'corredor vale lo que su peor punto, por muchos de los demás que estén '
    + 'abiertos.',

  panel_nodos:
    'Los puntos de cierre del país, uno por fila y el peor arriba. Pulse una '
    + 'fila para desplegar su detalle y señalar ese punto en el mapa.',

  semaforo:
    'Cómo está de abastecida cada región, en grano grueso y según el insumo que '
    + 'primero se le agote. El calendario fino lo lleva el Ministerio de '
    + 'Agricultura.',

  pliego:
    'El registro de lo que la mesa ha decidido y de quién respondió por cada '
    + 'cosa. Una decisión sin responsable se consigna igual, y queda marcada '
    + 'como tal.',

  // --- la esfera pública ----------------------------------------------------

  esfera:
    'Lo que se publica y se afirma, al margen de lo que el tablero tiene por '
    + 'cierto. Va al lado del tablero y no en otra pantalla, porque la '
    + 'distancia entre los dos solo se aprecia comparándolos.',

  encuadre:
    'El marco con el que la conversación pública está leyendo el episodio. La '
    + 'mesa lo cambia actuando, no declarándolo.',

  denuncias:
    'Denuncias graves cuya veracidad todavía no se ha establecido. Nada '
    + 'distingue una veraz de una falsa antes de ir a mirar, y quien va a mirar '
    + 'es el mismo equipo que verifica puntos.',

  generado_por:
    'De dónde sale el texto que se está leyendo. Sin llave de API el sistema '
    + 'usa plantillas y el ejercicio se desarrolla igual: ninguna decisión de '
    + 'la simulación está delegada a un modelo.',

  // --- la cartera de un rol -------------------------------------------------

  alerta_privada:
    'Lo más urgente que hay hoy en esta cartera. Se rehace en cada jornada.',

  repertorio:
    'Lo que esta cartera puede pedir hoy, con un color por acción según si '
    + 'sale, si sale con reparos o si todavía le falta algo. Dice qué falta, '
    + 'nunca qué conviene hacer.',

  consecuencias:
    'Lo que produjo la jornada, reunido en un solo sitio durante el tramo de '
    + 'noche. Enumera y no interpreta: qué significa cada cosa es de la mesa.',

  // --- la consola -----------------------------------------------------------

  ordenes:
    'Aquí se transcribe lo que la mesa acordó, tal como se dijo. La pantalla '
    + 'devuelve su interpretación para leerla en voz alta antes de que nada se '
    + 'ejecute.',

  plan_interpretado:
    'Cómo entendió el sistema la orden que se dictó, con los lugares y las '
    + 'unidades ya identificados. Es lo que se va a intentar, no lo que va a '
    + 'ocurrir.',

  riesgo_mostrado:
    'La banda de riesgo de que la operación termine en incidente tal como está '
    + 'planteada. Baja si se adoptan las salvaguardas que la mesa tiene a su '
    + 'alcance.',

  consulta:
    'Una respuesta de solo lectura, sacada del estado del ejercicio. Preguntar '
    + 'no gasta la jornada ni ordena nada.',

  omitidas:
    'Órdenes que estaban en el plan y no se ejecutaron porque les faltaba algo '
    + 'por resolver. Cada una aparece con su motivo, y basta volver a dictarla '
    + 'con el dato que le faltaba.',

  interpretado_por:
    'Qué capa tradujo la orden de lenguaje natural a acciones. Sin llave de API '
    + 'se emplea un intérprete determinista, y la validación y la ejecución son '
    + 'las mismas en los dos casos.',
}
