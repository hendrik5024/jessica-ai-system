"""
Object Detection and 3D Localization for Visual Servoing

This module provides real-time object detection with 3D position estimation
for visual servoing and spatial awareness.

Key capabilities:
- Object detection using YOLO/vision models
- 3D position estimation from 2D bounding boxes
- Object tracking across frames
- Confidence scoring and uncertainty quantification
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from pathlib import Path


class DetectionModel(Enum):
    """Available detection models"""
    YOLO_V8 = "yolov8"
    CLIP = "clip"
    CUSTOM = "custom"


@dataclass
class BoundingBox:
    """2D bounding box in image coordinates"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    confidence: float
    
    @property
    def center(self) -> Tuple[int, int]:
        """Center point of bounding box"""
        return (
            (self.x_min + self.x_max) // 2,
            (self.y_min + self.y_max) // 2
        )
    
    @property
    def width(self) -> int:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> int:
        return self.y_max - self.y_min
    
    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass
class Position3D:
    """3D position in camera or world coordinates"""
    x: float  # meters
    y: float  # meters
    z: float  # meters (depth)
    confidence: float
    coordinate_frame: str = "camera"  # "camera" or "world"
    
    def to_world(self, transform_matrix: np.ndarray) -> 'Position3D':
        """Transform to world coordinates"""
        pos = np.array([self.x, self.y, self.z, 1.0])
        world_pos = transform_matrix @ pos
        return Position3D(
            x=world_pos[0],
            y=world_pos[1],
            z=world_pos[2],
            confidence=self.confidence,
            coordinate_frame="world"
        )


@dataclass
class DetectedObject:
    """Detected object with 2D and 3D information"""
    object_id: str
    class_name: str
    bounding_box: BoundingBox
    position_3d: Optional[Position3D]
    timestamp: float
    features: Optional[np.ndarray] = None  # Visual features for tracking
    
    def __hash__(self):
        return hash(self.object_id)


class CameraIntrinsics:
    """Camera intrinsic parameters for 3D projection"""
    
    def __init__(
        self,
        fx: float,
        fy: float,
        cx: float,
        cy: float,
        width: int,
        height: int
    ):
        self.fx = fx  # Focal length x
        self.fy = fy  # Focal length y
        self.cx = cx  # Principal point x
        self.cy = cy  # Principal point y
        self.width = width
        self.height = height
        
        # Build camera matrix
        self.K = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ])
    
    @classmethod
    def from_fov(cls, fov_degrees: float, width: int, height: int) -> 'CameraIntrinsics':
        """Create from field of view"""
        fov_rad = np.radians(fov_degrees)
        fx = width / (2 * np.tan(fov_rad / 2))
        fy = fx  # Assume square pixels
        cx = width / 2
        cy = height / 2
        return cls(fx, fy, cx, cy, width, height)


class ObjectDetector:
    """Real-time object detection with 3D localization"""
    
    def __init__(
        self,
        model: DetectionModel = DetectionModel.YOLO_V8,
        camera_intrinsics: Optional[CameraIntrinsics] = None,
        confidence_threshold: float = 0.5
    ):
        self.model = model
        self.camera_intrinsics = camera_intrinsics
        self.confidence_threshold = confidence_threshold
        
        # Object tracking
        self.tracked_objects: Dict[str, DetectedObject] = {}
        self.next_object_id = 0
        
        # Performance metrics
        self.detection_times: List[float] = []
        
        # Initialize model
        self._init_model()
    
    def _init_model(self):
        """Initialize detection model"""
        if self.model == DetectionModel.YOLO_V8:
            # In production, load YOLOv8 model
            # from ultralytics import YOLO
            # self.detector = YOLO('yolov8n.pt')
            pass
        elif self.model == DetectionModel.CLIP:
            # In production, load CLIP model
            pass
        else:
            # Custom model
            pass
    
    def detect(
        self,
        image: np.ndarray,
        depth_map: Optional[np.ndarray] = None
    ) -> List[DetectedObject]:
        """
        Detect objects in image
        
        Args:
            image: RGB image (H, W, 3)
            depth_map: Optional depth map (H, W) in meters
            
        Returns:
            List of detected objects with 3D positions
        """
        start_time = time.time()
        
        # Run detection
        detections_2d = self._run_detection(image)
        
        # Estimate 3D positions
        detections_3d = []
        for det_2d in detections_2d:
            if depth_map is not None and self.camera_intrinsics is not None:
                pos_3d = self._estimate_3d_position(det_2d, depth_map)
            else:
                pos_3d = None
            
            # Create detected object
            obj = DetectedObject(
                object_id=self._get_next_id(),
                class_name=det_2d["class"],
                bounding_box=det_2d["bbox"],
                position_3d=pos_3d,
                timestamp=time.time(),
                features=det_2d.get("features")
            )
            detections_3d.append(obj)
        
        # Update tracking
        self._update_tracking(detections_3d)
        
        # Record performance
        elapsed = time.time() - start_time
        self.detection_times.append(elapsed)
        
        return detections_3d
    
    def _run_detection(self, image: np.ndarray) -> List[Dict]:
        """Run 2D detection on image"""
        # In production, use actual model
        # For now, return mock detections
        
        # Example: Detect using YOLO
        # results = self.detector(image)
        # detections = []
        # for r in results:
        #     boxes = r.boxes
        #     for box in boxes:
        #         detections.append({
        #             "class": box.cls,
        #             "bbox": BoundingBox(...),
        #             "confidence": box.conf
        #         })
        
        return []  # Mock
    
    def _estimate_3d_position(
        self,
        detection_2d: Dict,
        depth_map: np.ndarray
    ) -> Position3D:
        """Estimate 3D position from 2D detection and depth"""
        bbox = detection_2d["bbox"]
        
        # Get depth at object center
        cx, cy = bbox.center
        depth = self._get_robust_depth(depth_map, bbox)
        
        # Back-project to 3D using camera intrinsics
        x_3d = (cx - self.camera_intrinsics.cx) * depth / self.camera_intrinsics.fx
        y_3d = (cy - self.camera_intrinsics.cy) * depth / self.camera_intrinsics.fy
        z_3d = depth
        
        # Estimate confidence based on depth quality
        confidence = self._estimate_position_confidence(depth_map, bbox)
        
        return Position3D(
            x=x_3d,
            y=y_3d,
            z=z_3d,
            confidence=confidence,
            coordinate_frame="camera"
        )
    
    def _get_robust_depth(self, depth_map: np.ndarray, bbox: BoundingBox) -> float:
        """Get robust depth estimate from bounding box region"""
        # Extract depth values in bbox
        depth_region = depth_map[
            bbox.y_min:bbox.y_max,
            bbox.x_min:bbox.x_max
        ]
        
        # Use median for robustness (ignore outliers)
        valid_depths = depth_region[depth_region > 0]
        if len(valid_depths) == 0:
            return 1.0  # Default depth
        
        return float(np.median(valid_depths))
    
    def _estimate_position_confidence(
        self,
        depth_map: np.ndarray,
        bbox: BoundingBox
    ) -> float:
        """Estimate confidence in 3D position"""
        # Extract depth region
        depth_region = depth_map[
            bbox.y_min:bbox.y_max,
            bbox.x_min:bbox.x_max
        ]
        
        valid_depths = depth_region[depth_region > 0]
        if len(valid_depths) == 0:
            return 0.1
        
        # Confidence based on:
        # 1. Depth variance (lower is better)
        # 2. Coverage (more valid pixels is better)
        variance = float(np.var(valid_depths))
        coverage = len(valid_depths) / depth_region.size
        
        # Combine metrics
        confidence = coverage * np.exp(-variance / 0.1)
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _update_tracking(self, new_detections: List[DetectedObject]):
        """Update object tracking across frames"""
        # Simple tracking based on IoU and feature matching
        # In production, use Kalman filter or SORT
        
        for det in new_detections:
            # Find best match in existing tracks
            best_match = None
            best_score = 0.0
            
            for obj_id, tracked_obj in self.tracked_objects.items():
                score = self._compute_match_score(det, tracked_obj)
                if score > best_score and score > 0.5:
                    best_score = score
                    best_match = obj_id
            
            if best_match:
                # Update existing track
                det.object_id = best_match
                self.tracked_objects[best_match] = det
            else:
                # New track
                self.tracked_objects[det.object_id] = det
        
        # Remove stale tracks (not seen in last 5 seconds)
        current_time = time.time()
        stale_ids = [
            obj_id for obj_id, obj in self.tracked_objects.items()
            if current_time - obj.timestamp > 5.0
        ]
        for obj_id in stale_ids:
            del self.tracked_objects[obj_id]
    
    def _compute_match_score(
        self,
        det1: DetectedObject,
        det2: DetectedObject
    ) -> float:
        """Compute matching score between detections"""
        # Class must match
        if det1.class_name != det2.class_name:
            return 0.0
        
        # IoU of bounding boxes
        iou = self._compute_iou(det1.bounding_box, det2.bounding_box)
        
        # Feature similarity (if available)
        feature_sim = 1.0
        if det1.features is not None and det2.features is not None:
            feature_sim = self._cosine_similarity(det1.features, det2.features)
        
        # Combined score
        return 0.7 * iou + 0.3 * feature_sim
    
    def _compute_iou(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """Compute Intersection over Union"""
        x_left = max(bbox1.x_min, bbox2.x_min)
        y_top = max(bbox1.y_min, bbox2.y_min)
        x_right = min(bbox1.x_max, bbox2.x_max)
        y_bottom = min(bbox1.y_max, bbox2.y_max)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = bbox1.area
        area2 = bbox2.area
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Compute cosine similarity between feature vectors"""
        norm1 = np.linalg.norm(feat1)
        norm2 = np.linalg.norm(feat2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(feat1, feat2) / (norm1 * norm2))
    
    def _get_next_id(self) -> str:
        """Generate next object ID"""
        obj_id = f"obj_{self.next_object_id}"
        self.next_object_id += 1
        return obj_id
    
    def get_tracked_object(self, object_id: str) -> Optional[DetectedObject]:
        """Get currently tracked object by ID"""
        return self.tracked_objects.get(object_id)
    
    def get_all_tracked_objects(self) -> List[DetectedObject]:
        """Get all currently tracked objects"""
        return list(self.tracked_objects.values())
    
    def find_object_by_class(self, class_name: str) -> List[DetectedObject]:
        """Find all tracked objects of a specific class"""
        return [
            obj for obj in self.tracked_objects.values()
            if obj.class_name == class_name
        ]
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get detection performance statistics"""
        if not self.detection_times:
            return {"avg_time": 0.0, "fps": 0.0}
        
        avg_time = np.mean(self.detection_times[-100:])  # Last 100 frames
        fps = 1.0 / avg_time if avg_time > 0 else 0.0
        
        return {
            "avg_time": avg_time,
            "fps": fps,
            "tracked_objects": len(self.tracked_objects)
        }


def create_mock_detector(
    image_width: int = 640,
    image_height: int = 480,
    fov_degrees: float = 60.0
) -> ObjectDetector:
    """Create mock detector for testing"""
    intrinsics = CameraIntrinsics.from_fov(fov_degrees, image_width, image_height)
    return ObjectDetector(
        model=DetectionModel.YOLO_V8,
        camera_intrinsics=intrinsics,
        confidence_threshold=0.5
    )
