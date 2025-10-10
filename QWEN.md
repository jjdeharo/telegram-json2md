# Instrucciones para convertir JSON de Telegram a Markdown con hilos

## Objetivo
Convertir uno o varios archivos JSON exportados de Telegram en un único documento Markdown legible por NotebookLM, manteniendo los hilos de respuesta, el orden temporal y la estructura por días.

## Procedimiento

### 1. Preparación
- Asegurarse de que los archivos JSON de Telegram se encuentran en la carpeta actual.
- Detectar automáticamente todos los archivos `*.json` en el directorio.

### 2. Procesamiento
- Ejecutar el script `procesar_telegram.py` que:
  - Lee y fusiona los archivos JSON, eliminando duplicados
  - Extrae información del canal/grupo (nombre y tipo) para incluirla en el encabezado
  - Reconstruye los hilos de conversación usando `reply_to_message_id`
  - Agrupa los mensajes por día con encabezados en español (formato: `## 5 mayo 2025`)
  - Formatea los mensajes raíz como: `**Autor (ID: ID_único) (HH:MM)**  \nTexto`
  - Formatea las respuestas como: `> ↩︎ **Autor (ID: ID_único) (HH:MM)** en respuesta a AutorOriginal (ID: ID_único) (HH:MM)  \n> Texto`
  - Convierte adecuadamente el formato de texto (negritas, cursivas, enlaces, código)
  - Ordena cronológicamente dentro de cada día y hilo
  - Omite mensajes con `type != "message"` o sin texto útil

### 3. Generación de archivos
- Si el contenido es muy grande, dividir por meses en archivos `conversacion-YYYY-MM.md`
- Crear un `README.md` con índice de los archivos mensuales
- Los archivos se generan en la subcarpeta `salida/`

### 4. Validación
- Verificar que no hay días vacíos
- Confirmar que las fechas están correctamente ordenadas
- Asegurar que los encabezados de día están en español
- Validar que hay al menos un archivo `.md` con contenido

## Archivos generados
- `conversacion-YYYY-MM.md`: Contenido mensual de la conversación
- `README.md`: Índice con enlaces a los archivos mensuales
- `salida/`: Carpeta que contiene los archivos mensuales

## Formato de salida
- Imprimir al final las rutas absolutas de los archivos generados con el formato:
```
RESULT_PATH:/ruta/completa/al/archivo.md
```

## Notas
- El script maneja correctamente el formato de texto de Telegram (strings o listas de spans)
- Mantiene emojis y formatea enlaces correctamente
- Se ejecuta localmente sin subir datos a servicios externos
- Es tolerante a errores en el esquema JSON