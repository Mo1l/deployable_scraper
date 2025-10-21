
DROP VIEW IF EXISTS latest_connector_groups; -- "OR REPLACE"
CREATE VIEW latest_connector_groups AS
WITH latest_revisions AS (
  SELECT 
    locationId,
    MAX(revision) as revision
  FROM locations
  GROUP BY locationId
)
SELECT cg.*
FROM latest_revisions lr
INNER JOIN connectorGroups cg
ON lr.locationId = cg.locationId AND lr.revision = cg.revision;



