# Documentación

Cuatro documentos vigentes, uno de referencia y una carpeta de historial. Se
leen en este orden.

---

## Los vigentes

### 1 · [`propuesta.md`](propuesta.md) — **el diseño del juego**

Cómo funciona el ejercicio **como juego**: qué ve cada uno de los ocho, qué puede
hacer, y cómo se afectan entre sí. Incluye el modelo del mundo —qué se simula y
hasta dónde—, las 34 acciones y un glosario.

> **Empiece por aquí si no conoce el caso.** No hay que saber programar para
> leerlo.

### 2 · [`COMO_FUNCIONA.md`](COMO_FUNCIONA.md) — **cómo está construido**

Del juego al código. Cada sección tiene la misma forma: qué pasa en la sala, qué
cálculo lo produce, y en qué archivo está.

> Para entender el motor sin leer 4.000 líneas de Python.

### 3 · [`EL_CODIGO.md`](EL_CODIGO.md) — **cómo está organizado el repositorio**

Para quien va a tocar el código: dónde vive cada cosa, cómo añadir una acción o
un punto sin romper nada, qué custodia cada prueba y qué convenciones hay.

> Este sí pide saber programar. El anterior no.

### 4 · [`../PENDIENTES.md`](../PENDIENTES.md) — **qué falta y cómo probarlo**

Separado por lo único que decide qué se puede hacer el lunes: **lo que se hace
sin convocar a nadie**, lo que **necesita personas en una sala**, y las
decisiones del equipo docente. **Es el único sitio donde se lleva la cuenta.**

---

## La referencia transversal

### [`guia_arquitectura_simulaciones.md`](guia_arquitectura_simulaciones.md)

Describe **la forma, no el caso**: cómo montar cualquier ejercicio de simulación
de crisis con participantes humanos y asistencia de IA. Sirve igual para un
sismo, un brote o una falla de infraestructura.

De aquí sale el principio que ordena todo el repositorio:

> **El LLM traduce. El motor decide, valida, ejecuta y reporta.**

Y los ocho modos de falla del canal de órdenes, cada uno medido en un ejercicio
real. Sigue vigente entera.

---

## El historial

No está obsoleto: **está superado**. Se conserva porque explica de dónde salieron
las decisiones actuales, y porque el porqué de un diseño se pierde en cuanto se
borra el documento que lo discutió.

| | Qué es |
|---|---|
| [`historial/propuesta_inicial.md`](historial/propuesta_inicial.md) | El primer documento de diseño, escrito antes que el código. Ahí están los seis motores, los dilemas garantizados y los razonamientos largos —por qué el oxígeno, por qué la saturación exponencial, por qué dos denuncias y no una— que la propuesta actual da por sentados |
| [`historial/como_funciona_motor_v1.md`](historial/como_funciona_motor_v1.md) | Cómo funcionaba el primer motor, con sus números |
| [`historial/mapa_de_palancas.md`](historial/mapa_de_palancas.md) | **El diagnóstico del que salió la versión actual.** Midió que la mezcla real de los puntos no cambiaba nada, que el polo de negociación no podía negociar y que la cohesión era una rampa determinista. Los siete hallazgos y su desenlace están resumidos en `PENDIENTES.md` |

---

*Escuela de Gobierno · Universidad de La Sabana*
