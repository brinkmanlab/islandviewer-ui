import env

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'my_secret_key'

IV_DATABASE = 'islandviewerV4'
DATABASE_USER = 'db_app_user'
DATABASE_PASSWORD = 'db_app_pw'
DATABASE_HOST = 'full_hostname_of_db_instance'

DATABASE_PORT = '3306'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/islandviewer/'
SOCIAL_AUTH_LOGIN_URL = '/islandviewer/'

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True


##--- GOOGLE
# Brinkman Lab organisation account secrets for Google:
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'longrandomcharacterstringfromgoole.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'secretcharacterstringfromgoogle'


##--- TWITTER
# Brinkman Lab organisation account secrets for Twitter:
SOCIAL_AUTH_TWITTER_KEY = 'randomcharacterstringfromtwitter'
SOCIAL_AUTH_TWITTER_SECRET = 'secretcharacterstringfromtwitter'


##--- GITHUB
# BrinkmanLab organisation account secrets:
SOCIAL_AUTH_GITHUB_KEY = 'randomcharacterstringfromgithub'
SOCIAL_AUTH_GITHUB_SECRET = 'secretcharacterstringfromgithub'
