"""
Digital Wellness Store: Media literacy, source verification, digital ethics, online safety.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DIGITAL_WELLNESS_FILE = os.path.join(DATA_DIR, "digital_wellness.json")


class DigitalWellnessStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(DIGITAL_WELLNESS_FILE):
            with open(DIGITAL_WELLNESS_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_knowledge()
            self.save()

    def _get_starter_knowledge(self):
        return {
            "media_literacy": {
                "principle": "Don't believe everything you read—verify sources and check for bias",
                "source_verification_checklist": [
                    {
                        "question": "Who is the author?",
                        "red_flags": ["No author listed", "Anonymous", "Unverifiable credentials"],
                        "green_flags": ["Named author with credentials", "Byline on reputable site", "Expert in the field"]
                    },
                    {
                        "question": "What is the source?",
                        "red_flags": ["Unknown website", "URL tries to mimic legitimate site (e.g., cnn.co vs cnn.com)", "Ends in .co, .biz, .info (often less credible)"],
                        "green_flags": ["Established news organization", "Peer-reviewed journal", "Government/edu domain"]
                    },
                    {
                        "question": "Is there bias?",
                        "how_to_check": "Look for loaded language, one-sided presentation, missing context. Use AllSides.com or Media Bias/Fact Check to rate source bias.",
                        "tip": "Even biased sources can report facts—but verify with other sources"
                    },
                    {
                        "question": "Can you verify the claim elsewhere?",
                        "method": "Check at least 2-3 other reputable sources. If only one site reports it, be skeptical.",
                        "tools": ["Google News", "Snopes (fact-checking)", "FactCheck.org", "Reuters/AP (neutral wire services)"]
                    },
                    {
                        "question": "When was it published?",
                        "red_flags": ["Old article presented as new", "No date listed"],
                        "tip": "Context changes over time—2015 advice may be outdated"
                    },
                    {
                        "question": "Does it cite sources?",
                        "red_flags": ["'Studies show...' with no link", "'Experts say...' with no names", "No citations"],
                        "green_flags": ["Links to original research", "Direct quotes with attribution", "Transparent methodology"]
                    },
                    {
                        "question": "Does the headline match the content?",
                        "red_flags": ["Clickbait headline that overpromises", "Headline contradicts article body"],
                        "tip": "Always read past the headline—many people share articles without reading them"
                    }
                ],
                "recognizing_misinformation": [
                    {
                        "type": "Deepfakes & Manipulated Media",
                        "how_to_spot": "Look for unnatural movements, lighting inconsistencies, weird blurring around edges, check if original exists elsewhere",
                        "example": "Video of politician saying something shocking—verify on official channels"
                    },
                    {
                        "type": "Satire Presented as News",
                        "how_to_spot": "Check if the site is satire (The Onion, Babylon Bee). Look for 'About' page disclaimer.",
                        "example": "Outrageous celebrity story—verify on legitimate entertainment news"
                    },
                    {
                        "type": "Emotional Manipulation",
                        "how_to_spot": "Extreme language (outrage, fear, disgust). Designed to make you share without thinking.",
                        "example": "'You won't BELIEVE what they're hiding from you!' (probably nothing)"
                    },
                    {
                        "type": "Cherry-Picked Data",
                        "how_to_spot": "Uses one statistic out of context, ignores contradicting data",
                        "example": "'Crime up 50%!' (compared to what period? What's the long-term trend?)"
                    }
                ]
            },
            "digital_security_hygiene": [
                {
                    "practice": "Two-Factor Authentication (2FA)",
                    "description": "Requires a second form of verification beyond password (code via text, app, or hardware key)",
                    "why_it_matters": "Even if someone steals your password, they can't access your account without the 2FA code",
                    "how_to_enable": [
                        "Go to account security settings on each service (Google, banking, social media, etc.)",
                        "Choose 'Two-factor authentication' or '2-Step Verification'",
                        "Use an authenticator app (Google Authenticator, Authy) instead of SMS if possible (SMS can be intercepted)"
                    ],
                    "priority_accounts": ["Email (controls password resets for everything)", "Banking", "Social media", "Cloud storage"],
                    "tip": "Save backup codes in a secure place in case you lose your phone"
                },
                {
                    "practice": "Unique Passwords for Every Account",
                    "description": "Never reuse passwords—if one site is breached, all your accounts are compromised",
                    "why_it_matters": "Data breaches happen constantly. If LinkedIn gets hacked and you use that password for Gmail, hackers now have your Gmail.",
                    "how_to_do_it": [
                        "Use a password manager (Bitwarden, 1Password, LastPass)",
                        "Let it generate strong, unique passwords (16+ characters, random)",
                        "You only need to remember ONE master password for the manager"
                    ],
                    "password_requirements": "12+ characters, mix of uppercase, lowercase, numbers, symbols. Or use 4+ random words (correct-horse-battery-staple)",
                    "never_use": ["'password', '123456', 'qwerty'", "Your name, birthday, pet's name", "Common words or phrases"]
                },
                {
                    "practice": "Recognize Phishing",
                    "description": "Fake emails/messages that trick you into giving up passwords or personal info",
                    "how_to_spot": [
                        "Urgent language: 'Your account will be closed!' 'Verify now!'",
                        "Suspicious sender: Check email address carefully (amaz0n.com vs amazon.com)",
                        "Requests for passwords, SSN, credit cards (legitimate companies never ask via email)",
                        "Hover over links (don't click!) to see real URL—does it match the supposed sender?",
                        "Grammar/spelling errors in 'official' emails",
                        "Too good to be true: 'You won a prize!' 'Refund available!'"
                    ],
                    "what_to_do": [
                        "Don't click links—go directly to the site by typing the URL",
                        "Call the company using a number YOU looked up (not one in the email)",
                        "Report phishing to your email provider",
                        "Delete the email"
                    ],
                    "example": "Email from 'PayPal' saying account suspended → Don't click link → Go to PayPal.com directly → Likely a scam"
                },
                {
                    "practice": "Regular Software Updates",
                    "description": "Updates patch security vulnerabilities that hackers exploit",
                    "why_it_matters": "Outdated software is the #1 way hackers get in. Updates aren't just new features—they fix security holes.",
                    "what_to_update": ["Operating system (Windows, macOS, iOS, Android)", "Browser (Chrome, Firefox, Safari)", "Apps (especially banking, email, social media)", "Router firmware"],
                    "tip": "Enable automatic updates whenever possible"
                },
                {
                    "practice": "Be Careful on Public Wi-Fi",
                    "description": "Public Wi-Fi is insecure—hackers can intercept your data",
                    "risks": "Login credentials, credit card info, personal messages can be stolen",
                    "how_to_stay_safe": [
                        "Use a VPN (Virtual Private Network) to encrypt your traffic—NordVPN, ProtonVPN, Mullvad",
                        "Avoid logging into banking/sensitive accounts on public Wi-Fi",
                        "Turn off file sharing and AirDrop",
                        "Use HTTPS sites only (look for lock icon in address bar)",
                        "Forget the network after use (don't auto-connect)"
                    ]
                }
            ],
            "digital_ethics": [
                {
                    "topic": "Consent & Privacy",
                    "principle": "Don't share others' info, photos, or messages without permission",
                    "examples": [
                        "Don't post photos of friends without asking",
                        "Don't screenshot and share private messages",
                        "Don't share someone's phone number, address, or email without consent"
                    ],
                    "why_it_matters": "Privacy violations can have real-world consequences (doxxing, harassment, job loss)"
                },
                {
                    "topic": "Digital Footprint",
                    "principle": "Everything online is permanent—think before you post",
                    "reality_check": [
                        "Screenshots exist forever even if you delete",
                        "Employers and schools Google applicants",
                        "Wayback Machine archives old web pages",
                        "Cloud storage can be hacked or subpoenaed"
                    ],
                    "tips": [
                        "Google yourself periodically to see what's public",
                        "Adjust privacy settings on social media",
                        "Don't post anything you wouldn't want your employer/family to see",
                        "Use separate accounts for professional vs. personal"
                    ]
                },
                {
                    "topic": "Misinformation Responsibility",
                    "principle": "Don't spread misinformation—verify before sharing",
                    "why_it_matters": "Fake news spreads 6x faster than real news. You're responsible for what you amplify.",
                    "before_sharing": [
                        "Read past the headline",
                        "Check the source (is it credible?)",
                        "Verify with 2-3 other sources",
                        "Ask: Could this be satire or manipulated?"
                    ],
                    "if_you_shared_something_false": "Publicly correct it—don't just delete and hope no one noticed"
                },
                {
                    "topic": "Online Behavior (Don't Be a Jerk)",
                    "principle": "Treat people online like you would in person",
                    "examples": [
                        "Don't say anything online you wouldn't say to someone's face",
                        "No pile-ons or harassment",
                        "Don't feed trolls—block and move on",
                        "Disagree respectfully—attack ideas, not people"
                    ],
                    "tip": "If you're angry, draft the response but don't send. Come back in an hour and re-evaluate."
                }
            ],
            "healthy_digital_habits": [
                "Set screen time limits (use built-in tools: Screen Time on iOS, Digital Wellbeing on Android)",
                "No phones in bedroom—charge in another room to improve sleep",
                "Turn off non-essential notifications to reduce distraction",
                "Schedule 'digital detox' times (e.g., no screens after 8pm, or one day per week)",
                "Curate your feeds—unfollow accounts that make you feel bad",
                "Use grayscale mode to make phone less appealing",
                "Practice 'FOMO immunity'—missing out on some things is okay and healthy"
            ],
            "tips": [
                "If something online makes you feel strong emotions (outrage, fear), pause and fact-check before reacting",
                "Teach kids digital literacy early—they'll encounter this stuff whether we like it or not",
                "Use privacy-focused alternatives when possible: DuckDuckGo (search), Signal (messaging), ProtonMail (email)",
                "Your data is valuable—companies monetize it. Read privacy policies for important services.",
                "Be skeptical by default, but not cynical—most people online are real, not bots"
            ]
        }

    def save(self):
        with open(DIGITAL_WELLNESS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant digital wellness information."""
        query_lower = query.lower()
        results = []

        # Media literacy
        if any(term in query_lower for term in ["media literacy", "source", "verify", "fake news", "misinformation", "fact check"]):
            results.append({"type": "media_literacy", "data": self.data.get("media_literacy", {})})

        # Digital security
        if any(term in query_lower for term in ["2fa", "two factor", "password", "phishing", "security", "update", "wifi", "vpn"]):
            results.extend([{"type": "security", "data": practice} for practice in self.data.get("digital_security_hygiene", [])])

        # Digital ethics
        if any(term in query_lower for term in ["ethics", "privacy", "consent", "digital footprint", "sharing", "online behavior"]):
            results.extend([{"type": "ethics", "data": topic} for topic in self.data.get("digital_ethics", [])])

        # Healthy habits
        if any(term in query_lower for term in ["screen time", "digital detox", "healthy", "habit", "balance"]):
            results.append({"type": "habits", "data": self.data.get("healthy_digital_habits", [])})

        return results[:5]

    def format_response(self, results):
        """Format digital wellness information for display."""
        if not results:
            return "I don't have specific digital wellness info on that yet."

        output = []

        for result in results:
            if result["type"] == "media_literacy":
                ml = result["data"]
                output.append(f"🔍 **Media Literacy**")
                output.append(f"{ml['principle']}\n")
                output.append("**Source Verification Checklist:**\n")
                for check in ml["source_verification_checklist"][:5]:
                    output.append(f"**{check['question']}**")
                    if "red_flags" in check:
                        output.append(f"  🚩 Red flags: {', '.join(check['red_flags'])}")
                    if "green_flags" in check:
                        output.append(f"  ✅ Green flags: {', '.join(check['green_flags'])}")
                    if "how_to_check" in check:
                        output.append(f"  {check['how_to_check']}")
                    if "tip" in check:
                        output.append(f"  💡 {check['tip']}")
                    output.append("")

            elif result["type"] == "security":
                security = result["data"]
                output.append(f"🔒 **{security['practice']}**")
                output.append(f"{security['description']}\n")
                output.append(f"**Why it matters:** {security['why_it_matters']}\n")

                if "how_to_enable" in security:
                    output.append("**How to enable:**")
                    for step in security["how_to_enable"]:
                        output.append(f"  {step}")
                    output.append("")

                if "how_to_do_it" in security:
                    output.append("**How to do it:**")
                    for step in security["how_to_do_it"]:
                        output.append(f"  • {step}")
                    output.append("")

                if "how_to_spot" in security:
                    output.append("**How to spot phishing:**")
                    for sign in security["how_to_spot"]:
                        output.append(f"  • {sign}")
                    output.append("")

                if "tip" in security:
                    output.append(f"💡 {security['tip']}\n")

            elif result["type"] == "ethics":
                ethics = result["data"]
                output.append(f"⚖️ **{ethics['topic']}**")
                output.append(f"**Principle:** {ethics['principle']}\n")

                if "examples" in ethics:
                    output.append("**Examples:**")
                    for ex in ethics["examples"]:
                        output.append(f"  • {ex}")
                    output.append("")

                if "why_it_matters" in ethics:
                    output.append(f"**Why it matters:** {ethics['why_it_matters']}\n")

                if "before_sharing" in ethics:
                    output.append("**Before sharing:**")
                    for item in ethics["before_sharing"]:
                        output.append(f"  • {item}")
                    output.append("")

            elif result["type"] == "habits":
                output.append("🌱 **Healthy Digital Habits:**")
                for habit in result["data"]:
                    output.append(f"  • {habit}")
                output.append("")

        # Add tips
        if len(results) <= 2:
            output.append("💡 **Digital Wellness Tips:**")
            for tip in self.data.get("tips", [])[:3]:
                output.append(f"  • {tip}")

        return "\n".join(output)


if __name__ == "__main__":
    store = DigitalWellnessStore()
    results = store.search("how to spot phishing")
    print(store.format_response(results))
