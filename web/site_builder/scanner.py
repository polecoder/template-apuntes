# -*- coding: utf-8 -*-
"""
## @file scanner.py
#  @brief Descubrimiento de documentos fuente (Markdown) dentro del repositorio.
#  @details Recorre las carpetas "teorico/src" y "practico/practicoN/src"
#           y construye una representación en memoria de cada documento
#           (número, título, ruta al Markdown y ruta a su carpeta de
#           imágenes), lista para ser convertida a HTML por converter.py.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from site_builder import config


## @brief Representa un documento individual (una clase o un ejercicio).
@dataclass
class Documento:
    ## @brief Número identificador dentro de su colección (ej: 1 para "clase1").
    numero: int
    ## @brief Título legible extraído del primer encabezado "#" del Markdown.
    titulo: str
    ## @brief Ruta absoluta al archivo Markdown de origen.
    ruta_md: Path
    ## @brief Ruta absoluta a la carpeta de imágenes asociada (puede no existir).
    ruta_img: Optional[Path]


## @brief Representa un práctico completo, con todos sus ejercicios.
@dataclass
class Practico:
    ## @brief Número del práctico (ej: 1 para "practico1").
    numero: int
    ## @brief Lista de ejercicios pertenecientes a este práctico, ordenados.
    ejercicios: List[Documento] = field(default_factory=list)


## @brief Extrae el número entero contenido en el nombre de un archivo o carpeta.
#  @param nombre Cadena de texto de la cual extraer el número (ej: "clase10.md").
#  @param prefijo Prefijo textual que antecede al número (ej: "clase", "ej", "practico").
#  @return El número entero encontrado, o 0 si no se pudo determinar.
def _extraer_numero(nombre: str, prefijo: str) -> int:
    patron = re.compile(rf"{prefijo}(\d+)", re.IGNORECASE)
    coincidencia = patron.search(nombre)
    return int(coincidencia.group(1)) if coincidencia else 0


## @brief Obtiene el título de un documento a partir de su primer encabezado H1.
#  @param ruta_md Ruta al archivo Markdown a inspeccionar.
#  @param titulo_por_defecto Título a devolver si no se encuentra un encabezado H1.
#  @return El texto del título, sin el símbolo "#" ni espacios sobrantes.
def _obtener_titulo(ruta_md: Path, titulo_por_defecto: str) -> str:
    try:
        with ruta_md.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea.startswith("# "):
                    return linea[2:].strip()
    except OSError:
        pass
    return titulo_por_defecto


## @brief Escanea la carpeta de clases teóricas y devuelve los documentos encontrados.
#  @return Lista de objetos Documento correspondientes a cada "claseN.md", ordenada por número.
def escanear_teorico() -> List[Documento]:
    documentos: List[Documento] = []

    if not config.TEORICO_SRC_DIR.is_dir():
        return documentos

    for ruta_md in config.TEORICO_SRC_DIR.glob("*.md"):
        numero = _extraer_numero(ruta_md.stem, "clase")
        titulo = _obtener_titulo(ruta_md, f"Clase {numero}")
        ruta_img = config.TEORICO_IMG_DIR if config.TEORICO_IMG_DIR.is_dir() else None
        documentos.append(Documento(numero=numero, titulo=titulo, ruta_md=ruta_md, ruta_img=ruta_img))

    documentos.sort(key=lambda doc: doc.numero)
    return documentos


## @brief Escanea la carpeta de prácticos y devuelve, para cada uno, sus ejercicios.
#  @return Lista de objetos Practico ordenada por número, cada uno con sus ejercicios ordenados.
def escanear_practicos() -> List[Practico]:
    practicos: List[Practico] = []

    if not config.PRACTICO_ROOT_DIR.is_dir():
        return practicos

    carpetas_practico = sorted(
        (p for p in config.PRACTICO_ROOT_DIR.iterdir() if p.is_dir()),
        key=lambda p: _extraer_numero(p.name, "practico"),
    )

    for carpeta_practico in carpetas_practico:
        numero_practico = _extraer_numero(carpeta_practico.name, "practico")
        carpeta_src = carpeta_practico
        carpeta_img = carpeta_practico / config.IMG_SUBDIR_NAME

        if not carpeta_src.is_dir():
            continue

        practico = Practico(numero=numero_practico)

        for ruta_md in carpeta_src.glob("*.md"):
            numero_ejercicio = _extraer_numero(ruta_md.stem, "ej")
            titulo = _obtener_titulo(ruta_md, f"Ejercicio {numero_ejercicio}")
            ruta_img = carpeta_img if carpeta_img.is_dir() else None
            practico.ejercicios.append(
                Documento(numero=numero_ejercicio, titulo=titulo, ruta_md=ruta_md, ruta_img=ruta_img)
            )

        practico.ejercicios.sort(key=lambda doc: doc.numero)
        practicos.append(practico)

    practicos.sort(key=lambda p: p.numero)
    return practicos
