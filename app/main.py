from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from app.routers import auth, dashboard

app = FastAPI()

# Load environment variables (e.g., FIREBASE_API_KEY)
load_dotenv()

# Optionally initialize Firebase if configured
try:
    # Importing config triggers firebase_admin.initialize_app
    from app import config as _config  # noqa: F401
except Exception as e:
    # Don't crash the app if credentials are not set yet
    print(f"[init] Firebase not initialized: {e}")

# Attach templates
app.state.templates = Jinja2Templates(directory="app/templates")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes
app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return RedirectResponse("/login")