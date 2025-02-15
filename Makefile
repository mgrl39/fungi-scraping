# Variables
PYTHON = python3
SCRIPT = scraper.py  # Nombre del script
VENV = venv
REQS = requirements.txt

# Instalación de dependencias
.PHONY: install
install:
	@echo "Creando entorno virtual..."
	@$(PYTHON) -m venv $(VENV)
	@echo "Activando entorno virtual e instalando dependencias..."
	@$(VENV)/bin/pip install -r $(REQS)
	@echo "Instalación completa."

# Ejecutar el script principal
.PHONY: run
run:
	@echo "Ejecutando scraper..."
	@$(VENV)/bin/python $(SCRIPT)

# Descargar imágenes
.PHONY: download_images
download_images:
	@echo "Descargando imágenes..."
	@$(VENV)/bin/python -c 'from scraper import download_images_from_json; download_images_from_json("output_jsons", "images")'

# Limpiar archivos generados
.PHONY: clean
clean:
	@echo "Eliminando archivos JSON e imágenes..."
	@rm -rf output_jsons images
	@echo "Limpieza completa."

# Eliminar el entorno virtual
.PHONY: clean_venv
clean_venv:
	@echo "Eliminando entorno virtual..."
	@rm -rf $(VENV)
	@echo "Entorno virtual eliminado."

# Limpiar todo
.PHONY: clean_all
clean_all: clean clean_venv
	@echo "Limpieza total completada."

# Ayuda
.PHONY: help
help:
	@echo "Comandos disponibles:"
	@echo "  make install         - Instala dependencias en un entorno virtual"
	@echo "  make run             - Ejecuta el scraper"
	@echo "  make download_images - Descarga imágenes basadas en los JSON generados"
	@echo "  make clean           - Elimina archivos JSON e imágenes"
	@echo "  make clean_venv      - Elimina el entorno virtual"
	@echo "  make clean_all       - Limpia todo (JSON, imágenes, entorno virtual)"
