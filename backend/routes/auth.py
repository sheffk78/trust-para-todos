"""Trust Para Todos — Auth Routes (stub)."""
from __future__ import annotations
import logging
import hashlib
import secrets
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

logger = logging.getLogger("trust_para_todos.routes.auth")
router = APIRouter()

# In-memory store for auth codes (replace with Redis in production)
_auth_codes: dict[str, dict] = {}

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

@router.post("/login")
async def request_login_code(data: LoginRequest):
    """Send a one-time login code to the user's email.
    Currently stubs the code; production should send via Brevo."""
    code = secrets.token_hex(3)[:6].upper()
    _auth_codes[data.email] = {"code": code, "expires": time.time() + 600}
    logger.info("🔑 Código de acceso para %s: %s", data.email, code)
    return {"status": "sent", "message": "Si el correo existe, recibirás un código."}

@router.post("/verify")
async def verify_login_code(data: VerifyRequest):
    """Verify the one-time code and return a session token."""
    stored = _auth_codes.pop(data.email, None)
    if stored is None:
        raise HTTPException(status_code=401, detail="No code requested or expired")
    if time.time() > stored["expires"]:
        raise HTTPException(status_code=401, detail="Code expired")
    if stored["code"] != data.code.upper():
        raise HTTPException(status_code=401, detail="Invalid code")

    token = hashlib.sha256(f"{data.email}:{secrets.token_hex(16)}".encode()).hexdigest()
    logger.info("✅ Login exitoso: %s", data.email)
    return {"status": "ok", "token": token, "email": data.email}