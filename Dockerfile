# Using Python base image version 3.8
FROM python:3.8

#Label it
LABEL maintainer="Ramakrishna Madugula"

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file into the container
COPY ./techtrends/requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./techtrends .

# Expose the application port
EXPOSE 3111

# Initialize the database with pre-defined posts
RUN python init_db.py

# Command to run the application on container start
CMD ["python", "app.py"]
