# Peshawar Agriculture Monitoring System (Agri-GIS)

A full-stack Geospatial application designed to digitize agricultural field reporting and crop health monitoring for the Peshawar region. This system replaces legacy paper-based workflows with a real-time, spatial database-driven architecture.

## 🚀 The Stack

- **Frontend:** Leaflet.js (Web Mapping), HTML5, CSS3, JavaScript (ES6+)
- **Backend:** Python, FastAPI (High-performance REST API)
- **Database:** PostgreSQL with **PostGIS** extension (Spatial Data Storage)
- **Data Engineering:** GeoPandas, SQLAlchemy

## 🛠️ Key Features

- **Polygon Digitizer:** Professional drawing tools for mapping exact farm boundaries.
- **Automated Spatial Analysis:** Real-time calculation of farm area in Acres using PostGIS `ST_Area`.
- **Industrial Sidebar UI:** A dedicated interface for attribute data entry (Owner Name, Crop Type).
- **Interactive Spatial Dashboard:** Visualize farm locations and crop data on a live map.
- **Real-time Data Entry:** Field workers can click the map to submit crop health reports directly to the database.
- **Spatial Database Architecture:** Uses PostGIS `geometry` types to handle coordinates accurately (EPSG:4326).
- **RESTful API:** Decoupled architecture allowing for future integration with Mobile (Flutter) or BI tools.

## 🏗️ System Architecture

1. **Data Layer:** PostgreSQL/PostGIS stores geometries and attribute data.
2. **Logic Layer:** FastAPI handles spatial queries and serves GeoJSON to the client.
3. **Presentation Layer:** Leaflet.js renders vector data and handles user interaction.

## 📖 How to Run

1. **Database:** Ensure Postgres.app is running and PostGIS extension is enabled.
2. **Backend:**

   ```bash
   pip install fastapi uvicorn geopandas sqlalchemy psycopg2-binary
   python3 main.py
   ```

   - **Automated Data Seeding:** Includes a Python utility to generate large-scale synthetic datasets for stress-testing spatial queries.
