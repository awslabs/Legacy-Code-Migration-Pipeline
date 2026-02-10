#!/usr/bin/env python3
"""
ACM Tools Installation Script

This script downloads and installs ACM tools from the AWS Code repository.
It can be run standalone or as part of the project creation process.

Features:
1. Downloads ACM tools from AWS Code repository (or uses local ZIP file)
2. Extracts to project's ./tools directory
3. Installs Python dependencies from requirements.txt
4. Gracefully handles private repository access issues

Usage: 
    python install_acm_tools.py [OPTIONS]
    
Options:
    --tools-dir PATH       Target directory for tools (default: ./tools)
    --zip-file PATH        Use existing ZIP file instead of downloading
    --skip-on-error        Skip installation if download fails (for automation)
"""

import os
import sys
import subprocess
import argparse
import shutil
import urllib.request
import urllib.error
import zipfile
import tempfile
from pathlib import Path
from typing import Optional


# ACM Tools repository configuration
ACM_TOOLS_URL = "https://code.aws.dev/personal_projects/alias_k/kerimman/acm-tools/-/archive/main/acm-tools-main.zip?ref_type=heads"
ACM_TOOLS_ARCHIVE_NAME = "acm-tools-main"


def print_header(message: str) -> None:
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def print_step(step_num: int, total_steps: int, message: str) -> None:
    """Print a formatted step message."""
    print(f"\n[{step_num}/{total_steps}] {message}")


def run_command(command, shell=False, check=True, capture_output=False, cwd=None):
    """Run a command and handle errors gracefully."""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=shell, 
                check=check,
                capture_output=True, 
                text=True,
                cwd=cwd
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check, cwd=cwd)
            return True
    except subprocess.CalledProcessError as e:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Command failed: {cmd_str}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command
        print(f"❌ Command not found: {cmd_name}")
        return False
    except Exception as e:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"❌ Unexpected error: {cmd_str}")
        print(f"   Error: {str(e)}")
        return False


def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    return shutil.which(command) is not None


def download_file(url: str, destination: Path) -> bool:
    """Download a file from URL to destination."""
    try:
        print(f"   Downloading from: {url}")
        print(f"   Destination: {destination}")
        
        # Create a request with headers
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ACM-Tools-Installer/1.0')
        
        # Download with progress indication
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = response.headers.get('Content-Length')
            
            if total_size:
                total_size = int(total_size)
                print(f"   Size: {total_size / 1024 / 1024:.2f} MB")
            
            with open(destination, 'wb') as f:
                downloaded = 0
                chunk_size = 8192
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
                
                if total_size:
                    print()  # New line after progress
        
        print("   ✅ Download complete")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        if e.code == 403:
            print("\n⚠️  Access Denied - This may be a private repository")
            print("   You may not have permission to access this repository.")
        elif e.code == 404:
            print("\n⚠️  Repository Not Found")
            print("   The repository may have been moved or deleted.")
        return False
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error: {e.reason}")
        print("\n⚠️  Network or DNS issue")
        print("   Check your internet connection and DNS settings.")
        return False
    except Exception as e:
        print(f"\n❌ Download failed: {str(e)}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> Optional[Path]:
    """Extract a zip file and return the path to the extracted directory."""
    try:
        print(f"   Extracting: {zip_path.name}")
        print(f"   Target: {extract_to}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the list of files
            file_list = zip_ref.namelist()
            print(f"   Files in archive: {len(file_list)}")
            
            # Extract all files
            zip_ref.extractall(extract_to)
        
        print("   ✅ Extraction complete")
        
        # Find the extracted directory (should be acm-tools-main)
        extracted_dirs = [d for d in extract_to.iterdir() if d.is_dir()]
        
        if extracted_dirs:
            return extracted_dirs[0]
        else:
            print("⚠️  Warning: No directory found in extracted archive")
            return extract_to
        
    except zipfile.BadZipFile:
        print("❌ Invalid or corrupted zip file")
        return None
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        return None


def install_requirements(requirements_file: Path) -> bool:
    """Install Python dependencies from requirements.txt."""
    if not requirements_file.exists():
        print(f"⚠️  No requirements.txt found at: {requirements_file}")
        print("   Skipping dependency installation")
        return True
    
    print(f"   Installing dependencies from: {requirements_file}")
    
    # Check if pip is available
    if not check_command_exists("pip3") and not check_command_exists("pip"):
        print("❌ pip is not installed")
        print("   Please install pip to install dependencies")
        return False
    
    pip_cmd = "pip3" if check_command_exists("pip3") else "pip"
    
    # Install dependencies
    success = run_command(
        [pip_cmd, "install", "-r", str(requirements_file)],
        check=False
    )
    
    if success:
        print("   ✅ Dependencies installed successfully")
    else:
        print("   ⚠️  Some dependencies may have failed to install")
        print("   You can retry manually: pip3 install -r", str(requirements_file))
    
    return success


def install_acm_tools(tools_dir: Path, zip_file: Optional[Path] = None, skip_on_error: bool = False) -> bool:
    """Main installation function for ACM tools."""
    print_header("ACM Tools Installation")
    
    print("Configuration:")
    print(f"  • Target directory: {tools_dir}")
    if zip_file:
        print(f"  • Using ZIP file: {zip_file}")
    else:
        print(f"  • Source URL: {ACM_TOOLS_URL}")
    print()
    
    # Create tools directory if it doesn't exist
    tools_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine ZIP file location
    if zip_file:
        # Use provided ZIP file
        if not zip_file.exists():
            print(f"❌ ZIP file not found: {zip_file}")
            return False
        
        print_step(1, 2, "Using provided ZIP file")
        print(f"   ZIP file: {zip_file}")
        zip_path = zip_file
        temp_dir_obj = None
    else:
        # Download ZIP file
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir_obj.name)
        zip_path = temp_path / "acm-tools.zip"
        
        print_step(1, 3, "Downloading ACM tools")
        if not download_file(ACM_TOOLS_URL, zip_path):
            print("\n❌ Failed to download ACM tools")
            print("\n" + "=" * 60)
            print("⚠️  ALTERNATIVE INSTALLATION METHODS")
            print("=" * 60)
            print("\n1. Manual Download:")
            print(f"   • Visit: {ACM_TOOLS_URL}")
            print("   • Download the ZIP file manually")
            print("   • Run: python3 install_acm_tools.py --zip-file /path/to/downloaded.zip")
            print("\n2. Request Access:")
            print("   • Contact the repository owner for access")
            print("   • The repository may be private or require authentication")
            print("\n3. Skip Installation (if optional):")
            print("   • Continue without ACM tools")
            print("   • Some features may not be available")
            print("\n" + "=" * 60)
            
            if temp_dir_obj:
                temp_dir_obj.cleanup()
            
            if skip_on_error:
                print("\n⚠️  Skipping ACM tools installation (--skip-on-error enabled)")
                return True  # Return success to continue workflow
            
            return False
    
    try:
        # Step 2: Extract
        step_num = 2 if zip_file else 2
        total_steps = 2 if zip_file else 3
        print_step(step_num, total_steps, "Extracting ACM tools")
        extracted_dir = extract_zip(zip_path, temp_path if not zip_file else zip_path.parent)
        
        if not extracted_dir:
            print("\n❌ Failed to extract ACM tools")
            if temp_dir_obj:
                temp_dir_obj.cleanup()
            return False
        
        # Move to target directory
        target_acm_dir = tools_dir / "acm-tools"
        
        # Remove existing directory if it exists
        if target_acm_dir.exists():
            print(f"   Removing existing directory: {target_acm_dir}")
            shutil.rmtree(target_acm_dir)
        
        print(f"   Moving to: {target_acm_dir}")
        shutil.move(str(extracted_dir), str(target_acm_dir))
        print("   ✅ ACM tools installed")
        
        # Step 3: Install dependencies
        step_num = 3 if not zip_file else 3
        total_steps = 3 if not zip_file else 2
        print_step(step_num, total_steps, "Installing dependencies")
        requirements_file = target_acm_dir / "requirements.txt"
        
        if not install_requirements(requirements_file):
            print("\n⚠️  Dependency installation had issues")
            print("   ACM tools are installed but may not work correctly")
            print("   Please install dependencies manually:")
            print(f"   pip3 install -r {requirements_file}")
            if temp_dir_obj:
                temp_dir_obj.cleanup()
            return False
        
        # Cleanup temporary directory
        if temp_dir_obj:
            temp_dir_obj.cleanup()
    
    except Exception as e:
        print(f"\n❌ Installation error: {str(e)}")
        if temp_dir_obj:
            temp_dir_obj.cleanup()
        return False
    
    # Success
    print_header("Installation Complete!")
    
    print("✅ ACM tools successfully installed")
    print()
    print("Installation Summary:")
    print(f"  • Location: {target_acm_dir}")
    print(f"  • Dependencies: Installed")
    if zip_file:
        print(f"  • Source: Local ZIP file")
    else:
        print(f"  • Source: Downloaded from AWS Code")
    print()
    print("Next Steps:")
    print("  • Explore tools: ls", str(target_acm_dir))
    print("  • Read documentation: cat", str(target_acm_dir / "README.md"))
    print()
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Install ACM tools from AWS Code repository or local ZIP file"
    )
    parser.add_argument(
        "--tools-dir",
        type=Path,
        default=Path("./tools"),
        help="Target directory for tools installation (default: ./tools)"
    )
    parser.add_argument(
        "--zip-file",
        type=Path,
        help="Use existing ZIP file instead of downloading (useful for private repos)"
    )
    parser.add_argument(
        "--skip-on-error",
        action="store_true",
        help="Skip installation if download fails (for automation scripts)"
    )
    
    args = parser.parse_args()
    
    try:
        # Resolve tools directory
        tools_dir = args.tools_dir.resolve()
        
        # Resolve ZIP file if provided
        zip_file = args.zip_file.resolve() if args.zip_file else None
        
        # Run installation
        success = install_acm_tools(tools_dir, zip_file, args.skip_on_error)
        
        if success:
            sys.exit(0)
        else:
            print("\n❌ Installation failed")
            if not args.skip_on_error:
                print("\nTip: Use --zip-file option if you have the ZIP file locally")
                print("Example: python3 install_acm_tools.py --zip-file /path/to/acm-tools.zip")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
