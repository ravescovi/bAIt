# Migration Quick Reference

## Essential Commands

```bash
# 1. Create package structure
mkdir -p bits_deployments/tst-nsls-bits/src/tst_instrument/{devices,plans,configs,callbacks,utils,suspenders}

# 2. Install in development mode
cd bits_deployments/tst-nsls-bits
pip install -e .

# 3. Test migration
python -c "from tst_instrument.devices.tst_motor import TSTMotor; print('✅ Motor migration successful')"
```

## Key File Mappings

| Profile Collection | BITS Deployment | Purpose |
|-------------------|-----------------|---------|
| `startup/05-motors.py` | `src/tst_instrument/devices/tst_motor.py` | Motor wrapper class |
| `startup/15-manta.py` | `src/tst_instrument/devices/tst_detector.py` | Detector wrapper class |
| `startup/10-panda.py` | `src/tst_instrument/devices/tst_panda.py` | PandA wrapper class |
| `startup/90-plans.py` | `src/tst_instrument/plans/tomography_plans.py` + `xas_plans.py` | Enhanced plans |
| Hardcoded values | `src/tst_instrument/configs/devices.yml` | YAML configuration |

## Validation Commands

```python
# Test devices
from tst_instrument.devices.tst_motor import TSTMotor
motor = TSTMotor("TEST:PREFIX", name="test")
assert motor.name == "test"

# Test plans
from tst_instrument.plans.tomography_plans import tomo_demo_async
import inspect
sig = inspect.signature(tomo_demo_async)
assert 'detectors' in sig.parameters
```

## Common Issues & Solutions

1. **Import Error**: Ensure `pip install -e .` was run
2. **Device Creation**: Check PV prefixes in configs/devices.yml
3. **Plan Execution**: Verify oregistry registration in startup.py

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for complete details.