from fastapi import APIRouter , HTTPException , status
from ..schema.product import Product  , ProductSchema
from aredis_om import NotFoundError

product_router = APIRouter()


@product_router.get('/read_product/{proID}', response_model=ProductSchema ,status_code=status.HTTP_200_OK)
async def API_read_product(proID: str):
    """
    Fetch product details by product ID.

    Args:
        proID (str): The unique identifier of the product to retrieve.

    Returns:
        ProductSchema: The product data if found.

    Raises:
        HTTPException: If the product is not found (404 Not Found).
    """
    try:
        product_info = await Product.get(proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    return product_info


@product_router.post('/create_product', status_code=status.HTTP_201_CREATED) 
async def API_save_product(product: ProductSchema):
    """
    Create a new product.

    Args:
        product (ProductSchema): The product data to be saved.

    Returns:
        dict: A success message and the newly created product ID.
    """
    new_product = Product(**product.model_dump())
    await new_product.save()
    return {"message":"product created successfully", "proID" :f"{new_product.pk}"}


@product_router.put('/update_product/{proID}', status_code=status.HTTP_200_OK)
async def API_update_product(product: ProductSchema , proID: str):
    """
    Update product details by product ID.

    Args:
        product (ProductSchema): The new product data to update.
        proID (str): The unique identifier of the product to update.

    Returns:
        dict: A success message if the product is updated.

    Raises:
        HTTPException: 
            - If the product is not found (404 Not Found).
            - If an error occurs during the update process (400 Bad Request).
    """
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
    """
    Delete a product by product ID.

    Args:
        proID (str): The unique identifier of the product to delete.

    Returns:
        dict: A success message if the product is deleted.

    Raises:
        HTTPException: If the product is not found (404 Not Found).
    """
    try:
        product_info = await Product.get(proID)
        await product_info.delete(pk=proID)
    except NotFoundError:
        raise HTTPException(detail="product NOT found", status_code=status.HTTP_404_NOT_FOUND)
    return {"message":"product deleted successfully"}