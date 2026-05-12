#====================================================================================
# MODULO: graficas_tools.py
# TOOLS YA EXISTENTES
# Graficar resultados de pérdida de grasa a los largo de una sesión de entrenamiento
# Graficar tablas y curva FATMAX y datos de tiempo y geolocalización
# Se usan las funciones line_chart y area_chart como tools existentes
#====================================================================================



import streamlit as st

import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

def graficar_oxidacion_grasas(lista_grasas):
    plt.close('all') 
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(lista_grasas, color='#e74c3c', linewidth=2, marker='o', markersize=4, label='Grasas (g/s)')
    ax.set_title("Curva de Oxidación de Grasas", fontsize=12, pad=10)
    ax.set_ylabel("Gramos/Segundo")
    ax.set_xlabel("Muestras (Tiempo)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    plt.tight_layout() # Ajusta los márgenes para que no se corten los textos
    return fig #Devolvemos objeto real

def graficar_vo2(lista_vo2):
    # No cerramos 'all' aquí si se llaman seguidas, o podrías cerrar la anterior.
    # Pero como app.py las maneja por separado en el estado, está bien.
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.fill_between(range(len(lista_vo2)), lista_vo2, color='#3498db', alpha=0.3)
    ax.plot(lista_vo2, color='#2980b9', linewidth=2, label='VO2 (ml/kg/min)')
    ax.set_title("Consumo de Oxígeno (VO2)", fontsize=12, pad=10)
    ax.set_ylabel("ml/kg/min")
    ax.set_xlabel("Muestras (Tiempo)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    plt.tight_layout()
    return fig #Devolvemos objeto real