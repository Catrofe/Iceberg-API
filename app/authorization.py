import datetime

import jwt
from fastapi import Header, HTTPException

from app.models import UserToken

KEY_TOKEN = "Apolo@ana@catrofe"


async def decode_token_jwt(authorization: str = Header()) -> UserToken:
    try:
        token = jwt.decode(
            authorization,
            KEY_TOKEN,
            leeway=datetime.timedelta(hours=+2),
            algorithms=["HS256"],
        )
        return UserToken(id=token["id"], type=token["type"])

    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(401, "INVALID_SIGNATURE")

    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(401, "TOKEN_HAS_EXPIRED")

    except jwt.exceptions.DecodeError:
        raise HTTPException(401, "TOKEN_INVALID")


async def encode_token_jwt(id: int, type: str) -> str:
    return jwt.encode(
        {
            "id": id,
            "type": type,
            "exp": datetime.datetime.now() + datetime.timedelta(hours=+2),
        },
        KEY_TOKEN,
        algorithm="HS256",
    )
