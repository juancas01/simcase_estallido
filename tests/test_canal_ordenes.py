"""
test_canal_ordenes.py — La capa 4, que es la que habla con personas.

    El LLM traduce. El motor decide, valida, ejecuta y reporta.

Hasta esta tanda, **la capa 4 no tenía ni una sola prueba**. Sesenta y tres
verificadores custodiaban el motor —que nadie toca durante el ejercicio— y cero
custodiaban el canal por el que entran las órdenes de ocho personas en dos horas.
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
    assert all("Puente" in n for n in nombres)


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
    a = solo(estado, "operen el Anillo hospitalario")
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

    assert operar.estado == "ambigua", "«el puente» sigue siendo tres puentes"
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
    p = plan(estado, "operen todos los puntos")
    assert len(p.acciones) == nlu.TOPE_ACCIONES
    assert len({a.argumentos["nodo_id"] for a in p.acciones}) == nlu.TOPE_ACCIONES
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
    assert a.herramienta == "asignar_duplas"
    assert a.argumentos["puntos"], "el criterio tiene que expandirse"


def test_verificar_sin_decir_que_no_es_viable(estado, motor):
    """La misma regla, custodiada también desde el motor."""
    from src.engine.actions import AsignarDuplas
    v = AsignarDuplas(nodos=[], denuncias=[]).validar(estado)
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
    Un error del proveedor no puede dejar a ocho personas mirando la pantalla. Y
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
