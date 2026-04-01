import logging
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI
from app.api.endpoints import router as api_router

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audio Async MLOps Pipeline",
    description="로컬 서버 기반 비동기 오디오-MIDI 변환 FastAPI (basic-pitch)",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    # ProcessPoolExecutor allows heavy basic-pitch inference to not block async event loop
    # Limit max workers (e.g. 2-4) to prevent CPU/RAM overload depending on deployment size
    app.state.executor = ProcessPoolExecutor(max_workers=2)
    logger.info("ProcessPoolExecutor started with 2 workers.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    app.state.executor.shutdown(wait=True)
    logger.info("ProcessPoolExecutor shut down.")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1", tags=["Audio"])

@app.get("/")
def read_root():
    return {
        "message": "Audio Async MLOps Pipeline API is running. Check /docs for Swagger UI.",
        "status": "healthy"
    }
