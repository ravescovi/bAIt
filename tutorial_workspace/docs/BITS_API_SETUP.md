# Creating my_beamline with BITS API

This document shows how to properly create the `my_beamline` project using the BITS framework API and tools.

## Method 1: Using create-bits Command (Recommended)

The BITS framework provides a `create-bits` command for creating new instrument packages:

```bash
# Navigate to tutorial workspace
cd /home/ravescovi/workspace/bAIt/tutorial_workspace

# Ensure BITS environment is active
conda activate BITS_demo

# Create the instrument package using BITS
create-bits my_beamline

# This creates src/my_beamline/ with proper BITS structure
```

**What create-bits creates:**
- `src/my_beamline/startup.py` - BITS-powered startup module
- `src/my_beamline/configs/` - YAML configuration files
- `src/my_beamline/devices/` - Device definition modules
- `src/my_beamline/plans/` - Custom scan plans
- `src/my_beamline/callbacks/` - Data writing callbacks
- `src/my_beamline/suspenders/` - Safety suspenders
- `src/my_beamline/utils/` - Utility functions

## Method 2: Manual BITS Integration

If you need to create the structure manually (like for tutorial purposes), use these BITS components:

### Startup Module with BITS

```python
"""
BITS-powered startup module for my_beamline
"""

from apsbits.startup import InstrumentStartup
from pathlib import Path

# Get configuration directory  
config_dir = Path(__file__).parent / "configs"

# Initialize BITS instrument
instrument = InstrumentStartup(
    config_path=config_dir / "iconfig.yml",
    device_config_path=config_dir / "devices.yml"
)

# Start the instrument (creates RE, db, bec)
instrument.startup()

# Access BITS-created objects
RE = instrument.RE
db = instrument.db
bec = instrument.bec
```

### Device Configuration with BITS

```python
from apsbits.devices import EpicsMotorDevice, ScalerDevice

# Create devices using BITS device classes
m1 = EpicsMotorDevice("gp:m1", name="m1")
scaler1 = ScalerDevice("gp:scaler1", name="scaler1")
```

### Callbacks with BITS

```python
from apsbits.callbacks import SpecWriterCallback, NeXusWriterCallback

# BITS callbacks with built-in functionality
spec_writer = SpecWriterCallback(
    filename="my_beamline_data.spec",
    auto_write=True
)

nexus_writer = NeXusWriterCallback(
    filename_template="scan_{scan_id}.h5"
)
```

## Current Tutorial Workspace Status

The tutorial workspace currently contains:
- ✅ Basic project structure created manually
- ✅ Placeholder startup module (needs BITS integration)
- ✅ Configuration templates
- ❌ **Needs**: Proper BITS API integration

## Next Steps

1. **Replace manual structure** with `create-bits` generated structure
2. **Update tutorials** to show proper BITS workflow
3. **Test integration** with actual BITS framework

## BITS vs Manual Comparison

| Aspect | Manual Creation | BITS create-bits |
|--------|----------------|------------------|
| Setup time | 30+ minutes | 2 minutes |
| Configuration | Manual YAML writing | Pre-configured templates |
| Device integration | Manual ophyd setup | BITS device classes |  
| Data management | Manual broker setup | Auto-configured |
| Queue server | Manual setup | Built-in integration |
| Best practices | User responsibility | Enforced by framework |

**Recommendation**: Use `create-bits` for real beamline development, manual for learning internal details.