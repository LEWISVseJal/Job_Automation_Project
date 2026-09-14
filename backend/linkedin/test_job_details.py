"""
Test LinkedIn Job Details Extraction.

This test:
- Uses the shared Selenium browser.
- Checks LinkedIn login.
- Reads jobs from data/jobs.json.
- Opens saved LinkedIn jobs.
- Extracts detailed information.
- Updates data/jobs.json.

It DOES NOT:
- Click Apply.
- Fill applications.
- Submit applications.
"""

from backend.linkedin.browser import linkedin_browser
from backend.linkedin.session_service import linkedin_session_service
from backend.linkedin.job_details import (
    linkedin_job_details_service,
)


def main():

    print()
    print("=" * 80)
    print("LINKEDIN JOB DETAILS TEST")
    print("=" * 80)
    print()

    # --------------------------------------------------------------
    # Start shared browser
    # --------------------------------------------------------------

    linkedin_browser.start()

    # --------------------------------------------------------------
    # Check LinkedIn session
    # --------------------------------------------------------------

    linkedin_session_service.open_linkedin()

    print("Checking LinkedIn login...")
    print()

    status = (
        linkedin_session_service
        .get_session_status()
    )

    print(
        "Logged in:",
        status["logged_in"],
    )

    print(
        "URL:",
        status["url"],
    )

    print()

    if not status["logged_in"]:

        print(
            "❌ LinkedIn login was not detected."
        )

        print()
        print(
            "Please run:"
        )

        print(
            "python -m backend.linkedin.login_setup"
        )

        print()

        linkedin_browser.close()

        return

    print(
        "✓ LinkedIn session confirmed"
    )

    print()

    # --------------------------------------------------------------
    # Process saved jobs
    # --------------------------------------------------------------

    jobs = (
        linkedin_job_details_service
        .process_saved_jobs(
            max_jobs=5
        )
    )

    # --------------------------------------------------------------
    # Results
    # --------------------------------------------------------------

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    if not jobs:

        print(
            "⚠ No jobs were successfully processed."
        )

    else:

        print(
            f"✓ Processed {len(jobs)} jobs"
        )

        print()

        for index, job in enumerate(
            jobs,
            start=1,
        ):

            print(
                f"{index}. "
                f"{job.get('title', '')}"
            )

            print(
                "   Company:",
                job.get(
                    "company",
                    "",
                ),
            )

            print(
                "   Location:",
                job.get(
                    "location",
                    "",
                ),
            )

            print(
                "   Employment:",
                job.get(
                    "employment_type",
                    "",
                ),
            )

            print(
                "   Experience:",
                job.get(
                    "experience_level",
                    "",
                ),
            )

            print(
                "   Easy Apply:",
                job.get(
                    "easy_apply",
                    False,
                ),
            )

            print(
                "   Skills:",
                job.get(
                    "skills",
                    [],
                ),
            )

            print(
                "   Description:",
                len(
                    job.get(
                        "description",
                        "",
                    )
                ),
                "characters",
            )

            print(
                "   URL:",
                job.get(
                    "url",
                    "",
                ),
            )

            print()

    print(
        "Updated jobs are stored in:"
    )

    print(
        "data/jobs.json"
    )

    print()

    print(
        "Chrome will remain open."
    )

    print(
        "Press CTRL+C when you want to stop."
    )

    print()

    try:

        while True:
            input()

    except KeyboardInterrupt:

        print()
        print(
            "Stopping test..."
        )

        linkedin_browser.close()

        print(
            "✓ Browser closed."
        )


if __name__ == "__main__":
    main()