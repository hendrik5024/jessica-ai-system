"""
Systems Thinking Store: Root cause analysis, substitution logic, interconnected problem-solving.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SYSTEMS_THINKING_FILE = os.path.join(DATA_DIR, "systems_thinking.json")


class SystemsThinkingStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(SYSTEMS_THINKING_FILE):
            with open(SYSTEMS_THINKING_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_knowledge()
            self.save()

    def _get_starter_knowledge(self):
        return {
            "root_cause_analysis": {
                "method": "The 5 Whys",
                "description": "Ask 'Why?' repeatedly to drill down from symptom to root cause",
                "how_it_works": "Start with the problem. Ask why it happened. Take that answer and ask why again. Repeat until you reach something actionable.",
                "examples": [
                    {
                        "problem": "Car won't start",
                        "whys": [
                            "Why? → Battery is dead",
                            "Why? → Alternator isn't charging it",
                            "Why? → Alternator belt is broken",
                            "Why? → Belt wasn't replaced during maintenance",
                            "Why? → I don't have a maintenance schedule"
                        ],
                        "root_cause": "Missing maintenance schedule",
                        "solution": "Create and follow a car maintenance schedule"
                    },
                    {
                        "problem": "Website crashed during product launch",
                        "whys": [
                            "Why? → Server overloaded",
                            "Why? → Too many simultaneous users",
                            "Why? → Didn't expect this much traffic",
                            "Why? → Marketing campaign went viral unexpectedly",
                            "Why? → No load testing before launch"
                        ],
                        "root_cause": "Missing pre-launch load testing process",
                        "solution": "Implement load testing as part of launch checklist"
                    },
                    {
                        "problem": "Always running late to work",
                        "whys": [
                            "Why? → Leave house too late",
                            "Why? → Can't find things in the morning",
                            "Why? → Don't prepare the night before",
                            "Why? → Too tired in the evening",
                            "Why? → Stay up too late"
                        ],
                        "root_cause": "Poor sleep schedule",
                        "solution": "Set earlier bedtime, prepare clothes/bag at night"
                    }
                ],
                "tips": [
                    "Stop when you reach something you can control and change",
                    "Sometimes the root is 3 whys away, sometimes 7—it's not always exactly 5",
                    "Beware of blame—focus on processes, not people",
                    "If you get stuck, try asking 'What caused that?' instead of 'Why?'"
                ]
            },
            "substitution_logic": {
                "category": "Cooking Substitutions",
                "description": "When you're missing an ingredient, understand its function to find the right substitute",
                "ingredient_functions": {
                    "Eggs": {
                        "functions": ["Binding (holds ingredients together)", "Leavening (helps rise)", "Moisture", "Richness"],
                        "substitutes": [
                            {
                                "substitute": "Flax egg (1 tbsp ground flax + 3 tbsp water)",
                                "best_for": "Binding in muffins, pancakes, brownies",
                                "note": "Gives nutty flavor, adds fiber"
                            },
                            {
                                "substitute": "Applesauce (1/4 cup per egg)",
                                "best_for": "Moisture in cakes, muffins",
                                "note": "Makes things denser, sweeter—reduce sugar slightly"
                            },
                            {
                                "substitute": "Mashed banana (1/4 cup per egg)",
                                "best_for": "Moisture + binding in quick breads",
                                "note": "Adds banana flavor (good for banana bread!)"
                            },
                            {
                                "substitute": "Commercial egg replacer or aquafaba (3 tbsp per egg)",
                                "best_for": "Leavening in cakes, meringues",
                                "note": "Aquafaba (chickpea liquid) can even be whipped like egg whites"
                            }
                        ]
                    },
                    "Butter": {
                        "functions": ["Fat (flavor, texture)", "Moisture", "Tenderizing"],
                        "substitutes": [
                            {
                                "substitute": "Oil (vegetable, coconut, olive)",
                                "ratio": "Use 3/4 the amount (e.g., 3/4 cup oil for 1 cup butter)",
                                "best_for": "Muffins, cakes (makes them more moist but less rich)",
                                "note": "Coconut oil solidifies like butter, olive oil adds flavor"
                            },
                            {
                                "substitute": "Applesauce or mashed avocado",
                                "ratio": "1:1 but reduce other liquids slightly",
                                "best_for": "Healthier baking (reduces fat)",
                                "note": "Denser texture, less buttery flavor"
                            },
                            {
                                "substitute": "Greek yogurt or sour cream",
                                "ratio": "1:1",
                                "best_for": "Moisture + tang in cakes, muffins",
                                "note": "Adds protein, makes things fluffy"
                            }
                        ]
                    },
                    "Milk": {
                        "functions": ["Liquid", "Fat", "Protein", "Flavor"],
                        "substitutes": [
                            {
                                "substitute": "Non-dairy milk (almond, oat, soy, coconut)",
                                "ratio": "1:1",
                                "note": "Oat milk is creamiest for baking, almond is neutral, coconut adds flavor"
                            },
                            {
                                "substitute": "Water + butter/oil",
                                "ratio": "1 cup water + 1 tbsp butter/oil",
                                "note": "Adds back the fat content"
                            },
                            {
                                "substitute": "Half-and-half or cream (diluted with water)",
                                "ratio": "1:1 but dilute cream 50/50 with water",
                                "note": "Richer result"
                            }
                        ]
                    },
                    "Baking Powder": {
                        "functions": ["Leavening (makes baked goods rise)"],
                        "substitutes": [
                            {
                                "substitute": "Baking soda + acid (cream of tartar, lemon juice, vinegar)",
                                "ratio": "1 tsp baking powder = 1/4 tsp baking soda + 1/2 tsp cream of tartar (or 1/2 tsp lemon juice/vinegar)",
                                "note": "Mix right before using—reaction happens immediately"
                            }
                        ]
                    },
                    "Sugar": {
                        "functions": ["Sweetness", "Moisture", "Browning", "Structure"],
                        "substitutes": [
                            {
                                "substitute": "Honey or maple syrup",
                                "ratio": "Use 3/4 cup liquid sweetener for 1 cup sugar, reduce other liquids by 3 tbsp",
                                "note": "Adds distinct flavor, makes things moister"
                            },
                            {
                                "substitute": "Coconut sugar or brown sugar",
                                "ratio": "1:1",
                                "note": "Coconut sugar is less sweet, brown sugar adds molasses flavor"
                            }
                        ]
                    }
                },
                "general_rules": [
                    "Match the function: If eggs are for binding, use a binder (not a liquid)",
                    "Taste as you go: Substitutes often have distinct flavors",
                    "Expect texture changes: Substitutes rarely produce identical results—embrace the variation",
                    "Google '[ingredient] substitute' for specific scenarios"
                ]
            },
            "systems_thinking_principles": [
                {
                    "principle": "Everything is Connected",
                    "description": "Changes in one part of a system affect other parts",
                    "example": "You start waking up earlier → More time for breakfast → Better energy → More productive at work → Less stress → Better sleep → Wake up earlier easier (positive feedback loop)",
                    "application": "When solving a problem, ask: What else does this affect? What knock-on effects will my solution have?"
                },
                {
                    "principle": "Delays Between Cause and Effect",
                    "description": "Systems often have lag time between action and result",
                    "example": "Start working out → Sore for weeks → No weight loss yet → Give up (didn't wait long enough for results)",
                    "application": "Be patient with changes. Ask: How long until I see results? Don't quit during the delay."
                },
                {
                    "principle": "Feedback Loops",
                    "description": "Systems self-regulate through reinforcing or balancing loops",
                    "types": {
                        "Reinforcing (amplify)": "Rich get richer—success breeds more success (or failure breeds more failure)",
                        "Balancing (stabilize)": "Thermostat—when temp rises, AC turns on to bring it back down"
                    },
                    "example": "Reinforcing: Procrastinate → More stress → Worse performance → More stress (vicious cycle)\nBalancing: Eat too much → Feel full → Stop eating (homeostasis)"
                },
                {
                    "principle": "Leverage Points",
                    "description": "Small interventions in the right place can have huge impacts",
                    "example": "Instead of treating individual symptoms (headaches, fatigue), address the root: poor sleep. Fixing sleep fixes everything downstream.",
                    "application": "Find the bottleneck or root cause. Don't just treat symptoms."
                }
            ],
            "troubleshooting_framework": {
                "method": "DMAIC (Define, Measure, Analyze, Improve, Control)",
                "description": "Systematic problem-solving from Six Sigma",
                "steps": [
                    {
                        "step": "Define",
                        "description": "What exactly is the problem? Who is affected?",
                        "example": "Problem: Spending too much money. Define: Overspending by $300/month on dining out."
                    },
                    {
                        "step": "Measure",
                        "description": "Quantify the problem. Gather data.",
                        "example": "Track every dining expense for a month. Result: $450 on restaurants, $200 on coffee."
                    },
                    {
                        "step": "Analyze",
                        "description": "Why is this happening? Use 5 Whys or root cause analysis.",
                        "example": "Why so much dining out? → Too tired to cook after work → Stay late at work → No morning routine → Oversleep → Poor sleep schedule."
                    },
                    {
                        "step": "Improve",
                        "description": "Implement a solution targeting the root cause.",
                        "example": "Solution: Set bedtime alarm, meal prep on Sundays, leave work at 5pm."
                    },
                    {
                        "step": "Control",
                        "description": "Monitor to ensure the fix sticks. Create systems to prevent recurrence.",
                        "example": "Track spending monthly, set calendar reminder for meal prep, use app to track bedtime."
                    }
                ]
            },
            "tips": [
                "When stuck, zoom out—look at the whole system, not just the immediate problem",
                "Ask 'What if?' to explore unintended consequences before implementing solutions",
                "Document your systems (morning routine, workflows, checklists) so they become automatic",
                "Use checklists for recurring tasks to prevent errors (pilots do this for a reason)",
                "Fix upstream problems—they're often easier and more impactful than downstream fixes"
            ]
        }

    def save(self):
        with open(SYSTEMS_THINKING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant systems thinking information."""
        query_lower = query.lower()
        results = []

        # Root cause analysis / 5 Whys
        if any(term in query_lower for term in ["5 whys", "five whys", "root cause", "why"]):
            results.append({"type": "root_cause", "data": self.data.get("root_cause_analysis", {})})

        # Substitution logic
        if any(term in query_lower for term in ["substitute", "substitution", "out of", "replacement", "egg", "butter", "milk", "sugar", "baking"]):
            results.append({"type": "substitution", "data": self.data.get("substitution_logic", {})})

        # Systems thinking principles
        if any(term in query_lower for term in ["systems thinking", "connected", "feedback loop", "leverage", "system"]):
            results.extend([{"type": "principle", "data": p} for p in self.data.get("systems_thinking_principles", [])])

        # Troubleshooting framework
        if any(term in query_lower for term in ["troubleshoot", "dmaic", "problem solving", "framework"]):
            results.append({"type": "troubleshooting", "data": self.data.get("troubleshooting_framework", {})})

        return results[:5]

    def format_response(self, results):
        """Format systems thinking information for display."""
        if not results:
            return "I don't have specific systems thinking info on that yet."

        output = []

        for result in results:
            if result["type"] == "root_cause":
                rca = result["data"]
                output.append(f"🔍 **{rca['method']}**")
                output.append(f"{rca['description']}\n")
                output.append(f"**How it works:** {rca['how_it_works']}\n")
                
                output.append("**Examples:**\n")
                for ex in rca["examples"][:2]:
                    output.append(f"**Problem:** {ex['problem']}")
                    for why in ex["whys"]:
                        output.append(f"  {why}")
                    output.append(f"  **Root cause:** {ex['root_cause']}")
                    output.append(f"  **Solution:** {ex['solution']}\n")

                output.append("**Tips:**")
                for tip in rca["tips"]:
                    output.append(f"  • {tip}")
                output.append("")

            elif result["type"] == "substitution":
                sub = result["data"]
                output.append(f"🔄 **{sub['category']}**")
                output.append(f"{sub['description']}\n")

                # Show a couple of key ingredients
                for ingredient in ["Eggs", "Butter"]:
                    if ingredient in sub["ingredient_functions"]:
                        ing_data = sub["ingredient_functions"][ingredient]
                        output.append(f"**{ingredient}**")
                        output.append(f"*Functions: {', '.join(ing_data['functions'])}*\n")
                        output.append("Substitutes:")
                        for subst in ing_data["substitutes"][:2]:
                            output.append(f"  • **{subst['substitute']}**")
                            if "ratio" in subst:
                                output.append(f"    Ratio: {subst['ratio']}")
                            output.append(f"    Best for: {subst['best_for']}")
                            output.append(f"    Note: {subst['note']}")
                        output.append("")

                output.append("**General Rules:**")
                for rule in sub["general_rules"]:
                    output.append(f"  • {rule}")
                output.append("")

            elif result["type"] == "principle":
                principle = result["data"]
                output.append(f"🌐 **{principle['principle']}**")
                output.append(f"{principle['description']}\n")
                output.append(f"**Example:** {principle['example']}\n")
                if "application" in principle:
                    output.append(f"**Application:** {principle['application']}\n")
                if "types" in principle:
                    output.append("**Types:**")
                    for ptype, desc in principle["types"].items():
                        output.append(f"  • {ptype}: {desc}")
                    output.append("")

            elif result["type"] == "troubleshooting":
                framework = result["data"]
                output.append(f"🛠️ **{framework['method']}**")
                output.append(f"{framework['description']}\n")
                output.append("**Steps:**\n")
                for step in framework["steps"]:
                    output.append(f"**{step['step']}:** {step['description']}")
                    output.append(f"  Example: {step['example']}")
                output.append("")

        # Add tips
        if len(results) <= 2:
            output.append("💡 **Systems Thinking Tips:**")
            for tip in self.data.get("tips", [])[:3]:
                output.append(f"  • {tip}")

        return "\n".join(output)


if __name__ == "__main__":
    store = SystemsThinkingStore()
    results = store.search("egg substitute baking")
    print(store.format_response(results))
