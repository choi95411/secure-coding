from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import LoginThrottle


def login_identifier(username, remote_addr):
    value = f"{username.strip().casefold()}|{remote_addr or 'unknown'}"
    return salted_hmac("login-throttle", value).hexdigest()


def is_login_locked(identifier_hash):
    throttle = LoginThrottle.objects.filter(identifier_hash=identifier_hash).first()
    return bool(throttle and throttle.locked_until and throttle.locked_until > timezone.now())


@transaction.atomic
def record_login_failure(identifier_hash):
    now = timezone.now()
    window_seconds = int(getattr(settings, "LOGIN_FAILURE_WINDOW_SECONDS", 300))
    max_failures = int(getattr(settings, "LOGIN_MAX_FAILURES", 5))
    lock_seconds = int(getattr(settings, "LOGIN_LOCK_SECONDS", 900))
    try:
        throttle = LoginThrottle.objects.select_for_update().get(identifier_hash=identifier_hash)
    except LoginThrottle.DoesNotExist:
        try:
            # Isolate a concurrent unique-key collision in a savepoint so the
            # surrounding transaction remains usable for the locked retry.
            with transaction.atomic():
                throttle = LoginThrottle.objects.create(
                    identifier_hash=identifier_hash,
                    window_started_at=now,
                )
        except IntegrityError:
            throttle = LoginThrottle.objects.select_for_update().get(
                identifier_hash=identifier_hash
            )
    if throttle.window_started_at < now - timedelta(seconds=window_seconds):
        throttle.failures = 0
        throttle.window_started_at = now
        throttle.locked_until = None
    throttle.failures += 1
    if throttle.failures >= max_failures:
        throttle.locked_until = now + timedelta(seconds=lock_seconds)
    throttle.save()
    return throttle


def clear_login_failures(identifier_hash):
    LoginThrottle.objects.filter(identifier_hash=identifier_hash).delete()
