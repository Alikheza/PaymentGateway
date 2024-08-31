from fastapi import APIRouter , HTTPException
from ..schema.product import Product , Product_OUT
from aredis_om import NotFoundError

product_router = APIRouter()

@product_router.get('/read_product/{proID}' , response_model=Product_OUT)
async def API_read_product(proID: str):
    try:
        product_info = await Product.get(proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=404)
    return product_info


@product_router.post('/create_product') 
async def API_save_product(product: Product):
    await product.save()
    return {"message":f"product created successfully  , proID : {product.pk}"}


@product_router.delete('/delete_product/{proID}')
async def API_delete_product(proID: str):
    try:
        product_info = await Product.get(proID)
        await product_info.delete(pk=proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=404)
    return {"message":"product deleted successfully" }