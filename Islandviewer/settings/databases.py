import env, os, sys

if 'TRAVIS' in os.environ:
    SECRET_KEY = "SecretKeyForUseOnTravis"
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'travisci',
            'USER':     'travis',
            'HOST':     '127.0.0.1',
         },
        'microbedb': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'travisci',
            'USER':     'travis',
            'HOST':     '127.0.0.1',
        }
    }
elif 'test' in sys.argv or 'test_coverage' in sys.argv:
    import secrets
    DATABASES = {
       'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': secrets.IV_DATABASE,
            'USER': secrets.DATABASE_USER,
            'PASSWORD': secrets.DATABASE_PASSWORD,
            'HOST': secrets.DATABASE_HOST,                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': secrets.DATABASE_PORT,                      # Set to empty string for default.
         },
        'microbedb': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': secrets.IV_DATABASE,
            'USER': secrets.DATABASE_USER,
            'PASSWORD': secrets.DATABASE_PASSWORD,
            'HOST': secrets.DATABASE_HOST,
            'PORT': secrets.DATABASE_PORT,
        }
    }
else:
    import secrets
    DATABASES = {
       'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': secrets.IV_DATABASE,
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
