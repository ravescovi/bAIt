#!/usr/bin/env python3
"""
Check connectivity to IOCs

This script verifies that IOCs are running and responding.
Created during tutorial development.
"""

import subprocess
import sys

def check_ioc_connectivity():
    """Check if IOCs are responding to caget commands."""
    test_pvs = [
        "gp:m1.VAL",
        "gp:m2.VAL", 
        "gp:scaler1.CNT",
        "adsim:cam1:Acquire"
    ]
    
    print("🔍 Checking IOC connectivity...")
    print("=" * 40)
    
    success_count = 0
    for pv in test_pvs:
        try:
            result = subprocess.run(
                ["caget", pv], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ {pv}: {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"❌ {pv}: Not responding")
        except subprocess.TimeoutExpired:
            print(f"❌ {pv}: Timeout")
        except FileNotFoundError:
            print("❌ caget command not found - EPICS tools not installed")
            return False
    
    print("=" * 40)
    print(f"📊 Summary: {success_count}/{len(test_pvs)} PVs responding")
    
    if success_count == len(test_pvs):
        print("🎉 All IOCs are responding!")
        return True
    elif success_count > 0:
        print("⚠️  Some IOCs are not responding")
        return False
    else:
        print("🚨 No IOCs are responding - check containers")
        return False

if __name__ == "__main__":
    success = check_ioc_connectivity()
    sys.exit(0 if success else 1)