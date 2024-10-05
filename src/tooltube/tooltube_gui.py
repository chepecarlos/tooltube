from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox
from PySide6.QtCore import QSize, Qt
import sys
import argparse

import tooltube.miLibrerias as miLibrerias
import tooltube.tooltube_analisis as analitica
from tooltube.minotion.minotion import abriNotion
logger = miLibrerias.ConfigurarLogging(__name__)


class ventanaEstados(QMainWindow):
    def __init__(self, ruta: str):
        super().__init__()
        self.ruta = ruta

        seleccionaEstados = QComboBox()
        self.setCentralWidget(seleccionaEstados)
        seleccionaEstados.addItems(
            [
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
        )

        # TODO selecionado esta actual del video

        self.setWindowTitle("Asignar Estado")
        seleccionaEstados.currentTextChanged.connect(self.cambiarEstado)

    def cambiarEstado(self, estado):
        print(f"Nuevo estado {estado}")
        analitica.cambiarEstado(estado, self.ruta)


class ventanaAsignado(QMainWindow):
    def __init__(self, ruta: str):
        super().__init__()
        self.ruta = ruta

        seleccionaAsignado = QComboBox()
        self.setCentralWidget(seleccionaAsignado)
        seleccionaAsignado.addItems(
            [
                'desconocido',
                'paty',
                'chepecarlos',
                'ingjuan',
                'luis'
            ]
        )

        self.setWindowTitle("Asignar Encargado")
        seleccionaAsignado.currentTextChanged.connect(self.cambiarAsignado)
        logger.info("Creando ventana Asignado")

    def cambiarAsignado(self, asignado):
        logger.info(f"Nuevo asignado {asignado}")
        analitica.cambiarAsignado(asignado, self.ruta)


class ventanaCanal(QMainWindow):
    def __init__(self, ruta: str):
        super().__init__()
        self.ruta = ruta

        seleccionaAsignado = QComboBox()
        self.setCentralWidget(seleccionaAsignado)
        seleccionaAsignado.addItems(
            [
                'desconocido',
                'ChepeCarlos',
                'Curso_Venta',
                'CtrlZ',
                'Tiktok'
            ]
        )

        self.setWindowTitle("Asignar Canal")
        seleccionaAsignado.currentTextChanged.connect(self.cambiarAsignado)
        logger.info("Creando ventana Canal")

    def cambiarAsignado(self, canal):
        logger.info(f"Nuevo canal {canal}")
        analitica.cambiarCanal(canal, self.ruta)


def menuEstado(ruta: str):
    app = QApplication(sys.argv)
    ventana = ventanaEstados(ruta)
    ventana.show()
    sys.exit(app.exec_())


def menuAsignado(ruta: str):
    app = QApplication(sys.argv)
    ventana = ventanaAsignado(ruta)
    ventana.show()
    sys.exit(app.exec_())


def menuCanal(ruta: str):
    app = QApplication(sys.argv)
    ventana = ventanaCanal(ruta)
    ventana.show()
    sys.exit(app.exec_())


def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="tooltube_gui", description="Herramienta de gui de Youtube")

    parser.add_argument("--estado", "-e", help="actualiza estado del proyecto de video",  action="store_true")
    parser.add_argument("--asignado", "-a",  help="actualiza a quien esta asignado del proyecto de video", action="store_true")
    parser.add_argument("--canal", "-c",  help="actualiza el canal asignado proyecto de video", action="store_true")
    parser.add_argument("--notion", "-n",  help="Abre la ruta de notion en navegador", action="store_true")

    parser.add_argument("--folder", help="Folder a Realizar operación")

    return parser.parse_args()


def main():
    logger.info("Iniciando el programa ToolTube Analisis")
    args = ArgumentosCLI()

    if args.folder is None:
        logger.error("falta folder")
        return

    if args.estado:
        menuEstado(args.folder)
    elif args.asignado:
        menuAsignado(args.folder)
    elif args.canal:
        menuCanal(args.folder)
    elif args.notion:   
        abriNotion(args.folder)


if __name__ == "__main__":
    main()
