# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app



# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app/src"
# Expose port 8000 to the outside world
EXPOSE 8000

# Run main.py when the container launches
CMD ["uvicorn", "src.api.endpoints.rag:app", "--host", "0.0.0.0", "--port", "8000"]
