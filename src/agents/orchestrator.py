from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import operator
from src.tools import WebScraperTool, SentimentAnalyzerTool, MarketTrendAnalyzerTool, ReportGeneratorTool
from src.logger import logger
from src.config import settings

class AgentState(TypedDict):
    """State definition for the agent workflow."""
    messages: Annotated[List, operator.add]
    product_name: Optional[str]
    product_data: Optional[Dict[str, Any]]
    sentiment_data: Optional[Dict[str, Any]]
    market_data: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    error: Optional[str]
    current_step: str

class MarketAnalysisOrchestrator:
    """LangGraph-based orchestrator for market analysis agents."""

    def __init__(self):
        self.tools = self._initialize_tools()
        self.llm = self._initialize_llm()
        self.workflow = self._build_workflow()

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all analysis tools."""
        return {
            "web_scraper": WebScraperTool(),
            "sentiment_analyzer": SentimentAnalyzerTool(),
            "market_trend": MarketTrendAnalyzerTool(),
            "report_generator": ReportGeneratorTool()
        }

    def _initialize_llm(self):
        """Initialize Gemini 2.5 Flash for orchestration decisions."""
        if settings.google_api_key:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.google_api_key,
                temperature=0.3
            )
        else:
            logger.error("Google API key not configured - required for LangGraph orchestration")
            return None

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_request", self.analyze_request)
        workflow.add_node("scrape_products", self.scrape_products)
        workflow.add_node("analyze_sentiment", self.analyze_sentiment)
        workflow.add_node("analyze_market", self.analyze_market)
        workflow.add_node("generate_report", self.generate_report)
        workflow.add_node("handle_error", self.handle_error)

        # Add edges
        workflow.add_edge("analyze_request", "scrape_products")
        workflow.add_edge("scrape_products", "analyze_sentiment")
        workflow.add_edge("analyze_sentiment", "analyze_market")
        workflow.add_edge("analyze_market", "generate_report")
        workflow.add_edge("generate_report", END)
        workflow.add_edge("handle_error", END)

        # Set entry point
        workflow.set_entry_point("analyze_request")

        return workflow.compile()

    def analyze_request(self, state: AgentState) -> AgentState:
        """Analyze the user request and extract parameters."""
        logger.info("Analyzing user request")
        state["current_step"] = "analyze_request"

        try:
            # Extract product information from messages
            last_message = state["messages"][-1] if state["messages"] else None
            if not last_message:
                state["error"] = "No request message found"
                return state

            # Parse request content from message
            content = last_message.content if hasattr(last_message, 'content') else str(last_message)

            # Extract product name from request
            if "analyze" in content.lower():
                state["product_name"] = content.split("analyze")[-1].strip()
            else:
                state["product_name"] = content.strip()

            logger.info(f"Product to analyze: {state['product_name']}")
            return state

        except Exception as e:
            logger.error(f"Error in analyze_request: {e}")
            state["error"] = str(e)
            return state


    def scrape_products(self, state: AgentState) -> AgentState:
        """Search and scrape product information."""
        logger.info("Searching and scraping product information")
        state["current_step"] = "scrape_products"

        try:
            tool = self.tools["web_scraper"]
            product_name = state.get("product_name", "product")

            scraping_result = tool._run(product_name=product_name, max_results=3)
            state["product_data"] = scraping_result
            state["messages"].append(AIMessage(content=f"Found {scraping_result.get('count', 0)} products"))
            return state

        except Exception as e:
            logger.error(f"Error in scrape_products: {e}")
            state["error"] = str(e)
            state["product_data"] = {"status": "error", "error": str(e), "products": []}
            return state

    def analyze_sentiment(self, state: AgentState) -> AgentState:
        """Analyze customer sentiment."""
        logger.info("Analyzing customer sentiment")
        state["current_step"] = "analyze_sentiment"

        try:
            tool = self.tools["sentiment_analyzer"]
            sentiment_result = tool._run(
                product_name=state.get("product_name", "Product"),
                review_count=20
            )
            state["sentiment_data"] = sentiment_result
            state["messages"].append(AIMessage(content="Sentiment analysis completed"))
            return state

        except Exception as e:
            logger.error(f"Error in analyze_sentiment: {e}")
            state["error"] = str(e)
            return state

    def analyze_market(self, state: AgentState) -> AgentState:
        """Analyze market trends."""
        logger.info("Analyzing market trends")
        state["current_step"] = "analyze_market"

        try:
            tool = self.tools["market_trend"]
            market_result = tool._run(
                product_name=state.get("product_name", "Product"),
                time_period_days=90
            )
            state["market_data"] = market_result
            state["messages"].append(AIMessage(content="Market analysis completed"))
            return state

        except Exception as e:
            logger.error(f"Error in analyze_market: {e}")
            state["error"] = str(e)
            return state

    def generate_report(self, state: AgentState) -> AgentState:
        """Generate final report."""
        logger.info("Generating final report")
        state["current_step"] = "generate_report"

        try:
            tool = self.tools["report_generator"]

            # Compile all analysis results
            combined_analysis = {
                "product_analysis": state.get("product_data", {}),
                "sentiment_analysis": state.get("sentiment_data", {}),
                "market_trends": state.get("market_data", {})
            }

            report_result = tool._run(
                analysis_results=combined_analysis,
                report_format="comprehensive",
                include_visualizations=True
            )

            state["final_report"] = report_result
            state["messages"].append(AIMessage(content="Report generation completed"))
            return state

        except Exception as e:
            logger.error(f"Error in generate_report: {e}")
            state["error"] = str(e)
            return state

    def handle_error(self, state: AgentState) -> AgentState:
        """Handle errors in the workflow."""
        logger.error(f"Workflow error at step {state.get('current_step')}: {state.get('error')}")
        state["messages"].append(
            AIMessage(content=f"Error occurred: {state.get('error')}. Please try again.")
        )
        return state

    def run(self, request: str) -> Dict[str, Any]:
        """Run the complete analysis workflow."""
        logger.info(f"Starting market analysis for: {request}")

        initial_state = AgentState(
            messages=[HumanMessage(content=request)],
            product_name=None,
            product_data=None,
            sentiment_data=None,
            market_data=None,
            final_report=None,
            error=None,
            current_step="start"
        )

        try:
            final_state = self.workflow.invoke(initial_state)
            if final_state.get("error"):
                return {
                    "status": "error",
                    "error": final_state["error"],
                    "step": final_state.get("current_step")
                }

            return {
                "status": "success",
                "report": final_state.get("final_report"),
                "steps_completed": [
                    "analyze_request",
                    "scrape_products",
                    "analyze_sentiment",
                    "analyze_market",
                    "generate_report"
                ]
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }