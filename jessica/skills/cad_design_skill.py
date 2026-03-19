"""
CAD Design Skill - Natural language interface to Jessica CAD system.

Handles voice/text commands like:
- "Design a 40x40 bracket with a 5mm hole"
- "Generate a box 50x50x20"
- "Create a part 100x100x50"

Uses functional pattern matching Jessica's architecture.
"""
import logging
import re
from typing import Optional, Dict, Any

from jessica.skills.cad_skill import JessicaCAD, get_jessica_cad

logger = logging.getLogger("jessica.cad_design_skill")


def can_handle(intent: Dict) -> bool:
    """
    Determine if this skill can handle the query.
    
    Triggers on:
    - "cad", "design", "create", "generate"
    - "bracket", "box", "part", "stl"
    - "3d", "print", "hole", "drill"
    """
    intent_type = intent.get("intent", "").lower()
    text = (intent.get("text", "") or "").lower()
    
    # Check if explicit CAD intent
    if intent_type == "cad":
        return True
    
    cad_keywords = [
        "design", "create", "generate",
        "bracket", "box", "part",
        "cad", "3d", "stl",
        "hole", "drill", "print",
        "parametric"
    ]
    
    return any(keyword in text for keyword in cad_keywords)


def run(intent: Dict, context: Optional[Dict] = None, relevant=None, manager=None) -> Dict[str, Any]:
    """
    Handle CAD design request.
    
    Parses natural language to extract dimensions and features,
    then generates the 3D model.
    """
    try:
        query = intent.get("text", "")
        cad = get_jessica_cad(output_dir="./cad_output")
        
        # Parse the query for dimensions and features
        parsed = _parse_cad_request(query)
        
        if not parsed['success']:
            return {
                "reply": "I couldn't understand the design request. Please specify dimensions like '40x40x20' and hole size if needed."
            }
        
        # Generate the part
        result = cad.generate_parametric_part(
            length=parsed['length'],
            width=parsed['width'],
            height=parsed['height'],
            hole_diameter=parsed['hole_diameter'],
            hole_depth=parsed['hole_depth'],
            part_name=parsed['part_name']
        )
        
        if not result['success']:
            return {
                "reply": f"CAD generation failed: {result.get('error', 'Unknown error')}"
            }
        
        # Validate the generated model
        validation = cad.validate_stl_watertight(result['file_path'])
        
        # Build response
        filename = result['filename']
        dims = f"{parsed['length']}x{parsed['width']}x{parsed['height']}mm"
        hole_info = f", {parsed['hole_diameter']}mm hole" if parsed['hole_diameter'] > 0 else ""
        
        reply = f"✨ Created your design! Generated **{filename}**\n"
        reply += f"📦 Dimensions: {dims}{hole_info}\n"
        
        if validation['success']:
            if validation['ready_for_print']:
                reply += f"🖨️ **Ready for 3D printing!** Model is watertight.\n"
                reply += f"   • Volume: {validation['volume_cm3']} cm³\n"
                reply += f"   • Surface area: {validation['surface_area_cm2']} cm²\n"
            else:
                reply += f"⚠️ Model has issues - review before printing\n"
                for warning in validation['warnings']:
                    reply += f"   • {warning}\n"
        
        reply += f"📂 Saved to: `{result['file_path']}`"
        
        return {
            "reply": reply,
            "file_path": result['file_path'],
            "validation": validation
        }
        
    except Exception as e:
        logger.error(f"CAD design error: {e}")
        return {
            "reply": f"Error generating design: {str(e)}"
        }


def _parse_cad_request(query: str) -> Dict[str, Any]:
    """
    Parse natural language CAD request to extract dimensions.
    
    Looks for patterns like:
    - "40x40x20" or "40 x 40 x 20"
    - "5mm hole" or "hole 5"
    - "bracket", "box", "part" (for naming)
    
    Returns dict with:
    - 'success': bool
    - 'length', 'width', 'height': float (mm)
    - 'hole_diameter': float (mm)
    - 'hole_depth': Optional[float]
    - 'part_name': str
    """
    query_lower = query.lower()
    
    # Default values
    length = width = height = 40.0
    hole_diameter = 0.0
    hole_depth = None
    part_name = "design"
    
    try:
        # Extract dimensions: "40x40x20" or "40 x 40 x 20" or "40, 40, 20"
        dim_patterns = [
            r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',  # 40x40x20
            r'(\d+(?:\.\d+)?)\s*[,]\s*(\d+(?:\.\d+)?)\s*[,]\s*(\d+(?:\.\d+)?)',  # 40, 40, 20
        ]
        
        for pattern in dim_patterns:
            match = re.search(pattern, query)
            if match:
                length = float(match.group(1))
                width = float(match.group(2))
                height = float(match.group(3))
                break
        
        # Extract hole diameter: "5mm hole", "hole 5", "5mm diameter"
        hole_patterns = [
            r'(\d+(?:\.\d+)?)\s*mm\s*hole',
            r'hole\s*(?:diameter\s+)?(\d+(?:\.\d+)?)',
            r'drill\s*(?:a\s+)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*mm\s*(?:hole|drill)',
        ]
        
        for pattern in hole_patterns:
            match = re.search(pattern, query)
            if match:
                hole_diameter = float(match.group(1))
                break
        
        # Extract hole depth if specified
        hole_depth_pattern = r'hole\s+depth\s+(\d+(?:\.\d+)?)'
        depth_match = re.search(hole_depth_pattern, query)
        if depth_match:
            hole_depth = float(depth_match.group(1))
        
        # Determine part name from context
        if 'bracket' in query_lower:
            part_name = "bracket"
        elif 'box' in query_lower:
            part_name = "box"
        elif 'mount' in query_lower:
            part_name = "mount"
        elif 'plate' in query_lower:
            part_name = "plate"
        
        return {
            'success': True,
            'length': length,
            'width': width,
            'height': height,
            'hole_diameter': hole_diameter,
            'hole_depth': hole_depth,
            'part_name': part_name
        }
        
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return {'success': False}
