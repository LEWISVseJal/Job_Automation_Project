"""
LinkedIn browser manager.

This module owns the Selenium Chrome session.

Important:
- Uses the project's persistent Chrome profile.
- Runs Chrome visibly.
- Does NOT use the user's normal Chrome profile.
- Keeps one browser session for the complete automation run.
"""

import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from backend.config.settings import (
    CHROME_USER_DATA_DIR,
    CHROME_PROFILE_NAME,
    HEADLESS,
    PAGE_LOAD_TIMEOUT,
)


class LinkedInBrowser:
    """
    Persistent Selenium browser used by the automation pipeline.
    """

    def __init__(self):
        self.driver = None

    # ---------------------------------------------------------------
    # START
    # ---------------------------------------------------------------

    def start(self):
        """
        Start Chrome using the project's persistent profile.
        """

        if self.driver is not None:
            return self.driver

        options = Options()

        options.add_argument(
            f"--user-data-dir={CHROME_USER_DATA_DIR}"
        )

        options.add_argument(
            f"--profile-directory={CHROME_PROFILE_NAME}"
        )

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        if HEADLESS:
            options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(
            options=options
        )

        self.driver.set_page_load_timeout(
            PAGE_LOAD_TIMEOUT
        )

        return self.driver

    # ---------------------------------------------------------------
    # OPEN
    # ---------------------------------------------------------------

    def open(self, url: str):
        """
        Open a URL in the active browser.
        """

        if not self.driver:
            self.start()

        try:
            self.driver.get(url)

        except WebDriverException:
            # LinkedIn pages can continue loading after a
            # Selenium timeout. We leave the browser open.
            pass

        time.sleep(1)

    # ---------------------------------------------------------------
    # CURRENT URL
    # ---------------------------------------------------------------

    def current_url(self) -> str:
        """
        Return the current browser URL.
        """

        if not self.driver:
            return ""

        try:
            return self.driver.current_url

        except Exception:
            return ""

    # ---------------------------------------------------------------
    # CLOSE
    # ---------------------------------------------------------------

    def close(self):
        """
        Close the Selenium session.
        """

        if self.driver:

            try:
                self.driver.quit()

            except Exception:
                pass

            finally:
                self.driver = None


# Shared browser manager
linkedin_browser = LinkedInBrowser()