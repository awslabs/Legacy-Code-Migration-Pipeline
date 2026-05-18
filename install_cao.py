#!/usr/bin/env python3
"""
CAO (CLI Agent Orchestrator) Installation Script

This script installs the CLI Agent Orchestrator (CAO) and its dependencies.
Agent installation is now handled separately by install_agents.py

Features:
1. Installs tmux (version 3.3+) using official installer
2. Installs uv using official installer
3. Installs CAO using uv tool install

Usage: python install_cao.py

Note: To install agents, use the install_agents.py script in your project's lcmp folder
"""

import os
import sys
import subprocess
import argparse
import shutil
import socket
import urllib.request
import urllib.error
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


class AgentSourceType(Enum):
    """Types of agent sources supported by the installation system."""
    BUILTIN = "builtin"
    LOCAL_FILE = "local_file"
    URL = "url"


@dataclass
class ProviderConfig:
    """Configuration for a CLI provider."""
    name: str
    display_name: str
    requires_cli: bool
    cli_command: Optional[str] = None
    installation_notes: Optional[str] = None


@dataclass
class AgentInstallConfig:
    """Configuration for installing an agent."""
    name: str
    source_type: AgentSourceType
    source_path: str
    provider: str
    metadata: Optional[Dict] = None


@dataclass
class InstallationResult:
    """Result of an agent installation attempt."""
    agent_name: str
    success: bool
    provider: str
    error_message: Optional[str] = None
    installation_method: Optional[str] = None


class ProviderManager:
    """Manages CLI providers for agent integration."""
    
    SUPPORTED_PROVIDERS = ['kiro_cli', 'q_cli', 'claude_code']
    DEFAULT_PROVIDER = 'kiro_cli'
    
    PROVIDER_CONFIGS = {
        'kiro_cli': ProviderConfig(
            name='kiro_cli',
            display_name='Kiro CLI',
            requires_cli=True,
            cli_command='kiro-cli',
            installation_notes='Ensure Kiro CLI is installed and accessible via kiro-cli command'
        ),
        'q_cli': ProviderConfig(
            name='q_cli', 
            display_name='Amazon Q CLI',
            requires_cli=True,
            cli_command='q',
            installation_notes='Install Amazon Q CLI from AWS'
        ),
        'claude_code': ProviderConfig(
            name='claude_code',
            display_name='Claude Code',
            requires_cli=False,
            installation_notes='No additional CLI installation required'
        )
    }
    
    def __init__(self, provider: Optional[str] = None):
        """Initialize provider manager with specified or default provider."""
        # Handle None, empty strings, and whitespace-only strings as default
        if not provider or not provider.strip():
            self.provider = self.DEFAULT_PROVIDER
        else:
            self.provider = provider
    
    def validate_provider(self) -> bool:
        """Validate that the specified provider is supported."""
        return self.provider in self.SUPPORTED_PROVIDERS
    
    def get_provider_config(self) -> ProviderConfig:
        """Get configuration for the current provider."""
        return self.PROVIDER_CONFIGS.get(self.provider)
    
    def get_supported_providers(self) -> List[str]:
        """Get list of all supported providers."""
        return self.SUPPORTED_PROVIDERS.copy()
    
    def get_provider_display_name(self) -> str:
        """Get display name for the current provider."""
        config = self.get_provider_config()
        return config.display_name if config else self.provider
    
    def check_provider_availability(self) -> bool:
        """Check if the provider CLI tool is available on the system."""
        config = self.get_provider_config()
        if not config:
            return False
        
        if not config.requires_cli:
            return True
        
        if config.cli_command:
            return check_command_exists(config.cli_command)
        
        return True
    
    def get_provider_specific_commands(self) -> Dict[str, str]:
        """Return provider-specific installation commands and options."""
        config = self.get_provider_config()
        if not config:
            return {}
        
        return {
            'provider_param': f'--provider={self.provider}',
            'display_name': config.display_name,
            'installation_notes': config.installation_notes or ''
        }
    
    def get_error_message_for_invalid_provider(self) -> str:
        """Get error message for invalid provider with supported options."""
        supported = ', '.join(self.SUPPORTED_PROVIDERS)
        return (f"Invalid provider '{self.provider}'. "
                f"Supported providers: {supported}")


class AgentSourceClassifier:
    """Classifies agent sources and generates appropriate installation commands."""
    
    def classify_agent_source(self, agent_input: str) -> AgentSourceType:
        """Classify agent input as built-in, local file, or URL."""
        # Check if it's a URL
        if agent_input.startswith(('http://', 'https://')):
            return AgentSourceType.URL
        
        # Check if it's a local file path
        if ('/' in agent_input or '\\' in agent_input or 
            agent_input.endswith('.md')):
            return AgentSourceType.LOCAL_FILE
        
        # Check if it exists as a file (but protect against checking command names)
        # Only check if it looks like a path (has extension or path separators)
        try:
            if '.' in agent_input or '/' in agent_input or '\\' in agent_input:
                if Path(agent_input).exists():
                    return AgentSourceType.LOCAL_FILE
        except (OSError, ValueError):
            # If Path operations fail, it's not a valid path
            pass
        
        # Otherwise assume it's a built-in agent name
        return AgentSourceType.BUILTIN
    
    def get_installation_command(self, source_type: AgentSourceType, 
                                agent_input: str, provider: str) -> List[str]:
        """Generate appropriate cao install command."""
        # FIXED: Changed from ["cao", "agent", "install"] to ["cao", "install"]
        # According to CAO documentation, the correct command is "cao install" not "cao agent install"
        base_cmd = ["cao", "install"]
        
        if source_type == AgentSourceType.BUILTIN:
            base_cmd.append(agent_input)
        elif source_type == AgentSourceType.LOCAL_FILE:
            # Resolve to absolute path for reliability, with error handling
            try:
                abs_path = str(Path(agent_input).resolve())
                base_cmd.append(abs_path)
            except (OSError, ValueError):
                # If path resolution fails, use the input as-is
                base_cmd.append(agent_input)
        elif source_type == AgentSourceType.URL:
            base_cmd.append(agent_input)
        
        # Add provider specification
        base_cmd.extend(["--provider", provider])
        
        return base_cmd


class InstallationError(Exception):
    """Custom exception for installation-related errors."""
    
    def __init__(self, message: str, source: Optional[str] = None, 
                 error_type: Optional[str] = None, suggestion: Optional[str] = None):
        self.message = message
        self.source = source
        self.error_type = error_type
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def get_formatted_message(self) -> str:
        """Get a formatted error message with source and suggestion."""
        parts = []
        
        if self.source:
            parts.append(f"Source: {self.source}")
        
        parts.append(f"Error: {self.message}")
        
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        
        return " | ".join(parts)


class NetworkErrorHandler:
    """Handles network-related errors and provides offline alternatives."""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self._network_available = None
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for detailed troubleshooting information."""
        logger = logging.getLogger('cao_network')
        logger.setLevel(logging.DEBUG)
        
        # Create file handler for detailed logs
        log_file = Path.home() / '.cao_install.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger if not already added
        if not logger.handlers:
            logger.addHandler(file_handler)
        
        return logger
    
    def check_network_connectivity(self, timeout: int = 5) -> bool:
        """
        Check if network connectivity is available.
        
        Args:
            timeout: Timeout in seconds for network check
            
        Returns:
            True if network is available, False otherwise
        """
        if self._network_available is not None:
            return self._network_available
        
        test_hosts = [
            ('8.8.8.8', 53),  # Google DNS
            ('1.1.1.1', 53),  # Cloudflare DNS
            ('github.com', 443),  # GitHub HTTPS
        ]
        
        for host, port in test_hosts:
            try:
                socket.setdefaulttimeout(timeout)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    self.logger.info(f"Network connectivity confirmed via {host}:{port}")
                    self._network_available = True
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Network check failed for {host}:{port}: {e}")
                continue
        
        self.logger.warning("No network connectivity detected")
        self._network_available = False
        return False
    
    def test_url_accessibility(self, url: str, timeout: int = 10) -> tuple[bool, Optional[str]]:
        """
        Test if a specific URL is accessible.
        
        Args:
            url: URL to test
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            self.logger.info(f"Testing URL accessibility: {url}")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'CAO-Installer/1.0')
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.getcode() == 200:
                    self.logger.info(f"URL accessible: {url}")
                    return True, None
                else:
                    error_msg = f"HTTP {response.getcode()}"
                    self.logger.warning(f"URL returned non-200 status: {url} - {error_msg}")
                    return False, error_msg
                    
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}: {e.reason}"
            self.logger.error(f"HTTP error accessing {url}: {error_msg}")
            return False, error_msg
            
        except urllib.error.URLError as e:
            error_msg = f"URL error: {e.reason}"
            self.logger.error(f"URL error accessing {url}: {error_msg}")
            return False, error_msg
            
        except socket.timeout:
            error_msg = "Connection timeout"
            self.logger.error(f"Timeout accessing {url}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error accessing {url}: {error_msg}")
            return False, error_msg
    
    def get_offline_alternatives(self, source_type: AgentSourceType, source_path: str) -> List[str]:
        """
        Get offline installation alternatives for network-dependent operations.
        
        Args:
            source_type: Type of agent source
            source_path: Path or URL of the source
            
        Returns:
            List of offline alternative suggestions
        """
        alternatives = []
        
        if source_type == AgentSourceType.URL:
            alternatives.extend([
                f"Download the agent file manually from: {source_path}",
                "Save the downloaded file to your project's agents/ directory",
                "Install using local file: cao install /path/to/downloaded/agent.md",
                "Check if the agent is available as a built-in: cao list --available"
            ])
        
        elif source_type == AgentSourceType.BUILTIN:
            # For built-in agents, network might be needed for initial CAO setup
            alternatives.extend([
                "Ensure CAO is properly installed with all built-in agents",
                "Try updating CAO when network is available: uv tool install --upgrade cli-agent-orchestrator",
                "Check local agent cache: ~/.aws/cli-agent-orchestrator/agent-store/"
            ])
        
        # General network troubleshooting
        alternatives.extend([
            "Check your internet connection and firewall settings",
            "Try again later if the issue is temporary",
            "Use a different network connection if available",
            "Contact your network administrator if behind a corporate firewall"
        ])
        
        return alternatives
    
    def handle_network_error(self, source_type: AgentSourceType, source_path: str, 
                           error_message: str) -> InstallationResult:
        """
        Handle network errors and provide user-friendly error messages with alternatives.
        
        Args:
            source_type: Type of agent source
            source_path: Path or URL of the source
            error_message: Original error message
            
        Returns:
            InstallationResult with detailed error information
        """
        agent_name = Path(source_path).stem
        
        # Log detailed error for troubleshooting
        self.logger.error(f"Network error for {source_type.value} agent '{agent_name}': {error_message}")
        
        # Create user-friendly error message
        if source_type == AgentSourceType.URL:
            user_message = f"Failed to download agent from URL: {source_path}"
        else:
            user_message = f"Network error during installation of {agent_name}"
        
        user_message += f"\nError details: {error_message}"
        
        # Add offline alternatives
        alternatives = self.get_offline_alternatives(source_type, source_path)
        if alternatives:
            user_message += "\n\nOffline alternatives:"
            for alt in alternatives:
                user_message += f"\n  • {alt}"
        
        # Add troubleshooting log location
        log_file = Path.home() / '.cao_install.log'
        user_message += f"\n\nDetailed logs available at: {log_file}"
        
        return InstallationResult(
            agent_name=agent_name,
            success=False,
            provider='unknown',
            error_message=user_message,
            installation_method='network_error'
        )


class OfflineInstallationManager:
    """Manages offline installation alternatives and caching."""
    
    def __init__(self):
        self.cache_dir = Path.home() / '.cao_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger('cao_offline')
    
    def cache_agent_file(self, url: str, content: str) -> Optional[Path]:
        """
        Cache an agent file for offline use.
        
        Args:
            url: Original URL of the agent
            content: Content of the agent file
            
        Returns:
            Path to cached file or None if caching failed
        """
        try:
            # Create a safe filename from URL
            safe_name = url.replace('/', '_').replace(':', '_').replace('?', '_')
            if not safe_name.endswith('.md'):
                safe_name += '.md'
            
            cache_file = self.cache_dir / safe_name
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Cached agent file: {cache_file}")
            return cache_file
            
        except Exception as e:
            self.logger.error(f"Failed to cache agent file from {url}: {e}")
            return None
    
    def get_cached_agents(self) -> List[Path]:
        """
        Get list of cached agent files.
        
        Returns:
            List of cached agent file paths
        """
        try:
            return list(self.cache_dir.glob('*.md'))
        except Exception as e:
            self.logger.error(f"Failed to list cached agents: {e}")
            return []
    
    def suggest_offline_installation(self, failed_sources: List[str]) -> None:
        """
        Suggest offline installation alternatives for failed sources.
        
        Args:
            failed_sources: List of sources that failed due to network issues
        """
        if not failed_sources:
            return
        
        print("\n🔌 Network Installation Failed - Offline Alternatives Available:")
        print("=" * 60)
        
        cached_agents = self.get_cached_agents()
        if cached_agents:
            print(f"📁 Found {len(cached_agents)} cached agent files:")
            for cached_file in cached_agents:
                print(f"  • {cached_file.name}")
            print("\nTo install cached agents:")
            print("  cao install ~/.cao_cache/<agent_file>.md --provider <provider>")
        
        print("\n💡 Manual Download Options:")
        for source in failed_sources:
            if source.startswith(('http://', 'https://')):
                print(f"  1. Download manually: {source}")
                print(f"  2. Save to: agents/{Path(source).name}")
                print(f"  3. Install: cao install agents/{Path(source).name}")
                print()
        
        print("🔧 Troubleshooting Steps:")
        print("  • Check internet connection: ping google.com")
        print("  • Test firewall settings")
        print("  • Try different network connection")
        print("  • Check proxy settings if behind corporate firewall")
        print(f"  • View detailed logs: cat {Path.home() / '.cao_install.log'}")


class EnhancedAgentSourceClassifier(AgentSourceClassifier):
    """Enhanced agent source classifier with network error handling."""
    
    def __init__(self):
        super().__init__()
        self.network_handler = NetworkErrorHandler()
        self.offline_manager = OfflineInstallationManager()
    
    def get_installation_command_with_network_handling(self, source_type: AgentSourceType, 
                                                     agent_input: str, provider: str) -> tuple[List[str], bool]:
        """
        Generate installation command with network connectivity checking.
        
        Args:
            source_type: Type of agent source
            agent_input: Agent input string
            provider: Provider name
            
        Returns:
            Tuple of (command_list, network_required)
        """
        base_cmd = self.get_installation_command(source_type, agent_input, provider)
        network_required = source_type == AgentSourceType.URL
        
        if network_required:
            # Check if URL is accessible
            accessible, error_msg = self.network_handler.test_url_accessibility(agent_input)
            if not accessible:
                self.network_handler.logger.warning(f"URL not accessible: {agent_input} - {error_msg}")
                return base_cmd, False  # Command generated but network check failed
        
        return base_cmd, True
    
    def handle_installation_with_fallback(self, config: AgentInstallConfig) -> InstallationResult:
        """
        Handle agent installation with network error fallback.
        
        Args:
            config: Agent installation configuration
            
        Returns:
            Installation result with network error handling
        """
        # Generate command with network checking
        install_command, network_ok = self.get_installation_command_with_network_handling(
            config.source_type, config.source_path, config.provider
        )
        
        if not network_ok and config.source_type == AgentSourceType.URL:
            # Network issue detected for URL source
            return self.network_handler.handle_network_error(
                config.source_type, 
                config.source_path, 
                "URL not accessible or network connectivity issue"
            )
        
        # Attempt installation
        try:
            # DEBUG: Print the command before execution
            print(f"   🔧 Executing command: {' '.join(install_command)}")
            
            success = run_command(install_command, check=False)
            
            if success:
                return InstallationResult(
                    agent_name=config.name,
                    success=True,
                    provider=config.provider,
                    installation_method="cao install"
                )
            else:
                # Installation failed - check if it's network-related
                if config.source_type == AgentSourceType.URL:
                    if not self.network_handler.check_network_connectivity():
                        return self.network_handler.handle_network_error(
                            config.source_type,
                            config.source_path,
                            "Network connectivity lost during installation"
                        )
                
                return InstallationResult(
                    agent_name=config.name,
                    success=False,
                    provider=config.provider,
                    error_message="Installation command failed",
                    installation_method="failed"
                )
                
        except Exception as e:
            # Check if exception is network-related
            error_str = str(e).lower()
            if any(term in error_str for term in ['network', 'connection', 'timeout', 'dns', 'resolve']):
                return self.network_handler.handle_network_error(
                    config.source_type,
                    config.source_path,
                    str(e)
                )
            
            return InstallationResult(
                agent_name=config.name,
                success=False,
                provider=config.provider,
                error_message=f"Installation error: {str(e)}",
                installation_method="failed"
            )


class ProgressIndicator:
    """Simple progress indicator for installation steps."""
    
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
    
    def start_step(self, description: str) -> None:
        """Start a new step with description."""
        self.current_step += 1
        progress = f"[{self.current_step}/{self.total_steps}]"
        print(f"\n{progress} {description}")
    
    def complete_step(self, success: bool = True) -> None:
        """Mark current step as complete."""
        if success:
            print("✅ Step completed successfully")
        else:
            print("❌ Step failed")
    
    def show_summary(self, successful_steps: int) -> None:
        """Show final summary."""
        print(f"\n📊 Installation Summary: {successful_steps}/{self.total_steps} steps completed successfully")


class PrerequisiteValidator:
    """Validates system prerequisites before installation."""
    
    REQUIRED_TOOLS = {
        'git': {
            'name': 'Git',
            'check_command': 'git',
            'install_help': 'Install Git from https://git-scm.com/ or use your system package manager',
            'critical': True
        },
        'tmux': {
            'name': 'tmux',
            'check_command': 'tmux',
            'version_check': True,
            'min_version': '3.3',
            'install_help': 'Install tmux 3.3+ using the CAO installer or your system package manager',
            'critical': False  # Will be installed by the installer
        },
        'uv': {
            'name': 'uv',
            'check_command': 'uv',
            'install_help': 'Install uv from https://docs.astral.sh/uv/getting-started/installation/',
            'critical': False  # Will be installed by the installer
        },
        'cao': {
            'name': 'CLI Agent Orchestrator',
            'check_command': 'cao',
            'install_help': 'CAO will be installed automatically if missing',
            'critical': False  # Can be installed during the process
        }
    }
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_all_prerequisites(self) -> bool:
        """Validate all system prerequisites."""
        print("🔍 Validating system prerequisites...")
        
        all_valid = True
        
        for tool_key, tool_info in self.REQUIRED_TOOLS.items():
            is_valid = self._validate_tool(tool_key, tool_info)
            self.validation_results[tool_key] = is_valid
            
            if not is_valid and tool_info['critical']:
                all_valid = False
        
        self._report_validation_results()
        return all_valid
    
    def _validate_tool(self, tool_key: str, tool_info: dict) -> bool:
        """Validate a specific tool."""
        tool_name = tool_info['name']
        check_command = tool_info['check_command']
        
        if not check_command_exists(check_command):
            error_msg = f"{tool_name} is required but not found"
            suggestion = tool_info['install_help']
            
            if tool_info['critical']:
                self.errors.append(InstallationError(
                    error_msg, 
                    source=tool_key,
                    error_type='missing_prerequisite',
                    suggestion=suggestion
                ))
            else:
                self.warnings.append(f"⚠️  {error_msg}. {suggestion}")
            
            return False
        
        # Check version if required
        if tool_info.get('version_check') and tool_key == 'tmux':
            return self._validate_tmux_version(tool_info)
        
        return True
    
    def _validate_tmux_version(self, tool_info: dict) -> bool:
        """Validate tmux version specifically."""
        try:
            version_output = run_command(["tmux", "-V"], capture_output=True)
            if version_output:
                version_str = version_output.split()[1]
                version_num = ''.join(c for c in version_str if c.isdigit() or c == '.')
                major, minor = map(int, version_num.split('.')[:2])
                
                if major > 3 or (major == 3 and minor >= 3):
                    return True
                else:
                    error_msg = f"tmux version {version_str} found, but 3.3+ is required"
                    self.errors.append(InstallationError(
                        error_msg,
                        source='tmux',
                        error_type='version_mismatch',
                        suggestion=tool_info['install_help']
                    ))
                    return False
        except Exception:
            self.warnings.append("⚠️  Could not determine tmux version")
            return True  # Assume it's okay if we can't check
        
        return False
    
    def _report_validation_results(self) -> None:
        """Report validation results to user."""
        if self.errors:
            print("\n❌ Critical prerequisites missing:")
            for error in self.errors:
                print(f"  • {error.get_formatted_message()}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ All prerequisites validated successfully")
    
    def get_validation_summary(self) -> dict:
        """Get summary of validation results."""
        return {
            'all_valid': len(self.errors) == 0,
            'critical_errors': len(self.errors),
            'warnings': len(self.warnings),
            'results': self.validation_results.copy()
        }


def enhanced_error_handler(func):
    """Decorator to add enhanced error handling to functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InstallationError as e:
            print(f"❌ Installation Error: {e.get_formatted_message()}")
            return False
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(e.cmd) if hasattr(e, 'cmd') else 'Unknown command'}"
            suggestion = "Check command syntax and system requirements"
            print(f"❌ {error_msg}")
            print(f"💡 Suggestion: {suggestion}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"Details: {e.stderr}")
            return False
        except FileNotFoundError as e:
            error_msg = f"Required file or command not found: {e.filename if hasattr(e, 'filename') else str(e)}"
            suggestion = "Ensure all required tools are installed and in PATH"
            print(f"❌ {error_msg}")
            print(f"💡 Suggestion: {suggestion}")
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            suggestion = "Please check the installation logs and try again"
            print(f"❌ {error_msg}")
            print(f"💡 Suggestion: {suggestion}")
            return False
    
    return wrapper


@enhanced_error_handler
def run_command(command, shell=False, check=True, capture_output=False):
    """Run a command and handle errors gracefully."""
    try:
        # Ensure uv tools are in PATH
        import os
        uv_bin_path = os.path.expanduser("~/.local/bin")
        current_path = os.environ.get("PATH", "")
        if uv_bin_path not in current_path:
            os.environ["PATH"] = f"{uv_bin_path}:{current_path}"
        
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check)
            return True
    except subprocess.CalledProcessError as e:
        # Enhanced error reporting with context
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Command failed: {cmd_str}")
        
        # Provide specific error context
        if hasattr(e, 'returncode'):
            print(f"   Exit code: {e.returncode}")
        
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        elif hasattr(e, 'stdout') and e.stdout:
            print(f"   Output: {e.stdout.strip()}")
        
        # Provide contextual suggestions based on command type
        suggestions = _get_command_failure_suggestions(command, e)
        if suggestions:
            print(f"💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        
        return False
    except FileNotFoundError as e:
        cmd_name = command[0] if isinstance(command, list) else command
        print(f"❌ Command not found: {cmd_name}")
        
        # Provide installation suggestions for common tools
        suggestions = _get_missing_command_suggestions(cmd_name)
        if suggestions:
            print(f"💡 To install {cmd_name}:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        
        return False
    except Exception as e:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Unexpected error running command: {cmd_str}")
        print(f"   Error: {str(e)}")
        print(f"💡 Suggestion: Check command syntax and system requirements")
        return False


def _get_command_failure_suggestions(command, error) -> List[str]:
    """Get contextual suggestions based on command failure."""
    suggestions = []
    cmd_name = command[0] if isinstance(command, list) else command.split()[0]
    
    if cmd_name == 'cao':
        suggestions.extend([
            "Ensure CAO is properly installed: uv tool install git+https://github.com/awslabs/cli-agent-orchestrator.git@main",
            "Check if CAO is in your PATH: echo $PATH",
            "Try restarting your shell or running: source ~/.bashrc"
        ])
    elif cmd_name == 'uv':
        suggestions.extend([
            "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh",
            "Restart your shell after installation",
            "Check uv installation: which uv"
        ])
    elif cmd_name == 'tmux':
        suggestions.extend([
            "Install tmux 3.3+: Use the CAO tmux installer or your system package manager",
            "On macOS: brew install tmux",
            "On Ubuntu/Debian: sudo apt install tmux"
        ])
    elif cmd_name == 'git':
        suggestions.extend([
            "Install Git from https://git-scm.com/",
            "On macOS: brew install git or use Xcode Command Line Tools",
            "On Ubuntu/Debian: sudo apt install git"
        ])
    else:
        suggestions.append("Check if the command is installed and accessible in your PATH")
    
    return suggestions


def _get_missing_command_suggestions(cmd_name: str) -> List[str]:
    """Get installation suggestions for missing commands."""
    suggestions = []
    
    if cmd_name == 'cao':
        suggestions.extend([
            "Install CAO: uv tool install git+https://github.com/awslabs/cli-agent-orchestrator.git@main",
            "Ensure uv is installed first"
        ])
    elif cmd_name == 'uv':
        suggestions.extend([
            "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh",
            "Visit: https://docs.astral.sh/uv/getting-started/installation/"
        ])
    elif cmd_name == 'tmux':
        suggestions.extend([
            "Use CAO tmux installer (recommended)",
            "macOS: brew install tmux",
            "Ubuntu/Debian: sudo apt install tmux",
            "CentOS/RHEL: sudo yum install tmux"
        ])
    elif cmd_name == 'git':
        suggestions.extend([
            "Visit: https://git-scm.com/downloads",
            "macOS: brew install git",
            "Ubuntu/Debian: sudo apt install git"
        ])
    elif cmd_name in ['kiro', 'q', 'claude']:
        provider_name = {'kiro': 'K-CLI (Kiro)', 'q': 'Amazon Q CLI', 'claude': 'Claude Code'}[cmd_name]
        suggestions.append(f"Install {provider_name} - check provider documentation")
    
    return suggestions


def check_command_exists(command):
    """Check if a command exists in the system PATH."""
    # First try the standard approach
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # For tmux, try -V instead of --version
    if command == "tmux":
        try:
            subprocess.run([command, "-V"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # For CAO, try --help instead of --version
    if command == "cao":
        try:
            subprocess.run([command, "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # Try with explicit PATH including uv tools directory
    import os
    uv_bin_path = os.path.expanduser("~/.local/bin")
    current_path = os.environ.get("PATH", "")
    if uv_bin_path not in current_path:
        new_path = f"{uv_bin_path}:{current_path}"
        env = os.environ.copy()
        env["PATH"] = new_path
        
        try:
            if command == "cao":
                subprocess.run([command, "--help"], capture_output=True, check=True, env=env)
            else:
                subprocess.run([command, "--version"], capture_output=True, check=True, env=env)
            # Update the current process PATH for subsequent calls
            os.environ["PATH"] = new_path
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    return False


def install_tmux_fallback():
    """Fallback tmux installation using system package managers."""
    print("📦 Attempting fallback tmux installation...")
    
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        if check_command_exists("brew"):
            print("Using Homebrew to install tmux...")
            return run_command(["brew", "install", "tmux"])
        else:
            print("❌ Homebrew not found. Please install tmux manually:")
            print("  1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("  2. Run: brew install tmux")
            return False
    elif system == "linux":
        # Try different package managers
        if check_command_exists("apt"):
            print("Using apt to install tmux...")
            return (run_command(["sudo", "apt", "update"]) and 
                   run_command(["sudo", "apt", "install", "-y", "tmux"]))
        elif check_command_exists("yum"):
            print("Using yum to install tmux...")
            return run_command(["sudo", "yum", "install", "-y", "tmux"])
        elif check_command_exists("dnf"):
            print("Using dnf to install tmux...")
            return run_command(["sudo", "dnf", "install", "-y", "tmux"])
        else:
            print("❌ No supported package manager found. Please install tmux manually.")
            return False
    else:
        print(f"❌ Unsupported operating system: {system}")
        print("Please install tmux 3.3+ manually")
        return False


def install_tmux():
    """Install tmux using the official CAO installer script."""
    print("📦 Installing tmux (version 3.3+ required)...")
    
    # Check if tmux is already installed and version is sufficient
    if check_command_exists("tmux"):
        try:
            version_output = run_command(["tmux", "-V"], capture_output=True)
            if version_output:
                # Extract version number (format: "tmux 3.3a")
                version_str = version_output.split()[1]
                # Remove any letter suffix (like 'a' in '3.3a')
                version_num = ''.join(c for c in version_str if c.isdigit() or c == '.')
                major, minor = map(int, version_num.split('.')[:2])
                
                if major > 3 or (major == 3 and minor >= 3):
                    print("✅ tmux 3.3+ is already installed")
                    return True
                else:
                    print(f"⚠️  tmux version {version_str} found, but 3.3+ is required")
        except Exception:
            print("⚠️  Could not determine tmux version, proceeding with installation")
    
    # Install using official CAO tmux installer
    print("📥 Using official CAO tmux installer...")
    
    # Download and execute the script in two steps to avoid bash process substitution issues
    download_cmd = "curl -s https://raw.githubusercontent.com/awslabs/cli-agent-orchestrator/refs/heads/main/tmux-install.sh"
    execute_cmd = "bash"
    
    try:
        # Download the script
        result = subprocess.run(download_cmd, shell=True, capture_output=True, text=True, check=True)
        script_content = result.stdout
        
        # Execute the script
        process = subprocess.run(execute_cmd, input=script_content, shell=True, text=True, check=True)
        
        print("✅ tmux installation completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install tmux using CAO installer")
        print(f"Error: {e}")
        print("Trying fallback installation method...")
        return install_tmux_fallback()


def install_uv():
    """Install uv using the official installer."""
    print("📦 Installing uv...")
    
    if check_command_exists("uv"):
        print("✅ uv is already installed")
        return True
    
    # Install uv using the official installer
    install_script = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    if not run_command(install_script, shell=True):
        print("❌ Failed to install uv. Please install manually: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    print("✅ uv installation completed")
    print("📝 Note: You may need to restart your shell or run 'source ~/.bashrc' to use uv")
    return True


def install_cao():
    """Install CLI Agent Orchestrator using uv tool install."""
    print("📦 Installing CLI Agent Orchestrator...")
    
    # Check if cao is already installed
    if check_command_exists("cao"):
        print("✅ CAO is already installed")
        response = input("Upgrade to latest version? (Y/n): ")
        if response.lower() == 'n':
            return True
    
    # Install CAO using uv tool install
    install_command = [
        "uv", "tool", "install", 
        "git+https://github.com/awslabs/cli-agent-orchestrator.git@main",
        "--upgrade"
    ]
    
    if not run_command(install_command):
        print("❌ Failed to install CAO")
        print("Make sure uv is properly installed and in your PATH")
        return False
    
    print("✅ CAO installation completed")
    return True


def install_dependencies():
    """Install all required dependencies."""
    print("🔧 Installing required dependencies...")
    
    # Check git first
    if not check_command_exists("git"):
        print("❌ Git is required but not found. Please install git first.")
        return False
    else:
        print("✅ git is available")
    
    # Install tmux
    if not install_tmux():
        return False
    
    # Install uv
    if not install_uv():
        return False
    
    # Install CAO
    if not install_cao():
        return False
    
    return True


def verify_cao_installation():
    """Verify that CAO is properly installed and accessible."""
    print("🔍 Verifying CAO installation...")
    
    if not check_command_exists("cao"):
        print("❌ CAO command not found in PATH")
        print("You may need to restart your shell or add uv tools to your PATH")
        print("Try running: export PATH=\"$HOME/.local/bin:$PATH\"")
        return False
    
    # Test CAO help command
    try:
        result = run_command(["cao", "--help"], capture_output=True)
        if result:
            print("✅ CAO is properly installed and accessible")
            
            # Check available commands
            print("🔍 Checking available CAO commands...")
            help_output = run_command(["cao", "--help"], capture_output=True, check=False)
            if help_output and "install" in help_output.lower():
                print("✅ CAO install command is available")
            else:
                print("⚠️  CAO install command may not be available")
            
            return True
    except Exception as e:
        print(f"❌ Error testing CAO: {e}")
    
    print("❌ CAO installation verification failed")
    return False


def get_agent_files(project_dir):
    """Get all agent files from the agents directory and subdirectories."""
    agents_dir = project_dir / "agents"
    
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return []
    
    # Use recursive glob to find all .md files in agents directory and subdirectories
    agent_files = list(agents_dir.glob("**/*.md"))
    return agent_files


def parse_agent_metadata(agent_file):
    """Parse the YAML frontmatter from an agent file to get the agent name and metadata."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1])
                    if isinstance(metadata, dict):
                        # Ensure name is a string and return full metadata dict
                        if 'name' in metadata:
                            metadata['name'] = str(metadata['name']) if metadata['name'] is not None else agent_file.stem
                        else:
                            metadata['name'] = agent_file.stem
                        return metadata
                    else:
                        # If YAML doesn't parse to a dict, fall back to simple parsing
                        for line in parts[1].split('\n'):
                            if line.strip().startswith('name:'):
                                name = line.split(':', 1)[1].strip().strip('"\'')
                                return {'name': name}
                except ImportError:
                    # Fallback: simple parsing for name field
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            name = line.split(':', 1)[1].strip().strip('"\'')
                            return {'name': name}
                except Exception:
                    # If YAML parsing fails, fall back to simple parsing
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            name = line.split(':', 1)[1].strip().strip('"\'')
                            return {'name': name}
        
        # Fallback to filename - return as dict for consistency
        return {'name': agent_file.stem}
    
    except Exception as e:
        print(f"Warning: Could not parse metadata from {agent_file}: {e}")
        return {'name': agent_file.stem}


def install_agents_v2(project_dir: Path, provider_manager: ProviderManager, 
                     agent_sources: Optional[List[str]] = None) -> bool:
    """
    Updated agent installation using new CAO commands with provider support and network error handling.
    
    Args:
        project_dir: Project directory path
        provider_manager: Provider manager instance
        agent_sources: Optional list of specific agent sources to install
    
    Returns:
        True if installation was successful, False otherwise
    """
    print("🤖 Installing agents with provider support and network error handling...")
    
    # Enhanced K-CLI integration and provider compatibility checking
    provider_available = provider_manager.check_provider_availability()
    config = provider_manager.get_provider_config()
    
    # Display selected provider (Requirement 5.2)
    print(f"🔧 Selected provider: {provider_manager.get_provider_display_name()}")
    
    if not provider_available:
        print(f"⚠️  Provider {provider_manager.get_provider_display_name()} is not available on this system")
        
        # Provide specific guidance based on provider type
        if config and config.installation_notes:
            print(f"📝 Installation guidance: {config.installation_notes}")
        
        # For K-CLI specifically, provide detailed instructions and alternatives (Requirements 5.4, 5.5)
        if provider_manager.provider == 'kiro_cli':
            print("\n🔧 Kiro CLI Setup Instructions:")
            print("   Kiro CLI is required for agent integration with CAO.")
            print("   To install Kiro CLI:")
            print("   1. Visit: https://kiro.ai")
            print("   2. Follow the installation instructions for your platform")
            print("   3. Ensure 'kiro-cli' command is available in your PATH")
            print("   4. Verify installation: kiro-cli --version")
            
            # Offer alternative providers (Requirement 5.5)
            print("\n🔄 Alternative Provider Options:")
            alternatives = [p for p in provider_manager.get_supported_providers() if p != 'kiro_cli']
            for alt_provider in alternatives:
                alt_config = ProviderManager.PROVIDER_CONFIGS.get(alt_provider)
                if alt_config:
                    print(f"   • {alt_config.display_name} (--provider {alt_provider})")
                    if alt_config.installation_notes:
                        print(f"     {alt_config.installation_notes}")
            
            # Ask user if they want to continue or switch providers
            print("\nOptions:")
            print("1. Continue with K-CLI (agents will be installed but may not work until K-CLI is available)")
            print("2. Switch to an alternative provider")
            print("3. Exit and install K-CLI first")
            
            choice = input("Choose an option (1/2/3): ").strip()
            
            if choice == '2':
                print("\nAvailable alternative providers:")
                for i, alt_provider in enumerate(alternatives, 1):
                    alt_config = ProviderManager.PROVIDER_CONFIGS.get(alt_provider)
                    if alt_config:
                        print(f"{i}. {alt_config.display_name} (--provider {alt_provider})")
                
                try:
                    alt_choice = int(input(f"Select provider (1-{len(alternatives)}): ").strip())
                    if 1 <= alt_choice <= len(alternatives):
                        new_provider = alternatives[alt_choice - 1]
                        provider_manager = ProviderManager(new_provider)
                        print(f"✅ Switched to provider: {provider_manager.get_provider_display_name()}")
                    else:
                        print("Invalid choice, continuing with K-CLI")
                except (ValueError, IndexError):
                    print("Invalid choice, continuing with K-CLI")
            
            elif choice == '3':
                print("Exiting. Please install K-CLI and run the script again.")
                return False
            
            else:
                print("Continuing with K-CLI provider...")
        
        else:
            # For other providers, provide their specific guidance
            print(f"\n📋 To use {provider_manager.get_provider_display_name()}:")
            if config and config.cli_command:
                print(f"   Ensure '{config.cli_command}' command is available in your PATH")
            if config and config.installation_notes:
                print(f"   {config.installation_notes}")
    
    else:
        # Provider is available - provide usage instructions (Requirement 5.4)
        if provider_manager.provider == 'kiro_cli':
            print("✅ Kiro CLI is available and ready for use")
            print("📋 After installation, you can use agents with:")
            print("   • kiro-cli chat --agent <agent_name>")
            print("   • Or through the Kiro IDE interface")
        else:
            print(f"✅ {provider_manager.get_provider_display_name()} is available and ready for use")
    
    # Initialize enhanced agent source classifier with network handling
    classifier = EnhancedAgentSourceClassifier()
    offline_manager = OfflineInstallationManager()
    
    # Check network connectivity upfront
    network_available = classifier.network_handler.check_network_connectivity()
    if not network_available:
        print("⚠️  Network connectivity issues detected")
        print("   Installation will proceed but URL-based agents may fail")
        print("   Offline alternatives will be provided for failed installations")
    
    # Determine which agents to install
    if agent_sources:
        # Install specific agent sources provided via command line
        agent_configs = []
        for source in agent_sources:
            source_type = classifier.classify_agent_source(source)
            
            # Determine agent name
            if source_type == AgentSourceType.BUILTIN:
                agent_name = source
            elif source_type == AgentSourceType.LOCAL_FILE:
                metadata = parse_agent_metadata(Path(source))
                agent_name = metadata.get('name', Path(source).stem)
            else:  # URL
                agent_name = Path(source).stem
            
            agent_configs.append(AgentInstallConfig(
                name=agent_name,
                source_type=source_type,
                source_path=source,
                provider=provider_manager.provider
            ))
    else:
        # Discover agents from project directory
        agent_configs = discover_and_classify_agents(project_dir, provider_manager.provider)
    
    if not agent_configs:
        print("❌ No agent configurations found")
        return False
    
    print(f"\n📋 Found {len(agent_configs)} agents to install:")
    print("=" * 60)
    
    # Separate network-dependent and offline agents
    url_agents = [config for config in agent_configs if config.source_type == AgentSourceType.URL]
    offline_agents = [config for config in agent_configs if config.source_type != AgentSourceType.URL]
    
    for i, config in enumerate(agent_configs, 1):
        print(f"{i}. Agent: {config.name}")
        print(f"   Source Type: {config.source_type.value}")
        print(f"   Source Path: {config.source_path}")
        print(f"   Target Provider: {provider_manager.get_provider_display_name()}")
        
        # Show network dependency warning
        if config.source_type == AgentSourceType.URL and not network_available:
            print("   ⚠️  Requires network connectivity (may fail)")
        
        # Display additional metadata if available
        if config.metadata and isinstance(config.metadata, dict):
            if 'description' in config.metadata:
                print(f"   Description: {config.metadata['description']}")
            if 'version' in config.metadata:
                print(f"   Version: {config.metadata['version']}")
            if 'author' in config.metadata:
                print(f"   Author: {config.metadata['author']}")
        
        print()  # Empty line between agents
    
    print("=" * 60)
    
    # Warn about network-dependent installations
    if url_agents and not network_available:
        print(f"\n⚠️  Warning: {len(url_agents)} agents require network connectivity")
        print("   These installations may fail. Offline alternatives will be provided.")
        
        response = input("Continue with installation? (Y/n): ")
        if response.lower() == 'n':
            return False
    
    # Ask user for confirmation unless specific sources were provided
    if not agent_sources:
        response = input(f"\nInstall all {len(agent_configs)} agents with {provider_manager.get_provider_display_name()}? (Y/n): ")
        if response.lower() == 'n':
            # Let user select specific agents
            selected_configs = []
            for config in agent_configs:
                response = input(f"Install {config.name}? (y/N): ")
                if response.lower() == 'y':
                    selected_configs.append(config)
            agent_configs = selected_configs
    
    if not agent_configs:
        print("No agents selected for installation.")
        return True
    
    # Install agents with enhanced error handling
    results = []
    failed_network_sources = []
    original_cwd = os.getcwd()
    
    try:
        os.chdir(project_dir)
        
        for config in agent_configs:
            print(f"\n📦 Installing agent: {config.name}")
            print(f"   Source: {config.source_path} ({config.source_type.value})")
            print(f"   Provider: {provider_manager.get_provider_display_name()}")
            
            # Use enhanced installation with network error handling
            result = classifier.handle_installation_with_fallback(config)
            
            if result.success:
                print(f"✅ Successfully installed agent: {config.name}")
            else:
                print(f"❌ Failed to install agent: {config.name}")
                if result.installation_method == 'network_error':
                    failed_network_sources.append(config.source_path)
                    print(f"🔌 Network error details:")
                    # Print error message with proper indentation
                    for line in result.error_message.split('\n'):
                        if line.strip():
                            print(f"   {line}")
                else:
                    print(f"   Error: {result.error_message}")
                
                # Try legacy method as fallback for non-network errors
                if result.installation_method != 'network_error':
                    print(f"🔄 Trying legacy installation method for {config.name}...")
                    legacy_success = install_agent_legacy(config, project_dir)
                    
                    if legacy_success:
                        result.success = True
                        result.installation_method = "legacy"
                        print(f"✅ Successfully installed agent using legacy method: {config.name}")
                    else:
                        print(f"❌ Legacy installation also failed for: {config.name}")
            
            results.append(result)
    
    finally:
        os.chdir(original_cwd)
    
    # Report results
    success_count = sum(1 for r in results if r.success)
    network_failures = sum(1 for r in results if r.installation_method == 'network_error')
    
    print(f"\n🎉 Successfully installed {success_count}/{len(results)} agents")
    
    if network_failures > 0:
        print(f"🔌 {network_failures} agents failed due to network issues")
        
        # Provide offline alternatives for network failures
        offline_manager.suggest_offline_installation(failed_network_sources)
    
    # Verify installations
    if success_count > 0:
        verify_installation_results(results, provider_manager)
    
    return success_count > 0


def discover_and_classify_agents(project_dir: Path, provider: str) -> List[AgentInstallConfig]:
    """
    Enhanced agent discovery that classifies agents by source type
    and prepares them for installation with appropriate providers.
    """
    agents = []
    agents_dir = project_dir / "agents"
    
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return []
    
    # Use recursive glob to find all .md files in agents directory and subdirectories
    for agent_file in agents_dir.glob("**/*.md"):
        try:
            metadata = parse_agent_metadata(agent_file)
            # metadata is now always a dict
            agent_name = metadata.get('name', agent_file.stem)
            
            # For now, treat all discovered agents as local files
            # In the future, we could check if they're available as built-ins
            agents.append(AgentInstallConfig(
                name=agent_name,
                source_type=AgentSourceType.LOCAL_FILE,
                source_path=str(agent_file.resolve()),
                provider=provider,
                metadata=metadata
            ))
        except Exception as e:
            print(f"⚠️  Warning: Could not process agent file {agent_file}: {e}")
    
    return agents


def install_agent_legacy(config: AgentInstallConfig, project_dir: Path) -> bool:
    """
    Legacy agent installation method for backward compatibility.
    """
    try:
        if config.source_type == AgentSourceType.LOCAL_FILE:
            # Try copying the file to agents directory
            agents_config_dir = project_dir / ".cao" / "agents"
            agents_config_dir.mkdir(parents=True, exist_ok=True)
            
            target_file = agents_config_dir / f"{config.name}.md"
            shutil.copy2(config.source_path, target_file)
            return True
        else:
            # For built-in and URL agents, try the old cao install command
            install_command = ["cao", "install", config.source_path]
            return run_command(install_command, check=False)
    except Exception:
        return False


def parse_agent_list_output(output: str) -> Dict[str, Dict[str, str]]:
    """
    Parse the output from 'cao list' command.
    
    Returns:
        Dict mapping agent names to their information (provider, etc.)
    """
    agents = {}
    if not output:
        return agents
    
    lines = output.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('No agents found') or line.startswith('Available agents'):
            continue
        
        # Try to parse different possible formats
        # Format 1: "agent_name (provider)"
        if '(' in line and ')' in line:
            parts = line.split('(')
            if len(parts) >= 2:
                agent_name = parts[0].strip()
                provider_part = parts[1].split(')')[0].strip()
                agents[agent_name] = {'provider': provider_part}
        # Format 2: Simple agent name per line
        else:
            agent_name = line.strip()
            if agent_name:
                agents[agent_name] = {'provider': 'unknown'}
    
    return agents


def verify_installation_results(results: List[InstallationResult], 
                               provider_manager: ProviderManager) -> None:
    """Enhanced verification using cao list command."""
    print("\n🔍 Installation Verification:")
    
    try:
        # Try to get list of installed agents from CAO
        output = run_command(["cao", "list"], capture_output=True, check=False)
        
        if output:
            print("✅ CAO list command successful")
            installed_agents = parse_agent_list_output(output)
            
            # Verify each installation result
            for result in results:
                if result.success:
                    # Strip agent name for comparison since parser strips names
                    agent_name_stripped = result.agent_name.strip()
                    if agent_name_stripped in installed_agents:
                        provider_info = installed_agents[agent_name_stripped]
                        provider_display = provider_info.get('provider', 'unknown')
                        print(f"✅ {result.agent_name} ({provider_display}) - Verified in agent list")
                    else:
                        print(f"⚠️  {result.agent_name} - Installation reported success but not found in agent list")
                        print(f"    This may be normal if the agent was installed using legacy methods")
                else:
                    error_msg = result.error_message or 'Installation failed'
                    print(f"❌ {result.agent_name} - {error_msg}")
            
            # Show summary of all installed agents
            if installed_agents:
                print(f"\n📋 All agents currently installed ({len(installed_agents)} total):")
                for agent_name, info in installed_agents.items():
                    provider_display = info.get('provider', 'unknown')
                    print(f"  • {agent_name} ({provider_display})")
        else:
            print("⚠️  Could not verify installations using 'cao list'")
            print("Falling back to file-based verification...")
            
            # Fallback verification by checking files
            for result in results:
                if result.success:
                    method_info = f" - {result.installation_method}" if result.installation_method else ""
                    print(f"✅ {result.agent_name} ({provider_manager.get_provider_display_name()}){method_info}")
                else:
                    error_msg = result.error_message or 'Installation failed'
                    print(f"❌ {result.agent_name} - {error_msg}")
                    
    except Exception as e:
        print(f"⚠️  Could not verify installations: {e}")
        
        # Simple success/failure report
        for result in results:
            status = "✅" if result.success else "❌"
            method_info = f" - {result.installation_method}" if result.installation_method else ""
            print(f"{status} {result.agent_name}{method_info}")


# Legacy install_agents function has been replaced by install_agents_v2
# which provides enhanced functionality with provider support and modern CAO commands


def setup_cao_environment(project_dir):
    """Set up CAO environment in the project directory."""
    print("⚙️  Setting up CAO environment in project...")
    
    # Change to project directory
    original_cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        
        # Initialize CAO in project directory
        print("🔧 Initializing CAO in project directory...")
        if not run_command(["cao", "init"], check=False):
            print("Note: CAO init may have failed, but this might be expected if already initialized")
        
        # Create .cao directory if it doesn't exist
        cao_config_dir = project_dir / ".cao"
        cao_config_dir.mkdir(exist_ok=True)
        
        print("✅ CAO environment setup complete")
        return True
        
    finally:
        os.chdir(original_cwd)


def main():
    parser = argparse.ArgumentParser(
        description="Install CLI Agent Orchestrator (CAO) and its dependencies"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip prerequisite validation (not recommended)"
    )
    
    args = parser.parse_args()
    
    # Initialize progress indicator
    total_steps = 3
    progress = ProgressIndicator(total_steps)
    
    try:
        # Check for problematic files in current directory
        import os
        current_dir_files = os.listdir('.')
        problematic_files = [f for f in current_dir_files if f in ['cao', 'tmux', 'uv', 'git']]
        if problematic_files:
            print(f"\n⚠️  Warning: Found files with command names in current directory: {', '.join(problematic_files)}")
            print("   These files may cause conflicts during installation.")
            print("   Consider renaming them or running the installer from a different directory.\n")
        
        # Enhanced prerequisite validation
        if not args.skip_validation:
            progress.start_step("Validating system prerequisites")
            validator = PrerequisiteValidator()
            
            if not validator.validate_all_prerequisites():
                progress.complete_step(True)
                print("\n❌ Critical prerequisites not met. Installation cannot continue.")
                print("Please resolve the issues above and try again.")
                sys.exit(1)
            
            progress.complete_step(True)
        
        # Step 1: Install dependencies
        progress.start_step("Installing system dependencies (tmux, uv, CAO)")
        if not install_dependencies():
            raise InstallationError(
                "Failed to install required dependencies",
                source="dependency_installation",
                error_type="installation_failure",
                suggestion="Check network connectivity and system permissions"
            )
        progress.complete_step(True)
        
        # Step 2: Verify CAO installation
        progress.start_step("Verifying CAO installation")
        if not verify_cao_installation():
            raise InstallationError(
                "CAO installation verification failed",
                source="cao_verification",
                error_type="verification_failure",
                suggestion="Try restarting your shell or adding uv tools to PATH"
            )
        progress.complete_step(True)
        
        # Show final summary
        progress.show_summary(progress.current_step)
        
        print(f"\n🎉 CAO installation complete!")
        
        print("\nNext steps:")
        print("1. Create a project using: python create_project.py <project_name>")
        print("2. Install agents using the install_agents.py script in your project")
        
        print("\nUseful commands:")
        print("• Start server: cao-server")
        print("• Install agent: cao install <agent_file> --provider <provider>")
        print("• Launch session: cao launch --agents <agent_name>")
        print("• List agents: cao list")
        print("• Get help: cao --help")
        
        print("\nNote: The CAO server must be running to launch agent sessions.")
        print("\nUninstall CAO (if needed):")
        print("• uv tool uninstall cli-agent-orchestrator")
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except InstallationError as e:
        print(f"\n❌ Installation failed: {e.get_formatted_message()}")
        sys.exit(1)
    except OSError as e:
        print(f"\n❌ File system error during installation: {str(e)}")
        if 'Not a directory' in str(e):
            print("💡 This error often occurs when there are files named after commands (cao, tmux, uv, git)")
            print("   in the current directory. Please check and rename any such files.")
        print("💡 Suggestion: Try running the installer from a different directory")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        if hasattr(e, 'errno'):
            print(f"   Error number: {e.errno}")
        print("💡 Suggestion: Check the error details above and try again")
        print("💡 If the error persists, try running from a different directory")
        sys.exit(1)


if __name__ == "__main__":
    main()