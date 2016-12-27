from webui.models import UserToken
import os, uuid
from datetime import datetime, timedelta

def generate_token(user, usertoken = None):
    
    if not usertoken:
        usertoken = UserToken(user=user)

    token = uuid.UUID(bytes = os.urandom(16))

    usertoken.token = token
    
    usertoken.save()
    
    return usertoken

def reset_token(usertoken):

    token = uuid.UUID(bytes = os.urandom(16))

    usertoken.token = token

    usertoken.expires = datetime.now()+timedelta(days=30)
    
    usertoken.save()
    
    return usertoken
