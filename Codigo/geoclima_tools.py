#=======================================================
#MODULO con tools de TERCEROS de clima y geolocalización
# obtener geolocalización (IP-API)
# obtener clima -> open-meteo (no requiere api_key)
# ======================================================

import requests

#==================
# TOOLS DE TERCEROS
#==================

# TOOL 1: GEOLOCALIZACIÓN (IP-API)
def obtener_ubicacion_automatica():
    """
    Obtiene coordenadas aproximadas mediante la IP.
    API de terceros.
    """
    try:
        # Modo gratuito: usa http (no https)
        res = requests.get("http://ip-api.com/json/", timeout=5)
        data = res.json()
        if data['status'] == 'success':
            return {
                "lat": data['lat'],
                "lon": data['lon'],
                "ciudad": data['city']
            }
        return None
    except:
        return None

# TOOL 2: CLIMA (OPEN-METEO)
def obtener_clima_local(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": "true"}
    
    try:
        data = requests.get(url, params=params, timeout=5).json()
        current = data.get("current_weather", {})
        
        return {
            "temperatura": current.get("temperature"),
            "viento": current.get("windspeed"),
            "condicion": current.get("weathercode")
        }
    except:
        return {"error": "Servicio no disponible"}

    


#===================================
#PRUEBAS: punto de entrada al módulo
#===================================

if __name__ == "__main__":
    print("--- 🔍 INICIANDO PRUEBA DE HERRAMIENTAS ---")
    
    ubicacion = obtener_ubicacion_automatica()
    
    if ubicacion:
        print(f"Estás en: {ubicacion['ciudad']} (Lat: {ubicacion['lat']}, Lon: {ubicacion['lon']})")
        
        print("\n[2] Consultando clima en Open-Meteo...")
        clima = obtener_clima_local(ubicacion['lat'], ubicacion['lon'])
        
        if "temperatura" in clima:
            print(f"Temperatura: {clima['temperatura']}°C")
            # Usamos .get() para evitar que el programa explote si la clave no existe
            viento = clima.get("viento", "N/A") 
            print(f"Velocidad del viento: {viento} km/h")
            print(f"Condición: {clima['condicion']}")
        else:
            print(f"Error en clima: {clima.get('error')}")
    else:
        print("No se pudo detectar la ubicación.")
        
    print("\n--- PRUEBA FINALIZADA ---")

    