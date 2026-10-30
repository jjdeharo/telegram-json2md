# eXeLearning en cada plataforma

Cómo se publica un contenido de eXeLearning en las plataformas que se usan en
España, y qué falla habitualmente en cada una.

Este documento es una síntesis: reúne en un solo sitio respuestas que están
dispersas por las conversaciones del grupo de Telegram y por los repositorios de
los plugins. **Cada afirmación indica de dónde sale.** Cuando la respuesta la dio
el equipo de eXeLearning (Ignacio, Cristina, Martín Núñez, Ernesto Serrano) se
señala; cuando viene de la experiencia de un usuario, también, porque no tiene el
mismo valor.

Última revisión: 30 de octubre de 2026.

---

## Dónde se puede publicar

Hay dos caminos, y una respuesta completa cuenta los dos:

1. **Exportar** desde eXeLearning (sitio web, página sola, SCORM 1.2, IMS,
   ePub3, PDF) y subir el resultado a la plataforma. Es lo que explica el manual
   de usuario.
2. **Usar el plugin de la plataforma**: el recurso (`.elpx`) se crea, se edita y
   se publica sin salir de ella, con el editor de eXeLearning integrado. Todos
   son gratuitos y de código abierto.

| Plataforma | Plugin | Qué permite | Quién lo instala |
|---|---|---|---|
| Moodle | `mod_exelearning` (Recurso eXeLearning), **el recomendado** | Actividades que se califican solas, una columna por ejercicio | Administración del Moodle |
| Moodle | `mod_exescorm` | Paquete SCORM 1.2, una nota global | Administración del Moodle |
| Moodle | `mod_exeweb` | Materiales de consulta, sin nota | Administración del Moodle |
| Nextcloud | app eXeLearning | Ver, editar y crear recursos desde Archivos | Administración del Nextcloud |
| WordPress | plugin eXeLearning | Subir el recurso a Medios, editarlo y mostrarlo en entradas y páginas con un bloque o un código corto | Administración del WordPress |
| Omeka S | módulo ExeLearning | Añadir recursos como medios de las fichas, verlos y editarlos | Administración del Omeka S |
| Google Drive | eXeLearning para Google Drive (`exelearning.github.io/gdrive-exelearning`) | Abrir, editar y crear recursos guardados en Drive y compartirlos con el alumnado con un enlace público | Nadie: cada docente entra con su cuenta |
| OneDrive | eXeLearning para OneDrive (`exelearning.github.io/onedrive-exelearning`) | Abrir, editar y crear recursos guardados en OneDrive | Nadie: cada docente entra con su cuenta |

Fuente: documentación oficial de los plugins (`doc/plugins/` del repositorio de
eXeLearning, publicada el 19/10/2026). Cada plugin tiene una demostración que se
abre en el navegador sin instalar nada (Moodle, Nextcloud, WordPress y Omeka S
Playground); los enlaces están en esa documentación.

Detalles que suelen preguntarse:

- **Requisitos.** `mod_exelearning` pide Moodle 4.5 o posterior; `mod_exescorm`
  y `mod_exeweb`, Moodle 4.2. La app de Nextcloud, Nextcloud 31 a 33 (la 4.0.5
  del plugin, solo la 33). WordPress 6.1 y PHP 8.0. Omeka S 4.0.
- **Google Drive y OneDrive con cuentas del centro.** Si el dominio de Google
  Workspace restringe aplicaciones de terceros, la administración tiene que
  permitir eXeLearning; en Microsoft 365, si los usuarios no pueden aceptar
  aplicaciones, la administración concede el consentimiento («Se necesita la
  aprobación del administrador»). El enlace público de Drive exige que el
  dominio permita compartir con «Cualquier persona con el enlace».
- **OneDrive no añade eXeLearning a sus menús**: siempre se empieza desde la
  página de la aplicación. En Drive, sí aparece en **Abrir con** y **Nuevo**.
- **No es lo que había en la 3.x.** La subida a Dropbox y Google Drive desde el
  propio programa se retiró en la 4.0.1 (registro de cambios); los plugins de
  Drive y OneDrive son aplicaciones aparte.

---

## Moodle

### Qué formato elegir

| Quieres… | Sube… | Se ve… |
|---|---|---|
| Calificaciones y seguimiento | SCORM 1.2 | Dentro del visor SCORM de Moodle |
| Solo mostrar el contenido | ZIP de sitio web | Igual que en la vista previa de eXeLearning |

> «Si no tienes que recoger calificaciones ni hacer seguimiento del alumnado,
> puedes subirlo como archivo zip en lugar de scorm, y así podrás verlo igual que
> lo ves en exe en visualización previa» — Cristina, equipo de eXeLearning,
> 17/06/2026.

### «Se ve raro, con una barra lateral que yo no puse»

No es un fallo de eXeLearning. Moodle muestra **todos** los paquetes SCORM dentro
de su propio visor, con su barra de navegación:

> «Moodle utiliza un visor de scorm para mostrar este tipo de paquetes, cualquier
> SCORM que subas se verá así, esté creado con exe o con otra herramienta» —
> Cristina, equipo de eXeLearning, 17/06/2026.

Esa barra se puede quitar desde los ajustes de la actividad SCORM en Moodle
(Juanjo de Haro, 17/06/2026).

### «No aparecen los botones de siguiente página»

Depende de los ajustes de la actividad, no del contenido. Moodle muestra las
flechas de navegación por defecto en los SCORM que sube uno; si no salen, hay que
revisar la sección **Apariencia** de la actividad y pulsar «Mostrar más» para ver
todas las opciones (Ange Sago, 19/08/2026, comprobado con SCORM del plugin y
estándar).

*Nota: en ese mismo hilo se dijo primero que SCORM no lleva botones y que los
recrea la plataforma. Es incorrecto y quedó rectificado.*

### Intentos y calificación

Se configuran en la actividad de Moodle, no en eXeLearning: número de intentos
permitidos y si cuenta la nota del primero, la mejor o la última (JM, 18/06/2026).

Conviene **desactivar «auto-continue»**, que hace saltar de página aunque no se
haya visto (JM, 16/06/2026).

### Publicar como sitio web (ZIP), paso a paso

1. Añadir un recurso de tipo **Archivo**.
2. Subir el ZIP del sitio web exportado.
3. Hacer clic en el archivo subido y pulsar **Descomprimir**.
4. Hacer clic en `index.html` y elegir **Configurar como archivo principal**.
5. Guardar. Se recomienda abrirlo en ventana nueva.

(JM, 17/06/2026, citando el manual oficial de eXeLearning.)

### Los plugins oficiales de Moodle

Hay tres, mantenidos por el proyecto, que pueden convivir en el mismo Moodle:

- **mod_exelearning** (Recurso eXeLearning) — `github.com/exelearning/moodle-mod_exelearning`.
  Es el recomendado para contenidos nuevos: conserva el menú del recurso y manda
  al libro de calificaciones la nota de cada ejercicio por separado. Requiere
  **Moodle 4.5** o posterior.
- **mod_exescorm** — `github.com/exelearning/mod_exescorm`. Paquete SCORM 1.2,
  una nota global.
- **mod_exeweb** — `github.com/exelearning/mod_exeweb`. Sitio web, sin nota.

`mod_exescorm` y `mod_exeweb` requieren **Moodle 4.2 como mínimo** y están
verificados hasta Moodle 5.2.x (README de los plugins, `version.php`). Los tres
incluyen un editor de eXeLearning integrado, así que se puede editar el
contenido dentro de Moodle sin servidor externo (documentación oficial de los
plugins, 19/10/2026).

**El fallo más repetido del grupo, con diferencia**: una plataforma institucional
rechaza un exportado hecho con eXeLearning 3.x o 4.x, o lo muestra mal. La causa
casi siempre es que esa plataforma lleva la **versión antigua** de los módulos,
que solo admite exportados de la 2.9:

> «Lo que les ocurre […] es que dichas plataformas tienen ahora los módulos
> mod_exeweb y mod_exescorm antiguos, los que solo admiten los exportados web y
> scorm 1.2 de eXeLearning 2.9. Y necesitan ser actualizados a los nuevos módulos
> […], algo que sólo pueden hacer los administradores de dichas plataformas» —
> ismagago, 09/06/2026.

No hay nada que el docente pueda hacer desde su lado salvo pedir la
actualización, o exportar en 2.9 mientras tanto.

Si la plataforma va por Moodle 3.x, los plugins **no se pueden instalar**: por
debajo de Moodle 4.2 solo queda la actividad SCORM estándar de Moodle; entre la
4.2 y la 4.4, `mod_exescorm` y `mod_exeweb`, pero no `mod_exelearning`.

### Comprobar si el problema es del paquete o de Moodle

Para salir de dudas, probar el paquete en **SCORM Cloud**
(`cloud.scorm.com`) o comparar con los paquetes SCORM oficiales de ejemplo de
`scorm.com`. Hay que usar el ejemplo **multi-sco**, que es la modalidad de
empaquetado que usa eXeLearning (JM, 19/06/2026).

### GeoGebra dentro de Moodle

Se pueden poner **varias** actividades de GeoGebra en una misma página si no se
guarda la puntuación. Si se va a guardar en un LMS, **solo una por página**
(Manuel Narváez, 31/08/2026).

### Exportar solo una parte

No existe exportar una sola página como SCORM. Lo que se hace es exportar esa
página como `.elpx` independiente y convertir ese archivo (Ernesto J. Abad,
14/08/2026).

---

## Procomún

- Admite los exportados **SCORM 1.2 de eXeLearning 4.x**: se pueden publicar,
  aunque **no editar** dentro de Procomún (ismagago, 23/06/2026, con un ejemplo
  publicado; confirmado por Cristina con los compañeros de Procomún).
- **Límite de tamaño: 42 MB** por archivo (ismagago, 23/06/2026).

---

## EducaMadrid

Opciones de publicación, según Ignacio (equipo de eXeLearning, 08/06/2026):

- **Aula Virtual**, con los plugins de eXeLearning — sujeto a que la
  administración los tenga actualizados (ver el apartado de Moodle).
- **Cloud EducaMadrid**: subir el `.elpx`, crear un enlace para compartir y
  abrirlo con eXeViewer.
- **Directorio de Ficheros del Portal** u otro espacio con enlace directo, más
  eXeViewer.
- **Mediateca**: alojar y editar desde ahí estaba anunciado, aún no disponible.

Hay una explicación detallada en vídeo, a partir del minuto 55:
`mediateca.educa.madrid.org/video/qgj4oo2393fgyczs`.

Un camino que varios usuarios confirman que funciona hoy: colgar el `.elpx` en el
Cloud, compartirlo por enlace y abrirlo con un visor; la URL resultante se puede
incrustar en el Aula Virtual (Pablo, 17/06/2026).

---

## Junta de Andalucía (EducaAnd, EducaAndOS)

- Existe un **estilo EducaAnd** actualizado para eXeLearning 4, en pruebas a
  mediados de 2026 y aún no publicado en ese momento (Ernesto J. Abad,
  01/07/2026). Los proyectos ya empezados con más de 100 situaciones de
  aprendizaje se mantenían en 2.9 por unidad de estilo.
- **EducaAndOS** (basado en Ubuntu 20.04): se informó de que al guardar desde
  eXeLearning online se descargaban carpetas sueltas en vez de un `.elpx`. La
  explicación más probable, no confirmada del todo, es que el `.elpx` sí se
  descarga pero el sistema lo reconoce como ZIP —al no tener eXeLearning 4
  instalado— y lo abre mostrando su contenido (Juanjo de Haro y Pablo,
  19–20/06/2026).

---

## Compartir sin aula virtual

### eXeViewer

`exeviewer.intef.es` — abre `.elpx` y `.zip` en el navegador, sin instalar nada
ni crear cuenta.

Desde agosto de 2026 se puede **instalar como aplicación** (PWA) y **funciona sin
conexión**: se entra con un navegador que permita instalar PWA y se pulsa
«Instalar»; si hay conexión, avisa cuando hay versión nueva (Ignacio, equipo de
eXeLearning, 21/08/2026). Verificado por usuarios en Ubuntu con Chromium en modo
avión y en Android.

Admite abrir archivos alojados en Google Drive, Nextcloud y similares mediante
enlace de descarga directa.

**La puntuación de las actividades no se guarda en ninguna plataforma.** Si hace
falta registrar notas, el camino es un LMS.

### Visor Web-ZIP

`visor-webzip.github.io` — mismo funcionamiento, y además permite fijar día y
hora de apertura y cierre del contenido (Juanjo de Haro, 29/08/2026).

---

## GitHub Pages

Sirve para publicar un contenido exportado como sitio web y tener una dirección
propia.

- Para **actualizar** un contenido ya publicado: borrar los archivos anteriores,
  volcar el ZIP descomprimido en la carpeta y subir. Con GitHub Desktop no hace
  falta borrar nada, el programa se encarga (Juanjo de Haro, 16/06/2026).
- Si la página se publica pero **no se ve bien o faltan archivos**, la causa
  habitual es que falta el archivo `.nojekyll` en la raíz (Ernesto Serrano
  `@erseco`, equipo de desarrollo de eXeLearning, 05/2026).

---

## Qué mirar antes de culpar a la plataforma

Tres comprobaciones que resuelven buena parte de los casos:

1. **La versión con la que se exportó** frente a la que admite la plataforma. Es
   la causa número uno.
2. **El tamaño**. Procomún corta en 42 MB; y un proyecto de cientos de megas dará
   problemas en cualquier sitio. Lo recomendado es sacar los vídeos y audios a un
   proveedor externo y optimizar las imágenes: un curso completo cabe en 25 MB
   (Manuel Romero, 28/08/2026).
3. **Si el problema se reproduce fuera de la plataforma**: probar el mismo
   paquete en eXeViewer o en SCORM Cloud. Si allí va bien, el problema es de la
   plataforma.
