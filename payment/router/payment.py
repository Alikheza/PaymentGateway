from fastapi import APIRouter , HTTPException , status
from ..schema.payment import Order
from ..app.publisher import message_to_inventory

payment_router = APIRouter()


@payment_router.post('/Orders/')
async def Order_product(order:Order):

    message = {"method":"read",
               "product_id":order.Product_id}
    
    response = await message_to_inventory(message)
    
    if int(response["Product_Inventory"]) < order.Quantity :
        raise HTTPException(detail="Quantity requested is more than inventory",status_code=status.HTTP_400_BAD_REQUEST)
    
    message = {"method":"subtract",
               "product_id":order.Product_id, 
               "Quantity": order.Quantity}
    await message_to_inventory(message)

    return {"message": "order completed"}