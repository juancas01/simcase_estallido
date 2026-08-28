# -*- coding: utf-8 -*-
"""
Paso 2 · de los trozos sueltos de costa a UNA silueta de tierra.

TRES INTENTOS, Y POR QUE LOS DOS PRIMEROS NO SIRVEN
---------------------------------------------------
1 · Coser los tramos por sus extremos. No sirve: Overpass devuelve las vias que
    TOCAN el recuadro, asi que la costa llega partida en cuarenta y un pedazos
    que no casan entre si.
2 · Inundar el mar desde «un punto que se sabe que es mar». Tampoco: dentro de
    este recuadro los dos mares NO se comunican —habria que rodear el cabo del
    norte, que queda fuera— y quedaba el 91 % en tierra.
3 · Sembrar cada segmento por su izquierda (la convencion de OSM es que la
    tierra queda a la izquierda del sentido de avance) e inundar. Casi: con
    132.554 segmentos, unas cuantas semillas caen del lado equivocado en los
    canales estrechos, **y una sola semilla mala contamina la componente
    entera.** Quedaba el 2 %.

LO QUE SI FUNCIONA: separar las dos cosas.

    a · la barrera de costa parte el recuadro en componentes conexas — 255
    b · cada componente se decide POR MAYORIA de las semillas que caen en ella

Una semilla suelta del lado equivocado ya no decide nada: la mayoria de las
5.000 que caen en el Mar del Norte dicen mar, y las tres que se colaron pierden.
Ese es todo el arreglo.
"""
import json, sys, io, os, math
from collections import deque, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
S, W, N, E = geo.S, geo.W, geo.N, geo.E
ANCHO, ALTO = 900, 1000
SEPARACION = 4.0

costa = json.load(open(SP + '/p2_costa.json', encoding='utf-8'))


def celda(lon, lat):
    return ((lon - W) / (E - W) * (ANCHO - 1),
            (N - lat) / (N - S) * (ALTO - 1))          # y hacia abajo


barrera = bytearray(ANCHO * ALTO)


def pintar(x0, y0, x1, y1):
    """Bresenham. La barrera queda 8-conexa y el agua se inunda a 4."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < ANCHO and 0 <= y0 < ALTO:
            barrera[y0 * ANCHO + x0] = 1
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x0 += sx
        if e2 < dx:
            err += dx; y0 += sy


segmentos = []
for e in costa['elements']:
    g = e.get('geometry') or []
    for a, b in zip(g, g[1:]):
        p, q = celda(a['lon'], a['lat']), celda(b['lon'], b['lat'])
        pintar(*p, *q)
        segmentos.append((p, q))
print('segmentos de costa:', len(segmentos), '· celdas de barrera:', sum(barrera))

# --- a · las componentes que deja la barrera --------------------------------
etiqueta = [0] * (ANCHO * ALTO)
tam = {}
n_comp = 0
for arranque in range(ANCHO * ALTO):
    if barrera[arranque] or etiqueta[arranque]:
        continue
    n_comp += 1
    cuantas = 0
    cola = deque([arranque])
    etiqueta[arranque] = n_comp
    while cola:
        i = cola.popleft()
        cuantas += 1
        x, y = i % ANCHO, i // ANCHO
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < ANCHO and 0 <= ny < ALTO:
                j = ny * ANCHO + nx
                if not etiqueta[j] and not barrera[j]:
                    etiqueta[j] = n_comp
                    cola.append(j)
    tam[n_comp] = cuantas
print('componentes:', n_comp)

# --- b · cada componente vota ------------------------------------------------
# La normal que apunta a tierra es (dy, -dx). En la rejilla la `y` va hacia
# abajo, asi que el marco es zurdo y la izquierda de OSM se invierte respecto de
# la formula de libro. El signo NO se razono: se comprobo. Con el contrario, la
# componente grande de la peninsula votaba «mar» por 36.711 a 8.999.
votos = defaultdict(lambda: [0, 0])         # id → [tierra, mar]
for (ax, ay), (bx, by) in segmentos:
    dx, dy = bx - ax, by - ay
    norma = math.hypot(dx, dy)
    if norma < 1e-9:
        continue
    nx, ny = dy / norma, -dx / norma
    mx, my = (ax + bx) / 2, (ay + by) / 2
    for casilla, signo in ((0, 1), (1, -1)):
        cx = int(round(mx + signo * nx * SEPARACION))
        cy = int(round(my + signo * ny * SEPARACION))
        if 0 <= cx < ANCHO and 0 <= cy < ALTO:
            e = etiqueta[cy * ANCHO + cx]
            if e:
                votos[e][casilla] += 1

es_tierra = {}
for cid, cuantas in tam.items():
    t, m = votos.get(cid, (0, 0))
    # Sin un solo voto no hay con que decidir. Una bolsa sin costa alrededor es
    # un hueco interior de la tierra —un lago, un patio entre carreteras— y
    # pintarla de mar abriria agujeros de agua en mitad del pais.
    es_tierra[cid] = (t >= m) if (t or m) else True

superficie = sum(tam[c] for c in tam if es_tierra[c])
print('tierra:', superficie, f'({100*superficie/(ANCHO*ALTO):.1f} %)')
mayores = sorted(tam.items(), key=lambda kv: -kv[1])[:6]
for cid, cuantas in mayores:
    t, m = votos.get(cid, (0, 0))
    print(f'  comp {cid:>4}: {100*cuantas/(ANCHO*ALTO):5.1f} % · votos tierra {t:>6} '
          f'mar {m:>6} → {"TIERRA" if es_tierra[cid] else "mar"}')

tierra = bytearray(
    1 if (barrera[i] or es_tierra[etiqueta[i]]) else 0
    for i in range(ANCHO * ALTO))

json.dump({'ancho': ANCHO, 'alto': ALTO, 'tierra': list(tierra)},
          open(SP + '/rejilla_tierra.json', 'w'), separators=(',', ':'))
print('guardado rejilla_tierra.json ·', f'{100*sum(tierra)/(ANCHO*ALTO):.1f} % tierra')
