# 0003. Copia diaria del registro de administradores de los grupos

- Fecha: 31/10/2026
- Estado: aceptada

## Contexto

En los grupos entra spam casi a diario: anuncios en chino con mención a otro bot,
publicados por cuentas recién llegadas que superan la verificación de AntiUserbotsBot y
escriben entre 1 y 15 horas después. Del 29 al 31/10/2026 los administradores borraron a
mano cuatro (tres en eXeLearning y uno en Vibe Coding Educativo). El 31/10/2026 Juanjo
activó el antispam propio de Telegram en los cuatro grupos que cubren los bots
(ChatGPT-IA-edu, Vibe Coding Educativo, EduMedia-IAG y eXeLearning) y quiere comprobar
al cabo de una semana si basta o si hace falta que los bots borren el spam.

Para eso hay que saber qué ha borrado el antispam, qué siguen borrando los
administradores y si ha borrado algo legítimo. Telegram solo conserva **48 horas** del
registro de administradores (documentación de `channels.getAdminLog`: «events from the
last 48 hours»; comprobado el 31/10/2026: el registro más antiguo de los cuatro grupos
era del 29/10/2026), así que mirarlo el día de la revisión no basta.

## Decisión

- `scripts/registro-admin.py` lee con la sesión de Telegram del proyecto los borrados y
  las expulsiones del registro de administradores de los cuatro grupos y los añade a
  `datos/registro-admin/<grupo>.jsonl` (fecha en UTC, quién actúa, autor, texto y
  adjunto del mensaje borrado). No repite lo que ya tenía: compara por el identificador
  del evento.
- Lo llama `diario.sh` justo después del archivado, una vez al día. Entre dos pasadas
  hay como mucho un día, menos que las 48 horas que guarda Telegram.
- EduMedia-IAG no se archiva en este proyecto, pero entra en esta copia porque es uno de
  los grupos de los bots.
- Un fallo no detiene la pasada (`|| true`): es un dato de apoyo, no del archivado.

## Alternativas descartadas

- Que lo copien los bots: la API de bots no da acceso al registro de administradores;
  hace falta la cuenta de Juanjo, cuya sesión ya usa este proyecto en el NAS.
- Un proceso aparte en el portátil: puede estar apagado, y la sesión de Telegram no debe
  conectarse desde dos sitios a la vez fuera de la red de casa.

## Consecuencias

- `datos/` no se sube a GitHub (contiene mensajes de personas reales), igual que el
  resto de las exportaciones.
- Si tras la revisión el antispam basta, la copia puede seguir como registro o
  retirarse; si se retira, se quita la llamada de `diario.sh` y este ADR pasa a
  «sustituida».

## Validación

Probado el 31/10/2026 en el portátil con la misma cuenta: 60 acciones de los cuatro
grupos guardadas; una segunda ejecución no añadió ninguna.
