from django.core.management import call_command


def test_system_checks_pass():
    call_command('check', fail_level='WARNING')


def test_models_have_no_missing_migrations(db):
    call_command('makemigrations', '--check', '--dry-run', verbosity=0)
