import os
from datetime import datetime

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
                logger.info(f"Se guardo cambio en {archivo}")
                return

    logger.info(f"Error no se encontró {archivo}")
