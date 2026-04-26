#====================================
#MODULO: llm_mistral.py
#Implementación del LLM MIstral con:
# - Definición de rol
# - tools que puede "usar"
# - función enviar_pregunta
# -  memoria de contexto
# - reinicio de memoria contextual
#===================================


import ollama
from especificaciones_tools_propias import TOOLS_PROPIAS
from especificaciones_tools_externas import TOOLS_EXTERNAS
from especificaciones_tools_graficas import TOOLS_GRAFICAS

# Combinamos las herramientas en una sola lista
TODAS_LAS_TOOLS = TOOLS_PROPIAS + TOOLS_EXTERNAS + TOOLS_GRAFICAS

# Nuestra "memoria" en formato lista (muy fácil de depurar con un print)
historial_mensajes = [
    {
        "role": "system", 
        "content": (
            "Eres un agente ejecutor de FatMaxLab. REGLA DE ORO: Si necesitas datos externos, "
            "USA UNA HERRAMIENTA inmediatamente. NO expliques cómo usarla, NO pongas ejemplos "
            "en Markdown, y NO digas 'puedes usar...'. Simplemente emite la llamada técnica. "
            "Tu respuesta DEBE ser una llamada a función si no tienes los datos."
        )
    }
]

def enviar_pregunta(texto_usuario):
    """Manda la pregunta a Mistral y nos dice si quiere hablar o actuar."""
    historial_mensajes.append({"role": "user", "content": texto_usuario})
    
    respuesta = ollama.chat(
        model="mistral",
        messages=historial_mensajes,
        tools=TODAS_LAS_TOOLS,
        options={"temperature": 0.1} # <--- Esto la hace más precisa

    )
    
    # Extraemos el mensaje para no escribir tanto código después
    mensaje = respuesta['message']
    
    # Caso A: Mistral quiere usar una herramienta (Patrón detectado)
    if mensaje.get('tool_calls'):
        return "ACCION", mensaje['tool_calls']
    
    # Caso B: Mistral solo quiere responder con texto
    historial_mensajes.append(mensaje)
    return "RESPUESTA", mensaje['content']

def reiniciar_memoria():
    """Limpia el historial por si Mistral se marea con tantos datos."""
    global historial_mensajes
    historial_mensajes = [historial_mensajes[0]] # Mantenemos solo el sistema