# -*- coding: utf-8 -*-
"""
## @file page_builder.py
#  @brief Ensamblado de las páginas HTML finales a partir de las plantillas.
#  @details Toma el HTML de contenido ya convertido (converter.py) y la
#           información de navegación (navigation.py) y produce el documento
#           HTML completo de cada página, reemplazando los marcadores
#           "{{...}}" de las plantillas en templates/.
"""

from pathlib import Path
from typing import List, Optional

from site_builder import config
from site_builder.navigation import Pagina, ruta_relativa
from site_builder.scanner import Practico


## @brief Carga el contenido de una plantilla desde disco.
#  @param nombre_archivo Nombre del archivo de plantilla dentro de templates/.
#  @return Contenido de la plantilla como cadena de texto.
def _cargar_plantilla(nombre_archivo: str) -> str:
    ruta = config.TEMPLATES_DIR / nombre_archivo
    return ruta.read_text(encoding="utf-8")


## @brief Reemplaza los marcadores "{{CLAVE}}" de una plantilla por sus valores.
#  @param plantilla Texto de la plantilla con marcadores "{{CLAVE}}".
#  @param valores Diccionario {clave: valor} a insertar en la plantilla.
#  @return Texto final con todos los marcadores reemplazados.
def _renderizar(plantilla: str, valores: dict) -> str:
    resultado = plantilla
    for clave, valor in valores.items():
        resultado = resultado.replace("{{" + clave + "}}", valor)
    return resultado


## @brief Construye el bloque HTML de la barra lateral de navegación para una página dada.
#  @param ruta_pagina_actual Ruta absoluta del archivo HTML que se está generando (para marcar el enlace activo y calcular rutas relativas).
#  @param paginas_teorico Lista de páginas de clases teóricas.
#  @param paginas_practico Diccionario {numero_practico: [Pagina, ...]}.
#  @return Cadena HTML lista para insertar en el marcador {{SIDEBAR}}.
def construir_sidebar(
    ruta_pagina_actual: Path,
    paginas_teorico: List[Pagina],
    paginas_practico: dict,
) -> str:
    partes = []

    # --- Sección "Teórico" ---
    partes.append('<div class="nav-seccion">')
    partes.append('<span class="nav-seccion__titulo">Teórico</span>')
    partes.append('<ul class="nav-lista">')
    for pagina in paginas_teorico:
        href = ruta_relativa(ruta_pagina_actual, pagina.ruta_salida)
        clase_activa = " activo" if pagina.ruta_salida == ruta_pagina_actual else ""
        partes.append(
            f'<li><a class="{clase_activa.strip()}" href="{href}">'
            f"Clase {pagina.documento.numero} · {pagina.documento.titulo}</a></li>"
        )
    partes.append("</ul>")
    partes.append("</div>")

    # --- Sección "Práctico" (con un subgrupo colapsable por cada práctico) ---
    partes.append('<div class="nav-seccion">')
    partes.append('<span class="nav-seccion__titulo">Práctico</span>')
    for numero_practico in sorted(paginas_practico.keys()):
        paginas_ejercicios = paginas_practico[numero_practico]
        contiene_activo = any(p.ruta_salida == ruta_pagina_actual for p in paginas_ejercicios)
        clase_subgrupo = "nav-subgrupo abierto" if contiene_activo else "nav-subgrupo"

        partes.append(f'<div class="{clase_subgrupo}">')
        partes.append(
            f'<button type="button" class="nav-subgrupo__titulo">'
            f'Práctico {numero_practico} <span class="nav-subgrupo__flecha">›</span></button>'
        )
        partes.append('<ul class="nav-subgrupo__lista nav-lista">')
        for pagina in paginas_ejercicios:
            href = ruta_relativa(ruta_pagina_actual, pagina.ruta_salida)
            clase_activa = " activo" if pagina.ruta_salida == ruta_pagina_actual else ""
            partes.append(
                f'<li><a class="{clase_activa.strip()}" href="{href}">'
                f"Ej. {pagina.documento.numero} · {pagina.documento.titulo}</a></li>"
            )
        partes.append("</ul>")
        partes.append("</div>")
    partes.append("</div>")

    return "\n".join(partes)


## @brief Construye el HTML de un enlace de navegación secuencial (anterior/siguiente).
#  @param ruta_pagina_actual Ruta absoluta de la página desde la cual se enlaza.
#  @param pagina_destino Página vecina a enlazar, o None si no existe.
#  @param es_siguiente Indica si el enlace corresponde a "siguiente" (True) o "anterior" (False).
#  @return Cadena HTML con el enlace, o cadena vacía si no hay página vecina.
def _construir_enlace_secuencial(
    ruta_pagina_actual: Path, pagina_destino: Optional[Pagina], es_siguiente: bool
) -> str:
    if pagina_destino is None:
        return "<span></span>"

    href = ruta_relativa(ruta_pagina_actual, pagina_destino.ruta_salida)
    etiqueta_direccion = "Siguiente" if es_siguiente else "Anterior"
    clase_extra = "navegacion-secuencial__siguiente" if es_siguiente else "navegacion-secuencial__anterior"
    flecha = "→" if es_siguiente else "←"
    contenido = (
        f"{etiqueta_direccion} {flecha} {pagina_destino.etiqueta}"
        if es_siguiente
        else f"← {etiqueta_direccion} · {pagina_destino.etiqueta}"
    )
    return f'<a class="{clase_extra}" href="{href}">{contenido}</a>'


## @brief Genera el documento HTML completo de una página de contenido (clase o ejercicio).
#  @param pagina Página a generar (contiene el documento de origen y sus enlaces prev/next).
#  @param contenido_html Fragmento HTML ya convertido desde el Markdown de origen.
#  @param paginas_teorico Lista completa de páginas de clases teóricas (para la barra lateral).
#  @param paginas_practico Diccionario completo de páginas de ejercicios (para la barra lateral).
#  @return Documento HTML completo, listo para escribirse en disco.
def construir_pagina_contenido(
    pagina: Pagina,
    contenido_html: str,
    paginas_teorico: List[Pagina],
    paginas_practico: dict,
) -> str:
    plantilla_base = _cargar_plantilla("base.html")

    valores = {
        "TITLE": f"{pagina.documento.titulo}",
        "SITE_TITLE": config.SITE_TITLE,
        "SITE_AUTHOR": config.SITE_AUTHOR,
        "CSS_HREF": ruta_relativa(pagina.ruta_salida, config.OUTPUT_DIR / "static" / "css" / "styles.css"),
        "JS_HREF": ruta_relativa(pagina.ruta_salida, config.OUTPUT_DIR / "static" / "js" / "nav.js"),
        "INDEX_HREF": ruta_relativa(pagina.ruta_salida, config.OUTPUT_DIR / "index.html"),
        "SIDEBAR": construir_sidebar(pagina.ruta_salida, paginas_teorico, paginas_practico),
        "CONTENT": contenido_html,
        "PREV_HTML": _construir_enlace_secuencial(pagina.ruta_salida, pagina.anterior, es_siguiente=False),
        "NEXT_HTML": _construir_enlace_secuencial(pagina.ruta_salida, pagina.siguiente, es_siguiente=True),
    }

    return _renderizar(plantilla_base, valores)


## @brief Genera la página de portada (index.html) con tarjetas de acceso a todo el contenido.
#  @param paginas_teorico Lista de páginas de clases teóricas.
#  @param paginas_practico Diccionario {numero_practico: [Pagina, ...]}.
#  @return Documento HTML completo de la portada.
def construir_pagina_index(paginas_teorico: List[Pagina], paginas_practico: dict) -> str:
    ruta_index = config.OUTPUT_DIR / "index.html"
    plantilla_index = _cargar_plantilla("index.html")

    tarjetas_teorico = []
    for pagina in paginas_teorico:
        href = ruta_relativa(ruta_index, pagina.ruta_salida)
        tarjetas_teorico.append(
            f'<a class="portada__tarjeta" href="{href}">'
            f'<span class="portada__tarjeta-numero">Clase {pagina.documento.numero}</span>'
            f"{pagina.documento.titulo}</a>"
        )

    bloques_practico = []
    for numero_practico in sorted(paginas_practico.keys()):
        tarjetas_ejercicios = []
        for pagina in paginas_practico[numero_practico]:
            href = ruta_relativa(ruta_index, pagina.ruta_salida)
            tarjetas_ejercicios.append(
                f'<a class="portada__tarjeta" href="{href}">'
                f'<span class="portada__tarjeta-numero">Ejercicio {pagina.documento.numero}</span>'
                f"{pagina.documento.titulo}</a>"
            )
        bloques_practico.append(
            f"<h3>Práctico {numero_practico}</h3>"
            f'<div class="portada__grilla">{"".join(tarjetas_ejercicios)}</div>'
        )

    valores = {
        "SITE_TITLE": config.SITE_TITLE,
        "SITE_AUTHOR": config.SITE_AUTHOR,
        "CSS_HREF": ruta_relativa(ruta_index, config.OUTPUT_DIR / "static" / "css" / "styles.css"),
        "JS_HREF": ruta_relativa(ruta_index, config.OUTPUT_DIR / "static" / "js" / "nav.js"),
        "INDEX_HREF": ruta_relativa(ruta_index, config.OUTPUT_DIR / "index.html"),
        "SIDEBAR": construir_sidebar(ruta_index, paginas_teorico, paginas_practico),
        "TARJETAS_TEORICO": "".join(tarjetas_teorico),
        "BLOQUES_PRACTICO": "".join(bloques_practico),
    }

    return _renderizar(plantilla_index, valores)
