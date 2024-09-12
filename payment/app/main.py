from fastapi import FastAPI 
from contextlib import asynccontextmanager
from aredis_om import get_redis_connection
from aio_pika.exceptions import AMQPConnectionError
from ..router.payment import payment_router
from ..schema.payment import Payment
from .config import Evariable
from .publisher import Publisher

REDIS_DATA_URL = f"redis://{Evariable.redis_username}:{Evariable.redis_password}@{Evariable.redis_host}:{Evariable.redis_port}/{Evariable.redis_database}"
redis = get_redis_connection(url=REDIS_DATA_URL , decode_responses=True)


@asynccontextmanager
async def check_database_is_up(app: FastAPI):
    """
    Asynchronous context manager to check the connection status of Redis and RabbitMQ.

    This function checks if Redis is available by pinging it and ensures a RabbitMQ
    consumer is running. It raises a ConnectionError if either service is unreachable.

    """
    publisher = None
    
    try:
        # Check Redis connection
        Payment.Meta.database = redis
        if not await redis.ping():
            raise ConnectionError("Unable to ping the Redis database!")

        # Check RabbitMQ connection
        publisher = await Publisher().connect()

        # If both checks pass, yield to continue execution
        yield

    except AMQPConnectionError as amqp_error:
        # logging.error(f"Failed to connect to RabbitMQ: {amqp_error}")
        raise SystemExit("Shutting down due to RabbitMQ connection failure.")
    
    except ConnectionError as redis_error:
        # logging.error(f"Cannot connect to Redis database: {redis_error}")
        raise SystemExit(f"Cannot connect to the Redis database! Error: {redis_error}")
    
    finally:
        # Ensure RabbitMQ connection is closed if it was established
        if publisher:
            await publisher.close_connection()


app = FastAPI(lifespan=check_database_is_up)

app.include_router(payment_router , prefix="/v1" ,tags=['Payment'])
