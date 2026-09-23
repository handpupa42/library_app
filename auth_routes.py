from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import (
    LoginRequest, Token, UserResponse, PasswordChangeRequest, UserCreate
)
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_password_hash, 
    get_user_by_username,
    verify_password
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения JWT токена.
    Принимает username и password в формате JSON.
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем авторизованном пользователе.
    """
    return current_user

@router.put("/users/me/password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Смена пароля текущего пользователя с проверкой старого пароля.
    """
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Пароль успешно изменен"}

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Деактивация пользователя по ID. Доступно только администратору.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав (требуется роль admin)"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Вы не можете деактивировать сами себя")
        
    user.is_active = False
    db.commit()
    return {"message": f"Пользователь {user.username} успешно деактивирован"}


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового пользователя. Доступно только администратору.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав (требуется роль admin)"
        )

    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user