import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# ================= CONFIG =================
INPUT_EXCEL = "database.xlsx"
OUTPUT_EXCEL = "reverse_geocoded_database.xlsx"

CRS_GEOGRAPHIC = "EPSG:4326"

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

CAPITAL_OVERRIDE = {
    "HARYANA": "CHANDIGARH",
    "PUNJAB": "CHANDIGARH"
}

DISPUTED_KEYWORD = "DISPUTED"

# ================= HELPERS =================
def validate_lat_lon(lat, lon):
    return (
        pd.notna(lat) and
        pd.notna(lon) and
        -90 <= lat <= 90 and
        -180 <= lon <= 180
    )

def load_layer(cfg, name):
    if not os.path.exists(cfg["path"]):
        raise FileNotFoundError(cfg["path"])
    gdf = gpd.read_file(cfg["path"], engine="pyogrio")
    if cfg["column"] not in gdf.columns:
        raise ValueError(f"{cfg['column']} missing in {cfg['path']}")
    return gdf[[cfg["column"], "geometry"]].to_crs(CRS_GEOGRAPHIC)

def normalize(s):
    return s.astype(str).str.upper().str.strip()

# ================= MAIN =================
def reverse_geocode():

    print("\n" + "-" * 60)
    print("OFFLINE REVERSE GEOCODING PIPELINE STARTED")
    print("-" * 60)

    df = pd.read_excel(INPUT_EXCEL)

    # Clean lat / lon
    df["latitude"] = pd.to_numeric(df["latitude"].astype(str).str.strip(), errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"].astype(str).str.strip(), errors="coerce")

    df["__valid__"] = df.apply(
        lambda r: validate_lat_lon(r["latitude"], r["longitude"]),
        axis=1
    )

    gdf = gpd.GeoDataFrame(
        df,
        geometry=[
            Point(lon, lat) if v else None
            for lat, lon, v in zip(df.latitude, df.longitude, df["__valid__"])
        ],
        crs=CRS_GEOGRAPHIC
    )

    # Load layers
    layers = {k: load_layer(v, k) for k, v in LAYERS.items()}

    # Polygon joins
    for k, cfg in LAYERS.items():
        if cfg["type"] == "polygon":
            gdf = gpd.sjoin(
                gdf,
                layers[k].rename(columns={cfg["column"]: k}),
                how="left",
                predicate="within"
            ).drop(columns="index_right", errors="ignore")

    # ---------------- DISTRICT HQ (ADMINISTRATIVE) ----------------
    district_poly = layers["district"][["geometry"]].copy()
    district_poly["district"] = layers["district"][LAYERS["district"]["column"]]

    district_hq = gpd.sjoin(
        layers["district_hq"],
        district_poly,
        how="left",
        predicate="within"
    ).rename(
        columns={LAYERS["district_hq"]["column"]: "district_hq"}
    ).drop(columns="index_right", errors="ignore")

    district_hq_lookup = (
        district_hq[["district", "district_hq"]]
        .dropna()
        .drop_duplicates()
    )

    gdf["district_norm"] = normalize(gdf["district"])
    district_hq_lookup["district_norm"] = normalize(district_hq_lookup["district"])

    gdf = gdf.merge(
        district_hq_lookup[["district_norm", "district_hq"]],
        on="district_norm",
        how="left"
    ).drop(columns="district_norm")

    # ---------------- STATE CAPITAL ----------------
    state_caps = gpd.sjoin(
        layers["state_capital"],
        layers["state"],
        how="left",
        predicate="within"
    ).rename(
        columns={
            LAYERS["state"]["column"]: "state",
            LAYERS["state_capital"]["column"]: "state_capital"
        }
    )[["state", "state_capital"]]

    state_cap_lookup = (
        state_caps.dropna().drop_duplicates(subset="state")
    )

    gdf = gdf.merge(
        state_cap_lookup,
        on="state",
        how="left"
    )

    for s, cap in CAPITAL_OVERRIDE.items():
        mask = gdf["state"].eq(s) & gdf["state_capital"].isna()
        gdf.loc[mask, "state_capital"] = cap

    # ---------------- PINCODE ----------------
    gdf_pin = gpd.read_file(PINCODE_GEOJSON).to_crs(CRS_GEOGRAPHIC)

    gdf = gpd.sjoin(
        gdf,
        gdf_pin[[PINCODE_FIELD, "geometry"]],
        how="left",
        predicate="within"
    ).drop(columns="index_right", errors="ignore")

    # ---------------- DISPUTED ----------------
    disputed_mask = gdf["state"].str.contains(DISPUTED_KEYWORD, na=False)
    for col in [
        "state", "district", "subdistrict",
        "district_hq", "state_capital", PINCODE_FIELD
    ]:
        if col in gdf.columns:
            gdf.loc[disputed_mask, col] = "DISPUTED"

    # ---------------- OUTPUT ----------------
    gdf_out = gdf.drop(columns=["geometry", "__valid__"], errors="ignore")
    gdf_out.to_excel(OUTPUT_EXCEL, index=False)

    # ==================================================
    #     FINAL DATA QUALITY ANALYSIS (PRINT ONLY)
    # ==================================================
    print("\n" + "-" * 60)
    print("DATA QUALITY REPORT – MISSING VALUES")
    print("-" * 60)

    total_rows = len(gdf_out)

    for col in gdf_out.columns:
        missing = gdf_out[col].isna().sum()
        percent = (missing / total_rows * 100) if total_rows else 0
        print(f"{col:<20} : {missing:>6} ({percent:.2f}%)")

    print("-" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("-" * 60 + "\n")

# ================= RUN =================
if __name__ == "__main__":
    reverse_geocode()
