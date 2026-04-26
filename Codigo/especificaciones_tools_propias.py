
#===================================================================================
#MODULO especificaciones_tools_propias.py
# Se espcifican las tools propias implementadas que puede pedir Mistral
# La tool especificada es la función orquestadora 
# "procesar_sesion_entrenamiento_completo()" definida en el módulo deporte_tools.py
#====================================================================================





import ollama

# Este es el "manual de instrucciones" con el "menu" de herramientas que le damos a Mistral
#las  herramientas NO las ejecuta Mistral, solo realiza la petición al servidor para que las ejecute (el desarrollador) a través del hardware del PC
#Con esto Mistral sabe qué herramientas puede usar
# especificacion_herramientas.py

# especificacion_herramientas.py



HERRAMIENTAS_DEPORTE = [
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
                        'description': 'Ruta local al archivo .fit dentro de la carpeta datos/ (ej: datos/ruta_llana.fit)'
                    },
                    'fc_reposo': {
                        'type': 'integer', 
                        'description': 'Frecuencia cardíaca en reposo del usuario para el cálculo de intensidad. Por defecto 60.'
                    }
                },
                'required': ['ruta_archivo'],
            },
        },
    }
]



print("Esperando a que Mistral decida qué tools necesita...")


