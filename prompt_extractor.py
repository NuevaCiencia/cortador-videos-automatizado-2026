def obtener_prompt_mapa(texto_completo, solicitud_especial=""):
    return f"""
    Analiza el siguiente texto de una entrevista y divídelo en "Unidades Temáticas Coherentes".
    Un hilo narrativo debe tener un inicio, un desarrollo y una conclusión lógica sobre un tema específico.
    Enfócate en que el mensaje sea completo y tenga sentido por sí mismo.
    
    TEXTO COMPLETO:
    {texto_completo}
    
    SOLICITUD ESPECIAL DEL USUARIO:
    {solicitud_especial}
    
    Responde con la lista de temas en formato:
    [min_inicio:seg --> min_fin:seg] - Título del hilo narrativo
    """

def obtener_prompt_final(mapa_bloques, granular, solicitud_especial=""):
    return f"""
    Eres un editor de video experto. Basándote en estos "Hilos Narrativos":
    {mapa_bloques}
    
    Tu tarea es extraer los clips EXACTOS para cada uno de esos temas. 
    Asegúrate de que el clip comience justo cuando empieza la idea y termine exactamente cuando la idea se cierra de forma coherente.
    
    REGLAS DE ORO:
    1. El clip debe ser un mensaje completo. No lo cortes a mitad de una frase.
    2. Usa los tiempos EXACTOS del 'DESGLOSE GRANULAR'.
    3. El formato debe ser: [HH:MM:SS,mmm --> HH:MM:SS,mmm] // Título del tema
    
    SOLICITUD ESPECIAL DEL USUARIO:
    {solicitud_especial}
    
    DESGLOSE GRANULAR (Usa esto para los tiempos finales):
    {granular}
    """
