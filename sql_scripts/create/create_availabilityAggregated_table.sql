-- Python should handle that the foreign Key used actually exists in ConnectorCounts.

CREATE TABLE availabilityAggregated (
    locationId TEXT, 
    revision INTEGER,
    chargingGroup INTEGER, 
    registeredTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    availableCount INTEGER,
    totalCount INTEGER,
    FOREIGN KEY (locationId, revision, chargingGroup) 
        REFERENCES connectorCounts(locationId, revision, chargingGroup)
);


