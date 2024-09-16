import asyncio
import json
import uuid
import logging    
from typing import MutableMapping
from .config import Evariable
from aio_pika import Message, connect
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue

logger = logging.getLogger("publisher_logger") 

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
        logger.info("Publisher initialized with empty futures dictionary.")

    async def connect(self) -> "Publisher":
        """
        Connects to the RabbitMQ server and sets up the callback queue for responses.

        Returns:
            Publisher: The instance of the Publisher after connection is established.
        """
        logger.debug("Attempting to connect to RabbitMQ server.")
        self.connection = await connect(f"amqp://{Evariable.RabbitMQ_user}:{Evariable.RabbitMQ_password}@{Evariable.RabbitMQ_host}:{Evariable.RabbitMQ_port}/")
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        logger.info("Connected to RabbitMQ server and callback queue set up.")
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
            logger.warning("Received message without a correlation ID.")
            return 
        
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        logger.debug(f"Processing response with correlation ID: {message.correlation_id}")
        future.set_result(message.body.decode())

        if message.body.decode() == "NOT FOUND":
            logger.warning("Received 'NOT FOUND' response. Cancelling future.")
            future.cancel()

    async def call(self, value: dict) -> dict|None:
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
        logger.info(f"Sending message with correlation ID: {correlation_id}")

        await self.channel.default_exchange.publish(
            Message(json.dumps(value).encode(),       #use json.dumps to pass a valid JSON STRING
                    content_type="text/plain", correlation_id=correlation_id, reply_to=self.callback_queue.name),
            routing_key="read")
        

        try:
            response = await asyncio.wait_for(future, 10)
            logger.info(f"Received response for correlation ID: {correlation_id}")
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout while waiting for response for correlation ID: {correlation_id}")
            del self.futures[correlation_id]  
            raise asyncio.TimeoutError
        
        except asyncio.CancelledError:
            logger.error(f"Request cancelled for correlation ID: {correlation_id}")
            raise ValueError
        
        return response

    async def close_connection(self) -> None:
        """
        Closes the RabbitMQ connection.
        """
        await self.connection.close()
        logger.info("RabbitMQ connection closed.")


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

    if publisher is None or publisher.connection.is_closed == True:
        publisher = await Publisher().connect()

    match value["method"]:
        case "subtract":

            response = await publisher.call(value)
            if response is None:
                logger.error("Error during 'subtract' operation: No response received.")
                raise Exception('Something went wrong')
            logger.info("'Subtract' operation successful.")
            return response
            
        case "read":
          
            try:
                response = await publisher.call(value)
            except ValueError:
                logger.error("Product not found in 'read' operation.")
                raise ValueError('Product NOT found')
            except TimeoutError:
                logger.error("Timeout during 'read' operation.")
                raise TimeoutError('The request is taking longer than expected to complete.')

            logger.info("'Read' operation successful.")
            return json.loads(response)
