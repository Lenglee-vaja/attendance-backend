from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your_secret_key"
def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message
    }
def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }

def ResponseLogin(token, user, message):
    return {
        "data": {
            "user":user,
            "token": token
        },
        "code": 200,
        "message": message
    }

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "payload": payload}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_student(token: str = Depends(oauth2_scheme)) -> dict:
    result = verify_token(token)
    return result["payload"]
