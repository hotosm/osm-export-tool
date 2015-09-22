DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'hot_exports_dev',
        'OPTIONS': {
            'options': '-c search_path=exports,public',
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': None,
        'USER': 'hot',
    }
}