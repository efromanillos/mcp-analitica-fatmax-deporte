#========================================
#MODULO: app.py
#Implementación de la interfaz de usuario
#========================================

import streamlit as st
import llm_mistral
import geoclima_tools
import deporte_tools
# Importamos las herramientas para poder llamarlas dinámicamente
import json


# 1. Definimos el diccionario de herramientas 
DICCIONARIO_TOOLS = {
    "obtener_clima_local": geoclima_tools.obtener_clima_local,
    "obtener_ubicacion_automatica": geoclima_tools.obtener_ubicacion_automatica,
    "procesar_sesion_entrenamiento_completo": deporte_tools.procesar_sesion_entrenamiento_completo
}


st.set_page_config(page_title="FatMaxLab", page_icon="🚴‍♂️")

st.title("🚴‍♂️ FatMaxLab: Análisis de Entrenamientos a través de IA y Redes Neuronales")
st.markdown("---")

# 1. INICIALIZACIÓN DEL ESTADO (Memoria de Streamlit)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. BARRA LATERAL
with st.sidebar:
    st.header("Configuración")
    if st.button("Reiniciar Laboratorio"):
        llm_mistral.reiniciar_memoria()
        st.session_state.messages = []
        st.rerun()
    st.info("Sube tus archivos .fit o pregunta por el clima de tu ruta.")

# 3. MOSTRAR HISTORIAL EN PANTALLA
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. BUCLE PRINCIPAL DE INTERACCIÓN
# ... (tus imports y DICCIONARIO_TOOLS están perfectos)

if prompt := st.chat_input("¿Cómo estuvo mi entrenamiento hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Interpretando patrones..."):
            # 1. Llamada al cerebro
            tipo, contenido = llm_mistral.enviar_pregunta(prompt)
            
            # --- INTERCEPTOR DE SEGURIDAD ---
            if tipo == "RESPUESTA":
                if "obtener_ubicacion_automatica" in contenido:
                    tipo = "ACCION"
                    contenido = [{'function': {'name': 'obtener_ubicacion_automatica', 'arguments': {}}}]
                elif "obtener_clima_local" in contenido:
                    tipo = "ACCION"
                    contenido = [{'function': {'name': 'obtener_clima_local', 'arguments': {'lat': 40.41, 'lon': -3.70}}}]

            print(f"DEBUG - Tipo final: {tipo}") 
            
            if tipo == "ACCION":
                for tool_call in contenido:
                    nombre_func = tool_call['function']['name']
                    args = tool_call['function']['arguments']
        
                    st.caption(f"🔧 Ejecutando: {nombre_func}...")
        
                    # EJECUCIÓN DINÁMICA (Dentro del bucle for)
                    if nombre_func in DICCIONARIO_TOOLS:
                        res = DICCIONARIO_TOOLS[nombre_func](**args)
                    else:
                        res = {"error": f"La herramienta '{nombre_func}' no está registrada."}

                    # El cable de retorno (Dentro del bucle for)
                    prompt_retorno = f"El resultado de {nombre_func} es: {json.dumps(res)}. Responde al usuario con naturalidad."
                    _, respuesta_final = llm_mistral.enviar_pregunta(prompt_retorno)
                    
                    st.markdown(respuesta_final)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
            
            else:
                st.markdown(contenido)
                st.session_state.messages.append({"role": "assistant", "content": contenido})