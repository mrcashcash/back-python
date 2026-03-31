import os
import asyncpg
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from the .env file
load_dotenv()

app = FastAPI(title="Health Check API")
# Add this right after creating the app:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Angular's default port
    allow_methods=["*"],
    allow_headers=["*"],
)
# Fetch the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint that verifies server status and database connectivity.
    """
    health_status = {
        "server": "up",
        "database": "unknown"
    }

    if not DATABASE_URL:
        health_status["database"] = "unconfigured (DATABASE_URL missing)"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=health_status
        )

    try:
        # Open a connection, execute a simple query, and close it
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        
        health_status["database"] = "connected"
        return health_status

    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["error_details"] = str(e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )