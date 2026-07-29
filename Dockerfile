# Use the official Microsoft Playwright Python image based on jammy (Ubuntu 22.04)
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port for the FastAPI server
EXPOSE 8000

# Command to run uvicorn server binding to 0.0.0.0 and the port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
