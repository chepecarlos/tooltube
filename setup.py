from shutil import rmtree
from distutils.dir_util import copy_tree
from pathlib import Path
import os

from setuptools import find_packages, setup
from setuptools.command.install import install

nombrePaquete = "tooltube"

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
        dataIconos = os.path.join(dataIconos, "src/tooltube/data")
        if os.path.exists(dataIconos): 
            print(f"Copiando {dataIconos} a {folderIconos}")  
            copy_tree(dataIconos, folderIconos)

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
        'install' : comandoPostInstalacion
    },
    package_data = {
        'src/data': ['*.md', "*.png"],
    }
)
