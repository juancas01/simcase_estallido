// ---------------------------------------------------------------------------
// LA ESFERA PÚBLICA — lo que se dice, dentro del tablero.
//
// **Ya no tiene ruta propia, y eso es una decisión de diseño, no una poda.**
//
// Antes vivía en dos sitios: como página en `/esfera` para montajes de dos
// proyectores, y como barra lateral del tablero para los de uno. Pero la
// doctrina de este ejercicio siempre fue la misma:
//
//     La distancia entre lo que el Estado tiene por cierto y lo que se dice
//     es el caso, y SOLO SE PERCIBE SIMULTÁNEA.
//
// Mientras la esfera tuvo ruta propia, esa doctrina dependía de que quien monta
// la sala hiciera lo correcto: bastaba proyectar `/esfera` sola, o `/tablero`
// solo, para perder justamente lo que hay que enseñar. Al vivir dentro del
// tablero, **el montaje incorrecto deja de ser posible.**
//
// Una regla que el software garantiza vale más que una que el software
// recomienda.
//
// Sigue siendo plegable: quien la pliega toma una decisión explícita y el
// contador de denuncias sin verificar se queda visible en el botón.
// ---------------------------------------------------------------------------

import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { ESTADO_DENUNCIA, FUENTE, POSICION_GREMIOS, rotulo } from '../etiquetas.jsx'

export const ENCUADRE = {
  represion: { texto: 'Represión', chip: 'mal' },
  desorden: { texto: 'Desorden', chip: 'medio' },
  negociacion: { texto: 'Negociación', chip: 'bien' },
  abandono: { texto: 'Abandono', chip: 'medio' },
}

export function sinVerificar(datos) {
  return (datos?.denuncias || []).filter(d => d.estado !== 'verificada')
}

export default function EsferaContenido({ datos }) {
  if (!datos) return null
  const abiertas = sinVerificar(datos)
  const enc = ENCUADRE[datos.encuadre_dominante] || ENCUADRE.desorden

  return (
    <>
      <div className="tarjeta" style={{ marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between',
                      alignItems: 'center', gap: '0.5rem' }}>
          <span className="eyebrow">
            Encuadre dominante
            <Ayuda etiqueta="Definición de encuadre dominante">{D.encuadre}</Ayuda>
          </span>
          <span className={`chip chip-${enc.chip}`}>{enc.texto}</span>
        </div>
      </div>

      <div className="tarjeta" style={{ marginBottom: '0.75rem' }}>
        <h2>Publicaciones</h2>
        {datos.publicaciones?.length ? (
          datos.publicaciones.slice(0, 10).map((p, i) => (
            <div key={i} className={`publicacion${p.sin_verificar ? ' sin-verificar' : ''}`}>
              <span className="fuente">
                {rotulo(FUENTE, p.fuente)}
                {p.turno ? ` · turno ${p.turno}` : ''}
                {p.sin_verificar && ' · sin verificar'}
              </span>
              <p style={{ fontSize: '0.88rem' }}>{p.texto}</p>
            </div>
          ))
        ) : (
          <p style={{ margin: 0, color: 'var(--texto-3)' }}>Sin publicaciones.</p>
        )}
        <p className="procedencia">
          Generado por: {datos.generado_por}
          <Ayuda etiqueta="Origen del texto mostrado">{D.generado_por}</Ayuda>
        </p>
      </div>

      <div className="tarjeta" style={{ marginBottom: '0.75rem' }}>
        <Titulo ayuda={D.denuncias}>Denuncias graves sin verificar</Titulo>
        {abiertas.length ? (
          abiertas.map(d => (
            <div key={d.denuncia_id} className="publicacion sin-verificar">
              <span className="fuente">
                {d.denuncia_id} · desde el turno {d.turno}
                {' · '}{rotulo(ESTADO_DENUNCIA, d.estado)}
              </span>
              <p style={{ fontSize: '0.88rem' }}>{d.texto}</p>
            </div>
          ))
        ) : (
          <p style={{ margin: 0, color: 'var(--texto-3)' }}>Ninguna abierta.</p>
        )}
      </div>

      <div className="tarjeta">
        <h2>Posiciones</h2>
        <table>
          <tbody>
            <tr>
              <td>Comité Nacional del Paro</td>
              <td style={{ textAlign: 'right' }}>
                <span className={`chip chip-${datos.comite_disponible ? 'bien' : 'mal'}`}>
                  {datos.comite_disponible ? 'Disponible' : 'Suspendida'}
                </span>
              </td>
            </tr>
            <tr>
              <td>Gremios camioneros</td>
              <td style={{ textAlign: 'right' }}>
                <span className={`chip chip-${
                  datos.posicion_gremios === 'fuera' ? 'bien'
                    : datos.posicion_gremios === 'evaluando' ? 'medio' : 'mal'}`}>
                  {rotulo(POSICION_GREMIOS, datos.posicion_gremios)}
                </span>
              </td>
            </tr>
            <tr>
              <td>
                Respaldo internacional
                <Ayuda etiqueta="Definición de respaldo internacional">
                  {D.respaldo_internacional}
                </Ayuda>
              </td>
              <td className="num" style={{ textAlign: 'right' }}>
                {Math.round(datos.respaldo_internacional)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </>
  )
}
