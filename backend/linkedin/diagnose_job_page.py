"""
LinkedIn Job Page DOM Diagnostic Tool
=====================================

Purpose:
    Diagnose the actual LinkedIn job-detail page DOM.

This script:
    1. Uses the existing LinkedIn session service.
    2. Uses the existing LinkedInBrowser.
    3. Gets the real Selenium WebDriver.
    4. Reads the first saved job from data/jobs.json.
    5. Opens that job.
    6. Saves the HTML.
    7. Saves a screenshot.
    8. Prints the important DOM information.

SAFETY
------
This script DOES NOT:

    - Click Apply
    - Click Easy Apply
    - Fill forms
    - Upload resume
    - Click Next
    - Click Review
    - Submit applications

It is ONLY a diagnostic tool.
"""

import json
import os
import re
import time

from selenium.webdriver.common.by import By

from backend.config.settings import (
    DATA_DIR,
    ELEMENT_WAIT_TIMEOUT,
    ACTION_DELAY,
    HTML_DIR,
    SCREENSHOTS_DIR,
)

from backend.linkedin.session_service import (
    linkedin_session_service,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def print_section(title):
    """
    Print a clear diagnostic section heading.
    """

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def safe_get_attribute(element, attribute):
    """
    Safely retrieve an element attribute.
    """

    try:
        return element.get_attribute(attribute) or ""

    except Exception:
        return ""


def safe_element_text(element):
    """
    Safely retrieve element text.
    """

    try:
        return (element.text or "").strip()

    except Exception:
        return ""


# =============================================================================
# DOM PRINTING
# =============================================================================


def print_elements(
    driver,
    selector,
    label,
    limit=30,
):
    """
    Print information about elements matching a CSS selector.
    """

    print_section(label)

    print(
        f"Selector: {selector}"
    )

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            selector,
        )

        print(
            f"Found: {len(elements)}"
        )

        for index, element in enumerate(
            elements[:limit],
            start=1,
        ):

            try:
                tag = element.tag_name
            except Exception:
                tag = ""

            text = safe_element_text(
                element
            )

            classes = safe_get_attribute(
                element,
                "class",
            )

            aria_label = safe_get_attribute(
                element,
                "aria-label",
            )

            href = safe_get_attribute(
                element,
                "href",
            )

            data_test_id = safe_get_attribute(
                element,
                "data-test-id",
            )

            data_control_name = safe_get_attribute(
                element,
                "data-control-name",
            )

            print()
            print(
                f"[{index}]"
            )

            print(
                f"  TAG        : {tag}"
            )

            print(
                f"  TEXT       : {text[:500]!r}"
            )

            print(
                f"  CLASS      : {classes[:500]}"
            )

            if aria_label:

                print(
                    f"  ARIA-LABEL : {aria_label[:500]}"
                )

            if href:

                print(
                    f"  HREF       : {href[:500]}"
                )

            if data_test_id:

                print(
                    f"  DATA-TEST  : {data_test_id[:500]}"
                )

            if data_control_name:

                print(
                    f"  CONTROL    : {data_control_name[:500]}"
                )

    except Exception as exc:

        print(
            f"ERROR: {exc}"
        )


def print_text_matches(
    driver,
    pattern,
    label,
    limit=30,
):
    """
    Search visible page text using a regular expression.

    Context lines around the match are printed so we can understand
    the actual LinkedIn DOM structure.
    """

    print_section(label)

    try:

        body = driver.find_element(
            By.TAG_NAME,
            "body",
        )

        body_text = body.text or ""

        lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]

        regex = re.compile(
            pattern,
            re.IGNORECASE,
        )

        matches = []

        for index, line in enumerate(lines):

            if regex.search(line):

                start = max(
                    0,
                    index - 2,
                )

                end = min(
                    len(lines),
                    index + 3,
                )

                matches.append(
                    lines[start:end]
                )

        if not matches:

            print(
                "No matches found."
            )

            return

        print(
            f"Matches found: {len(matches)}"
        )

        for index, context in enumerate(
            matches[:limit],
            start=1,
        ):

            print()
            print(
                f"[MATCH {index}]"
            )

            for line in context:

                print(
                    f"  {line[:500]}"
                )

    except Exception as exc:

        print(
            f"ERROR: {exc}"
        )


def print_attributes(
    driver,
    selector,
    label,
    attributes,
    limit=50,
):
    """
    Print selected attributes from matching elements.
    """

    print_section(label)

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            selector,
        )

        print(
            f"Selector: {selector}"
        )

        print(
            f"Found: {len(elements)}"
        )

        for index, element in enumerate(
            elements[:limit],
            start=1,
        ):

            print()
            print(
                f"[{index}]"
            )

            for attribute in attributes:

                value = safe_get_attribute(
                    element,
                    attribute,
                )

                if value:

                    print(
                        f"  {attribute}: "
                        f"{value[:1000]}"
                    )

    except Exception as exc:

        print(
            f"ERROR: {exc}"
        )


# =============================================================================
# GET SELENIUM DRIVER
# =============================================================================


def get_driver():
    """
    Get the actual Selenium WebDriver.

    Project architecture:

        LinkedInSessionService
                ↓
        LinkedInBrowser
                ↓
        Selenium WebDriver

    The Selenium driver is:

        linkedin_session_service.browser.driver
    """

    print_section(
        "LINKEDIN SESSION"
    )

    service = (
        linkedin_session_service
    )

    print(
        "✓ LinkedIn session service loaded."
    )

    # -------------------------------------------------------------------------
    # Get LinkedInBrowser
    # -------------------------------------------------------------------------

    browser = getattr(
        service,
        "browser",
        None,
    )

    if browser is None:

        print()
        print(
            "⚠ LinkedInBrowser is not initialized."
        )

        print()
        print(
            "Starting LinkedIn browser..."
        )

        try:

            result = service.open_linkedin()

            print(
                f"open_linkedin() result: {result}"
            )

        except Exception as exc:

            print()
            print(
                f"❌ Could not open LinkedIn: {exc}"
            )

            return None

        browser = getattr(
            service,
            "browser",
            None,
        )

    if browser is None:

        print()
        print(
            "❌ LinkedInBrowser is unavailable."
        )

        return None

    print()
    print(
        f"✓ LinkedInBrowser found: {type(browser)}"
    )

    # -------------------------------------------------------------------------
    # Get actual Selenium driver
    # -------------------------------------------------------------------------

    driver = getattr(
        browser,
        "driver",
        None,
    )

    if driver is None:

        print()
        print(
            "⚠ Selenium driver is not initialized."
        )

        print()
        print(
            "Starting the existing LinkedIn browser..."
        )

        try:

            browser.start()

        except Exception as exc:

            print()
            print(
                f"❌ Could not start browser: {exc}"
            )

            return None

        driver = getattr(
            browser,
            "driver",
            None,
        )

    if driver is None:

        print()
        print(
            "❌ Selenium WebDriver is unavailable."
        )

        return None

    print()
    print(
        "✓ Selenium WebDriver found."
    )

    # -------------------------------------------------------------------------
    # Check LinkedIn session
    # -------------------------------------------------------------------------

    try:

        session_status = (
            service.check_session()
        )

        print()
        print(
            "Session check:"
        )

        print(
            session_status
        )

    except Exception as exc:

        print()
        print(
            f"⚠ Session check failed: {exc}"
        )

    # -------------------------------------------------------------------------
    # Get stored session status
    # -------------------------------------------------------------------------

    try:

        status = (
            service.get_session_status()
        )

        print()
        print(
            "Stored session status:"
        )

        print(
            status
        )

    except Exception as exc:

        print()
        print(
            f"⚠ Could not read session status: {exc}"
        )

    # -------------------------------------------------------------------------
    # Current URL
    # -------------------------------------------------------------------------

    try:

        current_url = (
            browser.current_url()
        )

    except Exception:

        try:

            current_url = (
                driver.current_url
            )

        except Exception:

            current_url = ""

    print()
    print(
        f"Current URL: {current_url}"
    )

    # -------------------------------------------------------------------------
    # Page title
    # -------------------------------------------------------------------------

    try:

        print(
            f"Page title: {driver.title}"
        )

    except Exception:

        pass

    return driver


# =============================================================================
# LOAD JOBS.JSON
# =============================================================================


def load_jobs():
    """
    Load jobs directly from data/jobs.json.

    We intentionally do not use a nonexistent repository attribute
    from LinkedInJobSearchService.
    """

    print_section(
        "LOADING SAVED JOBS"
    )

    jobs_file = (
        DATA_DIR / "jobs.json"
    )

    print()
    print(
        f"Jobs file: {jobs_file}"
    )

    if not jobs_file.exists():

        print()
        print(
            "❌ jobs.json does not exist."
        )

        print()
        print(
            "Run the LinkedIn job search first."
        )

        return []

    try:

        with open(
            jobs_file,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

    except Exception as exc:

        print()
        print(
            f"❌ Could not read jobs.json: {exc}"
        )

        return []

    # -------------------------------------------------------------------------
    # Support both:
    #
    #   [...]
    #
    # and:
    #
    #   {"jobs": [...]}
    # -------------------------------------------------------------------------

    if isinstance(
        data,
        list,
    ):

        jobs = data

    elif isinstance(
        data,
        dict,
    ):

        jobs = data.get(
            "jobs",
            [],
        )

    else:

        jobs = []

    if not isinstance(
        jobs,
        list,
    ):

        print()
        print(
            "❌ jobs.json does not contain a job list."
        )

        return []

    print()
    print(
        f"✓ Loaded {len(jobs)} jobs"
    )

    return jobs


# =============================================================================
# SELECT FIRST JOB
# =============================================================================


def get_first_job():
    """
    Get the first saved job.
    """

    jobs = load_jobs()

    if not jobs:

        return None

    job = jobs[0]

    if not isinstance(
        job,
        dict,
    ):

        print()
        print(
            "❌ First saved job is not an object."
        )

        return None

    job_id = (
        job.get("job_id")
        or job.get("id")
        or "unknown"
    )

    title = (
        job.get("title")
        or ""
    )

    company = (
        job.get("company")
        or ""
    )

    job_url = (
        job.get("job_url")
        or job.get("url")
        or ""
    )

    print()
    print(
        "Selected job:"
    )

    print(
        f"  Job ID : {job_id}"
    )

    print(
        f"  Title  : {title}"
    )

    print(
        f"  Company: {company}"
    )

    print(
        f"  URL    : {job_url}"
    )

    if not job_url:

        print()
        print(
            "❌ Job URL is missing."
        )

        return None

    return job


# =============================================================================
# OPEN JOB
# =============================================================================


def open_job(
    driver,
    job,
):
    """
    Open the selected job page.
    """

    print_section(
        "OPENING JOB"
    )

    job_id = (
        job.get("job_id")
        or job.get("id")
        or "unknown"
    )

    job_url = (
        job.get("job_url")
        or job.get("url")
        or ""
    )

    print(
        f"Job ID: {job_id}"
    )

    print(
        f"URL: {job_url}"
    )

    try:

        driver.get(
            job_url
        )

    except Exception as exc:

        print()
        print(
            f"⚠ Browser navigation returned: {exc}"
        )

        print(
            "Continuing with current page."
        )

    # -------------------------------------------------------------------------
    # Wait for LinkedIn's dynamic content
    # -------------------------------------------------------------------------

    print()
    print(
        "Waiting for LinkedIn job page..."
    )

    time.sleep(
        ACTION_DELAY
    )

    time.sleep(
        ELEMENT_WAIT_TIMEOUT
    )

    try:

        current_url = (
            driver.current_url
        )

    except Exception:

        current_url = ""

    print()
    print(
        f"Current URL: {current_url}"
    )

    try:

        print(
            f"Page title: {driver.title}"
        )

    except Exception:

        pass

    return job_id, job_url


# =============================================================================
# SAVE DIAGNOSTICS
# =============================================================================


def save_diagnostics(
    driver,
    job_id,
):
    """
    Save page HTML and screenshot.
    """

    print_section(
        "SAVING DIAGNOSTICS"
    )

    os.makedirs(
        str(HTML_DIR),
        exist_ok=True,
    )

    os.makedirs(
        str(SCREENSHOTS_DIR),
        exist_ok=True,
    )

    html_path = os.path.join(
        str(HTML_DIR),
        f"{job_id}_detail.html",
    )

    screenshot_path = os.path.join(
        str(SCREENSHOTS_DIR),
        f"{job_id}_detail.png",
    )

    # -------------------------------------------------------------------------
    # HTML
    # -------------------------------------------------------------------------

    try:

        page_source = (
            driver.page_source
        )

        with open(
            html_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                page_source
            )

        print()
        print(
            "✓ HTML saved:"
        )

        print(
            f"  {html_path}"
        )

    except Exception as exc:

        print()
        print(
            f"⚠ HTML save failed: {exc}"
        )

    # -------------------------------------------------------------------------
    # Screenshot
    # -------------------------------------------------------------------------

    try:

        driver.save_screenshot(
            screenshot_path
        )

        print()
        print(
            "✓ Screenshot saved:"
        )

        print(
            f"  {screenshot_path}"
        )

    except Exception as exc:

        print()
        print(
            f"⚠ Screenshot save failed: {exc}"
        )

    return (
        html_path,
        screenshot_path,
    )


# =============================================================================
# INSPECT DOM
# =============================================================================


def inspect_dom(driver):
    """
    Inspect the actual LinkedIn job page DOM.
    """

    # =========================================================================
    # HEADINGS
    # =========================================================================

    print_elements(
        driver,
        "h1",
        "ALL H1 ELEMENTS",
        limit=30,
    )

    print_elements(
        driver,
        "h2",
        "ALL H2 ELEMENTS",
        limit=30,
    )

    print_elements(
        driver,
        "h3",
        "ALL H3 ELEMENTS",
        limit=50,
    )

    # =========================================================================
    # COMPANY LINKS
    # =========================================================================

    print_elements(
        driver,
        "a[href*='/company/']",
        "COMPANY LINKS",
        limit=50,
    )

    # =========================================================================
    # JOB LINKS
    # =========================================================================

    print_elements(
        driver,
        "a[href*='/jobs/view/']",
        "JOB LINKS",
        limit=50,
    )

    # =========================================================================
    # BUTTONS
    # =========================================================================

    print_elements(
        driver,
        "button",
        "ALL BUTTONS",
        limit=100,
    )

    # =========================================================================
    # INPUTS
    # =========================================================================

    print_elements(
        driver,
        "input",
        "ALL INPUT ELEMENTS",
        limit=80,
    )

    # =========================================================================
    # TEXTAREAS
    # =========================================================================

    print_elements(
        driver,
        "textarea",
        "ALL TEXTAREA ELEMENTS",
        limit=30,
    )

    # =========================================================================
    # SECTIONS
    # =========================================================================

    print_elements(
        driver,
        "section",
        "ALL SECTION ELEMENTS",
        limit=50,
    )

    # =========================================================================
    # LIST ITEMS
    # =========================================================================

    print_elements(
        driver,
        "li",
        "ALL LI ELEMENTS",
        limit=100,
    )

    # =========================================================================
    # SPANS
    # =========================================================================

    print_elements(
        driver,
        "span",
        "SPAN ELEMENTS",
        limit=100,
    )

    # =========================================================================
    # DIVS
    # =========================================================================

    print_elements(
        driver,
        "div[class]",
        "DIV ELEMENTS WITH CLASSES",
        limit=150,
    )

    # =========================================================================
    # BUTTON ATTRIBUTES
    # =========================================================================

    print_attributes(
        driver,
        "button",
        "BUTTON ATTRIBUTES",
        [
            "aria-label",
            "data-test-id",
            "data-control-name",
            "class",
            "type",
        ],
        limit=100,
    )

    # =========================================================================
    # LINK ATTRIBUTES
    # =========================================================================

    print_attributes(
        driver,
        "a",
        "LINK ATTRIBUTES",
        [
            "href",
            "aria-label",
            "data-test-id",
            "data-control-name",
            "class",
        ],
        limit=120,
    )

    # =========================================================================
    # TEXT SEARCH
    # =========================================================================

    print_text_matches(
        driver,
        r"about the job",
        "ABOUT THE JOB TEXT",
    )

    print_text_matches(
        driver,
        r"description",
        "DESCRIPTION TEXT",
    )

    print_text_matches(
        driver,
        r"employment type",
        "EMPLOYMENT TYPE TEXT",
    )

    print_text_matches(
        driver,
        r"experience level",
        "EXPERIENCE LEVEL TEXT",
    )

    print_text_matches(
        driver,
        r"seniority",
        "SENIORITY TEXT",
    )

    print_text_matches(
        driver,
        r"location",
        "LOCATION TEXT",
    )

    print_text_matches(
        driver,
        r"skills",
        "SKILLS TEXT",
    )

    print_text_matches(
        driver,
        r"easy apply",
        "EASY APPLY TEXT",
    )

    print_text_matches(
        driver,
        r"apply",
        "ALL APPLY TEXT",
        limit=50,
    )

    # =========================================================================
    # BODY TEXT
    # =========================================================================

    print_section(
        "BODY TEXT PREVIEW"
    )

    try:

        body = driver.find_element(
            By.TAG_NAME,
            "body",
        )

        body_text = body.text or ""

        lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]

        print(
            f"Total non-empty lines: {len(lines)}"
        )

        print()

        for index, line in enumerate(
            lines[:250],
            start=1,
        ):

            print(
                f"{index:03d}: {line[:500]}"
            )

    except Exception as exc:

        print(
            f"ERROR reading body text: {exc}"
        )


# =============================================================================
# MAIN DIAGNOSTIC
# =============================================================================


def diagnose_job_page():
    """
    Run the complete diagnostic workflow.
    """

    print()
    print("=" * 80)
    print("LINKEDIN JOB PAGE DOM DIAGNOSTIC")
    print("=" * 80)

    print()
    print(
        f"HTML directory       : {HTML_DIR}"
    )

    print(
        f"Screenshot directory : {SCREENSHOTS_DIR}"
    )

    # =========================================================================
    # STEP 1 - GET DRIVER
    # =========================================================================

    driver = get_driver()

    if driver is None:

        print()
        print("=" * 80)
        print("DIAGNOSTIC STOPPED")
        print("=" * 80)

        return

    # =========================================================================
    # STEP 2 - GET SAVED JOB
    # =========================================================================

    job = get_first_job()

    if job is None:

        print()
        print("=" * 80)
        print("DIAGNOSTIC STOPPED")
        print("=" * 80)

        return

    # =========================================================================
    # STEP 3 - OPEN JOB
    # =========================================================================

    job_id, job_url = open_job(
        driver,
        job,
    )

    # =========================================================================
    # STEP 4 - SAVE HTML + SCREENSHOT
    # =========================================================================

    html_path, screenshot_path = (
        save_diagnostics(
            driver,
            job_id,
        )
    )

    # =========================================================================
    # STEP 5 - INSPECT DOM
    # =========================================================================

    inspect_dom(
        driver
    )

    # =========================================================================
    # COMPLETE
    # =========================================================================

    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

    print()
    print(
        f"Job ID     : {job_id}"
    )

    print(
        f"Job URL    : {job_url}"
    )

    print(
        f"HTML       : {html_path}"
    )

    print(
        f"Screenshot : {screenshot_path}"
    )

    print()
    print(
        "SAFETY:"
    )

    print(
        "  ✓ No Apply button clicked"
    )

    print(
        "  ✓ No Easy Apply button clicked"
    )

    print(
        "  ✓ No form filled"
    )

    print(
        "  ✓ No resume uploaded"
    )

    print(
        "  ✓ No Next button clicked"
    )

    print(
        "  ✓ No Review button clicked"
    )

    print(
        "  ✓ No application submitted"
    )


# =============================================================================
# ENTRY POINT
# =============================================================================


if __name__ == "__main__":

    diagnose_job_page()