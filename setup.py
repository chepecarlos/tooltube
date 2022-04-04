from setuptools import find_packages, setup

with open("VERSION", "r") as f:
    version = f.read().strip()

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    name="tooltube",
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
            "tooltube_get = tooltube.tooltube_get:mail",
        ]
    },
)
