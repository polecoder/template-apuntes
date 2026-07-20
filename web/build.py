#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## @file build.py
#  @brief Punto de entrada del generador de sitio de apuntes.
#  @details Orquesta el proceso completo:
#           1) escanea los Markdown de teoria y practica (scanner.py),
#           2) calcula la navegación y el orden de las páginas (navigation.py),
#           3) convierte cada Markdown a HTML vía Pandoc (converter.py),
#           4) ensambla cada página final con la plantilla común (page_builder.py),
#           5) copia los recursos estáticos (CSS/JS) e imágenes al sitio de salida.
#
#  @usage   Ejecutar desde cualquier ubicación: `python3 web/build.py`
#           El sitio generado queda en "web/site/", listo para abrirse
#           localmente o publicarse (por ejemplo, con GitHub Pages).
"""

import shutil
import sys
from pathlib import Path

# Permite ejecutar este script tanto como "python3 build.py" desde dentro de
# "web/" como "python3 web/build.py" desde la raíz del repositorio.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_builder import config, converter, navigation, page_builder, scanner


## @brief Copia recursivamente una carpeta de imágenes de origen a su destino, si existe.
#  @param origen Carpeta de imágenes de origen (puede ser None si el documento no tiene imágenes).
#  @param destino Carpeta de destino dentro del sitio generado.
def _copiar_imagenes(origen, destino) -> None:
    if origen is None or not origen.is_dir():
        return
    destino.mkdir(parents=True, exist_ok=True)
    for archivo_imagen in origen.iterdir():
        if archivo_imagen.is_file():
            shutil.copy2(archivo_imagen, destino / archivo_imagen.name)


## @brief Copia los recursos estáticos (CSS, JS) desde static/ al sitio de salida.
def _copiar_estaticos() -> None:
    destino_static = config.OUTPUT_DIR / "static"
    if destino_static.exists():
        shutil.rmtree(destino_static)
    shutil.copytree(config.STATIC_DIR, destino_static)


## @brief Limpia por completo la carpeta de salida antes de regenerar el sitio.
def _limpiar_salida() -> None:
    if config.OUTPUT_DIR.exists():
        shutil.rmtree(config.OUTPUT_DIR)
    config.OUTPUT_DIR.mkdir(parents=True)


## @brief Genera todas las páginas HTML de las clases teóricas.
#  @param paginas_teorico Lista de páginas de teoría ya enlazadas (prev/next).
#  @param paginas_practico Diccionario completo de páginas de práctica (para la barra lateral).
def _generar_paginas_teorico(paginas_teorico, paginas_practico) -> None:
    for pagina in paginas_teorico:
        contenido_html = converter.convertir_md_a_html(pagina.documento.ruta_md)
        html_final = page_builder.construir_pagina_contenido(
            pagina, contenido_html, paginas_teorico, paginas_practico
        )
        pagina.ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        pagina.ruta_salida.write_text(html_final, encoding="utf-8")
        _copiar_imagenes(pagina.documento.ruta_img, pagina.ruta_salida.parent.parent / "img")


## @brief Genera todas las páginas HTML de los ejercicios prácticos.
#  @param paginas_teorico Lista completa de páginas de teoría (para la barra lateral).
#  @param paginas_practico Diccionario {numero_practico: [Pagina, ...]} ya enlazado (prev/next).
def _generar_paginas_practico(paginas_teorico, paginas_practico) -> None:
    for lista_paginas in paginas_practico.values():
        for pagina in lista_paginas:
            contenido_html = converter.convertir_md_a_html(pagina.documento.ruta_md)
            html_final = page_builder.construir_pagina_contenido(
                pagina, contenido_html, paginas_teorico, paginas_practico
            )
            pagina.ruta_salida.parent.mkdir(parents=True, exist_ok=True)
            pagina.ruta_salida.write_text(html_final, encoding="utf-8")
            _copiar_imagenes(pagina.documento.ruta_img, pagina.ruta_salida.parent.parent / "img")


## @brief Función principal: ejecuta el proceso de construcción completo del sitio.
def main() -> None:
    print("→ Verificando que Pandoc esté disponible...")
    converter.verificar_pandoc_disponible()

    print("→ Escaneando clases teóricas y ejercicios prácticos...")
    documentos_teorico = scanner.escanear_teorico()
    practicos = scanner.escanear_practicos()

    if not documentos_teorico and not practicos:
        print(
            "⚠ No se encontraron documentos en 'teorico' ni en 'practico/practicoN'. "
            "Verificar la configuración de rutas en site_builder/config.py."
        )

    print("→ Calculando navegación y orden de las páginas...")
    paginas_teorico = navigation.construir_paginas_teorico(documentos_teorico)
    paginas_practico = navigation.construir_paginas_practico(practicos)

    print("→ Limpiando carpeta de salida...")
    _limpiar_salida()

    print("→ Copiando recursos estáticos (CSS/JS)...")
    _copiar_estaticos()

    print(f"→ Generando {len(paginas_teorico)} página(s) de teoría...")
    _generar_paginas_teorico(paginas_teorico, paginas_practico)

    total_ejercicios = sum(len(lista) for lista in paginas_practico.values())
    print(f"→ Generando {total_ejercicios} página(s) de práctica en {len(paginas_practico)} práctico(s)...")
    _generar_paginas_practico(paginas_teorico, paginas_practico)

    print("→ Generando portada (index.html)...")
    html_index = page_builder.construir_pagina_index(paginas_teorico, paginas_practico)
    (config.OUTPUT_DIR / "index.html").write_text(html_index, encoding="utf-8")

    print(f"\n✔ Sitio generado correctamente en: {config.OUTPUT_DIR}")
    print("  Podés abrirlo localmente o servirlo, por ejemplo con:")
    print(f"  python3 -m http.server --directory {config.OUTPUT_DIR} 8000")


if __name__ == "__main__":
    main()
