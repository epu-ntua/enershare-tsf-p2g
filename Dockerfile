FROM deeptsf-dagster-base:latest

# Set the working directory in the container
WORKDIR /dagster-dev/
ENV DAGSTER_HOME=/dagster-dev

# Copy the current directory contents into the container at /leif_app
COPY ./deeptsf-dagster /dagster-dev/deeptsf-dagster/