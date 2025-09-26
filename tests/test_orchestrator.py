import pytest
from unittest.mock import patch
from src.agents import MarketAnalysisOrchestrator

class TestMarketAnalysisOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return MarketAnalysisOrchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        assert orchestrator.tools is not None
        assert len(orchestrator.tools) == 4
        assert "web_scraper" in orchestrator.tools
        assert "sentiment_analyzer" in orchestrator.tools
        assert "market_trend" in orchestrator.tools
        assert "report_generator" in orchestrator.tools

    def test_run_complete_workflow(self, orchestrator):
        # Mock all tools to return success
        with patch.object(orchestrator.tools["web_scraper"], "_run") as mock_web, \
             patch.object(orchestrator.tools["sentiment_analyzer"], "_run") as mock_sentiment, \
             patch.object(orchestrator.tools["market_trend"], "_run") as mock_market, \
             patch.object(orchestrator.tools["report_generator"], "_run") as mock_report:

            mock_web.return_value = {"status": "success", "products": [], "count": 0}
            mock_sentiment.return_value = {"status": "success", "analysis": {}}
            mock_market.return_value = {"status": "success", "price_trends": {}}
            mock_report.return_value = {"status": "success", "report": {}}

            result = orchestrator.run("analyze Test Product")

            assert result["status"] == "success"
            assert "report" in result

            # Verify all tools were called
            mock_web.assert_called_once()
            mock_sentiment.assert_called_once()
            mock_market.assert_called_once()
            mock_report.assert_called_once()

    def test_run_with_tool_failure(self, orchestrator):
        # Test orchestrator handles tool failures
        with patch.object(orchestrator.tools["web_scraper"], "_run") as mock_web:
            mock_web.side_effect = Exception("Tool failed")

            result = orchestrator.run("analyze Test Product")
            assert result["status"] == "error"