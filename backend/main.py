"""
Main FastAPI application.

Job Automation backend.

Architecture:

Frontend
    ↓
FastAPI
    ↓
API Routes
    ↓
Services
    ↓
Repositories
    ↓
JSON Storage
"""

from fastapi import FastAPI

from backend.config.settings import (
    ensure_directories,
    validate_settings,
    get_config_summary,
)

from backend.api.profile_routes import router as profile_router
from backend.api.resume_routes import router as resume_router


# -------------------------------------------------------------------
# Application setup
# -------------------------------------------------------------------

ensure_directories()

errors = validate_settings()

if errors:
    raise RuntimeError(
        "Configuration errors:\n" +
        "\n".join(f"- {error}" for error in errors)
    )


app = FastAPI(
    title="Job Automation API",
    description="Backend API for personal job search and application automation.",
    version="1.0.0",
)


# -------------------------------------------------------------------
# Register API routes
# -------------------------------------------------------------------

app.include_router(profile_router)
app.include_router(resume_router)


# -------------------------------------------------------------------
# Basic routes
# -------------------------------------------------------------------

@app.get("/")
def root():
    """
    Root endpoint.
    """

    return {
        "application": "Job Automation",
        "status": "running",
        "message": "Job Automation API is running.",
    }


@app.get("/health")
def health():
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
    }


@app.get("/api/status")
def api_status():
    """
    Return basic application status.
    """

    from backend.storage.repositories import (
        job_repository,
        job_match_repository,
        application_repository,
    )

    from backend.config.settings import (
        ENABLE_EASY_APPLY,
        STOP_BEFORE_FINAL_SUBMIT,
        ALLOW_FINAL_SUBMIT,
        PROJECT_ROOT,
        DATA_DIR,
    )

    return {
        "application": "Job Automation",
        "status": "running",

        "paths": {
            "project_root": str(PROJECT_ROOT),
            "data_dir": str(DATA_DIR),
        },

        "storage": {
            "jobs_count": len(job_repository.get_all()),
            "matches_count": len(job_match_repository.get_all()),
            "applications_count": len(
                application_repository.get_all()
            ),
        },

        "automation": {
            "easy_apply_enabled": ENABLE_EASY_APPLY,
        },

        "safety": {
            "stop_before_final_submit": STOP_BEFORE_FINAL_SUBMIT,
            "allow_final_submit": ALLOW_FINAL_SUBMIT,
        },
    }


# -------------------------------------------------------------------
# Configuration endpoint
# -------------------------------------------------------------------

@app.get("/api/config")
def api_config():
    """
    Return a safe configuration summary.
    """

    return get_config_summary()