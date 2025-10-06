"""
Generadores de modelos de optimización.
Convierte OptimizationProblem a diferentes formatos de solver.
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
    Generador de modelos para el solver Simplex existente.
    Convierte OptimizationProblem al formato esperado por SimplexSolver.

    Principios SOLID:
    - SRP: Solo se encarga de generar modelos para Simplex
    - OCP: Extensible sin modificar código existente
    - LSP: Implementa completamente IModelGenerator
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Genera modelo en formato SimplexSolver.

        Args:
            problem: Problema de optimización estructurado

        Returns:
            Dict con 'c', 'A', 'b', 'maximize' para SimplexSolver
        """
        try:
            # Extraer función objetivo
            c = problem.objective_coefficients
            maximize = problem.objective_type == "maximize"

            # Construir matriz A y vector b
            A = []
            b = []

            for constraint in problem.constraints:
                coeffs = constraint["coefficients"]
                operator = constraint["operator"]
                rhs = constraint["rhs"]

                # Convertir restricciones >= a <= multiplicando por -1
                if operator == ">=":
                    coeffs = [-coeff for coeff in coeffs]
                    rhs = -rhs
                elif operator == "=":
                    # Para restricciones de igualdad, agregar dos restricciones
                    A.append(coeffs)
                    b.append(rhs)
                    A.append([-coeff for coeff in coeffs])
                    b.append(-rhs)
                    continue

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
    Generador de modelos PuLP.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not PULP_AVAILABLE:
            raise ImportError("PuLP library not available")

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """Genera modelo PuLP."""
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
    Generador de modelos OR-Tools.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not ORTOOLS_AVAILABLE:
            raise ImportError("OR-Tools library not available")

    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """Genera modelo OR-Tools."""
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
    Validador de problemas de optimización.
    Verifica que el problema extraído por NLP sea coherente.
    """

    def __init__(self, max_variables: int = 20, max_constraints: int = 50):
        self.max_variables = max_variables
        self.max_constraints = max_constraints
        self.logger = logging.getLogger(__name__)

    def validate(self, problem: OptimizationProblem) -> bool:
        """
        Valida el problema de optimización.

        Args:
            problem: Problema a validar

        Returns:
            True si es válido, False en caso contrario
        """
        errors = self.get_validation_errors(problem)
        return len(errors) == 0

    def get_validation_errors(self, problem: OptimizationProblem) -> List[str]:
        """
        Obtiene lista de errores de validación.

        Args:
            problem: Problema a validar

        Returns:
            Lista de errores encontrados
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
