"""
Central application configuration.

All major settings for Job Automation are kept here.

The rest of the application should import settings from this
file instead of hard-coding paths and values in individual modules.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/config/settings.py
#         ↓
# backend/config
#         ↓
# backend
#         ↓
# project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Main data directory
DATA_DIR = PROJECT_ROOT / "data"

# Resume files
RESUMES_DIR = DATA_DIR / "resumes"

# Persistent Chrome profile
CHROME_PROFILE_DIR = DATA_DIR / "chrome_profile"

# Diagnostics
DIAGNOSTICS_DIR = DATA_DIR / "diagnostics"

SCREENSHOTS_DIR = DIAGNOSTICS_DIR / "screenshots"

HTML_DIR = DIAGNOSTICS_DIR / "html"

LOGS_DIR = DIAGNOSTICS_DIR / "logs"


# ============================================================
# JSON DATA FILES
# ============================================================

PROFILE_FILE = DATA_DIR / "profile.json"

RESUME_FILE = DATA_DIR / "resume.json"

JOBS_FILE = DATA_DIR / "jobs.json"

JOB_MATCHES_FILE = DATA_DIR / "job_matches.json"

APPLICATIONS_FILE = DATA_DIR / "applications.json"

LINKEDIN_SESSION_FILE = DATA_DIR / "linkedin_session.json"

SETTINGS_FILE = DATA_DIR / "settings.json"


# ============================================================
# LINKEDIN
# ============================================================

LINKEDIN_URL = "https://www.linkedin.com/"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/"

# ============================================================
# CHROME / SELENIUM
# ============================================================

# Use a persistent Chrome profile so that LinkedIn login
# can remain available between automation runs.
USE_PERSISTENT_CHROME_PROFILE = True

# Path where the application's Chrome profile will be stored.
CHROME_USER_DATA_DIR = CHROME_PROFILE_DIR

# Chrome profile directory.
#
# IMPORTANT:
# This is our application's own Chrome profile.
# We are NOT using the user's normal Chrome profile.
CHROME_PROFILE_NAME = "Default"

# Keep browser visible while developing/testing.
HEADLESS = False

# Give LinkedIn pages time to load.
PAGE_LOAD_TIMEOUT = 30

# General Selenium wait time.
ELEMENT_WAIT_TIMEOUT = 15

# Small delay between automation actions.
ACTION_DELAY = 1.0


# ============================================================
# JOB SEARCH
# ============================================================

# Maximum number of jobs to process during one run.
MAX_JOBS_TO_PROCESS = 5

# Maximum number of jobs to collect from a search page.
MAX_JOBS_TO_COLLECT = 25

# Number of jobs to keep after matching/ranking.
MAX_MATCHED_JOBS = 20


# ============================================================
# JOB MATCHING
# ============================================================

# Minimum score required for a job to be considered a useful match.
MIN_MATCH_SCORE = 60.0

# Easy Apply jobs receive priority when scores are otherwise similar.
EASY_APPLY_PRIORITY = True

# Matching weights.
#
# Total = 100
MATCH_WEIGHT_TITLE = 20.0
MATCH_WEIGHT_SKILLS = 35.0
MATCH_WEIGHT_EXPERIENCE = 20.0
MATCH_WEIGHT_PROJECTS = 10.0
MATCH_WEIGHT_EDUCATION = 5.0
MATCH_WEIGHT_EXPERIENCE_LEVEL = 5.0
MATCH_WEIGHT_PREFERENCES = 5.0


# ============================================================
# EASY APPLY
# ============================================================

# Easy Apply is the primary automation workflow.
ENABLE_EASY_APPLY = True

# Generic LinkedIn Apply is allowed to be clicked so that
# the destination can be inspected.
ENABLE_GENERIC_APPLY_CLICK = True

# External applications must NOT be automatically completed.
ENABLE_EXTERNAL_APPLICATION_AUTOMATION = False

# Application automation can fill safe fields and move through
# the form, but must stop before final submission.
STOP_BEFORE_FINAL_SUBMIT = True

# Never automatically click the final application submission.
ALLOW_FINAL_SUBMIT = False


# ============================================================
# FORM AUTOMATION
# ============================================================

# Upload resume when an Easy Apply form requests one.
ENABLE_RESUME_UPLOAD = True

# Fill common/safe fields automatically.
ENABLE_SAFE_FIELD_FILLING = True

# Continue through application steps.
ENABLE_NEXT_BUTTON = True

# Allow review-page detection.
ENABLE_REVIEW_DETECTION = True


# ============================================================
# SAFETY
# ============================================================

# The bot should never submit an application automatically.
SAFETY_STOP_BEFORE_SUBMIT = True

# Save diagnostic information when an automation step fails.
SAVE_DIAGNOSTICS_ON_ERROR = True

# Capture screenshots during important application stages.
CAPTURE_APPLICATION_SCREENSHOTS = True

# Save page HTML when application detection fails.
CAPTURE_FAILED_PAGE_HTML = True

# =========================================================================
# DIAGNOSTICS PATHS
# =========================================================================

DIAGNOSTICS_DIR = DATA_DIR / "diagnostics"

DIAGNOSTICS_SCREENSHOT_DIR = (
    DIAGNOSTICS_DIR / "screenshots"
)

DIAGNOSTICS_HTML_DIR = (
    DIAGNOSTICS_DIR / "html"
)

DIAGNOSTICS_LOG_DIR = (
    DIAGNOSTICS_DIR / "logs"
)


# ============================================================
# LOGGING
# ============================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOGS_DIR / "job_automation.log"


# ============================================================
# APPLICATION STATUS VALUES
# ============================================================

APPLICATION_STATUS_NOT_STARTED = "NOT_STARTED"

APPLICATION_STATUS_PROCESSING = "PROCESSING"

APPLICATION_STATUS_FORM_DETECTED = "FORM_DETECTED"

APPLICATION_STATUS_FORM_FILLED = "FORM_FILLED"

APPLICATION_STATUS_REVIEW_READY = "REVIEW_READY"

APPLICATION_STATUS_STOPPED_BEFORE_SUBMIT = "STOPPED_BEFORE_SUBMIT"

APPLICATION_STATUS_SUBMITTED = "SUBMITTED"

APPLICATION_STATUS_EXTERNAL_APPLICATION = "EXTERNAL_APPLICATION"

APPLICATION_STATUS_FAILED = "FAILED"


# ============================================================
# LINKEDIN APPLY TYPES
# ============================================================

APPLY_TYPE_EASY_APPLY = "EASY_APPLY"

APPLY_TYPE_GENERIC = "GENERIC_APPLY"

APPLY_TYPE_EXTERNAL = "EXTERNAL"

APPLY_TYPE_UNKNOWN = "UNKNOWN"


# ============================================================
# DIRECTORY INITIALIZATION
# ============================================================

def ensure_directories() -> None:
    """
    Create required application directories if they do not exist.
    """

    directories = [
        DATA_DIR,
        RESUMES_DIR,
        CHROME_PROFILE_DIR,
        DIAGNOSTICS_DIR,
        SCREENSHOTS_DIR,
        HTML_DIR,
        LOGS_DIR,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_settings() -> list[str]:
    """
    Validate important configuration values.

    Returns:
        A list of configuration problems.

        An empty list means the configuration is valid.
    """

    errors: list[str] = []

    if not 0 <= MIN_MATCH_SCORE <= 100:
        errors.append(
            "MIN_MATCH_SCORE must be between 0 and 100."
        )

    if MAX_JOBS_TO_PROCESS < 1:
        errors.append(
            "MAX_JOBS_TO_PROCESS must be at least 1."
        )

    if MAX_JOBS_TO_COLLECT < 1:
        errors.append(
            "MAX_JOBS_TO_COLLECT must be at least 1."
        )

    if MAX_MATCHED_JOBS < 1:
        errors.append(
            "MAX_MATCHED_JOBS must be at least 1."
        )

    weights = [
        MATCH_WEIGHT_TITLE,
        MATCH_WEIGHT_SKILLS,
        MATCH_WEIGHT_EXPERIENCE,
        MATCH_WEIGHT_PROJECTS,
        MATCH_WEIGHT_EDUCATION,
        MATCH_WEIGHT_EXPERIENCE_LEVEL,
        MATCH_WEIGHT_PREFERENCES,
    ]

    if sum(weights) != 100:
        errors.append(
            "Job matching weights must add up to 100."
        )

    if not STOP_BEFORE_FINAL_SUBMIT:
        errors.append(
            "STOP_BEFORE_FINAL_SUBMIT must remain True."
        )

    if ALLOW_FINAL_SUBMIT:
        errors.append(
            "ALLOW_FINAL_SUBMIT must remain False."
        )

    if ENABLE_EXTERNAL_APPLICATION_AUTOMATION:
        errors.append(
            "External application automation is disabled "
            "for this project."
        )

    return errors


# ============================================================
# CONFIGURATION SUMMARY
# ============================================================

def get_config_summary() -> dict:
    """
    Return important configuration values in dictionary form.

    Useful for debugging and API endpoints later.
    """

    return {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "resumes_dir": str(RESUMES_DIR),
        "chrome_profile_dir": str(CHROME_PROFILE_DIR),
        "headless": HEADLESS,
        "max_jobs_to_process": MAX_JOBS_TO_PROCESS,
        "max_jobs_to_collect": MAX_JOBS_TO_COLLECT,
        "max_matched_jobs": MAX_MATCHED_JOBS,
        "min_match_score": MIN_MATCH_SCORE,
        "easy_apply_enabled": ENABLE_EASY_APPLY,
        "easy_apply_priority": EASY_APPLY_PRIORITY,
        "generic_apply_click_enabled": ENABLE_GENERIC_APPLY_CLICK,
        "external_application_automation": (
            ENABLE_EXTERNAL_APPLICATION_AUTOMATION
        ),
        "stop_before_final_submit": STOP_BEFORE_FINAL_SUBMIT,
        "allow_final_submit": ALLOW_FINAL_SUBMIT,
        "resume_upload_enabled": ENABLE_RESUME_UPLOAD,
        "safe_field_filling_enabled": ENABLE_SAFE_FIELD_FILLING,
        "next_button_enabled": ENABLE_NEXT_BUTTON,
        "review_detection_enabled": ENABLE_REVIEW_DETECTION,
    }


# ============================================================
# INITIALIZE REQUIRED DIRECTORIES
# ============================================================

ensure_directories()