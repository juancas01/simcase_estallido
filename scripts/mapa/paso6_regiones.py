# -*- coding: utf-8 -*-
"""
Paso 6 · las cuatro regiones y el contorno, con las fronteras COMPARTIDAS.

EL PROBLEMA QUE RESUELVE, que no es cosmetico
---------------------------------------------
Trazar cada region por su cuenta y el pais por la suya deja huecos y solapes:
cada poligono se simplifica por separado, asi que la costa de Bellaflor y la
costa del pais quedan a un cuarto de unidad la una de la otra, y entre las dos
aparece una cuchilla de tierra que no pertenece a ninguna region. Medido sobre
el primer intento: 265 muestras de tierra sin region.

Un hueco es un trozo de pais que el mapa pinta sin color y del que la ficha no
sabe decir nada. Un solape es un punto que el mapa situa dos veces.

LA SOLUCION: no se simplifican poligonos, se simplifican FRONTERAS.

  1 · se reparte la rejilla de tierra entre las cuatro semillas (Voronoi)
  2 · se extraen las «grietas»: los segmentos unitarios entre celdas de etiqueta
      distinta --region contra region, o region contra mar--
  3 · la red de grietas se parte en ARCOS entre nudos (donde se juntan tres o
      mas etiquetas), y cada arco separa exactamente un par de etiquetas
  4 · CADA ARCO SE SIMPLIFICA UNA SOLA VEZ
  5 · cada region se arma cosiendo sus arcos, y el pais cosiendo los que dan al
      mar

Como el arco entre Bellaflor y Las Cumbres es literalmente la misma lista de
puntos en las dos, la teselacion es exacta por construccion y no por cuidado.
"""
import json, sys, io, os, math
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
rej = json.load(open(SP + '/rejilla_tierra.json'))
A, L, tierra = rej['ancho'], rej['alto'], rej['tierra']
pr, (ANCHO_UTIL, ALTO_UTIL) = geo.proyector()

SEMILLAS = [
    ('R-ESP', 70.0, 14.0),      # el cabo del norte, con el puerto
    ('R-BEL', 56.0, 42.0),      # la ciudad epicentro, sobre el estrecho
    ('R-VER', 20.0, 68.0),      # la costa del oeste
    ('R-CUM', 66.0, 86.0),      # el sur, la region mas poblada
]
MAR = 0
TOL = 0.22


def celda_a_lienzo(cx, cy):
    lon = geo.W + (cx / (A - 1)) * (geo.E - geo.W)
    lat = geo.N - (cy / (L - 1)) * (geo.N - geo.S)
    return pr(lon, lat)


xs = [celda_a_lienzo(cx, 0)[0] for cx in range(A)]
ys = [celda_a_lienzo(0, cy)[1] for cy in range(L)]

# --- 0 · el agua interior se rellena para repartir, y se dibuja aparte --------
#
# El estuario que parte la ciudad epicentro es un AGUJERO dentro de la tierra, y
# un agujero rompe la teselacion: el contorno del pais lo encierra --su area lo
# incluye-- pero ninguna region lo cubre, asi que cada muestra que cae en el
# agua sale como «tierra sin region». Medido: 326 unidades de area de diferencia
# entre el contorno y la suma de las cuatro regiones.
#
# Se rellena para el REPARTO, de modo que el contorno y las regiones salgan sin
# agujeros y `dentro()` siga siendo una prueba de rayo sobre un poligono simple;
# y se guarda aparte en `aguas`, para dibujarlo encima con el color del mar. El
# estrecho se sigue viendo --es lo que hace de esa ciudad un cuello de botella--
# y la geometria se queda simple.
from collections import deque

comp_mar = [0] * (A * L)
cid_mar = 0
toca_borde = {}
for arranque in range(A * L):
    if tierra[arranque] or comp_mar[arranque]:
        continue
    cid_mar += 1
    borde = False
    cola = deque([arranque])
    comp_mar[arranque] = cid_mar
    celdas = []
    while cola:
        i = cola.popleft()
        celdas.append(i)
        x, y = i % A, i // A
        if x == 0 or y == 0 or x == A - 1 or y == L - 1:
            borde = True
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < A and 0 <= ny < L:
                j = ny * A + nx
                if not tierra[j] and not comp_mar[j]:
                    comp_mar[j] = cid_mar
                    cola.append(j)
    toca_borde[cid_mar] = (borde, celdas)

interiores = [c for c, (borde, _) in toca_borde.items() if not borde]
aguas_celdas = []
for c in interiores:
    celdas = toca_borde[c][1]
    if len(celdas) < 400:          # charcos del rasterizado, no accidentes
        for i in celdas:
            tierra[i] = 1
        continue
    aguas_celdas.append(celdas)
    for i in celdas:
        tierra[i] = 1
print('aguas interiores rellenadas para el reparto:', len(aguas_celdas),
      'de', len(interiores), 'bolsas ·',
      sum(len(c) for c in aguas_celdas), 'celdas')

# --- 1 · repartir -------------------------------------------------------------
etiq = bytearray(A * L)
for cy in range(L):
    y = ys[cy]
    base = cy * A
    for cx in range(A):
        if not tierra[base + cx]:
            continue
        x = xs[cx]
        mejor, cual = 1e18, 0
        for i, (_, sx, sy) in enumerate(SEMILLAS):
            d = (x - sx) ** 2 + (y - sy) ** 2
            if d < mejor:
                mejor, cual = d, i + 1
        etiq[base + cx] = cual

# Cada region tiene que ser UNA pieza: un islote suelto no se puede rotular ni
# ampliar de un clic. Los trozos que no son el cuerpo principal se ceden a la
# region vecina, y como se ceden en la REJILLA la teselacion no se entera.
def componentes(objetivo):
    visto = bytearray(A * L)
    piezas = []
    for arranque in range(A * L):
        if etiq[arranque] != objetivo or visto[arranque]:
            continue
        pila, celdas = [arranque], []
        visto[arranque] = 1
        while pila:
            i = pila.pop()
            celdas.append(i)
            x, y = i % A, i // A
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < A and 0 <= ny < L:
                    j = ny * A + nx
                    if etiq[j] == objetivo and not visto[j]:
                        visto[j] = 1
                        pila.append(j)
        piezas.append(celdas)
    piezas.sort(key=len, reverse=True)
    return piezas


for ronda in range(6):
    movidas = 0
    for idx in range(1, len(SEMILLAS) + 1):
        piezas = componentes(idx)
        for suelta in piezas[1:]:
            vecinas = defaultdict(int)
            for i in suelta:
                x, y = i % A, i // A
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < A and 0 <= ny < L:
                        e = etiq[ny * A + nx]
                        if e and e != idx:
                            vecinas[e] += 1
            if not vecinas:
                continue
            destino = max(vecinas, key=vecinas.get)
            for i in suelta:
                etiq[i] = destino
            movidas += len(suelta)
    if not movidas:
        break
print('piezas sueltas cedidas a la region vecina en', ronda, 'rondas')
for idx, (rid, _, _) in enumerate(SEMILLAS, start=1):
    print('  %s: %d piezas' % (rid, len(componentes(idx))))

# --- 2 · las grietas ----------------------------------------------------------
# Una grieta vive entre dos celdas contiguas de etiqueta distinta. Se identifica
# por el par de puntos de la retícula que la delimitan, en coordenadas de nodo
# (esquinas de celda), donde la celda (cx, cy) ocupa el cuadrado [cx, cx+1].
def lado(i):
    return etiq[i] if 0 <= i < A * L else MAR


aristas = {}        # (p, q) ordenado → frozenset{etiqueta_a, etiqueta_b}
for cy in range(L):
    base = cy * A
    for cx in range(A):
        a = etiq[base + cx]
        # vecino de la derecha
        b = etiq[base + cx + 1] if cx + 1 < A else MAR
        if a != b:
            p, q = (cx + 1, cy), (cx + 1, cy + 1)
            aristas[(p, q)] = frozenset((a, b))
        # vecino de abajo
        c = etiq[base + A + cx] if cy + 1 < L else MAR
        if a != c:
            p, q = (cx, cy + 1), (cx + 1, cy + 1)
            aristas[(p, q)] = frozenset((a, c))
        # los bordes del lienzo, que son costa contra el exterior
        if cx == 0 and a != MAR:
            aristas[((0, cy), (0, cy + 1))] = frozenset((a, MAR))
        if cy == 0 and a != MAR:
            aristas[((cx, 0), (cx + 1, 0))] = frozenset((a, MAR))

print('grietas:', len(aristas))

# --- 3 · partir la red en arcos ----------------------------------------------
inc = defaultdict(list)
for (p, q), par in aristas.items():
    inc[p].append((q, par))
    inc[q].append((p, par))

# Un nudo es donde la red se bifurca o donde cambia el par de etiquetas.
nudos = set()
for punto, vecinos in inc.items():
    pares = {par for _, par in vecinos}
    if len(vecinos) != 2 or len(pares) != 1:
        nudos.add(punto)
print('nudos:', len(nudos))

arcos = []          # {par, puntos}
usada = set()


def clave_arista(p, q):
    return (p, q) if p <= q else (q, p)


for arranque in nudos:
    for vecino, par in inc[arranque]:
        if clave_arista(arranque, vecino) in usada:
            continue
        camino = [arranque, vecino]
        usada.add(clave_arista(arranque, vecino))
        actual, previo = vecino, arranque
        while actual not in nudos:
            siguiente = None
            for v, pr2 in inc[actual]:
                if v != previo and clave_arista(actual, v) not in usada:
                    siguiente = v
                    break
            if siguiente is None:
                break
            usada.add(clave_arista(actual, siguiente))
            camino.append(siguiente)
            previo, actual = actual, siguiente
        arcos.append({'par': par, 'puntos': camino})

# Los ciclos sin ningun nudo --una isla entera rodeada de mar, sin frontera
# interior-- no los alcanza el barrido anterior.
for (p, q), par in aristas.items():
    if clave_arista(p, q) in usada:
        continue
    camino = [p, q]
    usada.add(clave_arista(p, q))
    actual, previo = q, p
    while True:
        siguiente = None
        for v, _ in inc[actual]:
            if v != previo and clave_arista(actual, v) not in usada:
                siguiente = v
                break
        if siguiente is None:
            break
        usada.add(clave_arista(actual, siguiente))
        camino.append(siguiente)
        previo, actual = actual, siguiente
    arcos.append({'par': par, 'puntos': camino})

print('arcos:', len(arcos))

# --- 4 · simplificar CADA ARCO UNA VEZ ---------------------------------------
def nodo_a_lienzo(p):
    cx, cy = p
    lon = geo.W + ((cx - 0.5) / (A - 1)) * (geo.E - geo.W)
    lat = geo.N - ((cy - 0.5) / (L - 1)) * (geo.N - geo.S)
    return pr(lon, lat)


for a in arcos:
    crudo = [nodo_a_lienzo(p) for p in a['puntos']]
    simple = geo.dp(crudo, TOL)
    limpio = [simple[0]]
    for p in simple[1:]:
        if p != limpio[-1]:
            limpio.append(p)
    a['linea'] = limpio
    a['ini'] = a['puntos'][0]
    a['fin'] = a['puntos'][-1]

print('vertices tras simplificar:', sum(len(a['linea']) for a in arcos))


# --- 5 · coser los arcos de cada region --------------------------------------
def armar(etiqueta):
    """Cose en un anillo los arcos que bordean `etiqueta`."""
    mios = [a for a in arcos if etiqueta in a['par']]
    if not mios:
        return None
    porta = defaultdict(list)
    for k, a in enumerate(mios):
        porta[a['ini']].append(k)
        porta[a['fin']].append(k)

    usados = set()
    anillos = []
    for arranque in range(len(mios)):
        if arranque in usados:
            continue
        usados.add(arranque)
        a = mios[arranque]
        anillo = list(a['linea'])
        extremo = a['fin']
        primero = a['ini']
        while extremo != primero:
            siguiente = None
            for k in porta.get(extremo, []):
                if k not in usados:
                    siguiente = k
                    break
            if siguiente is None:
                break
            usados.add(siguiente)
            b = mios[siguiente]
            if b['ini'] == extremo:
                anillo.extend(b['linea'][1:])
                extremo = b['fin']
            else:
                anillo.extend(b['linea'][::-1][1:])
                extremo = b['ini']
        anillos.append(anillo)
    anillos.sort(key=lambda r: abs(geo.area(r)), reverse=True)
    return anillos[0]


poligonos = {}
for idx, (rid, _, _) in enumerate(SEMILLAS, start=1):
    poly = armar(idx)
    poligonos[rid] = poly
    print('  %s: %3d vertices · area %7.1f' % (rid, len(poly), abs(geo.area(poly))))

contorno = armar(MAR)
print('  contorno: %d vertices · area %.1f' % (len(contorno), abs(geo.area(contorno))))

# --- el agua interior, como poligonos para dibujar encima ---------------------
import trazar
aguas = []
for celdas in aguas_celdas:
    mascara = bytearray(A * L)
    for i in celdas:
        mascara[i] = 1
    for anillo in trazar.anillos(mascara, A, L, minimo=16)[:1]:
        puntos = [celda_a_lienzo(*q) for q in anillo]
        simple = geo.dp(puntos, 0.18)
        limpio = [simple[0]]
        for q in simple[1:]:
            if q != limpio[-1]:
                limpio.append(q)
        if len(limpio) >= 8:
            aguas.append(limpio)
aguas.sort(key=lambda a: -abs(geo.area(a)))
print('  aguas interiores:', [len(a) for a in aguas],
      '· areas', [round(abs(geo.area(a)), 1) for a in aguas])

suma = sum(abs(geo.area(p)) for p in poligonos.values())
print('  suma de regiones %.1f · contorno %.1f · diferencia %.1f'
      % (suma, abs(geo.area(contorno)), abs(geo.area(contorno)) - suma))

json.dump({'regiones': poligonos, 'contorno': contorno, 'aguas': aguas},
          open(SP + '/regiones.json', 'w'), separators=(',', ':'))
print('guardado regiones.json (regiones + contorno + aguas)')
