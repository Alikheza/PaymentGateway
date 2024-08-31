from typing import Optional
from pydantic_settings import  BaseSettings

class ENV (BaseSettings):

    redis_username : Optional[str] = ""
    redis_password : Optional[str] = ""
    redis_database : Optional[str] = ""  
    redis_host : str = "localhost"
    redis_port : str = "6379"

    class Config :
        env_file = ".env"

Evariable=ENV()