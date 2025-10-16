-- Python should handle that the foreign Key used actually exists in ConnectorCounts.

CREATE TABLE availabilityAggregated (
    locationId TEXT, 
    revision INTEGER,
    chargingGroup INTEGER, 
    registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    connectors_available INTEGER,
    connectors_total INTEGER,
    FOREIGN KEY (locationId, revision, chargingGroup) 
        REFERENCES connectorCounts(locationId, revision, chargingGroup)
);


