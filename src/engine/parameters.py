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

# LOS MINUTOS DE INSTALACIÓN Y DEBRIEFING SE FUERON A LA GUÍA DEL FACILITADOR.
# `MIN_INSTALACION = 12` y `MIN_DEBRIEFING = 20` vivían aquí sin que ningún
# cálculo del motor los leyera: el reloj del ejercicio solo conduce las cinco
# jornadas. Una constante que nadie lee se documenta, se calibra y se discute
# como si moviera algo — y estas dos son del cuadro de tiempos de la sesión, que
# es material de sala y no de motor.

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

# Mitigadores multiplicativos. Producto de los cuatro ≈ 0.288 → divide por ~3,5.
#
# ERAN CINCO Y SON CUATRO: `identificacion_agentes` (0,85) se fundió en
# `reglas_escritas`. No era una decisión aparte —ninguna acción la encendía sola
# y ningún cálculo la consultaba fuera de este diccionario—, así que era un
# factor multiplicativo que solo aparecía acompañado. El producto se conserva:
#
#     antes   0,70 × 0,85 = 0,595
#     ahora   0,60
#
# Las otras dos del estándar SÍ tienen vida propia y por eso siguen separadas:
# `reglas_escritas` la enciende también la firma delimitada de la asistencia
# militar, y `registro_av` tiene un segundo efecto distinto —baja la
# probabilidad de que la imagen circule, ver P_VIRAL_*.
MITIGADORES = {
    "reglas_escritas": 0.60,        # reglas escritas E IDENTIFICACIÓN de agentes
    "registro_av": 0.80,
    "concertado_con_alcaldia": 0.80,
    "unidades_descansadas": 0.75,   # aplica si fatiga_media < UMBRAL_FATIGA_DESCANSADA
}
UMBRAL_FATIGA_DESCANSADA = 0.30

# Custodia de infraestructura crítica: unidades inmovilizadas por instalación.
#
# LA GEMELA MILITAR SE FUE. `CUSTODIA_MILITARES_POR_INSTALACION = 3` no la leía
# nadie: el redespliegue militar inmoviliza POR UNIDAD y no por instalación. Que
# la custodia militar pase a costar por instalación como la policial es una
# decisión de diseño que cambia la aritmética que enfrenta al Interior con
# Defensa, y mientras no se tome, la constante no debe existir.
CUSTODIA_POLICIAS_POR_INSTALACION = 2

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

# LOS QUE BAJAN LA INTENSIDAD, Y DECAEN IGUAL QUE LOS QUE LA SUBEN.
#
# Estaban exentos, con este argumento escrito: «un acuerdo verificable no vale
# menos por ser el segundo». Suena bien y era el agujero central del motor.
# Mientras los eventos malos se amortiguaban y los buenos no, **repetir la misma
# buena noticia era un sumidero infinito de intensidad**: seis sesiones de mesa
# nacional en una jornada bajaban la presión de 61 a 36, y en cinco jornadas la
# dejaban en cero con las cuatro reservas al techo.
#
# El argumento de la exención tampoco se sostiene fuera del motor: la sexta
# sesión de la mesa nacional en un mismo día NO desinfla la calle como la
# primera, exactamente igual que el sexto muerto no la enciende como el primero.
# Es la misma saturación de atención, y va en las dos direcciones.
#
# `turno_sin_incidentes` se retiró de la tabla: no lo registraba nadie —era una
# huérfana escondida entre claves vivas— y lo que decía que hacía ya lo hace
# `TASA_DECAIMIENTO_PROPORCIONAL`, que es una sola regla en vez de dos.
DELTA_INTENSIDAD_NEGATIVO = {
    "acuerdo_verificable": -8.0,
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
# LO QUE ESTABA ESCRITO A MANO DENTRO DE LAS ACCIONES
# ---------------------------------------------------------------------------
#
# Nueve umbrales y factores vivían dentro de la acción que los usaba, y dos de
# ellos estaban COPIADOS en varios roles a la vez. El peor era el de la
# fragilidad: la misma regla de diseño escrita tres veces —Interior, Alcalde y
# Agricultura—, de modo que cambiarla exigía acordarse de las tres y nada
# avisaba si se cambiaba en dos.
#
# Las tres mesas siguen siendo tres acciones distintas con su jurisdicción y su
# contraparte. Lo que comparten ahora es el número, que es una regla del mundo y
# no una capacidad de rol.

# Lo que queda del caudal cuando el acuerdo sale frágil: quien firmó no manda
# sobre quien sostiene el cierre. Lo leen las tres mesas.
CAUDAL_RESTANTE_ACUERDO_FRAGIL = 0.40

# Vocería mínima para que haya con quién acordar un paso o una mesa técnica.
# Por debajo de esto no manda nadie reconocible. La leen Transporte (pasos
# seguros) y Agricultura (mesa técnica rural).
VOCERIA_MINIMA_PARA_ACORDAR = 0.25

# Por encima de esto, la vocería del punto responde al Comité del Paro — y si el
# Comité suspende, la mesa local del Interior en ese punto se cae con él.
VOCERIA_QUE_RESPONDE_AL_COMITE = 0.50

# Caudal por debajo del cual anunciar un corredor como abierto se desmiente
# solo: una docena de camiones presentada como normalización.
CAUDAL_MINIMO_PARA_ANUNCIAR = 0.30

# Cuánto abre una ventana de despacho concertada, sobre el control de vocería.
# No abre el punto: abre una ventana.
CAUDAL_VENTANA_PASO_SEGURO = 0.25

# Cuánto baja el apoyo al cierre cada instrumento que no es el esquema
# humanitario municipal (0,12, más arriba). Los tres son deliberadamente
# menores: llegan al productor o a la opinión, no al barrio que sostiene el punto.
DESGASTE_POR_CORREDOR_HUMANITARIO = 0.06   # la misión médica se vuelve línea roja
DESGASTE_POR_BALANCE_PUBLICADO = 0.04      # circula por el país entero

# Días de autonomía que repone una caravana escoltada, por clase de prioridad
# del corredor. Menos que el acopio concentrado (ACOPIO_CONCENTRADO, 1,1): la
# carga va dispersa.
REPOSICION_POR_CARAVANA = 0.6

# Cuánto ceden los precios. El acopio concentrado descarga mucha comida de golpe
# en la región; los alivios sectoriales solo sostienen al productor.
ALIVIO_PRECIOS_POR_ACOPIO = 0.08
ALIVIO_PRECIOS_POR_INSTRUMENTOS = 0.04

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

# ---------------------------------------------------------------------------
# LA ESCALA DE GRAVEDAD — seis peldaños, y es lo único que se calibra
# ---------------------------------------------------------------------------
#
# ANTES HABÍA DOCE MAGNITUDES REPARTIDAS POR DOS ARCHIVOS. Veintinueve costos
# tenían nombre y vivían aquí; otros veintidós estaban escritos a mano dentro de
# la acción que los cobraba, en `actions.py`. Entre los dos sistemas se usaban
# **todos los enteros del 1 al 12**, como si cada uno significara algo distinto
# del de al lado — y nadie podía defender por qué un hecho costaba 7 y no 6,
# porque ninguno de estos coeficientes está medido.
#
# Ahora una acción no elige una cifra: elige una GRAVEDAD. Calibrar deja de ser
# mover cincuenta y seis números sueltos y pasa a ser mover seis peldaños.
#
#     Un número se optimiza. Un peldaño se defiende.
#
# La misma regla que el tablero aplica al territorio (`BANDAS_*`), aplicada al
# precio de las decisiones.
#
# LOS SEIS VALORES SON UNA CONVENCIÓN DECLARADA, como todo lo demás en este
# archivo. Salen de agrupar lo que ya se usaba —nearest rung, empates hacia
# arriba— y no de una medición.
# LOS TRES PELDAÑOS ALTOS SON LOS QUE YA HABÍA, y no es casualidad: son los que
# sostienen comportamiento documentado, así que la escala se eligió para caer
# encima de ellos y no al revés.
#
#     alto   10  el acuerdo incumplido · marca el acantilado de la mesa
#     grave  12  operar con el Comité sentado · 45 → 33 → 21 en dos operaciones
#     maximo 22  firmar la asistencia sin delimitar, y nada más
#
# Redondear cualquiera de los tres movía estrategias enteras al otro lado del
# umbral de credibilidad 30, donde los acuerdos se caen por tirada — y eso hacía
# BAILAR las muertes con la semilla, que es justo lo que `PENDIENTES.md` declara
# que nunca debe pasar.
GRAVEDAD = {
    "minimo":   2.0,    # se nota en el acta y no en la calle
    "leve":     3.0,
    "moderado": 5.0,
    "serio":    8.0,
    "alto":    10.0,
    "grave":   12.0,
    "maximo":  22.0,    # un solo caso: firmar la asistencia sin delimitar
}


def _costo(**peldanos: str) -> dict[str, float]:
    """
    Traduce peldaños a deltas de reserva. `-` delante = cuesta; sin nada, repone.

        _costo(legitimidad="-serio", respaldo_internacional="-serio")

    Devuelve flotantes, de modo que `Reservas.aplicar` no cambia y ningún módulo
    de fuera se entera de que la escala existe.
    """
    fuera = {p.lstrip("-") for p in peldanos.values()} - set(GRAVEDAD)
    if fuera:
        raise KeyError(f"peldaño de gravedad desconocido: {sorted(fuera)}")
    return {
        reserva: (-1.0 if peldano.startswith("-") else 1.0) * GRAVEDAD[peldano.lstrip("-")]
        for reserva, peldano in peldanos.items()
    }


# El multiplicador del rédito de una constitutiva adoptada DESPUÉS de un
# incidente. No es un costo de reserva —es una escala— y por eso ya no vive
# dentro de `COSTO_RESERVAS`, donde obligaba a todo el que recorriera el
# diccionario a acordarse de que una de las entradas no era un diccionario.
#
# NO LO LEE NADIE, y hasta ahora eso era invisible: escondido entre veintinueve
# diccionarios, ninguna prueba podía distinguirlo de un costo vivo. Sacarlo a la
# luz lo convierte en una huérfana DECLARADA, que es lo que la prueba
# `test_ninguna_constante_de_parameters_queda_sin_leer` existe para exigir.
#
# Lo que habría que decidir: que constituirse tarde rinda menos que constituirse
# a tiempo es una idea del diseño original que nunca se conectó. O se conecta
# —y entonces adoptar el registro escrito tras el primer incidente vale la mitad—
# o se retira. Mientras tanto, no gobierna nada.
MULTIPLICADOR_CONSTITUTIVA_REACTIVA = 0.5

COSTO_RESERVAS = {
    "incidente_con_victima": _costo(legitimidad="-serio", respaldo_internacional="-serio"),
    "imagen_viral": _costo(legitimidad="-moderado", respaldo_internacional="-moderado"),
    "cifra_desmentida": _costo(legitimidad="-leve"),
    "operacion_dia_de_mesa": _costo(credibilidad_mesa="-grave"),
    "operacion_no_informada": _costo(cohesion_mesa="-serio"),
    "corredor_humanitario_negado": _costo(
        respaldo_internacional="-grave", legitimidad="-moderado"),
    "acuerdo_verificable_cumplido": _costo(
        legitimidad="moderado", credibilidad_mesa="serio", cohesion_mesa="leve"),
    # `alto` y no `grave`: es el peldaño que decide si la mesa cruza el umbral de
    # credibilidad 30, y moverlo cambia qué estrategias sobreviven.
    "acuerdo_incumplido": _costo(credibilidad_mesa="-alto", legitimidad="-leve"),
    "apertura_concertada": _costo(legitimidad="minimo"),
    "sin_registro_escrito": _costo(cohesion_mesa="-serio"),
    "sin_protocolo_voceria": _costo(cohesion_mesa="-moderado"),
    "sin_criterio_priorizacion": _costo(cohesion_mesa="-leve"),
    "turno_sin_decision": _costo(legitimidad="-leve"),
    "decision_con_responsable": _costo(cohesion_mesa="minimo"),
    "escolta_lograda": _costo(legitimidad="leve"),
    "escolta_atacada": _costo(legitimidad="-moderado", respaldo_internacional="-leve"),
    # LAS CUATRO SALIDAS DE VERIFICAR UNA DENUNCIA, y son cuatro y no dos desde
    # que el que verifica es el sector del que se denuncia. Lo que separa cada
    # par es si hay protocolo común de verificación adoptado: sin él, la mesa
    # está oyendo a una parte hablar de su propia conducta.
    #
    # Documentar la propia falta DENTRO del protocolo sigue saliendo más barato
    # que el estallido; fuera de él no ahorra nada. Y desmentir sin protocolo no
    # da credibilidad —se lee como una absolución— aunque sigue evitando que se
    # desplace fuerza a algo que no pasó, que es lo que conserva la legitimidad.
    "denuncia_veraz_confirmada": _costo(
        respaldo_internacional="-moderado", legitimidad="-leve"),
    "denuncia_veraz_sin_protocolo": _costo(
        respaldo_internacional="-grave", legitimidad="-serio"),
    "denuncia_falsa_desmentida": _costo(legitimidad="leve", credibilidad_mesa="minimo"),
    "denuncia_falsa_sin_protocolo": _costo(legitimidad="minimo"),
    # EL PRECIO DE ATARSE LAS MANOS UNO MISMO. El estandar completo lo pedia un
    # tercero y lo concedia el Gobierno; sin ese rol lo adopta el propio sector,
    # y encender los tres mitigadores el primer dia sin costo desequilibraria el
    # ejercicio entero. Gana respaldo fuera y cuesta cohesion dentro, que es lo
    # que se paga cuando quien manda la fuerza se limita delante de la mesa.
    #
    # SIN CALIBRAR: los dos numeros son provisionales y salen de C5.
    "estandar_autoimpuesto": _costo(respaldo_internacional="serio", cohesion_mesa="-moderado"),
    # --- el frente agroalimentario ---
    # Reordenar un criterio de priorización que la mesa ya adoptó no es lo mismo
    # que llegar antes de que exista: en el primer caso hay un ministro que ve
    # deshacerse su propio orden delante de todos.
    "clase_alimentaria_sobre_criterio": _costo(cohesion_mesa="-moderado"),
    "clase_alimentaria": _costo(cohesion_mesa="-minimo"),
    # La mesa técnica rural es un segundo canal. Cuando el Interior tiene una
    # vocería única fijada o un acuerdo nacional vivo, abrirlo se lo quita.
    "canal_rural_paralelo": _costo(cohesion_mesa="-leve"),
    # Publicar la pérdida traslada el costo del cierre a la población: gana
    # legitimidad y le entrega a quien pide mano dura su mejor argumento.
    "balance_perdida_publicado": _costo(legitimidad="minimo", cohesion_mesa="-leve"),
    "cifra_sectorial_disputada": _costo(credibilidad_mesa="-moderado"),
    "cifra_sectorial_verificada": _costo(respaldo_internacional="minimo"),
    # Un esquema de cupos produce ganadores y perdedores entre productores, y
    # hace rendir la escolta que ya está puesta.
    "acopio_por_cupos": _costo(legitimidad="-minimo", cohesion_mesa="minimo"),

    # -----------------------------------------------------------------------
    # LOS VEINTIDÓS QUE ESTABAN ESCRITOS DENTRO DE UNA ACCIÓN
    # -----------------------------------------------------------------------
    #
    # Hasta ahora `actions.py` llamaba a `reservas.aplicar({...})` con el
    # diccionario escrito ahí mismo, veintidós veces. Eso incumplía la regla de
    # la cabecera de este archivo —«si un número gobierna el motor, vive aquí y
    # en ningún otro sitio»— y hacía imposible contestar «¿cuánto cuesta una
    # decisión seria?» sin abrir dos archivos y leer cincuenta y seis sitios.
    #
    # Ninguna acción cobra sobre una reserva distinta de la que cobraba, ni
    # cambia de signo, ni deja de cobrar: solo se redondeó la magnitud al
    # peldaño más cercano.

    # --- Presidente ---
    "lineas_rojas_sin_margen": _costo(credibilidad_mesa="-serio"),
    "asistencia_militar_firmada": _costo(credibilidad_mesa="-grave"),
    "asistencia_militar_delimitada": _costo(
        respaldo_internacional="-serio", legitimidad="-moderado"),
    # El único «máximo» del repertorio, y es deliberado: entrega a la narrativa
    # de represión su mejor argumento.
    "asistencia_militar_sin_delimitar": _costo(
        respaldo_internacional="-maximo", legitimidad="-grave"),
    "alcaldes_con_prioridad": _costo(cohesion_mesa="leve", legitimidad="minimo"),
    "alcaldes_sin_prioridad": _costo(cohesion_mesa="minimo"),
    "presidente_acompana_mesa": _costo(credibilidad_mesa="moderado", legitimidad="leve"),
    "presidente_acompana_operacion": _costo(legitimidad="-minimo", cohesion_mesa="leve"),
    "presidente_sin_acompanar": _costo(legitimidad="minimo"),

    # --- Interior ---
    "contraprestacion_tramitada": _costo(credibilidad_mesa="moderado", legitimidad="leve"),
    "contraprestacion_fallida": _costo(credibilidad_mesa="-serio", legitimidad="-leve"),
    "corredor_humanitario_requerido": _costo(respaldo_internacional="moderado"),

    # --- Alcalde ---
    "parte_municipal_en_protocolo": _costo(legitimidad="minimo", respaldo_internacional="leve"),

    # --- Defensa ---
    "operacion_sin_concertar_epicentro": _costo(
        legitimidad="-serio", cohesion_mesa="-leve"),
    "evidencia_con_solidez": _costo(cohesion_mesa="leve", credibilidad_mesa="minimo"),
    "evidencia_sin_solidez": _costo(legitimidad="-leve", credibilidad_mesa="-moderado"),

    # --- Policía ---
    "esmad_concentrado": _costo(cohesion_mesa="-leve"),

    # --- Transporte ---
    "gremios_compensados": _costo(legitimidad="minimo", credibilidad_mesa="-leve"),
    "caravana_organizada": _costo(legitimidad="leve"),
    "paso_seguro_contra_lineas_rojas": _costo(cohesion_mesa="-leve"),
    "apertura_anunciada_sin_sostener": _costo(legitimidad="-leve"),
    "apertura_anunciada_verificada": _costo(legitimidad="leve", credibilidad_mesa="minimo"),

    # --- Agricultura ---
    # Se aplica con el factor de decaimiento del paquete: el segundo alivio en
    # la misma región rinde la mitad que el primero.
    "instrumentos_sectoriales": _costo(legitimidad="leve"),
    "calendario_entregado": _costo(cohesion_mesa="leve"),
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
#
# LA CLAVE DECÍA `defensoria` Y NADIE LA LEÍA. Quedó del rol que se retiró, y
# `information._rol_de()` devuelve `defensa` para la inteligencia y para los
# equipos de terreno — de modo que el `.get()` no encontraba nada y devolvía
# 0,0. Consecuencia medida, y silenciosa: **las dos fuentes del Ministerio de
# Defensa eran las únicas del ejercicio que leían la vocería exactamente bien**,
# sin que nada en el diseño dijera que debían.
#
# No hubo excepción, ni traza, ni error: el motor entregaba un número
# perfectamente plausible. Ahora la clave se llama como el rol que la usa, y
# `estimar_nodo` falla ruidosamente si algún día vuelve a faltar una.
SESGO_CONTROL_VOCERIA = {
    "interior": 0.20,
    "alcalde_cali": 0.03,
    "defensa": 0.05,
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

# CONTRA QUÉ VOCERÍA SE MIDE ESE CAUDAL. Un punto con esta vocería recibe el
# caudal íntegro; por encima abre más y por debajo, menos. Estaba escrito a mano
# —un `/ 0.6` suelto en `ConvocarMesaNacional`— y era el único número del motor
# que gobernaba comportamiento fuera de este archivo.
VOCERIA_DE_REFERENCIA_ACUERDO = 0.6
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
