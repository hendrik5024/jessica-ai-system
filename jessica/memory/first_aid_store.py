"""
First Aid: Basic emergency response guidance.
DISCLAIMER: This is for informational purposes only. Always call emergency services for serious injuries.
"""
import json
from pathlib import Path
from typing import Optional, List, Dict

FIRST_AID_FILE = Path(__file__).resolve().parent.parent / "data" / "first_aid.json"

STARTER_FIRST_AID = {
    "choking_adult": {
        "emergency": "Adult choking",
        "signs": "Cannot cough, speak, or breathe; clutching throat; turning blue",
        "steps": [
            "Ask 'Are you choking?' If they nod and can't speak, proceed.",
            "Call 911 or have someone else call.",
            "Stand behind them, wrap arms around waist.",
            "Make a fist above their navel, below ribcage.",
            "Grasp fist with other hand and thrust inward and upward sharply.",
            "Repeat thrusts until object dislodges or person becomes unconscious.",
            "If unconscious, lower to ground and begin CPR."
        ],
        "warnings": ["Never perform if person can cough or speak", "Call 911 immediately for severe cases"],
        "tags": ["choking", "emergency", "heimlich"]
    },
    "minor_burns": {
        "emergency": "Minor burns (first or second degree)",
        "signs": "Redness, pain, blistering on small area (less than 3 inches)",
        "steps": [
            "Remove from heat source immediately.",
            "Cool burn under cool (not cold) running water for 10-15 minutes.",
            "Remove jewelry or tight items before swelling begins.",
            "Do NOT apply ice, butter, or ointments initially.",
            "Cover with sterile, non-stick bandage or clean cloth.",
            "Take over-the-counter pain reliever if needed.",
            "Keep burn elevated if possible to reduce swelling.",
            "Do NOT pop blisters - leave intact to prevent infection."
        ],
        "warnings": ["Seek medical attention for: burns larger than 3 inches, on face/hands/feet/joints/groin, third-degree burns (white or charred), chemical or electrical burns", "Watch for signs of infection: increased pain, redness, swelling, pus"],
        "tags": ["burns", "fire", "heat"]
    },
    "sprained_ankle": {
        "emergency": "Sprained ankle",
        "signs": "Pain, swelling, bruising, difficulty walking",
        "steps": [
            "RICE protocol: Rest, Ice, Compression, Elevation",
            "Rest: Stop activity immediately, avoid putting weight on ankle.",
            "Ice: Apply ice pack for 15-20 minutes every 2-3 hours for first 48 hours.",
            "Compression: Wrap with elastic bandage (not too tight - should not cause numbness).",
            "Elevation: Keep ankle elevated above heart level when sitting or lying.",
            "Take anti-inflammatory medication (ibuprofen) as directed.",
            "Use crutches if walking is painful.",
            "After 48-72 hours, gentle range-of-motion exercises."
        ],
        "warnings": ["See doctor if: severe pain, can't bear any weight, significant swelling/bruising, numbness or tingling, no improvement after 5-7 days"],
        "tags": ["sprain", "ankle", "injury", "RICE"]
    },
    "nosebleed": {
        "emergency": "Nosebleed",
        "signs": "Bleeding from nose",
        "steps": [
            "Sit upright and lean forward slightly (NOT back).",
            "Pinch soft part of nose (just below the bridge) firmly.",
            "Hold for 10-15 minutes without releasing to check.",
            "Breathe through mouth.",
            "Apply cold compress to bridge of nose.",
            "After bleeding stops, avoid blowing nose for several hours.",
            "Keep head elevated and avoid strenuous activity for rest of day."
        ],
        "warnings": ["Seek medical help if: bleeding doesn't stop after 20 minutes, caused by head injury, accompanied by difficulty breathing, you're on blood thinners"],
        "tags": ["nosebleed", "bleeding"]
    },
    "cuts_scrapes": {
        "emergency": "Minor cuts and scrapes",
        "signs": "Shallow wound, minimal bleeding",
        "steps": [
            "Wash hands thoroughly with soap and water.",
            "Apply gentle pressure with clean cloth to stop bleeding (5-10 min).",
            "Clean wound with cool water, remove debris gently.",
            "Apply antibiotic ointment (like Neosporin).",
            "Cover with sterile bandage or gauze.",
            "Change bandage daily and when it gets wet or dirty.",
            "Watch for signs of infection over next few days."
        ],
        "warnings": ["Seek medical help if: deep cut (might need stitches), won't stop bleeding after 10 min pressure, caused by rusty or dirty object (tetanus risk), shows signs of infection (redness, warmth, pus, red streaks)"],
        "tags": ["cuts", "scrapes", "wounds"]
    },
    "bee_sting": {
        "emergency": "Bee or wasp sting",
        "signs": "Pain, redness, swelling at sting site",
        "steps": [
            "Remove stinger quickly by scraping with credit card edge (don't pinch).",
            "Wash area with soap and water.",
            "Apply cold compress or ice pack for 15-20 minutes.",
            "Take antihistamine (Benadryl) to reduce swelling and itching.",
            "Apply hydrocortisone cream or calamine lotion.",
            "Keep area elevated if possible.",
            "Avoid scratching to prevent infection."
        ],
        "warnings": ["CALL 911 IMMEDIATELY if signs of severe allergic reaction: difficulty breathing, swelling of face/throat/tongue, rapid pulse, dizziness, hives all over body"],
        "tags": ["sting", "bee", "insect", "allergic reaction"]
    },
    "heat_exhaustion": {
        "emergency": "Heat exhaustion",
        "signs": "Heavy sweating, weakness, cold/pale/clammy skin, nausea, fainting, headache",
        "steps": [
            "Move to cool, air-conditioned place immediately.",
            "Lie down and elevate legs slightly.",
            "Remove tight or heavy clothing.",
            "Apply cool, wet cloths or take cool shower.",
            "Drink water or sports drink with electrolytes (sip slowly).",
            "Do NOT give sugary or alcoholic drinks.",
            "Rest and monitor for at least 30 minutes."
        ],
        "warnings": ["CALL 911 if: symptoms last longer than 1 hour, vomiting occurs and can't keep fluids down, progresses to heat stroke (hot/red/dry skin, confusion, unconsciousness)"],
        "tags": ["heat", "exhaustion", "dehydration"]
    },
    "splinter": {
        "emergency": "Removing a splinter",
        "signs": "Small foreign object embedded in skin",
        "steps": [
            "Wash hands and clean area with soap and water.",
            "Sterilize tweezers with rubbing alcohol.",
            "If splinter protrudes above skin, grasp with tweezers and pull at same angle it entered.",
            "If embedded: sterilize needle with alcohol, gently expose end of splinter, then remove with tweezers.",
            "After removal, wash area again with soap and water.",
            "Apply antibiotic ointment and bandage.",
            "Watch for signs of infection over next few days."
        ],
        "warnings": ["See doctor if: splinter is deep, large, or made of glass, unable to remove completely, in sensitive area (eye, under nail), signs of infection develop"],
        "tags": ["splinter", "foreign object"]
    }
}


class FirstAidStore:
    def __init__(self):
        self.path = FIRST_AID_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.first_aid = self._load()
        
        if not self.first_aid:
            self.first_aid = STARTER_FIRST_AID.copy()
            self.save()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.load(open(self.path, "r", encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.first_aid, f, indent=2, ensure_ascii=False)

    def search(self, query: str) -> List[Dict]:
        """Search first aid guidance by keywords."""
        query_lower = query.lower()
        results = []
        
        for aid_id, item in self.first_aid.items():
            emergency = item.get("emergency", "").lower()
            signs = item.get("signs", "").lower()
            tags = [t.lower() for t in item.get("tags", [])]
            
            if (query_lower in emergency or 
                query_lower in signs or
                any(query_lower in tag for tag in tags)):
                results.append({"id": aid_id, **item})
        
        return results

    def format_guidance(self, item: dict) -> str:
        """Format first aid guidance for display."""
        lines = [
            f"🚨 {item['emergency'].upper()}",
            f"\n⚠️ Signs: {item['signs']}",
            "\n📋 Steps:"
        ]
        
        for i, step in enumerate(item.get("steps", []), 1):
            lines.append(f"  {i}. {step}")
        
        if item.get("warnings"):
            lines.append("\n⚠️ WARNING:")
            for warning in item["warnings"]:
                lines.append(f"  • {warning}")
        
        lines.append("\n⚕️ This is NOT a substitute for professional medical care. Call 911 for emergencies.")
        
        return "\n".join(lines)
