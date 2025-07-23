#!/usr/bin/env python3
"""
bAIt Accessible Submodule Initializer

This script initializes only the submodules that the user has access to,
allowing for partial repository setups when not all repositories are accessible.
"""

import subprocess
import sys
from pathlib import Path
import argparse
from typing import Dict, List
import json

# Import the access checker
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("check_submodule_access", os.path.join(os.path.dirname(__file__), "check-submodule-access.py"))
check_submodule_access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_submodule_access)
get_submodule_urls = check_submodule_access.get_submodule_urls
check_git_access = check_submodule_access.check_git_access  
categorize_submodules = check_submodule_access.categorize_submodules


def get_initialized_submodules() -> List[str]:
    """
    Get list of already initialized submodules.
    
    Returns:
        List of submodule paths that are already initialized
    """
    try:
        result = subprocess.run(
            ["git", "submodule", "status"],
            capture_output=True,
            text=True
        )
        
        initialized = []
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('-'):
                # Extract submodule path (skip status character and commit hash)
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[1]
                    initialized.append(path)
        
        return initialized
        
    except Exception:
        return []


def init_submodule(path: str) -> bool:
    """
    Initialize a specific submodule.
    
    Args:
        path: Submodule path to initialize
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize the submodule
        result = subprocess.run(
            ["git", "submodule", "update", "--init", path],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
        
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Initialize accessible bAIt submodules"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be initialized without actually doing it"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Try to initialize even repositories that fail access check"
    )
    parser.add_argument(
        "--category", choices=["bits_base", "bits_deployments", "nsls_deployments", "containers"],
        help="Initialize only specific category of submodules"
    )
    parser.add_argument(
        "--parallel", type=int, default=1, metavar="N",
        help="Number of parallel initialization jobs (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Get all submodules
    submodules = get_submodule_urls()
    if not submodules:
        print("ERROR: No submodules found. Run this script from the bAIt repository root.")
        sys.exit(1)
    
    # Get already initialized submodules
    initialized = get_initialized_submodules()
    
    # Categorize submodules
    categories = categorize_submodules(submodules)
    
    # Filter by category if requested
    if args.category:
        check_submodules = {
            path: submodules[path] 
            for path in categories[args.category]
        }
    else:
        check_submodules = submodules
    
    print("bAIt Submodule Initialization")
    print("="*50)
    
    # Check access and determine what to initialize
    to_initialize = []
    skipped = []
    already_initialized = []
    
    for path, url in check_submodules.items():
        if path in initialized:
            already_initialized.append(path)
            continue
            
        if args.force:
            has_access = True
            error = ""
        else:
            has_access, error = check_git_access(url)
        
        if has_access:
            to_initialize.append(path)
        else:
            skipped.append((path, error))
    
    # Report what will be done
    print(f"Already initialized: {len(already_initialized)}")
    print(f"Will initialize: {len(to_initialize)}")
    print(f"Will skip (no access): {len(skipped)}")
    print()
    
    if already_initialized:
        print("ALREADY INITIALIZED:")
        for path in already_initialized:
            print(f"  ✅ {path}")
        print()
    
    if to_initialize:
        print("WILL INITIALIZE:")
        for path in to_initialize:
            print(f"  🔄 {path}")
        print()
    
    if skipped:
        print("SKIPPED (NO ACCESS):")
        for path, error in skipped:
            print(f"  ❌ {path}")
            print(f"     {error}")
        print()
    
    # Exit if dry run
    if args.dry_run:
        print("DRY RUN - No changes made")
        return
    
    # Ask for confirmation unless forcing
    if to_initialize and not args.force:
        response = input(f"Initialize {len(to_initialize)} submodules? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Cancelled")
            return
    
    # Initialize submodules
    if to_initialize:
        print("INITIALIZING SUBMODULES:")
        success_count = 0
        
        for path in to_initialize:
            print(f"  Initializing {path}...", end=" ")
            
            if init_submodule(path):
                print("✅")
                success_count += 1
            else:
                print("❌")
        
        print()
        print(f"Successfully initialized: {success_count}/{len(to_initialize)}")
        
        if success_count < len(to_initialize):
            print("Some submodules failed to initialize. Run with --force to retry.")
            sys.exit(1)
    else:
        print("Nothing to initialize")
    
    # Provide next steps
    if skipped:
        print("\nNEXT STEPS:")
        print("- For repositories you need access to, contact the repository owners")
        print("- Run 'python scripts/check-submodule-access.py --fix-permissions' for detailed help")
        print("- Once you have access, run this script again to initialize additional submodules")


if __name__ == "__main__":
    main()