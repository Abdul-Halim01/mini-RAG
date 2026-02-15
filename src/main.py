from fastapi import FastAPI 
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings



app = FastAPI()
@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown():
    app.mongodb_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)


