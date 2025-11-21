from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from firebase_admin import auth
import os
import requests

router = APIRouter()

@router.get("/login")
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(email: str = Form(...), password: str = Form(...)):
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        return {"error": "FIREBASE_API_KEY not set"}
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
    data = r.json()

    if "idToken" not in data:
        return {"error": "Invalid credentials"}

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("session", data["idToken"], httponly=True, max_age=86400)
    return response

@router.get("/register")
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_post(email: str = Form(...), password: str = Form(...)):
    try:
        auth.create_user(email=email, password=password)
    except Exception as e:
        return {"error": str(e)}
    return RedirectResponse("/login", status_code=302)

@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("session")
    return response
