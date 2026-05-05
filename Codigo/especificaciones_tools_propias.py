#===================================================================================
# MODULO especificaciones_tools_propias.py
# Se especifican las tools propias implementadas que puede pedir Mistral
#====================================================================================

import ollama

# Este es el "manual de instrucciones" con el "menu" de herramientas que le damos a Mistral
# las herramientas NO las ejecuta Mistral, solo realiza la petición al servidor para que 
# las ejecute el desarrollador a través del hardware del PC.

TOOLS_PROPIAS = [
    {
        'type': 'function',
        'function': {
            'name': 'procesar_sesion_entrenamiento_completo',
            'description': 'Realiza un análisis integral de un archivo .fit. Extrae FC, calcula intensidad Karvonen y estima el VO2 por segundo.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'ruta_archivo': {
                        'type': 'string', 
                        'description': 'Ruta local al archivo .fit dentro de la carpeta datos/ (ej: datos_usr/ruta_llana.fit)'
                    },
                    'fc_reposo': {
                        'type': 'integer', 
                        'description': 'Frecuencia cardíaca en reposo del usuario para el cálculo de intensidad. Por defecto 60.'
                    }
                },
                'required': ['ruta_archivo'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'calcular_zonas_entrenamiento',
            'description': 'Calcula la zona de entrenamiento y el porcentaje de intensidad usando el método Karvonen para un momento puntual o promedio.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'fc_max': {
                        'type': 'integer',
                        'description': 'Frecuencia cardíaca máxima del usuario.'
                    },
                    'fc_reposo': {
                        'type': 'integer',
                        'description': 'Frecuencia cardíaca en reposo habitual del usuario.'
                    },
                    'fc_actual': {
                        'type': 'integer',
                        'description': 'Frecuencia cardíaca media de la sesión o valor actual a analizar.'
                    }
                },
                'required': ['fc_max', 'fc_reposo', 'fc_actual'],
            },
        },
    }
]

print("Esperando a que Mistral decida qué tools necesita del menú de FatMaxLab...")