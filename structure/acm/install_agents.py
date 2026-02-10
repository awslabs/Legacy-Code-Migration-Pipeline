#!/usr/bin/env python3
"""
Agent Installation Script

This script installs agents from the agents directory into CAO (CLI Agent Orchestrator).
It can be run standalone at any time to install or update agents.

Usage: python install_agents.py [--provider PROVIDER] [--agent-sources SOURCE ...]
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
from typing import Dict, List, Optional


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
    
    def get_error_message_for_invalid_provider(self) -> str:
        """Get error message for invalid provider with supported options."""
        supported = ', '.join(self.SUPPORTED_PROVIDERS)
        return (f"Invalid provider '{self.provider}'. "
                f"Supported providers: {supported}")


class AgentSourceClassifier:
    """Classifies agent sources and generates appropriate installation commands."""
    
    def classify_agent_source(self, agent_input: str) -> AgentSourceType:
        """Classify agent input as built-in, local file, or URL."""
        if agent_input.startswith(('http://', 'https://')):
            return AgentSourceType.URL
        
        if ('/' in agent_input or '\\' in agent_input or 
            agent_input.endswith('.md') or 
            Path(agent_input).exists()):
            return AgentSourceType.LOCAL_FILE
        
        return AgentSourceType.BUILTIN
    
    def get_installation_command(self, source_type: AgentSourceType, 
                                agent_input: str, provider: str) -> List[str]:
        """Generate appropriate cao install command."""
        base_cmd = ["cao", "install"]
        
        if source_type == AgentSourceType.BUILTIN:
            base_cmd.append(agent_input)
        elif source_type == AgentSourceType.LOCAL_FILE:
            try:
                abs_path = str(Path(agent_input).resolve())
                base_cmd.append(abs_path)
            except (OSError, ValueError):
                base_cmd.append(agent_input)
        elif source_type == AgentSourceType.URL:
            base_cmd.append(agent_input)
        
        base_cmd.extend(["--provider", provider])
        
        return base_cmd


def run_command(command, shell=False, check=True, capture_output=False):
    """Run a command and handle errors gracefully."""
    try:
        # Ensure uv tools are in PATH
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
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Command failed: {cmd_str}")
        
        if hasattr(e, 'returncode'):
            print(f"   Exit code: {e.returncode}")
        
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        
        return False
    except FileNotFoundError as e:
        cmd_name = command[0] if isinstance(command, list) else command
        print(f"❌ Command not found: {cmd_name}")
        return False
    except Exception as e:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Unexpected error running command: {cmd_str}")
        print(f"   Error: {str(e)}")
        return False


def check_command_exists(command):
    """Check if a command exists in the system PATH."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if command == "tmux":
        try:
            subprocess.run([command, "-V"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    if command == "cao":
        try:
            subprocess.run([command, "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
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
            os.environ["PATH"] = new_path
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    return False


def parse_agent_metadata(agent_file):
    """Parse the YAML frontmatter from an agent file to get the agent name and metadata."""
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1])
                    if isinstance(metadata, dict):
                        if 'name' in metadata:
                            metadata['name'] = str(metadata['name']) if metadata['name'] is not None else agent_file.stem
                        else:
                            metadata['name'] = agent_file.stem
                        return metadata
                    else:
                        for line in parts[1].split('\n'):
                            if line.strip().startswith('name:'):
                                name = line.split(':', 1)[1].strip().strip('"\'')
                                return {'name': name}
                except ImportError:
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            name = line.split(':', 1)[1].strip().strip('"\'')
                            return {'name': name}
                except Exception:
                    for line in parts[1].split('\n'):
                        if line.strip().startswith('name:'):
                            name = line.split(':', 1)[1].strip().strip('"\'')
                            return {'name': name}
        
        return {'name': agent_file.stem}
    
    except Exception as e:
        print(f"Warning: Could not parse metadata from {agent_file}: {e}")
        return {'name': agent_file.stem}


def discover_agents(agents_dir: Path, provider: str) -> List[AgentInstallConfig]:
    """Discover all agent files in the agents directory."""
    agents = []
    
    if not agents_dir.exists():
        print(f"❌ Agents directory not found: {agents_dir}")
        return []
    
    for agent_file in agents_dir.glob("**/*.md"):
        try:
            metadata = parse_agent_metadata(agent_file)
            agent_name = metadata.get('name', agent_file.stem)
            
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


def install_agent(config: AgentInstallConfig, classifier: AgentSourceClassifier) -> InstallationResult:
    """Install a single agent."""
    install_command = classifier.get_installation_command(
        config.source_type, config.source_path, config.provider
    )
    
    print(f"   🔧 Executing: {' '.join(install_command)}")
    
    success = run_command(install_command, check=False)
    
    if success:
        return InstallationResult(
            agent_name=config.name,
            success=True,
            provider=config.provider,
            installation_method="cao install"
        )
    else:
        return InstallationResult(
            agent_name=config.name,
            success=False,
            provider=config.provider,
            error_message="Installation command failed",
            installation_method="failed"
        )


def install_agents(agents_dir: Path, provider_manager: ProviderManager, 
                  agent_sources: Optional[List[str]] = None) -> bool:
    """Install agents from the agents directory or specified sources."""
    print("🤖 Installing agents...")
    print(f"🔧 Selected provider: {provider_manager.get_provider_display_name()}")
    
    # Check provider availability
    provider_available = provider_manager.check_provider_availability()
    config = provider_manager.get_provider_config()
    
    if not provider_available:
        print(f"⚠️  Provider {provider_manager.get_provider_display_name()} is not available on this system")
        if config and config.installation_notes:
            print(f"📝 Installation guidance: {config.installation_notes}")
    
    # Initialize classifier
    classifier = AgentSourceClassifier()
    
    # Determine which agents to install
    if agent_sources:
        agent_configs = []
        for source in agent_sources:
            source_type = classifier.classify_agent_source(source)
            
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
        agent_configs = discover_agents(agents_dir, provider_manager.provider)
    
    if not agent_configs:
        print("❌ No agents found to install")
        return False
    
    print(f"\n📋 Found {len(agent_configs)} agents to install:")
    print("=" * 60)
    
    for i, config in enumerate(agent_configs, 1):
        print(f"{i}. Agent: {config.name}")
        print(f"   Source Type: {config.source_type.value}")
        print(f"   Source Path: {config.source_path}")
        print(f"   Target Provider: {provider_manager.get_provider_display_name()}")
        
        if config.metadata and isinstance(config.metadata, dict):
            if 'description' in config.metadata:
                print(f"   Description: {config.metadata['description']}")
            if 'version' in config.metadata:
                print(f"   Version: {config.metadata['version']}")
        print()
    
    print("=" * 60)
    
    # Ask for confirmation unless specific sources were provided
    if not agent_sources:
        response = input(f"\nInstall all {len(agent_configs)} agents? (Y/n): ")
        if response.lower() == 'n':
            selected_configs = []
            for config in agent_configs:
                response = input(f"Install {config.name}? (y/N): ")
                if response.lower() == 'y':
                    selected_configs.append(config)
            agent_configs = selected_configs
    
    if not agent_configs:
        print("No agents selected for installation.")
        return True
    
    # Install agents
    results = []
    
    for config in agent_configs:
        print(f"\n📦 Installing agent: {config.name}")
        print(f"   Source: {config.source_path} ({config.source_type.value})")
        print(f"   Provider: {provider_manager.get_provider_display_name()}")
        
        result = install_agent(config, classifier)
        
        if result.success:
            print(f"✅ Successfully installed agent: {config.name}")
        else:
            print(f"❌ Failed to install agent: {config.name}")
            if result.error_message:
                print(f"   Error: {result.error_message}")
        
        results.append(result)
    
    # Report results
    success_count = sum(1 for r in results if r.success)
    
    print(f"\n🎉 Successfully installed {success_count}/{len(results)} agents")
    
    return success_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="Install or update agents for CLI Agent Orchestrator (CAO)"
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        help="Path to agents directory (default: ./agents or ../agents)"
    )
    parser.add_argument(
        "--provider",
        default="kiro_cli",
        choices=['kiro_cli', 'q_cli', 'claude_code'],
        help="CLI provider for agent integration (default: kiro_cli)"
    )
    parser.add_argument(
        "--agent-sources",
        nargs='*',
        help="Specific agent sources to install (built-in names, file paths, or URLs)"
    )
    
    args = parser.parse_args()
    
    try:
        # Determine agents directory
        if args.agents_dir:
            agents_dir = args.agents_dir.resolve()
        else:
            # Try ./agents first, then ../agents
            current_dir = Path.cwd()
            if (current_dir / "agents").exists():
                agents_dir = current_dir / "agents"
            elif (current_dir.parent / "agents").exists():
                agents_dir = current_dir.parent / "agents"
            else:
                agents_dir = current_dir / "agents"
        
        print(f"📁 Using agents directory: {agents_dir}")
        
        # Check if CAO is installed
        if not check_command_exists("cao"):
            print("❌ CAO (CLI Agent Orchestrator) is not installed")
            print("Please install CAO first using install_cao.py")
            sys.exit(1)
        
        # Initialize provider manager
        provider_manager = ProviderManager(args.provider)
        
        if not provider_manager.validate_provider():
            print(provider_manager.get_error_message_for_invalid_provider())
            sys.exit(1)
        
        # Install agents
        success = install_agents(agents_dir, provider_manager, args.agent_sources)
        
        if success:
            print("\n✅ Agent installation complete!")
            print(f"🔧 Provider: {provider_manager.get_provider_display_name()}")
            print("\nUseful commands:")
            print("• List agents: cao list")
            print("• Launch agent: cao launch --agents <agent_name>")
            print("• Get help: cao --help")
        else:
            print("\n⚠️  Agent installation completed with issues")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
