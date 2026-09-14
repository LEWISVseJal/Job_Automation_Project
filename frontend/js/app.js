/*
============================================================
JOB AUTOMATION FRONTEND

This file currently handles:

1. Sidebar navigation
2. Page switching
3. Basic API connectivity
4. Dashboard statistics

Later we will connect:
- Resume parser
- LinkedIn job collector
- Job matcher
- Easy Apply automation
- Application tracking
============================================================
*/


// ============================================================
// CONFIGURATION
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000";


// ============================================================
// PAGE TITLES
// ============================================================

const pageTitles = {

    dashboard: "Dashboard",

    profile: "Profile",

    resume: "Resume",

    jobs: "Jobs",

    matches: "Matches",

    applications: "Applications",

    settings: "Settings"

};


// ============================================================
// NAVIGATION
// ============================================================

function navigateTo(pageName) {

    /*
    Hide every page.
    */

    document
        .querySelectorAll(".page")
        .forEach(page => {

            page.classList.remove("active");

        });


    /*
    Show selected page.
    */

    const selectedPage =
        document.getElementById(
            `page-${pageName}`
        );


    if (selectedPage) {

        selectedPage.classList.add("active");

    }


    /*
    Update sidebar active item.
    */

    document
        .querySelectorAll(".nav-item")
        .forEach(item => {

            item.classList.remove("active");

        });


    const selectedNav =
        document.querySelector(
            `.nav-item[data-page="${pageName}"]`
        );


    if (selectedNav) {

        selectedNav.classList.add("active");

    }


    /*
    Update page title.
    */

    const title =
        pageTitles[pageName] || "Dashboard";


    document.getElementById(
        "page-title"
    ).textContent = title;


    /*
    Update browser URL without reload.
    */

    window.history.replaceState(
        {},
        "",
        `#${pageName}`
    );

}


// ============================================================
// SIDEBAR EVENTS
// ============================================================

document
    .querySelectorAll(".nav-item")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const page =
                    button.dataset.page;

                navigateTo(page);

            }
        );

    });


// ============================================================
// LOAD PAGE FROM URL
// ============================================================

function loadPageFromHash() {

    const hash =
        window.location.hash
            .replace("#", "")
            .trim();


    if (
        hash &&
        pageTitles[hash]
    ) {

        navigateTo(hash);

    } else {

        navigateTo("dashboard");

    }

}


// ============================================================
// API HELPER
// ============================================================

async function apiRequest(
    endpoint,
    options = {}
) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}${endpoint}`,
                options
            );


        if (!response.ok) {

            throw new Error(
                `API error: ${response.status}`
            );

        }


        return await response.json();

    } catch (error) {

        console.error(
            "API request failed:",
            error
        );

        return null;

    }

}


// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

async function loadDashboard() {

    const data =
        await apiRequest(
            "/api/status"
        );


    if (!data) {

        console.log(
            "Backend not available."
        );

        return;

    }


    /*
    Update job count.
    */

    if (data.storage) {

        document.getElementById(
            "jobs-count"
        ).textContent =
            data.storage.jobs_count ?? 0;


        document.getElementById(
            "matches-count"
        ).textContent =
            data.storage.matches_count ?? 0;


        document.getElementById(
            "applications-count"
        ).textContent =
            data.storage.applications_count ?? 0;

    }


    console.log(
        "Dashboard data loaded:",
        data
    );

}


// ============================================================
// APPLICATION STARTUP
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadPageFromHash();

        loadDashboard();

    }
);


// ============================================================
// HANDLE BROWSER BACK/FORWARD
// ============================================================

window.addEventListener(
    "hashchange",
    loadPageFromHash
);