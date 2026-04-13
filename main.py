from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import geopandas as gpd
from sqlalchemy import create_engine, text
import json
from typing import Dict

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])

db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

        # Added this back so the seeder works
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS peshawar_reports (
                id SERIAL PRIMARY KEY,
                farmer_name TEXT,
                crop_type TEXT,
                health_status TEXT,
                geometry geometry(Point, 4326)
            );
        """))

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


class FarmBoundary(BaseModel):
    owner_name: str
    crop_type: str
    geometry: Dict


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


@app.get("/api/get-boundaries")
def get_boundaries():
    query = "SELECT * FROM farm_boundaries"
    try:
        gdf = gpd.read_postgis(query, engine, geom_col='geometry')
        return json.loads(gdf.to_json())
    except Exception:
        return {"type": "FeatureCollection", "features": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
