CREATE TABLE locations (
    locationId TEXT, 
    revision INTEGER, 
    name TEXT, 
    partnerStatus TEXT, 
    isRoamingPartner BOOLEAN, 
    origin TEXT, 
    coords_lat FLOAT, 
    coords_lng FLOAT, 
    ts_seconds BIGINT,
    ts_nanoseconds BIGINT,  
    PRIMARY KEY (locationId, revision)
);

CREATE INDEX idx_location_revision_speed_plugtype ON locations(locationId, revision)