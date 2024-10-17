from shutil import rmtree
from distutils.dir_util import copy_tree
from pathlib import Path
import os
import shutil

from setuptools import find_packages, setup
from setuptools.command.install import install

nombrePaquete = "tooltube"


def copiarSinSobreEscribir(origen, destino):

    for archivo in os.listdir(origen):
        rutaOrigen = os.path.join(origen, archivo)
        rutaDestino = os.path.join(destino, archivo)

        if os.path.isfile(rutaOrigen):
            if not os.path.exists(rutaDestino):
                shutil.copy2(rutaOrigen, rutaDestino)
                print(f"Copiando {archivo} a {destino}")
            else:
                print(f"El archivo {archivo} ya existe en {destino}, no se ha copiado.")
        elif os.path.isdir(rutaOrigen):
            copiarSinSobreEscribir(rutaOrigen, rutaDestino)
        else:
            print(f"{archivo} es un directorio, no se ha copiado.")


def copiarSobreEscribir(origen, destino):
    for archivo in os.listdir(origen):
        rutaOrigen = os.path.join(origen, archivo)
        rutaDestino = os.path.join(destino, archivo)

        if os.path.isfile(rutaOrigen):
            shutil.copy2(rutaOrigen, rutaDestino)
            print(f"Copiando {archivo} a {destino}")
        elif os.path.isdir(rutaOrigen):
            copiarSobreEscribir(rutaOrigen, rutaDestino)
        else:
            print(f"{archivo} es un directorio, no se ha copiado.")


class comandoPostInstalacion(install):
    def run(self):
        install.run(self)
        print("")
        print("***********Código Propio Después de Instalar********")

        folderIconos = Path.home()
        folderIconos = os.path.join(folderIconos, ".icons/hicolor/256x256/emblems")

        if not os.path.exists(folderIconos):
            Path(folderIconos).mkdir(parents=True, exist_ok=True)
            print(f"Folder icono creado {folderIconos}")

        dataIconos = os.getcwd()
        dataIconos = os.path.join(dataIconos, f"src/{nombrePaquete}/data/emblem")
        if os.path.exists(dataIconos):
            print(f"Copiando {dataIconos} a {folderIconos}")
            copy_tree(dataIconos, folderIconos)

        folderConfig = Path.home()
        folderConfig = os.path.join(folderConfig, f".config/{nombrePaquete}/data")

        if not os.path.exists(folderConfig):
            Path(folderConfig).mkdir(parents=True, exist_ok=True)
            print(f"Folder Configuraciones creado {folderConfig}")

        dataConfig = os.getcwd()
        dataConfig = os.path.join(dataConfig, f"src/{nombrePaquete}/data/config")

        print(f"Recargando Archivos de configuración de {nombrePaquete}")

        copiarSinSobreEscribir(dataConfig, folderConfig)

        folderAciones = Path.home()
        folderAciones = os.path.join(folderAciones, f".local/share/nemo")

        if not os.path.exists(folderAciones):
            Path(folderAciones).mkdir(parents=True, exist_ok=True)
            print(f"Folder Configuraciones creado {folderAciones}")

        dataAcciones = os.getcwd()
        dataAcciones = os.path.join(dataAcciones, f"src/{nombrePaquete}/data/nemo")

        print(f"Recargando Acciones de Nemo de {nombrePaquete}")
        copiarSobreEscribir(dataAcciones, folderAciones)

        print("****************************************************")
        print()


with open("VERSION", "r") as f:
    version = f.read().strip()

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

try:
    rmtree("build")
except:
    pass
try:
    rmtree("dist")
except:
    pass

setup(
    name=nombrePaquete,
    version=version,
    description="Herramienta para Actualizar procesos de Youtube",
    long_description=long_description,
    author="ChepeCarlos",
    author_email="chepecarlos@alswblog.org",
    url="https://github.com/chepecarlos/tooltube",
    install_requires=required,
    packages=find_packages(where="src", exclude=("tests*", "testing*")),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "tooltube = tooltube.tooltube:main",
            "tooltube_analisis = tooltube.tooltube_analisis:main",
            "tooltube_get = tooltube.tooltube_get:main",
            "tooltube_gui = tooltube.tooltube_gui:main"
        ]
    },
    include_package_data=True,
    cmdclass={
        'install': comandoPostInstalacion
    },
    package_data={
        'src/data': ['*.md', "*.png"],
    }
)
