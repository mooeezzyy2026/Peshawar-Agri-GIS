from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from sqlalchemy import create_engine, text
import geopandas as gpd
from typing import Dict
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
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
    with engine.connect() as conn:
        conn.execute(sql, {"name": data.owner_name,
                     "crop": data.crop_type, "geom": geom_json})
        conn.commit()
    return {"message": "Saved"}


@app.get("/api/get-boundaries")
def get_boundaries():

    query = "SELECT *, ST_Area(geometry::geography) / 4046.86 AS acres FROM farm_boundaries"
    try:
        gdf = gpd.read_postgis(query, engine, geom_col='geometry')
        return json.loads(gdf.to_json())
    except:
        return {"type": "FeatureCollection", "features": []}


@app.get("/api/stats")
def get_stats():
    query = """
        SELECT COUNT(*) as count, 
               ROUND(SUM(ST_Area(geometry::geography)/4046.86)::numeric, 2) as acres 
        FROM farm_boundaries
    """
    with engine.connect() as conn:
        res = conn.execute(text(query)).fetchone()

        if res is not None:
            total_farms = res[0] if res[0] is not None else 0
            total_acres = float(res[1]) if res[1] is not None else 0.0
        else:
            total_farms = 0
            total_acres = 0.0

        return {
            "total_farms": total_farms,
            "total_acres": total_acres
        }


@app.delete("/api/delete-boundary/{id}")
def delete_boundary(id: int):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM farm_boundaries WHERE id = :id"), {"id": id})
        conn.commit()
    return {"message": "Deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
