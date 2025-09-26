import pytest
from unittest.mock import Mock, patch
from src.tools import WebScraperTool, SentimentAnalyzerTool, ReportGeneratorTool

class TestErrorHandling:
    def test_web_scraper_missing_api_key(self):
        tool = WebScraperTool()
        with patch('src.tools.web_scraper.settings') as mock_settings:
            mock_settings.google_api_key = None
            result = tool._run("Test Product")
            assert result["status"] == "error"
            assert "Google API key not configured" in result["error"]

    def test_web_scraper_invalid_input(self):
        tool = WebScraperTool()
        result = tool._run("")
        assert result["status"] == "error"
        assert "Product name is required" in result["error"]

    def test_web_scraper_api_failure(self):
        tool = WebScraperTool()
        with patch('src.tools.web_scraper.settings') as mock_settings, \
             patch('google.genai.Client') as mock_client_class:
            mock_settings.google_api_key = "test-key"
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.models.generate_content.side_effect = Exception("API Error")

            result = tool._run("Test Product")
            assert result["status"] == "error"

    def test_sentiment_analyzer_empty_reviews(self):
        tool = SentimentAnalyzerTool()
        result = tool._analyze_sentiment([])
        assert "error" in result
        assert result["error"] == "No reviews to analyze"

    def test_report_generator_empty_data(self):
        tool = ReportGeneratorTool()
        result = tool._run({})
        assert result["status"] == "success"  # Should handle gracefully
        assert "report" in result