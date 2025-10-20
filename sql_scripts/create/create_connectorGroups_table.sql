CREATE TABLE connectorGroups (
    locationId TEXT, 
    revision INTEGER,
    connectorGroup INTEGER,  
    plugType TEXT, 
    speed TEXT, 
    count INT,
    PRIMARY KEY (locationId, revision, connectorGroup),
    UNIQUE(locationId, revision, speed, plugType),
    FOREIGN KEY (locationId, revision) 
        REFERENCES locations(locationId, revision)
);

CREATE INDEX idx_location_revision_speed_plugtype ON connectorGroups(locationId, revision, speed, plugType)