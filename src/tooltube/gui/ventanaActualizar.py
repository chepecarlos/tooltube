from nicegui import ui, app
import asyncio

import os
from pathlib import Path

from tooltube.minotion.minotion import actualizarNotion, crearNotion
from tooltube.tooltube_analisis import actualizarIconos
import tooltube.miLibrerias as miLibrerias


class ventanaActualizar:
    """
    Ventana para actualizar el estado de un proyecto.
    """

    folder: str
    "Ruta del Proyecto"

    actualizandoSistema: bool = False
    "Indica si se está actualizando el sistema"

    pararActualizar: bool = False
    "Indica si se debe parar la actualización"

    def __init__(self, ruta: str):
        self.folder = ruta

    def ejecutar(self):

        with ui.column().classes("fixed-center"):
            with ui.column().classes("w-full items-center"):
                with ui.row():
                    ui.label(f"Folder: {self.folder}")
                    self.textLog = ui.log().classes("w-full h-80")
                    self.barraProgreso = ui.linear_progress(show_value=False, size="30px")

                    with ui.column().classes("w-full items-center"):
                        with ui.row():
                            ui.button("Actualizar", on_click=self.iniciar_actualizar)
                            ui.button("Parar", on_click=self.parar_actualizar, color="red")
                            ui.button("Limpiar", on_click=self.limpiar, color="green")

        ui.run(native=True, reload=False, dark=True, language="es", title="Actualizar Proyectos")

    def limpiar(self):
        """
        Limpiar el log de la ventana.
        """
        self.textLog.clear()

    def parar_actualizar(self):
        """
        Parar la actualización del sistema.
        """
        self.pararActualizar = True

    async def iniciar_actualizar(self):

        if self.actualizandoSistema:
            return

        self.actualizandoSistema = True

        self.barraProgreso.value = 0
        self.textLog.push(f"Empezar a Actualizar Proyectos")
        self.listaProyectos = self.calcularListaProyectos()

        self.textLog.push(f"Cantidad Proyectos: {len(self.listaProyectos)}")

        for proyecto in self.listaProyectos:
            if self.pararActualizar:
                self.textLog.push("Actualización parada por el usuario.")
                self.pararActualizar = False
                self.actualizandoSistema = False
                await asyncio.sleep(0.1)
                return
            nombreProyecto = proyecto.get("nombre")
            archivoInfo = proyecto.get("info")
            folderProyecto = proyecto.get("ruta")

            self.textLog.push(f"Proyecto: {nombreProyecto}")
            await asyncio.sleep(0.1)

            seActualizoNotion = actualizarNotion(archivoInfo)
            if seActualizoNotion is None:
                crearNotion(folderProyecto)
                actualizarNotion(archivoInfo)
            actualizarIconos(folderProyecto)

            error = miLibrerias.ObtenerValor(archivoInfo, "error", "no-error")
            terminar = miLibrerias.ObtenerValor(archivoInfo, "terminado", False)

            if error == "no-notion":
                self.textLog.push(f"Error: no-notion")
            elif terminar:
                self.textLog.push(f"Estado: Terminado")
            else:
                estado = miLibrerias.ObtenerValor(archivoInfo, "estado")
                asignado = miLibrerias.ObtenerValor(archivoInfo, "asignado")
                canal = miLibrerias.ObtenerValor(archivoInfo, "canal")
                self.textLog.push(f"Estado: {estado}")
                self.textLog.push(f"Asignado: {asignado}")
                self.textLog.push(f"Canal: {canal}")

            self.textLog.push(f"-" * 10)

            self.barraProgreso.value = (self.listaProyectos.index(proyecto) + 1) / len(self.listaProyectos)

        self.actualizandoSistema = False

    def calcularListaProyectos(self):
        """
        Calcula la lista de proyectos a actualizar.
        """
        listaFolder = list()

        for base, dirs, files in os.walk(self.folder):
            for name in files:
                if name.endswith(("Info.md")):
                    archivoInfo = base + os.sep + name
                    folderProyecto = Path(base + os.sep).parent
                    listaFolder.append(
                        {"nombre": Path(folderProyecto).name, "ruta": folderProyecto, "info": archivoInfo}
                    )
            listaFolder.sort(key=lambda x: x.get("nombre"), reverse=True)

        return listaFolder
