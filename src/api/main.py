from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.agents import MarketAnalysisOrchestrator
from src.logger import logger
from src.config import settings
import uuid
from datetime import datetime

app = FastAPI(
    title="E-commerce Market Analysis Agent API",
    description="API for orchestrating market analysis agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for analysis results
analysis_cache: Dict[str, Any] = {}

class AnalysisRequest(BaseModel):
    """Request model for market analysis."""
    product_name: str = Field(..., description="Product name to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis: quick, detailed, comprehensive")

class AnalysisResponse(BaseModel):
    """Response model for analysis request."""
    request_id: str
    status: str
    message: str
    result_url: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Market Analysis Agent API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "/analyze": "POST - Submit analysis request",
            "/results/{request_id}": "GET - Retrieve analysis results",
            "/health": "GET - Health check",
            "/demo": "GET - Run demo analysis"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "google_api_configured": bool(settings.google_api_key)
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_product(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Submit a product for market analysis."""
    request_id = str(uuid.uuid4())

    # Initialize status
    analysis_cache[request_id] = {
        "status": "processing",
        "started_at": datetime.now().isoformat(),
        "request": request.dict()
    }

    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        request_id,
        request.product_name
    )

    return AnalysisResponse(
        request_id=request_id,
        status="processing",
        message=f"Analysis started for {request.product_name}",
        result_url=f"/results/{request_id}"
    )

async def run_analysis(
    request_id: str,
    product_name: str
):
    """Run the analysis in background."""
    logger.info(f"Starting LangGraph analysis {request_id} for {product_name}")

    try:
        orchestrator = MarketAnalysisOrchestrator()
        analysis_result = orchestrator.run(
            request=f"analyze {product_name}"
        )

        analysis_cache[request_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "result": analysis_result,
            "framework_used": "langgraph"
        })

    except Exception as e:
        logger.error(f"Analysis failed for {request_id}: {e}")
        analysis_cache[request_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

@app.get("/results/{request_id}")
async def get_results(request_id: str):
    """Retrieve analysis results."""
    if request_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_cache[request_id]


@app.get("/demo")
async def run_demo():
    """Run a demo analysis on iPhone 17 Pro Max."""
    orchestrator = MarketAnalysisOrchestrator()
    demo_result = orchestrator.run(
        request="analyze iPhone 17 Pro Max"
    )

    return {
        "demo": True,
        "product": "iPhone 17 Pro Max",
        "result": demo_result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )