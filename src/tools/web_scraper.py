from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from src.logger import logger
from src.config import settings
import json
import re
from pydantic import BaseModel, Field

class ProductSearchInput(BaseModel):
    product_name: str = Field(description="Name of the product to search and analyze")
    max_results: int = Field(default=3, description="Maximum number of results to analyze")
    extract_fields: Optional[List[str]] = Field(
        default=["title", "price", "description", "features", "availability", "images"],
        description="Fields to extract from the product page"
    )

class WebScraperTool(BaseTool):
    name: str = "web_scraper"
    description: str = "Searches for product information online using Gemini's search capabilities."
    args_schema: type[BaseModel] = ProductSearchInput

    def _run(self, product_name: str = None, max_results: int = 3, extract_fields: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Search for product information online and extract data using Gemini's search and URL context features."""
        # Handle LangChain invocation with kwargs
        if product_name is None and kwargs:
            product_name = kwargs.get('product_name')
            max_results = kwargs.get('max_results', 3)
            extract_fields = kwargs.get('extract_fields')

        if not product_name:
            return {
                "status": "error",
                "error": "Product name is required",
                "products": [],
                "count": 0
            }

        if not settings.google_api_key:
            logger.error("Google API key not configured and required for URL discovery")
            return {
                "status": "error",
                "error": "Google API key not configured. Cannot search for or analyze URLs without Gemini API access.",
                "products": [],
                "count": 0
            }

        try:
            from google import genai
            from google.genai.types import GenerateContentConfig

            # Initialize Gemini client
            client = genai.Client(api_key=settings.google_api_key)

            # Configure with both google_search and url_context tools
            tools = [
                {"google_search": {}},
                {"url_context": {}}
            ]

            config = GenerateContentConfig(
                tools=tools,
                temperature=0.1,
                top_p=0.95,
            )

            logger.info(f"Searching for product: {product_name} with {len(tools)} tools")

            # Create a comprehensive prompt that searches and analyzes
            default_fields = ["title", "price", "description", "features", "availability", "images"]
            fields = extract_fields or default_fields
            fields_str = "\n".join([f"- {field}" for field in fields])

            prompt = f"""Search online for "{product_name}" and analyze the product information from the most relevant sources.

Your task:
1. Use google_search to find relevant product pages for "{product_name}"
2. Use url_context to analyze the discovered URLs
3. Extract detailed product information from the pages

Extract the following information:
{fields_str}

Focus on:
- Official brand/manufacturer websites
- Major e-commerce platforms (Amazon, BestBuy, Walmart, etc.)
- Authorized retailers

Return a JSON array with up to {max_results} products found, each containing:
{{
    "title": "Product name",
    "price": "Current price with currency",
    "description": "Product description",
    "features": ["feature1", "feature2"],
    "availability": "Stock status",
    "rating": "Customer rating if available",
    "images": ["image_url1", "image_url2"],
    "source_url": "URL where found"
}}

Return ONLY the JSON array, no other text."""

            try:
                logger.info(f"About to call Gemini API with model=gemini-2.5-flash")
                logger.info(f"Prompt length: {len(prompt)}")
                logger.info(f"Config tools: {config.tools}")

                # Generate content with search and URL analysis
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config,
                )

                logger.info("Gemini API call completed successfully")

                response_text = response.text if hasattr(response, 'text') else str(response)

                # Log grounding metadata if available
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'grounding_metadata'):
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'grounding_chunks'):
                            logger.info(f"Found {len(metadata.grounding_chunks)} sources for {product_name}")
                            for chunk in metadata.grounding_chunks[:3]:
                                if hasattr(chunk, 'uri'):
                                    logger.info(f"  Source: {chunk.uri}")

                # Parse JSON from response

                # Try to extract JSON array
                if '```json' in response_text:
                    json_content = response_text.split('```json')[1].split('```')[0].strip()
                else:
                    # Try to find JSON array or object
                    json_match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', response_text)
                    json_content = json_match.group() if json_match else response_text

                try:
                    parsed_data = json.loads(json_content)

                    # Ensure we have a list of products
                    if isinstance(parsed_data, dict):
                        products = [parsed_data]
                    elif isinstance(parsed_data, list):
                        products = parsed_data
                    else:
                        products = []

                    # Add source_url if missing
                    for product in products:
                        if 'source_url' not in product:
                            product['source_url'] = f"Search result for {product_name}"

                    logger.info(f"Successfully found {len(products)} products for {product_name}")

                    return {
                        "status": "success",
                        "products": products[:max_results],
                        "count": len(products[:max_results])
                    }

                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    return {
                        "status": "success",
                        "products": [{
                            "title": product_name,
                            "description": f"Product information found but parsing failed: {response_text[:500]}",
                            "error": "JSON parsing failed",
                            "source_url": "Search result"
                        }],
                        "count": 1
                    }

            except Exception as e:
                logger.error(f"Error searching for {product_name}: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Failed to search for {product_name}: {str(e)}",
                    "products": [],
                    "count": 0
                }

        except ImportError:
            logger.error("google.genai package not available. Install with: pip install google-genai")
            return {
                "status": "error",
                "error": "google.genai package not available. Install with: pip install google-genai",
                "products": [],
                "count": 0
            }
        except Exception as e:
            logger.error(f"WebScraperTool error: {str(e)}")
            return {
                "status": "error",
                "error": f"WebScraperTool failed: {str(e)}",
                "products": [],
                "count": 0
            }


    async def _arun(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of the tool."""
        return self._run(*args, **kwargs)