# College Application Tracker

College Application Tracker is a Django web application that helps students organize college research and application progress in one place. Instead of juggling spreadsheets, browser bookmarks, and sticky notes for deadlines, users can browse a searchable college catalog, save schools to a personal list, update each school's application status over time, and keep a per-school checklist of remaining work (essays, recommendations, portal uploads, and similar steps).

The main user flow is: register or log in, optionally save search preferences (state, campus setting, climate, size, meal options, athletics, financial aid, and extracurricular interests), discover colleges from the shared catalog, optionally filter that catalog against those preferences, add interesting colleges to “My Colleges,” track status changes (researching, applying, submitted, accepted, rejected, or deferred), and manage checklist tasks on each college’s detail page. Live countdown timers on the dashboard, list, and detail views keep deadlines visible without refreshing the page constantly.

The interface is intentionally straightforward and mobile-friendly: Bootstrap provides the layout grid and components, while custom CSS and JavaScript handle the sidebar layout, responsive offcanvas navigation on small screens, deadline countdowns, and asynchronous task completion toggles.

## Distinctiveness and Complexity

This project is distinct from the earlier CS50 Web assignments both in domain and in how the pieces fit together. Project 0 is a static Google-style search front end with no server models. Project 1 (Wiki) is collaborative Markdown encyclopedia editing with a single primary content type. Project 2 (Commerce) is an auction marketplace with listings, bids, and watchlists. Project 3 (Mail) is a single-page email client driven by a JSON API. Project 4 (Network) is a Twitter-like social feed with posts, follows, and likes. College Application Tracker is none of those products. It is a personal planning tool: a shared reference catalog of colleges combined with private, per-user application records, preference profiles, and task lists. There is no social graph, no public feed, no bidding, and no email composition metaphor. A student using this app is organizing their own admissions process, not publishing content for other users to consume.

The complexity comes from combining several course topics into one coherent workflow rather than from a single flashy feature. On the data side, colleges are global objects curated through Django admin, while applications, preferences, and tasks are user-scoped and linked through foreign keys and a one-to-one profile. Uniqueness constraints prevent duplicate applications for the same user and college. Signals create a preference profile when a user registers so preference editing never depends on a missing row. On the query side, catalog browsing supports multi-token fuzzy search across many college text fields (name, location, state, institution type, climate, meals, extracurriculars, housing, sports, and free-form search notes), plus an optional “Match my preferences” mode that applies the saved profile as structured filters before the keyword search runs. Results are annotated so newly added colleges surface first, then paginated.

The authenticated experience spans multiple pages with different jobs: a dashboard that aggregates status metrics and upcoming deadlines; an all-colleges browser with search, preference matching, and pagination; a personal list sorted by deadline; a preference editor; and college detail pages that combine profile-style campus information with application status controls and a checklist UI. Status updates and list add/remove actions use POST forms with safe `next` redirects. Checklist completion uses JavaScript `fetch` with CSRF headers so toggling a checkbox does not require a full page reload, while creating and deleting tasks remains ordinary form POSTs for reliability.

Compared with a thin CRUD demo, the project therefore requires thinking about shared versus private data, search and filtering semantics, pagination, authentication boundaries, admin curation of the catalog, responsive navigation, and a mix of server-rendered pages with targeted client-side behavior. That combination is intentionally more involved than any single earlier project, while remaining clearly outside the social-network and e-commerce shapes the staff warn against.

## What’s contained in each file

Top-level project files:

- `manage.py`: Django management entry point for running the server, migrations, tests, and admin tasks.
- `README.md`: this writeup, including distinctiveness, setup, and staff notes.
- `requirements.txt`: Python package dependencies required to run the project.
- `.gitignore`: ignores virtualenvs, SQLite databases, caches, and local tooling folders.

Project configuration (`capstone/`):

- `capstone/settings.py`: Django settings (installed apps including `tracker.apps.TrackerConfig`, templates, SQLite database, static files, auth redirects).
- `capstone/urls.py`: root URL routing (admin site plus tracker app routes).
- `capstone/asgi.py` and `capstone/wsgi.py`: deployment entry points for ASGI/WSGI servers.
- `capstone/__init__.py`: package marker.

Main app (`tracker/`):

- `tracker/models.py`: `College` (catalog), `Application` (user–college status), `Task` (per-application checklist items), and `UserProfile` (saved search preferences).
- `tracker/views.py`: dashboard metrics, fuzzy search helpers, preference matching, catalog/detail/list pages, auth views, preference save, and task JSON/form endpoints.
- `tracker/urls.py`: app routes mapped to those views.
- `tracker/admin.py`: admin configuration for colleges, applications (with task inlines), tasks, and profiles.
- `tracker/apps.py`: app config that loads signals on startup.
- `tracker/signals.py`: creates a `UserProfile` when a new user is created.
- `tracker/context_processors.py`: injects the college sidebar list into authenticated templates.
- `tracker/tests.py`: automated tests for fuzzy search, preference filtering, apply/task flow, and profile signals.
- `tracker/migrations/`: schema migration history.
- `tracker/templates/tracker/`: HTML templates for layout, dashboard, catalog, my colleges, detail (including checklist), preferences, login, and register.
- `tracker/static/tracker/css/styles.css`: custom layout, sidebar, mobile breakpoints, and task/countdown styling.
- `tracker/static/tracker/js/app.js`: client-side deadline countdowns and CSRF-aware task toggle requests.

## How to run the application

1. Open a terminal in the project directory (the folder that contains `manage.py`).

2. Create and activate a virtual environment:

   - `python3 -m venv .venv`
   - macOS/Linux: `source .venv/bin/activate`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`

3. Install dependencies:

   - `pip install -r requirements.txt`

4. Apply database migrations:

   - `python manage.py migrate`

5. Create an admin user (recommended so you can add colleges):

   - `python manage.py createsuperuser`

6. Start the development server:

   - `python manage.py runserver`

7. Open `http://127.0.0.1:8000/` in a browser. Register a student account, then use `/admin/` with the superuser to add college catalog rows. After colleges exist, browse All colleges, optionally enable “Match my preferences,” add schools to your list, update statuses, and manage checklist tasks on each college detail page.

8. Run automated tests (optional but useful):

   - `python manage.py test tracker`

## Additional information for staff

- **Database:** local development uses SQLite (`db.sqlite3`), created after migrations. The database file is gitignored and is not part of the submission artifact.
- **Catalog data:** colleges are intended to be entered through Django admin. Fields such as institution type, state, setting, climate, size, meals, housing, sports, extracurriculars, financial-aid availability, and search notes both display on detail pages and participate in fuzzy search / preference matching.
- **Preferences:** saving preferences alone does not hide colleges until the user checks “Match my preferences” on All colleges. That keeps browsing the full catalog available while still offering a personalized filter when wanted.
- **JavaScript behavior:** `app.js` updates `.countdown` elements from `data-deadline` attributes about once a minute, and toggles task completion via `PUT` to `/api/task/<id>/toggle` with an `X-CSRFToken` header. Creating and deleting tasks uses normal POST forms.
- **Mobile layout:** the authenticated shell uses a sticky desktop sidebar and a Bootstrap offcanvas menu on smaller viewports, with CSS tweaks for status controls and preference cards.
- **Scope:** this project targets local demonstration. Production deployment would need environment-based secrets, hardened settings, and a production-grade database.
- **Honesty note on tooling:** generative AI was used only as allowed for helping draft and expand this `README.md`. Application code was written and revised as part of the project implementation itself.
