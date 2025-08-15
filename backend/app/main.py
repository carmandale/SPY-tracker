"""
SPY TA Tracker - Main FastAPI Application

A streamlined, modular FastAPI application for tracking SPY predictions,
generating AI-powered suggestions, and managing option strategies.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError

from .config import settings
from .startup import run_startup_tasks
from .exceptions import (
    SPYTrackerException,
    spy_tracker_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)

# Import routers
from .routers import (
    predictions,
    admin,
    market,
    suggestions,
    ai,
    scheduler as scheduler_router,
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="SPY TA Tracker - Options trading assistant with AI predictions",
    version="2.0.0"
)

# Register exception handlers
app.add_exception_handler(SPYTrackerException, spy_tracker_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS
origins = [settings.frontend_origin] if settings.frontend_origin != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run startup tasks and get scheduler instance
_scheduler = run_startup_tasks()

# Pass scheduler to router that needs it
scheduler_router.set_scheduler(_scheduler)

# Include API routers
app.include_router(predictions.router)
app.include_router(admin.router)
app.include_router(market.router)
app.include_router(suggestions.router)
app.include_router(ai.router)
app.include_router(scheduler_router.router)


# Health check endpoint
@app.get("/healthz")
def healthz():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "app": settings.app_name}


# Static file serving for frontend (MUST be at the end after all API routes)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

if os.path.exists(static_dir):
    # Mount static assets
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir, html=False), name="assets")
        print(f"✅ Mounted assets directory: {assets_dir}")
        
        # List available assets for debugging
        try:
            asset_files = os.listdir(assets_dir)
            print(f"📁 Available assets: {asset_files}")
        except Exception as e:
            print(f"⚠️ Could not list assets: {e}")
    else:
        print(f"❌ Assets directory not found: {assets_dir}")
    
    # Serve favicon if it exists
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        @app.get("/favicon.ico")
        async def get_favicon():
            return FileResponse(favicon_path, media_type="image/x-icon")
    
    # Serve React app for production - catch-all route MUST be last
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes."""
        # Don't intercept explicit asset requests
        if full_path.startswith("assets/"):
            print(f"⚠️ Asset request reached SPA handler: {full_path}")
            raise HTTPException(status_code=404, detail=f"Asset not found: {full_path}")
        
        # Don't intercept API routes or documentation
        if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="API route not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file, media_type="text/html")
        else:
            raise HTTPException(
                status_code=404, 
                detail="Frontend not built or static files not found"
            )
else:
    print(f"❌ Static directory not found: {static_dir}")
    print("🔍 Available directories in backend:")
    try:
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        backend_contents = os.listdir(backend_dir)
        print(f"📁 Backend directory contents: {backend_contents}")
    except Exception as e:
        print(f"⚠️ Could not list backend directory: {e}")