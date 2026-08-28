# -*- coding: utf-8 -*-
"""
Una vista previa del mapa en PNG, sin dependencias.

No es el mapa que ve la sala --eso lo dibuja `Mapa.jsx` en SVG-- pero usa
EXACTAMENTE los mismos datos, y sirve para lo unico que hace falta aqui:
comprobar con los ojos que el pais tiene forma de pais, que las carreteras van
por donde van, que los corredores siguen las carreteras y que ningun punto de
cierre ha quedado flotando en el mar.
"""
import json, sys, io, os, math, zlib, struct

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapa.png')
ESC = 11            # pixeles por unidad de lienzo
W, H = int(93 * ESC), int(100 * ESC)

MAR = (14, 29, 42)
TIERRA = (27, 34, 44)
COSTA = (67, 113, 143)
FRONTERA = (90, 100, 116)
VIA = (142, 163, 189)
CORREDOR = {'C-PUE': (127, 163, 216), 'C-SUR': (95, 176, 140),
            'C-HOS': (179, 137, 207), 'C-REF': (207, 160, 85)}
REGION = [(95, 168, 127), (143, 168, 105), (201, 160, 90), (194, 112, 122)]
PUNTO = (207, 112, 121)
INFRA_OK = (111, 178, 201)
INFRA_NO = (201, 143, 122)

lienzo = bytearray()
buf = [[MAR[0], MAR[1], MAR[2]] for _ in range(W * H)]


def poner(x, y, color, alfa=1.0):
    xi, yi = int(x), int(y)
    if not (0 <= xi < W and 0 <= yi < H):
        return
    i = yi * W + xi
    if alfa >= 1.0:
        buf[i] = list(color)
    else:
        for k in range(3):
            buf[i][k] = int(buf[i][k] * (1 - alfa) + color[k] * alfa)


def linea(a, b, color, grosor=1.0, alfa=1.0):
    x0, y0 = a[0] * ESC, a[1] * ESC
    x1, y1 = b[0] * ESC, b[1] * ESC
    n = max(2, int(math.hypot(x1 - x0, y1 - y0)))
    r = max(0, int(grosor / 2))
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                poner(x + dx, y + dy, color, alfa)


def polilinea(pts, color, grosor=1.0, alfa=1.0):
    for a, b in zip(pts, pts[1:]):
        linea(a, b, color, grosor, alfa)


def rellenar(poly, color, alfa=0.5):
    ys = [p[1] * ESC for p in poly]
    for y in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
        cortes = []
        for i in range(len(poly)):
            x1, y1 = poly[i][0] * ESC, poly[i][1] * ESC
            x2, y2 = poly[(i + 1) % len(poly)][0] * ESC, poly[(i + 1) % len(poly)][1] * ESC
            if (y1 > y) != (y2 > y):
                cortes.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        cortes.sort()
        for k in range(0, len(cortes) - 1, 2):
            for x in range(max(0, int(cortes[k])), min(W, int(cortes[k + 1]) + 1)):
                poner(x, y, color, alfa)


def marca(p, color, radio=4, forma='o'):
    cx, cy = p[0] * ESC, p[1] * ESC
    for dy in range(-radio, radio + 1):
        for dx in range(-radio, radio + 1):
            if forma == 'o' and dx * dx + dy * dy > radio * radio:
                continue
            if forma == 'd' and abs(dx) + abs(dy) > radio:
                continue
            poner(cx + dx, cy + dy, color)


d = json.load(io.open(RAIZ + '/data/escenario/estado_inicial.json', encoding='utf-8'))
m = d['mapa']

rellenar(m['contorno'], TIERRA, 1.0)
for i, (rid, poly) in enumerate(m['regiones'].items()):
    rellenar(poly, REGION[i % 4], 0.16)
for a in m.get('aguas', []):
    rellenar(a, MAR, 1.0)
for v in m['vias']:
    g = {'autopista': 2, 'troncal': 1, 'primaria': 1}[v['clase']]
    al = {'autopista': 0.42, 'troncal': 0.32, 'primaria': 0.22}[v['clase']]
    polilinea(v['puntos'], VIA, g, al)
for t in m['tramos']:
    polilinea(t['puntos'], FRONTERA if t['frontera'] else COSTA, 2, 0.9)
for cid, tz in m['trazados'].items():
    polilinea(tz, CORREDOR.get(cid, (120, 120, 120)), 3, 0.95)
for i in d['infraestructura']:
    marca((i['x'], i['y']), INFRA_OK if i['infra_id'] == 'I-REF' else INFRA_NO, 3, 'd')
for n in d['nodos']:
    marca((n['x'], n['y']), (10, 10, 12), 6)
    marca((n['x'], n['y']), PUNTO, 4)
for s in m['sitios']:
    marca((s['x'], s['y']), (230, 236, 244), 3, 'd')

crudo = bytearray()
for y in range(H):
    crudo.append(0)
    for x in range(W):
        crudo.extend(buf[y * W + x])


def trozo(tipo, datos):
    c = struct.pack('>I', len(datos)) + tipo + datos
    return c + struct.pack('>I', zlib.crc32(tipo + datos) & 0xffffffff)


png = (b'\x89PNG\r\n\x1a\n'
       + trozo(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
       + trozo(b'IDAT', zlib.compress(bytes(crudo), 6))
       + trozo(b'IEND', b''))
open(SALIDA, 'wb').write(png)
print('escrito', SALIDA, W, 'x', H, len(png), 'bytes')
