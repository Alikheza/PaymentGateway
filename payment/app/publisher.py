import asyncio
import json
import uuid    
from typing import MutableMapping
from .config import Evariable
from aio_pika import Message, connect
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue

class Publisher:

    """
    A Publisher class to send and receive messages via RabbitMQ using aio-pika.
    This class handles request/response communication with the message queue.
    """

    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue


    def __init__(self) -> None:

        self.futures: MutableMapping[str, asyncio.Future] = {}


    async def connect(self) -> "Publisher":
        """
        Connects to the RabbitMQ server and sets up the callback queue for responses.

        Returns:
            Publisher: The instance of the Publisher after connection is established.
        """
        self.connection = await connect(f"amqp://{Evariable.RabbitMQ_user}:{Evariable.RabbitMQ_password}@{Evariable.RabbitMQ_host}:{Evariable.RabbitMQ_port}/")
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        return self


    async def on_response(self, message: AbstractIncomingMessage) -> str|None:
        """
        Callback function that processes incoming responses to published messages.

        Args:
            message (AbstractIncomingMessage): The incoming message from RabbitMQ.

        Returns:
            str | None: The decoded response body, or None if no correlation ID exists.
        """
        if message.correlation_id is None:
            return 
        
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body.decode())

        if message.body.decode()=="NOT FOUND" :
            future.cancel()

    async def call(self, value: dict) -> dict|None :
        """
        Sends a message to RabbitMQ and waits for a response.

        Args:
            value (dict): The data to be sent in the message.

        Returns:
            dict | None: The response data if available, or None if no valid response is returned.
        
        Raises:
            asyncio.TimeoutError: If the request times out.
            ValueError: If the product is not found.
        """
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(json.dumps(value).encode(),       #use json.dumps to pass a valid JSON STRING
                    content_type="text/plain",correlation_id=correlation_id,reply_to=self.callback_queue.name),
            routing_key="read")
        
        
        try:
            response = await asyncio.wait_for(future, 10)
        except asyncio.TimeoutError:
            del self.futures[correlation_id]  # Remove the future if it times out
            raise asyncio.TimeoutError
        except asyncio.CancelledError:
            raise ValueError
        return response
        
    async def close_connection(self) ->None :

        await self.connection.close()


publisher: Publisher = None

async def message_to_inventory(value: dict) -> dict:

    """
    Communicates with the inventory system to either read product information or subtract inventory.

    Args:
        value (dict): The data containing the method (read/subtract) and product details.

    Returns:
        dict: The product details or confirmation of inventory subtraction.

    Raises:
        Exception: If something goes wrong during the subtract operation.
        ValueError: If the product is not found.
        TimeoutError: If the request to the inventory system times out.
    """

    global publisher

    if publisher is None or publisher.connection.is_closed==True :
        publisher = await Publisher().connect()

    match value["method"]:

        case "subtract":
            response = await publisher.call(value)
            if response is None :
                raise Exception('Something went wrong')
            
            return response 
            
        case "read":
            try :
                response = await publisher.call(value)

            except ValueError :
                raise ValueError('product NOT found')
            
            except TimeoutError:
                raise TimeoutError('The request is taking longer than expected to complete.')
            
            return json.loads(response)
