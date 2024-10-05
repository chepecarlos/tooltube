import os
import subprocess
import webbrowser

from tooltube.miLibrerias import ObtenerArchivo, SalvarValor, UnirPath
from pathlib import Path

import tooltube.miLibrerias as miLibrerias

logger = miLibrerias.ConfigurarLogging(__name__)


def ObtenerRuta(subir, archivo, folder: str = None):
    if subir > 0:
        subir = -subir
    if folder is None:
        folder = os.getcwd()
    else:
        folder = str(folder)
    folder = folder.split("/")
    if subir != 0:
        folder = folder[:subir]
    folder.append(archivo)
    folder = "/".join(folder)
    existe = os.path.isdir(folder)
    return existe, folder


def buscarID():
    """
    Busca el ID del video de Youtube
    """
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion")
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
            data = ObtenerArchivo(ruta, False)
            if data is not None:
                if "youtube_id" in data:
                    return data["youtube_id"]
    return None


def rutaBase(folderArchivo: str = None):
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion", folderArchivo)
        if existe:
            ruta = ruta.split("/")
            ruta = ruta[:-1]
            ruta = "/".join(ruta)
            return ruta
    return None


def SalvarID(ID):
    logger.info("Intentando Salvar ID")

    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion")
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
            SalvarValor(ruta, "youtube_id", ID, False)
            logger.info("Salvada info en 1.info")
            return

    logger.warning("No se puedo salvar ID")


def buscarDato(Atributo: str, folderActual: str = None) -> str:
    """
    Busca el ID del video de Youtube
    """
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion", folderActual)
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
            data = ObtenerArchivo(ruta, False)
            if data is not None:
                if Atributo in data:
                    return data[Atributo]
    return None


def SalvarDato(Atributo, Dato, folderArchivo: str = None):
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion", folderArchivo)
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
            SalvarValor(ruta, Atributo, Dato, False)
            logger.info(f"Salvando {Atributo}, para el futuro")
            return
    logger.warning("No se encontró folder proyecto 1.Guion")


def buscarRaiz():
    # TODO Mejorar este algoritmo debe existir una forma para buscar el fonder
    niveles = 5
    folderObligatorio = "1.Guion"
    rutaActual = os.getcwd()
    listaRutaActual = rutaActual.split("/")
    for i in range(niveles):
        if i == 0:
            rutaProbar = listaRutaActual
        else:
            rutaProbar = listaRutaActual[:-i]

        rutaProbarObligatoria = rutaProbar[:]
        rutaProbarObligatoria.append(folderObligatorio)
        rutaProbarObligatoria = "/".join(rutaProbarObligatoria)
        if os.path.isdir(rutaProbarObligatoria):
            rutaBase = "/".join(rutaProbar)
            return rutaBase

    return None


def actualizarIconoDeterminado(icono, folder):

    if icono is None or folder is None:
        print("Error Faltan Datos")
        return

    # TODO cambiar icono solo si es diferente

    Comando = f"gio set {folder} -t string metadata::custom-icon file://{icono}"
    os.system(Comando)


def ruta(ruta):
    logger.info(f"abriendo[{ruta}]")
    webbrowser.open(ruta)


def EmpezarSubProceso(comando):
    """Crear nuevo Sub Proceso."""

    process = subprocess.Popen(Comando, stdout=subprocess.PIPE, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        logger.info(output.strip())
        return_code = process.poll()
        if return_code is not None:
            logger.info(f"RETURN CODE {return_code}")
            for output in process.stdout.readlines():
                logger.info(output.strip())
            return return_code
            break
