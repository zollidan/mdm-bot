import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# MARK: settings

class Settins(BaseSettings):
    BOT_TOKEN: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    model_config = SettingsConfigDict(env_file= os.path.join(os.path.dirname(__file__), ".env"))

settings = Settins()