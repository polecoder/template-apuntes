# -*- coding: utf-8 -*-
"""
## @file config.py
#  @brief Configuración centralizada del generador de sitio.
#  @details Este módulo concentra todas las rutas de entrada (repositorio de
#           apuntes) y de salida (sitio HTML generado), de forma que el resto
#           de los módulos nunca contengan rutas "hardcodeadas". Si el
#           repositorio cambia su organización de carpetas, este es el único
#           archivo que debería modificarse.
"""

import json
from pathlib import Path

## @brief Carpeta raíz del proyecto (donde vive este script "web/").
#  @details Se asume que esta carpeta ("web/") se coloca en la raíz del
#           repositorio de apuntes, es decir, como hermana de "teorico/" y
#           "practico/". Ajustar esta constante si se decide otra ubicación.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

## @brief Raíz del repositorio de apuntes (contiene teorico/ y practico/).
REPO_ROOT = PROJECT_ROOT.parent

## @brief Ruta al archivo de configuración editable por materia (título, autor, etc.).
#  @details Se ubica en la raíz del repositorio (no dentro de "web/") para que,
#           al crear un repositorio nuevo a partir del template, alcance con
#           editar este único archivo JSON sin tocar código Python.
_ARCHIVO_CONFIG_MATERIA = REPO_ROOT / "site.config.json"


## @brief Lee "site.config.json" si existe; devuelve un diccionario vacío en caso contrario.
#  @details Nunca lanza una excepción: si el archivo no existe o está mal
#           formado, se recurre a los valores por defecto definidos más abajo,
#           para que el generador siga funcionando igual (aunque sin personalizar).
#  @return Diccionario con las claves presentes en el archivo de configuración.
def _leer_configuracion_materia() -> dict:
    if not _ARCHIVO_CONFIG_MATERIA.is_file():
        return {}
    try:
        return json.loads(_ARCHIVO_CONFIG_MATERIA.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


_config_materia = _leer_configuracion_materia()

## @brief Carpeta con los Markdown de las clases teóricas.
TEORICO_SRC_DIR = REPO_ROOT / "teorico"

## @brief Carpeta con las imágenes asociadas a las clases teóricas.
TEORICO_IMG_DIR = REPO_ROOT / "teorico" / "img"

## @brief Carpeta que contiene una subcarpeta por cada práctico (practico1, practico2, ...).
PRACTICO_ROOT_DIR = REPO_ROOT / "practico"

## @brief Nombre de la subcarpeta que contiene las imágenes dentro de cada práctico/clase.
IMG_SUBDIR_NAME = "img"

## @brief Carpeta de plantillas HTML (base, índice, etc.).
TEMPLATES_DIR = PROJECT_ROOT / "templates"

## @brief Carpeta de recursos estáticos (CSS, JS) a copiar tal cual al sitio final.
STATIC_DIR = PROJECT_ROOT / "static"

## @brief Carpeta de salida donde se genera el sitio HTML final.
OUTPUT_DIR = PROJECT_ROOT / "site"

## @brief Nombre de la subcarpeta de salida para las páginas de clases teóricas.
OUTPUT_TEORICO_PAGES_DIRNAME = "clases"

## @brief Nombre de la subcarpeta de salida para las páginas de ejercicios prácticos.
OUTPUT_PRACTICO_PAGES_DIRNAME = "ejercicios"

## @brief Título general del sitio, usado en el <title> y en el encabezado.
#  @details Se toma de "site.config.json" (clave "site_title"). Si no existe
#           el archivo o la clave, se usa un valor por defecto genérico.
SITE_TITLE = _config_materia.get("site_title", "Apuntes de la materia")

## @brief Autor mostrado en el pie de página del sitio.
#  @details Se toma de "site.config.json" (clave "site_author"). Si no existe
#           el archivo o la clave, se usa un valor por defecto genérico.
SITE_AUTHOR = _config_materia.get("site_author", "Nombre del autor/a")
