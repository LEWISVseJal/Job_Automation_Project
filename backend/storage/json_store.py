"""
JSON Storage Engine
===================

Centralized JSON file storage for the Job Automation application.

Responsibilities:
- Create missing JSON files/directories.
- Read JSON safely.
- Write JSON atomically.
- Protect writes with a file lock.
- Handle empty/corrupted JSON files gracefully.
- Provide basic record-level operations.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

from filelock import FileLock


# ---------------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------------

# json_store.py
#     ↓
# backend/storage/
#     ↓
# backend/
#     ↓
# project root
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"


# ---------------------------------------------------------------------------
# DEFAULT JSON FILES
# ---------------------------------------------------------------------------

DEFAULT_FILES = {
    "profile": DATA_DIR / "profile.json",
    "resume": DATA_DIR / "resume.json",
    "jobs": DATA_DIR / "jobs.json",
    "job_matches": DATA_DIR / "job_matches.json",
    "applications": DATA_DIR / "applications.json",
    "linkedin_session": DATA_DIR / "linkedin_session.json",
    "settings": DATA_DIR / "settings.json",
}


# ---------------------------------------------------------------------------
# DEFAULT DATA
# ---------------------------------------------------------------------------

DEFAULT_DATA = {
    "profile": {},
    "resume": {},
    "jobs": [],
    "job_matches": [],
    "applications": [],
    "linkedin_session": {},
    "settings": {},
}


class JSONStorageError(Exception):
    """Base exception for JSON storage errors."""


class JSONStore:
    """
    Safe JSON file storage manager.

    All application services should use this class instead of directly
    opening JSON files.
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_default_files()

    # -----------------------------------------------------------------------
    # INITIALIZATION
    # -----------------------------------------------------------------------

    def _initialize_default_files(self) -> None:
        """
        Create the application's JSON files if they don't exist.
        """

        for name, path in DEFAULT_FILES.items():
            self._ensure_file(
                name=name,
                path=path,
            )

    def _ensure_file(
        self,
        name: str,
        path: Path,
    ) -> None:
        """
        Ensure a JSON file exists and contains valid JSON.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not path.exists():
            self._write_file(
                path,
                DEFAULT_DATA.get(name, {}),
            )
            return

        # If the file exists but is empty, initialize it.
        if path.stat().st_size == 0:
            self._write_file(
                path,
                DEFAULT_DATA.get(name, {}),
            )

    # -----------------------------------------------------------------------
    # PATH HELPERS
    # -----------------------------------------------------------------------

    def get_file_path(self, name: str) -> Path:
        """
        Return the path of a registered JSON storage file.
        """

        if name not in DEFAULT_FILES:
            raise JSONStorageError(
                f"Unknown storage file: {name}"
            )

        return self.data_dir / DEFAULT_FILES[name].name

    def get_lock_path(self, name: str) -> Path:
        """
        Return the lock-file path for a storage file.
        """

        return Path(
            str(self.get_file_path(name)) + ".lock"
        )

    # -----------------------------------------------------------------------
    # LOW-LEVEL READ
    # -----------------------------------------------------------------------

    def _read_file(self, path: Path) -> Any:
        """
        Read and parse a JSON file.
        """

        if not path.exists():
            return {}

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                content = file.read().strip()

            if not content:
                return {}

            return json.loads(content)

        except json.JSONDecodeError as exc:
            raise JSONStorageError(
                f"Invalid JSON in file: {path}"
            ) from exc

        except OSError as exc:
            raise JSONStorageError(
                f"Unable to read JSON file: {path}"
            ) from exc

    # -----------------------------------------------------------------------
    # LOW-LEVEL WRITE
    # -----------------------------------------------------------------------

    def _write_file(
        self,
        path: Path,
        data: Any,
    ) -> None:
        """
        Atomically write JSON data.

        The data is first written to a temporary file and then replaced
        into the destination. This prevents partially-written JSON files.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path: Optional[Path] = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.stem}_",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:

                temporary_path = Path(
                    temporary_file.name
                )

                json.dump(
                    data,
                    temporary_file,
                    indent=4,
                    ensure_ascii=False,
                )

                temporary_file.write("\n")
                temporary_file.flush()

                # Ensure data reaches disk before replacement.
                os.fsync(
                    temporary_file.fileno()
                )

            os.replace(
                temporary_path,
                path,
            )

        except OSError as exc:
            raise JSONStorageError(
                f"Unable to write JSON file: {path}"
            ) from exc

        finally:
            if (
                temporary_path is not None
                and temporary_path.exists()
            ):
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    # -----------------------------------------------------------------------
    # PUBLIC READ
    # -----------------------------------------------------------------------

    def read(self, name: str) -> Any:
        """
        Read a registered JSON file.
        """

        path = self.get_file_path(name)

        return self._read_file(path)

    # -----------------------------------------------------------------------
    # PUBLIC WRITE
    # -----------------------------------------------------------------------

    def write(
        self,
        name: str,
        data: Any,
    ) -> None:
        """
        Safely write data to a registered JSON file.
        """

        path = self.get_file_path(name)
        lock_path = self.get_lock_path(name)

        lock = FileLock(
            str(lock_path),
            timeout=10,
        )

        with lock:
            self._write_file(
                path,
                data,
            )

    # -----------------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------------

    def update(
        self,
        name: str,
        data: Any,
    ) -> Any:
        """
        Replace the contents of a JSON storage file.

        Returns the data that was written.
        """

        self.write(
            name,
            data,
        )

        return data

    # -----------------------------------------------------------------------
    # LIST OPERATIONS
    # -----------------------------------------------------------------------

    def append(
        self,
        name: str,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Append a record to a list-based JSON file.

        Intended for:
        - jobs
        - job_matches
        - applications
        """

        path = self.get_file_path(name)
        lock_path = self.get_lock_path(name)

        lock = FileLock(
            str(lock_path),
            timeout=10,
        )

        with lock:

            data = self._read_file(path)

            if not isinstance(data, list):
                raise JSONStorageError(
                    f"Storage file '{name}' does not contain a list."
                )

            data.append(record)

            self._write_file(
                path,
                data,
            )

        return record

    def get_all(
        self,
        name: str,
    ) -> list[Any]:
        """
        Return all records from a list-based JSON file.
        """

        data = self.read(name)

        if not isinstance(data, list):
            raise JSONStorageError(
                f"Storage file '{name}' does not contain a list."
            )

        return data

    # -----------------------------------------------------------------------
    # FIND
    # -----------------------------------------------------------------------

    def find_by_id(
        self,
        name: str,
        record_id: str,
        id_field: str = "id",
    ) -> Optional[dict[str, Any]]:
        """
        Find one record by ID.
        """

        records = self.get_all(name)

        for record in records:

            if not isinstance(record, dict):
                continue

            if str(record.get(id_field)) == str(record_id):
                return record

        return None

    # -----------------------------------------------------------------------
    # UPDATE RECORD
    # -----------------------------------------------------------------------

    def update_by_id(
        self,
        name: str,
        record_id: str,
        updates: dict[str, Any],
        id_field: str = "id",
    ) -> Optional[dict[str, Any]]:
        """
        Update one record identified by an ID.
        """

        path = self.get_file_path(name)
        lock_path = self.get_lock_path(name)

        lock = FileLock(
            str(lock_path),
            timeout=10,
        )

        with lock:

            records = self._read_file(path)

            if not isinstance(records, list):
                raise JSONStorageError(
                    f"Storage file '{name}' does not contain a list."
                )

            for index, record in enumerate(records):

                if not isinstance(record, dict):
                    continue

                if str(record.get(id_field)) == str(record_id):

                    record.update(updates)

                    records[index] = record

                    self._write_file(
                        path,
                        records,
                    )

                    return record

        return None

    # -----------------------------------------------------------------------
    # DELETE RECORD
    # -----------------------------------------------------------------------

    def delete_by_id(
        self,
        name: str,
        record_id: str,
        id_field: str = "id",
    ) -> bool:
        """
        Delete one record identified by an ID.

        Returns:
            True  -> record deleted
            False -> record not found
        """

        path = self.get_file_path(name)
        lock_path = self.get_lock_path(name)

        lock = FileLock(
            str(lock_path),
            timeout=10,
        )

        with lock:

            records = self._read_file(path)

            if not isinstance(records, list):
                raise JSONStorageError(
                    f"Storage file '{name}' does not contain a list."
                )

            original_length = len(records)

            records = [
                record
                for record in records
                if not (
                    isinstance(record, dict)
                    and str(record.get(id_field))
                    == str(record_id)
                )
            ]

            if len(records) == original_length:
                return False

            self._write_file(
                path,
                records,
            )

            return True


# ---------------------------------------------------------------------------
# SHARED STORAGE INSTANCE
# ---------------------------------------------------------------------------

storage = JSONStore()