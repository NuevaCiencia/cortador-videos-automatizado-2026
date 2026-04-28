import whisper
import os
import glob
import json

def format_time(seconds):
    """Convierte segundos a formato HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def extraer_texto():
    folder = 'descargados'
    
    # 1. Buscar el audio más reciente
    files = glob.glob(os.path.join(folder, "*.mp3"))
    if not files:
        print("Error: No se encontraron archivos MP3 en la carpeta 'descargados'.")
        return

    latest_audio = max(files, key=os.path.getctime)
    print(f"Procesando: {os.path.basename(latest_audio)}...")

    # 2. Cargar modelo (usamos 'small' para balance velocidad/precisión)
    print("Cargando modelo Whisper (esto puede tardar la primera vez)...")
    model = whisper.load_model("small")

    # 3. Transcribir con timestamps a nivel de palabra
    print("Transcribiendo... (esto depende de la duración del audio)")
    result = model.transcribe(latest_audio, word_timestamps=True)

    # 4. Generar el archivo de salida
    output_file = "extraccion.txt"
    
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

    print(f"\n¡Listo! El texto se ha guardado en: {output_file}")

if __name__ == "__main__":
    extraer_texto()
