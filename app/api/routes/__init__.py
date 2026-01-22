from fastapi import APIRouter

from app.api.routes import tokens, users

router = APIRouter()
router.include_router(tokens.router, prefix="/tokens", tags=["Tokens"])
router.include_router(users.router, prefix="/users", tags=["Users"])
