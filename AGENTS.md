<!-- markdownlint-disable MD013 MD025 -->

# AGENTS.md

Guidance for AI coding agents in **osm-export-tool**.
Human maintainers are accountable for all merged changes.

---

## Project

The Export Tool (export.hotosm.org) lets users export OpenStreetMap data for
an area of interest in GIS formats. It also runs scheduled exports for
humanitarian partners (including HDX), stores YAML feature-tag selections, and
authenticates users via OSM accounts.

**This is a long-lived Django service on older pinned dependencies.** Treat
version pins as deliberate: `Django~=3.2`, `djangorestframework~=3.11`,
`django-oauth-toolkit==1.3.2`, and the `hdx-python-*` pins are load-bearing.
Do not upgrade them as a side effect of another change.

**Stack:** Python / Django 3.2 / Django REST Framework / PostgreSQL + PostGIS /
dramatiq workers / Overpass API / React + OpenLayers built with webpack + yarn

---

## Required Reading Order

1. `docs/setup-development.md` - how to get a working local environment.
2. `CONTRIBUTING.md` - contribution rules, including AI tool usage.
3. `ops/README.md` - how this is actually deployed, if your change touches ops.
4. The app you are touching (`api/`, `jobs/`, `tasks/`, `hdx_exports/`, `ui/`).

---

## Structure

```text
core/settings/       # Django settings (base, project, contrib, utils)
api/                 # REST API: views, serializers, permissions, validators
jobs/                # Export job models and the export pipeline
tasks/               # dramatiq task runners, email, models
hdx_exports/         # HDX export sets and mailer
ui/                  # Django views plus the webpack/React frontend in ui/app
utils/               # shared helpers
ops/                 # deployment: Overpass, packer, systemd
docs/                # MkDocs documentation
locales/             # translations (managed via Transifex)
```

---

## Commands

```bash
pip install -r requirements-dev.txt   # dependencies
python manage.py migrate              # apply migrations (Postgres db: exports)
python manage.py runserver            # dev server

make test                             # pytest for hdx_exports
make django_test                      # Django tests: api, jobs, tasks
make test_all                          # the above plus ui.tests, verbose
make worker                            # run the dramatiq task runner
```

Frontend, from `ui/`:

```bash
yarn install
yarn start        # watch and recompile
yarn run dist     # production build
```

Translations are pulled and pushed through Transifex (`yarn run tx:pull`,
`yarn run tx:push`) - do not hand-edit files under `locales/`.

---

## Decisions Already Made

- **Dependency pins stay put.** This service runs on Django 3.2 and matching
  pinned libraries. A dependency bump is its own PR with its own testing, never
  a drive-by.
- **Overpass is an external dependency.** Export jobs read from an Overpass
  instance (see `ops/overpass`); the app does not hold its own OSM extract.
- **Exports run in dramatiq workers, not in request handlers.** An API call
  queues a job; nothing waits on export completion in-request.
- **Translations live in Transifex.** `locales/` is generated.

Approaches previously tried and rejected are not recorded in-repo. Ask a
maintainer rather than assuming a design is accidental.

---

## Where AI Help Is Welcome

- Tests for existing behaviour
- Documentation and docstrings
- Frontend components in `ui/app`
- Tightly scoped bug fixes with a reproducing test

## Where AI Must Not Act Unsupervised

- Authentication and OAuth (`django-oauth-toolkit`, `social-auth-*`, OSM login)
- API permissions and validators (`api/permissions.py`, `api/validators.py`)
- Database migrations
- The export pipeline and task runners (`jobs/`, `tasks/`)
- HDX publishing (`hdx_exports/`) - it writes to a live external platform
- Anything under `ops/`
- Dependency upgrades

---

## Coding Standards

- Match the surrounding code: this is an older codebase, and consistency beats
  modernisation.
- Use the ORM and DRF layers as they exist; no raw SQL where a query works.
- Geospatial correctness matters: be explicit about CRS and do not assume
  polygons are well-behaved.
- No new dependency without a clear reason and a maintainer's agreement.

---

## Testing Standards

- New behaviour needs a test in the matching `tests/` package
  (`api/tests`, `jobs/tests`, `tasks/tests`, `ui/tests`, `hdx_exports/tests`).
- Run `make test_all` before proposing a change to backend behaviour.
- Never weaken or skip a failing test to make a change pass.

---

## Anti-Patterns

- Upgrading or unpinning dependencies opportunistically
- Editing generated assets or `locales/` by hand
- Committing secrets; use `.env.example` as the reference
- Broad reformat-the-world diffs mixed into a behavioural change
- Long-running work inside a request handler

---

## Workflow

1. Read the relevant app and its tests before changing code.
2. Keep the diff scoped to the task; raise anything else separately.
3. Run the relevant test target and report exactly what you ran.
4. Report what you changed and what you did not verify.

When uncertain, ask instead of assuming.

---

## Responsible AI Contribution Policy

- Org guidance for AI-assisted contributions: <https://responsibleai.guide>
- Declare the AI assistance level (0-5) in the PR template honestly. Never
  lower the declared level to get a PR reviewed.
- If nobody has read the result, that is level 5: open the PR as a draft.
- Do not work on issues labelled `good first issue` - they exist for humans.
- A human is accountable for every merged change.
