#==========================================
#MODULO servidor_mcp.py
#Se incicializa el servidor
#Se registran las herramientas
#que podrá usar el modelo (ollama/Mistral)
#=========================================


# NOTA: para hacer pruebas con el servidor MCP con el entorno virtual activado en el cmd ejecutar el siguiente comando:
# npx @modelcontextprotocol/inspector python servidor_mcp.py
# La primera vez que se ejecuta se descarga automáticamente: @modelcontextprotocol/inspector@0.21.2
# Es una herramienta de node.js
# Hay que tener instalado previamente node.js


from mcp.server.fastmcp import FastMCP
import deporte_tools  # Aquí están las funciones de cálculos de Intensidades, VO2 y orquestadora
import geoclima_tools #Aquí están las funciones de geolocalización por IP y clima


# NOTA_1: NO es necesario llamar la función definida aquí igual que en deporte_tools.py pero se decide hacerlo por claridad


# NOTA_2:
# En Python, un decorador no es más que una función que envuelve a otra. 
# Cuando el servidor arranca, recorre el archivo buscando todo lo que tenga ese "sello" 
# para construir el catálogo que luego lee el Inspector. 
# Es como si estuvieras etiquetando cajas en un almacén para que 
# el operario (Mistral) sepa qué hay dentro de cada una sin tener que abrirlas todas
# el nombre mcp debe coincidir en el decorador con el nombre del objeto creado al hacer mcp = FastMCP("FatMax_Lab")

#Inicializamos el servidor MCP
mcp = FastMCP("FatMax_Lab")

#=============
#TOOLS PROPIAS
#=============

@mcp.tool()
def procesar_sesion_entrenamiento_completo(ruta_archivo: str, fc_reposo: int = 60) -> dict:
    """
    Analiza una sesión .fit completa.
    Devuelve: Metadatos, Intensidad (Karvonen) y VO2 por segundo.
    """
    # Esta es la única puerta que necesita Mistral
    return deporte_tools.procesar_sesion_entrenamiento_completo(ruta_archivo, fc_reposo)


@mcp.tool()
def calcular_zonas_entrenamiento(fc_max: int, fc_reposo: int, fc_actual: int) -> dict:
    """
    Calcula el porcentaje de intensidad y la zona de entrenamiento específica
    según el método Karvonen. Útil para análisis rápidos sin archivo .fit.
    """
    # Llamamos a la lógica pura que está en deporte_tools
    return deporte_tools.calcular_zonas_entrenamiento(fc_max, fc_reposo, fc_actual)


#==========================================
#TOOLS DE TERCEROS: geolocalizacion y clima
#==========================================


@mcp.tool()
def obtener_ubicacion_automatica() -> dict:
    """
    Obtiene coordenadas aproximadas (lat, lon, ciudad) mediante la IP del usuario.
    Útil para situar el contexto general del entrenamiento si no hay GPS.
    """
    return geoclima_tools.obtener_ubicacion_automatica()

@mcp.tool()
def obtener_clima_local(lat: float, lon: float) -> dict:
    """
    Consulta el clima actual (temperatura, viento, código de condición) para coordenadas decimales.
    Permite a la IA analizar cómo afectan las condiciones externas al rendimiento.
    """
    return geoclima_tools.obtener_clima_local(lat, lon)

#==========================================
#TOOLS PARA GRÁFICAS:
#==========================================


if __name__ == "__main__":
    mcp.run()