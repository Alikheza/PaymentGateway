import asyncio
import logging
from fastapi import FastAPI , HTTPException
from fastapi.exception_handlers import http_exception_handler
from aio_pika.exceptions import AMQPConnectionError
from contextlib import asynccontextmanager
from aredis_om import get_redis_connection
from ..router.product import product_router
from ..schema.product import Product
from .config import Evariable
from .consumer import consumer , connect_consumer
from .logging_config import configure_logging


REDIS_DATA_URL = f"redis://{Evariable.redis_username}:{Evariable.redis_password}@{Evariable.redis_host}:{Evariable.redis_port}/{Evariable.redis_database}"
redis = get_redis_connection(url=REDIS_DATA_URL , decode_responses=True)

logger = logging.getLogger(__name__)
logger_error = logging.getLogger('error_logger')

@asynccontextmanager
async def check_database_is_up(app: FastAPI):
    """
    Asynchronous context manager to check the connection status of Redis and RabbitMQ.

    This function checks if Redis is available by pinging it and ensures a RabbitMQ
    consumer is running. It raises a ConnectionError if either service is unreachable.

    """
    try:
        configure_logging()

        Product.Meta.database = redis

        await connect_consumer()
        
        asyncio.create_task(consumer())
        
        if not await redis.ping() :
            raise ConnectionError("Unable to ping the Redis database!") # If Redis is reachable, continue with FastAPI app startup
        
        else:
            yield # If Redis and RabbitMQ is reachable, continue with FastAPI app startup
        
        
    except AMQPConnectionError as amqp_error:
        logger_error.critical(f"Failed to connect to RabbitMQ: {amqp_error}")
        raise SystemExit("Shutting down due to RabbitMQ connection failure.")
    
    except ConnectionError as redis_error:
        logger_error.critical(f"Failed to connect to Redis: {redis_error}")
        raise SystemExit(f"Cannot connect to the Redis database! Error: {redis_error}")


app = FastAPI(lifespan=check_database_is_up )

app.include_router(product_router , prefix="/v1" ,tags=['Product'])


@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request , exc):
    logger_error.error(f"HTTPException:  {exc.detail}|{exc.status_code}")
    return await http_exception_handler(request, exc)