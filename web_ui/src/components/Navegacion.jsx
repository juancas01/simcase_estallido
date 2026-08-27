// ---------------------------------------------------------------------------
// IR DE UNA SUPERFICIE A OTRA.
//
// Las cuatro superficies vivían cada una en su ruta y sin salida: quien tenía
// abierta su vista personal o la consola solo podía volver con el botón de atrás
// del navegador o escribiendo la ruta. En un ejercicio de dos horas, con ocho
// personas que no montaron el sistema, eso es un callejón.
//
// SE DECLARAN LOS DESTINOS, no se ocultan los que sobran. Cada superficie dice a
// cuáles lleva —el tablero a la consola, las personales de vuelta al tablero y
// al menú— y así un enlace que apunta a donde uno ya está no es algo que haya
// que acordarse de apagar: es algo que no se escribió.
// ---------------------------------------------------------------------------

const DESTINOS = {
  tablero: { href: '/tablero', texto: 'Tablero de situación', flecha: '←' },
  menu: { href: '/', texto: 'Menú principal', flecha: '←' },
  // La consola no se proyecta. El enlace existe porque quien conduce necesita
  // llegar a ella en un clic, no porque la sala tenga que verla.
  consola: { href: '/consola', texto: 'Consola de órdenes', flecha: '→' },
}

export default function Navegacion({ destinos = ['tablero', 'menu'] }) {
  return (
    <nav className="nav-superficies" aria-label="Ir a otra superficie">
      {destinos.map(id => {
        const d = DESTINOS[id]
        if (!d) return null
        return (
          <a key={id} className="enlace-superficie" href={d.href}>
            {d.flecha === '←' && (
              <span className="enlace-flecha" aria-hidden="true">←</span>
            )}
            {d.texto}
            {d.flecha === '→' && (
              <span className="enlace-flecha" aria-hidden="true">→</span>
            )}
          </a>
        )
      })}
    </nav>
  )
}
