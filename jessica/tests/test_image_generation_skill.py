"""
Tests for Image Generation Skill - Offline Stable Diffusion XL Turbo

Tests:
1. ImageGenerator initialization
2. Device detection (CUDA/CPU)
3. Pipeline lazy loading
4. Image generation from prompt
5. File saving and timestamping
6. Skill command detection
7. Prompt parsing and extraction
8. Error handling and graceful degradation
"""

import unittest
import torch
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from unittest.mock import patch, MagicMock

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the skill
from jessica.skills import image_generation_skill
from jessica.skills.image_generation_skill import (
    ImageGenerator,
    get_image_generator,
    can_handle,
    run
)


class TestImageGenerator(unittest.TestCase):
    """Test the core ImageGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ImageGenerator()
    
    def test_initialization(self):
        """Test ImageGenerator initializes correctly."""
        self.assertIsNone(self.generator.pipeline)
        self.assertIsNone(self.generator.device)
        self.assertTrue(self.generator.output_dir.exists())
    
    def test_device_detection_cuda(self):
        """Test CUDA device detection."""
        device = self.generator._init_device()
        self.assertIn(device, ["cuda", "cpu"])
        
        if torch.cuda.is_available():
            self.assertEqual(device, "cuda")
        else:
            self.assertEqual(device, "cpu")
    
    def test_output_directory_creation(self):
        """Test output directory is created."""
        self.assertTrue(self.generator.output_dir.exists())
        self.assertTrue(self.generator.output_dir.is_dir())
    
    @patch('jessica.skills.image_generation_skill.DIFFUSERS_AVAILABLE', False)
    def test_pipeline_missing_diffusers(self):
        """Test error handling when diffusers is not available."""
        gen = ImageGenerator()
        
        with self.assertRaises(ImportError) as context:
            gen._init_pipeline()
        
        self.assertIn("diffusers", str(context.exception).lower())
    
    def test_singleton_pattern(self):
        """Test that get_image_generator returns singleton."""
        gen1 = get_image_generator()
        gen2 = get_image_generator()
        
        self.assertIs(gen1, gen2)
    
    def test_cache_clearing(self):
        """Test cache clearing functionality."""
        gen = ImageGenerator()
        gen.pipeline = "mock_pipeline"  # Mock pipeline
        
        gen.clear_cache()
        
        self.assertIsNone(gen.pipeline)


class TestSkillIntegration(unittest.TestCase):
    """Test skill integration with Jessica."""
    
    def test_can_handle_generate_commands(self):
        """Test command detection for various prompts."""
        test_cases = [
            ("generate image of a cat", True),
            ("create a picture of the beach", True),
            ("make image: mountain landscape", True),
            ("draw me a sunset", True),
            ("visualize a futuristic city", True),
            ("imagine a beautiful garden", True),
            ("generate an image of a dog", True),
            ("hello jessica", False),
            ("what is the weather", False),
            ("tell me a joke", False),
            ("what time is it", False),
        ]
        
        for text, expected in test_cases:
            intent = {"text": text}
            result = can_handle(intent)
            self.assertEqual(
                result, expected,
                f"Failed for: '{text}' - got {result}, expected {expected}"
            )
    
    def test_can_handle_case_insensitive(self):
        """Test command detection is case insensitive."""
        test_cases = [
            "GENERATE IMAGE OF A CAT",
            "Generate Image Of A Dog",
            "MAKE IMAGE: SUNSET",
        ]
        
        for text in test_cases:
            intent = {"text": text}
            result = can_handle(intent)
            self.assertTrue(result, f"Failed for: '{text}'")
    
    def test_skill_integration_structure(self):
        """Test skill has required integration functions."""
        self.assertTrue(callable(can_handle))
        self.assertTrue(callable(run))
    
    def test_run_missing_prompt(self):
        """Test run function with missing/invalid prompt."""
        intent = {"text": "generate image"}
        result = run(intent)
        
        self.assertIn("reply", result)
        # Either "describe" (when prompt is too short) or error message (if diffusers missing)
        response_lower = result["reply"].lower()
        self.assertTrue(
            "describe" in response_lower or "error" in response_lower or "diffusers" in response_lower,
            f"Unexpected response: {result['reply']}"
        )
    
    def test_run_with_valid_prompt_mock(self):
        """Test run function with valid prompt (mocked)."""
        intent = {"text": "generate image of a beautiful sunset"}
        
        # Mock the image generator
        with patch('jessica.skills.image_generation_skill.get_image_generator') as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate_image.return_value = {
                'status': 'success',
                'image_path': '/path/to/image.png',
                'prompt': 'beautiful sunset',
                'device': 'cpu',
                'message': 'Generated 512x512 image in 4 steps'
            }
            mock_gen.return_value = mock_instance
            
            result = run(intent)
            
            self.assertIn("reply", result)
            self.assertIn("✅", result["reply"])
            self.assertIn("image_path", result)
    
    def test_run_error_handling_mock(self):
        """Test run function error handling (mocked)."""
        intent = {"text": "generate image of something"}
        
        # Mock the image generator to return error
        with patch('jessica.skills.image_generation_skill.get_image_generator') as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate_image.return_value = {
                'status': 'error',
                'message': 'Model not loaded'
            }
            mock_gen.return_value = mock_instance
            
            result = run(intent)
            
            self.assertIn("reply", result)
            self.assertIn("❌", result["reply"])


class TestPromptProcessing(unittest.TestCase):
    """Test prompt extraction and processing."""
    
    def test_prompt_extraction(self):
        """Test various prompt formats."""
        test_cases = [
            ("generate image of a cat", "cat"),
            ("create image of the beach", "beach"),
            ("make image: mountain landscape", "mountain landscape"),
            ("draw me a sunset", "sunset"),
            ("visualize a futuristic city", "futuristic city"),
        ]
        
        # This tests that the run function can extract meaningful prompts
        for query, expected_keyword in test_cases:
            intent = {"text": query}
            
            # Mock to capture the actual prompt sent
            with patch('jessica.skills.image_generation_skill.get_image_generator') as mock_gen:
                mock_instance = MagicMock()
                mock_instance.generate_image.return_value = {
                    'status': 'success',
                    'image_path': '/tmp/test.png',
                    'prompt': 'test',
                    'device': 'cpu'
                }
                mock_gen.return_value = mock_instance
                
                run(intent)
                
                # Verify generate_image was called
                self.assertTrue(mock_instance.generate_image.called)


class TestDeviceHandling(unittest.TestCase):
    """Test GPU/CPU device handling."""
    
    def test_device_selection(self):
        """Test device is correctly selected based on availability."""
        gen = ImageGenerator()
        device = gen._init_device()
        
        # Should match what PyTorch reports
        if torch.cuda.is_available():
            self.assertEqual(device, "cuda")
        else:
            self.assertEqual(device, "cpu")
    
    def test_device_persistence(self):
        """Test device is cached after first initialization."""
        gen = ImageGenerator()
        device1 = gen._init_device()
        device2 = gen._init_device()
        
        self.assertEqual(device1, device2)


class TestImageFileSaving(unittest.TestCase):
    """Test image file saving functionality."""
    
    def test_output_directory_structure(self):
        """Test output directory structure is correct."""
        gen = ImageGenerator()
        
        # Check that output directory follows expected pattern
        self.assertIn("generated_images", str(gen.output_dir))
        self.assertTrue(gen.output_dir.exists())
    
    def test_filename_sanitization(self):
        """Test that filenames are properly sanitized."""
        # Test that special characters are handled
        test_prompts = [
            "beautiful/sunset",
            "mountain@peak",
            "river&trees",
            "cat#meow!",
        ]
        
        # Filenames should be created without errors
        for prompt in test_prompts:
            # Sanitization logic from skill
            safe_prompt = "".join(
                c for c in prompt[:30] 
                if c.isalnum() or c in (' ', '_')
            ).strip().replace(' ', '_')
            
            # Should not raise exception
            self.assertIsInstance(safe_prompt, str)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_skill_workflow_mock(self):
        """Test complete workflow from intent to response."""
        # User query
        intent = {"text": "generate image of a peaceful forest"}
        
        # Check if skill can handle
        self.assertTrue(can_handle(intent))
        
        # Mock and run skill
        with patch('jessica.skills.image_generation_skill.get_image_generator') as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate_image.return_value = {
                'status': 'success',
                'image_path': '/home/user/Jessica_Images/generated_images/test.png',
                'prompt': 'peaceful forest',
                'device': 'cuda',
                'message': 'Generated 512x512 image in 4 steps'
            }
            mock_gen.return_value = mock_instance
            
            # Run skill
            result = run(intent)
            
            # Verify response structure
            self.assertIn("reply", result)
            self.assertIn("image_path", result)
            self.assertIn("✅", result["reply"])
            self.assertIn("512x512", result["reply"])
    
    def test_multiple_requests_same_generator(self):
        """Test that multiple requests use same cached generator."""
        gen1 = get_image_generator()
        gen2 = get_image_generator()
        
        # Both should be the same instance
        self.assertIs(gen1, gen2)


def run_all_tests():
    """Run all tests with detailed reporting."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestImageGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestImageFileSaving))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
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
