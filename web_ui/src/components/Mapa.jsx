// ---------------------------------------------------------------------------
// EL MAPA — dos niveles: el país y la región.
//
// Sustituye al esquema de líneas. Aquel decía la verdad sobre la topología —un
// corredor ES una secuencia ordenada de puntos— y no decía nada sobre el país:
// once motas sobre un lienzo vacío, sin costa, sin puerto y sin forma. Una sala
// que mira eso durante trece minutos no llega a preguntarse dónde está.
//
//     NIVEL 1 · EL PAÍS
//     Valcanto entera, con sus dos mares, su puerto y sus cuatro regiones.
//     Cada región va teñida de su ESTADO DE BLOQUEO, y al posarse encima
//     entrega las seis lecturas promediadas de sus puntos.
//
//     La SILUETA Y LA RED VIAL son reales —datos abiertos de una costa que no
//     consta en ninguna parte, igual que Macondo se dibujó sobre Mocoa— y las
//     regiones se dibujan encima. Un contorno inventado a mano se nota: las
//     costas tienen estuarios, cabos y entrantes que nadie dibuja por
//     intuición, y lo que hace falta es que la sala mire un país y no un
//     diagrama. El territorio sigue siendo ficticio; lo prestado es el trazo.
//
//     NIVEL 2 · LA REGIÓN
//     Un clic hace zoom. Ahí aparecen sus puntos con nombre, los corredores
//     que la cruzan, y cada punto entrega sus seis lecturas propias.
//
//
// LA RED VIAL VA CASI TRANSPARENTE, Y ESO ES EL DISEÑO
// ====================================================
// Las carreteras no son la información: son el suelo sobre el que se lee la
// información. Lo que tiene que resaltar son los corredores y los puntos de
// cierre, y para eso la rejilla vial tiene que estar —un bloqueo flotando sobre
// un polígono de color no se lee como un bloqueo de carretera— y tiene que
// callarse. Tres grosores y una opacidad baja.
//
// Y LOS CORREDORES VAN POR DONDE VA LA CARRETERA. Antes se unían sus puntos con
// una Bézier suave, y esa curva afirmaba algo falso: que entre un bloqueo y el
// siguiente la vía pasa por ahí. Ahora cada corredor trae su trazado ruteado
// sobre la red real (`geografia.trazados`), así que dos puntos que en línea
// recta parecen vecinos pueden estar a media vuelta por carretera — y el mapa
// lo enseña en vez de esconderlo.
//
//
// QUÉ SE ESTÁ HACIENDO EN CADA PUNTO
// ==================================
// La forma del punto ya no dice cómo se abrió: dice **qué se está haciendo con
// él**, que es la pregunta que la sala tiene delante.
//
//     ◆ rombo      se intervino a la fuerza — cediera o no cediera
//     ■ cuadrado   hay mesa instalada, o está abierto porque se pactó
//     ● círculo    no se está haciendo nada en absoluto
//
// El cambio no es cosmético. `modo_apertura` solo se escribe cuando el punto
// cede, así que de los puntos cerrados —la mayoría durante casi todo el
// ejercicio— no decía nada: un punto operado con ESMAD que no cedió y un punto
// que nadie ha tocado salían con la misma forma y el mismo color, y son dos
// conversaciones distintas.
//
// Y UNA MESA INSTALADA LLEVA SU MARCA, con un hueco si hoy no ha sesionado: una
// mesa local hay que instalarla cada jornada para que surta efecto, y no
// instalarla un día equivale a congelar la negociación.
//
//
// LAS CIFRAS NO SE CALCULAN AQUÍ
// ==============================
// Ni una. Las bandas de cada punto y los promedios de cada región vienen
// resueltos del motor, en `puntos[i].lectura` y `regiones[i].lectura`. Este
// archivo dibuja.
//
// Es una consecuencia directa de `PENDIENTES.md · B9`: una línea de la capa de
// presentación vació las vistas privadas y las 163 pruebas pasaron enteras,
// porque nada de lo que la interfaz calcula por su cuenta está cubierto por una
// prueba. Un promedio por región calculado en JavaScript es un promedio que
// nadie verifica nunca. En `territory.py` sí.
//
//
// QUÉ SE CONSERVA DEL ESQUEMA, Y POR QUÉ
// --------------------------------------
//   · LA FORMA DICE CÓMO SE ABRIÓ.  Rombo lo abierto por la fuerza, cuadrado lo
//     pactado. No valen lo mismo: uno vuelve a cerrarse esta noche.
//   · EL ANILLO DICE QUÉ PASÓ ANOCHE.  El cambio, no el nivel.
//   · LA INTERROGACIÓN DICE QUE NADIE HA MIRADO.  Es una petición de decisión
//     proyectada en la pared, y hay alguien en la mesa que puede resolverla.
//   · NOMBRES, NO CÓDIGOS.  «Puente Amarillo» se señala en voz alta desde el
//     fondo de la sala; `N003` hay que traducirlo primero.
//
// TRES GUARDARRAÍLES
//   1 · No hay escala ni distancias reales. El país es inventado y del todo: la
//       geometría sitúa, no mide, y no hay tiempos de desplazamiento en el motor.
//   2 · No muestra lo que el tablero no muestra: ni la mezcla real de un punto,
//       ni si una denuncia es cierta. Tampoco por la puerta de atrás de una banda.
//   3 · No dice dónde está la fuerza. Eso es de la Dirección General de la
//       Policía, y en el tablero dejaría sin oficio a uno de los siete.
// ---------------------------------------------------------------------------

import Ayuda from './Ayuda'
import { D } from '../definiciones.jsx'
import {
  COLOR_CORREDOR, ESTADO_PUNTO, INTERVENCION, INTERVENCION_CORTA, banda, rotulo,
} from '../etiquetas.jsx'

// LA PALETA, BAJADA DE TONO. La primera versión usaba los colores del tablero a
// plena saturación sobre un fondo casi negro, y a tamaño de pared eso vibra: los
// bordes cortan, los rellenos pelean con las líneas y el ojo no sabe dónde
// posarse. Un mapa de situación tiene que poder mirarse trece minutos seguidos.
//
// El orden de contraste es el mismo de siempre —lo que hay que ver primero es lo
// más claro— pero el rango se comprime y la diferencia la hacen el tono y la
// forma, no el brillo.

const MAR = { hondo: '#0a151f', llano: '#0e1d2a', orilla: '#1c4560' }
const TIERRA = { alto: '#1b222c', bajo: '#151a22' }

const COLOR_ESTADO = {
  abierto: '#5fb08c',
  parcial: '#cfa055',
  cerrado: '#cf7079',
  sin_verificar: '#6b7688',
}

// QUÉ SE ESTÁ HACIENDO decide la FORMA del punto. No es `modo_apertura`: eso
// solo habla de los puntos abiertos. Lo calcula `territory.intervencion_nodo`.
const FORMA = { fuerza: 'fuerza', negociacion: 'pactado', ninguna: 'nada' }

// LA RED VIAL, casi transparente. Es el suelo, no la información.
const VIA = {
  autopista: { ancho: 0.62, opacidad: 0.30 },
  troncal: { ancho: 0.42, opacidad: 0.24 },
  primaria: { ancho: 0.28, opacidad: 0.18 },
}
const TINTA_VIA = '#8ea3bd'

// La infraestructura relevante. Protegida y sin proteger se distinguen a
// simple vista: es lo único que la sala decide sobre ella.
const INFRA = {
  energia: 'M -1.4 1.4 L 0.2 -0.3 L -0.4 -0.3 L 1.2 -1.6',
  salud: 'M -1.3 0 h 2.6 M 0 -1.3 v 2.6',
  agua: 'M 0 -1.5 C 1.4 -0.2 1.2 1.4 0 1.4 C -1.2 1.4 -1.4 -0.2 0 -1.5',
  alimentos: 'M -1.2 1.2 h 2.4 M -1.2 1.2 L 0 -1.3 L 1.2 1.2',
  logistica: 'M -1.4 -0.8 h 2.8 v 1.7 h -2.8 z',
  telecom: 'M 0 1.4 v -2.8 M -1.1 -0.4 L 0 -1.5 L 1.1 -0.4',
}

// El estado de bloqueo tiñe la región. NO es el semáforo de abastecimiento: una
// región puede estar despejada y quedarse sin oxígeno porque su corredor empieza
// en otra. Que sean dos lecturas distintas es justamente el punto, y por eso el
// abastecimiento va aparte, en su chip.
const TINTA_BLOQUEO = ['#5fa87f', '#8fa869', '#c9a05a', '#c2707a']

const HECHO = {
  operacion: { rango: 2, color: '#cfa055', texto: 'se operó' },
  operacion_grave: { rango: 3, color: '#cf7079', texto: 'se operó, con incidente' },
  reapertura: { rango: 3, color: '#cf7079', texto: 'volvió a cerrarse de noche' },
  acuerdo_incumplido: { rango: 3, color: '#cf7079', texto: 'el acuerdo se incumplió' },
  apertura: { rango: 1, color: '#5fb08c', texto: 'se abrió' },
  desgaste: { rango: 1, color: '#5fb08c', texto: 'se abrió por desgaste' },
  paso_seguro: { rango: 1, color: '#5fb08c', texto: 'se acordó paso seguro' },
  punto_verificado: { rango: 0, color: '#7099cf', texto: 'lo verificó un equipo de terreno' },
}

const UNIDAD = { esmad: 'ESMAD', policia: 'Policía', militar: 'Ejército' }

const claveDe = h => (h.tipo === 'operacion' && h.incidente ? 'operacion_grave' : h.tipo)

/** El anillo se pinta del hecho MÁS GRAVE. Los demás se cuentan en el globo. */
function anilloDe(hechos) {
  let peor = null
  for (const h of hechos || []) {
    const d = HECHO[claveDe(h)]
    if (d && (!peor || d.rango > peor.rango)) peor = d
  }
  return peor
}

function frasesDe(hechos) {
  return (hechos || []).map(h => {
    const d = HECHO[claveDe(h)]
    if (!d) return null
    if (h.tipo === 'operacion') {
      return `${d.texto} con ${UNIDAD[h.unidad] || h.unidad}`
    }
    if (h.tipo === 'apertura' && h.via) return `${d.texto} por ${h.via}`
    return d.texto
  }).filter(Boolean)
}

// ---------------------------------------------------------------------------
// Geometría de pantalla
// ---------------------------------------------------------------------------

const trazo = pts => pts.map((p, i) => `${i ? 'L' : 'M'} ${p[0]} ${p[1]}`).join(' ')
const cerrado = pts => `${trazo(pts)} Z`

/**
 * La misma polilínea, curvada (Catmull-Rom pasada a Bézier cúbica).
 *
 * Un corredor dibujado con segmentos rectos hace codos de noventa grados en cada
 * punto de cierre, y **el codo dice algo que no es cierto**: que ahí la carretera
 * gira. No gira; ahí hay un bloqueo. Curvando, la línea vuelve a leerse como lo
 * que representa —una vía— y el punto vuelve a ser lo que interrumpe la vía.
 *
 * `tension` a 0,5 da el trazo suave estándar. Más alto se pasa de rosca y la
 * curva se sale de sus propios puntos.
 */
function curva(pts, tension = 0.5) {
  if (pts.length < 3) return trazo(pts)
  const d = [`M ${pts[0][0]} ${pts[0][1]}`]
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i]
    const p1 = pts[i]
    const p2 = pts[i + 1]
    const p3 = pts[i + 2] || p2
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension]
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension]
    d.push(`C ${c1[0].toFixed(2)} ${c1[1].toFixed(2)} `
      + `${c2[0].toFixed(2)} ${c2[1].toFixed(2)} ${p2[0]} ${p2[1]}`)
  }
  return d.join(' ')
}

/**
 * El nombre de un punto, en una o dos líneas.
 *
 * «Acceso Hospital Universitario» son veintinueve caracteres: puesto en una sola
 * línea ocupa un tercio del ancho del país y se monta sobre sus dos vecinos. La
 * alternativa era darle a cada punto un nombre corto para el mapa, y eso son dos
 * nombres para la misma cosa —uno en la pared y otro en el eco de la consola—,
 * que es justo lo que este repositorio no hace. Se parte por el hueco más
 * cercano a la mitad y el nombre sigue siendo uno.
 */
function partir(nombre) {
  if (nombre.length <= 15) return [nombre]
  const palabras = nombre.split(' ')
  if (palabras.length < 2) return [nombre]
  let mejor = 1
  for (let i = 1; i < palabras.length; i++) {
    const izq = palabras.slice(0, i).join(' ').length
    const der = palabras.slice(i).join(' ').length
    if (Math.abs(izq - der) < Math.abs(
      palabras.slice(0, mejor).join(' ').length
      - palabras.slice(mejor).join(' ').length)) mejor = i
  }
  return [palabras.slice(0, mejor).join(' '), palabras.slice(mejor).join(' ')]
}

/** Punto dentro de polígono, por lanzamiento de rayo. Solo para decidir si una
    vía pertenece a la región ampliada: la aritmética que la sala lee viene
    resuelta del motor, y aquí no se calcula ninguna cifra. */
function dentroDe(p, poligono) {
  if (!poligono) return false
  let dentro = false
  for (let i = 0, j = poligono.length - 1; i < poligono.length; j = i++) {
    const [xi, yi] = poligono[i]
    const [xj, yj] = poligono[j]
    if ((yi > p[1]) !== (yj > p[1])
        && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) dentro = !dentro
  }
  return dentro
}

function caja(poligono) {
  const xs = poligono.map(p => p[0])
  const ys = poligono.map(p => p[1])
  return { x: Math.min(...xs), y: Math.min(...ys),
           w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) }
}

/**
 * El encuadre: cuánto acercar y hacia dónde, para que una región llene la vista.
 *
 * Se aplica como `transform` sobre un grupo y NO cambiando el `viewBox`, porque
 * un `viewBox` no se puede animar con CSS y un salto seco de encuadre en una
 * pantalla proyectada desorienta a la sala entera: nadie sabe si lo que está
 * viendo es otro sitio o el mismo más cerca.
 */
// ---------------------------------------------------------------------------
// DÓNDE VA CADA RÓTULO
//
// Los once puntos del escenario están colocados a mano y no se pisan. Pero el
// motor **genera cierres nuevos donde quiere** cuando la intensidad sube
// (`mobilization._generar_nodo`), y en la quinta jornada Bellaflor puede tener
// nueve puntos en el mismo racimo. Colocar los rótulos a ojo sirve para el
// escenario inicial y no sirve para la jornada 5, que es cuando la sala más
// necesita leerlos.
//
// Se colocan por sitio libre: cada rótulo prueba pisos por encima de su punto y
// se queda en el primero que no toque nada ya puesto. Lo que ya está puesto son
// los rótulos de los corredores y los de los puntos anteriores.
//
// EL ORDEN ES FIJO —de arriba abajo, y a igual altura de izquierda a derecha—
// así que con los mismos puntos sale siempre la misma colocación. En una
// pantalla que se repinta cada dos segundos eso importa más que la colocación
// óptima: un rótulo que cambia de sitio solo se lee como un fallo de la pantalla.
//
// Todo en UNIDADES DE PANTALLA, que es donde ocurre el choque. En unidades del
// mapa, dos puntos que con el zoom del país están a tres unidades pueden estar a
// doce con el zoom de una región, y el mismo cálculo daría dos respuestas.
// ---------------------------------------------------------------------------

const ANCHO_CARACTER = 0.55        // del tamaño de letra. Basta para no chocar.
const ALTO_LINEA = 2.5
const PISO = 5.8                   // cuánto sube el rótulo al no caber

function anchoDe(lineas, tam) {
  return Math.max(...lineas.map(l => l.length)) * ANCHO_CARACTER * tam
}

function cajaTexto(lineas, cx, cy, tam, ancla) {
  const w = anchoDe(lineas, tam)
  const x0 = ancla === 'middle' ? cx - w / 2 : ancla === 'end' ? cx - w : cx
  return { x0, x1: x0 + w, y0: cy - tam * 0.85, y1: cy + (lineas.length - 1) * ALTO_LINEA + tam * 0.3 }
}

const chocan = (a, b) =>
  !(a.x1 <= b.x0 || b.x1 <= a.x0 || a.y1 <= b.y0 || b.y1 <= a.y0)

/**
 * Dónde se rotula la línea de un corredor: en su último punto.
 *
 * Con el zoom puesto, en el último que está DENTRO de la región ampliada. Un
 * corredor que sale de Bellaflor termina en Puerto Espejo, y su nombre se
 * quedaba fuera del encuadre: el recorte del lienzo se lo comía y la sala veía
 * cuatro líneas de colores sin nombre justo en el nivel donde hacen falta.
 */
function anclaDe(c, porId, zoom) {
  const nodos = (c.nodos || []).map(id => porId[id]).filter(Boolean)
  if (nodos.length < 2) return null
  let i = nodos.length - 1
  if (zoom) {
    const dentro = nodos.map((n, j) => (n.region_id === zoom ? j : -1)).filter(j => j >= 0)
    if (dentro.length) i = dentro[dentro.length - 1]
  }
  const fin = nodos[i]
  const otro = nodos[i > 0 ? i - 1 : 1]
  // Al lado por el que la línea NO sigue, para no tumbarse sobre ella.
  return { nombre: c.nombre, x: fin.x, y: fin.y, region_id: fin.region_id,
           derecha: fin.x >= otro.x }
}

/**
 * Devuelve `{[nodo_id]: piso}` en unidades de pantalla, esquivando `obstaculos`.
 */
function colocar(puntos, k, obstaculos) {
  const puestos = [...obstaculos]
  const out = {}
  for (const q of [...puntos].sort((a, b) => a.y - b.y || a.x - b.x)) {
    const lineas = partir(q.nombre)
    const ancla = q.x > 78 ? 'end' : q.x < 14 ? 'start' : 'middle'
    const dx = ancla === 'end' ? 2.6 : ancla === 'start' ? -2.6 : 0
    const base = lineas.length > 1 ? 5.9 : 3.8

    let piso = 0
    for (; piso < 4; piso++) {
      const caja = cajaTexto(lineas, k * q.x + dx, k * q.y - base - piso * PISO,
                             2.35, ancla)
      if (!puestos.some(o => chocan(caja, o))) { puestos.push(caja); break }
      if (piso === 3) puestos.push(caja)
    }
    out[q.nodo_id] = Math.min(piso, 3)
  }
  return out
}

function encuadre(poligono, lienzo) {
  if (!poligono) return { k: 1, tx: 0, ty: 0 }
  const b = caja(poligono)
  const margen = 6
  const k = Math.min(4, Math.min(lienzo / (b.w + margen * 2), lienzo / (b.h + margen * 2)))
  return {
    k,
    tx: lienzo / 2 - k * (b.x + b.w / 2),
    ty: lienzo / 2 - k * (b.y + b.h / 2),
  }
}

const LIENZO = 100

// ---------------------------------------------------------------------------

export default function Mapa({
  tablero, seleccionado, onSeleccionar, zoom, onZoom, sobre, onSobre,
}) {
  const setZoom = onZoom
  const setSobre = onSobre

  const geo = tablero?.geografia
  if (!tablero?.puntos?.length || !geo?.regiones) return null

  const puntos = tablero.puntos
  const porId = Object.fromEntries(puntos.map(p => [p.nodo_id, p]))
  const corredores = tablero.corredores || []
  const regiones = Object.fromEntries((tablero.regiones || []).map(r => [r.region_id, r]))
  const hechos = tablero.hechos || {}
  const infraestructura = tablero.infraestructura || []

  const { k, tx, ty } = encuadre(zoom ? geo.regiones[zoom] : null, LIENZO)
  const esc = 1 / k                            // lo que debe medir siempre igual

  const pais = geo.contorno || []
  const dPais = cerrado(pais)

  // Con el zoom puesto, los sitios de las OTRAS regiones quedan medio fuera del
  // encuadre: media palabra pegada al borde del lienzo, que se lee como un fallo
  // de dibujo y no como un puerto que está en otra parte.
  const sitios = (geo.sitios || []).filter(s => !zoom || s.region_id === zoom)

  // Los rótulos de los corredores se ponen primero y los de los puntos los
  // esquivan. El orden importa: un corredor tiene un solo sitio posible —donde
  // acaba su línea— y un punto tiene cuatro.
  const anclas = Object.fromEntries(corredores
    .map(c => [c.corredor_id, anclaDe(c, porId, zoom)])
    .filter(([, a]) => a && (!zoom || a.region_id === zoom)))
  // Lo que ya tiene su sitio y no lo puede mover: el rótulo de cada corredor
  // —que solo cabe donde acaba su línea— y el del puerto. Los nombres de los
  // puntos se colocan DESPUÉS y los esquivan, porque un punto tiene cuatro
  // pisos donde caber y estos dos no tienen ninguno.
  const obstaculos = [
    ...(zoom ? Object.values(anclas).map(a => cajaTexto(
      [a.nombre], k * a.x + (a.derecha ? 3.4 : -3.4), k * a.y + 4.6, 2.2,
      a.derecha ? 'start' : 'end')) : []),
    ...sitios.filter(s => s.tipo !== 'ciudad').map(s => cajaTexto(
      [s.nombre], k * s.x, k * s.y - 4.4, 2.1, 'middle')),
    ...(zoom ? [] : sitios.filter(s => s.tipo === 'ciudad').map(s => cajaTexto(
      [s.nombre.toUpperCase()], k * s.x, k * (s.y - (s.radio || 12)) - 1.6,
      2.5, 'middle'))),
  ]
  const piso = colocar(zoom ? puntos.filter(p => p.region_id === zoom) : puntos,
                       k, obstaculos)

  function abrirRegion(id) {
    setZoom(zoom === id ? null : id)
    onSeleccionar?.(null)
  }

  return (
    <div className="mapa">
      <div className="eyebrow mapa-titulo">
        <span>
          {zoom ? regiones[zoom]?.nombre : geo.pais}
          <Ayuda etiqueta="Qué representa este mapa">{D.mapa}</Ayuda>
        </span>
        {zoom ? (
          <button className="mapa-volver" onClick={() => { setZoom(null); onSeleccionar?.(null) }}>
            ← {geo.pais}
          </button>
        ) : (
          <span className="mapa-pista">Toque una región para acercarse</span>
        )}
      </div>

      {/* EL LIENZO VIVE EN SU PROPIA CAJA, y esa caja es la que se estira.
          El SVG se posiciona en absoluto para llenar el hueco que sobre; si el
          bloque relativo que lo contiene es toda la columna del mapa —como lo
          era— el lienzo se extiende POR ENCIMA del título, de la ficha y de la
          leyenda, y esas tres se ven por debajo del dibujo. El contenedor
          relativo tiene que abrazar al lienzo y a nada más. */}
      <div className="mapa-lienzo">
        <svg
          viewBox={`-4 -3 ${LIENZO + 8} ${LIENZO + 7}`}
          className="mapa-svg"
          preserveAspectRatio="xMidYMid meet"
          role="img"
          aria-label={zoom
            ? `Mapa de ${regiones[zoom]?.nombre}, con sus puntos de cierre y sus corredores`
            : `Mapa de ${geo.pais}: cuatro regiones y once puntos de cierre`}
          onMouseLeave={() => setSobre(null)}
        >
          {/* --- el mar ------------------------------------------------------
              Un degradado y cuatro halos siguiendo el litoral, cada uno más ancho
              y más tenue. Es el recurso cartográfico de toda la vida y hace dos
              cosas a la vez: dice dónde acaba la tierra, y dice por dónde entra lo
              que entra. */}
          <defs>
            <linearGradient id="mapa-mar" x1="0" y1="0" x2="0.35" y2="1">
              <stop offset="0%" stopColor={MAR.llano} />
              <stop offset="100%" stopColor={MAR.hondo} />
            </linearGradient>
            <linearGradient id="mapa-tierra" x1="0" y1="0" x2="0.2" y2="1">
              <stop offset="0%" stopColor={TIERRA.alto} />
              <stop offset="100%" stopColor={TIERRA.bajo} />
            </linearGradient>
            {/* El halo de la costa, difuminado de verdad. Cuatro trazos duros
                concéntricos se ven como cuatro trazos duros concéntricos. */}
            <filter id="mapa-difuso" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="1.1" />
            </filter>
            {/* Los puntos, despegados del relleno con una sombra en vez de con un
                borde negro. Un contorno oscuro de medio punto sobre un color
                saturado es el efecto «recorte de revista» que hacía brusco el
                dibujo entero. */}
            <filter id="mapa-relieve" x="-60%" y="-60%" width="220%" height="220%">
              <feDropShadow dx="0" dy={0.5 * esc} stdDeviation={0.5 * esc}
                            floodColor="#05090e" floodOpacity="0.75" />
            </filter>
            {/* La mancha urbana se recorta contra el país: Bellaflor es una ciudad
                de puerto y su casco llega al agua, así que el círculo tiene que
                verse mordido por el litoral en vez de flotar sobre el mar. */}
            <clipPath id="mapa-tierra-recorte">
              <path d={dPais} />
            </clipPath>
          </defs>

          <rect x={-4} y={-3} width={LIENZO + 8} height={LIENZO + 7} fill="url(#mapa-mar)" />

          <g transform={`translate(${tx} ${ty}) scale(${k})`}
             style={{ transition: 'transform 520ms cubic-bezier(.4,0,.2,1)' }}>

            <g filter="url(#mapa-difuso)" style={{ pointerEvents: 'none' }}>
              {[6.5, 4.0, 2.2].map((w, i) => (
                <path key={w} d={dPais} fill="none" stroke={MAR.orilla}
                      strokeWidth={w * esc} strokeOpacity={0.13 + i * 0.08}
                      strokeLinejoin="round" />
              ))}
            </g>
            <path d={dPais} fill="url(#mapa-tierra)" stroke="none" />

            {/* --- el agua de dentro ----------------------------------------
                El estuario que parte la ciudad epicentro. Va encima del relleno
                y debajo de todo lo demás: para repartir el territorio se rellena
                —un agujero dentro del país deja trozos que no son de ninguna
                región— y para dibujar se pinta con el color del mar. El estrecho
                se sigue viendo, que es lo que hace de esa ciudad un cuello de
                botella. */}
            {(geo.aguas || []).map((a, i) => (
              <path key={i} d={cerrado(a)} fill="url(#mapa-mar)"
                    stroke={MAR.orilla} strokeOpacity={0.5}
                    strokeWidth={0.3 * esc} strokeLinejoin="round"
                    style={{ pointerEvents: 'none' }} />
            ))}

            {/* --- las regiones -------------------------------------------- */}
            {Object.entries(geo.regiones).map(([id, poly]) => {
              const r = regiones[id] || {}
              const tinta = TINTA_BLOQUEO[r.lectura?.bloqueo?.peldano ?? 3]
              const apagada = zoom && zoom !== id
              const activa = !zoom && sobre?.tipo === 'region' && sobre.id === id

              return (
                <path
                  key={id}
                  d={cerrado(poly)}
                  fill={tinta}
                  fillOpacity={apagada ? 0.04 : activa ? 0.26 : 0.14}
                  stroke={tinta}
                  strokeOpacity={apagada ? 0.10 : activa ? 0.55 : 0.30}
                  strokeWidth={0.45 * esc}
                  strokeLinejoin="round"
                  style={{ cursor: 'pointer',
                           transition: 'fill-opacity 260ms ease, stroke-opacity 260ms ease' }}
                  onMouseEnter={() => setSobre({ tipo: 'region', id })}
                  onClick={() => abrirRegion(id)}
                />
              )
            })}

            {/* --- LA RED VIAL ----------------------------------------------
                Casi transparente, y a propósito: no es la información, es el
                suelo sobre el que se lee la información. Sin ella un bloqueo
                flota sobre un polígono de color y deja de leerse como lo que es
                —una carretera cortada—; con ella encima, la sala ve por dónde se
                mueve el país antes de mirar dónde está roto. */}
            <g style={{ pointerEvents: 'none' }}>
              {(geo.vias || []).map((v, i) => {
                const d = VIA[v.clase] || VIA.primaria
                const apagada = zoom && !v.puntos.some(
                  p => dentroDe(p, geo.regiones[zoom]))
                return (
                  <path key={i} d={trazo(v.puntos)} fill="none"
                        stroke={TINTA_VIA} strokeWidth={d.ancho * esc}
                        strokeOpacity={d.opacidad * (apagada ? 0.35 : 1)}
                        strokeLinecap="round" strokeLinejoin="round" />
                )
              })}
            </g>

            {/* --- el litoral y la frontera, encima del relleno -------------
                Dos trazos distintos porque son dos cosas distintas: por uno entra
                el combustible del país y por el otro no entra nada que el
                ejercicio modele. */}
            {(geo.tramos || []).map((t, i) => (
              <path key={i} d={trazo(t.puntos)} fill="none"
                    stroke={t.frontera ? '#414c5c' : '#43718f'}
                    strokeWidth={(t.frontera ? 0.4 : 0.75) * esc}
                    strokeOpacity={t.frontera ? 0.85 : 1}
                    strokeDasharray={t.frontera
                      ? `${0.4 * esc} ${1.5 * esc}` : undefined}
                    strokeLinejoin="round" strokeLinecap="round"
                    style={{ pointerEvents: 'none' }} />
            ))}

            {/* --- la ciudad epicentro: una mancha urbana, no un punto ------
                Seis de los once puntos están dentro de ella. Dibujados como seis
                motas sueltas sobre el campo, la tensión territorial del caso —lo
                que se ve por la ventana contra lo que solo existe en el tablero—
                no se ve por ninguna parte. */}
            {sitios.filter(s => s.tipo === 'ciudad').map(s => (
              <g key={s.id} clipPath="url(#mapa-tierra-recorte)"
                 style={{ pointerEvents: 'none' }}>
                <circle cx={s.x} cy={s.y} r={s.radio || 12}
                        fill="#dce4f0" fillOpacity={0.055} />
                <circle cx={s.x} cy={s.y} r={(s.radio || 12) * 0.62}
                        fill="#dce4f0" fillOpacity={0.045} />
                <circle cx={s.x} cy={s.y} r={s.radio || 12} fill="none"
                        stroke="#dce4f0" strokeOpacity={0.14}
                        strokeWidth={0.35 * esc} />
              </g>
            ))}

            {/* --- los corredores ------------------------------------------
                Que la línea se vea entera y el corredor esté cerrado es
                exactamente lo que hay que enseñar: vale lo que su peor punto. */}
            {corredores.map(c => {
              const nodos = (c.nodos || []).map(id => porId[id]).filter(Boolean)
              if (nodos.length < 2) return null
              const pasa = c.caudal > 0.05
              const tinta = COLOR_CORREDOR[c.corredor_id] || '#5b6478'
              // EL TRAZADO REAL, ruteado sobre la red vial. La curva suave entre
              // puntos era una afirmación falsa —que la carretera va por ahí— y
              // se queda solo como respaldo por si un corredor no trae trazado.
              const trazado = geo.trazados?.[c.corredor_id]
              const d = trazado?.length >= 2
                ? trazo(trazado)
                : curva(nodos.map(n => [n.x, n.y]))
              const suyo = !zoom || nodos.some(n => n.region_id === zoom)
              // Solo el de los corredores que pasan por la región ampliada. El de
              // los demás cae fuera del encuadre: media palabra pegada al borde
              // del lienzo, que se lee como un fallo de dibujo.
              const rotulo = anclas[c.corredor_id]

              return (
                <g key={c.corredor_id} style={{ pointerEvents: 'none' }}
                   opacity={suyo ? 1 : 0.22}>
                  {/* Un trazo oscuro por debajo separa la línea del relleno de la
                      región sin tener que subirle la opacidad. */}
                  <path d={d} fill="none" stroke={MAR.hondo} strokeWidth={2.4 * esc}
                        strokeOpacity={0.5} strokeLinecap="round" strokeLinejoin="round" />
                  <path d={d} fill="none" stroke={tinta}
                        strokeWidth={(pasa ? 1.35 : 0.9) * esc}
                        strokeOpacity={pasa ? 0.9 : 0.32}
                        strokeDasharray={pasa ? undefined : `${2.2 * esc} ${2.2 * esc}`}
                        strokeLinecap="round" strokeLinejoin="round" />
                  {/* El nombre del corredor, SOLO con el zoom puesto. Los
                      cuatro rotulados a la vez sobre el país entero son cuatro
                      líneas de texto largo cruzando cuatro regiones, y al nivel
                      de país la tinta ya los distingue: la tabla de al lado es su
                      leyenda y no hay dos listas que desincronizar. */}
  {/* DEBAJO del punto final, no encima. El nombre de un punto va arriba
                      y el rótulo del corredor se pone donde acaba su línea, que es
                      ese mismo punto: los dos textos salían superpuestos en los
                      cuatro corredores, siempre, y ninguno de los dos se leía. */}
                  {zoom && rotulo && (
                    <text x={rotulo.x + (rotulo.derecha ? 3.4 : -3.4) * esc}
                          y={rotulo.y + 4.6 * esc}
                          textAnchor={rotulo.derecha ? 'start' : 'end'}
                          fontSize={2.1 * esc} fill={tinta}
                          fillOpacity={pasa ? 0.9 : 0.5}
                          style={{ letterSpacing: `${0.03 * esc}px` }}>
                      {c.nombre}
                    </text>
                  )}
                </g>
              )
            })}

            {/* --- puerto y otros sitios con nombre ------------------------- */}
            {sitios.filter(s => s.tipo !== 'ciudad').map(s => (
              <g key={s.id} style={{ pointerEvents: 'none' }}>
                {s.tipo === 'puerto' ? (
                  <>
                    <circle cx={s.x} cy={s.y} r={2.2 * esc} fill="#7fa3d8"
                            fillOpacity={0.12} />
                    <path d={`M ${s.x - 1.25 * esc} ${s.y + 0.42 * esc} h ${2.5 * esc}
                              M ${s.x} ${s.y - 1.35 * esc} v ${2.45 * esc}`}
                          stroke="#8fb6e4" strokeWidth={0.5 * esc} fill="none"
                          strokeLinecap="round" />
                    <circle cx={s.x} cy={s.y - 1.7 * esc} r={0.55 * esc}
                            fill="none" stroke="#8fb6e4" strokeWidth={0.45 * esc} />
                  </>
                ) : (
                  <rect x={s.x - 0.75 * esc} y={s.y - 0.75 * esc}
                        width={1.5 * esc} height={1.5 * esc}
                        transform={`rotate(45 ${s.x} ${s.y})`}
                        fill="none" stroke="#8e9aae" strokeWidth={0.4 * esc} />
                )}
                {/* ENCIMA, sobre el agua. El mar es el único hueco garantizado
                    del mapa, y debajo del ancla estaba el punto de cierre más
                    cercano con su propio nombre. */}
                <text x={s.x} y={s.y - 3.9 * esc} textAnchor="middle"
                      fontSize={2.1 * esc} fill="#8fb6e4"
                      stroke={MAR.hondo} strokeWidth={0.55 * esc} paintOrder="stroke"
                      style={{ letterSpacing: `${0.05 * esc}px` }}>
                  {s.nombre}
                </text>
              </g>
            ))}

            {/* --- la ciudad, con su nombre --------------------------------- */}
            {/* El nombre de la ciudad, SOLO al nivel de país. Es donde orienta
                —seis de los once puntos están dentro de esa mancha— y es donde no
                compite con nada, porque ahí los puntos no llevan rótulo. Con el
                zoom puesto sobre Bellaflor, la cabecera del mapa ya dice dónde
                está la sala. */}
            {!zoom && sitios.filter(s => s.tipo === 'ciudad').map(s => (
              <text key={`t-${s.id}`} x={s.x} y={s.y - (s.radio || 12) - 1.6 * esc}
                    textAnchor="middle" fontSize={2.5 * esc} fontWeight={600}
                    fill="#cbd4e1" stroke={TIERRA.bajo} strokeWidth={0.7 * esc}
                    paintOrder="stroke" style={{ pointerEvents: 'none',
                                                 letterSpacing: `${0.16 * esc}px` }}>
                {s.nombre.toUpperCase()}
              </text>
            ))}

            {/* --- LA INFRAESTRUCTURA RELEVANTE ------------------------------
                No hay acciones en contra de ella, y por eso no lleva estado de
                daño: lo único que la sala decide es si gasta fuerza en
                custodiarla. Protegida y sin proteger se distinguen a simple
                vista, porque esa es toda la decisión — y lo que el debriefing
                cobra es el riesgo que se asumió al dejarla sola.

                Al nivel de país no salen: doce marcas más sobre once puntos de
                cierre es un mapa que no se lee. Aparecen con el zoom puesto, que
                es cuando la pregunta «¿qué hay aquí que haya que proteger?»
                tiene respuesta accionable. */}
            {zoom && infraestructura.filter(i => i.region_id === zoom).map(i => (
              <g key={i.infra_id} style={{ pointerEvents: 'none' }}
                 opacity={i.protegida ? 1 : 0.82}>
                <title>
                  {`${i.nombre} · ${i.criticidad}`
                   + ` · ${i.protegida ? 'bajo custodia' : 'SIN PROTEGER'}`
                   + (i.de_que_depende ? ` · ${i.de_que_depende}` : '')}
                </title>
                <circle cx={i.x} cy={i.y} r={2.1 * esc}
                        fill={i.protegida ? '#26404f' : '#3a2f33'}
                        fillOpacity={0.9}
                        stroke={i.protegida ? '#6fb2c9' : '#c98f7a'}
                        strokeOpacity={i.protegida ? 0.85 : 0.75}
                        strokeWidth={0.42 * esc}
                        strokeDasharray={i.protegida
                          ? undefined : `${0.8 * esc} ${0.7 * esc}`} />
                <path d={INFRA[i.tipo] || INFRA.logistica}
                      transform={`translate(${i.x} ${i.y}) scale(${0.66 * esc})`}
                      fill="none" stroke={i.protegida ? '#a8d8e8' : '#e0b5a4'}
                      strokeWidth={0.55} strokeLinecap="round"
                      strokeLinejoin="round" />
                <text x={i.x} y={i.y + 4.1 * esc} textAnchor="middle"
                      fontSize={1.85 * esc}
                      fill={i.protegida ? '#8fb6c9' : '#d0a08e'}
                      stroke={TIERRA.bajo} strokeWidth={0.6 * esc}
                      paintOrder="stroke">
                  {i.nombre}
                </text>
              </g>
            ))}

            {/* --- el nombre de cada región --------------------------------- */}
            {Object.entries(geo.rotulos || {}).map(([id, pos]) => {
              const r = regiones[id] || {}
              if (zoom && zoom !== id) return null
              return (
                <text key={id} x={pos.x} y={pos.y} textAnchor="middle"
                      fontSize={2.45 * esc} fontWeight={r.epicentro ? 650 : 500}
                      fill={r.epicentro ? '#c2ccdb' : '#8b97a9'}
                      stroke={TIERRA.bajo} strokeWidth={0.7 * esc} paintOrder="stroke"
                      style={{ pointerEvents: 'none', letterSpacing: `${0.18 * esc}px` }}>
                  <tspan x={pos.x}>{(r.nombre || id).toUpperCase()}</tspan>
                  {/* Cuántos puntos hay dentro. Al nivel de país los nombres no
                      salen, así que sin este recuento una región con seis
                      bloqueos y otra con uno se leen igual de lejos. */}
                  <tspan x={pos.x} dy={3.1 * esc} fontSize={1.95 * esc}
                         fontWeight={400} fill="#6f7b8d" letterSpacing="0">
                    {r.lectura?.puntos === 1 ? '1 punto' : `${r.lectura?.puntos || 0} puntos`}
                  </tspan>
                </text>
              )
            })}

            {/* --- los puntos de cierre ------------------------------------- */}
            {puntos.map(p => {
              const color = COLOR_ESTADO[p.estado] || COLOR_ESTADO.cerrado
              // QUÉ SE ESTÁ HACIENDO AQUÍ, no cómo se abrió. Ver la cabecera.
              const forma = FORMA[p.intervencion] || 'nada'
              const sel = seleccionado === p.nodo_id
              const mirado = sobre?.tipo === 'punto' && sobre.id === p.nodo_id
              const sinMirar = p.estado === 'sin_verificar'
              const anillo = anilloDe(hechos[p.nodo_id])
              const frases = frasesDe(hechos[p.nodo_id])
              const fuera = zoom && p.region_id !== zoom
              // LA MARCA, MÁS PEQUEÑA. Todo lo que rodea al punto —el halo
              // de lo mirado, el aro de la mesa, el anillo de anoche— se deriva
              // de este radio, así que bajarlo encoge el racimo entero y no
              // solo el relleno. En las ciudades donde se juntan cinco o seis
              // puntos, esa diferencia es la que separa una constelación
              // legible de un borrón.
              const r = 2.0 * esc

              // El rótulo nunca se sale del lienzo.
              const lineas = partir(p.nombre)

              const ancla = p.x > 78 ? 'end' : p.x < 14 ? 'start' : 'middle'
              const dx = (ancla === 'end' ? 2.3 : ancla === 'start' ? -2.3 : 0) * esc
              const dy = -((lineas.length > 1 ? 5.4 : 3.4) + (piso[p.nodo_id] || 0) * PISO)

              return (
                <g key={p.nodo_id}
                   opacity={fuera ? 0.25 : 1}
                   onMouseEnter={() => setSobre({ tipo: 'punto', id: p.nodo_id })}
                   onClick={e => { e.stopPropagation(); onSeleccionar?.(sel ? null : p.nodo_id) }}
                   style={{ cursor: 'pointer' }}>

                  {/* Un solo hijo de texto: React 19 trata `<title>` como metadato
                      y con varios trozos no lo compone — se pierde el globo. */}
                  <title>
                    {[
                      `${p.nombre} (${p.nodo_id})`,
                      p.lectura?.caudal?.banda,
                      rotulo(INTERVENCION, p.intervencion),
                      p.mesa && (p.mesa.sesionada_hoy
                        ? 'mesa instalada hoy'
                        : `mesa sin sesionar${p.mesa.jornadas_congelada
                            ? ` · ${p.mesa.jornadas_congelada} jornada(s) congelada`
                            : ''}`),
                      `${p.lectura?.masa_presente?.aprox} personas`,
                      `${p.lectura?.dias_sostenido?.dias} días de cierre`,
                      frases.length ? `anoche: ${frases.join('; ')}` : null,
                    ].filter(Boolean).join(' · ')}
                  </title>

                  {/* El anillo dice QUE AQUÍ PASÓ ALGO desde la última vez que la
                      sala miró, y se apaga solo en la ventana siguiente. */}
  {/* El anillo de lo que pasó anoche: un halo tenue por debajo y el
                      aro encima. Un aro solo, a pelo, se lee como un segundo punto
                      concéntrico; con el halo se lee como lo que es, una señal. */}
                  {anillo && (
                    <>
                      <circle cx={p.x} cy={p.y} r={r * 1.75} fill="none"
                              stroke={anillo.color} strokeOpacity={0.18}
                              strokeWidth={(anillo.rango >= 3 ? 2.4 : 1.8) * esc} />
                      <circle cx={p.x} cy={p.y} r={r * 1.75} fill="none"
                              stroke={anillo.color} strokeOpacity={0.9}
                              strokeWidth={(anillo.rango >= 3 ? 0.75 : 0.5) * esc} />
                    </>
                  )}
                  {(sel || mirado) && (
                    <circle cx={p.x} cy={p.y} r={r * 2.3} fill="#e8ecf4"
                            fillOpacity={sel ? 0.09 : 0.05} stroke="#e8ecf4"
                            strokeOpacity={sel ? 0.7 : 0.35}
                            strokeWidth={(sel ? 0.55 : 0.4) * esc} />
                  )}

                  {/* SOMBRA, NO BORDE NEGRO. Un contorno oscuro de medio punto
                      alrededor de cada marca es lo que le daba al mapa entero el
                      aire de recorte pegado encima. Una sombra suave separa igual
                      de bien y no dibuja una línea que no significa nada. */}
                  <g filter="url(#mapa-relieve)">
                    {forma === 'pactado' ? (
                      <rect x={p.x - r * 0.85} y={p.y - r * 0.85} width={r * 1.7}
                            height={r * 1.7} rx={r * 0.3} fill={color} />
                    ) : forma === 'fuerza' ? (
                      <rect x={p.x - r * 0.82} y={p.y - r * 0.82} width={r * 1.64}
                            height={r * 1.64} rx={r * 0.18}
                            transform={`rotate(45 ${p.x} ${p.y})`} fill={color} />
                    ) : (
                      <circle cx={p.x} cy={p.y} r={r}
                              fill={sinMirar ? TIERRA.bajo : color}
                              stroke={sinMirar ? color : 'none'}
                              strokeWidth={0.8 * esc} />
                    )}
                  </g>

                  {/* LA MESA INSTALADA. Sólida si hoy ha sesionado, a trazos si
                      no: una mesa local hay que instalarla cada jornada para que
                      surta efecto, y la que hoy nadie ha convocado tiene la
                      negociación congelada. Es la diferencia que el Ministro del
                      Interior y el Alcalde tienen que ver desde la pared. */}
                  {p.mesa && (
                    <circle cx={p.x} cy={p.y} r={r * 1.42} fill="none"
                            stroke={p.mesa.sesionada_hoy ? '#7fc4a8' : '#c9a05a'}
                            strokeOpacity={p.mesa.sesionada_hoy ? 0.95 : 0.8}
                            strokeWidth={0.55 * esc}
                            strokeDasharray={p.mesa.sesionada_hoy
                              ? undefined : `${1.1 * esc} ${1.0 * esc}`}
                            style={{ pointerEvents: 'none' }} />
                  )}

                  {/* Una interrogación proyectada en la pared es una petición de
                      decisión: hay alguien en la mesa que puede resolverla
                      gastando un equipo de terreno, y todos lo están viendo. */}
                  {sinMirar && (
                    <text x={p.x} y={p.y + 0.85 * esc} textAnchor="middle"
                          fontSize={2.3 * esc} fill="#a7b1c2" fontWeight={600}
                          style={{ pointerEvents: 'none' }}>?</text>
                  )}

                  {/* EL NOMBRE, no el código: se señala en voz alta desde el
                      fondo de la sala y `N003` hay que traducirlo primero.

                      Al nivel de país sale solo el del punto que se está mirando.
                      Los doce a la vez son doce nombres largos sobre un racimo de
                      seis puntos en la misma ciudad, y de ese amontonamiento no se
                      lee ninguno: hay que ampliar la región para leerlos, que es
                      exactamente para lo que está el segundo nivel. */}
                  {(zoom || sel || mirado) && (
                    <text x={p.x + dx} y={p.y + dy * esc}
                          textAnchor={ancla} fontSize={2.35 * esc}
                          fontWeight={sel || mirado ? 700 : 500}
                          fill={sel || mirado ? '#eef2f8' : '#a7b1c2'}
                          stroke={TIERRA.bajo} strokeWidth={0.75 * esc}
                          paintOrder="stroke"
                          style={{ pointerEvents: 'none',
                                   letterSpacing: `${0.02 * esc}px` }}>
                      {lineas.map((linea, i) => (
                        <tspan key={i} x={p.x + dx} dy={i ? 2.5 * esc : 0}>{linea}</tspan>
                      ))}
                    </text>
                  )}
                </g>
              )
            })}
          </g>

          {/* --- los mares, fuera del grupo que se acerca -------------------
              Un rótulo de mar que crece con el zoom acaba cruzando el país. */}
          {!zoom && (geo.mares || []).map(m => (
            <text key={m.nombre} x={m.x} y={m.y} fontSize={2.3}
                  textAnchor="middle" fill="#3f6d8d" fillOpacity={0.8}
                  transform={m.rotacion ? `rotate(${m.rotacion} ${m.x} ${m.y})` : undefined}
                  style={{ pointerEvents: 'none', letterSpacing: '0.14em' }}>
              {m.nombre.toUpperCase()}
            </text>
          ))}
        </svg>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// EL DETALLE — las seis lecturas, en palabras.
//
// Un punto y una región dicen exactamente las mismas seis cosas, y eso es
// deliberado: la sala aprende a leer UNA lista, no dos. Lo único que cambia es
// que la región añade su recuento —cuántos puntos, cuántos cerrados, qué se
// está haciendo en ellos— y el punto añade a qué corredor pertenece.
//
// NINGUNA LLEVA EL NÚMERO INTERNO. Ni «dureza 0,84» ni «vocería 0,22». Las dos
// cifras que sí salen son las dos que se cuentan de verdad: personas y días. La
// misma frontera que en el tablero separa «Legitimidad: alta» de «Muertes
// evitables: 3».
//
//
// ESTO YA NO ES UNA FICHA APARTE
// ==============================
// Fue una tarjeta —debajo del mapa primero, al pie del panel después— y en los
// dos sitios cometía el mismo error: sacaba la lectura de un punto FUERA de la
// lista donde está el punto. Quien comparaba dos filas tenía que ir a un
// segundo bloque, cargar seis palabras en la cabeza, volver, y repetir.
//
// Ahora esto se dibuja DENTRO de la tabla, en la propia fila que se desplegó.
// El detalle no está cerca de su fila: **es** su fila. Por eso el archivo
// exporta las piezas y no la tarjeta — la tarjeta ya no existe.
// ---------------------------------------------------------------------------

const FILAS = [
  ['caudal', 'Paso'],
  ['dureza', 'Dureza'],
  ['masa_presente', 'Gente en la calle'],
  ['dias_sostenido', 'Días de cierre'],
  ['apoyo_local', 'Apoyo del barrio'],
  ['control_voceria', 'Vocería reconocida'],
]

const COLOR_PELDANO = ['var(--mal)', 'var(--medio)', 'var(--bien)']

/** Del peldaño a un color, sea la escala de tres bandas o de cinco. */
function tinta(m) {
  const t = m.de <= 1 ? 0 : m.peldano / (m.de - 1)
  const bueno = m.sentido === 'arriba_mejor' ? t : 1 - t
  return COLOR_PELDANO[bueno < 0.34 ? 0 : bueno < 0.67 ? 1 : 2]
}

function Escala({ m }) {
  const color = tinta(m)
  return (
    <span className="ficha-escala" aria-hidden="true">
      {Array.from({ length: m.de }, (_, i) => (
        <span key={i} className={i <= m.peldano ? 'peldano lleno' : 'peldano'}
              style={i <= m.peldano ? { background: color } : undefined} />
      ))}
    </span>
  )
}

const miles = n => new Intl.NumberFormat('es-CO').format(n)

/** El texto de una fila. Es donde vive la única cifra que sale. */
function decir(clave, m, esRegion) {
  if (clave === 'masa_presente') {
    // El total y el promedio, salvo cuando la región tiene un solo punto: ahí
    // son el mismo número dicho dos veces.
    return esRegion && m.aprox !== m.aprox_por_punto
      ? `≈${miles(m.aprox)} personas · ≈${miles(m.aprox_por_punto)} por punto`
      : `≈${miles(m.aprox)} personas`
  }
  if (clave === 'dias_sostenido') {
    if (!esRegion) return `${m.dias} ${m.dias === 1 ? 'día' : 'días'} · ${banda(m.banda)}`
    return `${m.dias} de media · el más antiguo, ${m.dias_max}`
  }
  return banda(m.banda)
}


/**
 * LAS SEIS LECTURAS. La misma rejilla para un punto y para una región.
 */
export function Lecturas({ lectura, esRegion }) {
  return (
    <dl className="ficha-lecturas">
      {FILAS.map(([clave, nombre]) => {
        const m = lectura[clave]
        if (!m) return null
        return (
          <div key={clave} className="ficha-fila">
            <dt>{nombre}</dt>
            <dd style={{ color: tinta(m) }}>
              {decir(clave, m, esRegion)}
              {/* Solo en un punto. En una región, `constatado` es «los constató
                  a todos», y decir «sin constatar» de una región con cuatro de
                  cinco verificados sería afirmar algo falso. La constatación es
                  un hecho de un punto. */}
              {clave === 'control_voceria' && !esRegion && !m.constatado && (
                <span className="ficha-nota"> · sin constatar</span>
              )}
            </dd>
            <Escala m={m} />
          </div>
        )
      })}
    </dl>
  )
}

/**
 * EL DETALLE DE UN PUNTO — su sitio en el mapa y sus seis lecturas.
 *
 * Lo que la fila NO puede decir en una celda: de qué región es, por qué
 * corredor pasa y si alguien lo ha ido a mirar. Estado, intervención y mesa no
 * se repiten aquí: están en la propia fila, dos renglones más arriba.
 */
export function DetallePunto({ punto, region, corredor }) {
  const lectura = punto?.lectura
  if (!lectura) return null
  return (
    <>
      <div className="ficha-sub">
        {[region?.nombre,
          corredor ? corredor.nombre : 'no pertenece a ningún corredor',
          punto.verificado_turno
            ? `constatado en la jornada ${punto.verificado_turno}`
            : 'nadie lo ha verificado',
        ].filter(Boolean).join(' · ')}
      </div>
      <Lecturas lectura={lectura} esRegion={false} />
    </>
  )
}

/**
 * EL DETALLE DE UNA REGIÓN — su recuento y sus seis lecturas.
 *
 * QUÉ SE ESTÁ HACIENDO AQUÍ, CONTADO. El promedio de caudal no lo dice: cuatro
 * puntos cerrados sobre los que nadie hace nada y cuatro con mesa instalada dan
 * el mismo promedio, y son dos regiones distintas.
 */
export function DetalleRegion({ region }) {
  const lectura = region?.lectura
  if (!lectura || lectura.sin_puntos_modelados) {
    return (
      <p className="ficha-sub">
        Este ejercicio no modela ningún cierre en {region?.nombre || 'esta región'}.
      </p>
    )
  }
  const bloqueo = lectura.bloqueo
  return (
    <>
      <div className="ficha-sub">
        {`${lectura.puntos} punto${lectura.puntos === 1 ? '' : 's'} modelado`}
        {`${lectura.puntos === 1 ? '' : 's'} · ${lectura.cerrados} sin dejar pasar nada`}
        {bloqueo && (
          <>
            {' '}
            <span className="chip" style={{
              color: TINTA_BLOQUEO[bloqueo.peldano],
              borderColor: TINTA_BLOQUEO[bloqueo.peldano],
            }}>
              {banda(bloqueo.banda)}
            </span>
          </>
        )}
      </div>

      {lectura.intervencion && (
        <div className="ficha-intervencion">
          {['fuerza', 'negociacion', 'ninguna']
            .filter(k => lectura.intervencion[k] > 0)
            .map(k => (
              <span key={k} className={`chip chip-${k === 'fuerza' ? 'mal'
                : k === 'negociacion' ? 'bien' : 'neutro'}`}>
                {lectura.intervencion[k]} {rotulo(INTERVENCION_CORTA, k).toLowerCase()}
              </span>
            ))}
          {/* UNA MESA INSTALADA Y UNA MESA INSTALADA HOY no son la misma cosa:
              la primera existe, la segunda avanza. Sin esto, una sala instala
              una mesa la jornada 1 y da por hecho que sigue trabajando sola
              hasta la 5, que es exactamente lo que no pasa. */}
          {lectura.mesas?.instaladas > 0 && (
            <span className={`chip chip-${lectura.mesas.congeladas ? 'medio' : 'bien'}`}>
              {lectura.mesas.instaladas} mesa
              {lectura.mesas.instaladas === 1 ? '' : 's'}
              {lectura.mesas.congeladas
                ? ` · ${lectura.mesas.congeladas} sin sesionar` : ''}
            </span>
          )}
        </div>
      )}

      <Lecturas lectura={lectura} esRegion />
    </>
  )
}

// ---------------------------------------------------------------------------
// LA MARCA DE UN PUNTO — el mismo dibujo, a tamaño de renglón.
//
// EL PROBLEMA QUE RESUELVE. Al nivel de país el mapa NO rotula los puntos: solo
// sale el nombre del que se está mirando, y es a propósito —doce nombres largos
// sobre un racimo de seis puntos en la misma ciudad no se leen—. De modo que
// quien lee la tabla ve doce filas con nombre, y el mapa de al lado le devuelve
// una constelación de formas de colores sin una sola palabra que las case. La
// fila y el punto eran el mismo hecho contado en dos idiomas.
//
// La marca es el puente: **cada fila lleva dibujado su propio punto**, con la
// forma de lo que se está haciendo, el color de su estado, el aro de la mesa y
// el anillo de lo que pasó anoche. Se busca la forma, no el nombre.
//
// Y LO DIBUJA ESTE ARCHIVO, no la tabla. Una copia de estas reglas en el panel
// se desincroniza en cuanto alguien toque un color o un umbral aquí: la sala
// vería un rombo en la fila y un círculo en el mapa para el mismo punto, y no
// habría manera de saber cuál de los dos miente.
// ---------------------------------------------------------------------------

export function MarcaPunto({ punto, hechos }) {
  if (!punto) return null

  const color = COLOR_ESTADO[punto.estado] || COLOR_ESTADO.cerrado
  const forma = FORMA[punto.intervencion] || 'nada'
  const sinMirar = punto.estado === 'sin_verificar'
  const anillo = anilloDe(hechos)

  const c = 9          // el centro del lienzo de la marca
  const r = 3.6        // el mismo radio proporcional que en el mapa

  return (
    <svg className="marca-punto" viewBox="0 0 18 18" width="18" height="18"
         role="img" aria-label={[
           rotulo(ESTADO_PUNTO, punto.estado),
           rotulo(INTERVENCION, punto.intervencion),
           punto.mesa && (punto.mesa.sesionada_hoy ? 'mesa hoy' : 'mesa sin sesionar'),
           anillo && anillo.texto,
         ].filter(Boolean).join(' · ')}>
      {anillo && (
        <circle cx={c} cy={c} r={r * 1.75} fill="none" stroke={anillo.color}
                strokeOpacity={0.9} strokeWidth={anillo.rango >= 3 ? 1.1 : 0.8} />
      )}

      {forma === 'pactado' ? (
        <rect x={c - r * 0.85} y={c - r * 0.85} width={r * 1.7} height={r * 1.7}
              rx={r * 0.3} fill={color} />
      ) : forma === 'fuerza' ? (
        <rect x={c - r * 0.82} y={c - r * 0.82} width={r * 1.64} height={r * 1.64}
              rx={r * 0.18} transform={`rotate(45 ${c} ${c})`} fill={color} />
      ) : (
        <circle cx={c} cy={c} r={r} fill={sinMirar ? TIERRA.bajo : color}
                stroke={sinMirar ? color : 'none'} strokeWidth={1} />
      )}

      {punto.mesa && (
        <circle cx={c} cy={c} r={r * 1.42} fill="none"
                stroke={punto.mesa.sesionada_hoy ? '#7fc4a8' : '#c9a05a'}
                strokeOpacity={punto.mesa.sesionada_hoy ? 0.95 : 0.8}
                strokeWidth={0.8}
                strokeDasharray={punto.mesa.sesionada_hoy ? undefined : '1.6 1.4'} />
      )}

      {sinMirar && (
        <text x={c} y={c + 1.5} textAnchor="middle" fontSize={4} fill="#a7b1c2"
              fontWeight={600}>?</text>
      )}
    </svg>
  )
}

/**
 * LA CLAVE DEL MAPA — qué quiere decir cada forma y cada anillo.
 *
 * Vivía debajo del lienzo y ahora vive al pie de la tabla de nodos, que es
 * donde están las marcas que explica. Una leyenda lejos de lo que nombra
 * obliga a mirar en dos sitios para leer una sola cosa.
 *
 * Va en UNA línea y no en dos: en una pantalla que no se desplaza, cada fila
 * de leyenda se paga en filas de tabla.
 *
 * Los nombres de los corredores no están aquí: los ponen el propio mapa y la
 * tabla de corredores, y tres leyendas de lo mismo eran dos de más.
 */
export function ClaveDelMapa() {
  return (
    <div className="mapa-formas">
      <span className="eyebrow">Se hace</span>
      <span>◆ A la fuerza</span>
      <span>■ En negociación</span>
      <span>● Nada</span>
      <span>? Sin verificar</span>
      <span><i className="aro" style={{ borderColor: '#7fc4a8' }} /> Mesa hoy</span>
      <span><i className="aro punteado" style={{ borderColor: '#c9a05a' }} /> Congelada</span>
      <Ayuda etiqueta="Qué significa cada forma">{D.formas_mapa}</Ayuda>

      <span className="mapa-formas-corte" aria-hidden="true" />

      <span className="eyebrow">Anoche</span>
      <span><i className="aro" style={{ borderColor: '#d9636f' }} /> Cierre o incidente</span>
      <span><i className="aro" style={{ borderColor: '#d9a441' }} /> Se operó</span>
      <span><i className="aro" style={{ borderColor: '#4fb286' }} /> Se abrió</span>
      <span><i className="aro" style={{ borderColor: '#7aa5e8' }} /> Se verificó</span>
      <Ayuda etiqueta="Qué significan los anillos">{D.hechos_mapa}</Ayuda>
    </div>
  )
}
