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

## Pasar una web a eXeLearning (Google Sites y otras)

eXeLearning no importa webs. eXeConvert (https://execonvert.github.io/), de
Juan José de Haro, convierte una web guardada en un proyecto de eXeLearning
(`.elpx`): una página o un sitio entero en un ZIP. **Pasa el contenido, no el
diseño.** Lo que sigue vale desde la versión 0.7.2 de eXeConvert (29-10-2026).

**Google Sites.** Google Sites no tiene botón de descarga; se saca con Google
Takeout (takeout.google.com):
1. Desmarca todo, marca Drive y, en la lista de carpetas de Drive, deja marcada
   solo la carpeta donde está el sitio. Takeout no deja elegir archivos sueltos:
   si el sitio está suelto en «Mi unidad», muévelo antes a una carpeta propia y
   devuélvelo después.
2. Crea la exportación. Google avisa por correo cuando está lista y pide la
   contraseña de la cuenta al descargar el ZIP.
3. Sube a eXeConvert el ZIP tal como llega, sin abrirlo, y guarda el `.elpx`.

Si el sitio está publicado, el ZIP trae el borrador y la versión publicada;
eXeConvert convierte el borrador, con los cambios que aún no se hayan publicado.

**Otras webs.** Funciona con un ZIP de una web estática cuyas páginas se enlazan
entre sí con rutas relativas, como la que guardan los programas para descargar
webs (HTTrack, `wget`) o la que crean los generadores de webs (MkDocs, Jekyll…).
Una página suelta se puede subir como `.html` o en un ZIP con sus imágenes.

**Qué hace eXeConvert:**
- Cada página de la web es una página del proyecto, en el orden y con la
  jerarquía del menú de la web, y con el nombre que lleva en el menú.
- Los encabezados de cada página se convierten en bloques.
- Los enlaces entre páginas siguen funcionando; los enlaces a otras webs se
  mantienen.
- Las imágenes se guardan en el proyecto, y las de más de 1920 px se reducen a
  esa medida para que el proyecto no pese de más.
- Deja fuera el menú, la cabecera, el pie y las barras laterales de la web: en
  eXeLearning el menú es el del propio programa.

**Qué no llega o hay que retocar:**
- El diseño: columnas, colores, fondos y tarjetas.
- El tamaño con que se veía cada imagen. Una imagen grande puede verse más
  grande que en la web original; se ajusta en eXeLearning, en las propiedades
  de la imagen.
- Lo que la web genera al mostrarse, como la lista automática de subpáginas de
  Google Sites, y los archivos de Drive incrustados.
- Las webs que cargan el contenido con JavaScript llegan vacías.
- Las páginas enlazadas con la dirección completa de la web
  (`https://…`) no se siguen: solo entra la principal.
- Los desplegables del menú que no son una página (un rótulo que agrupa
  otras) no se conservan: sus páginas quedan a su mismo nivel.

Probado el 29-10-2026 con dos Google Sites, uno de ellos de 27 páginas, y con la
web de MkDocs descargada con `wget`. eXeLearning 4.0.6 abrió los proyectos y
los exportó con sus imágenes y sus enlaces.
