// ---------------------------------------------------------------------------
// LOS RÓTULOS — cómo se escribe en pantalla lo que el motor llama por su nombre.
//
// El motor usa identificadores estables y opacos: `sin_verificar`, `ambar`,
// `parte_privado`, `concertacion`. Está bien que lo haga —son claves, no prosa—
// pero pintarlos tal cual deja el tablero lleno de guiones bajos, minúsculas y
// palabras sin tilde. En una pared proyectada eso se lee como un descuido.
//
//     El identificador es del motor. El rótulo es de la sala.
//
// Vive en un solo archivo por la misma razón que las definiciones: un rótulo en
// dos sitios se desincroniza. Y `rotulo()` degrada bien — si mañana el motor
// añade un valor que aquí no está, sale «Valor nuevo» y no `valor_nuevo`.
// ---------------------------------------------------------------------------

/** Sustituto digno para un valor que aún no tiene rótulo propio. */
function prettificar(valor) {
  const s = String(valor).replace(/_/g, ' ').trim()
  return s ? s[0].toUpperCase() + s.slice(1) : s
}

/**
 * El rótulo de un valor. Si el mapa no lo conoce, lo compone: nunca sale un
 * `sin_verificar` a la pantalla, ni siquiera cuando el motor gana un enum nuevo.
 *
 * ADMITE UN SOLO ARGUMENTO, y ahí estaba el peor fallo que ha tenido esta
 * interfaz. `rotulo('Puente Amarillo')` tenía que capitalizar y devolver el
 * texto; devolvía **un guion**, porque la primera guarda miraba `valor` —que
 * con un solo argumento es `undefined`— antes de darse cuenta de que el
 * argumento único ERA el valor.
 *
 * Y así es como se formatea cada celda de texto de las nueve vistas privadas.
 * El resultado no era un error visible: era que **el nombre de cada punto, cada
 * corredor, cada región y cada estado salía como «—»** en la pantalla de su
 * titular. Ocho tablas llenas de guiones, que es lo que se ve como una pantalla
 * en blanco desde el otro lado de la sala.
 *
 * La forma de fallar importa tanto como el fallo: no reventó nada, no salió en
 * ninguna traza, y las pruebas del motor pasaban todas — porque el motor
 * entregaba bien los nombres y era la última capa la que los borraba.
 */
export function rotulo(mapa, valor) {
  // Un solo argumento: ese argumento ES el valor, y no hay mapa que consultar.
  const soloValor = valor === undefined && typeof mapa !== 'object'
  const v = soloValor ? mapa : valor
  const tabla = soloValor ? null : mapa

  if (v === null || v === undefined) return '—'
  if (!tabla) return prettificar(v)
  return tabla[v] ?? prettificar(v)
}

// --- el territorio ---------------------------------------------------------

export const ESTADO_PUNTO = {
  abierto: 'Abierto',
  parcial: 'Parcial',
  cerrado: 'Cerrado',
  sin_verificar: 'Sin verificar',
}

// QUÉ SE ESTÁ HACIENDO EN UN PUNTO. No es lo mismo que cómo se abrió: de los
// puntos cerrados —la mayoría durante casi todo el ejercicio— `modo_apertura` no
// dice nada, y un punto operado que no cedió no es un punto que nadie ha tocado.
export const INTERVENCION = {
  fuerza: 'Intervenido a la fuerza',
  negociacion: 'En negociación',
  ninguna: 'Sin intervención',
}

// La misma distinción, en una palabra, para las celdas estrechas.
export const INTERVENCION_CORTA = {
  fuerza: 'Fuerza',
  negociacion: 'Negociación',
  ninguna: 'Nada',
}

export const CRITICIDAD = {
  vital: 'Vital',
  alta: 'Alta',
  media: 'Media',
}

export const TIPO_INFRA = {
  energia: 'Energía',
  salud: 'Salud',
  agua: 'Agua',
  alimentos: 'Alimentos',
  logistica: 'Logística',
  telecom: 'Telecomunicaciones',
}

export const MODO_APERTURA = {
  cerrado: 'Cerrado',
  fuerza: 'Fuerza',
  concertacion: 'Concertación',
  desgaste: 'Desgaste',
}

export const SEMAFORO = {
  verde: 'Verde',
  ambar: 'Ámbar',
  rojo: 'Rojo',
}

// --- el tiempo -------------------------------------------------------------

export const FRANJA = { dia: 'Día', noche: 'Noche' }

export const FASE = {
  dia: 'Día · se ordena',
  noche: 'Noche · sin órdenes',
}

// --- la esfera pública -----------------------------------------------------

export const FUENTE = {
  prensa_nacional: 'Prensa nacional',
  prensa_internacional: 'Prensa internacional',
  redes: 'Redes sociales',
  comite_del_paro: 'Comité Nacional del Paro',
  gremios: 'Gremios',
  alcaldes_entorno: 'Alcaldes de entorno',
}

export const POSICION_GREMIOS = {
  fuera: 'Fuera del paro',
  evaluando: 'Evaluando',
  sumados: 'Sumados al paro',
}

export const ESTADO_DENUNCIA = {
  'sin verificar': 'Sin verificar',
  verificada: 'Verificada',
  'declarada en verificación': 'Declarada en verificación',
}

// --- las acciones ----------------------------------------------------------
//
// TRES CATEGORÍAS, Y CADA UNA SE LLAMA POR SU NOMBRE CORRIENTE. «Constitutiva»,
// «operativa» e «informativa» son vocabulario de diseño y siguen siendo lo que
// el motor escribe en `clase`; lo que llega a la pantalla es la palabra que
// cualquiera entiende sin que se la expliquen:
//
//   Protocolo    cambia cómo trabaja la mesa · rinde en todo lo que venga
//   Operación    toca el mundo — el territorio, la fuerza, el abastecimiento
//   Información  cambia lo que el país tiene por cierto
//
// El motor no cambia de vocabulario porque la distinción es de diseño y está
// documentada como tal; la pantalla sí, porque quien la lee llegó esta mañana.

export const CLASE_ACCION = {
  constitutiva: 'Protocolo',
  operativa: 'Operación',
  informativa: 'Información',
}

// LOS TRES VAN EN NEUTRO, A PROPÓSITO. Antes eran verde, ámbar y gris, los
// mismos tres colores que la columna «Hoy» usa al lado para decir si la acción
// sale o no sale — y dos semáforos contiguos que significan cosas distintas se
// leen como uno solo mal calibrado. Un tipo no es mejor ni peor que otro: lo
// distingue la palabra. El único semáforo de la tabla es el de la primera
// columna.
export const CHIP_CLASE = {
  constitutiva: 'neutro',
  operativa: 'neutro',
  informativa: 'neutro',
}

// --- el semáforo del repertorio --------------------------------------------
//
// El rótulo dice qué puede hacer su titular, no cómo se llama el estado en el
// motor. «Bloqueada» describe la acción; «Aún no» describe la jornada — y quien
// lee su repertorio está decidiendo qué pedir en esta jornada.

export const DISPONIBILIDAD = {
  disponible: 'Se puede pedir',
  condicionada: 'Con reparos',
  bloqueada: 'Aún no',
  hecha: 'Ya vigente',
}

export const CHIP_DISPONIBILIDAD = {
  disponible: 'bien',
  condicionada: 'medio',
  bloqueada: 'mal',
  hecha: 'neutro',
}

// --- los hechos de la jornada ----------------------------------------------
//
// Lo que el motor emite como `{"tipo": "acuerdo_incumplido"}` se lee en la pared
// durante los dos minutos de noche. `Acuerdo incumplido` ya sería legible;
// «Se incumplió un acuerdo» es lo que alguien diría en voz alta.

export const EVENTO = {
  operacion: 'Se operó un punto',
  apertura: 'Se abrió un punto',
  reapertura: 'Un punto volvió a cerrarse',
  desgaste: 'Un punto cedió por desgaste',
  paso_seguro: 'Se acordó un paso seguro',
  punto_verificado: 'Una dupla verificó un punto',
  acuerdo_incumplido: 'Se incumplió un acuerdo',
  acuerdo_cumplido: 'Se cumplió un acuerdo',
  incidente_mortal: 'Incidente con víctima',
  imagen_viral: 'Imagen viral',
  militares_en_multitudes: 'Militares frente a multitudes',
  jornada_nacional: 'Jornada nacional de movilización',
  escolta_lograda: 'Escolta lograda',
  escolta_atacada: 'Escolta atacada',
  nodo_nuevo: 'Apareció un cierre nuevo',
  denuncia_estallo: 'Una denuncia estalló afuera',
  ultimatum_gremios: 'Ultimátum de los gremios',
  gremios_se_suman: 'Los gremios se suman al paro',
  comite_suspende: 'El Comité suspende su participación',
  comite_vuelve: 'El Comité vuelve a sentarse',
  comite_se_retira_definitivo: 'El Comité se retira en definitiva',
  turno_sin_decision: 'La jornada pasó sin órdenes',
  mesa_congelada: 'Una mesa se quedó sin sesionar',
  duda_permanencia: 'La Defensoría duda de su permanencia',
  movilizacion: 'Se movió la presión en la calle',
  condicional_caducada: 'Una orden condicional caducó',
  condicional_descartada: 'Una orden condicional se descartó',
  corredor_humanitario_requerido: 'Se requirió paso humanitario',
  caravana: 'Salió una caravana',
  defensoria_aislada: 'La mesa aisló a la Defensoría',
  clase_alimentaria: 'Los alimentos ganaron turno propio',
  acopio_concentrado: 'Salió un despacho concentrado de alimentos',
  instrumentos_sectoriales: 'Se activaron alivios al campo',
  balance_perdida: 'Se publicó la pérdida del campo',
  cifra_sectorial_disputada: 'La cifra del campo se disputa',
  contraparte_no_social: 'Se pactó con quien no era una comunidad',
}

// --- la fuerza -------------------------------------------------------------

export const TIPO_UNIDAD = {
  esmad: 'ESMAD',
  policia: 'Policía',
  militar: 'Militar',
}

// --- el canal de órdenes ---------------------------------------------------
//
// En qué punto del cauce se quedó una acción. `no_viable` y `falta_dato` no son
// lo mismo y la distinción importa: una no se puede pedir, la otra sí en cuanto
// se complete un dato.

export const ESTADO_PLAN = {
  lista: 'Lista',
  falta_dato: 'Falta un dato',
  ambigua: 'Ambigua',
  no_viable: 'No viable',
}

// Los campos de la hoja de datos. Las claves del motor son estables y feas; en
// pantalla se leen a distancia.

export const CAMPO_CONSULTA = {
  ambito: 'Ámbito',
  aviso: 'Aviso',
  esmad_total: 'ESMAD, total',
  esmad_sin_comprometer: 'ESMAD sin comprometer',
  fatiga_media: 'Fatiga media',
  instalaciones_bajo_custodia: 'Instalaciones bajo custodia',
  asistencia_militar: 'Asistencia militar',
  corredores: 'Corredores',
  regiones: 'Regiones',
  reservas: 'Reservas',
  comite_disponible: 'Comité disponible',
  posicion_gremios: 'Posición de los gremios',
  banderas_activas: 'Banderas activas',
}

// ---------------------------------------------------------------------------
// LA TINTA DE CADA CORREDOR
//
// Vive aquí y no en `Mapa.jsx` porque la usan dos superficies —el mapa dibuja la
// línea y la tabla de al lado pinta su cuadradito— y este archivo es justamente
// el sitio de las traducciones de identificador del motor a algo de pantalla.
//
// De paso, `Mapa.jsx` se queda exportando solo componentes, que es lo que la
// regla `react-refresh/only-export-components` pide.
// ---------------------------------------------------------------------------

export const COLOR_CORREDOR = {
  'C-PUE': '#7fa3d8',
  'C-SUR': '#5fb08c',
  'C-HOS': '#b389cf',
  'C-REF': '#cfa055',
  'C-NOR': '#6cb4c2',
}
