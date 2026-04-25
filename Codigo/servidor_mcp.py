#==========================================
#MODULO servidor_mcp.py
#Se incicializa el servidor
#Se registran las herramientas
#que podrá usar el modelo (ollama/Mistral)
#=========================================


# NOTA: para hacer pruebas con el servidor MCP en el cmd ejecutar el siguiente comando:
# npx @modelcontextprotocol/inspector python servidor_mcp.py
# La primera vez que se ejecuta se descarga automáticamente: @modelcontextprotocol/inspector@0.21.2
# Es una herramienta de node.js
# Hay que tener instalado previamente node.js


from mcp.server.fastmcp import FastMCP
import deporte_tools  # Aquí están tus funciones de cálculos con listas

# 1. Inicializamos el servidor MCP
mcp = FastMCP("FatMax_Lab")

# 2. Registramos la extracción de datos
@mcp.tool()
def extraer_datos_fit(ruta_archivo: str) -> list[dict]:
    """Extrae los registros de FC y potencia de un archivo .fit."""
    return deporte_tools.extraer_datos_fit(ruta_archivo)


# 3. Registramos la herramienta de Karvonen (ahora acepta listas)
@mcp.tool()
def calcular_intensidad_karvonen(fc_sesion_lista: list[int], fc_max: int, fc_reposo: int) -> list[float]:
    """Calcula una lista de intensidades de Karvonen (0.0 a 1.0) a partir de una lista de pulsaciones."""
    return deporte_tools.calcular_intensidad_karvonen(fc_sesion_lista, fc_max, fc_reposo)

# 4. Registramos la herramienta de VO2 (ahora acepta listas)
@mcp.tool()
def convertir_intensidad_en_vo2(intensidad_lista: list[float], vo2_max: float = 4.0) -> list[float]:
    """Convierte una lista de intensidades relativas a una lista de VO2 en L/min."""
    return deporte_tools.convertir_intensidad_en_vo2(intensidad_lista, vo2_max)


if __name__ == "__main__":
    mcp.run()