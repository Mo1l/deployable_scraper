CREATE TABLE connectorCounts (
    locationId TEXT, 
    revision INTEGER,
    chargingGroup INTEGER,  
    type TEXT, 
    count INT,
    speed TEXT, 
    plugType TEXT, 
    PRIMARY KEY (locationId, revision, chargingGroup),
    UNIQUE(locationId, revision, speed, plugType),
);

CREATE TRIGGER create_chargingGroup_var
BEFORE INSERT ON connectorCounts
FOR EACH ROW
WHEN NEW.chargingGroup IS NULL
BEGIN 
    SELECT COALESCE(MAX(chargingGroup), 0) + 1
    FROM connectorCounts 
    where locationId = NEW.locationId AND revision = NEW.revision
    INTO NEW.chargingGroup;
END;

CREATE INDEX idx_location_revision_speed_plugtype ON connectorCounts(locationId, revision, speed, plugType)