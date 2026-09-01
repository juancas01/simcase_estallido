// ---------------------------------------------------------------------------
// IR DE UNA SUPERFICIE A LA OTRA.
//
// Con DOS superficies de sala el problema de navegación desaparece: no hay un
// menú al que volver ni un árbol que recorrer — hay «esta» y «la otra». Este
// enlace es la otra, y por eso no recibe una lista de destinos sino uno solo.
//
// EL DEBRIEFING ES EL TERCER DESTINO y no cuenta como superficie: existe con
// el ejercicio terminado, lo abre quien conduce el cierre, y el servidor
// responde 409 si alguien llega antes. El enlace desde el tablero no existe a
// propósito — durante la corrida la sala no tiene adónde ir — y el de vuelta
// desde el debriefing sí, porque el cierre se abre y se cierra.
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
  // El cierre. No se proyecta con la sala sentada: es del equipo docente.
  debriefing: { href: '/debriefing', texto: 'Debriefing', flecha: '→' },
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
