FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make script executable
RUN chmod +x run_pipeline.sh

# Default command
CMD ["./run_pipeline.sh"]