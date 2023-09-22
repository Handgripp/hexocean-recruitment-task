import jwt
from datetime import datetime
from django.conf import settings
from decouple import config


def validate_jwt_token(token):
    try:
        decoded_token = jwt.decode(
            token,
            config('SIGNING_KEY'),
            algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
        )

        if 'exp' in decoded_token:
            expiration_timestamp = decoded_token['exp']
            current_timestamp = datetime.utcnow().timestamp()
            if current_timestamp > expiration_timestamp:
                return False
        return decoded_token
    except jwt.ExpiredSignatureError:
        return False
    except jwt.DecodeError:
        return False
