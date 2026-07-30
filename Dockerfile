# Use the official Microsoft Playwright Python image based on jammy (Ubuntu 22.04)
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Hugging Face Spaces runs containers on port 7860
ENV PORT=7860

# Set up a non-root user (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Change ownership of the app directory to the non-root user
RUN chown -R user:user /app
USER user

# Expose the port for the FastAPI server
EXPOSE 7860

# Command to run uvicorn server binding to 0.0.0.0 and the port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 7860"]
