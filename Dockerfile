# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first (leverage Docker cache for dependencies)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini alembic.ini
COPY migrations/ migrations/

# Copy the rest of the application code into the container
COPY . .

# Expose the application port
EXPOSE 8000

# Set the environment variable for Python to run in unbuffered mode (useful for logs)
ENV PYTHONUNBUFFERED=1

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Make sure the entrypoint script is executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to run the migrations and then the FastAPI app
ENTRYPOINT ["/entrypoint.sh"]

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]