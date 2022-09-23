from fastapi import FastAPI
import uvicorn
from app.routes import router

app = FastAPI(docs_url="/docs", redoc_url=None)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
