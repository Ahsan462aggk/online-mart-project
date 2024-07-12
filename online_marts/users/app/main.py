
from contextlib import asynccontextmanager
from typing import  Annotated
from sqlmodel import  Session,select
from fastapi import FastAPI, Depends,HTTPException,status
from typing import AsyncGenerator
from app.deps import get_session
from app.database import create_db_and_tables
from app.cruds import create_user,login_for_access_token
from app.models.user_models import UserCreate,User
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm 
from app.utilis import ALGORITHM,SECRET_KEY,jwt
from jose import JWTError

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("LifeSpan Event..")
   
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan,
              title="Hello Kafka With FastAPI",
              version="0.0.1",
              )

@app.post("/Singup/")
def registration(user_details:UserCreate,session:Annotated[Session,Depends(get_session)]):
    return create_user(user=user_details,session=session)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
def login(form_detail:Annotated[OAuth2PasswordRequestForm,Depends(OAuth2PasswordRequestForm)],session:Annotated[Session,Depends(get_session)]):
    return login_for_access_token(form_data=form_detail,session=session)

@app.get("/me")
def get_current_user(session: Annotated[Session,Depends(get_session)], token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user





    
    



   



