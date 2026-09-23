from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import auth_routes
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "перейдите на /docs для тестирования"}
