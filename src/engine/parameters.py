"""
parameters.py — Todas las constantes del modelo, con nombre y unidad.

Regla heredada de Macondo: si un número gobierna el comportamiento del motor,
vive aquí y en ningún otro sitio. Ningún módulo define constantes propias.

ADVERTENCIA DE CALIBRACIÓN
--------------------------
Ninguno de estos coeficientes está medido. Son convenciones declaradas, elegidas
para que ninguna estrategia pura (solo fuerza / solo mesa) gane. Ver §12.3 de
`docs/historial/propuesta_inicial.md`. La primera corrida con personas
es una medición, no un ejercicio.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# RELOJ
# ---------------------------------------------------------------------------

TURNOS_DECISION = 5          # turnos de día, con deliberación
HORAS_POR_TURNO = 12         # cada turno cubre media jornada
FECHA_INICIO = "2021-05-11T06:00"

# Minutos de mundo real por fase (el presupuesto de 120 min, §6.2 de la v2)
MIN_PARTE_PRIVADO = 1
MIN_INSTALACION = 12
MIN_TURNO_DECISION = 13
MIN_INTERLUDIO_NOCHE = 3
MIN_DEBRIEFING = 20

TURNOS_PROYECCION_FINAL = 3  # T+72h sin nadie al mando

# ---------------------------------------------------------------------------
# FUERZA — capacidad e incidentes
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

# Techo de la probabilidad de incidente. Una operación puede ser un disparate y
# aun así no terminar mal, que es precisamente por lo que se repiten.
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

# Concentrar el ESMAD: cuántos escuadrones se pueden traer de la contención
# estática por turno, y qué cuesta en puntos secundarios descubiertos.
ESMAD_CONCENTRABLE_POR_TURNO = 8
NODOS_CONSOLIDADOS_POR_REPLIEGUE = 2   # puntos que se endurecen al replegar

# Escolta: cada misión inmoviliza escuadrones durante el turno
ESCUADRONES_POR_ESCOLTA = 2
REPOSICION_POR_ESCOLTA = 1.1      # días de autonomía que entrega una escolta lograda
P_ESCOLTA_ATACADA_BASE = 0.12     # sube con la intensidad de la región

# Consecuencias de un incidente
P_VIRAL_SIN_REGISTRO = 0.55      # sin registro audiovisual propio
P_VIRAL_CON_REGISTRO = 0.25
VICTIMAS_ESPERADAS = {"esmad": 0.4, "policia": 0.9, "militar": 2.1}

# ---------------------------------------------------------------------------
# LA MEZCLA REAL DE UN PUNTO — decisión de diseño nº 1 (P1 de la v2)
# ---------------------------------------------------------------------------
#
# Hasta la v2 `composicion_real` estaba protegida por una invariante y no entraba
# en ningún cálculo: daba igual operar sobre protesta pura o sobre estructura
# organizada. Se conecta por DOS vías y solo dos:
#
#   1 · operar sobre un punto mayoritariamente de protesta legítima cuesta más
#   2 · concertar donde hay estructura organizada produce un acuerdo que se rompe
#
# Nada más. La verdad sigue sin salir nunca del motor.

# Costo de operar sobre población civil. Un punto con 90 % de protesta legítima
# cuesta 1,8 veces lo que uno con 50 %.
UMBRAL_PROTESTA_CIVIL = 0.50
MULTIPLICADOR_COSTO_PROTESTA = 2.0

# Un acuerdo pactado donde hay estructura organizada se incumple: no controla el
# punto quien lo firmó. P = estructura_organizada × este factor.
FACTOR_INCUMPLIMIENTO_POR_ESTRUCTURA = 1.5

# ---------------------------------------------------------------------------
# MOVILIZACIÓN — el adversario reflexivo
# ---------------------------------------------------------------------------

INTENSIDAD_MAX = 100.0
INTENSIDAD_NACIONAL_T0 = 61.0

# Incrementos base, con rendimientos decrecientes: el segundo muerto de la semana
# mueve menos que el primero.
DELTA_INTENSIDAD = {
    "incidente_mortal": 20.0,
    "imagen_viral": 8.0,
    "militares_en_multitudes": 8.0,
    "jornada_nacional": 10.0,
    "turno_sin_acuerdo": 1.5,
    "cifra_desmentida": 4.0,
    "acuerdo_incumplido": 6.0,
    "escolta_atacada": 7.0,
}
DELTA_INTENSIDAD_NEGATIVO = {
    "acuerdo_verificable": -8.0,
    "turno_sin_incidentes": -2.0,
    "apertura_concertada": -4.0,
    "contraprestacion_tramitada": -6.0,
    "denuncia_desmentida": -3.0,
}

DECAIMIENTO_REPETICION = 0.6
TASA_DECAIMIENTO_PROPORCIONAL = 0.04

# Realimentación de la intensidad sobre el mundo
NODOS_NUEVOS_POR_INTENSIDAD = 0.04   # nodos nuevos por turno por punto sobre 50
DUREZA_POR_INTENSIDAD = 0.0035       # incremento de dureza por punto sobre 50
MASA_POR_INTENSIDAD = 4.0            # personas por punto de intensidad

# La jornada nacional de movilización, programada en el calendario
TURNO_JORNADA_NACIONAL = 3

# ---------------------------------------------------------------------------
# APERTURA Y REAPERTURA
# ---------------------------------------------------------------------------

TURNOS_APERTURA = {"fuerza": 1, "concertacion": 2, "desgaste": 4}

CAUDAL_APERTURA_FUERZA = (0.70, 1.00)      # rango
CAUDAL_APERTURA_CONCERTACION = 0.90        # se multiplica por control_voceria
CAUDAL_APERTURA_DESGASTE = (0.50, 0.80)

REAPERTURA_FUERZA_TURNOS_BASE = 2
UMBRAL_APOYO_DESGASTE = 0.25
TURNOS_APOYO_BAJO_PARA_DESGASTE = 3
P_DESGASTE_POR_TURNO = 0.20
DESGASTE_POR_ESQUEMA_HUMANITARIO = 0.12

# ---------------------------------------------------------------------------
# RESERVAS SISTÉMICAS
# ---------------------------------------------------------------------------
#
# CAMBIO DE LA v2: la «exposición internacional» estaba invertida —arriba era
# peor— y obligaba a explicar el tablero. Pasa a ser RESPALDO INTERNACIONAL:
# las cuatro reservas se leen igual, arriba es mejor.

RESERVAS_T0 = {
    "legitimidad": 52.0,
    "credibilidad_mesa": 45.0,
    "respaldo_internacional": 55.0,     # antes exposicion 45, invertida
    "cohesion_mesa": 68.0,
}

UMBRALES = {
    "legitimidad_gremios_evaluan": 40.0,
    "legitimidad_gremios_se_suman": 25.0,
    "credibilidad_comite_suspende": 30.0,
    "credibilidad_comite_definitivo": 15.0,
    "respaldo_pronunciamientos": 30.0,   # por DEBAJO de 30 hay pronunciamientos
    "cohesion_contradicciones": 35.0,
}

COSTO_RESERVAS = {
    "incidente_con_victima": {"legitimidad": -9.0, "respaldo_internacional": -7.0},
    "imagen_viral": {"legitimidad": -6.0, "respaldo_internacional": -5.0},
    "cifra_desmentida": {"legitimidad": -4.0},
    "operacion_dia_de_mesa": {"credibilidad_mesa": -12.0},
    "operacion_no_informada": {"cohesion_mesa": -8.0},
    "corredor_humanitario_negado": {"respaldo_internacional": -12.0, "legitimidad": -5.0},
    "acuerdo_verificable_cumplido": {
        "legitimidad": 5.0, "credibilidad_mesa": 8.0, "cohesion_mesa": 3.0,
    },
    "acuerdo_incumplido": {"credibilidad_mesa": -10.0, "legitimidad": -3.0},
    "apertura_concertada": {"legitimidad": 2.0},
    "sin_registro_escrito": {"cohesion_mesa": -8.0},
    "sin_protocolo_voceria": {"cohesion_mesa": -5.0},
    "sin_criterio_priorizacion": {"cohesion_mesa": -3.0},
    "turno_sin_decision": {"legitimidad": -3.0},
    "decision_con_responsable": {"cohesion_mesa": 2.0},
    "escolta_lograda": {"legitimidad": 3.0},
    "escolta_atacada": {"legitimidad": -6.0, "respaldo_internacional": -4.0},
    "denuncia_veraz_confirmada": {"respaldo_internacional": -6.0, "legitimidad": -3.0},
    "denuncia_falsa_desmentida": {"legitimidad": 3.0, "credibilidad_mesa": 2.0},
    "defensoria_duda_permanencia": {"legitimidad": -7.0, "respaldo_internacional": -9.0},
    "constitutiva_reactiva": 0.5,   # multiplicador del rédito si se adopta tras incidente
}

# La cohesión se cobra SOLO en turnos de decisión. Cobrarla también de noche y en
# la proyección la convertía en una rampa determinista de 12 peajes en 5
# decisiones: bajaba igual hiciera lo que hiciera la sala.
COBRAR_BANDERAS_SOLO_DE_DIA = True

# Tope de la duda de permanencia: la credibilidad de la Defensoría se consume.
# El n-ésimo pronunciamiento vale base × este factor ** (n-1).
DECAIMIENTO_DUDA_PERMANENCIA = 0.45

# ---------------------------------------------------------------------------
# ABASTECIMIENTO
# ---------------------------------------------------------------------------

CONSUMO_BASE_DIARIO = 1.0            # unidades de autonomía por día

# Cuánto repone un corredor a caudal pleno, por día. DEBE superar el consumo: si
# un corredor abierto al 100 % no cubre el gasto, la región se agota pase lo que
# pase y el reloj deja de ser un dilema para volverse un guion.
CAPACIDAD_CORREDOR_DIARIA = 2.6
FACTOR_PANICO_POR_DIFUSION = 0.35
UMBRAL_AUTONOMIA_DEGRADA_FUERZA = 1.0

# Oxígeno: el único reloj que produce muertes irreversibles
PACIENTES_EN_SOPORTE_POR_REGION = 180
TASA_MUERTE_POR_HORA_SIN_OXIGENO = 0.0022
# La presión hospitalaria modula el contador: una red al 92 % de ocupación no
# absorbe lo mismo que una al 74 %. Antes era un dato del escenario que ningún
# cálculo leía.
PRESION_HOSPITALARIA_MODULA_MUERTES = True

ORDEN_PRIORIDAD_COMBUSTIBLE = [
    "mision_medica", "fuerza_publica", "transporte_alimentos", "consumo_general",
]
# Cuánta autonomía mueve la prioridad de combustible, POR DÍA.
#
# Es un criterio PERMANENTE, no una decisión de un turno: mientras esté fijado,
# se aplica en cada paso. Es la segunda entrada del reloj y la única que Minas
# controla por sí solo — y es suma cero: lo que se pone en misión médica sale
# del transporte de alimentos, y las dos cosas tienen quien las reclame.
EFECTO_ASIGNACION_COMBUSTIBLE = 0.85

# ---------------------------------------------------------------------------
# INFORMACIÓN — sesgos, duplas y denuncias
# ---------------------------------------------------------------------------

# Sesgo aplicado a `estructura_organizada` al estimar la mezcla de un punto.
SESGO_FUENTE = {
    "parte_operacional": 0.10,
    "inteligencia_defensa": 0.28,     # sobreestima
    "parte_municipal": -0.22,         # subestima
    "dupla_defensoria": 0.02,         # casi sin sesgo
}

# UN SOLO BOLSILLO DE TRES (decisión V6 de la v2). Verificar un punto, verificar
# una denuncia y acompañar una operación salen del mismo presupuesto, y cada
# dupla hace UNA sola cosa por turno. Antes acompañar salía gratis y la
# asignación de la Defensoría no era una decisión.
DUPLAS_TOTALES = 3

# control_voceria: Interior lo sobreestima; Cali lo estima bien en su jurisdicción
SESGO_CONTROL_VOCERIA = {
    "interior": 0.20,
    "alcalde_cali": 0.03,
    "defensoria": 0.05,
}

# Denuncias sin verificar: cada cuánto aparece un par nuevo, y con qué
# probabilidad crece con la intensidad. NUNCA una sola: siempre al menos dos,
# con veracidad distinta y sin ninguna señal que las distinga.
DENUNCIAS_POR_PAQUETE = 2
P_PAQUETE_DENUNCIAS_BASE = 0.15       # por turno, más el exceso de intensidad
TURNOS_DENUNCIA_SIN_VERIFICAR_ESTALLA = 2

# ---------------------------------------------------------------------------
# CONCERTACIÓN Y GREMIOS
# ---------------------------------------------------------------------------

# La mesa nacional necesita al Comité disponible; produce un acuerdo verificable
# que la sala tiene que cumplir en el turno siguiente o pagarlo.
TURNOS_PARA_CUMPLIR_ACUERDO = 2
CAUDAL_ACUERDO_NACIONAL = 0.35        # cuánto abre un acuerdo nacional en cada punto pactado
NODOS_POR_ACUERDO_NACIONAL = 3

# Contraprestación legislativa: baja la intensidad, y si no se tramita, cuesta
P_CONGRESO_RESPONDE = 0.6

# Gremios: el ultimátum del turno 1 es un disparador independiente del umbral
TURNO_ULTIMATUM_GREMIOS = 1
TURNOS_PLAZO_ULTIMATUM = 2

# ---------------------------------------------------------------------------
# PLAN Y ACCIONES
# ---------------------------------------------------------------------------

TOPE_ACCIONES_POR_PLAN = 12    # menor que en Macondo: aquí hay 5 turnos, no 288
CADUCIDAD_ORDEN_CONDICIONAL = 3   # turnos

# ---------------------------------------------------------------------------
# REPRODUCIBILIDAD
# ---------------------------------------------------------------------------
#
# La semilla queda registrada para poder repetir la corrida en el debriefing con
# una decisión cambiada. NO es un elemento visible de la interfaz (decisión A6).

SEMILLA_POR_DEFECTO = 20210511
