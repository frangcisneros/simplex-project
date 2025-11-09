"""
Procesamiento de lenguaje natural usando modelos Transformer.

Toma descripciones de problemas en español y extrae automáticamente
los coeficientes, restricciones y función objetivo para resolver
con algoritmos de optimización.
"""

import json
import re
import logging
from typing import Optional, Dict, Any, List
import time

try:
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForSeq2SeqLM,
        AutoModelForCausalLM,
        pipeline,
        BitsAndBytesConfig,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .interfaces import INLPProcessor, NLPResult, OptimizationProblem
from .config import (
    NLPModelType,
    ModelConfig,
    PromptTemplates,
    ErrorMessages,
    DefaultSettings,
)
from .complexity_analyzer import ModelSelector


class TransformerNLPProcessor(INLPProcessor):
    """
    Procesador avanzado que utiliza modelos de lenguaje para interpretar
    descripciones de problemas de optimización en español.

    Este procesador soporta múltiples modelos (como FLAN-T5, Mistral) y
    automatiza la extracción de información matemática necesaria para
    resolver problemas de optimización.

    Funcionalidades principales:
    - Selección automática del modelo óptimo según la complejidad del problema.
    - Generación de prompts especializados para extraer información estructurada.
    - Manejo de modelos con soporte para quantización y uso eficiente de recursos.
    """

    def __init__(
        self,
        model_type: Optional[NLPModelType] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        auto_select_model: bool = True,
    ):
        """
        Inicializa el procesador con un modelo específico o habilita la selección automática.

        Args:
            model_type (Optional[NLPModelType]): Tipo de modelo a usar. Si es None y auto_select_model=True,
                se seleccionará automáticamente.
            custom_config (Optional[Dict[str, Any]]): Configuración personalizada para el modelo.
            auto_select_model (bool): Si es True, selecciona automáticamente el modelo óptimo.
        """
        self.model_type = model_type
        self.auto_select_model = auto_select_model
        self.custom_config = custom_config

        # Inicializar el selector de modelos si está habilitado
        self.model_selector = ModelSelector() if auto_select_model else None

        # Variables para almacenar el modelo y su configuración
        self.config: Optional[Dict[str, Any]] = None
        self.tokenizer: Optional[Any] = None
        self.model: Optional[Any] = None
        self.pipeline: Optional[Any] = None
        self._is_loaded = False
        self._current_model_type: Optional[NLPModelType] = None

        # Configurar logging para registrar eventos importantes
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        """
        Verifica si el procesador puede ejecutarse en el sistema actual.

        Comprueba la disponibilidad de las librerías necesarias y ajusta
        configuraciones según los recursos del sistema (como GPU).

        Returns:
            bool: True si el procesador está disponible, False en caso contrario.
        """
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("La librería transformers no está disponible.")
            return False

        # Ajustar configuración si ya está inicializada
        if self.config is not None:
            if not torch.cuda.is_available() and self.config.get("load_in_4bit", False):
                self.logger.warning("CUDA no está disponible, deshabilitando quantización.")
                self.config["load_in_4bit"] = False
                self.config["load_in_8bit"] = False

        return True

    def _load_model(self, model_type: Optional[NLPModelType] = None) -> bool:
        """
        Carga el modelo de lenguaje en memoria.

        Args:
            model_type (Optional[NLPModelType]): Tipo de modelo a cargar. Si es None, usa self.model_type.

        Returns:
            bool: True si el modelo se cargó correctamente, False en caso de error.
        """
        # Determinar el modelo objetivo
        target_model = model_type or self.model_type or DefaultSettings.DEFAULT_MODEL

        # Evitar recargar el modelo si ya está cargado
        if self._is_loaded and self._current_model_type == target_model:
            return True

        # Liberar el modelo anterior si es necesario
        if self._is_loaded and self._current_model_type != target_model:
            # Verificar que _current_model_type no sea None antes de acceder a .value
            if self._current_model_type is not None:
                self.logger.info(f"Liberando modelo anterior: {self._current_model_type.value}")
            else:
                self.logger.warning("No hay un modelo cargado para liberar.")
            self._unload_model()

        if not self.is_available():
            return False

        try:
            model_name = target_model.value
            self.logger.info(f"Cargando modelo: {model_name}")

            # Configuración del modelo
            self.config = ModelConfig.DEFAULT_CONFIGS[target_model].copy()
            if self.custom_config:
                self.config.update(self.custom_config)

            # Configurar quantización si está habilitada
            quantization_config = None
            if self.config.get("load_in_4bit", False):
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
                )
            elif self.config.get("load_in_8bit", False):
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)

            # Cargar el tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

            # Cargar el modelo según el tipo
            if "t5" in model_name.lower():
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map=self.config.get("device_map", "auto"),
                    trust_remote_code=True,
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    device_map=self.config.get("device_map", "auto"),
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                )

            # Crear el pipeline para generación de texto
            task = "text2text-generation" if "t5" in model_name.lower() else "text-generation"
            self.pipeline = pipeline(
                task,
                model=self.model,
                tokenizer=self.tokenizer,
                **{
                    k: v
                    for k, v in self.config.items()
                    if k not in ["load_in_4bit", "load_in_8bit", "device_map"]
                },
            )

            self._is_loaded = True
            self._current_model_type = target_model
            self.logger.info(f"Modelo cargado exitosamente: {model_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {e}")
            return False

    def _unload_model(self):
        """
        Libera la memoria ocupada por el modelo actual.
        """
        if self.model is not None:
            del self.model
        if self.tokenizer is not None:
            del self.tokenizer
        if self.pipeline is not None:
            del self.pipeline

        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._is_loaded = False
        self._current_model_type = None

        # Limpiar caché de GPU si está disponible
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Convierte una descripción en español a un problema de optimización estructurado.

        Args:
            natural_language_text (str): Descripción del problema en lenguaje natural.

        Returns:
            NLPResult: Resultado con el problema extraído o un mensaje de error.
        """
        # Seleccionar modelo óptimo si está habilitado
        if self.auto_select_model and self.model_selector:
            selected_model = self.model_selector.select_model(natural_language_text)
            models_to_try = [selected_model]
            models_to_try.extend(self.model_selector.get_fallback_models(selected_model))
        elif self.model_type:
            models_to_try = [self.model_type]
        else:
            models_to_try = [DefaultSettings.DEFAULT_MODEL]

        # Intentar procesar con cada modelo en orden
        last_error = None
        for model_type in models_to_try:
            try:
                result = self._process_with_model(natural_language_text, model_type)
                if result.success:
                    return result
                last_error = result.error_message
            except Exception as e:
                self.logger.warning(f"El modelo {model_type.value} falló: {e}")
                last_error = str(e)
                continue

        # Si todos los modelos fallaron
        return NLPResult(
            success=False,
            error_message=last_error or ErrorMessages.INVALID_JSON_RESPONSE,
        )

    def _process_with_model(
        self, natural_language_text: str, model_type: NLPModelType
    ) -> NLPResult:
        """
        Procesa texto con un modelo específico.

        Args:
            natural_language_text (str): Descripción del problema en lenguaje natural.
            model_type (NLPModelType): Tipo de modelo a usar.

        Returns:
            NLPResult: Resultado con el problema extraído o un mensaje de error.
        """
        if not self._load_model(model_type):
            return NLPResult(success=False, error_message=ErrorMessages.MODEL_NOT_AVAILABLE)

        try:
            start_time = time.time()

            # Preparar prompt
            prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
                problem_text=natural_language_text.strip()
            )

            # Generar respuesta
            self.logger.info("Generando respuesta NLP...")
            if self.pipeline is None:
                self.logger.error("El pipeline del modelo no está cargado.")
                return NLPResult(success=False, error_message=ErrorMessages.MODEL_NOT_AVAILABLE)

            try:
                response = self.pipeline(prompt)
                self.logger.debug(f"Respuesta cruda del pipeline: {response}")
            except Exception as e:
                self.logger.error(f"Error en la ejecución del pipeline: {e}")
                raise

            # Procesar respuesta según el tipo de modelo
            try:
                if isinstance(response, list):
                    generated_text = response[0].get("generated_text", "")
                else:
                    generated_text = response.get("generated_text", "")

                self.logger.debug(f"Texto generado antes del procesamiento: '{generated_text}'")
            except Exception as e:
                self.logger.error(f"Error al extraer el texto generado de la respuesta: {e}")
                raise

            # Para modelos causales, extraer solo la parte nueva
            if self.model_type is not None and not "t5" in self.model_type.value.lower():
                generated_text = generated_text.replace(prompt, "").strip()

            self.logger.info(f"Respuesta generada por el modelo: {generated_text}")

            # Extraer JSON de la respuesta
            problem = self._extract_optimization_problem(generated_text)

            # Si no se pudo extraer JSON, intentar con el texto original del problema
            if not problem:
                self.logger.info(
                    "Falló la extracción del JSON, intentando con el problema original..."
                )
                problem = self._extract_from_complex_problem(natural_language_text)

            processing_time = time.time() - start_time
            confidence_score = self._calculate_confidence(generated_text, problem)

            if problem:
                self.logger.info(f"Problema extraído exitosamente en {processing_time:.2f}s")
                return NLPResult(success=True, problem=problem, confidence_score=confidence_score)
            else:
                return NLPResult(success=False, error_message=ErrorMessages.INVALID_JSON_RESPONSE)

        except Exception as e:
            self.logger.error(f"Error procesando el texto: {e}")
            # Intentar extracción de respaldo antes de fallar
            try:
                self.logger.info("Intentando extracción de respaldo...")
                problem = self._extract_from_complex_problem(natural_language_text)
                if problem:
                    processing_time = time.time() - start_time
                    return NLPResult(
                        success=True,
                        problem=problem,
                        confidence_score=0.6,  # Confianza media para respaldo
                    )
            except Exception as fallback_error:
                self.logger.error(f"Falló también la extracción de respaldo: {fallback_error}")

            return NLPResult(success=False, error_message=f"Error en el procesamiento: {str(e)}")

    def _extract_optimization_problem(self, response_text: str) -> Optional[OptimizationProblem]:
        """
        Busca y parsea el JSON con el problema en la respuesta del modelo.

        Usa varios patrones regex para encontrar JSON en diferentes formatos
        (bloques de código, JSON directo, etc.), valida la estructura, normaliza
        los tipos de objetivo, y valida que todos los coeficientes sean numéricos.

        Args:
            response_text (str): Texto generado por el modelo de lenguaje.

        Returns:
            Optional[OptimizationProblem]: Objeto con el problema extraído si se encontró y validó el JSON, None si no pudo extraerlo.
        """
        try:
            # Limpiar el texto de respuesta
            cleaned_text = response_text.strip()

            self.logger.debug(f"Intentando extraer JSON de la respuesta: {cleaned_text[:200]}...")

            # Buscar JSON en la respuesta usando múltiples patrones
            json_patterns = [
                r"```json\s*(\{[\s\S]*?\})\s*```",  # JSON en bloques de código (prioridad)
                r"```\s*(\{[\s\S]*?\})\s*```",  # JSON en bloques sin especificar lenguaje
                r"JSON:\s*(\{[\s\S]*?\})",  # JSON después de etiqueta
                r"\{[\s\S]*?\}",  # Patrón más permisivo
            ]

            all_matches = []
            for pattern in json_patterns:
                matches = re.findall(pattern, cleaned_text, re.DOTALL | re.IGNORECASE)
                all_matches.extend(matches)

            # Si no encuentra JSON, intentar extraer manualmente del problema complejo
            if not all_matches:
                self.logger.warning("No se encontraron patrones de JSON en la respuesta")
                return self._extract_from_complex_problem(response_text)

            self.logger.debug(f"Se encontraron {len(all_matches)} posibles coincidencias de JSON")

            for idx, json_str in enumerate(all_matches):
                try:
                    # Limpiar el JSON string
                    json_str = json_str.strip()
                    if not json_str.startswith("{"):
                        continue

                    self.logger.debug(
                        f"Intentando parsear coincidencia de JSON {idx + 1}: {json_str[:100]}..."
                    )
                    data = json.loads(json_str)

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

                    # Normalizar tipo de objetivo
                    obj_type = str(data["objective_type"]).lower()
                    if obj_type not in ["maximize", "minimize"]:
                        # Intentar mapear variaciones comunes
                        if any(word in obj_type for word in ["max", "maximiz"]):
                            obj_type = "maximize"
                        elif any(word in obj_type for word in ["min", "minimiz"]):
                            obj_type = "minimize"
                        else:
                            continue

                    # Validar coeficientes objetivos
                    obj_coeffs = data["objective_coefficients"]
                    if not isinstance(obj_coeffs, list) or not all(
                        isinstance(x, (int, float)) for x in obj_coeffs
                    ):
                        continue

                    # Validar restricciones
                    constraints = data["constraints"]
                    if not isinstance(constraints, list) or len(constraints) == 0:
                        continue

                    valid_constraints = []
                    for constraint in constraints:
                        if (
                            isinstance(constraint, dict)
                            and "coefficients" in constraint
                            and "operator" in constraint
                            and "rhs" in constraint
                        ):

                            coeffs = constraint["coefficients"]
                            if (
                                isinstance(coeffs, list)
                                and len(coeffs) == len(obj_coeffs)
                                and all(isinstance(x, (int, float)) for x in coeffs)
                            ):
                                valid_constraints.append(constraint)

                    if not valid_constraints:
                        continue

                    # Crear problema de optimización
                    self.logger.info(
                        f"JSON parseado y validado exitosamente desde la coincidencia {idx + 1}"
                    )
                    return OptimizationProblem(
                        objective_type=obj_type,
                        objective_coefficients=obj_coeffs,
                        constraints=valid_constraints,
                        variable_names=data.get("variable_names"),
                    )

                except json.JSONDecodeError as e:
                    self.logger.debug(
                        f"Error de decodificación JSON en la coincidencia {idx + 1}: {e}"
                    )
                    continue
                except Exception as e:
                    self.logger.debug(f"Error de validación en la coincidencia {idx + 1}: {e}")
                    continue

            self.logger.warning("No se encontró un JSON válido en ninguna de las coincidencias")
            return None

        except Exception as e:
            self.logger.error(f"Error extrayendo el problema de optimización: {e}")
            return None

    def _extract_from_complex_problem(self, text: str) -> Optional[OptimizationProblem]:
        """
        Método de respaldo cuando el modelo no genera un JSON válido.

        Intenta extraer información básica del texto usando patrones generales,
        pero no tiene conocimiento de problemas específicos hardcodeados.
        """
        try:
            # Por ahora, este método no tiene una extracción genérica implementada
            # Si el modelo no genera JSON válido, simplemente retornamos None
            self.logger.warning("No hay extracción de respaldo disponible para este problema")
            return None

        except Exception as e:
            self.logger.error(f"Error en la extracción de respaldo: {e}")
            return None

    def _calculate_confidence(
        self, response_text: str, problem: Optional[OptimizationProblem]
    ) -> float:
        """
        Estima qué tan confiable es el problema extraído.

        Analiza si el JSON estaba bien formado, si el problema está completo,
        si la respuesta tiene texto irrelevante, etc. Un score alto (>0.8) significa
        que el modelo entendió bien el problema.

        Args:
            response_text (str): Texto generado por el modelo.
            problem (Optional[OptimizationProblem]): Problema extraído (None si falló).

        Returns:
            float: Número entre 0 (no confiable) y 1 (muy confiable).
        """
        if not problem:
            return 0.0

        confidence = 0.5  # Base

        # Bonus por estructura JSON válida
        if "{" in response_text and "}" in response_text:
            confidence += 0.2

        # Bonus por completitud del problema
        if len(problem.constraints) > 0:
            confidence += 0.1

        if len(problem.objective_coefficients) > 0:
            confidence += 0.1

        # Penalty por respuesta muy larga o con texto irrelevante
        if len(response_text) > 1000:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))


class MockNLPProcessor(INLPProcessor):
    """
    Procesador simple para pruebas sin necesidad de modelos grandes.

    No usa modelos de lenguaje reales. Devuelve un problema de ejemplo siempre.
    Útil para testing, demos, o cuando no tenemos los modelos descargados.
    Es instantáneo y no consume memoria.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        return True

    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Simula el procesamiento NLP con un problema de ejemplo.
        Ahora detecta problemas de transporte y genera la cantidad correcta de variables.
        """
        self.logger.info("Usando procesador NLP simulado")

        text_lower = natural_language_text.lower()

        # Detectar tipo de optimización
        if "maximiz" in text_lower or "maximum" in text_lower:
            obj_type = "maximize"
        elif "minimiz" in text_lower or "minimum" in text_lower:
            obj_type = "minimize"
        else:
            obj_type = "maximize"  # Por defecto

        # Detectar problema de transporte: buscar "X almacenes" y "Y tiendas"
        import re

        almacenes = 0
        tiendas = 0
        almacenes_match = re.search(r"(\d+)\s+almacen", text_lower)
        tiendas_match = re.search(r"(\d+)\s+tienda", text_lower)
        if almacenes_match and tiendas_match:
            almacenes = int(almacenes_match.group(1))
            tiendas = int(tiendas_match.group(1))
        if almacenes > 0 and tiendas > 0:
            n_vars = almacenes * tiendas
            variable_names = [f"x{i+1}" for i in range(n_vars)]
            # Coeficientes y restricciones dummy
            objective_coefficients = [1.0 for _ in range(n_vars)]
            constraints = []
            # Restricciones de oferta (una por almacén)
            for i in range(almacenes):
                coefs = [1.0 if j // tiendas == i else 0.0 for j in range(n_vars)]
                constraints.append({"coefficients": coefs, "operator": "<=", "rhs": 100.0})
            # Restricciones de demanda (una por tienda)
            for i in range(tiendas):
                coefs = [1.0 if j % tiendas == i else 0.0 for j in range(n_vars)]
                constraints.append({"coefficients": coefs, "operator": ">=", "rhs": 50.0})
            problem = OptimizationProblem(
                objective_type=obj_type,
                objective_coefficients=objective_coefficients,
                constraints=constraints,
                variable_names=variable_names,
            )
            return NLPResult(success=True, problem=problem, confidence_score=0.9)

        # Problema de dieta
        if "dieta" in text_lower or "alimento" in text_lower:
            alimentos = re.findall(r"pan|pollo|vegetales|carne|arroz|leche", text_lower)
            if not alimentos:
                alimentos = ["pan", "pollo", "vegetales"]
            n_vars = len(alimentos)
            variable_names = alimentos
            objective_coefficients = [2.0 for _ in range(n_vars)]
            constraints = [
                {
                    "coefficients": [150.0, 300.0, 80.0][:n_vars],
                    "operator": ">=",
                    "rhs": 2000.0,
                },  # calorías
                {
                    "coefficients": [5.0, 25.0, 3.0][:n_vars],
                    "operator": ">=",
                    "rhs": 50.0,
                },  # proteína
                {
                    "coefficients": [3.0, 0.0, 8.0][:n_vars],
                    "operator": ">=",
                    "rhs": 30.0,
                },  # fibra
            ]
            problem = OptimizationProblem(
                objective_type="minimize",
                objective_coefficients=objective_coefficients,
                constraints=constraints,
                variable_names=variable_names,
            )
            return NLPResult(success=True, problem=problem, confidence_score=0.9)

        # Problema de producción
        if "fabrica" in text_lower or "produccion" in text_lower or "carpinteria" in text_lower:
            productos = re.findall(r"mesas|sillas|producto\s*[a-z]", text_lower)
            if not productos:
                productos = ["mesas", "sillas"]
            n_vars = len(productos)
            variable_names = productos
            objective_coefficients = [80.0, 50.0][:n_vars]
            constraints = [
                {
                    "coefficients": [4.0, 2.0][:n_vars],
                    "operator": "<=",
                    "rhs": 200.0,
                },  # horas
                {
                    "coefficients": [6.0, 3.0][:n_vars],
                    "operator": "<=",
                    "rhs": 300.0,
                },  # madera
            ]
            problem = OptimizationProblem(
                objective_type="maximize",
                objective_coefficients=objective_coefficients,
                constraints=constraints,
                variable_names=variable_names,
            )
            return NLPResult(success=True, problem=problem, confidence_score=0.9)

        # Problema ejemplo simple (por defecto)
        problem = OptimizationProblem(
            objective_type=obj_type,
            objective_coefficients=[1.0, 2.0],
            constraints=[
                {"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0},
                {"coefficients": [2.0, 1.0], "operator": "<=", "rhs": 15.0},
            ],
        )
        return NLPResult(success=True, problem=problem, confidence_score=0.8)
