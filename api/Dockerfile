# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first for better caching
COPY api/requirements.txt ./requirements.txt

# Install all dependencies in one layer
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code into the container at /app
COPY api/ ./api/

# Copy data and other necessary files
COPY data/ ./data/
COPY BellaTerra/ ./BellaTerra/
COPY chroma_db/ ./chroma_db/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the API when the container launches
CMD ["sh", "-c", "cd /app && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"]
