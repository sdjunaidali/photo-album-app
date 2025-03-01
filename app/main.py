from fastapi import FastAPI
from app.api import users, photos, groups
from app.services.minio_client import setup_minio_bucket
from app.core.config import settings
import os

# Define the lifespan for the app
async def app_lifespan(app: FastAPI):
    # Perform startup tasks
    setup_minio_bucket()  # Ensure the MinIO bucket exists
    yield  # Control flow will pause here during the lifespan of the app
    # Perform shutdown tasks if needed
    print("Shutting down the application.")

# Create the FastAPI app with a lifespan context
app = FastAPI(title="Photo Album App", debug=settings.debug, lifespan=app_lifespan)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(photos.router, prefix="/photos", tags=["Photos"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])

# Get host and port from environment
HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)