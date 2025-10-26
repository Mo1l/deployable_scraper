CREATE TABLE locations (
    locationId TEXT, 
    revision INTEGER, 
    name TEXT, 
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    partnerStatus TEXT, 
    isRoamingPartner BOOLEAN, 
    origin TEXT, 
    coords_lat FLOAT, 
    coords_lng FLOAT, 
    ts_seconds BIGINT,
    ts_nanoseconds BIGINT,  
    PRIMARY KEY (locationId, revision)
);

CREATE INDEX idx_locationId_revision ON locations(locationId, revision)