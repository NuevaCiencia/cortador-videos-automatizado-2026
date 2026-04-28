import os
from openai import OpenAI
import re

def evaluador_ia():
    # 1. Configurar cliente de OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No se encontró la variable de entorno OPENAI_API_KEY.")
        return

    # Usamos el nombre de modelo solicitado (ajustar si es necesario a 'gpt-4o-mini')
    MODELO = "gpt-5.4-mini" 
    client = OpenAI(api_key=api_key)

    # 2. Leer el archivo de extracción
    if not os.path.exists("extraccion.txt"):
        print("Error: No se encuentra el archivo 'extraccion.txt'. Ejecuta 01_extraer_texto.py primero.")
        return

    with open("extraccion.txt", "r", encoding="utf-8") as f:
        contenido = f.read()

    # Separamos el texto completo del desglose granular para dar contexto a la IA
    partes = contenido.split("=== DESGLOSE GRANULAR (PALABRA POR PALABRA) ===")
    texto_completo = partes[0].replace("=== TEXTO COMPLETO ===", "").strip()
    granular = partes[1].strip() if len(partes) > 1 else ""

    print(f"Enviando texto a la IA ({MODELO}). Analizando momentos poderosos...")

    # 3. Prompt para la IA
    prompt = f"""
    Eres un experto editor de video para redes sociales (TikTok, Instagram Reels, Shorts).
    Tu tarea es analizar el siguiente texto de un video y encontrar los 3-5 momentos más "poderosos", inspiradores o impactantes.
    
    REGLAS:
    1. Cada segmento debe durar máximo 30 segundos.
    2. Debes usar los timestamps exactos del 'DESGLOSE GRANULAR' para marcar el inicio y el fin.
    3. El resultado debe ser EXCLUSIVAMENTE una lista con este formato:
    [tiempo_inicio --> tiempo_fin] // frase_breve_explicativa
    
    TEXTO COMPLETO PARA CONTEXTO:
    {texto_completo}
    
    DESGLOSE GRANULAR (Usa esto para los tiempos):
    {granular}
    """

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

        # 4. Guardar en partes_poderosas.txt
        with open("partes_poderosas.txt", "w", encoding="utf-8") as f:
            f.write(resultado_ia)

        print("\n¡Análisis completado!")
        print(f"Los momentos poderosos se han guardado en: partes_poderosas.txt")
        print("\nContenido extraído:")
        print(resultado_ia)

    except Exception as e:
        print(f"\nOcurrió un error con la API de OpenAI: {e}")
        if "model_not_found" in str(e):
            print("TIP: El modelo 'gpt-5.4-mini' parece no existir aún. Intenta cambiarlo por 'gpt-4o-mini' en el script.")

if __name__ == "__main__":
    evaluador_ia()
