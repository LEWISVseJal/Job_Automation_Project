"""
LinkedIn session service.

Responsible for:
- Opening LinkedIn
- Checking whether the user is logged in
- Saving session status to JSON
- Reusing the same Selenium browser session
"""

import time
from datetime import datetime

from selenium.webdriver.common.by import By

from backend.config.settings import (
    LINKEDIN_URL,
    ACTION_DELAY,
)

from backend.storage.repositories import (
    linkedin_session_repository,
)

from backend.linkedin.browser import linkedin_browser


class LinkedInSessionService:
    """Manage LinkedIn login/session state."""

    def __init__(self):
        self.browser = linkedin_browser

    # -------------------------------------------------------------------------
    # OPEN LINKEDIN
    # -------------------------------------------------------------------------

    def open_linkedin(self):
        """Open LinkedIn using the shared Selenium browser."""

        driver = self.browser.start()

        self.browser.open(LINKEDIN_URL)

        time.sleep(ACTION_DELAY)

        return driver

    # -------------------------------------------------------------------------
    # LOGIN DETECTION
    # -------------------------------------------------------------------------

    def is_logged_in(self):
        """
        Detect whether LinkedIn appears to be logged in.

        Uses multiple signals because LinkedIn's DOM can change.
        """

        driver = self.browser.driver

        if not driver:
            return False

        current_url = self.browser.current_url().lower()

        # -------------------------------------------------------------
        # URL-BASED CHECK
        # -------------------------------------------------------------

        login_url_parts = [
            "/login",
            "/signup",
            "/checkpoint",
            "/uas/login",
        ]

        if any(part in current_url for part in login_url_parts):
            return False

        # -------------------------------------------------------------
        # LOGGED-IN NAVIGATION ELEMENTS
        # -------------------------------------------------------------

        selectors = [
            "a[href*='/feed/']",
            "a[href*='/mynetwork/']",
            "a[href*='/messaging/']",
            "a[href*='/notifications/']",
            "a[href*='/jobs/']",
            "button[aria-label*='Me']",
            "button[aria-label*='Account']",
        ]

        for selector in selectors:

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                if elements:
                    return True

            except Exception:
                continue

        # -------------------------------------------------------------
        # PAGE TEXT CHECK
        # -------------------------------------------------------------

        try:

            page_text = driver.find_element(
                By.TAG_NAME,
                "body",
            ).text.lower()

            logged_in_indicators = [
                "home",
                "my network",
                "jobs",
                "messaging",
                "notifications",
            ]

            matches = sum(
                indicator in page_text
                for indicator in logged_in_indicators
            )

            if matches >= 2:
                return True

        except Exception:
            pass

        return False

    # -------------------------------------------------------------------------
    # SESSION STATUS
    # -------------------------------------------------------------------------

    def get_session_status(self):
        """Build the current LinkedIn session status."""

        logged_in = self.is_logged_in()

        return {
            "id": "linkedin",
            "logged_in": logged_in,
            "url": self.browser.current_url(),
            "checked_at": datetime.now().isoformat(),
        }

    # -------------------------------------------------------------------------
    # SAVE SESSION STATUS
    # -------------------------------------------------------------------------

    def save_session_status(self):
        """
        Save the current session status.

        The repository already provides save/update-style methods,
        so we use the repository's existing interface instead of
        assuming a create() method exists.
        """

        status = self.get_session_status()

        existing = linkedin_session_repository.get()

        if existing:
            linkedin_session_repository.update(
                status
            )
        else:
            linkedin_session_repository.save(
                status
            )

        return status

    # -------------------------------------------------------------------------
    # CHECK SESSION
    # -------------------------------------------------------------------------

    def check_session(self):
        """
        Open LinkedIn and check the current login state.
        """

        self.open_linkedin()

        time.sleep(2)

        status = self.save_session_status()

        return status


# =============================================================================
# SHARED SERVICE INSTANCE
# =============================================================================

linkedin_session_service = LinkedInSessionService()