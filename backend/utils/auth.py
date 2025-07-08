"""Utilitaires d'authentification : hashage de mot de passe (bcrypt), génération et vérification de JWT.
Tout est rédigé en français.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv(".env")

SECRET_KEY = os.getenv("JWT_SECRET", "secret-demo")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Retourne le hash bcrypt d'un mot de passe."""
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash_: str) -> bool:
    """Vérifie qu'un mot de passe correspond à son hash."""
    return pwd_context.verify(mot_de_passe, hash_)


def creer_jwt(data: dict, expire_delta: Optional[timedelta] = None) -> str:
    """Crée un JWT signé avec expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verifier_jwt(token: str) -> Optional[dict]:
    """Décode le JWT et retourne le payload si valide, None sinon."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
