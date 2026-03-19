"""
Emotional Intelligence Store: Active listening, empathy, and emotional validation frameworks.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EMOTIONAL_INTELLIGENCE_FILE = os.path.join(DATA_DIR, "emotional_intelligence.json")


class EmotionalIntelligenceStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(EMOTIONAL_INTELLIGENCE_FILE):
            with open(EMOTIONAL_INTELLIGENCE_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_frameworks()
            self.save()

    def _get_starter_frameworks(self):
        return {
            "active_listening": [
                {
                    "framework": "Reflective Listening",
                    "description": "Mirror back what someone said to show you understand",
                    "when_to_use": "When someone shares a problem or emotion",
                    "examples": [
                        "Person: 'I'm overwhelmed with work.' → You: 'It sounds like you're feeling really swamped right now.'",
                        "Person: 'My boss doesn't appreciate me.' → You: 'That must feel really discouraging.'",
                        "Person: 'I don't know what to do about this.' → You: 'It seems like you're feeling uncertain about your options.'"
                    ],
                    "avoid": "Jumping straight to solutions or saying 'just do this'",
                    "key_phrases": ["It sounds like...", "That must feel...", "I hear you saying...", "What I'm understanding is..."]
                },
                {
                    "framework": "Validation Before Solution",
                    "description": "Acknowledge feelings first, then ask if advice is wanted",
                    "when_to_use": "When someone vents about a frustration",
                    "examples": [
                        "That sounds really frustrating. Do you want to brainstorm solutions, or just need to vent?",
                        "I can see why that would be upsetting. Would it help to talk through options?",
                        "That's such a tough situation. Are you looking for advice, or just someone to listen?"
                    ],
                    "avoid": "Immediately offering unsolicited advice or saying 'you should...'",
                    "key_phrases": ["That's understandable", "Anyone would feel that way", "Your feelings are valid", "Do you want advice, or just to talk?"]
                },
                {
                    "framework": "The LEARN Technique",
                    "description": "Listen, Empathize, Ask, Reflect, Normalize",
                    "when_to_use": "Deep conversations where someone needs emotional support",
                    "steps": [
                        "Listen: Give full attention, no interruptions",
                        "Empathize: 'That sounds really hard'",
                        "Ask: 'How are you feeling about it?' (open-ended)",
                        "Reflect: 'So what I'm hearing is...'",
                        "Normalize: 'It's completely normal to feel this way'"
                    ],
                    "examples": [
                        "Friend shares breakup → Listen quietly → 'That sounds heartbreaking' → 'What's the hardest part for you?' → 'So you're grieving the future you imagined together' → 'Breakups are one of the hardest things we go through'"
                    ],
                    "avoid": "Minimizing ('it could be worse'), comparing ('when I went through...'), or fixing ('you'll find someone better')"
                }
            ],
            "empathy_responses": [
                {
                    "situation": "Someone shares a loss or grief",
                    "empathetic_response": "I'm so sorry you're going through this. There are no right words, but I'm here for you.",
                    "avoid_saying": ["At least they lived a long life", "Everything happens for a reason", "They're in a better place"]
                },
                {
                    "situation": "Someone is stressed or anxious",
                    "empathetic_response": "That sounds overwhelming. It's okay to feel this way. What would help you feel supported right now?",
                    "avoid_saying": ["Just calm down", "Don't worry about it", "You're overreacting"]
                },
                {
                    "situation": "Someone made a mistake",
                    "empathetic_response": "Mistakes happen to everyone. What matters is what you do next. How can I help?",
                    "avoid_saying": ["I told you so", "Why didn't you...", "That was careless"]
                },
                {
                    "situation": "Someone is disappointed",
                    "empathetic_response": "I know you worked really hard for this. It's okay to feel disappointed. Your effort still matters.",
                    "avoid_saying": ["There will be other chances", "It's not a big deal", "Just move on"]
                },
                {
                    "situation": "Someone feels misunderstood",
                    "empathetic_response": "I want to understand better. Can you help me see it from your perspective?",
                    "avoid_saying": ["You're being too sensitive", "That's not what I meant", "You're taking it wrong"]
                }
            ],
            "emotional_vocabulary": {
                "happy": ["joyful", "content", "grateful", "excited", "proud", "relieved", "hopeful", "peaceful"],
                "sad": ["disappointed", "heartbroken", "lonely", "discouraged", "grieving", "melancholy", "defeated"],
                "angry": ["frustrated", "irritated", "resentful", "furious", "indignant", "betrayed", "outraged"],
                "anxious": ["worried", "nervous", "overwhelmed", "uncertain", "apprehensive", "stressed", "panicked"],
                "confused": ["uncertain", "ambivalent", "conflicted", "perplexed", "torn", "indecisive"]
            },
            "tips": [
                "Use 'I' statements instead of 'you' statements: 'I feel concerned' vs 'You're worrying me'",
                "Silence is okay—don't rush to fill every pause in emotional conversations",
                "Mirror body language to show attentiveness (in person)",
                "Repeat key words they use to show you're listening: 'You mentioned feeling stuck...'",
                "Ask 'How can I support you?' instead of assuming what they need"
            ]
        }

    def save(self):
        with open(EMOTIONAL_INTELLIGENCE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant emotional intelligence frameworks."""
        query_lower = query.lower()
        results = []

        # Search active listening frameworks
        for framework in self.data.get("active_listening", []):
            if any(term in query_lower for term in ["listen", "validate", "empathy", "understand", "hear"]):
                results.append({"type": "active_listening", "data": framework})

        # Search empathy responses
        for response in self.data.get("empathy_responses", []):
            situation_words = response["situation"].lower().split()
            if any(word in query_lower for word in situation_words):
                results.append({"type": "empathy_response", "data": response})

        # If query asks for emotional vocabulary
        if any(term in query_lower for term in ["feeling", "emotion", "word for", "express"]):
            results.append({"type": "vocabulary", "data": self.data.get("emotional_vocabulary", {})})

        # General tips
        if any(term in query_lower for term in ["tip", "how to be", "empathetic", "better listener"]):
            results.append({"type": "tips", "data": self.data.get("tips", [])})

        return results if results else [{"type": "general", "data": self.data}]

    def format_response(self, results):
        """Format search results for display."""
        if not results:
            return "I don't have specific guidance on that emotional intelligence topic yet."

        output = []

        for result in results:
            if result["type"] == "active_listening":
                framework = result["data"]
                output.append(f"🎧 **{framework['framework']}**")
                output.append(f"{framework['description']}\n")
                output.append(f"**When to use:** {framework['when_to_use']}\n")
                if "examples" in framework:
                    output.append("**Examples:**")
                    for ex in framework["examples"]:
                        output.append(f"  • {ex}")
                    output.append("")
                if "steps" in framework:
                    output.append("**Steps:**")
                    for step in framework["steps"]:
                        output.append(f"  • {step}")
                    output.append("")
                output.append(f"**Avoid:** {framework['avoid']}\n")
                if "key_phrases" in framework:
                    output.append("**Key phrases:** " + ", ".join(framework["key_phrases"]))
                output.append("")

            elif result["type"] == "empathy_response":
                response = result["data"]
                output.append(f"💙 **Situation:** {response['situation']}")
                output.append(f"**Empathetic response:** \"{response['empathetic_response']}\"")
                output.append(f"**Avoid saying:** {', '.join(response['avoid_saying'])}\n")

            elif result["type"] == "vocabulary":
                vocab = result["data"]
                output.append("📖 **Emotional Vocabulary** (to express feelings more precisely):")
                for base, nuances in vocab.items():
                    output.append(f"  • Instead of '{base}': {', '.join(nuances)}")
                output.append("")

            elif result["type"] == "tips":
                tips = result["data"]
                output.append("💡 **Emotional Intelligence Tips:**")
                for tip in tips:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Quick test
    store = EmotionalIntelligenceStore()
    results = store.search("how to validate someone's feelings")
    print(store.format_response(results))
