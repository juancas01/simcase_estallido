// ---------------------------------------------------------------------------
// LA CABECERA — la misma en las dos superficies.
//
// El tablero y la consola tenían dos cabeceras distintas escritas a mano: una
// con los logos y el reloj, otra con un bloque de texto alineado a la derecha.
// Dos superficies del mismo ejercicio que no se parecen obligan a la sala a
// reorientarse cada vez que la pantalla cambia, y quien transcribe mira las dos
// a la vez.
//
// UNA SOLA PIEZA, tres huecos: quién ejercita (izquierda), qué superficie es
// esta y cómo se va a la otra (centro), y lo que esta superficie necesita
// tener siempre a la vista (derecha) — el reloj en las dos, y en el tablero
// además el mando de la esfera.
// ---------------------------------------------------------------------------

import Navegacion from './Navegacion'
import LogoEscuela from '../../logos/escuela-gobierno-blanco.png'
import LogoAiLab from '../../logos/LOGO Ai Lab_blanco.png'

export default function Cabecera({ eyebrow, titulo, a, children }) {
  return (
    <header className="cabecera">
      <img src={LogoEscuela} alt="Escuela de Gobierno" className="cabecera-logo" />

      <div className="cabecera-centro">
        <div className="cabecera-rotulo">
          <span className="eyebrow">{eyebrow}</span>
          <Navegacion a={a} />
        </div>
        <h1>{titulo}</h1>
      </div>

      <div className="cabecera-derecha">
        {children}
        <img src={LogoAiLab} alt="AI Lab" className="cabecera-logo" />
      </div>
    </header>
  )
}
