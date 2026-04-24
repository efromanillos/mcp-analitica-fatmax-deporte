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

def obtener_intensidad_karvonen(fc_sesion, fc_max, fc_reposo):
    """
    Calcula el % de intensidad real de una sesión.
    Revela el esfuerzo oculto tras los latidos del FR255.
    """
    fc_reserva = fc_max - fc_reposo
    
    if fc_reserva <= 0:
        return 0.0 # Evitamos división entre cero si los datos son erróneos
        
    intensidad = (fc_sesion - fc_reposo) / fc_reserva
    
    # Devolvemos intensidad redondeada a dos cifras como el dataset original
    return round(intensidad, 2)

#===========================================
#FUNCIÓN convertir intensidad en VO2 [L/min]
#===========================================

def convertir_intensidad_vo2(intensidad, vo2_max=4.0, vo2_rep=0.25):
    """
    Convierte el tanto por uno de Karvonen a L/min 
    para que la red neuronal reciba los datos de entrada en misma unidad de su entrenamiento .
    """
    vo2_reserva = vo2_max - vo2_rep
    vo2_final = (intensidad * vo2_reserva) + vo2_rep
    return round(vo2_final, 2)