from fastapi import FastAPI

from app.channels.telegram.webhook import router as telegram_router

from app.channels.whatsapp.webhook import router as whatsapp_router

app = FastAPI(title="Project Echo")

app.include_router(telegram_router)
app.include_router(whatsapp_router)


@app.get("/")
def home():
    return {"message": "Project Echo Running"}