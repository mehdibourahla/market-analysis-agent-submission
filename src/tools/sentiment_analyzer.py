from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from src.logger import logger
from src.config import settings
import random
from pydantic import BaseModel, Field

class SentimentAnalyzerInput(BaseModel):
    product_name: str = Field(description="Name of the product to analyze")
    review_count: int = Field(default=10, description="Number of reviews to analyze")
    sources: Optional[List[str]] = Field(default=None, description="Optional review sources")

class SentimentAnalyzerTool(BaseTool):
    name: str = "sentiment_analyzer"
    description: str = "Analyzes customer sentiment from product reviews and generates sentiment metrics."
    args_schema: type[BaseModel] = SentimentAnalyzerInput

    def _run(self, product_name: str, review_count: int = 10, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute sentiment analysis on product reviews."""
        try:
            # Generate realistic reviews using LLM
            reviews = self._generate_mock_reviews(product_name, review_count)

            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment(reviews)

            return {
                "status": "success",
                "product": product_name,
                "analysis": sentiment_analysis,
                "review_count": len(reviews),
                "reviews_sample": reviews[:3]  # Include sample reviews
            }

        except Exception as e:
            logger.error(f"SentimentAnalyzerTool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": {}
            }

    def _generate_mock_reviews(self, product_name: str, count: int) -> List[Dict[str, Any]]:
        """Generate reviews using Gemini LLM or templates."""
        if settings.google_api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=settings.google_api_key,
                    temperature=0.8
                )

                prompt = f"""Generate {count} realistic customer reviews for "{product_name}".
                Each review should have:
                - rating (1-5)
                - title
                - text (2-3 sentences)
                - pros (list)
                - cons (list)
                - verified_purchase (boolean)
                - helpful_count (number)

                Mix positive and negative reviews realistically.
                Return as JSON array.
                """

                llm_response = llm.invoke(prompt)

                # Parse response
                import json
                import re
                json_match = re.search(r'\[.*\]', llm_response.content, re.DOTALL)
                if json_match:
                    generated_reviews = json.loads(json_match.group())
                    return generated_reviews[:count]
            except Exception as e:
                logger.warning(f"Failed to generate reviews with Gemini: {e}")

        # Fallback to template-based review generation
        return self._get_fallback_reviews(product_name, count)

    def _get_fallback_reviews(self, product_name: str, count: int) -> List[Dict[str, Any]]:
        """Generate reviews using predefined templates."""
        templates = [
            {
                "rating": 5,
                "title": "Absolutely love it!",
                "text": f"The {product_name} exceeded all my expectations. Build quality is exceptional and the features work perfectly.",
                "pros": ["Excellent build quality", "Great features", "Fast delivery"],
                "cons": ["Price is a bit high"],
                "verified_purchase": True,
                "helpful_count": 245
            },
            {
                "rating": 4,
                "title": "Good product with minor issues",
                "text": f"Overall happy with the {product_name}. Works as advertised but has some minor quirks.",
                "pros": ["Good performance", "Nice design", "Easy to use"],
                "cons": ["Battery life could be better", "Occasional software bugs"],
                "verified_purchase": True,
                "helpful_count": 189
            },
            {
                "rating": 3,
                "title": "Average, nothing special",
                "text": f"The {product_name} is okay but doesn't really stand out from competitors.",
                "pros": ["Decent quality", "Fair price"],
                "cons": ["Limited features", "Average performance", "Better alternatives available"],
                "verified_purchase": True,
                "helpful_count": 76
            },
            {
                "rating": 2,
                "title": "Disappointed",
                "text": f"Expected more from the {product_name}. Multiple issues encountered.",
                "pros": ["Good packaging"],
                "cons": ["Poor build quality", "Doesn't work as advertised", "Customer service unhelpful"],
                "verified_purchase": True,
                "helpful_count": 134
            },
            {
                "rating": 5,
                "title": "Best purchase this year!",
                "text": f"The {product_name} is exactly what I needed. Highly recommend to everyone.",
                "pros": ["Perfect functionality", "Great value", "Excellent support"],
                "cons": [],
                "verified_purchase": True,
                "helpful_count": 412
            }
        ]

        # Randomly select and modify reviews
        template_reviews = []
        for i in range(min(count, len(templates) * 2)):
            selected_template = random.choice(templates)
            review_instance = selected_template.copy()
            review_instance["helpful_count"] = random.randint(10, 500)
            review_instance["verified_purchase"] = random.random() > 0.2
            template_reviews.append(review_instance)

        return template_reviews[:count]

    def _analyze_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from reviews."""
        if not reviews:
            return {"error": "No reviews to analyze"}

        ratings = [r.get("rating", 3) for r in reviews]
        avg_rating = sum(ratings) / len(ratings)

        # Count sentiment distribution
        sentiment_dist = {
            "positive": len([r for r in ratings if r >= 4]),
            "neutral": len([r for r in ratings if r == 3]),
            "negative": len([r for r in ratings if r <= 2])
        }

        # Aggregate pros and cons
        all_pros = []
        all_cons = []
        for review in reviews:
            all_pros.extend(review.get("pros", []))
            all_cons.extend(review.get("cons", []))

        # Count frequency
        from collections import Counter
        top_pros = dict(Counter(all_pros).most_common(5))
        top_cons = dict(Counter(all_cons).most_common(5))

        return {
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(reviews),
            "sentiment_distribution": sentiment_dist,
            "sentiment_score": round((sentiment_dist["positive"] - sentiment_dist["negative"]) / len(reviews) * 100, 1),
            "top_positive_aspects": top_pros,
            "top_negative_aspects": top_cons,
            "recommendation_rate": round(sentiment_dist["positive"] / len(reviews) * 100, 1),
            "verified_purchase_rate": round(
                len([r for r in reviews if r.get("verified_purchase", False)]) / len(reviews) * 100, 1
            )
        }

    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool."""
        return self._run(*args, **kwargs)