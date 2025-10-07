"""
Script de verificación rápida para Ollama.

Verifica que Ollama esté instalado, funcionando, y puede descargar/usar modelos.
"""

import requests
import json
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def check_ollama_installation():
    """Verifica si Ollama está instalado y ejecutándose."""
    print("🔍 Verificando instalación de Ollama...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está ejecutándose correctamente")
            return True
        else:
            print(f"❌ Ollama responde con código: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ No se puede conectar a Ollama")
        print("   ¿Está Ollama ejecutándose? Prueba: ollama serve")
        return False
    except requests.Timeout:
        print("❌ Timeout conectando a Ollama")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_available_models():
    """Lista los modelos disponibles en Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])

            if models:
                print(f"\n📦 Modelos instalados ({len(models)}):")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"   • {name} ({size_gb:.1f} GB)")
                return models
            else:
                print("\n📦 No hay modelos instalados")
                return []
        else:
            print("❌ Error obteniendo lista de modelos")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def recommend_model():
    """Recomienda un modelo según la RAM disponible."""
    try:
        import psutil

        total_ram_gb = psutil.virtual_memory().total / (1024**3)

        print(f"\n💾 RAM detectada: {total_ram_gb:.1f} GB")

        if total_ram_gb < 8:
            recommended = "llama3.2:3b"
            print(f"💡 Modelo recomendado: {recommended} (~2GB)")
        elif total_ram_gb < 16:
            recommended = "mistral:7b"
            print(f"💡 Modelo recomendado: {recommended} (~4GB)")
        else:
            recommended = "llama3.1:8b"
            print(f"💡 Modelo recomendado: {recommended} (~4.7GB)")

        print(f"\n📥 Para descargar: ollama pull {recommended}")
        return recommended

    except ImportError:
        print("❌ No se puede detectar RAM (falta psutil)")
        return "llama3.2:3b"


def test_simple_generation():
    """Prueba una generación simple de texto."""
    models = list_available_models()

    if not models:
        print("\n⚠️  No hay modelos para probar")
        return False

    # Usar el primer modelo disponible
    model_name = models[0].get("name", "")
    print(f"\n🧪 Probando generación con {model_name}...")

    try:
        request_data = {
            "model": model_name,
            "prompt": "¿Cuál es la capital de España?",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50,
            },
        }

        response = requests.post(
            "http://localhost:11434/api/generate", json=request_data, timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            generated_text = data.get("response", "").strip()
            print(f"✅ Respuesta: {generated_text[:100]}...")
            return True
        else:
            print(f"❌ Error en generación: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error en generación: {e}")
        return False


def main():
    print("=" * 60)
    print("🚀 VERIFICADOR DE OLLAMA")
    print("=" * 60)

    # 1. Verificar instalación
    if not check_ollama_installation():
        print("\n📝 Pasos para instalar Ollama:")
        print("   1. Descargar desde: https://ollama.ai/")
        print("   2. Instalar el ejecutable")
        print("   3. Ejecutar: ollama serve")
        print("   4. Ejecutar este script nuevamente")
        return

    # 2. Listar modelos
    models = list_available_models()

    # 3. Recomendar modelo si no hay ninguno
    if not models:
        recommend_model()
        print("\n📝 Después de descargar un modelo:")
        print("   1. python verificar_ollama.py  # Verificar instalación")
        print("   2. python test_modelos.py      # Probar con problemas")
        return

    # 4. Probar generación
    if test_simple_generation():
        print("\n🎉 ¡Ollama está funcionando correctamente!")
        print("\n📝 Próximos pasos:")
        print("   • python test_modelos.py  # Probar con problemas de optimización")
        print(
            "   • python nlp_simplex.py --nlp --file ejemplos/nlp/problema_complejo.txt"
        )
    else:
        print("\n⚠️  Ollama está instalado pero hay problemas con la generación")


if __name__ == "__main__":
    main()
