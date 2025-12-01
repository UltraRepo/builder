#!/usr/bin/env python3
"""
VENV Manager for Repository Schema Generator

Provides utilities for detecting, validating, and managing Python virtual environments
for the reposchema application.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VENVManager:
    """Manages Python virtual environment detection and validation"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.venv_path = self.project_root / "venv"
        self.required_packages = [
            'rdflib',
            'pathspec',
            'fastapi',
            'uvicorn',
            'pydantic'
        ]

    def is_venv_active(self) -> bool:
        """Check if currently running in a virtual environment"""
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

    def get_venv_python_path(self) -> Optional[Path]:
        """Get the path to Python executable in the VENV"""
        if self.venv_path.exists():
            if sys.platform == "win32":
                python_path = self.venv_path / "Scripts" / "python.exe"
            else:
                python_path = self.venv_path / "bin" / "python"
            return python_path if python_path.exists() else None
        return None

    def check_required_packages(self, python_path: Optional[str] = None) -> Dict[str, bool]:
        """Check if required packages are installed"""
        python_cmd = python_path or sys.executable
        results = {}

        for package in self.required_packages:
            try:
                result = subprocess.run(
                    [python_cmd, "-c", f"import {package}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                results[package] = result.returncode == 0
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                results[package] = False
                logger.warning(f"Failed to check package: {package}")

        return results

    def validate_environment(self) -> Dict[str, Any]:
        """Comprehensive environment validation"""
        validation = {
            "venv_active": self.is_venv_active(),
            "venv_exists": self.venv_path.exists(),
            "python_path": None,
            "packages_status": {},
            "recommendations": []
        }

        # Check VENV status
        if not validation["venv_active"]:
            validation["recommendations"].append(
                "Not running in virtual environment. Consider activating VENV."
            )

        # Check VENV existence
        if not validation["venv_exists"]:
            validation["recommendations"].append(
                f"VENV not found at {self.venv_path}. Run setup script."
            )

        # Get Python path
        python_path = self.get_venv_python_path()
        if python_path:
            validation["python_path"] = str(python_path)
        else:
            validation["recommendations"].append(
                "Could not locate Python executable in VENV."
            )

        # Check packages
        validation["packages_status"] = self.check_required_packages(
            str(python_path) if python_path else None
        )

        missing_packages = [
            pkg for pkg, installed in validation["packages_status"].items()
            if not installed
        ]

        if missing_packages:
            validation["recommendations"].append(
                f"Missing packages: {', '.join(missing_packages)}. Run: pip install -r requirements.txt"
            )

        return validation

    def get_activation_command(self) -> Optional[str]:
        """Get the command to activate the VENV"""
        if not self.venv_path.exists():
            return None

        if sys.platform == "win32":
            return f"{self.venv_path}\\Scripts\\activate"
        else:
            return f"source {self.venv_path}/bin/activate"

    def suggest_setup_steps(self) -> list[str]:
        """Provide setup steps for VENV issues"""
        steps = []

        if not self.venv_path.exists():
            steps.extend([
                f"cd {self.project_root}",
                "python3 -m venv venv",
                self.get_activation_command() or "source venv/bin/activate",
                "pip install -r requirements.txt"
            ])

        validation = self.validate_environment()
        steps.extend(validation.get("recommendations", []))

        return steps

def main():
    """CLI interface for VENV management"""
    import argparse

    parser = argparse.ArgumentParser(description="VENV Manager for Repository Schema")
    parser.add_argument("--check", action="store_true", help="Check VENV status")
    parser.add_argument("--setup-steps", action="store_true", help="Show setup steps")
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    manager = VENVManager(args.project_root)

    if args.check:
        validation = manager.validate_environment()
        print("VENV Validation Results:")
        print(f"  VENV Active: {validation['venv_active']}")
        print(f"  VENV Exists: {validation['venv_exists']}")
        print(f"  Python Path: {validation['python_path']}")

        print("\nPackage Status:")
        for pkg, status in validation['packages_status'].items():
            print(f"  {pkg}: {'✓' if status else '✗'}")

        if validation['recommendations']:
            print("\nRecommendations:")
            for rec in validation['recommendations']:
                print(f"  - {rec}")

    elif args.setup_steps:
        steps = manager.suggest_setup_steps()
        print("Setup Steps:")
        for i, step in enumerate(steps, 1):
            print(f"{i}. {step}")

    else:
        print("Use --check or --setup-steps")

if __name__ == "__main__":
    main()