# Functionality Comparison Report: TST NSLS-II Deployments

## Overview

This report compares the functionality of devices and plans between two TST NSLS-II beamline deployments:

1. **BITS Deployment**: `bits_deployments/tst-nsls-bits/` - Modern, structured, object-oriented approach
2. **Profile Collection**: `nsls_deployments/tst-profile-collection/` - Traditional startup-script approach

## Device Comparison

### Motors

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Implementation** | TSTMotor class (enhanced Motor) | Direct Motor instantiation |
| **File Location** | `src/tst_instrument/devices/tst_motor.py` | `startup/05-motors.py` |
| **Mock Mode Support** | ✅ Environment variable controlled | ✅ RUNNING_IN_NSLS2_CI flag |
| **BITS Framework Integration** | ✅ Labels support, structured init | ❌ Basic instantiation |
| **Configuration Management** | ✅ Via configs/devices.yml | ❌ Hardcoded PV prefixes |
| **Logging** | ✅ Structured logging with context | ❌ Basic print statements |

**BITS Motor Code:**
```python
class TSTMotor(Motor):
    def __init__(self, prefix: str, name: str = "", labels=None, **kwargs):
        # Enhanced with TST-specific configuration
        mock_mode = os.environ.get("TST_MOCK_MODE", "NO") == "YES"
        self._labels = labels or []
        with init_devices(mock=mock_mode):
            super().__init__(prefix, name=name, **kwargs)
```

**Profile Collection Motor Code:**
```python
with init_devices(mock=RUNNING_IN_NSLS2_CI):
    rot_motor = Motor("XF:31ID1-OP:1{CMT:1-Ax:Rot}Mtr", name="rot_motor")
```

### Detectors

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Implementation** | TSTDetector class (enhanced VimbaDetector) | Direct VimbaDetector instantiation |
| **File Location** | `src/tst_instrument/devices/tst_detector.py` | `startup/15-manta.py` |
| **Path Provider** | ✅ TST-specific path provider integration | ✅ TSTPathProvider |
| **Multiple Detectors** | ✅ Configurable via YAML | ✅ manta1, manta2 hardcoded |
| **Enhancement Features** | ✅ Labels, structured initialization | ❌ Basic functionality |
| **Error Handling** | ✅ Comprehensive error context | ❌ Basic error handling |

### PandA Devices

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Implementation** | TSTPanda class (enhanced HDFPanda) | Direct HDFPanda instantiation |
| **File Location** | `src/tst_instrument/devices/tst_panda.py` | `startup/10-panda.py` |
| **Path Provider** | ✅ TST path provider integration | ✅ TSTPathProvider |
| **BITS Integration** | ✅ Labels, metadata support | ❌ Basic functionality |
| **Initialization** | ✅ Structured with error handling | ❌ Simple instantiation |

### Flyer Devices

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Implementation** | Comprehensive flyer ecosystem | Basic StandardFlyer |
| **File Location** | `src/tst_instrument/devices/tst_flyer.py` | Imported from ophyd_async |
| **Flyer Types** | ✅ TSTFlyer, TSTMantaFlyer, TSTPandAFlyer | ❌ Generic StandardFlyer |
| **Advanced Features** | ✅ Coordination, timing validation | ❌ Basic flyer functionality |
| **Trigger Logic** | ✅ TSTTriggerLogic with state management | ❌ Default trigger logic |
| **Multi-Device Coordination** | ✅ TSTFlyerCoordinator | ❌ Manual coordination |

**BITS Advanced Flyer Features:**
- State management with TriggerState enum
- Timing validation and parameter optimization
- Multi-device coordination with TSTFlyerCoordinator
- Specialized flyers for Manta and PandA devices
- Advanced error recovery and validation

## Plan Comparison

### Tomography Plans

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Function Name** | `tomo_demo_async` | `tomo_demo_async` |
| **File Location** | `src/tst_instrument/plans/tomography_plans.py` | `startup/90-plans.py` |
| **Parameters** | Enhanced with optional parameters | Direct parameter passing |
| **Device Access** | ✅ oregistry with error handling | ✅ Direct oregistry access |
| **Metadata** | ✅ Comprehensive structured metadata | ❌ No metadata |
| **Error Handling** | ✅ Comprehensive validation | ✅ Basic validation |
| **Logging** | ✅ Structured logging throughout | ❌ Print statements only |
| **Documentation** | ✅ Comprehensive docstrings | ❌ Minimal comments |

**BITS Enhanced Features:**
- Comprehensive parameter validation
- Structured metadata with beamline_id, scan_type
- Device error handling with fallbacks
- Enhanced logging with context
- Dark/flat field collection support

### XAS Plans

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Function Name** | `xas_demo_async` | `xas_demo_async` |
| **File Location** | `src/tst_instrument/plans/xas_plans.py` | `startup/90-plans.py` |
| **Advanced Coordination** | ✅ TSTFlyerCoordinator integration | ❌ Basic device coordination |
| **Flyer Management** | ✅ Advanced flyer creation and management | ❌ Basic flyer usage |
| **Timing Coordination** | ✅ Sophisticated timing validation | ❌ Basic timing setup |
| **Error Recovery** | ✅ Comprehensive error handling | ❌ Basic error handling |
| **Calibration Support** | ✅ energy_calibration_plan included | ❌ No calibration support |

**BITS XAS Enhancements:**
- Advanced flyer coordinator for multi-device synchronization
- Energy calibration plan for measurement validation
- Enhanced timing precision with validation
- Comprehensive error recovery mechanisms

### Simulation Plans

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Implementation** | ✅ Comprehensive sim_plans.py | ❌ Not present |
| **Plan Types** | ✅ sim_count_plan, sim_print_plan, sim_rel_scan_plan | ❌ None |
| **Device Integration** | ✅ oregistry integration with fallbacks | ❌ N/A |
| **Testing Support** | ✅ Designed for development/testing | ❌ N/A |

## Framework Integration

### BITS Framework Support

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Oregon Registry** | ✅ Full integration | ✅ Basic usage |
| **Configuration Management** | ✅ YAML-based configs/ directory | ❌ Hardcoded values |
| **Callbacks** | ✅ nexus_data_file_writer, spec_data_file_writer | ❌ Not present |
| **Utilities** | ✅ providers.py, system_tools.py, warmup_hdf5.py | ❌ Basic utilities |
| **Suspenders** | ✅ Dedicated suspenders/ directory | ❌ Not present |
| **Documentation** | ✅ Comprehensive READMEs and docs | ❌ Minimal documentation |

### Package Structure

| Feature | BITS Deployment | Profile Collection |
|---------|----------------|-------------------|
| **Structure** | ✅ Modern Python package with src/ layout | ❌ Traditional startup script approach |
| **Dependencies** | ✅ pyproject.toml with managed dependencies | ✅ pixi.toml for environment |
| **Testing** | ✅ Structured for testing with mock support | ❌ Manual testing approach |
| **Modularity** | ✅ Clear separation of concerns | ❌ Monolithic startup files |

## Key Advantages by Deployment

### BITS Deployment Advantages

1. **Enhanced Device Classes**: All devices have TST-specific enhancements with labels, structured initialization, and comprehensive error handling

2. **Advanced Flyer Ecosystem**: Sophisticated flyer coordination with state management, timing validation, and multi-device synchronization

3. **Comprehensive Plans**: Enhanced plans with structured metadata, comprehensive error handling, and detailed logging

4. **Configuration Management**: YAML-based configuration system instead of hardcoded values

5. **Development Support**: Simulation plans, comprehensive testing support, and mock mode integration

6. **Documentation**: Extensive documentation with clear docstrings and usage examples

7. **Framework Integration**: Full BITS framework integration with callbacks, utilities, and suspenders

8. **Package Structure**: Modern Python package structure with proper dependency management

### Profile Collection Advantages

1. **Simplicity**: Direct, straightforward implementation that's easy to understand

2. **Performance**: Minimal overhead with direct device instantiation

3. **Traditional Approach**: Familiar startup script pattern used across many beamlines

4. **Immediate Functionality**: Direct access to all devices without abstraction layers

## Recommendations

### For New Development
- **Use BITS Deployment**: The enhanced features, better error handling, and structured approach provide significant advantages for long-term maintainability

### For Existing Systems
- **Migration Path**: Gradually adopt BITS patterns while maintaining compatibility with existing workflows

### For Specific Use Cases
- **Research/Development**: BITS deployment provides superior simulation and testing capabilities
- **Production**: Both can work, but BITS provides better error recovery and monitoring
- **Simple Scans**: Profile collection may be sufficient for basic operations

## Migration Path

For teams looking to migrate from profile collection to BITS deployment, see the comprehensive **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** which provides:

- **Step-by-step migration process** with detailed examples
- **Device and plan migration patterns** showing before/after code
- **Configuration system setup** for YAML-based management
- **Validation and testing procedures** to ensure successful migration
- **Troubleshooting guide** for common migration issues

## Conclusion

The BITS deployment represents a significant evolution in beamline control software, providing enhanced functionality, better error handling, and improved maintainability compared to the traditional profile collection approach. While the profile collection offers simplicity and direct access, the BITS deployment provides a more robust, scalable, and feature-rich platform for advanced beamline operations.

Both deployments implement the same core functionality but with different levels of sophistication and framework integration. The migration guide provides a clear path for teams to transition from the traditional approach to the enhanced BITS framework while preserving existing functionality and adding new capabilities.