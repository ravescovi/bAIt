# bAIt Repository Access Requirements

This document details the access requirements for all submodules in the bAIt repository.

## Quick Reference

| Repository | Organization | Access Level | Requirements |
|------------|--------------|--------------|--------------|
| **bits_base/** |
| BITS | BCDA-APS | Public | None |
| apstools | BCDA-APS | Public | None |
| guarneri | BCDA-APS | Public | None |
| BITS-Starter | BCDA-APS | Public | None |
| ophyd-registry | BCDA-APS | Public | None |
| **bits_deployments/** |
| 12id-bits | BCDA-APS | Public | None |
| 16bm-bits | BCDA-APS | Public | None |
| 28id-bits | BCDA-APS | Public | None |
| 8id-bits | BCDA-APS | Public | None |
| 9id_bits | BCDA-APS | Public | None |
| bluesky-mic | BCDA-APS | Public | None |
| haven | spc-group | Public | None |
| polar-bits | BCDA-APS | Public | None |
| tomo-bits | BCDA-APS | Public | None |
| usaxs-bits | BCDA-APS | Public | None |
| **resources/** |
| bluesky_training | BCDA-APS | Public | None |
| eureka_beamline | ravescovi | Public | None |
| **containers/** |
| epics-podman | APS GitLab | Restricted | APS network + permissions |

## Access Categories

### 📗 Public Repositories (No Special Access Required)

Most repositories in bAIt are publicly accessible on GitHub. You can clone and read these repositories without any special permissions.

**Repositories:**
- All `github.com/BCDA-APS/*` repositories
- `github.com/spc-group/haven`
- `github.com/ravescovi/eureka_beamline`

**Requirements:**
- None - publicly accessible
- Can be cloned over HTTPS without authentication
- Read-only access for anonymous users

**Usage:**
```bash
# These work for anyone
git clone https://github.com/BCDA-APS/BITS.git
git clone https://github.com/spc-group/haven.git
```

### 🔒 Restricted Repositories (Special Access Required)

Some repositories require special access or network connectivity.

#### APS GitLab (`git.aps.anl.gov`)

**Repository:** `containers/epics-podman`

**Requirements:**
1. **Network Access:** Must be on APS network or connected via VPN
2. **Account:** APS GitLab account required
3. **Repository Permissions:** Explicit access to the specific repository
4. **Authentication:** SSH key or GitLab credentials configured

**How to Get Access:**
1. **APS Network Access:**
   - Contact APS IT for VPN access if off-site
   - Ensure you're on APS subnet when on-site

2. **GitLab Account:**
   - Contact APS IT to create GitLab account
   - May require APS employee/affiliate status

3. **Repository Access:**
   - Contact repository maintainers
   - May require justification for access

**Testing Access:**
```bash
# Test network connectivity
ping git.aps.anl.gov

# Test repository access
git ls-remote https://git.aps.anl.gov/xsd-det/epics-podman.git
```

## Access Scenarios

### 🏠 Home/Personal Use
**Accessible:**
- All GitHub repositories (public)
- Full bAIt analysis framework
- Most beamline deployments

**Not Accessible:**
- APS GitLab repositories (network restriction)
- Container configurations

**Recommendation:**
```bash
# Use selective initialization
python scripts/init-accessible-submodules.py
```

### 🏢 APS On-Site
**Accessible:**
- All repositories including APS GitLab
- Complete bAIt functionality
- All container configurations

**Requirements:**
- APS network connection
- GitLab account and permissions

**Recommendation:**
```bash
# Full initialization should work
git clone --recursive https://github.com/your-org/bAIt.git
```

### 🌐 Remote with VPN
**Accessible:**
- All repositories if VPN configured correctly
- Complete functionality

**Requirements:**
- APS VPN connection
- Proper DNS resolution for git.aps.anl.gov

**Troubleshooting:**
```bash
# Verify VPN connectivity
nslookup git.aps.anl.gov
ping git.aps.anl.gov

# Test repository access
git ls-remote https://git.aps.anl.gov/xsd-det/epics-podman.git
```

### 👥 Collaborator Access
**For GitHub Repositories:**
- **Public access:** No special requirements
- **Contributor access:** Fork repositories and submit pull requests
- **Organization membership:** Contact BCDA-APS or spc-group administrators

**For APS GitLab:**
- Contact repository owners directly
- May require collaboration agreement
- APS network access still required

## Authentication Setup

### GitHub (Recommended for Most Repositories)

#### Option 1: SSH (Best for Developers)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key and add to GitHub
cat ~/.ssh/id_ed25519.pub
# Go to https://github.com/settings/ssh and add the key

# Test connection
ssh -T git@github.com
```

#### Option 2: HTTPS with Personal Access Token
```bash
# Generate token at: https://github.com/settings/tokens
# Configure git to use token
git config --global credential.helper store

# On first clone, provide username and token as password
git clone https://github.com/BCDA-APS/BITS.git
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxxxxxxxxxx (your token)
```

#### Option 3: GitHub CLI (Easiest)
```bash
# Install GitHub CLI: https://cli.github.com/
gh auth login
# Follow prompts to authenticate

# All git operations will now work automatically
```

### APS GitLab

#### SSH Setup
```bash
# Use same SSH key as GitHub or generate new one
ssh-keygen -t ed25519 -C "your_email@aps.anl.gov"

# Add public key to APS GitLab
cat ~/.ssh/id_ed25519.pub
# Go to https://git.aps.anl.gov/-/profile/keys and add key

# Test connection (requires APS network)
ssh -T git@git.aps.anl.gov
```

#### HTTPS Setup
```bash
# Configure credentials for APS GitLab
git config --global credential.https://git.aps.anl.gov.username your-aps-username

# On first clone, provide APS credentials
git clone https://git.aps.anl.gov/xsd-det/epics-podman.git
```

## Troubleshooting Access Issues

### Diagnosis Tools
```bash
# Check all repository access
python scripts/check-submodule-access.py

# Get detailed troubleshooting
python scripts/check-submodule-access.py --fix-permissions

# Diagnose specific issues
python scripts/diagnose-submodule-issues.py --verbose
```

### Common Issues

#### "Repository not found" (GitHub)
**Possible Causes:**
- Repository is private and you don't have access
- Repository name/URL is incorrect
- Not authenticated properly

**Solutions:**
1. Verify repository URL and spelling
2. Check if you're logged into correct GitHub account
3. Request access from repository owner
4. For organization repos, request organization membership

#### "Permission denied (publickey)" (SSH)
**Causes:**
- SSH key not configured
- SSH key not added to GitHub/GitLab
- Wrong SSH key being used

**Solutions:**
```bash
# Check SSH agent
ssh-add -l

# Test specific key
ssh -i ~/.ssh/id_ed25519 -T git@github.com

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# Verify key is added to GitHub/GitLab account
```

#### "Connection timeout" (APS GitLab)
**Causes:**
- Not on APS network
- VPN not properly configured
- Firewall blocking connection

**Solutions:**
1. Verify APS network connectivity
2. Connect to APS VPN
3. Test network access: `ping git.aps.anl.gov`
4. Contact APS IT for network issues

#### "Authentication failed" (HTTPS)
**Causes:**
- Wrong username/password
- Personal access token expired
- Two-factor authentication issues

**Solutions:**
1. Regenerate personal access token
2. Use GitHub CLI for easier authentication
3. Check 2FA requirements for organization

## Getting Help

### For Access Issues
1. **GitHub repositories:** Contact repository owners or organization admins
2. **APS GitLab:** Contact APS IT or repository maintainers
3. **Network issues:** Contact APS IT for VPN/network support

### For bAIt Framework
- Run diagnostic scripts first
- Check documentation in this repository
- Contact bAIt development team

### Emergency Procedures

If you need to work with bAIt but cannot access all repositories:

```bash
# 1. Clone main repository only
git clone https://github.com/your-org/bAIt.git

# 2. Initialize only accessible repositories
python scripts/init-accessible-submodules.py

# 3. Use bAIt with available components
pip install -e ./bait_base/
bait-analyze --help

# 4. Document which repositories you're missing for future reference
python scripts/check-submodule-access.py --json > my-access-status.json
```

This allows you to use the core bAIt functionality even without access to all repositories.