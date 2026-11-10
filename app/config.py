from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   database_url: str = "sqlite:////app/data/pricinghub.db"

class Config:
        env_file = ".env"


settings = Settings()