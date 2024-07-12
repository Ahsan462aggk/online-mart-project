from sqlmodel import SQLModel,Field,table
from datetime import datetime

from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3)  # Enforce minimum length
    email: str = Field(unique=True, index=True, min_length=5)  # Enforce minimum length
    hashed_password: str = Field(default=None, nullable=False)  # Make non-nullable
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)



class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    full_name: str

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool    
class UserUpdate(SQLModel):
    username: str
    email: str
    password: str
    full_name: str    