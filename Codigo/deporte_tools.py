#===================================================================================
#TOOLS PROPIAS para:
# - optener la frecuencia cardiaca a los largo del tiempo de un archivo .fit
# - calcular el nivel de intensidad del ejercicio en función de la frecuencia cardiaca
#   a través de la fórmula de Karvonen
# - Convertir el nivel de intensidad (adimensional) a VO2 [L/min]
# RELOJ FITNESS: Garmin Forerunner 255
#====================================================================================

from fitparse import FitFile
import datetime


#========================================
#FUNCIÓN para extraer frecuencia cardiaca 
#a partir de un archivo .fit
#========================================

def extraer_datos_fit(ruta_archivo):
    fitfile = FitFile(ruta_archivo)
    registros = []

    for record in fitfile.get_messages('record'):
        v = record.get_values()
        
        # El FR255 nos da una riqueza de datos increíble
        datos_fit = {
            'timestamp': v.get('timestamp'),
            'fc': v.get('heart_rate'),
            'potencia': v.get('power'),       # medida en vatios
            'altitud': v.get('enhanced_altitude'), 
            'cadencia': v.get('cadence')
        }
        
        # Limpieza de GPS (Semicírculos a Grados)
        lat = v.get('position_lat')
        lon = v.get('position_long')
        if lat and lon:
            datos_fit['lat'] = lat * (180.0 / 2**31)
            datos_fit['lon'] = lon * (180.0 / 2**31)
            
        registros.append(datos_fit)
            
    return registros


#==========================================================================
#FUNCIÓN para calcular nivel de intensidad
#a partir de datos de frecuencia cardiaca
#NOTA: 1% de FCR (Karvonen) es aproximadamente igual a 1% de VO2 Reserva
#==========================================================================

# Devolvemos lista de intensidades redondeadas a dos cifras como el dataset original
# La intensidad se ha calculado en tanto por 1 -> 0,70 equivale a 70% de intensidad

def calcular_intensidad_karvonen(fc_sesion_lista, fc_max, fc_reposo):
    """Calcula una lista de intensidades a partir de una lista de pulsaciones."""
    reserva = fc_max - fc_reposo

    return [round((fc - fc_reposo) / reserva, 2) for fc in fc_sesion_lista]


#===========================================
#FUNCIÓN convertir intensidad en VO2 [L/min]
#===========================================

# el VO2 max es el volumen de oxígeno máximo que el cuerpo puede procesar (pulmones y sangre)
# el VO2 reposo es el volumen de oxígeno basal, se consume por estar vivo
# el VO2 reserva es el que realmente podemos hacer uso para las actividades (andar, correr, etc.)
# el VO2 total es que se ha consumido dada un nivel de intensidad + el basal (sumando a los largo del tiempode sesión será el total de VO2 de la sesión de entrenamiento)

def convertir_intensidad_en_vo2(intensidad_lista, vo2_max=4.0, vo2_rep=0.25):
    """Convierte una lista de intensidades en una lista de VO2 total."""
    reserva_vo2 = vo2_max - vo2_rep
    return [round((intensidad * reserva_vo2) + vo2_rep, 2) for intensidad in intensidad_lista]