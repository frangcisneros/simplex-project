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
    Usa modelos de lenguaje avanzados para entender problemas de optimización.

    Soporta varios modelos (FLAN-T5, Mistral, etc.) que pueden leer descripciones
    en español y extraer automáticamente toda la información matemática necesaria:
    qué maximizar/minimizar, las restricciones, y los coeficientes.

    El procesador maneja la carga del modelo, la generación de prompts, y la
    extracción de información estructurada del texto generado.

    Selecciona automáticamente el modelo óptimo basándose en:
    - Complejidad del problema
    - Capacidades del sistema (RAM, GPU, CPU)
    """

    def __init__(
        self,
        model_type: Optional[NLPModelType] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        auto_select_model: bool = True,
    ):
        """
        Prepara el procesador con un modelo específico o selección automática.

        El modelo no se carga inmediatamente para ahorrar memoria. Se cargará
        cuando se procese el primer texto.

        Args:
            model_type: Qué modelo usar. Si es None y auto_select_model=True,
                       se seleccionará automáticamente según el problema.
            custom_config: Parámetros adicionales como temperature, max_length, etc.
            auto_select_model: Si es True, selecciona automáticamente el modelo óptimo
        """
        self.model_type = model_type
        self.auto_select_model = auto_select_model
        self.custom_config = custom_config

        # Inicializar selector de modelos si está habilitado
        self.model_selector = ModelSelector() if auto_select_model else None

        # Estas se inicializarán cuando se cargue el modelo
        self.config: Optional[Dict[str, Any]] = None
        self.tokenizer: Optional[Any] = None
        self.model: Optional[Any] = None
        self.pipeline: Optional[Any] = None
        self._is_loaded = False
        self._current_model_type: Optional[NLPModelType] = None

        # Configurar logging
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        """
        Chequea si podemos usar el procesador en este sistema.

        Verifica que las librerías estén instaladas, que haya GPU disponible
        (si el modelo lo requiere), y ajusta la configuración si es necesario.
        """
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("transformers library not available")
            return False

        # Solo verificar config si ya está inicializado
        if self.config is not None:
            if not torch.cuda.is_available() and self.config.get("load_in_4bit", False):
                self.logger.warning("CUDA not available, disabling quantization")
                self.config["load_in_4bit"] = False
                self.config["load_in_8bit"] = False

        return True

    def _load_model(self, model_type: Optional[NLPModelType] = None) -> bool:
        """
        Carga el modelo de lenguaje en memoria.

        Descarga el modelo si no está en caché, lo carga con la configuración
        adecuada (quantización, device_map), y crea el pipeline para generar texto.

        Args:
            model_type: Tipo de modelo a cargar. Si es None, usa self.model_type
        """
        # Determinar qué modelo cargar
        target_model = model_type or self.model_type or DefaultSettings.DEFAULT_MODEL

        # Si ya está cargado el modelo correcto, no hacer nada
        if self._is_loaded and self._current_model_type == target_model:
            return True

        # Si hay un modelo diferente cargado, liberarlo primero
        if self._is_loaded and self._current_model_type != target_model:
            self.logger.info(
                f"Unloading previous model: {self._current_model_type.value}"
            )
            self._unload_model()

        if not self.is_available():
            return False

        try:
            model_name = target_model.value
            self.logger.info(f"Loading model: {model_name}")

            # Obtener configuración del modelo
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

            # Cargar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )

            # Cargar modelo según el tipo
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

            # Crear pipeline
            task = (
                "text2text-generation"
                if "t5" in model_name.lower()
                else "text-generation"
            )
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
            self.logger.info(f"Model loaded successfully: {model_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False

    def _unload_model(self):
        """Libera la memoria del modelo actual."""
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

        Lee el texto, selecciona automáticamente el modelo óptimo (si está habilitado),
        genera un prompt especializado, pide al modelo que extraiga la información,
        y parsea el JSON resultante. Si el modelo falla, intenta con modelos alternativos.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural

        Returns:
            NLPResult con el problema extraído, un score de confianza, o un error
        """
        # Seleccionar modelo óptimo si está habilitado
        if self.auto_select_model and self.model_selector:
            selected_model = self.model_selector.select_model(natural_language_text)
            models_to_try = [selected_model]
            # Agregar fallbacks
            models_to_try.extend(
                self.model_selector.get_fallback_models(selected_model)
            )
        elif self.model_type:
            models_to_try = [self.model_type]
        else:
            models_to_try = [DefaultSettings.DEFAULT_MODEL]

        # Intentar con cada modelo en orden
        last_error = None
        for model_type in models_to_try:
            try:
                result = self._process_with_model(natural_language_text, model_type)
                if result.success:
                    return result
                last_error = result.error_message
            except Exception as e:
                self.logger.warning(f"Model {model_type.value} failed: {e}")
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
            natural_language_text: Descripción del problema en lenguaje natural
            model_type: Tipo de modelo a usar

        Returns:
            NLPResult con el problema extraído, un score de confianza, o un error
        """
        if not self._load_model(model_type):
            return NLPResult(
                success=False, error_message=ErrorMessages.MODEL_NOT_AVAILABLE
            )

        try:
            start_time = time.time()

            # Preparar prompt
            prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
                problem_text=natural_language_text.strip()
            )

            # Generar respuesta
            self.logger.info("Generating NLP response...")
            if self.pipeline is None:
                self.logger.error("Model pipeline is not loaded.")
                return NLPResult(
                    success=False, error_message=ErrorMessages.MODEL_NOT_AVAILABLE
                )

            try:
                response = self.pipeline(prompt)
                self.logger.debug(f"Raw pipeline response: {response}")
            except Exception as e:
                self.logger.error(f"Error in pipeline execution: {e}")
                raise

            # Procesar respuesta según el tipo de modelo
            try:
                if isinstance(response, list):
                    generated_text = response[0].get("generated_text", "")
                else:
                    generated_text = response.get("generated_text", "")

                self.logger.debug(
                    f"Generated text before processing: '{generated_text}'"
                )
            except Exception as e:
                self.logger.error(f"Error extracting generated text from response: {e}")
                raise

            # Para modelos causales, extraer solo la parte nueva
            if not "t5" in self.model_type.value.lower():
                generated_text = generated_text.replace(prompt, "").strip()

            self.logger.info(f"Model generated response: {generated_text}")

            # Extraer JSON de la respuesta
            problem = self._extract_optimization_problem(generated_text)

            # Si no se pudo extraer JSON, intentar con el texto original del problema
            if not problem:
                self.logger.info(
                    "Failed to extract from model response, trying fallback..."
                )
                problem = self._extract_from_complex_problem(natural_language_text)

            processing_time = time.time() - start_time
            confidence_score = self._calculate_confidence(generated_text, problem)

            if problem:
                self.logger.info(
                    f"Successfully extracted problem in {processing_time:.2f}s"
                )
                return NLPResult(
                    success=True, problem=problem, confidence_score=confidence_score
                )
            else:
                return NLPResult(
                    success=False, error_message=ErrorMessages.INVALID_JSON_RESPONSE
                )

        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            # Intentar extracción de respaldo antes de fallar
            try:
                self.logger.info("Attempting fallback extraction...")
                problem = self._extract_from_complex_problem(natural_language_text)
                if problem:
                    processing_time = time.time() - start_time
                    return NLPResult(
                        success=True,
                        problem=problem,
                        confidence_score=0.6,  # Confianza media para respaldo
                    )
            except Exception as fallback_error:
                self.logger.error(f"Fallback extraction also failed: {fallback_error}")

            return NLPResult(success=False, error_message=f"Processing error: {str(e)}")

    def _extract_optimization_problem(
        self, response_text: str
    ) -> Optional[OptimizationProblem]:
        """
        Busca y parsea el JSON con el problema en la respuesta del modelo.

        Usa varios patrones regex para encontrar JSON en diferentes formatos
        (bloques de código, JSON directo, etc.), valida la estructura, normaliza
        los tipos de objetivo, y valida que todos los coeficientes sean numéricos.

        Args:
            response_text: Texto generado por el modelo de lenguaje

        Returns:
            OptimizationProblem si encontró y validó el JSON, None si no pudo extraerlo
        """
        try:
            # Limpiar el texto de respuesta
            cleaned_text = response_text.strip()

            self.logger.debug(
                f"Attempting to extract JSON from response: {cleaned_text[:200]}..."
            )

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
                self.logger.warning("No JSON patterns found in response")
                return self._extract_from_complex_problem(response_text)

            self.logger.debug(f"Found {len(all_matches)} potential JSON matches")

            for idx, json_str in enumerate(all_matches):
                try:
                    # Limpiar el JSON string
                    json_str = json_str.strip()
                    if not json_str.startswith("{"):
                        continue

                    self.logger.debug(
                        f"Attempting to parse JSON match {idx + 1}: {json_str[:100]}..."
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
                        f"Successfully parsed and validated JSON from match {idx + 1}"
                    )
                    return OptimizationProblem(
                        objective_type=obj_type,
                        objective_coefficients=obj_coeffs,
                        constraints=valid_constraints,
                        variable_names=data.get("variable_names"),
                    )

                except json.JSONDecodeError as e:
                    self.logger.debug(f"JSON decode error on match {idx + 1}: {e}")
                    continue
                except Exception as e:
                    self.logger.debug(f"Validation error on match {idx + 1}: {e}")
                    continue

            self.logger.warning("No valid JSON found in any matches")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting optimization problem: {e}")
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
            self.logger.warning("No fallback extraction available for this problem")
            return None

        except Exception as e:
            self.logger.error(f"Error in fallback extraction: {e}")
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
            response_text: Texto generado por el modelo
            problem: Problema extraído (None si falló)

        Returns:
            Número entre 0 (no confiable) y 1 (muy confiable)
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
        self.logger.info("Using mock NLP processor")

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
                constraints.append(
                    {"coefficients": coefs, "operator": "<=", "rhs": 100.0}
                )
            # Restricciones de demanda (una por tienda)
            for i in range(tiendas):
                coefs = [1.0 if j % tiendas == i else 0.0 for j in range(n_vars)]
                constraints.append(
                    {"coefficients": coefs, "operator": ">=", "rhs": 50.0}
                )
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
        if (
            "fabrica" in text_lower
            or "produccion" in text_lower
            or "carpinteria" in text_lower
        ):
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
