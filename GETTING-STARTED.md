# Getting Started with bAIt

Quick verification guide for new users to test the repository setup.

## 🚀 Quick Setup Test

### 1. Clone the Repository
```bash
git clone https://github.com/ravescovi/bAIt.git
cd bAIt
```

### 2. Verify Repository Structure
```bash
# Check main directory structure
ls -la
# Should show: bait_base/, bits_base/, bits_deployments/, resources/, containers/, scripts/

# Check submodule configuration
cat .gitmodules | grep "path =" | wc -l
# Should show: 18 (number of submodules)
```

### 3. Test Access to Repositories
```bash
# Check which repositories you can access
python scripts/check-submodule-access.py

# Expected output: Report showing ✅ for accessible and ❌ for inaccessible repos
```

### 4. Initialize Accessible Submodules
```bash
# See what would be initialized (dry run)
python scripts/init-accessible-submodules.py --dry-run

# Initialize repositories you have access to
python scripts/init-accessible-submodules.py
```

### 5. Install bAIt Core Framework
```bash
# Install the core bAIt analysis framework
pip install -e ./bait_base/

# Verify installation
python -c "import bait_base; print('bAIt core framework installed successfully!')"
```

### 6. Test bAIt Functionality
```bash
# Test basic CLI functionality
python -m bait_base.cli --help

# Check deployment configurations
ls bait_deployments/*/config.json
```

## 🧪 Verification Commands

### Check Repository Health
```bash
# Run full diagnostic
python scripts/diagnose-submodule-issues.py

# Check specific category
python scripts/check-submodule-access.py --category bits_base
```

### Verify Submodule Status
```bash
# Show all submodule status
git submodule status

# Count initialized submodules
git submodule status | grep -v "^-" | wc -l
```

### Test Development Workflow
```bash
# Navigate to a submodule
cd bits_base/BITS
git status
git log --oneline -5

# Return to main repository
cd ../..
git status
```

## 📊 Expected Results

**Successful Setup Should Show:**
- ✅ 18 submodules configured in `.gitmodules`
- ✅ Access validation script runs without errors
- ✅ At least some submodules initialize successfully
- ✅ bAIt core framework installs via pip
- ✅ No critical errors in diagnostic script

**Partial Success (Normal for Some Users):**
- ✅ Most GitHub repositories accessible
- ❌ APS GitLab repositories may be inaccessible (requires APS network)
- ✅ Core functionality works with available submodules

## 🚨 Common Issues & Solutions

### No Submodules Initialize
```bash
# Check git and network connectivity
git --version
python scripts/diagnose-submodule-issues.py --fix-suggestions
```

### APS GitLab Access Issues
```bash
# Expected for users outside APS network
# Container functionality may be limited
# Core analysis still works with GitHub repositories
```

### Permission Denied Errors
```bash
# Check GitHub authentication
ssh -T git@github.com
# Or configure HTTPS credentials
git config --global credential.helper store
```

## 📞 Getting Help

1. **Run Diagnostics First**: `python scripts/diagnose-submodule-issues.py --verbose`
2. **Check Documentation**: See `docs/submodules/` for detailed guides
3. **Repository Issues**: Contact repository owners for access
4. **bAIt Framework**: Open issue in this repository

## ✅ Success Indicators

You have a working bAIt setup when:
- [ ] Repository clones successfully
- [ ] Access checker runs and shows some ✅ results
- [ ] At least `bits_base/` submodules initialize
- [ ] `pip install -e ./bait_base/` completes successfully
- [ ] Core CLI shows help output: `python -m bait_base.cli --help`

Even with partial access, you can use bAIt's core analysis framework effectively!