"""
test_canal_ordenes.py — La capa 4, que es la que habla con personas.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

Hasta esta tanda, **la capa 4 no tenía ni una sola prueba**. Sesenta y tres
verificadores custodiaban el motor —que nadie toca durante el ejercicio— y cero
custodiaban el canal por el que entran las órdenes de nueve personas en dos horas.
Todo lo que hay aquí nació de sondear el canal con órdenes reales, y **cada
prueba corresponde a algo que estaba roto**.

LA REGLA QUE ORDENA EL ARCHIVO

    Si el canal no entiende, PREGUNTA. Nunca adivina, nunca fuerza la acción más
    parecida, y nunca ejecuta una orden a medias.

El fallo que hay que impedir no es que el canal se equivoque: es que se equivoque
**en silencio**. Una orden rechazada con un motivo legible cuesta veinte
segundos de sala. Una orden ejecutada en el punto equivocado no cuesta nada
—hasta el debriefing.

NINGUNA PRUEBA LLAMA A UN MODELO. El accesorio `sin_modelo` fuerza la rama
determinista, que es la que corre cuando no hay llave. Si alguna necesitara red,
la suite dejaría de ser reproducible y dejaría de correr en cada cambio.
"""

from __future__ import annotations

import importlib

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from src.agents import herramientas, nlu, resolver
from src.engine.loader import cargar_estado
from src.engine.simulation import MotorCrisis


# ===========================================================================
# Accesorios
# ===========================================================================

@pytest.fixture(autouse=True)
def sin_modelo(monkeypatch):
    """
    Ninguna prueba sale a la red. Nunca.

    Además de hacer la suite reproducible, esto prueba algo del diseño: **el
    canal entero funciona sin llave**. Si alguna de estas pruebas dejara de pasar
    al quitar el modelo, la degradación sería decorativa.
    """
    monkeypatch.setattr(nlu, "cliente", lambda: None)


@pytest.fixture
def estado():
    return cargar_estado()


@pytest.fixture
def motor(estado):
    return MotorCrisis(estado)


@pytest.fixture
def consola(monkeypatch):
    """Una API recién cargada por prueba: `/ejecutar` corre turnos de verdad."""
    import src.api.main as main
    main = importlib.reload(main)
    monkeypatch.setattr(main.nlu, "cliente", lambda: None)
    return TestClient(main.app)


def plan(estado, texto):
    return nlu.interpretar(estado, texto, "prueba")


def solo(estado, texto):
    """El plan de una sola acción, para las pruebas que esperan exactamente una."""
    p = plan(estado, texto)
    assert len(p.acciones) == 1, [a.herramienta for a in p.acciones]
    return p.acciones[0]


# ===========================================================================
# UN RECURSO QUE NO EXISTE
#
# «Operen el Puente de Brooklyn». No hay tal puente. Lo que NO puede pasar es
# que se opere el que más se le parezca.
# ===========================================================================

def test_un_lugar_que_no_existe_no_se_ejecuta(estado):
    a = solo(estado, "operen el Puente de Brooklyn")
    assert a.estado == "falta_dato"
    assert "no existe" in (a.motivo or "").lower()


def test_un_lugar_que_no_existe_ofrece_los_que_se_le_parecen(estado):
    """
    Ofrecer no es elegir. La sala corrige en un segundo y el sistema no decidió
    nada por ella.
    """
    a = solo(estado, "operen el Puente de Brooklyn")
    nombres = [c["nombre"] for c in a.entidades[0].candidatos]
    assert nombres, "sin sugerencias no hay por dónde corregir"
    assert any("Puente" in n for n in nombres), "los que se llaman igual, primero"


def test_un_nombre_que_no_se_parece_a_nada_no_inventa_sugerencias(estado):
    """
    Tres nombres al azar porque son los menos malos de veinticuatro no son
    ayuda: son ruido con forma de ayuda. Se dice qué CLASE de cosa se esperaba.
    """
    r = resolver.resolver(estado, "xyzzy", "punto")
    assert r.estado == "no_encontrado"
    assert not r.candidatos
    assert "punto de cierre" in r.eco()


def test_un_corredor_donde_se_esperaba_un_punto_lo_dice(estado):
    """
    Antes respondía «no corresponde a ningún punto, corredor ni región» — y es
    un corredor. El filtro por tipo tapaba la única respuesta útil.
    """
    a = solo(estado, "operen el Corredor hospitalario")
    assert a.estado == "falta_dato"
    assert "es un corredor" in (a.motivo or "")
    # Y dice qué pedir en su lugar: los puntos del corredor, que son públicos.
    assert "Acceso Hospital Universitario" in (a.motivo or "")


def test_al_explicar_el_corredor_no_se_filtra_cual_lo_bloquea(estado):
    """
    Qué punto bloquea cada corredor es el dato EXCLUSIVO del Ministro de
    Transporte. La consola la opera cualquiera y el plan se lee en voz alta: si
    saliera por aquí, el rol se consultaría una vez y después sobraría.
    """
    r = resolver.resolver(estado, "Anillo hospitalario", "punto")
    corredor = estado.corredores["C-HOS"]
    bloquea = corredor.punto_que_bloquea(estado.nodos)
    assert bloquea, "premisa: en el turno 0 el corredor está bloqueado"
    assert "bloquea" not in (r.pista or "").lower()


def test_una_region_que_no_existe_enumera_las_cuatro(estado):
    """Con cuatro opciones, la lista completa resuelve la duda de una."""
    r = resolver.resolver(estado, "Antioquia", "region")
    assert r.estado == "no_encontrado"
    assert len(r.candidatos) == len(estado.regiones)


# ===========================================================================
# UNA ORDEN QUE NO EXISTE
#
# «Declaren el estado de sitio». No está en el repertorio y no hay nada
# parecido. Restringir el espacio de salida no impide que el modelo se salga:
# lo empuja a FORZAR la orden dentro de lo disponible, y eso es peor.
# ===========================================================================

@pytest.mark.parametrize("texto", [
    "declaren el estado de sitio en todo el pais",
    "corten el internet en la region",
    "renuncia el presidente",
    "convoquen elecciones anticipadas",
])
def test_una_orden_fuera_del_repertorio_no_se_fuerza(estado, texto):
    p = plan(estado, texto)
    assert p.acciones == [], [a.herramienta for a in p.acciones]
    assert p.avisos


def test_al_no_reconocer_nada_se_dice_por_que(estado):
    """
    Cuatro silencios distintos, cuatro respuestas distintas. Antes los cinco
    casos daban el mismo párrafo, y la sala no podía saber si había escrito mal
    el nombre, si le faltaba el verbo, o si eso no existe en este mundo.
    """
    assert "No se escribió ninguna orden" in plan(estado, "   ").avisos[0]

    # Nombra un lugar del mapa pero ningún verbo del repertorio
    aviso = plan(estado, "bombardeen el Puente Amarillo").avisos[0]
    assert "Puente Amarillo" in aviso and "no qué hacer" in aviso

    # Pregunta que el canal no sabe responder
    aviso = plan(estado, "¿y qué opina la comunidad internacional?").avisos[0]
    assert "pregunta" in aviso.lower()

    # Nada de lo anterior
    aviso = plan(estado, "declaren el estado de sitio").avisos[0]
    assert "repertorio" in aviso.lower()


def test_si_se_entiende_la_accion_pero_no_el_sitio_se_dice_asi(estado,
                                                               monkeypatch):
    """
    El quinto diagnóstico. Con el modelo puesto, un sitio ambiguo hacía a veces
    que no llamara a nada, y la sala leía «esa acción no existe» sobre una
    acción que sí existe: la mandaba a corregir donde no estaba el problema.
    """
    monkeypatch.setattr(herramientas, "interpretar_sin_modelo",
                        lambda *_: [])          # el modelo no devolvió nada
    p = plan(estado, "operen eso de alli")
    assert p.acciones == []
    aviso = p.avisos[0]
    assert "Se entiende la acción" in aviso
    assert "no sobre qué" in aviso


def test_si_de_verdad_no_existe_la_accion_se_sigue_diciendo(estado):
    """La contraparte: no vale responder siempre lo mismo."""
    p = plan(estado, "declaren el estado de sitio")
    assert "Ninguna acción del repertorio" in p.avisos[0]


# ===========================================================================
# LA AMBIGÜEDAD SE PREGUNTA, NUNCA SE ADIVINA
#
# Quedarse con la primera coincidencia parcial produce el peor fallo posible:
# la orden se ejecuta en el lugar equivocado y nadie se entera.
# ===========================================================================

def test_un_nombre_ambiguo_se_repregunta(estado):
    a = solo(estado, "operen el puente")
    assert a.estado == "ambigua"
    assert len(a.entidades[0].candidatos) >= 2


def test_el_nombre_oficial_completo_gana_aunque_sea_prefijo_de_otro(estado):
    """
    Sin esto, un desplegable de nombres oficiales ofrece opciones que el sistema
    luego repregunta. Costó descubrirlo.
    """
    r = resolver.resolver(estado, "Peaje del Puerto", "punto")
    assert r.estado == "ok"
    assert r.nombre == "Peaje del Puerto"


def test_una_orden_compuesta_no_le_roba_el_lugar_a_la_otra(estado):
    """
    EL PEOR FALLO QUE TENÍA EL CANAL.

    «Operen el puente y concertar el Alto del Mirador» producía DOS acciones
    sobre el Alto del Mirador: el intérprete buscaba nombres en TODO el texto,
    así que el de la segunda cláusula se colaba en la primera y la ambigüedad de
    «el puente» —que era la respuesta correcta— desaparecía sin dejar rastro.
    """
    p = plan(estado, "operen el puente y concertar el Alto del Mirador")
    assert len(p.acciones) == 2

    operar = next(a for a in p.acciones if a.herramienta == "operar_punto")
    concertar = next(a for a in p.acciones if a.herramienta == "abrir_mesa_local")

    assert operar.estado == "ambigua", "«el puente» sigue siendo dos puentes"
    assert concertar.argumentos["nodo_id"] == "N004"


# ===========================================================================
# UN VALOR QUE NO ESTÁ EN LA ENUMERACIÓN
#
# El modelo devuelve «militares» donde el motor espera «militar». Normalizar eso
# está bien. Sustituirlo por un valor por defecto NO: la orden se ejecutaría con
# una unidad que nadie pidió.
# ===========================================================================

def test_un_valor_de_enumeracion_invalido_no_se_sustituye(estado):
    a = nlu._a_accion_plan(estado, {
        "nombre": "redesplegar_militares",
        "argumentos": {"modo": "nacional"}})
    assert a.estado == "falta_dato"
    assert "no es un valor válido" in (a.motivo or "")


def test_un_modo_invalido_tambien_lo_rechaza_el_motor(estado):
    """
    Defensa en dos capas, y hace falta: la capa 4 lo marca `falta_dato`, y aun
    así llegaba al motor porque `/ejecutar` solo saltaba `no_viable`. Sin
    `validar()`, un modo desconocido caía por el `else` de `ejecutar` y se hacía
    PROYECCIÓN AÉREA — algo que nadie pidió, reportado como ejecutado con éxito.
    """
    from src.engine.actions import RedesplegarMilitares
    v = RedesplegarMilitares(modo="nacional").validar(estado)
    assert not v.ok
    assert "no es un modo" in (v.motivo or "")


def test_las_variantes_conocidas_si_se_normalizan(estado):
    """Normalizar «militares» → «militar» es traducir. Es lo que sí toca."""
    args, avisos = herramientas.normalizar_enums({"tipo_unidad": "Ejército"})
    assert args["tipo_unidad"] == "militar"
    assert not avisos


def test_la_unidad_pedida_no_se_cambia_por_la_de_por_defecto(estado):
    """
    «Operen X con militares» salía como ESMAD porque el intérprete de reserva no
    leía la unidad. Emplear tropa multiplica el riesgo por cinco y requiere una
    firma que puede no existir: eso no se infiere ni se rellena solo.
    """
    a = solo(estado, "operen el Puente Amarillo con militares")
    assert a.argumentos["tipo_unidad"] == "militar"
    assert "militares" in a.en_claro()


def test_un_cargo_del_texto_no_se_confunde_con_la_unidad(estado):
    """
    «Responsable el Director de Policía» NO es una orden de emplear policía. Por
    eso la unidad solo se lee tras una marca: «con», «usando», «empleando».
    """
    a = solo(estado, "operen el Puente Amarillo, responsable el Director de Policia")
    assert a.argumentos.get("tipo_unidad") != "policia"


# ===========================================================================
# UN CRITERIO ES N LUGARES, NO EL PRIMERO DE LA LISTA
# ===========================================================================

def test_un_criterio_produce_una_accion_por_punto(estado):
    """
    «Operen todos los puntos» ejecutaba UNO. El resolutor devolvía el criterio,
    el expansor devolvía veinticuatro identificadores y el código se quedaba con
    `ids[0]`. La sala creía haber ordenado veinticuatro operaciones.
    """
    cerrados = [n for n in estado.nodos.values() if not n.abierto]
    p = plan(estado, "operen todos los puntos")
    assert len(p.acciones) == len(cerrados) <= nlu.TOPE_ACCIONES
    assert len({a.argumentos["nodo_id"] for a in p.acciones}) == len(cerrados)

    # Y el tope sigue vivo: con más puntos que el tope, se corta y se avisa.
    for i in range(nlu.TOPE_ACCIONES + 2):
        estado.nodos[f"NX{i:02d}"] = replace(
            cerrados[0], nodo_id=f"NX{i:02d}", nombre=f"Cierre de prueba {i}")
    p = plan(estado, "operen todos los puntos")
    assert len(p.acciones) == nlu.TOPE_ACCIONES
    assert any("tope" in av.lower() for av in p.avisos)


def test_los_criterios_documentados_funcionan_todos(estado):
    """
    Cuatro claves de la tabla de selectores eran INALCANZABLES: `normalizar()`
    quita el artículo, así que «el más duro» llegaba como «mas duro» y no
    estaba. Cuatro criterios documentados que nunca funcionaron.
    """
    for frase in resolver.FRASES_SELECTOR:
        r = resolver.resolver(estado, frase, "punto")
        assert r.estado == "selector", f"«{frase}» no llega a la tabla"


def test_verificar_por_criterio_no_produce_una_lista_vacia(estado):
    """
    «Verificar los cerrados» daba una acción con la lista de puntos VACÍA y la
    daba por lista: se ordenaba verificar y no se verificaba nada.
    """
    a = solo(estado, "verificar los cerrados")
    assert a.herramienta == "desplegar_equipos"
    assert a.argumentos["puntos"], "el criterio tiene que expandirse"


def test_verificar_sin_decir_que_no_es_viable(estado, motor):
    """La misma regla, custodiada también desde el motor."""
    from src.engine.actions import DesplegarEquiposTerreno
    v = DesplegarEquiposTerreno(nodos=[], denuncias=[]).validar(estado)
    assert not v.ok
    assert "qué verificar" in (v.motivo or "")


# ===========================================================================
# PREGUNTAR NO ES ORDENAR
#
# Un clasificador orden/consulta que se equivoca manda una orden que nadie dio,
# y eso es irreversible. Por eso consultar es una herramienta más.
# ===========================================================================

def test_una_pregunta_no_produce_ninguna_orden(estado):
    p = plan(estado, "cuantos escuadrones nos quedan disponibles?")
    assert len(p.acciones) == 1
    assert p.acciones[0].herramienta == "consultar"
    assert p.acciones[0].datos, "la consulta trae su respuesta del motor"


def test_consultar_existe_de_verdad_en_el_repertorio(estado):
    """
    Se le ofrecía al modelo como herramienta —es la mitigación declarada del
    séptimo modo de falla— pero no estaba en `HERRAMIENTAS`. Cuando el modelo la
    llamaba, el plan respondía «Herramienta desconocida: consultar». La defensa
    estaba anunciada y no existía.
    """
    a = nlu._a_accion_plan(estado, {"nombre": "consultar",
                                    "argumentos": {"tema": "fuerza"}})
    assert a.estado == "lista"
    assert a.datos["ambito"]


def test_un_tema_de_consulta_que_no_existe_se_dice(estado):
    a = nlu._a_accion_plan(estado, {"nombre": "consultar",
                                    "argumentos": {"tema": "el clima"}})
    assert a.estado == "falta_dato"
    assert "tema de consulta" in (a.motivo or "")


def test_un_mensaje_puede_ser_orden_y_consulta_a_la_vez(estado):
    p = plan(estado, "cuantos escuadrones quedan? y operen el Puente Amarillo")
    tipos = {a.herramienta for a in p.acciones}
    assert tipos == {"consultar", "operar_punto"}


def test_la_hoja_de_datos_nunca_dice_null(estado):
    """
    `null` es ambiguo entre «no lo sé» y «no hay», y un modelo lo lee como
    laguna. Se pone un texto explícito.
    """
    for tema in herramientas.TEMAS_CONSULTA:
        hoja = nlu.hoja_de_datos(estado, tema)
        assert "None" not in repr(hoja), tema


# ===========================================================================
# LO QUE LA SALA OYE ANTES DE CONFIRMAR
#
# El paso 5 existe para que la sala oiga su propia decisión reformulada, con su
# riesgo. Si no dice sobre qué actúa, no la está oyendo.
# ===========================================================================

def test_la_lectura_dice_sobre_que_punto_se_actua(estado):
    """
    Antes decía «Operación de desbloqueo sobre un punto de cierre» y nada más:
    la sala confirmaba una operación sin oír sobre cuál.
    """
    p = plan(estado, "operen el Puente Amarillo")
    lectura = p.lectura()
    assert "Puente Amarillo" in lectura
    assert "N003" in lectura, "el identificador es lo que hace auditable el eco"


def test_la_lectura_dice_la_banda_de_riesgo_antes_de_decidir(estado):
    lectura = plan(estado, "operen el Puente Amarillo").lectura()
    assert "Riesgo de incidente" in lectura
    assert "Mitigadores ausentes" in lectura


def test_la_lectura_nunca_la_escribe_el_modelo(estado):
    """
    Si la escribiera, podría afirmar un éxito que todavía no ocurrió — el
    primero de los ocho modos de falla y el más difícil de detectar. Es
    determinista: el mismo plan da el mismo texto, siempre.
    """
    p = plan(estado, "operen el Puente Amarillo con dupla de la Defensoria")
    assert p.lectura() == p.lectura()


def test_una_condicion_se_señala_porque_el_canal_no_la_traduce(estado):
    """
    El motor sabe encolar condicionales; el canal no sabe leerlas. Callarlo
    convierte «si la Defensoría verifica X, opérenlo» en una orden inmediata.
    """
    p = plan(estado, "si la Defensoria verifica el Puente Amarillo, operenlo")
    assert any("condición" in av for av in p.avisos)


def test_una_negacion_se_señala_porque_el_canal_no_la_traduce(estado):
    """
    No se suprime la acción: eso sería el canal decidiendo, que es lo único que
    esta capa no puede hacer. Se señala, y la lee una persona.
    """
    p = plan(estado, "no operen ningun punto este turno")
    assert any("negación" in av for av in p.avisos)


def test_falta_un_dato_obligatorio_y_se_dice_cual(estado):
    a = solo(estado, "operenlo ya")
    assert a.estado == "falta_dato"
    assert "punto de cierre" in (a.motivo or "")


# ===========================================================================
# LA CONSOLA — nada se ejecuta a medias, nada se cae en silencio
# ===========================================================================

def test_una_accion_incompleta_no_se_encola(consola):
    """
    `/ejecutar` solo saltaba `no_viable` y `ambigua`. Una acción en
    `falta_dato` llegaba al motor y se ejecutaba con lo que hubiera.
    """
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente de Brooklyn"}).json()
    assert p["acciones"][0]["estado"] == "falta_dato"

    r = consola.post("/api/consola/ejecutar",
                     json={"plan_id": p["plan_id"]}).json()
    assert r["acciones_encoladas"] == 0
    assert r["omitidas"], "y se dice cuál se quedó fuera, y por qué"


def test_lo_que_no_se_ejecuta_se_reporta(consola):
    """
    Antes un `except: continue` tiraba la acción sin decirlo. La sala confirmaba
    tres órdenes, se ejecutaban dos, y el hueco no aparecía en ningún sitio.
    """
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el puente"}).json()
    r = consola.post("/api/consola/ejecutar",
                     json={"plan_id": p["plan_id"]}).json()
    assert [o["herramienta"] for o in r["omitidas"]] == ["operar_punto"]
    assert r["omitidas"][0]["estado"] == "ambigua"


def test_una_orden_que_el_motor_rechaza_se_omite_y_no_tumba_la_consola(consola):
    """
    **La rama que ninguna prueba tocaba, y era la única que reventaba.**

    Las omisiones que sí estaban cubiertas —`ambigua`, `falta_dato`— las decide
    el canal antes de llegar al motor. Esta es la otra: la orden sale del canal
    marcada «lista» y es `MotorCrisis.encolar` quien la rechaza. Ahí la consola
    leía `v.mensaje`, que es el campo de `Resultado` y no el de `Validacion`, y
    devolvía un 500 en vez de una omisión.

    Se llega por dos caminos y los dos son de sala: que `validar()` cambie de
    opinión entre interpretar y confirmar, y —seguro— la orden que pasa el tope
    de la cola, que es donde `encolar` rechaza por su cuenta sin que ninguna
    capa anterior lo haya visto venir.
    """
    import src.api.main as main
    from src.engine import parameters as P
    from src.engine.actions import DesplegarEquiposTerreno

    main.motor.cola_inmediata.extend(
        DesplegarEquiposTerreno(nodos=["N003"])
        for _ in range(P.TOPE_ACCIONES_POR_PLAN)
    )

    p = consola.post("/api/consola/interpretar",
                     json={"texto": "verificar el Puente Amarillo"}).json()
    assert p["acciones"][0]["estado"] == "lista", "el canal no ve el tope"

    r = consola.post("/api/consola/encolar", json={"plan_id": p["plan_id"]})
    assert r.status_code == 200, "la consola no puede caerse por una orden de más"
    r = r.json()
    assert r["acciones_encoladas"] == 0
    assert r["omitidas"][0]["estado"] == "no_viable"
    assert r["omitidas"][0]["motivo"], "y se dice por qué, no un hueco"


def test_una_consulta_no_ejecuta_nada(consola):
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "como esta el abastecimiento?"}).json()
    r = consola.post("/api/consola/ejecutar",
                     json={"plan_id": p["plan_id"]}).json()
    assert r["acciones_encoladas"] == 0
    assert not r["omitidas"], "una consulta no es una orden omitida"


def test_los_identificadores_de_plan_no_se_reutilizan(consola):
    """
    Salían de `len(planes) + 1`, y `ejecutar` saca el plan del diccionario. Con
    dos planes abiertos, ejecutar el primero hacía que el siguiente
    `interpretar` reutilizara un identificador vivo y lo sobrescribiera.
    """
    a = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente Amarillo"}).json()["plan_id"]
    b = consola.post("/api/consola/interpretar",
                     json={"texto": "concertar el Alto del Mirador"}).json()["plan_id"]
    consola.post("/api/consola/ejecutar", json={"plan_id": a})
    c = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Peaje del Norte"}).json()["plan_id"]
    assert len({a, b, c}) == 3


def test_una_ambiguedad_se_resuelve_con_una_eleccion_tipada(consola):
    """
    Sin esto aparecen las ejecuciones fantasma: la respuesta corta a una
    repregunta —«no», «400», «sí, confirmo»— entra de nuevo por el canal como si
    fuera una orden nueva. En la simulación anterior esas tres palabras
    produjeron cada una una evacuación.
    """
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el puente"}).json()
    assert p["acciones"][0]["estado"] == "ambigua"

    p2 = consola.post("/api/consola/elegir", json={
        "plan_id": p["plan_id"], "indice": 0,
        "campo": "nodo_id", "valor": "N003"}).json()
    assert p2["acciones"][0]["estado"] == "lista"
    assert "Puente Amarillo" in p2["acciones"][0]["en_claro"]


def test_un_nombre_que_no_existe_tambien_se_corrige_con_un_boton(consola):
    """
    La pantalla ofrecia botones solo para la ambiguedad. Para «Puente de
    Brooklyn» habia que reescribir la orden entera, y el resolutor ya habia
    calculado a que se parecia.
    """
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente de Brooklyn"}).json()
    e = p["acciones"][0]["entidades"][0]
    assert e["estado"] == "no_encontrado"
    assert e["candidatos"], "sin candidatos no hay boton que pulsar"

    elegido = e["candidatos"][0]["id"]
    p2 = consola.post("/api/consola/elegir", json={
        "plan_id": p["plan_id"], "indice": 0,
        "campo": "nodo_id", "valor": elegido}).json()
    assert p2["acciones"][0]["estado"] == "lista"


def test_una_eleccion_solo_puede_tocar_campos_declarados(consola):
    """La reanudación no puede ser una vía para inyectar argumentos arbitrarios."""
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el puente"}).json()
    r = consola.post("/api/consola/elegir", json={
        "plan_id": p["plan_id"], "indice": 0,
        "campo": "lo_que_sea", "valor": "x"})
    assert r.status_code == 400


def test_un_plan_ya_consumido_no_se_ejecuta_dos_veces(consola):
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente Amarillo"}).json()
    assert consola.post("/api/consola/ejecutar",
                        json={"plan_id": p["plan_id"]}).status_code == 200
    assert consola.post("/api/consola/ejecutar",
                        json={"plan_id": p["plan_id"]}).status_code == 404


# ===========================================================================
# LA DEGRADACIÓN
#
# El ejercicio corre entero sin llave. No es tolerancia a fallos por cortesía:
# es la prueba operativa de que ninguna decisión está delegada a un modelo.
# ===========================================================================

def test_sin_llave_el_canal_traduce_igual_y_lo_dice(estado):
    p = plan(estado, "operen el Puente Amarillo con dupla de la Defensoria")
    assert p.interpretado_por == "determinista"
    assert p.acciones[0].estado == "lista"


def test_si_el_proveedor_falla_se_degrada_y_se_dice_que_se_degrado(estado,
                                                                   monkeypatch):
    """
    Un error del proveedor no puede dejar a nueve personas mirando la pantalla. Y
    la sala tiene que enterarse de que está en modo degradado: descubrirlo a
    mitad del ejercicio es peor que empezar sabiéndolo.
    """
    class ClienteRoto:
        class chat:
            class completions:
                @staticmethod
                def create(**_):
                    raise TimeoutError("el proveedor no responde")

    monkeypatch.setattr(nlu, "cliente", lambda: ClienteRoto())
    p = plan(estado, "operen el Puente Amarillo")
    assert "determinista" in p.interpretado_por
    assert "TimeoutError" in p.interpretado_por
    assert p.acciones[0].estado == "lista"


def test_si_el_modelo_devuelve_algo_que_no_es_json_no_revienta_el_turno(estado,
                                                                        monkeypatch):
    """
    NUNCA parsear prosa a mano. Si el modelo no devolvió JSON válido, esa llamada
    se descarta y las demás siguen.
    """
    class Fn:
        name = "operar_punto"
        arguments = "esto no es json"

    class TC:
        function = Fn()

    class Msg:
        tool_calls = [TC()]

    class Choice:
        message = Msg()

    class Respuesta:
        choices = [Choice()]

    class Cliente:
        class chat:
            class completions:
                @staticmethod
                def create(**_):
                    return Respuesta()

    monkeypatch.setattr(nlu, "cliente", lambda: Cliente())
    p = plan(estado, "operen el Puente Amarillo")
    assert p.acciones == []
    assert p.avisos


# ===========================================================================
# LO QUE EL CANAL NO PUEDE DEJAR SALIR
# ===========================================================================

def test_el_canal_jamas_expone_la_mezcla_real_ni_la_veracidad(estado):
    """
    La misma invariante que custodia el tablero, aplicada a la otra superficie
    por la que sale texto. Si esto se filtrara, el dilema central desaparece.
    """
    textos = [
        "operen el Puente Amarillo",
        "operen el puente",
        "verificar los cerrados",
        "cuantos escuadrones quedan?",
        "como estan los corredores?",
    ]
    for t in textos:
        crudo = repr(plan(estado, t).a_dict())
        assert "composicion_real" not in crudo, t
        assert "'veraz'" not in crudo, t


def test_el_tope_de_acciones_por_plan_no_se_puede_saltar(estado):
    p = plan(estado, "operen todos los puntos")
    assert len(p.acciones) <= nlu.TOPE_ACCIONES


# ===========================================================================
# EL REPERTORIO COMPLETO, TAMBIÉN SIN LLAVE
#
# Sin llave el canal traduce con `interpretar_sin_modelo`, y ahí una herramienta
# sin disparador **no existe**: el canal responde «ninguna acción del repertorio
# corresponde a eso» sobre una acción que sí tiene. No se equivoca de acción:
# niega tener una que tiene, y manda a la sala a corregir donde no estaba el
# problema. Faltaban dos de veintiséis.
# ===========================================================================

def test_toda_herramienta_del_repertorio_es_alcanzable_sin_modelo():
    """
    La lista se recorre entera. Una herramienta nueva sin disparador es
    invisible en la rama determinista, y **A3 deja abierto que la primera
    corrida se haga sin llave**.
    """
    con_disparador = {n for n, _, _ in herramientas.DISPARADORES}
    huerfanas = [
        n for n, spec in herramientas.HERRAMIENTAS.items()
        if not spec.get("solo_lectura") and n not in con_disparador
    ]
    assert not huerfanas, f"sin disparador, invisibles sin llave: {huerfanas}"


def test_ningun_disparador_apunta_a_una_herramienta_que_no_existe():
    nombres = set(herramientas.HERRAMIENTAS)
    perdidos = [n for n, _, _ in herramientas.DISPARADORES if n not in nombres]
    assert not perdidos


def test_el_redespliegue_militar_no_se_niega_a_si_mismo(estado):
    """«Redesplegar militares a la refinería» decía que eso no existe. Existe."""
    a = solo(estado, "redesplegar militares a infraestructura")
    assert a.herramienta == "redesplegar_militares"
    assert a.argumentos["modo"] == "infraestructura"


def test_la_mesa_del_alcalde_no_es_la_del_interior(estado):
    """
    Son dos acciones distintas con dos jurisdicciones opuestas: la del Alcalde
    **solo** vale en el epicentro; la del Interior en el epicentro exige que
    esté la Alcaldía. Confundirlas cambia de dueño la palanca sin decirlo.
    """
    a = solo(estado, "instalar mesa con voceros en Barrio Las Palmas")
    assert a.herramienta == "mesa_con_voceros"
    assert a.rol == "Alcalde"


def test_una_raiz_tiene_que_aguantar_la_conjugacion(estado):
    """
    `condicionar` es un infinitivo, no una raíz: «el Alcalde condiciona el
    empleo de la fuerza» no disparaba nada. La gente conjuga.
    """
    a = solo(estado, "el Alcalde condiciona el empleo de la fuerza en su jurisdiccion")
    assert a.herramienta == "condicionar_empleo_fuerza"


# ===========================================================================
# EL CANAL NO SE CONCEDE REQUISITOS A SÍ MISMO
#
# `AbrirMesaLocal` exige a la Alcaldía en la jurisdicción del epicentro: es la
# única puerta que obliga al Interior a traer al Alcalde a la mesa. El
# constructor de la herramienta ponía `con_alcaldia=True` cuando nadie lo había
# dicho, y esa puerta **no se cerró nunca por el canal**.
# ===========================================================================

def test_el_canal_no_se_da_a_si_mismo_la_alcaldia(estado):
    a = solo(estado, "concertar en el Puente Amarillo")
    assert a.argumentos["con_alcaldia"] is False
    assert a.estado == "no_viable"
    assert "Alcaldía" in (a.motivo or "")
    assert a.habilitada_por, "y se dice quién puede habilitarla"


def test_la_alcaldia_dicha_si_cuenta(estado):
    a = solo(estado, "concertar en el Puente Amarillo con la Alcaldia")
    assert a.argumentos["con_alcaldia"] is True
    assert a.estado == "lista"


def test_la_ausencia_de_la_alcaldia_se_dice_en_voz_alta(estado):
    """
    El resto de booleanos solo se dicen cuando son ciertos —«sin dupla» en cada
    línea sería ruido—. Este se dice en los dos sentidos, porque su ausencia es
    lo que hace inviable la acción y la sala tiene que oírlo ANTES.
    """
    a = solo(estado, "concertar en el Puente Amarillo")
    assert "SIN la Alcaldía" in a.en_claro()


def test_el_mitigador_de_la_alcaldia_no_abre_una_mesa_aparte(estado):
    """
    «Operen X concertado con la Alcaldía» no son dos acciones. La raíz «concert»
    abría una mesa que nadie pidió y **se llevaba el resto de la frase**: la
    operación se quedaba sin el mitigador y sin el responsable que venían detrás.
    """
    a = solo(estado, "operen el Puente Amarillo con ESMAD, concertado con la "
                     "Alcaldia, responsable el Ministro de Defensa")
    assert a.herramienta == "operar_punto"
    assert a.argumentos["concertado_con_alcaldia"] is True
    assert a.argumentos["responsable_nominado"] == "Ministro de Defensa"


def test_quien_firma_la_orden_se_extrae(estado):
    """
    `responsable_nominado` no es adorno: con el registro escrito adoptado es lo
    que hace ATRIBUIBLE un incidente, y la vista privada muestra «— SIN NOMBRE
    —» cuando falta. Sin extraerlo, esa mecánica moría al correr sin llave.
    """
    a = solo(estado, "operen el Puente Amarillo, responsable: el Presidente")
    assert a.argumentos["responsable_nominado"] == "Presidente"


# ===========================================================================
# LAS CANTIDADES Y LOS VALORES POR DEFECTO
#
# Es N4 otra vez, con una cifra en lugar de una unidad: la orden se ejecuta con
# un valor que nadie pidió y la lectura en voz alta no lo dice, así que la sala
# no tiene dónde notarlo.
# ===========================================================================

def test_una_cantidad_dicha_no_se_sustituye_por_la_de_por_defecto(estado):
    p = plan(estado, "concentrar 8 escuadrones del ESMAD y relevar 4 unidades")
    por_nombre = {a.herramienta: a for a in p.acciones}
    assert por_nombre["disponer_esmad"].argumentos["n_escuadrones"] == 8
    assert por_nombre["relevar_unidades"].argumentos["n_unidades"] == 4


def test_una_cantidad_dictada_en_letras_tambien_cuenta(estado):
    """La sala dicta en voz alta y quien transcribe escribe lo que oye."""
    a = solo(estado, "concentrar ocho escuadrones del ESMAD")
    assert a.argumentos["n_escuadrones"] == 8


def test_un_margen_dicho_no_se_sustituye(estado):
    """
    ERA UN DECIMAL Y SON DOS PALABRAS. El motor comparaba `margen` una sola vez
    contra 0,25, así que «0,3» y «1,0» hacían lo mismo: la consola pedía un
    número del que solo dos valores significaban algo distinto, y el plan se lo
    leía de vuelta a la sala como si fuera un dial.

    Lo que la prueba sigue exigiendo es lo mismo: **lo que la sala dijo no se
    sustituye por el valor por defecto.**
    """
    a = solo(estado, "fijar lineas rojas sin margen")
    assert a.argumentos["margen"] == "estrecho"
    assert "SIN margen" in a.en_claro()


def test_el_margen_por_defecto_es_amplio_y_se_dice(estado):
    """Y si no se dice nada, queda el amplio — y la sala tiene que oírlo."""
    a = solo(estado, "fijar las lineas rojas del Ejecutivo")
    assert a.argumentos["margen"] == "amplio"
    assert "con margen" in a.en_claro()


def test_el_valor_por_defecto_viaja_en_el_plan_y_se_dice(estado):
    """
    Estaban escondidos dentro de `construir`: la acción se ejecutaba con ESMAD y
    con seis escuadrones, y como el argumento no estaba en `argumentos`, la
    lectura no lo decía. La sala confirmaba una cosa y el motor hacía otra.
    """
    a = solo(estado, "despejen el Alto del Mirador")
    assert a.argumentos["tipo_unidad"] == "esmad"
    assert "con ESMAD" in a.en_claro()

    b = solo(estado, "concentrar el ESMAD")
    assert b.argumentos["n_escuadrones"] == 6
    assert "6 escuadrón(es)" in b.en_claro()


def test_la_firma_sin_delimitar_se_dice_en_voz_alta(estado):
    """
    El valor por defecto más caro del repertorio: firmar sin delimitar cuesta
    −22 de respaldo internacional frente a −8, entrega el encuadre de represión
    y dispara «militares en control de multitudes». Y era el que no se decía.
    """
    a = solo(estado, "firmar la asistencia militar")
    assert a.argumentos["delimitada"] is False
    assert "SIN límites" in a.en_claro()

    b = solo(estado, "firmar la asistencia militar delimitada")
    assert b.argumentos["delimitada"] is True
    assert "con límites escritos" in b.en_claro()


def test_todo_valor_por_defecto_declarado_se_puede_decir_en_voz_alta():
    """
    Un valor por defecto que el motor usa y la lectura calla es exactamente el
    agujero que esta tanda cerró. Que no se vuelva a abrir al añadir el
    siguiente.
    """
    mudos = []
    for nombre, spec in herramientas.HERRAMIENTAS.items():
        for campo in spec.get("por_defecto", {}):
            if campo in ("nodo_id", "corredor_id", "region_id", "puntos"):
                continue
            if campo not in nlu.ARGUMENTOS_EN_CLARO and campo != "tipo_unidad":
                mudos.append(f"{nombre}.{campo}")
    assert not mudos, f"valor por defecto que nadie oye: {mudos}"


# ===========================================================================
# LO QUE LA SALA OYE · segunda tanda
# ===========================================================================

def test_la_lectura_dice_de_que_rol_es_cada_accion(estado):
    """
    En un ejercicio cuyo objeto es quién tiene qué palanca, que la lectura no
    dijera de quién era la acción hacía inaudible una sustitución de rol.
    """
    lectura = plan(estado, "operen el Puente Amarillo").lectura()
    assert "[Ministro de Defensa]" in lectura


def test_la_lectura_cuenta_cuantos_puntos_entendio(estado):
    """
    Si la sala nombró tres y oye dos, la resta la hace ella. Es el único aviso
    posible cuando el tercero ni se reconoció como nombre — que es justo lo que
    pasa en la rama sin modelo.
    """
    a = nlu._a_accion_plan(estado, {"nombre": "desplegar_equipos", "argumentos": {
        "puntos": ["Puente Amarillo", "Puente de Brooklyn", "Alto del Mirador"]}})
    assert "Sobre 2:" in a.en_claro()
    assert "Puente de Brooklyn" in (a.motivo or "")


def test_casi_no_es_una_condicion(estado):
    """
    Con «si » a secas, «casi todos los puntos» disparaba el aviso de condicional.
    Un aviso que salta cuando no toca se deja de leer — y entonces tampoco se lee
    el que sí importa.
    """
    p = plan(estado, "casi todos los puntos siguen cerrados: operen el Puente Amarillo")
    assert not any("condición" in a for a in p.avisos)


def test_la_condicion_de_verdad_sigue_avisando(estado):
    p = plan(estado, "si la Defensoria verifica el Puente Amarillo, operenlo")
    assert any("condición" in a for a in p.avisos)


# ===========================================================================
# LA CONSOLA · segunda tanda
# ===========================================================================

def test_preguntar_no_gasta_un_turno(consola):
    """
    La hoja de datos ya viaja dentro del plan y se lee sin ejecutar nada. Pero
    `/ejecutar` corría `motor.paso()` igual: la sala preguntaba cuánto oxígeno
    quedaba, pulsaba el botón grande, y se le iba **una de las cinco ventanas**.
    """
    antes = consola.get("/api/tablero").json()["turno_decision"]
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "cuanto oxigeno queda?"}).json()
    r = consola.post("/api/consola/ejecutar",
                     json={"plan_id": p["plan_id"]}).json()
    assert r["turno_avanzado"] is False
    assert consola.get("/api/tablero").json()["turno_decision"] == antes


def test_una_orden_de_verdad_si_gasta_el_turno(consola):
    """La contraparte de la anterior: lo que no puede pasar es congelar el reloj."""
    antes = consola.get("/api/tablero").json()["turno_decision"]
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente Amarillo"}).json()
    r = consola.post("/api/consola/ejecutar",
                     json={"plan_id": p["plan_id"]}).json()
    assert r["turno_avanzado"] is True
    assert consola.get("/api/tablero").json()["turno_decision"] > antes


def test_corregir_un_punto_de_una_lista_completa_en_vez_de_borrar(consola):
    """
    `desplegar_equipos` lleva tres puntos en un solo acto. Elegir el que faltaba
    sustituía la lista entera por un texto suelto: el botón de corregir dejaba
    la orden peor que antes.
    """
    p = consola.post("/api/consola/interpretar", json={
        "texto": "asignar duplas al Puente Amarillo y al Alto del Mirador"}).json()
    assert p["acciones"][0]["argumentos"]["puntos"] == ["N003", "N004"]

    p2 = consola.post("/api/consola/elegir", json={
        "plan_id": p["plan_id"], "indice": 0,
        "campo": "puntos", "valor": "N012"}).json()
    assert p2["acciones"][0]["argumentos"]["puntos"] == ["N003", "N004", "N012"]
    assert p2["acciones"][0]["estado"] == "lista"


def test_cada_entidad_dice_de_que_campo_salio(consola):
    """
    La pantalla adivinaba el campo buscando el valor crudo entre los argumentos.
    Para los campos de lista no aparecía nunca —los que no resuelven no se
    guardan—, caía en `nodo_id`, y la corrección moría en un 400.
    """
    p = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el puente"}).json()
    assert p["acciones"][0]["entidades"][0]["campo"] == "nodo_id"


# ===========================================================================
# QUE LA SUITE NO SALGA A LA RED
#
# La cabecera de este archivo decía que ninguna prueba llamaba a un modelo, y
# era falso por la mitad que nadie miró: el accesorio silenciaba `nlu`, y las
# cinco pruebas que pasan por `/ejecutar` disparaban después la CAPA 3 con el
# cliente real. Medido: 176 s y llamadas facturadas en cada corrida.
# ===========================================================================

def test_las_dos_capas_estan_silenciadas_en_las_pruebas():
    from src.agents import entorno
    assert nlu.cliente() is None, "la capa 4 sale a la red"
    assert entorno.cliente() is None, "la capa 3 sale a la red"


# ===========================================================================
# EL PRESUPUESTO DE LATENCIA · B5
#
# «Presupuesto de tiempo duro», decía la cabecera de `entorno.py`, y no lo era:
# el SDK reintenta dos veces de fábrica, así que un presupuesto de 12 s se
# convertía en tres intentos y hasta 36 s de reloj. Medido en una sonda real:
# 35,3 s con el presupuesto puesto en 12.
# ===========================================================================

def test_el_presupuesto_de_latencia_es_el_que_se_declara(monkeypatch):
    """
    Sobre los valores POR DEFECTO, no sobre el `.env` de quien corre esto: una
    prueba que lee la configuración local falla en la máquina de al lado y no
    dice nada del código.
    """
    # `src/agents/__init__.py` reexporta la FUNCIÓN `config`, que tapa al módulo
    # del mismo nombre: `from src.agents import config` no trae lo que parece.
    mod = importlib.import_module("src.agents.config")

    for var in ("REINTENTOS_LLM", "TIMEOUT_NLU", "TIMEOUT_ENTORNO"):
        monkeypatch.delenv(var, raising=False)
    mod.config.cache_clear()
    try:
        c = mod.config()
        assert c.reintentos == 0, (
            "con reintentos, la espera real es el presupuesto multiplicado")
        d = c.diagnostico()
        assert d["espera_maxima_nlu_s"] == c.timeout_nlu
        assert d["espera_maxima_entorno_s"] == c.timeout_entorno
    finally:
        mod.config.cache_clear()


def test_el_esfuerzo_de_razonamiento_se_manda_solo_si_esta_puesto():
    """
    Vacío = no se manda el parámetro. Hace falta para apuntar a un modelo que no
    razona o a otro proveedor, que lo rechazarían con un 400 — y entonces el
    canal degradaría en todos los turnos.
    """
    Config = importlib.import_module("src.agents.config").Config
    puesto = Config(api_key="x", base_url=None, modelo_nlu="m", modelo_entorno="m",
                    timeout_nlu=1, timeout_entorno=1, reintentos=0,
                    esfuerzo_nlu="low", esfuerzo_entorno="low")
    assert puesto.extra_nlu() == {"reasoning_effort": "low"}
    assert puesto.extra_entorno() == {"reasoning_effort": "low"}

    vacio = Config(api_key="x", base_url=None, modelo_nlu="m", modelo_entorno="m",
                   timeout_nlu=1, timeout_entorno=1, reintentos=0,
                   esfuerzo_nlu="", esfuerzo_entorno="")
    assert vacio.extra_nlu() == {}
    assert vacio.extra_entorno() == {}


# ===========================================================================
# LA CAPA 3 · solo publican las seis
#
# El campo `fuente` volvía unas veces como clave y otras como nombre para
# mostrar, y la pantalla rotula por clave. Y un `fuente` inventado es contenido
# atribuido a un medio que no existe, en un ejercicio cuyo objeto es la
# distancia entre lo que el Estado tiene por cierto y lo que se dice.
# ===========================================================================

def test_la_esfera_publica_normaliza_la_fuente_al_nombre_canonico():
    from src.agents import entorno
    pubs = entorno._de_fuentes_conocidas([
        {"fuente": "Prensa nacional", "texto": "algo"},
        {"fuente": "redes", "texto": "algo"},
    ])
    assert [p["fuente"] for p in pubs] == ["prensa_nacional", "redes"]


def test_la_esfera_publica_no_atribuye_a_un_medio_que_no_existe():
    from src.agents import entorno
    pubs = entorno._de_fuentes_conocidas([
        {"fuente": "El Tiempo", "texto": "algo"},
        {"fuente": "prensa_nacional", "texto": ""},
        {"fuente": "prensa_nacional", "texto": "algo"},
    ])
    assert len(pubs) == 1, "ni medios inventados ni publicaciones vacías"


def test_sin_llave_la_esfera_publica_usa_plantilla_y_lo_dice(estado):
    """
    La degradación es la prueba operativa de que ninguna decisión de la
    simulación se delegó al modelo.
    """
    from src.agents import entorno
    r = entorno.publicaciones(
        estado, [{"tipo": "apertura", "nodo": "N003", "via": "fuerza"}])
    assert r["publicaciones"]
    assert "plantilla" in r["generado_por"]
    conocidas = set(entorno.AGENTES)
    assert all(p["fuente"] in conocidas for p in r["publicaciones"])



# ===========================================================================
# LO QUE NADIE DIJO NO SE DA POR PUESTO
#
# Hay booleanos que no describen la orden: CONCEDEN un requisito o rebajan un
# riesgo. El sistema ya se lo pide al modelo y aun así lo hace — medido:
# «concertar en el Puente Amarillo» volvía con `con_alcaldia: true` sin que
# nadie hubiera nombrado a la Alcaldía. Misma lección que ENUMS: restringir la
# salida no impide que el modelo se salga, así que la comprobación es
# determinista.
# ===========================================================================

def test_el_modelo_no_puede_concederse_la_alcaldia(estado):
    """El caso medido, tal cual volvió del modelo."""
    a = nlu._a_accion_plan(
        estado,
        {"nombre": "abrir_mesa_local",
         "argumentos": {"nodo_id": "N003", "con_alcaldia": True}},
        "concertar en el Puente Amarillo")
    assert a.argumentos["con_alcaldia"] is False
    assert a.estado == "no_viable"
    assert a.correcciones, "y se dice que se quitó, no se quita en silencio"


def test_lo_que_la_sala_si_dijo_se_respeta(estado):
    a = nlu._a_accion_plan(
        estado,
        {"nombre": "abrir_mesa_local",
         "argumentos": {"nodo_id": "N003", "con_alcaldia": True}},
        "concertar en el Puente Amarillo con la Alcaldia")
    assert a.argumentos["con_alcaldia"] is True
    assert not a.correcciones


def test_la_correccion_solo_baja_concesiones_nunca_las_sube(estado):
    """
    Si la sala lo dijo y el modelo no lo puso, **no se añade**: añadir también
    sería el canal decidiendo. Se queda en su valor declarado, se dice en voz
    alta, y la sala lo corrige con un botón.
    """
    a = nlu._a_accion_plan(
        estado,
        {"nombre": "operar_punto", "argumentos": {"nodo_id": "N003"}},
        "operen el Puente Amarillo con dupla de la Defensoria")
    # Ausente es lo mismo que falso, y aquí se prefiere ausente: la dupla que
    # falta ya sale nombrada en los «mitigadores ausentes» de la banda de
    # riesgo, que es más fuerte que una línea más de argumento.
    assert not a.argumentos.get("dupla_presente")
    assert not a.correcciones


def test_la_correccion_se_lee_en_voz_alta(estado):
    p = nlu.Plan(plan_id="x", texto_original="firmar la asistencia militar")
    p.acciones.append(nlu._a_accion_plan(
        estado,
        {"nombre": "firmar_asistencia_militar",
         "argumentos": {"delimitada": True}},
        "firmar la asistencia militar"))
    assert "no se da por puesto" in p.lectura()


def test_una_eleccion_tipada_no_pasa_por_la_correccion(estado):
    """
    La corrección contrasta contra el texto de la sala. Una elección tipada
    **es** la sala hablando, así que no se le aplica: si no, el botón no podría
    arreglar nunca lo que la corrección quitó.
    """
    a = nlu._a_accion_plan(
        estado,
        {"nombre": "abrir_mesa_local",
         "argumentos": {"nodo_id": "N003", "con_alcaldia": True}})
    assert a.argumentos["con_alcaldia"] is True


# ===========================================================================
# CADA CAMPO, EN SU TIPO
#
# `bool("false")` es `True`, y el `valor` de una elección tipada viaja siempre
# como cadena.
# ===========================================================================

def test_un_no_escrito_en_texto_no_se_convierte_en_si():
    spec = herramientas.HERRAMIENTAS["firmar_asistencia_militar"]
    args, avisos = herramientas.coercionar_tipos(spec, {"delimitada": "false"})
    assert args["delimitada"] is False and not avisos

    args, _ = herramientas.coercionar_tipos(spec, {"delimitada": "sí"})
    assert args["delimitada"] is True


def test_un_numero_que_llega_como_texto_se_convierte():
    spec = herramientas.HERRAMIENTAS["disponer_esmad"]
    args, avisos = herramientas.coercionar_tipos(spec, {"n_escuadrones": "8"})
    assert args["n_escuadrones"] == 8 and not avisos


def test_lo_que_no_se_puede_convertir_se_avisa_y_no_se_inventa(estado):
    a = nlu._a_accion_plan(estado, {"nombre": "disponer_esmad",
                                    "argumentos": {"n_escuadrones": "unos pocos"}})
    assert a.estado == "falta_dato"
    assert "no es un número" in (a.motivo or "")


# ===========================================================================
# DE NOCHE NO SE ORDENA, Y NO ES UN RÓTULO
#
# La jornada son quince minutos: trece de día en que se ordena y dos de noche en
# que no. La consola se apaga sola — pero apagar una pantalla no cierra un canal:
# basta una pestaña vieja abierta, o un doble clic tardío, para meter una orden
# en mitad de las consecuencias.
#
#     Una regla que el software garantiza vale más que una que el software
#     recomienda.
# ===========================================================================

def test_de_noche_el_canal_de_ordenes_esta_cerrado(consola):
    consola.post("/api/consola/reloj/iniciar")
    assert consola.get("/api/tablero").json()["admite_ordenes"] is True

    consola.post("/api/consola/reloj/noche")
    t = consola.get("/api/tablero").json()
    assert (t["fase"], t["admite_ordenes"]) == ("noche", False)

    for ruta, cuerpo in (("interpretar", {"texto": "operen el Puente Amarillo"}),
                         ("encolar", {"plan_id": "x"}),
                         ("ejecutar", {"plan_id": "x"}),
                         ("resolver", None)):
        r = consola.post(f"/api/consola/{ruta}", json=cuerpo)
        assert r.status_code == 409, ruta
        assert "de noche" in r.json()["detail"]


def test_con_el_reloj_parado_se_puede_transcribir_siempre(consola):
    """
    Montar y depurar no debería exigir cronometrar una sala. Mientras nadie pulse
    «Iniciar», el canal se comporta como antes de que hubiera reloj.
    """
    r = consola.post("/api/consola/interpretar",
                     json={"texto": "operen el Puente Amarillo"})
    assert r.status_code == 200


def test_el_reloj_encadena_las_jornadas(consola):
    consola.post("/api/consola/reloj/iniciar")
    t = consola.get("/api/tablero").json()
    assert (t["reloj"]["jornada"], t["reloj"]["fecha"]) == (1, "11 de mayo")

    consola.post("/api/consola/reloj/noche")
    consola.post("/api/consola/reloj/jornada")
    t = consola.get("/api/tablero").json()
    assert (t["reloj"]["jornada"], t["reloj"]["fecha"]) == (2, "12 de mayo")
    assert t["admite_ordenes"] is True


def test_las_consecuencias_se_sirven_durante_la_noche(consola):
    """
    Los dos minutos de noche existen para leerlas. Si hubiera que ir a buscarlas
    a cinco tarjetas distintas, no daría tiempo.
    """
    consola.post("/api/consola/reloj/iniciar")
    assert consola.get("/api/tablero").json()["consecuencias"] is None

    consola.post("/api/consola/reloj/noche")
    c = consola.get("/api/tablero").json()["consecuencias"]
    assert c and c["jornada"] == 1 and c["resumen"]

    # Y se retiran al abrir la jornada siguiente: son de la que acaba de pasar.
    consola.post("/api/consola/reloj/jornada")
    assert consola.get("/api/tablero").json()["consecuencias"] is None


def test_pausar_detiene_el_reloj_de_las_diez_pantallas(consola):
    """
    El mando de las interrupciones reales. El tiempo del ejercicio no corre
    mientras la sala no está en el ejercicio.
    """
    consola.post("/api/consola/reloj/iniciar")
    c = consola.post("/api/consola/reloj/pausa").json()
    assert c["pausado"] is True and c["pausa_desde"] is not None

    c = consola.post("/api/consola/reloj/pausa").json()
    assert c["pausado"] is False and c["pausa_desde"] is None


def test_el_ejercicio_se_cierra_con_la_quinta_jornada(consola):
    consola.post("/api/consola/reloj/iniciar")
    for _ in range(5):
        consola.post("/api/consola/reloj/noche")
        consola.post("/api/consola/reloj/jornada")

    t = consola.get("/api/tablero").json()
    assert t["cronometro"]["cerrado"] is True
    assert t["reloj"]["jornada"] == 5
    r = consola.post("/api/consola/interpretar", json={"texto": "operen el puente"})
    assert r.status_code == 409 and "terminó" in r.json()["detail"]
