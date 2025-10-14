import json
import logging
from nlp import NLPConnectorFactory, NLPModelType

# --- Configuración del Logging (muy importante para ver qué pasa por dentro) ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def leer_problema_desde_archivo(filepath: str) -> str:
    """Lee el texto de un problema desde un archivo."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Error: No se encontró el archivo del problema en '{filepath}'")
        return ""


def main():
    """
    Función principal para configurar el conector, procesar un problema y mostrar la solución.
    """
    # --- PASO 1: Elige el modelo y el archivo del problema ---
    # Puedes cambiar esto para probar diferentes modelos y problemas.
    # Modelos disponibles: LLAMA3_1_8B (el que tienes) o MISTRAL_7B (más rápido si lo descargas)
    # Para los problemas complejos, podrías necesitar modelos más grandes.
    modelo_a_usar = NLPModelType.LLAMA3_1_8B  # Usando el modelo disponible
    archivo_problema = "../ejemplos/nlp/problema_complejo.txt"  # Cambia a "problema_compolejo2.txt" para el segundo

    logging.info(f"Usando el modelo: {modelo_a_usar.value}")
    logging.info(f"Cargando problema desde: {archivo_problema}")

    # --- PASO 2: Carga el texto del problema ---
    texto_del_problema = leer_problema_desde_archivo(archivo_problema)
    if not texto_del_problema:
        return

    # --- PASO 3: Crea el conector NLP ---
    # La factory se encarga de construir todo el pipeline (procesador, solver, etc.)
    # Asegúrate de que Ollama esté corriendo con el modelo necesario antes de ejecutar.
    # Comando: `ollama run llama3.1:8b`
    conector = NLPConnectorFactory.create_connector(nlp_model_type=modelo_a_usar)

    logging.info("Conector creado. Procesando el texto del problema...")

    # --- PASO 4: Procesa el texto y resuelve el problema ---
    resultado = conector.process_and_solve(texto_del_problema)

    # --- PASO 5: Muestra los resultados de forma clara ---
    print("\n" + "=" * 50)
    print("           RESULTADO DEL PROCESAMIENTO NLP")
    print("=" * 50)

    # Usamos json.dumps para imprimir el diccionario de forma legible
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    # Mensaje final sobre el éxito o fracaso
    if resultado.get("success"):
        logging.info("El pipeline se completó con éxito.")
    else:
        logging.error(f"El pipeline falló. Error: {resultado.get('error')}")


if __name__ == "__main__":
    main()
