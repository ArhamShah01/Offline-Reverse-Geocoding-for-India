import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

INPUT_EXCEL = "database.xlsx"
OUTPUT_EXCEL = "reverse_geocoded_database.xlsx"

CRS_GEOGRAPHIC = "EPSG:4326"
CRS_PROJECTED = "EPSG:3857"

PINCODE_GEOJSON = "All_India_pincode_Boundary.geojson"
PINCODE_FIELD = "Pincode"

LAYERS = {
    "state": {
        "path": "STATE_BOUNDARY.shp",
        "column": "STATE",
        "type": "polygon"
    },
    "district": {
        "path": "DISTRICT_BOUNDARY.shp",
        "column": "DISTRICT",
        "type": "polygon"
    },
    "subdistrict": {
        "path": "SUBDISTRICT_BOUNDARY.shp",
        "column": "Sub_dist",
        "type": "polygon"
    },
    "state_capital": {
        "path": "STATE_HQ.shp",
        "column": "CAPITAL_NA",
        "type": "point"
    },
    "district_hq": {
        "path": "DISTRICT_HQ.shp",
        "column": "HQ",
        "type": "point"
    }
}

def validate_lat_lon(lat, lon):
    return (
        isinstance(lat, (int, float)) and
        isinstance(lon, (int, float)) and
        -90 <= lat <= 90 and
        -180 <= lon <= 180
    )

def load_layer(cfg, name):
    print(f"📂 Checking file: {cfg['path']}")
    if not os.path.exists(cfg["path"]):
        raise FileNotFoundError(cfg["path"])
    print(f"📖 Reading layer: {name}")
    gdf = gpd.read_file(cfg["path"], engine="pyogrio")
    if cfg["column"] not in gdf.columns:
        raise ValueError(cfg["column"])
    gdf = gdf[[cfg["column"], "geometry"]].to_crs(CRS_GEOGRAPHIC)
    print(f"✅ {name} layer loaded")
    return gdf

def reverse_geocode():
    print("\n" + "=" * 60)
    print("🚀 OFFLINE REVERSE GEOCODING PIPELINE STARTED")
    print("=" * 60)

    print(f"📄 Input file: {INPUT_EXCEL}")
    if not os.path.exists(INPUT_EXCEL):
        raise FileNotFoundError(INPUT_EXCEL)

    print("📊 Reading Excel file")
    df = pd.read_excel(INPUT_EXCEL)
    print(f"✅ Rows loaded: {len(df)}")

    if not {"latitude", "longitude"}.issubset(df.columns):
        raise ValueError("latitude/longitude")

    print("🧪 Validating coordinates")
    df["__valid__"] = df.apply(
        lambda r: validate_lat_lon(r["latitude"], r["longitude"]),
        axis=1
    )
    print(f"⚠️ Invalid rows: {(~df['__valid__']).sum()}")

    print("📍 Creating point geometries")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[
            Point(lon, lat) if v else None
            for lat, lon, v in zip(df.latitude, df.longitude, df["__valid__"])
        ],
        crs=CRS_GEOGRAPHIC
    )
    print("✅ Point layer created")

    print("🗂️ Loading administrative layers")
    layers = {k: load_layer(v, k) for k, v in LAYERS.items()}

    print("🧩 Performing polygon spatial joins")
    for k, cfg in LAYERS.items():
        if cfg["type"] == "polygon":
            print(f"➡️  Joining {k}")
            gdf = gpd.sjoin(
                gdf,
                layers[k].rename(columns={cfg["column"]: k}),
                how="left",
                predicate="within"
            ).drop(columns="index_right", errors="ignore")
            print(f"✅ {k} joined")

    print("📐 Projecting data for nearest-neighbor joins")
    gdf_proj = gdf.to_crs(CRS_PROJECTED)

    print("📌 Assigning nearest headquarters")
    for k, cfg in LAYERS.items():
        if cfg["type"] == "point":
            print(f"➡️  Finding nearest {k}")
            hq_proj = layers[k].to_crs(CRS_PROJECTED)
            gdf_proj = gpd.sjoin_nearest(
                gdf_proj,
                hq_proj.rename(columns={cfg["column"]: k}),
                how="left"
            ).drop(columns="index_right", errors="ignore")
            print(f"✅ {k} assigned")

    print("🌍 Reprojecting back to geographic CRS")
    gdf = gdf_proj.to_crs(CRS_GEOGRAPHIC)

    print("📮 Loading PIN code boundaries")
    if not os.path.exists(PINCODE_GEOJSON):
        raise FileNotFoundError(PINCODE_GEOJSON)

    gdf_pin = gpd.read_file(PINCODE_GEOJSON).to_crs(CRS_GEOGRAPHIC)

    if PINCODE_FIELD not in gdf_pin.columns:
        raise ValueError(PINCODE_FIELD)

    print("🏷️ Assigning PIN codes")
    gdf = gpd.sjoin(
        gdf,
        gdf_pin[[PINCODE_FIELD, "geometry"]],
        how="left",
        predicate="within"
    ).drop(columns="index_right", errors="ignore")
    print("✅ PIN codes assigned")

    print("🧹 Cleaning temporary columns")
    gdf = gdf.drop(columns=["geometry", "__valid__"], errors="ignore")

    print(f"💾 Writing output file: {OUTPUT_EXCEL}")
    gdf.to_excel(OUTPUT_EXCEL, index=False)

    print("=" * 60)
    print("🎉 REVERSE GEOCODING COMPLETED SUCCESSFULLY")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    reverse_geocode()
