from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from firebase_admin import firestore
from app.firebase.auth import verify_token
from app.config import db

router = APIRouter()

@router.get("/groups")
def groups_page(request: Request):
    return RedirectResponse("/dashboard", status_code=302)

@router.post("/groups/create")
def create_group(name: str = Form(...), description: str = Form(""), request: Request = None):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    db.collection('groups').add({
        'name': name,
        'description': description,
        'user_email': user['email'],
        'created_at': firestore.SERVER_TIMESTAMP
    })
    return RedirectResponse("/dashboard", status_code=302)

@router.get("/groups/{group_id}")
def group_detail(group_id: str, request: Request):
    return RedirectResponse(f"/dashboard?group_id={group_id}", status_code=302)

@router.post("/groups/{group_id}/cameras/add")
def add_camera(group_id: str, name: str = Form(...), rtsp_url: str = Form(...), description: str = Form(""), request: Request = None):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    group_doc = db.collection('groups').document(group_id).get()
    if not group_doc.exists or group_doc.to_dict().get('user_email') != user['email']:
        raise HTTPException(status_code=404)
    
    db.collection('cameras').add({
        'name': name,
        'rtsp_url': rtsp_url,
        'description': description,
        'group_id': group_id,
        'status': 'offline',
        'created_at': firestore.SERVER_TIMESTAMP
    })
    return RedirectResponse(f"/dashboard?group_id={group_id}", status_code=302)

@router.post("/groups/{group_id}/delete")
def delete_group(group_id: str, request: Request = None):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    group_doc = db.collection('groups').document(group_id).get()
    if group_doc.exists and group_doc.to_dict().get('user_email') == user['email']:
        for camera_doc in db.collection('cameras').where('group_id', '==', group_id).stream():
            camera_doc.reference.delete()
        db.collection('groups').document(group_id).delete()
    
    return RedirectResponse("/dashboard", status_code=302)

@router.post("/cameras/{camera_id}/delete")
def delete_camera(camera_id: str, request: Request = None):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    camera_doc = db.collection('cameras').document(camera_id).get()
    if camera_doc.exists:
        group_id = camera_doc.to_dict().get('group_id')
        group_doc = db.collection('groups').document(group_id).get()
        if group_doc.exists and group_doc.to_dict().get('user_email') == user['email']:
            db.collection('cameras').document(camera_id).delete()
            return RedirectResponse(f"/dashboard?group_id={group_id}", status_code=302)
    
    return RedirectResponse("/dashboard", status_code=302)
