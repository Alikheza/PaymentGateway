from aredis_om import HashModel 
from pydantic import BaseModel 



class ProductSchema(BaseModel):

    Product_Name: str
    Product_Info: str
    Product_Inventory: int
    Product_Price: float
    num_of_order : int = 0

    class Config:
        extra='ignore'
        from_attributes = True


class Product(HashModel, ProductSchema):

    """
    
    Represents a product stored in the Redis database using a Redis Hash structure.

    This class combines the schema validation from ProductSchema with Redis
    HashModel functionality, allowing for easy interaction with the Redis database.
    
    Attributes:
    - Automatically generates a unique primary key ('pk') for each product instance.
    - Inherits fields such as `Product_Name`, `Product_Info`, `Product_Inventory`,
      `Product_Price`, and `Is_Updated` from ProductSchema.
    
    Redis HashModel capabilities allow the product to be saved, retrieved, and managed
    efficiently in the Redis database, while Pydantic's schema validation ensures data integrity.

    """
    pass
