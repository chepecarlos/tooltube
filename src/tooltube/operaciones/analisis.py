import os
from datetime import datetime

import colorama
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from colorama import Back, Fore, Style

import tooltube.miLibrerias as miLibrerias
from tooltube import funcionesExtras
from tooltube.miLibrerias import FuncionesArchivos
from tooltube.operaciones import usuario

logger = miLibrerias.ConfigurarLogging(__name__)


def salvar_data_analitica(archivo: str, cambio: str, mensaje: str, folderArchivo: str = None):
    nombre_usuario = usuario.ObtenerUsuario()
    fecha_actual = pd.Timestamp.now()

    data = pd.DataFrame([(fecha_actual, cambio, mensaje, nombre_usuario)], columns=['fecha', 'cambio', 'mensaje', 'autor'])

    for i, _ in enumerate(range(5)):
        existe, ruta = funcionesExtras.ObtenerRuta(i, "10.Analitica", folderArchivo)
        if existe:
            ruta = funcionesExtras.UnirPath(ruta, archivo)
            if os.path.isfile(ruta):
                data_archivo = pd.read_csv(ruta)
                data_archivo = pd.concat([data_archivo, data])
                data_archivo.to_csv(ruta, index=False)
                logger.info(f"Se guardo cambio {cambio} en {archivo}")
                return

    logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT +
                   f"Error no se encontró {archivo}")


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


def crearGraficaLocal(archivo=None):
    logger.info("Empezar gráfica Local")
    rutaBase = "."
    dataYoutube = cargarData(rutaBase, archivo, True)
    etiqueta = list(dataYoutube.columns)[1]
    crearGrafica(etiqueta, archivo)


def crearGrafica(etiqueta, archivo=None):
    logger.info("Empezar a hacer gráfica")

    if archivo is None:
        rutaBase = funcionesExtras.buscarRaiz()

        if rutaBase is None:
            logger.warning("No folder de proyecto")
            return
        dataYoutube = cargarData(
            rutaBase, "10.Analitica/2.Data/Datos de la tabla.csv", True)
        if dataYoutube is None:
            logger.warning(Fore.WHITE + Back.RED + Style.BRIGHT +
                           "Necesario data de youtube descargalo con -csv")
            return
    else:
        rutaBase = "."
        dataYoutube = cargarData(rutaBase, archivo, True)

    if archivo is None:
        dataTitulo = cargarCambios("titulos", rutaBase, "10.Analitica/1.Cambios/titulos.csv")
        dataMiniatura = cargarCambios("miniatura", rutaBase, "10.Analitica/1.Cambios/miniatura.csv")
        dataEstado = cargarCambios("estado", rutaBase, "10.Analitica/1.Cambios/estado.csv")

    etiquetaFecha = dataYoutube.columns[0]

    # Quitar mensaje de hasta 500
    dataYoutube = dataYoutube.drop(
        dataYoutube[dataYoutube[etiquetaFecha] ==
                    "Mostrando los 500 resultados principales"].index
    )

    etiquetaFecha = dataYoutube.columns[0]

    dataYoutube[etiquetaFecha] = pd.to_datetime(dataYoutube[etiquetaFecha])

    dataYoutube.sort_values(etiquetaFecha, inplace=True)

    all_data = pd.DataFrame(
        pd.date_range(dataYoutube[etiquetaFecha].min(), dataYoutube[etiquetaFecha].max()), columns=[etiquetaFecha]
    )

    dataYoutube = all_data.merge(right=dataYoutube, how="left", on=etiquetaFecha)

    fechas = dataYoutube[etiquetaFecha]
    valores = dataYoutube[etiqueta]
    valores.fillna(valores.min() / 2, inplace=True)  # valor a mitad del mínimo

    if etiqueta == "Duración promedio de vistas":
        for id in range(len(valores)):
            valores.iloc[id] = tiempoASegundos(valores.iloc[id])

    # for valor, fecha in zip(valores, fechas):
    # print(fecha, valor)

    [sum7, sum30, suma365] = encontrarSumas(valores)

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

    etiquetaVisible = etiqueta
    if etiquetaVisible == "Tasa de clics de las impresiones (%)":
        etiquetaVisible = "CTR"

    cantidadGraficas = 2

    fig, axs = plt.subplots(cantidadGraficas, 1)

    if len(valores) > 30:
        [min30, max30] = encontrarMaxMin(sum30[30:])
        grafica30 = axs[0]
        # grafica30.plot(fechas[30:], valores[30:], "#cfcfcf", label=etiquetaVisible)
        suma7_30 = np.array(sum7[30:])
        sum30_30 = np.array(sum30[30:])
        tiempo_30 = np.array(fechas[30:])
        grafica30.plot(tiempo_30, suma7_30, label=f"Suma7")
        grafica30.plot(tiempo_30, sum30_30, linewidth=2,
                       color="indigo", label=f"Suma30")

        grafica30.fill_between(
            tiempo_30,
            suma7_30,
            sum30_30,
            where=(suma7_30 > sum30_30),
            interpolate=True,
            alpha=0.5,
            color="cyan",
        )

        grafica30.fill_between(
            tiempo_30,
            suma7_30,
            sum30_30,
            where=(suma7_30 < sum30_30),
            interpolate=True,
            alpha=0.5,
            color="red",
        )
        if len(fechas) > 365:
            grafica30.plot(fechas[365:], suma365[365:], color="lawngreen", linewidth=3, alpha=0.9, label=f"Suma365")
        grafica30.grid(axis="y", color="gray", linestyle="dashed")
        grafica30.set_xlabel(etiquetaFecha)
        grafica30.set_ylabel(etiquetaVisible)
        grafica30.legend(loc="upper left")
        grafica30.hlines(max30, fechas.iloc[30], fechas.iloc[-1], colors="#000000", linestyles="dashed")
        grafica30.hlines(min30, fechas.iloc[30], fechas.iloc[-1], colors="#ff0000", linestyles="dashed")
        if archivo is None:
            graficaCambios(grafica30, dataTitulo, dataMiniatura, dataEstado)

    if len(valores) > 7:
        [min7, max7] = encontrarMaxMin(sum7[7:])
        grafica7 = axs[1]
        grafica7.plot(fechas[7:], valores[7:], "#cfcfcf",
                      linewidth=1.5, label=etiquetaVisible)
        grafica7.plot(fechas[7:], sum7[7:], "#1414fa", label=f"Suma7")
        grafica7.grid(axis="y", color="gray", linestyle="dashed")
        grafica7.set_xlabel(etiquetaFecha)
        grafica7.set_ylabel(etiquetaVisible)
        grafica7.legend(loc="upper left")
        grafica7.hlines(max7, fechas.iloc[7], fechas.iloc[-1], colors=["#000000"], linestyles="dashed")
        grafica7.hlines(min7, fechas.iloc[7], fechas.iloc[-1], colors=["#ff0000"], linestyles="dashed")
        if archivo is None:
            graficaCambios(grafica7, dataTitulo, dataMiniatura, dataEstado)

    if cantidadGraficas >= 3:

        # [min30, max30] = encontrarMaxMin(valores)
        graficaNormal = axs[2]
        graficaNormal.plot(fechas, valores, "#fa8714",
                           linewidth=1.2, label=etiquetaVisible)

        graficaNormal.grid(axis="y", color="gray", linestyle="-")
        graficaNormal.set_xlabel(etiquetaFecha)
        graficaNormal.set_ylabel(etiquetaVisible)
        # graficaNormal.hlines(max30, fechas.iloc[0], fechas.iloc[-1], colors="#000000")
        # graficaNormal.hlines(min30, fechas.iloc[0], fechas.iloc[-1], colors="#ff0000")
        if archivo is None:
            graficaCambios(graficaNormal, dataTitulo, dataMiniatura, dataEstado)
        graficaNormal.legend(loc="upper left")

        graficaNormal.vlines(dataMiniatura[fechaMiniatura], 0, 1, transform=graficaNormal.get_xaxis_transform(), colors="r")

    plt.gcf().autofmt_xdate()
    plt.xticks(inicioMes, etiquetaMes)

    plt.tight_layout()
    diferencia = fechas.max() - fechas.min()
    fig.suptitle(
        f"Gráfica de {etiquetaVisible} de {fechas.min().strftime('%d/%m/%Y')} al {fechas.max().strftime('%d/%m/%Y')} ({diferencia.days} días)",
        y=0.99,
        fontsize=10,
    )
    plt.show()


def cargarCambios(tipo, rutaBase, direccion):
    data = cargarData(rutaBase, direccion)
    etiquetaFechas = data.columns[0]
    data[etiquetaFechas] = pd.to_datetime(data[etiquetaFechas])

    if not data.empty:
        print(f"Cambios {tipo}:")
        for i, linea in data.iterrows():
            fechaActual = linea["fecha"].strftime("%I:%M %p %d/%m/%Y")
            mensaje = linea["mensaje"]
            if pd.isnull(mensaje):
                mensaje = ""
            print(f" {fechaActual} - {linea['autor']} - {mensaje}")
            print(f"Cambio: {linea['cambio']}")
        print()

    return data


def graficaCambios(grafica, titulo, miniatura, estado):
    etiquetaFecha = titulo.columns[0]
    grafica.vlines(titulo[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(
    ), colors="r", label="Titulo")
    grafica.vlines(
        miniatura[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(), colors="#00ff00", label="Miniatura"
    )
    grafica.vlines(estado[etiquetaFecha], 0, 1, transform=grafica.get_xaxis_transform(
    ), colors="b", label="Estado")
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
    suma365 = []
    cantidad = len(valores)
    for id in range(len(valores)):
        sum7.append(0)
        sum30.append(0)
        suma365.append(0)
        for j in range(id - 6, id + 1):
            if j >= 0 and j < cantidad:
                sum7[id] += valores.iloc[j]
        sum7[id] /= 7
        for j in range(id - 29, id + 1):
            if j >= 0 and j < cantidad:
                sum30[id] += valores.iloc[j]
        sum30[id] /= 30
        for j in range(id - 364, id + 1):
            if j >= 0 and j < cantidad:
                suma365[id] += valores.iloc[j]
        suma365[id] /= 365
    return (sum7, sum30, suma365)


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
