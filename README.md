# FatMax AI Consultant
**Consultoría deportiva avanzada basada en IA para la optimización de la oxidación de grasas.**

Este proyecto es una plataforma de análisis metabólico que utiliza una **Red Neuronal (Keras)** entrenada con datos del estudio original de **Achten & Jeukendrup (2002)**. El sistema integra un modelo de lenguaje local (**Mistral vía Ollama**) para actuar como un consultor experto que interpreta la telemetría de entrenamientos (Garmin/CSV) y factores ambientales.

---

## Requisitos del Sistema
Para garantizar que la IA se ejecute correctamente en local, se requiere:

1. **Ollama:** [Descargar e instalar](https://ollama.com/)
2. **Modelo Mistral:** Ejecutar en la terminal: `ollama pull mistral`
3. **Python 3.10+**
4. **Hardware recomendado:** GPU NVIDIA (optimizado para RTX 3060 o superior mediante CUDA).

---

## Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/efromanillos/mcp-analitica-fatmax-deporte.git](https://github.com/efromanillos/mcp-analitica-fatmax-deporte.git)
   cd mcp-analitica-fatmax-deporte
   ```
   
2. **Crear y activar entorno virtual:**
    python -m venv venv

    # En Windows:
    .\venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
    
3. **Instalar dependencias**

   pip install -r requirements.txt


4. **Estructura del Proyecto**

- codigo/: Carpeta principal con el código fuente.

- app.py: Interfaz de usuario (Streamlit).

- mcp_tools.py: Orquestador de las 6 Tools (APIs y Lógica propia).

- entrenar_rn_fatmax.py: Script para el entrenamiento de la Red Neuronal.

- modelos_rn/: Contiene fatmax_v1.h5 (el cerebro de la aplicación).

- org.txt: Bitácora de desarrollo.


5. **Ejecución**

    cd codigo
    streamlit run app.py
    
 
___

##**Créditos y Fuentes de Datos**

El motor de inferencia de este proyecto ha sido desarrollado y validado utilizando datos 
de investigación abierta:Dataset Principal: Se ha utilizado el dataset de Zignoli disponible en Kaggle, 
que contiene perfiles metabólicos detallados de 31 sujetos durante pruebas de esfuerzo.Referencia Científica: 
El modelo fatmax_v1.h5 utiliza estos datos para aprender la relación entre la Frecuencia Cardíaca (HR) 
y el Consumo de Oxígeno ($VO_2$) para predecir la oxidación de grasas.
Agradecimientos: A la comunidad de investigadores que liberan estos datos, permitiendo que proyectos como FatMax_Lab 
puedan democratizar el acceso a métricas de rendimiento deportivo avanzadas.