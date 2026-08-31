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

TURNOS_DECISION = 5          # jornadas de día, con deliberación
HORAS_POR_TURNO = 12         # cada ventana del motor cubre media jornada
FECHA_INICIO = "2021-05-11T06:00"

# Cinco jornadas del 11 al 15 de mayo. Cada una tiene DOS ventanas de motor —día
# y noche— y de ahí que el ejercicio tenga nueve y no cinco: cinco de decisión y
# cuatro interludios que se sufren.
#
# El reloj se calcula en `Estado.reloj()` y no en la interfaz. Un reloj calculado
# en cada pantalla es un reloj por pantalla, y en una sala con diez pantallas eso
# se nota el primer turno.
VENTANAS_TOTALES = TURNOS_DECISION * 2 - 1   # 5 días + 4 noches

# ---------------------------------------------------------------------------
# EL RELOJ DE SALA — dos partes por jornada, y solo dos
# ---------------------------------------------------------------------------
#
# La jornada dura quince minutos de mundo real y se parte en dos tramos con
# reglas OPUESTAS. No hay fases intermedias: siete fases obligaban a la sala a
# saber en cuál estaba antes de poder hablar, y la única distinción que cambia
# lo que se puede hacer es esta.
#
#     DÍA    13 min   se lee, se discute y SE ORDENA, en cualquier momento
#     NOCHE   2 min   se resuelve y se mira. NO SE RECIBEN ÓRDENES
#
# Que la noche no admita órdenes no es una convención de guion: la consola se
# apaga sola y el servidor rechaza lo que llegue. Una regla que el software
# garantiza vale más que una que el software recomienda.
MIN_DIA = 13.0
MIN_NOCHE = 2.0
MIN_JORNADA = MIN_DIA + MIN_NOCHE      # 15 min · ×5 jornadas = 75 min de mesa

MIN_INSTALACION = 12
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
    "concertado_con_alcaldia": 0.80,
    "unidades_descansadas": 0.75,   # aplica si fatiga_media < UMBRAL_FATIGA_DESCANSADA
}
UMBRAL_FATIGA_DESCANSADA = 0.30

# Custodia de infraestructura crítica: unidades inmovilizadas por instalación
CUSTODIA_POLICIAS_POR_INSTALACION = 2
CUSTODIA_MILITARES_POR_INSTALACION = 3

# ---------------------------------------------------------------------------
# EL RIESGO DE INFRAESTRUCTURA — se acumula callado, se cobra en el debriefing
# ---------------------------------------------------------------------------
#
# NO HAY ACCIONES EN CONTRA DE LA INFRAESTRUCTURA, y es deliberado: el ejercicio
# no simula un ataque a la refinería. Lo que simula es la decisión de inmovilizar
# fuerza para custodiarla, que es la que enfrenta al Interior con Defensa — proteger
# resta exactamente de la capacidad de desbloquear.
#
# Pero una decisión que no cuesta nada tampoco es una decisión. Lo que se cobra
# es **el riesgo asumido**: cada jornada que una instalación pasa sin custodia
# suma exposición, ponderada por lo que depende de ella. No produce ningún
# evento durante la corrida —la sala no puede jugar contra este número porque no
# lo ve moverse— y sale entero al cierre, que es donde se responde de él.
#
#     Un riesgo que se materializa es un guion. Un riesgo que se nombra al
#     final es una conversación sobre lo que se decidió no hacer.
PESO_CRITICIDAD = {"vital": 3.0, "alta": 2.0, "media": 1.0}

# Por encima de esto, la exposición acumulada se reporta como grave. Es un corte
# para redactar el cierre, no un umbral que produzca nada durante la corrida.
EXPOSICION_INFRA_GRAVE = 40.0

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

# Y la probabilidad de que una mesa técnica rural termine reconociéndole
# interlocución al Estado a quien no es una comunidad. Misma forma que el de
# arriba —P = estructura_organizada × factor— y por la misma razón: un umbral
# fijo aquí sería código muerto. Medido sobre el escenario, la estructura real
# de los puntos rurales va de 0,04 a 0,12, de modo que esto es una cola del 6 %
# al 18 %: un riesgo que se corre, no un peaje que se paga.
FACTOR_LEGITIMAR_ESTRUCTURA = 1.5

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
MASA_POR_INTENSIDAD = 4.0            # personas por punto de intensidad...
# ...en un punto DE TAMAÑO DE REFERENCIA. La masa de cada cierre se escala desde
# su `masa_base`, así que un peaje de 180 y una glorieta de 420 no crecen igual
# con la misma intensidad regional. Antes no se escalaba nada: todos los puntos
# de una región tenían siempre la misma cifra exacta de personas.
MASA_BASE_REFERENCIA = 200
# De noche hay menos gente en la calle. Era un segundo valor absoluto (120 frente
# a 200) que no seguía al tamaño del punto; ahora es una fracción del propio.
MASA_FACTOR_NOCTURNO = 0.6

# La jornada nacional de movilización, programada en el calendario
TURNO_JORNADA_NACIONAL = 3

# ---------------------------------------------------------------------------
# APERTURA Y REAPERTURA
# ---------------------------------------------------------------------------

TURNOS_APERTURA = {"fuerza": 1, "concertacion": 2, "desgaste": 4}

CAUDAL_APERTURA_FUERZA = (0.70, 1.00)      # rango
CAUDAL_APERTURA_CONCERTACION = 0.90        # se multiplica por control_voceria
CAUDAL_APERTURA_DESGASTE = (0.50, 0.80)

# Cuántos PASOS del motor —no jornadas— tiene que llevar abierto por la fuerza
# un punto antes de poder volver a cerrarse. Con 1, la reapertura ocurre la
# primera noche, que es lo que el caso dice y lo que el motor ya hacía.
#
# Antes esto se llamaba `REAPERTURA_FUERZA_TURNOS_BASE = 2` y **no lo leía
# nadie**: el código comparaba contra un 1 escrito a mano. Quien calibrara
# moviendo el 2 no habría cambiado nada, y habría creído que sí. El nombre dice
# ahora en qué unidad cuenta, porque contaba pasos y decía turnos.
PASOS_ANTES_DE_REABRIR = 1
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
    # LAS CUATRO SALIDAS DE VERIFICAR UNA DENUNCIA, y son cuatro y no dos desde
    # que el que verifica es el sector del que se denuncia. Lo que separa cada
    # par es si hay protocolo común de verificación adoptado: sin él, la mesa
    # está oyendo a una parte hablar de su propia conducta.
    #
    # Documentar la propia falta DENTRO del protocolo sigue saliendo más barato
    # que el estallido; fuera de él no ahorra nada. Y desmentir sin protocolo no
    # da credibilidad —se lee como una absolución— aunque sigue evitando que se
    # desplace fuerza a algo que no pasó, que es lo que conserva la legitimidad.
    "denuncia_veraz_confirmada": {"respaldo_internacional": -6.0, "legitimidad": -3.0},
    "denuncia_veraz_sin_protocolo": {"respaldo_internacional": -11.0, "legitimidad": -7.0},
    "denuncia_falsa_desmentida": {"legitimidad": 3.0, "credibilidad_mesa": 2.0},
    "denuncia_falsa_sin_protocolo": {"legitimidad": 1.0},
    # EL PRECIO DE ATARSE LAS MANOS UNO MISMO. El estandar completo lo pedia un
    # tercero y lo concedia el Gobierno; sin ese rol lo adopta el propio sector,
    # y encender los tres mitigadores el primer dia sin costo desequilibraria el
    # ejercicio entero. Gana respaldo fuera y cuesta cohesion dentro, que es lo
    # que se paga cuando quien manda la fuerza se limita delante de la mesa.
    #
    # SIN CALIBRAR: los dos numeros son provisionales y salen de C5.
    "estandar_autoimpuesto": {"respaldo_internacional": 8.0, "cohesion_mesa": -6.0},
    "constitutiva_reactiva": 0.5,   # multiplicador del rédito si se adopta tras incidente
    # --- el frente agroalimentario ---
    # Reordenar un criterio de priorización que la mesa ya adoptó no es lo mismo
    # que llegar antes de que exista: en el primer caso hay un ministro que ve
    # deshacerse su propio orden delante de todos.
    "clase_alimentaria_sobre_criterio": {"cohesion_mesa": -5.0},
    "clase_alimentaria": {"cohesion_mesa": -2.0},
    # La mesa técnica rural es un segundo canal. Cuando el Interior tiene una
    # vocería única fijada o un acuerdo nacional vivo, abrirlo se lo quita.
    "canal_rural_paralelo": {"cohesion_mesa": -4.0},
    # Publicar la pérdida traslada el costo del cierre a la población: gana
    # legitimidad y le entrega a quien pide mano dura su mejor argumento.
    "balance_perdida_publicado": {"legitimidad": 2.0, "cohesion_mesa": -3.0},
    "cifra_sectorial_disputada": {"credibilidad_mesa": -5.0},
    "cifra_sectorial_verificada": {"respaldo_internacional": 2.0},
    # Un esquema de cupos produce ganadores y perdedores entre productores, y
    # hace rendir la escolta que ya está puesta.
    "acopio_por_cupos": {"legitimidad": -2.0, "cohesion_mesa": 2.0},
}

# La cohesión se cobra SOLO en turnos de decisión. Cobrarla también de noche y en
# la proyección la convertía en una rampa determinista de 12 peajes en 5
# decisiones: bajaba igual hiciera lo que hiciera la sala.
COBRAR_BANDERAS_SOLO_DE_DIA = True

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
# se aplica en cada paso. Es la segunda entrada del reloj y la única que Transporte
# controla por sí solo — y es suma cero: lo que se pone en misión médica sale
# del transporte de alimentos, y las dos cosas tienen quien las reclame.
EFECTO_ASIGNACION_COMBUSTIBLE = 0.85

# ---------------------------------------------------------------------------
# EL FRENTE AGROALIMENTARIO
#
# La cartera de Agricultura no tiene fuerza ni corredores: TODO lo que hace pasa
# por lo que otro despeja o acompaña. Sus cinco números son, por eso, pequeños:
# lo que aporta no es capacidad, es criterio y una interlocución que nadie más
# tiene. Si aquí las cifras fueran generosas, el rol resolvería solo lo que el
# caso quiere que se negocie en la mesa.
# ---------------------------------------------------------------------------

# Lo que la excepción sanitaria y los alivios devuelven de autonomía alimentaria
# a una región. Media jornada: mitiga, no compensa. La ficha del rol lo dice —
# los instrumentos no alcanzan a la escala del daño— y el número tiene que
# decirlo también.
ALIVIO_ALIMENTOS_POR_INSTRUMENTOS = 0.5

# Cuánto baja el apoyo al cierre un paquete de alivios en la región donde cae.
# Menos que el esquema humanitario municipal del Alcalde (0,12), porque el
# alivio llega al productor y no al barrio que sostiene el punto.
ALIVIO_APOYO_POR_INSTRUMENTOS = 0.06

# Y CADA PAQUETE SIGUIENTE EN LA MISMA REGIÓN RINDE LA MITAD. No es una regla
# de juego: es el hallazgo de la ficha —«un alivio parcial puede leerse como
# insuficiente y alimentar nueva movilización rural»— puesto en un número. Sin
# esto, repetir la misma acción cinco jornadas apagaba el frente rural entero.
DECAIMIENTO_ALIVIO_SECTORIAL = 0.5

# Lo que entrega un despacho concentrado por una ventana ya escoltada, frente al
# 0,6 de una caravana normal. Concentrar el acopio hace rendir la misma escolta:
# ese es el aporte real del rol al frente logístico, y es cooperativo — necesita
# que la Policía haya puesto la escolta y que el corredor lleve carga alimentaria.
ACOPIO_CONCENTRADO = 1.1

# El respaldo internacional que cuesta sentarse en un punto donde quien sostiene
# el cierre es una estructura organizada y no una comunidad. Es el riesgo propio
# de su acción de mesa, y nadie en la sala puede saber de antemano si lo corre:
# la mezcla real de un punto es capa 1.
COSTO_LEGITIMAR_ESTRUCTURA = 6.0

# ---------------------------------------------------------------------------
# INFORMACIÓN — sesgos, equipos de terreno y denuncias
# ---------------------------------------------------------------------------

# Sesgo aplicado a `estructura_organizada` al estimar la mezcla de un punto.
SESGO_FUENTE = {
    "parte_operacional": 0.10,
    "inteligencia_defensa": 0.28,     # sobreestima
    "parte_municipal": -0.22,         # subestima
    # IR AL TERRENO CORRIGE, NO LIMPIA. Cuando esto lo hacía la Defensoría del
    # Pueblo el sesgo era 0,02 —la única lectura limpia del ejercicio— porque
    # quien miraba no respondía ante quien operaba. Ahora los equipos son del
    # mismo ministerio que ordena la operación: bajan a menos de la mitad del
    # +0,28 que tiene la inteligencia desde el escritorio, y siguen tirando hacia
    # arriba, que es la dirección que justifica escalar.
    "equipo_terreno": 0.12,
    # AGRICULTURA SUBESTIMA LA ESTRUCTURA ARMADA EN EL CAMPO. Lleva años
    # tratando con esas organizaciones y las conoce como interlocutoras, así que
    # lee de menos lo que pueda haber detrás de ellas.
    #
    # Y AQUÍ ESTÁ LA PARTE INCÓMODA, que es la del caso: MEDIDO CONTRA EL
    # ESCENARIO, EN EL CAMPO ELLA ACIERTA CASI SIEMPRE. La estructura real de
    # los cinco puntos rurales va de 0,04 a 0,12; la inteligencia de Defensa los
    # lee entre 0,33 y 0,42. El que se equivoca de largo en el campo es el
    # frente de seguridad, y ella no tiene con qué demostrarlo. ANTES SÍ HABÍA
    # CON QUÉ: una dupla de la Defensoría del Pueblo leía sin sesgo, y era el
    # árbitro posible de esa discusión. Desde que los equipos de terreno son del
    # propio Ministerio de Defensa, la lectura que la contradice y la que la
    # arbitraría vienen de la misma casa.
    #
    # Su exposición no es equivocarse en general: es el punto concreto donde sí
    # se equivoca. Sentarse ahí le reconoce interlocución a quien sostiene el
    # cierre con otra cosa, y eso se paga fuera.
    "interlocucion_rural": -0.10,     # subestima, y en el campo suele acertar
}

# UN SOLO BOLSILLO DE TRES. Verificar un punto y verificar una denuncia salen
# del mismo presupuesto, y cada equipo hace UNA sola cosa por turno.
#
# Eran tres usos y son dos: acompañar una operación salía de aquí mientras el
# acompañamiento era de un tercero y descontaba riesgo. Desde que los equipos son
# del mismo ministerio que opera, acompañarse a sí mismo no mitiga nada, así que
# ni gasta bolsillo ni lo ahorra.
EQUIPOS_TERRENO_TOTALES = 3

# control_voceria: Interior lo sobreestima; Cali lo estima bien en su jurisdicción
SESGO_CONTROL_VOCERIA = {
    "interior": 0.20,
    "alcalde_cali": 0.03,
    "defensoria": 0.05,
    # En el campo sí sabe quién manda: es su interlocución de años y casi no se
    # equivoca. Lo que no ve es QUIÉN ESTÁ DETRÁS de quien manda, y eso es el
    # otro sesgo, el de arriba.
    "agricultura": 0.06,
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

# ---------------------------------------------------------------------------
# LAS BANDAS DEL MAPA — de un número interno a una palabra que se dice en voz alta
# ---------------------------------------------------------------------------
#
# El mapa proyectado da SEIS lecturas por punto y las mismas seis promediadas por
# región. Ninguna sale como el número crudo del motor, y no es adorno:
#
#     Un nivel se interpreta. Un número se optimiza.
#
# Es la misma regla de las métricas del tablero (`Medidor`), aplicada al
# territorio. Con «control_voceria 0,68» proyectado en la pared, la sala compara
# decimales entre puntos y elige el máximo; con «vocería reconocida» tiene que
# decidir qué hace con eso.
#
# LOS CORTES DEL CAUDAL SON LOS DEL MOTOR, no unos propios: 0,05 es el umbral de
# `Nodo.abierto` y 0,60 el de `_estado_punto`. Si el mapa se inventara los suyos,
# habría puntos rotulados «cerrado» con el chip en «parcial», y la sala
# discutiría sobre la interfaz en vez de sobre el país.
#
# Cada banda es `(tope_exclusivo, palabra)` y se evalúa en orden.

BANDAS_CAUDAL = (
    (0.05, "cerrado"),          # == Nodo.abierto
    (0.25, "goteo"),
    (0.60, "paso parcial"),     # == _estado_punto: por encima de aquí, «abierto»
    (0.85, "casi normal"),
    (1.01, "abierto"),
)

BANDAS_DUREZA = (
    (0.20, "muy blando"), (0.40, "blando"), (0.60, "medio"),
    (0.80, "duro"), (1.01, "muy duro"),
)

BANDAS_APOYO = (
    (0.20, "muy bajo"), (0.40, "bajo"), (0.60, "medio"),
    (0.80, "alto"), (1.01, "muy alto"),
)

# TRES BANDAS Y NO CINCO, a propósito. El control de la vocería es el dato
# exclusivo de Interior y del Alcalde, y sus lecturas van sesgadas +0,20 y +0,03
# (`SESGO_CONTROL_VOCERIA`). Con cinco bandas de 0,20 el sesgo de Interior sería
# exactamente un peldaño y el tablero lo desmentiría solo; con tres, la banda
# gruesa coincide casi siempre y **la discrepancia sigue siendo cosa de la mesa.**
# El grano fino —«controla el 0,62 según mi parte»— sigue viviendo en su vista.
BANDAS_VOCERIA = (
    (0.34, "sin vocería clara"), (0.67, "vocería parcial"), (1.01, "vocería reconocida"),
)

BANDAS_MASA = (
    (150, "poca gente"), (400, "concurrido"),
    (900, "muy concurrido"), (10 ** 9, "multitudinario"),
)

BANDAS_DIAS_SOSTENIDO = (
    (3, "reciente"), (8, "asentado"), (15, "enquistado"), (10 ** 9, "crónico"),
)

# Cuántos de los puntos de una región están cerrados. Es el «estado de bloqueo»
# que colorea el mapa al nivel de país, y NO es el semáforo de abastecimiento:
# una región puede estar despejada y quedarse sin oxígeno porque su corredor
# empieza en otra. Que sean dos colores distintos es el punto.
BANDAS_BLOQUEO = (
    (0.001, "despejada"), (0.34, "cierres puntuales"),
    (0.67, "parcialmente bloqueada"), (1.01, "bloqueada"),
)

# La masa presente se redondea antes de mostrarse: 337 se dice «unas 340». Dos
# cifras significativas dan un error relativo constante —5 % en el peor caso—,
# que es como se comporta de verdad una estimación de aforo. Por debajo de veinte
# se cuenta entero: ahí ya no es una multitud sino un grupo.
CIFRAS_MASA = 2
MASA_SE_CUENTA_ENTERA = 20
