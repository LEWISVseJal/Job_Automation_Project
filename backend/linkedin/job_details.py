"""
LinkedIn Job Details Service

Responsibilities:
- Open LinkedIn job detail pages using the shared Selenium browser.
- Extract detailed job information.
- Clean LinkedIn UI text from job titles.
- Extract company, location, description and metadata.
- Detect Easy Apply conservatively.
- Update existing jobs in data/jobs.json.

This module DOES NOT:
- Click Apply.
- Submit applications.
- Automate external application websites.
"""

import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from backend.linkedin.browser import linkedin_browser
from backend.storage.repositories import job_repository
from backend.config.settings import (
    ELEMENT_WAIT_TIMEOUT,
    ACTION_DELAY,
)


class LinkedInJobDetailsService:
    """
    Extract detailed information from a LinkedIn job page.
    """

    def __init__(self):
        self.browser = linkedin_browser

    # ------------------------------------------------------------------
    # BASIC HELPERS
    # ------------------------------------------------------------------

    def safe_find(self, selectors):
        """
        Return the first matching visible element.
        """

        driver = self.browser.driver

        if not driver:
            return None

        for selector in selectors:

            try:
                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                for element in elements:

                    try:
                        if element.is_displayed():
                            return element
                    except Exception:
                        continue

            except Exception:
                continue

        return None

    def safe_text(self, selectors):
        """
        Return text from the first matching element.
        """

        element = self.safe_find(selectors)

        if not element:
            return ""

        try:
            return element.text.strip()
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------------

    def clean_title(self, title: str) -> str:
        """
        Clean LinkedIn UI text from the job title.
        """

        if not title:
            return ""

        title = title.strip()

        # Remove common LinkedIn verification suffix.
        title = re.sub(
            r"\s+with verification\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Remove duplicate title caused by nested LinkedIn elements.
        lines = [
            line.strip()
            for line in title.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        # If the first two lines are identical, keep only one.
        if len(lines) >= 2:
            if lines[0].lower() == lines[1].lower():
                return lines[0]

        return lines[0]

    def extract_title(self):
        """
        Extract the job title from the detail page.
        """

        selectors = [
            "h1.top-card-layout__title",
            "h1.top-card__title",
            "h1.job-details-jobs-unified-top-card__job-title",
            "h1",
        ]

        title = self.safe_text(selectors)

        return self.clean_title(title)

    # ------------------------------------------------------------------
    # COMPANY
    # ------------------------------------------------------------------

    def extract_company(self):
        """
        Extract company name.
        """

        selectors = [
            "a.topcard__org-name-link",
            "a.top-card-layout__card a[href*='/company/']",
            "div.job-details-jobs-unified-top-card__company-name a",
            "div.job-details-jobs-unified-top-card__company-name",
            "a[data-tracking-control-name='public_jobs_topcard-org-name']",
            "a[href*='/company/']",
        ]

        company = self.safe_text(selectors)

        if company:
            return company

        # Fallback:
        # Inspect links on the page for company URLs.
        driver = self.browser.driver

        if driver:

            try:

                links = driver.find_elements(
                    By.CSS_SELECTOR,
                    "a[href*='/company/']",
                )

                for link in links:

                    try:
                        text = link.text.strip()

                        if text:
                            return text

                    except Exception:
                        continue

            except Exception:
                pass

        return ""

    # ------------------------------------------------------------------
    # LOCATION
    # ------------------------------------------------------------------

    def extract_location(self):
        """
        Extract job location.
        """

        selectors = [
            "span.topcard__flavor--bullet",
            "span.top-card-layout__first-subline span",
            "div.job-details-jobs-unified-top-card__primary-description-container span",
            "div.job-details-jobs-unified-top-card__primary-description-container",
            "span.jobs-unified-top-card__bullet",
            "span.jobs-unified-top-card__workplace-type",
        ]

        location = self.safe_text(selectors)

        if not location:
            return ""

        # Clean multiple spaces/newlines.
        location = re.sub(
            r"\s+",
            " ",
            location,
        ).strip()

        return location

    # ------------------------------------------------------------------
    # JOB METADATA
    # ------------------------------------------------------------------

    def extract_metadata(self):
        """
        Extract employment type and experience level
        from the job detail page.
        """

        result = {
            "employment_type": "",
            "experience_level": "",
        }

        driver = self.browser.driver

        if not driver:
            return result

        # --------------------------------------------------------------
        # Primary metadata section
        # --------------------------------------------------------------

        selectors = [
            "li.description__job-criteria-item",
            "li.jobs-description-details__list-item",
            "ul.description__job-criteria-list li",
            "ul.jobs-unified-top-card__job-insight",
        ]

        items = []

        for selector in selectors:

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                if elements:
                    items.extend(elements)

            except Exception:
                continue

        for item in items:

            try:

                text = item.text.strip()

                if not text:
                    continue

                lower = text.lower()

                # Employment type
                if (
                    "employment type" in lower
                    or "full-time" in lower
                    or "part-time" in lower
                    or "contract" in lower
                    or "internship" in lower
                    or "temporary" in lower
                    or "volunteer" in lower
                ):

                    value = self.extract_metadata_value(
                        text
                    )

                    if value:
                        result["employment_type"] = value

                # Experience level
                if (
                    "experience level" in lower
                    or "entry level" in lower
                    or "associate" in lower
                    or "mid-senior level" in lower
                    or "director" in lower
                    or "executive" in lower
                ):

                    value = self.extract_metadata_value(
                        text
                    )

                    if value:
                        result["experience_level"] = value

            except Exception:
                continue

        return result

    def extract_metadata_value(self, text: str):
        """
        Extract value from LinkedIn metadata text.

        Example:
            Employment type
            Full-time

        returns:
            Full-time
        """

        if not text:
            return ""

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if len(lines) >= 2:
            return lines[-1]

        # Handle single-line metadata.
        patterns = [
            r"employment type\s*[:\-]?\s*(.+)",
            r"experience level\s*[:\-]?\s*(.+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(1).strip()

        return ""

    # ------------------------------------------------------------------
    # DESCRIPTION
    # ------------------------------------------------------------------

    def extract_description(self):
        """
        Extract complete visible job description.
        """

        selectors = [
            "div.jobs-description__content",
            "div.jobs-box__html-content",
            "div.jobs-description-content__text",
            "div.jobs-description",
            "section.jobs-description",
            "article.jobs-description__container",
        ]

        description = self.safe_text(selectors)

        if description:
            return description

        # Fallback for current LinkedIn unified layout.
        driver = self.browser.driver

        if driver:

            try:

                elements = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'description')]",
                )

                candidates = []

                for element in elements:

                    try:

                        if not element.is_displayed():
                            continue

                        text = element.text.strip()

                        if len(text) > 200:
                            candidates.append(text)

                    except Exception:
                        continue

                if candidates:
                    return max(
                        candidates,
                        key=len,
                    )

            except Exception:
                pass

        return ""

    # ------------------------------------------------------------------
    # SKILLS
    # ------------------------------------------------------------------

    def extract_skills(self):
        """
        Extract LinkedIn skill suggestions when available.
        """

        driver = self.browser.driver

        if not driver:
            return []

        skills = []

        selectors = [
            "a.job-details-how-you-match__skills-item-subtitle",
            "div.job-details-how-you-match__skills-item",
            "a[href*='/skills/']",
            "span.job-details-how-you-match__skills-item-subtitle",
        ]

        for selector in selectors:

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                for element in elements:

                    try:

                        text = element.text.strip()

                        if text:
                            skills.append(text)

                    except Exception:
                        continue

            except Exception:
                continue

        # Remove duplicates while preserving order.
        unique_skills = []

        seen = set()

        for skill in skills:

            key = skill.lower()

            if key not in seen:

                seen.add(key)
                unique_skills.append(skill)

        return unique_skills

    # ------------------------------------------------------------------
    # EASY APPLY
    # ------------------------------------------------------------------

    def detect_easy_apply(self):
        """
        Detect Easy Apply on the job detail page.

        Only explicit Easy Apply text is accepted.
        """

        driver = self.browser.driver

        if not driver:
            return False

        selectors = [
            "button.jobs-apply-button",
            "button[aria-label*='Easy Apply']",
            "button[aria-label*='easy apply']",
            "button",
            "a",
        ]

        for selector in selectors:

            try:

                elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                for element in elements:

                    try:

                        if not element.is_displayed():
                            continue

                        text = (
                            element.text
                            or element.get_attribute("aria-label")
                            or ""
                        ).strip().lower()

                        if "easy apply" in text:
                            return True

                    except Exception:
                        continue

            except Exception:
                continue

        return False

    # ------------------------------------------------------------------
    # JOB ID
    # ------------------------------------------------------------------

    def extract_job_id(self, url: str = ""):
        """
        Extract LinkedIn job ID from URL.
        """

        if not url:
            try:
                url = self.browser.current_url()
            except Exception:
                url = ""

        if not url:
            return ""

        match = re.search(
            r"/jobs/view/(\d+)",
            url,
        )

        if match:
            return match.group(1)

        return ""

    # ------------------------------------------------------------------
    # COMPLETE JOB EXTRACTION
    # ------------------------------------------------------------------

    def extract_current_job(self, original_job=None):
        """
        Extract all available details from the currently
        opened LinkedIn job page.
        """

        current_url = self.browser.current_url()

        job_id = self.extract_job_id(
            current_url
        )

        title = self.extract_title()
        company = self.extract_company()
        location = self.extract_location()

        metadata = self.extract_metadata()

        description = self.extract_description()

        skills = self.extract_skills()

        easy_apply = self.detect_easy_apply()

        # Preserve original job information when necessary.
        if original_job:

            if not job_id:
                job_id = original_job.get(
                    "linkedin_job_id",
                    "",
                )

            if not title:
                title = original_job.get(
                    "title",
                    "",
                )

            if not company:
                company = original_job.get(
                    "company",
                    "",
                )

            if not location:
                location = original_job.get(
                    "location",
                    "",
                )

        return {
            "id": job_id,
            "linkedin_job_id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": current_url,
            "description": description,
            "description_preview": (
                description[:500]
                if description
                else ""
            ),
            "skills": skills,
            "requirements": [],
            "employment_type": metadata[
                "employment_type"
            ],
            "experience_level": metadata[
                "experience_level"
            ],
            "apply_type": (
                "EASY_APPLY"
                if easy_apply
                else "UNKNOWN"
            ),
            "easy_apply": easy_apply,
            "source": "linkedin",
            "details_extracted_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # OPEN JOB
    # ------------------------------------------------------------------

    def open_job(self, url: str):
        """
        Open one LinkedIn job URL.
        """

        if not url:
            return False

        print()
        print("Opening job:")
        print(url)

        self.browser.open(url)

        driver = self.browser.driver

        if not driver:
            return False

        try:

            WebDriverWait(
                driver,
                ELEMENT_WAIT_TIMEOUT,
            ).until(
                lambda d: self.extract_title() != ""
            )

        except Exception:
            # Page may still contain useful information.
            pass

        time.sleep(ACTION_DELAY)

        return True

    # ------------------------------------------------------------------
    # UPDATE ONE JOB
    # ------------------------------------------------------------------

    def update_job(self, job):
        """
        Update one existing job in jobs.json.
        """

        job_id = (
            job.get("linkedin_job_id")
            or job.get("id")
        )

        if not job_id:
            return False

        existing = job_repository.get_by_id(
            job_id
        )

        if not existing:
            return False

        job_repository.update(
            job_id,
            job,
        )

        return True

    # ------------------------------------------------------------------
    # PROCESS SAVED JOBS
    # ------------------------------------------------------------------

    def process_saved_jobs(self, max_jobs=5):
        """
        Open and enrich saved jobs.
        """

        jobs = job_repository.get_all()

        if not jobs:
            print()
            print("⚠ No jobs found in data/jobs.json")
            print()
            return []

        jobs = jobs[:max_jobs]

        enriched_jobs = []

        print()
        print("=" * 80)
        print("LINKEDIN JOB DETAILS EXTRACTION")
        print("=" * 80)
        print()

        print(
            f"Processing {len(jobs)} saved jobs..."
        )
        print()

        for index, original_job in enumerate(
            jobs,
            start=1,
        ):

            print("-" * 80)
            print(
                f"JOB {index}/{len(jobs)}"
            )
            print("-" * 80)

            url = original_job.get(
                "url",
                "",
            )

            if not url:

                print("⚠ Job has no URL.")
                print()

                continue

            try:

                if not self.open_job(url):

                    print(
                        "⚠ Could not open job."
                    )
                    print()

                    continue

                job = self.extract_current_job(
                    original_job=original_job
                )

                if not job.get("id"):
                    job["id"] = (
                        original_job.get("id")
                    )

                # Keep original URL if current URL
                # could not be obtained.
                if not job.get("url"):
                    job["url"] = url

                # Update saved record.
                updated = self.update_job(
                    job
                )

                print()
                print(
                    "Title:",
                    job.get("title", ""),
                )

                print(
                    "Company:",
                    job.get("company", ""),
                )

                print(
                    "Location:",
                    job.get("location", ""),
                )

                print(
                    "Employment:",
                    job.get(
                        "employment_type",
                        "",
                    ),
                )

                print(
                    "Experience:",
                    job.get(
                        "experience_level",
                        "",
                    ),
                )

                print(
                    "Easy Apply:",
                    job.get(
                        "easy_apply",
                        False,
                    ),
                )

                print(
                    "Description length:",
                    len(
                        job.get(
                            "description",
                            "",
                        )
                    ),
                )

                print(
                    "Skills:",
                    job.get(
                        "skills",
                        [],
                    ),
                )

                print(
                    "Saved:",
                    updated,
                )

                print()

                enriched_jobs.append(job)

            except Exception as exc:

                print()
                print(
                    "⚠ Error processing job:"
                )
                print(exc)
                print()

        print("=" * 80)
        print("DETAIL EXTRACTION COMPLETE")
        print("=" * 80)
        print()

        print(
            f"Successfully processed: "
            f"{len(enriched_jobs)}"
        )

        print()

        return enriched_jobs


# =========================================================================
# SHARED SERVICE
# =========================================================================

linkedin_job_details_service = LinkedInJobDetailsService()