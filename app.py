from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
SECRET_KEY = os.getenv("SECRET_KEY", "ChangeMe")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# FastAPI instance
app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:newpassword@localhost:3306/addressbook_fastapi")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    contacts = relationship("Contact", back_populates="owner")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="contacts")

# Pydantic models
class ContactBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Routes
@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/contacts", response_model=List[ContactResponse])
def get_contacts(db: SessionLocal = Depends(get_db), user: User = Depends(get_current_user)):
    contacts = db.query(Contact).filter(Contact.owner_id == user.id).all()
    return contacts

@app.post("/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: SessionLocal = Depends(get_db), user: User = Depends(get_current_user)):
    new_contact = Contact(**contact.dict(), owner_id=user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, updated_contact: ContactCreate, db: SessionLocal = Depends(get_db), user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in updated_contact.dict().items():
        setattr(contact, key, value)
    db.commit()
    return contact

@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: SessionLocal = Depends(get_db), user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted"}

# Initialize database
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
