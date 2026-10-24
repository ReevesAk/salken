# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-24

The first tagged release. Before this, most user-facing flows crashed. This
release makes them work, puts them under test, and adds the tooling to keep
them working.

### Upgrade notes

- **Python 3.10 or newer is required** (Django 5.2).
- **`DEBUG=False` now requires `SECRET_KEY`.** The app refuses to start
  without it instead of running on a public fallback key.
- **`RDS_*` values in `.env` are now read.** Previously only real environment
  variables were, so a `.env`-configured PostgreSQL silently fell back to
  SQLite.
- Point the load balancer health check at `/health/`.
- Optional: `HTTPS=True` (redirect, secure cookies, HSTS), `SENTRY_DSN`
  (error tracking), `LOG_FORMAT` (`json` or `text`).

### Security

- Customers could view other customers' orders (name, address, phone, items)
  on the order detail page. Orders are now scoped to their owner (#1).
- Upgrade Django 4.1.5 (end of life, known vulnerabilities) to 5.2 LTS (#2).
- Upgrade Pillow to 13.0.0, which fixes critical image-decoding advisories
  reachable through profile picture uploads, along with pytest (#8) and
  certifi (#12), and refresh the other dependencies (#2).
- Validate login input with a form, follow `?next=` only to same-site URLs,
  and escape the admin profile thumbnail (#1).
- Production settings: required `SECRET_KEY`, opt-in HTTPS hardening, and
  `check --deploy` enforced by a test (#4).
- CI audits `requirements.lock` with pip-audit (#8).

### Fixed

- Registration, login, password reset, account activation, profile editing,
  and the dashboard (#1).
- Add to cart, cart quantity and removal, merging the guest cart on login,
  and new visitors getting a `None` cart id (#1).
- Home page, store listing, product detail, search, reviews, checkout, order
  placement, and payment capture (#1).
- S3 static file storage, which Django 5.1 would have silently ignored (#2).
- Product gallery images can be managed from the product admin page (#2).
- `.env` database settings being ignored (#9).
- The cart badge querying the cart and starting a session on admin pages (#10).
- Console logging writing to stderr instead of stdout (#12).

### Added

- Test suite: pytest-django, 140 tests, 97% coverage, and a 90% coverage gate
  (#1, #10).
- GitHub Actions CI: lint, format check, tests on SQLite and PostgreSQL,
  Docker build, dependency audit, and lockfile freshness (#1, #6, #7, #8, #11).
- `requirements.lock` with transitive pins, Dependabot, and lockfile sync
  checks (#1, #3, #11).
- `/health/` endpoint with a database check (#5).
- JSON logs in production and optional Sentry error tracking (#5, #12).
- Dockerfile and Docker Compose with PostgreSQL 16 (#6).
- README setup guide and `.env.example` (#1, #9).

### Changed

- Code formatted with `ruff format`, enforced in CI (#7).
- Duplicated cart variation lookup extracted into `_resolve_variations()` (#1).

### Removed

- Unused `django-admin-honeypot` and `requests` dependencies (#2).
- Unused `salken/media_storage.py` (#10).

[Unreleased]: https://github.com/ReevesAk/salken/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ReevesAk/salken/releases/tag/v1.0.0
