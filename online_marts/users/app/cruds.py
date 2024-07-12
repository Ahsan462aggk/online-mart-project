from app.models.user_models import User,UserCreate
from app.utilis import get_password_hash,create_access_token,verify_password
from fastapi import HTTPException, status
from sqlmodel import Session,select
from fastapi.security import OAuth2PasswordRequestForm

def create_user(user: UserCreate, session:Session):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def login_for_access_token(form_data: OAuth2PasswordRequestForm ,session:Session):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
def authenticate_user(session: Session, username: str, password: str):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user




    
    
    
    
    
    

    
