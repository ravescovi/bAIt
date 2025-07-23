"""
Tutorial Parser for BITS Framework

Extracts executable commands, validation criteria, and step structure
from tutorial markdown files.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .tutorial_test_agent import TutorialStep


@dataclass
class CodeBlock:
    """Represents a code block from markdown"""
    language: str
    content: str
    line_number: int
    is_executable: bool = False


class TutorialParser:
    """
    Parses BITS tutorial markdown files to extract executable steps.
    
    Features:
    - Code block extraction (bash, python, shell)
    - Command identification and categorization
    - Expected outcome parsing
    - Validation criteria extraction
    - Dependency analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("bait.agents.tutorial_parser")
        
        # Executable language patterns
        self.executable_languages = {
            'bash', 'sh', 'shell', 'python', 'py', 'console', 'terminal'
        }
        
        # Command patterns to recognize
        self.command_patterns = {
            'conda_env': re.compile(r'conda\s+(create|activate)\s+.*'),
            'pip_install': re.compile(r'pip\s+install\s+.*'),
            'git_command': re.compile(r'git\s+\w+.*'),
            'container_start': re.compile(r'\./start_demo_iocs\.sh'),
            'python_script': re.compile(r'python\s+.*\.py'),
            'import_statement': re.compile(r'(import|from)\s+\w+.*'),
            'device_creation': re.compile(r'\w+\s*=\s*\w+Device\s*\(.*\)'),
            'plan_execution': re.compile(r'RE\s*\(.*\)'),
            'validation_check': re.compile(r'(caget|caput|validate_|test_).*')
        }
        
        # Expected outcome indicators
        self.outcome_patterns = {
            'success_indicator': re.compile(r'(✅|success|completed|ready|running)', re.IGNORECASE),
            'error_indicator': re.compile(r'(❌|error|failed|timeout|not found)', re.IGNORECASE),
            'output_example': re.compile(r'(output:|result:|returns:|shows:)', re.IGNORECASE)
        }
        
        # Path resolution mappings - configurable by user
        bits_demo_path = self.config.get('bits_demo_path', 'bits_base/BITS/src/bits_demo')
        self.path_mappings = {
            '/path/to/bits_demo': str(Path.cwd() / bits_demo_path),
            'bits_demo/': str(Path.cwd() / bits_demo_path) + '/',
            'cd bits_demo/': f'cd {str(Path.cwd() / bits_demo_path)}/',
            'scripts/explore_iocs.py': str(Path.cwd() / bits_demo_path / 'scripts/explore_iocs.py'),
            '/home/ravescovi/workspace/bAIt/scripts/': str(Path.cwd() / bits_demo_path / 'scripts/'),
            'tutorial_workspace/': str(Path.cwd() / 'tutorial_workspace/'),
            'containers/epics-podman/': 'containers/epics-podman/',
            'cd containers/epics-podman/': f'cd {str(Path.cwd())}/containers/epics-podman/',
            'ghcr.io/bcda-aps/epics-podman:latest': 'epics-podman:latest',
            'localhost/epics-podman:latest': 'epics-podman:latest'
        }
    
    def resolve_paths(self, command: str) -> str:
        """Resolve template paths to actual project paths"""
        resolved_command = command
        for template, actual in self.path_mappings.items():
            resolved_command = resolved_command.replace(template, actual)
        return resolved_command
    
    async def parse_file(self, file_path: Path, base_step_number: int = 0) -> List[TutorialStep]:
        """
        Parse a tutorial markdown file and extract executable steps.
        
        Args:
            file_path: Path to markdown file
            base_step_number: Starting step number for this file
            
        Returns:
            List of TutorialStep objects
        """
        self.logger.debug(f"Parsing tutorial file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract sections and code blocks
            sections = self._extract_sections(content)
            code_blocks = self._extract_code_blocks(content)
            
            # Parse steps from sections
            steps = []
            for i, section in enumerate(sections):
                step_number = base_step_number + i + 1
                
                # Find relevant code blocks for this section
                section_blocks = self._find_section_code_blocks(section, code_blocks)
                
                # Create tutorial step
                if section_blocks:
                    tutorial_step = self._create_tutorial_step(
                        step_number, section, section_blocks
                    )
                    if tutorial_step:
                        steps.append(tutorial_step)
                        
            self.logger.debug(f"Extracted {len(steps)} executable steps from {file_path.name}")
            return steps
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return []
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from markdown content"""
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            # Check for section headers (## or ###)
            if line.startswith(('##', '###')):
                # Save previous section
                if current_section:
                    current_section['content'] = '\n'.join(current_content)
                    current_section['end_line'] = i - 1
                    sections.append(current_section)
                
                # Start new section
                level = 2 if line.startswith('##') else 3
                title = line.lstrip('#').strip()
                
                current_section = {
                    'title': title,
                    'level': level,
                    'start_line': i,
                    'content': ''
                }
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Don't forget the last section
        if current_section:
            current_section['content'] = '\n'.join(current_content)
            current_section['end_line'] = len(lines) - 1
            sections.append(current_section)
            
        return sections
    
    def _extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """Extract code blocks from markdown content"""
        code_blocks = []
        lines = content.split('\n')
        
        in_code_block = False
        current_block = None
        current_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_block:
                        current_block.content = '\n'.join(current_lines)
                        current_block.is_executable = self._is_executable_block(current_block)
                        code_blocks.append(current_block)
                    
                    in_code_block = False
                    current_block = None
                    current_lines = []
                else:
                    # Start of code block
                    language = line[3:].strip() or 'text'
                    current_block = CodeBlock(
                        language=language.lower(),
                        content='',
                        line_number=i + 1
                    )
                    current_lines = []
                    in_code_block = True
            elif in_code_block:
                current_lines.append(line)
        
        return code_blocks
    
    def _is_executable_block(self, block: CodeBlock) -> bool:
        """Determine if a code block contains executable commands"""
        if block.language in self.executable_languages:
            return True
            
        # Check for executable patterns in content
        for pattern_name, pattern in self.command_patterns.items():
            if pattern.search(block.content):
                return True
                
        return False
    
    def _find_section_code_blocks(self, section: Dict[str, Any], code_blocks: List[CodeBlock]) -> List[CodeBlock]:
        """Find code blocks that belong to a specific section"""
        section_blocks = []
        
        for block in code_blocks:
            # Check if code block is within section boundaries
            if (section['start_line'] <= block.line_number <= section.get('end_line', float('inf')) and 
                block.is_executable):
                section_blocks.append(block)
                
        return section_blocks
    
    def _create_tutorial_step(self, step_number: int, section: Dict[str, Any], code_blocks: List[CodeBlock]) -> Optional[TutorialStep]:
        """Create a TutorialStep from section and code blocks"""
        if not code_blocks:
            return None
            
        # Extract commands from code blocks
        commands = []
        for block in code_blocks:
            block_commands = self._extract_commands_from_block(block)
            commands.extend(block_commands)
            
        if not commands:
            return None
        
        # Extract expected outcomes and validation criteria
        expected_outcomes = self._extract_expected_outcomes(section['content'])
        validation_criteria = self._extract_validation_criteria(section['content'])
        prerequisites = self._extract_prerequisites(section['content'])
        
        # Determine timeout based on command types
        timeout = self._calculate_step_timeout(commands)
        
        return TutorialStep(
            step_number=step_number,
            title=section['title'],
            commands=commands,
            expected_outcomes=expected_outcomes,
            validation_criteria=validation_criteria,
            prerequisites=prerequisites,
            timeout=timeout
        )
    
    def _extract_commands_from_block(self, block: CodeBlock) -> List[str]:
        """Extract individual commands from a code block"""
        commands = []
        
        if block.language in ['bash', 'sh', 'shell', 'console', 'terminal']:
            # Split bash commands by lines, handle multi-line commands
            lines = block.content.strip().split('\n')
            current_command = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    # Skip empty lines and comments
                    continue
                    
                if line.endswith('\\'):
                    # Multi-line command continuation
                    current_command.append(line[:-1].strip())
                else:
                    current_command.append(line)
                    if current_command:
                        raw_command = ' '.join(current_command).strip()
                        resolved_command = self.resolve_paths(raw_command)
                        commands.append(resolved_command)
                        current_command = []
                        
        elif block.language in ['python', 'py']:
            # For Python blocks, treat the entire block as one command
            if block.content.strip():
                resolved_command = self.resolve_paths(block.content.strip())
                commands.append(resolved_command)
                
        return [cmd for cmd in commands if cmd]  # Filter empty commands
    
    def _extract_expected_outcomes(self, content: str) -> List[str]:
        """Extract expected outcomes from section content"""
        outcomes = []
        lines = content.split('\n')
        
        for line in lines:
            # Look for outcome indicators
            for pattern_name, pattern in self.outcome_patterns.items():
                if pattern.search(line):
                    outcomes.append(line.strip())
                    break
                    
        return outcomes
    
    def _extract_validation_criteria(self, content: str) -> List[str]:
        """Extract validation criteria from section content"""
        criteria = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for validation-related text
            if any(keyword in line.lower() for keyword in [
                'should see', 'should show', 'verify', 'check', 'validate', 
                'confirm', 'ensure', 'expect'
            ]):
                criteria.append(line)
                
        return criteria
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisites from section content"""
        prerequisites = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            # Look for prerequisite indicators
            if any(keyword in line for keyword in [
                'before', 'first', 'prerequisite', 'require', 'need', 'must have'
            ]):
                prerequisites.append(line)
                
        return prerequisites
    
    def _calculate_step_timeout(self, commands: List[str]) -> int:
        """Calculate appropriate timeout for step based on command types"""
        base_timeout = 60  # 1 minute default
        
        for command in commands:
            # Container operations need more time
            if any(keyword in command.lower() for keyword in [
                'start_demo_iocs', 'podman', 'docker', 'container'
            ]):
                base_timeout = max(base_timeout, 300)  # 5 minutes
                
            # Package installations need more time
            elif any(keyword in command.lower() for keyword in [
                'conda create', 'pip install', 'apt install'
            ]):
                base_timeout = max(base_timeout, 180)  # 3 minutes
                
            # Git operations can take time
            elif 'git clone' in command.lower():
                base_timeout = max(base_timeout, 120)  # 2 minutes
                
        return base_timeout
    
    def get_command_category(self, command: str) -> str:
        """Categorize a command for better handling"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ['conda', 'pip', 'apt']):
            return 'package_management'
        elif any(keyword in command_lower for keyword in ['podman', 'docker', 'container']):
            return 'container_management'
        elif any(keyword in command_lower for keyword in ['git']):
            return 'version_control'
        elif any(keyword in command_lower for keyword in ['python', 'import', 'from']):
            return 'python_execution'
        elif any(keyword in command_lower for keyword in ['caget', 'caput', 'validate']):
            return 'validation'
        else:
            return 'general'