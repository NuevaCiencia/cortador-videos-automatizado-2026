import os
import subprocess
import glob
import re

def parse_timestamp(ts):
    """Convierte HH:MM:SS,mmm a HH:MM:SS.mmm para FFmpeg"""
    return ts.replace(',', '.')

def recortador():
    input_folder = 'descargados'
    output_folder = 'extraidos'
    
    # 1. Crear carpeta de salida
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Buscar el video más reciente
    video_files = glob.glob(os.path.join(input_folder, "*.mp4"))
    if not video_files:
        print("Error: No se encontraron videos MP4 en 'descargados'.")
        return
    
    latest_video = max(video_files, key=os.path.getctime)
    video_name = os.path.basename(latest_video)
    print(f"Video origen detectado: {video_name}")

    # 3. Leer partes poderosas
    if not os.path.exists("partes_poderosas.txt"):
        print("Error: No se encuentra 'partes_poderosas.txt'. Ejecuta 02_evaluador_ia.py primero.")
        return

    with open("partes_poderosas.txt", "r", encoding="utf-8") as f:
        lineas = f.readlines()

    count = 0
    for i, linea in enumerate(lineas):
        # Buscar patrón: [00:00:00,000 --> 00:00:00,000]
        match = re.search(r'\[(.*?) --> (.*?)\]', linea)
        if match:
            start_time = parse_timestamp(match.group(1).strip())
            end_time = parse_timestamp(match.group(2).strip())
            
            # Limpiar el nombre del clip (usar parte de la explicación si existe)
            explicacion = "clip"
            if "//" in linea:
                explicacion = linea.split("//")[1].strip()[:30] # Primeros 30 caracteres
                explicacion = re.sub(r'[^\w\s]', '', explicacion).replace(' ', '_') # Limpiar caracteres raros

            output_name = f"clip_{i+1:02d}_{explicacion}.mp4"
            output_path = os.path.join(output_folder, output_name)

            print(f"\nRecortando Clip {i+1}: {start_time} a {end_time}...")
            
            # Comando FFmpeg para recortar re-codificando (garantiza visibilidad desde el segundo 0)
            command = [
                'ffmpeg', '-y',
                '-ss', start_time,
                '-to', end_time,
                '-i', latest_video,
                '-c:v', 'libx264', # Codec de video estándar
                '-crf', '18',      # Alta calidad (menor número = mejor calidad, 18-23 es ideal)
                '-c:a', 'aac',     # Codec de audio estándar
                '-b:a', '192k',    # Calidad de audio
                output_path
            ]

            try:
                subprocess.run(command, check=True, capture_output=True)
                print(f"¡Guardado! -> {output_name}")
                count += 1
            except subprocess.CalledProcessError as e:
                print(f"Error al recortar clip {i+1}: {e.stderr.decode()}")

    print(f"\nProceso finalizado. Se han extraído {count} clips en la carpeta '{output_folder}'.")

if __name__ == "__main__":
    recortador()
