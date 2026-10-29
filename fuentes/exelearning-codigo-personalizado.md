# eXeLearning: ajustes con código personalizado

Recetas para cambiar el aspecto de todo un proyecto de eXeLearning con un trozo
de código, cuando el programa no tiene una opción para hacerlo. Cada receta se
ha probado en una exportación real: se dice con qué versión, con qué estilos y en
qué formatos funciona, y en cuáles no.

Este documento es una síntesis propia. **Cada afirmación indica de dónde sale**:
el manual, el código del programa, un mensaje del grupo o la prueba hecha.

Última revisión: 29 de octubre de 2026.

---

## Dónde se pone el código

En **Propiedades del proyecto** (menú Archivo), apartado **Código personalizado**,
hay dos cuadros: **HEAD** y **Pie de página**. Lo que se escribe en HEAD se añade
a todas las páginas del contenido exportado; ahí van los estilos (`<style>…</style>`).
El manual de la 4.0.5 lo menciona sin más detalle: en las propiedades del proyecto
se puede «añadir código personalizado».

**Ojo: en la 4.0.5, el código de HEAD solo llega a la exportación como sitio web.**
Al exportar como página única, SCORM o ePub no se incluye. Comprobado el
29-10-2026 exportando el mismo proyecto en los cuatro formatos, y en el código del
programa: solo el exportador de sitio web lo añade, también en la versión en
desarrollo de esa fecha. Para los demás formatos, la vía es poner la regla en el
estilo (ver más abajo).

Para deshacer cualquier receta, basta con borrar el trozo y volver a exportar.

---

## Ocultar el título de todas las páginas

Cada página tiene la casilla **Ocultar título de la página** en sus propiedades,
pero no hay una opción para todas a la vez. Con este código, el título deja de
verse en todas las páginas del proyecto:

```
<style>
.page-title {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    margin: -1px !important;
    padding: 0 !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}
</style>
```

**Qué hace.** Oculta el título igual que la casilla de cada página: deja de verse,
pero sigue en la página para los lectores de pantalla y los buscadores. Es lo que
pide el equipo de eXeLearning: las páginas siempre tienen título, y no debe
quitarse del todo (Ignacio, equipo de eXeLearning:
https://t.me/eXeLearning/34114). Por eso no vale un `display: none`.

**No toca** el título del proyecto, que va en la cabecera, ni los títulos de los
iDevices.

**Por qué esta regla y no otra.** Varios estilos sacan el título de la cabecera de
la página y lo colocan encima del contenido. Una regla que busque el título dentro
de la cabecera (`.page-header .page-title`) no funciona con ellos: en la prueba
dejó el título a la vista con Flux, Neo, Nova y Zen.

**Probado** el 29-10-2026 con eXeLearning 4.0.5, exportando como sitio web un
proyecto de 14 páginas con los siete estilos que trae el programa (Base,
Educablue, Flux, Neo, Nova, Universal y Zen): el título queda oculto en todas las
páginas, en Chromium y en Firefox, en ordenador y en móvil, y la página no se
descoloca.

### En SCORM, página única o ePub

Como el código de HEAD no llega a esos formatos, la misma regla (sin las líneas
`<style>` y `</style>`) tiene que ir dentro del estilo, al final de su archivo
`style.css`. El estilo viaja con el contenido en todos los formatos.

**Probado** el 29-10-2026 con la 4.0.5: con la regla al final del `style.css` del
estilo, el título queda oculto en SCORM 1.2, en página única y en ePub (el ePub,
abierto en Chromium).

Para editar el estilo sin instalar nada está el
[Editor de estilos para eXeLearning (EdEX)](https://exe-style-editor.github.io/),
de Juan José de Haro: se carga el proyecto `.elpx` o el estilo, se pega la regla
al final de `style.css` en la pestaña Archivos y se exporta el `.elpx` con el
estilo ya modificado (o el estilo en `.zip` para importarlo en eXeLearning). Este
recorrido por EdEX no se ha probado con esta regla; lo que se ha probado es que la
regla funciona dentro del estilo.
