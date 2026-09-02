# El cuaderno de eXeLearning

El cuaderno **Karla - Experta en eXeLearning** responde a usuarios de
eXeLearning, pero con criterio de programador: además del manual de usuario
lleva la documentación técnica del proyecto, para poder explicar *por qué* el
programa se comporta como lo hace y no solo *qué* botón pulsar.

Tiene tres clases de fuentes:

1. **Las conversaciones del grupo de Telegram**, que se actualizan solas cada
   día como las de los otros dos grupos.
2. **El manual de usuario**, consolidado del sitio oficial de CEDEC/INTEF.
3. **La documentación técnica del repositorio**, sincronizada desde
   `github.com/exelearning/exelearning`.

Los dos últimos los mantiene `scripts/exelearning.py`.

## Qué documentación entra y cuál no

El criterio es una sola pregunta: **¿ayuda a explicar el programa o su formato de
archivo?**

**Entra**: el formato `.elpx` al completo —incluido el catálogo de iDevices, que
es la referencia autorizada de qué hace cada uno y cómo guarda su estado—, la
arquitectura, las decisiones de arquitectura (ADR), las convenciones, la
instalación y el despliegue, la API REST, la autenticación, el tiempo real, la
personalización y estilos, el contrato del runtime SCORM 1.2, los problemas
conocidos y la guía de actualización de la 3.x a la 4.x.

**No entra** lo que solo explica cómo se colabora en el repositorio: cómo abrir
un pull request, la estrategia de ramas, cómo ejecutar las pruebas, el entorno
de desarrollo o las herramientas de *profiling*. No pueden responder a nadie y
compiten con lo útil a la hora de recuperar fragmentos.

Tampoco entran `AGENTS.md` ni `CLAUDE.md`: son **instrucciones dirigidas a una
IA que trabaja sobre el código**, y en un cuaderno de soporte pueden filtrarse en
las respuestas y acabar diciéndole a un profesor que siga las convenciones de
commits del proyecto.

La lista concreta está en `INCLUIR`, dentro de `scripts/exelearning.py`.

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

Los PDF pedagógicos (`guia_rea_exe.pdf`, requisitos de calidad de las SdA) y la
hoja de HackeXe no los gestiona el script: se quedan como estén.

## La revisión mensual

La sincronización mantiene al día los documentos de una lista fija. Lo que no
puede hacer sola es darse cuenta de que **la lista se ha quedado corta**. Eso es
exactamente lo que pasó entre mayo y septiembre de 2026: apareció en el
repositorio todo el subárbol `doc/elpx-format/` —37.500 palabras sobre el formato
de archivo, con el catálogo de iDevices dentro— y el cuaderno siguió
sincronizando tan tranquilo la lista de mayo.

Por eso hay dos capas. `scripts/revisar-exelearning.py` corre una vez al mes
dentro de la pasada diaria, no cambia nada y deja un informe en
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
