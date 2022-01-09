import os
from pathlib import Path

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

from MiLibrerias import ObtenerArchivo, SalvarValor, UnirPath


def ObtenerRuta(suvir, folder):
    ruta = os.getcwd()
    ruta = ruta.split("/")
    if suvir != 0:
        ruta = ruta[:suvir]
    ruta.append(folder)
    ruta = "/".join(ruta)
    existe = os.path.isdir(ruta)
    return existe, ruta


def buscarID():
    """
    Busca el ID del video de Youtube
    """
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(-i, "1.Guion")
        print(ruta, existe)
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
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
