# -*- coding: utf-8 -*-
"""
Paso 8 · el bloque `mapa` completo, listo para el escenario.

Junta lo que produjeron los pasos anteriores y calcula lo que falta:

  · contorno .... la silueta de tierra
  · tramos ...... el contorno partido en LITORAL y FRONTERA. Por uno entra el
                  combustible del pais y por el otro no entra nada que el
                  ejercicio modele, asi que se dibujan distinto.
  · rotulos ..... donde cabe el nombre de cada region, sin salirse de ella
  · mares ....... donde cabe el nombre de cada mar, sin pisar tierra
  · sitios ...... el puerto y la ciudad epicentro, sobre asentamientos reales
  · vias ........ la red vial, casi transparente
  · regiones .... los cuatro poligonos

Los rotulos NO se ponen en el centroide. El centroide de una region con forma de
C cae fuera de la region, y el nombre acaba escrito en el mar. Se usa el punto
mas interior --el centro del circulo mas grande que cabe dentro-- calculado con
una transformada de distancia sobre la rejilla.
"""
import json, sys, io, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo, trazar

SP = geo.SP
pr, (ANCHO_UTIL, ALTO_UTIL) = geo.proyector()

rej = json.load(open(SP + '/rejilla_tierra.json'))
A, L, tierra = rej['ancho'], rej['alto'], rej['tierra']
# El contorno YA NO se traza aparte: sale del mismo tejido de arcos que las
# regiones (paso 6). Trazarlo por su cuenta era lo que dejaba huecos entre la
# costa del pais y la costa de cada region.
_reg = json.load(open(SP + '/regiones.json'))
regiones = {k: [tuple(p) for p in v] for k, v in _reg['regiones'].items()}
CONTORNO = [tuple(p) for p in _reg['contorno']]
AGUAS = [[tuple(p) for p in a] for a in _reg['aguas']]
vias = json.load(open(SP + '/vias.json'))
red = json.load(open(SP + '/red.json'))
lugares = json.load(open(SP + '/lugares.json'))


def celda_a_lienzo(cx, cy):
    lon = geo.W + (cx / (A - 1)) * (geo.E - geo.W)
    lat = geo.N - (cy / (L - 1)) * (geo.N - geo.S)
    return pr(lon, lat)


# --- el punto mas interior de una mascara ------------------------------------
def mas_interior(mascara):
    """Transformada de distancia de chamfer en dos pasadas, y su maximo.

    EL BORDE DE LA REJILLA CUENTA COMO FONDO. Sin eso el maximo se va siempre a
    una esquina --el rotulo de Las Cumbres salia en (50, 99.8), pegado al canto
    del lienzo, y el del mar en (0, 0)-- porque una celda del borde no tiene
    vecino de fuera que le ponga limite.
    """
    INF = 10 ** 9
    d = [0 if not mascara[i] else INF for i in range(A * L)]
    for y in range(L):
        base = y * A
        for x in range(A):
            i = base + x
            if d[i] == 0:
                continue
            mejor = d[i]
            if x == 0 or y == 0:
                mejor = min(mejor, 5)
            if x > 0:
                mejor = min(mejor, d[i - 1] + 5)
            if y > 0:
                mejor = min(mejor, d[i - A] + 5)
                if x > 0:
                    mejor = min(mejor, d[i - A - 1] + 7)
                if x < A - 1:
                    mejor = min(mejor, d[i - A + 1] + 7)
            d[i] = mejor
    for y in range(L - 1, -1, -1):
        base = y * A
        for x in range(A - 1, -1, -1):
            i = base + x
            if d[i] == 0:
                continue
            mejor = d[i]
            if x == A - 1 or y == L - 1:
                mejor = min(mejor, 5)
            if x < A - 1:
                mejor = min(mejor, d[i + 1] + 5)
            if y < L - 1:
                mejor = min(mejor, d[i + A] + 5)
                if x < A - 1:
                    mejor = min(mejor, d[i + A + 1] + 7)
                if x > 0:
                    mejor = min(mejor, d[i + A - 1] + 7)
            d[i] = mejor
    mejor_i = max(range(A * L), key=lambda i: d[i])
    return celda_a_lienzo(mejor_i % A, mejor_i // A), d[mejor_i] / 5.0


# --- contorno y tramos -------------------------------------------------------
contorno = CONTORNO
BORDE = 0.45


def en_el_borde(p):
    return (p[0] <= BORDE or p[0] >= ANCHO_UTIL - BORDE
            or p[1] <= BORDE or p[1] >= ALTO_UTIL - BORDE)


tramos, actual, clase_actual = [], [], None
for p in contorno + [contorno[0]]:
    c = 'frontera' if en_el_borde(p) else 'litoral'
    if clase_actual is None:
        clase_actual, actual = c, [p]
    elif c == clase_actual:
        actual.append(p)
    else:
        actual.append(p)
        if len(actual) >= 2:
            tramos.append({'frontera': clase_actual == 'frontera', 'puntos': actual})
        clase_actual, actual = c, [p]
if len(actual) >= 2:
    tramos.append({'frontera': clase_actual == 'frontera', 'puntos': actual})

# Los trocitos de dos o tres vertices son ruido del recorte: alternan litoral y
# frontera en la misma esquina y se dibujan como puntadas sueltas.
tramos = [t for t in tramos if geo.largo(t['puntos']) > 1.2]
print('contorno:', len(contorno), 'vertices · tramos:', len(tramos),
      '(frontera %d, litoral %d)' % (sum(1 for t in tramos if t['frontera']),
                                     sum(1 for t in tramos if not t['frontera'])))

# --- rotulos de region -------------------------------------------------------
rotulos = {}
for rid, poly in regiones.items():
    mascara = bytearray(A * L)
    for cy in range(0, L):
        base = cy * A
        for cx in range(0, A):
            if not tierra[base + cx]:
                continue
            x, y = celda_a_lienzo(cx, cy)
            if geo.dentro(x, y, poly):
                mascara[base + cx] = 1
    (px, py), radio = mas_interior(mascara)
    rotulos[rid] = {'x': px, 'y': py}
    print('  rotulo %s en (%5.2f,%5.2f) · radio %.0f celdas · dentro: %s'
          % (rid, px, py, radio, geo.dentro(px, py, poly)))

# --- rotulos de mar ----------------------------------------------------------
mar = bytearray(1 if not tierra[i] else 0 for i in range(A * L))
comp, cid = [0] * (A * L), 0
tam = {}
for arranque in range(A * L):
    if not mar[arranque] or comp[arranque]:
        continue
    cid += 1
    pila, n = [arranque], 0
    comp[arranque] = cid
    while pila:
        i = pila.pop(); n += 1
        x, y = i % A, i // A
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < A and 0 <= ny < L:
                j = ny * A + nx
                if mar[j] and not comp[j]:
                    comp[j] = cid
                    pila.append(j)
    tam[cid] = n

# LOS DOS MARES SON UNO SOLO, y por eso no se toman las dos componentes mayores:
# el recuadro llega hasta el cabo del norte, asi que el agua del oeste y la del
# este se comunican rodeandolo y forman una unica componente de 450.000 celdas.
# Tomar «las dos mayores» ponia el segundo rotulo dentro del estuario, que no es
# un mar. Se parte la componente grande por el meridiano de la ciudad y se
# rotula cada mitad.
mayor = max(tam, key=tam.get)
mares = []
for nombre, izquierda, rot in (('Mar de Poniente', True, -68),
                               ('Mar de Levante', False, 72)):
    mascara = bytearray(A * L)
    for i in range(A * L):
        if comp[i] != mayor:
            continue
        x, _ = celda_a_lienzo(i % A, i // A)
        if (x < 56.0) == izquierda:
            mascara[i] = 1
    (px, py), radio = mas_interior(mascara)
    mares.append({'nombre': nombre, 'x': px, 'y': py, 'rotacion': rot})
    print('  mar %-16s en (%5.2f,%5.2f) · %d celdas' % (nombre, px, py, sum(mascara)))

# --- sitios ------------------------------------------------------------------
CIUDAD = max((s for s in lugares if 30 < s['y'] < 55), key=lambda s: s['hab'])
PUERTO = max((s for s in lugares if s['costero'] and s['y'] < 30),
             key=lambda s: s['hab'])
sitios = [
    {'id': 'S-PTO', 'nombre': 'Puerto Espejo', 'tipo': 'puerto',
     'region_id': 'R-ESP', 'x': PUERTO['x'], 'y': PUERTO['y'],
     '_papel': 'Por aqui entra el combustible del pais.'},
    {'id': 'S-CIU', 'nombre': 'Bellaflor', 'tipo': 'ciudad',
     'region_id': 'R-BEL', 'x': CIUDAD['x'], 'y': CIUDAD['y'], 'radio': 11,
     'epicentro': True,
     '_papel': 'La ciudad epicentro. Sede del PMU y cinco de los diez puntos.'},
]
print('  puerto en (%.2f,%.2f) · ciudad en (%.2f,%.2f)'
      % (PUERTO['x'], PUERTO['y'], CIUDAD['x'], CIUDAD['y']))
for s in sitios:
    dentro_de = [r for r, poly in regiones.items() if geo.dentro(s['x'], s['y'], poly)]
    print('    %s cae en %s (esperado %s)' % (s['id'], dentro_de, s['region_id']))

mapa = {
    'aguas': [[list(p) for p in a] for a in AGUAS],
    'pais': 'Valcanto',
    'lienzo': [round(ANCHO_UTIL, 2), round(ALTO_UTIL, 2)],
    'contorno': contorno,
    'tramos': tramos,
    'regiones': {k: [list(p) for p in v] for k, v in regiones.items()},
    'rotulos': rotulos,
    'sitios': sitios,
    'mares': mares,
    'vias': vias,
}

json.dump(mapa, open(SP + '/mapa.json', 'w'), separators=(',', ':'))
print('')
print('guardado mapa.json ·',
      sum(len(v['puntos']) for v in vias), 'puntos de via ·',
      len(contorno), 'de contorno')
