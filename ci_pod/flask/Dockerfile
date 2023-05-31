# Use Fedora as the base image
FROM fedora:38

# Install Python 3 and pip, Flask, and boto3
RUN dnf update -y && \
    dnf install -y python3 python3-pip && \
    pip3 install flask boto3

# Copy the app directory
COPY app /app

# Set the working directory and change ownership
WORKDIR /app

# Set the user to root
USER root

# Start the application
CMD ["python3", "app.py"]
