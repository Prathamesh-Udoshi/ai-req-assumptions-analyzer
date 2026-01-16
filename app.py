"""
Intelligent Test Case Quality Analyzer API

FastAPI application providing test case quality analysis.
Analyzes test cases and requirements to detect ambiguity
and hidden assumptions before test automation.
"""

# Workaround for pydantic v1 compatibility with Python 3.11+
import typing
if hasattr(typing, '_GenericAlias'):
    # Python 3.9+
    typing._GenericAlias.__module__ = 'typing'
if hasattr(typing, 'ForwardRef'):
    # Monkey patch ForwardRef._evaluate for Python 3.11+ compatibility
    original_evaluate = typing.ForwardRef._evaluate
    def patched_evaluate(self, globalns, localns, type_params=None, *, recursive_guard=frozenset()):
        return original_evaluate(self, globalns, localns, type_params, recursive_guard=recursive_guard)
    typing.ForwardRef._evaluate = patched_evaluate

import logging
from typing import Dict, Any,List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.scorer import RequirementScorer
from core.suggestions import SuggestionGenerator
from nlp.preprocess import TextPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Test Case Quality Analyzer",
    description="Detects ambiguity and hidden assumptions in test cases and requirements",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
scorer = RequirementScorer()
suggestion_generator = SuggestionGenerator()
text_preprocessor = TextPreprocessor()


class AnalyzeRequest(BaseModel):
    """Request model for test case analysis."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The test case or requirement text to analyze",
        example="User logs in with valid credentials and accesses dashboard"
    )


class ComponentScore(BaseModel):
    """Component score with breakdown."""
    score: float = Field(ge=0, le=100, description="Component score")
    components: dict = Field(description="Sub-component scores")

class AmbiguityAnalysis(BaseModel):
    """Multi-signal ambiguity analysis."""
    score: float = Field(ge=0, le=100, description="Overall ambiguity score")
    confidence: str = Field(description="Analysis confidence: HIGH/MEDIUM/LOW")
    components: dict = Field(description="Component scores: lexical, testability, references")

class AssumptionAnalysis(BaseModel):
    """Multi-signal assumption analysis."""
    score: float = Field(ge=0, le=100, description="Overall assumption score")
    components: dict = Field(description="Component breakdown with strength classification")

class ImpactIssue(BaseModel):
    """Issue with impact explanation."""
    type: str = Field(description="Issue type: Ambiguity or Assumption")
    message: str = Field(description="Human-readable issue description")
    impact: str = Field(description="Why this matters for testing/automation")
    category: str = Field(default=None, description="Assumption category")
    assumption: str = Field(default=None, description="Specific assumption text")

class AnalyzeResponse(BaseModel):
    """Enhanced response model with multi-signal analysis."""
    ambiguity: AmbiguityAnalysis = Field(description="Multi-signal ambiguity analysis")
    assumptions: AssumptionAnalysis = Field(description="Multi-signal assumption analysis")
    readiness_score: float = Field(ge=0, le=100, description="Overall readiness score")
    readiness_level: str = Field(description="Readiness classification")
    issues: List[ImpactIssue] = Field(description="Issues with impact explanations")
    clarifying_questions: List[str] = Field(description="Questions to improve testability")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Intelligent Test Case Quality Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "nlp_processor": "available",
            "scorer": "available",
            "suggestion_generator": "available"
        }
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_test_case(request: AnalyzeRequest):
    """
    Analyze test case or requirement text for ambiguity and assumptions.

    This endpoint performs comprehensive analysis to detect:
    - Ambiguous terms and phrases in test cases
    - Hidden assumptions about environment, data, and state
    - Overall readiness for test automation
    """
    try:
        text = request.text.strip()

        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        logger.info(f"Analyzing text: {text[:100]}...")

        # Perform analysis
        analysis_result = scorer.analyze_text(text)

        # Generate clarifying questions (always provide for comprehensive coverage)
        clarifying_questions = scorer._generate_clarifying_questions(
            analysis_result.get("issues", []),
            text
        )

        # Add clarifying questions to result
        analysis_result["clarifying_questions"] = clarifying_questions

        logger.info(f"Analysis complete - Readiness: {analysis_result.get('readiness_level')}")

        return AnalyzeResponse(**analysis_result)

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/detailed")
async def analyze_detailed(request: AnalyzeRequest):
    """
    Detailed analysis with preprocessing information.

    Returns comprehensive analysis including:
    - Basic analysis results
    - Text preprocessing details
    - Token-level information
    - Dependency parsing results
    """
    try:
        text = request.text.strip()

        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Get basic analysis
        analysis_result = scorer.analyze_text(text)

        # Add preprocessing details
        preprocessing = text_preprocessor.preprocess_text(text)
        analysis_result["preprocessing"] = {
            "sentences": preprocessing["sentences"],
            "token_count": len(preprocessing["tokens"]),
            "word_count": sum(1 for t in preprocessing["tokens"] if t["is_alpha"]),
            "entities": preprocessing["entities"]
        }

        # Generate clarifying questions (always provide for comprehensive coverage)
        clarifying_questions = suggestion_generator.generate_suggestions(
            analysis_result.get("issues", []),
            text,
            always_ask=True
        )
        analysis_result["clarifying_questions"] = clarifying_questions

        return analysis_result

    except Exception as e:
        logger.error(f"Detailed analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detailed analysis failed: {str(e)}")


@app.post("/analyze/batch")
async def analyze_batch(request: Dict[str, Any]):
    """
    Analyze multiple requirements in batch.

    Expects a JSON object with a 'texts' array containing requirement texts.
    Returns analysis results for each text.
    """
    try:
        texts = request.get("texts", [])

        if not texts:
            raise HTTPException(status_code=400, detail="No texts provided for batch analysis")

        if len(texts) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size limited to 50 texts")

        results = []

        for text in texts:
            if not isinstance(text, str) or not text.strip():
                results.append({"error": "Invalid text provided"})
                continue

            try:
                analysis = scorer.analyze_text(text.strip())
                clarifying_questions = scorer._generate_clarifying_questions(
                    analysis.get("issues", []),
                    text.strip()
                )
                analysis["clarifying_questions"] = clarifying_questions
                results.append(analysis)
            except Exception as e:
                results.append({"error": f"Analysis failed: {str(e)}"})

        return {"results": results, "total": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )