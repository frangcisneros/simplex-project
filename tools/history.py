#!/usr/bin/env python3
"""
Unified History Management Tool for Simplex Solver
===================================================

This tool consolidates history viewing and testing functionality.
Provides both interactive menu and diagnostic capabilities.

Usage:
    python tools/history.py             # Launch interactive menu (default)
    python tools/history.py --test      # Test history system
    python tools/history.py --stats     # Show quick statistics

Author: Francisco Cisneros
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simplex_solver.problem_history import ProblemHistory, show_history_menu


def test_history() -> int:
    """Test the history system functionality."""
    print("=" * 80)
    print("HISTORY SYSTEM TEST")
    print("=" * 80)

    try:
        history = ProblemHistory()

        # Test 1: Get all problems
        print("\n1. Retrieving all problems...")
        problems = history.get_all_problems()
        print(f"   ✓ Found: {len(problems)} problem(s)")

        if not problems:
            print("\n⚠️  No problems in history yet.")
            print("   Solve a problem first to populate the history.")
            return 0

        # Test 2: Display problems table
        print("\n2. Displaying problems table...")
        history.display_problems_table(problems)

        # Test 3: Get details of first problem
        print("\n3. Retrieving details of first problem...")
        first_id = problems[0]["id"]
        problem = history.get_problem_by_id(first_id)
        if problem:
            print(f"   ✓ Problem #{first_id} found")
            history.display_problem_detail(problem)
        else:
            print(f"   ✗ Problem #{first_id} not found")
            return 1

        # Test 4: Create temporary file
        print("\n4. Creating temporary file from problem...")
        temp_file = history.create_temp_file_from_history(first_id)
        if temp_file:
            print(f"   ✓ Temporary file created: {temp_file}")
            print(f"   ✓ Exists: {os.path.exists(temp_file)}")

            # Clean up
            try:
                os.remove(temp_file)
                print(f"   ✓ Temporary file cleaned up")
            except Exception as e:
                print(f"   ⚠️  Could not remove temp file: {e}")
        else:
            print(f"   ✗ Failed to create temporary file")
            return 1

        # Test 5: Statistics
        print("\n5. Calculating statistics...")
        total = len(problems)
        optimal = sum(1 for p in problems if p.get("status") == "optimal")
        infeasible = sum(1 for p in problems if p.get("status") == "infeasible")
        unbounded = sum(1 for p in problems if p.get("status") == "unbounded")

        print(f"   Total problems: {total}")
        print(f"   Optimal: {optimal}")
        print(f"   Infeasible: {infeasible}")
        print(f"   Unbounded: {unbounded}")

        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


def show_stats() -> int:
    """Show quick statistics about problem history."""
    try:
        history = ProblemHistory()
        problems = history.get_all_problems()

        if not problems:
            print("⚠️  No problems in history yet.")
            return 0

        # Calculate stats
        total = len(problems)
        optimal = sum(1 for p in problems if p.get("status") == "optimal")
        max_vars = max((p.get("num_variables", 0) for p in problems), default=0)
        max_constraints = max((p.get("num_constraints", 0) for p in problems), default=0)

        # Recent problems
        recent = problems[:5]  # First 5 (assuming they're ordered by date DESC)

        print("\n📊 History Statistics:")
        print(f"   Total problems: {total}")
        print(f"   Optimal solutions: {optimal} ({optimal/total*100:.1f}%)")
        print(f"   Max variables: {max_vars}")
        print(f"   Max constraints: {max_constraints}")

        if recent:
            print("\n📝 Recent problems:")
            for p in recent:
                date = p.get("solved_at", "Unknown")[:10]  # Just the date
                status = p.get("status", "Unknown")
                vars_count = p.get("num_variables", 0)
                print(f"   [{date}] {status} - {vars_count} variables")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def launch_interactive_menu() -> int:
    """Launch the interactive history menu."""
    try:
        temp_file = show_history_menu()

        if temp_file:
            # User wants to re-solve a problem
            print("\n¿Deseas ejecutar el Simplex Solver con este problema? (s/n)")
            choice = input().strip().lower()

            if choice == "s":
                print(f"\nEjecutando: python simplex.py {temp_file}")
                os.system(f'python simplex.py "{temp_file}"')
            else:
                print(f"\nPuedes ejecutarlo manualmente con:")
                print(f'python simplex.py "{temp_file}"')

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified history management tool for Simplex Solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/history.py           # Launch interactive menu
  python tools/history.py --test    # Test history system
  python tools/history.py --stats   # Show quick statistics
        """,
    )

    parser.add_argument("--test", action="store_true", help="Test history system functionality")
    parser.add_argument("--stats", action="store_true", help="Show quick statistics")

    args = parser.parse_args()

    if args.test:
        return test_history()
    elif args.stats:
        return show_stats()
    else:
        # Default: launch interactive menu
        return launch_interactive_menu()


if __name__ == "__main__":
    sys.exit(main())
