from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from src.logger import logger
import random
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class MarketTrendInput(BaseModel):
    product_name: str = Field(description="Product name to analyze")
    category: Optional[str] = Field(default=None, description="Product category")
    time_period_days: int = Field(default=90, description="Analysis period in days")

class MarketTrendAnalyzerTool(BaseTool):
    name: str = "market_trend_analyzer"
    description: str = "Analyzes market trends including price history, demand patterns, and competitor analysis."
    args_schema: type[BaseModel] = MarketTrendInput

    def _run(self, product_name: str, category: Optional[str] = None, time_period_days: int = 90) -> Dict[str, Any]:
        """Execute market trend analysis."""
        try:
            # Generate market data
            price_history = self._generate_price_history(product_name, time_period_days)
            demand_data = self._generate_demand_data(product_name, time_period_days)
            competitor_data = self._generate_competitor_analysis(product_name, category)
            market_insights = self._generate_market_insights(product_name, category)

            return {
                "status": "success",
                "product": product_name,
                "category": category or "General",
                "analysis_period": f"{time_period_days} days",
                "price_trends": price_history,
                "demand_analysis": demand_data,
                "competitor_landscape": competitor_data,
                "market_insights": market_insights,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"MarketTrendAnalyzerTool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": {}
            }

    def _generate_price_history(self, product_name: str, days: int) -> Dict[str, Any]:
        """Generate price history data."""
        base_price = random.uniform(50, 1500)
        prices = []
        dates = []

        for i in range(0, days, 7):  # Weekly data points
            date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
            # Add some realistic price fluctuation
            variation = random.uniform(-0.1, 0.15)
            price = base_price * (1 + variation)
            prices.append(round(price, 2))
            dates.append(date)
            base_price = price

        current_price = prices[-1]
        initial_price = prices[0]
        price_change = ((current_price - initial_price) / initial_price) * 100

        return {
            "current_price": f"${current_price:.2f}",
            "price_change_percent": round(price_change, 2),
            "price_trend": "increasing" if price_change > 0 else "decreasing",
            "historical_prices": {
                "dates": dates,
                "prices": prices
            },
            "price_volatility": "medium",
            "min_price": f"${min(prices):.2f}",
            "max_price": f"${max(prices):.2f}",
            "average_price": f"${sum(prices)/len(prices):.2f}"
        }

    def _generate_demand_data(self, product_name: str, days: int) -> Dict[str, Any]:
        """Generate demand analysis data."""
        base_demand = random.randint(1000, 50000)

        # Simulate seasonal patterns
        demand_scores = []
        for i in range(0, days, 7):
            seasonal_factor = 1 + 0.3 * random.random()
            trend_factor = 1 + (i / days) * 0.2  # Growing trend
            demand = base_demand * seasonal_factor * trend_factor
            demand_scores.append(int(demand))

        return {
            "current_demand_score": demand_scores[-1],
            "demand_trend": "growing",
            "search_volume_change": f"+{random.randint(15, 45)}%",
            "seasonal_patterns": {
                "peak_season": "Q4 (Holiday Season)",
                "low_season": "Q1 (Post-Holiday)"
            },
            "demand_forecast": {
                "next_30_days": "High",
                "next_quarter": "Moderate to High",
                "confidence": 78
            },
            "market_saturation": random.randint(45, 75),
            "growth_potential": "High" if random.random() > 0.5 else "Moderate"
        }

    def _generate_competitor_analysis(self, product_name: str, category: Optional[str]) -> Dict[str, Any]:
        """Generate competitor analysis data."""
        competitors = []

        # Generate 3-5 competitors
        competitor_names = [
            f"Competitor A ({category or 'Premium'})",
            f"Competitor B ({category or 'Budget'})",
            f"Competitor C ({category or 'Mid-range'})"
        ]

        for comp_name in competitor_names:
            competitors.append({
                "name": comp_name,
                "market_share": random.randint(10, 35),
                "price_point": f"${random.uniform(40, 1600):.2f}",
                "rating": round(random.uniform(3.5, 4.8), 1),
                "key_features": random.sample([
                    "Premium materials",
                    "Extended warranty",
                    "Fast shipping",
                    "Eco-friendly",
                    "Advanced features",
                    "Budget-friendly",
                    "Brand reputation"
                ], 3)
            })

        return {
            "total_competitors": len(competitors),
            "main_competitors": competitors,
            "market_position": random.choice(["Leader", "Challenger", "Follower"]),
            "competitive_advantages": [
                "Superior quality",
                "Competitive pricing",
                "Strong brand recognition"
            ],
            "market_share_estimate": random.randint(15, 40),
            "competitive_pressure": random.choice(["High", "Medium", "Low"])
        }

    def _generate_market_insights(self, product_name: str, category: Optional[str]) -> Dict[str, Any]:
        """Generate market insights."""
        insights = {
            "key_trends": [
                f"Increasing demand for sustainable {category or 'products'}",
                "Shift towards premium quality offerings",
                "Growing importance of online reviews",
                "Price sensitivity due to economic conditions"
            ],
            "opportunities": [
                "Expand into emerging markets",
                "Develop eco-friendly variants",
                "Enhance digital marketing presence",
                "Create bundle offers"
            ],
            "risks": [
                "Supply chain disruptions",
                "New market entrants",
                "Changing consumer preferences",
                "Economic downturn impact"
            ],
            "recommendations": [
                f"Focus on differentiating {product_name} through unique features",
                "Invest in customer loyalty programs",
                "Monitor competitor pricing strategies closely",
                "Enhance product visibility on major platforms"
            ],
            "market_maturity": random.choice(["Growing", "Mature", "Emerging"]),
            "innovation_index": random.randint(60, 90)
        }

        return insights

    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool."""
        return self._run(*args, **kwargs)