# Use the official lightweight Python image.
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8080

# Run the application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "wsgi:app"]
