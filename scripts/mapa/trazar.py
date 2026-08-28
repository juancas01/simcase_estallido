# -*- coding: utf-8 -*-
"""Marching squares reutilizable: de una mascara de celdas a anillos cerrados."""
import math

CASOS = {
    1: [('I', 'S')], 2: [('S', 'D')], 3: [('I', 'D')],
    4: [('D', 'B')], 5: [('I', 'S'), ('D', 'B')], 6: [('S', 'B')],
    7: [('I', 'B')], 8: [('B', 'I')], 9: [('B', 'S')],
    10: [('S', 'D'), ('B', 'I')], 11: [('B', 'D')], 12: [('D', 'I')],
    13: [('D', 'S')], 14: [('S', 'I')],
}


def anillos(mascara, ancho, alto, minimo=8):
    def v(x, y):
        if 0 <= x < ancho and 0 <= y < alto:
            return 1 if mascara[y * ancho + x] else 0
        return 0

    desde = {}
    for y in range(-1, alto):
        for x in range(-1, ancho):
            a, b = v(x, y), v(x + 1, y)
            c, d = v(x + 1, y + 1), v(x, y + 1)
            caso = a + 2 * b + 4 * c + 8 * d
            if caso in (0, 15):
                continue
            medio = {'S': (x + 0.5, float(y)), 'D': (x + 1.0, y + 0.5),
                     'B': (x + 0.5, y + 1.0), 'I': (float(x), y + 0.5)}
            for p, q in CASOS[caso]:
                desde.setdefault(medio[p], []).append(medio[q])

    salida, vistos = [], set()
    for arranque in list(desde):
        if arranque in vistos:
            continue
        anillo = [arranque]
        vistos.add(arranque)
        actual = arranque
        while True:
            siguientes = [s for s in desde.get(actual, []) if s not in vistos]
            if not siguientes:
                break
            actual = siguientes[0]
            vistos.add(actual)
            anillo.append(actual)
        if len(anillo) >= minimo:
            salida.append(anillo)
    salida.sort(key=len, reverse=True)
    return salida
