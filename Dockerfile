FROM python:3.14-slim

# Install git (required for git dependencies)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# create data/db
RUN mkdir -p ./data/db ./data/logs

# Copy pyproject.toml
COPY pyproject.toml ./
COPY src/ ./src/

# This will now work because git is installed
RUN pip install -e . -v 

# Copy the rest

CMD ["python", "src/main_scripts/run_scraper_schedule.py"]