import os
from pathlib import Path

# ✅ Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Secret Key (Keep Secure - Use Environment Variable)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")  # Update in production

# ✅ Debug Mode - Keep False in Production!
DEBUG = True  # Change to False in production

# ✅ Allowed Hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # Add your production domain if needed

# ✅ Installed Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "users",
    "django_extensions",
]

# ✅ Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ✅ Root URL Configuration
ROOT_URLCONF = "password_manager.urls"

# ✅ Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ✅ WSGI Application
WSGI_APPLICATION = "password_manager.wsgi.application"

# ✅ Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ Custom User Model
AUTH_USER_MODEL = "users.CustomUser"

# ✅ Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ✅ Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ✅ Static Files
STATIC_URL = "/assets/"
# IMAGE UPLOAD DIR
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ✅ Default Primary Key Type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ✅ Django REST Framework & JWT Authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
}


# ✅ Add this in settings.py
CORS_ALLOW_CREDENTIALS = True  # Allow cookies & auth headers
CORS_ALLOW_ALL_ORIGINS = False  # Disable unrestricted access
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Your frontend URL
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Add this line for your current frontend URL
]

CORS_ALLOW_METHODS = [  # Allow these HTTP methods
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = [  # Allow these headers
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=24
    ),  # Set access token expiration time to 24 hours
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=7
    ),  # Optional: Set refresh token expiration time (default is 7 days)
    "ROTATE_REFRESH_TOKENS": False,  # Optional: Configure whether to rotate refresh tokens
    "BLACKLIST_AFTER_ROTATION": True,  # Optional: Configure whether to blacklist the refresh token after rotation
}


# settings.py

# Email settings for sending emails through Gmail SMTP server
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"  # Use SMTP for sending emails
)
EMAIL_HOST = "smtp.gmail.com"  # Gmail's SMTP server
EMAIL_PORT = 587  # Port for sending emails over TLS
EMAIL_USE_TLS = True  # Enable TLS for encryption during email transmission
EMAIL_HOST_USER = "bbramadhikari@gmail.com"  # Your Gmail address
EMAIL_HOST_PASSWORD = (
    "sjbu texf yxtp fuve"  # Your Gmail password or app-specific password
)
DEFAULT_FROM_EMAIL = "bbramadhikari@gmail.com"  # The sender email address
