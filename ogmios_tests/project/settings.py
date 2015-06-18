
SECRET_KEY = 'some secret key'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
    }
]

INSTALLED_APPS = (
    'app',
)
