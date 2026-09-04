# El cuaderno de eXeLearning

El cuaderno **Karla - Experta en eXeLearning** responde a usuarios de
eXeLearning, pero con criterio de programador: además del manual de usuario
lleva la documentación técnica del proyecto, para poder explicar *por qué* el
programa se comporta como lo hace y no solo *qué* botón pulsar.

Tiene cuatro clases de fuentes:

1. **Las conversaciones del grupo de Telegram**, que se actualizan solas cada
   día como las de los otros dos grupos.
2. **El manual de usuario**, consolidado del sitio oficial de CEDEC/INTEF.
3. **La documentación técnica del repositorio**, sincronizada desde
   `github.com/exelearning/exelearning`.
4. **La documentación del ecosistema**: los plugins con los que se publica
   (Moodle y WordPress), el visor y las utilidades.
5. **Los documentos escritos a mano**, en `fuentes/`, para lo que se pregunta y
   no está documentado en ningún repositorio.

Los tres últimos los mantiene `scripts/exelearning.py`.

## Qué documentación entra y cuál no

El criterio es una sola pregunta: **¿ayuda a explicar el programa o su formato de
archivo?**

**Entra**: el formato `.elpx` al completo —incluido el catálogo de iDevices, que
es la referencia autorizada de qué hace cada uno y cómo guarda su estado—, la
arquitectura, las decisiones de arquitectura (ADR), las convenciones, la
instalación y el despliegue, la API REST, la autenticación, el tiempo real, la
personalización y estilos, el contrato del runtime SCORM 1.2, los problemas
conocidos, la guía de actualización de la 3.x a la 4.x, el registro de cambios de
cada versión y el iDevice de fundamentación curricular LOMLOE.

**No entra** lo que solo explica cómo se colabora en el repositorio: cómo abrir
un pull request, la estrategia de ramas, cómo ejecutar las pruebas, el entorno
de desarrollo o las herramientas de *profiling*. No pueden responder a nadie y
compiten con lo útil a la hora de recuperar fragmentos.

Tampoco entran `AGENTS.md` ni `CLAUDE.md`: son **instrucciones dirigidas a una
IA que trabaja sobre el código**, y en un cuaderno de soporte pueden filtrarse en
las respuestas y acabar diciéndole a un profesor que siga las convenciones de
commits del proyecto.

La lista concreta está en `INCLUIR`, dentro de `scripts/exelearning.py`.

## De qué versión es lo que hay aquí

El cuaderno describe el programa **publicado**, no el que se está escribiendo.
La documentación técnica del repositorio se toma del último tag —hoy la v4.0.3—
y no de `main`, que va decenas de commits por delante. El motivo es el público:
quien pregunta tiene instalada la versión publicada, y una respuesta que explique
cómo usar algo que aún no ha salido le manda a buscar un menú que no existe.

Se descartó subir las dos versiones de cada documento, la publicada y la de
desarrollo. Duplicar no sale caro por el número de fuentes —hoy serían cinco
más—, sino por la recuperación: dos textos casi idénticos sobre el mismo tema
compiten entre sí, y lo probable no es que el cuaderno elija bien, sino que
mezcle párrafos de ambos. Cuanto más se parecen, peor.

Lo que está por llegar vive concentrado en dos fuentes, y solo en esas dos:

- **`exelearning-public-CHANGELOG`**, que sí se toma de `main` porque su sección
  `Unreleased` es justamente la frontera entre lo publicado y lo que viene.
- **`exelearning-doc-architecture-decisiones`**, los ADR, que por naturaleza son
  decisiones sobre el futuro. Abre con un aviso que dice desde dónde se
  sincroniza, cuántos commits se le lleva a la versión publicada y qué significan
  `Proposed` y `Accepted` —ninguno de los dos es «publicado»—.

El índice lleva el aviso equivalente para el conjunto. Ambos se generan en cada
pasada con `git describe`, así que la versión y la distancia no se quedan viejas,
y el día que salga una versión nueva los documentos que se hubieran adelantado
entran solos.

Un documento que todavía no exista en el tag no se sube, y si ya estaba subido se
retira: es el caso de `doc/development/scorm12-runtime-contract.md`, el contrato
del runtime SCORM reescrito, que volverá cuando se publique.

## El ecosistema, y por qué está aquí

Lo que más se pregunta en el grupo no es cómo se usa eXeLearning —el manual lo
cubre bien— sino **cómo se saca el contenido del programa y se pone donde el
alumnado lo use**. En los cinco meses hasta septiembre de 2026, SCORM se
mencionó 67 veces y Moodle 46, las plataformas educativas (EducaMadrid, EDIXGAL,
EducaAnd, Procomún) 43, eXeViewer 39 y las utilidades 31. Nada de eso vive en el
repositorio del programa, así que el cuaderno no podía responderlo.

Por eso se sincronizan también, cada uno con sus documentos elegidos en
`COMPLEMENTARIOS`, dentro de `scripts/exelearning.py`:

| Prefijo | Qué es | Para qué responde |
|---|---|---|
| `mod_exescorm-`, `mod_exeweb-` | Plugins de Moodle | Un aula virtual que rechaza un exportado de la 4.x casi siempre lleva el módulo antiguo |
| `wp-exelearning-` | Plugin de WordPress | Publicar y editar REA desde WordPress |
| `exeviewer-` | eXeViewer | Compartir sin aula virtual; se instala como aplicación y funciona sin conexión |
| `visor-webzip-` | Visor Web-ZIP | Lo mismo, con fechas de apertura y cierre |
| `edex-` | Editor de estilos EdEX | Estilos propios, y convertir los de la 2.x |
| `execonvert-` | eXeConvert | Convertir entre `.elp`, `.elpx`, `.docx`, `.md` y `.pdf` |
| `hackexe4-` | HackeXe4 | Ampliar los iDevices pegando HTML, CSS o JS |

Las rutas están en `repos_complementarios`, en `config.json`; el que no esté
configurado o no esté en el disco se salta con un aviso, sin romper la pasada.
De estos repositorios **no se busca documentación nueva**: serían decenas de
archivos y casi todos de desarrollo. Solo se comprueba que lo elegido siga
existiendo.

Antes de cada pasada se hace `git pull` de todos, pero **solo si no tienen
trabajo sin guardar**: varios son de Juanjo y puede estar editándolos.

## Uso

```bash
python3 scripts/exelearning.py              # sincroniza con el repositorio
python3 scripts/exelearning.py --sin-subir  # ver qué cambiaría, sin tocar nada
python3 scripts/exelearning.py --manual     # además, rehace el manual desde la web
```

Hace `git pull` del repositorio de eXeLearning antes de empezar, así que no hace
falta actualizarlo a mano. La ruta está en `config.json`, en `repo_exelearning`.

## Cómo decide qué hacer con cada documento

- **Falta en el cuaderno** → lo añade.
- **Está y ha cambiado** (huella distinta a la de lo último subido) → lo
  sustituye, con el mismo orden seguro de siempre: subir primero, borrar después.
- **Está y no ha cambiado** → no lo toca.
- **Está, lo gestiona este script y ya no está en el repositorio** → lo retira.

El material subido a mano —los requisitos de calidad de las SdA y la hoja de
HackeXe— no lo gestiona el script: se queda como esté. Eso no significa que nadie
lo mire. La revisión periódica comprueba, para cada uno, que siga en el cuaderno y
que su original no se haya reeditado, y lo dice en su informe: la tabla está en
`MATERIAL_EXTERNO`, dentro de `scripts/revisar-exelearning.py`.

De los recursos hechos con eXeLearning se vigila el `content.xml`, que cambia
cuando se reedita el material y no cuando el sitio se retoca por fuera. De una
entrada de blog o de un wiki solo se comprueba que siga en pie, porque su HTML
cambia solo y compararlo daría un aviso por semana.

Esta comprobación existe porque faltaba: `guia_rea_exe.pdf` era la guía de 2019,
escrita para eXeLearning 2.9, y estuvo siete años en el cuaderno sin que nada lo
señalara. Se descubrió preguntándole a Karla de qué año era su propia fuente.

## Los documentos escritos a mano

En `fuentes/` van los documentos que no salen de ningún repositorio porque nadie
los ha escrito: los redacta quien mantiene el cuaderno. Todo `.md` que haya ahí
se sube con su propio nombre.

Están **versionados**, y no en `material/`, precisamente porque no se generan de
nada: si se perdieran no habría forma de rehacerlos, y así además queda su
historia y se pueden revisar los cambios en un diff.

Hoy hay uno, `exelearning-en-cada-plataforma.md`, y responde a la laguna más
grande que tenía el cuaderno: **buena parte de lo que se pregunta no es sobre
eXeLearning sino sobre la plataforma donde se publica**. Entre noviembre de 2025
y septiembre de 2026, Moodle se mencionó 97 veces (33 de ellas en preguntas),
Procomún 24, EducaMadrid 20 y la Junta de Andalucía 20.

La documentación de esas plataformas no se puede sincronizar: MoodleDocs devuelve
un «Moodle challenge» a cualquier petición que no venga de un navegador, y volcar
la documentación de cinco plataformas dispersaría la recuperación en vez de
mejorarla. Así que el documento es una **síntesis**: reúne lo que en las
conversaciones está disperso —una respuesta del equipo de eXeLearning en un
mensaje suelto de junio— y lo fecha.

Dos reglas al escribir ahí:

1. **Cada afirmación dice de dónde sale**, con autor y fecha, y distingue al
   equipo de eXeLearning de un usuario que cuenta su experiencia. Sin eso, dentro
   de un año nadie sabrá si algo era un dato o una conjetura.
2. **Lo que quedó rectificado se escribe rectificado.** En el hilo del 19 de
   agosto de 2026 se dijo primero que SCORM no lleva botones de navegación y
   luego se demostró que Moodle sí los muestra. Vale lo segundo, y el documento
   lo dice, porque el cuaderno tiene las dos versiones en las conversaciones.

## La revisión: ¿ha aparecido documentación nueva?

La sincronización mantiene al día los documentos de una lista fija. Lo que no
puede hacer sola es darse cuenta de que **la lista se ha quedado corta**. Eso es
exactamente lo que pasó entre mayo y septiembre de 2026: apareció en el
repositorio todo el subárbol `doc/elpx-format/` —37.500 palabras sobre el formato
de archivo, con el catálogo de iDevices dentro— y el cuaderno siguió
sincronizando tan tranquilo la lista de mayo.

Por eso hay dos comprobaciones distintas, las dos diarias, que no se cubren la
una a la otra:

- **Sincronizar** compara las huellas de una lista fija de rutas. Nunca mira
  fuera de la lista, así que jamás vería aparecer una carpeta nueva.
- **Revisar** recorre los `.md` del repositorio y los cruza contra `INCLUIR` y
  `EXCLUIR`. No mira contenidos: solo busca lo que no está en ninguna lista.

Y la revisión solo encuentra donde mira. `FUERA`, en
`scripts/revisar-exelearning.py`, dejaba fuera la carpeta `public/` entera por
ser código y recursos, y con ella quedó invisible `public/CHANGELOG.md`: el
registro de qué trae cada versión, que es exactamente lo que se pregunta cada vez
que sale una («acabo de instalar la 4.0.3, ¿qué mejoras trae?», 6 de agosto de
2026). El informe decía «la lista está completa» y era verdad dentro de su
alcance. Desde septiembre de 2026 `FUERA` son **prefijos de ruta** en vez de
carpetas de primer nivel, así que de `public/` solo se descartan las librerías
empaquetadas (`public/app/`, `public/libs/`) y lo demás se ve.

`scripts/revisar-exelearning.py` no cambia nada y deja un informe en
`registro/revision-exelearning-YYYY-MM.md` con:

- La documentación del repositorio que no cubre ni `INCLUIR` ni `EXCLUIR`, para
  decidir una por una.
- Las entradas de `INCLUIR` que ya no encuentran archivo (renombrados, borrados).
- Si la portada del manual de usuario ha cambiado.
- El recuento de fuentes del cuaderno, para vigilar el límite de 300.

Y a continuación se decide solo. Clasificar un documento exige leerlo —la ruta y
el nombre no bastan: `doc/development/profiling.md` parece documentación del
programa y resulta ser instrumentación de desarrollo; `doc/conventions.md` parece
normas internas y resulta documentar comportamientos intencionados—, así que ese
juicio se le pide a un Claude sin sesión interactiva
(`scripts/decidir-exelearning.py`), se valida lo que responde y se escribe en
`INCLUIR` o `EXCLUIR`.

Lo mecánico va con ello: las entradas que apuntan a archivos borrados se retiran
solas, y si hay manual nuevo se reconstruye.

### Cómo saber si ha actuado

Cada decisión deja tres rastros:

1. **La bitácora** [`docs/decisiones-automaticas.md`](decisiones-automaticas.md),
   versionada: qué documento, qué se decidió y por qué. Si está vacía o no
   existe, es que nunca ha hecho falta actuar.
2. **Un commit** con las decisiones y su motivo, que además la hace reversible.
3. **Un aviso en pantalla** con el recuento.

```bash
python3 scripts/decidir-exelearning.py --historial   # ¿ha actuado alguna vez?
python3 scripts/decidir-exelearning.py --probar      # qué decidiría, sin tocar nada
```

### Qué sigue sin decidir sola

Cambiar el propósito del cuaderno, tocar las fuentes que Juanjo puso a mano (los
PDF pedagógicos, la hoja de HackeXe) y cambiar la dirección del manual oficial si
CEDEC publica una carpeta nueva. Eso se avisa, no se hace.

## El manual de usuario

`scripts/manual_exelearning.py` recorre las 83 páginas del manual oficial y las
junta en un único Markdown de unas 49.000 palabras, con la jerarquía de títulos
recompuesta —cada página vuelve a empezar en `#`, y sin recolocarlas NotebookLM
trocea mal— y los enlaces e imágenes absolutizados.

Se rehace solo cuando sale un manual nuevo, no a diario:

```bash
python3 scripts/manual_exelearning.py
```

Si algún día cambia la dirección del manual, está en `RAIZ`, dentro de ese
script. Queda en `material/exelearning/`, que no se versiona.

## Por qué Markdown y no `.docx` ni PDF

La primera versión del cuaderno se llenó convirtiendo los documentos a `.docx`.
NotebookLM acepta Markdown directamente, que es lo que son en origen: convertir
degrada las tablas y los bloques de código, y precisamente el catálogo de
iDevices es una tabla enorme. Del manual, un PDF solo añadiría las capturas de
pantalla, que en un cuaderno de texto no aportan, a cambio de artefactos de
maquetación.
