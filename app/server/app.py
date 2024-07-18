from fastapi import FastAPI
from server.routes.index import router as ApiRouter
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Define allowed origins, methods, headers, and credentials
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(ApiRouter, tags=["api"], prefix="/api")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to attendance system"}