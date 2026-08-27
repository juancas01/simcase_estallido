// ---------------------------------------------------------------------------
// SUPERFICIE 4 · LA CONSOLA — donde se transcriben las órdenes.
//
// NO HAY MODERADOR COMO FIGURA APARTE. Esta es una superficie más, y quien la
// opera —puede ser uno de los ocho— solo transcribe: no conduce, no reparte
// información, no decide el ritmo y no sabe nada que los demás no sepan.
//
// EL MOMENTO QUE IMPORTA es el paso 3: se escribe lo que la mesa acordó, y la
// pantalla devuelve el plan interpretado CON SU BANDA DE RIESGO. La sala lo lee
// junta y con frecuencia cambia la orden. Que salga de la pantalla y no de una
// persona lo hace todavía más difícil de discutir.
//
//     El LLM traduce. El motor decide, valida, ejecuta y reporta.
//
// Ninguna frase sobre el RESULTADO de una orden se escribe antes de que la orden
// se ejecute. Es el primero de los ocho modos de falla y el más difícil de ver.
// ---------------------------------------------------------------------------

import { useState } from 'react'
import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { CAMPO_CONSULTA, ESTADO_PLAN, FASE, FRANJA, rotulo } from '../etiquetas.jsx'
import { api, FASES, useDatos } from '../comun.jsx'

export default function Consola() {
  const { datos: tablero, recargar } = useDatos('/tablero', 5000)
  const { datos: cfg } = useDatos('/config', 0)
  const [texto, setTexto] = useState('')
  const [plan, setPlan] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [error, setError] = useState(null)

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

  const ejecutar = () => hacer(async () => {
    const r = await api('/consola/ejecutar', {
      method: 'POST', body: JSON.stringify({ plan_id: plan.plan_id }),
    })
    setResultado(r); setPlan(null); setTexto(''); recargar()
  })

  const noche = () => hacer(async () => {
    setResultado(await api('/consola/noche', { method: 'POST' }))
    setPlan(null); recargar()
  })

  const elegir = (indice, campo, valor) => hacer(async () => {
    setPlan(await api('/consola/elegir', {
      method: 'POST',
      body: JSON.stringify({ plan_id: plan.plan_id, indice, campo, valor }),
    }))
  })

  const fase = (f) => hacer(async () => {
    await api(`/consola/fase/${f}`, { method: 'POST' }); recargar()
  })

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <span className="eyebrow">Consola · no proyectar</span>
          <h1>Transcripción de órdenes</h1>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="num" style={{ fontWeight: 600 }}>
            Turno {tablero?.turno_decision ?? 0} · {rotulo(FRANJA, tablero?.franja)}
          </div>
          <div className="eyebrow">{rotulo(FASE, tablero?.fase)}</div>
        </div>
      </header>

      <div className="cuerpo" style={{ maxWidth: 1000, width: '100%', margin: '0 auto' }}>
        {cfg && !cfg.llave_presente && (
          <div className="tarjeta" style={{ borderColor: 'var(--medio)', marginBottom: '1rem' }}>
            {/* El diagnóstico del motor no se borra: se retira al globo. Es un
                dato, y además el único sitio donde consta qué falta exactamente. */}
            <h2 style={{ color: 'var(--medio)' }}>
              Sin llave de API
              <Ayuda etiqueta="Qué implica correr sin llave">
                <>
                  <p>{cfg.mensaje}</p>
                  <p>
                    Las capas de lenguaje natural quedan en modo determinista. El
                    ejercicio se desarrolla completo: ninguna decisión de la
                    simulación está delegada al modelo.
                  </p>
                </>
              </Ayuda>
            </h2>
            <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--texto-2)' }}>
              Escriba <code>OPENAI_API_KEY</code> en <code>{cfg.archivo_env}</code> y
              reinicie el servidor.
            </p>
          </div>
        )}

        {/* --- El reloj de fases: lo lleva el sistema, no una persona ------- */}
        <div className="tarjeta" style={{ marginBottom: '1rem' }}>
          <Titulo ayuda={D.fases}>Fase del turno</Titulo>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {FASES.map(f => (
              <button
                key={f.id}
                onClick={() => fase(f.id)}
                disabled={ocupado}
                className={tablero?.fase === f.id ? 'primario' : ''}
                style={{ fontSize: '0.8rem', padding: '0.35rem 0.7rem' }}
              >
                {f.nombre} · {f.min} min
              </button>
            ))}
          </div>
          {tablero?.congelado && (
            <p style={{ margin: '0.6rem 0 0', fontSize: '0.8rem', color: 'var(--medio)' }}>
              Pantallas congeladas
              <Ayuda etiqueta="Qué significa congelado">{D.congelado}</Ayuda>
            </p>
          )}
        </div>

        {/* --- Paso 3 · órdenes ------------------------------------------- */}
        <div className="tarjeta">
          <Titulo ayuda={D.ordenes}>Lo que la mesa acordó</Titulo>
          <textarea
            rows={3}
            value={texto}
            onChange={e => setTexto(e.target.value)}
            placeholder="Ej.: operen el Puente Amarillo con ESMAD, con dupla de la Defensoría, responsable el Ministro de Defensa"
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) interpretar()
            }}
          />
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.6rem',
                        flexWrap: 'wrap' }}>
            <button className="primario" onClick={interpretar}
                    disabled={ocupado || !texto.trim()}>
              Interpretar y leer de vuelta
            </button>
            <button onClick={noche} disabled={ocupado}>
              Resolver el interludio nocturno
            </button>
          </div>
          {error && <p style={{ color: 'var(--mal)', marginBottom: 0 }}>{error}</p>}
        </div>

        {/* --- El plan de vuelta ------------------------------------------- */}
        {plan && (
          <div className="tarjeta" style={{ marginTop: '1rem', borderColor: 'var(--acento)' }}>
            <Titulo ayuda={D.plan_interpretado}>Plan interpretado · léalo en voz alta</Titulo>
            <pre className="lectura">{plan.lectura_en_voz_alta}</pre>

            {plan.avisos?.map((a, i) => (
              <p key={i} style={{ color: 'var(--medio)', fontSize: '0.85rem' }}>{a}</p>
            ))}

            {/* Las dudas se resuelven con una ELECCIÓN TIPADA, no con texto
                libre. Sin esto, «no», «400» y «sí, confirmo» vuelven a entrar
                por el canal como si fueran órdenes nuevas.

                Se ofrecen botones también cuando el nombre NO EXISTE: el
                resolutor ya calculó a qué se parece, y sin esto había que
                reescribir la orden entera para corregir una letra. */}
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
                lee aquí mismo, sin gastar el turno. */}
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
              <button className="primario" onClick={ejecutar} disabled={ocupado}>
                Ejecutar
              </button>
              <button onClick={() => setPlan(null)} disabled={ocupado}>
                Corregir
              </button>
            </div>
            <p className="procedencia">
              Interpretado por: {plan.interpretado_por}
              <Ayuda etiqueta="Qué capa tradujo la orden">{D.interpretado_por}</Ayuda>
            </p>
          </div>
        )}

        {/* --- Paso 7 · reportar, DESPUÉS de ejecutar ---------------------- */}
        {resultado && (
          <div className="tarjeta" style={{ marginTop: '1rem' }}>
            <h2>Lo que ocurrió</h2>
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
                      {' '}· riesgo {Math.round(r.datos.p_incidente * 100)} %
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
                  <li key={i}>{e.tipo || e.evento}{e.nodo ? ` · ${e.nodo}` : ''}</li>
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

/** El campo cuyo valor está en duda. Solo se pueden tocar campos declarados. */
function campoDe(accion, entidad) {
  const par = Object.entries(accion.argumentos)
    .find(([, v]) => v === entidad.crudo)
  return par ? par[0] : 'nodo_id'
}
