# -*- coding: utf-8 -*-
"""Utilidades de geometria compartidas por los pasos de construccion del mapa."""
from __future__ import annotations
import json, math, os

# Los intermedios --descargas de decenas de megas, rejillas de un millon de
# celdas-- van a `trabajo/`, que esta en .gitignore. Lo que se versiona es el
# RESULTADO, que vive en `data/escenario/estado_inicial.json`.
SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trabajo')
os.makedirs(SP, exist_ok=True)
S, W, N, E = 55.95, 8.00, 57.80, 11.30
LIENZO = 100.0


def proyector():
    """Equirectangular con correccion de latitud, normalizada al lienzo 0..100.

    `y` crece HACIA ABAJO: es el sistema de la pantalla, que es el que ya usan
    los puntos del escenario y todo `Mapa.jsx`.
    """
    lat0 = math.radians((S + N) / 2)
    kx = math.cos(lat0)
    x0, x1 = W * kx, E * kx
    y0, y1 = S, N
    ancho, alto = x1 - x0, y1 - y0
    k = LIENZO / max(ancho, alto)

    def pr(lon, lat):
        x = (lon * kx - x0) * k
        y = (y1 - lat) * k          # invertido: norte arriba
        return (round(x, 2), round(y, 2))

    return pr, (ancho * k, alto * k)


def dp(puntos, tol):
    """Douglas-Peucker iterativo."""
    if len(puntos) < 3:
        return list(puntos)
    guardar = [False] * len(puntos)
    guardar[0] = guardar[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        i, j = pila.pop()
        if j <= i + 1:
            continue
        ax, ay = puntos[i]
        bx, by = puntos[j]
        dx, dy = bx - ax, by - ay
        norma = math.hypot(dx, dy)
        peor, idx = -1.0, -1
        for k in range(i + 1, j):
            px, py = puntos[k]
            if norma == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / norma
            if d > peor:
                peor, idx = d, k
        if peor > tol:
            guardar[idx] = True
            pila.append((i, idx))
            pila.append((idx, j))
    return [p for p, g in zip(puntos, guardar) if g]


def dentro(x, y, poligono):
    d = False
    n = len(poligono)
    for i in range(n):
        x1, y1 = poligono[i]
        x2, y2 = poligono[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            corte = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < corte:
                d = not d
    return d


def area(poligono):
    a = 0.0
    for i in range(len(poligono)):
        x1, y1 = poligono[i]
        x2, y2 = poligono[(i + 1) % len(poligono)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def largo(cadena):
    return sum(math.dist(cadena[i], cadena[i + 1]) for i in range(len(cadena) - 1))
