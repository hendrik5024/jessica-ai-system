"""
Jessica Perception Module

Multi-modal sensory perception for AGI-level environmental understanding.
"""

from .object_detector import (
    ObjectDetector,
    DetectedObject,
    BoundingBox,
    Position3D,
    CameraIntrinsics,
    DetectionModel,
    create_mock_detector
)

from .visual_servoing import (
    VisualServoController,
    ServoingState,
    ServoConfig,
    ServoMode,
    create_servo_controller
)

from .sensory_fusion import (
    SensoryFusionEngine,
    FusedPercept,
    ModalityType,
    AttentionState,
    SensoryInput,
    create_fusion_engine
)

__all__ = [
    # Object Detection
    "ObjectDetector",
    "DetectedObject",
    "BoundingBox",
    "Position3D",
    "CameraIntrinsics",
    "DetectionModel",
    "create_mock_detector",
    
    # Visual Servoing
    "VisualServoController",
    "ServoingState",
    "ServoConfig",
    "ServoMode",
    "create_servo_controller",
    
    # Sensory Fusion
    "SensoryFusionEngine",
    "FusedPercept",
    "ModalityType",
    "AttentionState",
    "SensoryInput",
    "create_fusion_engine",
]
