import os
from datetime import datetime

import matplotlib.pyplot as plt
import MiLibrerias
import pandas as pd
from MiLibrerias import FuncionesArchivos
from tooltube import funcionesExtras
from tooltube.operaciones import usuario

logger = MiLibrerias.ConfigurarLogging(__name__)


def salvar_data_analitica(archivo: str, cambio: str, mensaje: str):
    nombre_usuario = usuario.ObtenerUsuario()
    fecha_actual = pd.Timestamp.now()

    data = {"fecha": fecha_actual, "cambio": cambio, "mensaje": mensaje, "autor": nombre_usuario}

    for i, _ in enumerate(range(5)):
        existe, ruta = funcionesExtras.ObtenerRuta(i, "10.Analitica")
        if existe:
            ruta = funcionesExtras.UnirPath(ruta, archivo)
            if os.path.isfile(ruta):
                data_archivo = pd.read_csv(ruta)
                data_archivo = data_archivo.append(data, ignore_index=True)
                data_archivo.to_csv(ruta, index=False)
                logger.info(f"Se guardo cambio {cambio} en {archivo}")
                return

    logger.info(f"Error no se encontró {archivo}")


def cargarData(ruta, archivo, noTotales=False):
    archivoData = FuncionesArchivos.UnirPath(ruta, archivo)
    if not os.path.exists(archivoData):
        logger.warning(f"No se control {archivo}")
        return None
    data = pd.read_csv(archivoData)
    if noTotales:
        data = data.iloc[1:, :]  # Quitando totales

    # etiquetaFecha = data.columns[0]
    # data[etiquetaFecha] = pd.to_datetime(data[etiquetaFecha])
    # data.sort_values(etiquetaFecha, inplace=True)
    return data


def crearGrafica():
    logger.info("Empezar a hacer gráfica")
    rutaBase = funcionesExtras.buscarRaiz()

    if rutaBase is None:
        logger.warning("No folder de proyecto")
        return
    dataYoutube = cargarData(rutaBase, "10.Analitica/2.Data/Datos de la tabla.csv", True)
    if dataYoutube is None:
        logger.info("Necesario data de youtube descargalo con -csv")
        return

    print()
    print("Data Youtube")
    print(dataYoutube)

    dataTitulo = cargarData(rutaBase, "10.Analitica/1.Cambios/titulos.csv")

    print()
    print("Data Titulo")
    print(dataTitulo)

    dataMiniatura = cargarData(rutaBase, "10.Analitica/1.Cambios/miniatura.csv")

    print()
    print("Data Miniatura")
    print(dataMiniatura)

    etiquetaFecha = dataYoutube.columns[0]

    dataFecha = dataYoutube[etiquetaFecha]
    # dataValor = dataYoutube["Vistas"]

    print(dataFecha)
    # print(dataValor)
