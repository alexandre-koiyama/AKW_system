from firebase_admin import auth
from fastapi import HTTPException, Request

def verify_token(request: Request):
    """Verify Firebase ID token sent from frontend."""
    token = request.cookies.get("session")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # contains email, uid, etc.
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
