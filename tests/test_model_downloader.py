"""
Unit tests for ModelDownloader.
"""

import pytest
from jessica.skills.model_downloader import ModelDownloader


class TestModelDownloader:
    """Test ModelDownloader functionality."""

    def test_search_models(self):
        """Test model search by task."""
        dl = ModelDownloader()
        result = dl.search_models("image-generation", source="huggingface", limit=3)
        assert result.get("ok") is True
        assert result.get("task") == "image-generation"
        assert len(result.get("models", [])) > 0

    def test_search_invalid_task(self):
        """Test search with invalid task."""
        dl = ModelDownloader()
        result = dl.search_models("invalid-task-xyz", source="huggingface")
        assert result.get("ok") is False

    def test_suggest_model_for_task(self):
        """Test task-based model suggestions."""
        dl = ModelDownloader()
        
        test_cases = [
            ("generate images", "runwayml/stable-diffusion-v1-5"),
            ("analyze sentiment", "distilbert-base-uncased-finetuned-sst-2-english"),
            ("summarize articles", "facebook/bart-large-cnn"),
        ]
        
        for task, expected_model in test_cases:
            result = dl.suggest_model_for_task(task)
            assert result.get("ok") is True
            rec = result.get("recommended", {})
            assert rec.get("model") == expected_model

    def test_model_sources(self):
        """Test that MODEL_SOURCES are populated."""
        dl = ModelDownloader()
        assert len(dl.MODEL_SOURCES) >= 3
        assert "huggingface" in dl.MODEL_SOURCES
        assert "pytorch-hub" in dl.MODEL_SOURCES

    def test_get_download_status(self):
        """Test checking model download status."""
        dl = ModelDownloader()
        status = dl.get_download_status("gpt2")
        assert status.get("ok") is True
        assert status.get("model_id") == "gpt2"
        assert isinstance(status.get("cached"), bool)

    def test_model_info_hf(self):
        """Test getting HuggingFace model info."""
        dl = ModelDownloader()
        info = dl.model_info("gpt2", source="huggingface")
        assert info.get("ok") is True
        assert info.get("model_id") == "gpt2"
