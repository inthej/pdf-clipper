from fastapi import FastAPI
from routes.pdf_router import router as pdf_router

app = FastAPI()

app.include_router(pdf_router)


@app.get("/")
async def root():
    return {"message": "Hello, World"}
