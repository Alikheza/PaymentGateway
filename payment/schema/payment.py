from pydantic import BaseModel
from aredis_om import HashModel 
from datetime import datetime


class Order(BaseModel):
    Product_id : str 
    Quantity : int



class Payment (HashModel):

    Product_id : str 
    Purchase_time : datetime = None
    Quantity : int
    Total_price : float
    status : str = "pending" 


    class Config:
        extra='ignore'
        from_attributes = True


class Purchase_Order (Payment) :

    Payment_Gateway : str  = 'x' # The name of the payment-gateway used 
    Purchase_time_gateway : datetime = None # the Payment-gateway response time
