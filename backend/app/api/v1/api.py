"""
Router principal de la API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, usuarios, empresas
from app.api.v1.endpoints.conductores import router as conductores_router
from app.api.v1.endpoints.habilitaciones import router as habilitaciones_router
from app.api.v1.endpoints.pagos import router as pagos_router


api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(empresas.router)
api_router.include_router(conductores_router)
api_router.include_router(habilitaciones_router)
api_router.include_router(pagos_router, prefix="/pagos", tags=["pagos"])
