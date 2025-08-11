# core/config.py
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    base_url: AnyUrl = "http://localhost:8000"
    username: str = "standard_user"
    password: str = "secret_sauce"
    headless: bool = True
    browser: str = "chromium"  # chromium|firefox|webkit
    artifacts_dir: str = "artifacts"

    class Config:
        env_prefix = "APP_"  # APP_BASE_URL, APP_USERNAME, ...

settings = Settings()  # import anywhere
