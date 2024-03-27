# Use the official Python image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your FastAPI application
CMD ["uvicorn", "main:app", "--reload", "--host=0.0.0.0", "--port=8000"]
