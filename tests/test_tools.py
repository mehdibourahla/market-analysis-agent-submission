import pytest
from unittest.mock import Mock, patch
from src.tools import WebScraperTool, SentimentAnalyzerTool, MarketTrendAnalyzerTool, ReportGeneratorTool

class TestWebScraperTool:
    @pytest.fixture
    def web_scraper(self):
        return WebScraperTool()

    def test_tool_initialization(self, web_scraper):
        assert web_scraper.name == "web_scraper"
        assert "google_search" in web_scraper.description
        assert web_scraper.args_schema is not None

    def test_run_success_with_api(self, web_scraper):
        mock_response = Mock()
        mock_response.text = '''[{"title": "Test Product", "price": "$100"}]'''
        mock_response.candidates = []  # Empty candidates to avoid attribute errors

        with patch('src.tools.web_scraper.settings') as mock_settings, \
             patch('google.genai.Client') as mock_client_class:
            mock_settings.google_api_key = "test-key"
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.models.generate_content.return_value = mock_response

            result = web_scraper._run("Test Product")
            assert result["status"] == "success"
            assert len(result["products"]) > 0

    def test_run_without_api_key(self, web_scraper):
        with patch('src.tools.web_scraper.settings') as mock_settings:
            mock_settings.google_api_key = None
            result = web_scraper._run("Test Product")
            assert result["status"] == "error"
class TestSentimentAnalyzerTool:
    @pytest.fixture
    def sentiment_analyzer(self):
        return SentimentAnalyzerTool()

    def test_tool_initialization(self, sentiment_analyzer):
        assert sentiment_analyzer.name == "sentiment_analyzer"
        assert "sentiment analysis" in sentiment_analyzer.description

    def test_run_success(self, sentiment_analyzer):
        result = sentiment_analyzer._run("Test Product")
        assert result["status"] == "success"
        assert "analysis" in result
        assert "total_reviews" in result["analysis"]
        assert "average_rating" in result["analysis"]
class TestMarketTrendAnalyzerTool:
    @pytest.fixture
    def market_analyzer(self):
        return MarketTrendAnalyzerTool()

    def test_tool_initialization(self, market_analyzer):
        assert market_analyzer.name == "market_trend_analyzer"
        assert "market trends" in market_analyzer.description

    def test_run_success(self, market_analyzer):
        result = market_analyzer._run("Test Product")
        assert result["status"] == "success"
        assert "price_trends" in result
        assert "demand_analysis" in result
        assert "competitor_landscape" in result
class TestReportGeneratorTool:
    @pytest.fixture
    def report_generator(self):
        return ReportGeneratorTool()

    @pytest.fixture
    def sample_analysis_data(self):
        return {
            "product_analysis": {
                "status": "success",
                "products": [{"title": "Test Product", "price": "$100"}],
                "count": 1
            },
            "sentiment_analysis": {
                "status": "success",
                "analysis": {"average_rating": 4.5}
            },
            "market_trends": {
                "status": "success",
                "price_trends": {"price_change_percent": 5.2}
            }
        }

    def test_tool_initialization(self, report_generator):
        assert report_generator.name == "report_generator"
        assert "comprehensive" in report_generator.description

    def test_run_success(self, report_generator, sample_analysis_data):
        result = report_generator._run(sample_analysis_data)
        assert result["status"] == "success"
        assert "report" in result
        assert "executive_summary" in result["report"]
        assert "detailed_analysis" in result["report"]