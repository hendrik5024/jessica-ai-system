"""
Robotics Skill - Inverse Kinematics Solver for 3-DOF Robotic Arm

Provides:
- 3-DOF arm kinematics (forward and inverse)
- Joint state memory with SQLite persistence
- Natural language interface for robot control
"""

import math
import sqlite3
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Any
import os

logger = logging.getLogger(__name__)


@dataclass
class JointState:
    """Represents robot arm joint angles."""
    joint_1: float  # degrees (base rotation)
    joint_2: float  # degrees (shoulder angle)
    joint_3: float  # degrees (elbow angle)
    
    def to_radians(self) -> tuple:
        """Convert to radians."""
        return (
            math.radians(self.joint_1),
            math.radians(self.joint_2),
            math.radians(self.joint_3)
        )
    
    def to_degrees(self) -> tuple:
        """Return angles in degrees."""
        return (self.joint_1, self.joint_2, self.joint_3)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'joint_1': self.joint_1,
            'joint_2': self.joint_2,
            'joint_3': self.joint_3
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"J1: {self.joint_1:.1f}° | J2: {self.joint_2:.1f}° | J3: {self.joint_3:.1f}°"


@dataclass
class CartesianPose:
    """Represents end-effector position in Cartesian space."""
    x: float  # mm
    y: float  # mm
    z: float  # mm
    
    def to_tuple(self) -> tuple:
        """Return as tuple."""
        return (self.x, self.y, self.z)
    
    def __str__(self) -> str:
        """String representation."""
        return f"X: {self.x:.1f} | Y: {self.y:.1f} | Z: {self.z:.1f}"


class RoboticArm3DOF:
    """
    3-DOF Robotic Arm with Forward and Inverse Kinematics.
    
    Configuration:
    - Link 1: 150mm (vertical base offset)
    - Link 2: 100mm (upper arm)
    - Link 3: 80mm (forearm/gripper)
    - Max reach: 180mm (link2 + link3)
    - Min reach: 20mm (link2 - link3)
    """
    
    def __init__(
        self,
        link_1: float = 150.0,
        link_2: float = 100.0,
        link_3: float = 80.0
    ):
        """
        Initialize 3-DOF arm.
        
        Args:
            link_1: Base to shoulder distance (mm)
            link_2: Shoulder to elbow distance (mm)
            link_3: Elbow to gripper distance (mm)
        """
        self.link_1 = link_1  # Vertical offset
        self.link_2 = link_2  # Upper arm
        self.link_3 = link_3  # Forearm
        
        # Safe limits (degrees)
        self.joint_limits = {
            'joint_1': (-180, 180),  # Base rotation
            'joint_2': (0, 180),      # Shoulder
            'joint_3': (0, 180)       # Elbow
        }
        
        logger.info(f"3-DOF Arm initialized: L1={link_1}mm, L2={link_2}mm, L3={link_3}mm")
    
    def forward_kinematics(self, joints: JointState) -> CartesianPose:
        """
        Calculate end-effector position from joint angles (Forward Kinematics).
        
        Simple 3-DOF model:
        - Link 1: Vertical base (150mm)
        - Link 2: Horizontal arm (100mm) with joint 2 controlling angle
        - Link 3: Forearm (80mm) with joint 3 controlling relative angle
        - Joint 1: Base rotation in XY plane
        
        Args:
            joints: Joint state (degrees)
        
        Returns:
            Cartesian position (mm)
        """
        # Convert to radians
        theta1, theta2, theta3 = joints.to_radians()
        
        # Base position
        z = self.link_1
        
        # Link 2 extends from base
        # theta2 is the angle from horizontal (0 = pointing forward, 90 = pointing up)
        r2 = self.link_2 * math.cos(theta2)  # Horizontal component
        z += self.link_2 * math.sin(theta2)  # Vertical component
        
        # Link 3 extends from link 2
        # theta3 is relative to link 2
        combined_angle = theta2 + theta3
        r3 = self.link_3 * math.cos(combined_angle)
        z += self.link_3 * math.sin(combined_angle)
        
        # Total horizontal reach
        r = r2 + r3
        
        # Convert from cylindrical (r, theta1) to Cartesian (x, y)
        x = r * math.cos(theta1)
        y = r * math.sin(theta1)
        
        return CartesianPose(x, y, z)
    
    def inverse_kinematics(
        self,
        target: CartesianPose,
        tolerance: float = 15.0,
        max_iterations: int = 1000
    ) -> Optional[JointState]:
        """
        Solve Inverse Kinematics for target position using numerical gradient descent.
        
        Args:
            target: Target position (X, Y, Z in mm)
            tolerance: Position tolerance (mm)
            max_iterations: Maximum iterations for numerical solver
        
        Returns:
            Joint angles in degrees, or None if unreachable
        """
        # Check if target is reachable
        if not self.is_reachable(target):
            return None
        
        # Use numerical IK with multiple random restarts for robustness
        best_solution = None
        best_error = tolerance + 1
        
        # Try multiple starting configurations
        for attempt in range(5):
            if attempt == 0:
                # First attempt: start from home position
                joints = [0, 45, 90]
            else:
                # Other attempts: random within limits
                import random
                joints = [
                    random.uniform(-90, 90),
                    random.uniform(10, 90),
                    random.uniform(10, 90)
                ]
            
            # Numerical optimization: gradient descent
            learning_rate = 0.5
            
            for iteration in range(max_iterations):
                # Calculate current position
                current_state = JointState(joints[0], joints[1], joints[2])
                current_pos = self.forward_kinematics(current_state)
                
                # Calculate error
                error = math.sqrt(
                    (current_pos.x - target.x)**2 +
                    (current_pos.y - target.y)**2 +
                    (current_pos.z - target.z)**2
                )
                
                # Check if solution found
                if error < tolerance:
                    return JointState(joints[0], joints[1], joints[2])
                
                # Calculate gradients numerically (small delta)
                delta = 0.1
                gradients = []
                for i in range(3):
                    # Positive delta
                    joints[i] += delta
                    joint_plus = JointState(joints[0], joints[1], joints[2])
                    pos_plus = self.forward_kinematics(joint_plus)
                    error_plus = math.sqrt(
                        (pos_plus.x - target.x)**2 +
                        (pos_plus.y - target.y)**2 +
                        (pos_plus.z - target.z)**2
                    )
                    joints[i] -= delta
                    
                    gradient = (error_plus - error) / delta
                    gradients.append(gradient)
                
                # Update joints using gradient descent
                for i in range(3):
                    joints[i] -= learning_rate * gradients[i]
                    
                    # Clamp to limits
                    joint_name = f'joint_{i+1}'
                    min_limit, max_limit = self.joint_limits[joint_name]
                    joints[i] = max(min_limit, min(max_limit, joints[i]))
                
                # Reduce learning rate over time (cooling schedule)
                learning_rate *= 0.995
            
            # Track best solution across attempts
            current_state = JointState(joints[0], joints[1], joints[2])
            current_pos = self.forward_kinematics(current_state)
            error = math.sqrt(
                (current_pos.x - target.x)**2 +
                (current_pos.y - target.y)**2 +
                (current_pos.z - target.z)**2
            )
            
            if error < best_error:
                best_error = error
                best_solution = JointState(joints[0], joints[1], joints[2])
        
        # Return best solution if within reasonable tolerance
        if best_solution and best_error < tolerance * 1.5:
            if best_error > tolerance:
                logger.warning(f"IK solution has error: {best_error:.1f}mm (tolerance: {tolerance}mm)")
            return best_solution
        
        logger.warning(f"IK failed: best error {best_error:.1f}mm")
        return None
    
    def _clamp_angle(self, angle: float, joint_name: str) -> float:
        """Clamp angle to joint limits."""
        min_limit, max_limit = self.joint_limits[joint_name]
        
        # Normalize angle to [-180, 180]
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        
        return max(min_limit, min(max_limit, angle))
    
    def is_reachable(self, target: CartesianPose) -> bool:
        """Check if target is within workspace."""
        r = math.sqrt(target.x**2 + target.y**2)
        z = target.z - self.link_1
        d = math.sqrt(r**2 + z**2)
        
        max_reach = self.link_2 + self.link_3
        min_reach = abs(self.link_2 - self.link_3)
        
        return d <= max_reach and d >= min_reach
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get workspace information."""
        max_reach = self.link_2 + self.link_3
        min_reach = abs(self.link_2 - self.link_3)
        
        return {
            'max_reach_mm': max_reach,
            'min_reach_mm': min_reach,
            'link_lengths': {
                'link_1': self.link_1,
                'link_2': self.link_2,
                'link_3': self.link_3
            },
            'joint_limits': self.joint_limits
        }


class JointStateMemory:
    """SQLite-backed memory for saving and loading robot joint configurations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize memory store."""
        if db_path is None:
            db_path = os.environ.get('ROBOT_DB', str(Path.home() / '.jessica' / 'jessica_robot_memory.db'))
        
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS joint_states (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    joint_1 REAL NOT NULL,
                    joint_2 REAL NOT NULL,
                    joint_3 REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS position_records (
                    id INTEGER PRIMARY KEY,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    z REAL NOT NULL,
                    joint_1 REAL NOT NULL,
                    joint_2 REAL NOT NULL,
                    joint_3 REAL NOT NULL,
                    label TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def save_joint_state(
        self,
        name: str,
        joint_state: JointState,
        description: str = ""
    ) -> Dict[str, Any]:
        """Save a named joint configuration."""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute('''
                    INSERT INTO joint_states (name, joint_1, joint_2, joint_3, description, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, joint_state.joint_1, joint_state.joint_2, joint_state.joint_3, description))
            except sqlite3.IntegrityError:
                # Update existing
                conn.execute('''
                    UPDATE joint_states
                    SET joint_1=?, joint_2=?, joint_3=?, description=?, updated_at=CURRENT_TIMESTAMP
                    WHERE name=?
                ''', (joint_state.joint_1, joint_state.joint_2, joint_state.joint_3, description, name))
            
            conn.commit()
        
        return {'status': 'saved', 'name': name, 'joints': joint_state.to_dict()}
    
    def load_joint_state(self, name: str) -> Optional[JointState]:
        """Load a named joint configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT joint_1, joint_2, joint_3 FROM joint_states WHERE name=?',
                (name,)
            )
            row = cursor.fetchone()
        
        if row:
            logger.info(f"Loaded joint state: {name}")
            return JointState(row[0], row[1], row[2])
        
        logger.warning(f"Joint state not found: {name}")
        return None
    
    def list_joint_states(self) -> List[Dict[str, Any]]:
        """List all saved joint configurations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT name, joint_1, joint_2, joint_3, description, updated_at FROM joint_states ORDER BY updated_at DESC'
            )
            rows = cursor.fetchall()
        
        return [
            {
                'name': row[0],
                'joints': {'j1': row[1], 'j2': row[2], 'j3': row[3]},
                'description': row[4],
                'updated_at': row[5]
            }
            for row in rows
        ]
    
    def delete_joint_state(self, name: str) -> bool:
        """Delete a named joint configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM joint_states WHERE name=?', (name,))
            conn.commit()
            deleted = cursor.rowcount > 0
        
        if deleted:
            logger.info(f"Deleted joint state: {name}")
        else:
            logger.warning(f"Joint state not found: {name}")
        
        return deleted
    
    def record_position(
        self,
        x: float,
        y: float,
        z: float,
        joint_state: JointState,
        label: str = ""
    ) -> Dict[str, Any]:
        """Record a position in history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO position_records (x, y, z, joint_1, joint_2, joint_3, label)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (x, y, z, joint_state.joint_1, joint_state.joint_2, joint_state.joint_3, label))
            conn.commit()
        
        return {
            'status': 'recorded',
            'position': {'x': x, 'y': y, 'z': z},
            'joints': joint_state.to_dict()
        }
    
    def get_position_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get position history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT x, y, z, joint_1, joint_2, joint_3, label, recorded_at
                FROM position_records
                ORDER BY recorded_at DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        
        return [
            {
                'position': {'x': row[0], 'y': row[1], 'z': row[2]},
                'joints': {'j1': row[3], 'j2': row[4], 'j3': row[5]},
                'label': row[6],
                'recorded_at': row[7]
            }
            for row in rows
        ]


# Singleton instances
_robot_arm: Optional[RoboticArm3DOF] = None
_joint_memory: Optional[JointStateMemory] = None


def get_robot_arm() -> RoboticArm3DOF:
    """Get or create singleton robot arm instance."""
    global _robot_arm
    if _robot_arm is None:
        _robot_arm = RoboticArm3DOF()
    return _robot_arm


def get_joint_state_memory() -> JointStateMemory:
    """Get or create singleton memory instance."""
    global _joint_memory
    if _joint_memory is None:
        _joint_memory = JointStateMemory()
    return _joint_memory
