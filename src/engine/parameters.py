"""
parameters.py — Todas las constantes del modelo, con nombre y unidad.

Regla heredada de Macondo: si un número gobierna el comportamiento del motor,
vive aquí y en ningún otro sitio. Ningún módulo define constantes propias.

ADVERTENCIA DE CALIBRACIÓN
--------------------------
Ninguno de estos coeficientes está medido. Son convenciones declaradas, elegidas
para que ninguna estrategia pura (solo fuerza / solo mesa) gane. Ver §12.3 de
`docs/propuesta_simulacion_estallido_social.md`. La primera corrida con personas
es una medición, no un ejercicio.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# RELOJ
# ---------------------------------------------------------------------------

TURNOS_DECISION = 5          # turnos de día, con deliberación
HORAS_POR_TURNO = 12         # cada turno cubre media jornada
FECHA_INICIO = "2021-05-11T06:00"

# Minutos de mundo real por fase (el presupuesto de 120 min, §5.8)
MIN_INSTALACION = 12
MIN_TURNO_DECISION = 13
MIN_INTERLUDIO_NOCHE = 3
MIN_DEBRIEFING = 20

TURNOS_PROYECCION_FINAL = 3  # T+72h sin nadie al mando (§5.11)

# ---------------------------------------------------------------------------
# FUERZA — capacidad e incidentes (§4.2)
# ---------------------------------------------------------------------------

ESMAD_ESCUADRONES_TOTALES = 40
ESMAD_DESPLEGADOS_T0 = 34            # solo 6 libres al empezar
FATIGA_MEDIA_T0 = 0.55

FATIGA_POR_TURNO_DESPLEGADO = 0.15
FATIGA_RECUPERADA_EN_RELEVO = 0.30
FATIGA_MAX = 1.0

# Probabilidad base de incidente por tipo de unidad
BASE_INCIDENTE = {
    "esmad": 0.08,       # entrenado y equipado para control de multitudes
    "policia": 0.22,     # no es su función
    "militar": 0.45,     # tropa de combate en control de multitudes
}

FACTOR_NOCTURNO = 1.6

# Techo de la probabilidad de incidente. Con riesgo alto, 1 - e^(-riesgo)
# alcanza 1,0 exacto en coma flotante, y una probabilidad de 1 vuelve la tirada
# irrelevante: no queda ninguna corrida en que la operación temeraria salga
# bien. Siempre queda un margen; una operación puede ser un disparate y aun así
# no terminar mal, que es precisamente por lo que se repiten los disparates.
P_INCIDENTE_MAX = 0.98
MASA_REFERENCIA = 300    # personas; normaliza el término de masa

# Mitigadores multiplicativos. Producto de los seis ≈ 0.214 → divide por ~4,7.
MITIGADORES = {
    "reglas_escritas": 0.70,
    "identificacion_agentes": 0.85,
    "registro_av": 0.80,
    "dupla_presente": 0.75,
    "concertado_con_alcaldia": 0.80,
    "unidades_descansadas": 0.75,   # aplica si fatiga_media < UMBRAL_FATIGA_DESCANSADA
}
UMBRAL_FATIGA_DESCANSADA = 0.30

# Custodia de infraestructura crítica: unidades inmovilizadas por instalación
CUSTODIA_POLICIAS_POR_INSTALACION = 2
CUSTODIA_MILITARES_POR_INSTALACION = 3

# Consecuencias de un incidente
P_VIRAL_SIN_REGISTRO = 0.55      # sin registro audiovisual propio
P_VIRAL_CON_REGISTRO = 0.25
VICTIMAS_ESPERADAS = {"esmad": 0.4, "policia": 0.9, "militar": 2.1}

# ---------------------------------------------------------------------------
# MOVILIZACIÓN — el adversario reflexivo (§4.1)
# ---------------------------------------------------------------------------

INTENSIDAD_MAX = 100.0
INTENSIDAD_NACIONAL_T0 = 61.0

# Incrementos base. Se aplican con rendimientos decrecientes (ver T1 en §12.2):
# el segundo muerto de la semana mueve menos que el primero.
DELTA_INTENSIDAD = {
    "incidente_mortal": 20.0,
    "imagen_viral": 8.0,
    "militares_en_multitudes": 8.0,
    "jornada_nacional": 10.0,
    "turno_sin_acuerdo": 1.5,
    "cifra_desmentida": 4.0,
}
DELTA_INTENSIDAD_NEGATIVO = {
    "acuerdo_verificable": -8.0,
    "turno_sin_incidentes": -2.0,
    "apertura_concertada": -4.0,
    "contraprestacion_tramitada": -6.0,
}

# Rendimientos decrecientes: el n-ésimo evento del mismo tipo vale
# base * DECAIMIENTO_REPETICION ** (n-1)
DECAIMIENTO_REPETICION = 0.6

# Decaimiento proporcional al nivel, no constante: evita que la variable se
# clave en 100 y deje de discriminar.
TASA_DECAIMIENTO_PROPORCIONAL = 0.04

# Realimentación de la intensidad sobre el mundo
NODOS_NUEVOS_POR_INTENSIDAD = 0.04   # nodos nuevos por turno por punto sobre 50
DUREZA_POR_INTENSIDAD = 0.0035       # incremento de dureza por punto sobre 50
MASA_POR_INTENSIDAD = 4.0            # personas por punto de intensidad

# ---------------------------------------------------------------------------
# APERTURA Y REAPERTURA (§4.3)
# ---------------------------------------------------------------------------

TURNOS_APERTURA = {"fuerza": 1, "concertacion": 2, "desgaste": 4}

CAUDAL_APERTURA_FUERZA = (0.70, 1.00)      # rango
CAUDAL_APERTURA_CONCERTACION = 0.90        # se multiplica por control_voceria
CAUDAL_APERTURA_DESGASTE = (0.50, 0.80)

# Reapertura tras apertura por fuerza: turnos hasta reabrir, escalado con intensidad
REAPERTURA_FUERZA_TURNOS_BASE = 2
UMBRAL_APOYO_DESGASTE = 0.25               # apoyo_local por debajo del cual se abre solo
TURNOS_APOYO_BAJO_PARA_DESGASTE = 3        # y sostenido: el desgaste es lento
P_DESGASTE_POR_TURNO = 0.20                # aun cumpliendo todo, no es automático
DESGASTE_POR_ESQUEMA_HUMANITARIO = 0.12    # baja de apoyo_local por turno

# ---------------------------------------------------------------------------
# RESERVAS SISTÉMICAS (§3.4)
# ---------------------------------------------------------------------------

RESERVAS_T0 = {
    "legitimidad": 52.0,
    "credibilidad_mesa": 45.0,
    "exposicion_internacional": 45.0,   # invertida: arriba es peor
    "cohesion_mesa": 68.0,
}

UMBRALES = {
    "legitimidad_gremios_evaluan": 40.0,
    "legitimidad_gremios_se_suman": 25.0,
    "credibilidad_comite_suspende": 30.0,
    "credibilidad_comite_definitivo": 15.0,
    "exposicion_pronunciamientos": 70.0,
    "cohesion_contradicciones": 35.0,
}

COSTO_RESERVAS = {
    # (reserva, delta) por evento
    "incidente_con_victima": {"legitimidad": -9.0, "exposicion_internacional": 7.0},
    "imagen_viral": {"legitimidad": -6.0, "exposicion_internacional": 5.0},
    "cifra_desmentida": {"legitimidad": -4.0},
    "operacion_dia_de_mesa": {"credibilidad_mesa": -12.0},
    "operacion_no_informada": {"cohesion_mesa": -8.0},
    "corredor_humanitario_negado": {"exposicion_internacional": 12.0, "legitimidad": -5.0},
    "acuerdo_verificable_cumplido": {"legitimidad": 5.0, "credibilidad_mesa": 8.0},
    "apertura_concertada": {"legitimidad": 2.0},
    "sin_registro_escrito": {"cohesion_mesa": -8.0},
    "sin_protocolo_voceria": {"cohesion_mesa": -5.0},
    "sin_criterio_priorizacion": {"cohesion_mesa": -3.0},
    "turno_sin_decision": {"legitimidad": -3.0},
    "constitutiva_reactiva": 0.5,   # multiplicador del rédito si se adopta tras incidente
}

# ---------------------------------------------------------------------------
# ABASTECIMIENTO (§4.5)
# ---------------------------------------------------------------------------

CONSUMO_BASE_DIARIO = 1.0            # unidades de autonomía por día

# Cuánto repone un corredor a caudal pleno, por día. DEBE superar el consumo:
# si un corredor abierto al 100 % no alcanza a cubrir el gasto, la región se
# agota pase lo que pase y el reloj deja de ser un dilema para volverse un guion.
CAPACIDAD_CORREDOR_DIARIA = 2.6
FACTOR_PANICO_POR_DIFUSION = 0.35    # sube el consumo si se publica el calendario
UMBRAL_AUTONOMIA_DEGRADA_FUERZA = 1.0  # días; por debajo, la escolta se degrada

# Oxígeno: el único reloj que produce muertes irreversibles
PACIENTES_EN_SOPORTE_POR_REGION = 180
TASA_MUERTE_POR_HORA_SIN_OXIGENO = 0.004

ORDEN_PRIORIDAD_COMBUSTIBLE = [
    "mision_medica", "fuerza_publica", "transporte_alimentos", "consumo_general",
]

# ---------------------------------------------------------------------------
# PLAN Y ACCIONES
# ---------------------------------------------------------------------------

TOPE_ACCIONES_POR_PLAN = 12    # menor que en Macondo: aquí hay 5 turnos, no 288
CADUCIDAD_ORDEN_CONDICIONAL = 3   # turnos

# ---------------------------------------------------------------------------
# ESTIMACIÓN — sesgos por fuente (§4.4)
# ---------------------------------------------------------------------------

# Sesgo aplicado a `estructura_organizada` al estimar la composición de un nodo.
SESGO_FUENTE = {
    "parte_operacional": 0.10,
    "inteligencia_defensa": 0.28,     # sobreestima
    "parte_municipal": -0.22,         # subestima
    "dupla_defensoria": 0.02,         # casi sin sesgo
}
COBERTURA_DUPLAS_POR_TURNO = 3       # nodos que la Defensoría puede verificar

# control_voceria: Interior lo sobreestima; Cali lo estima bien en su jurisdicción
SESGO_CONTROL_VOCERIA = {
    "interior": 0.20,
    "alcalde_cali": 0.03,
    "defensoria": 0.05,
}

# ---------------------------------------------------------------------------
# REPRODUCIBILIDAD
# ---------------------------------------------------------------------------

SEMILLA_POR_DEFECTO = 20210511
