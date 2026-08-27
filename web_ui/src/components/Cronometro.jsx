// ---------------------------------------------------------------------------
// EL CRONÓMETRO DE SALA — el mismo número en las diez pantallas.
//
// El tiempo dejó de cambiarse a mano. Arranca UNA VEZ, desde la consola, y a
// partir de ahí corre solo: la fase que toca se calcula, no se elige.
//
// POR QUÉ NO CUENTA EL NAVEGADOR
// ------------------------------
// Porque hay diez pantallas mirando —el tablero, la consola y las ocho vistas—
// y un cronómetro por pantalla es un cronómetro DISTINTO por pantalla en cuanto
// una se recarga a mitad de turno. El servidor guarda dos instantes; aquí solo
// se dibuja lo que se deriva de ellos.
//
// EL DESFASE, QUE ES LA PIEZA QUE LO SOSTIENE
// -------------------------------------------
// El servidor manda su `ahora` en cada respuesta. Al llegar una nueva, esta capa
// mide cuánto se aparta del reloj de esta máquina y guarda la diferencia. A
// partir de ahí cuenta sola, cada medio segundo, sobre el reloj del servidor y
// no sobre el suyo.
//
// Eso resuelve las dos cosas a la vez: **entre respuesta y respuesta el número
// avanza** —un cronómetro que salta de cuatro en cuatro segundos no es un
// cronómetro— y **el portátil que va tres minutos adelantado enseña la misma
// hora que los demás**, porque su hora no se usa para nada salvo para medir su
// propio desfase.
//
// AGOTADO EL CICLO NO SE ENCADENA NADA. Se queda en la última fase y cuenta la
// prórroga. Que el ejercicio pase de turno es una decisión de la sala, y el
// reloj no la toma por ella.
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
 * En qué fase cae `t` segundos de ciclo, y cuánto le queda.
 *
 * La tabla llega del servidor en cada respuesta. Tenerla aquí escrita otra vez
 * sería un dato en dos sitios, y un dato en dos sitios se desincroniza.
 */
function faseEn(fases, t) {
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
  useEffect(() => {
    if (!c?.corriendo) return undefined
    const t = setInterval(
      () => setAhoraLocal(Date.now() / 1000 + desfase.current), 500)
    return () => clearInterval(t)
  }, [c?.corriendo])

  if (!c) return null
  if (!c.corriendo) return { corriendo: false }

  // El mayor de los dos, y no el latido a secas. Cubre los dos huecos: antes
  // del primer latido manda el `ahora` del servidor —exacto en el instante de
  // la respuesta—, y tras un reinicio manda también él, porque el latido que
  // quedó guardado es de antes. El tiempo solo avanza.
  const ahora = Math.max(ahoraLocal ?? 0, c.ahora)
  const enTurno = Math.max(0, ahora - c.turno_desde)
  return {
    corriendo: true,
    total: Math.max(0, ahora - (c.sesion_desde ?? c.turno_desde)),
    ...faseEn(c.fases, enTurno),
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

  const { fase, dura, transcurrido, restante, prorroga, total } = r
  const hayProrroga = prorroga > 0
  const avance = Math.min(100, (transcurrido / dura) * 100)

  return (
    <div className={`cronometro${hayProrroga ? ' en-prorroga' : ''}`}>
      <div className="cronometro-cabeza">
        <span className="cronometro-fase">{fase.nombre}</span>
        <span className="cronometro-resta num">
          {hayProrroga ? `+${reloj(prorroga)}` : reloj(restante)}
        </span>
      </div>

      <div className="cronometro-barra">
        <div style={{ width: `${avance}%` }} />
      </div>

      <div className="cronometro-pie">
        <span>
          {hayProrroga ? 'Prórroga'
            : fase.congela ? 'Pantallas congeladas' : 'En curso'}
        </span>
        <span className="num">{reloj(total)} en total</span>
      </div>
    </div>
  )
}
