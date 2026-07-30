from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserLogin, Token, UserOut, PasswordChangeIn
from app.services import media_service
from app.services.auth_service import authenticate_user, get_current_user, change_own_password
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
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me/password")
def cambiar_password(
    data: PasswordChangeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_own_password(db, current_user, data)
    return {"success": True, "message": "Contraseña actualizada correctamente"}


@router.post("/me/photo", response_model=UserOut)
def subir_foto_perfil(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return media_service.upload_user_photo(db, current_user, file)


@router.delete("/me/photo")
def quitar_foto_perfil(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media_service.delete_user_photo(db, current_user)
    return {"success": True, "message": "Foto de perfil eliminada correctamente"}
