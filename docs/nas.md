# La pasada diaria en el NAS

Desde el 08/09/2026 el archivado diario no corre en el portátil, sino en el NAS
de casa (`DXP2800-BD1F`, `192.168.1.113`), dentro de un contenedor. El motivo es
el evidente: el NAS está siempre encendido y el portátil no, así que un día sin
abrir el ordenador ya no es un día sin archivar.

Lo que corre es exactamente el mismo código de este repositorio; lo único que
cambia es dónde está y quién lo dispara.

## Dónde vive

```
/volume1/docker/memoria-telegram/
  compose.yml  Dockerfile  bucle.sh   la definición del contenedor (copia de nas/)
  clonar-repos.sh                     clona los repositorios de eXeLearning
  repo/     clon de este repositorio, con los datos dentro (se monta en /proyecto)
  repos/    exelearning y su ecosistema, que lee el sincronizador (en /repos)
  home/     el home del contenedor: .notebooklm, .claude, .config/avisar-juanjo
```

Nada importante vive dentro de la imagen: reconstruirla no toca ni los datos ni
las sesiones. Lo que hay que respaldar es `repo/` y `home/`.

## Cómo se opera

```bash
ssh jjdeharo@192.168.1.113
cd /volume1/docker/memoria-telegram

docker compose up -d --build          # construir y arrancar
docker compose logs -f                # ver el bucle
docker exec -it memoria-telegram bash # entrar a trabajar a mano
docker exec memoria-telegram /proyecto/scripts/diario.sh   # forzar la pasada

tail -f repo/registro/diario-$(date +%F).log               # el registro del día
```

El registro y el índice se leen desde el propio NAS, sin entrar al contenedor:
`repo/` está montado desde el disco.

## El reloj

En el portátil el disparo era cron: `@reboot` y cada cuarto de hora de 7 a 23.
Aquí el contenedor está siempre vivo, así que `nas/bucle.sh` hace ambas cosas: el
arranque del contenedor hace de `@reboot` y el bucle, de cuartos de hora. La
idempotencia sigue siendo de `diario.sh`, que corta los disparos sobrantes con la
marca del día.

**La pasada arranca a las 4 de la mañana**, no a las 7 como en el portátil: el
NAS no se apaga, así que no hay que esperar a que haya alguien delante, y a esa
hora ni Telegram ni NotebookLM tienen tráfico. Los cuartos de hora siguen hasta
las 23, que son los reintentos por si algo falla. Para moverla, se cambia la
ventana en `nas/bucle.sh` y se reconstruye la imagen: el fichero va dentro.

`restart: unless-stopped` se ocupa de que un reinicio del NAS lo vuelva a
levantar. **No hay que instalar nada en el crontab del NAS.**

## Las tres sesiones

Este era el punto que parecía difícil y no lo es: ninguna de las tres necesita
navegador en el NAS. Se copiaron del portátil una vez y viven en `home/`.

| Sesión | Dónde | Cómo se rehace si caduca |
|---|---|---|
| Telegram | `repo/sesion/telegram.session` | Es la misma sesión, no una nueva: Telegram no pide código. Si algún día se revoca, hay que autorizarla a mano con `docker exec -it` y el código del móvil. |
| NotebookLM | `home/.notebooklm/` | Lo primero, `docker exec memoria-telegram notebooklm auth refresh`: desde el master token lo rehace sin navegador y sin salir del NAS (ver abajo). Si eso fallara, se entra en el portátil y se copia `profiles/default/storage_state.json` a `/volume1/docker/memoria-telegram/home/.notebooklm/profiles/default/`. **Con eso valen los dos contenedores**: el del boletín tiene esa misma carpeta montada, no una copia. |
| Claude | `home/.claude/.credentials.json` y `home/.claude.json` | Copiar de nuevo desde el portátil, o `claude setup-token`. |
| El bot de avisos | `home/.config/avisar-juanjo/config.json` | Copiar de nuevo desde el portátil. |

El día que el trabajo diario empiece a fallar con «la sesión de NotebookLM ha
caducado», eso es lo único que hay que rehacer.

**Ojo con el orden**: entrar en NotebookLM desde el portátil **no** arregla el
NAS. Son dos copias distintas de la sesión, y mientras no se copie el fichero
los avisos de caducidad siguen llegando. Pasó el 11 de septiembre de 2026.

### El master token, ya puesto

Desde el 11 de septiembre de 2026 el NAS **renueva la sesión él solo, sin
navegador**:

```bash
docker exec memoria-telegram notebooklm auth refresh
```

Responde `ok refreshed: …/profiles/default/storage_state.json`. Vale igual desde
`boletin-semanal`, porque comparten la carpeta.

**Pero ni eso hace falta**: el CLI lo hace solo cuando le hace falta. Probado el
11 de septiembre de 2026 rompiendo a mano las cookies de sesión (`SID`,
`__Secure-1PSID`, `__Secure-3PSID`, `SAPISID`): el `notebooklm list` siguiente
respondió bien, sin avisar de nada, y dejó el fichero reescrito con cookies
nuevas. `auth refresh` queda para forzarlo a mano.

Lo que lo hace posible es `home/.notebooklm/profiles/default/master_token.json`,
acuñado una vez en el portátil con
`notebooklm -p nas login --master-token --account jjdeharo@gmail.com`. Ese
bootstrap **sí** necesita una firma con navegador —se queda esperando en la
ventana de Chromium, sin decir nada en el terminal—, y por eso se hace en el
portátil; lo que evita es el navegador de todas las veces siguientes. Del perfil
`nas` del portátil se copiaron al NAS dos ficheros: `master_token.json` y
`storage_state.json`.

Dos cosas que lo sostienen y conviene no romper:

- Los Dockerfiles instalan `notebooklm-py[browser,headless]`. **Los dos extras en
  la misma orden**: el extra `headless` es el que trae `gpsoauth`, y una
  reinstalación con solo `headless` deja sin `playwright`. Si algún día se
  reconstruye la imagen, esto ya va dentro; en los contenedores de ahora
  `gpsoauth` se añadió en caliente con
  `uv pip install --python /opt/uv/tools/notebooklm-py/bin/python gpsoauth`.
- El master token es una credencial duradera de la cuenta de Google. Tiene
  permisos 600 y no sale de `home/`.

## Lo que es distinto respecto del portátil

- **`config.json` no es el mismo fichero.** El del NAS apunta a `/repos/…` en vez
  de a `~/Documentos/github/…`. Lo demás —claves y notebooks— es idéntico.
- **Los repositorios de eXeLearning se clonaron por HTTPS y en anónimo**, que es
  todo lo que hace falta para leerlos. El de eXeLearning va con
  `--filter=blob:none`: ocupa 690 MB en vez de 2,5 GB y `git show` se baja lo que
  necesite.
- **El repositorio del NAS es un clon aparte.** Los commits que dejen ahí el
  reparador o la decisión automática son locales: no llegan a GitHub solos. Vale
  la pena mirar de vez en cuando `git -C repo log --oneline -5` y traérselos.
- **No hay pantalla**, así que `avisar.sh` no muestra nada —sale limpio si no
  encuentra `notify-send`— y `diario.sh` ya no espera a la sesión gráfica. Los
  avisos que importan siguen llegando por Telegram.

## Si hay que volver al portátil

Es reversible en dos órdenes: parar el contenedor y devolver el cron.

```bash
ssh jjdeharo@192.168.1.113 'cd /volume1/docker/memoria-telegram && docker compose down'
cd ~/Documentos/github/automatizaciones/memoria-telegram && scripts/instalar.sh
```

Antes de eso, traerse `repo/estado.json`, `repo/datos/` y `repo/salida/` del NAS:
mientras el contenedor archiva, el portátil se queda atrás.

**Lo que no se puede hacer es tenerlo en los dos sitios a la vez.** Dos procesos
con la misma sesión de Telegram y el mismo notebook acabarían duplicando fuentes
—o revocando la sesión—, así que el disparo del portátil se retiró al migrar.
