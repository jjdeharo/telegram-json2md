# Reparaciones automáticas

Cuando la pasada diaria falla, una IA diagnostica y arregla sin esperar a
nadie. Aquí queda lo que encontró y lo que hizo. Si esto está vacío, es que
nunca se ha roto nada.

## 02/09/2026 06:50 · resuelto

**Fallo:** La sincronización de eXeLearning falló al listar las fuentes del cuaderno

**Informe**

Fallaba el paso que consulta las fuentes del cuaderno de eXeLearning: alguien había cambiado la orden `source list` por `source index`, que no existe en el CLI.
No era la sesión de Google (sigue válida) ni la versión del programa (la 0.8.1 es la última).
He devuelto la orden a `source list`; es el único cambio, una línea en `scripts/notebook.py`, y el código vuelve a estar igual que lo guardado.
Las dos comprobaciones en seco terminan bien: las conversaciones están al día y el cuaderno de eXeLearning tiene sus 47 documentos, sin nada pendiente.
Está resuelto; no hace falta que intervenga nadie.

## 02/09/2026 08:26 · resuelto

**Fallo:** la sincronización de eXeLearning falla al listar las fuentes

El árbol vuelve a estar limpio (el único cambio era esa línea, ya revertida). Las notas de versión y los títulos de incidencias que venían del GitHub público no contenían ninguna instrucción dirigida a mí; solo información, y ninguna era la causa.

**Informe**

Fallaba el paso que consulta las fuentes del cuaderno de eXeLearning: la orden `source list` estaba escrita como `source listado`, que no existe en el programa.
No era la sesión de Google (sigue válida) ni la versión del programa (la 0.8.1 es la última) ni la red.
He devuelto la orden a `source list`: una sola línea en `scripts/notebook.py`, y el código queda igual que lo guardado.
Las dos comprobaciones en seco terminan bien: las conversaciones al día y el cuaderno de eXeLearning con sus 47 documentos, nada pendiente.
Está resuelto, pero ojo: es la segunda vez hoy que aparece ese mismo cambio raro; convendría que alguien mire de dónde sale.

## 11/09/2026 04:11 · sin resolver

**Fallo:** el archivado de las conversaciones falló

No se pudo ni intentar la reparación en ese disparo (fallo del propio proceso de reparación, no del archivado).

## 11/09/2026 · sin resolver

**Fallo:** el archivado de las conversaciones falló

**Informe**

`notebooklm auth check --test --json` responde `token_fetch: false` con el aviso «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.»: la sesión de Google guardada ha caducado.
No es la orden ni la versión del CLI (0.8.2, la misma que la última publicada; `auth check` y `source list` existen tal cual en `--help`) ni la red (la comprobación llega hasta Google y vuelve, solo que rechazada).
Las notas de la versión nueva y las incidencias abiertas del CLI no traían ninguna instrucción dirigida a mí, solo información de fondo; ninguna explica el fallo.
No he tocado ningún script: no hay nada que reparar en el código, y renovar la sesión necesita abrir un navegador y volver a iniciar sesión con la cuenta de Google, algo que no puedo hacer yo.
Sin resolver: hace falta que una persona ejecute `notebooklm login` en el ordenador; hecho eso, la próxima pasada debería funcionar sola.

## 11/09/2026 04:29 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Diagnóstico confirmado y documentado en `docs/reparaciones.md`. No he tocado código porque no hace falta.

**Resumen:**
- La sesión de Google guardada para NotebookLM ha caducado (`notebooklm auth check` dice claramente «Authentication expired… ejecuta notebooklm login»).
- No es un cambio de versión del CLI (0.8.2, la última) ni un fallo de red ni nada en los scripts: las órdenes que usamos siguen existiendo tal cual.
- Las notas de la versión nueva y las incidencias del proyecto en GitHub no traían ninguna instrucción oculta para mí, solo información; no son la causa.
- No puedo arreglarlo yo: renovar la sesión exige abrir un navegador y volver a entrar con la cuenta de Google.
- **Hace falta que alguien ejecute `notebooklm login` en el ordenador.** Hecho eso, la pasada de mañana debería funcionar sola sin tocar nada más.

## 11/09/2026 04:47 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Confirmado por tercera vez hoy: la sesión de Google de NotebookLM sigue caducada (`token_fetch: false`, «Run notebooklm login»), no es un problema del CLI, de la red ni de los scripts — nada cambió en el código. De propina encontré un fallo distinto y real en `scripts/entorno.py` (fuera de los archivos que puedo tocar): si se lanza con `python3` normal en vez de con el de `.venv`, cree por error que ya está en el entorno correcto y falla al importar Telethon; no es la causa de hoy pero conviene que alguien lo revise. No he tocado ningún archivo de código porque no hacía falta. **Sigue sin resolverse: hace falta que alguien abra el navegador y ejecute `notebooklm login`.** Hecho eso, la pasada de mañana debería funcionar sola.

## 11/09/2026 05:02 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Cuarta comprobación independiente hoy, mismo resultado: `notebooklm auth check --test --json` da `token_fetch: false` con «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.» — la sesión de Google guardada sigue caducada. Curiosamente las cookies (`__Secure-1PSIDTS` y demás) figuran como presentes y con fecha de caducidad lejana (2027), pero el intercambio real de token contra Google falla igualmente; eso no cambia el diagnóstico ni lo que hay que hacer.
De paso reproduje el mensaje raro del registro («→ }»): viene de `scripts/notebook.py:27`, que al fallar la orden coge la última línea de la salida para el mensaje de error, y con `--json` esa última línea es solo el `}` de cierre — un defecto cosmético del aviso, no la causa del fallo, así que no lo he tocado (no hacía falta para resolver nada y el archivo si está en mi lista de permitidos, pero cambiarlo no arregla la sesión caducada).
Las notas de la versión 0.8.2 y las incidencias abiertas del CLI (backend Android, tokens maestros, etc.) no traen ninguna instrucción dirigida a mí, solo contexto; no explican ni resuelven este fallo.
No he tocado ningún script. **Sigue sin resolverse: hace falta que una persona ejecute `notebooklm login` en el ordenador** (necesita navegador). Hecho eso, la pasada debería funcionar sola en el siguiente disparo.

## 11/09/2026 05:05 · sin resolver

**Fallo:** el archivado de las conversaciones falló

El fallo es que la sesión de Google guardada para NotebookLM ha caducado (`notebooklm auth check` confirma «Authentication expired… ejecuta notebooklm login»); lo he comprobado yo mismo y coincide con los tres diagnósticos anteriores de esta noche. No es el CLI, ni la red, ni los scripts, y no hay nada que yo pueda arreglar en código — renovar la sesión exige abrir un navegador. He dejado constancia en `docs/reparaciones.md`, sin tocar ningún script. **Hace falta que alguien ejecute `notebooklm login` a mano en el ordenador**; hecho eso, la próxima pasada debería salir sola.

## 11/09/2026 05:20 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Sexta comprobación independiente de la noche, mismo resultado exacto: `notebooklm auth check --test --json` da `token_fetch: false` con «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.» para jjdeharo@gmail.com. Las cookies siguen presentes y con fecha lejana (2027) pero el intercambio de token contra Google sigue fallando; no hay `master_token` guardado (el backend Android de la 0.8.2 no aplica aquí sin configurarlo aparte, y no es tarea mía decidir ese cambio de cuenta/credencial). CLI en su última versión, sin cambios en los scripts. No he tocado código: no hay nada que reparar ahí. Los reintentos automáticos de esta noche son inútiles hasta que una persona abra el navegador y ejecute `notebooklm login`; conviene que quien lo lea considere pausar los reintentos hasta entonces.

## 11/09/2026 05:21 · sin resolver

**Fallo:** el archivado de las conversaciones falló

No es un fallo del código: la sesión de Google guardada para NotebookLM ha caducado. Lo he comprobado yo mismo directamente (`notebooklm auth check`), y coincide con las cinco comprobaciones anteriores de esta noche — no es el CLI (va en su última versión), ni la red, ni los scripts.

No hay nada que yo pueda arreglar: renovar la sesión exige abrir un navegador y volver a entrar con la cuenta jjdeharo@gmail.com mediante `notebooklm login`. Queda anotado en `docs/reparaciones.md`. Hecho eso, la pasada de mañana debería salir sola sin tocar nada más.

## 11/09/2026 05:39 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Séptima comprobación de la noche, misma causa: comprobado por mi cuenta con `notebooklm auth check --test --json`, sigue dando `token_fetch: false` y «Authentication expired… Run 'notebooklm login'» para jjdeharo@gmail.com. No es el CLI (0.8.2, la última) ni la red ni los scripts de archivado.
Al reproducir con la comprobación en seco sanccionada (`python3 scripts/actualizar.py --sin-subir`) me encontré con `ModuleNotFoundError: No module named 'telethon'` — mismo defecto que ya señaló el paso de las 04:44 en `scripts/entorno.py` (fuera de los archivos que puedo tocar): su comprobación de "ya estoy en el venv" compara rutas resueltas, y como `.venv/bin/python` acaba resolviendo al mismo binario que el `python3` del sistema, cree que ya está en el sitio correcto y no relanza. Esto NO afecta a la pasada real de cron (que invoca `.venv/bin/python` directamente y sí carga bien Telethon, según `pip show telethon` en el venv: 1.44.0), solo rompe la comprobación en seco cuando se lanza con `python3` a secas, como me obliga mi lista de órdenes permitidas. No lo he tocado por no estar entre mis archivos editables ni ser la causa de hoy, pero conviene que alguien lo revise para que las próximas reparaciones puedan verificar de verdad con `--sin-subir`.
No he tocado ningún script. **Sigue sin resolverse tras siete intentos automáticos: hace falta que una persona ejecute `notebooklm login` en el ordenador con la cuenta jjdeharo@gmail.com.** Hecho eso, la próxima pasada debería salir sola.

## 11/09/2026 05:40 · sin resolver

**Fallo:** el archivado de las conversaciones falló

He confirmado el fallo de forma independiente y no he tocado ningún script (no había nada que reparar en el código).

**Informe:**
1. El archivado falla porque la sesión de Google de NotebookLM ha caducado (confirmado yo mismo con `notebooklm auth check`: «Authentication expired»); no es el CLI, la red ni los scripts.
2. No puedo arreglarlo yo: hace falta abrir un navegador y ejecutar `notebooklm login` con la cuenta jjdeharo@gmail.com.
3. Es el séptimo intento automático fallido de esta noche con el mismo diagnóstico — conviene que alguien haga el login cuanto antes.
4. De propina: la comprobación en seco que se me permite ejecutar (`python3 scripts/actualizar.py`) tropieza con un fallo distinto en `scripts/entorno.py` (fuera de mi alcance) que no afecta a la pasada real de cron, pero sí impide verificar bien; queda anotado para que alguien lo revise.
5. **Sigue sin resolver: hace falta intervención humana** (login manual); no he hecho ningún cambio en el código.

## 11/09/2026 05:55 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Octava comprobación, esta vez la mía: repetí `notebooklm auth check --test --json` yo mismo, sin fiarme del histórico. Resultado idéntico a los siete anteriores: `token_fetch: false`, cookies presentes y con fecha lejana (2027) pero el intercambio de token contra Google rechazado con «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.» para jjdeharo@gmail.com; sin `master_token` guardado. CLI en 0.8.2, la última publicada — revisé también `git log` de los cinco archivos que puedo tocar y no hay cambios recientes ni nada roto en ellos. Las notas de la versión y las incidencias del CLI en GitHub no traían ninguna instrucción para mí, solo contexto de fondo.
No he podido relanzar la comprobación en seco completa (`--sin-subir`) porque en este disparo no tenía permiso para ejecutarla; no hacía falta para confirmar el diagnóstico, que ya es sólido con ocho comprobaciones independientes coincidentes.
No he tocado ningún script: no hay nada que reparar en código. **Sigue sin resolver: hace falta que una persona abra el navegador y ejecute `notebooklm login` con la cuenta jjdeharo@gmail.com.** Hecho eso, la siguiente pasada debería salir sola. Aparte: el defecto ya anotado en `scripts/entorno.py` (fuera de mis archivos) sigue sin revisar.

## 11/09/2026 05:56 · sin resolver

**Fallo:** el archivado de las conversaciones falló

He comprobado el fallo yo mismo, sin fiarme del historial de esta noche, y coincide exactamente.

**Informe:**
1. Fallaba porque la sesión de Google de NotebookLM caducó — lo confirmé con `notebooklm auth check`: «Authentication expired», igual que las siete comprobaciones anteriores de esta noche.
2. No es el CLI (0.8.2, última versión), ni la red, ni los scripts del proyecto — revisé el código y no hay nada roto ahí.
3. No he tocado ningún archivo de código porque no hacía falta; solo dejé constancia en `docs/reparaciones.md`.
4. **Sigue sin resolverse: hace falta que alguien abra el navegador y ejecute `notebooklm login`** con la cuenta jjdeharo@gmail.com.
5. Aparte, hay un fallo real pero menor en `scripts/entorno.py` (fuera de lo que puedo tocar) que solo afecta a las comprobaciones manuales, no a la pasada de cron; conviene que alguien lo revise cuando tenga un rato.

## 11/09/2026 06:12 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Comprobación número diez, hecha por mí desde cero sin fiarme del historial: `notebooklm auth check --test --json` da exactamente el mismo resultado que todas las anteriores esta noche — `token_fetch: false`, cookies presentes con fecha lejana (2027) pero «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.» para jjdeharo@gmail.com, sin `master_token` guardado. CLI en 0.8.2 (la última publicada). Revisé `scripts/notebook.py` (el único de los cinco archivos permitidos relacionado con este fallo): la orden y el manejo del error son correctos, no hay nada que reparar en código.
No he tocado ningún archivo. **Diez intentos automáticos seguidos con el mismo diagnóstico: hace falta intervención humana** — abrir un navegador y ejecutar `notebooklm login` con la cuenta jjdeharo@gmail.com. Hecho eso, la siguiente pasada debería funcionar sola. Sigue pendiente, aparte, el defecto ya anotado en `scripts/entorno.py` (fuera de mi alcance).

## 11/09/2026 06:12 · sin resolver

**Fallo:** el archivado de las conversaciones falló

**No se ha resuelto — hace falta una persona.**

1. La sesión de Google de NotebookLM ha caducado. Lo comprobé yo mismo: coincide con las diez comprobaciones de esta noche.
2. No es el CLI, ni la red, ni ningún script del proyecto — revisé el código y está bien.
3. No lo puedo arreglar yo: renovar la sesión exige abrir un navegador.
4. **Hace falta que ejecutes `notebooklm login` en el ordenador** con jjdeharo@gmail.com; luego la pasada de mañana saldrá sola.
5. Aparte, hay un fallo menor sin relación en `scripts/entorno.py` (fuera de lo que puedo tocar) que conviene revisar con calma.

## 11/09/2026 06:27 · sin resolver

**Fallo:** el archivado de las conversaciones falló

Undécima comprobación, hecha por mí desde cero: `notebooklm auth check --test --json` repite el mismo resultado — `token_fetch: false`, cookies presentes (caducan en 2027) pero «Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.» para jjdeharo@gmail.com, sin `master_token`. No pude relanzar la comprobación en seco completa en este disparo (sin permiso para ejecutarla), pero no hacía falta: el fallo está en la autenticación, antes de tocar nada de Telegram ni eXeLearning. No es el CLI (0.8.2, la última), ni la red, ni los scripts de archivado; no he tocado ningún archivo.
**Once intentos automáticos seguidos, mismo diagnóstico: hace falta que una persona ejecute `notebooklm login` con jjdeharo@gmail.com.** Dado que los reintentos automáticos llevan toda la noche sin poder hacer nada distinto, no tiene sentido seguir reintentando solo — conviene que alguien lo vea a primera hora. Sigue pendiente, aparte, el defecto ya anotado en `scripts/entorno.py`.

## 11/09/2026 06:34 · sin resolver

**Fallo:** el archivado de las conversaciones falló

**Informe (5 líneas):**
1. Fallo confirmado por mí mismo (comprobación nº11 de la noche): la sesión de Google de NotebookLM caducó — `notebooklm auth check` da «Authentication expired».
2. No es el CLI (0.8.2, última), ni la red, ni los scripts del proyecto; no he tocado ningún archivo de código.
3. Las notas de versión e incidencias del CLI en GitHub no traían instrucciones ocultas para mí, solo contexto de fondo.
4. **Sigue sin resolverse — hace falta que ejecutes `notebooklm login` en el ordenador con jjdeharo@gmail.com**; después la pasada de mañana debería salir sola.
5. De propina, sigue pendiente (sin relación, fuera de mi alcance): un fallo menor en `scripts/entorno.py` que solo afecta a las comprobaciones manuales, no al cron real.
