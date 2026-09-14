"""
Profile service.

Handles business logic related to the candidate profile.

Flow:

API
 ↓
ProfileService
 ↓
Profile schema
 ↓
ProfileRepository
 ↓
profile.json
"""

from typing import Any, Dict

from backend.schemas.profile import Profile
from backend.storage.repositories import profile_repository


class ProfileService:
    """Business logic for candidate profile management."""

    def get_profile(self) -> Profile:
        """
        Get the current candidate profile.

        If no profile exists, return an empty valid Profile object.
        """

        data = profile_repository.get()

        return Profile.model_validate(data)

    def save_profile(self, data: Dict[str, Any]) -> Profile:
        """
        Validate and save a complete profile.
        """

        profile = Profile.model_validate(data)

        profile_repository.save(
            profile.model_dump()
        )

        return profile

    def update_profile(
        self,
        updates: Dict[str, Any]
    ) -> Profile:
        """
        Update the existing profile.

        Nested profile sections are handled separately so that
        updating preferences does not accidentally remove contact
        or professional information.
        """

        current = profile_repository.get()

        updated = {
            **current,
            **updates,
        }

        profile = Profile.model_validate(updated)

        profile_repository.save(
            profile.model_dump()
        )

        return profile

    def clear_profile(self) -> None:
        """Clear the stored candidate profile."""

        profile_repository.save({})


# Shared service instance
profile_service = ProfileService()