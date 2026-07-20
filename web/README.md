# Generador de sitio — Apuntes de Probabilidad y Estadística

Prototipo mínimo que convierte los apuntes en Markdown + LaTeX (`teorico/` y
`practico/`) en un sitio HTML estático navegable, usando **Pandoc** como motor
de conversión y **MathJax** para renderizar las fórmulas del lado del cliente.

## 1. Requisitos

- Python 3.9 o superior (no requiere ninguna dependencia externa de `pip`).
- [Pandoc](https://pandoc.org/installing.html) instalado y accesible en el `PATH`.
  - Debian/Ubuntu: `sudo apt-get install pandoc`
  - macOS: `brew install pandoc`

## 2. Ubicación dentro del repositorio

Esta carpeta (`web/`) debe copiarse a la **raíz** del repositorio de apuntes,
como hermana de `teorico/` y `practico/`:

```
pye/
├── teorico/
│   └── img/
├── practico/
│   ├── practico1/
│   │   └── img/
│   └── ...
└── web/                  ← esta carpeta
    ├── build.py
    ├── site_builder/
    ├── templates/
    ├── static/
    └── site/              ← se genera automáticamente al ejecutar build.py
```

Si se prefiere otra ubicación, basta con ajustar las rutas en
`site_builder/config.py` (es el único archivo con rutas explícitas).

## 3. Generar el sitio

Desde la carpeta `web/`:

```bash
python3 build.py
```

Esto crea (o regenera desde cero) la carpeta `web/site/` con el sitio HTML
completo: portada, una página por cada clase teórica, una página por cada
ejercicio práctico, navegación lateral y navegación secuencial (anterior/siguiente).

## 4. Ver el sitio localmente

Como el sitio usa rutas relativas, puede abrirse directamente haciendo doble
clic en `web/site/index.html`, o servirse con el servidor embebido de Python
para evitar restricciones del navegador con `file://`:

```bash
python3 -m http.server --directory web/site 8000
```

Y luego abrir `http://localhost:8000` en el navegador.

## 5. Cómo agregar contenido nuevo

No es necesario tocar ningún archivo de `web/`. Basta con:

- Agregar `teorico/claseN.md` para una nueva clase teórica.
- Agregar `practico/practicoN/ejM.md` para un nuevo ejercicio (creando la
  carpeta `practicoN/` si es la primera vez).
- Agregar imágenes en la carpeta `img/` correspondiente y
  referenciarlas desde el Markdown como `![Figura 1](./img/archivo.png)`.

Al volver a ejecutar `python3 web/build.py`, el nuevo contenido aparece
automáticamente en la navegación y en la portada, sin necesidad de editar
código.

## 6. Build automático en cada commit (GitHub Actions)

El repositorio incluye `.github/workflows/build-and-deploy.yml`, que en cada
`push` a `main` que modifique `teorico/`, `practico/`, `web/` o
`site.config.json`:

1. instala Pandoc,
2. corre `python3 web/build.py`,
3. publica el contenido de `web/site/` como **GitHub Pages**.

Por eso `web/site/` está en `.gitignore`: no hace falta commitear el HTML
generado, se reconstruye solo en cada push.

**Paso manual único (una sola vez por repositorio):** en GitHub, ir a
`Settings → Pages` y, en "Build and deployment → Source", elegir
**"GitHub Actions"** (en lugar de "Deploy from a branch"). Este es un ajuste
de configuración del repositorio, no de código, por lo que no puede
incluirse en el propio código del template.

A partir de ahí, cada `git push` a `main` regenera y publica el sitio
automáticamente; el estado de cada corrida puede verse en la pestaña
**Actions** del repositorio, y la URL pública queda en
`https://<usuario>.github.io/<repositorio>/`.

## 7. Publicar el sitio manualmente (alternativa sin Actions)

Si se prefiere no usar GitHub Actions, `web/site/` es un sitio estático común
y corriente: puede generarse localmente (`python3 web/build.py`) y
publicarse tal cual en GitHub Pages, Netlify, Vercel o cualquier hosting
estático, apuntando la publicación a esa carpeta como raíz.

## 8. Usar este repositorio como template para otras materias

La idea es tener **un repositorio "base"** (este) y, por cada materia nueva,
crear un repositorio aparte a partir de él, sin duplicar código a mano.

### 8.1. Marcarlo como template (una sola vez, en el repositorio base)

En GitHub: `Settings → General → Template repository` → tildar la casilla.
Esto habilita el botón verde **"Use this template"** en la página principal
del repositorio, que crea un repositorio nuevo con todo el contenido pero
sin el historial de commits del original.

### 8.2. Qué queda parametrizado y qué no

- **Parametrizado (no requiere tocar código):** el título del sitio y el
  nombre del autor/a, vía `site.config.json` en la raíz del repositorio.
  Es el único archivo a editar al crear una materia nueva:

  ```json
  {
    "site_title": "Apuntes de Álgebra Lineal",
    "site_author": "Nombre Apellido"
  }
  ```

- **Convención fija (por diseño):** la estructura de carpetas
  `teorico/src/claseN.md` y `practico/practicoN/src/ejM.md`. Se mantiene
  igual en todas las materias para que el generador funcione sin cambios;
  si una materia particular no tiene "práctico" o usa otro nombre, ver el
  punto 8.4.

### 8.3. Pasos para crear una materia nueva a partir del template

1. Botón **"Use this template" → "Create a new repository"** en GitHub,
   eligiendo el nombre del repositorio nuevo (ej. `algebra-lineal`).
2. Clonar el repositorio nuevo localmente.
3. Editar `site.config.json` con el título y autor de la materia.
4. Volcar los apuntes en `teorico` y `practico/practicoN` (y sus
   respectivas carpetas `img/`).
5. Hacer commit y push.
6. Configurar una única vez `Settings → Pages → Source: GitHub Actions`
   (paso 6 de este documento).

Desde ese momento, cada push regenera y publica el sitio de esa materia de
forma independiente del resto de los repositorios.

### 8.4. Generalización opcional (si algunas materias no usan "práctico")

Si en el futuro alguna materia no tiene ejercicios prácticos, o usa otra
nomenclatura (por ejemplo "seminario" en vez de "práctico"), el escaneo
podría parametrizarse también desde `site.config.json` (por ejemplo,
agregando claves como `"tiene_practico": false` o
`"nombre_seccion_practico": "Seminario"`) y ajustando `scanner.py` y
`page_builder.py` para leer esas claves en lugar de asumirlas fijas. En este
prototipo se mantuvo la convención fija por simplicidad, dado que todas las
materias de matemática suelen compartir la división teórico/práctico.

## 7. Estructura del código

| Archivo                        | Responsabilidad                                                          |
| ------------------------------ | ------------------------------------------------------------------------ |
| `build.py`                     | Orquesta todo el proceso de principio a fin.                             |
| `site_builder/config.py`       | Centraliza todas las rutas de entrada/salida.                            |
| `site_builder/scanner.py`      | Descubre los archivos Markdown de teoría y práctica.                     |
| `site_builder/converter.py`    | Convierte Markdown a HTML mediante Pandoc.                               |
| `site_builder/navigation.py`   | Calcula rutas de salida, orden secuencial (prev/next) y rutas relativas. |
| `site_builder/page_builder.py` | Ensambla el HTML final combinando plantillas, contenido y navegación.    |
| `templates/base.html`          | Plantilla común para las páginas de contenido (clase/ejercicio).         |
| `templates/index.html`         | Plantilla de la portada.                                                 |
| `static/css/styles.css`        | Estilos del sitio (tema oscuro, tipografía serif, diseño responsive).    |
| `static/js/nav.js`             | Interactividad de la barra lateral (menú móvil y subgrupos colapsables). |

## 8. Notas de diseño

- Cada página se genera respetando la relación relativa entre los archivos `.md` y las carpetas `img` del
  repositorio original (`../img/archivo.png`), por lo que las imágenes se
  copian preservando esa misma relación en la salida y **no** es necesario
  reescribir ningún enlace generado por Pandoc.
- Las fórmulas entre `$...$` y `$$...$$` se delegan a MathJax en el navegador;
  Pandoc únicamente las traduce a `\(...\)` / `\[...\]` (opción `--mathjax`).
- El proyecto no utiliza ningún framework de plantillas (Jinja2, etc.) para
  mantener el prototipo sin dependencias de `pip`; el reemplazo de
  marcadores `{{CLAVE}}` se resuelve con un simple `str.replace`.
