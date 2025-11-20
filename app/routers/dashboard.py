# Dashboard routes
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.firebase.auth import verify_token

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request):
    try:
        user = verify_token(request)
    except HTTPException as e:
        if e.status_code == 401:
            return RedirectResponse("/login", status_code=302)
        raise

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )
