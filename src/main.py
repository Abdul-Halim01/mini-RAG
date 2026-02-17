from fastapi import FastAPI 
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.LLMProviderFactory import LLMProviderFactory


app = FastAPI()

async def startup():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]
    llm_provider_factory = LLMProviderFactory(settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDIDING_MODEL_ID,
                                            embedding_size=settings.EMBEDIDING_MODEL_SIZE)

async def shutdown():
    app.mongodb_conn.close()


app.router.lifespan.on_startup.append(startup)
app.router.lifespan.on_shutdown.append(shutdown)

app.include_router(base.base_router)
app.include_router(data.data_router)


