"""Configuration for the application"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API
    api_title: str = "Multi-Agent Productivity Assistant"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8000))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./productivity_assistant.db")
    
    # Agents
    max_workflow_steps: int = 100
    workflow_timeout: int = 300  # 5 minutes
    
    # Tools
    calendar_timeout: int = 30
    task_manager_timeout: int = 30
    notes_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
