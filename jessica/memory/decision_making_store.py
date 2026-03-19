"""
Decision-Making Store: Frameworks and models to help think through choices.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DECISION_MAKING_FILE = os.path.join(DATA_DIR, "decision_making.json")


class DecisionMakingStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(DECISION_MAKING_FILE):
            with open(DECISION_MAKING_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_frameworks()
            self.save()

    def _get_starter_frameworks(self):
        return {
            "frameworks": [
                {
                    "name": "Eisenhower Matrix (Urgent vs. Important)",
                    "description": "Prioritize tasks by urgency and importance",
                    "quadrants": {
                        "Do First (Urgent + Important)": [
                            "Crises, emergencies, deadlines",
                            "Example: Medical emergency, project due tomorrow"
                        ],
                        "Schedule (Important, Not Urgent)": [
                            "Long-term goals, planning, self-care",
                            "Example: Exercise, learning new skills, relationship building",
                            "This is where most meaningful work lives—don't neglect it!"
                        ],
                        "Delegate (Urgent, Not Important)": [
                            "Interruptions, some emails/calls, busywork",
                            "Example: Errands that someone else could do, routine tasks",
                            "Ask: Can someone else do this?"
                        ],
                        "Eliminate (Not Urgent, Not Important)": [
                            "Time wasters, distractions, mindless scrolling",
                            "Example: Excessive social media, pointless meetings",
                            "Be ruthless—these drain energy without adding value"
                        ]
                    },
                    "how_to_use": "List all your tasks/decisions. Ask: Is this urgent? Is this important? Place in the matrix. Focus on quadrant 2 (Important, Not Urgent) to prevent quadrant 1 fires.",
                    "when_to_use": "When you're overwhelmed with tasks or can't decide what to prioritize"
                },
                {
                    "name": "Pros and Cons List (with weights)",
                    "description": "Classic decision tool with a twist—assign importance weights",
                    "steps": [
                        "Draw a line down the middle: Pros | Cons",
                        "List all advantages on the left, disadvantages on the right",
                        "Rate each item 1-10 for importance",
                        "Multiply quantity × importance: e.g., 5 pros (avg 7/10) = 35 points",
                        "Compare totals—but also trust your gut if numbers feel wrong"
                    ],
                    "example": "Should I take this job?\nPros: Higher pay (9), better commute (6), growth potential (8) = 23\nCons: Longer hours (7), less vacation (5), new industry (4) = 16\nPros win numerically—but if 'longer hours' feels like a deal-breaker emotionally, that matters too.",
                    "when_to_use": "When you need to weigh multiple factors logically"
                },
                {
                    "name": "10-10-10 Rule (Temporal Perspective)",
                    "description": "Consider how you'll feel about this decision in 10 minutes, 10 months, and 10 years",
                    "questions": [
                        "In 10 minutes: Will I feel immediate regret or relief?",
                        "In 10 months: Will this still matter? Will I be glad I did it?",
                        "In 10 years: Will I remember this? Will I wish I'd chosen differently?"
                    ],
                    "example": "Should I quit my job without another lined up?\n10 min: Relief from stress\n10 months: Financial anxiety if no new job found\n10 years: Proud I took a risk, or regret being impulsive?\nThis reveals whether the decision is emotionally reactive or aligned with long-term values.",
                    "when_to_use": "When emotions are clouding judgment or you're thinking short-term only"
                },
                {
                    "name": "The Regret Minimization Framework (Jeff Bezos)",
                    "description": "Project yourself to age 80 and ask: Will I regret not doing this?",
                    "questions": [
                        "When I'm 80, will I regret trying this and failing?",
                        "Or will I regret never trying at all?"
                    ],
                    "insight": "Most people regret inaction more than action. 'I wish I had...' haunts more than 'I tried and it didn't work out.'",
                    "example": "Should I start a business? At 80, I'd probably regret not trying more than trying and failing.",
                    "when_to_use": "For big, life-changing decisions where fear of failure is holding you back"
                },
                {
                    "name": "The Two-Way Door vs. One-Way Door",
                    "description": "Categorize decisions as reversible or irreversible",
                    "two_way_door": [
                        "Reversible decisions—you can walk back through if it doesn't work",
                        "Examples: Trying a new restaurant, taking a short course, changing your hair",
                        "Strategy: Make these quickly, experiment freely"
                    ],
                    "one_way_door": [
                        "Irreversible or hard-to-reverse decisions",
                        "Examples: Accepting a job in another country, getting married, having kids",
                        "Strategy: Take time, gather information, consult trusted people"
                    ],
                    "when_to_use": "When you're overthinking small decisions or rushing big ones"
                },
                {
                    "name": "Decision Matrix (Multi-Criteria)",
                    "description": "Rate options against multiple criteria",
                    "steps": [
                        "List all options (e.g., Job A, Job B, Job C)",
                        "Define criteria (e.g., salary, culture, growth, work-life balance)",
                        "Rate each option 1-10 for each criterion",
                        "Optionally: Weight criteria by importance (e.g., work-life balance = 2x weight)",
                        "Total scores—highest wins"
                    ],
                    "example": "Choosing between apartments:\nCriteria: Price (weight 2x), Location (1x), Size (1x)\nApt A: Price 8, Location 6, Size 5 = (8×2) + 6 + 5 = 27\nApt B: Price 5, Location 9, Size 7 = (5×2) + 9 + 7 = 26\nApt A wins—price matters most to you.",
                    "when_to_use": "When comparing 3+ options with multiple factors"
                },
                {
                    "name": "The Hell Yeah or No (Derek Sivers)",
                    "description": "If it's not a 'hell yeah,' it's a no",
                    "philosophy": "Only commit to opportunities that excite you. Saying no to good things makes room for great things.",
                    "when_to_use": "When you're overcommitted or saying yes out of guilt/obligation",
                    "example": "Invited to a networking event—do you genuinely want to go, or just feel you 'should'? If it's not a clear yes, decline.",
                    "caveat": "Doesn't apply to all responsibilities (e.g., paying bills isn't 'hell yeah' but still necessary)"
                }
            ],
            "cognitive_biases_to_watch": [
                {
                    "bias": "Sunk Cost Fallacy",
                    "description": "Continuing something because you've already invested time/money, even if it's not working",
                    "antidote": "Ask: If I were starting fresh today, would I choose this? Past costs are gone—focus on future value."
                },
                {
                    "bias": "Confirmation Bias",
                    "description": "Only seeking information that supports what you already believe",
                    "antidote": "Actively seek opposing viewpoints. Ask: What would change my mind?"
                },
                {
                    "bias": "Analysis Paralysis",
                    "description": "Overthinking until you can't decide at all",
                    "antidote": "Set a decision deadline. Use 'good enough' instead of 'perfect.' Remember: Inaction is also a choice."
                },
                {
                    "bias": "Anchoring",
                    "description": "Over-relying on the first piece of information you hear",
                    "antidote": "Consider multiple perspectives and data points before deciding."
                }
            ],
            "tips": [
                "Sleep on big decisions—your subconscious processes while you rest",
                "Talk it out with someone who won't just agree with you",
                "Write down your gut feeling before doing analysis—intuition matters",
                "Set a 'decide by' date so you don't procrastinate indefinitely",
                "Remember: Not deciding is still a decision (often the worst one)"
            ]
        }

    def save(self):
        with open(DECISION_MAKING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant decision-making frameworks."""
        query_lower = query.lower()
        results = []

        # Specific framework searches
        for framework in self.data.get("frameworks", []):
            name_lower = framework["name"].lower()
            if any(term in query_lower for term in name_lower.split()):
                results.append({"type": "framework", "data": framework})
            elif "eisenhower" in query_lower and "eisenhower" in name_lower:
                results.append({"type": "framework", "data": framework})
            elif any(term in query_lower for term in ["pros cons", "pros and cons", "advantages disadvantages"]) and "pros" in name_lower:
                results.append({"type": "framework", "data": framework})
            elif "regret" in query_lower and "regret" in name_lower:
                results.append({"type": "framework", "data": framework})

        # General decision keywords
        if any(term in query_lower for term in ["decide", "choice", "decision", "choose", "should i"]):
            if not results:  # Show all frameworks if no specific match
                results = [{"type": "framework", "data": fw} for fw in self.data.get("frameworks", [])[:3]]

        # Bias awareness
        if any(term in query_lower for term in ["bias", "trap", "mistake", "avoid"]):
            results.append({"type": "biases", "data": self.data.get("cognitive_biases_to_watch", [])})

        # Tips
        if "tip" in query_lower:
            results.append({"type": "tips", "data": self.data.get("tips", [])})

        return results if results else [{"type": "general", "data": self.data}]

    def format_response(self, results):
        """Format search results for display."""
        if not results:
            return "I don't have specific guidance on that decision-making topic yet."

        output = []

        for result in results[:3]:  # Limit to 3 most relevant
            if result["type"] == "framework":
                framework = result["data"]
                output.append(f"🧠 **{framework['name']}**")
                output.append(f"{framework['description']}\n")

                if "quadrants" in framework:
                    output.append("**Quadrants:**")
                    for quad, details in framework["quadrants"].items():
                        output.append(f"  **{quad}:**")
                        for detail in details:
                            output.append(f"    • {detail}")
                    output.append("")

                if "steps" in framework:
                    output.append("**Steps:**")
                    for step in framework["steps"]:
                        output.append(f"  {step}")
                    output.append("")

                if "questions" in framework:
                    output.append("**Questions to ask:**")
                    for q in framework["questions"]:
                        output.append(f"  • {q}")
                    output.append("")

                if "example" in framework:
                    output.append(f"**Example:** {framework['example']}\n")

                if "when_to_use" in framework:
                    output.append(f"**When to use:** {framework['when_to_use']}\n")

                if "insight" in framework:
                    output.append(f"💡 {framework['insight']}\n")

            elif result["type"] == "biases":
                biases = result["data"]
                output.append("⚠️ **Cognitive Biases to Watch:**")
                for bias in biases:
                    output.append(f"  **{bias['bias']}:** {bias['description']}")
                    output.append(f"    Antidote: {bias['antidote']}")
                output.append("")

            elif result["type"] == "tips":
                tips = result["data"]
                output.append("💡 **Decision-Making Tips:**")
                for tip in tips:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Quick test
    store = DecisionMakingStore()
    results = store.search("eisenhower matrix")
    print(store.format_response(results))
