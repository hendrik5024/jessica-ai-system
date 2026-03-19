# Future Capabilities Roadmap

## Vision & Screen Monitoring
**Status:** Infrastructure ready, dependencies optional

Jessica can monitor your screen activity with explicit permission to provide context-aware assistance.

### Features
- Screenshot capture (local only, no cloud)
- OCR text extraction from screen
- Context understanding: "What am I working on?"
- Application/window detection

### Dependencies
```bash
pip install Pillow pytesseract
# Windows: install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
```

### Usage Examples
- "Take a screenshot and tell me what you see"
- "What am I currently working on?"
- "Help me with what's on my screen"

### Privacy Notes
- All processing happens locally (fully offline)
- Screenshots are stored in `jessica/data/screenshots/`
- User approval required before each capture
- No data leaves your machine

---

## Spreadsheet Automation
**Status:** Infrastructure ready, dependencies optional

Jessica can read, analyze, and edit Excel/CSV files with your approval.

### Features
- Read CSV and Excel (.xlsx) files
- Write/update spreadsheet data
- Data analysis and summarization
- Automated data entry
- Formula suggestions

### Dependencies
```bash
pip install openpyxl pandas
```

### Usage Examples
- "Read the CSV at data.csv and summarize it"
- "Add a row to my Excel spreadsheet"
- "Update cell B5 in budget.xlsx to 1500"
- "Create a new CSV with these columns: name, email, date"

### Safety Features
- User approval required for all read/write operations
- Preview of changes before committing
- Backup recommendations for important files
- Read-only mode by default

---

## Activation Instructions

### Enable Vision
1. Install dependencies: `pip install Pillow pytesseract`
2. For OCR: Install Tesseract OCR binary
3. Test: Ask Jessica "Can you see my screen?"

### Enable Spreadsheet Automation
1. Install dependencies: `pip install openpyxl pandas`
2. Test: Ask Jessica "Can you help with spreadsheets?"

### Configure BDI Desires
Edit `jessica/data/desire_state.json` to adjust how aggressively Jessica offers these features:

```json
{
  "desires": [
    "Proactively offer screen monitoring when the user seems stuck",
    "Suggest spreadsheet automation for repetitive data tasks"
  ]
}
```

---

## Development Roadmap

### Phase 1: Foundation (✓ Complete)
- [x] BDI architecture
- [x] Tool execution framework
- [x] User approval workflows
- [x] Vision module skeleton
- [x] Spreadsheet module skeleton

### Phase 2: Vision Capabilities (Next)
- [ ] Window/application detection
- [ ] Multi-monitor support
- [ ] Screenshot history/comparison
- [ ] Visual element recognition
- [ ] UI automation (read button labels, etc.)

### Phase 3: Spreadsheet Intelligence (Planned)
- [ ] Formula understanding
- [ ] Data validation
- [ ] Chart generation
- [ ] Pattern detection in data
- [ ] Automated reporting

### Phase 4: Advanced Automation (Future)
- [ ] Browser automation (web scraping, form filling)
- [ ] File system operations (organize, search, backup)
- [ ] Email automation
- [ ] Calendar integration
- [ ] Cross-application workflows

### Phase 5: Proactive Assistance (Vision)
- [ ] Context-aware suggestions
- [ ] Task interruption detection
- [ ] Work pattern learning
- [ ] Automated task triggering (with approval)

---

## Security & Privacy Principles

1. **Local-First:** All processing on your machine
2. **Approval-Required:** No autonomous actions
3. **Transparent:** Clear explanation of what Jessica will do
4. **Auditable:** Logs of all operations in `jessica/data/`
5. **Reversible:** Easy undo/restore mechanisms
6. **Sandboxed:** Limited to whitelisted operations
7. **User-Controlled:** Disable features anytime via config

---

## Contributing

To add new capabilities:
1. Create module in appropriate directory (`vision/`, `automation/`)
2. Implement `can_handle(intent)` and `run(intent, context, relevant, manager)`
3. Add approval workflow via `confirm_and_run()` or similar
4. Update `desire_state.json` with relevant beliefs/desires
5. Add intent keywords to `nlp/intent_parser.py`
6. Document in this file
7. Test with approval flow enabled

---

**Last Updated:** January 8, 2026
