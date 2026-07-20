import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()
username = os.environ["E2E_ADMIN_USERNAME"]
password = os.environ["E2E_ADMIN_PASSWORD"]
admin, _ = User.objects.get_or_create(
    username=username,
    defaults={"is_staff": True, "is_superuser": True},
)
admin.is_staff = True
admin.is_superuser = True
admin.set_password(password)
admin.save(update_fields=("password", "is_staff", "is_superuser"))
