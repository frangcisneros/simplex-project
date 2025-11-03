"""
Core Simplex algorithm implementation.
Contains the main SimplexSolver class following Single Responsibility Principle.
"""

from typing import Dict, Any, List
import numpy as np
from simplex_solver.utils.tableau import Tableau
from simplex_solver.logging_system import logger


class SimplexSolver:
    """
    Implements the Simplex method for solving linear programming problems.

    This class focuses solely on the algorithm logic, delegating
    I/O operations and UI concerns to other modules.
    """

    def __init__(self):
        """Initialize the SimplexSolver with default settings."""
        self.tableau = Tableau()
        self.max_iterations = 100
        self.steps = []  # History of steps for PDF generation

    def _solve_phase(self, maximize: bool) -> Dict[str, Any]:
        """
        Solve one phase of the simplex method.

        Args:
            maximize: True for maximization, False for minimization

        Returns:
            Dictionary with status, iterations, and optional message
        """
        iteration = 0
        logger.debug(f"Starting simplex phase (maximize={maximize})")

        while iteration < self.max_iterations - 1:
            iteration += 1
            logger.debug(f"Iteration {iteration}: Checking optimality")

            # Check optimality
            is_optimal = self.tableau.is_optimal(maximize)

            if is_optimal:
                logger.info(f"Optimal solution found at iteration {iteration}")
                return {"status": "optimal", "iterations": iteration}

            # Find entering variable
            entering_col = self.tableau.get_entering_variable(maximize)

            if entering_col == -1:
                logger.info("No entering variable found - optimal solution")
                return {"status": "optimal", "iterations": iteration}

            logger.debug(f"Entering variable: column {entering_col + 1}")

            # Check if problem is unbounded
            if self.tableau.is_unbounded(entering_col):
                logger.warning(f"Unbounded problem detected at iteration {iteration}")
                return {
                    "status": "unbounded",
                    "message": "The problem is unbounded",
                    "iterations": iteration,
                }

            # Find leaving variable
            leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)

            if leaving_row == -1:
                logger.error(f"Could not find leaving variable at iteration {iteration}")
                return {
                    "status": "error",
                    "message": "Could not find leaving variable",
                    "iterations": iteration,
                }

            logger.debug(f"Leaving variable: row {leaving_row + 1}, pivot: {pivot:.4f}")

            # Store step for PDF report
            self.steps.append(
                {
                    "iteration": iteration,
                    "tableau": self.tableau.tableau.copy(),
                    "basic_vars": self.tableau.basic_vars.copy(),
                    "entering_var": entering_col,
                    "leaving_var": self.tableau.basic_vars[leaving_row],
                    "pivot_coords_next": {
                        "entering_col": entering_col,
                        "leaving_row": leaving_row,
                    },
                }
            )

            # Perform pivoting
            self.tableau.pivot(entering_col, leaving_row)
            logger.debug(f"Pivot completed: [{leaving_row}, {entering_col}]")

            if iteration > 50:  # Prevent infinite loops
                logger.warning(f"Too many iterations ({iteration}), stopping")
                return {"status": "error", "message": "Too many iterations"}

        logger.error(f"Maximum iterations reached: {self.max_iterations}")
        return {
            "status": "error",
            "message": "Too many iterations",
            "iterations": iteration,
        }

    def solve(
        self, c: list, A: list, b: list, constraint_types: list, maximize: bool = True
    ) -> Dict[str, Any]:
        """
        Solve a linear programming problem using the simplex method.

        Args:
            c: Objective function coefficients
            A: Constraint coefficient matrix
            b: Right-hand side vector
            constraint_types: Constraint types ('<=', '>=', '=')
            maximize: True to maximize, False to minimize

        Returns:
            Dictionary with solution, optimal value, status, and iterations
        """
        logger.info(
            f"Starting solver - Variables: {len(c)}, Constraints: {len(A)}, "
            f"Type: {'MAX' if maximize else 'MIN'}"
        )
        self.steps.clear()  # Clear step history

        # Build initial tableau
        self.tableau.build_initial_tableau(c, A, b, constraint_types, maximize)
        logger.debug("Initial tableau built")

        total_iterations = 0
        phase1_iterations = 0

        # Phase 1: If there are artificial variables
        if self.tableau.artificial_vars:
            logger.info(
                f"Starting Phase 1 - Artificial variables: {len(self.tableau.artificial_vars)}"
            )
            phase1_result = self._solve_phase(maximize)
            phase1_iterations = phase1_result["iterations"]
            total_iterations += phase1_iterations

            if phase1_result["status"] != "optimal":
                logger.warning(f"Phase 1 not optimal: {phase1_result['status']}")
                return {**phase1_result, "iterations": total_iterations}

            # Check feasibility
            if (
                abs(self.tableau.tableau[-1, -1]) > 1e-10
                or self.tableau.has_artificial_vars_in_basis()
            ):
                logger.warning("Infeasible problem detected in Phase 1")
                return {
                    "status": "infeasible",
                    "message": "The problem has no feasible solution",
                    "iterations": total_iterations,
                }

            logger.info(f"Phase 1 completed successfully in {phase1_iterations} iterations")

            # Prepare Phase 2
            logger.info("Starting Phase 2")
            self.tableau.setup_phase2(np.array(c), maximize)

        # Phase 2 (or single phase)
        if not self.tableau.artificial_vars:
            logger.info("Solving in single phase (no artificial variables)")

        phase2_result = self._solve_phase(maximize)
        total_iterations += phase2_result["iterations"]

        if phase2_result["status"] == "optimal":
            solution, optimal_value = self.tableau.get_solution(maximize)
            logger.info(
                f"Optimal solution found - Value: {optimal_value:.6f}, "
                f"Total iterations: {total_iterations}"
            )

            # Store final state for report
            self.steps.append(
                {
                    "iteration": total_iterations,
                    "tableau": self.tableau.tableau.copy(),
                    "basic_vars": self.tableau.basic_vars.copy(),
                    "entering_var": None,
                    "leaving_var": None,
                    "pivot_coords_next": None,
                }
            )

            result = {
                "status": "optimal",
                "solution": solution,
                "optimal_value": optimal_value,
                "iterations": total_iterations,
                "steps": self.steps,
                "n_original_vars": self.tableau.num_vars,
            }
            if self.tableau.artificial_vars:
                result["phase1_iterations"] = phase1_iterations
            return result
        else:
            return {**phase2_result, "iterations": total_iterations}
