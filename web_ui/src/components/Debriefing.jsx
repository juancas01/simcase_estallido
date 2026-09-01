// ---------------------------------------------------------------------------
// EL DEBRIEFING — la superficie del cierre.
//
// Veinte minutos que valen más que cualquier turno, y hasta ahora no había nada
// que proyectar. No es un tablero de resultados: es HECHOS Y CONTRASTE. Qué se
// decidió, qué pasó después, y la lectura de la corrida: por qué vía buscaron
// salida y a quién atendieron mientras lo hacían.
//
// NO HAY NADA DE ESTO ANTES DEL CIERRE, y no es una decisión de esta pantalla:
// el servidor rechaza `/api/debriefing` con un 409 mientras la última jornada
// no esté resuelta. Un marcador visible deja de medir la conducta y pasa a
// producirla — lo que se lleva la sala tiene que ser un retrato, no un puntaje.
//
// EL ORDEN DE LAS PESTAÑAS ES EL ORDEN EN QUE SE CONDUCE UN DEBRIEFING:
//   1 · EL PAÍS ...... el que se recibió contra el que se entrega, y la
//                      proyección: ¿esto se sostiene sin ustedes?
//   2 · LA LECTURA ... la firma, las seis vías, la atención y el saldo — la
//                      caracterización del cómo y el qué (LA_MEDICION.md)
//   3 · LA LÍNEA ..... lo que cada rol declaró el turno 0 contra lo que hizo
//   4 · EL PLIEGO .... cada decisión con la ventana en que cayó
//   5 · LOS MOMENTOS . las tres veces que el ejercicio cambió de época
//
// LO QUE NUNCA MUESTRA: la mezcla real de un punto y la veracidad de una
// denuncia. El cierre no destapa la capa 1 — esa revelación, si algún día se
// hace, es una decisión del equipo docente y no de esta pantalla.
//
// AQUÍ SÍ HAY CIFRAS, y no es una contradicción con la regla del tablero. «Un
// nivel se interpreta; un número se optimiza» vale para la sala DECIDIENDO; el
// debriefing mira hacia atrás, ya no hay nada que optimizar, y la cifra es lo
// que tiene un peso en la conversación.
// ---------------------------------------------------------------------------

import { useState } from 'react'
import Cabecera from './Cabecera'
import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import {
  BANDA_SALDO, PUBLICO, VIA, VIAS_QUE_ABREN, VIAS_QUE_NO_ABREN,
} from '../etiquetas.jsx'
import { Cargando, Dinero, useDatos } from '../comun.jsx'

const PESTANAS = [
  { id: 'pais', nombre: 'El país' },
  { id: 'lectura', nombre: 'La lectura' },
  { id: 'linea', nombre: 'La línea' },
  { id: 'pliego', nombre: 'El pliego' },
  { id: 'momentos', nombre: 'Los momentos' },
]

export default function Debriefing() {
  // Una sola lectura: con el ejercicio cerrado, estos datos no cambian jamás.
  const { datos, error } = useDatos('/debriefing', 0)
  const [pestana, setPestana] = useState('pais')

  if (error && /no ha terminado/i.test(error)) {
    return (
      <div className="pantalla">
        <div className="cuerpo cargando">
          <div className="cargando-caja">
            <div className="eyebrow">Debriefing</div>
            <p className="cargando-titulo">El ejercicio no ha terminado.</p>
            <p className="cargando-detalle">{error}</p>
            <a className="enlace-superficie" href="/">Volver al tablero</a>
          </div>
        </div>
      </div>
    )
  }
  if (!datos) return <Cargando error={error} ruta="/debriefing" />

  return (
    <div className="pantalla">
      <Cabecera eyebrow="Cierre del ejercicio" titulo="Debriefing" a="tablero" />
      <div className="cuerpo cuerpo-debriefing">
        <div className="pestanas" role="tablist" aria-label="Paneles del debriefing">
          {PESTANAS.map((p) => (
            <button key={p.id} role="tab" type="button"
                    aria-selected={pestana === p.id}
                    className={`pestana${pestana === p.id ? ' activa' : ''}`}
                    onClick={() => setPestana(p.id)}>
              {p.nombre}
            </button>
          ))}
        </div>

        {pestana === 'pais' && <ElPais datos={datos} />}
        {pestana === 'lectura' && <LaLectura lectura={datos.lectura} />}
        {pestana === 'linea' && <LaLinea lineas={datos.lineas_vs_ejecutada} />}
        {pestana === 'pliego' && <ElPliego jornadas={datos.pliego_por_jornada} />}
        {pestana === 'momentos' && <LosMomentos momentos={datos.momentos} />}
      </div>
    </div>
  )
}


// ---------------------------------------------------------------------------
// 1 · EL PAÍS QUE SE RECIBIÓ Y EL QUE SE ENTREGA
// ---------------------------------------------------------------------------

function ElPais({ datos }) {
  const { recibido, entregado, proyeccion, lectura } = datos
  const despues = proyeccion?.despues || {}
  const antes_de_entregar = proyeccion?.antes || {}
  const reservasCierre = entregado?.reservas || {}
  const reservas72 = proyeccion?.reservas_finales || {}

  // NO LAS VEINTE: LAS SEIS QUE SIGNIFICAN ALGO. Las cuatro reservas juntas
  // no le dicen a la sala nada que no diga ya la conversación; estas seis son
  // las que abren el debriefing.
  const magnitudes = [
    { nombre: 'Presión en la calle', antes: recibido.presion_calle,
      cierre: antes_de_entregar.presion_calle, h72: despues.presion_calle },
    { nombre: 'Legitimidad', antes: recibido.legitimidad,
      cierre: reservasCierre.legitimidad, h72: reservas72.legitimidad },
    { nombre: 'Credibilidad de la mesa', antes: recibido.credibilidad_mesa,
      cierre: reservasCierre.credibilidad_mesa, h72: reservas72.credibilidad_mesa },
    { nombre: 'Muertes evitables', antes: recibido.muertes_evitables,
      cierre: entregado.muertes_evitables, h72: despues.muertes_evitables },
    { nombre: 'Puntos abiertos', antes: recibido.puntos_abiertos,
      cierre: antes_de_entregar.puntos_abiertos, h72: despues.puntos_abiertos },
  ]

  return (
    <section className="debrief-panel">
      <Titulo>El país que se recibió y el que se entrega</Titulo>
      <p className="panel-sub">
        Apertura contra cierre, y la proyección a 72 horas sin nadie al mando —
        la pregunta con la que abre un debriefing: ¿esto se sostiene sin ustedes?
      </p>
      <div className="pais-tabla">
        <div className="pais-fila pais-encabezado">
          <span />
          <span>Recibido</span>
          <span>Entregado</span>
          <span>+72 h</span>
        </div>
        {magnitudes.map((m) => (
          <div key={m.nombre} className="pais-fila">
            <span className="pais-nombre">{m.nombre}</span>
            <Celda valor={m.antes} />
            <Celda valor={m.cierre} />
            <Celda valor={m.h72} atenuada />
          </div>
        ))}
      </div>
      <p className="pais-nota">
        La pérdida por bloqueos acumulada en las cinco jornadas fue de{' '}
        <Dinero valor={lectura?.saldo?.empresa?.perdida_mm_cop || 0} />
        — no había una cifra de partida que oponerle, porque el país llegó con
        los corredores ya cerrados.
      </p>
    </section>
  )
}

function Celda({ valor, atenuada }) {
  const vacio = valor === undefined || valor === null
  return (
    <span className={`pais-celda${atenuada ? ' atenuada' : ''}`}>
      {vacio ? '—' : Math.round(valor)}
    </span>
  )
}


// ---------------------------------------------------------------------------
// 2 · LA LECTURA — la caracterización del cómo y el qué
// ---------------------------------------------------------------------------

function LaLectura({ lectura }) {
  if (!lectura) return null
  const { firma, como, que } = lectura
  return (
    <>
      <section className="debrief-panel">
        <Titulo>La firma de la sala</Titulo>
        <p className="firma">{firma}</p>
        <p className="panel-sub">Se lee en voz alta y se deja en pantalla.</p>
      </section>

      <section className="debrief-panel">
        <Titulo>Las seis vías{' '}
          <Ayuda etiqueta="Definición de las vías">{D.vias}</Ayuda>
        </Titulo>
        <p className="panel-sub">
          Por qué vía buscaron salida al bloqueo: las tres primeras abren un
          punto; las otras tres lo sortean, cambian las reglas o cambian lo que
          el país cree que pasa.
        </p>
        <div className="vias-bloques">
          <BloqueVias titulo="Abren un punto" vias={VIAS_QUE_ABREN} como={como} />
          <BloqueVias titulo="No abren ningún punto" vias={VIAS_QUE_NO_ABREN} como={como} />
        </div>
        <Desgaste desgaste={como.desgaste} />
        <Calificadores como={como} />
      </section>

      <section className="debrief-panel">
        <Titulo>A quién atendieron{' '}
          <Ayuda etiqueta="Definición de la atención">{D.atencion}</Ayuda>
        </Titulo>
        <p className="panel-sub">
          Dónde gastaron sus decisiones. Atender a uno es no atender a otro:
          el reparto mide una prioridad.
        </p>
        <div className="atencion-lista">
          {Object.entries(que.atencion.por_publico).map(([id, d]) => (
            <BarraAtencion key={id} nombre={PUBLICO[id]} decisiones={d.decisiones}
                           proporcion={d.proporcion} />
          ))}
          <BarraAtencion nombre="Gobierno de sí mismo"
                         decisiones={que.atencion.gobierno_de_si_mismo.decisiones}
                         proporcion={que.atencion.gobierno_de_si_mismo.proporcion}
                         residuo ayuda={D.gobierno_de_si_mismo} />
        </div>
      </section>

      <section className="debrief-panel">
        <Titulo>Atención contra saldo{' '}
          <Ayuda etiqueta="Definición del saldo">{D.saldo}</Ayuda>
        </Titulo>
        <p className="panel-sub">
          Atender no es servir. El cruce de las dos columnas es el material del
          debriefing; despliegue los hechos de cada celda.
        </p>
        <Cruce que={que} />
      </section>

      <section className="debrief-panel panel-nadie">
        <Titulo>El público que nadie miró{' '}
          <Ayuda etiqueta="Qué es esta línea">{D.el_publico_que_nadie_miro}</Ayuda>
        </Titulo>
        {que.publico_que_nadie_miro.publico ? (
          <>
            <p className="firma">
              {que.publico_que_nadie_miro.linea}{' '}
              {que.publico_que_nadie_miro.consecuencia}
            </p>
            <p className="panel-sub">
              La salida de una sola línea: es la que más se recuerda.
            </p>
          </>
        ) : (
          <p className="firma">{que.publico_que_nadie_miro.linea}</p>
        )}
      </section>

      {que.empresa_sin_fuerza.atendieron > 0 && (
        <section className="debrief-panel">
          <Titulo>Atender a la empresa sin gastar fuerza</Titulo>
          <p className="panel-sub">
            De las decisiones que atendieron a la empresa, cuántas fueron por
            una vía distinta de la fuerza. En este repertorio casi todo lo que
            la atiende gasta capacidad de la fuerza pública — esta cuenta es la
            que distingue una sala imaginativa de una obediente.
          </p>
          <p className="firma">
            {que.empresa_sin_fuerza.sin_fuerza} de{' '}
            {que.empresa_sin_fuerza.atendieron}
            {que.empresa_sin_fuerza.ejemplos?.length > 0 && (
              <> · {que.empresa_sin_fuerza.ejemplos.join(' · ')}</>
            )}
          </p>
        </section>
      )}

      <section className="debrief-panel">
        <Titulo>Lo que esta lectura no mide</Titulo>
        <ul className="cautelas">
          {lectura.cautelas.map((c) => <li key={c}>{c}</li>)}
        </ul>
      </section>
    </>
  )
}

function BloqueVias({ titulo, vias, como }) {
  const max = Math.max(...Object.values(como.vias).map((v) => v.decisiones), 1)
  return (
    <div className="vias-bloque">
      <h3>{titulo}</h3>
      {vias.map((v) => {
        const d = como.vias[v]
        const aperturas = v === 'despejar' ? como.aperturas.fuerza
          : v === 'concertar' ? como.aperturas.concertacion
          : v === 'desgastar' ? como.aperturas.desgaste : null
        return (
          <div key={v} className="via-fila">
            <span className="via-nombre">{VIA[v]}</span>
            <div className="via-barra-zona">
              <div className="via-barra"
                   style={{ width: `${(d.decisiones / max) * 100}%` }} />
            </div>
            <span className="via-cuenta">
              {d.decisiones}
              {aperturas !== null && d.decisiones > 0 && (
                <span className="via-detalle">
                  {' '}{aperturas} apertura{aperturas === 1 ? '' : 's'}
                </span>
              )}
            </span>
          </div>
        )
      })}
    </div>
  )
}

function Desgaste({ desgaste }) {
  if (!desgaste.lo_desgastaron.length && !desgaste.se_les_cayo_de_hambre.length) {
    return null
  }
  return (
    <div className="desgaste-partido">
      {desgaste.lo_desgastaron.length > 0 && (
        <p>
          <strong>Lo desgastaron:</strong>{' '}
          {desgaste.lo_desgastaron.map((d) => `${d.nodo} (J${d.jornada})`).join(', ')}
        </p>
      )}
      {desgaste.se_les_cayo_de_hambre.length > 0 && (
        <p className="con-mal">
          <strong>Se les cayó de hambre:</strong>{' '}
          {desgaste.se_les_cayo_de_hambre.map((d) => `${d.nodo} (J${d.jornada})`).join(', ')}
        </p>
      )}
      <p className="panel-sub">{desgaste.nota}</p>
    </div>
  )
}

function Calificadores({ como }) {
  const { c1_anticiparon: c1, c2_aguantaron: c2, c3_miraron: c3 } = como.calificadores
  const revertidas = c2.revertidas_misma_jornada.fuerza || 0
  return (
    <div className="calificadores">
      <div className="calificador">
        <h3>¿Anticiparon o reaccionaron?</h3>
        <p>
          {c1.anticipadas} banderas llegaron antes del primer incidente
          {c1.primer_incidente !== null && <> (jornada {c1.primer_incidente})</>}.
        </p>
      </div>
      <div className="calificador">
        <h3>¿Aguantó lo que abrieron?</h3>
        <p>
          {revertidas} de {c2.aperturas.fuerza} aperturas por fuerza se
          revirtieron esa misma jornada.
        </p>
      </div>
      <div className="calificador">
        <h3>¿Miraron antes de mover?</h3>
        <p>
          De {c3.puntos_operados} puntos operados, {c3.verificados_antes}
          estaban verificados antes.
        </p>
      </div>
    </div>
  )
}

function BarraAtencion({ nombre, decisiones, proporcion, residuo, ayuda }) {
  const pct = Math.round((proporcion || 0) * 100)
  return (
    <div className={`atencion-fila${residuo ? ' residuo' : ''}`}>
      <span className="atencion-nombre" title={ayuda}>{nombre}</span>
      <div className="atencion-barra-zona">
        <div className={`atencion-barra${residuo ? ' barra-residuo' : ''}`}
             style={{ width: `${Math.max(proporcion * 100, decisiones > 0 ? 4 : 0)}%` }} />
      </div>
      <span className="atencion-cuenta">{decisiones} · {pct}%</span>
    </div>
  )
}

function Cruce({ que }) {
  const niveles = ['alta', 'media', 'baja']
  const bandas = ['bien', 'regular', 'mal']
  return (
    <div className="cruce">
      <div className="cruce-fila cruce-encabezado">
        <span />
        {bandas.map((b) => <span key={b}>Saldo {BANDA_SALDO[b]}</span>)}
      </div>
      {niveles.map((n) => (
        <div key={n} className="cruce-fila">
          <span className="cruce-eje">
            {n === 'alta' ? 'Atención alta' : n === 'media' ? 'Atención media' : 'Atención baja'}
          </span>
          {bandas.map((b) => {
            const dentro = Object.entries(que.cruce)
              .filter(([, c]) => c.atencion === n && c.saldo === b)
            return (
              <span key={b} className={`cruce-celda${dentro.length ? ' con-alguien' : ''}`}>
                {dentro.map(([p, c]) => (
                  <details key={p}>
                    <summary>{PUBLICO[p]}</summary>
                    <div className="cruce-celda-frase">{c.celda}</div>
                    <ul>
                      {que.saldo[p].hechos.map((h) => <li key={h}>{h}</li>)}
                    </ul>
                  </details>
                ))}
              </span>
            )
          })}
        </div>
      ))}
    </div>
  )
}


// ---------------------------------------------------------------------------
// 3 · LA LÍNEA DECLARADA CONTRA LA EJECUTADA
// ---------------------------------------------------------------------------

function LaLinea({ lineas }) {
  return (
    <section className="debrief-panel">
      <Titulo>La línea declarada contra la ejecutada</Titulo>
      <p className="panel-sub">
        Lo que cada rol dijo en el turno 0, y lo que el pliego dice que hizo.
        Casi todas las salas declaran una secuencia —«primero la mesa, fuerza
        solo si falla»— y casi ninguna la cumple.
      </p>
      <div className="lineas-lista">
        {(lineas || []).map((l) => (
          <div key={l.rol} className="linea-rol">
            <div className="linea-cabecera">
              <strong>{l.rol}</strong>
              <span className="linea-contador">
                {l.decisiones} decisión{l.decisiones === 1 ? '' : 'es'}
              </span>
            </div>
            <p className="linea-declarada">
              {l.declarada || '— no declaró línea —'}
            </p>
            <p className="linea-ejecutada">
              {l.ejecutada.length > 0 ? l.ejecutada.join(' · ') : '— sin decisiones —'}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}


// ---------------------------------------------------------------------------
// 4 · EL PLIEGO, CON LA VENTANA EN QUE CAYÓ CADA DECISIÓN
// ---------------------------------------------------------------------------

function ElPliego({ jornadas }) {
  return (
    <section className="debrief-panel">
      <Titulo>Las decisiones y la ventana en que cayeron</Titulo>
      <p className="panel-sub">
        El pliego completo de la corrida. Al lado de cada decisión, sus vías y
        su público — la imputación que la lectura cuenta. El motor no atribuye
        una consecuencia a una decisión: varias caen en la misma ventana y el
        mundo además se mueve solo. Lo que se muestra es lo que es.
      </p>
      <div className="pliego-jornadas">
        {(jornadas || []).map((j) => (
          <div key={j.jornada} className="pliego-jornada">
            <div className="pliego-cabecera">
              <h3>Jornada {j.jornada}</h3>
              <span className="pliego-resumen">{j.resumen}</span>
            </div>
            {j.decisiones.length === 0 ? (
              <p className="pliego-vacia">Sin decisiones esta jornada.</p>
            ) : (
              <table className="pliego-tabla">
                <tbody>
                  {j.decisiones.map((d, i) => (
                    <tr key={i}>
                      <td className="pliego-rol">{d.rol}</td>
                      <td>
                        {d.nombre}
                        {d.responsable && (
                          <span className="pliego-responsable"> · {d.responsable}</span>
                        )}
                      </td>
                      <td className="pliego-vias">
                        {d.via.map((v) => (
                          <span key={v} className="chip-via">{VIA[v]}</span>
                        ))}
                        {d.atiende.length > 0 && d.atiende.map((p) => (
                          <span key={p} className="chip-publico">{PUBLICO[p]}</span>
                        ))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}


// ---------------------------------------------------------------------------
// 5 · LOS TRES MOMENTOS
// ---------------------------------------------------------------------------

function LosMomentos({ momentos }) {
  const m = momentos || {}
  const momentosLista = [
    {
      titulo: 'La mesa dejó de ser una mesa',
      valor: m.la_mesa_dejo_de_ser_mesa,
      texto: (v) => `El Comité suspendió su participación en la jornada ${v}.`,
      vacio: 'El Comité se sentó hasta el final.',
    },
    {
      titulo: 'El primer registro escrito',
      valor: m.primer_registro_escrito,
      texto: (v) => `Todo lo que vino después quedó por escrito desde la jornada ${v}.`,
      vacio: 'La sala nunca dejó registro escrito.',
    },
    {
      titulo: 'La primera región en rojo',
      valor: m.primera_region_en_rojo?.jornada,
      texto: () => `${m.primera_region_en_rojo?.region} cruzó el reloj de oxígeno.`,
      vacio: 'Ninguna región pasó el semáforo a rojo.',
    },
  ]
  return (
    <section className="debrief-panel">
      <Titulo>Los tres momentos</Titulo>
      <p className="panel-sub">
        Las tres veces que el ejercicio cambió de época. Ninguna se ve mientras
        pasa; todas se ven después.
      </p>
      <div className="momentos-lista">
        {momentosLista.map((x) => (
          <div key={x.titulo} className="momento">
            <h3>{x.titulo}</h3>
            {x.valor
              ? <p className="momento-dato">{x.texto(x.valor)}</p>
              : <p className="momento-dato atenuada">{x.vacio}</p>}
          </div>
        ))}
      </div>
    </section>
  )
}
