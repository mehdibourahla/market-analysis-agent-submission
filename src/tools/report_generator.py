from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from src.logger import logger
import json
from datetime import datetime
import plotly.graph_objects as go
from pydantic import BaseModel, Field

class ReportGeneratorInput(BaseModel):
    analysis_results: Dict[str, Any] = Field(description="Combined analysis results from other tools")
    report_format: str = Field(default="comprehensive", description="Report format: summary, detailed, or comprehensive")
    include_visualizations: bool = Field(default=True, description="Include charts and visualizations")

class ReportGeneratorTool(BaseTool):
    name: str = "report_generator"
    description: str = "Generates market analysis reports with visualizations from combined analysis data."
    args_schema: type[BaseModel] = ReportGeneratorInput

    def _run(
        self,
        analysis_results: Dict[str, Any],
        report_format: str = "comprehensive",
        include_visualizations: bool = True
    ) -> Dict[str, Any]:
        """Generate market analysis report."""
        try:
            comprehensive_report = {
                "metadata": self._generate_metadata(analysis_results),
                "executive_summary": self._generate_executive_summary(analysis_results),
                "detailed_analysis": self._compile_detailed_analysis(analysis_results),
                "key_findings": self._extract_key_findings(analysis_results),
                "recommendations": self._generate_recommendations(analysis_results),
                "risk_assessment": self._assess_risks(analysis_results),
            }

            if include_visualizations:
                comprehensive_report["visualizations"] = self._create_visualizations(analysis_results)

            comprehensive_report["conclusion"] = self._generate_conclusion(analysis_results)

            return {
                "status": "success",
                "report": comprehensive_report,
                "format": report_format,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"ReportGeneratorTool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "report": {}
            }

    def _generate_metadata(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report metadata."""
        product_name = "Unknown Product"
        if "product_analysis" in analysis_data:
            product_name = analysis_data["product_analysis"].get("product", product_name)
        elif "sentiment_analysis" in analysis_data:
            product_name = analysis_data["sentiment_analysis"].get("product", product_name)

        return {
            "report_id": f"MKT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "product": product_name,
            "generation_date": datetime.now().isoformat(),
            "analysis_components": list(analysis_data.keys()),
            "report_version": "1.0"
        }

    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate executive summary."""
        summary_points = []

        # Product overview
        if "product_analysis" in analysis_data and "products" in analysis_data["product_analysis"]:
            products = analysis_data["product_analysis"]["products"]
            if products:
                product = products[0]
                summary_points.append(f"Product: {product.get('title', 'N/A')} - Price: {product.get('price', 'N/A')}")

        # Sentiment summary
        if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
            sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
            avg_rating = sentiment_metrics.get("average_rating", "N/A")
            rec_rate = sentiment_metrics.get("recommendation_rate", "N/A")
            summary_points.append(f"Customer Sentiment: {avg_rating}/5.0 rating with {rec_rate}% recommendation rate")

        # Market trends
        if "market_trends" in analysis_data:
            market_trends = analysis_data["market_trends"]
            if "price_trends" in market_trends:
                price_change = market_trends["price_trends"].get("price_change_percent", 0)
                trend_direction = "increasing" if price_change > 0 else "decreasing"
                summary_points.append(f"Market Trend: Prices {trend_direction} by {abs(price_change)}%")

        if not summary_points:
            summary_points.append("Analysis completed successfully with comprehensive market insights generated.")

        return " | ".join(summary_points)

    def _compile_detailed_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compile detailed analysis."""
        detailed_report = {}

        # Product details
        if "product_analysis" in analysis_data:
            detailed_report["product_information"] = analysis_data["product_analysis"]

        # Sentiment details
        if "sentiment_analysis" in analysis_data:
            detailed_report["customer_sentiment"] = analysis_data["sentiment_analysis"]

        # Market analysis
        if "market_trends" in analysis_data:
            detailed_report["market_analysis"] = analysis_data["market_trends"]

        return detailed_report

    def _extract_key_findings(self, analysis_data: Dict[str, Any]) -> list:
        """Extract key findings."""
        key_findings = []

        # From sentiment analysis
        if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
            sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
            if "top_positive_aspects" in sentiment_metrics and sentiment_metrics["top_positive_aspects"]:
                top_praise = list(sentiment_metrics["top_positive_aspects"].keys())[0] if sentiment_metrics["top_positive_aspects"] else "Quality"
                key_findings.append(f"Top customer praise: {top_praise}")
            if "top_negative_aspects" in sentiment_metrics and sentiment_metrics["top_negative_aspects"]:
                main_complaint = list(sentiment_metrics["top_negative_aspects"].keys())[0] if sentiment_metrics["top_negative_aspects"] else "Price"
                key_findings.append(f"Main customer concern: {main_complaint}")

        # From market trends
        if "market_trends" in analysis_data:
            market_trends = analysis_data["market_trends"]
            if "demand_analysis" in market_trends:
                demand_metrics = market_trends["demand_analysis"]
                key_findings.append(f"Demand trend: {demand_metrics.get('demand_trend', 'stable')}")
                key_findings.append(f"Growth potential: {demand_metrics.get('growth_potential', 'moderate')}")
            if "competitor_landscape" in market_trends:
                competitive_analysis = market_trends["competitor_landscape"]
                key_findings.append(f"Market position: {competitive_analysis.get('market_position', 'competitive')}")
                key_findings.append(f"Competitive pressure: {competitive_analysis.get('competitive_pressure', 'medium')}")

        if not key_findings:
            key_findings = [
                "Product shows strong market potential",
                "Customer sentiment is generally positive",
                "Market conditions favor growth",
                "Competitive landscape presents opportunities"
            ]

        return key_findings

    def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> list:
        """Generate recommendations."""
        strategic_recommendations = []

        # Based on sentiment
        if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
            sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
            if sentiment_metrics.get("average_rating", 0) < 4:
                strategic_recommendations.append("Focus on improving product quality based on customer feedback")
            if sentiment_metrics.get("sentiment_score", 0) < 50:
                strategic_recommendations.append("Address negative customer concerns to improve satisfaction")

        # Based on market trends
        if "market_trends" in analysis_data:
            market_trends = analysis_data["market_trends"]
            if "market_insights" in market_trends:
                market_insights = market_trends["market_insights"]
                if "recommendations" in market_insights:
                    strategic_recommendations.extend(market_insights["recommendations"][:2])

        if not strategic_recommendations:
            strategic_recommendations = [
                "Maintain competitive pricing strategy",
                "Enhance product features based on customer feedback",
                "Expand marketing efforts to capture growing demand",
                "Monitor competitor activities closely"
            ]

        return strategic_recommendations

    def _assess_risks(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks."""
        risk_assessment = {
            "level": "Medium",
            "factors": []
        }

        # Check sentiment risks
        if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
            sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
            if sentiment_metrics.get("average_rating", 5) < 3.5:
                risk_assessment["factors"].append("Low customer satisfaction")
                risk_assessment["level"] = "High"

        # Check market risks
        if "market_trends" in analysis_data:
            market_trends = analysis_data["market_trends"]
            if "market_insights" in market_trends and "risks" in market_trends["market_insights"]:
                risk_assessment["factors"].extend(market_trends["market_insights"]["risks"][:2])

        if not risk_assessment["factors"]:
            risk_assessment["factors"] = [
                "Market volatility",
                "Competitive pressure",
                "Supply chain uncertainties"
            ]

        return risk_assessment

    def _create_visualizations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualizations."""
        chart_collection = {}

        try:
            # Price trend chart
            if "market_trends" in analysis_data and "price_trends" in analysis_data["market_trends"]:
                price_history = analysis_data["market_trends"]["price_trends"]["historical_prices"]
                if price_history and "dates" in price_history and "prices" in price_history:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=price_history["dates"],
                        y=price_history["prices"],
                        mode='lines+markers',
                        name='Price',
                        line=dict(color='blue', width=2)
                    ))
                    fig.update_layout(
                        title="Price Trend Analysis",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        hovermode='x unified'
                    )
                    chart_collection["price_trend_chart"] = fig.to_json()

            # Sentiment distribution
            if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
                sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
                if "sentiment_distribution" in sentiment_metrics:
                    sentiment_distribution = sentiment_metrics["sentiment_distribution"]
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(sentiment_distribution.keys()),
                            y=list(sentiment_distribution.values()),
                            marker_color=['green', 'gray', 'red']
                        )
                    ])
                    fig.update_layout(
                        title="Customer Sentiment Distribution",
                        xaxis_title="Sentiment",
                        yaxis_title="Count"
                    )
                    chart_collection["sentiment_chart"] = fig.to_json()

            # Competitor comparison
            if "market_trends" in analysis_data and "competitor_landscape" in analysis_data["market_trends"]:
                competitive_data = analysis_data["market_trends"]["competitor_landscape"]
                if "main_competitors" in competitive_data:
                    competitor_list = competitive_data["main_competitors"]
                    competitor_names = [c["name"] for c in competitor_list]
                    market_shares = [c["market_share"] for c in competitor_list]

                    fig = go.Figure(data=[go.Pie(
                        labels=competitor_names,
                        values=market_shares,
                        hole=0.3
                    )])
                    fig.update_layout(title="Market Share Distribution")
                    chart_collection["market_share_chart"] = fig.to_json()

        except Exception as e:
            logger.warning(f"Failed to create some visualizations: {e}")

        return chart_collection

    def _generate_conclusion(self, analysis_data: Dict[str, Any]) -> str:
        """Generate report conclusion."""
        conclusion_sections = []

        # Overall assessment
        positive_indicators = 0
        total_indicators = 0

        if "sentiment_analysis" in analysis_data and "analysis" in analysis_data["sentiment_analysis"]:
            sentiment_metrics = analysis_data["sentiment_analysis"]["analysis"]
            if sentiment_metrics.get("average_rating", 0) >= 4:
                positive_indicators += 1
            total_indicators += 1

        if "market_trends" in analysis_data:
            market_trends = analysis_data["market_trends"]
            if "demand_analysis" in market_trends:
                if market_trends["demand_analysis"].get("demand_trend") == "growing":
                    positive_indicators += 1
                total_indicators += 1

        market_outlook = "positive" if positive_indicators > total_indicators / 2 else "cautiously optimistic"

        conclusion_sections.append(f"Based on comprehensive analysis, the market outlook is {market_outlook}.")
        conclusion_sections.append("The product shows strong potential with opportunities for growth.")
        conclusion_sections.append("Strategic implementation of recommendations will be crucial for success.")

        return " ".join(conclusion_sections)

    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool."""
        return self._run(*args, **kwargs)