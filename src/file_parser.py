"""
Módulo para procesamiento de archivos de entrada.
Lee y parsea archivos con problemas de programación lineal.
"""

import sys
from typing import List, Tuple, Optional

# Agregar import del validador
from input_validator import InputValidator


class FileParser:
    """Parser para archivos de problemas de programación lineal."""
    
    @staticmethod
    def parse_file(filename: str) -> Tuple[List[float], List[List[float]], List[float], List[str], bool]:
        """
        Lee y parsea un archivo con el problema de programación lineal.
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not lines:
                raise ValueError("Archivo vacío")
            
            maximize = FileParser._parse_optimization_type(lines[0])
            c = FileParser._parse_objective_function(lines[1])
            A, b, constraint_types = FileParser._parse_constraints(lines, len(c))
            
            # Validar el problema parseado
            is_valid, error_msg = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
            if not is_valid:
                raise ValueError(f"Problema en archivo inválido: {error_msg}")
            
            return c, A, b, constraint_types, maximize
            
        except FileNotFoundError:
            raise FileNotFoundError(f"No se pudo encontrar el archivo {filename}")
        except Exception as e:
            raise ValueError(f"Error al leer el archivo: {e}")

"""
Módulo para procesamiento de archivos de entrada.
Lee y parsea archivos con problemas de programación lineal.
"""

import sys
from typing import List, Tuple, Optional


class FileParser:
    """Parser para archivos de problemas de programación lineal."""
    
    @staticmethod
    def parse_file(filename: str) -> Tuple[List[float], List[List[float]], List[float], List[str], bool]:
        """
        Lee y parsea un archivo con el problema de programación lineal.
        
        Formato esperado:
        MAXIMIZE (o MINIMIZE)
        c1 c2 c3 ... (coeficientes de la función objetivo)
        SUBJECT TO
        a11 a12 a13 ... <= b1
        a21 a22 a23 ... >= b2  
        a31 a32 a33 ... = b3
        ...
        
        Args:
            filename: Ruta del archivo a parsear
            
        Returns:
            Tupla con (c, A, b, constraint_types, maximize)
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not lines:
                raise ValueError("Archivo vacío")
            
            maximize = FileParser._parse_optimization_type(lines[0])
            c = FileParser._parse_objective_function(lines[1])
            A, b, constraint_types = FileParser._parse_constraints(lines, len(c))
            
            return c, A, b, constraint_types, maximize
            
        except FileNotFoundError:
            raise FileNotFoundError(f"No se pudo encontrar el archivo {filename}")
        except Exception as e:
            raise ValueError(f"Error al leer el archivo: {e}")
    
    @staticmethod
    def _parse_optimization_type(line: str) -> bool:
        """Parsea el tipo de optimización (MAXIMIZE/MINIMIZE)."""
        line_upper = line.upper()
        if line_upper == "MAXIMIZE":
            return True
        elif line_upper == "MINIMIZE":
            return False
        else:
            raise ValueError("Primera línea debe ser MAXIMIZE o MINIMIZE")
    
    @staticmethod
    def _parse_objective_function(line: str) -> List[float]:
        """Parsea los coeficientes de la función objetivo."""
        try:
            return list(map(float, line.split()))
        except ValueError:
            raise ValueError("Coeficientes de función objetivo inválidos")
    
    @staticmethod
    def _parse_constraints(lines: List[str], num_vars: int) -> Tuple[List[List[float]], List[float], List[str]]:
        """Parsea las restricciones del problema."""
        # Buscar "SUBJECT TO"
        subject_to_idx = -1
        for i, line in enumerate(lines):
            if "SUBJECT TO" in line.upper():
                subject_to_idx = i
                break
        
        if subject_to_idx == -1:
            raise ValueError("No se encontró 'SUBJECT TO'")
        
        A = []
        b = []
        constraint_types = []
        
        for line in lines[subject_to_idx + 1:]:
            line = line.strip()
            if not line:
                continue
                
            # Detectar tipo de restricción
            if '<=' in line:
                parts = line.split('<=')
                const_type = '<='
            elif '>=' in line:
                parts = line.split('>=')
                const_type = '>='
            elif '=' in line:
                parts = line.split('=')
                const_type = '='
            else:
                print(f"Advertencia: línea ignorada (formato no reconocido): {line}")
                continue
            
            if len(parts) != 2:
                print(f"Advertencia: línea ignorada (formato inválido): {line}")
                continue
            
            try:
                coeffs = list(map(float, parts[0].split()))
                rhs = float(parts[1])
                
                if len(coeffs) != num_vars:
                    raise ValueError(f"Número de coeficientes ({len(coeffs)}) no coincide con variables ({num_vars})")
                
                A.append(coeffs)
                b.append(rhs)
                constraint_types.append(const_type)
                
            except ValueError as e:
                print(f"Advertencia: línea ignorada (error en números): {line} - {e}")
                continue
        
        if not A:
            raise ValueError("Debe haber al menos una restricción válida")
        
        return A, b, constraint_types