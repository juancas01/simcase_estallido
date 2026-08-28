# Cómo se construye el mapa

El bloque `mapa` de [`data/escenario/estado_inicial.json`](../../data/escenario/estado_inicial.json)
—el contorno del país, sus cuatro regiones, la red vial, los trazados de los
corredores y la posición de los diez puntos de cierre— **no está escrito a
mano.** Se genera con los nueve pasos de esta carpeta.

> **Por qué vive en el repositorio.** El bloque `mapa` se perdió una vez y no se
> pudo recuperar de ninguna parte: no estaba en git y no se podía rehacer. Un
> artefacto generado cuyo generador no existe es un artefacto que se pierde
> entero la primera vez que alguien se equivoca de comando.

---

## Lo que entra y lo que sale

**Entra:** datos cartográficos abiertos de una costa real —su línea de costa,
sus carreteras principales y sus asentamientos.

**Sale:** un país inventado, con sus nombres, sus cuatro regiones y sus diez
bloqueos, sobre geometría de verdad.

> **Qué sitio real es no se registra en ninguna parte, y es deliberado.** El
> territorio del ejercicio es ficticio; saber a qué se parece el dibujo no
> aporta nada al material y solo invita a buscarle correspondencias que no
> existen. Es el mismo trato que Macondo tuvo con Mocoa: **lo prestado es el
> trazo, no el lugar.** El recuadro vive en `geo.py`, en un solo sitio, para que
> los nueve pasos hablen del mismo.

---

## Los nueve pasos

| | Paso | Qué hace |
|---|---|---|
| **1** | `paso1_descargar.py` | **El único que sale a la red.** Línea de costa y red vial del recuadro |
| **2** | `paso2_tierra.py` | De los trozos sueltos de costa a una máscara de tierra |
| **4** | `paso4_vias.py` | Proyectar, recortar al lienzo, **empalmar** y simplificar la red vial |
| **5** | `paso5_lugares.py` | Los asentamientos reales, para no poner el puerto donde no hay nada |
| **6** | `paso6_regiones.py` | Las cuatro regiones y el contorno, con **fronteras compartidas** |
| **7** | `paso7_red.py` | Rutear los cuatro corredores y sembrar los diez puntos encima |
| **8** | `paso8_mapa.py` | Rótulos, mares, sitios y el bloque `mapa` completo |
| **9** | `paso9_escenario.py` | Escribir el escenario, conservando los atributos de juego |
| — | `vista_previa.py` | Un PNG sin dependencias, para mirarlo con los ojos |

No hay paso 3: era una primera versión del trazado del contorno que el paso 6
absorbió al pasar a fronteras compartidas. Se deja el hueco en la numeración en
vez de renumerar, porque los números salen citados en los comentarios.

```bash
cd scripts/mapa
uv run python paso1_descargar.py     # una sola vez · ~13 MB · tarda
uv run python paso2_tierra.py
uv run python paso4_vias.py
uv run python paso5_lugares.py
uv run python paso6_regiones.py
uv run python paso7_red.py
uv run python paso8_mapa.py
uv run python paso9_escenario.py
uv run python vista_previa.py        # trabajo/mapa.png
```

Los intermedios van a `trabajo/`, que está en `.gitignore`.

---

## Las cuatro cosas que costaron una pasada cada una

Están explicadas en la cabecera de su paso; aquí solo el resumen, porque son las
que hay que tener delante si alguien mueve el recuadro.

**1 · Coser la costa por sus extremos no funciona.** Overpass devuelve las vías
que *tocan* el recuadro, así que la línea de costa llega partida en cuarenta y
un pedazos que no casan. Se rasteriza y se traza con marching squares.

**2 · Sembrar el mar «por donde se sabe que hay mar» tampoco.** Dentro de un
recuadro los dos mares pueden no comunicarse. Se usa la convención de los
propios datos —la tierra queda a la izquierda del sentido de avance— y **cada
componente se decide por mayoría** de las semillas que caen en ella: una semilla
suelta del lado equivocado contaminaba antes la componente entera.

**3 · Filtrar las vías por longitud antes de empalmarlas se come la red.** Una
autopista no viene como una línea: viene como cincuenta *ways* de trescientos
metros. Medido: 5.421 trozos quedaban en 439. Primero se cosen, después se mide.

**4 · Simplificar cada polígono por su cuenta rompe la teselación.** La costa de
una región y la costa del país quedan a un cuarto de unidad la una de la otra, y
entre las dos aparece una cuchilla de tierra que no es de nadie. Medido: 265
muestras huérfanas. Se simplifican **las fronteras**, una vez cada una, y cada
región se cose con las suyas — así el arco entre dos regiones es literalmente la
misma lista de puntos en las dos.

Y una quinta que no es del proceso sino del resultado: **el agua interior se
rellena para repartir y se dibuja aparte.** Un estuario es un agujero dentro de
la tierra, y un agujero deja trozos que ninguna región cubre. Se rellena para
que `dentro()` siga siendo una prueba de rayo sobre un polígono simple, y se
pinta encima con el color del mar.

---

## Si se mueve el recuadro

Cambiar `S, W, N, E` en `geo.py` y volver a correr los nueve pasos **no basta**:
las semillas de región (`paso6`), los extremos de cada corredor y las fracciones
donde se siembran los puntos (`paso7`), y las anclas de la infraestructura
(`paso9`) están en coordenadas del lienzo y hay que volver a elegirlas.

Las tres comprobaciones que dicen si quedó bien, y las tres las hace la suite:

- cada punto y cada instalación caen **dentro del polígono de su región**
- las cuatro regiones **teselan el país** sin huecos ni solapes
- **nada cae en el agua**, ni en el mar ni en el estuario de dentro

```bash
uv run pytest tests/test_invariantes.py -k "region or mapa or mar or agua"
```
