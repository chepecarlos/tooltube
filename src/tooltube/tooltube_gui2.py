from nicegui import ui
from pathlib import Path

import tooltube.tooltube_analisis as analitica
from tooltube.minotion.minotion import actualizarNotion
import tooltube.miLibrerias as miLibrerias

class ventanaEstado:

    def __init__(self, ruta: str):
        self.folder: str = ruta

        self.encargados = [
            'desconocido',
            'paty',
            'chepecarlos',
            'ingjuan',
            'luis'
        ]

        self.estados = [
            'desconocido',
            'idea',
            'desarrollo',
            'guion',
            'grabado',
            'edicion',
            'tomab',
            'revision',
            'preparado',
            'publicado',
            'analizando'
        ]

        self.canal = [
            'desconocido',
            'ChepeCarlos',
            'Curso_Venta',
            'CtrlZ',
            'Tiktok'
        ]

    def ejecutar(self):

        proyecto = self.folder.split("/")[-1]

        rutaInfo = f"{self.folder}/1.Guion/1.Info.md"

        if not Path(rutaInfo).exists():
            print("Error folder no es proyecto")
            ui.label("Error no se encontró proyecto")
            ui.run(native=True, reload=False, dark=True, language="es", title=f"Sistema Estado - Error")
        else:

            actualizarNotion(rutaInfo)
            
            estado = miLibrerias.ObtenerValor(rutaInfo, "estado")
            encargado = miLibrerias.ObtenerValor(rutaInfo, "asignado")
            canal = miLibrerias.ObtenerValor(rutaInfo, "canal")

            with ui.column():
                selecionEstado = ui.select(options=self.estados, with_input=True, label="Estado", on_change=lambda e: ui.notify(e.value), value=estado)
                selecionEncargado = ui.select(options=self.encargados, with_input=True, label="Encargado", on_change=lambda e: ui.notify(e.value), value=encargado)
                selecionCanal = ui.select(options=self.canal, with_input=True, label="Canal", on_change=lambda e: ui.notify(e.value), value=canal)

            ui.button('Actualizar', on_click=lambda: ui.notify('Actualizando Data!'))
            ui.run(native=True, reload=False, dark=True, language="es", title=f"Sistema Estado - {proyecto}")
