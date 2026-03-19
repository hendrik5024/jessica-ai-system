"""
Tests for Model Orchestrator - Multi-Model Routing & VRAM Management

Tests:
1. VRAMManager initialization and registration
2. VRAM usage tracking
3. Model loading/unloading
4. LRU eviction when VRAM full
5. Idle model cleanup
6. Intent classification
7. Model routing (Simple/Technical/Visual)
8. Cleanup thread management
9. Thread safety
10. Integration workflow
"""

import unittest
import time
import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

# Import orchestrator components
from jessica.llama_cpp_engine.model_orchestrator import (
    ModelOrchestrator,
    VRAMManager,
    ModelConfig,
    ModelState,
    ModelType,
    IntentCategory,
    get_orchestrator
)


class TestVRAMManager(unittest.TestCase):
    """Test VRAM Manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vram_manager = VRAMManager(max_vram_mb=8192)
    
    def tearDown(self):
        """Clean up after tests."""
        if self.vram_manager.running:
            self.vram_manager.stop_cleanup_thread()
    
    def test_initialization(self):
        """Test VRAM manager initializes correctly."""
        self.assertEqual(self.vram_manager.max_vram_mb, 8192)
        self.assertEqual(len(self.vram_manager.models), 0)
        self.assertFalse(self.vram_manager.running)
    
    def test_register_model(self):
        """Test model registration."""
        config = ModelConfig(
            name="Test Model",
            model_type=ModelType.GENERAL,
            vram_mb=2048
        )
        
        self.vram_manager.register_model(config)
        
        self.assertIn(ModelType.GENERAL, self.vram_manager.models)
        state = self.vram_manager.models[ModelType.GENERAL]
        self.assertEqual(state.config.name, "Test Model")
        self.assertFalse(state.is_loaded)
    
    def test_vram_usage_tracking(self):
        """Test VRAM usage tracking."""
        # Register models
        self.vram_manager.register_model(ModelConfig(
            name="Model1", model_type=ModelType.GENERAL, vram_mb=2048
        ))
        self.vram_manager.register_model(ModelConfig(
            name="Model2", model_type=ModelType.TECHNICAL, vram_mb=4096
        ))
        
        # Initially no usage
        self.assertEqual(self.vram_manager.get_vram_usage(), 0)
        self.assertEqual(self.vram_manager.get_available_vram(), 8192)
        
        # Mark first model as loaded
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_model_1")
        self.assertEqual(self.vram_manager.get_vram_usage(), 2048)
        self.assertEqual(self.vram_manager.get_available_vram(), 6144)
        
        # Mark second model as loaded
        self.vram_manager.mark_loaded(ModelType.TECHNICAL, "mock_model_2")
        self.assertEqual(self.vram_manager.get_vram_usage(), 6144)
        self.assertEqual(self.vram_manager.get_available_vram(), 2048)
    
    def test_can_load_model(self):
        """Test model loading constraint checking."""
        self.vram_manager.register_model(ModelConfig(
            name="SmallModel", model_type=ModelType.GENERAL, vram_mb=2048
        ))
        self.vram_manager.register_model(ModelConfig(
            name="LargeModel", model_type=ModelType.TECHNICAL, vram_mb=9000
        ))
        
        # Small model should fit
        self.assertTrue(self.vram_manager.can_load_model(ModelType.GENERAL))
        
        # Large model exceeds limit
        self.assertFalse(self.vram_manager.can_load_model(ModelType.TECHNICAL))
    
    def test_make_room_for_model(self):
        """Test LRU eviction to make room for new model."""
        # Register models
        self.vram_manager.register_model(ModelConfig(
            name="Model1", model_type=ModelType.ROUTER, vram_mb=500, always_loaded=True
        ))
        self.vram_manager.register_model(ModelConfig(
            name="Model2", model_type=ModelType.GENERAL, vram_mb=2048
        ))
        self.vram_manager.register_model(ModelConfig(
            name="Model3", model_type=ModelType.TECHNICAL, vram_mb=4096
        ))
        self.vram_manager.register_model(ModelConfig(
            name="Model4", model_type=ModelType.VISUAL, vram_mb=4500
        ))
        
        # Load router and general model
        self.vram_manager.mark_loaded(ModelType.ROUTER, "mock_router")
        time.sleep(0.01)
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_general")
        time.sleep(0.01)
        self.vram_manager.mark_loaded(ModelType.TECHNICAL, "mock_technical")
        
        # Now at: 500 + 2048 + 4096 = 6644 MB used
        # Available: 8192 - 6644 = 1548 MB
        
        # Try to load visual model (4500 MB) - should make room
        can_fit = self.vram_manager.make_room_for(ModelType.VISUAL)
        
        self.assertTrue(can_fit)
        # Should have unloaded GENERAL (oldest non-always_loaded)
        self.assertFalse(self.vram_manager.models[ModelType.GENERAL].is_loaded)
    
    def test_idle_model_cleanup(self):
        """Test cleanup of idle models."""
        # Register model with short timeout
        self.vram_manager.register_model(ModelConfig(
            name="TestModel",
            model_type=ModelType.GENERAL,
            vram_mb=2048,
            idle_timeout=1  # 1 second
        ))
        
        # Load model
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_model")
        self.assertTrue(self.vram_manager.models[ModelType.GENERAL].is_loaded)
        
        # Wait for timeout
        time.sleep(1.5)
        
        # Run cleanup
        self.vram_manager.cleanup_idle_models()
        
        # Should be unloaded
        self.assertFalse(self.vram_manager.models[ModelType.GENERAL].is_loaded)
    
    def test_always_loaded_not_evicted(self):
        """Test that always_loaded models are never unloaded."""
        # Register always_loaded model
        self.vram_manager.register_model(ModelConfig(
            name="Router",
            model_type=ModelType.ROUTER,
            vram_mb=500,
            always_loaded=True,
            idle_timeout=1
        ))
        
        # Load model
        self.vram_manager.mark_loaded(ModelType.ROUTER, "mock_router")
        
        # Wait beyond timeout
        time.sleep(1.5)
        
        # Run cleanup
        self.vram_manager.cleanup_idle_models()
        
        # Should still be loaded
        self.assertTrue(self.vram_manager.models[ModelType.ROUTER].is_loaded)
    
    def test_unload_model(self):
        """Test manual model unloading."""
        self.vram_manager.register_model(ModelConfig(
            name="TestModel", model_type=ModelType.GENERAL, vram_mb=2048
        ))
        
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_model")
        self.assertTrue(self.vram_manager.models[ModelType.GENERAL].is_loaded)
        
        self.vram_manager.unload_model(ModelType.GENERAL)
        self.assertFalse(self.vram_manager.models[ModelType.GENERAL].is_loaded)
    
    def test_cleanup_thread(self):
        """Test automatic cleanup thread."""
        # Register model with short timeout
        self.vram_manager.register_model(ModelConfig(
            name="TestModel",
            model_type=ModelType.GENERAL,
            vram_mb=2048,
            idle_timeout=1
        ))
        
        # Load model
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_model")
        
        # Start cleanup thread with short interval
        self.vram_manager.start_cleanup_thread(interval_seconds=1)
        self.assertTrue(self.vram_manager.running)
        
        # Wait for cleanup to run
        time.sleep(2.5)
        
        # Should be unloaded by thread
        self.assertFalse(self.vram_manager.models[ModelType.GENERAL].is_loaded)
        
        # Stop thread
        self.vram_manager.stop_cleanup_thread()
        self.assertFalse(self.vram_manager.running)
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        self.vram_manager.register_model(ModelConfig(
            name="TestModel", model_type=ModelType.GENERAL, vram_mb=2048
        ))
        
        self.vram_manager.mark_loaded(ModelType.GENERAL, "mock_model")
        
        stats = self.vram_manager.get_stats()
        
        self.assertEqual(stats['total_vram_mb'], 8192)
        self.assertEqual(stats['used_vram_mb'], 2048)
        self.assertEqual(stats['available_vram_mb'], 6144)
        self.assertEqual(len(stats['loaded_models']), 1)
        self.assertEqual(stats['loaded_models'][0]['name'], "TestModel")


class TestModelOrchestrator(unittest.TestCase):
    """Test Model Orchestrator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = TemporaryDirectory()
        self.models_dir = Path(self.temp_dir.name)
        
        # Create mock model files
        (self.models_dir / "phi-3.5-mini-instruct-q4_k_m.gguf").touch()
        (self.models_dir / "mistral-7b-instruct-v0.2.Q5_K_M.gguf").touch()
        (self.models_dir / "codellama-13b-instruct.Q5_K_M.gguf").touch()
        (self.models_dir / "sdxl-turbo").mkdir()
        
        self.orchestrator = ModelOrchestrator(
            models_dir=self.models_dir,
            max_vram_mb=8192
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.orchestrator.shutdown()
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test orchestrator initializes correctly."""
        self.assertEqual(len(self.orchestrator.vram_manager.models), 4)
        self.assertTrue(self.orchestrator.vram_manager.running)
    
    def test_intent_classification_visual(self):
        """Test intent classification for visual queries."""
        queries = [
            "Generate an image of a sunset",
            "Create a picture of a cat",
            "Draw me a mountain landscape",
            "Visualize a futuristic city"
        ]
        
        for query in queries:
            intent = self.orchestrator.classify_intent(query)
            self.assertEqual(intent, IntentCategory.VISUAL, f"Failed for: {query}")
    
    def test_intent_classification_coding(self):
        """Test intent classification for coding queries."""
        queries = [
            "Write a Python function to sort a list",
            "Debug this code",
            "How do I implement a binary search?",
            "Generate a JavaScript function"
        ]
        
        for query in queries:
            intent = self.orchestrator.classify_intent(query)
            self.assertEqual(intent, IntentCategory.CODING, f"Failed for: {query}")
    
    def test_intent_classification_robotics(self):
        """Test intent classification for robotics queries."""
        queries = [
            "Move the robot arm to position X",
            "Calculate inverse kinematics",
            "Control the joint angles",
            "Plan a motion path"
        ]
        
        for query in queries:
            intent = self.orchestrator.classify_intent(query)
            self.assertEqual(intent, IntentCategory.ROBOTICS, f"Failed for: {query}")
    
    def test_intent_classification_math(self):
        """Test intent classification for math queries."""
        queries = [
            "Calculate 25 * 17",
            "Solve this equation: x^2 + 5x + 6 = 0",
            "What's the derivative of x^3?",
            "Find the integral of sin(x)"
        ]
        
        for query in queries:
            intent = self.orchestrator.classify_intent(query)
            self.assertEqual(intent, IntentCategory.MATH, f"Failed for: {query}")
    
    def test_intent_classification_simple_chat(self):
        """Test intent classification for simple chat."""
        queries = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "How was your day?"
        ]
        
        for query in queries:
            intent = self.orchestrator.classify_intent(query)
            self.assertEqual(intent, IntentCategory.SIMPLE_CHAT, f"Failed for: {query}")
    
    @patch('jessica.llama_cpp_engine.model_orchestrator.ModelOrchestrator._load_model')
    def test_model_loading(self, mock_load):
        """Test model loading mechanism."""
        mock_load.return_value = "mock_model"
        
        # Load router (should work)
        model = self.orchestrator._ensure_model_loaded(ModelType.ROUTER)
        self.assertIsNotNone(model)
        
        # Check it's marked as loaded
        state = self.orchestrator.vram_manager.models[ModelType.ROUTER]
        self.assertTrue(state.is_loaded)
    
    @patch('jessica.llama_cpp_engine.model_orchestrator.ModelOrchestrator._load_model')
    def test_vram_constraint_enforcement(self, mock_load):
        """Test that VRAM constraints are enforced."""
        mock_load.return_value = "mock_model"
        
        # Load router (500MB)
        self.orchestrator._ensure_model_loaded(ModelType.ROUTER)
        
        # Load general (2048MB)
        self.orchestrator._ensure_model_loaded(ModelType.GENERAL)
        
        # Load technical (4096MB) - total now 6644MB
        self.orchestrator._ensure_model_loaded(ModelType.TECHNICAL)
        
        # At this point: 500 + 2048 + 4096 = 6644 MB used
        # Available: 8192 - 6644 = 1548 MB
        
        # Try to load visual (4500MB) - should trigger eviction
        model = self.orchestrator._ensure_model_loaded(ModelType.VISUAL)
        self.assertIsNotNone(model)
        
        # General model should have been unloaded (LRU)
        general_state = self.orchestrator.vram_manager.models[ModelType.GENERAL]
        self.assertFalse(general_state.is_loaded)
    
    @patch('jessica.skills.image_generation_skill.can_handle')
    @patch('jessica.skills.image_generation_skill.run')
    def test_visual_query_handling(self, mock_run, mock_can_handle):
        """Test handling of visual queries."""
        mock_can_handle.return_value = True
        mock_run.return_value = {'reply': 'Generated image at /path/to/image.png'}
        
        result = self.orchestrator.process_query("Generate an image of a sunset")
        
        self.assertEqual(result['intent'], 'visual')
        self.assertEqual(result['model_used'], ModelType.VISUAL.value)
        self.assertIn('response', result)
        self.assertIn('vram_stats', result)
    
    @patch('jessica.llama_cpp_engine.model_orchestrator.ModelOrchestrator._ensure_model_loaded')
    def test_technical_query_handling(self, mock_ensure):
        """Test handling of technical queries."""
        mock_model = MagicMock()
        mock_model.return_value = {
            'choices': [{'text': 'def sort_list(lst): return sorted(lst)'}]
        }
        mock_ensure.return_value = mock_model
        
        result = self.orchestrator.process_query("Write a Python function to sort a list")
        
        self.assertIn(result['intent'], ['coding', 'robotics', 'math'])
        self.assertEqual(result['model_used'], ModelType.TECHNICAL.value)
        self.assertIn('response', result)
    
    @patch('jessica.llama_cpp_engine.model_orchestrator.ModelOrchestrator._ensure_model_loaded')
    def test_general_query_handling(self, mock_ensure):
        """Test handling of general queries."""
        mock_model = MagicMock()
        mock_model.return_value = {
            'choices': [{'text': "Hello! I'm doing well, thank you for asking."}]
        }
        mock_ensure.return_value = mock_model
        
        result = self.orchestrator.process_query("Hello, how are you?")
        
        self.assertEqual(result['intent'], 'simple_chat')
        self.assertEqual(result['model_used'], ModelType.GENERAL.value)
        self.assertIn('response', result)
    
    def test_get_status(self):
        """Test status retrieval."""
        status = self.orchestrator.get_status()
        
        self.assertEqual(status['orchestrator'], 'active')
        self.assertIn('vram', status)
        self.assertIn('models', status)
        self.assertEqual(len(status['models']), 4)
    
    def test_singleton_pattern(self):
        """Test singleton orchestrator pattern."""
        orch1 = get_orchestrator(self.models_dir)
        orch2 = get_orchestrator(self.models_dir)
        
        self.assertIs(orch1, orch2)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of VRAM manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.vram_manager = VRAMManager(max_vram_mb=8192)
        self.vram_manager.register_model(ModelConfig(
            name="TestModel", model_type=ModelType.GENERAL, vram_mb=2048
        ))
    
    def test_concurrent_access(self):
        """Test concurrent model loading/unloading."""
        errors = []
        
        def load_unload():
            try:
                for _ in range(10):
                    self.vram_manager.mark_loaded(ModelType.GENERAL, "mock")
                    time.sleep(0.01)
                    self.vram_manager.unload_model(ModelType.GENERAL)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=load_unload) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")


def run_all_tests():
    """Run all orchestrator tests with detailed reporting."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVRAMManager))
    suite.addTests(loader.loadTestsFromTestCase(TestModelOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadSafety))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
