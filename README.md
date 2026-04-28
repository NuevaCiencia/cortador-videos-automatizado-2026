# Cortador de Videos Automatizado con IA 🎬🤖

Este proyecto es una herramienta automatizada para creadores de contenido (YouTubers, TikTokers, Instagramers). Te permite introducir la URL de un video de YouTube y, utilizando Inteligencia Artificial, identificar los momentos más "poderosos" o virales del video para recortarlos automáticamente y tenerlos listos para subir a Shorts, Reels o TikTok.

## ¿Qué hace exactamente?

El sistema funciona a través de un *pipeline* interactivo de 4 fases:
1. **Descarga**: Obtiene el video en la máxima calidad disponible (MP4) y extrae una copia del audio (MP3) de YouTube.
2. **Transcripción**: Utiliza OpenAI Whisper (procesamiento local) para generar una transcripción granular, palabra por palabra, con tiempos exactos (*timestamps*).
3. **Evaluación IA**: Envía la transcripción a la API de OpenAI (GPT-5.4-mini o GPT-4o-mini) para que un "editor experto" seleccione los 3-5 mejores momentos que duren menos de 30 segundos.
4. **Recorte**: Usa FFmpeg para recortar esos momentos del video original en alta calidad y sin pérdida.

Todo se organiza automáticamente en carpetas separadas por el ID del video de YouTube.

---

## 🛠️ Requisitos Previos

Antes de instalar Python, necesitas dos cosas fundamentales en tu sistema:

1. **FFmpeg**: Es el motor de procesamiento de video.
   - **Mac**: Instálalo usando Homebrew: `brew install ffmpeg`
   - **Windows**: Descárgalo desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) o usa Winget: `winget install ffmpeg`
2. **OpenAI API Key**: Necesitas una clave de API de OpenAI con saldo disponible.
   - Debes configurarla como variable de entorno llamada `OPENAI_API_KEY`.

---

## 🚀 Instalación y Entorno Virtual

Se recomienda encarecidamente utilizar un **entorno virtual** para instalar las dependencias y no afectar tu sistema principal.

### En Windows (PC)

1. Abre tu terminal (PowerShell o CMD) y navega a la carpeta del proyecto.
2. Crea el entorno virtual:
   ```powershell
   python -m venv venv
   ```
3. Activa el entorno virtual:
   ```powershell
   .\venv\Scripts\activate
   ```
   *(Si te da error de permisos en PowerShell, ejecuta primero: `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`)*
4. Instala las dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

### En macOS / Linux

1. Abre tu Terminal y navega a la carpeta del proyecto.
2. Crea el entorno virtual:
   ```bash
   python3 -m venv venv
   ```
3. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Cómo Usarlo

Una vez que tengas tu entorno virtual activado y tu clave de API configurada, simplemente ejecuta la aplicación principal:

**En Windows:**
```powershell
python app.py
```

**En Mac:**
```bash
python3 app.py
```

### El proceso paso a paso:
1. **Pega la URL**: El programa te pedirá que pegues el link de YouTube.
2. **Carpetas**: Se creará automáticamente una carpeta en `proyectos/{ID_DEL_VIDEO}`.
3. **Flujo Interactivo**: El programa hará una fase (ej. descargar) y se pausará preguntando: `¿Deseas continuar con la siguiente fase? (s/n)`. Presiona `s` y Enter para continuar.
4. **Resultados**: Al finalizar, entra en `proyectos/{ID_DEL_VIDEO}/extraidos/` y ahí estarán tus clips en formato `.mp4`, listos para publicar.

---

## 📂 Estructura del Proyecto Generado

Cuando procesas un video, el programa organiza todo así:

```text
proyectos/
└── QNDbqKYFOeQ/                    # ID único del video
    ├── video.mp4                   # Video original completo
    ├── video.mp3                   # Audio original
    ├── extraccion.txt              # Transcripción completa y granular
    ├── partes_poderosas.txt        # Análisis de la IA con los recortes
    └── extraidos/                  # ¡Tus clips finales!
        ├── clip_01_explicacion.mp4
        └── clip_02_explicacion.mp4
```

> **Nota**: La primera vez que ejecutes el paso de transcripción, Whisper descargará un modelo de IA (aprox 460MB). Las siguientes veces no lo hará.
