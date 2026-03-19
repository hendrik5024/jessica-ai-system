"""
Conflict Resolution Store: Strategies for difficult conversations and navigating disagreements.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONFLICT_RESOLUTION_FILE = os.path.join(DATA_DIR, "conflict_resolution.json")


class ConflictResolutionStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(CONFLICT_RESOLUTION_FILE):
            with open(CONFLICT_RESOLUTION_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_strategies()
            self.save()

    def _get_starter_strategies(self):
        return {
            "frameworks": [
                {
                    "name": "Nonviolent Communication (NVC)",
                    "description": "Four-step process to express needs without blame",
                    "steps": [
                        "Observation: State facts without judgment ('When you arrived 30 minutes late...')",
                        "Feeling: Share your emotion ('I felt worried and frustrated')",
                        "Need: Express the underlying need ('because I need reliability and respect for my time')",
                        "Request: Make a specific, actionable request ('Would you be willing to text me if you're running late?')"
                    ],
                    "example": "When you interrupted me in the meeting (observation), I felt dismissed (feeling), because I need to feel heard and respected (need). Would you let me finish my thoughts before responding in the future? (request)",
                    "when_to_use": "When you need to address a behavior without attacking the person"
                },
                {
                    "name": "The FBI Hostage Negotiation Technique",
                    "description": "De-escalation through active listening (adapted for everyday conflicts)",
                    "steps": [
                        "Listen actively without interrupting",
                        "Reflect back what they said: 'So what you're saying is...'",
                        "Label their emotion: 'It sounds like you're feeling frustrated'",
                        "Validate (doesn't mean agree): 'I can understand why you'd feel that way'",
                        "Ask open-ended questions: 'What would make this better for you?'"
                    ],
                    "example": "Angry coworker: 'You never help with the workload!' → You: 'I hear that you're feeling overwhelmed (label). It sounds like you feel I'm not pulling my weight (reflect). That must be really frustrating (validate). Can you help me understand which tasks you're needing support with?' (open question)",
                    "when_to_use": "When emotions are running high and you need to calm the situation first"
                },
                {
                    "name": "The DESC Script",
                    "description": "Describe, Express, Specify, Consequences",
                    "steps": [
                        "Describe the situation objectively",
                        "Express your feelings about it",
                        "Specify what you want to happen",
                        "Consequences: Explain positive outcomes or negative ones if unresolved"
                    ],
                    "example": "Roommate conflict: 'I've noticed dishes piling up in the sink for days (describe). I feel stressed when I come home to a messy kitchen (express). Could we agree to wash dishes within 24 hours? (specify) That way, we'll both feel more comfortable in our space and avoid resentment building up (consequences).'",
                    "when_to_use": "When you need a clear structure for a difficult conversation"
                },
                {
                    "name": "The Aikido Approach",
                    "description": "Deflect conflict by agreeing with part of what they say",
                    "technique": "Find the kernel of truth in their complaint and acknowledge it, then redirect",
                    "examples": [
                        "Them: 'You're always late!' → You: 'You're right, I was late today, and I can see how that's frustrating. Let me make sure it doesn't happen again.'",
                        "Them: 'You never listen to me!' → You: 'I can see I didn't give you my full attention just now. I want to hear what you're saying—can we start over?'"
                    ],
                    "when_to_use": "When someone is exaggerating but has a valid point buried in the accusation"
                }
            ],
            "difficult_conversations": [
                {
                    "scenario": "Giving critical feedback to a friend",
                    "approach": "Use the 'sandwich method' carefully (but don't be formulaic)",
                    "script": "I really value our friendship (positive). I want to bring something up that's been bothering me: when you cancel plans last minute, I feel like my time isn't valued (feedback). I know you don't mean it that way, and I'd love to find a way we can both feel respected (positive).",
                    "tips": ["Choose the right time (not when they're stressed)", "Use 'I' statements", "Be specific, not vague"]
                },
                {
                    "scenario": "Addressing a coworker who takes credit for your work",
                    "approach": "Direct but professional confrontation",
                    "script": "Hey [name], I wanted to discuss the presentation. I noticed the ideas I shared in our brainstorm were presented as your own. I'm sure it wasn't intentional, but moving forward, I'd appreciate if we could clarify who's contributing what. How do we make sure we're both credited fairly?",
                    "tips": ["Assume positive intent first", "Focus on the behavior, not character", "Propose a solution"]
                },
                {
                    "scenario": "Setting boundaries with a demanding family member",
                    "approach": "Clear, compassionate, consistent boundaries",
                    "script": "I love you and want to help when I can, but I'm not able to [drop everything/lend money/host every holiday] every time. I need to set some limits for my own well-being. Let's talk about what's realistic for me to commit to.",
                    "tips": ["Don't over-explain or justify", "Expect pushback—hold firm kindly", "Offer alternatives when possible"]
                },
                {
                    "scenario": "Apologizing after a conflict",
                    "approach": "Genuine, specific, action-oriented apology",
                    "script": "I'm sorry for [specific action]. That was wrong because [impact on them]. In the future, I'll [specific change]. How can I make this right?",
                    "tips": ["No 'but' in your apology", "Don't make excuses", "Show changed behavior, not just words"]
                }
            ],
            "red_flags": [
                "If someone refuses to hear you or shuts down every attempt to talk → This may be emotional unavailability, not just conflict",
                "If conflicts always escalate to yelling, threats, or insults → Consider whether this relationship is safe",
                "If you're always the one apologizing or compromising → This may be an imbalance of power",
                "If conflicts are repetitive with no change → They may not be willing to work on the issue"
            ],
            "tips": [
                "Pick the right time: Not when either person is hungry, tired, or stressed",
                "Use 'and' instead of 'but': 'I hear you, and I also need...' (validates both sides)",
                "Pause if emotions escalate: 'Can we take a 10-minute break and come back to this?'",
                "Focus on the issue, not the person: 'This behavior' not 'You always...'",
                "Ask for what you want, not just what you don't want: 'I need advance notice' vs 'Stop being flaky'"
            ]
        }

    def save(self):
        with open(CONFLICT_RESOLUTION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant conflict resolution strategies."""
        query_lower = query.lower()
        results = []

        # Search frameworks
        for framework in self.data.get("frameworks", []):
            if any(term in framework["name"].lower() or term in framework["description"].lower() 
                   for term in query_lower.split()):
                results.append({"type": "framework", "data": framework})

        # Search scenarios
        for scenario in self.data.get("difficult_conversations", []):
            if any(term in scenario["scenario"].lower() for term in query_lower.split()):
                results.append({"type": "scenario", "data": scenario})

        # General conflict keywords
        if any(term in query_lower for term in ["conflict", "argument", "fight", "disagree", "difficult conversation"]):
            if not results:  # If no specific match, show frameworks
                results = [{"type": "framework", "data": fw} for fw in self.data.get("frameworks", [])]

        # Tips
        if "tip" in query_lower or "how to" in query_lower:
            results.append({"type": "tips", "data": self.data.get("tips", [])})

        return results if results else [{"type": "general", "data": self.data}]

    def format_response(self, results):
        """Format search results for display."""
        if not results:
            return "I don't have specific guidance on that conflict resolution topic yet."

        output = []

        for result in results[:3]:  # Limit to 3 most relevant
            if result["type"] == "framework":
                framework = result["data"]
                output.append(f"🤝 **{framework['name']}**")
                output.append(f"{framework['description']}\n")
                output.append("**Steps:**")
                for step in framework["steps"]:
                    output.append(f"  {step}")
                output.append(f"\n**Example:** {framework['example']}")
                output.append(f"**When to use:** {framework['when_to_use']}\n")

            elif result["type"] == "scenario":
                scenario = result["data"]
                output.append(f"💬 **{scenario['scenario']}**")
                output.append(f"**Approach:** {scenario['approach']}")
                output.append(f"**Script:** \"{scenario['script']}\"")
                output.append("**Tips:**")
                for tip in scenario["tips"]:
                    output.append(f"  • {tip}")
                output.append("")

            elif result["type"] == "tips":
                tips = result["data"]
                output.append("💡 **Conflict Resolution Tips:**")
                for tip in tips:
                    output.append(f"  • {tip}")
                output.append("")

        # Add red flags if not already shown
        if len(results) <= 2:
            output.append("⚠️ **Red Flags in Conflict:**")
            for flag in self.data.get("red_flags", []):
                output.append(f"  • {flag}")

        return "\n".join(output)


if __name__ == "__main__":
    # Quick test
    store = ConflictResolutionStore()
    results = store.search("how to have a difficult conversation with coworker")
    print(store.format_response(results))
