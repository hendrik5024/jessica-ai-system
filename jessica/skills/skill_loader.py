import importlib
import pkgutil
import os

def load_skills(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__))
    skills = []
    
    # Load skills from jessica/skills/
    for finder, name, ispkg in pkgutil.iter_modules([path]):
        if name == "skill_loader":
            continue
        try:
            module = importlib.import_module(f"jessica.skills.{name}")
            if hasattr(module, "can_handle") and hasattr(module, "run"):
                skills.append(module)
        except Exception as e:
            print(f"[skill_loader] Failed to load {name}: {e}")
    
    # Load vision skills from jessica/vision/
    try:
        from jessica.vision import screen_monitor
        if hasattr(screen_monitor, "can_handle") and hasattr(screen_monitor, "run"):
            skills.append(screen_monitor)
    except Exception as e:
        print(f"[skill_loader] Vision module unavailable: {e}")
    
    try:
        from jessica.vision import webcam_capture
        if hasattr(webcam_capture, "can_handle") and hasattr(webcam_capture, "run"):
            skills.append(webcam_capture)
    except Exception as e:
        print(f"[skill_loader] Webcam module unavailable: {e}")
    
    # Load automation skills from jessica/automation/
    try:
        from jessica.automation import spreadsheet_editor
        if hasattr(spreadsheet_editor, "can_handle") and hasattr(spreadsheet_editor, "run"):
            skills.append(spreadsheet_editor)
    except Exception as e:
        print(f"[skill_loader] Automation module unavailable: {e}")
    
    try:
        from jessica.automation import excel_live
        if hasattr(excel_live, "can_handle") and hasattr(excel_live, "run"):
            skills.append(excel_live)
    except Exception as e:
        print(f"[skill_loader] Excel live module unavailable: {e}")
    
    return skills
