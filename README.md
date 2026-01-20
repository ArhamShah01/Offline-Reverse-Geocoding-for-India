# Offline Reverse Geocoding for India  
## Administrative Boundaries, Headquarters & PIN Codes (Fully Offline)

This repository provides a **complete, production-grade, offline reverse geocoding pipeline for India**.  
Given **only latitude and longitude**, the system derives multiple administrative attributes using **official Government of India GIS datasets**, without relying on any external APIs.

---

## What This Project Does

For each `(latitude, longitude)` pair, the pipeline determines:

- State  
- District  
- Subdistrict / Taluk  
- State Headquarters (Capital)  
- District Headquarters  
- PIN Code  

All outputs are generated locally using spatial joins on authoritative boundary datasets.

---

## What This Project Does Not Do

- No Google Maps, Mapbox, or other APIs  
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

This dataset provides state boundaries, district boundaries, subdistrict boundaries, and HQ point locations.

---

### PIN Code Boundaries

Government of India Open Data Portal (data.gov.in)  
https://www.data.gov.in/resource/delivery-post-office-pincode-boundary  

This dataset provides polygon boundaries for Indian PIN codes.

---

## Folder Structure

offline-reverse-geocoding-india  
├── database.xlsx  
├── main.py  
├── README.md  
├── STATE_BOUNDARY.shp  
├── DISTRICT_BOUNDARY.shp  
├── SUBDISTRICT_BOUNDARY.shp  
├── STATE_HQ.shp  
├── DISTRICT_HQ.shp  
└── All_India_pincode_Boundary.geojson

---

## Input Format

database.xlsx must contain only:

`latitude` | `longitude`  

---

## Output Format

reverse_geocoded_database.xlsx contains:

`latitude | longitude | state | district | subdistrict | state_capital | district_hq | pincode` 

---

## Installation

Python 3.9 or higher is required.

Install dependencies:

`pip install geopandas shapely pyogrio rtree pandas openpyxl fiona`

---

## How to Run

`python main.py`

The script prints progress messages and generates the output Excel file.

---

## Spatial Logic Overview

Two different spatial operations are used:

Polygon containment is used for state, district, subdistrict, and pincode assignment.

Nearest-neighbor distance calculations are used for state and district headquarters.

---

## Why Two Coordinate Reference Systems Are Required

Geographic CRS (EPSG:4326) uses degrees and is ideal for storing latitude and longitude and for topological operations such as polygon containment.

Projected CRS (EPSG:3857) uses meters and is required for accurate distance-based nearest-neighbor calculations.

Distance calculations performed directly in EPSG:4326 are mathematically incorrect because degrees are not uniform distance units. Therefore, nearest-HQ joins are performed in a projected CRS and then reprojected back.

---

## Challenges and Design Considerations

Managing multiple coordinate systems is essential to ensure correctness.

Points lying exactly on administrative boundaries may not always produce deterministic results.

Government datasets may contain naming inconsistencies or minor geometric misalignments.

The pipeline prioritizes data correctness over forced matches.

---

## Performance Considerations

Spatial joins use R-tree spatial indexing.

The pipeline scales well for thousands of points. For very large datasets, chunked processing is recommended.

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

It is designed for correctness, reproducibility, and offline operation.
