"""Extended tests for ModelDownloader to improve coverage."""
import pytest
from jessica.skills.model_downloader import ModelDownloader


class TestModelDownloaderExtended:
    """Extended coverage for ModelDownloader detailed functions."""

    def test_model_search_with_variations(self):
        """Test searching with various task names."""
        dl = ModelDownloader()
        tasks = ["image generation", "text summarization", "translation"]
        for task in tasks:
            result = dl.search_models(task)
            # Should return something with structure
            assert isinstance(result, dict)

    def test_suggest_model_edge_cases(self):
        """Test model suggestion with edge case inputs."""
        dl = ModelDownloader()
        # Empty string
        result = dl.suggest_model_for_task("")
        assert isinstance(result, dict)
        # Single word
        result = dl.suggest_model_for_task("summarize")
        assert isinstance(result, dict)

    def test_get_model_download_status(self):
        """Test getting model download status."""
        dl = ModelDownloader()
        # Test a known tiny model
        result = dl.get_download_status("sshleifer/tiny-distilbert-base-cased")
        assert isinstance(result, dict)

    def test_model_sources_accessible(self):
        """Test that model sources are properly defined."""
        dl = ModelDownloader()
        assert hasattr(dl, "MODEL_SOURCES")
        assert len(dl.MODEL_SOURCES) > 0

