from pydantic_settings import  BaseSettings

class ENV (BaseSettings):

    redis_username : str = ""
    redis_password : str = ""
    redis_database : str = ""  
    redis_host : str = "localhost"
    redis_port : str = "6379"

    class Config :
        env_file = ".env"

Evariable=ENV()