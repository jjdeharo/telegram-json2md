# eXeLearning: recetas probadas

Cómo resolver tareas para las que eXeLearning no tiene una opción directa (cambiar
algo en todas las páginas con un trozo de código, o traer contenido de otro
sitio) o que el programa permite aunque no lo parezca. Cada receta se ha probado de verdad: se dice con qué versión, en qué casos
funciona y en cuáles no, y lo que no se ha podido probar se dice como tal.

Este documento es una síntesis propia. **Cada afirmación indica de dónde sale**:
el manual, el código del programa, un mensaje del grupo o la prueba hecha.

Última revisión: 5 de noviembre de 2026.

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

---

## Saltos de línea en la retroalimentación del Formulario

En el iDevice **Formulario**, los campos de retroalimentación de cada pregunta
(el que se muestra al acertar y el que se muestra al fallar) son de una sola
línea: la tecla Intro no hace un salto. Para partir el texto, se escribe
`<br>` donde tiene que ir el salto:

```
¡Correcto!<br>El agua hierve a 100 °C a nivel del mar.
```

**Probado** el 5-11-2026 con eXeLearning 4.0.6 en una pregunta de verdadero o
falso: el texto sale en varias líneas en el editor y en la vista previa, y el
`<br>` se conserva al volver a editar la pregunta. Según el código del
programa, los otros tipos de pregunta del Formulario (rellenar, desplegable y
selección) usan los mismos campos; con ellos no se ha probado. Otra vía que
encontró un usuario del grupo, `\( \\ \)`, también parte la línea, pero lo
hace con el motor de fórmulas; `<br>` es más directo.

---

## Crear un proyecto a partir de un PDF o de un documento de LibreOffice

eXeLearning no importa PDF ni documentos de oficina: solo abre e importa
proyectos (`.elpx`, `.elp`), paquetes `.zip` editables y `.epub` (código de la
4.0.6). Para traer su contenido está eXeConvert (https://execonvert.github.io/),
de Juan José de Haro, que lo convierte en un proyecto de eXeLearning (`.elpx`)
en el navegador, sin subir el archivo a ningún sitio. **Pasa el contenido, no
el diseño.**

**PDF** (desde la versión 0.8.0 de eXeConvert, solo en la web):
1. Abre el PDF en eXeConvert, elige cómo se reparten las páginas (qué títulos
   abren página nueva) y pulsa **Previsualizar**.
2. En la ventana que se abre se eligen las páginas del PDF, se quitan los
   encabezados y pies repetidos, se conservan las imágenes y, si hay páginas
   escaneadas, se puede aplicar OCR para tener su texto. Pulsa **Convertir**,
   revisa la vista previa y pulsa **Crear el proyecto**.
3. Revisa la vista previa del proyecto y guarda el `.elpx`.

Llegan el texto, los títulos, las listas, las tablas con líneas, las imágenes y
las notas al pie (al final de la sección que las cita). No llegan el diseño ni
las columnas, y una tabla sin líneas verticales sale como párrafos. La primera
vez descarga el conversor (unos 34 MB), y en Firefox tarda algo más que en
Chrome.

**Documento de texto de LibreOffice (`.odt`)**: en LibreOffice, **Archivo >
Guardar como** en formato Word (`.docx`), que conserva mejor el formato que un
PDF, y abre ese `.docx` en eXeConvert.

**Presentación (`.odp` o `.pptx`)**: eXeConvert no las abre. Exporta la
presentación a PDF desde LibreOffice o PowerPoint y sigue los pasos del PDF;
llega el texto de cada diapositiva, no su composición.

**Probado** el 5-11-2026 con eXeConvert 0.8.0, en Chromium y en Firefox, con
tres PDF: uno con notas al pie y una tabla, uno con imagen, tablas y
encabezados repetidos, y uno escaneado con OCR. La vista previa de eXeConvert,
que usa el motor de eXeLearning 4.0.6, mostró el proyecto con sus páginas,
imágenes y notas. Lo de los `.odt` y las presentaciones no se ha probado.

---

## Recuperar un iDevice, un bloque o una página que se ha borrado

Mientras el proyecto siga abierto, se recupera con **Deshacer**: la flecha hacia
la izquierda de la barra superior, junto al menú Ayuda, o **Ctrl+Z** (**⌘+Z** en
Mac). La flecha de al lado, o **Ctrl+Mayús+Z**, lo rehace. El iDevice vuelve con
su contenido y en su sitio.

**No hay que fiarse del aviso.** Al borrar un iDevice, eXeLearning pregunta
«¿Eliminar el iDevice? Esta acción no se puede deshacer», pero sí se puede. Al
borrar una página, en cambio, el aviso ya dice que se puede deshacer. Está avisado
al equipo en la incidencia https://github.com/exelearning/exelearning/issues/2685.

**Cuándo no funciona:**
- Si hay un iDevice abierto para editar, primero hay que cerrarlo (guardándolo o
  descartando los cambios): mientras está abierto, Ctrl+Z deshace dentro de ese
  iDevice, no en el proyecto.
- Deshacer va paso a paso hacia atrás: si después de borrar se hicieron otros
  cambios, se deshacen antes esos.
- El historial se pierde al cerrar el proyecto o abrir otro. Entonces solo queda
  una copia guardada antes de borrarlo: si desde que se borró no se ha guardado,
  se puede cerrar sin guardar y volver a abrir el archivo, a costa de perder todo
  lo hecho desde la última vez que se guardó.

**Probado** el 1-11-2026 en la versión en desarrollo de eXeLearning en línea
(online.exelearning.dev): un iDevice de texto borrado volvió con la flecha y con
Ctrl+Z. Con bloques y páginas no se ha probado: según el código, el mismo
historial guarda todos los cambios de la estructura del proyecto. En el código
del programa, Deshacer existe desde la 4.0.0, y la parte que lo hace es igual en
la 4.0.6 que en la versión probada; en la 4.0.6 instalada no se ha probado.
