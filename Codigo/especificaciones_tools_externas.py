
#===============================================================================================
# MODULO: espcificaciones_tools_externas.py
# Donde se especifican las tools de terceros a través de API que MIstral podrá pedir que se usen
# Son las funciones definidas en geoclima_tools.py
#===============================================================================================


# especificaciones_tools_externas.py

# Este es el manual para que Mistral consulte datos de fuera del reloj Garmin
# (Clima, altitud, condiciones ambientales)

# especificaciones_tools_externas.py

TOOLS_EXTERNAS = [
    {
        'type': 'function',
        'function': {
            'name': 'obtener_ubicacion_automatica',
            'description': 'Obtiene la ubicación actual aproximada (latitud, longitud y ciudad) basándose en la dirección IP del usuario.',
            'parameters': {
                'type': 'object',
                'properties': {},  # No requiere parámetros de entrada
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'obtener_clima_local',
            'description': 'Consulta el clima actual (temperatura, viento, condición) para unas coordenadas dadas.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'lat': {  # Importante: coincide con función en geoclima_tools.py
                        'type': 'number',
                        'description': 'Latitud en grados decimales (ej: 40.44)'
                    },
                    'lon': {  # Importante: coincide con función en geoclima_tools.py
                        'type': 'number',
                        'description': 'Longitud en grados decimales (ej: -3.77)'
                    }
                },
                'required': ['lat', 'lon'],
            },
        },
    }
]

print("Especificaciones externas cargadas: Mistral ahora puede consultar el clima")