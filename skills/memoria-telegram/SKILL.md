---
name: memoria-telegram
description: Mantiene al día las conversaciones de los grupos de Telegram de Juanjo (ChatGPT-IA-edu, eXeLearning, Vibe Coding Educativo) y sus notebooks de NotebookLM. Usar cuando se pida actualizar, exportar o revisar esas conversaciones, cuando falle la actualización diaria automática, o cuando haya que rehacer un mes o arreglar una fuente de NotebookLM.
---

# Memoria de Telegram

Tres grupos públicos de Telegram se archivan como Markdown mensual y ese
Markdown es la fuente de un notebook de NotebookLM por grupo. **El proceso ya
está automatizado y corre solo cada mañana**: normalmente no hay nada que hacer.

**Dónde corre**: desde el 08/09/2026, en el NAS —`ssh jjdeharo@192.168.1.113`,
contenedor `memoria-telegram`, repositorio en
`/volume1/docker/memoria-telegram/repo`—, no en el portátil. Ahí es donde hay
que mirar los registros y ejecutar las órdenes de esta skill. El clon del
portátil (`~/Documentos/github/automatizaciones/memoria-telegram`) sigue siendo
donde se desarrolla, pero **no archiva nada**: su cron se retiró. Cómo se opera
el contenedor está en `docs/nas.md`.

Todas las órdenes de abajo se lanzan dentro del contenedor:

```bash
ssh jjdeharo@192.168.1.113
docker exec -it memoria-telegram bash    # y ya estás en /proyecto
```

| Grupo | Telegram | Carpeta | Notebook |
|---|---|---|---|
| ChatGPT-IA-edu | `@ChatGPTedu` | `salida/chatgpt-ia-edu/` | AGENTE de ChatGPT-IA-edu |
| eXeLearning | `@exelearning` | `salida/exelearning/` | Karla - Experta en eXeLearning |
| Vibe Coding Educativo | `@vceduca` | `salida/vibe-coding-educativo/` | Agente Vibe Coding Educativo |

Los identificadores de notebook y las credenciales están en `config.json`, que
no se versiona. Léelo de ahí; no los pidas ni los inventes.

## Lo primero: comprobar si hay algo que hacer

```bash
ssh jjdeharo@192.168.1.113
cd /volume1/docker/memoria-telegram/repo          # el registro se lee sin entrar
cat registro/diario-$(date +%F).log 2>/dev/null   # ¿corrió hoy?, ¿cómo acabó?
tail -5 registro/disparos.log                     # ¿llegó a dispararse el bucle?
docker ps --filter name=memoria-telegram          # ¿está el contenedor en pie?
python3 -c "import json;print(json.load(open('estado.json'))['actualizado'])"
```

Un registro que acaba en `=== terminado: N subida(s) ===` es una pasada
correcta. Si el día está al día, **no ejecutes nada más**: dilo y para.

## Poner al día a mano

```bash
python3 scripts/actualizar.py                     # lo pendiente hasta ayer
python3 scripts/actualizar.py --solo vceduca      # un solo grupo
python3 scripts/actualizar.py --desde 2026-08-01  # rehacer desde una fecha
python3 scripts/actualizar.py --sin-subir         # generar sin tocar NotebookLM
```

Es idempotente: repetirlo no duplica nada. Tarda uno o dos minutos. Nunca
procesa el día en curso, solo días terminados.

## El cuaderno de eXeLearning lleva algo más

Ese cuaderno no solo tiene conversaciones: lleva el manual de usuario y la
documentación técnica del repositorio de eXeLearning, para poder responder con
criterio de programador. Lo mantiene `scripts/exelearning.py`, que hace `git
pull` del repositorio y sincroniza (añade lo nuevo, sustituye lo cambiado,
retira lo que desapareció). Corre solo, después de las conversaciones.

```bash
python3 scripts/exelearning.py --sin-subir   # ver qué cambiaría
python3 scripts/exelearning.py               # sincronizar
python3 scripts/manual_exelearning.py        # rehacer el manual (solo si sale uno nuevo)
```

Qué entra y qué no está decidido y explicado en `docs/cuaderno-exelearning.md`;
la lista concreta, en `INCLUIR` dentro del script. **No metas `AGENTS.md` ni
`CLAUDE.md` del repositorio de eXeLearning**: son instrucciones para una IA que
toca ese código y se filtran en las respuestas al usuario.

## Esto se repara solo, y avisa por Telegram

Si una pasada falla, `scripts/reparar.py` le da el problema a un Claude sin
sesión interactiva —con el registro, la versión del CLI, las notas de la última
publicación y las incidencias del proyecto—, que puede leer, ejecutar las
comprobaciones en seco y editar cinco archivos concretos, y nada más. Después,
un cerrojo compara qué archivos se tocaron y deshace lo que esté fuera de esa
lista: el encargo incluye texto escrito por desconocidos en GitHub, y ahí es
donde muere cualquier instrucción que alguien intentara colar.

**Si amplías `EDITABLES` en `scripts/reparar.py`, piensa antes qué toca ese
archivo.** Todo lo que use la sesión de Telegram o las credenciales se queda
fuera: el peor caso no es que se rompa el archivo, es que algo escriba en nombre
de Juanjo a tres grupos con cientos de personas. Después se comprueba de verdad
si quedó arreglado, y se cuenta por Telegram.

Antes de ponerte a diagnosticar tú un fallo, mira si ya se intentó:

```bash
cat docs/reparaciones.md          # qué se rompió y qué se hizo
tail -20 registro/avisos.log      # qué se le ha contado a Juanjo
```

## Reglas que no debes romper

1. **Nunca versiones datos.** El repositorio es **público** y las conversaciones
   llevan nombre y apellidos de cientos de personas. `salida/`, `datos/`,
   `sesion/`, `registro/`, `estado.json` y `config.json` están en `.gitignore` y
   ahí se quedan. Antes de cualquier `git add`, comprueba `git status --short`.
2. **Al sustituir una fuente en NotebookLM: primero subir la nueva, esperar a que
   quede indexada, y solo entonces borrar la vieja.** Nunca al revés. Un fallo a
   mitad debe dejar un duplicado, nunca un notebook sin ese mes. Ya lo hace
   `scripts/notebook.py`: úsalo en vez de llamar al CLI por tu cuenta.
3. **No toques el formato del Markdown** (`scripts/procesar_telegram.py`). Los
   meses ya subidos siguen ese formato; cualquier cambio, hasta un espacio, haría
   que todos se dieran por modificados y se resubieran enteros.
4. **No cambies la periodicidad ni el troceado** sin que Juanjo lo pida. Se
   decidió a conciencia: un archivo por mes, sustituido a diario. Trocear por
   días fragmenta la recuperación del agente y no ahorra borrados.

## Cuando algo falla

Mira siempre primero `registro/diario-<fecha>.log`.

| Síntoma | Solución |
|---|---|
| `la sesión de NotebookLM ha caducado` | En el NAS no hay navegador: se hace `notebooklm login` en el portátil de Juanjo y se copia de nuevo `~/.notebooklm/` a `/volume1/docker/memoria-telegram/home/`. Ver `docs/nas.md` |
| Nada funciona con NotebookLM y la sesión es válida | El CLI es una herramienta no oficial y se rompe cuando Google cambia algo. `python3 scripts/actualizar-cli.py` instala la versión nueva y comprueba; si rompe, vuelve sola atrás |
| `La sesión de Telegram no está autorizada` | Borrar `sesion/telegram.session` y ejecutar `actualizar.py` a mano: pedirá el código por Telegram |
| Un mes duplicado en el notebook | Se arregla solo en la siguiente pasada; si urge, borra la fuente más antigua de ese título |
| Un grupo falla y los otros no | Es lo previsto. Reintenta ese grupo con `--solo <prefijo>` |
| Nada se ejecuta por la mañana | El disparo ya no es cron sino el bucle del contenedor: `docker ps --filter name=memoria-telegram` y, si no está, `cd /volume1/docker/memoria-telegram && docker compose up -d` |
| El notebook no tiene un mes que sí está en `salida/` | Borra su entrada en `estado.json` y ejecuta `--desde` del día 1 de ese mes |

## Cómo está montado

- `scripts/actualizar.py` es el orquestador y el punto de entrada. Por grupo:
  calcula lo pendiente desde `estado.json` hasta ayer, reexporta **el mes natural
  entero** (así se cura solo tras huecos o apagones), regenera el `.md` y, si su
  huella difiere de la de lo último subido, sustituye la fuente del notebook.
- `scripts/diario.sh` es la pasada. En el NAS la dispara `nas/bucle.sh` cada 15
  minutos de 4 a 23 —y el arranque del contenedor hace de `@reboot`—, con marca
  de día hecho y cerrojo, esperando a que haya red. Si una pasada falla, no deja
  marca y el siguiente disparo reintenta. En el portátil lo lanzaba cron, y
  `scripts/instalar.sh` sigue ahí por si hubiera que volver.
- `scripts/podar.py` corre al final de cada pasada: comprime las exportaciones
  JSON de más de tres meses y recorta `estado.json`. **No es pérdida de datos**:
  las conversaciones de `salida/` se guardan enteras y para siempre, y un mes
  comprimido se regenera igual. Los registros se limpian solos (60 días).
- `scripts/avisar.sh` da los avisos: el progreso reescribe una única
  notificación; solo el fallo deja cartel fijo.

Detalle completo en `docs/automatizacion.md`; el formato del Markdown, en
`docs/formato-markdown.md`. Si vas a modificar el automatismo, léelos antes.
