from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Wallet API",
    description="REST API для управления кошельками",
    version="1.0.0",
)

app.include_router(router)
