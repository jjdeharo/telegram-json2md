---
name: cuaderno-exelearning
description: Mantiene la documentación técnica y el manual del cuaderno de NotebookLM de eXeLearning (Karla). Usar para comprobar lo que el automatismo decidió solo, cuando aparezca documentación nueva en el repositorio de eXeLearning, cuando salga un manual de usuario nuevo, o cuando se pida revisar, actualizar o decidir qué fuentes lleva ese cuaderno.
---

# El cuaderno de eXeLearning

El cuaderno **Karla - Experta en eXeLearning** responde a usuarios de
eXeLearning con criterio de programador: lleva el manual de usuario, la
documentación técnica del proyecto, la de las herramientas que lo rodean
—plugins de Moodle y WordPress, visores, utilidades— y las conversaciones del
grupo de Telegram.

Repositorio del automatismo: `~/Documentos/github/automatizaciones/memoria-telegram`
Repositorio de eXeLearning: la ruta está en `config.json`, en `repo_exelearning`.
Los del ecosistema, en `repos_complementarios` del mismo archivo.

Las conversaciones y la sincronización de la documentación **corren solas cada
día**. Esta skill es para comprobar lo que se decidió solo, y para corregir el criterio
cuando algo se clasifique mal.

## El reparto: qué es automático y qué no

| | Quién | Cuándo |
|---|---|---|
| Sincronizar los documentos de la lista | `scripts/exelearning.py` | Cada día, solo |
| Detectar que la lista se ha quedado corta | `scripts/revisar-exelearning.py` | Cada día, solo |
| Decidir qué hacer con lo que aparece | `scripts/decidir-exelearning.py` (un Claude sin sesión) | Detrás de la revisión, solo |
| **Comprobar lo decidido y el criterio** | **Tú, con esta skill** | Cuando quieras, o si algo chirría |
| **Leer el grupo y ver qué falta** | **Tú, con esta skill** | Nadie más puede: ningún script lee las preguntas |
| Rehacer el manual de usuario | `scripts/manual_exelearning.py` | Cuando salga uno nuevo |

Esto no es una separación caprichosa. Entre mayo y septiembre de 2026 apareció
en el repositorio todo el subárbol `doc/elpx-format/` —37.500 palabras sobre el
formato de archivo, incluido el catálogo de iDevices— y el cuaderno no se enteró,
porque un script con una lista fija sincroniza lo que le dijeron y nada más.

Y hay un tercer hueco que ninguno de los dos cubre: **lo que el grupo pregunta y
no está en ningún repositorio que se mire**. Eso solo se ve leyendo las
conversaciones, y es lo que llevó en septiembre de 2026 a añadir el ecosistema.
Ver «Leer el grupo para saber qué falta», más abajo.

## Lo primero: ¿ha actuado alguna vez?

```bash
python3 scripts/decidir-exelearning.py --historial
```

La bitácora `docs/decisiones-automaticas.md` recoge cada documento clasificado
automáticamente y su motivo; cada tanda deja además un commit propio, así que
`git log --grep="Clasificar automáticamente"` cuenta la misma historia y permite
revertir una decisión que no te convenza.

**Si algo se clasificó mal, la corrección no es solo mover esa ruta de lista: es
arreglar el enunciado.** El criterio que se le pasa a la IA está en `CRITERIO`,
dentro de `scripts/decidir-exelearning.py`. Ya pasó una vez: una cláusula
demasiado amplia («son instrucciones dirigidas a una IA → excluir») descartó
`doc/elpx-format/ai-generation.md`, que son las diez reglas del formato sacadas
del código del generador y del importador. Se acotó la cláusula a las
instrucciones dirigidas a quien desarrolla el proyecto y volvió a entrar.

## La revisión, paso a paso

1. **Mira el informe**, que la pasada diaria ya habrá generado:

   ```bash
   cat registro/revision-exelearning-$(date +%Y-%m).md
   ```

   Si no existe, o quieres uno fresco: `python3 scripts/revisar-exelearning.py`
   (no cambia nada, solo mira).

   Normalmente ya estará resuelto: la pasada diaria decide sola y sincroniza.
   Estos pasos son para comprobarlo o para rehacerlo a mano.

2. **El criterio con el que se decide**, y con el que debes juzgar tú si repasas:

   > ¿Ayuda a explicar **el programa** o **su formato de archivo**?

   - **Sí** → a `INCLUIR`, en `scripts/exelearning.py`.
   - **No, solo explica cómo se colabora en el repositorio** (pull requests,
     ramas, pruebas, entorno de desarrollo, *profiling*) → a `EXCLUIR`.
   - **Son instrucciones para una IA que toca el código** (`AGENTS.md`,
     `CLAUDE.md`, `.agents/`, `.github/`) → a `EXCLUIR` **siempre**. En un
     cuaderno de soporte se filtran en las respuestas y acaban diciéndole a un
     profesor que siga las convenciones de commits del proyecto.
   - **Son muchos archivos cortos del mismo tema** (como las ADR) → a
     `CONSOLIDAR`, para que vayan en un solo documento: como fuentes sueltas se
     pisan entre ellas al recuperar.

   Lo que decidas, escríbelo en la lista. Que quede en el código es lo que evita
   volver a decidir lo mismo el mes que viene.

3. **Entradas huérfanas**: si el informe dice que una entrada de `INCLUIR` ya no
   existe, es que el archivo se renombró o se borró. Apunta a la ruta nueva o
   quita la entrada.

4. **Manual nuevo**: si el informe avisa de que la portada ha cambiado, o si en
   https://descargas.intef.es/cedec/exe_learning/Manuales/ hay una carpeta más
   reciente que la de `RAIZ` en `scripts/manual_exelearning.py`, actualiza esa
   dirección y rehaz el manual:

   ```bash
   python3 scripts/manual_exelearning.py
   ```

5. **Sincroniza y comprueba**:

   ```bash
   python3 scripts/exelearning.py --sin-subir   # qué va a pasar
   python3 scripts/exelearning.py               # hacerlo
   ```

   Después, que no queden duplicados ni fuentes a medio indexar:

   ```bash
   notebooklm source list -n <id del cuaderno> --json | python3 -c "
   import json,sys,collections
   s=json.load(sys.stdin)['sources']
   print(len(s),'fuentes')
   print('duplicados:',[t for t,c in collections.Counter(x['title'] for x in s).items() if c>1] or 'ninguno')
   print('no listas:',[x['title'] for x in s if x['status']!='ready'] or 'ninguna')"
   ```

6. **Commit** de los cambios en las listas, con el porqué de cada decisión.

## Leer el grupo para saber qué falta

La revisión automática compara repositorios contra listas. Nunca puede decirte
que **falta un repositorio entero**, porque no sabe que existe. Eso solo sale de
leer lo que la gente pregunta:

```bash
cd salida/exelearning
grep -inE "karla" conversacion-2026-0[4-9].md      # dónde falló Karla, textualmente
grep -h "?" conversacion-2026-0[4-5].md | sed 's/^> ↩︎ //' | sort -u  # las preguntas
```

Dos cosas que buscar, y en este orden:

1. **Las menciones a Karla.** La gente dice en el grupo cuándo no le ha servido:
   «una duda y Karla no ha sabido responderla», «le consulté a Karla pero me da
   otras opciones». Cada una apunta a una laguna concreta y comprobable: en
   septiembre de 2026 había cuatro y las cuatro se explicaban por una fuente que
   no estaba (los FX no se pueden anidar, y `anidad` sale 0 veces en el manual;
   la importación de preguntas desde `.txt`, y `.txt` sale 0 veces).
2. **De qué se habla, contado.** Un `grep -c` por temas sobre cinco meses dice
   más que la impresión de leerlos. Así se vio que el grupo no pregunta tanto
   *cómo se usa* eXeLearning como *cómo se saca el contenido de él*: SCORM 67,
   Moodle 46, plataformas educativas 43, eXeViewer 39, utilidades 31.

Antes de dar por buena una laguna, compruébala contra las fuentes que ya hay
(`grep -ci` en `material/exelearning/manual-exelearning-4.0.1.md` y compañía). La
mitad de las veces la respuesta sí está y el problema es otro.

**Una laguna que no se arregla con fuentes**: en junio de 2026 alguien preguntó
por los iconos del estilo Predeterminado y Karla le dio una ruta del árbol de
código a alguien que solo tiene el programa instalado. Es la misma contaminación
que se evita excluyendo `AGENTS.md`, pero por la vía de la documentación técnica
legítima. El índice del cuaderno lo advierte desde septiembre de 2026; si vuelve
a pasar, lo que hay que tocar son las instrucciones del cuaderno en NotebookLM,
a mano, no la lista de fuentes.

## Reglas que no debes romper

1. **Subir siempre Markdown, nunca `.docx` ni PDF convertido.** La primera
   versión del cuaderno se llenó de `.docx` y se perdieron las tablas: el
   catálogo de iDevices es una tabla enorme. NotebookLM acepta Markdown, que es
   lo que los documentos son en origen.
2. **Al sustituir una fuente: subir la nueva, esperar a que se indexe, borrar la
   vieja.** Nunca al revés. Ya lo hace `scripts/notebook.py`; úsalo.
3. **No toques lo que el script no gestiona**: los PDF pedagógicos
   (`guia_rea_exe.pdf`, requisitos de calidad de las SdA) y la hoja de HackeXe
   (`HackeXe4 - Hoja 1`) los puso Juanjo a mano y se quedan. El
   `hackexe4-README.md` es otra fuente distinta y esa sí la lleva el script.
4. **Las conversaciones del grupo son otra cosa**: las lleva la skill
   `memoria-telegram`. No las toques desde aquí.

## Detalle completo

`docs/cuaderno-exelearning.md`, en el mismo repositorio: qué entra y por qué,
cómo se decide cada documento, y cómo está hecho el manual consolidado.
