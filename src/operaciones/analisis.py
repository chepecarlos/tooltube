import os
from datetime import datetime

import matplotlib.pyplot as plt
import MiLibrerias
import pandas as pd
from MiLibrerias import FuncionesArchivos
from tooltube import funcionesExtras

from operaciones import usuario

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


def crearGrafica():
    logger.info("Empezar a hacer gráfica")
    rutaBase = funcionesExtras.buscarRaiz()

    if rutaBase is None:
        logger.warning("No folder de proyecto")
        return
    archivo_data = FuncionesArchivos.UnirPath(rutaBase, "10.Analitica/2.Data/Datos de la tabla.csv")
    if not os.path.exists(archivo_data):
        logger.warning("No se control `10.Analitica/2.Data/Datos de la tabla.csv`")
        return
    data = pd.read_csv(archivo_data)
    data = data.iloc[1:, :]  # Quitando totales
    etiquetaFecha = data.columns[0]
    data[etiquetaFecha] = pd.to_datetime(data[etiquetaFecha])
    data.sort_values(etiquetaFecha, inplace=True)
    print(data)
