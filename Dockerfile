FROM python:3.10.12-slim

# Set the working directory in the container
WORKDIR /dagster-dev/
ENV DAGSTER_HOME=/dagster-dev

# Copy the current directory contents into the container at /leif_app
COPY ./python_requirements.txt /dagster-dev/python_requirements.txt
COPY ./deeptsf-dagster /dagster-dev/deeptsf-dagster/

# Install build-essential and other necessary system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*
    
# Install any needed packages specified in requirements.txt and cleanup temp files
# RUN apt update && apt upgrade --no-cache-dir
RUN pip install -r /dagster-dev/python_requirements.txt \ 
    && rm -rf /var/cache/apk/* /tmp/*
