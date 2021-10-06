import os
import paths
import env

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
#if env.TEST_ENV:
#    STATIC_URL = '/islandviewer4_dev/static/'
#    PIPELINE = 'islandviewerv4_dev'
#else:
STATIC_URL = '/islandviewer/static/'
PIPELINE = 'islandviewerv4'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(paths.BASE_DIR, 'static'), 

)

#STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = ''

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
