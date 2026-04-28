# Cortador de Videos Automatizado con IA 🎬🤖

Este proyecto es una herramienta avanzada para creadores de contenido que permite transformar videos largos de YouTube en clips virales (Shorts, Reels, TikTok) de forma 100% automatizada utilizando Inteligencia Artificial.

## ¿Qué hace exactamente?

El sistema unifica todo el proceso de edición en un solo lugar:
1. **Descarga**: Obtiene el video (MP4) y audio (MP3) de YouTube en la mejor calidad.
2. **Transcripción**: Genera un texto palabra por palabra con tiempos exactos usando **OpenAI Whisper**.
3. **Análisis con IA**: Envía la transcripción a **GPT-5.4-mini** para identificar los momentos más impactantes basándose en tus preferencias.
4. **Recorte de Precisión**: Extrae los clips automáticamente usando **FFmpeg**, asegurando que cada video sea independiente y visualmente perfecto.

---

## 🛠️ Requisitos Previos

1. **FFmpeg**: Necesario para el procesamiento de video.
   - **Mac**: `brew install ffmpeg`
   - **Windows**: `winget install ffmpeg` o descarga desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. **OpenAI API Key**: Configúrala en tu sistema como una variable de entorno:
   - `OPENAI_API_KEY=tu_clave_aqui`

---

## 🚀 Instalación y Entorno Virtual

Se recomienda usar un entorno virtual para mantener las dependencias aisladas.

### En Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### En macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 💻 Manual de Uso Interactivo

Para iniciar el sistema, ejecuta:
```bash
python app.py
```

### 1. Inicio y Proyecto
Al iniciar, el programa te pedirá la **URL de YouTube**. Automáticamente extraerá el ID del video y creará una carpeta en `proyectos/{ID_DEL_VIDEO}/` para mantener todo ordenado.

### 2. El Menú Principal
El sistema cuenta con un menú inteligente que te da control total:
*   **[1] Ejecutar Pipeline Completo**: El modo automático. Detecta si ya existen archivos (como la descarga o transcripción) y se los salta para ahorrarte tiempo.
*   **[2-4] Forzar Fases**: Si algo salió mal en una fase específica (ej. quieres que la IA analice el video de nuevo), puedes usar estas opciones para sobrescribir los archivos antiguos.
*   **[5] Recortar Clips**: Ejecuta el motor de edición sobre la última lista de momentos generada.

### 3. Personalización de Clips
Al llegar a la fase de IA, el sistema te pedirá tres parámetros clave:
1. **Duración Mínima**: (Ej. 15s) Evita clips demasiado cortos.
2. **Duración Máxima**: (Ej. 60s) Asegura que el contenido sea dinámico.
3. **Solicitud Especial**: Aquí puedes hablar con la IA. Ejemplo: *"Busca solo los momentos más graciosos"*, *"Prioriza cuando se hable de motivación"* o *"Ignora la parte del patrocinador"*.

---

## 📂 Estructura de Archivos

Cada video genera su propia "isla" de archivos:
```text
proyectos/
└── {ID_VIDEO}/
    ├── video.mp4          # Fuente original
    ├── video.mp3          # Audio para la IA
    ├── extraccion.txt     # Transcripción completa
    ├── partes_poderosas.txt # La lista de "tesoros" encontrados por la IA
    └── extraidos/         # ¡Tus clips finales listos para subir!
```

---

## ⚡ Optimización
El sistema usa **Lazy Loading** (carga perezosa). La aplicación abre instantáneamente y solo carga los motores pesados de IA (Whisper) cuando realmente vas a realizar una transcripción, ahorrando memoria y tiempo.
