import json
from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage
from aredis_om import NotFoundError
from product.schema.product import Product

async def consumer() -> None:

    connection = await connect("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    exchange = channel.default_exchange
    queue = await channel.declare_queue("read")

    async with queue.iterator() as qiterator:

        message: AbstractIncomingMessage

        async for message in qiterator:

            try:
                async with message.process(requeue=False):
            
                    assert message.reply_to is not None
                    assert message.body is not None
                    
                    response = await on_response(message.body.decode())
                    await exchange.publish(
                        Message(body=response.encode(),correlation_id=message.correlation_id,)
                        ,routing_key=message.reply_to)

            except Exception as E:
                print(f'something went wrong  {E}')


async def on_response (value: str) -> dict|str:

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
                return "The product update was successful"
            
            except Exception as E: 
                raise Exception(f"something went wrong  {E}")

        case "read":
            return json.dumps(product_info.model_dump())