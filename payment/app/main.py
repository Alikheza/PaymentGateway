from fastapi import FastAPI 
from contextlib import asynccontextmanager
from aredis_om import get_redis_connection
from ..router.payment import payment_router
from ..schema.payment import Payment
from .config import Evariable
REDIS_DATA_URL = f"redis://{Evariable.redis_username}:{Evariable.redis_password}@{Evariable.redis_host}:{Evariable.redis_port}/{Evariable.redis_database}"
redis = get_redis_connection(url=REDIS_DATA_URL , decode_responses=True)

@asynccontextmanager
async def check_database_is_up(app: FastAPI):
    try:
        
        Payment.Meta.database = redis

        if await redis.ping():
            yield
        else:
            raise ConnectionError("Unable to ping the Redis database!")
    except Exception as e:
        raise ConnectionError(f"Cannot connect to the database! Error: {e}")


app = FastAPI(lifespan=check_database_is_up)

app.include_router(payment_router , prefix="/v1" ,tags=['Payment'])
