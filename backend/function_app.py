"""
Azure Functions wrapper for FastAPI application
This file enables the FastAPI app to run on Azure Functions
"""
import logging
import azure.functions as func
from api.main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Azure Functions app with ASGI middleware
app = func.AsgiFunctionApp(
    app=fastapi_app,
    http_auth_level=func.AuthLevel.ANONYMOUS
)

logger.info("Azure Functions app initialized with FastAPI")
