"""
App Launcher Skill - Jessica can open applications.

Supports:
- Excel (empty spreadsheet)
- Word (empty document)
- Notepad
- Terminal (PowerShell)
- Outlook (email & calendar)
- And other Windows applications
"""
from typing import Dict, Any, List, Optional
import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger("jessica.app_skill")

# Safe app map with proper Windows paths
SAFE_APPS = {
    'excel': {
        'command': 'excel.exe',
        'description': 'Microsoft Excel (empty spreadsheet)',
        'windows_only': True
    },
    'word': {
        'command': 'winword.exe',
        'description': 'Microsoft Word (empty document)',
        'windows_only': True
    },
    'notepad': {
        'command': 'notepad.exe',
        'description': 'Notepad',
        'windows_only': True
    },
    'terminal': {
        'command': 'powershell.exe',
        'description': 'PowerShell',
        'windows_only': True
    },
    'cmd': {
        'command': 'cmd.exe',
        'description': 'Command Prompt',
        'windows_only': True
    },
    'calculator': {
        'command': 'calc.exe',
        'description': 'Calculator',
        'windows_only': True
    },
    'outlook': {
        'command': 'outlook.exe',
        'description': 'Microsoft Outlook (email & calendar)',
        'windows_only': True
    },
}


def _find_office_app(app_name: str) -> Optional[str]:
    """Locate Microsoft Office application via registry."""
    if sys.platform != 'win32':
        return None
    
    try:
        import winreg
    except ImportError:
        return None
    
    # Map app names to registry paths
    office_registry_paths = {
        'excel': [
            r'Software\Microsoft\Windows\CurrentVersion\App Paths\excel.exe',
        ],
        'word': [
            r'Software\Microsoft\Windows\CurrentVersion\App Paths\winword.exe',
            r'Software\Microsoft\Windows\CurrentVersion\App Paths\word.exe',
        ],
        'outlook': [
            r'Software\Microsoft\Windows\CurrentVersion\App Paths\outlook.exe',
        ]
    }
    
    paths_to_check = office_registry_paths.get(app_name, [])
    
    for reg_path in paths_to_check:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                path, _ = winreg.QueryValueEx(key, '')
                if Path(path).exists():
                    logger.info(f"Found {app_name} at {path} via registry")
                    return path
        except (FileNotFoundError, OSError):
            continue
    
    # Also check common Office installation paths
    common_paths = {
        'excel': [
            r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
            r'C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE',
            r'C:\Program Files\Microsoft Office\Office16\EXCEL.EXE',
            r'C:\Program Files (x86)\Microsoft Office\Office16\EXCEL.EXE',
        ],
        'word': [
            r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
            r'C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE',
            r'C:\Program Files\Microsoft Office\Office16\WINWORD.EXE',
            r'C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE',
        ],
        'outlook': [
            r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE',
            r'C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE',
            r'C:\Program Files\Microsoft Office\Office16\OUTLOOK.EXE',
            r'C:\Program Files (x86)\Microsoft Office\Office16\OUTLOOK.EXE',
        ]
    }
    
    for path_str in common_paths.get(app_name, []):
        if Path(path_str).exists():
            logger.info(f"Found {app_name} at {path_str} via file system")
            return path_str
    
    return None


def can_handle(intent: Dict[str, Any]) -> bool:
    """Check if this is an app opening request"""
    return intent.get('intent') == 'open_app'

def run(intent: Dict[str, Any], context: Dict[str, Any], relevant: List[Dict[str, Any]] = None, manager = None) -> Dict[str, Any]:
    """Open the requested application"""
    app = intent.get('app', '').lower().strip()
    
    if not app:
        available = '\n  - '.join([f"{k}: {v['description']}" for k, v in SAFE_APPS.items()])
        return {
            'error': 'No app specified',
            'available_apps': available,
            'examples': [
                'Open Excel',
                'Open Word',
                'Open Notepad',
                'Open Terminal'
            ]
        }
    
    # If app is in SAFE_APPS, use the predefined command
    if app in SAFE_APPS:
        app_config = SAFE_APPS[app]
        
        # Check platform
        if app_config.get('windows_only') and sys.platform != 'win32':
            return {
                'error': f'{app} is only available on Windows',
                'status': 'platform_incompatible'
            }
        
        # For Office apps, try registry first
        if app in ['excel', 'word', 'outlook']:
            full_path = _find_office_app(app)
            if full_path:
                try:
                    subprocess.Popen([full_path])
                    logger.info(f"Launched Office app: {app}")
                    return {
                        'status': 'launched',
                        'app': app,
                        'description': app_config['description'],
                        'message': f'Opening {app_config["description"]}...'
                    }
                except Exception as e:
                    logger.error(f"Failed to launch {app} via full path: {e}")
        
        # Try direct command (for system apps)
        try:
            subprocess.Popen([app_config['command']])
            logger.info(f"Launched application: {app}")
            return {
                'status': 'launched',
                'app': app,
                'description': app_config['description'],
                'message': f'Opening {app_config["description"]}...'
            }
        except FileNotFoundError as e:
            logger.warning(f"App {app} not found via direct command: {e}")
        except Exception as e:
            logger.error(f"Failed to launch {app}: {e}")
    
    # Free-form app launching: try PATH or shell association
    try:
        import shutil
        resolved = shutil.which(app)
        if resolved:
            subprocess.Popen([resolved])
            logger.info(f"Launched application via PATH: {app} -> {resolved}")
            return {
                'status': 'launched',
                'app': app,
                'message': f'Opening {app}...'
            }
        
        # Fallback: use Windows 'start' to open via shell associations
        if sys.platform == 'win32':
            subprocess.Popen(["cmd", "/c", "start", "", app], shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
            logger.info(f"Launched application via shell start: {app}")
            return {
                'status': 'launched',
                'app': app,
                'message': f'Opening {app}...'
            }
        
        # Last resort: try direct Popen
        subprocess.Popen([app])
        logger.info(f"Launched application directly: {app}")
        return {
            'status': 'launched',
            'app': app,
            'message': f'Opening {app}...'
        }
    except FileNotFoundError:
        return {
            'error': f'{app} not found on system',
            'status': 'app_not_found',
            'app': app
        }
    except Exception as e:
        logger.error(f"Failed to launch {app}: {e}")
        return {
            'error': f'Failed to launch {app}: {str(e)}',
            'status': 'launch_failed',
            'app': app
        }

def get_available_apps() -> Dict[str, str]:
    """Return list of available apps and descriptions"""
    return {app: config['description'] for app, config in SAFE_APPS.items()}
