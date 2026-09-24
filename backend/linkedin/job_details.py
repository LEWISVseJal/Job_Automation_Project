"""
LinkedIn Job Details Extractor

Responsibilities:
- Open saved LinkedIn jobs
- Extract detailed information from the LinkedIn job page
- Use DOM-based selectors that match the current LinkedIn page
- Detect Easy Apply
- Extract title, company, location, workplace type,
  employment type, experience level, description and skills
- Update jobs.json through the existing job_repository

Safety:
- Does NOT click Apply
- Does NOT open Easy Apply
- Does NOT fill application forms
- Does NOT submit applications
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support.ui import WebDriverWait

from backend.linkedin.session_service import linkedin_session_service
from backend.storage.repositories import job_repository


class LinkedInJobDetailsService:
    """Extract detailed information from individual LinkedIn job pages."""

    def __init__(self):
        self.session_service = linkedin_session_service
        self.browser = self.session_service.browser

    # ================================================================
    # BASIC HELPERS
    # ================================================================

    @property
    def driver(self):
        """Return the active Selenium driver."""
        return self.browser.driver

    def wait_for_page(self, timeout: int = 15) -> bool:
        """Wait until the LinkedIn page is loaded."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script(
                    "return document.readyState"
                )
                in ("interactive", "complete")
            )

            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(
                    driver.find_elements(By.TAG_NAME, "body")
                ) > 0
            )

            return True

        except TimeoutException:
            return False

        except WebDriverException:
            return False

    def clean_whitespace(self, text: Any) -> str:
        """Normalize whitespace while preserving lines."""
        if text is None:
            return ""

        text = str(text).replace("\xa0", " ")

        lines = []

        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()

    def safe_text(self, element) -> str:
        """Safely extract text from a Selenium element."""
        if element is None:
            return ""

        try:
            return self.clean_whitespace(element.text)

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):
            return ""

    def first_element(
        self,
        selectors: List[str],
        timeout: float = 0,
    ):
        """Return the first visible matching element."""

        if timeout > 0:
            end_time = time.time() + timeout

            while time.time() < end_time:
                element = self.first_element(
                    selectors,
                    timeout=0,
                )

                if element is not None:
                    return element

                time.sleep(0.25)

            return None

        for selector in selectors:
            try:
                elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                for element in elements:
                    try:
                        if element.is_displayed():
                            return element
                    except WebDriverException:
                        continue

            except WebDriverException:
                continue

        return None

    def elements(self, selectors: List[str]):
        """Return all elements matching supplied selectors."""

        result = []

        for selector in selectors:
            try:
                result.extend(
                    self.driver.find_elements(
                        By.CSS_SELECTOR,
                        selector,
                    )
                )

            except WebDriverException:
                continue

        return result

    def get_body_text(self) -> str:
        """Return visible page body text."""

        try:
            body = self.driver.find_element(
                By.TAG_NAME,
                "body",
            )

            return self.clean_whitespace(body.text)

        except WebDriverException:
            return ""

    # ================================================================
    # TITLE
    # ================================================================

    def clean_title(self, title: str) -> str:
        """
        Clean LinkedIn title text.

        Removes:
        - duplicate title lines
        - "with verification"
        - unnecessary whitespace
        """

        title = self.clean_whitespace(title)

        if not title:
            return ""

        lines = [
            line.strip()
            for line in title.splitlines()
            if line.strip()
        ]

        cleaned = []

        for line in lines:

            line = re.sub(
                r"\s*with verification.*$",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()

            if not line:
                continue

            if line not in cleaned:
                cleaned.append(line)

        if not cleaned:
            return ""

        return cleaned[0]

    def extract_title(self) -> str:
        """Extract the job title from h1."""

        element = self.first_element(
            [
                "h1",
                "main h1",
            ]
        )

        if element is None:
            return ""

        return self.clean_title(
            self.safe_text(element)
        )

    # ================================================================
    # COMPANY
    # ================================================================

    def extract_company(self) -> str:
        """
        Extract company name from the company link.

        LinkedIn diagnostic showed:
        /company/apguru/
        """

        elements = self.elements(
            [
                'a[href*="/company/"]',
            ]
        )

        candidates = []

        for element in elements:
            try:
                text = self.safe_text(element)

                if not text:
                    continue

                href = element.get_attribute("href") or ""

                if "/company/" not in href:
                    continue

                candidates.append(text)

            except WebDriverException:
                continue

        blocked = {
            "about the company",
            "see all jobs",
            "follow",
        }

        for candidate in candidates:

            if (
                len(candidate) < 150
                and candidate.lower() not in blocked
            ):
                return candidate.strip()

        # Fallback based on page header.
        body = self.get_body_text()

        if body:
            lines = body.splitlines()

            title = self.extract_title()

            for index, line in enumerate(lines):

                if self.clean_title(line) == title:

                    for candidate in lines[
                        index + 1 : index + 8
                    ]:

                        candidate = candidate.strip()

                        if not candidate:
                            continue

                        if candidate.lower() in {
                            "easy apply",
                            "save",
                            "promoted by hirer",
                        }:
                            continue

                        if "·" in candidate:
                            continue

                        return candidate

        return ""

    def extract_company_url(self) -> str:
        """Extract company page URL."""

        for element in self.elements(
            [
                'a[href*="/company/"]',
            ]
        ):
            try:
                href = element.get_attribute(
                    "href"
                ) or ""

                if "/company/" in href:
                    return href.split("?")[0]

            except WebDriverException:
                continue

        return ""

    # ================================================================
    # JOB URL / ID
    # ================================================================

    def extract_job_url(self) -> str:
        """Extract current LinkedIn job URL."""

        try:
            current_url = self.browser.current_url()

            if "/jobs/view/" in current_url:
                return current_url.split("?")[0]

        except Exception:
            pass

        for element in self.elements(
            [
                'a[href*="/jobs/view/"]',
            ]
        ):
            try:
                href = element.get_attribute(
                    "href"
                ) or ""

                if "/jobs/view/" in href:
                    return href.split("?")[0]

            except WebDriverException:
                continue

        return ""

    def extract_job_id(self, url: str = "") -> str:
        """Extract LinkedIn numeric job ID."""

        if not url:
            url = self.extract_job_url()

        match = re.search(
            r"/jobs/view/(\d+)",
            url,
        )

        if match:
            return match.group(1)

        for element in self.elements(
            [
                'a[href*="/jobs/view/"]',
            ]
        ):
            try:
                href = element.get_attribute(
                    "href"
                ) or ""

                match = re.search(
                    r"/jobs/view/(\d+)",
                    href,
                )

                if match:
                    return match.group(1)

            except WebDriverException:
                continue

        return ""

    # ================================================================
    # HEADER
    # ================================================================

    def extract_header_lines(self) -> List[str]:
        """
        Extract lines around the job title.

        Current LinkedIn structure observed in diagnostics:

        Title
        Company
        Location · Posted · Applicants
        Workplace
        Employment
        Easy Apply
        Save
        """

        body = self.get_body_text()

        if not body:
            return []

        lines = [
            line.strip()
            for line in body.splitlines()
            if line.strip()
        ]

        title = self.extract_title()

        if not title:
            return lines[:30]

        title_index = -1

        for index, line in enumerate(lines):

            if self.clean_title(line) == title:
                title_index = index
                break

        if title_index == -1:
            return lines[:30]

        return lines[
            title_index : title_index + 20
        ]

    # ================================================================
    # LOCATION
    # ================================================================

    def looks_like_location(
        self,
        text: str,
    ) -> bool:
        """Determine whether text resembles a location."""

        if not text:
            return False

        lower = text.lower()

        blocked = [
            "month ago",
            "months ago",
            "week ago",
            "weeks ago",
            "day ago",
            "days ago",
            "hour ago",
            "hours ago",
            "applicant",
            "applicants",
            "promoted",
            "actively reviewing",
            "easy apply",
            "save",
            "full-time",
            "part-time",
            "contract",
            "internship",
            "on-site",
            "remote",
            "hybrid",
        ]

        if any(
            item in lower
            for item in blocked
        ):
            return False

        if "," in text:
            return True

        known_terms = [
            "mumbai",
            "thane",
            "navi mumbai",
            "pune",
            "delhi",
            "bangalore",
            "bengaluru",
            "hyderabad",
            "chennai",
            "kolkata",
            "gurgaon",
            "gurugram",
            "noida",
            "india",
            "maharashtra",
            "karnataka",
        ]

        return any(
            term in lower
            for term in known_terms
        )

    def extract_location(self) -> str:
        """Extract job location."""

        lines = self.extract_header_lines()

        for line in lines:

            if "·" not in line:
                continue

            parts = [
                part.strip()
                for part in line.split("·")
            ]

            if not parts:
                continue

            location = parts[0]

            if self.looks_like_location(
                location
            ):
                return location

        return ""

    # ================================================================
    # WORKPLACE
    # ================================================================

    def extract_workplace_type(self) -> str:
        """Extract On-site / Remote / Hybrid."""

        lines = self.extract_header_lines()

        values = {
            "on-site": "On-site",
            "remote": "Remote",
            "hybrid": "Hybrid",
        }

        for line in lines:

            normalized = line.strip().lower()

            if normalized in values:
                return values[normalized]

        body = self.get_body_text()

        for key, value in values.items():

            if re.search(
                rf"(?<!\w){re.escape(key)}(?!\w)",
                body,
                flags=re.IGNORECASE,
            ):
                return value

        return ""

    # ================================================================
    # EMPLOYMENT
    # ================================================================

    def extract_employment_type(self) -> str:
        """Extract employment type."""

        values = {
            "full-time": "Full-time",
            "part-time": "Part-time",
            "contract": "Contract",
            "temporary": "Temporary",
            "volunteer": "Volunteer",
            "internship": "Internship",
            "apprenticeship": "Apprenticeship",
            "freelance": "Freelance",
        }

        lines = self.extract_header_lines()

        for line in lines:

            normalized = line.strip().lower()

            if normalized in values:
                return values[normalized]

        body = self.get_body_text()

        for key, value in values.items():

            if re.search(
                rf"(?<!\w){re.escape(key)}(?!\w)",
                body,
                flags=re.IGNORECASE,
            ):
                return value

        return ""

    # ================================================================
    # EXPERIENCE
    # ================================================================

    def extract_experience_level(self) -> str:
        """
        Extract LinkedIn seniority level.

        Examples:
        Entry level
        Associate
        Mid-Senior level
        Director
        Executive
        """

        body = self.get_body_text()

        if not body:
            return ""

        levels = [
            "Internship",
            "Entry level",
            "Associate",
            "Mid-Senior level",
            "Director",
            "Executive",
        ]

        # Prefer text close to Applicant seniority level.
        lines = body.splitlines()

        for index, line in enumerate(lines):

            if (
                "applicant seniority level"
                in line.lower()
            ):

                nearby = lines[
                    index : index + 12
                ]

                for candidate in nearby:

                    candidate = candidate.strip()

                    for level in levels:

                        if (
                            level.lower()
                            in candidate.lower()
                        ):
                            return level

        # General fallback.
        for level in levels:

            if re.search(
                rf"\b{re.escape(level)}\b",
                body,
                flags=re.IGNORECASE,
            ):
                return level

        return ""

    # ================================================================
    # DESCRIPTION
    # ================================================================

    def remove_description_heading(
        self,
        text: str,
    ) -> str:
        """Remove About the job heading."""

        lines = text.splitlines()

        result = []

        for line in lines:

            if (
                line.strip().lower()
                == "about the job"
            ):
                continue

            if line.strip():
                result.append(
                    line.strip()
                )

        return "\n".join(result).strip()

    def extract_description(self) -> str:
        """
        Extract the section beginning at "About the job".
        """

        # First try semantic DOM relationships.
        try:

            headings = self.driver.find_elements(
                By.XPATH,
                "//*[self::h2 or self::h3]"
                "[normalize-space()='About the job']",
            )

            for heading in headings:

                if not heading.is_displayed():
                    continue

                candidates = []

                try:
                    candidates.append(
                        heading.find_element(
                            By.XPATH,
                            "./following-sibling::*[1]",
                        )
                    )
                except NoSuchElementException:
                    pass

                try:
                    candidates.append(
                        heading.find_element(
                            By.XPATH,
                            "..",
                        )
                    )
                except NoSuchElementException:
                    pass

                try:
                    candidates.append(
                        heading.find_element(
                            By.XPATH,
                            "../..",
                        )
                    )
                except NoSuchElementException:
                    pass

                for candidate in candidates:

                    text = self.safe_text(
                        candidate
                    )

                    text = (
                        self.remove_description_heading(
                            text
                        )
                    )

                    if len(text) >= 50:
                        return text

        except WebDriverException:
            pass

        # Main fallback: body text.
        body = self.get_body_text()

        if not body:
            return ""

        lines = body.splitlines()

        start_index = None

        for index, line in enumerate(lines):

            if (
                line.strip().lower()
                == "about the job"
            ):
                start_index = index
                break

        if start_index is None:
            return ""

        stop_headers = {
            "set alert for similar jobs",
            "about the company",
            "people also viewed",
            "similar jobs",
            "show more",
        }

        description_lines = []

        for line in lines[
            start_index + 1 :
        ]:

            value = line.strip()

            if not value:
                continue

            if value.lower() in stop_headers:
                break

            description_lines.append(value)

        return "\n".join(
            description_lines
        ).strip()

    # ================================================================
    # SKILLS
    # ================================================================

    def clean_skills(
        self,
        skills: List[str],
    ) -> List[str]:
        """Clean extracted skills."""

        blocked = {
            "skills",
            "show more",
            "see all",
            "follow",
            "save",
            "easy apply",
        }

        result = []

        for skill in skills:

            skill = self.clean_whitespace(
                skill
            )

            if not skill:
                continue

            if skill.lower() in blocked:
                continue

            if skill not in result:
                result.append(skill)

        return result

    def extract_skills(self) -> List[str]:
        """
        Extract skills if LinkedIn exposes a Skills section.
        """

        body = self.get_body_text()

        if not body:
            return []

        lines = body.splitlines()

        start_index = None

        for index, line in enumerate(lines):

            if (
                line.strip().lower()
                == "skills"
            ):
                start_index = index
                break

        if start_index is None:
            return []

        stop_headers = {
            "about the company",
            "people also viewed",
            "similar jobs",
            "set alert for similar jobs",
        }

        skills = []

        for line in lines[
            start_index + 1 :
        ]:

            value = line.strip()

            if not value:
                continue

            if value.lower() in stop_headers:
                break

            if len(value) > 100:
                continue

            if value not in skills:
                skills.append(value)

            if len(skills) >= 30:
                break

        return self.clean_skills(skills)

    # ================================================================
    # EASY APPLY
    # ================================================================

    def detect_easy_apply(self) -> bool:
        """
        Detect Easy Apply without clicking it.

        Confirmed diagnostic selector:

        button[aria-label="Easy Apply to this job"]
        """

        selectors = [
            'button[aria-label="Easy Apply to this job"]',
            'button[aria-label*="Easy Apply"]',
        ]

        for selector in selectors:

            try:

                elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )

                for element in elements:

                    if element.is_displayed():
                        return True

            except WebDriverException:
                continue

        # Text fallback.
        try:

            buttons = self.driver.find_elements(
                By.TAG_NAME,
                "button",
            )

            for button in buttons:

                text = self.safe_text(
                    button
                ).lower()

                if text == "easy apply":
                    return True

        except WebDriverException:
            pass

        return False

    # ================================================================
    # COMPLETE EXTRACTION
    # ================================================================

    def extract_current_job(
        self,
        fallback_job: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """Extract all available details."""

        fallback_job = fallback_job or {}

        job_url = self.extract_job_url()

        if not job_url:
            job_url = fallback_job.get(
                "job_url",
                "",
            )

        job_id = self.extract_job_id(
            job_url
        )

        if not job_id:
            job_id = str(
                fallback_job.get(
                    "job_id",
                    "",
                )
            )

        title = self.extract_title()

        if not title:
            title = fallback_job.get(
                "title",
                "",
            )

        company = self.extract_company()

        if not company:
            company = fallback_job.get(
                "company",
                "",
            )

        location = self.extract_location()

        if not location:
            location = fallback_job.get(
                "location",
                "",
            )

        workplace_type = (
            self.extract_workplace_type()
        )

        employment_type = (
            self.extract_employment_type()
        )

        experience_level = (
            self.extract_experience_level()
        )

        description = (
            self.extract_description()
        )

        skills = self.extract_skills()

        easy_apply = (
            self.detect_easy_apply()
        )

        company_url = (
            self.extract_company_url()
        )

        result = dict(fallback_job)

        result["job_id"] = job_id
        result["job_url"] = job_url
        result["title"] = title
        result["company"] = company
        result["company_url"] = company_url
        result["location"] = location

        result["workplace_type"] = (
            workplace_type
        )

        result["employment_type"] = (
            employment_type
        )

        result["experience_level"] = (
            experience_level
        )

        result["description"] = (
            description
        )

        result["skills"] = skills
        result["easy_apply"] = easy_apply

        return result

    # ================================================================
    # OPEN JOB
    # ================================================================

    def open_job(
        self,
        job_url: str,
        wait_seconds: float = 2.0,
    ) -> bool:
        """Open a LinkedIn job page."""

        if not job_url:
            return False

        try:

            self.browser.open(job_url)

            if not self.wait_for_page(
                timeout=15
            ):
                return False

            if wait_seconds > 0:
                time.sleep(
                    wait_seconds
                )

            return True

        except WebDriverException as exc:

            print(
                f"Failed to open job URL: {exc}"
            )

            return False

    # ================================================================
    # STORAGE
    # ================================================================

    def update_job(
        self,
        job: Dict[str, Any],
    ) -> bool:
        """Update an existing job."""

        job_id = str(
            job.get(
                "job_id",
                "",
            )
        ).strip()

        if not job_id:
            return False

        try:

            existing = (
                job_repository.get_by_id(
                    job_id
                )
            )

            if existing is None:

                job_repository.save(
                    job
                )

            else:

                job_repository.update(
                    job_id,
                    job,
                )

            return True

        except Exception as exc:

            print(
                f"Failed to save job "
                f"{job_id}: {exc}"
            )

            return False

    # ================================================================
    # PROCESS SAVED JOBS
    # ================================================================

    def process_saved_jobs(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process saved jobs.

        No Apply interaction is performed.
        """

        jobs = job_repository.get_all()

        if limit is not None:
            jobs = jobs[:limit]

        processed = []

        for index, job in enumerate(
            jobs,
            start=1,
        ):

            print("-" * 80)
            print(
                f"JOB {index}/{len(jobs)}"
            )
            print("-" * 80)

            job_url = job.get(
                "job_url",
                "",
            )

            print()
            print("Opening job:")
            print(job_url)
            print()

            if not self.open_job(
                job_url
            ):

                print(
                    "✗ Could not open job"
                )

                continue

            enriched = (
                self.extract_current_job(
                    fallback_job=job
                )
            )

            print(
                f"Title: "
                f"{enriched.get('title', '')}"
            )

            print(
                f"Company: "
                f"{enriched.get('company', '')}"
            )

            print(
                f"Location: "
                f"{enriched.get('location', '')}"
            )

            print(
                f"Workplace: "
                f"{enriched.get('workplace_type', '')}"
            )

            print(
                f"Employment: "
                f"{enriched.get('employment_type', '')}"
            )

            print(
                f"Experience: "
                f"{enriched.get('experience_level', '')}"
            )

            print(
                f"Easy Apply: "
                f"{enriched.get('easy_apply', False)}"
            )

            print(
                f"Description length: "
                f"{len(enriched.get('description', ''))}"
            )

            print(
                f"Skills: "
                f"{enriched.get('skills', [])}"
            )

            saved = self.update_job(
                enriched
            )

            print(
                f"Saved: {saved}"
            )

            processed.append(
                enriched
            )

        return processed

    # ================================================================
    # SINGLE JOB
    # ================================================================

    def process_job(
        self,
        job: Dict[str, Any],
    ) -> Optional[
        Dict[str, Any]
    ]:
        """Process one job."""

        job_url = job.get(
            "job_url",
            "",
        )

        if not self.open_job(
            job_url
        ):
            return None

        enriched = (
            self.extract_current_job(
                fallback_job=job
            )
        )

        self.update_job(
            enriched
        )

        return enriched


# ====================================================================
# SHARED SERVICE
# ====================================================================

linkedin_job_details_service = (
    LinkedInJobDetailsService()
)


__all__ = [
    "LinkedInJobDetailsService",
    "linkedin_job_details_service",
]