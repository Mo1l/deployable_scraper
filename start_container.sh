### This will spin up the container ###

# create desired folder structure
mkdir -p data/db data/logs

# makes the script executable
chmod +x start_container.sh

# spin up the container
docker compose up -d