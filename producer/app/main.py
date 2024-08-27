from fastapi import FastAPI
from ..router import seller


app = FastAPI()

app.include_router()
