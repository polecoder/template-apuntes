# -*- coding: utf-8 -*-
"""
## @file navigation.py
#  @brief Construcción de la estructura de navegación del sitio.
#  @details A partir de los documentos escaneados (scanner.py), este módulo
#           calcula: (a) la ruta de salida de cada página HTML, (b) el árbol
#           de navegación lateral (sidebar) común a todas las páginas, y
#           (c) la secuencia de "anterior/siguiente" dentro de cada colección
#           (clases teóricas entre sí, y ejercicios dentro de un mismo práctico).
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from site_builder import config
from site_builder.scanner import Documento, Practico


## @brief Representa una página final del sitio, con su documento de origen y su ruta de salida.
@dataclass
class Pagina:
    ## @brief Documento Markdown de origen (clase o ejercicio).
    documento: Documento
    ## @brief Ruta absoluta del archivo HTML de salida correspondiente.
    ruta_salida: Path
    ## @brief Etiqueta descriptiva para mostrar en la navegación (ej: "Clase 3" o "Práctico 2 · Ej. 4").
    etiqueta: str
    ## @brief Página anterior en su misma colección (o None si es la primera).
    anterior: Optional["Pagina"] = None
    ## @brief Página siguiente en su misma colección (o None si es la última).
    siguiente: Optional["Pagina"] = None


## @brief Calcula la ruta de salida para una clase teórica.
#  @param documento Documento de la clase teórica.
#  @return Ruta absoluta donde debe generarse el archivo HTML de esa clase.
def _ruta_salida_teorico(documento: Documento) -> Path:
    nombre_archivo = f"clase{documento.numero}.html"
    return config.OUTPUT_DIR / "teorico" / config.OUTPUT_TEORICO_PAGES_DIRNAME / nombre_archivo


## @brief Calcula la ruta de salida para un ejercicio práctico.
#  @param numero_practico Número del práctico al que pertenece el ejercicio.
#  @param documento Documento del ejercicio.
#  @return Ruta absoluta donde debe generarse el archivo HTML de ese ejercicio.
def _ruta_salida_practico(numero_practico: int, documento: Documento) -> Path:
    nombre_archivo = f"ej{documento.numero}.html"
    return (
        config.OUTPUT_DIR
        / "practico"
        / f"practico{numero_practico}"
        / config.OUTPUT_PRACTICO_PAGES_DIRNAME
        / nombre_archivo
    )


## @brief Construye la lista enlazada de páginas de las clases teóricas (para prev/next).
#  @param documentos Lista de documentos de clases teóricas, ya ordenada por número.
#  @return Lista de objetos Pagina con los enlaces "anterior"/"siguiente" ya asignados.
def construir_paginas_teorico(documentos: List[Documento]) -> List[Pagina]:
    paginas = [
        Pagina(
            documento=doc,
            ruta_salida=_ruta_salida_teorico(doc),
            etiqueta=f"Clase {doc.numero}",
        )
        for doc in documentos
    ]
    _enlazar_secuencia(paginas)
    return paginas


## @brief Construye, para cada práctico, la lista enlazada de páginas de sus ejercicios.
#  @param practicos Lista de objetos Practico ya escaneados.
#  @return Diccionario {numero_practico: [Pagina, ...]} con prev/next ya asignados.
def construir_paginas_practico(practicos: List[Practico]) -> dict:
    paginas_por_practico = {}

    for practico in practicos:
        paginas = [
            Pagina(
                documento=doc,
                ruta_salida=_ruta_salida_practico(practico.numero, doc),
                etiqueta=f"Práctico {practico.numero} · Ej. {doc.numero}",
            )
            for doc in practico.ejercicios
        ]
        _enlazar_secuencia(paginas)
        paginas_por_practico[practico.numero] = paginas

    return paginas_por_practico


## @brief Asigna, "in place", los punteros anterior/siguiente a una lista de páginas consecutivas.
#  @param paginas Lista de páginas ya ordenada según el criterio de la colección.
def _enlazar_secuencia(paginas: List[Pagina]) -> None:
    for indice, pagina in enumerate(paginas):
        if indice > 0:
            pagina.anterior = paginas[indice - 1]
        if indice < len(paginas) - 1:
            pagina.siguiente = paginas[indice + 1]


## @brief Calcula la ruta relativa desde una página de origen hacia una ruta de destino.
#  @param ruta_origen Ruta absoluta del archivo HTML desde el cual se enlaza.
#  @param ruta_destino Ruta absoluta del archivo (HTML, CSS, imagen, etc.) de destino.
#  @return Cadena con la ruta relativa en formato compatible con URLs (separador "/").
def ruta_relativa(ruta_origen: Path, ruta_destino: Path) -> str:
    relativa = Path(os.path.relpath(ruta_destino, start=ruta_origen.parent))
    return relativa.as_posix()
