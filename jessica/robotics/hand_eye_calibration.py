"""
Hand-Eye Calibration for Visual Servoing

Computes the transformation between camera and robot base coordinates,
enabling visual feedback for robotic control.

Two calibration methods:
1. Eye-in-hand: Camera mounted on robot end-effector
2. Eye-to-hand: Camera fixed in workspace

Key formulas:
- Eye-in-hand: base_T_camera = base_T_ee * ee_T_camera
- Eye-to-hand: base_T_camera (fixed transformation)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class CalibrationType(Enum):
    """Camera mounting configuration"""
    EYE_IN_HAND = "eye_in_hand"  # Camera on robot
    EYE_TO_HAND = "eye_to_hand"  # Camera fixed


@dataclass
class Pose:
    """6-DOF pose (position + orientation)"""
    x: float  # meters
    y: float  # meters
    z: float  # meters
    roll: float  # radians
    pitch: float  # radians
    yaw: float  # radians
    
    def to_matrix(self) -> np.ndarray:
        """Convert to 4x4 homogeneous transformation matrix"""
        # Rotation matrix from Euler angles (ZYX convention)
        cr, sr = np.cos(self.roll), np.sin(self.roll)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        
        R = np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp, cp*sr, cp*cr]
        ])
        
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = [self.x, self.y, self.z]
        return T
    
    @classmethod
    def from_matrix(cls, T: np.ndarray) -> 'Pose':
        """Create from 4x4 transformation matrix"""
        x, y, z = T[:3, 3]
        
        # Extract Euler angles from rotation matrix
        R = T[:3, :3]
        pitch = np.arctan2(-R[2, 0], np.sqrt(R[0, 0]**2 + R[1, 0]**2))
        
        if np.abs(pitch - np.pi/2) < 1e-6:  # Gimbal lock
            roll = 0.0
            yaw = np.arctan2(R[0, 1], R[1, 1])
        elif np.abs(pitch + np.pi/2) < 1e-6:  # Gimbal lock
            roll = 0.0
            yaw = np.arctan2(-R[0, 1], -R[1, 1])
        else:
            roll = np.arctan2(R[2, 1], R[2, 2])
            yaw = np.arctan2(R[1, 0], R[0, 0])
        
        return cls(x, y, z, roll, pitch, yaw)


@dataclass
class CalibrationSample:
    """Single calibration measurement"""
    robot_pose: Pose  # Robot end-effector pose in base frame
    camera_observation: np.ndarray  # Detected marker pose in camera frame
    timestamp: float


class HandEyeCalibration:
    """
    Compute camera-to-robot transformation for visual servoing
    
    Uses AX = XB formulation where:
    - A: Robot motion (base to end-effector)
    - B: Camera observation (camera to marker)
    - X: Unknown hand-eye transformation
    """
    
    def __init__(
        self,
        calibration_type: CalibrationType = CalibrationType.EYE_IN_HAND,
        min_samples: int = 10
    ):
        self.calibration_type = calibration_type
        self.min_samples = min_samples
        
        # Calibration data
        self.samples: List[CalibrationSample] = []
        self.camera_to_base_transform: Optional[np.ndarray] = None
        self.calibration_error: Optional[float] = None
        
    def add_sample(
        self,
        robot_pose: Pose,
        camera_observation: np.ndarray
    ):
        """Add calibration sample"""
        import time
        sample = CalibrationSample(
            robot_pose=robot_pose,
            camera_observation=camera_observation,
            timestamp=time.time()
        )
        self.samples.append(sample)
    
    def calibrate(self) -> Tuple[np.ndarray, float]:
        """
        Compute hand-eye calibration
        
        Returns:
            (transformation_matrix, reprojection_error)
        """
        if len(self.samples) < self.min_samples:
            raise ValueError(
                f"Need at least {self.min_samples} samples, got {len(self.samples)}"
            )
        
        if self.calibration_type == CalibrationType.EYE_IN_HAND:
            transform = self._calibrate_eye_in_hand()
        else:
            transform = self._calibrate_eye_to_hand()
        
        # Compute calibration error
        error = self._compute_reprojection_error(transform)
        
        self.camera_to_base_transform = transform
        self.calibration_error = error
        
        return transform, error
    
    def _calibrate_eye_in_hand(self) -> np.ndarray:
        """
        Eye-in-hand calibration using Tsai-Lenz method
        
        Solves AX = XB where:
        - A: Robot motion between poses
        - B: Camera observation changes
        - X: End-effector to camera transform
        """
        n = len(self.samples)
        
        # Build system of equations
        A_matrices = []
        B_matrices = []
        
        for i in range(n - 1):
            # Robot motion from pose i to i+1
            T1 = self.samples[i].robot_pose.to_matrix()
            T2 = self.samples[i + 1].robot_pose.to_matrix()
            A = np.linalg.inv(T2) @ T1
            
            # Camera observation change
            C1 = self.samples[i].camera_observation
            C2 = self.samples[i + 1].camera_observation
            B = np.linalg.inv(C2) @ C1
            
            A_matrices.append(A)
            B_matrices.append(B)
        
        # Solve using closed-form solution (simplified)
        # In production, use proper Tsai-Lenz or dual quaternion method
        X = self._solve_ax_xb(A_matrices, B_matrices)
        
        return X
    
    def _calibrate_eye_to_hand(self) -> np.ndarray:
        """
        Eye-to-hand calibration
        
        Camera is fixed relative to base.
        Solves AX = ZB where:
        - A: Robot poses
        - B: Camera observations
        - X: Base to marker (unknown)
        - Z: Base to camera (what we want)
        """
        # Average over all samples (simplified)
        transforms = []
        
        for sample in self.samples:
            # base_T_marker = base_T_ee * ee_T_marker
            # camera_T_marker = sample.camera_observation
            # base_T_camera = base_T_marker * marker_T_camera
            
            base_T_ee = sample.robot_pose.to_matrix()
            camera_T_marker = sample.camera_observation
            
            # Assume marker is at end-effector (calibration target)
            base_T_marker = base_T_ee
            base_T_camera = base_T_marker @ np.linalg.inv(camera_T_marker)
            
            transforms.append(base_T_camera)
        
        # Average transformations (simplified - use proper SE(3) averaging in production)
        avg_transform = np.mean(transforms, axis=0)
        
        return avg_transform
    
    def _solve_ax_xb(
        self,
        A_list: List[np.ndarray],
        B_list: List[np.ndarray]
    ) -> np.ndarray:
        """
        Solve AX = XB for hand-eye calibration
        
        Uses rotation-then-translation approach:
        1. Solve for rotation: Ra * Rx = Rx * Rb
        2. Solve for translation: (Ra - I) * tx = Rx * tb - ta
        """
        n = len(A_list)
        
        # Extract rotations and translations
        Ra_list = [A[:3, :3] for A in A_list]
        ta_list = [A[:3, 3] for A in A_list]
        Rb_list = [B[:3, :3] for B in B_list]
        tb_list = [B[:3, 3] for B in B_list]
        
        # Solve for rotation using quaternion method (simplified)
        # In production, use proper dual quaternion or Tsai-Lenz
        Rx = self._solve_rotation(Ra_list, Rb_list)
        
        # Solve for translation
        tx = self._solve_translation(Ra_list, ta_list, Rx, tb_list)
        
        # Build transformation matrix
        X = np.eye(4)
        X[:3, :3] = Rx
        X[:3, 3] = tx
        
        return X
    
    def _solve_rotation(
        self,
        Ra_list: List[np.ndarray],
        Rb_list: List[np.ndarray]
    ) -> np.ndarray:
        """Solve for rotation component"""
        # Use SVD-based method (simplified)
        # In production, use quaternion or axis-angle method
        
        M = np.zeros((3, 3))
        for Ra, Rb in zip(Ra_list, Rb_list):
            M += Ra.T @ Rb
        
        U, _, Vt = np.linalg.svd(M)
        Rx = U @ Vt
        
        # Ensure proper rotation (det = 1)
        if np.linalg.det(Rx) < 0:
            Vt[-1, :] *= -1
            Rx = U @ Vt
        
        return Rx
    
    def _solve_translation(
        self,
        Ra_list: List[np.ndarray],
        ta_list: List[np.ndarray],
        Rx: np.ndarray,
        tb_list: List[np.ndarray]
    ) -> np.ndarray:
        """Solve for translation component"""
        # Build linear system: (Ra - I) * tx = Rx * tb - ta
        n = len(Ra_list)
        A = np.zeros((3 * n, 3))
        b = np.zeros(3 * n)
        
        for i, (Ra, ta, tb) in enumerate(zip(Ra_list, ta_list, tb_list)):
            A[3*i:3*(i+1), :] = Ra - np.eye(3)
            b[3*i:3*(i+1)] = Rx @ tb - ta
        
        # Solve using least squares
        tx, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        
        return tx
    
    def _compute_reprojection_error(self, transform: np.ndarray) -> float:
        """Compute average reprojection error"""
        errors = []
        
        for sample in self.samples:
            # Transform camera observation to base frame
            base_T_ee = sample.robot_pose.to_matrix()
            camera_T_marker = sample.camera_observation
            
            # Predicted marker position
            if self.calibration_type == CalibrationType.EYE_IN_HAND:
                # base_T_marker = base_T_ee * ee_T_camera * camera_T_marker
                predicted = base_T_ee @ transform @ camera_T_marker
            else:
                # base_T_marker = base_T_camera * camera_T_marker
                predicted = transform @ camera_T_marker
            
            # Actual marker position (at end-effector)
            actual = base_T_ee
            
            # Position error
            pos_error = np.linalg.norm(predicted[:3, 3] - actual[:3, 3])
            errors.append(pos_error)
        
        return float(np.mean(errors))
    
    def transform_point_camera_to_base(
        self,
        point_camera: np.ndarray
    ) -> np.ndarray:
        """
        Transform point from camera coordinates to robot base
        
        Args:
            point_camera: [x, y, z] in camera frame
            
        Returns:
            [x, y, z] in base frame
        """
        if self.camera_to_base_transform is None:
            raise ValueError("Must calibrate before transforming points")
        
        # Homogeneous coordinates
        point_h = np.append(point_camera, 1.0)
        
        # Transform
        point_base_h = self.camera_to_base_transform @ point_h
        
        return point_base_h[:3]
    
    def transform_pose_camera_to_base(
        self,
        pose_camera: Pose
    ) -> Pose:
        """Transform full pose from camera to base frame"""
        if self.camera_to_base_transform is None:
            raise ValueError("Must calibrate before transforming poses")
        
        # Convert to matrix
        T_camera = pose_camera.to_matrix()
        
        # Transform
        T_base = self.camera_to_base_transform @ T_camera
        
        # Convert back to pose
        return Pose.from_matrix(T_base)
    
    def save_calibration(self, filepath: Path):
        """Save calibration to file"""
        if self.camera_to_base_transform is None:
            raise ValueError("Must calibrate before saving")
        
        data = {
            "calibration_type": self.calibration_type.value,
            "transform": self.camera_to_base_transform.tolist(),
            "error": self.calibration_error,
            "num_samples": len(self.samples)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_calibration(cls, filepath: Path) -> 'HandEyeCalibration':
        """Load calibration from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        calib = cls(
            calibration_type=CalibrationType(data["calibration_type"])
        )
        calib.camera_to_base_transform = np.array(data["transform"])
        calib.calibration_error = data["error"]
        
        return calib


def create_mock_calibration(
    calibration_type: CalibrationType = CalibrationType.EYE_TO_HAND
) -> HandEyeCalibration:
    """
    Create mock calibration for testing
    
    Assumes camera is 30cm above and 20cm to the right of robot base
    """
    calib = HandEyeCalibration(calibration_type)
    
    # Mock transform: camera above robot
    transform = np.eye(4)
    transform[:3, 3] = [0.2, 0.0, 0.3]  # x=20cm, z=30cm
    
    calib.camera_to_base_transform = transform
    calib.calibration_error = 0.002  # 2mm
    
    return calib
