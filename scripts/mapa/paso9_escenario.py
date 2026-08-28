# -*- coding: utf-8 -*-
"""
Paso 9 · escribir `data/escenario/estado_inicial.json` entero.

Junta tres procedencias, y conviene tenerlas separadas en la cabeza:

  · del alijo de git ... los atributos de juego de cada punto (dureza, vocería,
    apoyo, composición real, días sostenido), las cuatro regiones, las dos
    denuncias y el hecho H1. Esto se RECUPERA, no se inventa.
  · de los pasos 1-8 ... toda la geografía: contorno, tramos, regiones, rótulos,
    mares, sitios, red vial, posiciones de los puntos y trazados de corredores.
  · redactado aquí ..... `masa_base` de ocho de los diez puntos, y la base de
    infraestructura relevante.
"""
import json, sys, io, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import geo

SP = geo.SP
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DESTINO = RAIZ + '/data/escenario/estado_inicial.json'

# Los atributos de juego de cada punto --dureza, voceria, apoyo, composicion
# real, dias sostenido--, las cuatro regiones, las dos denuncias y el hecho
# H1 se leen del escenario que ya existe: este paso reescribe la GEOGRAFIA,
# no el caso.
alijo = json.load(open(RAIZ + '/data/escenario/estado_inicial.json',
                       encoding='utf-8'))
mapa = json.load(open(SP + '/mapa.json', encoding='utf-8'))
red = json.load(open(SP + '/red.json', encoding='utf-8'))
regiones_poly = {k: [tuple(p) for p in v] for k, v in mapa['regiones'].items()}

O = collections.OrderedDict

# --- los nombres, con sus tildes --------------------------------------------
# El alijo los tiene sin acentuar. Los nombres se leen en voz alta desde el
# fondo de la sala y se proyectan en una pared: van bien escritos.
TILDES = {
    'Porteria de la refineria': 'Portería de la refinería',
    'Via de carrotanques': 'Vía de carrotanques',
    'Region de Bellaflor': 'Región de Bellaflor',
    'Bellaflor - Puerto Espejo': 'Bellaflor – Puerto Espejo',
    'Refineria - Acopios': 'Refinería – Acopios',
}

# CUANTA GENTE REUNE CADA PUNTO cuando la movilizacion esta en el nivel de
# referencia. Dos salen del working copy que se perdio; los otros ocho se
# REDACTAN AQUI a partir del `_papel` de cada punto, y hay que saberlo: son
# convenciones nuevas, no cifras recuperadas. La regla que siguen es la del
# propio caso --un peaje de carretera y una glorieta del centro no reunen la
# misma gente-- y el orden respeta lo que dice cada ficha.
MASA_BASE = {
    'N013': 260,   # recuperado
    'N001': 180,   # recuperado
    'N003': 420,   # el punto duro: quince dias y el barrio entero detras
    'N010': 150,   # el mas blando, dos dias, se abre hablando
    'N022': 340,   # quince dias sostenido y el barrio entero detras
    'N015': 160,   # via de carretera, poca poblacion alrededor
    'N004': 200,   # el acceso del puerto
    'N012': 240,   # rotonda urbana de la region mas apretada
    'N005': 190,   # cruce rural con vocacion de mesa muy alta
    'N008': 130,   # apoyo ya bajo y cayendo
}

FUERA = ['N002']         # se cae para dejar diez puntos, cinco en la ciudad

# --- puntos ------------------------------------------------------------------
nodos = []
for n in alijo['nodos']:
    nid = n['nodo_id']
    if nid in FUERA:
        continue
    sitio = red['puntos'][nid]
    nuevo = O()
    nuevo['nodo_id'] = nid
    nuevo['nombre'] = TILDES.get(n['nombre'], n['nombre'])
    nuevo['_papel'] = n['_papel']
    nuevo['region_id'] = n['region_id']
    nuevo['corredor_id'] = sitio['corredor_id']
    for c in ('dureza', 'control_voceria', 'apoyo_local', 'dias_sostenido'):
        nuevo[c] = n[c]
    nuevo['masa_base'] = MASA_BASE[nid]
    nuevo['composicion_real'] = n['composicion_real']
    nuevo['x'] = sitio['x']
    nuevo['y'] = sitio['y']
    if n.get('proximidad_infra_critica'):
        nuevo['proximidad_infra_critica'] = True
    nodos.append(nuevo)

por_id = {n['nodo_id']: n for n in nodos}
assert len(nodos) == 10, len(nodos)

# --- corredores ---------------------------------------------------------------
ORDEN = {'C-PUE': ['N003', 'N001', 'N004'], 'C-REF': ['N013', 'N015'],
         'C-HOS': ['N010', 'N012'], 'C-SUR': ['N005', 'N008']}
PAPEL_PUE = ('La arteria, y la mas larga: tres puntos, dos de ellos en la '
             'ciudad. Combustible, alimentos y mision medica por la misma via, '
             'de modo que abrirla resuelve mucho a la vez. Su primer punto es '
             'el mas duro del tablero.')

corredores = []
for c in alijo['corredores']:
    cid = c['corredor_id']
    nuevo = O()
    nuevo['corredor_id'] = cid
    nuevo['nombre'] = TILDES.get(c['nombre'], c['nombre'])
    nuevo['_papel'] = PAPEL_PUE if cid == 'C-PUE' else c['_papel']
    nuevo['nodos'] = ORDEN[cid]
    nuevo['poblacion_aguas_abajo'] = c['poblacion_aguas_abajo']
    nuevo['costo_diario_mm_cop'] = c['costo_diario_mm_cop']
    nuevo['clases_prioridad'] = c['clases_prioridad']
    corredores.append(nuevo)

# --- infraestructura ----------------------------------------------------------
# Cada instalacion se ancla a un punto de cierre o a un sitio, y se desplaza
# hasta encontrar hueco DENTRO de su region y lejos de los puntos: dos marcas
# superpuestas en el mapa no se leen ni se pinchan.
def acomodar(ax, ay, rid, separacion=2.6):
    ocupado = [(p['x'], p['y']) for p in nodos] + \
              [(i['x'], i['y']) for i in infraestructura]
    mejor, cual = -1.0, (ax, ay)
    for k in range(64):
        ang = k * (2 * math.pi / 16)
        radio = 1.8 + 1.5 * (k // 16)
        x = round(ax + math.cos(ang) * radio, 2)
        y = round(ay + math.sin(ang) * radio, 2)
        if not geo.dentro(x, y, regiones_poly[rid]):
            continue
        d = min((math.dist((x, y), q) for q in ocupado), default=99.0)
        if d > mejor:
            mejor, cual = d, (x, y)
        if d >= separacion:
            break
    return cual, mejor


SITIOS = {s['id']: s for s in mapa['sitios']}
PLAN = [
    ('I-REF', 'Refinería de Bellaflor', 'energia', 'R-BEL', 'N013', 'vital',
     'Todo el combustible del país sale de aquí. Sin ella no hay carrotanques, '
     'ni escoltas, ni plantas eléctricas de hospital.', ['N013'],
     'Aqui ocurrio H1 y ya tiene custodia reforzada, puesta por el hecho '
     'heredado. Es la instalacion sobre la que la mesa no decide si proteger, '
     'sino cuanto.'),
    ('I-HOS', 'Hospital Universitario de Bellaflor', 'salud', 'R-BEL', 'N010',
     'vital',
     'La red de alta complejidad de la región y los pacientes en soporte de '
     'oxígeno de tres municipios.', ['N010'],
     'El corredor hospitalario empieza aqui. Dejarlo sin proteger no produce '
     'ningun evento en la corrida: produce un riesgo que el debriefing nombra.'),
    ('I-AGU', 'Planta de agua La Ceiba', 'agua', 'R-BEL', 'N003', 'vital',
     'El agua potable de la ciudad epicentro entera.', ['N003'],
     'Contigua al Puente Amarillo, el punto que menos se deja abrir. Es la '
     'instalacion que nadie nombra en la sala y la que mas gente deja sin nada.'),
    ('I-SUB', 'Subestación eléctrica Bellaflor Sur', 'energia', 'R-BEL', 'N001',
     'alta', 'La energía de los barrios del sur y del bombeo de agua.',
     ['N001'], ''),
    ('I-TER', 'Terminal de transporte de Bellaflor', 'logistica', 'R-BEL',
     'N022', 'media',
     'La salida por carretera de la ciudad y el acopio de alimentos que llega '
     'del sur.', ['N022'],
     'Junto a Loma del Oriente, el unico punto que no pertenece a ningun corredor.'),
    ('I-PTO', 'Terminal marítimo de Puerto Espejo', 'logistica', 'R-ESP',
     'S-PTO', 'vital',
     'Por aquí entra el crudo importado y sale la carga de exportación. Es la '
     'boca del país.', [], 'El sitio S-PTO, ahora tambien declarable.'),
    ('I-COM', 'Acopio de combustible de Puerto Espejo', 'energia', 'R-ESP',
     'N015', 'vital',
     'La reserva de combustible de las cuatro regiones. El corredor de la '
     'refinería termina aquí.', ['N015'], 'El otro extremo de C-REF.'),
    ('I-AER', 'Aeropuerto de Valcanto', 'logistica', 'R-ESP', 'N004', 'alta',
     'La proyección aérea de fuerza y la entrada de misión médica cuando la '
     'carretera no sirve.', [],
     'Lo que hace posible el modo proyeccion_aerea del redespliegue militar.'),
    ('I-HCU', 'Hospital Regional de Las Cumbres', 'salud', 'R-CUM', 'N012',
     'vital', 'La única red hospitalaria de la región más apretada de oxígeno.',
     ['N012'], ''),
    ('I-BOM', 'Estación de bombeo San Isidro', 'energia', 'R-CUM', 'N005',
     'alta', 'El poliducto que lleva combustible al sur sin pasar por carretera.',
     ['N005'], ''),
    ('I-ACU', 'Acueducto regional de Alto Verde', 'agua', 'R-VER', 'N008',
     'alta', 'El agua de la región y de los municipios del extremo sur.',
     ['N008'], ''),
    ('I-ACO', 'Centro de acopio de Alto Verde', 'alimentos', 'R-VER', 'N008',
     'media',
     'El alimento fresco que sube al resto del país por el Corredor del Sur.',
     [], ''),
]

infraestructura = []
print('infraestructura:')
for iid, nombre, tipo, rid, ancla, crit, depende, contiguos, papel in PLAN:
    if ancla in por_id:
        ax, ay = por_id[ancla]['x'], por_id[ancla]['y']
    else:
        ax, ay = SITIOS[ancla]['x'], SITIOS[ancla]['y']
    (x, y), sep = acomodar(ax, ay, rid)
    reg = [r for r, poly in regiones_poly.items() if geo.dentro(x, y, poly)]
    print('  %s %-38s (%5.2f,%5.2f) %s sep %.1f %s'
          % (iid, nombre, x, y, rid, sep, 'ok' if reg == [rid] else 'OJO ' + str(reg)))
    e = O()
    e['infra_id'] = iid
    e['nombre'] = nombre
    e['tipo'] = tipo
    e['region_id'] = rid
    e['x'] = x
    e['y'] = y
    e['criticidad'] = crit
    e['de_que_depende'] = depende
    e['nodos_contiguos'] = contiguos
    if papel:
        e['_papel'] = papel
    infraestructura.append(e)

# --- el archivo ---------------------------------------------------------------
regiones = []
for r in alijo['regiones']:
    nuevo = O(r)
    nuevo['nombre'] = TILDES.get(r['nombre'], r['nombre'])
    regiones.append(nuevo)

mapa_out = O()
mapa_out['_nota'] = (
    'MAPA EN DOS NIVELES SOBRE GEOGRAFIA REAL. El nivel de pais dibuja Valcanto '
    'entera --su litoral, su frontera terrestre, sus dos mares, su puerto y sus '
    'cuatro regiones-- y tine cada region por su estado de bloqueo; el de region '
    'hace zoom y muestra sus puntos y sus corredores. LA SILUETA Y LA RED VIAL '
    'SON REALES: salen de datos abiertos de una costa que no consta en ninguna '
    'parte, igual que Macondo se dibujo sobre Mocoa. El territorio sigue siendo '
    'ficticio; lo prestado es el trazo. Las coordenadas van en un lienzo de '
    '0..100 con la y hacia abajo, y cada punto tiene que caer dentro del '
    'poligono de su region: el loader lo exige.')
mapa_out['pais'] = mapa['pais']
mapa_out['lienzo'] = mapa['lienzo']
mapa_out['_contorno'] = (
    'La silueta de tierra, trazada con marching squares sobre la linea de costa '
    'real. `tramos` es ese mismo contorno partido en litoral y frontera: por uno '
    'entra el combustible del pais y por el otro no entra nada que el ejercicio '
    'modele.')
mapa_out['contorno'] = [list(p) for p in mapa['contorno']]
mapa_out['tramos'] = [{'frontera': t['frontera'],
                       'puntos': [list(p) for p in t['puntos']]}
                      for t in mapa['tramos']]
mapa_out['_vias'] = (
    'LA RED VIAL REAL, y va casi transparente a proposito: no es la informacion, '
    'es el suelo sobre el que se lee la informacion. Lo que tiene que resaltar '
    'son los corredores y los puntos de cierre. Tres clases --autopista, troncal, '
    'primaria-- porque lo unico que hay que distinguir es el esqueleto por donde '
    'va el trafico pesado.')
mapa_out['vias'] = mapa['vias']
mapa_out['_trazados'] = (
    'EL RECORRIDO DE CADA CORREDOR SOBRE LA RED, ruteado con Dijkstra entre sus '
    'puntos. Antes el mapa unia los puntos de un corredor con una curva suave, y '
    'esa curva afirmaba que la carretera va por ahi. Va por donde dice esto.')
mapa_out['trazados'] = {k: [list(p) for p in v] for k, v in red['trazados'].items()}
mapa_out['_aguas'] = (
    'El agua de dentro: el estuario que parte la ciudad epicentro y sus brazos. '
    'Va aparte del contorno a proposito. Para REPARTIR el territorio se rellena '
    '--si no, el contorno del pais encierra un agujero que ninguna region cubre '
    'y la teselacion deja huecos-- y para DIBUJAR se pinta encima con el color '
    'del mar. Asi el estrecho se sigue viendo, que es lo que hace de esa ciudad '
    'un cuello de botella, y la geometria se queda simple.')
mapa_out['aguas'] = mapa['aguas']
mapa_out['regiones'] = {k: [list(p) for p in v] for k, v in mapa['regiones'].items()}
mapa_out['rotulos'] = mapa['rotulos']
mapa_out['sitios'] = mapa['sitios']
mapa_out['mares'] = mapa['mares']

d = O()
d['_nota'] = alijo['_nota']
d['fecha_inicio'] = alijo['fecha_inicio']
d['region_epicentro'] = alijo['region_epicentro']
d['_puntos'] = (
    'DIEZ puntos, y no veinticuatro. Con cinco decisiones, veinticuatro producian '
    'un tablero que ninguna sala recorria entera: se tocaban ocho o nueve y los '
    'quince restantes eran decorado con nombre propio. Diez caben en una '
    'deliberacion y cada uno tiene consecuencia si se abre. CINCO ESTAN EN LA '
    'CIUDAD EPICENTRO y cinco fuera, que es la tension territorial del caso: lo '
    'que se ve por la ventana contra lo que solo existe en el tablero. Cada punto '
    'esta sobre un vertice de la red vial real, no en un descampado.')
d['_identificadores'] = alijo['_identificadores']
d['regiones'] = regiones
d['_corredores'] = alijo['_corredores']
d['corredores'] = corredores
d['nodos'] = nodos
d['_infraestructura'] = (
    'LA INFRAESTRUCTURA RELEVANTE DEL PAIS, con nombre y con sitio. Existia la '
    'accion de declararla critica y no existia el objeto: DeclararInfraestructuraCritica '
    'recibia una cadena libre --refineria-- que nadie validaba contra nada, de '
    'modo que se podia declarar critica una instalacion inventada y el Ministro '
    'de Minas no tenia en ninguna pantalla la lista de lo que le toca proteger. '
    'NO HAY ACCIONES EN CONTRA DE ESTA INFRAESTRUCTURA, y es deliberado: el '
    'ejercicio no modela un ataque a la refineria, modela la decision de '
    'inmovilizar fuerza para custodiarla, que es la que enfrenta a Minas con '
    'Defensa. Lo que queda es el RIESGO ASUMIDO al dejarla sin proteger, que el '
    'debriefing cobra. La criticidad va en palabra --vital, alta, media-- y nunca '
    'en indice: con un numero, la sala protege por orden descendente sin discutir '
    'de que depende cada cosa.')
d['infraestructura'] = infraestructura
d['_denuncias'] = alijo['_denuncias']
d['denuncias_iniciales'] = alijo['denuncias_iniciales']
# H1 APUNTA A LA INSTALACION POR SU IDENTIFICADOR, no por su nombre. Con el
# nombre escrito a mano, una tilde de diferencia --«Refineria» contra
# «Refinería»-- dejaba la refineria sin marcar como custodiada, y el debriefing
# le imputaba a la sala un riesgo que no habia asumido: esa custodia la puso el
# hecho heredado.
h1 = O(alijo['hecho_h1'])
h1['instalacion'] = 'I-REF'
h1['_nota'] = (h1['_nota'] + ' `instalacion` es un identificador del registro de '
               'infraestructura, no un nombre suelto: el loader falla si no existe.')
d['hecho_h1'] = h1
d['mapa'] = mapa_out

io.open(DESTINO, 'w', encoding='utf-8').write(
    json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('')
print('escrito', DESTINO)
print('  %d puntos · %d corredores · %d regiones · %d instalaciones'
      % (len(nodos), len(corredores), len(regiones), len(infraestructura)))
print('  reparto por region:',
      {r: sum(1 for n in nodos if n['region_id'] == r)
       for r in ('R-BEL', 'R-ESP', 'R-CUM', 'R-VER')})
