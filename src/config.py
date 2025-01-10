from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = Field(None, description="App environment")
    MLFLOW_ENDOINT: str = Field(None, description="Example: http://localhost:5000")

    class Config:
        env_file = ".env"


settings = Settings()
