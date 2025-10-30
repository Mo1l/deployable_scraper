The repository provides a functional setup for scraping with apis, with easy deployment on a raspberry pi or a cloud service using dockers. Data is currently stored in SQLITE database, and scheduling is handled with the use of the schedule module. Environment options in the docker compose file can be used to control scraping intervals. 

The database has to be adapted to the use case and the api being called, but can be done by adding the necessary sql scripts. 

planned features and updates: postgredatabase, scheduling using chron, logging for easier debugging and mail notifications.  

just clone the repository onto your raspberry pi (or what you want to deploy on) and run the command .sh script.
