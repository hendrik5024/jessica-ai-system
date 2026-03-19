"""
Comprehensive Test Suite for Multi-Modal Sensory Fusion

Tests all components of the sensory fusion system:
- Object detection and localization
- Hand-eye calibration
- Visual servoing
- Spatial memory
- Sensory fusion
- Grasp planning
- Integrated manipulation
"""

import pytest
import numpy as np
import time
from pathlib import Path

# Import all components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from jessica.perception.object_detector import (
    ObjectDetector, DetectionModel, CameraIntrinsics, BoundingBox,
    DetectedObject, Position3D, create_mock_detector
)
from jessica.robotics.hand_eye_calibration import (
    HandEyeCalibration, CalibrationType, Pose, create_mock_calibration
)
from jessica.perception.visual_servoing import (
    VisualServoController, ServoMode, ServoConfig, create_servo_controller
)
from jessica.memory.spatial_memory import (
    SpatialMemoryStore, SpatialObject, ObjectStatus, SpatialQuery,
    create_spatial_memory
)
from jessica.perception.sensory_fusion import (
    SensoryFusionEngine, ModalityType, FusedPercept, create_fusion_engine
)
from jessica.robotics.grasp_planner import (
    GraspPlanner, GraspType, GraspPose, create_grasp_planner
)


# ============================================================================
# Test Object Detection
# ============================================================================

class TestObjectDetector:
    """Test object detection and 3D localization"""
    
    def test_camera_intrinsics(self):
        """Test camera intrinsic parameter creation"""
        intrinsics = CameraIntrinsics.from_fov(60.0, 640, 480)
        
        assert intrinsics.width == 640
        assert intrinsics.height == 480
        assert intrinsics.K[0, 0] > 0  # fx
        assert intrinsics.K[1, 1] > 0  # fy
        assert intrinsics.K[0, 2] == 320  # cx
        assert intrinsics.K[1, 2] == 240  # cy
    
    def test_detector_creation(self):
        """Test detector initialization"""
        detector = create_mock_detector()
        
        assert detector.model == DetectionModel.YOLO_V8
        assert detector.confidence_threshold == 0.5
        assert len(detector.tracked_objects) == 0
    
    def test_detection_mock(self):
        """Test mock detection (returns empty list)"""
        detector = create_mock_detector()
        
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        depth_map = np.ones((480, 640)) * 1.0
        
        detections = detector.detect(image, depth_map)
        
        # Mock detector returns empty list
        assert isinstance(detections, list)
    
    def test_3d_position_transform(self):
        """Test 3D position coordinate transformation"""
        pos_camera = Position3D(0.1, 0.2, 1.0, 0.9, "camera")
        
        transform = np.eye(4)
        transform[:3, 3] = [0.5, 0.0, 0.3]  # Translation
        
        pos_world = pos_camera.to_world(transform)
        
        assert pos_world.coordinate_frame == "world"
        assert pos_world.x == pytest.approx(0.6, 0.01)
        assert pos_world.z == pytest.approx(1.3, 0.01)


# ============================================================================
# Test Hand-Eye Calibration
# ============================================================================

class TestHandEyeCalibration:
    """Test camera-robot coordinate transformation"""
    
    def test_pose_to_matrix(self):
        """Test pose to transformation matrix conversion"""
        pose = Pose(0.3, 0.1, 0.2, 0.0, 0.0, np.pi/4)
        T = pose.to_matrix()
        
        assert T.shape == (4, 4)
        assert T[3, 3] == 1.0
        assert T[0, 3] == pytest.approx(0.3)
        assert T[1, 3] == pytest.approx(0.1)
        assert T[2, 3] == pytest.approx(0.2)
    
    def test_pose_from_matrix(self):
        """Test matrix to pose conversion"""
        original = Pose(0.3, 0.1, 0.2, 0.0, 0.0, np.pi/4)
        T = original.to_matrix()
        recovered = Pose.from_matrix(T)
        
        assert recovered.x == pytest.approx(original.x, 0.001)
        assert recovered.y == pytest.approx(original.y, 0.001)
        assert recovered.z == pytest.approx(original.z, 0.001)
    
    def test_mock_calibration(self):
        """Test mock calibration creation"""
        calib = create_mock_calibration(CalibrationType.EYE_TO_HAND)
        
        assert calib.camera_to_base_transform is not None
        assert calib.calibration_error == pytest.approx(0.002)
    
    def test_point_transformation(self):
        """Test point transformation from camera to base"""
        calib = create_mock_calibration()
        
        point_camera = np.array([0.0, 0.0, 0.5])
        point_base = calib.transform_point_camera_to_base(point_camera)
        
        assert len(point_base) == 3
        assert isinstance(point_base[0], (int, float))


# ============================================================================
# Test Visual Servoing
# ============================================================================

class TestVisualServoing:
    """Test visual servoing control"""
    
    def test_servo_controller_creation(self):
        """Test servo controller initialization"""
        controller = create_servo_controller()
        
        assert controller.config.mode == ServoMode.POSITION_BASED
        assert controller.config.position_gain > 0
        assert controller.config.max_velocity > 0
    
    def test_pose_error_computation(self):
        """Test pose error calculation"""
        controller = create_servo_controller()
        
        current = Pose(0.3, 0.0, 0.2, 0.0, 0.0, 0.0)
        target = Pose(0.4, 0.1, 0.3, 0.0, 0.0, 0.5)
        
        pos_error, ori_error = controller._compute_pose_error(current, target)
        
        assert pos_error > 0
        assert ori_error > 0
        assert pos_error == pytest.approx(0.173, 0.01)  # sqrt(0.1^2 + 0.1^2 + 0.1^2)
    
    def test_velocity_command_generation(self):
        """Test velocity command generation"""
        controller = create_servo_controller()
        
        current = Pose(0.3, 0.0, 0.2, 0.0, 0.0, 0.0)
        target = Pose(0.4, 0.0, 0.2, 0.0, 0.0, 0.0)
        
        pos_error, ori_error = controller._compute_pose_error(current, target)
        velocity = controller._compute_pbvs_velocity(current, target, pos_error, ori_error)
        
        assert len(velocity) == 6  # [vx, vy, vz, wx, wy, wz]
        assert velocity[0] > 0  # Moving in +x direction
        assert np.linalg.norm(velocity[:3]) <= controller.config.max_velocity


# ============================================================================
# Test Spatial Memory
# ============================================================================

class TestSpatialMemory:
    """Test spatial object location memory"""
    
    def test_spatial_memory_creation(self):
        """Test spatial memory initialization"""
        memory = create_spatial_memory(storage_path=None)
        
        assert len(memory.objects) == 0
        assert memory.total_observations == 0
    
    def test_add_observation(self):
        """Test adding object observation"""
        memory = create_spatial_memory(storage_path=None)
        
        detection = DetectedObject(
            object_id="obj_1",
            class_name="cup",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.3, 0.1, 0.5, 0.8, "world"),
            timestamp=time.time()
        )
        
        memory.add_observation(detection, semantic_id="cup_001")
        
        assert len(memory.objects) == 1
        assert memory.total_observations == 1
        assert "obj_1" in memory.objects
    
    def test_query_by_class(self):
        """Test querying objects by class"""
        memory = create_spatial_memory(storage_path=None)
        
        # Add multiple objects
        for i in range(3):
            detection = DetectedObject(
                object_id=f"obj_{i}",
                class_name="cup" if i < 2 else "bottle",
                bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
                position_3d=Position3D(0.3 + i*0.1, 0.1, 0.5, 0.8, "world"),
                timestamp=time.time()
            )
            memory.add_observation(detection)
        
        # Query for cups
        query = SpatialQuery(class_name="cup")
        results = memory.query(query)
        
        assert len(results) == 2
        assert all(obj.class_name == "cup" for obj in results)
    
    def test_object_location_retrieval(self):
        """Test getting object location"""
        memory = create_spatial_memory(storage_path=None)
        
        detection = DetectedObject(
            object_id="obj_1",
            class_name="screwdriver",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.5, -0.2, 0.3, 0.9, "world"),
            timestamp=time.time()
        )
        
        memory.add_observation(detection)
        
        location = memory.get_object_location(class_name="screwdriver")
        
        assert location is not None
        assert location.x == pytest.approx(0.5, 0.01)
        assert location.y == pytest.approx(-0.2, 0.01)


# ============================================================================
# Test Sensory Fusion
# ============================================================================

class TestSensoryFusion:
    """Test multi-modal sensory fusion"""
    
    def test_fusion_engine_creation(self):
        """Test fusion engine initialization"""
        engine = create_fusion_engine()
        
        assert engine.object_detector is not None
        assert engine.spatial_memory is not None
        assert len(engine.current_percepts) == 0
    
    def test_environmental_context(self):
        """Test environmental context extraction"""
        engine = create_fusion_engine()
        
        context = engine.get_environmental_context()
        
        assert "num_objects" in context
        assert "object_classes" in context
        assert context["num_objects"] == 0
    
    def test_attention_focus(self):
        """Test attention mechanism"""
        engine = create_fusion_engine()
        
        engine.set_attention_focus("obj_123", reason="query")
        
        assert engine.attention.focus_object_id == "obj_123"
        assert engine.attention.focus_reason == "query"


# ============================================================================
# Test Grasp Planning
# ============================================================================

class TestGraspPlanning:
    """Test grasp pose generation"""
    
    def test_grasp_planner_creation(self):
        """Test grasp planner initialization"""
        planner = create_grasp_planner()
        
        assert planner.gripper_max_width == 0.08
        assert planner.min_grasp_quality > 0
    
    def test_grasp_generation(self):
        """Test grasp candidate generation"""
        planner = create_grasp_planner()
        
        detection = DetectedObject(
            object_id="obj_1",
            class_name="cup",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.3, 0.0, 0.1, 0.9, "world"),
            timestamp=time.time()
        )
        
        grasps = planner.plan_grasps(detection, num_candidates=5)
        
        assert len(grasps) <= 5
        
        if grasps:
            best_grasp = grasps[0]
            assert best_grasp.quality_score >= planner.min_grasp_quality
            assert best_grasp.collision_free
            assert best_grasp.gripper_width <= planner.gripper_max_width
    
    def test_grasp_type_preference(self):
        """Test grasp type preferences by object class"""
        planner = create_grasp_planner()
        
        # Cup should prefer side grasp
        assert planner.class_preferences["cup"] == GraspType.SIDE
        
        # Box should prefer top-down
        assert planner.class_preferences["box"] == GraspType.TOP_DOWN
    
    def test_grasp_quality_evaluation(self):
        """Test grasp quality scoring"""
        planner = create_grasp_planner()
        
        detection = DetectedObject(
            object_id="obj_1",
            class_name="bottle",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.3, 0.0, 0.1, 0.9, "world"),
            timestamp=time.time()
        )
        
        grasps = planner.plan_grasps(detection, num_candidates=3)
        
        if len(grasps) >= 2:
            # Grasps should be sorted by quality
            assert grasps[0].quality_score >= grasps[1].quality_score


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test integrated multi-modal perception"""
    
    def test_full_perception_pipeline(self):
        """Test complete perception: detect → spatial → fusion"""
        # Create components
        detector = create_mock_detector()
        spatial_memory = create_spatial_memory(storage_path=None)
        fusion_engine = SensoryFusionEngine(detector, spatial_memory)
        
        # Process frame (mock)
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.ones((480, 640)) * 1.0
        
        percepts = fusion_engine.process_frame(image, depth)
        
        # Should complete without error
        assert isinstance(percepts, list)
        
        # Get context
        context = fusion_engine.get_environmental_context()
        assert "num_objects" in context
    
    def test_cross_modal_query(self):
        """Test cross-modal object location query"""
        fusion_engine = create_fusion_engine()
        
        # Add observation to spatial memory
        detection = DetectedObject(
            object_id="obj_1",
            class_name="wrench",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.4, 0.2, 0.1, 0.85, "world"),
            timestamp=time.time()
        )
        
        fusion_engine.spatial_memory.add_observation(detection)
        
        # Query: "Where is the wrench?"
        location = fusion_engine.query_object_location(class_name="wrench")
        
        assert location is not None
        assert location.x == pytest.approx(0.4, 0.05)
    
    def test_visual_servoing_with_grasp(self):
        """Test integrated visual servoing and grasp planning"""
        # Create components
        servo_controller = create_servo_controller()
        grasp_planner = create_grasp_planner()
        
        # Mock detection
        detection = DetectedObject(
            object_id="obj_1",
            class_name="screwdriver",
            bounding_box=BoundingBox(100, 100, 200, 200, 0.9),
            position_3d=Position3D(0.35, 0.0, 0.15, 0.9, "world"),
            timestamp=time.time()
        )
        
        # Plan grasp
        grasps = grasp_planner.plan_grasps(detection, num_candidates=3)
        
        assert len(grasps) > 0
        
        # Visualize best grasp
        if grasps:
            viz = grasp_planner.visualize_grasp(grasps[0])
            assert "position" in viz
            assert "quality" in viz
            assert viz["quality"] > 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance of sensory fusion system"""
    
    def test_detection_speed(self):
        """Test detection performance"""
        detector = create_mock_detector()
        
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.ones((480, 640)) * 1.0
        
        start = time.time()
        for _ in range(10):
            detector.detect(image, depth)
        elapsed = time.time() - start
        
        avg_time = elapsed / 10
        assert avg_time < 0.1  # Should be fast for mock
    
    def test_fusion_speed(self):
        """Test fusion performance"""
        engine = create_fusion_engine()
        
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        depth = np.ones((480, 640)) * 1.0
        
        start = time.time()
        for _ in range(10):
            engine.process_frame(image, depth)
        elapsed = time.time() - start
        
        avg_time = elapsed / 10
        assert avg_time < 0.5  # Should process reasonably fast


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
