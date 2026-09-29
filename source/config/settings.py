from pathlib import Path
import os
import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, True)
)

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings
SECRET_KEY = env('SECRET_KEY', default='django-insecure-ea8cs3!!7uy52k8!2%3x$#-$myi^&9^u*vl(*e=(63vy#=x9zz')

DEBUG = env('DEBUG', default=True)
# ============================================================
# MICROSOFT ENTRA ID / SSO CONFIGURATION
# ============================================================

ENTRA_CLIENT_ID = env('ENTRA_CLIENT_ID', default='')
ENTRA_CLIENT_SECRET = env('ENTRA_CLIENT_SECRET', default='')
ENTRA_TENANT_ID = env('ENTRA_TENANT_ID', default='')
ENTRA_REDIRECT_URI = env(
    'ENTRA_REDIRECT_URI',
    default='http://127.0.0.1:8000/api/accounts/sso/entra/callback/'
)

ALLOWED_HOSTS = [
    'enterprise-human-resource-management.onrender.com',
    'localhost',
    '127.0.0.1',
    '[::1]',
    '*'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'accounts',
    'organization',
    'leave',
    'claims',
    'hrms_modules',
    'recruitment',
    'payroll',
    'documents',
    'assets',
    'performance',
    'compliance',
    'training',
    'attendance_shifts',
    'authorization',
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Explicit and safe database configuration pointing strictly to local sqlite3 file
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'config.jwt_authentication.SecureJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login': '5/minute',
        'token_refresh': '10/minute',
    },
}

# ============================================================
# JWT SECURITY CONFIGURATION
# ============================================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    'AUTH_HEADER_TYPES': ('Bearer',),

    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
    ),

    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ---------------------------------------------------------------------------
# SECURITY: TRUSTED REVERSE PROXIES
# ---------------------------------------------------------------------------
#
# Empty by default. X-Forwarded-For is therefore NOT trusted unless
# a known reverse proxy/load balancer is explicitly configured here.
#
# Example:
# TRUSTED_PROXY_IPS = [
#     "10.0.0.10",
#     "10.0.0.0/24",
# ]
#
TRUSTED_PROXY_IPS = []

# Development email backend.
# Password-reset emails are displayed in the terminal during local testing.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@enterprise-hrms.local"

