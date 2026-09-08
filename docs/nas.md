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
| NotebookLM | `home/.notebooklm/` | `notebooklm login` necesita navegador, así que se hace en el portátil y se vuelve a copiar la carpeta. Para no repetirlo nunca más está `notebooklm login --master-token --account jjdeharo@gmail.com`, que acuña cookies sin navegador. |
| Claude | `home/.claude/.credentials.json` y `home/.claude.json` | Copiar de nuevo desde el portátil, o `claude setup-token`. |
| El bot de avisos | `home/.config/avisar-juanjo/config.json` | Copiar de nuevo desde el portátil. |

El día que el trabajo diario empiece a fallar con «la sesión de NotebookLM ha
caducado», eso es lo único que hay que rehacer.

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
