from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from app.routers import auth, dashboard, groups

app = FastAPI()
load_dotenv()

try:
    from app import config as _config
except Exception as e:
    print(f"Firebase init error: {e}")

app.state.templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(groups.router)

@app.get("/")
def home():
    return RedirectResponse("/login")