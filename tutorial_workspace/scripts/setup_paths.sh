#!/bin/bash
# Setup script paths for tutorial execution
# This script configures environment paths for the bAIt tutorial system

echo "Setting up tutorial environment paths..."

# Define base paths
export BITS_DEMO_PATH="/home/ravescovi/workspace/bAIt/bits_base/BITS/src/bits_demo"
export TUTORIAL_SCRIPTS="$BITS_DEMO_PATH/scripts"
export TUTORIAL_PATH="$BITS_DEMO_PATH/tutorial"
export CONDA_PATH="/home/ravescovi/miniconda3"
export TUTORIAL_WORKSPACE="/home/ravescovi/workspace/bAIt/tutorial_workspace"

# Add scripts to PATH
export PATH="$TUTORIAL_SCRIPTS:$TUTORIAL_WORKSPACE/scripts:$PATH"

# Conda initialization (BITS uses bits_env)
source "$CONDA_PATH/etc/profile.d/conda.sh"
if conda info --envs | grep -q bits_env; then
    echo "  ✅ BITS environment (bits_env) available"
else
    echo "  ⚠️  Consider creating BITS environment: conda create -y -n bits_env python=3.11 pyepics"
fi

echo "Environment configured:"
echo "  BITS_DEMO_PATH: $BITS_DEMO_PATH"
echo "  TUTORIAL_SCRIPTS: $TUTORIAL_SCRIPTS"
echo "  CONDA_PATH: $CONDA_PATH"
echo "  PATH includes tutorial scripts"

# Verify key components
echo ""
echo "Verification:"
which conda && echo "✅ Conda available"
which podman && echo "✅ Podman available"
[ -f "$TUTORIAL_SCRIPTS/explore_iocs.py" ] && echo "✅ explore_iocs.py found"
[ -f "$TUTORIAL_SCRIPTS/validate_setup.py" ] && echo "✅ validate_setup.py found"

echo "Setup complete!"