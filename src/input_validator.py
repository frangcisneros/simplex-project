"""
Módulo para validación de entrada en problemas de programación lineal.
"""

import sys
from typing import List, Tuple, Optional


class InputValidator:
    """Valida los parámetros de entrada para problemas de programación lineal."""
    
    @staticmethod
    def validate_problem(c: List[float], A: List[List[float]], b: List[float], 
                        constraint_types: List[str], maximize: bool) -> Tuple[bool, str]:
        """
        Valida todos los parámetros del problema de programación lineal.
        
        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de restricciones
            b: Términos independientes de restricciones
            constraint_types: Tipos de restricciones
            maximize: True para maximización, False para minimización
            
        Returns:
            Tuple (es_válido, mensaje_error)
        """
        # Validar función objetivo
        is_valid, error_msg = InputValidator._validate_objective_function(c)
        if not is_valid:
            return False, error_msg
        
        # Validar restricciones
        is_valid, error_msg = InputValidator._validate_constraints(A, b, constraint_types, len(c))
        if not is_valid:
            return False, error_msg
        
        # Validar consistencia del problema
        is_valid, error_msg = InputValidator._validate_problem_consistency(A, b, constraint_types)
        if not is_valid:
            return False, error_msg
        
        return True, "Problema válido"
    
    @staticmethod
    def _validate_objective_function(c: List[float]) -> Tuple[bool, str]:
        """Valida los coeficientes de la función objetivo."""
        if not c:
            return False, "La función objetivo debe tener al menos un coeficiente"
        
        if len(c) == 0:
            return False, "La función objetivo no puede estar vacía"
        
        # Verificar que todos los coeficientes sean números finitos
        for i, coeff in enumerate(c):
            if not isinstance(coeff, (int, float)):
                return False, f"Coeficiente {i+1} de la función objetivo no es un número válido"
            
            if not InputValidator._is_finite_number(coeff):
                return False, f"Coeficiente {i+1} de la función objetivo no es un número finito"
        
        # Verificar que no todos los coeficientes sean cero
        if all(abs(coeff) < 1e-10 for coeff in c):
            return False, "Todos los coeficientes de la función objetivo son cero"
        
        return True, "Función objetivo válida"
    
    @staticmethod
    def _validate_constraints(A: List[List[float]], b: List[float], 
                            constraint_types: List[str], num_vars: int) -> Tuple[bool, str]:
        """Valida las restricciones del problema."""
        if not A:
            return False, "Debe haber al menos una restricción"
        
        if len(A) != len(b) or len(A) != len(constraint_types):
            return False, "Número inconsistente de restricciones y términos independientes"
        
        # Validar cada restricción
        for i, (row, rhs, const_type) in enumerate(zip(A, b, constraint_types)):
            # Validar tipo de restricción
            if const_type not in ['<=', '>=', '=']:
                return False, f"Restricción {i+1}: tipo '{const_type}' no válido. Use '<=', '>=' o '='"
            
            # Validar número de coeficientes
            if len(row) != num_vars:
                return False, f"Restricción {i+1}: número de coeficientes ({len(row)}) no coincide con variables ({num_vars})"
            
            # Validar coeficientes
            for j, coeff in enumerate(row):
                if not isinstance(coeff, (int, float)):
                    return False, f"Restricción {i+1}, coeficiente {j+1}: no es un número válido"
                
                if not InputValidator._is_finite_number(coeff):
                    return False, f"Restricción {i+1}, coeficiente {j+1}: no es un número finito"
            
            # Validar término independiente
            if not isinstance(rhs, (int, float)):
                return False, f"Restricción {i+1}: término independiente no es un número válido"
            
            if not InputValidator._is_finite_number(rhs):
                return False, f"Restricción {i+1}: término independiente no es un número finito"
            
            # Validar restricciones de igualdad con RHS negativo
            if const_type == '=' and rhs < 0:
                return False, f"Restricción {i+1} de igualdad no puede tener término independiente negativo"
        
        return True, "Restricciones válidas"
    
    @staticmethod
    def _validate_problem_consistency(A: List[List[float]], b: List[float], 
                                    constraint_types: List[str]) -> Tuple[bool, str]:
        """Valida la consistencia general del problema."""
        # Verificar si hay restricciones redundantes o contradictorias
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                # Verificar si dos restricciones son idénticas
                if (A[i] == A[j] and b[i] == b[j] and constraint_types[i] == constraint_types[j]):
                    return False, f"Restricciones {i+1} y {j+1} son idénticas (redundantes)"
                
                # Verificar restricciones contradictorias simples
                if (A[i] == A[j] and constraint_types[i] == '<=' and 
                    constraint_types[j] == '>=' and b[i] < b[j]):
                    return False, f"Restricciones {i+1} y {j+1} son contradictorias"
        
        # Verificar si el problema podría ser infactible desde el inicio
        all_positive_constraints = all(const_type == '>=' for const_type in constraint_types)
        all_negative_coeffs = all(all(coeff <= 0 for coeff in row) for row in A)
        positive_rhs = all(rhs > 0 for rhs in b)
        
        if all_positive_constraints and all_negative_coeffs and positive_rhs:
            return False, "El problema parece infactible: todas las restricciones son >= con coeficientes no positivos y RHS positivos"
        
        return True, "Problema consistente"
    
    @staticmethod
    def _is_finite_number(x: float) -> bool:
        """Verifica si un número es finito (no NaN ni infinito)."""
        return isinstance(x, (int, float)) and abs(x) != float('inf') and x == x  # x == x verifica que no sea NaN
    
    @staticmethod
    def validate_solution_feasibility(solution: dict, A: List[List[float]], 
                                    b: List[float], constraint_types: List[str], 
                                    tol: float = 1e-6) -> Tuple[bool, List[str]]:
        """
        Valida que una solución cumpla con todas las restricciones.
        
        Args:
            solution: Diccionario con la solución {x1: val, x2: val, ...}
            A: Matriz de coeficientes
            b: Términos independientes
            constraint_types: Tipos de restricciones
            tol: Tolerancia para comparaciones numéricas
            
        Returns:
            Tuple (es_factible, lista_de_errores)
        """
        errors = []
        
        # Verificar no negatividad
        for var_name, value in solution.items():
            if value < -tol:
                errors.append(f"Variable {var_name} = {value:.6f} viola no negatividad")
        
        # Verificar cada restricción
        for i, (row, rhs, const_type) in enumerate(zip(A, b, constraint_types)):
            # Calcular valor del lado izquierdo
            lhs_value = 0.0
            for j, coeff in enumerate(row):
                var_name = f"x{j+1}"
                if var_name in solution:
                    lhs_value += coeff * solution[var_name]
            
            # Verificar según el tipo de restricción
            if const_type == '<=' and lhs_value > rhs + tol:
                errors.append(f"Restricción {i+1}: {lhs_value:.6f} > {rhs} (viola <=)")
            elif const_type == '>=' and lhs_value < rhs - tol:
                errors.append(f"Restricción {i+1}: {lhs_value:.6f} < {rhs} (viola >=)")
            elif const_type == '=' and abs(lhs_value - rhs) > tol:
                errors.append(f"Restricción {i+1}: {lhs_value:.6f} != {rhs} (viola =)")
        
        return len(errors) == 0, errors
