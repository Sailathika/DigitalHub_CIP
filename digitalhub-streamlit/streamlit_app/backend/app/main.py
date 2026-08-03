from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from app.database.seed import seed_default_admin
from app.database.seed_demo_data import seed_demo_marketplace
from app.database.session import init_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "DigitalHub backend API — dataset ingestion, ETL, customer analytics, "
        "RFM segmentation, CLV/churn prediction, product recommendations, "
        "and PDF reporting for the DigitalHub multi-vendor analytics platform."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Serves locally-stored uploads (currently: vendor product images under
# uploads/products/) at /static/products/<filename>.
app.mount("/static", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="static")


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    init_db()
    logger.info("Database tables verified/created")
    seed_default_admin()
    seed_demo_marketplace()


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
