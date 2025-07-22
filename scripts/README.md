# bAIt Submodule Management Scripts

This directory contains Python scripts for managing the complex submodule structure of the bAIt repository.

## Scripts

- **`check-submodule-access.py`** - Check user access to all configured submodules
- **`init-accessible-submodules.py`** - Initialize only accessible submodules
- **`diagnose-submodule-issues.py`** - Diagnose and troubleshoot submodule issues

## Quick Start

```bash
# Check which repositories you can access
python scripts/check-submodule-access.py

# Initialize only accessible repositories
python scripts/init-accessible-submodules.py

# Troubleshoot any issues
python scripts/diagnose-submodule-issues.py
```

## Requirements

- Python 3.6+
- Git 2.0+
- Network connectivity

## Documentation

See **[bait_base/docs/submodule-scripts.md](../bait_base/docs/submodule-scripts.md)** for complete documentation.

## Usage Examples

### For New Users
```bash
# Start here if you're new to the repository
python scripts/check-submodule-access.py --fix-permissions
python scripts/init-accessible-submodules.py --dry-run
python scripts/init-accessible-submodules.py
```

### For Troubleshooting
```bash
# If you're having submodule issues
python scripts/diagnose-submodule-issues.py --verbose
python scripts/diagnose-submodule-issues.py --fix-suggestions
```

### For Automation
```bash
# Check access in JSON format for scripting
python scripts/check-submodule-access.py --json

# Force initialization without prompts
python scripts/init-accessible-submodules.py --force
```