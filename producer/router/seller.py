from fastapi import APIRouter


seller = APIRouter()

@seller.get('/read_products/{proID}')
def API_read_product(proID : str = None):
    pass


@seller.post('/create_product/')
def API_create_product():
    pass


@seller.delete('/delete_product/{proID}')
def API_delete_product():
    pass


