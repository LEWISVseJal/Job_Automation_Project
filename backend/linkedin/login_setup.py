"""
Manual LinkedIn login setup.

This script:
1. Starts the project's persistent Chrome profile.
2. Opens LinkedIn.
3. Allows manual login.
4. Checks the login using the SAME Selenium process.
5. Saves the session status.
6. Keeps Chrome open.
"""

import time

from backend.linkedin.browser import linkedin_browser
from backend.linkedin.session_service import linkedin_session_service
from backend.config.settings import LINKEDIN_URL


def main():

    print()
    print("=" * 70)
    print("LINKEDIN LOGIN SETUP")
    print("=" * 70)
    print()

    print("Opening LinkedIn...")
    print()

    # Start the shared Selenium browser.
    linkedin_browser.start()

    # Open LinkedIn.
    linkedin_browser.open(LINKEDIN_URL)

    print("✓ Chrome opened")
    print()

    print("Please log in to LinkedIn manually.")
    print()
    print("Complete any:")
    print("  • Email/password login")
    print("  • OTP")
    print("  • Security verification")
    print("  • CAPTCHA, if shown")
    print()

    print("Make sure you reach your normal LinkedIn home page.")
    print()

    input("Press ENTER after you are completely logged in: ")

    print()
    print("Checking LinkedIn session...")
    print()

    # IMPORTANT:
    # This check happens inside the SAME Python process
    # that owns the Selenium browser.
    status = linkedin_session_service.save_session_status()

    print("Session result:")
    print(status)
    print()

    if status["logged_in"]:

        print("=" * 70)
        print("✓ LINKEDIN LOGIN SUCCESSFUL")
        print("=" * 70)
        print()
        print("Authenticated LinkedIn session detected.")
        print()
        print("Chrome will remain open.")
        print("Keep this window running for now.")
        print()

    else:

        print("=" * 70)
        print("⚠ LINKEDIN LOGIN NOT DETECTED")
        print("=" * 70)
        print()
        print("Current URL:")
        print(status["url"])
        print()
        print("Do not close Chrome.")
        print("Send me this output before continuing.")
        print()

    # Keep the browser alive.
    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print()
        print("Stopping LinkedIn login setup...")
        print()

        linkedin_browser.close()

        print("✓ Browser closed.")


if __name__ == "__main__":
    main()