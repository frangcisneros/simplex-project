#!/usr/bin/env python3
"""
Sistema de análisis de capacidades del sistema para recomendar modelos de IA.
"""
import psutil
import platform
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SystemCapabilities:
    """Información sobre las capacidades del sistema."""

    total_ram_gb: float
    available_ram_gb: float
    cpu_cores: int
    cpu_freq_ghz: float
    has_cuda: bool
    gpu_name: Optional[str]
    gpu_memory_gb: Optional[float]
    platform: str
    architecture: str


@dataclass
class ModelRecommendation:
    """Recomendación de modelo de IA."""

    name: str
    size: str
    ram_required_gb: float
    description: str
    recommended: bool
    reason: str


class SystemAnalyzer:
    """Analiza las capacidades del sistema."""

    # Requisitos mínimos de RAM para cada modelo (GB)
    MODEL_REQUIREMENTS = {
        "llama3.2:1b": {
            "ram": 2,
            "size": "1.3 GB",
            "desc": "Modelo pequeño y rápido, ideal para sistemas con recursos limitados",
        },
        "llama3.2:3b": {
            "ram": 4,
            "size": "2.0 GB",
            "desc": "Balance entre velocidad y calidad para sistemas modestos",
        },
        "phi3:mini": {
            "ram": 4,
            "size": "2.3 GB",
            "desc": "Modelo optimizado de Microsoft, excelente rendimiento",
        },
        "llama3.1:8b": {
            "ram": 8,
            "size": "4.7 GB",
            "desc": "Modelo balanceado con buena calidad de respuestas",
        },
        "mistral:7b": {
            "ram": 8,
            "size": "4.1 GB",
            "desc": "Excelente modelo para tareas generales",
        },
        "gemma2:9b": {
            "ram": 10,
            "size": "5.5 GB",
            "desc": "Modelo de Google con gran capacidad",
        },
        "llama3.1:70b": {
            "ram": 48,
            "size": "40 GB",
            "desc": "Modelo grande de alta calidad (solo para sistemas potentes)",
        },
    }

    def __init__(self):
        self.capabilities = self._analyze_system()

    def _analyze_system(self) -> SystemCapabilities:
        """Analiza las capacidades del sistema."""
        # Información de memoria
        mem = psutil.virtual_memory()
        total_ram_gb = mem.total / (1024**3)
        # Usar un cálculo más realista de RAM disponible:
        # RAM total menos lo que está realmente en uso (no solo "libre")
        # Esto da una mejor estimación de lo que Ollama puede usar
        available_ram_gb = (mem.total - mem.used) / (1024**3)

        # Información de CPU
        cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_ghz = cpu_freq.current / 1000 if cpu_freq else 0.0

        # Información de plataforma
        sys_platform = platform.system()
        architecture = platform.machine()

        # Detectar GPU (simplificado)
        has_cuda, gpu_name, gpu_memory = self._detect_gpu()

        return SystemCapabilities(
            total_ram_gb=total_ram_gb,
            available_ram_gb=available_ram_gb,
            cpu_cores=cpu_cores,
            cpu_freq_ghz=cpu_freq_ghz,
            has_cuda=has_cuda,
            gpu_name=gpu_name,
            gpu_memory_gb=gpu_memory,
            platform=sys_platform,
            architecture=architecture,
        )

    def _detect_gpu(self) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Detecta si hay GPU NVIDIA disponible.
        Retorna: (has_cuda, gpu_name, gpu_memory_gb)
        """
        try:
            # Intentar usar nvidia-smi
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                if lines:
                    parts = lines[0].split(",")
                    gpu_name = parts[0].strip()
                    # Convertir de MiB a GB
                    gpu_memory = float(parts[1].strip().split()[0]) / 1024
                    return True, gpu_name, gpu_memory

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        return False, None, None

    def get_system_info(self) -> Dict:
        """Obtiene información del sistema en formato dict."""
        cap = self.capabilities
        return {
            "RAM Total": f"{cap.total_ram_gb:.1f} GB",
            "RAM Disponible": f"{cap.available_ram_gb:.1f} GB",
            "CPU Núcleos": cap.cpu_cores,
            "CPU Frecuencia": f"{cap.cpu_freq_ghz:.2f} GHz",
            "GPU": cap.gpu_name if cap.has_cuda else "No detectada",
            "GPU VRAM": f"{cap.gpu_memory_gb:.1f} GB" if cap.gpu_memory_gb else "N/A",
            "Sistema Operativo": cap.platform,
            "Arquitectura": cap.architecture,
        }

    def get_model_recommendations(self) -> List[ModelRecommendation]:
        """
        Genera recomendaciones de modelos basadas en las capacidades del sistema.
        """
        recommendations = []
        # Usar RAM total con un margen del 20% para el sistema operativo
        available_ram = self.capabilities.total_ram_gb * 0.8

        for model_name, req in self.MODEL_REQUIREMENTS.items():
            ram_needed = req["ram"]

            # Determinar si es recomendado
            # Se considera recomendado si tiene suficiente RAM con margen
            recommended = available_ram >= (ram_needed * 1.3)

            # Generar razón
            if available_ram < ram_needed:
                reason = (
                    f"Requiere {ram_needed} GB RAM, solo hay {available_ram:.1f} GB disponibles"
                )
            elif recommended:
                reason = "Compatible con tu sistema"
            else:
                reason = f"Podría funcionar pero requiere {ram_needed} GB RAM"

            recommendations.append(
                ModelRecommendation(
                    name=model_name,
                    size=req["size"],
                    ram_required_gb=ram_needed,
                    description=req["desc"],
                    recommended=recommended,
                    reason=reason,
                )
            )

        # Ordenar por RAM requerida
        recommendations.sort(key=lambda x: x.ram_required_gb)

        return recommendations

    def get_recommended_models(self) -> List[str]:
        """Retorna solo los nombres de los modelos recomendados."""
        recommendations = self.get_model_recommendations()
        return [rec.name for rec in recommendations if rec.recommended]

    def get_best_available_model(self) -> str:
        """
        Retorna el mejor modelo disponible según la RAM del sistema.
        Prioriza modelos más potentes si el sistema lo permite.
        """
        # Obtener modelos recomendados ordenados por capacidad (descendente)
        recommendations = self.get_model_recommendations()
        recommended = [rec for rec in recommendations if rec.recommended]

        if not recommended:
            # Si no hay modelos recomendados, usar el más pequeño
            return "llama3.2:1b"

        # Ordenar por RAM requerida (descendente) para obtener el más potente
        recommended.sort(key=lambda x: x.ram_required_gb, reverse=True)

        return recommended[0].name

    def can_run_ollama(self) -> Tuple[bool, str]:
        """
        Verifica si el sistema puede ejecutar Ollama.
        Retorna: (puede_ejecutar, razón)
        """
        # Requisitos mínimos para Ollama
        MIN_RAM_GB = 4
        MIN_DISK_GB = 10

        cap = self.capabilities

        if cap.total_ram_gb < MIN_RAM_GB:
            return False, f"Se requiere mínimo {MIN_RAM_GB} GB de RAM"

        # Verificar espacio en disco
        try:
            disk = psutil.disk_usage("/")
            free_gb = disk.free / (1024**3)
            if free_gb < MIN_DISK_GB:
                return False, f"Se requiere mínimo {MIN_DISK_GB} GB de espacio libre"
        except:
            pass

        # Si tiene GPU es mejor
        if cap.has_cuda:
            return True, f"Sistema compatible con aceleración GPU ({cap.gpu_name})"

        # Si no tiene GPU pero tiene suficiente RAM
        return True, "Sistema compatible (modo CPU)"

    def print_system_summary(self):
        """Imprime un resumen del sistema."""
        info = self.get_system_info()

        print("\n" + "=" * 70)
        print(" " * 20 + "ANÁLISIS DEL SISTEMA")
        print("=" * 70)

        for key, value in info.items():
            print(f"  {key:20}: {value}")

        print("=" * 70)

        # Recomendaciones de Ollama
        can_run, reason = self.can_run_ollama()
        if can_run:
            print(f"\n✓ Tu sistema PUEDE ejecutar Ollama: {reason}")
        else:
            print(f"\n✗ Tu sistema NO cumple los requisitos para Ollama: {reason}")
