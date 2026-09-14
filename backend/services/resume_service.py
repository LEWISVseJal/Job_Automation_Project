"""
Resume service.

Handles business logic related to the parsed resume.

Flow:

API
 ↓
ResumeService
 ↓
Resume schema
 ↓
ResumeRepository
 ↓
resume.json
"""

from typing import Any, Dict

from backend.schemas.resume import Resume
from backend.storage.repositories import resume_repository


class ResumeService:
    """Business logic for resume management."""

    def get_resume(self) -> Resume:
        """
        Get the current parsed resume.

        If no resume exists, return an empty valid Resume object.
        """

        data = resume_repository.get()

        return Resume.model_validate(data)

    def save_resume(self, data: Dict[str, Any]) -> Resume:
        """
        Validate and save a complete parsed resume.
        """

        resume = Resume.model_validate(data)

        resume_repository.save(
            resume.model_dump()
        )

        return resume

    def update_resume(
        self,
        updates: Dict[str, Any]
    ) -> Resume:
        """
        Update the existing resume.
        """

        current = resume_repository.get()

        updated = {
            **current,
            **updates,
        }

        resume = Resume.model_validate(updated)

        resume_repository.save(
            resume.model_dump()
        )

        return resume

    def clear_resume(self) -> None:
        """Clear the stored parsed resume."""

        resume_repository.save({})


# Shared service instance
resume_service = ResumeService()