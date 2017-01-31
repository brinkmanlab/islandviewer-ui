import env

if env.PROD_ENV:
    ISLANDVIEWER_HOST = 'controlbk'
    ISLANDVIEWER_PORT = 8213
elif env.TEST_ENV:
    ISLANDVIEWER_HOST = 'controlbk'
    ISLANDVIEWER_PORT = 8214
else:
    # DEV_ENV
    ISLANDVIEWER_HOST = 'controlbk'
    ISLANDVIEWER_PORT = 8214

