# Offline Reverse Geocoding for India
## Administrative Boundaries, Headquarters & PIN Codes (Fully Offline)

This repository provides a complete, production-grade, offline reverse geocoding pipeline for India.
Given only latitude and longitude, the system derives multiple administrative attributes using official Government of India GIS datasets, without relying on any external APIs.

---

## What This Project Does

For each (latitude, longitude) pair, the pipeline determines:

- State
- District
- Subdistrict / Taluk
- State Headquarters (Capital)
- District Headquarters
- PIN Code

All outputs are generated locally using spatial joins on authoritative boundary datasets.

---

## What This Project Does Not Do

- No Google Maps, Mapbox, or other commercial APIs
- No internet access required after data download

This makes the project suitable for academic submissions, government workflows, restricted environments, and reproducible research.

---

## Official Data Sources

### Administrative Boundaries and Headquarters

Survey of India – Online Maps Portal  
https://onlinemaps.surveyofindia.gov.in/Digital_Product_Show.aspx

Product details:

Product Code: OVSF/1M/6  
Price: ₹0  
Format: Shapefile  
Scale: 1:1 Million  
Coverage: Entire India  
Detail Level: Up to Taluk level with State and District HQ  

This dataset provides state boundaries, district boundaries, subdistrict (taluk) boundaries, and headquarters point locations.

---

### PIN Code Boundaries

Government of India Open Data Portal (data.gov.in)  
https://www.data.gov.in/resource/delivery-post-office-pincode-boundary

This dataset provides polygon boundaries for Indian PIN codes.

---

## Folder Structure

```
offline-reverse-geocoding-india/
├── database.xlsx
├── main.py
├── README.md
├── requirements.txt
├── STATE_BOUNDARY.shp
├── STATE_BOUNDARY.shx
├── STATE_BOUNDARY.dbf
├── STATE_BOUNDARY.prj
├── STATE_BOUNDARY.cpg
├── DISTRICT_BOUNDARY.shp
├── DISTRICT_BOUNDARY.shx
├── DISTRICT_BOUNDARY.dbf
├── DISTRICT_BOUNDARY.prj
├── DISTRICT_BOUNDARY.cpg
├── SUBDISTRICT_BOUNDARY.shp
├── SUBDISTRICT_BOUNDARY.shx
├── SUBDISTRICT_BOUNDARY.dbf
├── SUBDISTRICT_BOUNDARY.prj
├── SUBDISTRICT_BOUNDARY.cpg
├── STATE_HQ.shp
├── STATE_HQ.shx
├── STATE_HQ.dbf
├── STATE_HQ.prj
├── STATE_HQ.cpg
├── DISTRICT_HQ.shp
├── DISTRICT_HQ.shx
├── DISTRICT_HQ.dbf
├── DISTRICT_HQ.prj
├── DISTRICT_HQ.cpg
└── All_India_pincode_Boundary.geojson
```

All shapefile components must reside in the same directory and share the same base filename.

---

## Input Format

`database.xlsx` must contain only:

`latitude | longitude`

---

## Output Format

reverse_geocoded_database.xlsx contains:

`latitude | longitude | state | district | subdistrict | state_capital | district_hq | pincode`

---

## Installation

Python 3.9 or higher is required.

Install dependencies:

```pip install geopandas shapely pyogrio rtree pandas openpyxl fiona```

---

## How to Run

```python main.py```

The script prints structured progress messages and generates the output Excel file.

---

## Spatial Logic Overview

Two types of spatial operations are used:

Polygon containment (within) is used for state, district, subdistrict, and pincode assignment.

Nearest-neighbor distance calculations (sjoin_nearest) are used for state and district headquarters.

---

## Why Two Coordinate Reference Systems Are Required

This pipeline deliberately uses two different Coordinate Reference Systems (CRS).

Geographic CRS (EPSG:4326) uses degrees and is suitable for storing latitude and longitude and for topological operations such as polygon containment.

Projected CRS (EPSG:3857) uses meters and is required for accurate distance-based nearest-neighbor calculations.

Distance calculations performed directly in EPSG:4326 are mathematically incorrect because degrees are not uniform units of distance.
Therefore, nearest-HQ joins are performed in a projected CRS and results are re-projected back to EPSG:4326.

---

## Shapefile Components and Their Roles

A shapefile is a multi-file dataset. Although only the .shp file is referenced in code, multiple files work together.

`.shp` stores geometry  
`.dbf` stores attribute data  
`.shx` provides geometry indexing  
`.prj` defines the coordinate reference system  

`.cpg` specifies the character encoding of the .dbf file.
It does not affect geometry or spatial joins and is only required when non-ASCII text is present.
It is commonly included as a best practice to ensure consistent text interpretation across platforms.

---

## Challenges and Design Considerations

Managing multiple coordinate systems is essential for correctness.

Points lying exactly on administrative boundaries may not always produce deterministic results.

Government datasets may contain naming inconsistencies or minor geometric misalignments.

The pipeline prioritizes data correctness over forced matches.

---

## Performance Considerations

Spatial joins use R-tree spatial indexing.

The pipeline scales well for thousands of points.
For very large datasets, chunked processing is recommended.

---

## Common Mistakes and Errors

- Columns not named `latitude` and `longitude`, i.e. they may be `LAT`, `LONG` or something similar.
  this should be changed.

- The latitudes and longitudes must not contain whitespaces in them, they must be purely numeric.

- Shapefile components not kept together
All shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`) must be present in the same directory and share the same base filename.  
Missing or renamed components can cause layers to fail loading or produce incorrect results.

- Missing or incorrect CRS information
If the `.prj` file is missing or incorrect, spatial joins may silently return wrong results.  
Always ensure the CRS is correctly defined before performing joins.

- Performing nearest-neighbor joins in geographic CRS
Using `sjoin_nearest` directly in EPSG:4326 (latitude/longitude) leads to incorrect distance calculations.  
Nearest-neighbor operations must be performed in a projected CRS (e.g., EPSG:3857).

- Points lying exactly on administrative boundaries
Coordinates that fall exactly on polygon boundaries may return null or ambiguous results due to geometric precision limitations.

---

## Licensing and Disclaimer

This repository contains code only.

Government datasets are subject to their respective licenses and usage terms.

Users are responsible for complying with Survey of India and data.gov.in policies.

---

## Intended Use Cases

GIS and remote sensing projects  
Disaster management and planning  
Census and demographic analysis  
Location intelligence pipelines  
Academic theses and research  
Government and PSU analytics

---

## Final Notes

This project demonstrates a professional, API-free reverse geocoding workflow using official Indian government data.
It is designed for correctness, transparency, and offline operation.
