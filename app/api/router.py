from fastapi import APIRouter

from app.callbacks.ondc_callbacks import router as callback_router
from app.callbacks.ondc_callbacks import workbench_alias_router
from app.routes.ondc import router as ondc_router

api_router = APIRouter()
api_router.include_router(ondc_router)
api_router.include_router(callback_router)
api_router.include_router(workbench_alias_router)
