"""
Generadores de modelos de optimización para diferentes solvers.

Cada solver (Simplex, PuLP, OR-Tools) espera su propia estructura de datos.
Estos generadores toman nuestro OptimizationProblem estándar y lo convierten
al formato específico que necesita cada solver.
"""

import logging
from typing import Dict, Any, List, Tuple
from abc import ABC, abstractmethod

try:
    import pulp

    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

try:
    from ortools.linear_solver import pywraplp

    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from .interfaces import IModelGenerator, OptimizationProblem, IModelValidator


class SimplexModelGenerator(IModelGenerator):
    """
    Convierte problemas a formato de matrices para el algoritmo Simplex.

    El solver Simplex espera el problema en forma estándar:
    - c: vector de coeficientes de la función objetivo
    - A: matriz de coeficientes de restricciones
    - b: vector de lados derechos de las restricciones

    Este generador transforma OptimizationProblem a ese formato,
    manejando restricciones >= y de igualdad.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Transforma el problema a formato de matrices listo para Simplex.

        Proceso:
        1. Extrae coeficientes c de la función objetivo
        2. Construye matriz A con coeficientes de restricciones
        3. Convierte TODAS las restricciones a forma estándar (<=)
        4. Divide restricciones = en dos restricciones
        5. Valida que todas las dimensiones coincidan

        Para minimización: se convierte a maximización (cambiar signo de c)

        Args:
            problem: Problema de optimización estructurado

        Returns:
            Dict con 'c', 'A', 'b', 'maximize' y 'variable_names' para SimplexSolver
        """
        try:
            # Extraer función objetivo
            c = problem.objective_coefficients
            is_minimize = problem.objective_type == "minimize"

            # Si es minimización, convertir a maximización negando los coeficientes
            if is_minimize:
                c = [-coeff for coeff in c]
                maximize = True  # Ahora es maximización
            else:
                maximize = True

            # Construir matriz A y vector b
            A = []
            b = []
            constraint_types = []

            for constraint in problem.constraints:
                coeffs = constraint["coefficients"]
                operator = constraint["operator"]
                rhs = constraint["rhs"]

                # Convertir TODAS las restricciones a forma estándar (<=)
                if operator == ">=":
                    # Convertir >= a <= multiplicando por -1
                    coeffs = [-coeff for coeff in coeffs]
                    rhs = -rhs
                    constraint_types.append("<=")
                elif operator == "=":
                    # Para igualdad, agregar dos restricciones (<= y >=)
                    A.append(coeffs)
                    b.append(rhs)
                    constraint_types.append("<=")
                    A.append([-coeff for coeff in coeffs])
                    b.append(-rhs)
                    constraint_types.append("<=")
                    continue
                else:
                    constraint_types.append(operator)

                A.append(coeffs)
                b.append(rhs)

            # Validar dimensiones
            if not A or not b:
                raise ValueError("No valid constraints found")

            if len(set(len(row) for row in A)) > 1:
                raise ValueError("Inconsistent constraint dimensions")

            if len(A[0]) != len(c):
                raise ValueError("Dimension mismatch between objective and constraints")

            model = {
                "c": c,
                "A": A,
                "b": b,
                "maximize": maximize,
                "variable_names": problem.variable_names,
                "is_minimization": is_minimize,  # Para ajustar el resultado final
                "constraint_types": constraint_types,
            }

            self.logger.info(
                f"Generated Simplex model: {len(c)} vars, {len(A)} constraints"
            )
            return model

        except Exception as e:
            self.logger.error(f"Error generating Simplex model: {e}")
            raise


class PuLPModelGenerator(IModelGenerator):
    """
    Genera modelos usando la librería PuLP de Python.

    PuLP es una librería popular para modelado de optimización. Tiene su propio
    sistema de variables, restricciones y funciones objetivo. Este generador
    crea objetos PuLP a partir de nuestro formato estándar.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not PULP_AVAILABLE:
            raise ImportError("PuLP library not available")

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Crea un problema PuLP con variables, objetivo y restricciones.

        Construye objetos LpVariable para cada variable de decisión,
        define la función objetivo usando lpSum, y agrega cada restricción
        con su operador correspondiente (<=, >=, =).
        """
        try:
            # Crear problema
            sense = (
                pulp.LpMaximize
                if problem.objective_type == "maximize"
                else pulp.LpMinimize
            )
            prob = pulp.LpProblem("NLP_Generated_Problem", sense)

            # Crear variables
            num_vars = len(problem.objective_coefficients)
            if problem.variable_names:
                var_names = problem.variable_names
            else:
                var_names = [f"x{i+1}" for i in range(num_vars)]

            variables = pulp.LpVariable.dicts("var", var_names, lowBound=0)

            # Función objetivo
            objective = pulp.lpSum(
                [
                    problem.objective_coefficients[i] * variables[var_names[i]]
                    for i in range(num_vars)
                ]
            )
            prob += objective

            # Restricciones
            for i, constraint in enumerate(problem.constraints):
                coeffs = constraint["coefficients"]
                operator = constraint["operator"]
                rhs = constraint["rhs"]

                lhs = pulp.lpSum(
                    [coeffs[j] * variables[var_names[j]] for j in range(len(coeffs))]
                )

                if operator == "<=":
                    prob += lhs <= rhs, f"constraint_{i}"
                elif operator == ">=":
                    prob += lhs >= rhs, f"constraint_{i}"
                elif operator == "=":
                    prob += lhs == rhs, f"constraint_{i}"

            return {
                "pulp_problem": prob,
                "variables": variables,
                "variable_names": var_names,
            }

        except Exception as e:
            self.logger.error(f"Error generating PuLP model: {e}")
            raise


class ORToolsModelGenerator(IModelGenerator):
    """
    Genera modelos para Google OR-Tools.

    OR-Tools es el conjunto de herramientas de optimización de Google.
    Este generador crea variables NumVar, define el objetivo, y construye
    restricciones usando la API de OR-Tools.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not ORTOOLS_AVAILABLE:
            raise ImportError("OR-Tools library not available")

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Construye un modelo OR-Tools completo.

        Crea un solver GLOP (para programación lineal), define variables no negativas,
        establece los coeficientes del objetivo, y agrega restricciones con sus
        límites (bounds) según el operador.
        """
        try:
            # Crear solver
            solver = pywraplp.Solver.CreateSolver("GLOP")
            if not solver:
                raise RuntimeError("Could not create OR-Tools solver")

            # Crear variables
            num_vars = len(problem.objective_coefficients)
            variables = []

            for i in range(num_vars):
                var_name = (
                    problem.variable_names[i] if problem.variable_names else f"x{i+1}"
                )
                var = solver.NumVar(0, solver.infinity(), var_name)
                variables.append(var)

            # Función objetivo
            objective = solver.Objective()
            for i, coeff in enumerate(problem.objective_coefficients):
                objective.SetCoefficient(variables[i], coeff)

            if problem.objective_type == "maximize":
                objective.SetMaximization()
            else:
                objective.SetMinimization()

            # Restricciones
            constraints = []
            for i, constraint_data in enumerate(problem.constraints):
                coeffs = constraint_data["coefficients"]
                operator = constraint_data["operator"]
                rhs = constraint_data["rhs"]

                constraint = solver.Constraint(
                    -solver.infinity(), solver.infinity(), f"constraint_{i}"
                )

                for j, coeff in enumerate(coeffs):
                    constraint.SetCoefficient(variables[j], coeff)

                if operator == "<=":
                    constraint.SetUB(rhs)
                elif operator == ">=":
                    constraint.SetLB(rhs)
                elif operator == "=":
                    constraint.SetBounds(rhs, rhs)

                constraints.append(constraint)

            return {
                "solver": solver,
                "variables": variables,
                "constraints": constraints,
                "variable_names": [var.name() for var in variables],
            }

        except Exception as e:
            self.logger.error(f"Error generating OR-Tools model: {e}")
            raise


class ModelValidator(IModelValidator):
    """
    Valida que los problemas extraídos por NLP sean matemáticamente correctos.

    Revisa que:
    - El tipo de objetivo sea 'maximize' o 'minimize'
    - Los coeficientes sean números
    - Las dimensiones de restricciones coincidan con las variables
    - Los operadores sean válidos (<=, >=, =)
    - No haya problemas demasiado grandes (límites configurables)

    Ayuda a detectar errores antes de intentar resolver el problema.
    """

    def __init__(self, max_variables: int = 20, max_constraints: int = 50):
        self.max_variables = max_variables
        self.max_constraints = max_constraints
        self.logger = logging.getLogger(__name__)

    def validate(self, problem: OptimizationProblem) -> bool:
        """
        Revisa si el problema se puede resolver o tiene errores.

        Ejecuta todas las validaciones (dimensiones, tipos, límites) y
        retorna True solo si pasa todas. Si falla alguna, retorna False.

        Args:
            problem: Problema de optimización a validar

        Returns:
            True si todo está correcto, False si hay algún error
        """
        errors = self.get_validation_errors(problem)
        return len(errors) == 0

    def get_validation_errors(self, problem: OptimizationProblem) -> List[str]:
        """
        Genera una lista detallada de todos los problemas encontrados.

        Revisa cada aspecto del problema y acumula mensajes de error descriptivos.
        Útil para debugging y para mostrar al usuario qué está mal con su problema.

        Args:
            problem: Problema a validar

        Returns:
            Lista de strings describiendo cada error (lista vacía si es válido)
        """
        errors = []

        try:
            # Validar tipo de objetivo
            if problem.objective_type not in ["maximize", "minimize"]:
                errors.append(f"Invalid objective type: {problem.objective_type}")

            # Validar coeficientes objetivo
            if not problem.objective_coefficients:
                errors.append("Empty objective coefficients")
            elif not all(
                isinstance(x, (int, float)) for x in problem.objective_coefficients
            ):
                errors.append("Invalid objective coefficients (must be numeric)")
            elif len(problem.objective_coefficients) > self.max_variables:
                errors.append(
                    f"Too many variables: {len(problem.objective_coefficients)} > {self.max_variables}"
                )

            # Validar restricciones
            if not problem.constraints:
                errors.append("No constraints found")
            elif len(problem.constraints) > self.max_constraints:
                errors.append(
                    f"Too many constraints: {len(problem.constraints)} > {self.max_constraints}"
                )
            else:
                for i, constraint in enumerate(problem.constraints):
                    # Validar estructura
                    if not isinstance(constraint, dict):
                        errors.append(f"Constraint {i}: Invalid format")
                        continue

                    required_keys = ["coefficients", "operator", "rhs"]
                    missing_keys = [k for k in required_keys if k not in constraint]
                    if missing_keys:
                        errors.append(f"Constraint {i}: Missing keys: {missing_keys}")
                        continue

                    # Validar coeficientes
                    coeffs = constraint["coefficients"]
                    if not isinstance(coeffs, list):
                        errors.append(f"Constraint {i}: Coefficients must be a list")
                    elif len(coeffs) != len(problem.objective_coefficients):
                        errors.append(
                            f"Constraint {i}: Dimension mismatch ({len(coeffs)} vs {len(problem.objective_coefficients)})"
                        )
                    elif not all(isinstance(x, (int, float)) for x in coeffs):
                        errors.append(
                            f"Constraint {i}: Invalid coefficients (must be numeric)"
                        )

                    # Validar operador
                    operator = constraint["operator"]
                    if operator not in ["<=", ">=", "="]:
                        errors.append(f"Constraint {i}: Invalid operator: {operator}")

                    # Validar RHS
                    rhs = constraint["rhs"]
                    if not isinstance(rhs, (int, float)):
                        errors.append(f"Constraint {i}: Invalid RHS (must be numeric)")

            # Validar nombres de variables
            if problem.variable_names:
                if len(problem.variable_names) != len(problem.objective_coefficients):
                    errors.append("Variable names count mismatch")
                elif len(set(problem.variable_names)) != len(problem.variable_names):
                    errors.append("Duplicate variable names")

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return errors
