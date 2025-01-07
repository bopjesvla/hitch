-- Add UNIQUE constraint so that foreign key works
CREATE UNIQUE INDEX PointId ON points (id);

-- Create temporary Points table
CREATE TABLE
  Temp_Points (
    ID INTEGER PRIMARY KEY,
    Latitude REAL,
    Longitude REAL,
    CreatedAt TEXT
  );

INSERT INTO
  Temp_Points (Latitude, Longitude, CreatedAt)
SELECT
  lat,
  lon,
  datetime
FROM
  points
GROUP BY
  lat,
  lon
ORDER BY
  datetime;

-- Reviews Table
CREATE TABLE
  Reviews (
    ID INTEGER PRIMARY KEY,
    Rating INTEGER,
    Duration INTEGER, -- Wait Time
    CreatedBy TEXT, -- IP Address / Username?
    CreatedAt TEXT,
    PointId INTEGER NOT NULL,
    OldPointId INTEGER, -- Will be removed later
    FOREIGN KEY (PointId) REFERENCES Temp_Points (ID)
  );

-- Comments Table
CREATE TABLE
  Comments (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    Comment TEXT,
    Signal TEXT,
    RideAt TEXT,
    PointId INTEGER NOT NULL,
    ReviewId INTEGER NOT NULL,
    FOREIGN KEY (PointId) REFERENCES Temp_Points (ID),
    FOREIGN KEY (ReviewId) REFERENCES Reviews (ID)
  );

-- Destinations Table
CREATE TABLE
  Destinations (
    ID INTEGER PRIMARY KEY,
    Latitude REAL,
    Longitude REAL,
    Distance REAL,
    PointId INTEGER NOT NULL,
    ReviewId INTEGER NOT NULL,
    FOREIGN KEY (PointId) REFERENCES Temp_Points (ID), -- Origin Point
    FOREIGN KEY (ReviewId) REFERENCES Reviews (ID)
  );

-- Loop through all Points to create Reviews
INSERT INTO
  Reviews (
    Rating,
    Duration,
    CreatedBy,
    CreatedAt,
    PointId,
    OldPointId
  )
SELECT
  CAST(points.rating as INTEGER),
  CAST(points.wait as INTEGER),
  points.ip,
  points.datetime,
  Temp_Points.ID,
  points.id
FROM
  points,
  Temp_Points
WHERE
  (
    points.comment NOT NULL
    OR points.signal NOT NULL
    OR points.wait NOT NULL
    OR points.rating NOT NULL
  )
  AND (
    points.lon = Temp_Points.Longitude
    AND points.lat = Temp_Points.Latitude
  );

-- Loop through all Points to create Destinations
-- TODO: Calculate Distance!
INSERT INTO
  Destinations (Latitude, Longitude, ReviewId, PointId)
SELECT
  points.dest_lat,
  points.dest_lon,
  Reviews.ID,
  Temp_Points.ID
FROM
  points,
  Reviews,
  Temp_Points
WHERE
  (
    points.dest_lat NOT NULL
    AND points.dest_lon NOT NULL
  )
  AND (
    points.lon = Temp_Points.Longitude
    AND points.lat = Temp_Points.Latitude
  )
  AND Reviews.OldPointId = points.id;

-- Loop through all Points to create Comments
-- TODO: Calculate Distance!
INSERT INTO
  Comments (Name, Comment, Signal, RideAt, PointId, ReviewId)
SELECT
  points.name,
  points.comment,
  points.signal,
  points.ride_datetime,
  Temp_Points.ID,
  Reviews.ID
FROM
  points,
  Reviews,
  Temp_Points
WHERE
  points.comment NOT NULL
  AND (
    points.lon = Temp_Points.Longitude
    AND points.lat = Temp_Points.Latitude
  )
  AND Reviews.OldPointId = points.id;

-- Duplicates
CREATE TABLE
  Temp_Duplicates (
    ID INTEGER PRIMARY KEY,
    FromPointId INTEGER NOT NULL,
    ToPointId INTEGER NOT NULL,
    CreatedBy TEXT, -- IP Address / Username?
    CreatedAt TEXT,
    FOREIGN KEY (FromPointId) REFERENCES Temp_Points (ID),
    FOREIGN KEY (ToPointId) REFERENCES Temp_Points (ID)
  );

INSERT INTO
  Temp_Duplicates (FromPointId, ToPointId, CreatedBy, CreatedAt)
SELECT
  t1.ID,
  t2.ID,
  duplicates.ip,
  duplicates.datetime
FROM
  duplicates,
  Temp_Points as t1,
  Temp_Points as t2
WHERE
  (
    duplicates.from_lat = t1.Latitude
    AND duplicates.from_lon = t1.Longitude
  )
  AND (
    duplicates.to_lat = t2.Latitude
    AND duplicates.to_lon = t2.Longitude
  );

-- Hitchwiki
CREATE TABLE
  Temp_Hitchwiki (
    ID INTEGER PRIMARY KEY,
    PointId INTEGER NOT NULL,
    Link TEXT NOT NULL,
    CreatedBy TEXT, -- IP Address / Username?
    CreatedAt TEXT,
    FOREIGN KEY (PointId) REFERENCES Temp_Points (ID)
  );

INSERT INTO
  Temp_Hitchwiki (PointId, Link, CreatedBy, CreatedAt)
SELECT
  Temp_Points.ID,
  hitchwiki.link,
  hitchwiki.ip,
  hitchwiki.datetime
FROM
  hitchwiki,
  Temp_Points
WHERE
  (
    hitchwiki.lat = Temp_Points.Latitude
    AND hitchwiki.lon = Temp_Points.Longitude
  );

-- Delete old tables and rename temporary tables
DROP TABLE points;

DROP TABLE duplicates;

DROP TABLE hitchwiki;

ALTER TABLE Temp_Points
RENAME TO Points;

ALTER TABLE Temp_Duplicates
RENAME TO Duplicates;

ALTER TABLE Temp_Hitchwiki
RENAME TO Hitchwiki;

ALTER TABLE Reviews
DROP COLUMN OldPointId;

-- Anonymous == NULL
UPDATE Comments
SET
  Name = NULL
WHERE
  Name = 'Anonymous'
  OR NAME = 'anonymous'
  OR NAME = 'Anon'
  OR NAME = 'Anonym';