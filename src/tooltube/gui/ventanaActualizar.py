from datetime import datetime
from nicegui import ui, background_tasks, app
import asyncio

import os
from pathlib import Path

from tooltube.minotion.minotion import actualizarNotion, crearNotion
from tooltube.tooltube_analisis import actualizarIconos
import tooltube.miLibrerias as miLibrerias

from tooltube.miLibrerias import ConfigurarLogging

logger = ConfigurarLogging(__name__)


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
    
    textLog: ui.log = None
    "Interface para mostrar la información del proceso"

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
                            ui.button(
                                "Actualizar", on_click=lambda: background_tasks.create(self.iniciarActualizar())
                            )
                            ui.button("Crear")
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

    async def iniciarActualizar(self) -> None:
        """Inicia el proceso de actualizar cada proyecto dentro folder
        """

        if self.actualizandoSistema:
            return

        self.actualizandoSistema = True

        self.barraProgreso.value = 0
        self.textLog.push(f"Empezar a Actualizar Proyectos")
        self.listaProyectos = self.calcularListaProyectos()

        self.textLog.push(f"Cantidad Proyectos: {len(self.listaProyectos)}")

        for proyecto in self.listaProyectos:
            self.textLog.push(f"-" * 30)
            if self.pararActualizar:
                self.textLog.push("Actualización parada por el usuario.")
                self.pararActualizar = False
                self.actualizandoSistema = False
                await asyncio.sleep(0.1)
                return
            nombreProyecto = proyecto.get("nombre")
            archivoInfo = proyecto.get("info")
            folderProyecto = proyecto.get("ruta")
            
            nombreProyectoLegible = nombreProyecto.replace("_", " ")

            self.textLog.push(f"Proyecto: {nombreProyectoLegible}")
            await asyncio.sleep(0.1)

            try:
                seActualizoNotion = actualizarNotion(archivoInfo)
            except TimeoutError as e:
                logger.warning(f"Consulta de {nombreProyecto} tardo mucho")
                self.textLog.push(f"Consulta {nombreProyecto} tardo mucho", classes="text-orange")
                continue

            if seActualizoNotion is None:
                self.textLog.push(f"No se puedo actualizar {nombreProyecto}",  classes="text-red")
                # crearNotion(folderProyecto)
                # actualizarNotion(archivoInfo)
            actualizarIconos(folderProyecto)

            error = miLibrerias.ObtenerValor(archivoInfo, "error", "no-error")
            terminar = miLibrerias.ObtenerValor(archivoInfo, "terminado", False)

            if error == "no-notion":
                self.textLog.push(f"Error: no-notion")
                continue
            elif terminar:
                self.textLog.push(f"Estado: Terminado")
            else:
                estado: str = miLibrerias.ObtenerValor(archivoInfo, "estado")
                asignado: str = miLibrerias.ObtenerValor(archivoInfo, "asignado")
                canal: str = miLibrerias.ObtenerValor(archivoInfo, "canal")

                if estado == "desconocido":
                    self.textLog.push(f"Estado: {estado}", classes="text-orange")
                else:
                    self.textLog.push(f"Estado: {estado}")
                if asignado == "desconocido":
                    self.textLog.push(f"Asignado: {asignado}", classes="text-orange")
                else:
                    self.textLog.push(f"Asignado: {asignado}")
                if canal == "desconocido":
                    self.textLog.push(f"Canal: {canal}", classes="text-orange")
                else:
                    self.textLog.push(f"Canal: {canal}")
                    
            ultimaEdicion: str = miLibrerias.ObtenerValor(archivoInfo, "ultima_edicion")
            
            if ultimaEdicion is not None:
                ultimaEdicion = ultimaEdicion.replace("Z", "+00:00")
                ultimaEdicion = datetime.fromisoformat(ultimaEdicion)
                ultimaEdicion = ultimaEdicion.strftime("%d/%m/%Y %I:%M %p")
                self.textLog.push(f"Ultima Edición: {ultimaEdicion}")

            self.barraProgreso.value = (self.listaProyectos.index(proyecto) + 1) / len(self.listaProyectos)

        self.actualizandoSistema = False

    def calcularListaProyectos(self) -> list[dict]:
        """
        Calcula la lista de proyectos a actualizar.
        
        Returns: 
            list[dict]: lista de proyectos encontrados
        """
        listaFolder: list[dict] = list()

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
