"""
Storytelling Store: Narrative structures, Hero's Journey, story analysis frameworks.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STORYTELLING_FILE = os.path.join(DATA_DIR, "storytelling.json")


class StorytellingStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(STORYTELLING_FILE):
            with open(STORYTELLING_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_structures()
            self.save()

    def _get_starter_structures(self):
        return {
            "heros_journey": {
                "structure": "The Hero's Journey (Joseph Campbell)",
                "description": "The monomyth—a universal story structure found in myths, movies, and novels across cultures",
                "why_it_works": "Mirrors human psychological transformation: leaving comfort, facing fears, returning changed",
                "stages": [
                    {
                        "act": "Act 1: Departure (The Ordinary World)",
                        "stages": [
                            {
                                "stage": "1. Ordinary World",
                                "description": "Hero's normal life before adventure",
                                "purpose": "Establish baseline, show what hero will risk/lose",
                                "examples": ["Luke on Tatooine (Star Wars)", "Frodo in the Shire (LOTR)", "Neo's boring office job (Matrix)"]
                            },
                            {
                                "stage": "2. Call to Adventure",
                                "description": "Something disrupts the ordinary—a challenge or quest appears",
                                "purpose": "Inciting incident that kicks off the story",
                                "examples": ["Leia's hologram 'Help me, Obi-Wan'", "Gandalf brings the One Ring", "Trinity: 'Follow the white rabbit'"]
                            },
                            {
                                "stage": "3. Refusal of the Call",
                                "description": "Hero hesitates, doubts, or rejects the adventure (optional but common)",
                                "purpose": "Shows stakes are high, hero is relatable (not fearless)",
                                "examples": ["Luke: 'I can't get involved'", "Frodo: 'I wish none of this had happened'", "Neo tries to escape from Morpheus' crew"]
                            },
                            {
                                "stage": "4. Meeting the Mentor",
                                "description": "Wise guide provides advice, training, or magical aid",
                                "purpose": "Gives hero confidence/tools to proceed",
                                "examples": ["Obi-Wan trains Luke", "Gandalf guides Frodo", "Morpheus: 'I can only show you the door'"]
                            },
                            {
                                "stage": "5. Crossing the Threshold",
                                "description": "Hero commits to the journey, leaves ordinary world for special world",
                                "purpose": "Point of no return—story truly begins",
                                "examples": ["Luke leaves Tatooine", "Frodo leaves the Shire", "Neo takes the red pill"]
                            }
                        ]
                    },
                    {
                        "act": "Act 2: Initiation (Tests & Transformation)",
                        "stages": [
                            {
                                "stage": "6. Tests, Allies, Enemies",
                                "description": "Hero faces challenges, makes friends/enemies, learns rules of special world",
                                "purpose": "Training montage, world-building, character development",
                                "examples": ["Luke trains on the Millennium Falcon", "Fellowship forms and travels", "Neo trains in the simulation"]
                            },
                            {
                                "stage": "7. Approach to the Inmost Cave",
                                "description": "Hero nears the central ordeal—tension builds",
                                "purpose": "Calm before the storm, preparation for big confrontation",
                                "examples": ["Sneaking into the Death Star", "Entering Moria/approaching Mordor", "Neo rescued from Agents, prepares to see Oracle"]
                            },
                            {
                                "stage": "8. The Ordeal",
                                "description": "The big battle/crisis—hero faces death (literal or metaphorical)",
                                "purpose": "Midpoint crisis, lowest point, hero must die/transform to proceed",
                                "examples": ["Death Star trash compactor, Obi-Wan dies", "Gandalf falls in Moria", "Neo shot and 'dies'"]
                            },
                            {
                                "stage": "9. Reward (Seizing the Sword)",
                                "description": "Hero survives ordeal, gains treasure/knowledge/power",
                                "purpose": "Payoff for overcoming ordeal, hero is now transformed",
                                "examples": ["Luke escapes with Leia & plans", "Frodo continues with new resolve", "Neo resurrected with Matrix-bending powers"]
                            }
                        ]
                    },
                    {
                        "act": "Act 3: Return (Back to the Ordinary World)",
                        "stages": [
                            {
                                "stage": "10. The Road Back",
                                "description": "Hero begins return journey, but not out of danger yet",
                                "purpose": "Renewed urgency, chase sequence often",
                                "examples": ["Escaping the Death Star with plans", "Escaping Mordor after Ring destroyed", "Neo and Trinity flee Agents"]
                            },
                            {
                                "stage": "11. Resurrection",
                                "description": "Final test—hero must use everything learned, prove transformation",
                                "purpose": "Climax, final showdown, hero demonstrates growth",
                                "examples": ["Luke trusts the Force, destroys Death Star", "Frodo resists Ring's final temptation", "Neo stops bullets, defeats Smith"]
                            },
                            {
                                "stage": "12. Return with the Elixir",
                                "description": "Hero returns home changed, brings wisdom/gift to ordinary world",
                                "purpose": "Resolution, show how hero and world are different",
                                "examples": ["Rebels celebrate, Luke is a hero", "Hobbits return to Shire, wiser", "Neo is 'The One', can save humanity"]
                            }
                        ]
                    }
                ],
                "key_insight": "Not every story hits all 12 stages literally—use it as a flexible template, not a rigid formula",
                "modern_variations": "Movies often compress stages (mentor dies early, skip refusal, etc.). The core pattern: Ordinary → Challenge → Transformation → Return"
            },
            "three_act_structure": {
                "structure": "Three-Act Structure",
                "description": "The foundation of Western storytelling—setup, confrontation, resolution",
                "acts": {
                    "Act 1 (Setup - 25%)": {
                        "purpose": "Introduce characters, world, conflict",
                        "key_beats": [
                            "Opening Image: First impression of hero's world",
                            "Inciting Incident (10-15%): Event that disrupts ordinary life",
                            "Act 1 Break (25%): Hero commits to journey (point of no return)"
                        ],
                        "example": "Star Wars Act 1: Luke on Tatooine → Leia captured → Luke's family killed, joins Obi-Wan"
                    },
                    "Act 2 (Confrontation - 50%)": {
                        "purpose": "Hero pursues goal, faces obstacles, things get worse",
                        "key_beats": [
                            "Midpoint (50%): False victory or defeat—stakes raised",
                            "All Is Lost (75%): Lowest point, hero seems defeated",
                            "Act 2 Break: Hero finds resolve, new information, or plan"
                        ],
                        "example": "Star Wars Act 2: Death Star rescue → Obi-Wan dies (midpoint) → Escape, but Death Star tracks them"
                    },
                    "Act 3 (Resolution - 25%)": {
                        "purpose": "Final confrontation, resolution, new equilibrium",
                        "key_beats": [
                            "Climax: Hero faces biggest challenge with everything they've learned",
                            "Resolution: Conflict resolved, hero changed",
                            "Closing Image: Mirror of opening, shows transformation"
                        ],
                        "example": "Star Wars Act 3: Death Star battle → Luke uses Force → Victory, medal ceremony"
                    }
                },
                "formula": "Setup (introduce) → Confrontation (complicate) → Resolution (resolve)"
            },
            "story_beats": {
                "save_the_cat": {
                    "framework": "Save the Cat Beat Sheet (Blake Snyder)",
                    "description": "15 specific story beats for screenplay structure (great for plotting novels too)",
                    "beats": [
                        "Opening Image: Snapshot of hero's flawed life",
                        "Theme Stated: Someone hints at the lesson hero will learn",
                        "Setup: Introduce hero's world and problems",
                        "Catalyst: Inciting incident (life-changing event)",
                        "Debate: Hero hesitates—should I do this?",
                        "Break into Two: Hero commits, enters new world",
                        "B Story: Subplot begins (often love interest or mentor)",
                        "Fun and Games: The promise of the premise—deliver what trailer showed",
                        "Midpoint: False victory or defeat—stakes raised",
                        "Bad Guys Close In: External/internal pressure mounts",
                        "All Is Lost: Lowest point, 'whiff of death'",
                        "Dark Night of the Soul: Hero wallows, seems truly lost",
                        "Break into Three: Hero gets idea/resolve for final push",
                        "Finale: Hero executes plan, demonstrates growth",
                        "Final Image: Opposite of opening—shows change"
                    ],
                    "when_to_use": "Screenwriting, plotting novels, fixing pacing issues"
                }
            },
            "character_archetypes": {
                "description": "Recurring character types across stories (from Hero's Journey & Carl Jung)",
                "archetypes": [
                    {
                        "archetype": "The Hero",
                        "role": "Protagonist on a journey of growth",
                        "examples": ["Luke Skywalker", "Frodo", "Harry Potter", "Katniss Everdeen"]
                    },
                    {
                        "archetype": "The Mentor",
                        "role": "Wise guide who trains/advises hero",
                        "examples": ["Obi-Wan Kenobi", "Gandalf", "Dumbledore", "Mr. Miyagi"],
                        "fate": "Often dies to force hero to stand alone"
                    },
                    {
                        "archetype": "The Threshold Guardian",
                        "role": "Tests hero's commitment before they can proceed",
                        "examples": ["Bouncers", "gatekeepers", "R2-D2 (tests Luke's resourcefulness)"]
                    },
                    {
                        "archetype": "The Herald",
                        "role": "Brings the call to adventure",
                        "examples": ["Princess Leia's hologram", "Hagrid (Harry Potter)"]
                    },
                    {
                        "archetype": "The Shapeshifter",
                        "role": "Loyalty unclear—ally or enemy?",
                        "examples": ["Severus Snape", "Loki", "romantic interests (keep hero guessing)"]
                    },
                    {
                        "archetype": "The Shadow",
                        "role": "Antagonist—represents hero's dark side or opposite",
                        "examples": ["Darth Vader", "Voldemort", "Sauron", "Joker"]
                    },
                    {
                        "archetype": "The Trickster",
                        "role": "Comic relief, brings chaos, challenges status quo",
                        "examples": ["Han Solo", "Jack Sparrow", "Loki", "Deadpool"]
                    }
                ]
            },
            "story_analysis_questions": [
                "What is the hero's ordinary world? What do they want?",
                "What's the inciting incident? When do they commit to the journey?",
                "Who is the mentor? What wisdom/tool do they provide?",
                "What's the midpoint—when do stakes escalate or false victory/defeat happen?",
                "What's the hero's lowest point (All Is Lost)?",
                "What transformation does the hero undergo? How are they different at the end?",
                "What's the central conflict? Internal (vs. self) or external (vs. villain/world)?",
                "What's the theme? What is the story really ABOUT beneath the plot?",
                "Which archetypes appear? (Hero, Mentor, Shadow, Trickster, etc.)"
            ],
            "writing_tips": [
                "Start with character want vs. need—want is external goal, need is internal growth",
                "Escalate stakes—each obstacle should be harder than the last",
                "Give your villain a compelling motivation—'evil for evil's sake' is boring",
                "Show don't tell—reveal character through actions, not exposition",
                "Subvert expectations carefully—surprise is good, but don't betray genre promises",
                "Kill your darlings—cut scenes/characters that don't serve the story",
                "Read your dialogue out loud—if it sounds unnatural, rewrite it",
                "Theme emerges from character choices—what do they sacrifice? What do they learn?"
            ]
        }

    def save(self):
        with open(STORYTELLING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant storytelling structures."""
        query_lower = query.lower()
        results = []

        # Hero's Journey
        if any(term in query_lower for term in ["hero's journey", "heros journey", "monomyth", "joseph campbell", "hero journey"]):
            results.append({"type": "heros_journey", "data": self.data.get("heros_journey", {})})

        # Three-Act Structure
        if any(term in query_lower for term in ["three act", "3 act", "act structure"]):
            results.append({"type": "three_act", "data": self.data.get("three_act_structure", {})})

        # Save the Cat
        if any(term in query_lower for term in ["save the cat", "beat sheet", "blake snyder"]):
            results.append({"type": "save_the_cat", "data": self.data.get("story_beats", {}).get("save_the_cat", {})})

        # Character archetypes
        if any(term in query_lower for term in ["archetype", "character type", "mentor", "shadow", "trickster"]):
            results.append({"type": "archetypes", "data": self.data.get("character_archetypes", {})})

        # Story analysis
        if any(term in query_lower for term in ["analyze", "analysis", "structure", "movie", "book", "story"]):
            if not results:
                results.append({"type": "heros_journey", "data": self.data.get("heros_journey", {})})
            results.append({"type": "analysis_questions", "data": self.data.get("story_analysis_questions", [])})

        # Writing tips
        if any(term in query_lower for term in ["write", "writing", "tip", "how to"]):
            results.append({"type": "writing_tips", "data": self.data.get("writing_tips", [])})

        return results[:5]

    def format_response(self, results):
        """Format storytelling structures for display."""
        if not results:
            return "I don't have specific storytelling info on that yet."

        output = []

        for result in results:
            if result["type"] == "heros_journey":
                journey = result["data"]
                output.append(f"🗡️ **{journey['structure']}**")
                output.append(f"{journey['description']}\n")
                output.append(f"**Why it works:** {journey['why_it_works']}\n")

                for act in journey["stages"]:
                    output.append(f"**{act['act']}**")
                    for stage in act["stages"]:
                        output.append(f"\n  **{stage['stage']}**")
                        output.append(f"  {stage['description']}")
                        output.append(f"  *Examples:* {', '.join(stage['examples'])}")
                    output.append("")

                output.append(f"💡 **Key insight:** {journey['key_insight']}\n")

            elif result["type"] == "three_act":
                structure = result["data"]
                output.append(f"🎬 **{structure['structure']}**")
                output.append(f"{structure['description']}\n")

                for act_name, act_data in structure["acts"].items():
                    output.append(f"**{act_name}**")
                    output.append(f"Purpose: {act_data['purpose']}")
                    output.append("Key beats:")
                    for beat in act_data["key_beats"]:
                        output.append(f"  • {beat}")
                    output.append(f"Example: {act_data['example']}\n")

                output.append(f"**Formula:** {structure['formula']}\n")

            elif result["type"] == "save_the_cat":
                beats = result["data"]
                output.append(f"📋 **{beats['framework']}**")
                output.append(f"{beats['description']}\n")
                output.append("**The 15 Beats:**")
                for i, beat in enumerate(beats["beats"], 1):
                    output.append(f"  {i}. {beat}")
                output.append(f"\n**When to use:** {beats['when_to_use']}\n")

            elif result["type"] == "archetypes":
                archetypes = result["data"]
                output.append(f"🎭 **Character Archetypes**")
                output.append(f"{archetypes['description']}\n")
                for arch in archetypes["archetypes"]:
                    output.append(f"**{arch['archetype']}**")
                    output.append(f"  Role: {arch['role']}")
                    output.append(f"  Examples: {', '.join(arch['examples'])}")
                    if "fate" in arch:
                        output.append(f"  💀 {arch['fate']}")
                    output.append("")

            elif result["type"] == "analysis_questions":
                output.append("🔍 **Story Analysis Questions:**")
                for question in result["data"]:
                    output.append(f"  • {question}")
                output.append("")

            elif result["type"] == "writing_tips":
                output.append("✍️ **Writing Tips:**")
                for tip in result["data"]:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    store = StorytellingStore()
    results = store.search("hero's journey")
    print(store.format_response(results))
