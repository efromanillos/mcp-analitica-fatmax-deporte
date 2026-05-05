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
import rn_utils


#========================================
#FUNCIÓN para extraer frecuencia cardiaca 
#a partir de un archivo .fit
#========================================

#ruta_archivo = 'datos_usr\ruta_llana.fit'

from fitparse import FitFile

def extraer_datos_fit(ruta_archivo):
    fitfile = FitFile(ruta_archivo)
    registros = []
    info_sesion = {}

    # 1. Extraer Metadatos de la Sesión (FC Máxima, Media, etc.)
    # Buscamos en 'session' que contiene el resumen global del entrenamiento
    for session in fitfile.get_messages('session'):
        v_session = session.get_values()
        info_sesion = {
            'fc_max': v_session.get('max_heart_rate'),
            'fc_media': v_session.get('avg_heart_rate'),
            'calorias': v_session.get('total_calories'),
            'distancia_metros': v_session.get('total_distance'),
            'fecha_hora_inicio_entrenamiento': v_session.get('start_time')
        }
        break  # Normalmente solo hay un mensaje de sesión relevante

    # 2. Extraer el segundo a segundo (Records)
    for record in fitfile.get_messages('record'):
        v = record.get_values()
        
        datos_fit = {
            'timestamp': v.get('timestamp'),
            'fc': v.get('heart_rate'),
            #'potencia': v.get('power'), #es necesario un sensor en el pedalier de la bici para tomar estos datos
            'altitud': v.get('enhanced_altitude') 
            #'cadencia': v.get('cadence') #necesario sensor para capturar estos datos
        }
        
        # Limpieza de GPS (Semicírculos a Grados)
        lat = v.get('position_lat')
        lon = v.get('position_long')
        if lat is not None and lon is not None:
            datos_fit['lat'] = lat * (180.0 / 2**31) #hay 2^31 semicirculos en 180 grados. Garmin usa una unidad llamada Semicírculos y no grados
            datos_fit['lon'] = lon * (180.0 / 2**31)
            
        registros.append(datos_fit)
            
    # Retornamos un dicionario completo
    return {
        "metadatos": info_sesion,
        "puntos": registros
    }


#==========================================================================
#FUNCIÓN para calcular nivel de intensidad
#a partir de datos de frecuencia cardiaca
#NOTA: 1% de FCR (Karvonen) es aproximadamente igual a 1% de VO2 Reserva
#==========================================================================

# Devolvemos lista de intensidades redondeadas a dos cifras como en el dataset original
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



#=====================================================
# FUNCION orquestadora que llama a todas las anteriores
# es la función que, Mistral, podrá pedir que se use
#======================================================

def procesar_sesion_entrenamiento_completo(ruta_archivo, fc_reposo_user=60):
    """
    Orquesta la transformación completa: del archivo .fit al VO2, intensidades, grasas por segundo
    """
    # 1. Extraer datos (Metadatos + Puntos)
    resultado = extraer_datos_fit(ruta_archivo)
    
    # 2. Preparar lista de FC y obtener el pico máximo alcanzado en la sesión
    fc_lista = [p['fc'] for p in resultado['puntos'] if p['fc'] is not None]
    
    # Cambiamos fc_max_real por fc_max_sesion para mayor precisión semántica
    fc_max_sesion = resultado['metadatos'].get('fc_max')

    # Validación de seguridad: si no hay FC max registrada en los metadatos del archivo, 
    # buscamos el valor más alto dentro de la serie temporal de puntos.
    if not fc_max_sesion:
        fc_max_sesion = max(fc_lista) if fc_lista else 180

    # 3. Calcular Intensidades (Karvonen) usando el pico de esta sesión específica
    intensidades = calcular_intensidad_karvonen(fc_lista, fc_max_sesion, fc_reposo_user)

    # 4. Convertir a VO2 
    vo2_datos = convertir_intensidad_en_vo2(intensidades)

    # 5. Obtener Oxidación de Grasas vía Red Neuronal (Híbrida: FC + VO2)
    grasas_datos = rn_utils.predecir_oxidacion_grasas(fc_lista, vo2_datos)

    return {
        "resumen": resultado['metadatos'],
        "fc_max_sesion": fc_max_sesion, # Lo devolvemos explícitamente para que Nemo lo vea
        "intensidades": intensidades,
        "vo2_por_segundo": vo2_datos,
        "grasas_por_segundo": grasas_datos # Para gráficas y análisis de Nemo
    }



#=================================================================
# FUNCION para calcular la Zona de entrenamiento 
# a través del porcentaje de intensidad con la fórmula de Karnoven
#=================================================================

def calcular_zonas_entrenamiento(fc_max, fc_reposo, fc_actual):
    """
    Calcula el porcentaje de intensidad usando la fórmula de Karvonen:
    % Intensidad = ((FC_actual - FC_reposo) / (FC_max - FC_reposo)) * 100
    """
    try:
        fc_reserva = fc_max - fc_reposo  # Frecuencia Cardíaca de Reserva
        intensidad = ((fc_actual - fc_reposo) / fc_reserva) * 100
        
        # Determinamos la zona de entrenamiento (Patrón de flujo)
        zona = ""
        if intensidad < 60: zona = "Zona 1 (Recuperación / Salud)"
        elif intensidad < 70: zona = "Zona 2 (FatMax - Oxidación de grasas óptima)"
        elif intensidad < 80: zona = "Zona 3 (Aeróbica - Resistencia)"
        elif intensidad < 90: zona = "Zona 4 (Umbral Anaeróbico)"
        else: zona = "Zona 5 (Esfuerzo Máximo)"
        
        return {
            "porcentaje_intensidad": round(intensidad, 2),
            "zona_entrenamiento": zona,
            "fc_reserva": fc_reserva
        }
    except Exception as e:
        return {"error": f"Error en el cálculo: {str(e)}"}