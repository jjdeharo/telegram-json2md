# Conversor de JSON de Telegram a Markdown

Esta herramienta permite convertir archivos JSON exportados de Telegram a formato Markdown, manteniendo la estructura de hilos de conversación y el orden cronológico de los mensajes.

## Características

- Conversión de uno o varios archivos JSON de Telegram a Markdown
- Reconstrucción de hilos de conversación usando `reply_to_message_id`
- Agrupación de mensajes por día con encabezados en español
- Formateo adecuado de texto (negritas, cursivas, enlaces, código)
- Previsualización en tiempo real de los archivos Markdown generados
- Descarga de archivos mensuales de conversación
- Interfaz web sencilla y amigable

## Cómo usar

1. Abre el archivo `index.html` en tu navegador web
2. Haz clic en "Subir Archivos JSON" y selecciona uno o más archivos JSON exportados de Telegram
3. Haz clic en el botón "Convertir a Markdown"
4. La herramienta procesará los archivos y mostrará una previsualización
5. Navega entre los archivos mensuales usando los botones de mes
6. Haz clic en "Descargar Archivo" para guardar el archivo Markdown actual

## Formato de salida

- Los mensajes raíz se formatean como: `**Autor (ID: ID_único) (HH:MM)**  \nTexto`
- Las respuestas se formatean como: `> ↩︎ **Autor (ID: ID_único) (HH:MM)** en respuesta a AutorOriginal (ID: ID_único) (HH:MM)  \n> Texto`
- Los encabezados de día están en español con el formato: `## 5 mayo 2025`
- La conversación se divide en archivos mensuales: `conversacion-YYYY-MM.md`

## Notas

- La herramienta funciona completamente en el navegador, sin subir tus datos a servicios externos
- Todos los cálculos se realizan localmente en tu dispositivo
- Se mantienen emojis y se formatean enlaces correctamente
- Se omiten mensajes con `type != "message"` o sin texto útil