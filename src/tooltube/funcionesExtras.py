from pathlib import Path
import os

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

from MiLibrerias import ObtenerArchivo


def buscarID():
    logger.info("Buscando ID folder proyecto")
    Ruta = os.getcwd()
    Ruta = Ruta.split("/")
    Ruta = Ruta[:-2]
    Ruta.append("1.Guion")
    Ruta.append("1.Info.md")
    Ruta = "/".join(Ruta)
    if not os.path.isfile(Ruta):
        logger.inf("No encontado ID en folder")
        return None
    
    Data = ObtenerArchivo(Ruta)
    ID = Data["youtube_id"]
    logger.info(f"ID Youtube encontrado {ID}")
    return ID
