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

## Running tests

```sh
pytest                                                    # run the suite
pytest --cov=accounts --cov=cart --cov=orders --cov=store # with coverage
ruff check .                                              # lint
```

Or run `make test` and `make lint`. CI (`.github/workflows/ci.yml`) runs the
lint and test steps on every push to `master` and on every pull request.

Tests live in each app's `tests/` package. Shared fixtures (`product`,
`variations`, `user`, `password`) are in the top-level `conftest.py`.

## Configuration

`salken/settings.py` reads these values from the environment, or from a `.env`
file via python-decouple. See `.env.example`.

| Variable                  | Default                     | Purpose                              |
|---------------------------|-----------------------------|--------------------------------------|
| `SECRET_KEY`              | insecure development key    | **Set in production.**               |
| `DEBUG`                   | `True`                      | Set to `False` in production.        |
| `ALLOWED_HOSTS`           | localhost + the EB hostname | Comma-separated.                     |
| `RDS_DB_NAME`             | unset (uses SQLite)         | When set, PostgreSQL is used along with `RDS_USERNAME`, `RDS_PASSWORD`, `RDS_HOSTNAME`, `RDS_PORT`. |
| `AWS_STORAGE_BUCKET_NAME` | unset (local static files)  | When set, static files go to S3, using `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. |

## Dependencies

- `requirements.txt` lists the app's direct runtime dependencies.
- `requirements-dev.txt` adds the test and lint tools.
- `requirements.lock` pins every transitive dependency. Install from it.

After you change `requirements*.txt`, regenerate the lockfile:

```sh
pip install uv
uv pip compile --python-version 3.11 --universal requirements-dev.txt -o requirements.lock
```

## Deployment

The project deploys to AWS Elastic Beanstalk (`.ebextensions/django.config`),
with PostgreSQL on RDS and static files on S3. In the Elastic Beanstalk
environment, set `SECRET_KEY`, `DEBUG=False`, the `RDS_*` variables, and the
`AWS_*` variables.
