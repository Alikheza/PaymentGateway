from fastapi import APIRouter , HTTPException , status
from ..schema.product import Product  , ProductSchema
from aredis_om import NotFoundError

product_router = APIRouter()


@product_router.get('/read_product/{proID}', response_model=ProductSchema ,status_code=status.HTTP_200_OK)
async def API_read_product(proID: str):
    try:
        product_info = await Product.get(proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    return product_info


@product_router.post('/create_product', status_code=status.HTTP_201_CREATED) 
async def API_save_product(product: ProductSchema):
    new_product = Product(**product.model_dump())
    await new_product.save()
    return {"message":"product created successfully", "proID" :f"{new_product.pk}"}


@product_router.put('/update_product/{proID}', status_code=status.HTTP_200_OK)
async def API_update_product(product: ProductSchema , proID: str):
    try: 
        product_info = await Product.get(proID)
        await product_info.update(**product.model_dump())
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception :
        raise HTTPException(detail="the update process failed", status_code=status.HTTP_400_BAD_REQUEST)
    return {"message":"product updated successfully"}


@product_router.delete('/delete_product/{proID}', status_code=status.HTTP_200_OK)
async def API_delete_product(proID: str):
    try:
        product_info = await Product.get(proID)
        await product_info.delete(pk=proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    return {"message":"product deleted successfully"}