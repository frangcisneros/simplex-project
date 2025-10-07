"""
Script para descargar modelos de Ollama recomendados según la RAM del sistema.

Este script detecta automáticamente la RAM disponible y descarga el modelo
más apropiado para el sistema del usuario.
"""

import subprocess
import sys
import os
import psutil
from pathlib import Path


def get_ollama_path():
    """Obtiene la ruta del ejecutable de Ollama."""
    # Ubicaciones comunes de Ollama en Windows
    possible_paths = [
        os.path.expandvars(r"$LOCALAPPDATA\Programs\Ollama\ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
        r"C:\Program Files (x86)\Ollama\ollama.exe",
        "ollama",  # Si está en PATH
    ]

    for path in possible_paths:
        if os.path.exists(path) or path == "ollama":
            try:
                # Probar ejecutar ollama --version
                result = subprocess.run(
                    [path, "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return path
            except:
                continue

    return None


def run_ollama_command(command_args):
    """Ejecuta un comando de Ollama."""
    ollama_path = get_ollama_path()
    if not ollama_path:
        print("❌ No se encontró Ollama instalado")
        print("💡 Descarga desde: https://ollama.ai/")
        return False

    try:
        print(f"🔧 Ejecutando: {ollama_path} {' '.join(command_args)}")
        result = subprocess.run(
            [ollama_path] + command_args, text=True, timeout=1800  # 30 minutos máximo
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout - La descarga está tomando mucho tiempo")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando Ollama: {e}")
        return False


def get_recommended_model():
    """Recomienda un modelo según la RAM disponible."""
    try:
        total_ram_gb = psutil.virtual_memory().total / (1024**3)

        if total_ram_gb < 8:
            return "llama3.2:3b", "Modelo ligero (~2GB)"
        elif total_ram_gb < 16:
            return "mistral:7b", "Equilibrio perfecto (~4GB)"
        else:
            return "llama3.1:8b", "Alta precisión (~4.7GB)"
    except:
        return "llama3.2:3b", "Modelo por defecto"


def list_installed_models():
    """Lista los modelos ya instalados."""
    ollama_path = get_ollama_path()
    if not ollama_path:
        return []

    try:
        result = subprocess.run(
            [ollama_path, "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:  # Hay modelos (primera línea es header)
                return [line.split()[0] for line in lines[1:] if line.strip()]
        return []
    except:
        return []


def main():
    print("=" * 60)
    print("📥 INSTALADOR DE MODELOS OLLAMA")
    print("=" * 60)

    # Verificar RAM
    try:
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"💾 RAM detectada: {total_ram_gb:.1f} GB")
    except:
        print("💾 RAM: No detectada")
        total_ram_gb = 8

    # Listar modelos instalados
    installed = list_installed_models()
    if installed:
        print(f"\n📦 Modelos ya instalados ({len(installed)}):")
        for model in installed:
            print(f"   ✅ {model}")
    else:
        print("\n📦 No hay modelos instalados")

    # Recomendar modelo
    recommended_model, description = get_recommended_model()
    print(f"\n💡 Modelo recomendado: {recommended_model}")
    print(f"   {description}")

    # Verificar si ya está instalado
    if any(recommended_model in model for model in installed):
        print(f"\n✅ {recommended_model} ya está instalado")
        print("\n🎉 ¡Todo listo! Puedes continuar con:")
        print("   python test_modelos.py")
        return

    # Ofrecer instalación
    response = input(f"\n¿Descargar {recommended_model}? (y/N): ").lower().strip()
    if response in ("y", "yes", "sí", "si"):
        print(f"\n📥 Descargando {recommended_model}...")
        print("⏳ Esto puede tomar varios minutos dependiendo de tu conexión...")

        if run_ollama_command(["pull", recommended_model]):
            print(f"\n🎉 ¡{recommended_model} descargado exitosamente!")
            print("\n📝 Próximos pasos:")
            print("   1. python verificar_ollama.py  # Verificar instalación")
            print("   2. python test_modelos.py      # Probar con problemas")
        else:
            print(f"\n❌ Error descargando {recommended_model}")
    else:
        print("\n💡 Modelos alternativos disponibles:")
        print("   • llama3.2:3b  # Ligero (~2GB)")
        print("   • mistral:7b   # Equilibrado (~4GB)")
        print("   • llama3.1:8b  # Preciso (~4.7GB)")
        print("\n📝 Para descargar manualmente:")
        print(f"   ollama pull <modelo>")


if __name__ == "__main__":
    main()
