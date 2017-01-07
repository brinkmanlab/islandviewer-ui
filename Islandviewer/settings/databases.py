import env, os

if 'TRAVIS' in os.environ:
    SECRET_KEY = "SecretKeyForUseOnTravis"
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'travisci',
            'USER':     'travis',
#            'PASSWORD': '',
            'HOST':     '127.0.0.1',
#            'PORT':     '',
        }
    }
else:
    import secrets
    DATABASES = {
       'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': secrets.IV_DATABASE,
    #        'NAME': '/home/lairdm/workspace/Islandviewer/sqlite.db',                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': secrets.DATABASE_USER,
            'PASSWORD': secrets.DATABASE_PASSWORD,
            'HOST': secrets.DATABASE_HOST,                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': secrets.DATABASE_PORT,                      # Set to empty string for default.
        },
        'microbedb': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'microbedbv2',
            'USER': secrets.DATABASE_USER,
            'PASSWORD': secrets.DATABASE_PASSWORD,
            'HOST': secrets.DATABASE_HOST,
            'PORT': secrets.DATABASE_PORT,
        }
    }
