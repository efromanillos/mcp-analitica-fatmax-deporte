#=========================================================
# MODULO: rn_utils.py
# Inferencia de la Red Neuronal para predicción de FatMax
#=========================================================

import pandas as pd
import numpy as np
import tensorflow as tf
import glob
import os

# Variable global para mantener el modelo en memoria
_MODELO_ENTRENADO = None



#==================================================
#PROCESAMIENTO Y CREACIÓN DATASET DE ENTRENAMIENTO
#Creado a partir de dataset de Kaggle (Zignoli)
#==================================================


def cargar_super_dataset(carpeta_datos="datos_entrenamiento_rn"):
    X_global = []
    y_global = []
    
    archivos = glob.glob(os.path.join(carpeta_datos, "*.csv"))
    
    for archivo in archivos:
        # 1. Carga limpia: Por defecto Pandas usa coma como separador 
        # y punto como decimal, que es exactamente lo que tienen tus archivos.
        df = pd.read_csv(archivo)
        
        # 2. Aseguramos que sean números (por si hay algún NaN o dato corrupto)
        df['Oxygen'] = pd.to_numeric(df['Oxygen'], errors='coerce')
        df['HR'] = pd.to_numeric(df['HR'], errors='coerce')
        df = df.dropna(subset=['Oxygen', 'HR'])
        
        # 3. Calculamos pérdida de grasa en función de VO2
        vo2 = df['Oxygen'] / 1000.0  # ml/min a L/min
        hr = df['HR']
        
        num = 10011.958 * vo2
        den = 900 + (76.7 * vo2)
        fat_ox = (1.67 * vo2) - (num / den)
        
        y = fat_ox.clip(lower=0).values
        X = np.column_stack((hr.values, vo2.values))
        
        X_global.append(X)
        y_global.append(y)
        
    return np.vstack(X_global), np.concatenate(y_global)

#======================================================
#Función para predecir con la RN pérdida de grasa
#en función una lista de VO2 a partir del pulso/segundo
#obtenido con el reloj Garmin
#=======================================================

def predecir_oxidacion_grasas(lista_fc, lista_vo2):
    global _MODELO_ENTRENADO
    ruta_modelo = 'modelos_rn/fatmax_v1.h5'
    
    # Solo cargamos si no se ha cargado antes
    if _MODELO_ENTRENADO is None:
        if not os.path.exists(ruta_modelo):
            return {"error": "Modelo no encontrado."}
        #_MODELO_ENTRENADO = tf.keras.models.load_model(ruta_modelo)
        _MODELO_ENTRENADO = tf.keras.models.load_model(ruta_modelo, compile=False)

    # Preparamos los datos
    X = np.column_stack((lista_fc, lista_vo2))
    
    # Predicción ultra rápida desde memoria RAM
    predicciones = _MODELO_ENTRENADO.predict(X, verbose=0)
    return predicciones.flatten().tolist()




