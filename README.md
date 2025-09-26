# E-commerce Market Analysis Agent System 🤖

## Executive Summary

A production-ready multi-agent system that orchestrates specialized tools to analyze e-commerce products and markets, generating strategic insights through AI-powered analysis. This MVP demonstrates the **LangGraph** framework implementation for intelligent agent orchestration.

## 🚀 Quick Start

```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (optional - will use mock data without)
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY and GROQ_API_KEY

# Run the API server
python main.py

# Or use Docker
docker-compose up -d
```

## 📊 Example Usage

```bash
# Run demo analysis
curl http://localhost:8000/demo

# Submit analysis - NO URLs required!
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 17 Pro Max"
  }'

# The system automatically:
# 1. Uses Gemini's google_search to find product information
# 2. Analyzes sentiment from generated review data
# 3. Performs market trend analysis
# 4. Generates comprehensive reports with visualizations

# Check analysis status
curl http://localhost:8000/results/{request_id}

# Example response includes:
# - Product analysis with pricing and features
# - Sentiment analysis with customer insights
# - Market trends and competitor analysis
# - Comprehensive report with recommendations
```

## 🏗️ Architecture Overview

### System Design

```
┌─────────────────┐
│   REST API      │  FastAPI endpoints for analysis requests
└────────┬────────┘
         │
┌────────▼────────┐
│  Orchestrator   │  LangGraph-based coordinator
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┐
    │         │        │          │
┌───▼──┐ ┌───▼──┐ ┌──▼───┐ ┌────▼────┐
│Scraper│ │Sentiment│ │Market│ │Reporter │
│ Tool  │ │Analyzer │ │Trend │ │Generator│
└───┬──┘ └───┬──┘ └──┬───┘ └────┬────┘
    │         │        │          │
    └─────────┴────────┴──────────┘
              Specialized Tools
```

### Tools Implementation

1. **WebScraperTool**:
   - Uses Gemini API's google_search and url_context features for product data extraction
   - Automatically searches for product information when given a product name
   - Handles fallback gracefully when API keys are not configured

2. **SentimentAnalyzerTool**:
   - Generates realistic review analysis using LLM or template fallback
   - Provides sentiment distribution, top pros/cons, and recommendation rates
   - Includes realistic review samples with ratings and verified purchase status

3. **MarketTrendAnalyzerTool**:
   - Creates market insights with algorithmic price history generation
   - Simulates demand patterns and competitor landscape analysis
   - Provides market positioning and growth potential assessments

4. **ReportGeneratorTool**:
   - Compiles comprehensive reports from all analysis tools
   - Generates Plotly visualizations for price trends and sentiment distribution
   - Creates executive summaries and actionable recommendations

## 🔍 LangGraph Implementation Analysis

### Why LangGraph for This Project

This implementation uses **LangGraph** to demonstrate advanced agent orchestration capabilities. LangGraph provides:

**Key Benefits Realized:**
- **State Management**: Automatic state transitions between analysis phases
- **Error Recovery**: Built-in retry and error handling mechanisms
- **Workflow Visualization**: Clear representation of the analysis pipeline
- **Extensibility**: Easy to add new analysis steps or conditional logic

**Implementation Details:**
- **AgentState**: Typed state management tracking product data, sentiment, and market analysis
- **Sequential Workflow**: analyze_request → scrape_products → analyze_sentiment → analyze_market → generate_report
- **Error Handling**: Dedicated error node with comprehensive logging
- **Tool Integration**: Seamless integration with specialized analysis tools

## 🎯 Production Concerns & Missing Pieces

### Current Limitations

1. **No Real Data Sources**: Using mock data except for Gemini URL scraping
2. **Memory Constraints**: In-memory storage instead of proper database
3. **Limited Error Recovery**: Basic retry logic, no circuit breakers
4. **No Authentication**: API is completely open
5. **Missing Monitoring**: No metrics, tracing, or alerting

### What's Needed for Production

- **Robust Data Pipeline**: Real-time data ingestion from multiple sources
- **Distributed Processing**: Message queues (Kafka/RabbitMQ) for scale
- **Persistent Storage**: PostgreSQL + Redis for state and caching
- **Service Mesh**: Istio/Linkerd for inter-service communication
- **Observability Stack**: Prometheus + Grafana + Jaeger
- **Security Layer**: OAuth2, rate limiting, input validation

## Data Architecture and Storage

**Current State**

The system uses basic in-memory storage (`analysis_cache = {}`) for analysis results and request tracking. Data persistence is minimal with no structured schema.

**Evolution**

### Recommended Data Schema

```python
# Analysis Results
{
    "id": "uuid",
    "request_id": "string",
    "product_name": "string",
    "timestamp": "datetime",
    "status": "pending|in_progress|completed|failed",
    "results": {
        "product_data": {...},
        "sentiment_analysis": {...},
        "market_trends": {...},
        "report": {...}
    },
    "metadata": {
        "processing_time": "float",
        "tools_used": ["list"],
        "api_version": "string"
    }
}

# Request History
{
    "id": "uuid",
    "user_id": "string",
    "product_name": "string",
    "parameters": {...},
    "created_at": "datetime",
    "status": "string"
}

# Cache Layer
{
    "cache_key": "string", # hash(product_name + params)
    "data": {...},
    "expires_at": "datetime",
    "source": "scraper|sentiment|trends"
}

# Agent Configurations
{
    "agent_id": "string",
    "config": {
        "llm_model": "string",
        "temperature": "float",
        "max_retries": "int",
        "timeout": "int"
    },
    "version": "string",
    "active": "boolean"
}
```

### Storage System Recommendation

**PostgreSQL + Redis** combination:

- **PostgreSQL**: Primary storage for analysis results, request history, and configurations
  - ACID compliance for critical data
  - Complex queries for analytics
  - JSON columns for flexible schema evolution

- **Redis**: High-performance caching and session management
  - Tool output caching (TTL: 1-6 hours depending on data freshness needs)
  - Request deduplication
  - Rate limiting counters
  - Real-time status updates

**Alternative for smaller scale**: SQLite + in-memory cache would suffice for demo/testing environments.

## Monitoring and Observability

**Current State**

Basic logging via Python logging module with minimal health checking through `/health` endpoint.

**Evolution**

### Monitoring Strategy

**Application Metrics:**
- Request throughput (requests/min)
- Processing latency (p50, p95, p99)
- Tool execution time per component
- Cache hit ratios
- Error rates by tool/endpoint

**Agent-Specific Metrics:**
- LLM token consumption and costs
- Agent workflow completion rates
- Tool failure rates and retry counts
- Data freshness (time since last scrape)

**System Health:**
- Memory usage and garbage collection
- Database connection pool status
- External API rate limit status
- Queue depth for async processing

### Implementation Approach

```python
# Observability Stack
- Prometheus: Metrics collection
- Grafana: Visualization dashboards
- Structured logging: JSON format with correlation IDs
- Health checks: Deep checks for dependencies (DB, external APIs)
- Alerting: Slack integration for critical failures
```

**Key Metrics to Monitor:**
- `analysis_requests_total{status, product_category}`
- `tool_execution_duration_seconds{tool_name}`
- `llm_tokens_consumed{model, operation}`
- `cache_operations_total{operation, result}`
- `external_api_calls{service, status_code}`

---

## Scaling Strategy

**Current State**

Single-threaded processing with no load balancing or horizontal scaling capabilities.

**Evolution**

### High-Load Architecture (100+ simultaneous analyses)

```
┌─────────────────┐
│   Load Balancer │  (Nginx)
└─────────┬───────┘
          │
    ┌─────▼─────┬─────────┬─────────┐
    │  API      │  API    │  API    │  (3+ FastAPI instances)
    │  Server 1 │  Server 2│ Server 3│
    └─────┬─────┴─────┬───┴─────┬───┘
          │           │         │
    ┌─────▼─────────────────────▼───┐
    │      Message Queue            │  (Redis/RabbitMQ)
    └─────┬─────────────────────────┘
          │
    ┌─────▼─────┬─────────┬─────────┐
    │  Worker   │ Worker  │ Worker  │  (Auto-scaling workers)
    │  Node 1   │ Node 2  │ Node 3  │
    └───────────┴─────────┴─────────┘
```

### Optimization Strategies

**LLM Cost Optimization:**
- Intelligent prompt caching based on product similarity
- Model selection by complexity (GPT-5 for analysis, GPT-4o-mini for simple tasks)
- Batch processing for similar requests

**Caching Strategy:**
- In-memory cache (Redis) for immediate responses
- Database cache for processed analysis results

**Parallel Processing:**
- Async tool execution within workflows
- Celery task queue for long-running analyses
- Connection pooling for external APIs

---

## Quality Evaluation and Continuous Improvement

**Current State**

No systematic quality evaluation.

**Evolution**

### Quality Evaluation (LLM as Judge)

```python
# Automated Quality Assessment
quality_metrics = {
    "factual_accuracy": llm_judge_factual_check(analysis, reference_data),
    "sentiment_consistency": compare_sentiment_across_sources(analysis),
    "recommendation_relevance": evaluate_business_recommendations(analysis),
    "report_completeness": check_required_sections(report)
}
```

**Implementation:**
- Dedicated evaluation LLM (GPT-4o) scores analysis quality
- Reference dataset for ground truth comparisons
- Automated quality scoring pipeline (1-10 scale)
- Quality trend tracking over time

### A/B Testing Framework

**Prompt Engineering Experiments:**
- Version control for prompts in Git
- Feature flags for prompt variants
- Statistical significance testing (minimum 100 samples per variant)
- Conversion metrics: user satisfaction, analysis accuracy

**Strategy Comparison:**
```python
strategies = {
    "sequential": "Current LangGraph sequential flow",
    "parallel": "Parallel tool execution with result merging",
    "iterative": "Multi-pass refinement approach"
}
```

### Feedback Loop Integration

**User Feedback:**
- Rating system (1-5 stars) for analysis quality
- Specific feedback categories (accuracy, completeness, usefulness)
- Free-text comments for qualitative insights

**Automated Learning:**
- User interaction patterns (which sections read most)
- Downstream decision tracking (if analysis led to business action)
- Comparative analysis success rates
- Continuous model fine-tuning based on feedback

**Agent Evolution:**
- Prompt optimization based on success metrics
- Tool chain adjustments based on performance data
- Dynamic parameter tuning (temperature, max tokens)
- New capability deployment through gradual rollout
