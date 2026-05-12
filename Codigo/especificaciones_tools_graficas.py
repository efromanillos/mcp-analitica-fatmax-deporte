
# MÓDULO especificaciones_tools_graficas.py
# se usan tools propias de streamlit para:
# - graficar oxidación de grasa por segundo
# - graficar consumo de VO2 por segundo


TOOLS_GRAFICAS = [
    {
        'type': 'function',
        'function': {
            'name': 'graficar_oxidacion_grasas',
            'description': 'Genera una visualización científica (Matplotlib) de la tasa de oxidación de grasas a lo largo del tiempo.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'lista_grasas': {
                        'type': 'array',
                        'items': {'type': 'number'},
                        'description': 'Serie temporal de valores de oxidación de grasas (g/seg) predichos por la Red Neuronal.'
                    }
                },
                'required': ['lista_grasas'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'graficar_vo2',
            'description': 'Genera una gráfica de área del consumo de oxígeno (VO2) para el análisis de intensidad metabólica.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'lista_vo2': {
                        'type': 'array',
                        'items': {'type': 'number'},
                        'description': 'Serie temporal de valores de VO2 (ml/kg/min) calculados durante la sesión.'
                    }
                },
                'required': ['lista_vo2'],
            },
        },
    }
]