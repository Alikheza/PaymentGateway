import asyncio
import logging
from fastapi import HTTPException , status
from .publisher import message_to_inventory

logger = logging.getLogger("payment_gateway")

async def process_payment(new_payment) -> None:

    """
    Background task to handle payment processing.

    This function is triggered after an order is placed. It simulates the time taken 
    for payment to be processed by waiting for 5 seconds (using asyncio.sleep).
    You can easily modify this function to connect to any gateway you want. Just make sure to change "PaymentGatewayName" accordingly and logging
    
    Args:
    new_payment (Payment): The payment object which contains details of the transaction 
    like product ID, quantity, and total price.

    Raises:
    HTTPException: If there is an error while interacting with the inventory service, 
    a 500 Internal Server Error is raised with a message asking the user to retry.
    """

    PaymentGatewayName = "XXX"

    await new_payment.update(Payment_Gateway = PaymentGatewayName) 
    await asyncio.sleep(10)
    logger.info('The payment was successful')
    subtract_message = {
        "method":"subtract",
        "product_id":new_payment.Product_id, 
        "Quantity": new_payment.Quantity}
    
    try : 
        await message_to_inventory(subtract_message)
    except Exception :
        logger.critical('sending message to inventory failed , so updating inventory failed')
        await new_payment.update(status = "Failed")
        raise HTTPException(detail="something went wrong!!! Try again in a few minutes", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    await new_payment.update(status = "Completed")