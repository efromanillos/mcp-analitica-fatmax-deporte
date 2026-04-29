#=========================================================
# MODULO: rn_utils.py
# Inferencia de la Red Neuronal para predicción de FatMax
#=========================================================

import tensorflow as tf
import numpy as np
import os

def predecir_oxidacion_grasas(lista_vo2):
    """
    Carga el modelo .h5 y predice la quema de grasas (g/min) 
    para una serie temporal de consumo de oxígeno.
    """
    ruta_modelo = 'modelos_rn/fatmax_v1.h5'
    
    if not os.path.exists(ruta_modelo):
        return {"error": "Modelo no encontrado. Entrena la red primero."}

    # Cargar el modelo entrenado
    model = tf.keras.models.load_model(ruta_modelo)
    
    # Preparar datos: la red espera (N muestras, 1 característica)
    X = np.array(lista_vo2).reshape(-1, 1)
    
    # Realizar la predicción
    predicciones = model.predict(X, verbose=0)
    
    # Devolvemos una lista simple de Python para que sea JSON-serializable
    return predicciones.flatten().tolist()