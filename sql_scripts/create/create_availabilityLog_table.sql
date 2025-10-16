-- Foreign Key onto evseIds table
CREATE TABLE availabilityLog (
    locationId TEXT, 
    revision INTEGER,
    evseId TEXT, 
    registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- info within 'availibility' within 'evses'
    status TEXT, 
    timestamp TEXT, 

    FOREIGN KEY (locationId, revision, evseId) 
        REFERENCES evseIds(locationId, revision, evseId)
);