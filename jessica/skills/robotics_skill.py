"""
Robotics Skill - Natural language interface for robot arm control.

Handles voice commands like:
- "Move to position 100, 200, 150"
- "Save home position"
- "Go to home"
- "List saved positions"
- "What's my reach?"
"""
import logging
import re
from typing import Optional, Dict, Any

from jessica.skills.robotics_ik_solver import (
    RoboticArm3DOF, CartesianPose, JointState, JointStateMemory,
    get_robot_arm, get_joint_state_memory
)

logger = logging.getLogger("jessica.robotics_skill")


def can_handle(intent: Dict) -> bool:
    """
    Determine if this skill can handle the query.
    
    Triggers on:
    - "robot", "arm", "move", "reach"
    - "home", "gripper", "servo"
    - "position", "angles", "joints"
    """
    intent_type = intent.get("intent", "").lower()
    text = (intent.get("text", "") or "").lower()
    
    if intent_type == "robotics":
        return True
    
    robotics_keywords = [
        "robot", "arm", "move", "reach",
        "home", "gripper", "servo",
        "position", "angle", "joint",
        "inverse", "kinematics", "ik"
    ]
    
    return any(keyword in text for keyword in robotics_keywords)


def run(intent: Dict, context: Optional[Dict] = None, relevant=None, manager=None) -> Dict[str, Any]:
    """
    Handle robotics request.
    
    Parses natural language commands for robot control.
    """
    try:
        query = intent.get("text", "").lower()
        
        arm = get_robot_arm()
        memory = get_joint_state_memory()
        
        # Parse command intent
        if _is_move_command(query):
            return _handle_move_command(query, arm, memory)
        
        elif _is_save_command(query):
            return _handle_save_command(query, arm, memory)
        
        elif _is_goto_command(query):
            return _handle_goto_command(query, arm, memory)
        
        elif _is_list_command(query):
            return _handle_list_command(memory)
        
        elif _is_workspace_command(query):
            return _handle_workspace_command(arm)
        
        elif _is_fk_command(query):
            return _handle_fk_command(query, arm)
        
        else:
            return {
                "reply": "I can help with robotics! Try: 'move to 100,200,150' or 'save home position'"
            }
    
    except Exception as e:
        logger.error(f"Robotics skill error: {e}")
        return {
            "reply": f"Error processing robot command: {str(e)}"
        }


def _is_move_command(query: str) -> bool:
    """Check if query is a move command."""
    return any(keyword in query for keyword in ["move", "go to", "reach", "target"])


def _is_save_command(query: str) -> bool:
    """Check if query is a save command."""
    return any(keyword in query for keyword in ["save", "remember", "store"])


def _is_goto_command(query: str) -> bool:
    """Check if query is a goto saved position command."""
    return any(keyword in query for keyword in ["go to", "move to", "return to"]) and \
           any(keyword in query for keyword in ["home", "pick", "place", "safe"])


def _is_list_command(query: str) -> bool:
    """Check if query is a list command."""
    return any(keyword in query for keyword in ["list", "show", "what", "saved"])


def _is_workspace_command(query: str) -> bool:
    """Check if query asks about workspace."""
    return any(keyword in query for keyword in ["workspace", "reach", "limit", "range"])


def _is_fk_command(query: str) -> bool:
    """Check if query is forward kinematics."""
    return any(keyword in query for keyword in ["position", "angles", "joint"]) and \
           any(keyword in query for keyword in ["calculate", "what"])


def _parse_coordinates(query: str) -> Optional[CartesianPose]:
    """
    Extract X, Y, Z coordinates from query.
    
    Supports formats:
    - "100, 200, 150"
    - "100 200 150"
    - "x=100 y=200 z=150"
    """
    # Try comma-separated format
    match = re.search(r'(\d+(?:\.\d+)?)\s*[,]\s*(\d+(?:\.\d+)?)\s*[,]\s*(\d+(?:\.\d+)?)', query)
    if match:
        x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
        return CartesianPose(x, y, z)
    
    # Try space-separated format
    match = re.search(r'(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)', query)
    if match:
        x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
        return CartesianPose(x, y, z)
    
    # Try named format
    match_x = re.search(r'x\s*[=:]\s*(\d+(?:\.\d+)?)', query)
    match_y = re.search(r'y\s*[=:]\s*(\d+(?:\.\d+)?)', query)
    match_z = re.search(r'z\s*[=:]\s*(\d+(?:\.\d+)?)', query)
    
    if match_x and match_y and match_z:
        x = float(match_x.group(1))
        y = float(match_y.group(1))
        z = float(match_z.group(1))
        return CartesianPose(x, y, z)
    
    return None


def _parse_position_name(query: str) -> Optional[str]:
    """Extract position name from query."""
    names = ["home", "pick", "place", "safe", "rest", "idle", "park"]
    
    for name in names:
        if name in query:
            return name
    
    return None


def _handle_move_command(query: str, arm: RoboticArm3DOF, memory: JointStateMemory) -> Dict[str, Any]:
    """Handle move to position command."""
    target = _parse_coordinates(query)
    
    if not target:
        return {
            "reply": "Please specify target position: 'move to 100, 200, 150' (X, Y, Z in mm)"
        }
    
    # Check reachability
    if not arm.is_reachable(target):
        workspace = arm.get_workspace_info()
        return {
            "reply": f"⚠️ Target position unreachable!\n"
                    f"Position: {target}\n"
                    f"Max reach: {workspace['max_reach_mm']:.0f}mm\n"
                    f"Try a position within arm's workspace."
        }
    
    # Solve IK
    joints = arm.inverse_kinematics(target)
    
    if joints is None:
        return {
            "reply": f"❌ Could not solve inverse kinematics for {target}"
        }
    
    # Record position
    memory.record_position(target.x, target.y, target.z, joints, label="move_command")
    
    # Calculate forward kinematics to verify
    calc_pos = arm.forward_kinematics(joints)
    error = ((calc_pos.x - target.x)**2 + (calc_pos.y - target.y)**2 + (calc_pos.z - target.z)**2)**0.5
    
    reply = f"🤖 Moving to position {target}\n\n"
    reply += f"**Joint Angles:**\n"
    reply += f"  • Joint 1 (Base): {joints.joint_1:.1f}°\n"
    reply += f"  • Joint 2 (Shoulder): {joints.joint_2:.1f}°\n"
    reply += f"  • Joint 3 (Elbow): {joints.joint_3:.1f}°\n\n"
    reply += f"**Verification:**\n"
    reply += f"  • Target: {target}\n"
    reply += f"  • Calculated: {calc_pos}\n"
    reply += f"  • Error: {error:.2f}mm\n"
    
    if error > 5.0:
        reply += f"\n⚠️ Position error higher than expected."
    else:
        reply += f"\n✅ Solution verified!"
    
    return {
        "reply": reply,
        "target": target.to_tuple(),
        "joints": joints.to_dict(),
        "error_mm": error
    }


def _handle_save_command(query: str, arm: RoboticArm3DOF, memory: JointStateMemory) -> Dict[str, Any]:
    """Handle save position command."""
    # Try to extract position name
    pos_name = _parse_position_name(query)
    
    if not pos_name:
        # Extract from quoted text
        match = re.search(r'"([^"]+)"', query)
        if match:
            pos_name = match.group(1).lower()
    
    if not pos_name:
        return {
            "reply": "Please specify a name: 'save this as home' or 'remember my pick position'"
        }
    
    # Extract coordinates to create a position
    target = _parse_coordinates(query)
    
    if target:
        # Solve IK for the position
        joints = arm.inverse_kinematics(target)
        if joints is None:
            return {
                "reply": f"❌ Cannot save unreachable position {target}"
            }
    else:
        # If no coordinates, create a default safe position
        # Example: home position at (150, 0, 100)
        target = CartesianPose(150, 0, 100)
        joints = arm.inverse_kinematics(target)
        if joints is None:
            joints = JointState(joint_1=0, joint_2=45, joint_3=90)
    
    # Save to memory
    result = memory.save_joint_state(
        name=pos_name,
        joint_state=joints,
        description=f"Saved position: {pos_name}"
    )
    
    if result['success']:
        return {
            "reply": f"✅ Saved position '{pos_name}'!\n\n"
                    f"**Joint Configuration:**\n"
                    f"  • Joint 1: {joints.joint_1:.1f}°\n"
                    f"  • Joint 2: {joints.joint_2:.1f}°\n"
                    f"  • Joint 3: {joints.joint_3:.1f}°\n\n"
                    f"Say 'go to {pos_name}' to return to this position."
        }
    else:
        return {
            "reply": f"❌ Failed to save position: {result.get('error')}"
        }


def _handle_goto_command(query: str, arm: RoboticArm3DOF, memory: JointStateMemory) -> Dict[str, Any]:
    """Handle go to saved position command."""
    pos_name = _parse_position_name(query)
    
    if not pos_name:
        return {
            "reply": "Which saved position? Try: 'go to home'"
        }
    
    # Load from memory
    joints = memory.load_joint_state(pos_name)
    
    if joints is None:
        saved = memory.list_joint_states()
        if saved:
            names = ", ".join([s['name'] for s in saved])
            return {
                "reply": f"Position '{pos_name}' not found. Saved positions: {names}"
            }
        else:
            return {
                "reply": "No saved positions found. Save one first!"
            }
    
    # Calculate forward kinematics
    target = arm.forward_kinematics(joints)
    
    return {
        "reply": f"🤖 Moving to '{pos_name}' position\n\n"
                f"**Target Position:**\n"
                f"  • X: {target.x:.1f}mm\n"
                f"  • Y: {target.y:.1f}mm\n"
                f"  • Z: {target.z:.1f}mm\n\n"
                f"**Joint Angles:**\n"
                f"  • Joint 1: {joints.joint_1:.1f}°\n"
                f"  • Joint 2: {joints.joint_2:.1f}°\n"
                f"  • Joint 3: {joints.joint_3:.1f}°\n\n"
                f"✅ Moving to {pos_name}",
        "position": pos_name,
        "target": target.to_tuple(),
        "joints": joints.to_dict()
    }


def _handle_list_command(memory: JointStateMemory) -> Dict[str, Any]:
    """Handle list saved positions command."""
    states = memory.list_joint_states()
    
    if not states:
        return {
            "reply": "No saved positions yet. Save one with: 'save this as home'"
        }
    
    reply = "📋 **Saved Robot Positions:**\n\n"
    
    for state in states:
        reply += f"**{state['name'].upper()}**\n"
        reply += f"  • J1: {state['joint_1']:.1f}° | J2: {state['joint_2']:.1f}° | J3: {state['joint_3']:.1f}°\n"
        if state['description']:
            reply += f"  • {state['description']}\n"
        reply += "\n"
    
    return {
        "reply": reply,
        "positions": states
    }


def _handle_workspace_command(arm: RoboticArm3DOF) -> Dict[str, Any]:
    """Handle workspace query."""
    info = arm.get_workspace_info()
    
    reply = "📏 **Arm Workspace Information:**\n\n"
    reply += f"**Reach Limits:**\n"
    reply += f"  • Maximum reach: {info['max_reach_mm']:.0f}mm\n"
    reply += f"  • Minimum reach: {info['min_reach_mm']:.0f}mm\n\n"
    reply += f"**Link Lengths:**\n"
    reply += f"  • Link 1 (base offset): {info['link_lengths']['link_1']:.0f}mm\n"
    reply += f"  • Link 2 (upper arm): {info['link_lengths']['link_2']:.0f}mm\n"
    reply += f"  • Link 3 (forearm): {info['link_lengths']['link_3']:.0f}mm\n\n"
    reply += f"**Joint Limits:**\n"
    reply += f"  • Base (J1): {info['joint_limits']['joint_1']}\n"
    reply += f"  • Shoulder (J2): {info['joint_limits']['joint_2']}\n"
    reply += f"  • Elbow (J3): {info['joint_limits']['joint_3']}"
    
    return {
        "reply": reply,
        "workspace": info
    }


def _handle_fk_command(query: str, arm: RoboticArm3DOF) -> Dict[str, Any]:
    """Handle forward kinematics query."""
    # Extract joint angles
    match = re.search(
        r'(\d+(?:\.\d+)?)\s*[,\s]+(\d+(?:\.\d+)?)\s*[,\s]+(\d+(?:\.\d+)?)',
        query
    )
    
    if not match:
        return {
            "reply": "Please provide joint angles: 'position at 0, 45, 90'"
        }
    
    j1, j2, j3 = float(match.group(1)), float(match.group(2)), float(match.group(3))
    joints = JointState(joint_1=j1, joint_2=j2, joint_3=j3)
    
    pos = arm.forward_kinematics(joints)
    
    return {
        "reply": f"📍 **Forward Kinematics Result:**\n\n"
                f"**Joint Angles:**\n"
                f"  • J1: {j1:.1f}°\n"
                f"  • J2: {j2:.1f}°\n"
                f"  • J3: {j3:.1f}°\n\n"
                f"**End-Effector Position:**\n"
                f"  • X: {pos.x:.1f}mm\n"
                f"  • Y: {pos.y:.1f}mm\n"
                f"  • Z: {pos.z:.1f}mm",
        "position": pos.to_tuple(),
        "joints": joints.to_dict()
    }
