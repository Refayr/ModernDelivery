# The Art and Science of Modern Delivery: From Factory to Final Mile

## Context
In today’s fast-paced world, the efficiency of delivery networks—spanning factories, supply depots, and the final destination—defines the backbone of global commerce. Whether by truck, car, or drone, each link in the chain must operate with precision to meet rising demands for speed, reliability, and sustainability.
_But how do businesses balance cost and efficiency while ensuring seamless logistics?_

The answer lies in leveraging data-driven strategies: _predictive analysis, real-time tracking and alternative delivery methods_ (such as drones and autonomous vehicles) to transform traditional supply chains.
This presentation explores the journey of goods—from production lines to doorsteps—and the cutting-edge solutions reshaping the future of delivery.

## Aim and Objectives

### Aim
_Optimize the delivery process from factory to customer_ by integrating data analytics and PostgreSQL database management.

### Objectives
_At this point, objectives may change regarding to the usability of the datasets._
+ _Route Optimization_: Minimize delivery times and maximize cargo load efficiency for each delivery vector (trucks, drones, etc.).
+ _Inventory Management_: Ensure optimal stock levels in supply depots to prevent stockouts and overstocking, aligning with demand forecasts.

## Datasets
To achieve these objectives, the following datasets could be utilized to build a comprehensive logistics database:

+ [Logistics and Supply Chain Dataset](https://www.kaggle.com/datasets/datasetengineer/logistics-and-supply-chain-dataset) – Focuses on shipment tracking, delivery times, and supply chain efficiency metrics.
+ [Delivery Logistics Dataset](https://www.kaggle.com/datasets/ayeshaseherr/delivery-logistics-dataset) – Contains data on delivery routes, timings, and performance indicators, useful for route optimization and last-mile delivery analysis.
+ [Transportation and Logistics Tracking Dataset](https://www.kaggle.com/datasets/nicolemachado/transportation-and-logistics-tracking-dataset) – Includes real-time tracking data for shipments, ideal for studying transportation efficiency and delays.
+ [Amazon Delivery Dataset](https://www.kaggle.com/datasets/sujalsuthar/amazon-delivery-dataset) – Focuses on last-mile logistics and delivery performance, with insights into delivery times, distances, and customer satisfaction.
+ [Logistics Shipment On-Time Delivery Classification Dataset](https://www.kaggle.com/datasets/sezginkaraglle/logistics-dataset) – Useful for predictive modeling to determine on-time delivery probabilities based on historical data.

## Setting up the environment
### PostgreSQL database creation
Be sure to have a PostgreSQL server running on you computer. You will also need to install PostGIS.
Then, create a database for this project and set the PostGIS extension (replace the username and the db name by yours):
- psql -U postgres -d gis_database
   - CREATE EXTENSION postgis;

### Python dependencies
pip install
- python = ">=3.12,<3.13"
- requests = ">=2.32.5,<3"
- keyring = ">=25.7.0,<26"
- pyside6 = ">=6.9.3, <7"
- shapely = ">=2.1.2,<3"

### PostgreSQL database creation
-- Table Countries
CREATE TABLE countries (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
);

-- Table Nodes
CREATE TABLE nodes (
    id VARCHAR(50) PRIMARY KEY,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- Table Seaports
CREATE TABLE seaports (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    node VARCHAR(50) REFERENCES nodes(id),
    country VARCHAR(10) REFERENCES countries(id)
);

-- Index pour les performances
CREATE INDEX idx_nodes_lat_lon ON nodes(latitude, longitude);
CREATE INDEX idx_seaports_node ON seaports(node);
CREATE INDEX idx_seaports_country ON seaports(country);

-- Table Ships
CREATE TABLE IF NOT EXISTS ships (
    imo VARCHAR(9) PRIMARY KEY,           -- IMO_Number (Clé primaire)
    mmsi VARCHAR(9),                      -- MMSI (extrait de Identifier)
    name VARCHAR(255),                    -- Nom du navire (utilisant Description par défaut)
    latitude DECIMAL(10, 7),              -- Latitude (nullable pour les navires sans position)
    longitude DECIMAL(10, 7),             -- Longitude (nullable)
    heading VARCHAR(50) REFERENCES seaports(id), -- ID du port de destination (Foreign Key vers Seaports)
    capacity INTEGER DEFAULT 0,           -- Capacité (défaut 0 car non fourni dans CSV)
    description TEXT,                     -- Description (Type de navire, etc.)
    type VARCHAR(100),                    -- Additional Type (Cargo, Fishing, etc.)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp de mise à jour (optionnel mais utile)
);

-- Index pour les performances
-- Permet de trouver rapidement un navire par MMSI
CREATE INDEX IF NOT EXISTS idx_ships_mmsi ON ships(mmsi);

-- Index spatial pour les requêtes de proximité (si vous voulez chercher les navires autour d'un point)
-- Nécessite l'extension postgis (déjà supposée active)
CREATE INDEX IF NOT EXISTS idx_ships_location ON ships USING GIST (ST_Point(longitude, latitude));

-- Index sur le champ heading pour les jointures avec Seaports
CREATE INDEX IF NOT EXISTS idx_ships_heading ON ships(heading);

-- Index sur le type pour les filtres (ex: afficher seulement les "Tankers")
CREATE INDEX IF NOT EXISTS idx_ships_type ON ships(type);
