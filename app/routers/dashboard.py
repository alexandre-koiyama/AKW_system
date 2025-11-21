from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from firebase_admin import firestore
from app.firebase.auth import verify_token
from app.config import db

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request, group_id: str = None):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    groups = []
    all_cameras = []
    selected_group = None
    
    try:
        for doc in db.collection('groups').where('user_email', '==', user['email']).stream():
            group_data = doc.to_dict()
            group_data['id'] = doc.id
            groups.append(group_data)
            if group_id and doc.id == group_id:
                selected_group = group_data
        
        for doc in db.collection('cameras').stream():
            camera_data = doc.to_dict()
            camera_data['id'] = doc.id
            cam_group_id = camera_data.get('group_id')
            
            if cam_group_id:
                group_doc = db.collection('groups').document(cam_group_id).get()
                if group_doc.exists and group_doc.to_dict().get('user_email') == user['email']:
                    camera_data['group_name'] = group_doc.to_dict().get('name', 'Unknown')
                    
                    if group_id:
                        if cam_group_id == group_id:
                            all_cameras.append(camera_data)
                    else:
                        all_cameras.append(camera_data)
    except Exception as e:
        print(f"Firestore error: {e}")
    
    return request.app.state.templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "groups": groups,
        "cameras": all_cameras,
        "selected_group": selected_group,
        "selected_group_id": group_id
    })

@router.post("/cameras/add")
def add_camera_from_dashboard(
    name: str = Form(...),
    group_id: str = Form(...),
    rtsp_url: str = Form(...),
    description: str = Form(""),
    request: Request = None
):
    try:
        user = verify_token(request)
    except HTTPException:
        return RedirectResponse("/login", status_code=302)
    
    group_doc = db.collection('groups').document(group_id).get()
    if not group_doc.exists or group_doc.to_dict().get('user_email') != user['email']:
        raise HTTPException(status_code=404, detail="Group not found")
    
    db.collection('cameras').add({
        'name': name,
        'rtsp_url': rtsp_url,
        'description': description,
        'group_id': group_id,
        'status': 'offline',
        'created_at': firestore.SERVER_TIMESTAMP
    })
    
    return RedirectResponse("/dashboard", status_code=302)
