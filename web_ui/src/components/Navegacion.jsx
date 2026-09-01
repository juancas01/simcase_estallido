// ---------------------------------------------------------------------------
// IR DE UNA SUPERFICIE A LA OTRA.
//
// Con DOS superficies el problema de navegación desaparece: no hay un menú al
// que volver ni un árbol que recorrer — hay «esta» y «la otra». Este enlace es
// la otra, y por eso no recibe una lista de destinos sino uno solo.
//
// Existía un tercer destino, `menu`, que llevaba a una portada que ya no
// existe. Un enlace que apunta a una pantalla retirada no es un enlace roto que
// haya que acordarse de apagar: es algo que no se vuelve a escribir.
// ---------------------------------------------------------------------------

const DESTINOS = {
  tablero: { href: '/', texto: 'Tablero de situación', flecha: '←' },
  // La consola no se proyecta. El enlace existe porque quien transcribe
  // necesita llegar a ella en un clic, no porque la sala tenga que verla.
  consola: { href: '/consola', texto: 'Consola de órdenes', flecha: '→' },
}

export default function Navegacion({ a = 'tablero' }) {
  const d = DESTINOS[a]
  if (!d) return null
  return (
    <nav className="nav-superficies" aria-label="Ir a la otra superficie">
      <a className="enlace-superficie" href={d.href}>
        {d.flecha === '←' && (
          <span className="enlace-flecha" aria-hidden="true">←</span>
        )}
        {d.texto}
        {d.flecha === '→' && (
          <span className="enlace-flecha" aria-hidden="true">→</span>
        )}
      </a>
    </nav>
  )
}
