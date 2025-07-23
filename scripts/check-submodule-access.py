#!/usr/bin/env python3
"""
bAIt Submodule Access Checker

This script validates user access to all configured submodules and provides
detailed reports on which repositories are accessible.
"""

import subprocess
import sys
from pathlib import Path
import json
from typing import Dict, List, Tuple
import argparse


def check_git_access(repo_url: str) -> Tuple[bool, str]:
    """
    Check if user has access to a git repository.
    
    Args:
        repo_url: The git repository URL to check
        
    Returns:
        Tuple of (has_access, error_message)
    """
    try:
        # Try to list remote references (lightweight operation)
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Timeout - repository not accessible"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_submodule_urls() -> Dict[str, str]:
    """
    Extract submodule URLs from .gitmodules file.
    
    Returns:
        Dictionary mapping submodule path to URL
    """
    gitmodules_path = Path(".gitmodules")
    if not gitmodules_path.exists():
        return {}
    
    submodules = {}
    current_path = None
    
    with open(gitmodules_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('[submodule'):
                # Extract path from [submodule "path"]
                current_path = line.split('"')[1]
            elif line.startswith('url =') and current_path:
                url = line.split('=', 1)[1].strip()
                submodules[current_path] = url
                current_path = None
                
    return submodules


def categorize_submodules(submodules: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Categorize submodules by directory.
    
    Args:
        submodules: Dictionary of submodule path to URL
        
    Returns:
        Dictionary of category to list of paths
    """
    categories = {
        "bits_base": [],
        "bits_deployments": [],
        "nsls_deployments": [],
        "resources": [],
        "containers": [],
        "other": []
    }
    
    for path in submodules.keys():
        if path.startswith("bits_base/"):
            categories["bits_base"].append(path)
        elif path.startswith("bits_deployments/"):
            categories["bits_deployments"].append(path)
        elif path.startswith("nsls_deployments/"):
            categories["nsls_deployments"].append(path)
        elif path.startswith("resources/"):
            categories["resources"].append(path)
        elif path.startswith("containers/"):
            categories["containers"].append(path)
        else:
            categories["other"].append(path)
            
    return categories


def main():
    parser = argparse.ArgumentParser(
        description="Check access to bAIt submodules"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--fix-permissions", action="store_true",
        help="Suggest solutions for access issues"
    )
    parser.add_argument(
        "--category", choices=["bits_base", "bits_deployments", "nsls_deployments", "resources", "containers"],
        help="Check only specific category of submodules"
    )
    
    args = parser.parse_args()
    
    # Get all submodules
    submodules = get_submodule_urls()
    if not submodules:
        print("ERROR: No submodules found. Run this script from the bAIt repository root.")
        sys.exit(1)
    
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
    
    # Check access to each submodule
    results = {}
    accessible_count = 0
    
    for path, url in check_submodules.items():
        has_access, error = check_git_access(url)
        results[path] = {
            "url": url,
            "accessible": has_access,
            "error": error
        }
        if has_access:
            accessible_count += 1
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"bAIt Submodule Access Report")
        print(f"{'='*50}")
        print(f"Total submodules checked: {len(check_submodules)}")
        print(f"Accessible: {accessible_count}")
        print(f"Inaccessible: {len(check_submodules) - accessible_count}")
        print()
        
        # Group by category for display
        for category, paths in categories.items():
            if args.category and category != args.category:
                continue
                
            category_paths = [p for p in paths if p in check_submodules]
            if not category_paths:
                continue
                
            print(f"{category.upper()}:")
            for path in category_paths:
                result = results[path]
                status = "✅" if result["accessible"] else "❌"
                print(f"  {status} {path}")
                if not result["accessible"]:
                    print(f"     Error: {result['error']}")
            print()
        
        # Provide suggestions if requested
        if args.fix_permissions:
            inaccessible = [
                (path, data) for path, data in results.items() 
                if not data["accessible"]
            ]
            
            if inaccessible:
                print("TROUBLESHOOTING SUGGESTIONS:")
                print("="*50)
                
                for path, data in inaccessible:
                    print(f"\n{path}:")
                    url = data["url"]
                    
                    if "github.com" in url:
                        if "permission denied" in data["error"].lower():
                            print("  • Check if you're a member of the GitHub organization")
                            print("  • Try switching to HTTPS authentication")
                            print("  • Verify your SSH key is configured correctly")
                        elif "repository not found" in data["error"].lower():
                            print("  • Repository may be private - request access")
                            print("  • Check if repository name/URL is correct")
                    elif "git.aps.anl.gov" in url:
                        print("  • This requires APS network access")
                        print("  • Contact APS IT for repository access")
                        print("  • May need to use VPN if off-site")
                    
                    print(f"  • URL: {url}")
    
    # Exit with error code if any repos are inaccessible
    if accessible_count < len(check_submodules):
        sys.exit(1)


if __name__ == "__main__":
    main()