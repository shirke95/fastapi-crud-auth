from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import user_router, tutorial_router

# =====================================================
# Application Lifespan
# =====================================================


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create tables
    # Use Alembic in production instead of this
    # Base.metadata.create_all(bind=engine)

    print("Application started")

    yield

    print("Application stopped")


# =====================================================
# FastAPI App
# =====================================================

app = FastAPI(
    title="FastAPI CRUD API",
    description="FastAPI JWT Authentication with Role Based Access Control",
    version="1.0.0",
    lifespan=lifespan,
)


# =====================================================
# CORS Configuration
# =====================================================

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


# =====================================================
# Routers
# =====================================================

app.include_router(user_router.router)


app.include_router(tutorial_router.router)


# =====================================================
# Health Check
# =====================================================


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():

    return {
        "status": "ok",
        "message": "API is running",
    }
