-- Run the queries below to create and populate the tables of the Modern_Delivery Database;

-- General set up:
-- Added to ensure that if any non-ASCII character (for example, letters with accents) is encountered, PostgresSQL will store it correctly
SET client_encoding = 'UTF8'; 
CREATE EXTENSION pgrouting; -- Add extension to later use for ship routing;
CREATE EXTENSION IF NOT EXISTS postgis; -- Make sure to add the PostGIS extension to work with geographical and geometric data;


-- Table 1:
-- Create table ships:
CREATE TABLE ships (
    imo VARCHAR(9) NOT NULL,
    description VARCHAR(100),
	ship_type VARCHAR(50) NULL,
    PRIMARY KEY (imo)
);

-- Populate the table:
COPY ships(imo, description, ship_type)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/ships.csv'
WITH CSV HEADER;


-- Table 2:
-- Create table freight_ships:
CREATE TABLE freight_ships (
    imo VARCHAR(9) NOT NULL,
    capacity INT DEFAULT 0,
    PRIMARY KEY (imo),
    FOREIGN KEY (imo) REFERENCES ships(imo)
);

-- Populate the table:
COPY freight_ships(imo, capacity)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/freight_ships.csv'
WITH CSV HEADER;


-- Table 3:
-- Create table countries:
CREATE TABLE countries (
    country_id VARCHAR(5) NOT NULL,
    country_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (country_id)
);

-- Populate the table:
COPY countries(country_id, country_name)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/countries.csv'
WITH CSV HEADER;


-- Table 4:
-- Create table seaports:
CREATE TABLE seaports (
    seaport_id VARCHAR(10) NOT NULL,
    seaport_name VARCHAR(50) NOT NULL,
    country_id VARCHAR(5),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
	wkb_geometry geography(Point, 4326),
    PRIMARY KEY (seaport_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Populate the table:
COPY seaports(seaport_id, seaport_name, country_id, latitude, longitude)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/seaports.csv'
WITH CSV HEADER;


UPDATE seaports
SET wkb_geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);

-- Table 5:
-- Create table chokepoints:
CREATE TABLE chokepoints (
    chokepoint_name VARCHAR(20) NOT NULL,

    lat1 DOUBLE PRECISION NOT NULL, lon1 DOUBLE PRECISION NOT NULL,
    lat2 DOUBLE PRECISION NOT NULL, lon2 DOUBLE PRECISION NOT NULL,
    lat3 DOUBLE PRECISION NOT NULL, lon3 DOUBLE PRECISION NOT NULL,
    lat4 DOUBLE PRECISION NOT NULL, lon4 DOUBLE PRECISION NOT NULL,
    lat5 DOUBLE PRECISION NOT NULL, lon5 DOUBLE PRECISION NOT NULL,
    lat6 DOUBLE PRECISION,
    lon6 DOUBLE PRECISION,
    lat7 DOUBLE PRECISION,
    lon7 DOUBLE PRECISION,
    lat8 DOUBLE PRECISION,
    lon8 DOUBLE PRECISION,

    active BOOLEAN DEFAULT TRUE,
    polygon GEOMETRY(POLYGON, 4326),

    PRIMARY KEY (chokepoint_name)
);

COPY chokepoints(
    chokepoint_name,
    lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4,
    lat5, lon5, lat6, lon6, lat7, lon7, lat8, lon8,
    active
)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/chokepoint.csv'
WITH CSV HEADER;

UPDATE chokepoints
SET polygon = ST_MakePolygon(
    ST_MakeLine(ARRAY[
        ST_MakePoint(lon1, lat1),
        ST_MakePoint(lon2, lat2),
        ST_MakePoint(lon3, lat3),
        ST_MakePoint(lon4, lat4),
        ST_MakePoint(lon5, lat5),
        ST_MakePoint(lon6, lat6),
        ST_MakePoint(lon7, lat7),
        ST_MakePoint(lon8, lat8),
        ST_MakePoint(lon1, lat1)
    ])
);


-- Table 6:
-- Note that table patches was created differently compared to others:
-- It contains polygones that we have manually created in QGIS to represent patches;
-- It was exported from QGIS as a SQL Dump, this is why we export it separately;
-- SELECT * FROM patches;


-- Table 7:
-- Create table ship_locations:
CREATE TABLE ship_locations (
    imo VARCHAR(9) NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
	wkb_geometry geography(Point, 4326),
	PRIMARY KEY (imo, updated_at),
    FOREIGN KEY (imo) REFERENCES ships(imo)
);

-- Populate the table:
COPY ship_locations(imo, updated_at, latitude, longitude)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/ship_locations.csv'
WITH CSV HEADER;

UPDATE ship_locations
SET wkb_geometry = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);


-- Table 8:
-- Create table loads:
CREATE TABLE loads (
    imo VARCHAR(9) NOT NULL,
    load_type VARCHAR(30) NOT NULL,
    quantity INT,
    PRIMARY KEY (imo),
    FOREIGN KEY (imo) REFERENCES freight_ships(imo)
);

-- Populate the table:
COPY loads(imo, load_type, quantity)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/loads.csv'
WITH CSV HEADER;

-- Table 9:
-- Create table heading_to:
CREATE TABLE heading_to (
    imo VARCHAR(9) NOT NULL,
    seaport_id VARCHAR(10) NULL,
    PRIMARY KEY (imo),
    FOREIGN KEY (imo) REFERENCES ships(imo),
    FOREIGN KEY (seaport_id) REFERENCES seaports(seaport_id)
);

-- Populate the table:
COPY heading_to(imo, seaport_id)
FROM 'C:/ModernDelivery/ModernDelivery/res/data/heading_to.csv'
WITH CSV HEADER;

