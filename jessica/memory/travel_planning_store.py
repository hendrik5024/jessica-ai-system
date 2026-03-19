"""
Travel Planning Store: Itineraries, destination guides, and travel logic.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRAVEL_PLANNING_FILE = os.path.join(DATA_DIR, "travel_planning.json")


class TravelPlanningStore:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(TRAVEL_PLANNING_FILE):
            with open(TRAVEL_PLANNING_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_starter_knowledge()
            self.save()

    def _get_starter_knowledge(self):
        return {
            "destinations": [
                {
                    "city": "Tokyo, Japan",
                    "vibe": "Tech-forward, quiet coffee culture, organized chaos",
                    "for_crowd_avoiders": {
                        "neighborhoods": ["Shimokitazawa (indie cafes)", "Nakameguro (canal walks)", "Kichijoji (parks, local feel)"],
                        "avoid": ["Shibuya crossing on weekends", "Harajuku Takeshita Street", "Tsukiji at peak hours"],
                        "timing": "Visit shrines early morning (7-8am), museums on weekdays, dinner after 8pm"
                    },
                    "for_coffee_lovers": [
                        "Blue Bottle Shinjuku - minimalist Japanese roastery",
                        "Fuglen Tokyo - Norwegian coffee bar",
                        "Onibus Coffee - micro-roaster in Nakameguro",
                        "Streamer Coffee - latte art champions"
                    ],
                    "3_day_itinerary": {
                        "day_1": "Morning: teamLab Borderless (10am opening, less crowded). Lunch: Quiet sushi spot in Ginza. Afternoon: Meiji Shrine (peaceful). Evening: Shimokitazawa cafe hopping.",
                        "day_2": "Morning: Tsukiji Outer Market (go at 8am). Coffee: Blue Bottle. Afternoon: Ueno Park museums. Evening: Nakameguro riverside walk + dinner.",
                        "day_3": "Day trip: Kamakura (seaside town, giant Buddha, fewer tourists than Kyoto). Coffee at Verve Coffee Roasters Kamakura."
                    },
                    "insider_tip": "Buy a Suica card for trains—less stressful than tickets. Stay in Nakameguro or Kichijoji for quieter vibes."
                },
                {
                    "city": "Lisbon, Portugal",
                    "vibe": "Laid-back, coastal, affordable, historic",
                    "perfect_for": "Coffee culture, walkable hills, sunset views, slow travel",
                    "3_day_itinerary": {
                        "day_1": "Morning: Alfama district (oldest neighborhood, Fado music). Lunch: Time Out Market. Afternoon: Tram 28 to Graça viewpoint. Evening: Sunset at Miradouro de Santa Catarina.",
                        "day_2": "Day trip: Sintra (fairytale palaces). Visit Pena Palace early to avoid crowds. Lunch in Cascais (seaside town). Return for dinner in Bairro Alto.",
                        "day_3": "Morning: Belém (Jerónimos Monastery, pastéis de nata). Afternoon: LX Factory (hipster creative hub). Evening: Rooftop bar in Chiado."
                    },
                    "coffee_spots": ["Fábrica Coffee Roasters", "Copenhagen Coffee Lab", "Heim Café"],
                    "insider_tip": "Get pastéis de nata from Pastéis de Belém (original recipe). Avoid tourist traps in Rossio—eat where locals eat."
                },
                {
                    "city": "Reykjavik, Iceland",
                    "vibe": "Nature-first, small-town feel, midnight sun or northern lights",
                    "perfect_for": "Solitude seekers, nature lovers, unique experiences",
                    "3_day_itinerary": {
                        "day_1": "Morning: Reykjavik city walk (Hallgrímskirkja church, Harpa concert hall). Afternoon: Blue Lagoon (book in advance). Evening: Dinner at Grillmarkaðurinn.",
                        "day_2": "Golden Circle tour (Þingvellir National Park, Geysir, Gullfoss waterfall). Soak in Secret Lagoon (less touristy than Blue Lagoon).",
                        "day_3": "South Coast: Black sand beaches (Reynisfjara), Skógafoss waterfall, Sólheimasandur plane wreck. Return for northern lights hunt (if winter)."
                    },
                    "insider_tip": "Rent a car—public transport is limited. Pack layers (weather changes fast). Book everything in advance (small country, fills up)."
                }
            ],
            "planning_frameworks": [
                {
                    "framework": "Vibe-Based Planning",
                    "description": "Design trips around feelings, not just sights",
                    "steps": [
                        "Define the vibe: Relaxing? Adventurous? Cultural? Party? Solo reflection?",
                        "Choose destination that matches energy level",
                        "Build itinerary around pace (slow travel vs. packed days)",
                        "Leave buffer time—over-scheduling kills the vibe"
                    ],
                    "examples": {
                        "Chill & Coffee": "Lisbon, Portland, Melbourne—walkable, cafe culture, slow mornings",
                        "Adventure & Nature": "Patagonia, New Zealand, Iceland—hiking, solitude, epic landscapes",
                        "Culture & History": "Rome, Kyoto, Istanbul—museums, temples, ancient sites",
                        "Party & Social": "Barcelona, Bangkok, Berlin—nightlife, hostels, group activities"
                    }
                },
                {
                    "framework": "3-Day Itinerary Template",
                    "structure": {
                        "Day 1": "City orientation—main sights, get bearings, adjust to timezone",
                        "Day 2": "Day trip or deep dive into one neighborhood",
                        "Day 3": "Hidden gems, local experiences, pack & reflect"
                    },
                    "daily_rhythm": "Morning (explore), Afternoon (eat + activity), Evening (relax + dinner + nightlife if desired)",
                    "rest_rule": "Build in 2-3 hours of downtime per day—travel exhaustion is real"
                }
            ],
            "travel_tips": [
                {
                    "category": "Avoiding Crowds",
                    "tips": [
                        "Visit major attractions at opening time (first 30 min are quietest)",
                        "Eat lunch at 11:30am or 1:30pm (avoid noon rush)",
                        "Book weekday flights and accommodations (cheaper + less crowded)",
                        "Use Google Maps 'Popular times' feature to plan visits"
                    ]
                },
                {
                    "category": "Packing Light",
                    "tips": [
                        "Capsule wardrobe: 3 tops, 2 bottoms, 1 jacket, 1 pair shoes (mix & match)",
                        "Wear bulkiest items on plane (jacket, boots)",
                        "Roll clothes, use packing cubes",
                        "Bring laundry detergent sheets—wash as you go"
                    ]
                },
                {
                    "category": "Budget Travel",
                    "tips": [
                        "Book flights on Tuesdays/Wednesdays (cheapest days)",
                        "Use Hopper or Google Flights price alerts",
                        "Stay in neighborhoods, not tourist centers (cheaper + authentic)",
                        "Eat where locals eat—street food and lunch specials",
                        "Free walking tours in most cities (tip-based)"
                    ]
                },
                {
                    "category": "Solo Travel",
                    "tips": [
                        "Stay in hostels (social) or boutique hotels (quiet but safe)",
                        "Join group tours for activities (meet people without commitment)",
                        "Tell someone your itinerary, check in daily",
                        "Trust your gut—if something feels off, leave"
                    ]
                }
            ],
            "destination_finder": {
                "loves_coffee": ["Melbourne", "Tokyo", "Lisbon", "Portland", "Seattle", "Vienna"],
                "hates_crowds": ["Iceland", "Faroe Islands", "Slovenia", "Estonia", "Uruguay", "Namibia"],
                "budget_friendly": ["Vietnam", "Portugal", "Mexico", "Poland", "Thailand", "Colombia"],
                "nature_focused": ["New Zealand", "Patagonia", "Norway", "Costa Rica", "Swiss Alps"],
                "city_culture": ["Paris", "Rome", "Kyoto", "Istanbul", "Barcelona", "Berlin"],
                "beach_relaxation": ["Maldives", "Bali", "Greece", "Croatia", "Seychelles", "Zanzibar"]
            },
            "general_tips": [
                "Book major things (flights, hotels, tours) in advance. Leave days flexible.",
                "Download offline maps (Google Maps lets you save areas)",
                "Learn 5 phrases: Hello, thank you, where is, how much, excuse me",
                "Take photos of important docs (passport, insurance) and email to yourself",
                "Don't over-plan—some of the best experiences are spontaneous"
            ]
        }

    def save(self):
        with open(TRAVEL_PLANNING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def search(self, query):
        """Search for relevant travel information."""
        query_lower = query.lower()
        results = []

        # Specific destinations
        for dest in self.data.get("destinations", []):
            if dest["city"].lower() in query_lower:
                results.append({"type": "destination", "data": dest})

        # Vibe-based search
        vibes = {
            "coffee": "loves_coffee",
            "crowd": "hates_crowds",
            "budget": "budget_friendly",
            "nature": "nature_focused",
            "city": "city_culture",
            "beach": "beach_relaxation"
        }
        for keyword, category in vibes.items():
            if keyword in query_lower:
                results.append({"type": "destination_list", "category": category, "data": self.data["destination_finder"][category]})

        # Planning frameworks
        if any(term in query_lower for term in ["plan", "itinerary", "trip", "how to"]):
            results.extend([{"type": "framework", "data": fw} for fw in self.data.get("planning_frameworks", [])])

        # Travel tips
        if any(term in query_lower for term in ["tip", "avoid crowd", "pack", "budget", "solo"]):
            results.extend([{"type": "tips", "data": tip} for tip in self.data.get("travel_tips", [])])

        # General tips
        if not results or "tip" in query_lower:
            results.append({"type": "general_tips", "data": self.data.get("general_tips", [])})

        return results[:5]

    def format_response(self, results):
        """Format travel knowledge for display."""
        if not results:
            return "I don't have specific travel information on that yet. Try asking about destinations, planning tips, or travel vibes!"

        output = []

        for result in results:
            if result["type"] == "destination":
                dest = result["data"]
                output.append(f"✈️ **{dest['city']}**")
                output.append(f"*Vibe: {dest['vibe']}*\n")

                if "perfect_for" in dest:
                    output.append(f"**Perfect for:** {dest['perfect_for']}\n")

                if "for_crowd_avoiders" in dest:
                    avoid = dest["for_crowd_avoiders"]
                    output.append("**Avoiding Crowds:**")
                    output.append(f"  • Neighborhoods: {', '.join(avoid['neighborhoods'])}")
                    output.append(f"  • Avoid: {', '.join(avoid['avoid'])}")
                    output.append(f"  • Timing: {avoid['timing']}\n")

                if "for_coffee_lovers" in dest:
                    output.append("**Coffee Spots:**")
                    for spot in dest["for_coffee_lovers"]:
                        output.append(f"  ☕ {spot}")
                    output.append("")

                if "3_day_itinerary" in dest:
                    output.append("**3-Day Itinerary:**")
                    for day, plan in dest["3_day_itinerary"].items():
                        output.append(f"  **{day.replace('_', ' ').title()}:** {plan}")
                    output.append("")

                if "insider_tip" in dest:
                    output.append(f"💡 **Insider tip:** {dest['insider_tip']}\n")

            elif result["type"] == "destination_list":
                output.append(f"🗺️ **Destinations for {result['category'].replace('_', ' ').title()}:**")
                output.append("  " + ", ".join(result["data"]))
                output.append("")

            elif result["type"] == "framework":
                fw = result["data"]
                output.append(f"📋 **{fw['framework']}**")
                output.append(f"{fw['description']}\n")

                if "steps" in fw:
                    output.append("**Steps:**")
                    for step in fw["steps"]:
                        output.append(f"  • {step}")
                    output.append("")

                if "examples" in fw:
                    output.append("**Vibe Examples:**")
                    for vibe, dests in fw["examples"].items():
                        output.append(f"  **{vibe}:** {dests}")
                    output.append("")

                if "structure" in fw:
                    output.append("**Structure:**")
                    for day, plan in fw["structure"].items():
                        output.append(f"  **{day}:** {plan}")
                    output.append("")

            elif result["type"] == "tips":
                tip = result["data"]
                output.append(f"💡 **{tip['category']}:**")
                for point in tip["tips"]:
                    output.append(f"  • {point}")
                output.append("")

            elif result["type"] == "general_tips":
                output.append("🌍 **General Travel Tips:**")
                for tip in result["data"]:
                    output.append(f"  • {tip}")
                output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    store = TravelPlanningStore()
    results = store.search("plan a trip to Tokyo for someone who hates crowds but loves coffee")
    print(store.format_response(results))
