import geopandas as gpd
from sqlalchemy import create_engine
from shapely.geometry import Polygon
import random

db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)

crops = ["Wheat", "Maize", "Sugarcane", "Tobacco", "Vegetables"]
farmers = ["Ali", "Ahmed", "Hassan", "Khan",
           "Zaman", "Bilal", "Sami", "Faisal"]


def seed_polygons(count=15):
    poly_data = []
    for i in range(count):
        lat, lng = 34.0151 + \
            random.uniform(-0.03, 0.03), 71.5249 + random.uniform(-0.03, 0.03)
        size = 0.002
        coords = [(lng, lat), (lng + size, lat), (lng + size,
                                                  lat + size), (lng, lat + size), (lng, lat)]
        poly_data.append({
            'owner_name': f"{random.choice(farmers)} Farm",
            'crop_type': random.choice(crops),
            'geometry': Polygon(coords)
        })
    gdf = gpd.GeoDataFrame(poly_data, crs="EPSG:4326")
    gdf.to_postgis("farm_boundaries", engine, if_exists="append")
    print(f"Uploaded {count} Polygons.")


if __name__ == "__main__":
    seed_polygons(15)
