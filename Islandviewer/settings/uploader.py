import env

if env.PROD_ENV:
    ISLANDVIEWER_HOST = 'localhost'
    ISLANDVIEWER_PORT = 8211
elif env.TEST_ENV:
    ISLANDVIEWER_HOST = 'localhost'
    ISLANDVIEWER_PORT = 8212
else:
    # DEV_ENV
    ISLANDVIEWER_HOST = 'localhost'
    ISLANDVIEWER_PORT = 8211

