import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SECRET_KEY = "local-calculator-suite"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
ROOT_URLCONF = "frontends.django_web.urls"
INSTALLED_APPS = [
    "frontends.django_web",
]
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(os.path.dirname(__file__), "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    }
]
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
