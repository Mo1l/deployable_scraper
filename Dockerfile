FROM python:3.14-slim

# Install git (required for git dependencies)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# create data/db
RUN mkdir -p ./data/db

# Copy pyproject.toml
COPY pyproject.toml ./

# This will now work because git is installed
RUN pip install -e .

# Copy the rest
COPY src/ ./src/

