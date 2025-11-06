# Development Tools - Simplex Solver

This directory contains consolidated development tools following SOLID principles. Each tool is designed for a single, well-defined purpose.

## Overview

All tools in this directory are standalone Python scripts that can be executed from the project root. They provide unified interfaces for common development tasks.

## Available Tools

### build.py - Unified Build System

Consolidates all build functionality for creating Windows executables using PyInstaller.

**Usage:**

```powershell
# Build the installer executable
python tools/build.py --installer

# Build the solver executable
python tools/build.py --solver

# Build both executables
python tools/build.py --all

# Clean build artifacts (dist/, build/, *.spec)
python tools/build.py --clean

# Clean and rebuild
python tools/build.py --clean --all
```

**Features:**

- Automatic PyInstaller installation if not present
- Separate configurations for installer and solver
- Generates .spec files dynamically
- Verifies output and displays file sizes
- Clean separation of concerns using SOLID principles

**Output:**

- `dist/SimplexInstaller.exe` - Interactive installer (~40-50 MB)
- `dist/SimplexSolver.exe` - Standalone solver (~30-40 MB)

**Build Configurations:**

- **Installer**: Includes UAC admin manifest, full documentation, context menu scripts
- **Solver**: Minimal package with core functionality only

**Architecture:**

- `BuildCleaner` - Removes build artifacts
- `PyInstallerManager` - Ensures PyInstaller availability
- `SpecFileGenerator` - Generates .spec files
- `ExecutableBuilder` - Compiles executables
- `BuildOrchestrator` - Coordinates the entire build process

### logs.py - Log Management Tool

Provides access to the SQLite-based logging system with multiple viewing and analysis modes.

**Usage:**

```powershell
# Launch interactive log viewer (default)
python tools/logs.py

# Show quick statistics
python tools/logs.py --stats

# Verify log system integrity
python tools/logs.py --verify
```

**Features:**

**Interactive Mode:**

- View recent logs
- Filter by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- View logs by session
- View solver events and file operations
- Search functionality
- Export logs
- Clean old logs

**Stats Mode:**

- Total log count
- Session count
- Problems solved
- Activity in last 24 hours

**Verify Mode:**

- Database integrity check
- Detailed statistics
- Last 5 log entries
- Last problem solved details
- System health verification

**Log Database Location:**

- **Development**: `logs/simplex_logs.db`
- **Production**: `%APPDATA%\SimplexSolver\logs\simplex_logs.db`

### history.py - Problem History Management

Manages the history of solved problems with interactive menu and diagnostics.

**Usage:**

```powershell
# Launch interactive history menu (default)
python tools/history.py

# Test history system functionality
python tools/history.py --test

# Show quick statistics
python tools/history.py --stats
```

**Features:**

**Interactive Menu:**

- View all solved problems
- Search by problem name
- View detailed problem information
- Re-solve problems from history
- Display problem statistics

**Test Mode:**

- Retrieves all problems
- Displays problems table
- Tests problem detail retrieval
- Creates and verifies temporary files
- Calculates comprehensive statistics

**Stats Mode:**

- Total problems count
- Success rate
- Maximum variables/constraints
- Recent problems list

**History Data:**

Stored in same SQLite database as logs, includes:

- File content
- Problem parameters
- Solution details
- Execution metadata

### system_analyzer.py - System Capabilities Analyzer

Analyzes system hardware and provides recommendations for Ollama model selection.

**Usage:**

```python
from tools.system_analyzer import SystemAnalyzer

analyzer = SystemAnalyzer()
capabilities = analyzer.analyze_system()

print(f"RAM: {capabilities.ram_gb} GB")
print(f"CPU Cores: {capabilities.cpu_count}")
print(f"Has NVIDIA GPU: {capabilities.has_nvidia_gpu}")

# Get model recommendations
recommendations = analyzer.get_model_recommendations()
for rec in recommendations:
    print(f"{rec.model_name}: {rec.recommendation_level}")
```

**Used by:**

- `installer.py` for automatic model recommendations

### test_installer.py - Installer Tests

Test suite for the interactive installer functionality.

**Usage:**

```powershell
python -m pytest tools/test_installer.py -v
```

**Tests:**

- System capabilities detection
- Model recommendations
- Installation workflows

## Requirements

All tools require the project's base dependencies:

```powershell
pip install -r requirements.txt
```

For building executables:

```powershell
pip install -r requirements-build.txt
```

## Architecture Principles

All tools follow SOLID principles:

- **Single Responsibility**: Each class/function has one clear purpose
- **Open/Closed**: Extendable without modifying existing code
- **Liskov Substitution**: Interfaces are properly abstracted
- **Interface Segregation**: No forced dependencies on unused methods
- **Dependency Inversion**: Depend on abstractions, not concretions

## Examples

### Building for Release

```powershell
# Clean previous builds
python tools/build.py --clean

# Build both executables
python tools/build.py --all

# Verify outputs
ls dist/
```

### Checking Logs After Error

```powershell
# Quick check
python tools/logs.py --stats

# Full verification
python tools/logs.py --verify

# Interactive viewing
python tools/logs.py
```

### Reviewing Problem History

```powershell
# Quick stats
python tools/history.py --stats

# Find and re-solve a problem
python tools/history.py
# Then select option to view/re-solve
```

## Output Format

All tools use consistent output formatting:

- `[OK]` - Successful operation
- `[ERROR]` - Error occurred
- `[WARNING]` - Warning message
- `[INFO]` - Informational message
- `[STATS]` - Statistical information
- `[BUILD]` - Build-related message
- `[CLEAN]` - Cleanup operation

No emojis are used to maintain professional output.

## Error Handling

All tools implement comprehensive error handling:

- Clear error messages
- Traceback printing for debugging
- Graceful failure with appropriate exit codes
- File/database existence checks

## Testing

Tools can be tested individually:

```powershell
# Test build system (dry run with --help)
python tools/build.py --help

# Test log system
python tools/logs.py --verify

# Test history system
python tools/history.py --test
```

## Integration with CI/CD

These tools are designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Build executables
  run: python tools/build.py --all

- name: Verify logs
  run: python tools/logs.py --verify
```

## Maintenance

### Adding New Build Targets

Edit `build.py` and add a new `BuildConfig` to `BuildOrchestrator.CONFIGS`:

```python
CONFIGS = {
    "new_target": BuildConfig(
        name="New Target",
        script="new_script.py",
        output_name="NewExecutable",
        add_data=[...],
        hidden_imports=[...],
        excludes=[...],
    )
}
```

### Extending Log Viewer

Subclass `LogViewer` in `simplex_solver/log_viewer.py` to add new features.

### Adding History Features

Extend `ProblemHistory` class in `simplex_solver/problem_history.py`.

## Troubleshooting

### Build Fails

```powershell
# Ensure PyInstaller is installed
pip install pyinstaller

# Check for import errors
python -c "import simplex_solver"

# Verify all dependencies
pip install -r requirements.txt
```

### Log Viewer Errors

```powershell
# Check database exists
python tools/logs.py --verify

# If missing, run solver once to create it
python simplex.py --interactive
```

### History Empty

The history only stores problems with optimal solutions. Solve at least one valid problem first.

## Performance

- **Build time**: ~30-60 seconds per executable
- **Log viewer**: Handles 10,000+ log entries efficiently
- **History**: SQLite database scales to thousands of problems

## Security

- All tools run locally, no external network calls
- SQLite databases use appropriate file permissions
- Build artifacts are gitignored

## Contributing

When adding new tools:

1. Follow SOLID principles
2. Add comprehensive docstrings
3. Implement `--help` flag
4. Use consistent error handling
5. Update this README
6. Add tests if applicable

## References

- **Main Documentation**: `GUIA_DESARROLLADOR.md`
- **User Guide**: `GUIA_USUARIO.md`
- **Build Configuration**: `pyproject.toml`

---

**Last Updated**: November 2025
**Version**: 3.1
