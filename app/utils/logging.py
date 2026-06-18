"""
Logging Configuration

Configures application logging using loguru.
"""

import sys
from typing import Any

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging.
    
    Sets up loguru with appropriate formatters and handlers
    based on the environment.
    """
    # Remove default handler
    logger.remove()
    
    # Define log format
    if settings.is_development:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        log_level = "DEBUG"
    else:
        log_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        log_level = "INFO"
    
    # Add stdout handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=settings.is_development,
    )
    
    # Add file handler for production
    if settings.is_production:
        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
        )
        
        logger.add(
            "logs/error.log",
            format=log_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
        )
    
    logger.info(f"Logging configured for {settings.environment} environment")


def get_logger(name: str = __name__) -> Any:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
