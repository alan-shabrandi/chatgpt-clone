from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
import psycopg2
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config import GOOGLE_CLIENT_ID, COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from schemas import UserRegister, GoogleAuthRequest
from security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/register")
async def register(user: UserRegister):
    hashed_pwd = hash_password(user.password)
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                    (user.username, hashed_pwd)
                )
                conn.commit()
        return {"message": "User registered successfully"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username already exists")

@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hashed_password FROM users WHERE username = %s", (form_data.username,))
            user = cur.fetchone()
        
    if not user or user[0] == "OAUTH_GOOGLE_USER" or not verify_password(form_data.password, user[0]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    access_token = create_access_token(data={"sub": form_data.username})
    
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"message": "Login successful"}

@router.post("/auth/google")
async def auth_google(response: Response, auth_data: GoogleAuthRequest):
    try:
        id_info = id_token.verify_oauth2_token(
            auth_data.token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        google_email = id_info.get("email")
        if not google_email:
            raise HTTPException(status_code=400, detail="Google account has no email.")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE username = %s", (google_email,))
            user = cur.fetchone()
            
            if not user:
                cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                    (google_email, "OAUTH_GOOGLE_USER")
                )
                conn.commit()

    access_token = create_access_token(data={"sub": google_email})
    
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"message": "Google login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}