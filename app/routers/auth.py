# Authentication routes
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import RedirectResponse
from firebase_admin import auth
import os
import requests

router = APIRouter()

@router.get("/login")
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(email: str = Form(...), password: str = Form(...), response: Response = None):
    """
    Firebase does not allow email/password login from backend.
    We use the REST API: https://identitytoolkit.googleapis.com/
    """
    api_key = os.getenv("FIREBASE_API_KEY")
    if not api_key:
        # Render login page with a clear error message when API key is missing
        return {
            "error": "FIREBASE_API_KEY is not set. Create a .env with FIREBASE_API_KEY=... or export it in your shell."
        }
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(url, json=payload)
    data = r.json()

    if "idToken" not in data:
        return {"error": "Invalid credentials"}

    session_token = data["idToken"]

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("session", session_token, httponly=True, max_age=3600*24)
    return response


@router.get("/register")
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register_post(email: str = Form(...), password: str = Form(...), response: Response = None):
    try:
        user = auth.create_user(email=email, password=password)
    except Exception as e:
        return {"error": str(e)}

    return RedirectResponse("/login", status_code=302)


@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("session")
    return response
