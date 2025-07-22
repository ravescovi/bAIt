# bAIt Submodule Management Scripts

The bAIt repository includes three Python scripts to help manage the complex submodule structure. These scripts are located in the `scripts/` directory at the repository root.

## Overview

- **`check-submodule-access.py`** - Validates access to all configured submodules
- **`init-accessible-submodules.py`** - Initializes only accessible submodules  
- **`diagnose-submodule-issues.py`** - Diagnoses and troubleshoots submodule problems

## check-submodule-access.py

Validates user access to repository submodules without actually cloning them.

### Usage
```bash
# Basic access check for all submodules
python scripts/check-submodule-access.py

# Check specific category only
python scripts/check-submodule-access.py --category bits_base

# Get detailed troubleshooting suggestions
python scripts/check-submodule-access.py --fix-permissions

# Output results in JSON format
python scripts/check-submodule-access.py --json
```

### Output Example
```
bAIt Submodule Access Report
==================================================
Total submodules checked: 18
Accessible: 17
Inaccessible: 1

BITS_BASE:
  ✅ bits_base/BITS
  ✅ bits_base/apstools
  ✅ bits_base/guarneri
  ✅ bits_base/BITS-Starter
  ✅ bits_base/ophyd-registry

CONTAINERS:
  ❌ containers/epics-podman
     Error: Connection timeout
```

### Features
- **Fast Operation**: Uses `git ls-remote` for lightweight access testing
- **Categorized Results**: Groups results by repository category
- **Detailed Diagnostics**: Provides specific error messages and solutions
- **JSON Output**: Machine-readable output for automation
- **Troubleshooting Mode**: Suggests specific solutions for access issues

## init-accessible-submodules.py

Initializes only the submodules that the user has access to, enabling partial repository setups.

### Usage
```bash
# Initialize all accessible submodules
python scripts/init-accessible-submodules.py

# See what would be initialized without doing it
python scripts/init-accessible-submodules.py --dry-run

# Initialize only specific category
python scripts/init-accessible-submodules.py --category bits_deployments

# Force initialization (ignore access checks)
python scripts/init-accessible-submodules.py --force
```

### Workflow
1. **Access Check**: Validates access to each submodule repository
2. **Status Check**: Identifies already initialized submodules
3. **User Confirmation**: Shows what will be initialized and asks for confirmation
4. **Initialization**: Runs `git submodule update --init` for accessible repositories
5. **Results**: Reports success/failure for each initialization

### Output Example
```
bAIt Submodule Initialization
==================================================
Already initialized: 5
Will initialize: 10
Will skip (no access): 3

WILL INITIALIZE:
  🔄 bits_deployments/8id-bits
  🔄 bits_deployments/9id_bits
  🔄 resources/bluesky_training

SKIPPED (NO ACCESS):
  ❌ containers/epics-podman
     Connection timeout

Initialize 10 submodules? [y/N]: y

INITIALIZING SUBMODULES:
  Initializing bits_deployments/8id-bits... ✅
  Initializing bits_deployments/9id_bits... ✅
  Initializing resources/bluesky_training... ✅

Successfully initialized: 10/10
```

### Features
- **Selective Initialization**: Only initializes accessible repositories
- **Dry Run Mode**: Preview what would be done without making changes
- **Category Filtering**: Initialize only specific categories of repositories
- **Progress Reporting**: Shows initialization progress with status indicators
- **Graceful Handling**: Continues on access failures, doesn't abort entire process

## diagnose-submodule-issues.py

Comprehensive diagnostic tool for troubleshooting submodule problems.

### Usage
```bash
# Run full diagnostic report
python scripts/diagnose-submodule-issues.py

# Diagnose specific submodule only
python scripts/diagnose-submodule-issues.py --submodule bits_base/BITS

# Show verbose diagnostic information
python scripts/diagnose-submodule-issues.py --verbose

# Include detailed fix suggestions
python scripts/diagnose-submodule-issues.py --fix-suggestions
```

### Diagnostic Categories

#### System Checks
- Git installation and version
- Repository validation (is this a git repo?)
- Submodule configuration validation

#### Submodule Status Analysis
- Initialization status (initialized vs not initialized)
- Directory state (exists, empty, has content)
- Git status within submodule
- Commit hash alignment

#### Access Diagnostics
- Repository URL accessibility
- Authentication method detection (SSH vs HTTPS)
- SSH key configuration and testing
- Credential helper configuration
- Network connectivity for special repositories

#### Issue-Specific Analysis
- Empty directory diagnosis
- Permission errors
- Network timeouts
- Authentication failures
- Commit mismatches

### Output Example
```
bAIt Submodule Diagnostic Tool
==================================================

SYSTEM CHECKS:
✅ Git is installed
✅ Valid git repository

SUBMODULE DIAGNOSTICS:

Checking: bits_base/BITS
URL: https://github.com/BCDA-APS/BITS.git
  ✅ Appears to be working

Checking: containers/epics-podman  
URL: https://git.aps.anl.gov/xsd-det/epics-podman.git
  ❌ Directory does not exist
     Using HTTPS authentication
     Repository access failed: Connection timeout
  💡 SUGGESTION: APS GitLab access required
    • Must be on APS network or VPN
    • Contact APS IT for repository access

SUMMARY: Found 1 issues
```

### Features
- **Comprehensive Analysis**: Checks system, network, authentication, and repository status
- **Targeted Diagnosis**: Can focus on specific problematic submodules
- **Detailed Explanations**: Provides context for each issue found
- **Specific Solutions**: Offers actionable fix suggestions
- **Progressive Disclosure**: Basic output by default, verbose mode for detailed analysis

## Integration with bAIt Workflow

### Recommended Usage Pattern

#### New Installation
```bash
# 1. Clone repository
git clone https://github.com/your-org/bAIt.git
cd bAIt

# 2. Check what you can access
python scripts/check-submodule-access.py

# 3. Initialize accessible repositories
python scripts/init-accessible-submodules.py

# 4. Install bAIt framework
pip install -e ./bait_base/
```

#### Troubleshooting Workflow
```bash
# 1. Diagnose issues
python scripts/diagnose-submodule-issues.py --fix-suggestions

# 2. Fix identified problems (following suggestions)

# 3. Re-check access
python scripts/check-submodule-access.py

# 4. Initialize newly accessible repositories
python scripts/init-accessible-submodules.py
```

### CI/CD Integration

The scripts can be integrated into continuous integration workflows:

```yaml
# Example GitHub Actions workflow
- name: Check submodule access
  run: python scripts/check-submodule-access.py --json > access-report.json
  
- name: Initialize accessible submodules
  run: python scripts/init-accessible-submodules.py --force
  
- name: Validate submodule health
  run: python scripts/diagnose-submodule-issues.py
```

## Error Handling and Exit Codes

### Exit Codes
- **0**: Success, all operations completed successfully
- **1**: Issues found or operations failed
- **Other**: System errors (git not found, not a repository, etc.)

### Error Categories
- **Network Errors**: Connection timeouts, DNS resolution failures
- **Authentication Errors**: Permission denied, invalid credentials
- **Repository Errors**: Repository not found, invalid URLs
- **System Errors**: Git not installed, not a git repository

## Advanced Usage

### Automation and Scripting

The scripts are designed to be automation-friendly:

```bash
# Check if all repositories are accessible before proceeding
if python scripts/check-submodule-access.py --json | jq '.[] | select(.accessible == false)' | grep -q .; then
    echo "Some repositories are not accessible"
    exit 1
fi

# Initialize only specific repositories
python scripts/init-accessible-submodules.py --category bits_base --force
```

### Custom Configuration

Scripts read from `.gitmodules` automatically but can be extended for custom configurations:

```python
# Example: Custom repository filtering
from check_submodule_access import get_submodule_urls

# Filter to only BCDA-APS repositories
submodules = get_submodule_urls()
bcda_repos = {
    path: url for path, url in submodules.items() 
    if 'BCDA-APS' in url
}
```

## Dependencies

### Required
- Python 3.6+ 
- Git 2.0+
- Network connectivity for repository access testing

### Optional
- SSH client (for SSH-based repositories)
- Git credential helpers (for HTTPS authentication)
- VPN client (for APS GitLab access)

## Limitations

- **Access Testing**: Uses `git ls-remote` which may not catch all permission issues
- **Network Dependencies**: Requires network access for remote repository testing
- **Authentication**: Cannot automatically fix authentication setup
- **Repository State**: Cannot fix corrupted repository states automatically

## See Also

- **[Submodule Management Guide](../docs/submodules/SUBMODULES.md)** - Comprehensive submodule workflows
- **[Access Requirements](../docs/submodules/ACCESS-REQUIREMENTS.md)** - Repository access details
- **Git Submodule Documentation**: `git help submodule`