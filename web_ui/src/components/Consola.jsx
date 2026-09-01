// ---------------------------------------------------------------------------
// SUPERFICIE 4 · LA CONSOLA — donde se transcriben las órdenes.
//
// NO HAY MODERADOR COMO FIGURA APARTE. Esta es una superficie más, y quien la
// opera —puede ser uno de los nueve— solo transcribe: no conduce, no reparte
// información, no decide el ritmo y no sabe nada que los demás no sepan.
//
// EL MOMENTO QUE IMPORTA: se escribe lo que la mesa acordó, y la pantalla
// devuelve el plan interpretado CON SU BANDA DE RIESGO. La sala lo lee junta y
// con frecuencia cambia la orden. Que salga de la pantalla y no de una persona
// lo hace todavía más difícil de discutir.
//
//     El LLM traduce. El motor decide, valida, ejecuta y reporta.
//
//
// DE NOCHE ESTA PANTALLA SE APAGA
// ===============================
// Trece minutos de día en los que se puede dictar en cualquier momento, y dos de
// noche en los que no se recibe nada. Cuando cae la noche, **el cuadro de
// órdenes se atenúa y sus botones se desactivan**, y encima aparece qué produjo
// lo que se ordenó.
//
// No es solo señalización: el servidor rechaza con un 409 cualquier orden que
// llegue de noche. La pantalla apagada explica; el 409 garantiza. Si solo
// estuviera lo primero, bastaría una pestaña vieja abierta para meter una orden
// en mitad de las consecuencias.
//
//     Una regla que el software garantiza vale más que una que el software
//     recomienda.
//
// LOS MANDOS DEL RELOJ son cuatro y son para lo imprevisto: la sala que termina
// antes, la interrupción de verdad, el proyector que se cae. El ritmo normal no
// los necesita.
//
// Ninguna frase sobre el RESULTADO de una orden se escribe antes de que la orden
// se ejecute. Es el primero de los ocho modos de falla y el más difícil de ver.
// ---------------------------------------------------------------------------

import { useState } from 'react'
import Ayuda, { Titulo } from './Ayuda'
import Cabecera from './Cabecera'
import { D } from '../definiciones.jsx'
import {
  CAMPO_CONSULTA, ESTADO_PLAN, EVENTO, FASE, FRANJA, rotulo,
} from '../etiquetas.jsx'
import Cronometro from './Cronometro'
import GuiaFases from './GuiaFases'
import { api, useDatos } from '../comun.jsx'

export default function Consola() {
  const { datos: tablero, recargar } = useDatos('/tablero')
  const { datos: cfg } = useDatos('/config', 0)
  const [texto, setTexto] = useState('')
  const [plan, setPlan] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [error, setError] = useState(null)

  const crono = tablero?.cronometro
  // Con el reloj parado se puede transcribir siempre: es lo que permite montar y
  // depurar sin cronometrar nada. En cuanto el reloj corre, manda la jornada.
  const abierta = !crono?.corriendo || crono?.admite_ordenes
  const cerrado = Boolean(crono?.cerrado)

  const hacer = async (fn) => {
    setOcupado(true); setError(null)
    try { await fn() } catch (e) { setError(e.message) } finally { setOcupado(false) }
  }

  const interpretar = () => hacer(async () => {
    setResultado(null)
    setPlan(await api('/consola/interpretar', {
      method: 'POST', body: JSON.stringify({ texto }),
    }))
  })

  // AÑADIR NO GASTA LA JORNADA. Es lo que permite dictar de una en una durante
  // los trece minutos completos: la orden queda en cola y la mesa sigue.
  const encolar = () => hacer(async () => {
    const r = await api('/consola/encolar', {
      method: 'POST', body: JSON.stringify({ plan_id: plan.plan_id }),
    })
    setResultado(r); setPlan(null); setTexto(''); recargar()
  })

  const ejecutar = () => hacer(async () => {
    const r = await api('/consola/ejecutar', {
      method: 'POST', body: JSON.stringify({ plan_id: plan.plan_id }),
    })
    setResultado(r); setPlan(null); setTexto(''); recargar()
  })

  const elegir = (indice, campo, valor) => hacer(async () => {
    setPlan(await api('/consola/elegir', {
      method: 'POST',
      body: JSON.stringify({ plan_id: plan.plan_id, indice, campo, valor }),
    }))
  })

  // EL ÚNICO SITIO DESDE EL QUE SE TOCA EL RELOJ. A partir de «Iniciar» el
  // tiempo corre solo y la jornada se cierra sola: estos mandos son para lo que
  // el reloj no puede prever.
  const reloj = (accion) => hacer(async () => {
    await api(`/consola/reloj/${accion}`, { method: 'POST' }); recargar()
  })

  return (
    <div className="pantalla">
      <Cabecera
        eyebrow="Consola · no se proyecta"
        titulo="Transcripción de órdenes"
        a="tablero"
      >
        <div className="cabecera-jornada">
          <div className="num">
            Jornada {crono?.jornada ?? 0} · {rotulo(FRANJA, tablero?.franja)}
          </div>
          <div className="eyebrow">{rotulo(FASE, tablero?.fase)}</div>
        </div>
      </Cabecera>

      <div className="cuerpo" style={{ maxWidth: 1000, width: '100%', margin: '0 auto' }}>
        {cfg && !cfg.llave_presente && (
          <div className="tarjeta" style={{ borderColor: 'var(--medio)', marginBottom: '1rem' }}>
            <h2 style={{ color: 'var(--medio)' }}>
              Sin llave de API
              <Ayuda etiqueta="Qué implica correr sin llave">
                Sin llave, las capas de lenguaje natural pasan a modo
                determinista. El ejercicio se desarrolla completo: ninguna
                decisión de la simulación está delegada al modelo.
              </Ayuda>
            </h2>
            <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--texto-2)' }}>
              Escriba <code>OPENAI_API_KEY</code> en <code>{cfg.archivo_env}</code> y
              reinicie el servidor.
            </p>
          </div>
        )}

        {/* --- El reloj de la jornada: lo lleva el sistema ------------------ */}
        <div className="tarjeta" style={{ marginBottom: '1rem' }}>
          <Titulo ayuda={D.fases}>Reloj de sala</Titulo>

          <div className="reloj-panel">
            <div>
              <Cronometro cronometro={crono} />

              <div className="reloj-mandos">
                {!crono?.corriendo ? (
                  <button className="primario" onClick={() => reloj('iniciar')}
                          disabled={ocupado}>
                    Iniciar el ejercicio
                  </button>
                ) : (
                  <>
                    {/* PAUSAR es el mando de las interrupciones reales. El
                        tiempo del ejercicio no corre mientras la sala no está
                        en el ejercicio. */}
                    <button className={crono?.pausado ? 'primario' : ''}
                            onClick={() => reloj('pausa')} disabled={ocupado}>
                      {crono?.pausado ? 'Reanudar el reloj' : 'Pausar el reloj'}
                    </button>
                    {!cerrado && crono?.fase === 'dia' && (
                      <button onClick={() => reloj('noche')} disabled={ocupado}>
                        Cerrar el día y ver consecuencias
                      </button>
                    )}
                    {!cerrado && crono?.fase === 'noche' && (
                      <button onClick={() => reloj('jornada')} disabled={ocupado}>
                        Empezar la jornada siguiente
                      </button>
                    )}
                    <button onClick={() => reloj('reiniciar')} disabled={ocupado}>
                      Reiniciar el reloj
                    </button>
                  </>
                )}
              </div>
              {crono?.pausado && (
                <p className="nota-boton">
                  <strong>El reloj está detenido.</strong> Las diez pantallas
                  muestran el mismo número congelado. Nada avanza hasta reanudar.
                </p>
              )}
            </div>

            {/* Qué tramo corre y qué debería estar pasando en la sala. Va aquí y
                no en el tablero: el tablero enuncia hechos y no instruye, pero
                a esta consola la opera alguien que no montó el sistema. */}
            <GuiaFases cronometro={crono} />
          </div>
        </div>

        {/* --- Lo confirmado que todavía no se ha resuelto ---------------- */}
        {tablero?.en_cola > 0 && abierta && (
          <div className="tarjeta cola-turno">
            <div>
              <span className="eyebrow">En cola para esta jornada</span>
              <div className="cola-n">
                {tablero.en_cola}
                <span>
                  {tablero.en_cola === 1 ? 'orden confirmada' : 'órdenes confirmadas'}
                  {' y sin resolver'}
                </span>
              </div>
            </div>
            <button className="primario" onClick={() => reloj('noche')}
                    disabled={ocupado}>
              Cerrar el día ahora
            </button>
          </div>
        )}

        {/* --- Lo que produjo la jornada, durante la noche ----------------- */}
        {!abierta && tablero?.consecuencias && (
          <div className="tarjeta consecuencias" style={{ marginBottom: '1rem' }}>
            <Titulo ayuda={D.consecuencias}>
              Consecuencias de la jornada {tablero.consecuencias.jornada}
            </Titulo>
            <p className="num" style={{ marginTop: 0, color: 'var(--texto)' }}>
              {tablero.consecuencias.resumen}
            </p>
            <div className="consecuencias-lista">
              {tablero.consecuencias.resultados?.map((x, i) => (
                <p key={i}>
                  <span className={`chip chip-${x.ok ? 'bien' : 'mal'}`}>
                    {x.ok ? 'Ejecutada' : 'No viable'}
                  </span>{' '}
                  {x.mensaje}
                </p>
              ))}
            </div>
            {tablero.consecuencias.eventos?.length > 0 && (
              <p className="consecuencias-eventos">
                {tablero.consecuencias.eventos.slice(0, 12).map((e, i) => (
                  <span key={i} className="chip chip-neutro">
                    {rotulo(EVENTO, e.tipo || e.evento)}
                    {e.nodo ? ` · ${e.nodo}` : ''}
                  </span>
                ))}
              </p>
            )}
          </div>
        )}

        {/* --- Las órdenes, apagadas de noche ------------------------------ */}
        <div className={`tarjeta canal${abierta ? '' : ' canal-cerrado'}`}
             aria-disabled={!abierta}>
          <Titulo ayuda={D.ordenes}>Lo que la mesa acordó</Titulo>

          {!abierta && (
            <p className="canal-aviso">
              {cerrado
                ? 'El ejercicio terminó. Lo que queda es la proyección y el '
                  + 'debriefing.'
                : 'Es de noche: no se reciben órdenes. La consola vuelve a abrir '
                  + 'con la jornada siguiente.'}
            </p>
          )}

          <textarea
            rows={3}
            value={texto}
            disabled={!abierta || ocupado}
            onChange={e => setTexto(e.target.value)}
            placeholder={abierta
              ? 'Ej.: operar el Puente Amarillo con ESMAD, responsable el Ministro de Defensa'
              : 'La consola no recibe órdenes durante la noche.'}
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && abierta) interpretar()
            }}
          />
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.6rem',
                        flexWrap: 'wrap' }}>
            <button className="primario" onClick={interpretar}
                    disabled={!abierta || ocupado || !texto.trim()}>
              Interpretar la orden
            </button>
          </div>
          {error && <p style={{ color: 'var(--mal)', marginBottom: 0 }}>{error}</p>}
        </div>

        {/* --- El plan de vuelta ------------------------------------------- */}
        {plan && (
          <div className="tarjeta" style={{ marginTop: '1rem', borderColor: 'var(--acento)' }}>
            <Titulo ayuda={D.plan_interpretado}>Plan interpretado · para leer en voz alta</Titulo>
            <pre className="lectura">{plan.lectura_en_voz_alta}</pre>

            {plan.avisos?.map((a, i) => (
              <p key={i} style={{ color: 'var(--medio)', fontSize: '0.85rem' }}>{a}</p>
            ))}

            {/* Las dudas se resuelven con una ELECCIÓN TIPADA, no con texto
                libre. Sin esto, «no», «400» y «sí, confirmo» vuelven a entrar
                por el canal como si fueran órdenes nuevas. */}
            {plan.acciones.map((a, i) => (
              a.entidades
                .filter(e => e.candidatos?.length && e.estado !== 'ok')
                .map((e, j) => (
                  <div key={`${i}-${j}`} style={{ marginTop: '0.8rem' }}>
                    <p style={{ margin: '0 0 0.35rem', fontSize: '0.88rem' }}>{e.eco}</p>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {e.candidatos.map(c => (
                        <button key={c.id} disabled={ocupado}
                                style={{ fontSize: '0.82rem', padding: '0.3rem 0.6rem' }}
                                onClick={() => elegir(i, campoDe(a, e), c.id)}>
                          {c.nombre}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
            ))}

            {/* Una consulta no ordena nada: trae su respuesta del motor y se
                lee aquí mismo, sin gastar la jornada. */}
            {plan.acciones.filter(a => a.datos).map((a, i) => (
              <div key={`c${i}`} className="tarjeta"
                   style={{ marginTop: '0.8rem', background: 'var(--superficie-2)' }}>
                <Titulo ayuda={D.consulta}>{a.descripcion}</Titulo>
                <dl className="hoja-datos">
                  {Object.entries(a.datos).map(([k, v]) => (
                    <div key={k}>
                      <dt>{rotulo(CAMPO_CONSULTA, k)}</dt>
                      <dd className="num">{formatear(v)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            ))}

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
              <button className="primario" onClick={encolar}
                      disabled={!abierta || ocupado}>
                Añadir a la jornada
              </button>
              <button onClick={ejecutar} disabled={!abierta || ocupado}>
                Añadir y cerrar el día
              </button>
              <button onClick={() => setPlan(null)} disabled={ocupado}>
                Corregir
              </button>
            </div>
            <p className="nota-boton">
              <strong>Añadir no gasta la jornada.</strong> La orden queda en cola
              y la mesa puede dictar la siguiente. Todo se resuelve junto cuando
              cae la noche, sola o a mano.
            </p>
            <p className="procedencia">
              Interpretado por: {plan.interpretado_por}
              <Ayuda etiqueta="Qué capa tradujo la orden">{D.interpretado_por}</Ayuda>
            </p>
          </div>
        )}

        {/* --- Reportar, DESPUÉS de ejecutar ------------------------------- */}
        {resultado && (
          <div className="tarjeta" style={{ marginTop: '1rem' }}>
            <h2>
              {resultado.turno_avanzado !== false ? 'Lo que ocurrió'
                : resultado.acciones_encoladas > 0 ? 'En cola' : 'Respuesta'}
            </h2>
            <p className="num" style={{ marginTop: 0, color: 'var(--texto)' }}>
              {resultado.resumen}
            </p>
            {resultado.resultados?.map((r, i) => (
              <div key={i} style={{ marginTop: '0.5rem' }}>
                <span className={`chip chip-${r.ok ? 'bien' : 'mal'}`}>
                  {r.ok ? 'Ejecutada' : 'No viable'}
                </span>{' '}
                <span style={{ fontSize: '0.9rem' }}>{r.mensaje}</span>
                {r.datos?.p_incidente !== undefined && (
                  <>
                    <span className="num" style={{ fontSize: '0.78rem',
                                                   color: 'var(--texto-3)' }}>
                      {' '}· riesgo {Math.round(r.datos.p_incidente * 100)}&nbsp;%
                      · atribuible {r.datos.atribuible ? 'sí' : 'no'}
                    </span>
                    <Ayuda etiqueta="Cómo se calcula el riesgo">{D.riesgo_mostrado}</Ayuda>
                  </>
                )}
              </div>
            ))}
            {/* LO QUE NO SE EJECUTÓ. Antes desaparecía en silencio: la sala
                confirmaba tres órdenes, se ejecutaban dos, y el hueco no
                aparecía en ningún sitio hasta el debriefing. */}
            {resultado.omitidas?.length > 0 && (
              <div style={{ marginTop: '0.9rem', paddingTop: '0.7rem',
                            borderTop: '1px solid var(--borde)' }}>
                <p className="eyebrow" style={{ color: 'var(--medio)' }}>
                  No se ejecutó ({resultado.omitidas.length})
                  <Ayuda etiqueta="Por qué una orden confirmada no se ejecuta">
                    {D.omitidas}
                  </Ayuda>
                </p>
                {resultado.omitidas.map((o, i) => (
                  <p key={i} style={{ margin: '0.25rem 0', fontSize: '0.86rem',
                                      color: 'var(--texto-2)' }}>
                    <span className="chip chip-medio">{rotulo(ESTADO_PLAN, o.estado)}</span>{' '}
                    {o.motivo}
                  </p>
                ))}
              </div>
            )}

            {!resultado.resultados?.length && resultado.eventos?.length > 0 && (
              <ul style={{ fontSize: '0.88rem', color: 'var(--texto-2)' }}>
                {resultado.eventos.slice(0, 8).map((e, i) => (
                  <li key={i}>
                    {rotulo(EVENTO, e.tipo || e.evento)}{e.nodo ? ` · ${e.nodo}` : ''}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

/** Un valor de la hoja de datos, legible. Las listas se cuentan, no se vuelcan. */
function formatear(v) {
  if (Array.isArray(v)) {
    return v.length <= 4
      ? v.map(x => (typeof x === 'object' ? Object.values(x)[0] : x)).join(' · ')
      : `${v.length} elementos`
  }
  if (v && typeof v === 'object') return Object.values(v).join(' · ')
  if (typeof v === 'boolean') return v ? 'sí' : 'no'
  return String(v)
}

/**
 * El campo cuyo valor está en duda. Solo se pueden tocar campos declarados.
 *
 * Lo dice el motor: cada entidad viaja con el argumento del que salió. Antes se
 * adivinaba aquí buscando el valor crudo entre los argumentos, y para los
 * campos de LISTA —los puntos de `desplegar_equipos`— no aparecía nunca,
 * porque los que no resuelven no se guardan. Se caía en 'nodo_id', que esa
 * herramienta no declara, y el botón de corregir devolvía un 400.
 */
function campoDe(accion, entidad) {
  if (entidad.campo) return entidad.campo
  const par = Object.entries(accion.argumentos)
    .find(([, v]) => v === entidad.crudo)
  return par ? par[0] : 'nodo_id'
}
