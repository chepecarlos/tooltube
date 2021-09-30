from pathlib import Path
import os

import MiLibrerias

logger = MiLibrerias.ConfigurarLogging(__name__)

from MiLibrerias import ObtenerArchivo, SalvarValor

def ObtenerRuta():
    Ruta = os.getcwd()
    Ruta = Ruta.split("/")
    Ruta = Ruta[:-1]
    if(Ruta[-1] == "7.Miniatura"):
        Ruta = Ruta[:-1]
    Ruta.append("1.Guion")
    Ruta.append("1.Info.md")
    Ruta = "/".join(Ruta)
    return Ruta


def buscarID():
    logger.info("Buscando ID folder proyecto")
    Ruta = ObtenerRuta()
    
    if not os.path.isfile(Ruta):
        logger.inf("No encontado ID en folder")
        return None
    
    Data = ObtenerArchivo(Ruta, False)
    ID = Data["youtube_id"]
    logger.info(f"ID Youtube encontrado {ID}")
    return ID

def SalvarID(ID):
    logger.info("Intentando Salvar ID")
    Ruta = ObtenerRuta()
    SalvarValor(Ruta, "youtube_id", ID, False)
    logger.info(f"Salvada info en 1.info")
