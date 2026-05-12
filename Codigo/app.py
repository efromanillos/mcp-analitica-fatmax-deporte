#========================================
# MODULO: app.py
# Implementación de la interfaz de usuario simplificada para Mistral-Nemo
#========================================

import streamlit as st
import llm_mistral
import geoclima_tools
import deporte_tools
import graficas_tools
import json
import datetime
import os  # Necesario para el manejo físico de archivos en el puente
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Esto evita errores de hilos (threads) en servidores web


# 0. CONFIGURACIÓN DE LA PÁGINA
# Usamos layout="wide" para que las 3 columnas centrales tengan espacio suficiente
st.set_page_config(page_title="FatMaxLab", page_icon="🚴‍♂️", layout="wide")

#Título principal, cabecera de la página
st.title("🚴‍♂️ FatMaxLab: Análisis de Entrenamientos a través de IA y Redes Neuronales")
st.markdown("---")

# Definimos las 3 columnas con pesos proporcionales: 1 + 2 + 3 = 6,  la columna 1 ocupa 1/6, la segunda 2/6...
col_estado, col_nemo, col_graficas = st.columns([1, 2, 3])


# --- Envoltorios (WRAPPERS) PARA REDIRIGIR LAS GRÁFICAS A LA COLUMNA 3 ---
def envoltorio_graficar_grasas(lista_grasas):
    # 1. Generamos la figura
    fig = graficas_tools.graficar_oxidacion_grasas(lista_grasas)
    
    # 2. La guardamos en el estado
    st.session_state.figura_grasas = fig
    
    # 3. FORZAMOS el refresco para que aparezca en la columna 3
    st.rerun() 
    return "Gráfica de oxidación de grasas generada y visible en el panel derecho."

def envoltorio_graficar_vo2(lista_vo2):
    fig = graficas_tools.graficar_vo2(lista_vo2)
    st.session_state.figura_vo2 = fig
    st.rerun()
    return "Gráfica de VO2 generada y visible en el panel derecho."

# 1. DEFINICIÓN DEL DICCIONARIO DE HERRAMIENTAS
# Centralizamos las funciones para que el bucle de ejecución sea limpio.

DICCIONARIO_HERRAMIENTAS = {
    "obtener_clima_local": geoclima_tools.obtener_clima_local,
    "obtener_ubicacion_automatica": geoclima_tools.obtener_ubicacion_automatica,
    "procesar_sesion_entrenamiento_completo": deporte_tools.procesar_sesion_entrenamiento_completo,
    "calcular_zonas_entrenamiento": deporte_tools.calcular_zonas_entrenamiento,
    
    # Usamos los wrappers en lugar de las funciones directas
    "graficar_oxidacion_grasas": envoltorio_graficar_grasas,
    "graficar_vo2": envoltorio_graficar_vo2
}


# 2. INICIALIZACIÓN DEL ESTADO (Memoria de Streamlit) 
# NOTA. Cada vez que se ejecuta en Streamlit algo, se resetea todo (re-run): para que entre reseteos la información
# previa permanezca, se usa session_state como memoria de sesion
# (si no Streamlit olvidaría los mensajes del chat, los datos calculados, etc.)

# Con el if se controla que la lista 'historial_mensajes' se cree una vez al principio de cada sesión y no en cada re-run
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []
# 'datos_usr' contiene los resultados procesados de la actividad física del usuario
if "datos_usr" not in st.session_state:
    st.session_state.datos_usr = None
# Control de archivos para evitar notificaciones duplicadas en el historial
if "ultimo_archivo_notificado" not in st.session_state:
    st.session_state.ultimo_archivo_notificado = None

if "figura_grasas" not in st.session_state:
    st.session_state.figura_grasas = None
if "figura_vo2" not in st.session_state:
    st.session_state.figura_vo2 = None

#-----------------------------------------------------------------------------------------------------


# =========================================================
# ZONA 1: PANEL DE CONTROL (SIDEBAR)
# =========================================================
with st.sidebar:
    st.title("⚙️ Configuración")

    # Selector de Tema (Simulado con CSS o nativo de Streamlit)
    modo_oscuro = st.toggle("Modo Oscuro", value=True)
    
    st.divider()
    
    # Uploader de Modelo y Datos
    # NOTA: los uploader devuelven el archivo completo en memoria (un buffer con los bytes del archivo), no la ruta al archivo que se sube
    st.subheader("📁 Gestión de Archivos")
    archivo_h5 = st.file_uploader("Modelo RN (.h5) [Carpeta: datos_entrenamiento_rn]", type=["h5"])
    archivo_fit = st.file_uploader("Sesión Garmin (.fit) [Carpeta: datos_usr]", type=["fit"])
    
    # --- LÓGICA DEL PUENTE DE ARCHIVOS ---
    # Si el usuario sube un archivo, lo guardamos físicamente para que Nemo tenga una ruta real que procesar
    if archivo_fit is not None:
        ruta_directorio = "datos_usr"
        if not os.path.exists(ruta_directorio):
            os.makedirs(ruta_directorio)
        
        ruta_completa = os.path.join(ruta_directorio, archivo_fit.name)
        
        # Guardado físico en disco
        with open(ruta_completa, "wb") as f:
            f.write(archivo_fit.getbuffer())
        
        #VERIFICACIÓN DE INTEGRIDAD
        tamaño = os.path.getsize(ruta_completa)
        st.sidebar.info(f"📁 {archivo_fit.name} guardado")
        st.sidebar.caption(f"Tamaño: {tamaño} bytes") # Esto te confirma que no es un archivo de 0 bytes
        
        # Notificación silenciosa al historial de Nemo
        if st.session_state.ultimo_archivo_notificado != archivo_fit.name:
            aviso_sistema = {
                "role": "user", 
                "contenido": f"(SISTEMA: El usuario ha subido un archivo. Está disponible físicamente en: {ruta_completa}. Si se solicita analizar el entrenamiento, usa esta ruta directamente sin pedirla)."
            }
            st.session_state.historial_mensajes.append(aviso_sistema)
            st.session_state.ultimo_archivo_notificado = archivo_fit.name
            st.toast(f"Archivo cargado en {ruta_directorio}", icon="✅")

    if st.button("🗑️ Reiniciar Laboratorio"):
        llm_mistral.reiniciar_memoria()
        st.session_state.historial_mensajes = []
        st.session_state.datos_usr = None
        st.session_state.ultimo_archivo_notificado = None
        st.rerun()
    st.info("Mistral-Nemo está listo para analizar.")

# =========================================================
# CUERPO PRINCIPAL (3 COLUMNAS CENTRALES)
# =========================================================


# --- COLUMNA 1: ESTADO / MÉTRICAS RÁPIDAS ---
with col_estado:
    st.subheader("🛠️ Estado")
    if st.session_state.datos_usr:
        # Mostramos la FC Máxima usando el componente metric
        st.metric("FC Máx", f"{st.session_state.datos_usr['fc_max_sesion']} bpm")
        st.success("Datos listos")
        # Aquí puedes añadir más métricas pequeñas del resumen
    else:
        st.warning("Sin datos")
        st.caption("Carga un archivo .fit para comenzar el análisis.")


# --- COLUMNA 2: NEMO AI (EL CHAT) ---
with col_nemo:
    st.subheader("🤖 Nemo AI")
    
    # Contenedor con scroll para el chat (mantiene la UI limpia si hay muchos mensajes)
    contenedor_chat = st.container(height=500)
    
    with contenedor_chat:
        # MOSTRAR HISTORIAL EN PANTALLA
        for mensaje in st.session_state.historial_mensajes:
            # FILTRO: Solo mostramos si el contenido es una cadena de texto (str)
            # Además, ocultamos los mensajes de (SISTEMA: ...) para mantener el chat limpio
            if isinstance(mensaje["contenido"], str) and not mensaje["contenido"].startswith("(SISTEMA:"):
                with st.chat_message(mensaje["role"]): # Usamos 'role' para que Streamlit reconozca el icono para Nemo
                    st.markdown(mensaje["contenido"])

    # BUCLE CONVERSACIONAL (Input del usuario)
    if entrada_usuario := st.chat_input("¿Cómo estuvo mi entrenamiento hoy?"):
        # Guardar mensaje del usuario en el estado
        st.session_state.historial_mensajes.append({"role": "user", "contenido": entrada_usuario})
        
        # Procesamiento de la respuesta
        with st.chat_message("assistant"):
            with st.spinner("El cerebro de la IA está procesando los patrones..."):
                
                # --- EL CORAZÓN DEL FLUJO ---
                # 'indicador_respuesta' nos da la señal: ¿Es texto o es una acción?
                #Aquí se envía la pregunta del usuario a Nemo y este analiza si contestar texto o proceder a un function calling
                indicador_respuesta, datos_respuesta = llm_mistral.enviar_pregunta(entrada_usuario)
                
                if indicador_respuesta == "ACCION":
                    # El modelo ha decidido usar una o varias herramientas
                    for llamada_herramienta in datos_respuesta:
                        nombre_funcion = llamada_herramienta['function']['name']
                        argumentos = llamada_herramienta['function']['arguments']
            
                        st.caption(f"🔧 Ejecutando herramienta nativa: {nombre_funcion}...")
            
                        # Ejecución dinámica y segura
                        # --- BUSCA ESTA PARTE DENTRO DEL BUCLE DE HERRAMIENTAS ---
                        if nombre_funcion in DICCIONARIO_HERRAMIENTAS:
                            try:
                                # Ejecutamos la función
                                resultado_tecnico = DICCIONARIO_HERRAMIENTAS[nombre_funcion](**argumentos)
                                
                                
                                # Si la función devolvió una FIGURA de Matplotlib (de los envoltorios)
                                # No podemos meter la figura en el JSON. Metemos un texto de confirmación.
                                if nombre_funcion in ["graficar_oxidacion_grasas", "graficar_vo2"]:
                                    resultado_tecnico = f"Gráfica {nombre_funcion} generada y mostrada en pantalla."
                                
                                if nombre_funcion == "procesar_sesion_entrenamiento_completo":
                                    st.session_state.datos_usr = resultado_tecnico
                                    
                            except Exception as error_ejecucion:
                                resultado_tecnico = {"error": f"Error en la ejecución: {str(error_ejecucion)}"}


                        # EL CABLE DE RETORNO: Inyectamos resultado_tecnico tras la ejecución
                        ahora_dt = datetime.datetime.now()
                        ahora = ahora_dt.strftime("%H:%M")
                        periodo = "MAÑANA (AM)" if ahora_dt.hour < 12 else "TARDE/NOCHE (PM)"

                        # --- SOLUCIÓN AL ERROR DE SERIALIZACIÓN ---
                        # Usamos un 'default' en json.dumps para que cualquier objeto datetime se convierta en texto ISO
                        resultado_tecnico_json = json.dumps(
                        resultado_tecnico, 
                        default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x)
)

                        contexto_retorno = (
                            f"Resultado técnico de {nombre_funcion}: {resultado_tecnico_json}. "
                            f"Hora actual: {ahora}. "
                            "MISION: Eres un Bioestadístico deportivo. Tu respuesta DEBE seguir este formato: "
                            "1. RESUMEN: (Fecha y duración de la sesión). "
                            "2. ANALISIS DE PATRONES: (Busca el valor máximo en 'grasas_por_segundo' y dime a qué FC y VO2 ocurrió exactamente). "
                            "3. DIAGNÓSTICO METABÓLICO: (¿Es eficiente? ¿Oxida grasas a intensidades altas o bajas?). "
                            "4. RECOMENDACIÓN: (Basada en la hora y el clima actual). "
                            "REGLA: Prohibido dar definiciones teóricas de qué es el FatMax. Ve directo al grano con los números."
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


# --- COLUMNA 3: GRÁFICAS / LABORATORIO VISUAL ---


with col_graficas:
    st.subheader("📊 Análisis Visual")
    
    # EL TRUCO (Descoméntalo así):
    if st.session_state.datos_usr and (st.session_state.figura_grasas is None):
        # Si hay datos pero no hay fotos, las creamos nosotros por si Nemo falla
        lista_g = st.session_state.datos_usr.get('grasas_por_segundo', [])
        lista_v = st.session_state.datos_usr.get('vo2_por_segundo', [])
        
        if lista_g:
            st.session_state.figura_grasas = graficas_tools.graficar_oxidacion_grasas(lista_g)
        if lista_v:
            st.session_state.figura_vo2 = graficas_tools.graficar_vo2(lista_v)

    # RENDERIZADO (Lo que ve el usuario)
    if st.session_state.figura_grasas:
        st.pyplot(st.session_state.figura_grasas, use_container_width=True)
    if st.session_state.figura_vo2:
        st.pyplot(st.session_state.figura_vo2, use_container_width=True)