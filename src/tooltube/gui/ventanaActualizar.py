from PySide6.QtWidgets import (QApplication, QMainWindow, QComboBox, QProgressBar,
                               QPushButton, QPlainTextEdit, QVBoxLayout, QWidget)
from PySide6.QtCore import QSize, Qt, QProcess
from PySide6.QtGui import QScreen

import sys
import os
from pathlib import Path

from tooltube.minotion.minotion import actualizarNotion, crearNotion
from tooltube.tooltube_analisis import actualizarIconos
import tooltube.miLibrerias as miLibrerias


class ventanaCanal(QMainWindow):
    def __init__(self, ruta: str):
        super().__init__()
        self.ruta = ruta

        self.setWindowTitle("Actualizar Proyectos")

        self.p = None

        self.boton = QPushButton("Actualizar")
        self.boton.pressed.connect(self.iniciar_actualizar)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.progreso = QProgressBar()
        self.progreso.setRange(0, 100)

        l = QVBoxLayout()
        l.addWidget(self.boton)
        l.addWidget(self.progreso)
        l.addWidget(self.text)

        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

        self.mensaje(Path(self.ruta).name)

    def mensaje(self, s):
        self.text.appendPlainText(s)

    def iniciar_actualizar(self):
        def soloNombre(propiedad):
            return propiedad.get("nombre")

        self.progreso.setValue(0)

        if self.p is None:  # No process running.
            self.mensaje("Iniciando Actualizar Proyectos")
            listaFolder = list()

            for base, dirs, files in os.walk(self.ruta):
                for name in files:
                    if name.endswith(("Info.md")):
                        archivoInfo = base + os.sep + name
                        folderProyecto = Path(base + os.sep).parent
                        listaFolder.append({"nombre": Path(folderProyecto).name, "ruta": folderProyecto, "info": archivoInfo})
                listaFolder.sort(key=soloNombre)

            cantidadProyectos = len(listaFolder)
            self.mensaje(f"Cantidad Proyectos: {cantidadProyectos}")

            i = 1
            for folder in listaFolder:
                nombreProyecto = folder.get("nombre")
                archivoInfo = folder.get("info")
                folderProyecto = folder.get("ruta")
                seActualizoNotion = actualizarNotion(archivoInfo)
                if seActualizoNotion is None:
                    crearNotion(folderProyecto)
                    actualizarNotion(archivoInfo)
                actualizarIconos(folderProyecto)

                error = miLibrerias.ObtenerValor(archivoInfo, "error", "no-error")
                terminar = miLibrerias.ObtenerValor(archivoInfo, "terminado", False)

                self.mensaje(f"Nombre: {nombreProyecto}")
                if error == "no-notion":
                    self.mensaje(f"Error: no-notion")
                elif terminar:
                    self.mensaje(f"Proyecto: Terminado")
                else:
                    estado = miLibrerias.ObtenerValor(archivoInfo, "estado")
                    asignado = miLibrerias.ObtenerValor(archivoInfo, "asignado")
                    canal = miLibrerias.ObtenerValor(archivoInfo, "canal")
                    self.mensaje(f"Estado: {estado}")
                    self.mensaje(f"Asignado: {asignado}")
                    self.mensaje(f"Canal: {canal}")
                self.mensaje(f"")

                porcentaje = i / cantidadProyectos
                self.progreso.setValue(int(porcentaje*100))
                i += 1


def menuActualizar(ruta: str):
    app = QApplication(sys.argv)
    ventana = ventanaCanal(ruta)
    ventana.show()

    centro = QScreen.availableGeometry(QApplication.primaryScreen()).center()
    posicion = ventana.frameGeometry()
    posicion.moveCenter(centro)
    ventana.move(posicion.topLeft())

    sys.exit(app.exec_())
