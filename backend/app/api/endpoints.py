from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.session import get_db
from app.db.models import User, Document
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.ai import get_ai_response
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email registered")
    new_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"access_token": create_access_token(subject=user.id), "token_type": "bearer"}
@router.post("/chat")
def chat(prompt: str, token: str = Depends(oauth2_scheme)):
    return {"answer": get_ai_response(prompt)}
@router.post("/documents")
def upload_document(title: str, content: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    doc = Document(title=title, content=content, owner_id=1)
    db.add(doc)
    db.commit()
    return {"msg": "Uploaded"}
@router.get("/recommendations")
def get_learning_path(token: str = Depends(oauth2_scheme)):
    return {"path": ["Chapter 1: Intro", "Chapter 2: Advanced AI"]}
