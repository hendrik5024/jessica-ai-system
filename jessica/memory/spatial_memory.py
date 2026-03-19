"""
Spatial Memory Store - Cross-Modal Object Location Memory

Maintains a persistent spatial map of objects in the physical environment.
Integrates visual detections with semantic memory.

Key capabilities:
- 3D spatial database of objects
- Temporal tracking (objects persist over time)
- Uncertainty quantification (confidence in locations)
- Cross-modal queries ("where is the screwdriver?")
- Integration with semantic memory
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path
from datetime import datetime

# Import from other modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from perception.object_detector import DetectedObject, Position3D


class ObjectStatus(Enum):
    """Object tracking status"""
    ACTIVE = "active"  # Currently visible
    INACTIVE = "inactive"  # Not recently seen
    MOVED = "moved"  # Detected at new location
    MISSING = "missing"  # Expected but not found


@dataclass
class SpatialObject:
    """Object with spatial and temporal information"""
    object_id: str
    class_name: str
    position: Position3D
    first_seen: float  # timestamp
    last_seen: float  # timestamp
    observation_count: int
    confidence: float  # Confidence in current position
    status: ObjectStatus
    semantic_id: Optional[str] = None  # Link to semantic memory
    properties: Dict = field(default_factory=dict)  # Additional metadata
    
    def age(self) -> float:
        """Time since last observation (seconds)"""
        return time.time() - self.last_seen
    
    def is_stale(self, threshold: float = 60.0) -> bool:
        """Check if object hasn't been seen recently"""
        return self.age() > threshold


@dataclass
class SpatialQuery:
    """Query for spatial memory"""
    class_name: Optional[str] = None
    semantic_id: Optional[str] = None
    position_near: Optional[Position3D] = None
    max_distance: Optional[float] = None
    min_confidence: float = 0.5
    status: Optional[ObjectStatus] = None


class SpatialMemoryStore:
    """
    Persistent spatial map of objects in the environment
    
    Maintains 3D positions with uncertainty, handles occlusion,
    and integrates with semantic memory.
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        stale_threshold: float = 60.0,  # seconds
        confidence_decay_rate: float = 0.01  # per second
    ):
        self.storage_path = storage_path
        self.stale_threshold = stale_threshold
        self.confidence_decay_rate = confidence_decay_rate
        
        # Spatial database
        self.objects: Dict[str, SpatialObject] = {}
        
        # Spatial index for fast queries
        self._position_index: Dict[Tuple[int, int, int], Set[str]] = {}
        self._grid_size = 0.1  # 10cm voxels
        
        # Statistics
        self.total_observations = 0
        self.total_updates = 0
        
        # Load existing data
        if storage_path and storage_path.exists():
            self.load()
    
    def add_observation(
        self,
        detected_object: DetectedObject,
        semantic_id: Optional[str] = None
    ):
        """
        Add or update object observation
        
        Args:
            detected_object: Newly detected object
            semantic_id: Optional link to semantic memory
        """
        self.total_observations += 1
        
        if detected_object.position_3d is None:
            return  # Can't store without 3D position
        
        # Check if object already exists (by matching)
        existing_id = self._find_matching_object(detected_object)
        
        if existing_id:
            # Update existing object
            self._update_object(existing_id, detected_object, semantic_id)
        else:
            # Create new object
            self._create_object(detected_object, semantic_id)
        
        # Decay confidence of other objects
        self._decay_confidence()
        
        # Save periodically
        if self.total_observations % 10 == 0:
            self.save()
    
    def _find_matching_object(
        self,
        detection: DetectedObject
    ) -> Optional[str]:
        """Find existing object that matches detection"""
        # Search nearby objects
        nearby = self._get_nearby_objects(detection.position_3d, radius=0.2)
        
        best_match = None
        best_score = 0.0
        
        for obj_id in nearby:
            obj = self.objects[obj_id]
            
            # Must match class
            if obj.class_name != detection.class_name:
                continue
            
            # Compute match score
            distance = self._compute_distance(obj.position, detection.position_3d)
            
            # Closer = better match
            score = np.exp(-distance / 0.1)  # 10cm characteristic length
            
            if score > best_score and score > 0.5:
                best_score = score
                best_match = obj_id
        
        return best_match
    
    def _update_object(
        self,
        object_id: str,
        detection: DetectedObject,
        semantic_id: Optional[str]
    ):
        """Update existing object with new observation"""
        obj = self.objects[object_id]
        
        # Update position (exponential moving average)
        alpha = 0.7  # Weight for new observation
        obj.position = Position3D(
            x=alpha * detection.position_3d.x + (1 - alpha) * obj.position.x,
            y=alpha * detection.position_3d.y + (1 - alpha) * obj.position.y,
            z=alpha * detection.position_3d.z + (1 - alpha) * obj.position.z,
            confidence=max(obj.position.confidence, detection.position_3d.confidence),
            coordinate_frame=obj.position.coordinate_frame
        )
        
        # Update temporal info
        obj.last_seen = time.time()
        obj.observation_count += 1
        obj.status = ObjectStatus.ACTIVE
        
        # Update confidence (more observations = higher confidence)
        obj.confidence = min(1.0, obj.confidence + 0.1)
        
        # Update semantic link
        if semantic_id:
            obj.semantic_id = semantic_id
        
        # Update spatial index
        self._update_spatial_index(object_id, obj.position)
        
        self.total_updates += 1
    
    def _create_object(
        self,
        detection: DetectedObject,
        semantic_id: Optional[str]
    ):
        """Create new spatial object"""
        current_time = time.time()
        
        obj = SpatialObject(
            object_id=detection.object_id,
            class_name=detection.class_name,
            position=detection.position_3d,
            first_seen=current_time,
            last_seen=current_time,
            observation_count=1,
            confidence=detection.position_3d.confidence,
            status=ObjectStatus.ACTIVE,
            semantic_id=semantic_id
        )
        
        self.objects[obj.object_id] = obj
        self._update_spatial_index(obj.object_id, obj.position)
    
    def _decay_confidence(self):
        """Decay confidence of objects not recently observed"""
        current_time = time.time()
        
        for obj in self.objects.values():
            if obj.status == ObjectStatus.ACTIVE:
                # Active objects don't decay
                continue
            
            # Decay based on age
            age = current_time - obj.last_seen
            decay = age * self.confidence_decay_rate
            obj.confidence = max(0.0, obj.confidence - decay)
            
            # Update status
            if obj.is_stale(self.stale_threshold):
                if obj.confidence < 0.3:
                    obj.status = ObjectStatus.MISSING
                else:
                    obj.status = ObjectStatus.INACTIVE
    
    def query(self, query: SpatialQuery) -> List[SpatialObject]:
        """
        Query spatial memory
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching objects
        """
        results = []
        
        for obj in self.objects.values():
            # Filter by class
            if query.class_name and obj.class_name != query.class_name:
                continue
            
            # Filter by semantic ID
            if query.semantic_id and obj.semantic_id != query.semantic_id:
                continue
            
            # Filter by position
            if query.position_near and query.max_distance:
                distance = self._compute_distance(obj.position, query.position_near)
                if distance > query.max_distance:
                    continue
            
            # Filter by confidence
            if obj.confidence < query.min_confidence:
                continue
            
            # Filter by status
            if query.status and obj.status != query.status:
                continue
            
            results.append(obj)
        
        # Sort by confidence (highest first)
        results.sort(key=lambda o: o.confidence, reverse=True)
        
        return results
    
    def get_object_location(
        self,
        class_name: Optional[str] = None,
        semantic_id: Optional[str] = None
    ) -> Optional[Position3D]:
        """
        Get location of object (most confident match)
        
        Args:
            class_name: Object class name
            semantic_id: Semantic memory ID
            
        Returns:
            Object position or None
        """
        query = SpatialQuery(
            class_name=class_name,
            semantic_id=semantic_id,
            status=ObjectStatus.ACTIVE
        )
        
        results = self.query(query)
        
        if results:
            return results[0].position
        return None
    
    def _compute_distance(self, pos1: Position3D, pos2: Position3D) -> float:
        """Compute Euclidean distance between positions"""
        return np.sqrt(
            (pos1.x - pos2.x)**2 +
            (pos1.y - pos2.y)**2 +
            (pos1.z - pos2.z)**2
        )
    
    def _get_nearby_objects(
        self,
        position: Position3D,
        radius: float
    ) -> Set[str]:
        """Get object IDs near position"""
        # Get voxel coordinates
        vx, vy, vz = self._position_to_voxel(position)
        
        # Search radius in voxels
        r_voxels = int(np.ceil(radius / self._grid_size))
        
        nearby_ids = set()
        
        for dx in range(-r_voxels, r_voxels + 1):
            for dy in range(-r_voxels, r_voxels + 1):
                for dz in range(-r_voxels, r_voxels + 1):
                    voxel = (vx + dx, vy + dy, vz + dz)
                    if voxel in self._position_index:
                        nearby_ids.update(self._position_index[voxel])
        
        return nearby_ids
    
    def _position_to_voxel(self, position: Position3D) -> Tuple[int, int, int]:
        """Convert position to voxel coordinates"""
        return (
            int(position.x / self._grid_size),
            int(position.y / self._grid_size),
            int(position.z / self._grid_size)
        )
    
    def _update_spatial_index(self, object_id: str, position: Position3D):
        """Update spatial index for fast queries"""
        voxel = self._position_to_voxel(position)
        
        if voxel not in self._position_index:
            self._position_index[voxel] = set()
        
        self._position_index[voxel].add(object_id)
    
    def get_statistics(self) -> Dict:
        """Get spatial memory statistics"""
        active_objects = sum(1 for o in self.objects.values() if o.status == ObjectStatus.ACTIVE)
        inactive_objects = sum(1 for o in self.objects.values() if o.status == ObjectStatus.INACTIVE)
        
        return {
            "total_objects": len(self.objects),
            "active_objects": active_objects,
            "inactive_objects": inactive_objects,
            "total_observations": self.total_observations,
            "total_updates": self.total_updates,
            "voxels_used": len(self._position_index)
        }
    
    def save(self):
        """Save spatial memory to disk"""
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "objects": [
                {
                    "object_id": obj.object_id,
                    "class_name": obj.class_name,
                    "position": {
                        "x": obj.position.x,
                        "y": obj.position.y,
                        "z": obj.position.z,
                        "confidence": obj.position.confidence,
                        "frame": obj.position.coordinate_frame
                    },
                    "first_seen": obj.first_seen,
                    "last_seen": obj.last_seen,
                    "observation_count": obj.observation_count,
                    "confidence": obj.confidence,
                    "status": obj.status.value,
                    "semantic_id": obj.semantic_id,
                    "properties": obj.properties
                }
                for obj in self.objects.values()
            ]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load spatial memory from disk"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        self.objects = {}
        self._position_index = {}
        
        for obj_data in data.get("objects", []):
            pos = obj_data["position"]
            position = Position3D(
                x=pos["x"],
                y=pos["y"],
                z=pos["z"],
                confidence=pos["confidence"],
                coordinate_frame=pos["frame"]
            )
            
            obj = SpatialObject(
                object_id=obj_data["object_id"],
                class_name=obj_data["class_name"],
                position=position,
                first_seen=obj_data["first_seen"],
                last_seen=obj_data["last_seen"],
                observation_count=obj_data["observation_count"],
                confidence=obj_data["confidence"],
                status=ObjectStatus(obj_data["status"]),
                semantic_id=obj_data.get("semantic_id"),
                properties=obj_data.get("properties", {})
            )
            
            self.objects[obj.object_id] = obj
            self._update_spatial_index(obj.object_id, obj.position)
    
    def clear_stale_objects(self):
        """Remove objects that haven't been seen in a long time"""
        to_remove = [
            obj_id for obj_id, obj in self.objects.items()
            if obj.status == ObjectStatus.MISSING and obj.confidence < 0.1
        ]
        
        for obj_id in to_remove:
            del self.objects[obj_id]
        
        # Rebuild spatial index
        self._rebuild_spatial_index()
    
    def _rebuild_spatial_index(self):
        """Rebuild spatial index from scratch"""
        self._position_index = {}
        for obj_id, obj in self.objects.items():
            self._update_spatial_index(obj_id, obj.position)


def create_spatial_memory(storage_path: Optional[Path] = None) -> SpatialMemoryStore:
    """Create spatial memory store"""
    if storage_path is None:
        storage_path = Path.home() / ".jessica" / "spatial_memory.json"
    
    return SpatialMemoryStore(storage_path=storage_path)
