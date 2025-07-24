# Migration Guide: Profile Collection to BITS Deployment

## Overview

This guide documents the complete process for migrating from a traditional NSLS-II profile collection startup script approach (`nsls_deployments/tst-profile-collection/`) to a modern BITS deployment structure (`bits_deployments/tst-nsls-bits/`).

## Migration Rationale

### Benefits of BITS Deployment
- **Enhanced Error Handling**: Comprehensive error recovery and validation
- **Structured Configuration**: YAML-based config management vs hardcoded values
- **Advanced Device Features**: Enhanced wrapper classes with labels and metadata
- **Testing Support**: Built-in simulation and mock mode capabilities
- **Documentation**: Comprehensive docstrings and structured documentation
- **Maintainability**: Modern Python package structure with clear separation of concerns
- **Framework Integration**: Full BITS framework support with callbacks and utilities

### What Gets Migrated
- ✅ **Device Definitions**: Motor, detectors, PandA → Enhanced wrapper classes
- ✅ **Plan Implementations**: Core plans → Enhanced versions with metadata
- ✅ **Configuration**: Hardcoded values → YAML configuration files
- ✅ **Package Structure**: Startup scripts → Modern Python package
- ✅ **Additional Features**: Simulation plans, calibration, advanced coordination

## Migration Architecture Overview

```
Profile Collection Structure          BITS Deployment Structure
├── startup/                     →    ├── src/tst_instrument/
│   ├── 00-startup.py           →    │   ├── __init__.py
│   ├── 03-providers.py         →    │   ├── startup.py
│   ├── 05-motors.py            →    │   ├── devices/
│   ├── 10-panda.py             →    │   │   ├── tst_motor.py
│   ├── 15-manta.py             →    │   │   ├── tst_detector.py
│   ├── 90-plans.py             →    │   │   ├── tst_panda.py
│   └── 99-pvscan.py            →    │   │   └── tst_flyer.py
└── existing_plans_and_devices.yaml  │   ├── plans/
                                →    │   │   ├── sim_plans.py
                                     │   │   ├── tomography_plans.py
                                     │   │   └── xas_plans.py
                                     │   ├── configs/
                                     │   │   ├── devices.yml
                                     │   │   └── iconfig.yml
                                     │   ├── callbacks/
                                     │   ├── utils/
                                     │   └── suspenders/
                                     └── pyproject.toml
```

## Phase 1: Project Structure Setup

### 1.1 Create BITS Package Structure

```bash
# Create main package structure
mkdir -p bits_deployments/tst-nsls-bits/src/tst_instrument/{devices,plans,configs,callbacks,utils,suspenders}

# Create core files
touch bits_deployments/tst-nsls-bits/src/tst_instrument/__init__.py
touch bits_deployments/tst-nsls-bits/pyproject.toml
```

### 1.2 Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "tst-nsls-bits"
version = "0.1.0"
description = "TST NSLS-II BITS Deployment"
dependencies = [
    "ophyd-async",
    "bluesky",
    "apsbits",
    "pyyaml",
    "h5py",
    "numpy",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "black",
    "ruff",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

## Phase 2: Device Migration

### 2.1 Motor Migration Pattern

**From** (`startup/05-motors.py`):
```python
from ophyd_async.epics.motor import Motor

with init_devices(mock=RUNNING_IN_NSLS2_CI):
    rot_motor = Motor("XF:31ID1-OP:1{CMT:1-Ax:Rot}Mtr", name="rot_motor")
```

**To** (`src/tst_instrument/devices/tst_motor.py`):
```python
"""TST NSLS-II Motor Device"""

import logging
import os
from ophyd_async.core import init_devices
from ophyd_async.epics.motor import Motor

logger = logging.getLogger(__name__)

class TSTMotor(Motor):
    """TST beamline motor device with enhanced features."""
    
    def __init__(self, prefix: str, name: str = "", labels=None, **kwargs):
        mock_mode = (
            os.environ.get("TST_MOCK_MODE", "NO") == "YES"
            or os.environ.get("RUNNING_IN_NSLS2_CI", "NO") == "YES"
        )
        
        self._labels = labels or []
        
        with init_devices(mock=mock_mode):
            super().__init__(prefix, name=name, **kwargs)
            
        logger.info(f"Initialized TST motor '{name}' with prefix '{prefix}' (mock={mock_mode})")
```

### 2.2 Detector Migration Pattern

**From** (`startup/15-manta.py`):
```python
def instantiate_manta_async(manta_id):
    with init_devices(mock=RUNNING_IN_NSLS2_CI):
        manta_async = VimbaDetector(
            f"XF:31ID1-ES{{GigE-Cam:{manta_id}}}",
            TSTPathProvider(RE.md),
            name=f"manta{manta_id}",
        )
    return manta_async

manta1 = instantiate_manta_async(1)
manta2 = instantiate_manta_async(2)
```

**To** (`src/tst_instrument/devices/tst_detector.py`):
```python
"""TST NSLS-II VimbaDetector Device"""

import logging
import os
from ophyd_async.core import init_devices
from ophyd_async.epics.advimba import VimbaDetector
from tst_instrument.utils.providers import get_tst_path_provider

logger = logging.getLogger(__name__)

class TSTDetector(VimbaDetector):
    """TST beamline VimbaDetector device with enhanced features."""
    
    def __init__(self, prefix: str, name: str = "", labels=None, **kwargs):
        mock_mode = (
            os.environ.get("TST_MOCK_MODE", "NO") == "YES"
            or os.environ.get("RUNNING_IN_NSLS2_CI", "NO") == "YES"
        )
        
        self._labels = labels or []
        path_provider = get_tst_path_provider(mock_mode=mock_mode)
        
        with init_devices(mock=mock_mode):
            super().__init__(prefix, path_provider, name=name, **kwargs)
            
        logger.info(f"Initialized TST detector '{name}' with prefix '{prefix}' (mock={mock_mode})")
```

### 2.3 PandA Migration Pattern

**From** (`startup/10-panda.py`):
```python
def instantiate_panda_async(panda_id):
    with init_devices(mock=RUNNING_IN_NSLS2_CI):
        panda = HDFPanda(
            f"XF:31ID1-ES{{PANDA:{panda_id}}}:",
            TSTPathProvider(RE.md),
            name=f"panda{panda_id}",
        )
    return panda

panda1 = instantiate_panda_async(1)
```

**To** (`src/tst_instrument/devices/tst_panda.py`):
```python
"""TST NSLS-II HDFPanda Device"""

import logging
import os
from ophyd_async.core import init_devices
from ophyd_async.fastcs.panda import HDFPanda
from tst_instrument.utils.providers import get_tst_path_provider

logger = logging.getLogger(__name__)

class TSTPanda(HDFPanda):
    """TST beamline HDFPanda device with enhanced features."""
    
    def __init__(self, prefix: str, name: str = "", labels=None, **kwargs):
        mock_mode = (
            os.environ.get("TST_MOCK_MODE", "NO") == "YES"
            or os.environ.get("RUNNING_IN_NSLS2_CI", "NO") == "YES"
        )
        
        self._labels = labels or []
        path_provider = get_tst_path_provider(mock_mode=mock_mode)
        
        with init_devices(mock=mock_mode):
            super().__init__(prefix, path_provider, name=name, **kwargs)
            
        logger.info(f"Initialized TST PandA '{name}' with prefix '{prefix}' (mock={mock_mode})")
```

### 2.4 Configuration Migration

**Create** (`src/tst_instrument/configs/devices.yml`):
```yaml
# TST NSLS-II Device Configuration
motors:
  rot_motor:
    prefix: "XF:31ID1-OP:1{CMT:1-Ax:Rot}Mtr"
    name: "rot_motor"
    labels: ["rotation", "sample"]

detectors:
  manta1:
    prefix: "XF:31ID1-ES{GigE-Cam:1}"
    name: "manta1"
    labels: ["detector", "camera"]
  manta2:
    prefix: "XF:31ID1-ES{GigE-Cam:2}"
    name: "manta2"
    labels: ["detector", "camera"]

pandas:
  panda1:
    prefix: "XF:31ID1-ES{PANDA:1}:"
    name: "panda1"
    labels: ["trigger", "coordination"]
```

## Phase 3: Plan Migration

### 3.1 Plan Migration Pattern

**From** (`startup/90-plans.py`):
```python
def tomo_demo_async(
    detectors,
    panda,
    num_images=21,
    scan_time=9,
    start_deg=0,
    exposure_time=None,
):
    # Basic implementation with minimal metadata
    yield from bps.open_run()
    # ... rest of implementation
    yield from bps.close_run()
```

**To** (`src/tst_instrument/plans/tomography_plans.py`):
```python
"""TST NSLS-II Tomography Plans"""

import logging
from typing import List, Optional
import bluesky.plan_stubs as bps
from apsbits.core.instrument_init import oregistry
from bluesky.utils import make_decorator
from ophyd_async.core import TriggerInfo
from ophyd_async.epics.motor import FlyMotorInfo

logger = logging.getLogger(__name__)

DEFAULT_MD = {"title": "TST Tomography Scan"}

def tomo_demo_async(
    detectors: Optional[List] = None,
    num_images: int = 21,
    scan_time: float = 9,
    start_deg: float = 0,
    exposure_time: Optional[float] = None,
    md: dict = DEFAULT_MD,
):
    """
    Enhanced tomography plan with comprehensive metadata and error handling.
    
    Parameters
    ----------
    detectors : List, optional
        List of detector objects. If None, uses [manta1] from oregistry
    num_images : int, optional
        Number of images to collect, by default 21
    scan_time : float, optional
        Total scan time in seconds, by default 9
    start_deg : float, optional
        Starting rotation angle in degrees, by default 0
    exposure_time : float, optional
        Exposure time per image. If None, calculated automatically.
    md : dict, optional
        Metadata dictionary
    """
    logger.info(f"Starting tomography scan: {num_images} images over {scan_time}s")

    # Get devices with error handling
    if detectors is None:
        detectors = [oregistry.find(name="manta1")]
    panda = oregistry.find(name="panda1")
    rot_motor = oregistry.find(name="rot_motor")

    # Enhanced metadata
    _md = {
        "plan_name": "tomo_demo_async",
        "beamline_id": "tst_nsls",
        "scan_type": "tomography",
        "num_images": num_images,
        "scan_time": scan_time,
        "start_deg": start_deg,
        "exposure_time": exposure_time,
        "detectors": [det.name for det in detectors],
        "motors": [rot_motor.name],
        **md,
    }

    yield from bps.open_run(md=_md)
    # ... enhanced implementation with validation
    yield from bps.close_run()
    
    logger.info("Tomography scan completed successfully")

# Apply decorator for proper plan metadata
tomo_demo_async = make_decorator(tomo_demo_async)
```

### 3.2 Add New Simulation Plans

**Create** (`src/tst_instrument/plans/sim_plans.py`):
```python
"""Simulation Plans for Development and Testing"""

import logging
from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps
from bluesky import plans as bp

logger = logging.getLogger(__name__)
DEFAULT_MD = {"title": "test run with simulator(s)"}

def sim_count_plan(detector=None, num: int = 1, imax: float = 10_000, md: dict = None):
    """Demonstrate the count() plan with simulators."""
    logger.debug("sim_count_plan()")
    
    if md is None:
        md = DEFAULT_MD
    
    if detector is None:
        try:
            detector = oregistry["sim_det"]
        except KeyError:
            logger.error("sim_det not found in oregistry")
            return
    
    if hasattr(detector, 'Imax'):
        yield from bps.mv(detector.Imax, imax)
    
    yield from bp.count([detector], num=num, md=md)

# Additional simulation plans...
```

## Phase 4: Enhanced Features Migration

### 4.1 Advanced Flyer Implementation

**Create** (`src/tst_instrument/devices/tst_flyer.py`):
```python
"""TST NSLS-II Advanced Flyer Devices"""

import asyncio
import logging
from enum import Enum
from typing import Dict, List, Optional
from ophyd_async.core import StandardFlyer, TriggerLogic, TriggerInfo, DetectorTrigger

logger = logging.getLogger(__name__)

class TriggerState(str, Enum):
    """Enumeration of flyer trigger states for coordination."""
    NULL = "null"
    PREPARING = "preparing"
    STARTING = "starting"
    STOPPING = "stopping"
    COMPLETE = "complete"
    ERROR = "error"

class TSTTriggerLogic(TriggerLogic):
    """TST-specific trigger logic with advanced coordination capabilities."""
    
    def __init__(self, name: str = "tst_trigger_logic"):
        super().__init__()
        self.name = name
        self.state = TriggerState.NULL
        self._timing_params: Dict[str, float] = {}
    
    def trigger_info(self, value: int) -> TriggerInfo:
        """Generate trigger information with TST-specific timing."""
        deadtime = max(0.001, 0.1 / value)
        livetime = deadtime * 0.9
        
        self._timing_params = {
            "num_triggers": value,
            "deadtime": deadtime,
            "livetime": livetime,
            "total_time": value * deadtime,
        }
        
        return TriggerInfo(
            num=value,
            trigger=DetectorTrigger.constant_gate,
            deadtime=deadtime,
            livetime=livetime,
        )

class TSTFlyerCoordinator:
    """Advanced flyer coordinator for multi-device synchronized acquisition."""
    
    def __init__(self, name: str = "tst_flyer_coordinator"):
        self.name = name
        self.flyers: Dict[str, StandardFlyer] = {}
        self._prepared = False
    
    def add_flyer(self, key: str, flyer: StandardFlyer):
        """Add a flyer to the coordination group."""
        self.flyers[key] = flyer
        logger.info(f"{self.name}: Added flyer '{key}' to coordination group")
    
    async def prepare_all(self, value: int):
        """Prepare all flyers with timing coordination."""
        logger.info(f"{self.name}: Preparing {len(self.flyers)} flyers for {value} frames")
        
        for key, flyer in self.flyers.items():
            await flyer.prepare(value)
        
        self._prepared = True
    
    async def kickoff_all(self):
        """Start all flyers with synchronization."""
        if not self._prepared:
            raise RuntimeError(f"{self.name}: Not prepared for kickoff")
        
        tasks = [flyer.kickoff() for flyer in self.flyers.values()]
        await asyncio.gather(*tasks)
    
    async def complete_all(self):
        """Complete all flyers and collect results."""
        tasks = [flyer.complete() for flyer in self.flyers.values()]
        await asyncio.gather(*tasks)
        self._prepared = False

def create_advanced_flyer_coordinator(detectors=None, panda=None, name="tst_coordinator"):
    """Factory function for creating advanced flyer coordinator."""
    coordinator = TSTFlyerCoordinator(name)
    
    if detectors:
        for i, detector in enumerate(detectors):
            if hasattr(detector, "hdf"):
                flyer = StandardFlyer(name=f"manta_flyer_{i}")
                coordinator.add_flyer(f"manta_{i}", flyer)
    
    if panda:
        panda_flyer = StandardFlyer(name="advanced_panda_flyer")
        coordinator.add_flyer("panda", panda_flyer)
    
    return coordinator
```

### 4.2 Utilities Migration

**Create** (`src/tst_instrument/utils/providers.py`):
```python
"""TST Path Provider Utilities"""

import os
from pathlib import Path

def get_tst_path_provider(mock_mode: bool = False):
    """
    Get TST-specific path provider for NSLS-II compliant data organization.
    
    Parameters
    ----------
    mock_mode : bool
        If True, use mock paths for testing
        
    Returns
    -------
    PathProvider
        Configured path provider instance
    """
    if mock_mode:
        base_path = Path("/tmp/tst_mock_data")
        base_path.mkdir(exist_ok=True)
    else:
        base_path = Path(os.environ.get("TST_DATA_PATH", "/nsls2/data/tst/legacy"))
    
    # Implementation would depend on your specific path provider class
    # This is a placeholder for the actual implementation
    from your_path_provider_module import TSTPathProvider
    return TSTPathProvider(base_path)
```

## Phase 5: Configuration and Integration

### 5.1 Main Startup File

**Create** (`src/tst_instrument/startup.py`):
```python
"""TST NSLS-II BITS Deployment Startup"""

import os
import yaml
from pathlib import Path
from apsbits.core.instrument_init import oregistry

# Load configuration
config_path = Path(__file__).parent / "configs" / "devices.yml"
with open(config_path) as f:
    config = yaml.safe_load(f)

# Import device classes
from tst_instrument.devices.tst_motor import TSTMotor
from tst_instrument.devices.tst_detector import TSTDetector
from tst_instrument.devices.tst_panda import TSTPanda

# Create devices from configuration
def create_devices():
    """Create all TST devices from configuration."""
    devices = {}
    
    # Create motors
    for name, motor_config in config.get("motors", {}).items():
        devices[name] = TSTMotor(
            prefix=motor_config["prefix"],
            name=motor_config["name"],
            labels=motor_config.get("labels", [])
        )
    
    # Create detectors
    for name, det_config in config.get("detectors", {}).items():
        devices[name] = TSTDetector(
            prefix=det_config["prefix"],
            name=det_config["name"],
            labels=det_config.get("labels", [])
        )
    
    # Create PandAs
    for name, panda_config in config.get("pandas", {}).items():
        devices[name] = TSTPanda(
            prefix=panda_config["prefix"],
            name=panda_config["name"],
            labels=panda_config.get("labels", [])
        )
    
    return devices

# Create and register devices
tst_devices = create_devices()
for name, device in tst_devices.items():
    oregistry[name] = device

# Import plans
from tst_instrument.plans.tomography_plans import tomo_demo_async
from tst_instrument.plans.xas_plans import xas_demo_async, energy_calibration_plan
from tst_instrument.plans.sim_plans import sim_count_plan, sim_print_plan, sim_rel_scan_plan

# Create flyers with TST enhancement
from tst_instrument.devices.tst_flyer import create_tst_flyers
mock_mode = os.environ.get("TST_MOCK_MODE", "NO") == "YES"
tst_flyers = create_tst_flyers(mock=mock_mode)
for name, flyer in tst_flyers.items():
    oregistry[name] = flyer

print("TST NSLS-II BITS deployment startup complete")
```

## Phase 6: Step-by-Step Migration Checklist

### 6.1 Pre-Migration Preparation
- [ ] **Backup existing profile-collection**
- [ ] **Document current device PV prefixes and names**
- [ ] **Test current functionality to establish baseline**
- [ ] **Set up development environment with required dependencies**

### 6.2 Package Structure Creation
- [ ] **Create BITS package directory structure**
- [ ] **Create pyproject.toml with dependencies**
- [ ] **Set up __init__.py files in all package directories**
- [ ] **Create configuration directory and YAML files**

### 6.3 Device Migration (Do in Order)
- [ ] **Migrate utilities first** (providers.py)
- [ ] **Migrate motor devices** (startup/05-motors.py → devices/tst_motor.py)
- [ ] **Migrate detector devices** (startup/15-manta.py → devices/tst_detector.py)
- [ ] **Migrate PandA devices** (startup/10-panda.py → devices/tst_panda.py)
- [ ] **Create advanced flyer classes** (devices/tst_flyer.py)
- [ ] **Test each device class individually**

### 6.4 Plan Migration
- [ ] **Migrate tomography plans** (90-plans.py → plans/tomography_plans.py)
- [ ] **Migrate XAS plans** (90-plans.py → plans/xas_plans.py)
- [ ] **Add simulation plans** (plans/sim_plans.py)
- [ ] **Add calibration plans** (energy_calibration_plan)
- [ ] **Test each plan individually**

### 6.5 Configuration Migration
- [ ] **Extract hardcoded values to YAML config**
- [ ] **Create devices.yml with all device configurations**
- [ ] **Create iconfig.yml for instrument configuration**
- [ ] **Update startup.py to use configuration files**

### 6.6 Integration and Testing
- [ ] **Create startup.py that initializes everything**
- [ ] **Test device creation and oregistry registration**
- [ ] **Test plan execution with new device classes**
- [ ] **Verify mock mode functionality**
- [ ] **Test error handling and logging**

### 6.7 Documentation and Cleanup
- [ ] **Update README with new structure and usage**
- [ ] **Document new features and capabilities**
- [ ] **Create development and testing guides**
- [ ] **Remove old profile-collection files (after verification)**

## Phase 7: Validation and Testing

### 7.1 Device Validation
```python
# Test device creation and basic functionality
def test_device_migration():
    """Validate that migrated devices work correctly."""
    
    # Test motor
    from tst_instrument.devices.tst_motor import TSTMotor
    motor = TSTMotor("XF:31ID1-OP:1{CMT:1-Ax:Rot}Mtr", name="test_motor")
    assert motor.name == "test_motor"
    
    # Test detector
    from tst_instrument.devices.tst_detector import TSTDetector
    detector = TSTDetector("XF:31ID1-ES{GigE-Cam:1}", name="test_detector")
    assert detector.name == "test_detector"
    
    # Test PandA
    from tst_instrument.devices.tst_panda import TSTPanda
    panda = TSTPanda("XF:31ID1-ES{PANDA:1}:", name="test_panda")
    assert panda.name == "test_panda"
    
    print("✅ Device migration validation passed")
```

### 7.2 Plan Validation
```python
# Test plan execution
def test_plan_migration():
    """Validate that migrated plans work correctly."""
    
    from tst_instrument.plans.tomography_plans import tomo_demo_async
    from tst_instrument.plans.xas_plans import xas_demo_async
    from tst_instrument.plans.sim_plans import sim_count_plan
    
    # Verify plans are callable and have proper signatures
    import inspect
    
    tomo_sig = inspect.signature(tomo_demo_async)
    assert 'detectors' in tomo_sig.parameters
    assert 'num_images' in tomo_sig.parameters
    
    xas_sig = inspect.signature(xas_demo_async)
    assert 'npoints' in xas_sig.parameters
    assert 'total_time' in xas_sig.parameters
    
    sim_sig = inspect.signature(sim_count_plan)
    assert 'detector' in sim_sig.parameters
    assert 'num' in sim_sig.parameters
    
    print("✅ Plan migration validation passed")
```

### 7.3 Configuration Validation
```python
# Test configuration loading
def test_config_migration():
    """Validate configuration system works correctly."""
    
    import yaml
    from pathlib import Path
    
    config_path = Path("src/tst_instrument/configs/devices.yml")
    assert config_path.exists(), "devices.yml must exist"
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Verify required sections exist
    assert "motors" in config
    assert "detectors" in config
    assert "pandas" in config
    
    # Verify required fields
    for motor_name, motor_config in config["motors"].items():
        assert "prefix" in motor_config
        assert "name" in motor_config
    
    print("✅ Configuration migration validation passed")
```

## Troubleshooting Common Migration Issues

### Issue 1: Import Errors
**Problem**: `ModuleNotFoundError` when importing migrated modules
**Solution**: 
- Verify `__init__.py` files exist in all directories
- Check `PYTHONPATH` includes the src directory
- Ensure package is installed in development mode: `pip install -e .`

### Issue 2: Device Creation Failures
**Problem**: Devices fail to initialize with new wrapper classes
**Solution**:
- Verify PV prefixes are correct in configuration files
- Check mock mode environment variables
- Ensure path providers are properly configured

### Issue 3: Plan Execution Errors
**Problem**: Plans fail with oregistry lookup errors
**Solution**:
- Verify devices are properly registered in oregistry
- Check device names match between configuration and plan code
- Ensure startup.py is executed before plan execution

### Issue 4: Configuration Loading Issues
**Problem**: YAML configuration files not found or malformed
**Solution**:
- Verify file paths are correct relative to package structure
- Validate YAML syntax using online validators
- Check file permissions and accessibility

## Post-Migration Verification

### Verification Checklist
- [ ] **All original functionality preserved**
- [ ] **Enhanced error handling working**
- [ ] **Configuration system operational**
- [ ] **Mock mode functioning**
- [ ] **Logging output appropriate**
- [ ] **Documentation complete and accurate**
- [ ] **Performance comparable or improved**

### Success Criteria
✅ **Core Functionality**: All original plans execute successfully
✅ **Enhanced Features**: New simulation and calibration plans work
✅ **Configuration**: YAML-based config system operational
✅ **Error Handling**: Improved error messages and recovery
✅ **Documentation**: Complete migration documentation
✅ **Testing**: Comprehensive test coverage

---

## Summary

This migration guide provides a complete roadmap for transforming a traditional NSLS-II profile collection into a modern BITS deployment. The process involves:

1. **Structural transformation** from startup scripts to Python package
2. **Device enhancement** with wrapper classes and configuration
3. **Plan modernization** with metadata and error handling
4. **Feature addition** with simulation and calibration capabilities
5. **Testing integration** with mock modes and validation

Following this guide ensures a systematic, verifiable migration that preserves existing functionality while adding significant improvements in maintainability, testability, and usability.