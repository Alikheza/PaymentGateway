import logging
import json
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage
from aredis_om import NotFoundError
from product.schema.product import Product
from .config import Evariable

logger = logging.getLogger('consumer_logger')
logger_error = logging.getLogger('error_logger')


async def connect_consumer() :

    connection = await connect(f"amqp://{Evariable.RabbitMQ_user}:{Evariable.RabbitMQ_password}@{Evariable.RabbitMQ_host}:{Evariable.RabbitMQ_port}/")
    # channel = await connection.channel()    
    return connection




async def consumer() -> None:
    """
    RabbitMQ consumer that listens to the 'read' queue for messages regarding product actions
    (read or subtract inventory) and responds with the requested information or performs
    inventory updates.

    It handles responses asynchronously and sends a message back to the reply queue.
    """
    connection = await connect_consumer()
    channel = await connection.channel()
    exchange = channel.default_exchange
    queue = await channel.declare_queue("read")

    async with queue.iterator() as qiterator:

        message: AbstractIncomingMessage

        async for message in qiterator:

            try:
                async with message.process(requeue=False):
                    logger.info(f"Message received | correlation_id : {message.correlation_id}")
                    
                    assert message.reply_to is not None
                    assert message.body is not None
                    
                    response = await on_response(message.body.decode() ,message.correlation_id)
                    logger.info(f"The message was processed | correlation_id : {message.correlation_id}")
                    
                    await exchange.publish(
                        Message(body=response.encode(),correlation_id=message.correlation_id,)
                        ,routing_key=message.reply_to)
                    logger.info(f"The message was sent to the PaymentGateway | correlation_id : {message.correlation_id}")

            except Exception as E:
                logger_error.critical(f'something went wrong in message broker!!   {E}')


async def on_response (value: str ,correlation_id: str ) -> dict|str:
    """
    Handles the incoming message and performs actions such as reading product info or
    subtracting product inventory.

    Args:
        value (str): JSON string containing the method (read or subtract) and product ID.

    Returns:
        dict | str: The result of the requested action or an error message.
    """
    value=json.loads(value)

    try :
        product_info = await Product.get(value["product_id"])
    except NotFoundError:
        return "NOT FOUND"
    
    match value["method"]:

        case "subtract":
            try:
                total = product_info.Product_Inventory - value["Quantity"]
                await product_info.update(Product_Inventory = total)

                logger.info(f"The product inventory updated | product_id : {product_info.pk} | Quantity : {value["Quantity"]} | correlation_id : {correlation_id}")

                return "The product update was successful"
            
            except Exception as E: 
                logger_error.critical(f'something went wrong in message broker!! | Error: {E}')
                raise Exception(f"something went wrong  {E}")

        case "read":
            logger.info(f"product info read | product_id : {product_info.pk} | correlation_id : {correlation_id}")
            return json.dumps(product_info.model_dump())