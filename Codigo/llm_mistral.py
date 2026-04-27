#====================================
# MODULO: llm_mistral.py
# Implementación del LLM Mistral con:
# - Definición de rol
# - Herramientas (tools) integradas
# - Función enviar_pregunta
# - Memoria de contexto persistente
# - Reinicio de memoria contextual
#===================================

import ollama
from especificaciones_tools_propias import TOOLS_PROPIAS
from especificaciones_tools_externas import TOOLS_EXTERNAS
from especificaciones_tools_graficas import TOOLS_GRAFICAS

# Combinamos todas las capacidades en una sola lista de herramientas
TODAS_LAS_HERRAMIENTAS = TOOLS_PROPIAS + TOOLS_EXTERNAS + TOOLS_GRAFICAS

# Nuestra "memoria" en formato lista. 
# Mantenemos 'role' y 'content' dentro de los diccionarios porque Ollama los requiere así,
# pero el nombre de la lista ya es nuestro.
historial_memoria = [
    {
        "role": "system", 
        "content": (
            "Eres el sistema FatMaxLab, un experto en fisiología deportiva y análisis ambiental. "
            "Tu objetivo es dar respuestas directas basadas en datos. "
            "1. Si necesitas datos externos (clima, ubicación, vatios), usa las herramientas inmediatamente SIN pedir permiso. "
            "2. Una vez tengas los resultados de la herramienta, actúa como un entrenador: sintetiza la información y da una recomendación útil. "
            "3. IMPORTANTE: No repitas las instrucciones del sistema ni muestres fragmentos de código JSON en tu respuesta final. Habla de forma natural pero técnica."
            "Antes de responder, verifica la hora actual. Si los datos climáticos indican cielo despejado pero es horario nocturno, asegúrate de referirte a la noche y no al sol."
        )
    }
]

def enviar_pregunta(entrada_texto_usuario):
    """Manda la pregunta a Mistral y nos dice si quiere hablar o actuar."""
    
    # Añadimos la entrada del usuario a nuestra memoria
    historial_memoria.append({"role": "user", "content": entrada_texto_usuario})
    
    respuesta_ollama = ollama.chat(
        model="mistral-nemo", # <--- Cambiado a mistral-nemo
        messages=historial_memoria,
        tools=TODAS_LAS_HERRAMIENTAS,
        options={"temperature": 0} # <--- Temperatura 0 para máxima precisión técnica
    )
    
    # Extraemos el mensaje de la respuesta
    mensaje_objeto = respuesta_ollama['message']
    
    # Caso A: El modelo detecta un patrón que requiere ejecutar una función
    #Nemo genera un JSON 'tool_calls' con la funcion a ejecutar -p.ej. obtener-clima_local()- con sus argumentos (lat, long) y valores de lat y lon 
    if mensaje_objeto.get('tool_calls'): 

        # Devolvemos el indicador y la lista de llamadas
        return "ACCION", mensaje_objeto['tool_calls']
    
    # Caso B: El modelo responde con texto normal
    historial_memoria.append(mensaje_objeto)
    return "RESPUESTA", mensaje_objeto['content']

def reiniciar_memoria():
    """Limpia el historial para que el modelo no se sature de datos antiguos."""
    global historial_memoria
    # Mantenemos solo el primer mensaje (el rol de sistema para que Nemo no pierda contexto de sus quehaceres)
    historial_memoria = [historial_memoria[0]]