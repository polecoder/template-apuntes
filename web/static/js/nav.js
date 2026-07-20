/**
 * @file nav.js
 * @brief Interactividad mínima de la barra lateral de navegación.
 * @details No depende de ninguna librería externa. Resuelve dos cosas:
 *          1) abrir/cerrar la barra lateral en pantallas angostas (móvil),
 *          2) desplegar/colapsar los subgrupos de "Práctico N" para no
 *             mostrar todos los ejercicios de todos los prácticos a la vez.
 */

/**
 * @brief Inicializa el botón hamburguesa que muestra/oculta la barra lateral en móvil.
 */
function inicializarMenuMovil() {
  const boton = document.getElementById("boton-menu");
  const barraLateral = document.getElementById("barra-lateral");
  const fondoSuperpuesto = document.getElementById("fondo-superpuesto");

  if (!boton || !barraLateral || !fondoSuperpuesto) {
    return;
  }

  const alternarMenu = (abrir) => {
    barraLateral.classList.toggle("abierta", abrir);
    fondoSuperpuesto.classList.toggle("visible", abrir);
    boton.setAttribute("aria-expanded", String(abrir));
  };

  boton.addEventListener("click", () => {
    const estaAbierta = barraLateral.classList.contains("abierta");
    alternarMenu(!estaAbierta);
  });

  fondoSuperpuesto.addEventListener("click", () => alternarMenu(false));
}

/**
 * @brief Habilita el despliegue/colapso de cada subgrupo "Práctico N" al hacer clic en su título.
 */
function inicializarSubgrupos() {
  const titulosSubgrupo = document.querySelectorAll(".nav-subgrupo__titulo");

  titulosSubgrupo.forEach((titulo) => {
    titulo.addEventListener("click", () => {
      const subgrupo = titulo.closest(".nav-subgrupo");
      if (subgrupo) {
        subgrupo.classList.toggle("abierto");
      }
    });
  });
}

/**
 * @brief Abre automáticamente el subgrupo que contiene el enlace marcado como activo.
 * @details Así, al entrar a un ejercicio puntual, el práctico correspondiente
 *          aparece ya desplegado en la barra lateral en lugar de colapsado.
 */
function abrirSubgrupoActivo() {
  const enlaceActivo = document.querySelector(".nav-lista a.activo");
  if (!enlaceActivo) {
    return;
  }

  const subgrupo = enlaceActivo.closest(".nav-subgrupo");
  if (subgrupo) {
    subgrupo.classList.add("abierto");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  inicializarMenuMovil();
  inicializarSubgrupos();
  abrirSubgrupoActivo();
});
