# Use official Python runtime
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /exporters

# Copy the current directory contents into /app
COPY . /exporters

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose exporter port
EXPOSE 9110

# Run db_activity_exporter.py when the container launches
CMD ["python", "db_activity_exporter.py"]
