# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables to avoid Python writing pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire FastAPI project to the container
COPY . /app/

# Expose the port on which the FastAPI app will run
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
