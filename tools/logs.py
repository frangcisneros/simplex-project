#!/usr/bin/env python3
"""
Unified Log Management Tool for Simplex Solver
===============================================

This tool consolidates log viewing and verification functionality.
Provides both quick stats and detailed log viewer functionality.

Usage:
    python tools/logs.py                # Launch interactive viewer (default)
    python tools/logs.py --stats        # Show quick statistics
    python tools/logs.py --verify       # Verify log system integrity

Author: Francisco Cisneros
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simplex_solver.log_viewer import LogViewer


def get_db_path() -> Path:
    """Get the path to the log database."""
    return Path.home() / "AppData" / "Roaming" / "SimplexSolver" / "logs" / "simplex_logs.db"


def verify_logs() -> int:
    """Verify log system integrity and show statistics."""
    import sqlite3

    db_path = get_db_path()

    print("=" * 70)
    print("LOG SYSTEM VERIFICATION")
    print("=" * 70)
    print(f"\nDatabase path: {db_path}")
    print(f"Exists: {'✓ YES' if db_path.exists() else '✗ NO'}")

    if not db_path.exists():
        print("\n⚠️  Database doesn't exist yet.")
        print("Run the program at least once to create logs.")
        return 1

    # Database size
    size = db_path.stat().st_size
    print(f"Size: {size:,} bytes ({size/1024:.2f} KB)")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n" + "=" * 70)
        print("STATISTICS")
        print("=" * 70)

        # Total logs
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]
        print(f"\n📊 Total logs: {total_logs}")

        # Logs by level
        cursor.execute(
            """
            SELECT level, COUNT(*) as count 
            FROM logs 
            GROUP BY level 
            ORDER BY count DESC
        """
        )
        print("\n📈 Logs by level:")
        for level, count in cursor.fetchall():
            print(f"   {level:10} : {count:4} logs")

        # Sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        print(f"\n🔄 Total sessions: {total_sessions}")

        # Solver events
        cursor.execute('SELECT COUNT(*) FROM solver_events WHERE event_type="solve_complete"')
        problems_solved = cursor.fetchone()[0]
        print(f"🎯 Problems solved: {problems_solved}")

        # Last session
        cursor.execute(
            """
            SELECT session_id, start_time, end_time 
            FROM sessions 
            ORDER BY start_time DESC 
            LIMIT 1
        """
        )
        last_session = cursor.fetchone()
        if last_session:
            print(f"\n⏱️  Last session:")
            print(f"   ID: {last_session[0]}")
            print(f"   Start: {last_session[1][:19]}")
            print(f"   End: {last_session[2][:19] if last_session[2] else 'In progress'}")

        # Last 5 logs
        print("\n" + "=" * 70)
        print("LAST 5 LOGS")
        print("=" * 70)
        cursor.execute(
            """
            SELECT timestamp, level, module, message 
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT 5
        """
        )

        for row in cursor.fetchall():
            timestamp = row[0][:19]
            level = row[1]
            module = row[2][:20]
            message = row[3][:60]
            print(f"\n[{timestamp}] [{level}] {module}")
            print(f"  → {message}")

        # Last problem solved
        print("\n" + "=" * 70)
        print("LAST PROBLEM SOLVED")
        print("=" * 70)
        cursor.execute(
            """
            SELECT timestamp, problem_type, num_variables, num_constraints, 
                   iterations, execution_time_ms, status, optimal_value
            FROM solver_events 
            WHERE event_type = 'solve_complete'
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        )

        result = cursor.fetchone()
        if result:
            print(f"\n⏰ Timestamp: {result[0][:19]}")
            print(f"📝 Type: {result[1]}")
            print(f"🔢 Variables: {result[2]}, Constraints: {result[3]}")
            print(f"🔄 Iterations: {result[4]}")
            print(f"⚡ Time: {result[5]:.2f} ms")
            print(f"✅ Status: {result[6]}")
            if result[7]:
                print(f"🎯 Optimal value: {result[7]:.6f}")
        else:
            print("\n⚠️  No problems solved yet.")

        conn.close()

        print("\n" + "=" * 70)
        print("✓ VERIFICATION COMPLETE")
        print("=" * 70)
        print("\nLog system is working correctly! 🎉")
        print("\nFor detailed view, run: python tools/logs.py")

        return 0

    except Exception as e:
        print(f"\n✗ Error accessing database: {e}")
        return 1


def show_stats() -> int:
    """Show quick statistics without launching full viewer."""
    import sqlite3

    db_path = get_db_path()

    if not db_path.exists():
        print("⚠️  No log database found. Run the solver first.")
        return 1

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Quick stats
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM solver_events WHERE event_type="solve_complete"')
        problems_solved = cursor.fetchone()[0]

        print("\n📊 Quick Stats:")
        print(f"   Logs: {total_logs}")
        print(f"   Sessions: {total_sessions}")
        print(f"   Problems solved: {problems_solved}")

        # Recent activity
        cursor.execute(
            """
            SELECT level, COUNT(*) 
            FROM logs 
            WHERE datetime(timestamp) > datetime('now', '-1 day')
            GROUP BY level
        """
        )
        recent = cursor.fetchall()

        if recent:
            print("\n📈 Last 24 hours:")
            for level, count in recent:
                print(f"   {level}: {count}")

        conn.close()
        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def launch_viewer() -> int:
    """Launch the interactive log viewer."""
    try:
        viewer = LogViewer()
        viewer.run()
        return 0
    except Exception as e:
        print(f"✗ Error launching viewer: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified log management tool for Simplex Solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/logs.py              # Launch interactive viewer
  python tools/logs.py --stats      # Show quick statistics
  python tools/logs.py --verify     # Verify system integrity
        """,
    )

    parser.add_argument("--stats", action="store_true", help="Show quick statistics")
    parser.add_argument("--verify", action="store_true", help="Verify log system integrity")

    args = parser.parse_args()

    if args.verify:
        return verify_logs()
    elif args.stats:
        return show_stats()
    else:
        # Default: launch interactive viewer
        return launch_viewer()


if __name__ == "__main__":
    sys.exit(main())
