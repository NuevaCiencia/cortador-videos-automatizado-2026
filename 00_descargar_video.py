import yt_dlp
import os

def descargar_video():
    # Asegurarse de que la carpeta de descargas exista
    output_folder = 'descargados'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Solicitar la URL al usuario
    url = input("Introduce la URL del video de YouTube: ").strip()
    
    if not url:
        print("Error: No se ha introducido ninguna URL.")
        return

    # Opciones para yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
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

    print(f"\nIniciando descarga en la carpeta '{output_folder}'...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n¡Descarga completada con éxito!")
    except Exception as e:
        print(f"\nOcurrió un error durante la descarga: {e}")

if __name__ == "__main__":
    descargar_video()
