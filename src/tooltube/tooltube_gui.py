from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox
from PySide6.QtCore import QSize, Qt
import sys
import argparse

import tooltube.miLibrerias as miLibrerias
import tooltube.tooltube_analisis as analitica

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

        seleccionaEstados.currentTextChanged.connect(self.cambiarEstado)

    def cambiarEstado(self, estado):
        print(f"Nuevo estado {estado}")
        analitica.cambiarEstado(estado, self.ruta)


def menuEstado(ruta: str):
    app = QApplication(sys.argv)
    ventana = ventanaEstados(ruta)
    ventana.show()
    sys.exit(app.exec_())
 


def ArgumentosCLI():
    parser = argparse.ArgumentParser(prog="tooltube_gui", description="Herramienta de gui de Youtube")
    
    parser.add_argument("--estado", "-e", help="actualiza estado del proyecto de video",  action="store_true")
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


if __name__ == "__main__":
    main()
