"""
Beamline startup module for my_beamline

This module initializes the beamline environment using the BITS framework,
loads devices, and sets up the data acquisition system.
"""

import logging
from pathlib import Path

# Import BITS framework components
from apsbits.startup import InstrumentStartup
from apsbits.devices import EpicsMotorDevice, ScalerDevice
from apsbits.callbacks import SpecWriterCallback
import bluesky.plans as bp
import bluesky.plan_stubs as bps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration directory
config_dir = Path(__file__).parent / "configs"

# Initialize BITS instrument startup
instrument = InstrumentStartup(
    config_path=config_dir / "iconfig.yml",
    device_config_path=config_dir / "devices.yml"
)

# Start the instrument (this creates RE, db, bec automatically)
instrument.startup()

# Access the created objects
RE = instrument.RE
db = instrument.db
bec = instrument.bec

logger.info("✅ BITS instrument environment initialized")

# Load devices from configuration
# These will be created based on devices.yml during device configuration tutorial
devices = {}

# Import devices (will be populated during device configuration step)
try:
    from .devices import *
    logger.info("✅ Devices loaded successfully")
except ImportError:
    logger.warning("⚠️  No devices found - run device configuration step")

# Import plans (will be populated during plan development step)
try:
    from .plans import *
    logger.info("✅ Custom plans loaded successfully")
except ImportError:
    logger.warning("⚠️  No custom plans found - run plan development step")

# Setup SPEC file writing
spec_writer = SpecWriterCallback(
    filename="my_beamline_data.spec",
    auto_write=True
)
RE.subscribe(spec_writer)

logger.info("🚀 my_beamline BITS startup complete!")

# Print available objects
print("Available objects (BITS-powered):")
print(f"  RE: {RE}")
print(f"  db: {db}")
print(f"  bec: {bec}")
print(f"  instrument: {instrument}")
print(f"  spec_writer: {spec_writer}")

# Print available devices (will be populated in tutorials)
if devices:
    print("Available devices:")
    for name, device in devices.items():
        print(f"  {name}: {device}")
else:
    print("No devices loaded yet - complete device configuration tutorial")