"""
Azure Static Web Apps API - FastAPI Backend
This serves the UP2D8 API through Static Web Apps managed functions
"""
import sys
import os

# Add backend directory to path so we can import the FastAPI app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import azure.functions as func
from api.main import app as fastapi_app

# Create the Static Web App function
app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
