# Jessica App Launcher - Quick Start Guide

Jessica can now open applications with simple voice or text commands!

## Supported Applications

- **Excel** - Opens empty spreadsheet
- **Word** - Opens empty document  
- **Notepad** - Text editor
- **Terminal** - PowerShell
- **CMD** - Command Prompt
- **Calculator** - Windows calculator

## How to Use

### Voice Commands
```
"Jessica, open Excel"
"Jessica, open Word"
"Jessica, launch Notepad"
"Jessica, open Terminal"
"Jessica, open Calculator"
```

### Text Commands
Simply type in Jessica's chat:
```
Open Excel
Open Word
Launch Notepad
```

## How It Works

1. **Intent Recognition**: Jessica parses your command and recognizes it as an app-opening request
2. **Safety Check**: Only approved applications can be launched
3. **Execution**: The application is launched with `subprocess.Popen()`
4. **Confirmation**: Jessica confirms the app has been launched

## Technical Details

### Modified Files

**1. `jessica/skills/app_skill.py`** - Enhanced app launcher
- Support for Excel, Word, Notepad, Terminal, CMD, Calculator
- Better error handling and reporting
- `get_available_apps()` method to list all supported apps

**2. `jessica/nlp/intent_parser.py`** - Updated intent detection
- Added "open_app" intent type
- Distinguishes between opening apps vs files vs spreadsheets
- Checks for "open [app]" or "launch [app]" patterns

### Example Use Cases

**User**: "Open Excel for me"
```
Intent Parsed: open_app (app='excel')
│
└─> app_skill.can_handle() ✓
│
└─> app_skill.run()
    │
    └─> subprocess.Popen(['excel.exe'])
    │
    └─> Returns: {'status': 'launched', 'app': 'excel', ...}
│
Jessica: "Opening Microsoft Excel (empty spreadsheet)..."
```

**User**: "I need to write something"
```
Intent Parsed: open_app (app='notepad')
│
└─> app_skill.can_handle() ✓
│
└─> app_skill.run()
    │
    └─> subprocess.Popen(['notepad.exe'])
    │
    └─> Returns: {'status': 'launched', 'app': 'notepad', ...}
│
Jessica: "Opening Notepad..."
```

## Integration with Jessica

The app launcher is automatically integrated:
- ✅ Added to `skill_loader.py` (loads from jessica/skills/)
- ✅ Intent parser recognizes "open_app" intents
- ✅ Works with voice commands (Jessica wake word listener)
- ✅ Works with text commands

## Adding New Apps

To add support for more applications, edit `jessica/skills/app_skill.py`:

```python
SAFE_APPS = {
    'your_app': {
        'command': 'app_executable.exe',
        'description': 'Your App Description',
        'windows_only': True
    },
}
```

Then update the intent parser to recognize it:
```python
app_keywords = ["excel", "word", "your_app", ...]
```

## Safety & Permissions

- Only whitelisted apps in `SAFE_APPS` can be launched
- No shell execution (uses `subprocess.Popen` directly)
- All errors are caught and reported gracefully
- User approval via voice command is sufficient permission

## Testing

Test the functionality:
```python
from jessica.nlp.intent_parser import parse_intent
from jessica.skills import app_skill

# Test parsing
intent = parse_intent("Open Excel")
# Returns: {'intent': 'open_app', 'app': 'excel', ...}

# Test skill
result = app_skill.run({'intent': 'open_app', 'app': 'excel'}, {})
# Launches Excel (or would if desktop was available)
```

---

**Jessica App Launcher** - Now you can ask Jessica to open applications for you! 🚀
