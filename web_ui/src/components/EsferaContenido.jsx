// ---------------------------------------------------------------------------
// EL CONTENIDO DE LA ESFERA PÚBLICA — compartido por sus dos presentaciones.
//
//   · como página propia, en `/esfera`, cuando hay dos proyectores
//   · como barra lateral del tablero, cuando hay uno solo o una sola pantalla
//
// Vive aquí y no duplicado en los dos sitios: un dato en dos sitios se
// desincroniza, y una lista propia en cada pantalla es el mismo error con otro
// nombre.
//
// Las glosas —qué es una denuncia sin verificar, qué cuesta comprobarla, de
// dónde sale el texto de las publicaciones— están en `definiciones.jsx` y solo
// aparecen al pedirlas. Aquí se ve lo que se dice, no lo que hay que saber para
// entenderlo.
// ---------------------------------------------------------------------------

import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'

export const FUENTES = {
  prensa_nacional: 'Prensa nacional',
  prensa_internacional: 'Prensa internacional',
  redes: 'Redes sociales',
  comite_del_paro: 'Comité Nacional del Paro',
  gremios: 'Gremios',
  alcaldes_entorno: 'Alcaldes de entorno',
}

export const ENCUADRE = {
  represion: { texto: 'Represión', chip: 'mal' },
  desorden: { texto: 'Desorden', chip: 'medio' },
  negociacion: { texto: 'Negociación', chip: 'bien' },
  abandono: { texto: 'Abandono', chip: 'medio' },
}

export function sinVerificar(datos) {
  return (datos?.denuncias || []).filter(d => d.estado !== 'verificada')
}

export default function EsferaContenido({ datos, compacto = false }) {
  if (!datos) return null
  const abiertas = sinVerificar(datos)
  const enc = ENCUADRE[datos.encuadre_dominante] || ENCUADRE.desorden

  return (
    <>
      {compacto && (
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
      )}

      <div className="tarjeta" style={{ marginBottom: '0.75rem' }}>
        <h2>Publicaciones</h2>
        {datos.publicaciones?.length ? (
          datos.publicaciones.slice(0, compacto ? 8 : 20).map((p, i) => (
            <div key={i} className={`publicacion${p.sin_verificar ? ' sin-verificar' : ''}`}>
              <span className="fuente">
                {FUENTES[p.fuente] || p.fuente}
                {p.turno ? ` · turno ${p.turno}` : ''}
                {p.sin_verificar && ' · sin verificar'}
              </span>
              <p style={compacto ? { fontSize: '0.88rem' } : undefined}>{p.texto}</p>
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
                {d.denuncia_id} · desde el turno {d.turno} · {d.estado}
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
                  {datos.comite_disponible ? 'se sienta' : 'suspendió'}
                </span>
              </td>
            </tr>
            <tr>
              <td>Gremios camioneros</td>
              <td style={{ textAlign: 'right' }}>
                <span className={`chip chip-${
                  datos.posicion_gremios === 'fuera' ? 'bien'
                    : datos.posicion_gremios === 'evaluando' ? 'medio' : 'mal'}`}>
                  {datos.posicion_gremios}
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
