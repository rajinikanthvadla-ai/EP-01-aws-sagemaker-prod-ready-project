# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application's code into the container
COPY . /app

# Make port 8501 available to the world outside this container (Streamlit's default port)
EXPOSE 8501

# Define environment variable for the API endpoint
# This should be replaced by the actual service endpoint in a K8s/ECS deployment
ENV API_ENDPOINT="http://fastapi-service:80/predict"

# Run streamlit when the container launches
CMD ["streamlit", "run", "app.py"] 