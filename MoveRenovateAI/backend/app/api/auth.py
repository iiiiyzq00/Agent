"""认证 API 模块"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/v1/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/register")
async def register(data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.get("username")))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")
    result = await db.execute(select(User).where(User.email == data.get("email")))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = User(username=data["username"], email=data["email"],
                password_hash=get_password_hash(data["password"]), full_name=data.get("full_name"))
    db.add(user); await db.commit(); await db.refresh(user)
    return {"id": str(user.id), "username": user.username, "email": user.email}

@router.post("/login")
async def login(data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(
        (User.username == data["username"]) | (User.email == data["username"])))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    user.last_login = datetime.utcnow()
    await db.commit()
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return {"access_token": access_token, "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "user": user.to_dict()}

@router.get("/me")
async def get_me(token: str, db: AsyncSession = Depends(get_db)):
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭证")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user.to_dict()
