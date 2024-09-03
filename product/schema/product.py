from aredis_om import HashModel 
from pydantic import BaseModel 

class Product(HashModel):
    
    Product_Name : str 
    Product_Info : str = "no Info added"
    Product_Inventory : int
    Product_Price : int 

    class Config:
        extra='ignore'
        from_attributes = True


class Product_OUT(BaseModel):

    Product_Name : str 
    Product_Info : str 
    Product_Inventory : int
    