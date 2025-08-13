# Carpeta donde guardar la documentación
DOCS_DIR = docs

# Paquete o ruta del código a documentar
PACKAGE = src/tooltube

# Generar documentación
docs:
	@echo "Generando documentación con pdoc..."
	pdoc $(PACKAGE) -o $(DOCS_DIR)

# Limpiar carpeta de documentación
clean-docs:
	@echo "Eliminando carpeta de documentación..."
	rm -rf $(DOCS_DIR)