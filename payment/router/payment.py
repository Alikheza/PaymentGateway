import datetime
import asyncio
from fastapi import APIRouter , HTTPException , status , BackgroundTasks
from aredis_om import NotFoundError
from ..schema.payment import Order , Payment
from ..app.publisher import message_to_inventory
from ..app.payment_gateway import process_payment

payment_router = APIRouter()


@payment_router.post('/orders/' ,status_code=status.HTTP_201_CREATED )
async def API_order_product(order:Order , background_tasks: BackgroundTasks):

    """
    Processes a new order and initiates the payment asynchronously.

    Args:
        order (Order): The order object containing details such as product ID and quantity.
        background_tasks (BackgroundTasks): Used to handle the payment processing asynchronously in the background.

    Returns:
        dict: A dictionary with a success message and the order ID.

    Raises:
        HTTPException:
            - 400 BAD REQUEST: If the requested quantity exceeds available inventory.
            - 404 NOT FOUND: If the product is not found in the inventory.
            - 408 REQUEST TIMEOUT: If the request to inventory takes too long.
    """
    try:

        inventory_response = await message_to_inventory({
            "method": "read",
            "product_id": order.Product_id})
        if int(inventory_response["Product_Inventory"]) < order.Quantity:
            raise HTTPException(detail="Quantity requested is more than available inventory",status_code=status.HTTP_400_BAD_REQUEST)

        total_price = order.Quantity * float(inventory_response["Product_Price"])

        payment_data = {
            "Product_id": inventory_response["pk"],
            "Purchase_time": datetime.datetime.now(),
            "Quantity": order.Quantity,
            "Total_price": total_price,
            "status": "pending" , 
            "Payment_Gateway": None
        }
    except ValueError:
        raise HTTPException(detail="Product not found!", status_code=status.HTTP_404_NOT_FOUND)
    except TimeoutError:
        raise HTTPException(detail="The request is taking longer than expected to complete.", status_code=status.HTTP_408_REQUEST_TIMEOUT)

    
    new_payment =  Payment(**payment_data)
    await new_payment.save()

    background_tasks.add_task(process_payment , new_payment)

    return {"message": "Order processed" , "order_id" : new_payment.pk}


@payment_router.get('/check_order/{order_id}')
async def API_check_order(order_id:str ):

    """
    API endpoint to check the status of an order by its ID.

    Args:
        order_id (str): The unique identifier for the order.

    Returns:
        dict: A dictionary containing the status message of the order.
    
    Raises:
        HTTPException: If the order is not found, returns a 404 error.
    """
    
    try:
        order = await Payment.get(order_id)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    
    return {"message" : order.status}