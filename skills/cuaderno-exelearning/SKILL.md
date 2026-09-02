---
name: cuaderno-exelearning
description: Mantiene la documentación técnica y el manual del cuaderno de NotebookLM de eXeLearning (Karla). Usar para comprobar lo que el automatismo decidió solo, cuando aparezca documentación nueva en el repositorio de eXeLearning, cuando salga un manual de usuario nuevo, o cuando se pida revisar, actualizar o decidir qué fuentes lleva ese cuaderno.
---

# El cuaderno de eXeLearning

El cuaderno **Karla - Experta en eXeLearning** responde a usuarios de
eXeLearning con criterio de programador: lleva el manual de usuario, la
documentación técnica del proyecto y las conversaciones del grupo de Telegram.

Repositorio del automatismo: `~/Documentos/github/automatizaciones/memoria-telegram`
Repositorio de eXeLearning: la ruta está en `config.json`, en `repo_exelearning`.

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
| Rehacer el manual de usuario | `scripts/manual_exelearning.py` | Cuando salga uno nuevo |

Esto no es una separación caprichosa. Entre mayo y septiembre de 2026 apareció
en el repositorio todo el subárbol `doc/elpx-format/` —37.500 palabras sobre el
formato de archivo, incluido el catálogo de iDevices— y el cuaderno no se enteró,
porque un script con una lista fija sincroniza lo que le dijeron y nada más.

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

## Reglas que no debes romper

1. **Subir siempre Markdown, nunca `.docx` ni PDF convertido.** La primera
   versión del cuaderno se llenó de `.docx` y se perdieron las tablas: el
   catálogo de iDevices es una tabla enorme. NotebookLM acepta Markdown, que es
   lo que los documentos son en origen.
2. **Al sustituir una fuente: subir la nueva, esperar a que se indexe, borrar la
   vieja.** Nunca al revés. Ya lo hace `scripts/notebook.py`; úsalo.
3. **No toques lo que el script no gestiona**: los PDF pedagógicos
   (`guia_rea_exe.pdf`, requisitos de calidad de las SdA) y la hoja de HackeXe
   los puso Juanjo a mano y se quedan.
4. **Las conversaciones del grupo son otra cosa**: las lleva la skill
   `memoria-telegram`. No las toques desde aquí.

## Detalle completo

`docs/cuaderno-exelearning.md`, en el mismo repositorio: qué entra y por qué,
cómo se decide cada documento, y cómo está hecho el manual consolidado.
