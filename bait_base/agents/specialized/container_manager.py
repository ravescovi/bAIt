"""
Container Manager for BITS Tutorial Testing

Manages containerized IOCs with podman/docker support, health monitoring,
and automated container lifecycle management.
"""

import asyncio
import logging
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class ContainerRuntime(Enum):
    """Supported container runtimes"""
    PODMAN = "podman"
    DOCKER = "docker"


@dataclass
class ContainerInfo:
    """Information about a container"""
    name: str
    image: str
    status: str
    ports: Dict[str, str]
    created: str
    runtime: ContainerRuntime


@dataclass
class ContainerConfig:
    """Configuration for a container"""
    name: str
    image: str
    ports: Dict[str, str] = None  # host_port: container_port
    environment: Dict[str, str] = None
    volumes: Dict[str, str] = None  # host_path: container_path
    command: Optional[str] = None
    args: List[str] = None  # Command arguments
    options: List[str] = None  # Container runtime options
    healthcheck: Optional[Dict[str, Any]] = None
    startup_timeout: int = 60
    

class ContainerManager:
    """
    Manages containers for BITS tutorial testing.
    
    Features:
    - Podman preference with Docker fallback
    - Container health monitoring
    - Automatic restart and recovery
    - Network validation
    - Resource management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, prefer_podman: bool = True):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.container_manager")
        
        # Detect available runtime
        self.runtime = self._detect_runtime(prefer_podman)
        self.logger.info(f"Using container runtime: {self.runtime.value}")
        
        # Container configurations
        self.container_configs = self._load_container_configs()
        
        # State tracking
        self.managed_containers: Dict[str, ContainerInfo] = {}
        
    def _detect_runtime(self, prefer_podman: bool) -> ContainerRuntime:
        """Detect available container runtime"""
        runtimes_to_check = [ContainerRuntime.PODMAN, ContainerRuntime.DOCKER] if prefer_podman else [ContainerRuntime.DOCKER, ContainerRuntime.PODMAN]
        
        for runtime in runtimes_to_check:
            try:
                result = subprocess.run(
                    [runtime.value, "--version"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    self.logger.debug(f"Found {runtime.value}: {result.stdout.strip()}")
                    return runtime
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
        raise RuntimeError("No container runtime found (podman or docker)")
    
    def _load_container_configs(self) -> Dict[str, ContainerConfig]:
        """Load container configurations from config file"""
        containers_config = self.config.get("containers", {})
        container_configs = {}
        
        for name, config in containers_config.items():
            container_configs[name] = ContainerConfig(
                name=config.get("name", name),
                image=config["image"],
                ports=config.get("ports", {}),
                environment=config.get("environment", {}),
                volumes=config.get("volumes", {}),
                command=config.get("command"),
                args=config.get("args", []),
                options=config.get("options", []),
                healthcheck=config.get("healthcheck"),
                startup_timeout=config.get("startup_timeout", 60)
            )
        
        # Fallback to hardcoded configs if none provided
        if not container_configs:
            return {
                "adsim_ioc": ContainerConfig(
                    name="adsim_ioc",
                    image="epics-podman:latest",
                    args=["adsim"],
                    options=["--net=host", "-d"],
                    environment={
                    "IOC_PREFIX": "adsim:",
                    "IOC_NAME": "adsim_ioc"
                },
                healthcheck={
                    "command": "caget adsim:cam1:Acquire_RBV",
                    "timeout": 10,
                    "retries": 3
                },
                startup_timeout=90
            ),
            "gp_ioc": ContainerConfig(
                name="gp_ioc", 
                image="ghcr.io/epics-containers/ioc-gp:latest",
                ports={"5066": "5064", "5067": "5065"},
                environment={
                    "IOC_PREFIX": "gp:",
                    "IOC_NAME": "gp_ioc"
                },
                healthcheck={
                    "command": "caget gp:m1.RBV",
                    "timeout": 10,
                    "retries": 3
                },
                startup_timeout=60
            )
        }
    
    async def setup_tutorial_environment(self) -> bool:
        """Setup complete tutorial container environment"""
        self.logger.info("Setting up tutorial container environment...")
        
        try:
            # Stop any existing containers first
            await self.cleanup_containers()
            
            # Pull required images
            for config in self.container_configs.values():
                await self._pull_image(config.image)
                
            # Start tutorial IOCs
            success = await self.start_demo_iocs()
            
            if success:
                # Validate container health
                healthy = await self._validate_container_health()
                if healthy:
                    self.logger.info("✅ Tutorial environment ready")
                    return True
                else:
                    self.logger.error("❌ Container health validation failed")
                    return False
            else:
                self.logger.error("❌ Failed to start demo IOCs")
                return False
                
        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
            return False
    
    async def start_demo_iocs(self) -> bool:
        """Start the demo IOC containers"""
        self.logger.info("Starting demo IOC containers...")
        
        success = True
        for container_name, config in self.container_configs.items():
            container_success = await self._start_container(config)
            if not container_success:
                success = False
                self.logger.error(f"Failed to start {container_name}")
            else:
                self.logger.info(f"✅ Started {container_name}")
                
        return success
    
    async def _start_container(self, config: ContainerConfig) -> bool:
        """Start a single container"""
        try:
            # Build run command with base options
            cmd = [self.runtime.value, "run", "--name", config.name]
            
            # Add container options (like --net=host, -d, etc.)
            if config.options:
                cmd.extend(config.options)
            else:
                cmd.append("-d")  # Default to detached mode
            
            # Add port mappings (only if not using --net=host)
            if config.ports and "--net=host" not in (config.options or []):
                for host_port, container_port in config.ports.items():
                    cmd.extend(["-p", f"{host_port}:{container_port}"])
                
            # Add environment variables
            if config.environment:
                for env_var, value in config.environment.items():
                    cmd.extend(["-e", f"{env_var}={value}"])
                    
            # Add volumes
            if config.volumes:
                for host_path, container_path in config.volumes.items():
                    cmd.extend(["-v", f"{host_path}:{container_path}"])
                    
            # Add image
            cmd.append(config.image)
            
            # Add command arguments
            if config.args:
                cmd.extend(config.args)
            elif config.command:
                cmd.extend(config.command.split())
                
            self.logger.debug(f"Starting container: {' '.join(cmd)}")
            
            # Execute container start
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                self.logger.debug(f"Container {config.name} started with ID: {container_id}")
                
                # Wait for container to be ready
                ready = await self._wait_for_container_ready(config)
                
                if ready:
                    # Update managed containers
                    info = await self._get_container_info(config.name)
                    if info:
                        self.managed_containers[config.name] = info
                    return True
                else:
                    self.logger.error(f"Container {config.name} failed to become ready")
                    return False
            else:
                self.logger.error(f"Failed to start {config.name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting container {config.name}: {e}")
            return False
    
    async def _wait_for_container_ready(self, config: ContainerConfig) -> bool:
        """Wait for container to be ready"""
        self.logger.debug(f"Waiting for {config.name} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < config.startup_timeout:
            # Check if container is running
            if await self._is_container_running(config.name):
                # If healthcheck is configured, validate health
                if config.healthcheck:
                    if await self._check_container_health(config):
                        return True
                else:
                    # No healthcheck, assume ready if running
                    return True
                    
            await asyncio.sleep(2)
            
        self.logger.error(f"Timeout waiting for {config.name} to be ready")
        return False
    
    async def _is_container_running(self, container_name: str) -> bool:
        """Check if container is running"""
        try:
            cmd = [self.runtime.value, "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"]
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
                return container_name in containers
            return False
            
        except Exception:
            return False
    
    async def _check_container_health(self, config: ContainerConfig) -> bool:
        """Check container health using configured healthcheck"""
        if not config.healthcheck:
            return True
            
        try:
            # Execute healthcheck command
            health_cmd = config.healthcheck["command"].split()
            result = await self._run_command(health_cmd, timeout=config.healthcheck.get("timeout", 10))
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.debug(f"Healthcheck failed for {config.name}: {e}")
            return False
    
    async def _validate_container_health(self) -> bool:
        """Validate health of all managed containers"""
        self.logger.info("Validating container health...")
        
        all_healthy = True
        for container_name, config in self.container_configs.items():
            if container_name in self.managed_containers:
                healthy = await self._check_container_health(config)
                if healthy:
                    self.logger.debug(f"✅ {container_name}: Healthy")
                else:
                    self.logger.warning(f"❌ {container_name}: Unhealthy")
                    all_healthy = False
                    
        return all_healthy
    
    async def stop_container(self, container_name: str) -> bool:
        """Stop a specific container"""
        try:
            cmd = [self.runtime.value, "stop", container_name]
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                self.logger.debug(f"Stopped container: {container_name}")
                if container_name in self.managed_containers:
                    del self.managed_containers[container_name]
                return True
            else:
                self.logger.error(f"Failed to stop {container_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error stopping {container_name}: {e}")
            return False
    
    async def remove_container(self, container_name: str) -> bool:
        """Remove a container"""
        try:
            # Stop first if running
            await self.stop_container(container_name)
            
            # Remove container
            cmd = [self.runtime.value, "rm", container_name]
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                self.logger.debug(f"Removed container: {container_name}")
                return True
            else:
                self.logger.error(f"Failed to remove {container_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing {container_name}: {e}")
            return False
    
    async def cleanup_containers(self):
        """Stop and remove all managed containers"""
        self.logger.info("Cleaning up containers...")
        
        for container_name in list(self.managed_containers.keys()):
            await self.remove_container(container_name)
            
        self.logger.info("Container cleanup completed")
    
    async def restart_container(self, container_name: str) -> bool:
        """Restart a specific container"""
        self.logger.info(f"Restarting container: {container_name}")
        
        if container_name not in self.container_configs:
            self.logger.error(f"Unknown container: {container_name}")
            return False
            
        # Remove existing container
        await self.remove_container(container_name)
        
        # Start fresh container
        config = self.container_configs[container_name]
        return await self._start_container(config)
    
    async def get_container_logs(self, container_name: str, lines: int = 50) -> Optional[str]:
        """Get container logs"""
        try:
            cmd = [self.runtime.value, "logs", "--tail", str(lines), container_name]
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"Failed to get logs for {container_name}: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting logs for {container_name}: {e}")
            return None
    
    async def _pull_image(self, image: str) -> bool:
        """Pull container image"""
        self.logger.info(f"Pulling image: {image}")
        
        try:
            cmd = [self.runtime.value, "pull", image]
            result = await self._run_command(cmd, timeout=300)  # 5 minute timeout for pulls
            
            if result.returncode == 0:
                self.logger.debug(f"Successfully pulled {image}")
                return True
            else:
                self.logger.error(f"Failed to pull {image}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error pulling {image}: {e}")
            return False
    
    async def _get_container_info(self, container_name: str) -> Optional[ContainerInfo]:
        """Get detailed container information"""
        try:
            cmd = [self.runtime.value, "inspect", container_name]
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                inspect_data = json.loads(result.stdout)[0]
                
                return ContainerInfo(
                    name=container_name,
                    image=inspect_data["Config"]["Image"],
                    status=inspect_data["State"]["Status"], 
                    ports={},  # Could parse port mappings from NetworkSettings
                    created=inspect_data["Created"],
                    runtime=self.runtime
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting container info for {container_name}: {e}")
            return None
    
    async def _run_command(self, cmd: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute command with timeout"""
        try:
            # Run command asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                cmd, process.returncode, stdout.decode(), stderr.decode()
            )
            
        except asyncio.TimeoutError:
            # Kill process on timeout
            try:
                process.kill()
                await process.wait()
            except:
                pass
            raise
            
    def get_managed_containers(self) -> Dict[str, ContainerInfo]:
        """Get all managed containers"""
        return self.managed_containers.copy()
    
    def is_container_managed(self, container_name: str) -> bool:
        """Check if container is managed by this instance"""
        return container_name in self.managed_containers