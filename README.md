# Modern Delivery Maritime Routing System

This project simulates maritime ship movement, rerouting, and chokepoint-based navigation using PostgreSQL with PostGIS. It models ships traveling between seaports while dynamically responding to geographic constraints such as ocean boundaries, and active/inactive chokepoints.

---

## 📦 Project Overview

The system is built entirely in SQL and focuses on:

- Loading and structuring maritime datasets
- Representing ships, seaports, and navigation constraints
- Simulating ship movement over time
- Handling rerouting when chokepoints become inactive
- Using spatial queries with PostGIS for geographic reasoning

---

## 🛠️ Requirements

Make sure to have the following installed:

- PostgreSQL: https://www.postgresql.org  
- PostGIS: https://postgis.net  
- pgAdmin: https://www.pgadmin.org  
- QGIS: https://www.qgis.org  

---

## 🗂️ Repository Structure

### 1. Schema Creation & CSV Import
`1-create_and_populate_schema_from_csv.sql`

- Creates core database tables (ships, seaports, ship_locations, etc.)
- Loads data from CSV files
- Initializes PostGIS geometry fields used throughout the project

---

### 2. Patches Data (QGIS Dump)
`2-create_and_populate_patches_from_dump.sql`

- Creates the **patches** table from a SQL dump
- Imports polygon data exported from QGIS
- Links patches to chokepoints

---

### 3. Ocean Data (SQL Dump)
`3-create_and_populate_oceans_from_dump.sql`

- Creates and populates ocean boundary dataset from a SQL dump
- Used to enforce navigation constraints (stay within water)

---

### 4. Routing & Simulation Logic
`4-rerouting_and_location_update_experimentation.sql`

- Simulates ship movement using:
  - Bearing calculations (`ST_Azimuth`)
  - Step-based projection (`ST_Project`)
- Applies land/ocean constraints
- Handles rerouting logic when chokepoints are inactive
- Updates ship positions dynamically

---

### 5. Triggers & Functions
`5-triggers_and_functions.sql`

- Implements procedural logic using PostgreSQL functions
- Automates rerouting when chokepoint status changes
- Uses triggers to react to database updates
- Ensures consistency between routing state and ship destinations

---

## 📊 Data Sources

The project uses CSV files to populate initial datasets:

- Ships (type, description, identifiers)
- Seaports (locations and countries)
- Ship locations (historical + current positions)
- Chokepoints and routing constraints

---

## 🧭 Core Concepts

### Ship Movement
Ships move step-by-step toward their destination using geospatial projections.

### Spatial Constraints
Movement is restricted by:
- Landmass avoidance
- Ocean boundary containment
- Chokepoint activity status

### Rerouting Logic
When a chokepoint becomes inactive:
- Ships in affected patches are identified
- Their destinations are reassessed
- New routing decisions are applied based on historical patterns

---

## 🛠️ Technologies Used

- PostgreSQL
- PostGIS
- QGIS (for spatial data preparation)
- SQL (procedural + recursive queries)

---

## 🚀 How to Run

1. Install PostgreSQL with PostGIS enabled
2. Run scripts in order: