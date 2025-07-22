#!/usr/bin/env python3
"""
bAIt Submodule Diagnostic Tool

This script diagnoses common submodule issues and provides specific solutions
for access problems, initialization failures, and synchronization issues.
"""

import subprocess
import sys
from pathlib import Path
import argparse
from typing import Dict, List, Tuple, Optional
import os

# Import functions from other scripts
from check_submodule_access import get_submodule_urls, check_git_access


def run_git_command(args: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Run a git command and return results.
    
    Args:
        args: Git command arguments
        cwd: Working directory (optional)
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_git_installation() -> bool:
    """Check if git is properly installed."""
    success, _, _ = run_git_command(["--version"])
    return success


def check_repository_status() -> Tuple[bool, str]:
    """Check if we're in a git repository."""
    success, _, stderr = run_git_command(["rev-parse", "--git-dir"])
    if success:
        return True, "Valid git repository"
    else:
        return False, f"Not a git repository: {stderr}"


def get_submodule_status() -> Dict[str, Dict]:
    """
    Get detailed status of all submodules.
    
    Returns:
        Dictionary with submodule status information
    """
    success, stdout, _ = run_git_command(["submodule", "status"])
    
    status_info = {}
    if success:
        for line in stdout.strip().split('\n'):
            if not line:
                continue
                
            # Parse submodule status line
            # Format: [status_char][commit_hash] [path] [(description)]
            status_char = line[0] if line else ' '
            parts = line[1:].split()
            
            if len(parts) >= 2:
                commit_hash = parts[0]
                path = parts[1]
                
                status_info[path] = {
                    'status_char': status_char,
                    'commit_hash': commit_hash,
                    'initialized': status_char != '-',
                    'updated': status_char == ' ',
                    'has_changes': status_char == '+',
                    'not_initialized': status_char == '-',
                    'exists': Path(path).exists()
                }
    
    return status_info


def check_ssh_config() -> Tuple[bool, str]:
    """Check SSH configuration for GitHub access."""
    try:
        # Test SSH connection to GitHub
        result = subprocess.run(
            ["ssh", "-T", "git@github.com"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # SSH to GitHub returns 1 on successful auth, 255 on failure
        if result.returncode == 1 and "successfully authenticated" in result.stderr:
            return True, "SSH authentication to GitHub working"
        else:
            return False, f"SSH authentication failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "SSH connection timeout"
    except Exception as e:
        return False, f"SSH test error: {str(e)}"


def check_git_credentials() -> Tuple[bool, str]:
    """Check git credential configuration."""
    # Check if credential helper is configured
    success, stdout, _ = run_git_command(["config", "--get", "credential.helper"])
    
    if success and stdout.strip():
        return True, f"Credential helper configured: {stdout.strip()}"
    else:
        return False, "No credential helper configured"


def diagnose_access_issues(submodule_path: str, url: str) -> List[str]:
    """
    Diagnose specific access issues for a submodule.
    
    Args:
        submodule_path: Path to the submodule
        url: Repository URL
        
    Returns:
        List of diagnostic messages and suggestions
    """
    diagnostics = []
    
    # Check URL format
    if url.startswith("git@"):
        diagnostics.append("Using SSH authentication")
        
        # Check SSH key
        ssh_ok, ssh_msg = check_ssh_config()
        if not ssh_ok:
            diagnostics.append(f"SSH issue: {ssh_msg}")
            diagnostics.append("SUGGESTION: Check SSH key configuration")
            diagnostics.append("  • Run: ssh-add -l (to list SSH keys)")
            diagnostics.append("  • Run: ssh-keygen -t ed25519 -C 'your_email@example.com' (to create key)")
            diagnostics.append("  • Add public key to GitHub/GitLab account")
        
    elif url.startswith("https://"):
        diagnostics.append("Using HTTPS authentication")
        
        # Check credentials
        cred_ok, cred_msg = check_git_credentials()
        if not cred_ok:
            diagnostics.append(f"Credential issue: {cred_msg}")
            diagnostics.append("SUGGESTION: Configure git credentials")
            diagnostics.append("  • Run: git config --global credential.helper store")
            diagnostics.append("  • Or use GitHub CLI: gh auth login")
    
    # Check repository accessibility
    has_access, error = check_git_access(url)
    if not has_access:
        diagnostics.append(f"Repository access failed: {error}")
        
        if "github.com" in url:
            if "repository not found" in error.lower():
                diagnostics.append("SUGGESTION: Repository may be private or not exist")
                diagnostics.append("  • Check repository URL spelling")
                diagnostics.append("  • Request access from repository owner")
                diagnostics.append("  • Verify you're logged into correct GitHub account")
            elif "permission denied" in error.lower():
                diagnostics.append("SUGGESTION: Permission denied")
                diagnostics.append("  • Request collaborator access to repository")
                diagnostics.append("  • Check if you're member of required organization")
        
        elif "git.aps.anl.gov" in url:
            diagnostics.append("SUGGESTION: APS GitLab access required")
            diagnostics.append("  • Must be on APS network or VPN")
            diagnostics.append("  • Contact APS IT for repository access")
            diagnostics.append("  • May need special permissions for this repository")
    
    # Check if submodule directory exists but is empty
    path_obj = Path(submodule_path)
    if path_obj.exists():
        if path_obj.is_dir() and not any(path_obj.iterdir()):
            diagnostics.append("Directory exists but is empty")
            diagnostics.append("SUGGESTION: Run 'git submodule update --init' for this submodule")
        elif not path_obj.is_dir():
            diagnostics.append("Path exists but is not a directory")
            diagnostics.append("SUGGESTION: Remove the file and reinitialize submodule")
    
    return diagnostics


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose bAIt submodule issues"
    )
    parser.add_argument(
        "--submodule", metavar="PATH",
        help="Diagnose specific submodule only"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show verbose diagnostic information"
    )
    parser.add_argument(
        "--fix-suggestions", action="store_true",
        help="Show detailed fix suggestions for all issues"
    )
    
    args = parser.parse_args()
    
    print("bAIt Submodule Diagnostic Tool")
    print("="*50)
    
    # Basic system checks
    print("SYSTEM CHECKS:")
    
    if not check_git_installation():
        print("❌ Git not installed or not in PATH")
        sys.exit(1)
    else:
        print("✅ Git is installed")
    
    repo_ok, repo_msg = check_repository_status()
    if not repo_ok:
        print(f"❌ {repo_msg}")
        sys.exit(1)
    else:
        print("✅ Valid git repository")
    
    print()
    
    # Get submodule information
    submodules = get_submodule_urls()
    if not submodules:
        print("❌ No submodules configured")
        sys.exit(1)
    
    submodule_status = get_submodule_status()
    
    # Filter to specific submodule if requested
    if args.submodule:
        if args.submodule not in submodules:
            print(f"❌ Submodule '{args.submodule}' not found")
            sys.exit(1)
        check_submodules = {args.submodule: submodules[args.submodule]}
    else:
        check_submodules = submodules
    
    print("SUBMODULE DIAGNOSTICS:")
    print()
    
    issues_found = 0
    
    for path, url in check_submodules.items():
        print(f"Checking: {path}")
        print(f"URL: {url}")
        
        # Get status
        status = submodule_status.get(path, {})
        
        # Basic status checks
        if not status.get('exists', False):
            print("  ❌ Directory does not exist")
            issues_found += 1
        elif not status.get('initialized', False):
            print("  ⚠️  Not initialized")
            issues_found += 1
        elif status.get('has_changes', False):
            print("  ⚠️  Has uncommitted changes")
        else:
            print("  ✅ Appears to be working")
        
        # Detailed diagnostics
        if args.verbose or not status.get('initialized', False) or not status.get('exists', False):
            diagnostics = diagnose_access_issues(path, url)
            for msg in diagnostics:
                if msg.startswith("SUGGESTION:"):
                    print(f"  💡 {msg}")
                elif msg.startswith("  •"):
                    print(f"    {msg}")
                else:
                    print(f"     {msg}")
        
        print()
    
    # Summary and suggestions
    if issues_found > 0:
        print(f"SUMMARY: Found {issues_found} issues")
        print()
        
        if args.fix_suggestions:
            print("GENERAL FIX SUGGESTIONS:")
            print("="*30)
            print("1. Initialize missing submodules:")
            print("   python scripts/init-accessible-submodules.py")
            print()
            print("2. Update all submodules:")
            print("   git submodule update --recursive")
            print()
            print("3. Check access to repositories:")
            print("   python scripts/check-submodule-access.py")
            print()
            print("4. For SSH issues:")
            print("   • Generate SSH key: ssh-keygen -t ed25519")
            print("   • Add to GitHub: https://github.com/settings/ssh")
            print("   • Test connection: ssh -T git@github.com")
            print()
            print("5. For HTTPS issues:")
            print("   • Configure credentials: git config --global credential.helper store")
            print("   • Use GitHub CLI: gh auth login")
            print()
            print("6. For permission issues:")
            print("   • Request repository access from owners")
            print("   • Join required GitHub organizations")
            print("   • Contact APS IT for APS GitLab repositories")
    else:
        print("✅ No issues found - all submodules appear to be working correctly")


if __name__ == "__main__":
    main()