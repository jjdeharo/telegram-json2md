import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

def parse_text(text_field) -> str:
    """Parse Telegram's text field which can be string or list of spans"""
    if isinstance(text_field, str):
        return text_field
    elif isinstance(text_field, list):
        result = []
        for item in text_field:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Handle formatting spans
                text_content = item.get('text', '')
                if item.get('type') == 'bold':
                    result.append(f'**{text_content}**')
                elif item.get('type') == 'italic':
                    result.append(f'*{text_content}*')
                elif item.get('type') == 'code':
                    result.append(f'`{text_content}`')
                elif item.get('type') == 'pre':
                    result.append(f'```\n{text_content}\n```')
                elif item.get('type') == 'text_link':
                    result.append(f'[{text_content}]({item.get("href", "")})')
                elif item.get('type') == 'mention':
                    result.append(f'@{text_content}')
                elif item.get('type') == 'hashtag':
                    result.append(f'#{text_content}')
                elif item.get('type') == 'cashtag':
                    result.append(f'${text_content}')
                else:
                    result.append(text_content)
        return ''.join(result)
    else:
        return str(text_field)

def procesar_archivos_json(rutas_archivos: List[str]) -> Dict[str, Any]:
    """Lee y fusiona múltiples archivos JSON"""
    mensajes = []
    chat_info = {}
    
    for ruta in rutas_archivos:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            mensajes.extend(datos.get('messages', []))
            # Extraer información del chat si está disponible
            if 'name' in datos:
                chat_info['name'] = datos['name']
            if 'type' in datos:
                chat_info['type'] = datos['type']
            if 'id' in datos:
                chat_info['id'] = datos['id']
    
    # Eliminar duplicados basados en ID
    mensajes_unicos = {}
    for msg in mensajes:
        msg_id = msg.get('id')
        if msg_id not in mensajes_unicos:
            mensajes_unicos[msg_id] = msg
    
    result = {'messages': list(mensajes_unicos.values()), 'chat_info': chat_info}
    return result

def construir_indice_mensajes(mensajes: List[Dict]) -> Dict[int, Dict]:
    """Construye un índice de mensajes por ID"""
    return {msg['id']: msg for msg in mensajes if 'id' in msg}

def formatear_fecha(date_str: str) -> str:
    """Convierte fecha ISO a formato '5 mayo 2025'"""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    return f"{dt.day} {meses[dt.month]} {dt.year}"

def formatear_hora(date_str: str) -> str:
    """Obtiene hora en formato HH:MM"""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return f"{dt.hour:02d}:{dt.minute:02d}"

def obtener_hilo_raiz(msg_id: int, mensajes_idx: Dict[int, Dict], visitados=None) -> List[Dict]:
    """Obtiene la cadena completa del hilo hasta la raíz"""
    if visitados is None:
        visitados = set()
    
    if msg_id in visitados:
        # Evitar bucles
        return []
    
    msg = mensajes_idx.get(msg_id)
    if not msg:
        return []
    
    visitados.add(msg_id)
    
    reply_to_id = msg.get('reply_to_message_id')
    if not reply_to_id or reply_to_id not in mensajes_idx:
        # Mensaje raíz
        return [msg]
    
    # Recursivamente obtener el hilo
    hilo_padre = obtener_hilo_raiz(reply_to_id, mensajes_idx, visitados)
    hilo_padre.append(msg)
    return hilo_padre

def generar_markdown(mensajes: List[Dict], chat_info: Dict = None) -> str:
    """Genera el contenido Markdown con hilos y agrupación por día"""
    # Filtrar mensajes válidos
    mensajes_validos = [
        msg for msg in mensajes
        if msg.get('type') == 'message'
        and msg.get('text')
        and (isinstance(msg.get('text'), str) or len(msg.get('text')) > 0)
    ]
    
    # Ordenar por fecha
    mensajes_validos.sort(key=lambda x: x['date'])
    
    # Agrupar por día
    mensajes_por_dia = {}
    for msg in mensajes_validos:
        dia = formatear_fecha(msg['date'])
        if dia not in mensajes_por_dia:
            mensajes_por_dia[dia] = []
        mensajes_por_dia[dia].append(msg)
    
    # Construir índice de mensajes para reconstruir hilos
    mensajes_idx = construir_indice_mensajes(mensajes_validos)
    
    # Procesar cada día
    resultado = []
    
    # Agregar información del chat al principio del archivo
    if chat_info:
        # Convertir tipo de chat a una forma más legible
        tipo_chat = chat_info.get('type', 'desconocido')
        nombre_tipo = {
            'private': 'Chat privado',
            'group': 'Grupo',
            'supergroup': 'Supergupo',
            'channel': 'Canal',
            'public_supergroup': 'Supergupo público'
        }
        tipo_legible = nombre_tipo.get(tipo_chat, tipo_chat)
        
        resultado.append(f"# {chat_info.get('name', 'Chat desconocido')} ({tipo_legible})\n\n")
    
    for dia in sorted(mensajes_por_dia.keys()):
        resultado.append(f"## {dia}\n")
        
        # Para cada día, construir hilos
        mensajes_dia = mensajes_por_dia[dia]
        procesados = set()
        
        for msg in mensajes_dia:
            if msg['id'] in procesados:
                continue
                
            # Verificar si es una respuesta
            reply_to_id = msg.get('reply_to_message_id')
            if reply_to_id and reply_to_id in mensajes_idx:
                # Este mensaje es respuesta, reconstruir el hilo
                hilo = obtener_hilo_raiz(msg['id'], mensajes_idx)
            else:
                # Mensaje raíz
                hilo = [msg]
            
            # Procesar cada mensaje en el hilo
            for hilo_msg in hilo:
                if hilo_msg['id'] in procesados:
                    continue
                
                texto = parse_text(hilo_msg['text'])
                if not texto.strip():
                    continue
                
                autor = hilo_msg.get('from', 'Desconocido')
                autor_id = hilo_msg.get('from_id', 'ID_desconocido')
                hora = formatear_hora(hilo_msg['date'])
                
                # Calcular nivel de anidamiento
                reply_id = hilo_msg.get('reply_to_message_id')
                if reply_id:
                    # Encontrar el mensaje al que responde
                    reply_msg = mensajes_idx.get(reply_id)
                    if reply_msg:
                        reply_autor = reply_msg.get('from', 'Desconocido')
                        reply_autor_id = reply_msg.get('from_id', 'ID_desconocido')
                        reply_hora = formatear_hora(reply_msg['date'])
                        
                        # Crear cadena de respuesta
                        resultado.append(f"> ↩︎ **{autor} (ID: {autor_id}) ({hora})** en respuesta a {reply_autor} (ID: {reply_autor_id}) ({reply_hora})  \n> {texto}\n")
                    else:
                        # Mensaje de respuesta pero no se encontró el original en este día
                        resultado.append(f"> ↩︎ **{autor} (ID: {autor_id}) ({hora})** en respuesta a mensaje anterior  \n> {texto}\n")
                else:
                    # Mensaje raíz
                    resultado.append(f"**{autor} (ID: {autor_id}) ({hora})**  \n{texto}\n")
                
                procesados.add(hilo_msg['id'])
        
        resultado.append("")  # Línea vacía entre días
    
    return "\n".join(resultado)

def main():
    # Detectar archivos JSON en directorio actual
    archivos_json = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not archivos_json:
        print("No se encontraron archivos JSON en el directorio actual")
        return
    
    # Procesar archivos
    resultado = procesar_archivos_json(archivos_json)
    mensajes = resultado['messages']
    chat_info = resultado.get('chat_info', {})
    
    # Generar contenido Markdown
    contenido = generar_markdown(mensajes, chat_info)
    
    # Dividir por meses si es grande
    if len(contenido) > 200000:  # 200k caracteres
        # Crear directorio para archivos divididos
        os.makedirs('salida', exist_ok=True)
        
        # Dividir por meses
        mensajes_fecha = [(datetime.fromisoformat(m['date'].replace('Z', '+00:00')), m) for m in mensajes if 'date' in m]
        mensajes_fecha.sort(key=lambda x: x[0])
        
        meses = {}
        for dt, msg in mensajes_fecha:
            mes_anio = f"{dt.year}-{dt.month:02d}"
            if mes_anio not in meses:
                meses[mes_anio] = []
            meses[mes_anio].append(msg)
        
        rutas_generadas = []
        for mes_anio, msgs in meses.items():
            contenido_mes = generar_markdown(msgs, chat_info)
            nombre_archivo = f"conversacion-{mes_anio}.md"
            ruta_archivo = os.path.join('salida', nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido_mes)
            
            rutas_generadas.append(os.path.abspath(ruta_archivo))
        
        # Crear README con índice
        readme_content = "# Conversación Telegram\n\n"
        readme_content += "Índice de conversaciones por mes:\n\n"
        for mes_anio in sorted(meses.keys()):
            readme_content += f"- [{mes_anio}](./salida/conversacion-{mes_anio}.md)\n"
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        rutas_generadas.append(os.path.abspath('README.md'))
        
        for ruta in rutas_generadas:
            print(f"RESULT_PATH:{ruta}")
    else:
        # Guardar en archivo único
        with open('conversacion.md', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"RESULT_PATH:{os.path.abspath('conversacion.md')}")

if __name__ == "__main__":
    main()