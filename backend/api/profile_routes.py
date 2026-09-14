"""
Profile API routes.

These endpoints expose the candidate profile through FastAPI.

Flow:

Frontend
    ↓
Profile API
    ↓
ProfileService
    ↓
ProfileRepository
    ↓
profile.json
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.services.profile_service import profile_service


router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"],
)


@router.get("/")
def get_profile():
    """
    Get the current candidate profile.
    """

    try:
        profile = profile_service.get_profile()

        return {
            "success": True,
            "profile": profile.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get profile: {str(e)}",
        )


@router.post("/")
def create_profile(data: Dict[str, Any]):
    """
    Create or replace the candidate profile.
    """

    try:
        profile = profile_service.save_profile(data)

        return {
            "success": True,
            "message": "Profile saved successfully.",
            "profile": profile.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile data: {str(e)}",
        )


@router.put("/")
def update_profile(data: Dict[str, Any]):
    """
    Update the existing candidate profile.
    """

    try:
        profile = profile_service.update_profile(data)

        return {
            "success": True,
            "message": "Profile updated successfully.",
            "profile": profile.model_dump(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile update: {str(e)}",
        )


@router.delete("/")
def delete_profile():
    """
    Clear the stored candidate profile.
    """

    try:
        profile_service.clear_profile()

        return {
            "success": True,
            "message": "Profile cleared successfully.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear profile: {str(e)}",
        )