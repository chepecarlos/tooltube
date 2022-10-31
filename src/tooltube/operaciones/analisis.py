import os
from datetime import datetime

import colorama
import matplotlib.pyplot as plt
import pandas as pd
import tooltube.miLibrerias as miLibrerias
from colorama import Back, Fore, Style
from tooltube import funcionesExtras
from tooltube.miLibrerias import FuncionesArchivos
from tooltube.operaciones import usuario

logger = miLibrerias.ConfigurarLogging(__name__)


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

    logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + f"Error no se encontró {archivo}")


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


def crearGrafica(etiqueta):
    logger.info("Empezar a hacer gráfica")
    rutaBase = funcionesExtras.buscarRaiz()

    if rutaBase is None:
        logger.warning("No folder de proyecto")
        return
    dataYoutube = cargarData(rutaBase, "10.Analitica/2.Data/Datos de la tabla.csv", True)
    if dataYoutube is None:
        logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT + "Necesario data de youtube descargalo con -csv")
        return

    dataTitulo = cargarCambios("titulos", rutaBase, "10.Analitica/1.Cambios/titulos.csv")
    dataMiniatura = cargarCambios("miniatura", rutaBase, "10.Analitica/1.Cambios/miniatura.csv")
    dataEstado = cargarCambios("estado", rutaBase, "10.Analitica/1.Cambios/estado.csv")

    etiquetaFecha = dataYoutube.columns[0]
    dataYoutube = dataYoutube.drop(
        dataYoutube[dataYoutube[etiquetaFecha] == "Mostrando los 500 resultados principales"].index
    )

    dataFecha = dataYoutube[etiquetaFecha]

    etiquetaFecha = dataYoutube.columns[0]

    dataYoutube[etiquetaFecha] = pd.to_datetime(dataYoutube[etiquetaFecha])

    dataYoutube.sort_values(etiquetaFecha, inplace=True)

    fechas = dataYoutube[etiquetaFecha]
    valores = dataYoutube[etiqueta]
    valores.fillna(0, inplace=True)

    if etiqueta == "Duración promedio de vistas":
        for id in range(len(valores)):
            valores.iloc[id] = tiempoASegundos(valores.iloc[id])

    [sum7, sum30] = encontrarSumas(valores)

    inicioMes = []
    etiquetaMes = []

    listaMeses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]

    for dia in dataYoutube[etiquetaFecha]:
        if dia.is_month_start:
            inicioMes.append(dia)
            etiquetaMes.append(f"{listaMeses[dia.month-1]}/{dia.year}")

    fig, axs = plt.subplots(3, 1)

    [min30, max30] = encontrarMaxMin(sum30[30:])
    grafica30 = axs[0]
    grafica30.plot(fechas, valores, "#cfcfcf", label=etiqueta)
    # grafica30.plot(fechas, sum7, label=f"Suma7")
    grafica30.plot(fechas[30:], sum30[30:], "#016f10", label=f"Suma30")
    grafica30.grid(axis="y", color="gray", linestyle="dashed")
    grafica30.set_xlabel(etiquetaFecha)
    grafica30.set_ylabel(etiqueta)
    grafica30.legend(loc="upper left")
    grafica30.hlines(max30, fechas.iloc[30], fechas.iloc[-1], colors="#000000")
    grafica30.hlines(min30, fechas.iloc[30], fechas.iloc[-1], colors="#ff0000")
    graficaCambios(grafica30, dataTitulo, dataMiniatura, dataEstado)

    [min30, max30] = encontrarMaxMin(sum7[30:])
    grafica7 = axs[1]
    grafica7.plot(fechas, valores, "#cfcfcf", label=etiqueta)
    grafica7.plot(fechas[7:], sum7[7:], "#1414fa", label=f"Suma7")
    grafica7.grid(axis="y", color="gray", linestyle="dashed")
    grafica7.set_xlabel(etiquetaFecha)
    grafica7.set_ylabel(etiqueta)
    grafica7.legend(loc="upper left")
    grafica7.hlines(max30, fechas.iloc[7], fechas.iloc[-1], colors="#000000")
    grafica7.hlines(min30, fechas.iloc[7], fechas.iloc[-1], colors="#ff0000")
    graficaCambios(grafica7, dataTitulo, dataMiniatura, dataEstado)

    # [min30, max30] = encontrarMaxMin(valores)
    graficaNormal = axs[2]
    graficaNormal.plot(fechas, valores, "#fa8714", label=etiqueta)
    graficaNormal.grid(axis="y", color="gray", linestyle="dashed")
    graficaNormal.set_xlabel(etiquetaFecha)
    graficaNormal.set_ylabel(etiqueta)
    # graficaNormal.hlines(max30, fechas.iloc[0], fechas.iloc[-1], colors="#000000")
    # graficaNormal.hlines(min30, fechas.iloc[0], fechas.iloc[-1], colors="#ff0000")
    graficaCambios(graficaNormal, dataTitulo, dataMiniatura, dataEstado)
    graficaNormal.legend(loc="upper left")

    # graficaNormal.vlines(dataMiniatura[fechaMiniatura], 0, 1, transform=graficaNormal.get_xaxis_transform(), colors="r")

    plt.gcf().autofmt_xdate()
    plt.xticks(inicioMes, etiquetaMes)

    plt.tight_layout()
    fig.suptitle(f"Gráfica suma7 y suma30 de {etiqueta}", y=0.99, fontsize=10)
    plt.show()


def cargarCambios(tipo, rutaBase, direccion):
    data = cargarData(rutaBase, direccion)
    etiquetaFechas = data.columns[0]
    data[etiquetaFechas] = pd.to_datetime(data[etiquetaFechas])

    if not data.empty:
        print(f"Cambios {tipo}:")
        print(data)
        print()

    return data


def graficaCambios(grafica, titulo, miniatura, estado):
    etiquetaFecha = titulo.columns[0]
    grafica.vlines(titulo[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(), colors="r", label="Titulo")
    grafica.vlines(
        miniatura[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(), colors="#00ff00", label="Miniatura"
    )
    grafica.vlines(estado[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(), colors="b", label="Estado")
    # grafica.legend()


def encontrarMaxMin(valores):
    max30 = valores[0]
    min30 = valores[0]
    for valor in valores:
        if min30 < valor:
            min30 = valor
        if max30 > valor:
            max30 = valor
    return (min30, max30)


def encontrarSumas(valores):
    sum7 = []
    sum30 = []
    cantidad = len(valores)
    for id in range(len(valores)):
        sum7.append(0)
        sum30.append(0)
        for j in range(id - 6, id + 1):
            if j >= 0 and j < cantidad:
                sum7[id] += valores.iloc[j]
        # sum7[id] /= 7
        for j in range(id - 29, id + 1):
            if j >= 0 and j < cantidad:
                sum30[id] += valores.iloc[j]
        # sum30[id] /= 30
    return (sum7, sum30)


def tiempoASegundos(tiempo):
    segundos = 0
    if isinstance(tiempo, str):
        pedadosTiempo = tiempo.split(":")
        segundos = int(pedadosTiempo[-1])
        if len(pedadosTiempo) > 1:
            segundos += int(pedadosTiempo[-2]) * 60
        if len(pedadosTiempo) > 2:
            segundos += int(pedadosTiempo[-3]) * 3600
    return segundos
