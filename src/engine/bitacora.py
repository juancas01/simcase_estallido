"""
bitacora.py — El archivo de la corrida (`B1`).

La corrida entera vive hoy en memoria: `estado.registro`, `historial`, la
`semilla`. Cuando el proceso muere, muere todo — y el debriefing se hace con
la sala todavía sentada y el proceso todavía vivo, o no se hace.

Este módulo es la única pieza que escribe a disco, y escribe **una sola cosa**:
un archivo JSONL de solo anexado por corrida.

    corridas/2026-08-31-1842/corrida.jsonl

POR QUÉ DE ANEXADO Y NO UN VOLCADO AL FINAL
-------------------------------------------
Si el proceso se cae a mitad del ejercicio, sobrevive todo lo anterior. Un
volcado final lo pierde todo — y una caída durante la corrida es exactamente
cuando más falta hace el registro. Cada línea lleva su marca temporal, que es
la que permite medir dónde se fue el tiempo.

LAS SEIS CLASES DE LÍNEA
------------------------
    apertura   semilla e indicadores de partida, al primer anexo
    linea      lo que cada rol declaró en el turno 0
    orden      lo que la sala dictó y cómo lo tradujo el canal
    decision   cada decisión ejecutada, con su VÍA y su PÚBLICO resueltos
    ventana    indicadores, deltas, eventos y semáforo por región al cerrar
               cada paso — el desarrollo de las métricas, jornada a jornada
    cierre     métricas, proyección y la lectura completa de la corrida

La `decision` lleva la imputación que declara cada acción (`via`, `atiende`,
ver `docs/LA_MEDICION.md` §4). No va en `Decision` ni en `Estado` a propósito:
`/api/tablero` serializa el registro tal cual, y el vocabulario de la lectura
no puede salir antes del cierre (§7).

LO QUE ESTO NO ES
-----------------
No permite *reanudar* la corrida: eso exigiría serializar el estado entero.
Con la semilla y las órdenes, **repetirla** cambiando una decisión es exacto —
y eso es la mejor herramienta del debriefing, no una consola de rebobinado.

Y UNA REGLA QUE VIENE DE LA SIMULACIÓN ANTERIOR
-----------------------------------------------
Que el código anote el dato no basta: hay que comprobar que **llega al
archivo**. Allí dos campos se perdían en la serialización y ninguna prueba lo
detectó, porque las pruebas miraban el código y no el archivo escrito. Las
pruebas de `tests/test_bitacora.py` leen el `.jsonl`.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIR_POR_DEFECTO = RAIZ / "corridas"

# Valores que apagan la bitácora desde el entorno. La suite de pruebas los usa
# para no sembrar carpetas de corrida en el repositorio con cada `reload` del
# módulo de la API; el único test que escribe de verdad apunta a `tmp_path`.
# Sin variable, la bitácora VA ENCENDIDA: es la condición de `B1`, que lo
# escrito sobreviva al proceso.
_APAGADO = {"off", "0", "no", "false"}


class Bitacora:
    """
    El escritor del archivo de la corrida.

    Es deliberadamente tonta: recibe líneas y las anexa. No lee el estado, no
    calcula nada y no sabe que existe un motor — así ninguna superficie en vivo
    puede importarla «solo para mirar» y arrastrar el vocabulario del cierre a
    mitad de la jornada.

    UNA BITÁCORA ROTA NO PUEDE TUMBAR EL EJERCICIO. Si el disco falla en plena
    corrida, lo caro es la corrida: la bitácora se desactiva, deja constancia
    en stderr y el motor sigue. Perder el registro es un daño; detener la sala
    por él sería dos.
    """

    def __init__(self, raiz: Path | None = None, *, activa: bool = True):
        self.raiz = Path(raiz) if raiz is not None else DIR_POR_DEFECTO
        self.activa = activa
        self.ruta: Path | None = None
        self.lineas = 0
        # La `apertura` se escribe perezosamente, con el primer anexo que
        # llegue: así el archivo empieza donde empieza la corrida de verdad,
        # y un proceso que solo carga y no corre no siembra carpetas vacías.
        self._apertura_escrita = False
        self._semilla: int | None = None
        self._indicadores_t0: dict = {}

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    @classmethod
    def inactiva(cls) -> "Bitacora":
        """La bitácora que no escribe: la que usa el motor cuando nadie la pidió."""
        return cls(activa=False)

    @classmethod
    def desde_entorno(cls) -> "Bitacora":
        """
        La que usa la API al arrancar.

        `SIMCASE_BITACORA=off` la apaga (pruebas) y `SIMCASE_CORRIDAS=<dir>`
        la redirige (también pruebas: `tmp_path`). Sin ninguna de las dos,
        escribe en `corridas/` desde la raíz del repositorio.
        """
        if os.environ.get("SIMCASE_BITACORA", "").strip().lower() in _APAGADO:
            return cls.inactiva()
        raiz = os.environ.get("SIMCASE_CORRIDAS", "").strip()
        return cls(Path(raiz)) if raiz else cls()

    # ------------------------------------------------------------------
    # El anexo
    # ------------------------------------------------------------------

    def _abrir(self) -> bool:
        try:
            carpeta = self.raiz / datetime.now().strftime("%Y-%m-%d-%H%M%S")
            carpeta.mkdir(parents=True, exist_ok=True)
            self.ruta = carpeta / "corrida.jsonl"
            return True
        except OSError as exc:
            self._renderse(f"No se pudo crear la carpeta de corrida: {exc}")
            return False

    def _renderse(self, motivo: str) -> None:
        print(f"[bitacora] desactivada: {motivo}", file=sys.stderr)
        self.activa = False

    def _anexar(self, t: str, linea: dict) -> None:
        if not self.activa:
            return
        if self.ruta is None and not self._abrir():
            return
        registro = {"t": t, "ts": round(time.time(), 3), **linea}
        try:
            texto = json.dumps(registro, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            # No perder la corrida por un valor raro: se anota el problema y se
            # reintenta con `default=str`, que degrada el valor y no la línea.
            print(f"[bitacora] valor no serializable ({exc}); "
                  f"línea «{t}» anotada con `str()`.", file=sys.stderr)
            texto = json.dumps(registro, ensure_ascii=False, default=str)
        try:
            with self.ruta.open("a", encoding="utf-8") as f:
                f.write(texto + "\n")
            self.lineas += 1
        except OSError as exc:
            self._renderse(f"el disco rechazó el anexo: {exc}")

    def _asegurar_apertura(self) -> None:
        if self._apertura_escrita:
            return
        self._apertura_escrita = True
        self._anexar("apertura", {
            "creada": datetime.now().isoformat(timespec="seconds"),
            "semilla": self._semilla,
            "indicadores": self._indicadores_t0,
        })

    # ------------------------------------------------------------------
    # Las seis clases de línea
    # ------------------------------------------------------------------

    def fijar_apertura(self, semilla: int, indicadores: dict) -> None:
        """
        La partida, para escribir con la primera línea que llegue.

        Semilla e indicadores de arranque: sin ellos no hay contra qué comparar
        la primera ventana, y la semilla es lo que permite repetir la corrida
        con una decisión cambiada.
        """
        self._semilla = semilla
        self._indicadores_t0 = indicadores

    def linea(self, rol: str, linea: str) -> None:
        """Lo que cada rol declaró en el turno 0."""
        self._asegurar_apertura()
        self._anexar("linea", {"rol": rol, "linea": linea})

    def orden(self, ventana: int, dictado: str, acciones: list[str],
              plan_id: str = "") -> None:
        """Lo que la sala dictó y qué acciones tradujo el canal."""
        self._asegurar_apertura()
        self._anexar("orden", {"ventana": ventana, "dictado": dictado,
                               "acciones": acciones, "plan": plan_id})

    def decision(self, ventana: int, rol: str, accion: str, nombre: str,
                 descripcion: str, responsable: str | None,
                 via: tuple | list, atiende: tuple | list) -> None:
        """
        Una decisión del pliego, con su imputación resuelta.

        La vía y el público se declaran en la acción (`Accion.imputacion`) y se
        resuelven AL EJECUTAR, porque cuatro de ellas se imputan por su objeto:
        el orden que fijaron, la carga que escoltaron, la región del punto.
        """
        self._asegurar_apertura()
        self._anexar("decision", {
            "ventana": ventana, "rol": rol, "accion": accion,
            "nombre": nombre, "descripcion": descripcion,
            "responsable": responsable,
            "via": list(via), "atiende": list(atiende),
        })

    def ventana(self, n: int, franja: str, indicadores: dict, deltas: dict,
                eventos: list[dict], regiones: dict,
                mitigadores: list[str]) -> None:
        """
        El cierre de un paso: el desarrollo de las métricas.

        Indicadores y deltas son los que ya ve la sala; el semáforo por región
        y los mitigadores activos solo viven aquí, porque son lo que la lectura
        necesita para reconstruir cómo estaba el país en cada ventana — y son
        exactamente lo que no puede dibujarse en vivo sin volverlos marcador.
        """
        self._asegurar_apertura()
        self._anexar("ventana", {
            "n": n, "franja": franja,
            "indicadores": indicadores, "deltas": deltas,
            "eventos": eventos, "regiones": regiones,
            "mitigadores": mitigadores,
        })

    def cierre(self, metricas: dict, proyeccion: dict, lectura: dict) -> None:
        """El cierre: métricas, el país proyectado sin mando y la lectura."""
        self._asegurar_apertura()
        self._anexar("cierre", {"metricas": metricas,
                                "proyeccion": proyeccion,
                                "lectura": lectura})
