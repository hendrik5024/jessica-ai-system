"""
Home Maintenance: Troubleshooting common household issues.
"""
import json
from pathlib import Path
from typing import Optional, List, Dict

HOME_MAINT_FILE = Path(__file__).resolve().parent.parent / "data" / "home_maintenance.json"

STARTER_HOME_MAINT = {
    "leaky_faucet": {
        "problem": "Leaky faucet (dripping from spout)",
        "common_causes": ["Worn washer", "Corroded valve seat", "O-ring problem", "Worn seals"],
        "diagnosis": [
            "Determine faucet type: compression, ball, cartridge, or ceramic disk.",
            "Turn off water supply under sink.",
            "Check if leak stops - if not, problem is elsewhere in plumbing."
        ],
        "steps": [
            "Turn off water supply valves under sink (turn clockwise).",
            "Close drain stopper to catch small parts.",
            "For compression faucets: Remove handle, unscrew packing nut, remove stem, replace washer and O-ring at bottom.",
            "For cartridge faucets: Remove handle cap, unscrew handle, pull out cartridge, replace cartridge or O-rings.",
            "Apply plumber's grease to new parts before reassembling.",
            "Reassemble in reverse order.",
            "Turn water back on slowly and check for leaks."
        ],
        "tools_needed": ["Adjustable wrench", "Screwdriver", "Replacement washers/O-rings", "Plumber's grease"],
        "when_to_call_pro": "If leak persists after replacing parts, if you can't identify faucet type, or if there's significant corrosion",
        "tags": ["faucet", "leak", "plumbing", "water"]
    },
    "tripped_breaker": {
        "problem": "Tripped circuit breaker",
        "common_causes": ["Circuit overload", "Short circuit", "Ground fault", "Faulty appliance"],
        "diagnosis": [
            "Go to electrical panel/breaker box.",
            "Look for breaker switch in middle position or 'OFF' position.",
            "Try to identify what was running when it tripped."
        ],
        "steps": [
            "Unplug devices or turn off lights on the affected circuit.",
            "Go to breaker panel and find the tripped breaker (will be in middle or OFF position).",
            "Firmly push breaker switch all the way to OFF position first.",
            "Then push it back to ON position.",
            "Listen for a click sound - if it clicks, it should be reset.",
            "If breaker trips immediately when turned on, likely a short circuit - call electrician.",
            "If it holds, gradually reconnect devices one at a time to identify culprit.",
            "If one device trips it again, that device needs service or replacement."
        ],
        "tools_needed": ["Flashlight (if power is out)"],
        "when_to_call_pro": "If breaker trips immediately when reset, if it keeps tripping repeatedly, if you smell burning or see scorch marks, if breaker feels hot",
        "tags": ["breaker", "electrical", "power", "circuit"]
    },
    "clogged_drain": {
        "problem": "Slow or clogged drain (sink or shower)",
        "common_causes": ["Hair buildup", "Soap scum", "Food particles", "Grease buildup"],
        "diagnosis": [
            "Check if multiple drains are slow (main sewer line issue) or just one.",
            "Look into drain with flashlight for visible blockage."
        ],
        "steps": [
            "Start with boiling water: Pour pot of boiling water down drain (not for PVC pipes).",
            "If not cleared, try plunger: Fill sink with enough water to cover plunger cup, plunge vigorously 15-20 times.",
            "Baking soda method: Pour 1/2 cup baking soda down drain, follow with 1/2 cup vinegar, cover for 30 min, flush with hot water.",
            "Remove and clean P-trap: Place bucket under pipe, unscrew slip nuts, remove trap, clean out debris, reassemble.",
            "Use drain snake: Insert into drain, twist to grab hair/debris, pull out.",
            "For prevention: Use drain screens, flush with hot water weekly, avoid pouring grease down drains."
        ],
        "tools_needed": ["Plunger", "Bucket", "Adjustable pliers", "Drain snake (optional)", "Baking soda and vinegar"],
        "when_to_call_pro": "If multiple drains are affected, if nothing works after trying all methods, if you suspect something valuable was dropped in",
        "tags": ["drain", "clog", "plumbing", "sink"]
    },
    "running_toilet": {
        "problem": "Toilet keeps running",
        "common_causes": ["Flapper valve worn out", "Float is set too high", "Fill tube disconnected", "Flush valve issue"],
        "diagnosis": [
            "Remove tank lid and observe water level.",
            "Listen for where water is running - into bowl or overflow tube?"
        ],
        "steps": [
            "Check flapper: Shut off water, flush toilet, watch flapper - if it doesn't seal or has visible wear, replace it.",
            "Adjust float: If water level is above overflow tube, bend float arm down or adjust float screw to lower water level.",
            "Check chain: Ensure chain isn't tangled or too tight (needs 1/2 inch slack).",
            "Check fill tube: Make sure it's attached to overflow tube.",
            "Replace flapper (most common fix): Turn off water, flush to empty tank, unhook old flapper, snap on new one, adjust chain length.",
            "Turn water back on and test flush several times."
        ],
        "tools_needed": ["Replacement flapper ($5-10)", "Sponge", "Towel"],
        "when_to_call_pro": "If problem persists after replacing flapper and adjusting float, if tank or bowl is cracked",
        "tags": ["toilet", "running water", "flapper", "plumbing"]
    },
    "garbage_disposal_jam": {
        "problem": "Garbage disposal is humming but not working",
        "common_causes": ["Foreign object stuck", "Overloaded with food", "Jammed flywheel"],
        "diagnosis": [
            "Turn off and unplug disposal or turn off breaker.",
            "Shine flashlight into disposal - can you see an object?"
        ],
        "steps": [
            "IMPORTANT: Turn off power at breaker or unplug disposal.",
            "Never put your hand in disposal - use tongs or pliers.",
            "Look for foreign objects (utensils, bones, etc.) and remove with tongs.",
            "Insert Allen wrench (hex key) into hex socket at bottom of disposal.",
            "Turn wrench back and forth several times to free up flywheel.",
            "Remove wrench, press red reset button on bottom or side of disposal.",
            "Turn power back on, run cold water, turn on disposal.",
            "If it works, let it run for a minute with cold water."
        ],
        "tools_needed": ["Allen wrench (often included with disposal)", "Flashlight", "Tongs or pliers"],
        "when_to_call_pro": "If motor won't turn even with wrench, if disposal is leaking, if motor is making grinding metal sounds",
        "tags": ["disposal", "garbage disposal", "kitchen", "jam"]
    },
    "no_hot_water": {
        "problem": "No hot water",
        "common_causes": ["Pilot light out (gas)", "Tripped breaker (electric)", "Faulty thermostat", "Heating element failure"],
        "diagnosis": [
            "Check if it's no hot water or just not enough hot water.",
            "Determine if you have gas or electric water heater.",
            "Check if other gas appliances work (gas heater only)."
        ],
        "steps": [
            "For GAS water heater: Look for pilot light viewing window, if out, relight following instructions on heater (usually: turn gas knob to pilot, press down, light with igniter button, hold 30-60 sec).",
            "For ELECTRIC water heater: Check breaker panel - reset tripped breaker if needed.",
            "Check thermostat setting: Should be 120-140°F.",
            "If pilot won't stay lit (gas): Thermocouple may need replacement - call pro.",
            "Test by running hot water for 5 minutes - should start warming up.",
            "If still no hot water after 30-60 minutes, likely heating element or thermostat issue."
        ],
        "tools_needed": ["Screwdriver (to access panels)", "Flashlight"],
        "when_to_call_pro": "If pilot light won't stay lit, if breaker keeps tripping, if water heater is leaking, if you smell gas",
        "tags": ["water heater", "hot water", "pilot light", "thermostat"]
    },
    "door_wont_close": {
        "problem": "Door won't close or latch properly",
        "common_causes": ["House settling", "Loose hinges", "Misaligned strike plate", "Warped door", "Paint buildup"],
        "diagnosis": [
            "Close door slowly to see where it's sticking.",
            "Check if latch aligns with strike plate hole.",
            "Look for loose or sagging hinges."
        ],
        "steps": [
            "Check hinges: Tighten all screws with screwdriver. If screw spins, replace with longer screws or use wooden matchstick + glue to fill hole.",
            "Check latch alignment: Close door and mark where latch hits strike plate. If off, remove strike plate, file hole larger or move plate up/down.",
            "If door is sticking at top: Tighten top hinge or place cardboard shim behind bottom hinge to push bottom out.",
            "If door is sticking at bottom: Tighten bottom hinge or shim behind top hinge.",
            "For minor warping: Plane or sand high spots (mark with pencil where rubbing occurs).",
            "Check for paint buildup: Sand or scrape excess paint from edges."
        ],
        "tools_needed": ["Screwdriver", "Longer screws", "File or sandpaper", "Pencil", "Hammer (for shims)"],
        "when_to_call_pro": "If door is severely warped, if frame is damaged, if problem persists after adjustments",
        "tags": ["door", "latch", "hinges", "alignment"]
    },
    "hvac_not_working": {
        "problem": "Air conditioning or heating not working",
        "common_causes": ["Dirty filter", "Thermostat issues", "Tripped breaker", "Frozen coils (AC)", "Pilot light out (furnace)"],
        "diagnosis": [
            "Check thermostat: Is it set correctly? Are batteries fresh?",
            "Listen for system - is it running at all?",
            "Feel vents - is any air coming out?"
        ],
        "steps": [
            "Check and replace air filter if dirty (do this monthly during heavy use).",
            "Check thermostat: Replace batteries if needed, ensure it's set to heat/cool with temp above/below current temp by 5°F.",
            "Check breaker panel: Reset any tripped breakers.",
            "For AC: Check outdoor unit - is it running? Clear debris from around unit (2 ft clearance needed).",
            "For AC: Check if coils are frozen - turn off system, turn fan to ON, let ice melt (several hours).",
            "For furnace: Check pilot light - relight if out following manufacturer instructions.",
            "Check vents: Ensure all supply and return vents are open and unobstructed.",
            "Reset system: Turn off at thermostat, wait 5 minutes, turn back on."
        ],
        "tools_needed": ["Replacement air filter", "Screwdriver"],
        "when_to_call_pro": "If system doesn't turn on at all, if outdoor unit won't run, if you smell gas, if coils keep freezing, if strange noises persist",
        "tags": ["HVAC", "air conditioning", "heating", "furnace", "thermostat"]
    }
}


class HomeMaintenanceStore:
    def __init__(self):
        self.path = HOME_MAINT_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.maintenance = self._load()
        
        if not self.maintenance:
            self.maintenance = STARTER_HOME_MAINT.copy()
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
            json.dump(self.maintenance, f, indent=2, ensure_ascii=False)

    def search(self, query: str) -> List[Dict]:
        """Search maintenance guides by keywords."""
        query_lower = query.lower()
        results = []
        
        for maint_id, item in self.maintenance.items():
            problem = item.get("problem", "").lower()
            causes = " ".join(item.get("common_causes", [])).lower()
            tags = [t.lower() for t in item.get("tags", [])]
            
            if (query_lower in problem or 
                query_lower in causes or
                any(query_lower in tag for tag in tags)):
                results.append({"id": maint_id, **item})
        
        return results

    def format_guide(self, item: dict) -> str:
        """Format maintenance guide for display."""
        lines = [
            f"🔧 {item['problem'].upper()}",
            f"\n🔍 Common causes: {', '.join(item.get('common_causes', []))}",
            "\n📋 Troubleshooting steps:"
        ]
        
        for i, step in enumerate(item.get("steps", []), 1):
            lines.append(f"  {i}. {step}")
        
        lines.append(f"\n🧰 Tools needed: {', '.join(item.get('tools_needed', []))}")
        lines.append(f"\n⚠️ Call a professional if: {item.get('when_to_call_pro', 'Problem persists')}")
        
        return "\n".join(lines)
