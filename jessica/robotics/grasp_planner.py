"""
Grasp Planning System

Generates grasp poses for robotic manipulation based on object
geometry, material properties, and task requirements.

Key capabilities:
- Grasp pose generation (6-DOF poses)
- Grasp quality metrics (stability, robustness)
- Multiple grasp candidates (ranked by quality)
- Collision checking
- Integration with IK solver and visual servoing
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

# Import from other modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from robotics.hand_eye_calibration import Pose
from perception.object_detector import DetectedObject, BoundingBox


class GraspType(Enum):
    """Types of grasps"""
    TOP_DOWN = "top_down"  # Grasp from above
    SIDE = "side"  # Grasp from side
    PINCH = "pinch"  # Two-finger pinch
    POWER = "power"  # Full-hand grasp


@dataclass
class GraspPose:
    """6-DOF grasp pose with quality metrics"""
    pose: Pose  # End-effector pose for grasp
    grasp_type: GraspType
    approach_vector: np.ndarray  # Direction to approach object
    quality_score: float  # 0-1, higher is better
    stability_score: float  # Resistance to disturbance
    collision_free: bool
    gripper_width: float  # Required gripper opening (meters)
    
    def __lt__(self, other):
        """For sorting by quality"""
        return self.quality_score < other.quality_score


@dataclass
class ObjectGeometry:
    """Simplified object geometry for grasp planning"""
    center: np.ndarray  # [x, y, z]
    dimensions: np.ndarray  # [width, height, depth]
    orientation: np.ndarray  # Rotation matrix 3x3
    class_name: str


class GraspPlanner:
    """
    Generate and rank grasp candidates for object manipulation
    
    Uses analytical methods for common object shapes.
    For production, integrate learning-based methods (GraspNet, etc.)
    """
    
    def __init__(
        self,
        gripper_max_width: float = 0.08,  # 8cm
        min_grasp_quality: float = 0.3
    ):
        self.gripper_max_width = gripper_max_width
        self.min_grasp_quality = min_grasp_quality
        
        # Grasp heuristics per object class
        self.class_preferences = {
            "cup": GraspType.SIDE,
            "bottle": GraspType.SIDE,
            "screwdriver": GraspType.SIDE,
            "wrench": GraspType.SIDE,
            "box": GraspType.TOP_DOWN,
            "ball": GraspType.TOP_DOWN,
            "book": GraspType.SIDE,
            "default": GraspType.TOP_DOWN
        }
    
    def plan_grasps(
        self,
        target_object: DetectedObject,
        num_candidates: int = 5,
        preferred_type: Optional[GraspType] = None
    ) -> List[GraspPose]:
        """
        Generate ranked list of grasp candidates
        
        Args:
            target_object: Object to grasp
            num_candidates: Number of candidates to generate
            preferred_type: Optional preferred grasp type
            
        Returns:
            List of grasp poses, sorted by quality (best first)
        """
        # Extract object geometry
        geometry = self._extract_geometry(target_object)
        
        # Determine preferred grasp type
        if preferred_type is None:
            preferred_type = self.class_preferences.get(
                target_object.class_name,
                self.class_preferences["default"]
            )
        
        # Generate candidates
        candidates = []
        
        if preferred_type == GraspType.TOP_DOWN:
            candidates.extend(self._generate_top_down_grasps(geometry, num_candidates))
        elif preferred_type == GraspType.SIDE:
            candidates.extend(self._generate_side_grasps(geometry, num_candidates))
        
        # Evaluate quality
        for grasp in candidates:
            grasp.quality_score = self._evaluate_grasp_quality(grasp, geometry)
            grasp.stability_score = self._evaluate_stability(grasp, geometry)
            grasp.collision_free = self._check_collision_free(grasp, geometry)
        
        # Filter by minimum quality
        candidates = [
            g for g in candidates
            if g.quality_score >= self.min_grasp_quality and g.collision_free
        ]
        
        # Sort by quality (best first)
        candidates.sort(reverse=True)
        
        return candidates[:num_candidates]
    
    def _extract_geometry(self, obj: DetectedObject) -> ObjectGeometry:
        """Extract simplified geometry from detected object"""
        # Use bounding box to estimate dimensions
        bbox = obj.bounding_box
        
        # Estimate real-world dimensions from bbox and depth
        if obj.position_3d:
            # Use depth to scale bbox
            depth = obj.position_3d.z
            # Assume 60-degree FOV
            fov_rad = np.radians(60)
            pixel_to_meter = (2 * depth * np.tan(fov_rad / 2)) / 480  # Assuming 480px height
            
            width = bbox.width * pixel_to_meter
            height = bbox.height * pixel_to_meter
            depth_dim = min(width, height) * 0.8  # Heuristic
            
            dimensions = np.array([width, height, depth_dim])
            center = np.array([obj.position_3d.x, obj.position_3d.y, obj.position_3d.z])
        else:
            # Default dimensions
            dimensions = np.array([0.05, 0.1, 0.05])
            center = np.array([0.3, 0.0, 0.1])
        
        return ObjectGeometry(
            center=center,
            dimensions=dimensions,
            orientation=np.eye(3),  # Assume upright
            class_name=obj.class_name
        )
    
    def _generate_top_down_grasps(
        self,
        geometry: ObjectGeometry,
        num_grasps: int
    ) -> List[GraspPose]:
        """Generate top-down grasp candidates"""
        grasps = []
        
        # Sample different approach angles
        for i in range(num_grasps):
            # Rotation around Z-axis (vertical)
            angle = (2 * np.pi * i) / num_grasps
            
            # Grasp pose: above object, pointing down
            grasp_position = geometry.center.copy()
            grasp_position[2] += 0.1  # 10cm above object
            
            # Orientation: pointing down, rotated around Z
            pose = Pose(
                x=grasp_position[0],
                y=grasp_position[1],
                z=grasp_position[2],
                roll=0.0,
                pitch=np.pi/2,  # Point down
                yaw=angle
            )
            
            # Approach vector (downward)
            approach = np.array([0.0, 0.0, -1.0])
            
            # Gripper width (based on object width)
            gripper_width = min(geometry.dimensions[0], self.gripper_max_width)
            
            grasp = GraspPose(
                pose=pose,
                grasp_type=GraspType.TOP_DOWN,
                approach_vector=approach,
                quality_score=0.0,  # Will be computed
                stability_score=0.0,
                collision_free=True,
                gripper_width=gripper_width
            )
            
            grasps.append(grasp)
        
        return grasps
    
    def _generate_side_grasps(
        self,
        geometry: ObjectGeometry,
        num_grasps: int
    ) -> List[GraspPose]:
        """Generate side grasp candidates"""
        grasps = []
        
        # Sample around object perimeter
        for i in range(num_grasps):
            # Angle around object
            angle = (2 * np.pi * i) / num_grasps
            
            # Position: offset from object center
            offset_distance = max(geometry.dimensions) / 2 + 0.05  # 5cm clearance
            
            grasp_position = geometry.center.copy()
            grasp_position[0] += offset_distance * np.cos(angle)
            grasp_position[1] += offset_distance * np.sin(angle)
            
            # Orientation: gripper pointing toward object center
            pose = Pose(
                x=grasp_position[0],
                y=grasp_position[1],
                z=grasp_position[2],
                roll=0.0,
                pitch=0.0,
                yaw=angle + np.pi  # Point toward center
            )
            
            # Approach vector (toward object)
            approach = np.array([
                -np.cos(angle),
                -np.sin(angle),
                0.0
            ])
            
            # Gripper width
            gripper_width = min(geometry.dimensions[2], self.gripper_max_width)
            
            grasp = GraspPose(
                pose=pose,
                grasp_type=GraspType.SIDE,
                approach_vector=approach,
                quality_score=0.0,
                stability_score=0.0,
                collision_free=True,
                gripper_width=gripper_width
            )
            
            grasps.append(grasp)
        
        return grasps
    
    def _evaluate_grasp_quality(
        self,
        grasp: GraspPose,
        geometry: ObjectGeometry
    ) -> float:
        """
        Evaluate grasp quality
        
        Considers:
        - Gripper fit (does object fit in gripper?)
        - Approach angle (is approach clear?)
        - Center alignment (grasp near object center of mass?)
        """
        score = 0.0
        
        # 1. Gripper fit (0.4 weight)
        if grasp.gripper_width <= self.gripper_max_width:
            fit_ratio = grasp.gripper_width / self.gripper_max_width
            # Prefer medium-sized objects (easier to grasp)
            fit_score = 1.0 - abs(fit_ratio - 0.5) * 2
            score += 0.4 * fit_score
        
        # 2. Approach angle (0.3 weight)
        # Top-down is generally more stable
        if grasp.grasp_type == GraspType.TOP_DOWN:
            score += 0.3 * 0.9
        else:
            score += 0.3 * 0.7
        
        # 3. Center alignment (0.3 weight)
        grasp_pos = np.array([grasp.pose.x, grasp.pose.y, grasp.pose.z])
        distance_to_center = np.linalg.norm(grasp_pos - geometry.center)
        alignment_score = np.exp(-distance_to_center / 0.1)  # 10cm characteristic length
        score += 0.3 * alignment_score
        
        return float(np.clip(score, 0.0, 1.0))
    
    def _evaluate_stability(
        self,
        grasp: GraspPose,
        geometry: ObjectGeometry
    ) -> float:
        """Evaluate grasp stability (resistance to disturbance)"""
        # Simple heuristic: larger contact area = more stable
        contact_area = grasp.gripper_width * 0.02  # Assume 2cm finger depth
        
        # Normalize by object size
        object_area = geometry.dimensions[0] * geometry.dimensions[1]
        stability = np.clip(contact_area / object_area, 0.0, 1.0)
        
        return float(stability)
    
    def _check_collision_free(
        self,
        grasp: GraspPose,
        geometry: ObjectGeometry
    ) -> bool:
        """Check if grasp approach is collision-free"""
        # Simplified collision check
        # In production, use proper collision checking library
        
        # Check if gripper would collide with table
        table_height = 0.0  # Assume table at z=0
        if grasp.pose.z < table_height + 0.05:  # 5cm clearance
            return False
        
        # Check if approach path is clear
        # (For now, assume clear)
        
        return True
    
    def visualize_grasp(self, grasp: GraspPose) -> Dict[str, any]:
        """Get grasp visualization data"""
        return {
            "position": [grasp.pose.x, grasp.pose.y, grasp.pose.z],
            "orientation": [grasp.pose.roll, grasp.pose.pitch, grasp.pose.yaw],
            "approach": grasp.approach_vector.tolist(),
            "quality": grasp.quality_score,
            "type": grasp.grasp_type.value,
            "gripper_width": grasp.gripper_width
        }


class IntegratedManipulationSystem:
    """
    Full manipulation pipeline: detect → plan grasp → servo → execute
    
    Integrates all components for end-to-end object manipulation.
    """
    
    def __init__(
        self,
        fusion_engine,
        grasp_planner: GraspPlanner,
        servo_controller
    ):
        self.fusion_engine = fusion_engine
        self.grasp_planner = grasp_planner
        self.servo_controller = servo_controller
    
    def pick_object(
        self,
        object_class: str,
        image: np.ndarray,
        depth_map: Optional[np.ndarray] = None
    ) -> bool:
        """
        Complete pick operation: detect → plan → servo → grasp
        
        Args:
            object_class: Class of object to pick
            image: Current camera image
            depth_map: Optional depth map
            
        Returns:
            True if successful
        """
        # 1. Perceive environment
        percepts = self.fusion_engine.process_frame(image, depth_map)
        
        # 2. Find target object
        target = None
        for percept in percepts:
            if percept.class_name == object_class:
                target = percept
                break
        
        if target is None:
            print(f"Object '{object_class}' not found")
            return False
        
        # 3. Set attention focus
        self.fusion_engine.set_attention_focus(target.object_id, reason="pick_task")
        
        # 4. Plan grasp
        # Convert percept to DetectedObject for grasp planner
        from perception.object_detector import DetectedObject, BoundingBox
        detected_obj = DetectedObject(
            object_id=target.object_id,
            class_name=target.class_name,
            bounding_box=BoundingBox(
                x_min=0, y_min=0, x_max=100, y_max=100, confidence=target.fusion_confidence
            ),
            position_3d=target.position,
            timestamp=target.timestamp
        )
        
        grasps = self.grasp_planner.plan_grasps(detected_obj, num_candidates=3)
        
        if not grasps:
            print("No valid grasps found")
            return False
        
        best_grasp = grasps[0]
        print(f"Best grasp: quality={best_grasp.quality_score:.2f}, type={best_grasp.grasp_type.value}")
        
        # 5. Visual servoing to pre-grasp pose
        # Offset by approach vector
        pre_grasp_pose = Pose(
            x=best_grasp.pose.x - best_grasp.approach_vector[0] * 0.1,
            y=best_grasp.pose.y - best_grasp.approach_vector[1] * 0.1,
            z=best_grasp.pose.z - best_grasp.approach_vector[2] * 0.1,
            roll=best_grasp.pose.roll,
            pitch=best_grasp.pose.pitch,
            yaw=best_grasp.pose.yaw
        )
        
        success = self.servo_controller.servo_to_pose(pre_grasp_pose)
        
        if not success:
            print("Failed to reach pre-grasp pose")
            return False
        
        # 6. Approach and grasp
        success = self.servo_controller.servo_to_pose(best_grasp.pose)
        
        if not success:
            print("Failed to reach grasp pose")
            return False
        
        # 7. Close gripper (in production, send gripper command)
        print(f"Closing gripper to {best_grasp.gripper_width*1000:.1f}mm")
        
        # 8. Lift object
        lift_pose = Pose(
            x=best_grasp.pose.x,
            y=best_grasp.pose.y,
            z=best_grasp.pose.z + 0.1,  # Lift 10cm
            roll=best_grasp.pose.roll,
            pitch=best_grasp.pose.pitch,
            yaw=best_grasp.pose.yaw
        )
        
        success = self.servo_controller.servo_to_pose(lift_pose)
        
        return success


def create_grasp_planner() -> GraspPlanner:
    """Create grasp planner with default settings"""
    return GraspPlanner(
        gripper_max_width=0.08,
        min_grasp_quality=0.3
    )
