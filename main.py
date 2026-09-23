from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from auth_routes import router as auth_router
from routers.books import router as books_router
from routers.readers import router as readers_router
from routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library API",
    description="API ",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "Library API запущен",
        "docs": "/docs"
    }

