from fastapi import APIRouter

from app.core.config import get_settings

settings = get_settings()
router = APIRouter()
