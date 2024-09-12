from pydantic_settings import  BaseSettings

class ENV (BaseSettings):

    redis_username : str = ""
    redis_password : str = ""
    redis_database : str = ""  
    redis_host : str = "localhost"
    redis_port : str = "6379"
    RabbitMQ_host : str = "localhost"
    RabbitMQ_port  : str = ""
    RabbitMQ_user : str = "guest"
    RabbitMQ_password : str = "guest"

    class Config :
        env_file = ".env"

Evariable=ENV()