import ollama

# Este es el "manual de instrucciones" que le damos a Mistral
# especificacion_herramientas.py

# especificacion_herramientas.py

HERRAMIENTAS_DEPORTE = [
    {
        'type': 'function',
        'function': {
            'name': 'extraer_datos_fit',
            'description': 'Extrae una lista de registros (pulsaciones, potencia, cadencia) de un archivo .fit de Garmin.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'ruta_archivo': {
                        'type': 'string', 
                        'description': 'Ruta local completa al archivo .fit (ej: C:/entrenamientos/actividad.fit)'
                    }
                },
                'required': ['ruta_archivo'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'calcular_intensidad_karvonen',
            'description': 'Calcula una lista de intensidades (0.0 a 1.0) a partir de una lista de pulsaciones.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'fc_sesion_lista': {
                        'type': 'array', 
                        'items': {'type': 'integer'},
                        'description': 'Lista de pulsaciones (FC) extraídas del archivo .fit'
                    },
                    'fc_max': {'type': 'integer', 'description': 'Frecuencia cardíaca máxima del usuario'},
                    'fc_reposo': {'type': 'integer', 'description': 'Frecuencia cardíaca en reposo'}
                },
                'required': ['fc_sesion_lista', 'fc_max', 'fc_reposo'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'convertir_intensidad_en_vo2',
            'description': 'Transforma una lista de intensidades en una lista de consumo de oxígeno total (L/min).',
            'parameters': {
                'type': 'object',
                'properties': {
                    'intensidad_lista': {
                        'type': 'array', 
                        'items': {'type': 'number'},
                        'description': 'Lista de valores de intensidad (0.0 a 1.0)'
                    },
                    'vo2_max': {'type': 'number', 'description': 'Capacidad máxima de oxígeno en L/min'},
                    'vo2_rep': {'type': 'number', 'description': 'Gasto basal en reposo (por defecto 0.25)'}
                },
                'required': ['intensidad_lista', 'vo2_max'],
            },
        },
    }
]

print("Esperando a que Mistral decida qué tools necesita...")


# Aquí es donde Mistral recibirá los datos y decidirá usar las fórmula de cálculos