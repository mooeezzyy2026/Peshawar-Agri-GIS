from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import geopandas as gpd
from sqlalchemy import create_engine, text
import json
from typing import Dict

app = FastAPI()

# SECURITY: Allow Frontend (5500/8000) to talk to Backend (8080)
app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])

# DATABASE CONNECTION
db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)

# INITIALIZE TABLES


def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        # Polygon Table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS farm_boundaries (
                id SERIAL PRIMARY KEY,
                owner_name TEXT,
                crop_type TEXT,
                geometry geometry(Polygon, 4326)
            );
        """))
        conn.commit()


init_db()

# DATA MODELS


class FarmBoundary(BaseModel):
    owner_name: str
    crop_type: str
    geometry: Dict

# ROUTES

# 1. SAVE: Receive a new farm from the map


@app.post("/api/add-boundary")
def add_boundary(data: FarmBoundary):
    geom_json = json.dumps(data.geometry)
    sql = text("""
        INSERT INTO farm_boundaries (owner_name, crop_type, geometry)
        VALUES (:name, :crop, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))
    """)
    try:
        with engine.connect() as conn:
            conn.execute(sql, {"name": data.owner_name,
                         "crop": data.crop_type, "geom": geom_json})
            conn.commit()
        return {"message": "Success! Farm saved."}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

# 2. READ: Send all saved farms back to the map


@app.get("/api/get-boundaries")
def get_boundaries():
    query = "SELECT * FROM farm_boundaries"
    try:
        # read_postgis converts database geometry to GeoJSON automatically
        gdf = gpd.read_postgis(query, engine, geom_col='geometry')
        return json.loads(gdf.to_json())
    except Exception:
        return {"type": "FeatureCollection", "features": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
