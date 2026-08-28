# -*- coding: utf-8 -*-
"""
Paso 4 · la red vial: proyectar, recortar, EMPALMAR y simplificar.

Overpass devuelve las vias ENTERAS aunque solo toquen el recuadro, asi que hay
que recortarlas: sin eso, media docena de autopistas salen disparadas fuera del
lienzo. Se recorta partiendo cada via en los trozos que caen dentro, y no
moviendo los puntos de fuera al borde: arrastrarlos al borde inventa un trazado
que no existe.

EL EMPALME NO ES OPCIONAL, y costo una pasada descubrirlo. Una autopista no
viene como una linea: viene como cincuenta ways de trescientos metros. Filtrando
por longitud ANTES de empalmar se cae la red entera —5.421 trozos quedaban en
439— porque cada pedazo mide menos que el minimo. Primero se cosen los pedazos
que comparten extremo, y despues se mide.
"""
import json, sys, io, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
pr, (ANCHO_UTIL, ALTO_UTIL) = geo.proyector()
MARGEN = 0.6

vias = json.load(open(SP + '/p2_vias.json', encoding='utf-8'))

# Tres clases y no siete. La rejilla vial va casi transparente: lo que tiene que
# distinguirse es el esqueleto —por donde va de verdad el trafico pesado— del
# resto, y para eso bastan tres grosores.
CLASE = {'motorway': 'autopista', 'trunk': 'troncal', 'primary': 'primaria'}


def dentro_lienzo(p):
    return (-MARGEN <= p[0] <= ANCHO_UTIL + MARGEN
            and -MARGEN <= p[1] <= ALTO_UTIL + MARGEN)


crudos = {c: [] for c in CLASE.values()}
for e in vias['elements']:
    g = e.get('geometry') or []
    clase = CLASE.get(e['tags'].get('highway'))
    if clase is None or len(g) < 2:
        continue
    corrido = []
    for p in (pr(q['lon'], q['lat']) for q in g):
        if dentro_lienzo(p):
            corrido.append(p)
        else:
            if len(corrido) >= 2:
                crudos[clase].append(corrido)
            corrido = []
    if len(corrido) >= 2:
        crudos[clase].append(corrido)

print('trozos recortados:', {c: len(v) for c, v in crudos.items()})


def empalmar(trozos):
    """Cose los trozos que comparten un extremo. Los nodos compartidos de OSM
    proyectan al mismo par de decimales, asi que el empalme es exacto."""
    pendientes = [list(t) for t in trozos]
    extremos = {}
    for i, t in enumerate(pendientes):
        extremos.setdefault(t[0], []).append((i, 'ini'))
        extremos.setdefault(t[-1], []).append((i, 'fin'))

    usado = [False] * len(pendientes)
    cadenas = []
    for i in range(len(pendientes)):
        if usado[i]:
            continue
        usado[i] = True
        cadena = list(pendientes[i])
        # crecer por los dos extremos
        for cabeza in (False, True):
            while True:
                punta = cadena[0] if cabeza else cadena[-1]
                siguiente = None
                for j, lado in extremos.get(punta, []):
                    if usado[j]:
                        continue
                    siguiente = (j, lado)
                    break
                if siguiente is None:
                    break
                j, lado = siguiente
                usado[j] = True
                otro = pendientes[j]
                trozo = otro if lado == 'ini' else otro[::-1]
                if cabeza:
                    cadena = trozo[::-1][:-1] + cadena
                else:
                    cadena = cadena + trozo[1:]
        cadenas.append(cadena)
    return cadenas


# La red SIN simplificar se guarda aparte: es sobre ella sobre la que se rutea.
# Simplificar antes de rutear parte el grafo, porque Douglas-Peucker se come
# justamente los vertices intermedios donde dos vias se cruzan.
ruteo = []
for clase, trozos in crudos.items():
    for c in empalmar(trozos):
        ruteo.append({'clase': clase, 'puntos': c})
json.dump(ruteo, open(SP + '/vias_ruteo.json', 'w'), separators=(',', ':'))
print('guardado vias_ruteo.json ·', len(ruteo), 'cadenas ·',
      sum(len(r['puntos']) for r in ruteo), 'puntos')

TOL = {'autopista': 0.10, 'troncal': 0.12, 'primaria': 0.16}
LARGO_MINIMO = {'autopista': 1.2, 'troncal': 1.2, 'primaria': 1.6}

salida = []
for clase, trozos in crudos.items():
    cadenas = empalmar(trozos)
    largas = [c for c in cadenas if geo.largo(c) >= LARGO_MINIMO[clase]]
    print(f'  {clase}: {len(trozos)} trozos → {len(cadenas)} cadenas → '
          f'{len(largas)} con longitud suficiente')
    for c in largas:
        simple = geo.dp(c, TOL[clase])
        limpio = [simple[0]]
        for p in simple[1:]:
            if p != limpio[-1]:
                limpio.append(p)
        if len(limpio) >= 2:
            salida.append({'clase': clase, 'puntos': limpio})

# Las mas largas primero: al dibujar, el esqueleto va debajo y las cortas encima.
salida.sort(key=lambda t: -geo.largo(t['puntos']))
print('total:', len(salida), 'vias ·', sum(len(t['puntos']) for t in salida), 'puntos')

json.dump(salida, open(SP + '/vias.json', 'w'), separators=(',', ':'))
print('guardado vias.json')
