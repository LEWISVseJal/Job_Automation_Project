"""
Resume API routes.

These endpoints expose the parsed resume through FastAPI.

Flow:

Frontend
    ↓
Resume API
    ↓
ResumeService
    ↓
ResumeRepository
    ↓
resume.json
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.services.resume_service import resume_service


router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"],
)


@router.get("/")
def get_resume():
    """
    Get the current parsed resume.
    """

    try:
        resume = resume_service.get_resume()

        return {
            "success": True,
            "resume": resume.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resume: {str(e)}",
        )


@router.post("/")
def create_resume(data: Dict[str, Any]):
    """
    Create or replace the parsed resume.
    """

    try:
        resume = resume_service.save_resume(data)

        return {
            "success": True,
            "message": "Resume saved successfully.",
            "resume": resume.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resume data: {str(e)}",
        )


@router.put("/")
def update_resume(data: Dict[str, Any]):
    """
    Update the existing parsed resume.
    """

    try:
        resume = resume_service.update_resume(data)

        return {
            "success": True,
            "message": "Resume updated successfully.",
            "resume": resume.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resume update: {str(e)}",
        )


@router.delete("/")
def delete_resume():
    """
    Clear the stored parsed resume.
    """

    try:
        resume_service.clear_resume()

        return {
            "success": True,
            "message": "Resume cleared successfully.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear resume: {str(e)}",
        )