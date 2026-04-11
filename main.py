from fastapi import FastAPI 
from s3 import upload_to_s3
from database import init_db
from routers import upload ,query


app = FastAPI()
init_db()


app.include_router(upload.router)
app.include_router(query.router)
@app.get("/")
def read_root():    return {"Hello": "World"}