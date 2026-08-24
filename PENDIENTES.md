# Pendientes

Lo que falta para que esto se pueda correr con ocho personas en una sala. **Este
es el único sitio donde se lleva la cuenta**: si algo está pendiente y no está
aquí, es que se me pasó.

Va ordenado por lo que bloquea. Hay tres clases de pendiente y no se resuelven
igual:

| Clase | Quién lo resuelve | Sección |
|---|---|---|
| **Decisiones** — no son técnicas y no son mías | el equipo docente | [A](#a--decisiones-que-no-son-mías) |
| **Código** — está diseñado y no escrito | yo | [B](#b--código-que-falta) |
| **Calibración** — solo se resuelve midiendo | la primera corrida | [C](#c--calibración) |

---

## En una mirada

| | Pendiente | Bloquea | Estado |
|---|---|---|---|
| **A1–A6** | seis decisiones de diseño | A1 y A5 bloquean B4 | esperando |
| **B1** | capa 4 · canal de órdenes en lenguaje natural | la consola del moderador | stub determinista |
| **B2** | capa 3 · seis agentes de entorno | la esfera pública | marcador de posición |
| **B3** | las tres cifras salen cableadas, no del motor de información | el dilema del error doble en la interfaz | cableado |
| **B4** | las ocho fichas de rol, en datos | imprimir los sobres | `data/roles/` vacío |
| **B5** | persistencia de la corrida | el debriefing | no existe |
| **B6** | presupuesto de latencia | depende de B2 | no existe |
| **C1–C4** | cuatro problemas medidos | la primera corrida real | medidos, sin ajustar |

Lo que **sí** funciona está en el README, sección «Estado actual».

---

## Cómo verlos desde el código

Los stubs están marcados en el sitio donde viven:

```bash
grep -rn "PENDIENTE\|TODO" src/
```

Cada marca lleva el identificador de esta lista (`PENDIENTE(B1)`), así que se
puede ir en las dos direcciones: del código a la explicación y de la explicación
al código.

---

## A · Decisiones que no son mías

Son las de §12.1 de la propuesta. Ninguna es técnica; todas cambian el ejercicio.
Van con mi recomendación, pero la decisión es del equipo docente.

| # | Decisión | Mi recomendación | Qué bloquea |
|---|---|---|---|
| **A1** | **¿Nombres reales o ficticios?** Ficcionalizar protege de convertir el ejercicio en un juicio sobre hechos con responsabilidad judicial viva; cuesta el reconocimiento que hace que el caso muerda. | Reales, por coherencia con el Manual, más una declaración expresa en el turno 0 de que el ejercicio no juzga hechos ni personas. | `data/escenario/` y **B4** |
| **A2** | **¿Se puntúa?** Y en particular: ¿las agendas reservadas suman? | Sin marcador. Las agendas se revelan, no se puntúan. | el guion del debriefing |
| **A3** | **¿La Defensoría puede retirarse de verdad**, dejando a la sala sin sus mitigadores? | Que pueda. Un condicionamiento que no se puede cumplir no es una palanca. | una acción en `actions.py` |
| **A4** | **¿`capital_politico` se queda?** Tal como está en §3.6 **no es implementable**: el motor no sabe quién se opone a quién porque la deliberación ocurre en voz alta y no entra al sistema. | Eliminarlo. Con ocho personas en una sala, el capital político lo administra la sala sola. | nada — ya está fuera del código |
| **A5** | **¿El paquete detonante es fijo o se sortea?** Fijo permite comparar salas; sorteado evita que el facilitador que ya lo vio lo anticipe. | Fijo las primeras corridas, sorteado después. | **B4** |
| **A6** | **¿Se acepta el estocástico?** «Hicimos todo bien y salió mal» es una lección real y difícil de recibir. | Decisión del equipo docente, no mía. Mitigado con la banda visible antes de decidir y la corrida reproducible; no resuelto. | el encuadre del turno 0 |

---

## B · Código que falta

### B1 · Capa 4 — el canal de órdenes en lenguaje natural

**Dónde:** [`src/api/main.py:128`](src/api/main.py#L128) · [`src/agents/`](src/agents/) (vacío)

El moderador escribe *«concentrar ESMAD en el anillo hospitalario, con dupla de la
Defensoría, responsable el Ministro de Defensa»* y el sistema debe devolver un
plan tipado —acciones, requisitos que faltan, banda de riesgo— **para que el
moderador lo lea de vuelta a la sala antes de ejecutarlo**. Ese momento no es un
trámite: la sala oye su propia decisión reformulada, con su riesgo, y con
frecuencia la cambia.

Hoy `/api/plan/interpretar` ignora el texto y devuelve una interpretación
determinista de prueba: escoge el nodo cerrado más duro y propone operarlo. Sirve
para probar la interfaz y para nada más.

Lo que falta es el NLU con herramientas tipadas del §7 de la guía de
arquitectura: el modelo **solo traduce** texto a llamadas de herramienta; no
decide, no valida y no toca el estado. La resolución de entidades es el punto
delicado —acertar mal en silencio aquí no manda ayuda al barrio equivocado sino
**ESMAD al nodo equivocado**—, así que necesita devolver la entidad resuelta en
el eco al moderador, con su nombre completo.

### B2 · Capa 3 — los seis agentes de entorno

**Dónde:** [`src/api/main.py:96`](src/api/main.py#L96) · lo consume [`web_ui/src/components/EsferaPublica.jsx`](web_ui/src/components/EsferaPublica.jsx)

Comité del Paro, prensa nacional, redes, gremios, comunidad internacional y
alcaldes. Producen **contenido y solo contenido**: publicaciones, comunicados y
reacciones que la sala lee. No mutan el estado — el motor ya calculó lo que pasó
y ellos lo narran desde su sesgo.

Hoy `_publicaciones_recientes()` recorre el historial y emite dos frases fijas
cuando encuentra un incidente mortal o una reapertura. La esfera pública se llena,
pero con plantilla.

### B3 · Las tres cifras salen cableadas

**Dónde:** [`src/api/main.py:79`](src/api/main.py#L79)

`/api/esfera` devuelve hoy `oficial = verificada − 3` y `municipal = verificada + 2`.
Los números divergen, que es el efecto que se busca, pero **divergen por
aritmética y no por el motor de información**.

Debe salir de `information.estimar_nodo()`, que ya existe, ya tiene los cuatro
sesgos calibrados y ya produce la dispersión real. Es poco trabajo y es
importante: es la diferencia entre una interfaz que ilustra el error doble y una
que lo produce.

### B4 · Las ocho fichas de rol, en datos

**Dónde:** [`data/roles/`](data/roles/) (vacío)

Las fichas del Manual de Roles y sus RADs viven hoy fuera del repositorio. Deben
entrar como datos, no como código, por la misma razón que el escenario: lo que se
duplique entre los datos y el prompt de un modelo se desincroniza. Siempre.

Depende de **A1** (nombres) y **A5** (paquete detonante fijo o sorteado).

### B5 · Persistencia de la corrida

**Dónde:** no existe

El motor guarda `historial` en memoria y la semilla en `MotorCrisis`. Al cerrar
el proceso se pierde todo — y el debriefing dura veinte minutos, más que
cualquier turno.

Hace falta escribir a disco la semilla, el estado inicial, el log de acciones y
los resultados por turno. Con eso la corrida se repite **con una decisión
cambiada**, que es la mejor herramienta de debriefing que da este diseño y ahora
mismo no se puede usar.

### B6 · Presupuesto de latencia

**Dónde:** depende de B2

Seis agentes, cinco turnos y cuatro interludios dan entre 40 y 50 invocaciones de
modelo. La fase de consecuencias dura sesenta segundos con ocho personas mirando
la pantalla.

Ejecución en paralelo con presupuesto de tiempo duro, degradando a contenido de
plantilla si el proveedor tarda. **No se puede calcular hasta que B2 exista**,
pero el diseño tiene que preverlo desde el principio.

---

## C · Calibración

**Ningún coeficiente está medido.** Son convenciones declaradas, elegidas para
que ninguna estrategia pura gane. El criterio es **por comportamiento, no por
realismo**: no hay respuesta empírica a cuánta legitimidad cuesta un muerto, y no
la va a haber.

La herramienta es `uv run python scripts/correr_ejercicio.py --comparar`.
Medición del 2026-08-24:

```
  estrategia      netas  reap  muertes  legit  cohes  credib
  solo_fuerza         3     3      147     25      0      21
  solo_mesa           6     0      147     52     41      45
  constituida         1     2      147     44     23      21
  humanitaria         3     0       70     37      0      45
  pasiva              1     0      147     25      0      45
```

Lee bien en lo esencial —ninguna estrategia domina: `solo_mesa` conserva las
reservas y no salva a nadie, `humanitaria` salva la mitad y lo paga en
legitimidad y cohesión— y mal en cuatro cosas concretas:

| # | Problema | Por qué importa |
|---|---|---|
| **C1** | **La cohesión se hunde a 0 en tres de las cinco.** Satura, y una variable saturada deja de discriminar: a partir de ahí toda decisión da igual. | Es una de las tres lecturas del debriefing. Si siempre termina en 0, no se lee nada. |
| **C2** | **Las muertes son 147 en cuatro de las cinco.** Solo `humanitaria` se despega, con 70. El reloj de oxígeno responde a abrir corredores humanitarios explícitamente y a casi nada más. | El reloj debe ser un dilema, no un guion. Es la misma clase de fallo que el de Buenaventura, más suave. |
| **C3** | **`constituida` rinde por debajo de lo que debería.** Una sala que se constituye bien —reglas escritas, protocolo de vocería, criterio de priorización— saca 1 corredor neto y 2 reaperturas. | Si constituirse no paga, el segundo hallazgo del caso se convierte en una moraleja sin respaldo aritmético. |
| **C4** | **Con cinco turnos, la fuerza casi nunca abre un corredor.** Lo que se abre de noche se cierra, el corredor se mide por su punto peor y el mínimo vuelve a cero. | **No lo diseñé: salió de la aritmética.** Refuerza la tesis del caso, pero conviene decidirlo a propósito y no heredarlo por accidente. |

Y tres cosas que solo se ven con personas dentro:

- **¿24 nodos son demasiados para 5 decisiones?** Si la sala toca menos de diez,
  bajar a 16.
- **¿Da tiempo a que la mesa se rompa?** Con cinco decisiones puede no aparecer.
  Si la cohesión termina por encima de 55 casi siempre, subir la sensibilidad —o
  aceptar que un ejercicio de dos horas mide la constitución de la mesa y no su
  desgaste, que también es un objeto legítimo.
- **¿Se cumplen los 13 minutos por turno?** Si no, el problema es de moderación y
  se corrige con guion, no con diseño.

**La primera corrida con personas es una medición, no un ejercicio**, y conviene
decirlo antes de empezar.

---

## D · Fuera del código

- **El guion de moderación.** Sin pantallas individuales, el ritmo entero depende
  de una persona: el moderador es el punto único de fallo. Requiere ensayo
  completo y un guion propio, no solo el manual de roles.
- **La declaración del turno 0** sobre el alcance del ejercicio, decida lo que se
  decida sobre A1.
- **El protocolo de los sobres.** La confidencialidad en papel depende de que
  nadie pase la hoja. Con ocho personas y un facilitador es sostenible; no
  escalaría a treinta.

---

## Lo que ya NO está pendiente

La propuesta §12.2 los lista como pendientes porque se escribió antes que el
código. **Están resueltos** — anotado aquí para que nadie los vuelva a levantar:

| | Era | Cómo quedó |
|---|---|---|
| **T1** | `intensidad_movilizacion` satura en 100 y deja de discriminar | Rendimientos decrecientes (`DECAIMIENTO_REPETICION = 0.6`) y decaimiento proporcional al nivel (`0.04`), en [`mobilization.py:37`](src/engine/mobilization.py#L37) y [`:82`](src/engine/mobilization.py#L82) |
| **T2** | `control_voceria` no está en la capa de estimación, así que Interior lo ve perfecto y el dilema desaparece | Entró con sesgo por fuente en [`information.py:67`](src/engine/information.py#L67): Interior lo sobreestima (+0,20), Cali lo estima bien en su jurisdicción (+0,03) |
| **T3** | `dureza` la escriben dos mecanismos sin precedencia declarada | Tres, y con orden fijo en `paso()`: turno sin decisión (+0,03) → reapertura (+0,08) → `g(intensidad)`. Determinista y reproducible |
| **—** | Toda región sin corredor humanitario acumula muertes evitables haga lo que haga la sala | Invariante con fallo ruidoso en [`loader.py`](src/engine/loader.py) y prueba automática |
| **—** | `P(incidente)` alcanzaba 1,0 exacto y volvía la tirada irrelevante | Techo en `P_INCIDENTE_MAX = 0.98`. Una operación puede ser un disparate y aun así no terminar mal, que es precisamente por lo que se repiten los disparates |

---

*Última revisión: 2026-08-24 · 18 pruebas en verde.*
