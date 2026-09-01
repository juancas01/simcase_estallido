# CONTEXTO — el mapa del repositorio

**Este es el punto de entrada.** Los documentos largos se retiraron para que
leer el repositorio no cueste milhares de líneas: su conocimiento vive en los
comentarios del código —que en este repositorio explican el porqué, no el
qué—, en [`PENDIENTES.md`](PENDIENTES.md) y en este archivo. Si una pregunta
no se responde aquí, la tabla de abajo dice exactamente qué archivo abrirla.

Cualquier documento retirado se recupera con
`git show HEAD:docs/LAS_ACCIONES.md` (la lista completa está al final).

---

## El caso en cuatro frases

Simulación de conducción de crisis sobre un estallido social ficticio
(territorio de **Bellaflor**, inspirado en el Paro Nacional de 2021). Nueve
personas alrededor de una mesa —siete roles con cartera— durante dos horas:
turno 0 de declaración, **cinco jornadas** de 15 minutos (13 de día en que se
ordena, 2 de noche en que se leen las consecuencias) y un debriefing. El motor
calcula las consecuencias de lo que la sala decide y **la movilización
reacciona**: cada operación, cifra desmentida o sesión de mesa modifica la
intensidad de lo que se intenta contener. El principio que ordena todo:
**el LLM traduce; el motor decide, valida, ejecuta y reporta.**

---

## La pregunta → dónde mirar

| Si la pregunta es sobre… | Abrir |
|---|---|
| qué falta, en qué está algo, decisiones abiertas (B·P·C·A) | [`PENDIENTES.md`](PENDIENTES.md) — el único sitio donde se lleva la cuenta |
| montar y correr, comandos, «estado actual» | [`README.md`](README.md) |
| **una acción**: qué hace, qué valida, qué cobra, sus tiempos | `src/engine/actions.py` (comentario de su clase) + `src/engine/parameters.py` (`COSTO_RESERVAS`, `GRAVEDAD`) |
| una regla del motor: riesgo, mesas, reloj, movilización, información | el docstring del módulo correspondiente — mapa abajo |
| qué ve la sala en el tablero, el mapa, los globos, las pestañas de rol | `src/engine/views.py` · `web_ui/src/definiciones.jsx` |
| cómo se entiende una orden dictada en lenguaje natural | `src/agents/nlu.py` · `src/agents/herramientas.py` · `src/agents/config.py` |
| la API de la consola y las pantallas | `src/api/main.py` · `web_ui/src/` |
| calibración, estrategias, semillas, la tabla de `--comparar` | `PENDIENTES.md` (C5) · `scripts/correr_ejercicio.py --comparar` |
| el debriefing futuro y la «lectura de la corrida» (B14) | `docs/LA_MEDICION.md` — propuesta sin implementar |
| el diseño original del juego, el historial de decisiones | git history — ver la tabla final |

---

## El mapa del código

| Módulo | Qué gobierna |
|---|---|
| `src/engine/simulation.py` | el motor: ciclo de turnos, colas, el contrato de doble validación de `encolar`, umbrales duros, métricas del debriefing |
| `src/engine/state.py` | el estado entero: `Estado`, `Nodo`, `Corredor`, `Composicion`, `Reservas`, `Banderas`, `Acuerdo`, `Decision` |
| `src/engine/parameters.py` | **todos los números**. Regla del archivo: si un número gobierna comportamiento, vive aquí y en ningún otro sitio (hay prueba que lo exige) |
| `src/engine/actions.py` | las **37 acciones** por rol (`CATALOGO`), `ventana_escoltada`, y `GUIA` — de ahí se regenera la guía impresa |
| `src/engine/force.py` | riesgo de incidente y los cuatro mitigadores, la operación, la escolta, fatiga y custodia |
| `src/engine/aperture.py` | las **tres vías de abrir** (fuerza · concertación · desgaste), las mesas y sus sesiones, los acuerdos y su vencimiento |
| `src/engine/supply.py` | el reloj: combustible → plantas → oxígeno → alimentos; las muertes evitables |
| `src/engine/mobilization.py` | el adversario reflexivo: intensidad, eventos, cierres nuevos, apoyo local |
| `src/engine/information.py` | estimaciones sesgadas, los tres equipos por día, denuncias y su verificación, la cifra oficial |
| `src/engine/territory.py` | lectura pública del territorio (la que no deja deducir la mezcla real) |
| `src/engine/views.py` | la vista pública (el tablero) y los datos por rol que consume la sección «Carteras» de la web UI · el cuadro `CONSTITUTIVAS` |
| `src/engine/loader.py` | carga y valida `data/escenario/estado_inicial.json` — el escenario se edita ahí, el motor identifica por código y no por nombre |
| `src/agents/` | las dos capas de lenguaje (con llave usan el modelo; sin llave degradan a plantilla y el ejercicio corre igual) |
| `src/api/main.py` | FastAPI: consola, `/encolar`, cerrar jornada, tablero y carteras |
| `scripts/correr_ejercicio.py` | correr el motor solo: `--detalle`, `--vistas`, `--comparar`, `--semilla` |
| `scripts/repertorio.py` | **regenera la guía de acciones** que se imprime para la sala |
| `tests/` | `test_invariantes.py` (el motor) · `test_canal_ordenes.py` (el canal) — cada prueba explica la regla que clava |

---

## Claves del motor — lo que más se pregunta

- **El ciclo**: turno 0 (declaración de línea) → jornadas 1–5 → proyección de
  3 turnos sin nadie al mando. Las órdenes se encolan durante el día y
  **todas se ejecutan al cerrar la jornada**; la noche corre inmediatamente
  después.
- **La cola es FIFO y no se reordena**: el orden del dictado es el orden de
  ejecución. Y la validación ocurre dos veces — al encolar contra la ventana
  anterior, y al ejecutar contra el plan a mitad. Lo que un mismo plan puede
  habilitar se avisa al validar y se exige al ejecutar (el contrato completo,
  en `MotorCrisis.encolar`).
- **Tres vías de abrir**, con sus tiempos: fuerza — 1 jornada y puede
  reabrir esa misma noche; concertación — 2 sesiones, y la mesa hay que
  instalarla cada jornada o se congela; desgaste — apoyo bajo sostenido,
  ~2 jornadas, y es la única gratis.
- **La escolta vale para el plan que la pide, Y PARA SU CORREDOR**: la asigna
  `Escoltar` al ejecutar —con el corredor apuntado— y la libera `paso_fatiga` al
  cerrar cada paso. La caravana y el acopio van después de ella, en la misma
  frase y sobre el mismo corredor.
- **Todo costo es un peldaño**: `GRAVEDAD` (minimo 2 · leve 3 · moderado 5 ·
  serio 8 · alto 10 · grave 12 · maximo 22). Ninguna acción escribe cifras.
- **Cuatro reservas** con umbrales duros: legitimidad (gremios 40/25),
  credibilidad de la mesa (Comité 30/15), respaldo internacional (30),
  cohesión (35). La cohesión solo se cobra en turnos de decisión.
- **Una orden no se dicta dos veces en la misma jornada.** Lo que la hace la
  misma es `Accion.llave()`: el acto, más su objetivo cuando el acto tiene uno.
  Dos puntos distintos son dos órdenes; la misma mesa nacional seis veces, una.
- **La calle se satura de lo que se repita, en las DOS direcciones.** Los
  rendimientos decrecientes se aplican a los eventos que bajan la intensidad
  igual que a los que la suben. Solo decaían los que la suben, y por ahí una
  acción repetida ganaba el ejercicio.
- **La autonomía tiene techo y suelo.** No se puede acumular más reserva de la
  que la región tenía antes del paro (`Region.techo_autonomia`), y toda región
  tiene al menos un corredor de cada clase — el `loader` lo exige, porque un
  contador que solo puede bajar es un guion que castiga, no un dilema.
- **Con la semilla**: `netas`, `reap` y las reservas bailan. `cohes` y `muert`
  **deberían** no moverse y hoy sí se mueven — es el criterio C5 y está roto;
  ver `PENDIENTES.md`.
- **Las 37 acciones**: 10 constitutivas (encienden bandera), 19 operativas
  (mueven el mundo), 8 informativas (cambian lo que se sabe). Policía es el
  único rol sin acción informativa. Las dos constitutivas de Policía son
  decisiones distintas desde la separación de `parte_clasificado` y
  `protocolo_verificacion`.
- **Las muertes evitables** salen del reloj de autonomía, que tiene tres
  entradas: corredores que pasan, prioridad del combustible, y el pánico que
  sube al entregar el calendario de agotamiento.
- **Las denuncias no esperan**: dos turnos sin verificar y estallan; siempre
  hay al menos dos, con veracidad distinta y sin señal que las distinga.
- **Un turno sin órdenes es una jugada**, con costo propio en legitimidad,
  endurecimiento y encuadre de abandono.

---

## Los documentos que se retiraron, y dónde quedó cada cosa

| Documento | Dónde vive ahora |
|---|---|
| `docs/propuesta.md` · `docs/historial/propuesta_inicial.md` | el diseño del juego y sus razonamientos largos — git history |
| `docs/COMO_FUNCIONA.md` | la explicación juego→motor está en los docstrings de `src/engine`; su §12 (la tabla de calibración) vive en `PENDIENTES.md` C5 |
| `docs/LAS_ACCIONES.md` | las 37 acciones con números: comentarios de cada clase en `actions.py` + `parameters.py` |
| `docs/GUIA_DE_ACCIONES.md` | **se regenera**: `uv run python scripts/repertorio.py` — es la hoja que se imprime para la sala |
| `docs/EL_CODIGO.md` | reemplazado por este archivo |
| `docs/guia_arquitectura_simulaciones.md` | cómo montar otro caso con esta arquitectura — git history |
| `docs/LA_SIMPLIFICACION.md` | los once cambios S1–S11, **ya aplicados**; el porqué de cada uno quedó escrito junto al cambio, en el código |
| `docs/historial/resueltos.md` · `mapa_de_palancas.md` · `como_funciona_motor_v1.md` | la historia de cómo se llegó aquí — git history |
| `scripts/mapa/README.md` | cómo se generó la geografía real de corredores — git history |

**Se quedan**: `PENDIENTES.md` (la cuenta de lo que falta), `README.md`
(arranque y estado actual), `docs/LA_MEDICION.md` (propuesta B14, sin
implementar) y este archivo.
