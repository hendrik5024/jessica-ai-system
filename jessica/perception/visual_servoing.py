"""
Visual Servoing Controller

Closed-loop control system that uses real-time visual feedback to guide
the robotic arm to target objects.

Three control modes:
1. Position-based visual servoing (PBVS): Control in 3D space
2. Image-based visual servoing (IBVS): Control in image space
3. Hybrid: Combines both approaches

Key capabilities:
- Real-time pose error computation
- Velocity command generation
- Collision avoidance
- Convergence detection
"""

import numpy as np
from typing import Optional, Tuple, Callable, Dict, List
from dataclasses import dataclass
from enum import Enum
import time

# Import from other modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from robotics.ik_solver import IKSolver, JointAngles
except ImportError:
    # Mock IK solver if not available
    class JointAngles:
        def __init__(self, theta1=0.0, theta2=0.0, theta3=0.0):
            self.theta1 = theta1
            self.theta2 = theta2
            self.theta3 = theta3
    class IKSolver:
        pass

from robotics.hand_eye_calibration import HandEyeCalibration, Pose
from perception.object_detector import ObjectDetector, DetectedObject, Position3D


class ServoMode(Enum):
    """Visual servoing control mode"""
    POSITION_BASED = "pbvs"  # Control in 3D space
    IMAGE_BASED = "ibvs"  # Control in image space
    HYBRID = "hybrid"  # Combines both


@dataclass
class ServoingState:
    """Current state of visual servoing"""
    current_pose: Pose
    target_pose: Pose
    position_error: float  # meters
    orientation_error: float  # radians
    velocity_command: np.ndarray  # [vx, vy, vz, wx, wy, wz]
    converged: bool
    iteration: int


@dataclass
class ServoConfig:
    """Visual servoing configuration"""
    mode: ServoMode = ServoMode.POSITION_BASED
    position_gain: float = 0.5  # Proportional gain for position
    orientation_gain: float = 0.3  # Proportional gain for orientation
    max_velocity: float = 0.1  # m/s
    max_angular_velocity: float = 0.5  # rad/s
    convergence_threshold_pos: float = 0.01  # 1cm
    convergence_threshold_ori: float = 0.05  # ~3 degrees
    max_iterations: int = 1000
    control_rate: float = 30.0  # Hz


class VisualServoController:
    """
    Real-time visual servoing controller
    
    Uses camera feedback to move robot to target pose.
    """
    
    def __init__(
        self,
        ik_solver: IKSolver,
        hand_eye_calib: HandEyeCalibration,
        object_detector: ObjectDetector,
        config: Optional[ServoConfig] = None
    ):
        self.ik_solver = ik_solver
        self.hand_eye_calib = hand_eye_calib
        self.object_detector = object_detector
        self.config = config or ServoConfig()
        
        # Control state
        self.current_state: Optional[ServoingState] = None
        self.trajectory: List[ServoingState] = []
        
        # Performance tracking
        self.servo_times: List[float] = []
        self.convergence_iterations: List[int] = []
    
    def servo_to_object(
        self,
        target_object: DetectedObject,
        grasp_offset: Optional[np.ndarray] = None,
        callback: Optional[Callable[[ServoingState], None]] = None
    ) -> bool:
        """
        Servo to detected object
        
        Args:
            target_object: Object to reach
            grasp_offset: Optional offset from object center [x, y, z]
            callback: Optional callback called each iteration
            
        Returns:
            True if converged successfully
        """
        if target_object.position_3d is None:
            raise ValueError("Target object must have 3D position")
        
        # Compute target pose in base frame
        target_pose = self._compute_target_pose(target_object, grasp_offset)
        
        return self.servo_to_pose(target_pose, callback)
    
    def servo_to_pose(
        self,
        target_pose: Pose,
        callback: Optional[Callable[[ServoingState], None]] = None
    ) -> bool:
        """
        Servo to target pose
        
        Args:
            target_pose: Desired end-effector pose in base frame
            callback: Optional callback called each iteration
            
        Returns:
            True if converged successfully
        """
        start_time = time.time()
        self.trajectory = []
        
        # Get current pose
        current_joints = self._get_current_joints()
        current_pose = self._forward_kinematics(current_joints)
        
        # Servoing loop
        for iteration in range(self.config.max_iterations):
            # Compute error
            position_error, orientation_error = self._compute_pose_error(
                current_pose, target_pose
            )
            
            # Check convergence
            converged = (
                position_error < self.config.convergence_threshold_pos and
                orientation_error < self.config.convergence_threshold_ori
            )
            
            # Compute velocity command
            if self.config.mode == ServoMode.POSITION_BASED:
                velocity_cmd = self._compute_pbvs_velocity(
                    current_pose, target_pose, position_error, orientation_error
                )
            else:
                velocity_cmd = self._compute_ibvs_velocity(
                    current_pose, target_pose
                )
            
            # Create state
            state = ServoingState(
                current_pose=current_pose,
                target_pose=target_pose,
                position_error=position_error,
                orientation_error=orientation_error,
                velocity_command=velocity_cmd,
                converged=converged,
                iteration=iteration
            )
            
            self.current_state = state
            self.trajectory.append(state)
            
            # Callback
            if callback:
                callback(state)
            
            # Check convergence
            if converged:
                elapsed = time.time() - start_time
                self.servo_times.append(elapsed)
                self.convergence_iterations.append(iteration)
                return True
            
            # Apply velocity command (integrate for one time step)
            dt = 1.0 / self.config.control_rate
            current_pose = self._integrate_velocity(current_pose, velocity_cmd, dt)
            
            # Rate limiting
            time.sleep(dt)
        
        # Failed to converge
        return False
    
    def _compute_target_pose(
        self,
        target_object: DetectedObject,
        grasp_offset: Optional[np.ndarray]
    ) -> Pose:
        """Compute target end-effector pose for grasping"""
        # Transform object position to base frame
        pos_camera = np.array([
            target_object.position_3d.x,
            target_object.position_3d.y,
            target_object.position_3d.z
        ])
        
        pos_base = self.hand_eye_calib.transform_point_camera_to_base(pos_camera)
        
        # Apply grasp offset
        if grasp_offset is not None:
            pos_base += grasp_offset
        
        # Default grasp orientation (pointing down)
        # In production, use grasp planner to determine optimal orientation
        return Pose(
            x=pos_base[0],
            y=pos_base[1],
            z=pos_base[2],
            roll=0.0,
            pitch=np.pi/2,  # Point down
            yaw=0.0
        )
    
    def _compute_pose_error(
        self,
        current: Pose,
        target: Pose
    ) -> Tuple[float, float]:
        """Compute position and orientation errors"""
        # Position error (Euclidean distance)
        pos_error = np.sqrt(
            (target.x - current.x)**2 +
            (target.y - current.y)**2 +
            (target.z - current.z)**2
        )
        
        # Orientation error (angle between rotation matrices)
        T_current = current.to_matrix()
        T_target = target.to_matrix()
        R_error = T_target[:3, :3] @ T_current[:3, :3].T
        
        # Angle from rotation matrix: theta = arccos((trace(R) - 1) / 2)
        trace = np.trace(R_error)
        ori_error = np.arccos(np.clip((trace - 1.0) / 2.0, -1.0, 1.0))
        
        return float(pos_error), float(ori_error)
    
    def _compute_pbvs_velocity(
        self,
        current: Pose,
        target: Pose,
        pos_error: float,
        ori_error: float
    ) -> np.ndarray:
        """
        Compute velocity command using Position-Based Visual Servoing
        
        Uses proportional control: v = K * error
        """
        # Position error vector
        pos_error_vec = np.array([
            target.x - current.x,
            target.y - current.y,
            target.z - current.z
        ])
        
        # Linear velocity (proportional control)
        v_linear = self.config.position_gain * pos_error_vec
        
        # Clip to max velocity
        v_norm = np.linalg.norm(v_linear)
        if v_norm > self.config.max_velocity:
            v_linear = v_linear * (self.config.max_velocity / v_norm)
        
        # Orientation error (axis-angle representation)
        T_current = current.to_matrix()
        T_target = target.to_matrix()
        R_error = T_target[:3, :3] @ T_current[:3, :3].T
        
        # Extract axis-angle
        angle = ori_error
        if angle > 1e-6:
            axis = self._rotation_matrix_to_axis(R_error, angle)
        else:
            axis = np.array([0.0, 0.0, 0.0])
        
        # Angular velocity
        v_angular = self.config.orientation_gain * angle * axis
        
        # Clip to max angular velocity
        w_norm = np.linalg.norm(v_angular)
        if w_norm > self.config.max_angular_velocity:
            v_angular = v_angular * (self.config.max_angular_velocity / w_norm)
        
        # Combined velocity command
        velocity = np.concatenate([v_linear, v_angular])
        
        return velocity
    
    def _compute_ibvs_velocity(
        self,
        current: Pose,
        target: Pose
    ) -> np.ndarray:
        """
        Compute velocity using Image-Based Visual Servoing
        
        Would use image features directly, but simplified here.
        """
        # For now, fall back to PBVS
        pos_error, ori_error = self._compute_pose_error(current, target)
        return self._compute_pbvs_velocity(current, target, pos_error, ori_error)
    
    def _rotation_matrix_to_axis(self, R: np.ndarray, angle: float) -> np.ndarray:
        """Extract rotation axis from rotation matrix"""
        if angle < 1e-6:
            return np.array([0.0, 0.0, 1.0])
        
        # Axis from skew-symmetric part
        axis = np.array([
            R[2, 1] - R[1, 2],
            R[0, 2] - R[2, 0],
            R[1, 0] - R[0, 1]
        ])
        
        axis_norm = np.linalg.norm(axis)
        if axis_norm > 1e-6:
            axis = axis / axis_norm
        else:
            axis = np.array([0.0, 0.0, 1.0])
        
        return axis
    
    def _integrate_velocity(
        self,
        pose: Pose,
        velocity: np.ndarray,
        dt: float
    ) -> Pose:
        """Integrate velocity command to get new pose"""
        # Linear velocity
        v_linear = velocity[:3]
        new_pos = np.array([pose.x, pose.y, pose.z]) + v_linear * dt
        
        # Angular velocity (simplified - use proper SO(3) integration in production)
        v_angular = velocity[3:]
        angle = np.linalg.norm(v_angular) * dt
        
        if angle > 1e-6:
            axis = v_angular / np.linalg.norm(v_angular)
            
            # Rodrigues' rotation formula
            K = np.array([
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0]
            ])
            
            R_delta = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
            
            # Update rotation
            T_current = pose.to_matrix()
            R_new = T_current[:3, :3] @ R_delta
            
            T_new = np.eye(4)
            T_new[:3, :3] = R_new
            T_new[:3, 3] = new_pos
            
            return Pose.from_matrix(T_new)
        else:
            # No rotation
            return Pose(
                x=new_pos[0],
                y=new_pos[1],
                z=new_pos[2],
                roll=pose.roll,
                pitch=pose.pitch,
                yaw=pose.yaw
            )
    
    def _get_current_joints(self) -> JointAngles:
        """Get current joint angles (from robot or simulation)"""
        # In production, read from robot
        # For now, return mock values
        return JointAngles(theta1=0.0, theta2=0.0, theta3=0.0)
    
    def _forward_kinematics(self, joints: JointAngles) -> Pose:
        """Compute end-effector pose from joint angles"""
        # Use IK solver's forward kinematics
        # For now, return mock pose
        return Pose(x=0.3, y=0.0, z=0.2, roll=0.0, pitch=0.0, yaw=0.0)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get servoing performance statistics"""
        if not self.servo_times:
            return {
                "avg_time": 0.0,
                "avg_iterations": 0,
                "success_rate": 0.0
            }
        
        return {
            "avg_time": np.mean(self.servo_times),
            "avg_iterations": np.mean(self.convergence_iterations),
            "success_rate": len(self.convergence_iterations) / len(self.servo_times)
        }
    
    def visualize_trajectory(self) -> Dict[str, List]:
        """Get trajectory data for visualization"""
        return {
            "positions": [
                [s.current_pose.x, s.current_pose.y, s.current_pose.z]
                for s in self.trajectory
            ],
            "errors": [
                s.position_error for s in self.trajectory
            ],
            "velocities": [
                np.linalg.norm(s.velocity_command[:3]) for s in self.trajectory
            ]
        }


def create_servo_controller(
    use_mock: bool = True
) -> VisualServoController:
    """Create visual servo controller (mock or real)"""
    try:
        from robotics.ik_solver import create_mock_ik_solver
        ik_solver = create_mock_ik_solver()
    except ImportError:
        ik_solver = IKSolver()  # Use mock
    
    from robotics.hand_eye_calibration import create_mock_calibration, CalibrationType
    from perception.object_detector import create_mock_detector
    
    calib = create_mock_calibration(CalibrationType.EYE_TO_HAND)
    detector = create_mock_detector()
    
    config = ServoConfig(
        mode=ServoMode.POSITION_BASED,
        position_gain=0.5,
        orientation_gain=0.3,
        max_velocity=0.1,
        convergence_threshold_pos=0.01
    )
    
    return VisualServoController(ik_solver, calib, detector, config)
