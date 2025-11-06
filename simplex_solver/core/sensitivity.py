"""
Sensitivity Analysis module for Simplex method.

Calculates Shadow Prices, Optimality Ranges, and Feasibility Ranges
after finding an optimal solution.
"""

from typing import Dict, Tuple, Optional, Any
import numpy as np
from simplex_solver.logging_system import logger


class SensitivityAnalyzer:
    """
    Performs sensitivity analysis on an optimal simplex tableau.

    Responsibilities:
    - Calculate shadow prices (dual values)
    - Determine optimality ranges for objective function coefficients
    - Determine feasibility ranges for RHS values
    """

    def __init__(self, tableau: np.ndarray, basic_vars: list, num_vars: int, num_constraints: int):
        """
        Initialize the sensitivity analyzer.

        Args:
            tableau: The optimal simplex tableau
            basic_vars: List of basic variable indices
            num_vars: Number of original decision variables
            num_constraints: Number of constraints (excluding non-negativity)
        """
        self.tableau = tableau
        self.basic_vars = basic_vars
        self.num_vars = num_vars
        self.num_constraints = num_constraints
        logger.debug(
            f"SensitivityAnalyzer initialized: {num_vars} vars, {num_constraints} constraints"
        )

    def calculate_shadow_prices(self) -> Dict[str, float]:
        """
        Calculate shadow prices (dual values) for each constraint.

        Shadow prices represent the marginal value of relaxing each constraint.
        They are extracted from the objective row coefficients of slack variables.

        Returns:
            Dictionary mapping constraint names to shadow prices
        """
        logger.debug("Calculating shadow prices...")
        shadow_prices = {}

        # The objective function row is the last row
        obj_row = self.tableau[-1, :]

        # Shadow prices are the negatives of the slack variable coefficients
        # in the objective row
        # Slack variables start after the decision variables
        for i in range(self.num_constraints):
            slack_col = self.num_vars + i
            shadow_price = -obj_row[slack_col]
            constraint_name = f"restriccion_{i + 1}"
            shadow_prices[constraint_name] = float(shadow_price)
            logger.debug(f"Shadow price for {constraint_name}: {shadow_price:.6f}")

        return shadow_prices

    def calculate_optimality_ranges(self, original_c: np.ndarray) -> Dict[str, Tuple[float, float]]:
        """
        Calculate optimality ranges for objective function coefficients.

        For each decision variable, determines the range [c_min, c_max] within which
        the coefficient can vary without changing the optimal basis.

        Args:
            original_c: Original objective function coefficients

        Returns:
            Dictionary mapping variable names to (min, max) tuples
        """
        logger.debug("Calculating optimality ranges...")
        opt_ranges = {}

        for j in range(self.num_vars):
            var_name = f"x{j + 1}"
            c_current = original_c[j]

            # Check if variable is in basis
            if j in self.basic_vars:
                # Basic variable: calculate range from reduced costs of non-basic vars
                min_delta, max_delta = self._calculate_basic_var_range(j)
            else:
                # Non-basic variable: use reduced cost directly
                min_delta, max_delta = self._calculate_nonbasic_var_range(j)

            c_min = c_current + min_delta
            c_max = c_current + max_delta

            opt_ranges[var_name] = (float(c_min), float(c_max))
            logger.debug(f"Optimality range for {var_name}: [{c_min:.4f}, {c_max:.4f}]")

        return opt_ranges

    def _calculate_basic_var_range(self, var_index: int) -> Tuple[float, float]:
        """
        Calculate the range for a basic variable's objective coefficient.

        Args:
            var_index: Index of the basic variable

        Returns:
            Tuple (min_delta, max_delta) for the coefficient change
        """
        # Find which row this variable is basic in
        try:
            row = self.basic_vars.index(var_index)
        except ValueError:
            logger.warning(f"Variable {var_index} not found in basic vars")
            return (float("-inf"), float("inf"))

        # Get the column of this variable in the tableau
        var_column = self.tableau[:, var_index]

        # For a basic variable, we look at how changing its coefficient
        # would affect the reduced costs of non-basic variables
        obj_row = self.tableau[-1, :]

        min_delta = float("-inf")
        max_delta = float("inf")

        # Check each non-basic variable column
        for j in range(self.num_vars):
            if j not in self.basic_vars:
                # Coefficient in the tableau for this non-basic variable in the basic var's row
                a_ij = self.tableau[row, j]
                reduced_cost = obj_row[j]

                if abs(a_ij) > 1e-10:
                    # Delta must maintain reduced cost >= 0 (for maximization)
                    # reduced_cost - delta * a_ij >= 0
                    # delta <= reduced_cost / a_ij (if a_ij > 0)
                    # delta >= reduced_cost / a_ij (if a_ij < 0)
                    ratio = reduced_cost / a_ij

                    if a_ij > 0:
                        max_delta = min(max_delta, ratio)
                    else:
                        min_delta = max(min_delta, ratio)

        return (min_delta, max_delta)

    def _calculate_nonbasic_var_range(self, var_index: int) -> Tuple[float, float]:
        """
        Calculate the range for a non-basic variable's objective coefficient.

        Args:
            var_index: Index of the non-basic variable

        Returns:
            Tuple (min_delta, max_delta) for the coefficient change
        """
        # For a non-basic variable, the reduced cost tells us how much
        # the coefficient needs to change to enter the basis
        obj_row = self.tableau[-1, :]
        reduced_cost = obj_row[var_index]

        # For maximization: variable can increase by reduced_cost before entering basis
        # It can decrease indefinitely without affecting optimality
        min_delta = float("-inf")
        max_delta = reduced_cost

        return (min_delta, max_delta)

    def calculate_feasibility_ranges(
        self, original_b: np.ndarray
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate feasibility ranges for RHS values.

        For each constraint, determines the range [b_min, b_max] within which
        the RHS can vary without changing the optimal basis.

        Args:
            original_b: Original RHS values

        Returns:
            Dictionary mapping constraint names to (min, max) tuples
        """
        logger.debug("Calculating feasibility ranges...")
        feas_ranges = {}

        # Extract the current RHS (solution values) from the tableau
        current_rhs = self.tableau[:-1, -1]  # All rows except objective, last column

        for i in range(self.num_constraints):
            constraint_name = f"restriccion_{i + 1}"
            b_current = original_b[i]

            # Calculate how much each basic variable can change
            # when we perturb the i-th RHS value
            min_delta, max_delta = self._calculate_rhs_range(i)

            b_min = b_current + min_delta
            b_max = b_current + max_delta

            feas_ranges[constraint_name] = (float(b_min), float(b_max))
            logger.debug(f"Feasibility range for {constraint_name}: [{b_min:.4f}, {b_max:.4f}]")

        return feas_ranges

    def _calculate_rhs_range(self, constraint_index: int) -> Tuple[float, float]:
        """
        Calculate the range for a constraint's RHS value.

        Args:
            constraint_index: Index of the constraint

        Returns:
            Tuple (min_delta, max_delta) for the RHS change
        """
        # The constraint_index corresponds to a slack variable column
        slack_col = self.num_vars + constraint_index

        # Get the column for this slack variable
        slack_column = self.tableau[:-1, slack_col]  # Exclude objective row

        # Current RHS values (basic solution values)
        current_rhs = self.tableau[:-1, -1]

        min_delta = float("-inf")
        max_delta = float("inf")

        # For each basic variable, calculate the ratio
        for row in range(len(current_rhs)):
            a_i = slack_column[row]
            b_i = current_rhs[row]

            if abs(a_i) > 1e-10:
                # When we increase RHS by delta, basic var changes by delta * a_i
                # We need: b_i + delta * a_i >= 0
                # delta >= -b_i / a_i (if a_i > 0)
                # delta <= -b_i / a_i (if a_i < 0)
                ratio = -b_i / a_i

                if a_i > 0:
                    min_delta = max(min_delta, ratio)
                else:
                    max_delta = min(max_delta, ratio)

        return (min_delta, max_delta)

    def analyze(self, original_c: np.ndarray, original_b: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """
        Perform complete sensitivity analysis.

        Args:
            original_c: Original objective function coefficients
            original_b: Original RHS values

        Returns:
            Dictionary containing shadow_prices, optimality_ranges, and feasibility_ranges
        """
        logger.info("Performing complete sensitivity analysis...")

        analysis = {
            "shadow_prices": self.calculate_shadow_prices(),
            "optimality_ranges": self.calculate_optimality_ranges(original_c),
            "feasibility_ranges": self.calculate_feasibility_ranges(original_b),
        }

        logger.info("Sensitivity analysis completed successfully")
        return analysis
