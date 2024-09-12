from pydantic import BaseModel , Field
from aredis_om import HashModel 
from datetime import datetime
from typing import Optional


class Order(BaseModel):

    Product_id : str 
    Quantity : int = Field(gt=0)



class Payment (HashModel):


    """
    Represents a product stored in the Redis database using a Redis Hash structure.

    This class combines the schema validation from ProductSchema with Redis
    HashModel functionality, allowing for easy interaction with the Redis database.
    
    Attributes:
    - Automatically generates a unique primary key ('pk') for each product instance.

    - Product_id : str
        Unique identifier for the product being paid for. This is typically a foreign key
        linking to an 'Order' or 'Product' table in a relational database.

    - Purchase_time : datetime, optional
        Timestamp indicating when the purchase was made. This field can be null initially.
        In a database, this would typically be stored as a 'datetime' type column.

    - Quantity : int
        The number of units purchased. This would be stored as an integer field in the database.

    - Total_price : float
        The total cost of the transaction. This would likely be a 'decimal' or 'float' type
        field in the database to handle monetary values.

    - Status : str, optional
        Current status of the payment (e.g., 'Pending', 'Completed', 'Failed'). This field
        helps track the progress of the payment process. In a database, this would likely
        be a 'varchar' or 'text' field.

    - Payment_Gateway : str, optional
        The payment gateway used for processing the transaction (e.g., 'PayPal', 'Stripe').
        This field helps identify the external payment service used. In a database, this 
        would be stored as a string.

    
    Redis HashModel capabilities allow the product to be saved, retrieved, and managed
    efficiently in the Redis database, while Pydantic's schema validation ensures data integrity.

    """
    Product_id : str 
    Purchase_time : datetime | None
    Quantity : int 
    Total_price : float
    status : str 
    Payment_Gateway : str | None

    class Config:
        extra='ignore'
        from_attributes = True