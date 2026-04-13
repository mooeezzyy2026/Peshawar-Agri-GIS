import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from shapely.geometry import Point, Polygon
import random

db_url = "postgresql://localhost:5432/moeezelahi"
engine = create_engine(db_url)

CENTER_LAT = 34.0151
CENTER_LNG = 71.5249

crop = ["wheat", "Maize", "Sugarcane", "Tobacco", "Vegetables"]
farmers = ["Ali", "Ahmed", "Hassan", "Khan",
           "Zaman", "Bilal", "Sami", "Faisal"]
statuses = ["Healthy", "Sick", "Warning"]


def seed_points(count=20):
    points_data = []
    for i in range(count):
        lat = CENTER_LAT + random.uniform(-0.05, 0.05)
        lng = CENTER_LNG + random.uniform(-0.05, 0.05)
        points_data.append({
            "farmer_name": random.choice(farmers),
            "crop_type": random.choice(crop),
            "health_status": random.choice(statuses),
            "geometry": Point(lng, lat)  # Changed 'geom' to 'geometry'
        })

    gdf = gpd.GeoDataFrame(points_data, geometry='geometry', crs="EPSG:4326")
    gdf.to_postgis("peshawar_reports", engine, if_exists="append")
    print(f"UPLOADED {count} Random POINTS TO DATABASE.")


def seed_polygons(count=10):
    poly_data = []
    for i in range(count):
        lat = CENTER_LAT + random.uniform(-0.05, 0.05)
        lng = CENTER_LNG + random.uniform(-0.05, 0.05)
        size = 0.002
        coords = [(lng, lat), (lng + size, lat), (lng + size,
                                                  lat + size), (lng, lat + size), (lng, lat)]
        poly_data.append({
            'owner_name': f"{random.choice(farmers)} Farm {i}",
            'crop_type': random.choice(crop),
            'geometry': Polygon(coords)
        })

    gdf_poly = gpd.GeoDataFrame(
        poly_data, geometry='geometry', crs="EPSG:4326")
    gdf_poly.to_postgis("farm_boundaries", engine, if_exists="append")
    print(f"UPLOADED {count} Random POLYGONS TO DATABASE.")


if __name__ == "__main__":
    seed_points(20)
    seed_polygons(10)
    print("------- Full Scale data is been seeded into the database. -------")
