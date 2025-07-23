#!/usr/bin/env python3
"""
Test Improved Tutorial System

This script validates the enhanced tutorial system with:
- Proper BITS workflow
- Container management
- Path resolution
- Workspace setup

Created by bAIt tutorial improvement system.
"""

import sys
import subprocess
import time
from pathlib import Path

class TutorialSystemTester:
    """Test the improved tutorial system components."""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"     {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        
        return success
    
    def test_workspace_structure(self):
        """Test that workspace structure is correct."""
        required_dirs = [
            'scripts', 'examples', 'configs', 'docs', 'test_outputs'
        ]
        
        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.workspace_root / dir_name
            if not dir_path.exists():
                all_exist = False
                break
        
        return self.log_test(
            "Workspace Structure",
            all_exist,
            f"Required directories: {', '.join(required_dirs)}"
        )
    
    def test_script_availability(self):
        """Test that required scripts are available and executable."""
        required_scripts = [
            'scripts/setup_paths.sh',
            'scripts/start_demo_iocs.sh', 
            'scripts/stop_demo_iocs.sh',
            'scripts/manage_demo_containers.py',
            'scripts/check_connectivity.py'
        ]
        
        all_exist = True
        missing = []
        
        for script in required_scripts:
            script_path = self.workspace_root / script
            if not script_path.exists():
                all_exist = False
                missing.append(script)
            elif not script_path.stat().st_mode & 0o111:  # Check executable bit
                all_exist = False
                missing.append(f"{script} (not executable)")
        
        return self.log_test(
            "Script Availability",
            all_exist,
            f"Missing/issues: {missing}" if missing else "All scripts available and executable"
        )
    
    def test_environment_detection(self):
        """Test environment detection and configuration."""
        try:
            # Test conda detection
            conda_result = subprocess.run(
                ["which", "conda"], 
                capture_output=True, text=True
            )
            conda_available = conda_result.returncode == 0
            
            # Test podman detection
            podman_result = subprocess.run(
                ["which", "podman"],
                capture_output=True, text=True
            )
            podman_available = podman_result.returncode == 0
            
            # Both should be available for tutorial
            success = conda_available and podman_available
            
            message = f"Conda: {'✓' if conda_available else '✗'}, Podman: {'✓' if podman_available else '✗'}"
            
        except Exception as e:
            success = False
            message = f"Environment detection failed: {e}"
        
        return self.log_test("Environment Detection", success, message)
    
    def test_container_manager(self):
        """Test container management functionality."""
        try:
            # Test container manager status command
            result = subprocess.run([
                "python3", str(self.workspace_root / "scripts/manage_demo_containers.py"), "status"
            ], capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            message = "Container manager responds to status command"
            
        except subprocess.TimeoutExpired:
            success = False
            message = "Container manager status command timed out"
        except Exception as e:
            success = False
            message = f"Container manager test failed: {e}"
        
        return self.log_test("Container Manager", success, message)
    
    def test_bits_tutorial_structure(self):
        """Test if BITS tutorial structure can be created."""
        try:
            # Check if we can import apsbits (might not be installed)
            result = subprocess.run([
                "python3", "-c", "import apsbits; print('BITS available')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                success = True
                message = "BITS framework can be imported"
            else:
                success = False  # But this is expected in some environments
                message = "BITS framework not installed (expected in tutorial workspace)"
        
        except Exception as e:
            success = False
            message = f"BITS test failed: {e}"
        
        return self.log_test("BITS Framework", success, message)
    
    def test_path_resolution(self):
        """Test path resolution functionality."""
        try:
            # Check if path mappings work
            from pathlib import Path
            
            # Test key paths that tutorials expect
            bits_demo_path = Path("/home/ravescovi/workspace/bAIt/bits_base/BITS/src/bits_demo")
            tutorial_scripts = bits_demo_path / "scripts"
            
            paths_exist = bits_demo_path.exists() and tutorial_scripts.exists()
            
            message = f"BITS demo path: {'✓' if bits_demo_path.exists() else '✗'}, Tutorial scripts: {'✓' if tutorial_scripts.exists() else '✗'}"
            
        except Exception as e:
            paths_exist = False
            message = f"Path resolution test failed: {e}"
        
        return self.log_test("Path Resolution", paths_exist, message)
    
    def test_tutorial_files(self):
        """Test that tutorial files are accessible and properly formatted."""
        try:
            tutorial_dir = Path("/home/ravescovi/workspace/bAIt/bits_base/BITS/src/bits_demo/tutorial")
            
            if not tutorial_dir.exists():
                return self.log_test("Tutorial Files", False, "Tutorial directory not found")
            
            # Check for key tutorial files
            key_files = [
                "00_introduction.md",
                "01_ioc_exploration.md", 
                "02_bits_starter_setup.md"
            ]
            
            all_exist = all((tutorial_dir / f).exists() for f in key_files)
            
            message = f"Tutorial files found: {len([f for f in key_files if (tutorial_dir / f).exists()])}/{len(key_files)}"
            
        except Exception as e:
            all_exist = False
            message = f"Tutorial files test failed: {e}"
        
        return self.log_test("Tutorial Files", all_exist, message)
    
    def run_all_tests(self):
        """Run all tests and return overall success."""
        print("🧪 Testing Improved Tutorial System")
        print("=" * 50)
        
        tests = [
            self.test_workspace_structure,
            self.test_script_availability,
            self.test_environment_detection,
            self.test_container_manager,
            self.test_bits_tutorial_structure,
            self.test_path_resolution,
            self.test_tutorial_files
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 50)
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Tutorial system is ready.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Review issues above.")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r['success']]
            if failed_tests:
                print("\nFailed tests:")
                for test in failed_tests:
                    print(f"  • {test['test']}: {test['message']}")
            
            return False

def main():
    """Main test runner."""
    tester = TutorialSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Next steps:")
        print("  1. Follow tutorial 00_introduction.md for BITS workflow")
        print("  2. Use scripts/start_demo_iocs.sh to start containers")
        print("  3. Test with scripts/check_connectivity.py")
        print("  4. Begin IOC exploration tutorial")
    else:
        print("\n🔧 Fix the issues above before proceeding with tutorials.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()