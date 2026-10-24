# Build all services
run:
	python3 manage.py runserver

# Run django makemigrations.
migrations:
	python3 manage.py makemigrations

# Run django migrate.
migrate:
	python3 manage.py migrate

# Run django collectstatic
collectstatic:
	python3 manage.py collectstatic

# Run the test suite with coverage.
test:
	python3 -m pytest --cov=accounts --cov=cart --cov=orders --cov=store

# Lint the Django apps.
lint:
	python3 -m ruff check .
	python3 -m ruff format --check .

# Format Python code.
format:
	python3 -m ruff format .
