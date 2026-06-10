from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.api.dependencies import get_model

# Create the app
app = FastAPI(
    title="Sentinel Lite API",
    description="Aerial perception pipeline — detection, geolocation, and intelligence reporting.",
    version="0.1.0"
)

# CORS middleware — this allows your frontend (running on a different
# port during development) to make requests to this API without being
# blocked by the browser's same-origin policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes under /api/v1
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """
    Pre-load the model when the server starts rather than
    on the first request. This means the first user request
    is just as fast as every subsequent one.
    """
    print("Starting Sentinel Lite API...")
    get_model()
    print("Ready.")


@app.get("/")
async def root():
    return {
        "name": "Sentinel Lite API",
        "version": "0.1.0",
        "docs": "/docs"
    }