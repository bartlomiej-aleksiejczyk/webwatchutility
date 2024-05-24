import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

User = get_user_model()

superuser_username = os.getenv("DJANGO_SUPERUSER_USERNAME")
superuser_email = os.getenv("DJANGO_SUPERUSER_EMAIL")
superuser_password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(username=superuser_username).exists():
    User.objects.create_superuser(
        username=superuser_username, email=superuser_email, password=superuser_password
    )
    print(f"Superuser {superuser_username} created")
else:
    print(f"Superuser {superuser_username} already exists")
