from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import user_router, tutorial_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD API", version="1.0.0")

# -----------------------
# CORS Configuration
# -----------------------

origins = [
    "http://localhost:3000",  # React (CRA)
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # React (Vite)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, PATCH, DELETE
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

# production
# origins = [
#     "https://myapp.com",
#     "https://www.myapp.com",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
#     allow_headers=[
#         "Authorization",
#         "Content-Type",
#     ],
# )
# production

app.include_router(user_router.router)
app.include_router(tutorial_router.router)
