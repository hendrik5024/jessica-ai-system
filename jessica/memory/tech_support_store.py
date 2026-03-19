"""
Tech Support Store: Software shortcuts, coding principles, online safety, digital troubleshooting.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TECH_SUPPORT_FILE = os.path.join(DATA_DIR, "tech_support.json")


class TechSupportStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(TECH_SUPPORT_FILE):
            with open(TECH_SUPPORT_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_knowledge()
            self.save()

    def _get_starter_knowledge(self):
        return {
            "keyboard_shortcuts": {
                "Windows": {
                    "General": {
                        "Win + D": "Show/hide desktop",
                        "Win + L": "Lock computer",
                        "Win + E": "Open File Explorer",
                        "Win + I": "Open Settings",
                        "Win + V": "Clipboard history (enable first in settings)",
                        "Alt + Tab": "Switch between open apps",
                        "Win + Shift + S": "Screenshot tool (Snipping Tool)",
                        "Ctrl + Shift + Esc": "Open Task Manager"
                    },
                    "Text Editing": {
                        "Ctrl + Z / Ctrl + Y": "Undo / Redo",
                        "Ctrl + F": "Find text",
                        "Ctrl + A": "Select all",
                        "Ctrl + Home / End": "Jump to start/end of document",
                        "Shift + Arrow keys": "Select text",
                        "Ctrl + Backspace": "Delete entire word"
                    },
                    "Browser": {
                        "Ctrl + T": "New tab",
                        "Ctrl + W": "Close tab",
                        "Ctrl + Shift + T": "Reopen closed tab",
                        "Ctrl + Tab": "Switch tabs",
                        "Ctrl + L": "Highlight address bar",
                        "Ctrl + Shift + N": "Incognito/private window"
                    }
                },
                "VS Code / IDEs": {
                    "Ctrl + P": "Quick file open",
                    "Ctrl + Shift + P": "Command palette",
                    "Ctrl + /": "Toggle comment",
                    "Alt + Up/Down": "Move line up/down",
                    "Ctrl + D": "Select next occurrence (multi-cursor)",
                    "F2": "Rename symbol",
                    "Ctrl + Space": "Trigger autocomplete",
                    "Ctrl + `": "Toggle terminal"
                }
            },
            "coding_principles": [
                {
                    "principle": "DRY (Don't Repeat Yourself)",
                    "description": "Avoid duplicating code—extract repeated logic into functions/classes",
                    "example": "Instead of writing the same validation 5 times, create a validate() function and call it 5 times",
                    "benefit": "Easier to maintain—fix bugs in one place, not everywhere"
                },
                {
                    "principle": "KISS (Keep It Simple, Stupid)",
                    "description": "Simple solutions are better than clever ones",
                    "example": "If you can solve it in 5 lines instead of 50, do that. Future you will thank you.",
                    "benefit": "Easier to debug, test, and understand"
                },
                {
                    "principle": "YAGNI (You Aren't Gonna Need It)",
                    "description": "Don't build features you 'might need later'—build what you need now",
                    "example": "Don't create a complex user role system if you only have one type of user today",
                    "benefit": "Saves time, reduces complexity, avoids over-engineering"
                },
                {
                    "principle": "Separation of Concerns",
                    "description": "Keep different responsibilities in different places",
                    "example": "Database logic in one file, business logic in another, UI in a third. Don't mix them.",
                    "benefit": "Changes to UI don't break database code. Easier to test and maintain."
                },
                {
                    "principle": "Readable Code > Clever Code",
                    "description": "Code is read 10x more than it's written. Prioritize clarity.",
                    "example": "Use descriptive variable names (user_age vs. x). Add comments for WHY, not WHAT.",
                    "benefit": "Other devs (and future you) can understand it quickly"
                }
            ],
            "online_safety": [
                {
                    "topic": "Password Security",
                    "best_practices": [
                        "Use a password manager (Bitwarden, 1Password, LastPass) to generate unique passwords",
                        "Enable two-factor authentication (2FA) everywhere possible",
                        "Use passkeys when available (newer, more secure than passwords)",
                        "Never reuse passwords across sites—one breach compromises everything",
                        "12+ characters with mix of letters, numbers, symbols (or 4+ random words)"
                    ],
                    "red_flags": [
                        "Email asking you to 'verify your password' (phishing)",
                        "Any site that emails you your password in plain text (they're storing it wrong)",
                        "Security questions with public info (mother's maiden name)—lie on these"
                    ]
                },
                {
                    "topic": "Phishing & Scams",
                    "how_to_spot": [
                        "Urgent language ('Your account will be closed!')",
                        "Suspicious sender email (amaz0n.com vs. amazon.com)",
                        "Requests for passwords, credit cards, or personal info",
                        "Links that don't match the supposed sender (hover to preview URL)",
                        "Grammar/spelling errors in 'official' emails"
                    ],
                    "what_to_do": [
                        "Don't click links—go directly to the site by typing URL",
                        "Call the company using a number YOU looked up, not one in the email",
                        "Report phishing to your email provider",
                        "Use Have I Been Pwned (haveibeenpwned.com) to check if your email/password leaked"
                    ]
                },
                {
                    "topic": "Public Wi-Fi Safety",
                    "risks": "Hackers can intercept data on public Wi-Fi (coffee shops, airports)",
                    "how_to_stay_safe": [
                        "Use a VPN (encrypts your traffic)—NordVPN, Mullvad, ProtonVPN",
                        "Avoid logging into banking/sensitive accounts on public Wi-Fi",
                        "Turn off file sharing and AirDrop",
                        "Use HTTPS sites only (look for lock icon in address bar)",
                        "Forget the network after use (don't auto-connect)"
                    ]
                },
                {
                    "topic": "Social Media Privacy",
                    "tips": [
                        "Review privacy settings—most platforms default to 'public'",
                        "Limit who can see your posts, friends list, email, phone",
                        "Be cautious with location tagging (burglar's paradise)",
                        "Google yourself periodically to see what's public",
                        "Don't overshare (address, routine, vacation dates while away)"
                    ]
                },
                {
                    "topic": "Software Updates",
                    "why_they_matter": "Updates patch security vulnerabilities that hackers exploit",
                    "best_practice": [
                        "Enable automatic updates for OS, browsers, and apps",
                        "Update immediately for security patches (not just feature updates)",
                        "Don't ignore update notifications—they're not just annoying, they're critical"
                    ]
                }
            ],
            "troubleshooting": [
                {
                    "problem": "Computer running slow",
                    "solutions": [
                        "Restart (clears memory leaks)",
                        "Check Task Manager (Ctrl+Shift+Esc) for high CPU/memory apps—close them",
                        "Disable startup programs (Settings > Apps > Startup)",
                        "Run Disk Cleanup (search 'Disk Cleanup' in Windows)",
                        "Check for malware (Windows Defender or Malwarebytes)",
                        "Upgrade RAM if <8GB (most impactful hardware upgrade)"
                    ]
                },
                {
                    "problem": "Internet slow but Wi-Fi connected",
                    "solutions": [
                        "Restart router (unplug 30 seconds, plug back in)",
                        "Move closer to router or reduce obstacles",
                        "Check if others are streaming/downloading (bandwidth hogs)",
                        "Run speed test (fast.com or speedtest.net) to confirm issue",
                        "Restart computer/device",
                        "Check for ISP outages (downdetector.com)",
                        "Use Ethernet cable if possible (faster & more stable)"
                    ]
                },
                {
                    "problem": "App won't open or crashes",
                    "solutions": [
                        "Restart the app",
                        "Restart your computer (classic IT fix)",
                        "Update the app to latest version",
                        "Clear app cache (Settings > Apps > [App] > Clear cache)",
                        "Uninstall and reinstall",
                        "Check if your OS is up to date (old OS can break apps)"
                    ]
                },
                {
                    "problem": "Forgot password",
                    "solutions": [
                        "Use 'Forgot Password' link (check spam folder for reset email)",
                        "Check password manager if you use one",
                        "Try common variations you use",
                        "Contact support if critical account",
                        "Set up password manager NOW so this doesn't happen again"
                    ]
                }
            ],
            "productivity_tips": [
                "Learn 5 shortcuts per week—muscle memory compounds",
                "Use Ctrl+F (Find) obsessively—faster than scrolling",
                "Bookmark frequently visited sites (Ctrl+D)",
                "Close unused tabs/apps—they slow you down mentally and technically",
                "Use dual monitors or virtual desktops (Win+Tab) to organize workspace",
                "Search your computer (Win+S) instead of browsing folders",
                "Learn regex basics for power searching (developers)",
                "Automate repetitive tasks (Python scripts, keyboard macros, Zapier)"
            ]
        }

    def save(self):
        with open(TECH_SUPPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant tech support info."""
        query_lower = query.lower()
        results = []

        # Shortcuts
        if any(term in query_lower for term in ["shortcut", "hotkey", "key", "ctrl", "alt", "win"]):
            results.append({"type": "shortcuts", "data": self.data.get("keyboard_shortcuts", {})})

        # Coding principles
        if any(term in query_lower for term in ["code", "coding", "programming", "principle", "dry", "kiss", "yagni"]):
            results.extend([{"type": "coding_principle", "data": item} for item in self.data.get("coding_principles", [])])

        # Security/safety
        if any(term in query_lower for term in ["security", "safe", "password", "phishing", "scam", "wifi", "vpn", "privacy", "hack"]):
            results.extend([{"type": "safety", "data": item} for item in self.data.get("online_safety", [])])

        # Troubleshooting
        if any(term in query_lower for term in ["slow", "crash", "won't", "not working", "fix", "problem", "issue", "troubleshoot"]):
            results.extend([{"type": "troubleshooting", "data": item} for item in self.data.get("troubleshooting", [])])

        # Productivity
        if any(term in query_lower for term in ["productive", "efficient", "faster", "tip"]):
            results.append({"type": "productivity", "data": self.data.get("productivity_tips", [])})

        # If no match, show general tips
        if not results:
            results.append({"type": "productivity", "data": self.data.get("productivity_tips", [])})

        return results[:5]

    def format_response(self, results):
        """Format tech support info for display."""
        if not results:
            return "I don't have specific tech support info on that yet."

        output = []

        for result in results:
            if result["type"] == "shortcuts":
                shortcuts = result["data"]
                output.append("⌨️ **Keyboard Shortcuts:**\n")
                for os_name, categories in shortcuts.items():
                    output.append(f"**{os_name}:**")
                    for category, keys in categories.items():
                        output.append(f"  *{category}:*")
                        for shortcut, description in list(keys.items())[:5]:  # Limit to 5 per category
                            output.append(f"    • `{shortcut}` - {description}")
                    output.append("")

            elif result["type"] == "coding_principle":
                principle = result["data"]
                output.append(f"💻 **{principle['principle']}**")
                output.append(f"{principle['description']}\n")
                output.append(f"**Example:** {principle['example']}")
                output.append(f"**Benefit:** {principle['benefit']}\n")

            elif result["type"] == "safety":
                safety = result["data"]
                output.append(f"🔒 **{safety['topic']}**\n")

                if "best_practices" in safety:
                    output.append("**Best Practices:**")
                    for practice in safety["best_practices"]:
                        output.append(f"  ✅ {practice}")
                    output.append("")

                if "how_to_spot" in safety:
                    output.append("**How to Spot:**")
                    for sign in safety["how_to_spot"]:
                        output.append(f"  🚩 {sign}")
                    output.append("")

                if "what_to_do" in safety:
                    output.append("**What to Do:**")
                    for action in safety["what_to_do"]:
                        output.append(f"  • {action}")
                    output.append("")

                if "how_to_stay_safe" in safety:
                    output.append("**How to Stay Safe:**")
                    for tip in safety["how_to_stay_safe"]:
                        output.append(f"  • {tip}")
                    output.append("")

                if "tips" in safety:
                    output.append("**Tips:**")
                    for tip in safety["tips"]:
                        output.append(f"  • {tip}")
                    output.append("")

            elif result["type"] == "troubleshooting":
                problem = result["data"]
                output.append(f"🔧 **Problem: {problem['problem']}**\n")
                output.append("**Solutions:**")
                for solution in problem["solutions"]:
                    output.append(f"  • {solution}")
                output.append("")

            elif result["type"] == "productivity":
                tips = result["data"]
                output.append("⚡ **Productivity Tips:**")
                for tip in tips:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    store = TechSupportStore()
    results = store.search("keyboard shortcuts windows")
    print(store.format_response(results))
