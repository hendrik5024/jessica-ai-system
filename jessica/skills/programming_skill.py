"""
Enhanced Programming Skill for Jessica
Integrates code generation, file management, dependency handling, and project awareness
"""

import os
import sys
import ast
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from jessica.automation.vscode_bridge import enqueue_task as vscode_enqueue_task
from jessica.skills.package_manager import PackageManager
from jessica.skills.model_downloader import ModelDownloader


def can_handle(intent: Dict[str, Any]) -> bool:
    """Handle programming-related intents."""
    intent_type = intent.get("intent", "").lower()
    text = intent.get("text", "").lower()
    
    # Match various programming keywords
    programming_keywords = [
        "code", "write", "create", "generate", "implement", "function",
        "class", "module", "script", "app", "application", "api", "project",
        "build", "develop", "fix", "debug", "refactor", "improve", "optimize",
        "install", "dependency", "package", "requirements", "python", "setup",
        "model", "download", "huggingface", "transformer", "llm", "neural"
    ]
    
    if intent_type in ["code", "programming", "development"]:
        return True
    
    for keyword in programming_keywords:
        if keyword in text:
            return True
    
    return False


def run(intent: Dict[str, Any], context: Any, relevant: List, manager: Any) -> Dict[str, Any]:
    """Execute programming task."""
    text = intent.get("text", "")
    
    # Initialize package manager
    pkg_mgr = PackageManager()
    model_downloader = ModelDownloader()
    
    # Route to appropriate handler
    if any(word in text.lower() for word in ["install", "dependency", "package", "requirements"]):
        return handle_dependency_request(text, pkg_mgr, manager)
    
    elif any(word in text.lower() for word in ["model", "download", "huggingface", "transformer"]):
        return handle_model_request(text, model_downloader, pkg_mgr, manager)
    
    elif any(word in text.lower() for word in ["openai", "anthropic", "huggingface", "api", "resource"]):
        return handle_api_resource_request(text, pkg_mgr)
    
    elif any(word in text.lower() for word in ["create file", "write file", "generate file", "new file"]):
        return handle_file_creation(text, manager, pkg_mgr)
    
    elif any(word in text.lower() for word in ["project", "workspace", "structure", "analyze"]):
        return handle_project_analysis(text, manager)
    
    else:
        return handle_code_generation(text, manager, pkg_mgr)


def handle_dependency_request(text: str, pkg_mgr: PackageManager, manager: Any) -> Dict[str, Any]:
    """Handle installation and dependency requests."""
    
    # Check if asking to install something
    if "install" in text.lower():
        # Extract package name
        parts = text.lower().split("install")
        if len(parts) > 1:
            package = parts[1].strip().split()[0]
            return {
                "type": "installation",
                "package": package,
                **pkg_mgr.install_package(package)
            }
    
    # Check if asking for suggestions
    if "suggest" in text.lower() or "recommend" in text.lower():
        # Try to extract use case
        for keyword in ["for", "to", "with"]:
            if keyword in text.lower():
                use_case = text.lower().split(keyword, 1)[1].strip()
                suggestions = pkg_mgr.suggest_installation(use_case)
                return {
                    "type": "suggestions",
                    **suggestions,
                    "installed": [pkg for pkg in suggestions["suggestions"] if pkg_mgr.is_installed(pkg)],
                    "not_installed": [pkg for pkg in suggestions["suggestions"] if not pkg_mgr.is_installed(pkg)],
                }
    
    # List optional dependencies
    optional = pkg_mgr.check_optional_dependencies()
    return {
        "type": "optional_dependencies",
        "available": {pkg: status for pkg, status in optional.items() if status},
        "missing": {pkg: status for pkg, status in optional.items() if not status},
        "message": "Jessica's optional capabilities status. Install missing packages as needed.",
    }


def handle_api_resource_request(text: str, pkg_mgr: PackageManager) -> Dict[str, Any]:
    """Handle API resource setup requests (OpenAI, etc.)."""
    
    # Identify which API resource
    for resource in ["openai", "anthropic", "huggingface", "github", "google", "aws", "azure"]:
        if resource.lower() in text.lower():
            resource_info = pkg_mgr.get_api_resource_info(resource)
            return {
                "type": "api_resource",
                "resource": resource,
                "url": resource_info.get("info", {}).get("url"),
                "auth": resource_info.get("info", {}).get("auth"),
                "setup_steps": resource_info.get("setup_steps"),
                "capabilities": resource_info.get("info", {}).get("capabilities") or 
                               resource_info.get("info", {}).get("services"),
            }
    
    return {
        "type": "api_resources",
        "available": list(pkg_mgr.API_RESOURCES.keys()),
        "message": "Available API resources. Ask about setup for any of them.",
    }


def handle_model_request(
    text: str,
    downloader: ModelDownloader,
    pkg_mgr: PackageManager,
    manager: Any
) -> Dict[str, Any]:
    """Handle model download and ML framework requests - Jessica can do this autonomously!"""
    
    # Check for autonomous download requirement
    # Examples: "I need a text generation model", "Download whisper", "Get Llama-2"
    
    # First, try to understand what model/task Jessica needs
    suggestion_result = downloader.suggest_model_for_task(text)
    
    if not suggestion_result.get("ok"):
        return suggestion_result
    
    recommended = suggestion_result.get("recommended", {})
    model_id = recommended.get("model")
    reason = recommended.get("reason")
    
    if not model_id:
        return {
            "ok": False,
            "error": "Could not identify model to download",
            "text": text
        }
    
    # Jessica autonomously downloads without explicit permission!
    # (She can do this because it's just downloading public models)
    print(f"🤖 Jessica autonomously downloading: {model_id}")
    print(f"   Reason: {reason}")
    
    # Check if already cached
    status = downloader.get_download_status(model_id)
    if status.get("cached"):
        return {
            "ok": True,
            "model_id": model_id,
            "already_cached": True,
            "cache_path": status.get("cache_path"),
            "ready_to_use": True,
            "message": f"Model {model_id} is already available locally. Ready to use!",
            "auto_downloaded": False
        }
    
    # Actually download the model
    download_result = downloader.download_model(model_id, "huggingface")
    
    if download_result.get("ok"):
        return {
            "ok": True,
            "model_id": model_id,
            "auto_downloaded": True,
            "ready_to_use": True,
            "cache_path": download_result.get("cache_dir"),
            "import_code": download_result.get("import_code"),
            "message": f"✅ Jessica autonomously downloaded {model_id}. Ready to use!",
            "next_steps": f"Use this import: {download_result.get('import_code')}"
        }
    else:
        return {
            "ok": False,
            "error": download_result.get("error"),
            "model_id": model_id,
            "manual_url": f"https://huggingface.co/{model_id}",
            "suggestion": download_result.get("suggestion"),
            "message": f"Could not auto-download. Check error or visit {download_result.get('manual_download', 'https://huggingface.co')}"
        }


def handle_file_creation(text: str, manager: Any, pkg_mgr: PackageManager) -> Dict[str, Any]:
    """Handle file creation requests."""
    
    # Generate code
    prompt = f"""You are Jessica, an offline AI programming assistant.
Generate clean, well-commented, production-ready Python code for:
{text}

Requirements:
- Include docstrings for functions/classes
- Add error handling
- Include type hints
- Add helpful comments
- Make it immediately runnable

Code:"""
    
    code = manager.model_router.generate(prompt, mode="code")
    
    # Validate Python syntax
    try:
        ast.parse(code)
        syntax_valid = True
    except SyntaxError as e:
        syntax_valid = False
        code += f"\n# Syntax error: {e}"
    
    # Extract suggested filename
    filename = extract_filename_suggestion(text)
    if not filename:
        filename = "generated_script.py"
    
    # Enqueue VS Code task to create file
    task = {
        "type": "vscode.create_file",
        "path": os.path.join(os.getcwd(), filename),
        "content": code,
    }
    result = vscode_enqueue_task(task)
    
    return {
        "type": "file_creation",
        "filename": filename,
        "syntax_valid": syntax_valid,
        "code_length": len(code),
        "created": result.get("ok", False),
        "message": f"Generated and {'created' if result.get('ok') else 'queued'} {filename}",
        "preview": code[:200] + "..." if len(code) > 200 else code,
    }


def handle_project_analysis(text: str, manager: Any) -> Dict[str, Any]:
    """Analyze current project structure and requirements."""
    
    root = os.getcwd()
    analysis = {
        "type": "project_analysis",
        "root": root,
        "files": [],
        "structure": {},
        "requirements": None,
        "py_files": [],
    }
    
    # Scan for Python files
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common ignore patterns
        dirnames[:] = [d for d in dirnames if d not in ['.git', '__pycache__', '.venv', 'node_modules']]
        
        for file in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, file), root)
            
            if file.endswith('.py'):
                analysis["py_files"].append(rel_path)
                analysis["files"].append(rel_path)
            elif file in ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']:
                analysis["files"].append(rel_path)
    
    # Read requirements if exists
    req_content = manager.package_manager.get_requirements_file(root) if hasattr(manager, 'package_manager') else None
    if req_content:
        analysis["requirements"] = req_content.split('\n')[:10]  # First 10 lines
    
    # Structure summary
    analysis["structure"] = {
        "python_files": len(analysis["py_files"]),
        "total_files": len(analysis["files"]),
        "has_requirements": req_content is not None,
    }
    
    return analysis


def handle_code_generation(text: str, manager: Any, pkg_mgr: PackageManager) -> Dict[str, Any]:
    """Handle general code generation requests."""
    
    # Build context
    optional_deps = pkg_mgr.check_optional_dependencies()
    available_packages = [pkg for pkg, available in optional_deps.items() if available]
    
    prompt = f"""You are Jessica, an offline AI programming assistant with full coding expertise.
Generate clean, production-ready Python code for:
{text}

Context:
- Available packages: {', '.join(available_packages)}
- Environment: Python {sys.version.split()[0]}
- Workspace: {os.getcwd()}

Requirements:
- Include docstrings
- Add type hints
- Handle errors gracefully
- Be production-ready
- Use available packages when beneficial

Code:"""
    
    code = manager.model_router.generate(prompt, mode="code")
    
    # Validate syntax
    try:
        ast.parse(code)
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False
    
    return {
        "type": "code_generation",
        "code": code,
        "syntax_valid": syntax_valid,
        "length": len(code),
        "available_packages": available_packages,
    }


def extract_filename_suggestion(text: str) -> Optional[str]:
    """Extract a filename suggestion from request text."""
    
    # Common patterns
    if "function" in text.lower():
        return "function_module.py"
    elif "class" in text.lower():
        return "class_module.py"
    elif "api" in text.lower() or "endpoint" in text.lower():
        return "api_server.py"
    elif "test" in text.lower():
        return "test_module.py"
    elif "script" in text.lower() or "automation" in text.lower():
        return "automation_script.py"
    elif "web" in text.lower():
        return "web_app.py"
    elif "cli" in text.lower() or "command" in text.lower():
        return "cli_tool.py"
    else:
        return None
