"""
LinkedIn Job Search Service

Responsibilities:
- Use the shared Selenium browser.
- Search LinkedIn Jobs.
- Extract visible job cards.
- Detect Easy Apply conservatively.
- Save collected jobs using JobRepository.

This module DOES NOT:
- Click Apply.
- Submit applications.
- Automate external application websites.
"""

import time
from datetime import datetime
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from backend.linkedin.browser import linkedin_browser
from backend.storage.repositories import job_repository
from backend.config.settings import (
    LINKEDIN_JOBS_URL,
    ELEMENT_WAIT_TIMEOUT,
    ACTION_DELAY,
    MAX_JOBS_TO_COLLECT,
)


class LinkedInJobSearchService:
    """Search LinkedIn Jobs and extract job cards."""

    def __init__(self):
        self.browser = linkedin_browser

    # =====================================================================
    # SEARCH URL
    # =====================================================================

    def build_search_url(
        self,
        keywords: str,
        location: str = "",
    ) -> str:
        """Build a LinkedIn Jobs search URL."""

        url = f"{LINKEDIN_JOBS_URL}search/"

        params = [
            f"keywords={quote_plus(keywords)}",
        ]

        if location:
            params.append(
                f"location={quote_plus(location)}"
            )

        return url + "?" + "&".join(params)

    # =====================================================================
    # SEARCH
    # =====================================================================

    def search(
        self,
        keywords: str,
        location: str = "",
    ):
        """Open LinkedIn Jobs with the requested search."""

        driver = self.browser.start()

        url = self.build_search_url(
            keywords=keywords,
            location=location,
        )

        print()
        print("Opening LinkedIn Jobs:")
        print(url)
        print()

        self.browser.open(url)

        time.sleep(ACTION_DELAY)

        return driver

    # =====================================================================
    # FIND JOB CARDS
    # =====================================================================

    def find_job_cards(self):
        """Find visible LinkedIn job cards."""

        driver = self.browser.driver

        if not driver:
            return []

        selectors = [
            "li.jobs-search-results__list-item",
            "div.job-card-container",
            "div.base-card",
            "li[data-occludable-job-id]",
        ]

        for selector in selectors:

            try:
                cards = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                visible_cards = [
                    card
                    for card in cards
                    if card.is_displayed()
                ]

                if visible_cards:
                    return visible_cards

            except Exception:
                continue

        return []

    # =====================================================================
    # SAFE TEXT
    # =====================================================================

    def safe_text(
        self,
        element,
        selectors,
    ) -> str:
        """Get text from the first matching child element."""

        for selector in selectors:

            try:
                child = element.find_element(
                    By.CSS_SELECTOR,
                    selector,
                )

                text = child.text.strip()

                if text:
                    return text

            except Exception:
                continue

        return ""

    # =====================================================================
    # JOB ID
    # =====================================================================

    def extract_job_id(self, card) -> str:
        """Extract LinkedIn's job ID."""

        selectors = [
            "[data-job-id]",
            "[data-occludable-job-id]",
            "a[href*='/jobs/view/']",
        ]

        for selector in selectors:

            try:
                element = card.find_element(
                    By.CSS_SELECTOR,
                    selector,
                )

                job_id = (
                    element.get_attribute("data-job-id")
                    or element.get_attribute(
                        "data-occludable-job-id"
                    )
                )

                if job_id:
                    return job_id.strip()

                href = element.get_attribute("href")

                if href and "/jobs/view/" in href:

                    job_part = href.split(
                        "/jobs/view/",
                        1,
                    )[1]

                    job_id = (
                        job_part
                        .split("/", 1)[0]
                        .split("?", 1)[0]
                    )

                    if job_id:
                        return job_id

            except Exception:
                continue

        return ""

    # =====================================================================
    # JOB URL
    # =====================================================================

    def extract_job_url(self, card) -> str:
        """Extract LinkedIn job URL."""

        selectors = [
            "a[href*='/jobs/view/']",
            "a.base-card__full-link",
            "a.job-card-list__title",
        ]

        for selector in selectors:

            try:
                element = card.find_element(
                    By.CSS_SELECTOR,
                    selector,
                )

                href = element.get_attribute("href")

                if href:
                    return href.split("?")[0]

            except Exception:
                continue

        return ""

    # =====================================================================
    # EASY APPLY
    # =====================================================================

    def detect_easy_apply(self, card) -> bool:
        """
        Detect Easy Apply conservatively.

        Only an explicit Easy Apply indicator is accepted.
        Normal Apply is NOT treated as Easy Apply.
        """

        try:

            text = card.text.lower()

            return "easy apply" in text

        except Exception:
            return False

    # =====================================================================
    # EXTRACT ONE JOB
    # =====================================================================

    def extract_job(self, card) -> dict:
        """Convert one LinkedIn job card into structured data."""

        title = self.safe_text(
            card,
            [
                "a.job-card-list__title",
                "a.base-search-card__title",
                "h3",
                "a[href*='/jobs/view/']",
            ],
        )

        company = self.safe_text(
            card,
            [
                "h4",
                "a.job-card-container__company-name",
                "a.base-search-card__subtitle",
            ],
        )

        location = self.safe_text(
            card,
            [
                "div.job-card-container__metadata-wrapper",
                "span.job-search-card__location",
                "div.base-search-card__metadata",
            ],
        )

        job_id = self.extract_job_id(card)
        job_url = self.extract_job_url(card)
        easy_apply = self.detect_easy_apply(card)

        try:
            card_text = card.text.strip()
        except Exception:
            card_text = ""

        # Use URL as fallback ID when LinkedIn does not expose
        # the numeric job ID in the card.
        record_id = job_id or job_url

        return {
            "id": record_id,
            "linkedin_job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "description_preview": card_text,
            "skills": [],
            "requirements": [],
            "employment_type": "",
            "experience_level": "",
            "apply_type": (
                "EASY_APPLY"
                if easy_apply
                else "UNKNOWN"
            ),
            "easy_apply": easy_apply,
            "source": "linkedin",
            "collected_at": datetime.now().isoformat(),
        }

    # =====================================================================
    # COLLECT
    # =====================================================================

    def collect_jobs(
        self,
        keywords: str,
        location: str = "",
        max_jobs: int = None,
    ) -> list:
        """Search LinkedIn and extract visible jobs."""

        if max_jobs is None:
            max_jobs = MAX_JOBS_TO_COLLECT

        self.search(
            keywords=keywords,
            location=location,
        )

        driver = self.browser.driver

        print("Waiting for LinkedIn job results...")

        try:

            WebDriverWait(
                driver,
                ELEMENT_WAIT_TIMEOUT,
            ).until(
                lambda d: len(
                    self.find_job_cards()
                ) > 0
            )

        except Exception:

            print()
            print("⚠ No LinkedIn job cards detected.")
            print("Current URL:")
            print(self.browser.current_url())
            print()

            return []

        time.sleep(ACTION_DELAY)

        cards = self.find_job_cards()

        print(
            f"✓ Found {len(cards)} visible job cards"
        )
        print()

        jobs = []
        seen_ids = set()

        for card in cards:

            if len(jobs) >= max_jobs:
                break

            try:

                job = self.extract_job(card)

                unique_id = (
                    job.get("linkedin_job_id")
                    or job.get("url")
                    or job.get("title")
                )

                if not unique_id:
                    continue

                if unique_id in seen_ids:
                    continue

                seen_ids.add(unique_id)

                jobs.append(job)

            except Exception as exc:

                print(
                    "⚠ Could not extract one job:",
                    exc,
                )

        return jobs

    # =====================================================================
    # SAVE
    # =====================================================================

    def save_jobs(self, jobs: list) -> list:
        """Save jobs using the existing JobRepository interface."""

        saved = []

        for job in jobs:

            try:

                job_id = job.get("id")

                if not job_id:
                    continue

                existing = job_repository.get_by_id(
                    job_id
                )

                if existing:

                    job_repository.update(
                        job_id,
                        job,
                    )

                else:

                    job_repository.save(
                        job
                    )

                saved.append(job)

            except Exception as exc:

                print(
                    "⚠ Could not save job "
                    f"{job.get('title', '')}: {exc}"
                )

        return saved

    # =====================================================================
    # SEARCH + SAVE
    # =====================================================================

    def search_and_save(
        self,
        keywords: str,
        location: str = "",
        max_jobs: int = None,
    ) -> list:
        """
        Search LinkedIn, extract jobs, and save them.

        No application actions are performed here.
        """

        jobs = self.collect_jobs(
            keywords=keywords,
            location=location,
            max_jobs=max_jobs,
        )

        if jobs:
            self.save_jobs(jobs)

        return jobs


# =========================================================================
# SHARED SERVICE
# =========================================================================

linkedin_job_search_service = LinkedInJobSearchService()