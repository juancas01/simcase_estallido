# -*- coding: utf-8 -*-
"""
Paso 7 · los diez puntos de cierre y los cuatro corredores, sobre vias de verdad.

UN CORREDOR NO ES UNA CURVA ENTRE DOS MOTAS. Hasta ahora el mapa unia los puntos
de un corredor con una Bezier suave, y esa curva afirmaba algo falso: que entre
un bloqueo y el siguiente la carretera va por ahi. Aqui el corredor se RUTEA
--Dijkstra sobre la red vial real-- y lo que se dibuja es el camino que existe.

PRIMERO SE RUTEA EL CORREDOR, DESPUES SE SIEMBRAN SUS PUNTOS ENCIMA, y el orden
importa. Colocando antes los puntos a ojo y ruteando despues entre ellos, dos
bloqueos de la misma ciudad separados por cinco unidades salian unidos por un
rodeo de cincuenta y siete: cada hueco del grafo --un enlace a distinto nivel
donde la autopista y la primaria no comparten vertice-- se convertia en media
vuelta al pais dibujada como si fuera el corredor. Sembrando los puntos SOBRE el
trazado, el corredor es un camino limpio y cada punto cae exactamente en el, en
orden.

EL GRAFO SE MONTA SOBRE LA RED SIN SIMPLIFICAR. Douglas-Peucker se come justo
los vertices intermedios donde dos vias se cruzan, asi que sobre la red
simplificada el grafo sale en pedazos y casi ningun par de puntos se alcanza.
"""
import json, sys, io, os, math, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
REJILLA = 0.05      # dos vertices a menos de esto son el mismo cruce

ruteo = json.load(open(SP + '/vias_ruteo.json', encoding='utf-8'))
_reg = json.load(open(SP + '/regiones.json'))
regiones = {k: [tuple(p) for p in v] for k, v in _reg['regiones'].items()}


def clave(p):
    return (round(p[0] / REJILLA), round(p[1] / REJILLA))


pos, ady = {}, {}
PESO_CLASE = {'autopista': 1.0, 'troncal': 1.15, 'primaria': 1.35}
for cadena in ruteo:
    w = PESO_CLASE[cadena['clase']]
    pts = [tuple(p) for p in cadena['puntos']]
    for a, b in zip(pts, pts[1:]):
        ka, kb = clave(a), clave(b)
        if ka == kb:
            continue
        pos.setdefault(ka, a)
        pos.setdefault(kb, b)
        d = math.dist(a, b) * w
        ady.setdefault(ka, []).append((kb, d))
        ady.setdefault(kb, []).append((ka, d))

print('grafo:', len(pos), 'vertices ·',
      sum(len(v) for v in ady.values()) // 2, 'aristas')

comp, cid = {}, 0
for k in pos:
    if k in comp:
        continue
    cid += 1
    pila = [k]
    comp[k] = cid
    while pila:
        u = pila.pop()
        for v, _ in ady.get(u, []):
            if v not in comp:
                comp[v] = cid
                pila.append(v)
tam = {}
for k, c in comp.items():
    tam[c] = tam.get(c, 0) + 1
grande = max(tam, key=tam.get)
print('componentes:', len(tam), '· la mayor tiene', tam[grande], 'vertices')


def pegar(x, y):
    mejor, cual = 1e18, None
    for k, p in pos.items():
        if comp[k] != grande:
            continue
        d = (p[0] - x) ** 2 + (p[1] - y) ** 2
        if d < mejor:
            mejor, cual = d, k
    return cual


def ruta(a, b):
    dist = {a: 0.0}
    previo = {}
    cola = [(0.0, a)]
    vistos = set()
    while cola:
        d, u = heapq.heappop(cola)
        if u in vistos:
            continue
        vistos.add(u)
        if u == b:
            break
        for v, w in ady.get(u, []):
            nd = d + w
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                previo[v] = u
                heapq.heappush(cola, (nd, v))
    if b not in dist:
        return None
    camino, u = [b], b
    while u != a:
        u = previo[u]
        camino.append(u)
    return [pos[k] for k in reversed(camino)]


def en_fraccion(camino, f):
    """El punto que esta a la fraccion `f` del recorrido, medido por longitud."""
    total = geo.largo(camino)
    objetivo = total * f
    acumulado = 0.0
    for a, b in zip(camino, camino[1:]):
        d = math.dist(a, b)
        if acumulado + d >= objetivo:
            t = 0.0 if d == 0 else (objetivo - acumulado) / d
            return (round(a[0] + (b[0] - a[0]) * t, 2),
                    round(a[1] + (b[1] - a[1]) * t, 2))
        acumulado += d
    return camino[-1]


# --- los cuatro corredores ---------------------------------------------------
# Cada uno se define por sus dos extremos y por DONDE cae cada punto de cierre a
# lo largo del recorrido. Cinco de los diez puntos quedan en la ciudad epicentro
# --que esta sobre un estrecho, asi que sus cruces son los cuellos de botella
# del pais entero-- y cinco fuera.
CORREDORES = [
    ('C-PUE', 'Bellaflor - Puerto Espejo', (56.0, 41.5), (74.6, 19.6), [
        ('N003', 'Puente Amarillo',               0.04, 'R-BEL'),
        ('N001', 'Peaje del Puerto',              0.26, 'R-BEL'),
        ('N004', 'Alto del Mirador',              0.82, 'R-ESP'),
    ]),
    ('C-REF', 'Refineria - Acopios', (52.5, 45.5), (66.5, 18.0), [
        ('N013', 'Porteria de la refineria',      0.03, 'R-BEL'),
        ('N015', 'Via de carrotanques',           0.95, 'R-ESP'),
    ]),
    ('C-HOS', 'Corredor hospitalario', (53.6, 37.2), (58.4, 70.0), [
        ('N010', 'Acceso Hospital Universitario', 0.03, 'R-BEL'),
        ('N012', 'Rotonda del Oriente',           0.96, 'R-CUM'),
    ]),
    ('C-SUR', 'Corredor del Sur', (63.0, 81.4), (30.0, 68.0), [
        ('N005', 'Cruce de San Isidro',           0.05, 'R-CUM'),
        ('N008', 'Puente de Guadua',              0.96, 'R-VER'),
    ]),
]

# El punto que no pertenece a ningun corredor: abrirlo por la fuerza no compra
# un solo dia de autonomia a nadie, y esa leccion necesita un punto que la
# encarne.
SUELTO = ('N022', 'Loma del Oriente', 64.5, 45.5, 'R-BEL')

# El punto suelto es UNO DE LOS DE LA CIUDAD: la leccion es que abrirlo por la
# fuerza no compra un dia de autonomia a nadie, y para eso tiene que estar donde
# la sala mira. Sin este radio, la busqueda por maxima separacion se lo llevaba
# al extremo oeste de la region --a veinticinco unidades de todo-- que cumple la
# invariante y no cuenta la historia.
CIUDAD = (56.76, 40.74)
RADIO_CIUDAD = 16.0

puntos, trazados = {}, {}
print('')
for cc, nombre, ini, fin, siembra in CORREDORES:
    ka, kb = pegar(*ini), pegar(*fin)
    camino = ruta(ka, kb)
    if camino is None:
        print('  %s SIN RUTA' % cc)
        continue
    recta = math.dist(pos[ka], pos[kb])
    largo = geo.largo(camino)
    simple = geo.dp(camino, 0.10)
    limpio = [simple[0]]
    for p in simple[1:]:
        if p != limpio[-1]:
            limpio.append(p)
    trazados[cc] = limpio
    print('  %s %-26s largo %5.1f (recta %5.1f · rodeo x%.2f) · %4d -> %3d vertices'
          % (cc, nombre, largo, recta, largo / recta, len(camino), len(limpio)))
    for nid, nom, f, rid in siembra:
        x, y = en_fraccion(camino, f)
        cae = [r for r, poly in regiones.items() if geo.dentro(x, y, poly)]
        marca = 'ok' if cae == [rid] else 'OJO: cae en ' + (','.join(cae) or 'ninguna')
        print('       %s %-32s f=%.2f -> (%5.2f,%5.2f) %s %s'
              % (nid, nom, f, x, y, rid, marca))
        puntos[nid] = {'nodo_id': nid, 'nombre': nom, 'x': x, 'y': y,
                       'region_id': rid, 'corredor_id': cc}

# No se pide un sitio a ojo y se pega al vertice mas cercano: pedirlo a ojo lo
# dejo dos veces a menos de metro y medio del Puente Amarillo, porque donde yo
# lo queria no habia carretera --hay estuario-- y el pegado lo devolvia al
# raciMO del centro. Se elige el vertice de la region que MAS LEJOS queda del
# punto mas proximo, que es justo lo que hace falta para que su rotulo se lea.
nid, nom, _, _, rid = SUELTO
ya = [(p['x'], p['y']) for p in puntos.values()]
mejor, cual = -1.0, None
for k, p in pos.items():
    if comp[k] != grande or not geo.dentro(p[0], p[1], regiones[rid]):
        continue
    if math.dist(p, CIUDAD) > RADIO_CIUDAD:
        continue
    d = min(math.dist(p, q) for q in ya)
    if d > mejor:
        mejor, cual = d, p
px, py = cual
print('  (suelto) %s %-24s -> (%5.2f,%5.2f) %s · a %.1f del punto mas proximo'
      % (nid, nom, px, py, rid, mejor))
puntos[nid] = {'nodo_id': nid, 'nombre': nom, 'x': px, 'y': py,
               'region_id': rid, 'corredor_id': None}

# --- comprobaciones ----------------------------------------------------------
print('')
print('reparto:', {r: sum(1 for p in puntos.values() if p['region_id'] == r)
                   for r in ('R-BEL', 'R-ESP', 'R-CUM', 'R-VER')})
peor = min(((math.dist((a['x'], a['y']), (b['x'], b['y'])), a['nodo_id'], b['nodo_id'])
            for i, a in enumerate(puntos.values())
            for b in list(puntos.values())[i + 1:]), key=lambda t: t[0])
print('los dos puntos mas juntos: %s y %s a %.2f' % (peor[1], peor[2], peor[0]))

json.dump({'puntos': puntos, 'trazados': trazados},
          open(SP + '/red.json', 'w'), separators=(',', ':'))
print('guardado red.json')
