from fastapi import FastAPI
from app.core.config import settings

# Import routers
from app.api.v1.health import router as health_router
from app.api.v1.parse_resume import router as parse_router
from app.api.v1.match_candidate import router as match_router
from app.api.v1.analyze_resume import router as analyze_router
from app.api.v1.batch_ranking import router as batch_router

# from app.api.v1.feedback import router as feedback_router  # Disabled for Phase 4 - postponed to Phase 5


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


@app.get("/")
def root():
    return {
        "message": "Resume Screening AI API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": "/api/v1",
    }


app.include_router(health_router, prefix="/api/v1", tags=["Health"])

app.include_router(parse_router, prefix="/api/v1", tags=["Parsing"])

app.include_router(match_router, prefix="/api/v1", tags=["Matching"])

app.include_router(analyze_router, prefix="/api/v1", tags=["Analysis"])

app.include_router(batch_router, prefix="/api/v1", tags=["Batch Ranking"])

# Feedback endpoint disabled for Phase 4 - keeping code for Phase 5
# Requires 50-100 feedback samples before enabling ML weight retraining
# app.include_router(
#     feedback_router,
#     prefix="/api/v1",
#     tags=["Feedback"]
# )
