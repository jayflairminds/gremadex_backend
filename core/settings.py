"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-z9l*oq)v(agbsp3uj%^wat4t4oer=og5btdnzj-tezxuisoiob"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "knox",
    "users",
    "construction",
    "corsheaders",
    "doc_summary_qna",
    "document_management",
    "alerts",
    # "user_payments",
    "user_payments.apps.UserPaymentsConfig"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware"
]

CORS_ORIGIN_ALLOW_ALL = True 
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
# For specific URLs
# CORS_ALLOWED_ORIGINS = [
#     'https://example.com',
#     'https://another-domain.com',
# ]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'build')],
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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST")
    }
}

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SIGNING_SECRET = os.getenv("WEBHOOK_SIGNING_SECRET")

# MONGODB = {
#     'URI': f"mongodb+srv://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@cluster0.jfno3.mongodb.net/",
#     'DATABASE_NAME': os.getenv('MONGODB_DATABASE_NAME')
# }

MONGODB = {
    'NAME': os.getenv('MONGODB_DATABASE_NAME'),
    'HOST': os.getenv('MONGODB_DATABASE_HOST'),
    'PORT': int(os.getenv('MONGODB_PORT')),
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "assets/"
# Add the path to your React build folder
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'build/assets'),  # Adjust the path as needed
]

# Specify the directory where static files will be collected
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",),
    'COERCE_DECIMAL_TO_STRING': False
}

EMAIL_CONFIG = {
    'BACKEND': os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
    'HOST': os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
    'PORT': int(os.getenv('EMAIL_PORT')),
    'USE_TLS': os.getenv('EMAIL_USE_TLS'),
    'HOST_USER': os.getenv('EMAIL_HOST_USER'),
    'HOST_PASSWORD': os.getenv('EMAIL_HOST_PASSWORD'),
    'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL'),
}

EMAIL_BACKEND = EMAIL_CONFIG['BACKEND']
EMAIL_HOST = EMAIL_CONFIG['HOST'] # Gmail SMTP server
EMAIL_PORT = EMAIL_CONFIG['PORT'] # Port for TLS
EMAIL_USE_TLS = EMAIL_CONFIG['USE_TLS'] # Use TLS for secure connection
EMAIL_HOST_USER = EMAIL_CONFIG['HOST_USER'] # Your Gmail address
EMAIL_HOST_PASSWORD = EMAIL_CONFIG['HOST_PASSWORD'] # Your Gmail password or app password
DEFAULT_FROM_EMAIL = EMAIL_CONFIG['DEFAULT_FROM_EMAIL'] # The default 'From' email address