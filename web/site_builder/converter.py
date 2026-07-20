# -*- coding: utf-8 -*-
"""
## @file converter.py
#  @brief Conversión de Markdown (con fórmulas LaTeX entre $ y $$) a HTML.
#  @details Utiliza Pandoc como motor de conversión, delegándole el parseo de
#           Markdown y dejando las fórmulas en formato "\\(...\\)" / "\\[...\\]"
#           para que MathJax las renderice del lado del navegador.
"""

import shutil
import subprocess
from pathlib import Path


## @brief Nombre del ejecutable de Pandoc, tal como se invoca en la línea de comandos.
_PANDOC_BIN = "pandoc"


## @brief Verifica que Pandoc esté instalado y disponible en el PATH del sistema.
#  @throws RuntimeError si Pandoc no se encuentra instalado.
def verificar_pandoc_disponible() -> None:
    if shutil.which(_PANDOC_BIN) is None:
        raise RuntimeError(
            "No se encontró Pandoc en el sistema. Instalarlo antes de generar el sitio "
            "(por ejemplo: 'sudo apt-get install pandoc' o 'brew install pandoc')."
        )


## @brief Convierte un archivo Markdown a un fragmento de HTML (sin <html>/<head>/<body>).
#  @param ruta_md Ruta absoluta al archivo Markdown de origen.
#  @return Cadena de texto con el HTML resultante, listo para insertarse en una plantilla.
#  @throws RuntimeError si Pandoc finaliza con un código de error.
def convertir_md_a_html(ruta_md: Path) -> str:
    comando = [
        _PANDOC_BIN,
        "--from=markdown",
        "--to=html5",
        "--mathjax",
        "--wrap=preserve",
        str(ruta_md),
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            f"Pandoc falló al convertir '{ruta_md}':\n{resultado.stderr}"
        )

    return resultado.stdout
