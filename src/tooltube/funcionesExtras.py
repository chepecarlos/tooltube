import os
from pathlib import Path

import tooltube.miLibrerias as miLibrerias

logger = miLibrerias.ConfigurarLogging(__name__)

from tooltube.miLibrerias import ObtenerArchivo, SalvarValor, UnirPath


def ObtenerRuta(subir, folder):
    if subir > 0:
        subir = -subir
    ruta = os.getcwd()
    ruta = ruta.split("/")
    if subir != 0:
        ruta = ruta[:subir]
    ruta.append(folder)
    ruta = "/".join(ruta)
    existe = os.path.isdir(ruta)
    return existe, ruta


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


def rutaBase():
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion")
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


def buscarDato(Atributo: str) -> str:
    """
    Busca el ID del video de Youtube
    """
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion")
        if existe:
            ruta = UnirPath(ruta, "1.Info.md")
            data = ObtenerArchivo(ruta, False)
            if data is not None:
                if Atributo in data:
                    return data[Atributo]
    return None


def SalvarDato(Atributo, Dato):
    for i, _ in enumerate(range(5)):
        existe, ruta = ObtenerRuta(i, "1.Guion")
        if existe:

            ruta = UnirPath(ruta, "1.Info.md")
            SalvarValor(ruta, Atributo, Dato, False)
            logger.info(f"Salvando {Atributo}, para el futuro")
            return


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


def actualizarEstado(rutaActual=None):

    if rutaActual is None:
        rutaActual = os.getcwd()
    iconos = miLibrerias.ObtenerArchivo("data/iconos.json", True)
    for base, dirs, files in os.walk(rutaActual):
        for name in files:
            if name.endswith(("Info.md")):
                filepath = base + os.sep + name
                estado = miLibrerias.ObtenerValor(filepath, "estado")
                if estado is None:
                    estado = "desconocido"
                folderProyecto = Path(base + os.sep).parent
                nombreProyecto = folderProyecto.name
                iconoProyecto = iconos.get(estado, estado[0])
                print(f"Proyecto: {nombreProyecto} - {estado}")
                actualizarIconoDeterminado(iconoProyecto, folderProyecto)


def actualizarIconoDeterminado(icono, folder):

    if icono is None or folder is None:
        print("Error Faltan Datos")
        return
    
    # TODO cambiar icono solo si es diferente

    Comando = f"gio set {folder} -t string metadata::custom-icon file://{icono}"
    os.system(Comando)