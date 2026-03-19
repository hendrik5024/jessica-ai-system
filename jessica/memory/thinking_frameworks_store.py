"""
Thinking Frameworks Store: Creative problem-solving methods like Six Thinking Hats.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
THINKING_FRAMEWORKS_FILE = os.path.join(DATA_DIR, "thinking_frameworks.json")


class ThinkingFrameworksStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(THINKING_FRAMEWORKS_FILE):
            with open(THINKING_FRAMEWORKS_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_frameworks()
            self.save()

    def _get_starter_frameworks(self):
        return {
            "six_thinking_hats": {
                "framework": "Six Thinking Hats (Edward de Bono)",
                "description": "A method to look at problems from six different perspectives, avoiding groupthink and exploring all angles",
                "how_it_works": "Each 'hat' represents a different mode of thinking. Put on each hat one at a time to explore the problem from that specific angle. Don't mix modes—focus on one at a time.",
                "hats": [
                    {
                        "hat": "White Hat 🤍 (Facts & Information)",
                        "focus": "Objective data, facts, figures—no opinions or interpretations",
                        "questions": [
                            "What information do we have?",
                            "What information is missing?",
                            "What facts are relevant?",
                            "What do the numbers say?"
                        ],
                        "example": "White Hat on 'Should we launch this product?' → Market research data, sales projections, competitor analysis, budget constraints"
                    },
                    {
                        "hat": "Red Hat ❤️ (Emotions & Intuition)",
                        "focus": "Gut feelings, emotions, hunches—no need to justify",
                        "questions": [
                            "How do I feel about this?",
                            "What does my intuition say?",
                            "What are my emotional reactions?",
                            "What's my gut instinct?"
                        ],
                        "example": "Red Hat on 'Should we hire this person?' → Something feels off, I'm excited about their energy, I'm worried they won't fit the team",
                        "note": "This is the ONLY hat where emotions are allowed. It prevents emotions from masquerading as logic in other hats."
                    },
                    {
                        "hat": "Black Hat 🖤 (Critical Judgment)",
                        "focus": "Risks, problems, what could go wrong—cautious and careful",
                        "questions": [
                            "What are the risks?",
                            "What could go wrong?",
                            "What are the weaknesses?",
                            "Why might this fail?"
                        ],
                        "example": "Black Hat on 'Let's pivot our business model' → We'll lose existing customers, team doesn't have expertise, competitors already tried and failed",
                        "note": "Most overused hat—valuable for risk assessment but paralyzing if used exclusively"
                    },
                    {
                        "hat": "Yellow Hat 💛 (Optimism & Benefits)",
                        "focus": "Positive thinking, opportunities, what could go right",
                        "questions": [
                            "What are the benefits?",
                            "What's the best-case scenario?",
                            "Why will this work?",
                            "What opportunities exist?"
                        ],
                        "example": "Yellow Hat on 'Let's pivot our business model' → New market is growing fast, we'll differentiate from competitors, team is excited",
                        "note": "Counterbalances Black Hat—ensures you don't dismiss good ideas prematurely"
                    },
                    {
                        "hat": "Green Hat 💚 (Creativity & Alternatives)",
                        "focus": "New ideas, possibilities, creative solutions—no judgment",
                        "questions": [
                            "What are alternative approaches?",
                            "What if we tried...?",
                            "How can we think outside the box?",
                            "What's a wild idea that might work?"
                        ],
                        "example": "Green Hat on 'We need more customers' → What if we gave the product away free with a premium tier? Partner with influencers? Create a viral challenge?",
                        "note": "Brainstorming mode—quantity over quality, defer judgment"
                    },
                    {
                        "hat": "Blue Hat 💙 (Process & Control)",
                        "focus": "Meta-thinking—organizing the thinking process itself",
                        "questions": [
                            "What thinking do we need?",
                            "Which hat should we use next?",
                            "What have we learned?",
                            "What's the summary and next steps?"
                        ],
                        "example": "Blue Hat on group meeting → Let's start with White Hat to gather facts, then Yellow and Black to weigh pros/cons, Green for alternatives, end with Blue for decision",
                        "note": "The facilitator hat—used at the beginning and end of thinking sessions"
                    }
                ],
                "when_to_use": "Complex decisions, group discussions (prevents arguing), personal dilemmas, stuck on a problem",
                "typical_sequence": [
                    "Blue Hat: Define the problem and thinking agenda",
                    "White Hat: Gather facts and information",
                    "Green Hat: Generate ideas and alternatives",
                    "Yellow Hat: Explore benefits and positives",
                    "Black Hat: Identify risks and problems",
                    "Red Hat: Check gut feelings and emotional responses",
                    "Blue Hat: Summarize, decide, and plan next steps"
                ],
                "key_insight": "By separating thinking modes, you avoid the paralysis of trying to be creative, critical, and emotional simultaneously. Each hat gets its moment."
            },
            "other_frameworks": [
                {
                    "framework": "First Principles Thinking",
                    "description": "Break problems down to fundamental truths, then reason up from there",
                    "how_it_works": "Question all assumptions until you reach the core truth, then rebuild your understanding",
                    "steps": [
                        "Identify the problem or belief",
                        "Break it down: What are the underlying assumptions?",
                        "Ask 'Why?' repeatedly (like a 5-year-old) until you hit bedrock truths",
                        "Rebuild from first principles: What's actually true? What follows from that?"
                    ],
                    "example": "Tesla battery cost:\nAssumption: Batteries are expensive, so electric cars will always cost more.\nFirst principles: What ARE batteries made of? Cobalt, nickel, lithium, carbon.\nWhat's the market cost of raw materials? Much cheaper than assembled batteries.\nConclusion: If we make batteries ourselves from raw materials, we can drastically cut costs.\nResult: Tesla disrupted the industry.",
                    "when_to_use": "When conventional wisdom seems limiting, when innovation is needed, when 'that's how it's always been done'"
                },
                {
                    "framework": "Inversion (Charlie Munger)",
                    "description": "Instead of asking 'How do I succeed?', ask 'How do I fail?' and avoid that",
                    "how_it_works": "Flip the problem—identify what would guarantee failure, then do the opposite",
                    "example": "Goal: Be happy\nInversion: What makes people miserable? → Isolation, poor health, no purpose, toxic relationships, financial stress\nSolution: Avoid these → Stay connected, exercise, find meaning, cultivate good relationships, manage money",
                    "when_to_use": "When forward-thinking feels overwhelming, when planning for success is unclear, when you want to avoid catastrophic mistakes",
                    "munger_quote": "All I want to know is where I'm going to die, so I'll never go there."
                },
                {
                    "framework": "SCAMPER (Creative Thinking)",
                    "description": "Seven prompts to spark creative solutions",
                    "prompts": {
                        "S - Substitute": "What can you replace? (materials, people, processes)",
                        "C - Combine": "What can you merge together? (two products, ideas, features)",
                        "A - Adapt": "What can you adjust to fit a new context? (borrow from another industry)",
                        "M - Modify": "What can you change? (size, shape, color, function)",
                        "P - Put to other use": "What else could this be used for?",
                        "E - Eliminate": "What can you remove or simplify?",
                        "R - Reverse/Rearrange": "What if you did the opposite or changed the order?"
                    },
                    "example": "Product: Coffee mug\nSubstitute: What if it was made of bamboo instead of ceramic?\nCombine: Mug + thermos = insulated travel mug\nAdapt: Add a built-in spoon holder like pen holders\nModify: Make it collapsible for travel\nPut to other use: Use as a planter when done with coffee\nEliminate: Remove the handle (like Japanese tea cups)\nReverse: What if the mug heated itself instead of relying on hot liquid?",
                    "when_to_use": "Brainstorming, product design, improving existing solutions"
                },
                {
                    "framework": "The 5 Whys (Root Cause Analysis)",
                    "description": "Ask 'Why?' five times to get to the root cause of a problem",
                    "how_it_works": "Start with the problem, ask why it happened, then ask why THAT happened, repeat 5 times",
                    "example": "Problem: The website crashed.\nWhy? The server was overloaded.\nWhy? Too many users accessed it at once.\nWhy? A marketing campaign went viral.\nWhy? We didn't anticipate the traffic spike.\nWhy? We don't have a process for load testing before campaigns.\nRoot cause: Missing load testing process → Solution: Implement pre-launch load testing",
                    "when_to_use": "Debugging, problem-solving, preventing recurring issues",
                    "note": "Stop when you reach something actionable—sometimes the root is 3 whys away, sometimes 7"
                }
            ],
            "tips": [
                "Use Six Thinking Hats in groups to prevent arguing—everyone wears the same hat at the same time",
                "When stuck, explicitly switch hats—'I've been in Black Hat too long, let me try Yellow'",
                "First Principles cuts through BS—if everyone says it's impossible, break it down to first principles",
                "Inversion is underrated—it's often easier to identify what NOT to do than what TO do",
                "Document your thinking process—it helps you spot patterns and biases"
            ]
        }

    def save(self):
        with open(THINKING_FRAMEWORKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant thinking frameworks."""
        query_lower = query.lower()
        results = []

        # Six Thinking Hats
        if any(term in query_lower for term in ["six thinking hats", "thinking hats", "six hats", "edward de bono", "hat"]):
            results.append({"type": "six_hats", "data": self.data.get("six_thinking_hats", {})})

        # Other frameworks
        for framework in self.data.get("other_frameworks", []):
            name_lower = framework["framework"].lower()
            if any(term in query_lower for term in name_lower.split()):
                results.append({"type": "framework", "data": framework})
            elif "first principles" in query_lower and "first principles" in name_lower:
                results.append({"type": "framework", "data": framework})
            elif "inversion" in query_lower and "inversion" in name_lower:
                results.append({"type": "framework", "data": framework})
            elif "scamper" in query_lower and "scamper" in name_lower:
                results.append({"type": "framework", "data": framework})
            elif "5 whys" in query_lower or "five whys" in query_lower:
                results.append({"type": "framework", "data": framework})

        # General creative thinking queries
        if any(term in query_lower for term in ["creative thinking", "problem solving", "thinking framework"]):
            if not results:
                results.append({"type": "six_hats", "data": self.data.get("six_thinking_hats", {})})
                results.extend([{"type": "framework", "data": fw} for fw in self.data.get("other_frameworks", [])[:2]])

        # Tips
        if "tip" in query_lower:
            results.append({"type": "tips", "data": self.data.get("tips", [])})

        return results[:5]

    def format_response(self, results):
        """Format thinking frameworks for display."""
        if not results:
            return "I don't have specific thinking framework info on that yet."

        output = []

        for result in results:
            if result["type"] == "six_hats":
                hats_data = result["data"]
                output.append(f"🎩 **{hats_data['framework']}**")
                output.append(f"{hats_data['description']}\n")
                output.append(f"**How it works:** {hats_data['how_it_works']}\n")

                output.append("**The Six Hats:**\n")
                for hat in hats_data["hats"]:
                    output.append(f"**{hat['hat']}**")
                    output.append(f"*Focus: {hat['focus']}*")
                    output.append("Questions:")
                    for q in hat["questions"][:3]:
                        output.append(f"  • {q}")
                    output.append(f"Example: {hat['example']}")
                    if "note" in hat:
                        output.append(f"💡 {hat['note']}")
                    output.append("")

                output.append(f"**When to use:** {hats_data['when_to_use']}\n")

                output.append("**Typical sequence:**")
                for step in hats_data["typical_sequence"]:
                    output.append(f"  {step}")
                output.append(f"\n💡 **Key insight:** {hats_data['key_insight']}\n")

            elif result["type"] == "framework":
                fw = result["data"]
                output.append(f"🧠 **{fw['framework']}**")
                output.append(f"{fw['description']}\n")

                if "how_it_works" in fw:
                    output.append(f"**How it works:** {fw['how_it_works']}\n")

                if "steps" in fw:
                    output.append("**Steps:**")
                    for step in fw["steps"]:
                        output.append(f"  {step}")
                    output.append("")

                if "prompts" in fw:
                    output.append("**Prompts:**")
                    for prompt, desc in fw["prompts"].items():
                        output.append(f"  **{prompt}:** {desc}")
                    output.append("")

                if "example" in fw:
                    output.append(f"**Example:** {fw['example']}\n")

                if "when_to_use" in fw:
                    output.append(f"**When to use:** {fw['when_to_use']}\n")

                if "munger_quote" in fw:
                    output.append(f"💬 \"{fw['munger_quote']}\"\n")

            elif result["type"] == "tips":
                output.append("💡 **Thinking Framework Tips:**")
                for tip in result["data"]:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    store = ThinkingFrameworksStore()
    results = store.search("six thinking hats")
    print(store.format_response(results))
