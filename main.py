from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import geopandas as gpd
from sqlalchemy import create_engine, text
import json

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])
db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("Create Extension, IF NOT EXISTS postgis;"))
        conn.execute(text("""Create TABLE if not EXISTS postgis;
                      peshawar_reports(
                        id SERIAL PRIMARY KEY,
                        farmer_name TEXT,
                        crop_type TEXT,
                        health_status TEXT,
                        geometry geometry(Point, 4326);
                      );"""))
        conn.commit()

        init_db()

        class CropReport(BaseModel):
            farmer_name: str
            crop_type: str
            health_status: str
            latitude: float
            longitude: float

            app.get("/api/reports")

            def get_reports():
                query = "SELECT * FROM peshawar_reports;"
                try:
                    gdf = gpd.read_postgis(query, engine, geom_col='geometry')
                    return json.loads(gdf.to_json())
                except Exception:
                    return {"type": "FeatureCollection", "features": []}


@app.post("/api/reports/add-report")
def add_report(data: CropReport):
    sql = text("""INSERT INTO peshawar_reports (farmer_name, crop_type, health_status, geometry)
                VALUES (:farmer, :crop, :status, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326));""")
    with engine.connect() as conn:
        conn.execute(sql, {"farmer": data.farmer_name, "crop": data.crop_type,
                     "status": data.status, "lng": data.longitude, "lat": data.latitude})
        conn.commit()
    return {"message": " Peshawar Farm Report added successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
