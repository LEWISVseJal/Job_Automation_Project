"""
Test LinkedIn job search.

This test owns the complete Selenium session in one process.
It does NOT apply to jobs.
"""

from backend.linkedin.browser import linkedin_browser
from backend.linkedin.session_service import linkedin_session_service
from backend.linkedin.job_search import linkedin_job_search_service


def main():

    print()
    print("=" * 80)
    print("LINKEDIN JOB SEARCH TEST")
    print("=" * 80)
    print()

    # Start the shared browser.
    linkedin_browser.start()

    # Open LinkedIn.
    linkedin_session_service.open_linkedin()

    print("Checking LinkedIn login...")
    print()

    status = linkedin_session_service.get_session_status()

    print("Logged in:", status["logged_in"])
    print("URL:", status["url"])
    print()

    if not status["logged_in"]:

        print("❌ LinkedIn login was not detected.")
        print()
        print("Please log in manually and run the test again.")
        print()

        linkedin_browser.close()
        return

    print("✓ LinkedIn session confirmed")
    print()

    # -------------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------------

    keywords = "AI ML Engineer"
    location = "Mumbai"

    print("Search:")
    print("  Keywords:", keywords)
    print("  Location:", location)
    print()

    jobs = linkedin_job_search_service.search_and_save(
        keywords=keywords,
        location=location,
        max_jobs=5,
    )

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    if not jobs:

        print("⚠ No jobs were extracted.")

    else:

        print(f"✓ Extracted {len(jobs)} jobs")
        print()

        for index, job in enumerate(jobs, start=1):

            print(f"{index}. {job.get('title', '')}")
            print(f"   Company: {job.get('company', '')}")
            print(f"   Location: {job.get('location', '')}")
            print(f"   Easy Apply: {job.get('easy_apply', False)}")
            print(f"   URL: {job.get('url', '')}")
            print()

    print("Jobs have been saved to data/jobs.json.")
    print()
    print("Chrome will remain open.")
    print("Press CTRL+C when you want to stop the test.")
    print()

    try:

        while True:
            input()

    except KeyboardInterrupt:

        print()
        print("Stopping test...")
        linkedin_browser.close()
        print("✓ Browser closed.")


if __name__ == "__main__":
    main()