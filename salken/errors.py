import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# init_error_tracking reports unhandled exceptions to Sentry. It does nothing
# when dsn is empty, so local development and tests never send events.
# Returns whether tracking was enabled.
def init_error_tracking(dsn, environment, traces_sample_rate=0.0):
    if not dsn:
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[DjangoIntegration()],
        traces_sample_rate=traces_sample_rate,
        # Don't attach user emails, IPs, cookies, or request bodies to events.
        send_default_pii=False,
    )
    return True
