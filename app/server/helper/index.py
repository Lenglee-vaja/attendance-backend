from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()
from jwt import PyJWTError
from server.controller.student import SECRET_KEY
import jwt
def ResponseRegister(data,token, message):
    return {
        "data": data,
        "token": token,
        "code": 200,
        "message": message
    }
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message
    }

def ResponseModels(data, message):
    return {
        "data": data,
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

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    
def verify_jwt_token_and_role(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role"] == "teacher":
            return payload
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
