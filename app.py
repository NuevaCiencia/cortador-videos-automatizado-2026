import os
import re
import glob
import subprocess

# ==========================================
# UTILIDADES
# ==========================================
def extraer_video_id(url):
    """Extrae el ID del video de una URL de YouTube."""
    # Soporta formatos como watch?v=ID, youtu.be/ID, shorts/ID
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if match:
        return match.group(1)
    return None

def format_time(seconds):
    """Convierte segundos a formato HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def parse_timestamp(ts):
    """Convierte HH:MM:SS,mmm a HH:MM:SS.mmm para FFmpeg y corrige errores de formato de la IA"""
    ts = ts.replace(',', '.')
    # Si la IA alucinó y puso 4 secciones (ej. 00:00:01:00.200), nos quedamos con las últimas 3 (HH:MM:SS.mmm)
    partes = ts.split(':')
    if len(partes) > 3:
        ts = ':'.join(partes[-3:])
    return ts

def preguntar_continuar(fase_completada):
    """Pausa la ejecución y pregunta al usuario si desea continuar."""
    respuesta = input(f"\n[+] Fase '{fase_completada}' completada. ¿Deseas continuar con la siguiente fase? (s/n): ").strip().lower()
    if respuesta != 's':
        print("\n[!] Proceso detenido por el usuario.")
        exit(0)

# ==========================================
# FASE 1: DESCARGA
# ==========================================
def fase_1_descargar(url, project_folder, force=False):
    print("\n--- FASE 1: DESCARGA DE VIDEO Y AUDIO ---")
    
    import yt_dlp # Importación perezosa para que la app cargue rápido
    
    if not force and os.path.exists(os.path.join(project_folder, 'video.mp4')) and os.path.exists(os.path.join(project_folder, 'video.mp3')):
        print("[INFO] El video y audio ya han sido descargados previamente. Saltando fase...")
        return
        
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(project_folder, 'video.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'keepvideo': True, # Mantiene el MP4 original intacto
        'postprocessors': [
            {
                # Extrae una copia en MP3
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls']
            }
        },
    }

    print(f"Descargando archivos en '{project_folder}'...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("¡Descarga completada!")
    except Exception as e:
        print(f"Error durante la descarga: {e}")
        exit(1)

# ==========================================
# FASE 2: TRANSCRIPCIÓN
# ==========================================
def fase_2_transcribir(project_folder, force=False):
    print("\n--- FASE 2: TRANSCRIPCIÓN CON WHISPER ---")
    
    import whisper # Importación perezosa (la más pesada)
    
    output_file = os.path.join(project_folder, "extraccion.txt")
    if not force and os.path.exists(output_file):
        print("[INFO] Ya existe la transcripción en este proyecto. Saltando fase...")
        return

    # Buscar el audio mp3
    audio_file = os.path.join(project_folder, "video.mp3")
    if not os.path.exists(audio_file):
        print(f"Error: No se encontró el archivo de audio '{audio_file}'.")
        exit(1)

    print("Cargando modelo Whisper 'small'...")
    model = whisper.load_model("small")

    print("Transcribiendo el audio... (verás el progreso línea por línea)")
    # verbose=True hace que Whisper imprima los segmentos a medida que los procesa, sirviendo como indicador de progreso
    result = model.transcribe(audio_file, word_timestamps=True, verbose=True)

    output_file = os.path.join(project_folder, "extraccion.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        # SECCIÓN 1: TEXTO PLANO
        f.write("=== TEXTO COMPLETO ===\n\n")
        f.write(result["text"])
        f.write("\n\n" + "="*30 + "\n\n")

        # SECCIÓN 2: DESGLOSE POR PALABRAS (GRANULAR)
        f.write("=== DESGLOSE GRANULAR (PALABRA POR PALABRA) ===\n\n")
        
        for segment in result["segments"]:
            for word_info in segment.get("words", []):
                word = word_info["word"].strip()
                start = word_info["start"]
                end = word_info["end"]
                f.write(f"[{format_time(start)} --> {format_time(end)}] {word}\n")

    print(f"¡Transcripción guardada en '{output_file}'!")

# ==========================================
# FASE 3: EVALUACIÓN IA
# ==========================================
def fase_3_evaluar_ia(project_folder, force=False, min_sec=10, max_sec=50, solicitud_especial=""):
    print("\n--- FASE 3: EVALUACIÓN CON IA ---")
    
    from openai import OpenAI # Importación perezosa
    
    output_file = os.path.join(project_folder, "partes_poderosas.txt")
    if not force and os.path.exists(output_file):
        print("[INFO] La IA ya evaluó este video previamente. Saltando fase...")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No se encontró la variable de entorno OPENAI_API_KEY.")
        exit(1)

    MODELO = "gpt-5.4-mini" 
    client = OpenAI(api_key=api_key)

    input_file = os.path.join(project_folder, "extraccion.txt")
    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo '{input_file}'.")
        exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        contenido = f.read()

    partes = contenido.split("=== DESGLOSE GRANULAR (PALABRA POR PALABRA) ===")
    texto_completo = partes[0].replace("=== TEXTO COMPLETO ===", "").strip()
    granular = partes[1].strip() if len(partes) > 1 else ""

    print(f"Enviando transcripción a {MODELO}...")

    prompt = f"""
    Eres un experto editor de video para redes sociales (TikTok, Instagram Reels, Shorts).
    Tu tarea es analizar el siguiente texto de un video y extraer TODAS las partes "poderosas", inspiradoras o impactantes que puedas identificar.
    
    REGLAS ESTRICTAS:
    1. Cada segmento debe durar ENTRE {min_sec} Y {max_sec} SEGUNDOS. (No más, no menos).
    2. Debes copiar EXACTAMENTE los timestamps que aparecen en el 'DESGLOSE GRANULAR'.
    3. El formato de tiempo TIENE QUE SER EXACTAMENTE: HH:MM:SS,mmm (Ejemplo: 00:01:23,450). NUNCA añades ceros extra ni cambies el formato.
    4. El tiempo de fin siempre debe ser mayor al tiempo de inicio.
    5. El resultado debe ser EXCLUSIVAMENTE una lista con este formato:
    [HH:MM:SS,mmm --> HH:MM:SS,mmm] // frase_breve_explicativa
    
    TEXTO COMPLETO PARA CONTEXTO:
    {texto_completo}
    
    DESGLOSE GRANULAR (Usa esto para los tiempos):
    {granular}
    """

    if solicitud_especial:
        prompt += f"\nSOLICITUD ESPECIAL DEL USUARIO:\n{solicitud_especial}\n"

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Eres un asistente que identifica hooks y momentos poderosos en transcripciones de video."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        resultado_ia = response.choices[0].message.content.strip()

        output_file = os.path.join(project_folder, "partes_poderosas.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(resultado_ia)

        print("¡Análisis completado!")
        print(f"Momentos poderosos guardados en '{output_file}':\n")
        print(resultado_ia)

    except Exception as e:
        print(f"Error con la API de OpenAI: {e}")
        exit(1)

# ==========================================
# FASE 4: RECORTADOR
# ==========================================
def fase_4_recortar(project_folder):
    print("\n--- FASE 4: RECORTAR CLIPS ---")
    
    video_file = os.path.join(project_folder, "video.mp4")
    if not os.path.exists(video_file):
        print(f"Error: No se encontró el video origen '{video_file}'.")
        exit(1)
        
    partes_file = os.path.join(project_folder, "partes_poderosas.txt")
    if not os.path.exists(partes_file):
        print(f"Error: No se encontró '{partes_file}'.")
        exit(1)

    extraidos_folder = os.path.join(project_folder, 'extraidos')
    if not os.path.exists(extraidos_folder):
        os.makedirs(extraidos_folder)

    with open(partes_file, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    count = 0
    for i, linea in enumerate(lineas):
        match = re.search(r'\[(.*?) --> (.*?)\]', linea)
        if match:
            start_time = parse_timestamp(match.group(1).strip())
            end_time = parse_timestamp(match.group(2).strip())
            
            # Evitar error de FFmpeg si la IA alucinó y puso el inicio mayor al fin
            if start_time >= end_time:
                print(f"  -> Error IA: El tiempo de inicio ({start_time}) es mayor al fin ({end_time}). Clip {i+1} descartado.")
                continue
            
            explicacion = "clip"
            if "//" in linea:
                explicacion = linea.split("//")[1].strip()[:30]
                explicacion = re.sub(r'[^\w\s]', '', explicacion).replace(' ', '_')

            output_name = f"clip_{i+1:02d}_{explicacion}.mp4"
            output_path = os.path.join(extraidos_folder, output_name)

            print(f"Recortando Clip {i+1}: {start_time} a {end_time}...")
            
            command = [
                'ffmpeg', '-y',
                '-ss', start_time,
                '-to', end_time,
                '-i', video_file,
                '-c:v', 'libx264',
                '-crf', '18',
                '-c:a', 'aac',
                '-b:a', '192k',
                output_path
            ]

            try:
                subprocess.run(command, check=True, capture_output=True)
                print(f"  -> Guardado como '{output_name}'")
                count += 1
            except subprocess.CalledProcessError as e:
                print(f"  -> Error al recortar clip {i+1}: {e.stderr.decode()}")

    print(f"\n¡Proceso finalizado! Se han extraído {count} clips en '{extraidos_folder}'.")

# ==========================================
# MAIN APP FLOW
# ==========================================
def main():
    print("="*50)
    print(" CORTADOR DE VIDEOS AUTOMATIZADO CON IA ".center(50))
    print("="*50)

    url = input("\nIntroduce la URL del video de YouTube: ").strip()
    if not url:
        print("Error: No se introdujo ninguna URL.")
        return

    video_id = extraer_video_id(url)
    if not video_id:
        print("Error: No se pudo extraer el ID del video de la URL proporcionada.")
        return

    print(f"Video ID detectado: {video_id}")
    
    project_folder = os.path.join('proyectos', video_id)
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
        print(f"Carpeta del proyecto creada: {project_folder}")

    while True:
        print("\n" + "="*40)
        print(" MENÚ PRINCIPAL ".center(40))
        print("="*40)
        print("[1] Ejecutar Pipeline Completo (Automático)")
        print("[2] Forzar Fase 1: Descargar Video/Audio")
        print("[3] Forzar Fase 2: Transcribir (Whisper)")
        print("[4] Forzar Fase 3: Evaluación IA (Regenerar clips + Pedido Especial)")
        print("[5] Forzar Fase 4: Recortar Clips")
        print("[0] Salir")
        print("="*40)
        
        opcion = input("Selecciona una opción: ").strip()

        if opcion == '1':
            fase_1_descargar(url, project_folder)
            preguntar_continuar("Descarga")
            
            fase_2_transcribir(project_folder)
            preguntar_continuar("Transcripción")
            
            # Pedir duraciones y solicitud especial para la fase 3
            try:
                min_s = int(input("\nDuración MÍNIMA del clip (segundos) [10]: ") or "10")
                max_s = int(input("Duración MÁXIMA del clip (segundos) [50]: ") or "50")
                solicitud = input("¿Tienes alguna solicitud especial para la IA? (opcional): ").strip()
            except ValueError:
                print("Valor no válido, usando por defecto 10-50s.")
                min_s, max_s = 10, 50
                solicitud = ""
                
            fase_3_evaluar_ia(project_folder, min_sec=min_s, max_sec=max_s, solicitud_especial=solicitud)
            preguntar_continuar("Evaluación IA")
            fase_4_recortar(project_folder)
            print("\n" + "="*50)
            print(" PIPELINE COMPLETADO EXITOSAMENTE ".center(50))
            print("="*50)
            break
        elif opcion == '2':
            fase_1_descargar(url, project_folder, force=True)
        elif opcion == '3':
            fase_2_transcribir(project_folder, force=True)
        elif opcion == '4':
            try:
                min_s = int(input("\nDuración MÍNIMA del clip (segundos) [10]: ") or "10")
                max_s = int(input("Duración MÁXIMA del clip (segundos) [50]: ") or "50")
                solicitud = input("¿Tienes alguna solicitud especial para la IA? (opcional): ").strip()
            except ValueError:
                print("Valor no válido, usando por defecto 10-50s.")
                min_s, max_s = 10, 50
                solicitud = ""
            fase_3_evaluar_ia(project_folder, force=True, min_sec=min_s, max_sec=max_s, solicitud_especial=solicitud)
        elif opcion == '5':
            fase_4_recortar(project_folder)
        elif opcion == '0':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()
