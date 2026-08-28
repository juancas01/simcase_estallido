# -*- coding: utf-8 -*-
"""Paso 5 · los asentamientos reales, para no poner el puerto donde no hay nada."""
import json, urllib.request, urllib.error, sys, io, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
S, W, N, E = geo.S, geo.W, geo.N, geo.E
destino = SP + '/p2_lugares.json'

if not (os.path.exists(destino) and os.path.getsize(destino) > 500):
    q = (f'[out:json][timeout:120];'
         f'(node["place"~"^(city|town)$"]({S},{W},{N},{E}););out;')
    for i in range(5):
        try:
            d = urllib.request.urlopen(urllib.request.Request(
                'https://overpass-api.de/api/interpreter', data=q.encode(),
                headers={'User-Agent': 'simcase-estallido/1.0 (ejercicio docente)'},
            ), timeout=180).read()
            open(destino, 'wb').write(d)
            break
        except urllib.error.HTTPError as e:
            print(' ', e.code, '· reintento'); time.sleep(20 * (i + 1))

lug = json.load(open(destino, encoding='utf-8'))
pr, _ = geo.proyector()
rej = json.load(open(SP + '/rejilla_tierra.json'))
A, L, tierra = rej['ancho'], rej['alto'], rej['tierra']


def es_costero(lon, lat, radio=9):
    """Hay mar a menos de `radio` celdas: sirve de puerto."""
    cx = int((lon - W) / (E - W) * (A - 1))
    cy = int((N - lat) / (N - S) * (L - 1))
    for dy in range(-radio, radio + 1, 3):
        for dx in range(-radio, radio + 1, 3):
            x, y = cx + dx, cy + dy
            if 0 <= x < A and 0 <= y < L and not tierra[y * A + x]:
                return True
    return False


sitios = []
for e in lug['elements']:
    t = e.get('tags', {})
    try:
        hab = int(str(t.get('population', '0')).replace('.', '').replace(' ', ''))
    except ValueError:
        hab = 0
    x, y = pr(e['lon'], e['lat'])
    sitios.append({'clase': t.get('place'), 'hab': hab, 'x': x, 'y': y,
                   'costero': es_costero(e['lon'], e['lat'])})

sitios.sort(key=lambda s: -s['hab'])
print('asentamientos:', len(sitios))
for s in sitios[:12]:
    print(f"  {s['clase']:>4} hab {s['hab']:>7} en ({s['x']:>5}, {s['y']:>5})"
          f"{' · costero' if s['costero'] else ''}")

json.dump(sitios, open(SP + '/lugares.json', 'w'), separators=(',', ':'))
print('guardado lugares.json')
