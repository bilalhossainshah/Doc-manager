from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from s3 import upload_to_s3
from database import init_db
from routers import upload ,query


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


app.include_router(upload.router)
app.include_router(query.router)
@app.get("/")
def read_root():    return {"Hello": "World"}