# my_beamline - Example Beamline Package

This is an example beamline instrument package created during the BITS tutorial.

## Structure

```
src/my_beamline/
├── __init__.py          # Package initialization
├── startup.py           # Main startup module
├── configs/             # Configuration files
│   ├── iconfig.yml      # Instrument configuration
│   └── devices.yml      # Device definitions
├── devices/             # Device implementations
├── plans/               # Custom scan plans
├── callbacks/           # Data writing callbacks
├── suspenders/          # Safety suspenders
└── utils/              # Utility functions
```

## Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

```python
# Import and start the beamline
from my_beamline.startup import *

# Run a simple count
RE(bp.count([detector], num=3))

# Run a motor scan
RE(bp.scan([detector], motor, -1, 1, 11))
```

## Tutorial Progress

This package structure is progressively built during the BITS tutorial:

- [ ] Step 1: IOC Exploration
- [ ] Step 2: Device Configuration  
- [ ] Step 3: Plan Development
- [ ] Step 4: Interactive Use
- [ ] Step 5: Remote Execution

Check each tutorial step to see how components are added and configured.