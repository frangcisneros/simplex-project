"""
Procesador NLP optimizado para usar modelos de Ollama.

Este procesador utiliza la API HTTP de Ollama para comunicarse con modelos
locales de forma eficiente, sin necesidad de cargar modelos en memoria Python.
"""

import json
import logging
import requests
import time
from typing import Optional, Dict, Any

from .interfaces import NLPResult, OptimizationProblem, INLPProcessor
from .config import NLPModelType, DefaultSettings, PromptTemplates, ErrorMessages


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
            # Generar prompt para el modelo
            prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
                problem_text=natural_language_text
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
                timeout=300,  # 5 minutos máximo
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
        Extrae y valida el problema de optimización del texto generado.
        """
        try:
            # Buscar JSON en el texto usando diferentes patrones
            import re

            # Patrones para encontrar JSON
            patterns = [
                r'\{[^{}]*"objective_type"[^{}]*\}',  # JSON simple
                r"```json\s*(\{.*?\})\s*```",  # Bloque de código JSON
                r"```\s*(\{.*?\})\s*```",  # Bloque de código sin especificar
                r'(\{.*"objective_type".*\})',  # JSON multilinea
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # Limpiar el JSON encontrado
                        json_text = match.strip()
                        if json_text.startswith("```"):
                            json_text = (
                                json_text.replace("```json", "")
                                .replace("```", "")
                                .strip()
                            )

                        # Parsear JSON
                        data = json.loads(json_text)

                        # Validar estructura mínima
                        if not all(
                            key in data
                            for key in [
                                "objective_type",
                                "objective_coefficients",
                                "constraints",
                            ]
                        ):
                            continue

                        # Crear problema de optimización
                        problem = OptimizationProblem(
                            objective_type=data["objective_type"],
                            objective_coefficients=data["objective_coefficients"],
                            constraints=data["constraints"],
                            variable_names=data.get("variable_names"),
                        )

                        self.logger.info(
                            f"Successfully extracted optimization problem with {len(problem.objective_coefficients)} variables"
                        )
                        return problem

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        self.logger.debug(f"Failed to parse JSON match: {e}")
                        continue

            self.logger.warning("No valid JSON found in model response")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting optimization problem: {e}")
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

    def get_available_models(self) -> list:
        """
        Obtiene la lista de modelos disponibles en Ollama.
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model.get("name") for model in models]
            return []
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Descarga un modelo en Ollama.

        Args:
            model_name: Nombre del modelo a descargar (ej: "llama3.2:3b")

        Returns:
            True si se descargó correctamente, False si no
        """
        try:
            self.logger.info(f"Downloading model: {model_name}")

            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=1800,  # 30 minutos para descarga
            )

            if response.status_code == 200:
                # Procesar respuesta streaming
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("status"):
                                self.logger.info(f"Pull status: {data['status']}")
                        except json.JSONDecodeError:
                            continue

                self.logger.info(f"Model {model_name} downloaded successfully")
                return True
            else:
                self.logger.error(f"Failed to pull model: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False
