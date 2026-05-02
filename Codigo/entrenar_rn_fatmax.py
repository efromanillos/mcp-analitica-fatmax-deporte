import os
import tensorflow as tf
from tensorflow.keras import layers
import rn_utils 

def validar_y_guardar_rn(model, history, umbral_mse=0.0005):
    """
    Solo guarda el modelo si el error final es menor al umbral.
    """
    # Obtenemos el último valor de pérdida (MSE) del historial
    final_loss = history.history['loss'][-1]
    
    os.makedirs('modelos_rn', exist_ok=True)
    ruta_modelo = 'modelos_rn/fatmax_v1.h5'
    
    print(f"\n--- VALIDACIÓN DE CALIDAD ---")
    print(f"MSE Final: {final_loss:.8f}")
   
    
    if final_loss <= umbral_mse:
        model.save(ruta_modelo)
        print(f"ÉXITO: El modelo supera el filtro de calidad y ha sido guardado.")
    else:
        print(f"FALLO: El error es demasiado alto (Umbral: {umbral_mse}).")
        print("El modelo NO se ha guardado para proteger la versión anterior.")

def ejecutar_entrenamiento():
    # 1. Carga de datos masiva desde la carpeta datos_entrenamiento
    X, y = rn_utils.cargar_super_dataset()
    
    # 2. Definición del modelo híbrido (HR, VO2)
    model = tf.keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=(2,)),  #El número 2 indica que cada ejemplo individual que entra en la red tiene dos características (HR, VO2) <-- 2 columnas
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    # 3. Entrenamiento
    print(f"Entrenando con {len(X)} muestras de 31 sujetos...")
    historial = model.fit(X, y, epochs=100, batch_size=32, verbose=1)
    
    # 4. Guardado Condicional
    validar_y_guardar_rn(model, historial)
    final_mae = historial.history['mae'][-1]
    print(f"Error Medio Absoluto (MAE): {final_mae:.4f} g/min")

if __name__ == "__main__":
    ejecutar_entrenamiento()