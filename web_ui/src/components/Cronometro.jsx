// ---------------------------------------------------------------------------
// EL CRONÓMETRO DE SALA — el mismo número en las diez pantallas.
//
// La jornada son quince minutos partidos en dos, y el cronómetro dice en cuál
// de los dos va y cuánto le queda:
//
//     DÍA    13 min   se lee, se discute y SE ORDENA
//     NOCHE   2 min   se resuelve y se mira. NO SE RECIBEN ÓRDENES
//
// El tiempo no se cambia a mano. Arranca UNA VEZ, desde la consola, y a partir
// de ahí corre solo: la jornada se cierra sola al minuto trece y la siguiente se
// abre sola dos minutos después.
//
// POR QUÉ NO CUENTA EL NAVEGADOR
// ------------------------------
// Porque hay once pantallas mirando —el tablero, la consola y las nueve vistas—
// y un cronómetro por pantalla es un cronómetro DISTINTO por pantalla en cuanto
// una se recarga a mitad de jornada. El servidor guarda tres instantes; aquí
// solo se dibuja lo que se deriva de ellos.
//
// EL DESFASE, QUE ES LA PIEZA QUE LO SOSTIENE
// -------------------------------------------
// El servidor manda su `ahora` en cada respuesta. Al llegar una nueva, esta capa
// mide cuánto se aparta del reloj de esta máquina y guarda la diferencia. A
// partir de ahí cuenta sola, cada medio segundo, sobre el reloj del servidor y
// no sobre el suyo.
//
// Eso resuelve las dos cosas a la vez: **entre respuesta y respuesta el número
// avanza** —un cronómetro que salta de dos en dos segundos no es un
// cronómetro— y **el portátil que va tres minutos adelantado enseña la misma
// hora que los demás**, porque su hora no se usa para nada salvo para medir su
// propio desfase.
//
// LA PAUSA SE VE. Con el reloj detenido el número se congela y la caja lo dice:
// un cronómetro parado que parece corriendo es peor que no tener cronómetro.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react'

/** `1:07`, y `1:02:30` en cuanto hay horas. La sesión entera dura dos. */
function reloj(segundos) {
  const v = Math.max(0, Math.floor(segundos))
  const h = Math.floor(v / 3600)
  const m = Math.floor((v % 3600) / 60)
  const s = v % 60
  const dd = (n) => String(n).padStart(2, '0')
  return h > 0 ? `${h}:${dd(m)}:${dd(s)}` : `${m}:${dd(s)}`
}

/**
 * En qué tramo cae `t` segundos de jornada, y cuánto le queda.
 *
 * La tabla llega del servidor en cada respuesta. Tenerla aquí escrita otra vez
 * sería un dato en dos sitios, y un dato en dos sitios se desincroniza.
 */
function tramoEn(fases, t) {
  let acumulado = 0
  for (const f of fases) {
    const dura = f.minutos * 60
    if (t < acumulado + dura) {
      return { fase: f, dura, transcurrido: t - acumulado,
               restante: acumulado + dura - t, prorroga: 0 }
    }
    acumulado += dura
  }
  const ultima = fases[fases.length - 1]
  const dura = ultima.minutos * 60
  return { fase: ultima, dura, transcurrido: dura, restante: 0,
           prorroga: t - acumulado }
}

function useCronometro(c) {
  const desfase = useRef(0)
  const [ahoraLocal, setAhoraLocal] = useState(null)

  // El desfase se remide SOLO al llegar una respuesta nueva, y en un efecto:
  // medirlo durante el pintado mezclaría un `ahora` viejo con la hora de ahora,
  // y el error crecería tanto como la edad de la respuesta.
  useEffect(() => {
    if (c?.ahora) desfase.current = c.ahora - Date.now() / 1000
  }, [c?.ahora])

  // Medio segundo: un cronómetro de segundos refrescado cada segundo se salta
  // uno de cada tantos por redondeo, y se nota.
  const corriendoDeVerdad = Boolean(c?.corriendo && !c?.pausado)
  useEffect(() => {
    if (!corriendoDeVerdad) return undefined
    const t = setInterval(
      () => setAhoraLocal(Date.now() / 1000 + desfase.current), 500)
    return () => clearInterval(t)
  }, [corriendoDeVerdad])

  if (!c) return null
  if (!c.corriendo) return { corriendo: false }

  // El mayor de los dos, y no el latido a secas. Cubre los dos huecos: antes
  // del primer latido manda el `ahora` del servidor —exacto en el instante de
  // la respuesta—, y tras un reinicio manda también él, porque el latido que
  // quedó guardado es de antes. El tiempo solo avanza.
  //
  // EN PAUSA MANDA `pausa_desde`, que es el instante en que el reloj se detuvo:
  // así el número se queda exactamente donde estaba en las diez pantallas.
  const ahora = c.pausado
    ? c.pausa_desde
    : Math.max(ahoraLocal ?? 0, c.ahora)
  const enJornada = Math.max(0, ahora - c.jornada_desde)
  const total = Math.max(0, ahora - (c.sesion_desde ?? c.jornada_desde))

  return {
    corriendo: true,
    pausado: Boolean(c.pausado),
    cerrado: Boolean(c.cerrado),
    total,
    ...tramoEn(c.fases, enJornada),
  }
}

export default function Cronometro({ cronometro }) {
  const r = useCronometro(cronometro)
  if (!r) return null

  if (!r.corriendo) {
    return (
      <div className="cronometro sin-iniciar">
        <div className="cronometro-cabeza">
          <span className="cronometro-fase">Sin iniciar</span>
          <span className="cronometro-resta num">—:—</span>
        </div>
        <div className="cronometro-pie">El reloj arranca desde la consola.</div>
      </div>
    )
  }

  const { fase, dura, transcurrido, restante, prorroga, total, pausado, cerrado } = r
  const hayProrroga = prorroga > 0
  const avance = Math.min(100, (transcurrido / dura) * 100)
  const esNoche = fase.id === 'noche'

  return (
    <div className={`cronometro${esNoche ? ' es-noche' : ''}`
      + `${pausado ? ' en-pausa' : hayProrroga ? ' en-prorroga' : ''}`}>
      <div className="cronometro-cabeza">
        <span className="cronometro-fase">
          {cerrado ? 'Ejercicio cerrado' : fase.nombre}
        </span>
        <span className="cronometro-resta num">
          {hayProrroga ? `+${reloj(prorroga)}` : reloj(restante)}
        </span>
      </div>

      <div className="cronometro-barra">
        <div style={{ width: `${avance}%` }} />
      </div>

      <div className="cronometro-pie">
        <span>
          {pausado ? 'En pausa'
            : cerrado ? 'No se reciben más órdenes'
              : fase.admite_ordenes ? 'Se pueden dictar órdenes'
                : 'Consecuencias · sin órdenes'}
        </span>
        <span className="num">{reloj(total)} en total</span>
      </div>
    </div>
  )
}
