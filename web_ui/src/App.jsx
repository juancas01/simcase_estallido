// ---------------------------------------------------------------------------
// DOS SUPERFICIES Y SU EPÍLOGO. NI UNA MÁS.
//
//   /consola      ORDENAR · donde se transcriben las órdenes · NO se proyecta
//   /debriefing   MIRAR ATRÁS · el cierre, con el ejercicio terminado
//   todo lo demás
//                 LEER · el tablero, que es la pantalla de la sala
//
// EL DEBRIEFING ES UNA RUTA Y NO UNA PESTAÑA DEL TABLERO, porque el tablero
// sigue proyectándose durante los dos minutos de la última noche — y lo que
// esa pantalla muestra después es el país que la sala dejó, no su retrato.
// El enlace existe desde el principio; el servidor decide cuándo hay algo que
// mostrar, y responde 409 hasta entonces.
//
// NO HAY PORTADA. Hubo un menú en `/` con una tarjeta por superficie, y era
// una pantalla que solo servía para salir de ella: nadie monta una sala de dos
// horas para mirar un lanzador. La raíz ES el tablero, y cualquier ruta vieja
// —`/esfera`, `/vista/{rol}`, un enlace copiado la semana pasada— aterriza en
// él sin rebotar por un menú intermedio.
//
// LAS VISTAS PRIVADAS SE RETIRARON. Cada rol tenía su pantalla; ahora su
// cartera es UNA PESTAÑA del tablero, al lado de la vista de sala. Siete
// destinos repartían por la sala la información que la mesa necesita junta.
//
// Y NO HAY MODERADOR COMO FIGURA APARTE: quien opera la consola puede ser uno
// de los siete. El sistema conduce el turno.
// ---------------------------------------------------------------------------

import { Component } from 'react'

import Tablero from './components/Tablero'
import Consola from './components/Consola'
import Debriefing from './components/Debriefing'

// ---------------------------------------------------------------------------
// LA RED DE SEGURIDAD
//
// React desmonta el árbol entero cuando un componente lanza durante el pintado.
// Sin nada que lo intercepte, **el resultado es una pantalla en blanco**: ni
// mensaje, ni traza, ni forma de saber si el problema es el servidor, la red o
// un dato con una forma inesperada. En una sala con pantallas encendidas y dos
// horas de reloj, eso es el fallo más caro que puede tener esta interfaz.
//
// Con esto, lo peor que puede pasar es una tarjeta que dice qué se rompió y un
// botón para recargar. Una pantalla que explica su fallo se arregla en la sala;
// una en blanco, no.
// ---------------------------------------------------------------------------

class Salvavidas extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="pantalla">
        <div className="cuerpo cargando">
          <div className="cargando-caja con-error">
            <div className="eyebrow">Esta pantalla se rompió al dibujarse</div>
            <p className="cargando-titulo">
              El motor sigue corriendo. Lo que falló es la interfaz.
            </p>
            <p className="cargando-detalle">{String(this.state.error)}</p>
            <button className="primario"
                    onClick={() => window.location.reload()}>
              Recargar la pantalla
            </button>
          </div>
        </div>
      </div>
    )
  }
}

export default function App() {
  return <Salvavidas><Superficie /></Salvavidas>
}

function Superficie() {
  const ruta = decodeURIComponent(window.location.pathname)

  // Dos rutas se apartan del tablero: la que no se proyecta y la que solo
  // existe después del cierre.
  if (ruta === '/consola') return <Consola />
  if (ruta === '/debriefing') return <Debriefing />

  return <Tablero />
}
