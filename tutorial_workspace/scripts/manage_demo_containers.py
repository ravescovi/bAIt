#!/usr/bin/env python3
"""
Container Management Script for BITS Demo

Manages the demo IOC containers with conflict resolution and health monitoring.
Created by bAIt tutorial system.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

class ContainerManager:
    """Manages demo IOC containers with conflict resolution."""
    
    def __init__(self):
        self.container_name = "demo_iocs"
        self.image_name = "epics-podman:latest"
        self.backup_image = "ghcr.io/bcda-aps/epics-podman:latest"
        
    def check_podman(self):
        """Check if Podman is available."""
        try:
            result = subprocess.run(["podman", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Podman available: {result.stdout.strip()}")
                return True
            else:
                print("❌ Podman not responding")
                return False
        except FileNotFoundError:
            print("❌ Podman not installed")
            return False
    
    def check_image_available(self):
        """Check if the container image is available."""
        try:
            result = subprocess.run(
                ["podman", "images", "--format", "json"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                images = json.loads(result.stdout)
                for image in images:
                    if any(self.image_name in tag for tag in image.get("Names", [])):
                        print(f"✅ Container image available: {self.image_name}")
                        return True
                
                print(f"⚠️  Image {self.image_name} not found")
                return False
            else:
                print("❌ Failed to check container images")
                return False
        except Exception as e:
            print(f"❌ Error checking images: {e}")
            return False
    
    def pull_image(self):
        """Pull the container image from registry."""
        print(f"📥 Pulling container image: {self.backup_image}")
        try:
            result = subprocess.run([
                "podman", "pull", self.backup_image
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Image pulled successfully")
                
                # Tag the image for local use
                tag_result = subprocess.run([
                    "podman", "tag", self.backup_image, self.image_name
                ], capture_output=True, text=True)
                
                if tag_result.returncode == 0:
                    print(f"✅ Image tagged as: {self.image_name}")
                    return True
                else:
                    print(f"⚠️  Failed to tag image: {tag_result.stderr}")
                    return False
            else:
                print(f"❌ Failed to pull image: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error pulling image: {e}")
            return False
    
    def stop_existing_container(self):
        """Stop and remove existing container if it exists."""
        try:
            # Check if container exists
            result = subprocess.run([
                "podman", "ps", "-a", "--format", "{{.Names}}"
            ], capture_output=True, text=True)
            
            if self.container_name in result.stdout:
                print(f"🛑 Stopping existing container: {self.container_name}")
                
                # Stop container
                stop_result = subprocess.run([
                    "podman", "stop", self.container_name
                ], capture_output=True, text=True)
                
                # Remove container
                rm_result = subprocess.run([
                    "podman", "rm", self.container_name
                ], capture_output=True, text=True)
                
                if stop_result.returncode == 0 and rm_result.returncode == 0:
                    print("✅ Existing container removed")
                    return True
                else:
                    print("⚠️  Issues removing existing container")
                    return False
            else:
                print("ℹ️  No existing container to remove")
                return True
                
        except Exception as e:
            print(f"❌ Error managing existing container: {e}")
            return False
    
    def start_container(self):
        """Start the demo IOCs container."""
        print(f"🚀 Starting container: {self.container_name}")
        try:
            result = subprocess.run([
                "podman", "run", "-d",
                "--name", self.container_name,
                "--network=host",
                self.image_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                print(f"✅ Container started successfully: {container_id[:12]}")
                return True
            else:
                print(f"❌ Failed to start container: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error starting container: {e}")
            return False
    
    def check_container_health(self):
        """Check if container is running and healthy."""
        try:
            result = subprocess.run([
                "podman", "ps", "--format", "{{.Names}} {{.Status}}"
            ], capture_output=True, text=True)
            
            if self.container_name in result.stdout:
                print(f"✅ Container is running: {self.container_name}")
                return True
            else:
                print(f"❌ Container not running: {self.container_name}")
                return False
        except Exception as e:
            print(f"❌ Error checking container health: {e}")
            return False
    
    def test_ioc_connectivity(self):
        """Test IOC connectivity using container's caget."""
        print("🔍 Testing IOC connectivity...")
        test_pvs = [
            "gp:m1.VAL",
            "gp:m2.VAL", 
            "gp:scaler1.CNT",
            "adsim:cam1:Acquire"
        ]
        
        success_count = 0
        for pv in test_pvs:
            try:
                result = subprocess.run([
                    "podman", "exec", self.container_name,
                    "caget", pv
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {pv}: {result.stdout.strip()}")
                    success_count += 1
                else:
                    print(f"❌ {pv}: Not responding")
            except subprocess.TimeoutExpired:
                print(f"❌ {pv}: Timeout")
            except Exception as e:
                print(f"❌ {pv}: Error - {e}")
        
        success_rate = success_count / len(test_pvs) * 100
        print(f"📊 IOC Connectivity: {success_count}/{len(test_pvs)} ({success_rate:.1f}%)")
        
        return success_count > 0
    
    def start_demo_system(self):
        """Complete startup procedure with error handling."""
        print("🎯 Starting BITS Demo Container System")
        print("=" * 50)
        
        # Step 1: Check Podman
        if not self.check_podman():
            print("❌ Cannot proceed without Podman")
            return False
        
        # Step 2: Check/pull image
        if not self.check_image_available():
            if not self.pull_image():
                print("❌ Cannot proceed without container image")
                return False
        
        # Step 3: Clean up existing containers
        if not self.stop_existing_container():
            print("⚠️  Proceeding despite cleanup issues")
        
        # Step 4: Start new container
        if not self.start_container():
            print("❌ Failed to start container")
            return False
        
        # Step 5: Wait for IOCs to initialize
        print("⏳ Waiting for IOCs to initialize (15 seconds)...")
        time.sleep(15)
        
        # Step 6: Check container health
        if not self.check_container_health():
            print("❌ Container health check failed")
            return False
        
        # Step 7: Test IOC connectivity
        if not self.test_ioc_connectivity():
            print("⚠️  Some IOCs may not be responding properly")
            return False
        
        print("\n🎉 Demo container system started successfully!")
        print("\nNext steps:")
        print("  1. Test IOCs: python scripts/check_connectivity.py")
        print("  2. Start tutorial: python -c \"from my_beamline.startup import *\"")
        print("  3. Run a scan: RE(bp.count([detector], num=3))")
        
        return True
    
    def stop_demo_system(self):
        """Stop the demo container system."""
        print("🛑 Stopping BITS Demo Container System")
        print("=" * 50)
        
        return self.stop_existing_container()
    
    def status(self):
        """Show current system status."""
        print("📊 BITS Demo System Status")
        print("=" * 30)
        
        self.check_podman()
        self.check_image_available()
        self.check_container_health()
        
        if self.check_container_health():
            self.test_ioc_connectivity()

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python manage_demo_containers.py [start|stop|status|restart]")
        sys.exit(1)
    
    manager = ContainerManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        success = manager.start_demo_system()
        sys.exit(0 if success else 1)
    elif command == "stop":
        success = manager.stop_demo_system()
        sys.exit(0 if success else 1)
    elif command == "restart":
        manager.stop_demo_system()
        time.sleep(2)
        success = manager.start_demo_system()
        sys.exit(0 if success else 1)
    elif command == "status":
        manager.status()
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: start, stop, status, restart")
        sys.exit(1)

if __name__ == "__main__":
    main()