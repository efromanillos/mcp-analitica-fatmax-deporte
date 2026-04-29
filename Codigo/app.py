#========================================
# MODULO: app.py
# Implementación de la interfaz de usuario simplificada para Mistral-Nemo
#========================================

import streamlit as st
import llm_mistral
import geoclima_tools
import deporte_tools
import json
import datetime

# 1. DEFINICIÓN DEL DICCIONARIO DE HERRAMIENTAS
# Centralizamos las funciones para que el bucle de ejecución sea limpio.
DICCIONARIO_HERRAMIENTAS = {
    "obtener_clima_local": geoclima_tools.obtener_clima_local,
    "obtener_ubicacion_automatica": geoclima_tools.obtener_ubicacion_automatica,
    "procesar_sesion_entrenamiento_completo": deporte_tools.procesar_sesion_entrenamiento_completo,
    "calcular_zonas_entrenamiento": deporte_tools.calcular_zonas_entrenamiento
}

# Configuración de la página
st.set_page_config(page_title="FatMaxLab", page_icon="🚴‍♂️")

st.title("🚴‍♂️ FatMaxLab: Análisis de Entrenamientos a través de IA y Redes Neuronales")
st.markdown("---")

# 2. INICIALIZACIÓN DEL ESTADO (Memoria de Streamlit) 
# NOTA. Cada vez que se ejecuta en Streamlit algo, se resetea todo (re-run), para que entre reseteos la información
# previa permanezca, se usa session_state como memoria de sesion
# (si no Streamlit olvidaría los mensajes del chat, los datos calculados, etc.)

# Con el if se controla que la lista 'historial_mensajes' se cree una vez al principio de cada sesión
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# 3. BARRA LATERAL
with st.sidebar:
    st.header("Configuración")
    if st.button("Reiniciar Laboratorio"):
        llm_mistral.reiniciar_memoria()
        st.session_state.historial_mensajes = []
        st.rerun()
    st.info("Utiliza Mistral-Nemo para analizar tu entrenamiento y el clima actual.")

# 4. MOSTRAR HISTORIAL EN PANTALLA
for mensaje in st.session_state.historial_mensajes:
    # FILTRO: Solo mostramos si el contenido es una cadena de texto (str)
    # Esto evita que los objetos técnicos de la IA (JSON/ToolCalls) ensucien el chat
    if isinstance(mensaje["contenido"], str):
        with st.chat_message(mensaje["role"]): # Usamos 'role' para que Streamlit reconozca el icono
            st.markdown(mensaje["contenido"])

# 5. BUCLE PRINCIPAL DE INTERACCIÓN (SISTEMA NATIVO)
if entrada_usuario := st.chat_input("¿Cómo estuvo mi entrenamiento hoy?"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.historial_mensajes.append({"role": "user", "contenido": entrada_usuario})
    with st.chat_message("user"):
        st.markdown(entrada_usuario)

    with st.chat_message("assistant"):
        with st.spinner("El cerebro de la IA está procesando los patrones..."):
            
            # --- EL CORAZÓN DEL FLUJO ---
            # 'indicador_respuesta' nos da la señal: ¿Es texto o es una acción?
            # 'datos_respuesta' contiene el mensaje o la lista de herramientas
            indicador_respuesta, datos_respuesta = llm_mistral.enviar_pregunta(entrada_usuario)
            
            if indicador_respuesta == "ACCION":
                # El modelo ha decidido usar una o varias herramientas
                for llamada_herramienta in datos_respuesta:
                    nombre_funcion = llamada_herramienta['function']['name']
                    argumentos = llamada_herramienta['function']['arguments']
        
                    st.caption(f"🔧 Ejecutando herramienta nativa: {nombre_funcion}...")
        
                    # Ejecución dinámica y segura
                    if nombre_funcion in DICCIONARIO_HERRAMIENTAS:
                        try:
                            # Los argumentos fluyen directamente desde el JSON del LLM
                            # NOTA: Los dos ** es el desempaquetado de diccionarios que hace Python, obtiene los valores de las claves
                            resultado_tecnico = DICCIONARIO_HERRAMIENTAS[nombre_funcion](**argumentos) 
                        except Exception as error_ejecucion:
                            resultado_tecnico = {"error": f"Error en la ejecución: {str(error_ejecucion)}"}
                    else:
                        resultado_tecnico = {"error": f"La herramienta '{nombre_funcion}' no está registrada en el sistema."}

                    # EL CABLE DE RETORNO: Inyectamos resultado_tecnico tras la ejecución de la función a mistral-nemo
                    # Esto es clave, porque es cuando el modelo recupera la salida de las funciones que ha pedido ejecutar 
                    # a Python (function calling)
                    #Le pasamos al modelo la hora actual para que responda el clima acorde al momento del día (diurno, nocturno)
                    
                    ahora_dt = datetime.datetime.now()
                    ahora = ahora_dt.strftime("%H:%M")
                    periodo = "MAÑANA (AM)" if ahora_dt.hour < 12 else "TARDE/NOCHE (PM)"

                    contexto_retorno = (
                        f"Resultado de la herramienta {nombre_funcion}: {json.dumps(resultado_tecnico)}. "
                        f"Hora actual en el laboratorio: {ahora} ({periodo}). "
                        "Explica estos datos al usuario de forma clara y técnica. "
                        "Sintetiza la info y da una recomendación de entrenamiento coherente con la hora y el clima."
                        "REGLA DE MEMORIA: Antes de pedir un dato al usuario (como FC_max o reposo), "
                        "revisa el historial de arriba. Si ya te los ha dado, NO los vuelvas a pedir, "
                        "utilízalos directamente para tus conclusiones."
                    )
                    

                    _, explicacion_final = llm_mistral.enviar_pregunta(contexto_retorno)
                    
                    st.markdown(explicacion_final)
                    # Guardamos la respuesta final en el historial
                    st.session_state.historial_mensajes.append({"role": "assistant", "contenido": explicacion_final})
            
            else:
                # Si el indicador es "RESPUESTA", mostramos el texto directamente
                st.markdown(datos_respuesta)
                st.session_state.historial_mensajes.append({"role": "assistant", "contenido": datos_respuesta})

    # Forzamos refresco final para asentar el estado y evitar parpadeos de re-run
    st.rerun()