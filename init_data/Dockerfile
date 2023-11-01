# Use a Python base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy your initialization script and data folder into the container
COPY init_elastic.py /app/
COPY .env /app/
COPY data /app/data/

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Define the command to run your initialization script
CMD ["python", "-u", "init_elastic.py"]
