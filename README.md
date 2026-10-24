# Salken

An e-commerce store built with Django. Shoppers can browse products by
category, search, choose product variations (color, size), keep a cart as a
guest or a logged-in user, check out, and leave reviews. Accounts are
activated by email.

Apps:

| App        | Responsibility                                               |
|------------|--------------------------------------------------------------|
| `accounts` | Registration, email activation, login, password reset, profile |
| `category` | Product categories                                           |
| `store`    | Product listing, detail, search, reviews, gallery            |
| `cart`     | Session and user carts, checkout summary                     |
| `orders`   | Order placement, payment capture, order confirmation         |

## Requirements

- Python 3.11
- No other services for local development: SQLite is the default database,
  and static files are served locally.

## Setup

```sh
git clone <this repository> salken
cd salken

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.lock   # pinned app + dev dependencies
cp .env.example .env               # optional; every value has a local default

python manage.py migrate
python manage.py createsuperuser   # optional, for the admin at /secure-login/
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

In development, emails (account activation, password reset, order receipts)
use Django's default SMTP backend. To print them to the console instead, add
`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` to your
local settings.

### With Docker

`docker-compose.yml` runs the app against PostgreSQL 16, the same database
engine as production:

```sh
docker compose up --build              # app on http://localhost:8000/
docker compose run --rm web pytest     # test suite against PostgreSQL
docker compose down -v                 # stop and delete the database volume
```

To run only the database and use it from a local `runserver`, start it with
`docker compose up -d db` and set `RDS_DB_NAME=salken` in `.env`.

The image runs Django's development server and is for local use only.

## Running tests

```sh
pytest                                                    # run the suite
make test                                                 # with coverage; fails below 90%
ruff check .                                              # lint
ruff format .                                             # format
pip-audit -r requirements.lock --no-deps --disable-pip    # vulnerabilities (pip install pip-audit)
```

Or run `make test` and `make lint`. CI (`.github/workflows/ci.yml`) runs lint,
the format check, tests on SQLite and PostgreSQL, a Docker build, and
`pip-audit` on every push to `master` and on every pull request.

Tests live in each app's `tests/` package. Shared fixtures (`product`,
`variations`, `user`, `password`) are in the top-level `conftest.py`.

## Health checks and logging

`GET /health/` returns `{"status": "ok", "database": "ok"}`, or a 503 when the
database is unreachable. Point the load balancer health check at it. It
responds before Django's host validation, so checks addressed to the instance
IP work without adding the IP to `ALLOWED_HOSTS`.

Application and Django logs go to stdout at `LOG_LEVEL` (default `INFO`).

## Configuration

`salken/settings.py` reads these values from the environment, or from a `.env`
file via python-decouple. See `.env.example`.

| Variable                  | Default                     | Purpose                              |
|---------------------------|-----------------------------|--------------------------------------|
| `DEBUG`                   | `True`                      | Set to `False` in production.        |
| `SECRET_KEY`              | insecure development key    | Required when `DEBUG=False`; the app refuses to start without it. |
| `HTTPS`                   | `False`                     | Set to `True` once served over TLS: HTTPS redirect, secure cookies, and HSTS. |
| `SECURE_HSTS_SECONDS`     | `3600`                      | Raise to `31536000` after HTTPS is confirmed working. |
| `ALLOWED_HOSTS`           | localhost + the EB hostname | Comma-separated.                     |
| `RDS_DB_NAME`             | unset (uses SQLite)         | When set, PostgreSQL is used along with `RDS_USERNAME`, `RDS_PASSWORD`, `RDS_HOSTNAME`, `RDS_PORT`. |
| `AWS_STORAGE_BUCKET_NAME` | unset (local static files)  | When set, static files go to S3, using `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. |

## Dependencies

- `requirements.txt` lists the app's direct runtime dependencies.
- `requirements-dev.txt` adds the test and lint tools.
- `requirements.lock` pins every transitive dependency. Install from it.

After you change `requirements*.txt`, regenerate the lockfile. `--exclude-newer`
skips releases published in the last two weeks, a basic guard against
compromised packages that are caught and pulled soon after release:

```sh
pip install uv
uv pip compile --upgrade --python-version 3.11 --universal \
  --exclude-newer "$(date -u -v-14d +%Y-%m-%d 2>/dev/null || date -u -d '14 days ago' +%Y-%m-%d)" \
  requirements-dev.txt -o requirements.lock
```

Dependabot opens one grouped update PR per week for Python packages and
GitHub Actions. It can bump `requirements*.txt` but not the lockfile, so
`tests/test_requirements.py` fails on its PRs until you check out the branch,
run the command above, and push the refreshed `requirements.lock`.

## Deployment

The project deploys to AWS Elastic Beanstalk (`.ebextensions/django.config`),
with PostgreSQL on RDS and static files on S3. In the Elastic Beanstalk
environment, set `SECRET_KEY`, `DEBUG=False`, the `RDS_*` variables, and the
`AWS_*` variables, plus `HTTPS=True` if the environment has a TLS listener.

To check a production configuration locally:

```sh
DEBUG=False HTTPS=True SECRET_KEY=<long random value> python manage.py check --deploy
```
