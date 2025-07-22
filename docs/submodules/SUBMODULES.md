# bAIt Submodule Management Guide

This document provides detailed information about managing git submodules in the bAIt repository.

## Overview

bAIt uses git submodules to integrate 18 separate repositories into a unified analysis framework. This approach provides:

- **Proper Attribution**: Each repository maintains its own history and ownership
- **Access Control**: Repository-specific permissions and access management
- **Scalable Development**: Teams can work independently on their components
- **Version Management**: Precise control over which version of each component is used

## Submodule Architecture

```
bAIt/
├── .gitmodules                    # Submodule configuration
├── bait_base/                     # Core bAIt framework (not submodule)
├── bait_deployments/              # Deployment configs (not submodule)
├── bits_base/                     # Foundation packages (5 submodules)
│   ├── BITS/                      # → github.com/BCDA-APS/BITS
│   ├── apstools/                  # → github.com/BCDA-APS/apstools
│   ├── guarneri/                  # → github.com/BCDA-APS/guarneri
│   ├── BITS-Starter/              # → github.com/BCDA-APS/BITS-Starter
│   └── ophyd-registry/            # → github.com/BCDA-APS/ophyd-registry
├── bits_deployments/              # Beamline deployments (10 submodules)
│   ├── 12id-bits/                 # → github.com/BCDA-APS/12id-bits
│   ├── 16bm-bits/                 # → github.com/BCDA-APS/16bm-bits
│   ├── 28id-bits/                 # → github.com/BCDA-APS/28id-bits
│   ├── 8id-bits/                  # → github.com/BCDA-APS/8id-bits
│   ├── 9id_bits/                  # → github.com/BCDA-APS/9id_bits
│   ├── bluesky-mic/               # → github.com/BCDA-APS/bluesky-mic
│   ├── haven/                     # → github.com/spc-group/haven
│   ├── polar-bits/                # → github.com/BCDA-APS/polar-bits
│   ├── tomo-bits/                 # → github.com/BCDA-APS/tomo-bits
│   └── usaxs-bits/                # → github.com/BCDA-APS/usaxs-bits
├── resources/                     # Training and utilities (2 submodules)
│   ├── bluesky_training/          # → github.com/BCDA-APS/bluesky_training
│   └── eureka_beamline/           # → github.com/ravescovi/eureka_beamline
├── containers/                    # Container configs (1 submodule)
│   └── epics-podman/              # → git.aps.anl.gov/xsd-det/epics-podman
└── scripts/                       # Submodule management tools
    ├── check-submodule-access.py
    ├── init-accessible-submodules.py
    └── diagnose-submodule-issues.py
```

## Understanding Submodule States

Git tracks submodules by their **commit hash**, not by branch. Each submodule can be in different states:

### Status Characters (from `git submodule status`)
- **` `** (space) - Submodule is up to date
- **`-`** - Submodule is not initialized
- **`+`** - Submodule has uncommitted changes
- **`U`** - Submodule has merge conflicts

### Directory States
- **Missing**: Directory doesn't exist (not initialized)
- **Empty**: Directory exists but is empty (initialization failed)
- **Outdated**: Directory contains older commit than referenced
- **Modified**: Directory contains uncommitted changes
- **Current**: Directory matches referenced commit exactly

## Installation Workflows

### 1. Fresh Clone with All Submodules
```bash
# Clone with all submodules (requires access to all repos)
git clone --recursive https://github.com/your-org/bAIt.git

# Alternative: clone then initialize
git clone https://github.com/your-org/bAIt.git
cd bAIt
git submodule update --init --recursive
```

### 2. Selective Installation (Recommended)
```bash
# Clone main repository only
git clone https://github.com/your-org/bAIt.git
cd bAIt

# Check which repositories you can access
python scripts/check-submodule-access.py

# Initialize only accessible repositories
python scripts/init-accessible-submodules.py
```

### 3. Manual Selective Installation
```bash
# Initialize specific submodules
git submodule update --init bits_base/BITS
git submodule update --init bits_base/apstools
git submodule update --init bits_deployments/8id-bits
```

## Development Workflows

### Working in a Submodule
```bash
# Navigate to submodule
cd bits_base/BITS

# Check current state
git status
git branch

# Make changes
# ... edit files ...

# Commit changes in submodule
git add .
git commit -m "Add new feature to BITS"
git push origin main

# Return to main repository
cd ../..

# The main repo now shows the submodule as modified
git status
# Changes not staged for commit:
#   modified: bits_base/BITS (new commits)

# Update main repository to reference new commit
git add bits_base/BITS
git commit -m "Update BITS submodule to include new feature"
git push origin main
```

### Updating Submodules

#### Update to Latest Remote Commits
```bash
# Update all submodules to latest commits on tracked branches
git submodule update --remote

# Update specific submodule
git submodule update --remote bits_base/BITS

# Commit the updates
git add .
git commit -m "Update all submodules to latest versions"
```

#### Update to Specific Commit
```bash
# Navigate to submodule
cd bits_base/BITS

# Check out specific commit or tag
git checkout v2.1.0
# or
git checkout abc1234

# Return and commit the reference
cd ../..
git add bits_base/BITS
git commit -m "Pin BITS to version 2.1.0"
```

### Adding New Submodules
```bash
# Add new repository as submodule
git submodule add https://github.com/org/new-repo.git path/to/new-repo

# This creates/updates .gitmodules and adds the submodule directory
# Commit the changes
git add .gitmodules path/to/new-repo
git commit -m "Add new-repo as submodule"
```

### Removing Submodules
```bash
# Remove submodule (complex process)
git submodule deinit path/to/submodule
git rm path/to/submodule
git commit -m "Remove submodule"

# Clean up .git/modules (optional)
rm -rf .git/modules/path/to/submodule
```

## Access Management

### Repository Categories by Access Level

#### Public Repositories (No special access required)
- Most `github.com/BCDA-APS/*` repositories
- `github.com/spc-group/haven`

#### Organization Repositories (Require membership)
- **BCDA-APS**: Contact APS team for organization membership
- **spc-group**: Contact group administrators

#### Restricted Repositories (Special permissions)
- **APS GitLab** (`git.aps.anl.gov`): 
  - APS network access required
  - Repository-specific permissions
  - Contact APS IT for access

### Authentication Methods

#### SSH (Recommended for Development)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Test GitHub connection
ssh -T git@github.com

# Add public key to GitHub: https://github.com/settings/ssh
```

#### HTTPS (Easier for Casual Use)
```bash
# Configure credential helper
git config --global credential.helper store

# Or use GitHub CLI
gh auth login
```

## Troubleshooting

### Common Issues and Solutions

#### Empty Submodule Directories
```bash
# Problem: Directory exists but is empty
ls bits_base/BITS/  # empty

# Solution: Initialize the submodule
git submodule update --init bits_base/BITS
```

#### Submodule Access Denied
```bash
# Problem: Permission denied during clone/fetch
# Solution 1: Check repository access
python scripts/check-submodule-access.py --fix-permissions

# Solution 2: Use different authentication
git config --global url."https://github.com/".insteadOf git@github.com:
```

#### Submodule Commit Conflicts
```bash
# Problem: Submodule shows as modified but no local changes
cd bits_base/BITS
git status  # clean working tree

# Solution: Reset to referenced commit
git reset --hard HEAD
cd ../..
git submodule update bits_base/BITS
```

#### Detached HEAD in Submodule
```bash
# Problem: Submodule is in detached HEAD state
cd bits_base/BITS
git branch  # * (HEAD detached at abc1234)

# Solution: Check out a branch
git checkout main
# or create new branch
git checkout -b feature-branch
```

### Advanced Troubleshooting

#### Complete Submodule Reset
```bash
# Nuclear option: completely reset all submodules
git submodule deinit --all
git submodule update --init --recursive
```

#### Fix Corrupted Submodule
```bash
# Remove and re-add submodule
git submodule deinit bits_base/BITS
git rm bits_base/BITS
rm -rf .git/modules/bits_base/BITS
git submodule add https://github.com/BCDA-APS/BITS.git bits_base/BITS
```

## Best Practices

### For Repository Maintainers

1. **Pin to Stable Versions**: Use tagged releases rather than latest commits
2. **Test Before Updating**: Verify compatibility before updating submodule references
3. **Document Dependencies**: Clearly document which submodules are required vs optional
4. **Provide Fallbacks**: Design code to gracefully handle missing submodules

### For Contributors

1. **Check Before Pushing**: Always check submodule state before committing
2. **Update Incrementally**: Update one submodule at a time for easier troubleshooting
3. **Test Across Platforms**: Verify submodule behavior on different systems
4. **Communicate Changes**: Notify team when updating shared submodules

### For Users

1. **Start Selective**: Use `init-accessible-submodules.py` rather than `--recursive`
2. **Check Access First**: Run access checks before attempting full initialization
3. **Keep Documentation**: Maintain notes about which repositories you have access to
4. **Regular Updates**: Periodically update accessible submodules

## Scripts Reference

### check-submodule-access.py
```bash
# Basic access check
python scripts/check-submodule-access.py

# Check specific category
python scripts/check-submodule-access.py --category bits_base

# Get detailed troubleshooting
python scripts/check-submodule-access.py --fix-permissions

# JSON output for automation
python scripts/check-submodule-access.py --json
```

### init-accessible-submodules.py
```bash
# Initialize accessible submodules
python scripts/init-accessible-submodules.py

# Dry run (see what would be done)
python scripts/init-accessible-submodules.py --dry-run

# Force initialization (ignore access checks)
python scripts/init-accessible-submodules.py --force

# Initialize specific category
python scripts/init-accessible-submodules.py --category bits_deployments
```

### diagnose-submodule-issues.py
```bash
# Full diagnostic report
python scripts/diagnose-submodule-issues.py

# Diagnose specific submodule
python scripts/diagnose-submodule-issues.py --submodule bits_base/BITS

# Verbose output with detailed analysis
python scripts/diagnose-submodule-issues.py --verbose

# Include fix suggestions
python scripts/diagnose-submodule-issues.py --fix-suggestions
```

## Migration Notes

This repository was migrated from a nested git repository structure to submodules. The migration:

1. **Preserved all repository histories** in their original locations
2. **Maintained access controls** - no changes to repository permissions
3. **Added management scripts** for easier submodule handling
4. **Improved scalability** for adding new beamline deployments

### For Existing Users

If you have an existing clone of the pre-migration repository:

1. **Backup your work**: Copy any uncommitted changes
2. **Fresh clone required**: Cannot migrate existing working copies
3. **New workflow**: Use submodule management scripts
4. **Access validation**: Check repository access with new scripts

The backup repository is available at `/home/ravescovi/workspace/bAIt-backup-*` for reference.