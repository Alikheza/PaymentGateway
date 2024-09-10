import asyncio
import json
from typing import MutableMapping
from aio_pika import Message, connect
from aio_pika.abc import (AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,)
import uuid    

class Publisher:

    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue


    def __init__(self) -> None:

        self.futures: MutableMapping[str, asyncio.Future] = {}


    async def connect(self) -> "Publisher":

        self.connection = await connect("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        return self


    async def on_response(self, message: AbstractIncomingMessage) -> None:

        if message.correlation_id is None:
            return 
        
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body.decode())

        if message.body.decode()=="NOT FOUND" :
            future.cancel()

    async def call(self, value: dict) -> dict|None :

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(json.dumps(value).encode(),       #use json.dumps to pass a valid JSON STRING
                    content_type="text/plain",correlation_id=correlation_id,reply_to=self.callback_queue.name),
            routing_key="read")
        
        
        if future.cancelled() != True :
            return await future
        else :
            return None


publisher: Publisher = None

async def message_to_inventory(value: dict) -> dict:
    global publisher

    if publisher is None :
        publisher = await Publisher().connect()

    match value["method"]:

        case "subtract":
            response = await publisher.call(value)
            if response is None :
                raise Exception('Something went wrong')
            
            return response 
            
        case "read":
            response = await publisher.call(value)
            if response is None :
                raise ValueError('product NOT found')
            
            return json.loads(response)

