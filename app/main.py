from fastapi import FastAPI
from .api import router
from config import config


app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version="1.0.0"
)

app.include_router(router)
