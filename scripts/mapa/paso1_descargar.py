# -*- coding: utf-8 -*-
"""
Paso 1 · descargar la linea de costa y la red vial de un area real.

ES EL UNICO PASO QUE SALE A LA RED, y se corre una sola vez: lo que queda en el
repositorio es la geometria ya normalizada, no esta descarga.

El recuadro vive en `geo.py` para que los nueve pasos hablen del mismo sitio.
QUE AREA ES NO SE REGISTRA EN NINGUNA PARTE, y es deliberado: el territorio del
ejercicio es ficticio, y saber a que se parece el dibujo no aporta nada al
material --solo invita a buscarle correspondencias que no existen. Lo prestado
es el trazo, no el lugar.
"""
import json, urllib.request, urllib.error, sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo
SP = geo.SP
S, W, N, E = geo.S, geo.W, geo.N, geo.E

def q(filtro):
    return f'[out:json][timeout:240];(way[{filtro}]({S},{W},{N},{E}););out geom;'

def pedir(filtro, nombre, intentos=5):
    destino = os.path.join(SP, nombre)
    if os.path.exists(destino) and os.path.getsize(destino) > 1000:
        print('ya estaba:', nombre, os.path.getsize(destino)); return
    for i in range(intentos):
        try:
            d = urllib.request.urlopen(urllib.request.Request(
                'https://overpass-api.de/api/interpreter', data=q(filtro).encode(),
                headers={'User-Agent': 'simcase-estallido/1.0 (ejercicio docente)'},
            ), timeout=300).read()
            open(destino, 'wb').write(d)
            print('bajado:', nombre, len(d)); return
        except urllib.error.HTTPError as e:
            espera = 20 * (i + 1)
            print(f'  {e.code} · reintento en {espera}s'); time.sleep(espera)
    raise SystemExit('no se pudo bajar ' + nombre)

pedir('"natural"="coastline"', 'p2_costa.json')
time.sleep(8)
pedir('"highway"~"^(motorway|trunk|primary)$"', 'p2_vias.json')
