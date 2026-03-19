"""
Sensory Fusion Architecture

Integrates multi-modal sensory data (vision, spatial, semantic, tactile)
into unified perception for AGI-level environmental understanding.

Key capabilities:
- Multi-modal embeddings (vision + language + position + time)
- Temporal coherence (track objects over time)
- Uncertainty fusion (combine noisy sensors)
- Attention mechanisms (what to focus on)
- Cross-modal prediction (predict one modality from another)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time

# Import from other modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from perception.object_detector import DetectedObject, ObjectDetector, Position3D
from memory.spatial_memory import SpatialMemoryStore, SpatialObject, ObjectStatus
try:
    from memory.semantic_memory import SemanticMemoryStore
except ImportError:
    SemanticMemoryStore = None  # Optional dependency


class ModalityType(Enum):
    """Sensory modality types"""
    VISION = "vision"
    SPATIAL = "spatial"
    SEMANTIC = "semantic"
    TACTILE = "tactile"
    AUDIO = "audio"
    PROPRIOCEPTION = "proprioception"


@dataclass
class SensoryInput:
    """Single sensory input"""
    modality: ModalityType
    data: Any
    timestamp: float
    confidence: float
    source_id: str


@dataclass
class FusedPercept:
    """Fused perception from multiple modalities"""
    object_id: str
    class_name: str
    position: Position3D
    semantic_embedding: Optional[np.ndarray]
    visual_features: Optional[np.ndarray]
    properties: Dict[str, Any]
    modalities_used: List[ModalityType]
    fusion_confidence: float
    timestamp: float
    
    def has_modality(self, modality: ModalityType) -> bool:
        """Check if percept includes data from modality"""
        return modality in self.modalities_used


@dataclass
class AttentionState:
    """What the system is currently paying attention to"""
    focus_object_id: Optional[str]
    focus_reason: str  # "task", "novelty", "motion", "query"
    attention_weights: Dict[ModalityType, float]  # Which modalities to prioritize
    timestamp: float


class SensoryFusionEngine:
    """
    Multi-modal sensory fusion for unified environmental perception
    
    Combines vision, spatial memory, semantic knowledge, and other modalities
    into coherent percepts with uncertainty quantification.
    """
    
    def __init__(
        self,
        object_detector: ObjectDetector,
        spatial_memory: SpatialMemoryStore,
        semantic_memory: Optional[SemanticMemoryStore] = None
    ):
        self.object_detector = object_detector
        self.spatial_memory = spatial_memory
        self.semantic_memory = semantic_memory
        
        # Current sensory state
        self.current_percepts: Dict[str, FusedPercept] = {}
        self.sensory_buffer: List[SensoryInput] = []
        
        # Attention state
        self.attention = AttentionState(
            focus_object_id=None,
            focus_reason="idle",
            attention_weights={
                ModalityType.VISION: 1.0,
                ModalityType.SPATIAL: 0.8,
                ModalityType.SEMANTIC: 0.6
            },
            timestamp=time.time()
        )
        
        # Temporal tracking
        self.percept_history: List[FusedPercept] = []
        self.max_history = 100
        
        # Performance metrics
        self.fusion_times: List[float] = []
    
    def process_frame(
        self,
        image: np.ndarray,
        depth_map: Optional[np.ndarray] = None
    ) -> List[FusedPercept]:
        """
        Process single frame and fuse all modalities
        
        Args:
            image: RGB image
            depth_map: Optional depth map
            
        Returns:
            List of fused percepts
        """
        start_time = time.time()
        
        # 1. Vision modality: Detect objects
        detections = self.object_detector.detect(image, depth_map)
        
        # 2. Spatial modality: Retrieve known object locations
        from memory.spatial_memory import SpatialQuery
        spatial_objects = self.spatial_memory.query(
            SpatialQuery(status=ObjectStatus.ACTIVE)
        )
        
        # 3. Associate detections with spatial memory
        associations = self._associate_detections_with_memory(
            detections, spatial_objects
        )
        
        # 4. Fuse modalities for each object
        fused_percepts = []
        for detection, spatial_obj in associations:
            percept = self._fuse_modalities(detection, spatial_obj)
            fused_percepts.append(percept)
            
            # Update spatial memory
            self.spatial_memory.add_observation(detection, percept.semantic_embedding)
        
        # 5. Handle unassociated detections (new objects)
        associated_detection_ids = {d.object_id for d, _ in associations if d}
        for detection in detections:
            if detection.object_id not in associated_detection_ids:
                percept = self._fuse_modalities(detection, None)
                fused_percepts.append(percept)
                self.spatial_memory.add_observation(detection)
        
        # 6. Apply attention mechanism
        fused_percepts = self._apply_attention(fused_percepts)
        
        # 7. Update current state
        self.current_percepts = {p.object_id: p for p in fused_percepts}
        
        # 8. Update history
        self.percept_history.extend(fused_percepts)
        if len(self.percept_history) > self.max_history:
            self.percept_history = self.percept_history[-self.max_history:]
        
        # Performance tracking
        elapsed = time.time() - start_time
        self.fusion_times.append(elapsed)
        
        return fused_percepts
    
    def _associate_detections_with_memory(
        self,
        detections: List[DetectedObject],
        spatial_objects: List[SpatialObject]
    ) -> List[Tuple[Optional[DetectedObject], Optional[SpatialObject]]]:
        """
        Associate visual detections with spatial memory
        
        Returns list of (detection, spatial_object) pairs
        """
        associations = []
        used_detections = set()
        used_spatial = set()
        
        # Greedy matching based on class and distance
        for spatial_obj in spatial_objects:
            best_detection = None
            best_distance = float('inf')
            
            for detection in detections:
                if detection.object_id in used_detections:
                    continue
                
                # Must match class
                if detection.class_name != spatial_obj.class_name:
                    continue
                
                # Compute distance
                if detection.position_3d:
                    distance = np.sqrt(
                        (detection.position_3d.x - spatial_obj.position.x)**2 +
                        (detection.position_3d.y - spatial_obj.position.y)**2 +
                        (detection.position_3d.z - spatial_obj.position.z)**2
                    )
                    
                    if distance < best_distance and distance < 0.3:  # 30cm threshold
                        best_distance = distance
                        best_detection = detection
            
            if best_detection:
                associations.append((best_detection, spatial_obj))
                used_detections.add(best_detection.object_id)
                used_spatial.add(spatial_obj.object_id)
            else:
                # Spatial object not currently visible
                associations.append((None, spatial_obj))
        
        return associations
    
    def _fuse_modalities(
        self,
        detection: Optional[DetectedObject],
        spatial_obj: Optional[SpatialObject]
    ) -> FusedPercept:
        """
        Fuse multiple modalities into single percept
        
        Uses weighted fusion based on confidence and attention.
        """
        modalities_used = []
        
        # Determine object identity
        if detection:
            object_id = detection.object_id
            class_name = detection.class_name
            modalities_used.append(ModalityType.VISION)
        elif spatial_obj:
            object_id = spatial_obj.object_id
            class_name = spatial_obj.class_name
            modalities_used.append(ModalityType.SPATIAL)
        else:
            raise ValueError("Must provide at least one of detection or spatial_obj")
        
        # Fuse position (weighted by confidence)
        if detection and detection.position_3d and spatial_obj:
            # Both available: weighted fusion
            w_det = detection.position_3d.confidence
            w_spatial = spatial_obj.confidence
            w_total = w_det + w_spatial
            
            position = Position3D(
                x=(w_det * detection.position_3d.x + w_spatial * spatial_obj.position.x) / w_total,
                y=(w_det * detection.position_3d.y + w_spatial * spatial_obj.position.y) / w_total,
                z=(w_det * detection.position_3d.z + w_spatial * spatial_obj.position.z) / w_total,
                confidence=min(1.0, w_total / 2.0),
                coordinate_frame="world"
            )
        elif detection and detection.position_3d:
            # Only detection available
            position = detection.position_3d
        elif spatial_obj:
            # Only spatial memory available
            position = spatial_obj.position
        else:
            # No position available
            position = Position3D(0, 0, 0, 0.0, "world")
        
        # Get semantic embedding
        semantic_embedding = None
        if self.semantic_memory and spatial_obj and spatial_obj.semantic_id:
            # Retrieve from semantic memory
            semantic_embedding = self._get_semantic_embedding(spatial_obj.semantic_id)
            modalities_used.append(ModalityType.SEMANTIC)
        
        # Visual features
        visual_features = detection.features if detection else None
        
        # Properties (combine from both sources)
        properties = {}
        if spatial_obj:
            properties.update(spatial_obj.properties)
        if detection:
            properties["bounding_box"] = {
                "x_min": detection.bounding_box.x_min,
                "y_min": detection.bounding_box.y_min,
                "x_max": detection.bounding_box.x_max,
                "y_max": detection.bounding_box.y_max
            }
        
        # Fusion confidence (average of all modalities)
        confidences = []
        if detection:
            confidences.append(detection.bounding_box.confidence)
        if spatial_obj:
            confidences.append(spatial_obj.confidence)
        if detection and detection.position_3d:
            confidences.append(detection.position_3d.confidence)
        
        fusion_confidence = np.mean(confidences) if confidences else 0.5
        
        return FusedPercept(
            object_id=object_id,
            class_name=class_name,
            position=position,
            semantic_embedding=semantic_embedding,
            visual_features=visual_features,
            properties=properties,
            modalities_used=modalities_used,
            fusion_confidence=fusion_confidence,
            timestamp=time.time()
        )
    
    def _get_semantic_embedding(self, semantic_id: str) -> Optional[np.ndarray]:
        """Retrieve semantic embedding from memory"""
        # In production, query semantic memory
        # For now, return mock embedding
        return np.random.randn(512)  # Mock 512-dim embedding
    
    def _apply_attention(
        self,
        percepts: List[FusedPercept]
    ) -> List[FusedPercept]:
        """
        Apply attention mechanism to prioritize important percepts
        
        Attention based on:
        - Current focus
        - Novelty (new objects)
        - Motion (moving objects)
        - Task relevance
        """
        if not percepts:
            return percepts
        
        # Compute attention scores
        for percept in percepts:
            attention_score = 0.0
            
            # Focus object gets highest attention
            if percept.object_id == self.attention.focus_object_id:
                attention_score += 1.0
            
            # Novel objects get attention
            if percept.object_id not in self.current_percepts:
                attention_score += 0.5
            
            # High confidence gets attention
            attention_score += percept.fusion_confidence * 0.3
            
            percept.properties["attention_score"] = attention_score
        
        # Sort by attention (for now, return all)
        percepts.sort(key=lambda p: p.properties.get("attention_score", 0.0), reverse=True)
        
        return percepts
    
    def set_attention_focus(
        self,
        object_id: Optional[str],
        reason: str = "query"
    ):
        """Set attention focus to specific object"""
        self.attention.focus_object_id = object_id
        self.attention.focus_reason = reason
        self.attention.timestamp = time.time()
    
    def query_object_location(
        self,
        class_name: Optional[str] = None,
        semantic_query: Optional[str] = None
    ) -> Optional[Position3D]:
        """
        Query for object location (cross-modal)
        
        Args:
            class_name: Object class ("screwdriver")
            semantic_query: Natural language query
            
        Returns:
            Object position or None
        """
        # Try current percepts first (most up-to-date)
        if class_name:
            for percept in self.current_percepts.values():
                if percept.class_name == class_name:
                    return percept.position
        
        # Fall back to spatial memory
        return self.spatial_memory.get_object_location(class_name=class_name)
    
    def predict_object_future_position(
        self,
        object_id: str,
        time_ahead: float
    ) -> Optional[Position3D]:
        """
        Predict where object will be in the future
        
        Uses temporal history to estimate velocity.
        """
        # Get object history
        history = [
            p for p in self.percept_history
            if p.object_id == object_id
        ]
        
        if len(history) < 2:
            # Not enough history
            return None
        
        # Estimate velocity from recent history
        recent = history[-5:]  # Last 5 observations
        
        velocities = []
        for i in range(len(recent) - 1):
            dt = recent[i+1].timestamp - recent[i].timestamp
            if dt > 0:
                vx = (recent[i+1].position.x - recent[i].position.x) / dt
                vy = (recent[i+1].position.y - recent[i].position.y) / dt
                vz = (recent[i+1].position.z - recent[i].position.z) / dt
                velocities.append([vx, vy, vz])
        
        if not velocities:
            return None
        
        # Average velocity
        avg_velocity = np.mean(velocities, axis=0)
        
        # Predict future position
        current_pos = history[-1].position
        predicted_pos = Position3D(
            x=current_pos.x + avg_velocity[0] * time_ahead,
            y=current_pos.y + avg_velocity[1] * time_ahead,
            z=current_pos.z + avg_velocity[2] * time_ahead,
            confidence=current_pos.confidence * 0.8,  # Lower confidence for prediction
            coordinate_frame=current_pos.coordinate_frame
        )
        
        return predicted_pos
    
    def get_environmental_context(self) -> Dict[str, Any]:
        """
        Get high-level environmental context
        
        Returns summary of what's currently perceived.
        """
        active_percepts = list(self.current_percepts.values())
        
        # Count objects by class
        class_counts = {}
        for percept in active_percepts:
            class_counts[percept.class_name] = class_counts.get(percept.class_name, 0) + 1
        
        # Spatial extent
        if active_percepts:
            positions = [p.position for p in active_percepts]
            x_vals = [p.x for p in positions]
            y_vals = [p.y for p in positions]
            z_vals = [p.z for p in positions]
            
            spatial_extent = {
                "x_range": (min(x_vals), max(x_vals)),
                "y_range": (min(y_vals), max(y_vals)),
                "z_range": (min(z_vals), max(z_vals))
            }
        else:
            spatial_extent = {}
        
        return {
            "num_objects": len(active_percepts),
            "object_classes": class_counts,
            "spatial_extent": spatial_extent,
            "attention_focus": self.attention.focus_object_id,
            "fusion_confidence": np.mean([p.fusion_confidence for p in active_percepts]) if active_percepts else 0.0
        }
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get fusion performance statistics"""
        if not self.fusion_times:
            return {"avg_time": 0.0, "fps": 0.0}
        
        avg_time = np.mean(self.fusion_times[-100:])
        fps = 1.0 / avg_time if avg_time > 0 else 0.0
        
        return {
            "avg_fusion_time": avg_time,
            "fusion_fps": fps,
            "active_percepts": len(self.current_percepts),
            "history_size": len(self.percept_history)
        }


def create_fusion_engine(
    use_mock: bool = True
) -> SensoryFusionEngine:
    """Create sensory fusion engine"""
    from perception.object_detector import create_mock_detector
    from memory.spatial_memory import create_spatial_memory
    
    detector = create_mock_detector()
    spatial_memory = create_spatial_memory()
    
    return SensoryFusionEngine(
        object_detector=detector,
        spatial_memory=spatial_memory,
        semantic_memory=None  # Optional
    )
