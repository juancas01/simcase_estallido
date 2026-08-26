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
 * `parte_privado` a la pantalla, ni siquiera cuando el motor gana un enum nuevo.
 */
export function rotulo(mapa, valor) {
  if (valor === null || valor === undefined) return '—'
  if (typeof mapa === 'string' || mapa === undefined) return prettificar(mapa ?? valor)
  return mapa[valor] ?? prettificar(valor)
}

// --- el territorio ---------------------------------------------------------

export const ESTADO_PUNTO = {
  abierto: 'Abierto',
  parcial: 'Parcial',
  cerrado: 'Cerrado',
  sin_verificar: 'Sin verificar',
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
  parte_privado: 'Parte privado',
  apertura: 'Apertura',
  deliberacion: 'Deliberación',
  ordenes: 'Órdenes',
  resolucion: 'Resolución',
  consecuencias: 'Consecuencias',
  registro: 'Registro',
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
// El rótulo dice qué HACE la acción, no cómo se clasifica. «Constitutiva» es
// vocabulario de diseño; «Constituye» es lo que le sirve a quien la va a pedir.

export const CLASE_ACCION = {
  constitutiva: 'Constituye',
  operativa: 'Toca el mundo',
  informativa: 'Informa',
}

export const CHIP_CLASE = {
  constitutiva: 'neutro',
  operativa: 'bien',
  informativa: 'medio',
}

// --- la fuerza -------------------------------------------------------------

export const TIPO_UNIDAD = {
  esmad: 'ESMAD',
  policia: 'Policía',
  militar: 'Militar',
}
