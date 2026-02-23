# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from pydantic_settings import BaseSettings

# env_path = Path(__file__).parent.parent.parent / ".env"
# load_dotenv(env_path)

# class Settings(BaseSettings):
#     PROJECT_NAME: str = "Resume Screening AI"
#     API_V1_PREFIX: str = "/api/v1"
#     ENVIRONMENT: str = "development"
#     GEMINI_API_KEY: str | None = None

#     class Config:
#         env_file = ".env"

# settings = Settings()


from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Resume Screening Engine"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    GEMINI_API_KEY: str | None = None
    UPLOAD_DIR: str = "tmp_resumes"

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def check_api_key(cls, v: str | None, info) -> str | None:
        # Correctness: Fail-fast logic for production
        if info.data.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("GEMINI_API_KEY must be set in production")
        return v

    class Config:
        env_file = ".env"


settings = Settings()
