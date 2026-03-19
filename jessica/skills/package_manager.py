"""
Package and Dependency Manager for Jessica
Helps Jessica understand, manage, and install Python packages and dependencies
"""

import subprocess
import sys
import json
import os
from typing import Dict, List, Any, Optional


class PackageManager:
    """Manage Python packages, dependencies, and installations."""
    
    COMMON_PACKAGES = {
        "requests": "HTTP library for API calls",
        "openai": "OpenAI API client",
        "anthropic": "Anthropic Claude API client",
        "flask": "Web framework",
        "django": "Full-featured web framework",
        "pandas": "Data analysis and manipulation",
        "numpy": "Numerical computing",
        "scipy": "Scientific computing",
        "matplotlib": "Data visualization",
        "seaborn": "Statistical data visualization",
        "scikit-learn": "Machine learning library",
        "tensorflow": "Deep learning framework",
        "torch": "PyTorch deep learning",
        "beautifulsoup4": "Web scraping",
        "selenium": "Browser automation",
        "pytest": "Testing framework",
        "black": "Code formatter",
        "pylint": "Code linter",
        "mypy": "Static type checker",
        "poetry": "Dependency management",
        "sqlalchemy": "ORM and SQL toolkit",
        "psycopg2": "PostgreSQL adapter",
        "pymongo": "MongoDB driver",
        "redis": "Redis client",
        "pillow": "Image processing",
        "pyyaml": "YAML parser",
        "toml": "TOML parser",
        "click": "CLI framework",
        "pydantic": "Data validation",
        "dotenv": "Environment variable management",
        "pynput": "Keyboard and mouse control",
        "pywin32": "Windows API access",
        "customtkinter": "Modern GUI framework",
        "streamlit": "Dashboard/app framework",
        "fastapi": "Modern API framework",
        "uvicorn": "ASGI server",
        "httpx": "Async HTTP client",
        "aiohttp": "Async HTTP client/server",
    }
    
    API_RESOURCES = {
        "openai": {
            "url": "https://platform.openai.com",
            "auth": "API key",
            "models": ["gpt-4", "gpt-3.5-turbo", "text-davinci-003"],
            "capabilities": ["chat", "completions", "embeddings", "images", "audio"],
        },
        "anthropic": {
            "url": "https://console.anthropic.com",
            "auth": "API key",
            "models": ["claude-3", "claude-2", "claude-instant"],
            "capabilities": ["chat", "completions"],
        },
        "huggingface": {
            "url": "https://huggingface.co",
            "auth": "API token",
            "resources": ["model hub", "datasets", "spaces"],
            "capabilities": ["inference", "fine-tuning"],
        },
        "github": {
            "url": "https://api.github.com",
            "auth": "Personal access token",
            "capabilities": ["repos", "issues", "pulls", "actions"],
        },
        "google": {
            "url": "https://cloud.google.com",
            "auth": "Service account key",
            "services": ["Cloud Functions", "Cloud Storage", "BigQuery", "Vertex AI"],
        },
        "aws": {
            "url": "https://aws.amazon.com",
            "auth": "Access key + secret",
            "services": ["Lambda", "S3", "EC2", "RDS", "SageMaker"],
        },
        "azure": {
            "url": "https://azure.microsoft.com",
            "auth": "Connection string / MSI",
            "services": ["Functions", "Blob Storage", "Cosmos DB", "Cognitive Services"],
        },
    }

    def __init__(self):
        self.installed_packages = self._get_installed_packages()

    def _get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages and their versions."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {pkg["name"]: pkg["version"] for pkg in packages}
        except Exception as e:
            print(f"[PackageManager] Error getting installed packages: {e}")
        return {}

    def is_installed(self, package_name: str) -> bool:
        """Check if a package is installed."""
        return package_name.lower() in {k.lower() for k in self.installed_packages.keys()}

    def get_version(self, package_name: str) -> Optional[str]:
        """Get installed version of a package."""
        for key, version in self.installed_packages.items():
            if key.lower() == package_name.lower():
                return version
        return None

    def suggest_installation(self, use_case: str) -> Dict[str, Any]:
        """Suggest packages based on use case."""
        suggestions = {
            "web scraping": ["beautifulsoup4", "selenium", "requests"],
            "data analysis": ["pandas", "numpy", "scipy", "matplotlib"],
            "machine learning": ["scikit-learn", "tensorflow", "torch"],
            "api client": ["requests", "httpx", "aiohttp"],
            "web framework": ["flask", "django", "fastapi"],
            "cli app": ["click", "typer", "argparse"],
            "testing": ["pytest", "unittest"],
            "code quality": ["black", "pylint", "mypy"],
            "database": ["sqlalchemy", "psycopg2", "pymongo"],
            "gui": ["customtkinter", "tkinter", "pyqt5"],
            "async": ["asyncio", "aiohttp", "httpx"],
        }
        
        matching = []
        for key in suggestions:
            if key.lower() in use_case.lower():
                matching.extend(suggestions[key])
        
        return {
            "use_case": use_case,
            "suggestions": list(set(matching)),  # Remove duplicates
            "descriptions": {pkg: self.COMMON_PACKAGES.get(pkg, "Package") for pkg in set(matching)},
        }

    def install_package(self, package_name: str, upgrade: bool = False) -> Dict[str, Any]:
        """Install a package."""
        if self.is_installed(package_name) and not upgrade:
            return {
                "ok": False,
                "message": f"{package_name} is already installed (v{self.get_version(package_name)})",
                "installed": True,
            }
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"]
            if upgrade:
                cmd.append("--upgrade")
            cmd.append(package_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.installed_packages = self._get_installed_packages()
                return {
                    "ok": True,
                    "message": f"Successfully installed {package_name}",
                    "package": package_name,
                    "version": self.get_version(package_name),
                }
            else:
                return {
                    "ok": False,
                    "message": f"Installation failed: {result.stderr}",
                    "error": result.stderr,
                }
        except subprocess.TimeoutExpired:
            return {"ok": False, "message": "Installation timed out"}
        except Exception as e:
            return {"ok": False, "message": f"Error: {str(e)}", "error": str(e)}

    def get_requirements_file(self, project_root: str = ".") -> Optional[str]:
        """Find and read requirements.txt or similar."""
        candidates = ["requirements.txt", "Pipfile", "pyproject.toml", "setup.py"]
        
        for filename in candidates:
            filepath = os.path.join(project_root, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    pass
        return None

    def generate_requirements(self) -> str:
        """Generate a requirements.txt from currently installed packages."""
        lines = []
        for pkg, version in sorted(self.installed_packages.items()):
            lines.append(f"{pkg}=={version}")
        return "\n".join(lines)

    def get_api_resource_info(self, resource: str) -> Dict[str, Any]:
        """Get information about an API resource (OpenAI, etc.)."""
        resource_lower = resource.lower()
        
        for key, info in self.API_RESOURCES.items():
            if key.lower() == resource_lower or key in resource_lower:
                return {
                    "name": key,
                    "info": info,
                    "setup_steps": self._get_setup_steps(key),
                }
        
        return {
            "name": resource,
            "info": None,
            "message": f"Unknown resource: {resource}. Available: {', '.join(self.API_RESOURCES.keys())}",
        }

    def _get_setup_steps(self, resource: str) -> List[str]:
        """Get setup steps for a resource."""
        steps = {
            "openai": [
                "1. Visit https://platform.openai.com/account/api-keys",
                "2. Create a new API key",
                "3. Set OPENAI_API_KEY environment variable",
                "4. Install openai: pip install openai",
                "5. Import and use: from openai import OpenAI",
            ],
            "anthropic": [
                "1. Visit https://console.anthropic.com",
                "2. Create API key",
                "3. Set ANTHROPIC_API_KEY environment variable",
                "4. Install anthropic: pip install anthropic",
                "5. Import and use: from anthropic import Anthropic",
            ],
            "huggingface": [
                "1. Create account at https://huggingface.co",
                "2. Generate API token from account settings",
                "3. Set HF_TOKEN environment variable",
                "4. Install transformers: pip install transformers",
            ],
            "github": [
                "1. Go to https://github.com/settings/tokens",
                "2. Generate Personal Access Token",
                "3. Set GITHUB_TOKEN environment variable",
                "4. Install PyGithub: pip install PyGithub",
            ],
            "google": [
                "1. Create project in Google Cloud Console",
                "2. Download service account key (JSON)",
                "3. Set GOOGLE_APPLICATION_CREDENTIALS env var",
                "4. Install google-cloud libraries as needed",
            ],
            "aws": [
                "1. Create AWS account and IAM user",
                "2. Generate access keys",
                "3. Configure with aws configure or env vars",
                "4. Install boto3: pip install boto3",
            ],
            "azure": [
                "1. Create Azure account and resource",
                "2. Get connection string from Azure Portal",
                "3. Set AZURE_CONNECTION_STRING env var",
                "4. Install azure-sdk: pip install azure-storage-blob",
            ],
        }
        return steps.get(resource, ["Resource setup not documented"])

    def check_optional_dependencies(self) -> Dict[str, bool]:
        """Check which optional dependencies are available."""
        optional = {
            "pillow": "Image processing",
            "pynput": "Keyboard/mouse control",
            "pywin32": "Windows API",
            "customtkinter": "Modern GUI",
            "requests": "HTTP library",
            "openai": "OpenAI API",
            "selenium": "Browser automation",
            "beautifulsoup4": "Web scraping",
            "pandas": "Data analysis",
        }
        
        return {
            pkg: self.is_installed(pkg)
            for pkg in optional.keys()
        }
