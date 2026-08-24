import TableroSituacion from './components/TableroSituacion'
import EsferaPublica from './components/EsferaPublica'
import ConsolaModerador from './components/ConsolaModerador'
import LogoAiLab from '../logos/LOGO Ai Lab_blanco.png'

// ---------------------------------------------------------------------------
// TRES SUPERFICIES, UN SOLO TECLADO (§10 de la propuesta)
//
// El ejercicio anterior enseñó que una pantalla por participante produce ocho
// personas mirando ocho pantallas y ninguna mirando a las otras siete. En un
// caso cuyo objeto es la ARQUITECTURA DE DECISIÓN de un cuerpo colegiado,
// retirar las pantallas individuales no es una concesión: es lo que hace que
// el objeto exista.
//
//   /tablero   proyectado a toda la sala · lo que el Estado tiene por cierto
//   /esfera    proyectado a toda la sala · lo que se dice
//   /consola   el único teclado, del moderador · NO se proyecta
//
// La distancia entre las dos proyecciones es el caso. Nunca en pestañas: la
// divergencia solo se percibe simultánea.
// ---------------------------------------------------------------------------

const PANTALLAS = [
  {
    ruta: '/tablero',
    nombre: 'Tablero de situación',
    detalle: 'Proyección para la sala. Lo que el Estado tiene por cierto, con su procedencia.',
    proyectar: true,
  },
  {
    ruta: '/esfera',
    nombre: 'Esfera pública',
    detalle: 'Proyección para la sala. Prensa, redes, internacional y la guerra de cifras.',
    proyectar: true,
  },
  {
    ruta: '/consola',
    nombre: 'Consola del moderador',
    detalle: 'El único teclado. Transcribe, lee el plan de vuelta con su riesgo, entrega notas.',
    proyectar: false,
  },
]

const Portada = () => (
  <div style={{
    minHeight: '100vh', display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center', gap: '2rem',
    backgroundColor: 'var(--bg-main, #0d1117)', color: 'var(--text-main, #e6e9ee)',
    fontFamily: 'system-ui, sans-serif', padding: '2rem',
  }}>
    <img src={LogoAiLab} alt="AI Lab" style={{ height: '3rem', opacity: 0.9 }} />
    <h1 style={{ fontSize: '1.5rem', fontWeight: 600, textAlign: 'center' }}>
      SIMCASE · El Estado frente al Estallido Social
    </h1>
    <p style={{ opacity: 0.7, maxWidth: '38rem', textAlign: 'center', lineHeight: 1.6 }}>
      Puesto de Mando Unificado · Casa de Nariño, segunda semana de mayo de 2021.
      <br />
      <strong>La mesa no lleva pantallas.</strong> Dos proyecciones para la sala y una consola
      para el moderador.
    </p>
    <div style={{ display: 'grid', gap: '0.75rem', width: '100%', maxWidth: '34rem' }}>
      {PANTALLAS.map(p => (
        <a key={p.ruta} href={p.ruta} style={{
          display: 'block', padding: '1rem 1.25rem', borderRadius: '0.5rem',
          border: '1px solid rgba(255,255,255,0.15)', textDecoration: 'none',
          color: 'inherit', backgroundColor: 'rgba(255,255,255,0.04)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <span style={{ fontWeight: 600 }}>{p.nombre}</span>
            <span style={{
              fontSize: '0.7rem', letterSpacing: '0.08em', textTransform: 'uppercase',
              opacity: 0.5,
            }}>
              {p.proyectar ? 'proyectar' : 'no proyectar'}
            </span>
          </div>
          <div style={{ opacity: 0.65, fontSize: '0.9rem', marginTop: '0.15rem' }}>{p.detalle}</div>
          <code style={{ opacity: 0.45, fontSize: '0.8rem' }}>{p.ruta}</code>
        </a>
      ))}
    </div>
  </div>
)

function App() {
  const ruta = window.location.pathname

  if (ruta === '/tablero') return <TableroSituacion />
  if (ruta === '/esfera') return <EsferaPublica />
  if (ruta === '/consola') return <ConsolaModerador />

  return <Portada />
}

export default App
