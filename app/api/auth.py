from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserLogin, Token, UserOut
from app.services.auth_service import authenticate_user, get_current_user
from app.utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        # Mensaje generico: nunca revelar errores tecnicos ni cual dato fallo
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
