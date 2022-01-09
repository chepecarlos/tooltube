import os
from pathlib import Path

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

from MiLibrerias import ObtenerArchivo, SalvarValor


def ObtenerRuta(recortar=0):
    ruta = os.getcwd()
    ruta = ruta.split("/")
    if recortar != 0:
        ruta = ruta[:recortar]
    ruta.append("1.Guion")
    ruta.append("1.Info.md")
    ruta = "/".join(ruta)
    existe = os.path.isfile(ruta)
    return existe, ruta


def buscarID():
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(-i)
        if existe:
            data = ObtenerArchivo(ruta, False)
            if data is not None:
                if "youtube_id" in data:
                    return data["youtube_id"]
    return None


def SalvarID(ID):
    logger.info("Intentando Salvar ID")

    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(-i)
        if existe:
            SalvarValor(ruta, "youtube_id", ID, False)
            logger.info("Salvada info en 1.info")
            return

    logger.warning("No se puedo salvar ID")
