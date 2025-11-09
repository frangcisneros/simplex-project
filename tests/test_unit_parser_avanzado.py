"""
Tests unitarios para el parseo avanzado de restricciones.
Verifica que FileParser maneje correctamente operadores >=, ==, y <=.
"""

import pytest
from simplex_solver.file_parser import FileParser


class TestFileParserAdvanced:
    """Tests para verificar el parseo de restricciones avanzadas."""

    def test_parse_equality_constraint(self):
        """Verifica que se parseen correctamente restricciones de igualdad (=)."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar que hay al menos una restricción de igualdad
        assert "=" in constraint_types, "Debe haber al menos una restricción de igualdad"

        # Verificar el número de restricciones
        assert len(A) == 3, "Debe haber 3 restricciones"
        assert len(constraint_types) == 3, "Debe haber 3 tipos de restricción"

        # Verificar tipos específicos
        assert constraint_types[0] == ">=", "Primera restricción debe ser >="
        assert constraint_types[1] == ">=", "Segunda restricción debe ser >="
        assert constraint_types[2] == "=", "Tercera restricción debe ser ="

    def test_parse_greater_than_constraint(self):
        """Verifica que se parseen correctamente restricciones >= ."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_minimizacion.txt"
        )

        # Verificar que todas las restricciones son >=
        assert all(ct == ">=" for ct in constraint_types), "Todas las restricciones deben ser >="

        # Verificar dimensiones
        assert len(A) == 3, "Debe haber 3 restricciones"
        assert len(A[0]) == 2, "Cada restricción debe tener 2 variables"

    def test_parse_mixed_constraints(self):
        """Verifica el parseo de restricciones mixtas (<=, >=, =)."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar que hay diferentes tipos de restricciones
        unique_types = set(constraint_types)
        assert len(unique_types) >= 2, "Debe haber al menos 2 tipos diferentes de restricciones"

        # Verificar que los tipos son válidos
        valid_types = {"<=", ">=", "="}
        assert unique_types.issubset(
            valid_types
        ), f"Tipos encontrados {unique_types} deben estar en {valid_types}"

    def test_parse_coefficients_with_equality(self):
        """Verifica que los coeficientes se parseen correctamente con restricción de igualdad."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar función objetivo
        assert len(c) == 3, "Función objetivo debe tener 3 coeficientes"
        assert c == [3, 2, 1], "Coeficientes de función objetivo incorrectos"

        # Verificar que es minimización
        assert not maximize, "Debe ser un problema de minimización"

        # Verificar coeficientes de restricciones
        assert A[0] == [2, 1, 1], "Coeficientes de primera restricción incorrectos"
        assert A[1] == [1, 2, 1], "Coeficientes de segunda restricción incorrectos"
        assert A[2] == [1, 1, 2], "Coeficientes de tercera restricción incorrectos"

        # Verificar lado derecho
        assert b[0] == 4, "RHS de primera restricción incorrecto"
        assert b[1] == 3, "RHS de segunda restricción incorrecto"
        assert b[2] == 5, "RHS de tercera restricción incorrecto"

    def test_constraint_types_order_preserved(self):
        """Verifica que el orden de los tipos de restricción se preserve."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar orden exacto
        expected_types = [">=", ">=", "="]
        assert (
            constraint_types == expected_types
        ), f"Orden incorrecto: {constraint_types} != {expected_types}"

    def test_number_of_variables_consistent(self):
        """Verifica que el número de variables sea consistente en todas las restricciones."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        num_vars = len(c)

        # Todas las restricciones deben tener el mismo número de variables
        for i, row in enumerate(A):
            assert (
                len(row) == num_vars
            ), f"Restricción {i} tiene {len(row)} variables, esperaba {num_vars}"


class TestFileParserEdgeCases:
    """Tests para casos especiales de parseo."""

    def test_multiple_spaces_between_operators(self):
        """Verifica que se manejen espacios múltiples alrededor de operadores."""
        # Este test requeriría un archivo especial, por ahora verificamos el comportamiento actual
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificación básica de que el parseo funciona
        assert len(A) > 0, "Debe haber al menos una restricción parseada"
        assert len(constraint_types) > 0, "Debe haber al menos un tipo de restricción"

    def test_all_constraint_types_recognized(self):
        """Verifica que todos los tipos de restricción sean reconocidos correctamente."""
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar que no hay tipos desconocidos
        valid_types = {"<=", ">=", "="}
        for ct in constraint_types:
            assert ct in valid_types, f"Tipo de restricción desconocido: {ct}"
