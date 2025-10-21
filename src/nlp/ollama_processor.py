"""
Procesador NLP optimizado para usar modelos de Ollama.

Este procesador utiliza la API HTTP de Ollama para comunicarse con modelos
locales de forma eficiente, sin necesidad de cargar modelos en memoria Python.
"""

import json
import logging
import requests
import time
import re
from typing import Optional, Dict, Any

from .interfaces import NLPResult, OptimizationProblem, INLPProcessor
from .config import NLPModelType, DefaultSettings, PromptTemplates, ErrorMessages
from .problem_structure_detector import ProblemStructureDetector


class OllamaNLPProcessor(INLPProcessor):
    """
    Procesador NLP que usa la API de Ollama para generar respuestas.

    Ollama maneja automáticamente la carga/descarga de modelos según
    la memoria disponible, sin necesidad de librerías complejas.
    """

    def __init__(
        self,
        model_type: Optional[NLPModelType] = None,
        ollama_url: str = "http://localhost:11434",
        custom_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa el procesador Ollama.

        Args:
            model_type: Modelo de Ollama a usar
            ollama_url: URL del servidor Ollama (por defecto localhost:11434)
            custom_config: Configuración personalizada para el modelo
        """
        self.model_type = model_type or DefaultSettings.DEFAULT_MODEL
        self.ollama_url = ollama_url.rstrip("/")
        self.custom_config = custom_config or {}

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Cargar configuración del modelo
        from .config import ModelConfig

        self.config = ModelConfig.DEFAULT_CONFIGS.get(self.model_type, {}).copy()
        self.config.update(self.custom_config)

        # Inicializar el detector de estructura
        self.structure_detector = ProblemStructureDetector()

    def is_available(self) -> bool:
        """
        Verifica si Ollama está ejecutándose y el modelo está disponible.
        """
        try:
            # Verificar que Ollama esté ejecutándose
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                self.logger.error("Ollama server not responding")
                return False

            # Verificar que el modelo esté disponible
            models = response.json().get("models", [])
            model_name = self.model_type.value

            # Buscar el modelo en la lista (puede tener tags adicionales)
            model_found = any(model_name in model.get("name", "") for model in models)

            if not model_found:
                self.logger.warning(
                    f"Model {model_name} not found in Ollama. Available models:"
                )
                for model in models:
                    self.logger.warning(f"  - {model.get('name')}")
                return False

            return True

        except requests.RequestException as e:
            self.logger.error(f"Cannot connect to Ollama: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking Ollama availability: {e}")
            return False

    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Procesa texto en lenguaje natural y extrae un problema de optimización.

        Args:
            natural_language_text: Descripción del problema en español

        Returns:
            NLPResult con el problema extraído o información del error
        """
        if not self.is_available():
            return NLPResult(
                success=False,
                error_message="Ollama no está disponible o el modelo no está descargado",
            )

        try:
            # 1. Analizar estructura para crear una pista para el modelo
            structure = self.structure_detector.detect_structure(natural_language_text)

            # Generar hint específico según tipo de problema
            problem_type = structure["problem_type"]
            expected_vars = structure["expected_variables"]

            if problem_type == "diet":
                foods = structure.get("product_names", [])
                structure_hint = (
                    f"Este es un problema de DIETA ÓPTIMA. "
                    f"Debes identificar {expected_vars} variables de decisión (alimentos): {', '.join(foods)}. "
                    f"Las restricciones son requisitos nutricionales MÍNIMOS (>=). "
                    f"El objetivo es MINIMIZAR el costo total."
                )
            elif problem_type == "transport":
                routes = structure.get("product_names", [])
                structure_hint = (
                    f"Este es un problema de TRANSPORTE. "
                    f"Debes identificar {expected_vars} variables de decisión (rutas de transporte). "
                    f"Incluye restricciones de capacidad de almacenes (<=) y demanda de tiendas (>=). "
                    f"El objetivo es MINIMIZAR el costo total de transporte."
                )
            elif problem_type == "multi_facility":
                structure_hint = (
                    f"Este es un problema MULTI-INSTALACIÓN. "
                    f"Debes crear {expected_vars} variables (combinaciones planta×producto). "
                    f"Asegúrate de incluir TODAS las combinaciones posibles."
                )
            else:
                structure_hint = (
                    f"Se ha detectado un problema de tipo '{problem_type}'. "
                    f"Se esperan aproximadamente {expected_vars} variables."
                )

            self.logger.info(f"Generated hint for model: {structure_hint}")

            # 2. Generar prompt para el modelo, inyectando la pista
            prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
                problem_text=natural_language_text, structure_analysis=structure_hint
            )

            # Configurar petición a Ollama
            request_data = {
                "model": self.model_type.value,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get("temperature", 0.1),
                    "top_p": self.config.get("top_p", 0.9),
                    "num_predict": self.config.get("max_tokens", 2048),
                },
            }

            self.logger.info(f"Generating response with model: {self.model_type.value}")
            start_time = time.time()

            # Llamar a la API de Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=request_data,
                timeout=600,  # 10 minutos máximo para problemas complejos
            )

            elapsed_time = time.time() - start_time

            if response.status_code != 200:
                self.logger.error(
                    f"Ollama API error: {response.status_code} - {response.text}"
                )
                return NLPResult(
                    success=False,
                    error_message=f"Error en API de Ollama: {response.status_code}",
                )

            # Extraer respuesta
            response_data = response.json()
            generated_text = response_data.get("response", "").strip()

            if not generated_text:
                self.logger.warning("Ollama returned empty response")
                return NLPResult(
                    success=False, error_message="El modelo no generó ninguna respuesta"
                )

            self.logger.info(f"Model response generated in {elapsed_time:.1f}s")
            self.logger.debug(f"Generated text: {generated_text[:200]}...")

            # Extraer problema de optimización de la respuesta
            problem = self._extract_optimization_problem(generated_text)

            if problem:
                confidence = self._calculate_confidence(generated_text, problem)
                return NLPResult(
                    success=True, problem=problem, confidence_score=confidence
                )
            else:
                return NLPResult(
                    success=False, error_message=ErrorMessages.INVALID_JSON_RESPONSE
                )

        except requests.Timeout:
            self.logger.error("Timeout waiting for Ollama response")
            return NLPResult(
                success=False, error_message="Timeout esperando respuesta del modelo"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return NLPResult(success=False, error_message=f"Error inesperado: {str(e)}")

    def _extract_optimization_problem(self, text: str) -> Optional[OptimizationProblem]:
        """
        Extrae y valida el problema de optimización del texto generado de forma robusta.
        """
        try:
            # 1. Buscar el inicio y fin del bloque JSON
            start_index = text.find("{")
            end_index = text.rfind("}")

            if start_index == -1 or end_index == -1 or end_index < start_index:
                self.logger.warning(
                    "No se encontró un bloque JSON delimitado por llaves en la respuesta."
                )
                return None

            json_str = text[start_index : end_index + 1]

            # 2. (Opcional pero recomendado) Limpiar errores comunes antes de parsear
            # Eliminar comas finales en arrays o diccionarios, que son un error común de JSON
            json_str = re.sub(r",\s*([\]\}])", r"\1", json_str)

            self.logger.debug(
                f"Intentando parsear el siguiente bloque JSON: {json_str[:300]}..."
            )

            # 3. Parsear el JSON limpio
            data = json.loads(json_str)

            # 4. Validar la estructura mínima
            if not all(
                key in data
                for key in [
                    "objective_type",
                    "objective_coefficients",
                    "constraints",
                ]
            ):
                self.logger.warning(
                    "El JSON extraído no tiene la estructura requerida."
                )
                return None

            # 5. Crear el objeto OptimizationProblem
            problem = OptimizationProblem(
                objective_type=data["objective_type"],
                objective_coefficients=data["objective_coefficients"],
                constraints=data["constraints"],
                variable_names=data.get("variable_names"),
            )

            self.logger.info(
                f"Problema de optimización extraído con éxito con {len(problem.objective_coefficients)} variables."
            )
            return problem

        except json.JSONDecodeError as e:
            self.logger.error(
                f"Error al decodificar el JSON extraído: {e}. Contenido: '{json_str[:300]}...'"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Error inesperado al extraer el problema de optimización: {e}"
            )
            return None

    def _calculate_confidence(
        self, response_text: str, problem: OptimizationProblem
    ) -> float:
        """
        Calcula un score de confianza basado en la calidad de la respuesta.
        """
        try:
            confidence = 0.5  # Base confidence

            # Factores que aumentan confianza
            if len(problem.objective_coefficients) > 0:
                confidence += 0.2

            if len(problem.constraints) > 0:
                confidence += 0.2

            if problem.variable_names and len(problem.variable_names) == len(
                problem.objective_coefficients
            ):
                confidence += 0.1

            # Verificar consistencia dimensional
            expected_vars = len(problem.objective_coefficients)
            constraints_ok = all(
                len(c.get("coefficients", [])) == expected_vars
                for c in problem.constraints
            )
            if constraints_ok:
                confidence += 0.2

            return min(confidence, 1.0)

        except Exception:
            return 0.3  # Confianza baja si hay errores
