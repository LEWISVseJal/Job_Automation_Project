"""
Repository layer for Job Automation.

This file provides clean access to the JSON storage layer.

Architecture:

    Services
        ↓
    Repositories
        ↓
    JSONStore
        ↓
    JSON files

The rest of the application should use these repositories
instead of directly reading/writing JSON files.
"""

from typing import Any, Dict, List, Optional

from backend.storage.json_store import storage


# ============================================================
# JOB REPOSITORY
# ============================================================

class JobRepository:
    """Repository for jobs.json."""

    STORAGE_NAME = "jobs"

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all stored jobs."""
        return storage.get_all(self.STORAGE_NAME)

    def get_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find a job by its ID."""
        return storage.find_by_id(
            self.STORAGE_NAME,
            job_id
        )

    def save(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new job."""
        return storage.append(
            self.STORAGE_NAME,
            job
        )

    def update(
        self,
        job_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing job."""
        return storage.update_by_id(
            self.STORAGE_NAME,
            job_id,
            updates
        )

    def delete(self, job_id: str) -> bool:
        """Delete a job by ID."""
        return storage.delete_by_id(
            self.STORAGE_NAME,
            job_id
        )

    def count(self) -> int:
        """Return the number of stored jobs."""
        return len(self.get_all())


# ============================================================
# JOB MATCH REPOSITORY
# ============================================================

class JobMatchRepository:
    """Repository for job_matches.json."""

    STORAGE_NAME = "job_matches"

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all job matches."""
        return storage.get_all(self.STORAGE_NAME)

    def get_by_id(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Find a match by its ID."""
        return storage.find_by_id(
            self.STORAGE_NAME,
            match_id
        )

    def save(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new job match."""
        return storage.append(
            self.STORAGE_NAME,
            match
        )

    def update(
        self,
        match_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing job match."""
        return storage.update_by_id(
            self.STORAGE_NAME,
            match_id,
            updates
        )

    def delete(self, match_id: str) -> bool:
        """Delete a job match by ID."""
        return storage.delete_by_id(
            self.STORAGE_NAME,
            match_id
        )

    def count(self) -> int:
        """Return the number of stored matches."""
        return len(self.get_all())


# ============================================================
# APPLICATION REPOSITORY
# ============================================================

class ApplicationRepository:
    """Repository for applications.json."""

    STORAGE_NAME = "applications"

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all applications."""
        return storage.get_all(self.STORAGE_NAME)

    def get_by_id(
        self,
        application_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find an application by its ID."""
        return storage.find_by_id(
            self.STORAGE_NAME,
            application_id
        )

    def save(
        self,
        application: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save a new application."""
        return storage.append(
            self.STORAGE_NAME,
            application
        )

    def update(
        self,
        application_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing application."""
        return storage.update_by_id(
            self.STORAGE_NAME,
            application_id,
            updates
        )

    def delete(self, application_id: str) -> bool:
        """Delete an application by ID."""
        return storage.delete_by_id(
            self.STORAGE_NAME,
            application_id
        )

    def count(self) -> int:
        """Return the number of applications."""
        return len(self.get_all())


# ============================================================
# PROFILE REPOSITORY
# ============================================================

class ProfileRepository:
    """Repository for profile.json."""

    STORAGE_NAME = "profile"

    def get(self) -> Dict[str, Any]:
        """Return the stored profile."""
        data = storage.read(self.STORAGE_NAME)

        if not isinstance(data, dict):
            return {}

        return data

    def save(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Replace the current profile."""
        storage.write(
            self.STORAGE_NAME,
            profile
        )

        return profile

    def update(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update fields in the current profile."""
        profile = self.get()

        profile.update(updates)

        self.save(profile)

        return profile


# ============================================================
# RESUME REPOSITORY
# ============================================================

class ResumeRepository:
    """Repository for resume.json."""

    STORAGE_NAME = "resume"

    def get(self) -> Dict[str, Any]:
        """Return the parsed resume."""
        data = storage.read(self.STORAGE_NAME)

        if not isinstance(data, dict):
            return {}

        return data

    def save(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Replace the current parsed resume."""
        storage.write(
            self.STORAGE_NAME,
            resume
        )

        return resume

    def update(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update fields in the parsed resume."""
        resume = self.get()

        resume.update(updates)

        self.save(resume)

        return resume


# ============================================================
# LINKEDIN SESSION REPOSITORY
# ============================================================

class LinkedInSessionRepository:
    """Repository for linkedin_session.json."""

    STORAGE_NAME = "linkedin_session"

    def get(self) -> Dict[str, Any]:
        """Return the LinkedIn session information."""
        data = storage.read(self.STORAGE_NAME)

        if not isinstance(data, dict):
            return {}

        return data

    def save(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Replace the stored LinkedIn session information."""
        storage.write(
            self.STORAGE_NAME,
            session_data
        )

        return session_data

    def update(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update LinkedIn session information."""
        session_data = self.get()

        session_data.update(updates)

        self.save(session_data)

        return session_data

    def clear(self) -> None:
        """Clear the stored LinkedIn session information."""
        storage.write(
            self.STORAGE_NAME,
            {}
        )


# ============================================================
# SETTINGS REPOSITORY
# ============================================================

class SettingsRepository:
    """Repository for settings.json."""

    STORAGE_NAME = "settings"

    def get(self) -> Dict[str, Any]:
        """Return application settings."""
        data = storage.read(self.STORAGE_NAME)

        if not isinstance(data, dict):
            return {}

        return data

    def save(
        self,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Replace application settings."""
        storage.write(
            self.STORAGE_NAME,
            settings
        )

        return settings

    def update(
        self,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update application settings."""
        settings = self.get()

        settings.update(updates)

        self.save(settings)

        return settings


# ============================================================
# SHARED REPOSITORY INSTANCES
# ============================================================

job_repository = JobRepository()

job_match_repository = JobMatchRepository()

application_repository = ApplicationRepository()

profile_repository = ProfileRepository()

resume_repository = ResumeRepository()

linkedin_session_repository = LinkedInSessionRepository()

settings_repository = SettingsRepository()