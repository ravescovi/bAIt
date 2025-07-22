# bAIt (Bluesky AI Tools)

An AI-powered analysis and intelligence system for Bluesky-based data acquisition instruments at the Advanced Photon Source (APS) at Argonne National Laboratory.

**Key Scope**: bAIt is a **separate analysis package** that analyzes existing deployments and answers questions about them. It does **NOT control** any hardware or systems.

## 🏗️ Repository Structure (Submodules)

This repository uses **git submodules** to manage multiple related repositories. Each component is maintained in its own repository with proper access controls.

### 📁 Core Framework (`bait_base/`)
- **analyzers/** - Analysis engines for different components
- **agents/** - AI agents for specialized analysis tasks  
- **MCP/** - Model Context Protocol servers for Claude Code integration
- **knowledge/** - RAG knowledge system for intelligent querying
- **visualization/** - Tools for generating system diagrams and visualizations
- **docs/** - bAIt framework documentation

### 📦 Foundation Packages (`bits_base/` - Submodules)
- **[BITS](https://github.com/BCDA-APS/BITS)** - Main apsbits package with instrument templates and framework
- **[apstools](https://github.com/BCDA-APS/apstools)** - Library of Python tools for Bluesky Framework at APS
- **[guarneri](https://github.com/BCDA-APS/guarneri)** - Instrument configuration management
- **[BITS-Starter](https://github.com/BCDA-APS/BITS-Starter)** - Template for creating new instruments
- **[ophyd-registry](https://github.com/BCDA-APS/ophyd-registry)** - Device registry and management

### 🔬 Beamline Deployments (`bits_deployments/` - Submodules)
- **[12id-bits](https://github.com/BCDA-APS/12id-bits)** - 12-ID beamline deployment
- **[16bm-bits](https://github.com/BCDA-APS/16bm-bits)** - 16-BM beamline deployment
- **[28id-bits](https://github.com/BCDA-APS/28id-bits)** - 28-ID beamline deployment
- **[8id-bits](https://github.com/BCDA-APS/8id-bits)** - 8-ID beamline deployment
- **[9id_bits](https://github.com/BCDA-APS/9id_bits)** - 9-ID beamline deployment
- **[bluesky-mic](https://github.com/BCDA-APS/bluesky-mic)** - Microscopy beamline deployment
- **[haven](https://github.com/spc-group/haven)** - Haven beamline framework
- **[polar-bits](https://github.com/BCDA-APS/polar-bits)** - Polar beamline deployment
- **[tomo-bits](https://github.com/BCDA-APS/tomo-bits)** - Tomography beamline deployment
- **[usaxs-bits](https://github.com/BCDA-APS/usaxs-bits)** - USAXS beamline deployment

### 📚 Resources (`resources/` - Submodules)
- **[bluesky_training](https://github.com/BCDA-APS/bluesky_training)** - Training materials and examples
- **[eureka_beamline](https://github.com/ravescovi/eureka_beamline)** - Eureka beamline utilities

### 🐳 Containers (`containers/` - Submodules)
- **[epics-podman](https://git.aps.anl.gov/xsd-det/epics-podman)** - EPICS container configurations

### 🗂️ Deployment Configs (`bait_deployments/`)
- Analysis configurations for each beamline
- Points to IOCs, BITS deployments, MEDM screens
- Contains metadata and analysis cache

## 🚀 Quick Start

### Option 1: Full Installation (Requires access to all repositories)
```bash
git clone --recursive https://github.com/your-org/bAIt.git
cd bAIt
python scripts/check-submodule-access.py
pip install -e ./bait_base/
```

### Option 2: Selective Installation (Recommended for most users)
```bash
git clone https://github.com/your-org/bAIt.git
cd bAIt
python scripts/init-accessible-submodules.py
pip install -e ./bait_base/
```

### Option 3: Core Framework Only
```bash
git clone https://github.com/your-org/bAIt.git
cd bAIt
pip install -e ./bait_base/
# Use bAIt with external repository references only
```

## 📚 Documentation

- **[Submodule Management Guide](docs/submodules/SUBMODULES.md)** - Comprehensive guide to working with submodules
- **[Access Requirements](docs/submodules/ACCESS-REQUIREMENTS.md)** - Repository access requirements and troubleshooting
- **[Migration Notes](docs/submodules/MIGRATION-REMOTES.md)** - Information about the submodule migration

## 🔧 Submodule Management

### Check Repository Access
```bash
# Check access to all submodules
python scripts/check-submodule-access.py

# Get detailed troubleshooting help
python scripts/check-submodule-access.py --fix-permissions

# Check only specific category
python scripts/check-submodule-access.py --category bits_base
```

### Initialize Accessible Submodules
```bash
# Initialize only repositories you have access to
python scripts/init-accessible-submodules.py

# Dry run to see what would be initialized
python scripts/init-accessible-submodules.py --dry-run

# Force initialization (ignore access checks)
python scripts/init-accessible-submodules.py --force
```

### Diagnose Issues
```bash
# Run comprehensive diagnostics
python scripts/diagnose-submodule-issues.py

# Diagnose specific submodule
python scripts/diagnose-submodule-issues.py --submodule bits_base/BITS

# Get detailed fix suggestions
python scripts/diagnose-submodule-issues.py --fix-suggestions
```

### Manual Submodule Operations
```bash
# Update all initialized submodules
git submodule update --recursive

# Initialize specific submodule
git submodule update --init bits_base/BITS

# Update to latest commits
git submodule update --remote

# Pull changes in submodule and commit reference
cd bits_base/BITS
git pull origin main
cd ../..
git add bits_base/BITS
git commit -m "Update BITS submodule"
```

## 🔐 Access Requirements

### Public Repositories (Always Accessible)
- Most BCDA-APS repositories on GitHub
- No special access required

### Organization Repositories (Require Membership)
- **BCDA-APS organization**: Request membership from APS team
- **spc-group organization**: Request access for Haven repository

### Private/Restricted Repositories (Require Special Access)
- **APS GitLab** (`git.aps.anl.gov`): APS network access + repository permissions
- Contact repository owners for access

## 🎯 Development Commands

### bAIt Analysis
```bash
# Analyze deployment
bait-analyze [deployment-name]

# Interactive query
bait-query [deployment-name]

# Generate visualization
bait-visualize [deployment-name] --type network
```

### Working with Submodules (Claude Code)
```bash
# Work in specific submodule
cd bits_base/BITS
# Make changes, commit normally
git add .
git commit -m "Add new feature"
git push origin main

# Update main repository with new submodule commit
cd ../..
git add bits_base/BITS
git commit -m "Update BITS submodule to include new feature"
```

## 🚨 Troubleshooting

### Common Issues

**"fatal: repository not found"**
- Repository may be private - request access
- Check repository URL spelling
- Verify GitHub organization membership

**"Permission denied (publickey)"**
- SSH key not configured or not added to GitHub
- Run: `ssh -T git@github.com` to test
- Generate key: `ssh-keygen -t ed25519 -C "your_email@example.com"`

**"Submodule directory is empty"**
- Run: `git submodule update --init [path]`
- Or use: `python scripts/init-accessible-submodules.py`

**"APS GitLab repositories not accessible"**
- Must be on APS network or VPN
- Contact APS IT for repository access
- Some repositories require special permissions

### Getting Help
1. **Run diagnostics**: `python scripts/diagnose-submodule-issues.py --fix-suggestions`
2. **Check access**: `python scripts/check-submodule-access.py --fix-permissions`
3. **Contact repository owners** for access to specific repositories
4. **Join GitHub organizations** (BCDA-APS, spc-group) as needed

## 🤝 Contributing

### To Main bAIt Framework
1. Fork this repository
2. Make changes to `bait_base/` core framework
3. Test with available submodules
4. Submit pull request

### To Individual Components
1. Navigate to specific submodule: `cd bits_base/BITS`
2. Make changes and commit in submodule
3. Push to submodule repository
4. Update main repository submodule reference if needed

### Adding New Beamlines
```bash
# Add new beamline as submodule
git submodule add https://github.com/org/new-beamline.git bits_deployments/new-beamline

# Commit the submodule addition
git add .gitmodules bits_deployments/new-beamline
git commit -m "Add new beamline deployment"
```

## 📄 License

See individual submodule repositories for their respective licenses.

## 📞 Support

- **bAIt Framework**: Contact bAIt development team
- **BITS/apstools**: Contact BCDA-APS team
- **Individual Beamlines**: Contact respective beamline teams
- **Access Issues**: Contact repository owners or APS IT