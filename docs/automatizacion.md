# Cómo funciona la actualización diaria

## Qué ocurre cada día

1. **A las 7:00** (o en cuanto el ordenador se enciende, si estaba apagado) cron
   lanza `scripts/diario.sh`, que espera a que haya red y sesión gráfica y llama
   a `scripts/actualizar.py`.
2. Para cada uno de los tres grupos:
   - Se calcula lo pendiente: desde el día siguiente al último procesado
     —`estado.json`— **hasta ayer**. El día en curso no entra nunca: aún no ha
     terminado y se subiría a medias.
   - Se **reexporta el mes natural completo** de Telegram a
     `datos/<grupo>-YYYY-MM.json`. Cuesta unos segundos más que exportar solo el
     día pendiente y a cambio el proceso se cura solo: da igual que una pasada
     se quedara a medias o que el ordenador llevara una semana apagado.
   - Se regenera `salida/<grupo>/conversacion-YYYY-MM.md`.
   - Si el Markdown resultante **no coincide** con el que se subió la última vez,
     se sustituye la fuente en NotebookLM.
3. Se rehace `salida/INDICE.md` y se avisa en pantalla del resultado.

Una pasada normal tarda entre uno y dos minutos.

## Por qué se sustituye la fuente en vez de editarla

Una fuente de NotebookLM no se puede modificar: para reflejar el día nuevo hay
que subir el archivo otra vez y retirar el anterior. El orden es siempre el
mismo y no es casual:

1. Subir la versión nueva.
2. Esperar a que NotebookLM termine de indexarla.
3. Solo entonces, borrar la anterior.

Así, un fallo a mitad deja el mes **duplicado** un rato —molesto pero
inofensivo, la siguiente pasada lo arregla— en vez de dejar al notebook **sin**
ese mes, que sí sería una pérdida. Si el indexado no termina a tiempo, no se
anota la huella y el mes se reintenta en la pasada siguiente.

## Por qué el día 1 de cada mes no pasa nada especial

El mes nuevo se crea como fuente nueva y el anterior queda cerrado, sin volver a
tocarse. Ese día se suben los dos: el último día del mes que termina y el primero
del que empieza.

## Los dos disparos de cron

```cron
@reboot          .../scripts/diario.sh --auto
*/15 7-23 * * *  .../scripts/diario.sh --auto
```

- El de **`@reboot`** cubre el caso de encender el ordenador con el día pendiente.
- El de **cada cuarto de hora** cubre que ya estuviera encendido, y también que
  al encender no hubiera red todavía.

Ninguno de los dos duplica trabajo: en cuanto una pasada termina bien se deja la
marca `registro/.hecho-<fecha>` y el resto de disparos del día no hacen nada.
Si la pasada **falla**, la marca no se pone y el siguiente disparo reintenta: un
corte de red pasajero se arregla solo. Además hay un cerrojo (`flock`) para el
momento en que coinciden el disparo de arranque y el del cuarto de hora.

## Los avisos en pantalla

- El progreso va en **una sola notificación que se reescribe** en su sitio, nunca
  una pila de avisos.
- Al terminar, un aviso breve que se desvanece solo.
- Si algo falla, un **cartel fijo con sonido** que se queda hasta que se lea: el
  proceso corre a las siete de la mañana y puede no haber nadie delante.

Se pueden probar sueltos:

```bash
scripts/avisar.sh paso "probando"
scripts/avisar.sh error "Título" "Mensaje"
scripts/avisar.sh retirar
```

## `estado.json`

Guarda, por grupo, la última fecha procesada y, por mes, la huella del Markdown
que está subido y el identificador de su fuente:

```json
{
  "grupos": {
    "chatgptedu": {
      "ultimo_dia": "2026-09-01",
      "meses": { "2026-09": { "huella": "3f2a…", "fuente": "a1b2…" } }
    }
  }
}
```

La huella es lo que evita resubir un mes cuando el grupo no ha tenido mensajes.
Se compara con lo **último subido**, no con la versión anterior del fichero: si
el `.md` se regeneró sin llegar a subirse, el notebook sigue desactualizado y
hay que subirlo igualmente.

Borrar `estado.json` no rompe nada: la siguiente pasada rehace el último mes
completo y lo vuelve a subir.

## Qué crece y qué se poda

El archivo de conversaciones crece por definición: es la memoria de los grupos.
Son unos **4 MB al año** entre los tres, y no se toca nada de eso. Lo demás está
acotado, y de ello se encarga `scripts/podar.py` al final de cada pasada:

| Qué | Cuánto se guarda |
|---|---|
| `salida/*.md` | **Todo, para siempre.** Es el producto |
| `datos/*.json` | Los 3 últimos meses en claro; los anteriores, comprimidos (ocupan la décima parte) |
| `estado.json` | Los 3 últimos meses por grupo |
| `registro/diario-*.log` | 60 días |
| `registro/.hecho-*` | 7 días |
| `registro/disparos.log` | Las últimas 200 líneas |
| `registro/exelearning-sync.log` | Se reescribe en cada pasada |
| El repositorio git | Solo código: no crece con los datos |

Las exportaciones antiguas se comprimen en vez de borrarse porque son la única
copia congelada de lo que Telegram tenía ese día, y se siguen leyendo sin
descomprimir nada a mano: regenerar un mes comprimido funciona igual. Si se
reexporta un mes que estaba comprimido, la versión nueva sustituye a la vieja.

En NotebookLM se añaden 3 fuentes al mes, una por grupo. Con el plan Pro —300
fuentes por notebook— hay margen para unos veinte años.

También se puede podar suelto:

```bash
python3 scripts/podar.py
```

## De qué depende esto

Todo el trato con NotebookLM pasa por el CLI `notebooklm`, del paquete
[`notebooklm-py`](https://github.com/teng-lin/notebooklm-py) (Teng Lin, MIT). Es
una herramienta **no oficial**: automatiza NotebookLM reutilizando las cookies de
la sesión de Google, así que un cambio en NotebookLM puede romperla cualquier
día. Si eso pasa, saldrá como cartel en pantalla y quedará en `registro/`.

Publica una versión estable cada pocas semanas. **La pasada diaria la instala
sola**, pero nunca a ciegas: después comprueba que el CLI sigue hablando con
NotebookLM y que las dos pasadas en seco terminan bien. Si la versión nueva rompe
algo, vuelve sola a la anterior —perder una versión no cuesta nada; perder días
de archivo, sí— y lo cuenta por Telegram. Si ni volviendo atrás se arregla, ya no
es cosa de versiones y llama a la reparación automática.

Para hacerlo a mano, o solo mirar:

```bash
python3 scripts/actualizar-cli.py             # actualizar y comprobar
python3 scripts/actualizar-cli.py --solo-ver  # solo decir si hay novedad
```

Si algo falla, se vuelve atrás con `uv tool install notebooklm-py==<versión>`.

## Cuando algo se rompe, se busca la solución

Un fallo a las siete de la mañana no tiene a nadie delante, y dejarlo esperando a
que alguien lea un cartel cuesta días de archivo. Así que la pasada diaria, si
falla, le da el problema a un Claude sin sesión interactiva junto con el registro
del fallo, la versión instalada del CLI, las notas de la última publicación y las
incidencias abiertas del proyecto. Si lo arregla, se reintenta la pasada.

Lo que puede hacer está acotado a propósito: leer, ejecutar las comprobaciones en
seco y editar **cinco archivos concretos** (`notebook.py`, `generar.py`,
`exelearning.py`, `podar.py`, `revisar-exelearning.py`). **No puede borrar fuentes
de NotebookLM —el único daño irreversible de este sistema—, ni tocar `datos/`,
`salida/` o `material/`, ni subir nada a GitHub.**

### Por qué esa lista tan corta

Al encargo se le adjuntan las notas de publicación y los títulos de las
incidencias abiertas del repositorio del CLI, porque son buenas pistas: si algo
se ha roto para nosotros, probablemente alguien lo haya contado allí. Pero **ese
tablón de GitHub lo escribe cualquiera**, y para un modelo todo el encargo es un
solo texto: no hay una frontera dura entre las órdenes y el material adjunto. Una
nota redactada a propósito podría intentar pasar por instrucción.

Se hacen dos cosas al respecto. La primera, marcarlo: el material ajeno va
etiquetado como tal y el encargo dice explícitamente que son pistas y nunca
órdenes, y que si algo ahí parece una instrucción hay que ignorarlo y contarlo.

La segunda es la que de verdad protege, porque no depende de que el modelo se
porte bien: **después de cada reparación se comparan los archivos tocados con la
lista de permitidos, y cualquier cambio fuera de ella se deshace** —revertido si
git lo seguía, borrado si era nuevo— y salta un aviso. Fuera de esa lista está
todo lo que toca la cuenta de Telegram de Juanjo y las credenciales, que es donde
un cambio malicioso haría daño de verdad: escribir en su nombre a tres grupos con
cientos de personas.

Y su palabra no basta: quien decide si está arreglado es
`comprobaciones_pasan()`, que vuelve a ejecutar las dos pasadas en seco. Si la IA
dice que lo ha resuelto y las comprobaciones fallan, el aviso que sale es el de
«no he podido arreglarlo».

Cada reparación queda en [`docs/reparaciones.md`](reparaciones.md), versionado, y
se cuenta por Telegram. Si ese archivo está vacío, es que nunca se ha roto nada.

## Cómo te enteras de lo que pasa

| Canal | Para qué |
|---|---|
| Notificación en pantalla | El progreso de la pasada, si estás delante |
| Cartel fijo con sonido | Un fallo que nadie ha podido arreglar |
| **Telegram, desde el bot @claude_ia_jjdeharo_bot** | Lo que hay que contar aunque no estés: actualizaciones, reparaciones, documentación clasificada sola |
| `registro/avisos.log` | Todo lo enviado, por si Telegram falla |
| `docs/reparaciones.md` y `docs/decisiones-automaticas.md` | El detalle, versionado |

### Por qué un bot y no «Mensajes guardados»

Telegram **no notifica los mensajes que uno se escribe a sí mismo**. Los primeros
avisos iban a «Mensajes guardados» y ahí se quedaban, mudos: llegaban, pero nadie
se enteraba. Un mensaje de un bot sí suena en el móvil.

El bot **no es de este proyecto**: es «Claude IA», el canal por el que Claude le
escribe a Juanjo desde cualquier sesión, y por eso sus credenciales viven fuera,
en `~/.claude/telegram-claude-ia.json` (permisos 600). La skill `avisar-juanjo`
documenta su uso general; aquí solo se usa.

Si algún día hay que rehacerlo o montarlo en otro ordenador:

```bash
python3 ~/.claude/scripts/crear-bot-claude.py
```

Si faltara, los avisos caen a «Mensajes guardados»: no notifican, pero no se
pierden. Y pase lo que pase quedan en `registro/avisos.log`.

## Cuando algo va mal

Lo primero, el registro del día: `registro/diario-<fecha>.log`. Y `disparos.log`
dice si cron llegó a dispararse.

| Síntoma | Qué pasa | Solución |
|---|---|---|
| `la sesión de NotebookLM ha caducado` | Las cookies dejan de valer cada cierto tiempo | `notebooklm login` |
| `La sesión de Telegram no está autorizada` | Sesión revocada o caducada | Borrar `sesion/telegram.session` y ejecutar `actualizar.py` a mano para meter el código |
| El mes aparece duplicado en el notebook | Una subida se quedó a medias | Se arregla sola en la siguiente pasada |
| Un grupo falla y los otros no | Es el comportamiento previsto | Se avisa al final; el resto se procesa igual |
| Nada se ejecuta por la mañana | Cron no está instalado | `crontab -l` y, si falta, `scripts/instalar.sh` |

Para rehacer un tramo concreto:

```bash
python3 scripts/actualizar.py --desde 2026-08-01 --solo exelearning
```
