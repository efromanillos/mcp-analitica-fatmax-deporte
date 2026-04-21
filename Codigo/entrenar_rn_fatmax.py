#=========================================================
# MODULO. Entrenamiento red neuronal 
# con datos extraídos del paper (Jeukendrup et al., 2002)
#=========================================================


import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import os

# 1. DATOS extraídos de: https://www.researchgate.net/publication/228854514_Fatmax_A_new_concept_to_optimize_fat_oxidation_during_exercise

def obtener_datos_entrenamiento():
    """Extrae los puntos digitalizados de la gráfica de Jeukendrup."""
    # X: VO2 (L/min) | y: Fat Oxidation (g/min)
    X = np.array([1.2, 1.5, 1.8, 2.0, 2.2, 2.6, 3.0, 3.5, 4.0]).reshape(-1, 1)
    y = np.array([0.28, 0.31, 0.33, 0.34, 0.33, 0.30, 0.25, 0.12, 0.00]).reshape(-1, 1)
    return X, y




# 2. MODELO
#en cada época calcula el error cuadrático medio (MSE) y se espera que baje
#podemos acceder a el valor del MSE en cada época a través del objeto model que continen una lista (loss)
#El MSE le sirve al optimizador ADAM para saber cuando debe ajustar los pesos de la neuronas en la siguiente época (epochs)
#NOTA relu usa la función max(0, x) si x > 0 el valor pasa tal cual. si el valor x <= 0 lo convierte en cero, lo bloquea y en la siguiente epoch la neurona se apaga (Dying ReLu)
#Los valores de x son la "suma" que hace la neurona con los valores que la entran. Las neuronas tienen tantas entradas como neuronas había en la capa anterior
def crear_modelo_rn():
    """Define la estructura de la Red Neuronal."""
    model = tf.keras.Sequential([
        layers.Dense(32, activation='relu', input_shape=(1,)),  #1ª capa oculta 32 neuronas 1 sola entrada cada neurona (pq recibe solo un dato de VO2)
                                                                #-> input_sahpe = (1,) le dice que solo va a recibir un dato a la vez (el valor de VO2)

        layers.Dense(16, activation='relu'),                    #2ª capa oculta -> 16 neuronas -> 32 entradas cada una
        layers.Dense(1)                                         #Neurona de salida, 16 entradas. Todo colapsa en un solo número (1 valor de tasa de oxidación de grasa)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model



# 3. ENTRENAMIENTO
def entrenar_modelo(model, X, y, n_epochs=1000):
    """
    Ejecuta el entrenamiento y devuelve el historial de métricas.
    Permite controlar las épocas para pruebas rápidas o entrenamiento real.
    """
    print(f"Iniciando entrenamiento ({n_epochs} épocas)...")
    
    # Guardamos historial de MSE en cada época
    historial = model.fit(
        X, 
        y, 
        epochs=n_epochs, 
        verbose=1 # Ponemos 1 para ver el progreso en la terminal
    )
    return historial


# 4. MÉTRICA DE RENDIMIENTO GUARDADO CONDICIONAL
#acceso al última cálculo de MSE (la última epochs) en final_loss
def validar_y_guardar(model, history):
    """Aplica el filtro de calidad MSE antes de persistir el modelo."""
    final_loss = history.history['loss'][-1]
    os.makedirs('modelos_rn', exist_ok=True)
    
    if final_loss < 0.001:
        model.save('modelos_rn/fatmax_v1.h5')
        print(f"ÉXITO: Modelo guardado con MSE: {final_loss:.6f}")
    else:
        print(f"FALLO: Precisión insuficiente (MSE: {final_loss:.6f}).")
        print("El modelo NO ha sido guardado.")


# --- FLUJO PRINCIPAL PRUEBAS ---
if __name__ == "__main__":
    # 1. Obtener datos
    X_train, y_train = obtener_datos_entrenamiento()
    
    # 2. Crear arquitectura
    mi_modelo = crear_modelo_rn()
    
    # 3. Entrenar (Prueba de 10 épocas como acordamos)
    # Cambiar a 1000 cuando para el modelo definitivo
    historial_final = entrenar_modelo(mi_modelo, X_train, y_train, n_epochs=10)
    
    # 4. Validar y Guardar
    validar_y_guardar(mi_modelo, historial_final)