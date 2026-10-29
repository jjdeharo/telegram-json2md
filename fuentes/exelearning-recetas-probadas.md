# eXeLearning: recetas probadas

Cómo resolver tareas para las que eXeLearning no tiene una opción directa: cambiar
algo en todas las páginas con un trozo de código, o traer contenido de otro
sitio. Cada receta se ha probado de verdad: se dice con qué versión, en qué casos
funciona y en cuáles no, y lo que no se ha podido probar se dice como tal.

Este documento es una síntesis propia. **Cada afirmación indica de dónde sale**:
el manual, el código del programa, un mensaje del grupo o la prueba hecha.

Última revisión: 29 de octubre de 2026.

---

## Código personalizado: dónde se pone

En **Propiedades del proyecto** (menú Archivo), apartado **Código personalizado**,
hay dos cuadros: **HEAD** y **Pie de página**. Lo que se escribe en HEAD se añade
a todas las páginas del contenido exportado; ahí van los estilos (`<style>…</style>`).
El manual de la 4.0.5 lo menciona sin más detalle: en las propiedades del proyecto
se puede «añadir código personalizado».

**Ojo: en la 4.0.5, el código de HEAD solo llega a la exportación como sitio web.**
Al exportar como página única, SCORM o ePub no se incluye. Comprobado el
29-10-2026 exportando el mismo proyecto en los cuatro formatos, y en el código del
programa: solo el exportador de sitio web lo añade, también en la versión en
desarrollo de esa fecha. Lo mismo pasa con el cuadro **Pie de página**. En la
3.0.2 sí llegaba a todos los formatos. Está avisado al equipo en la incidencia
https://github.com/exelearning/exelearning/issues/2667. Para los demás formatos,
la vía es poner la regla en el estilo (ver más abajo).

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

---

## Pasar un sitio de Google Sites a eXeLearning

eXeLearning no importa un sitio de Google Sites. Se puede llevar su contenido en
dos pasos: sacar el sitio de Google como páginas HTML y convertir cada página con
eXeConvert. **Pasa el contenido, pero no el diseño**, y hay que rematarlo a mano.
Probado el 29-10-2026 con un sitio de dos páginas hecho con una plantilla de
Google Sites, sin publicar.

**1. Sacar el sitio con Google Takeout.** Google Sites no tiene un botón de
descargar, pero Google Takeout (takeout.google.com) exporta el sitio dentro de los
datos de Drive. Para no exportar todo Drive:
- Pon el sitio en una carpeta de «Mi unidad», sola. Según la Universidad de
  Míchigan, un sitio en una unidad compartida no se puede exportar
  (https://teamdynamix.umich.edu/TDClient/30/Portal/KB/Article/15738/Google-Download-Site-as-HTML-File);
  esto no se ha probado.
- En Takeout, desmarca todo, marca Drive y, en la lista de carpetas de Drive,
  deja marcada solo esa carpeta.
- Crea la exportación. Google avisa por correo cuando está lista (en la prueba,
  en unos minutos) y pide la contraseña de la cuenta al descargar el ZIP.

Dentro del ZIP, cada página del sitio es un archivo `.html`, con sus imágenes en
una carpeta del mismo nombre. En la prueba, con un sitio sin publicar, salieron
en una carpeta `DRAFT` (borrador). Los nombres de archivo pierden las tildes
(«Documentación» llegó como `Documentacin.html`).

**2. Convertir cada página con eXeConvert** (https://execonvert.github.io/), de
Juan José de Haro, que importa páginas HTML a `.elpx`. Para que entren las
imágenes, hay que hacer un ZIP con el `.html` de la página y su carpeta de
imágenes, y subir ese ZIP. Una página por ZIP: si van varias, se convierte solo
una. Los encabezados de la página se convierten en bloques de eXeLearning.

**Qué llega y qué no** (comparando la página original con la convertida):
- Llegan el texto, los encabezados, las listas, los enlaces y las imágenes que
  van dentro del contenido.
- No llegan el diseño de Google Sites (columnas, tarjetas, la imagen de fondo de
  la cabecera) ni el menú del sitio. Las secciones desplegables quedan abiertas.
- Desde la versión 0.6.4 de eXeConvert (29-10-2026):
  - La página toma el título de la pestaña del navegador: en la página de
    inicio, el nombre del sitio; en las demás, el del sitio y el de la página
    («Centro de Ayuda - Documentación»), que se puede acortar a mano.
  - Los enlaces a otras páginas del sitio y a secciones de la misma página se
    quitan y queda su texto, porque dentro del proyecto no llevarían a ninguna
    parte: si hacen falta, se rehacen en eXeLearning. Los enlaces a otras webs
    se mantienen.
  - Las imágenes se guardan como archivos del proyecto, y las de más de
    1920 px de lado se reducen a esa medida, que basta para verlas en
    eXeLearning. En la prueba, la página con una foto grande pasó de 16,5 MB a
    2,4 MB, y eXeLearning 4.0.5 la abrió y la exportó con sus imágenes.

**3. Juntar las páginas en un proyecto.** Según el manual de la 4.0.5, desde las
opciones de una página (los tres puntos) se puede importar un proyecto completo,
que entra como subpáginas de la página elegida. Así se reúnen las páginas
convertidas. Este paso no se ha probado.
