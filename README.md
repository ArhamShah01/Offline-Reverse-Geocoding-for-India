# Offline Reverse Geocoding for India
## Administrative Boundaries, Headquarters & PIN Codes (Fully Offline)

This repository provides a **complete, production-grade offline reverse geocoding pipeline for India**.
Given latitude and longitude coordinates, the system derives administrative attributes using official Government of India GIS datasets, **without relying on any external APIs or internet access**.

The project is designed for **correctness, transparency, and reproducibility**, making it suitable for academic work, government use, and restricted environments.

---

## What This Project Does

For each `(latitude, longitude)` pair, the pipeline determines:

- State  
- District  
- Subdistrict / Taluk  
- State Capital  
- District Headquarters (where administratively defined)  
- PIN Code  

All outputs are generated locally using spatial joins on authoritative boundary datasets.

---

## What This Project Does Not Do

- No Google Maps, Mapbox, OpenStreetMap, or other commercial APIs  
- No online geocoding services  
- No forced or guessed administrative values  

If an administrative attribute is not defined in the source data, it is intentionally left blank.

---

## Official Data Sources

### Administrative Boundaries and Headquarters

**Survey of India – Online Maps Portal**  
https://onlinemaps.surveyofindia.gov.in/Digital_Product_Show.aspx  

Product details:

- Product Code: OVSF/1M/6  
- Format: Shapefile  
- Scale: 1:1 Million  
- Coverage: Entire India  
- Detail Level: State, District, Subdistrict boundaries with headquarters locations  

---

### PIN Code Boundaries

**Government of India Open Data Portal (data.gov.in)**  
https://www.data.gov.in/resource/delivery-post-office-pincode-boundary  

Provides polygon boundaries for Indian PIN codes.

---

## Folder Structure

```
offline-reverse-geocoding-india/
├── database.xlsx
├── main.py
├── README.md
├── requirements.txt
├── STATE_BOUNDARY.*
├── DISTRICT_BOUNDARY.*
├── SUBDISTRICT_BOUNDARY.*
├── STATE_HQ.*
├── DISTRICT_HQ.*
└── All_India_pincode_Boundary.geojson
```

All shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`) must be present in the same directory.

---

## Input Format

`database.xlsx` must contain:

```
latitude | longitude
```

- Whitespace and text values are automatically cleaned
- Invalid coordinates are safely ignored

---

## Output Format

`reverse_geocoded_database.xlsx` contains:

```
latitude | longitude | state | district | subdistrict | state_capital | district_hq | pincode
```

---

## Spatial Logic Overview

### Polygon-Based Assignment

The following attributes are derived using **polygon containment (`within`)**:

- State  
- District  
- Subdistrict  
- PIN Code  

Polygon containment reflects true administrative ownership rather than proximity.

---

### State Capital Assignment

State capitals are assigned by spatially associating capital point locations with state polygons.
Certain states share a capital city (e.g., Chandigarh for Haryana and Punjab); these cases are handled explicitly to ensure correctness.

---

### District Headquarters Assignment

District headquarters are assigned **only when administratively defined**.

- District HQ points are spatially linked to district polygons
- A strict district-to-HQ relationship is applied
- No distance-based approximation is used

If a district does not have a defined headquarters in the source dataset, the `district_hq` field is left blank.

---

## Why Some District HQ Values Are Empty

Empty `district_hq` values are **expected and correct** in the following cases:

- **New or reorganized districts** that do not exist in the headquarters dataset  
- **Gramin / Rural districts**, where the HQ is recorded under the parent district name  
- **Delhi districts**, which do not have separate district headquarters in official administrative data  
- **Disputed or special administrative regions**  
- **Source data limitations or naming inconsistencies**

The pipeline intentionally avoids guessing or inferring headquarters where no authoritative definition exists.

---

## Coordinate Handling

- Latitude and longitude values are cleaned to remove whitespace
- Text values are safely converted to numeric form
- Invalid coordinates are excluded from spatial operations

This prevents silent errors caused by spreadsheet formatting issues.

---

## Coordinate Reference System (CRS)

All spatial operations are performed using **EPSG:4326 (Geographic CRS)**.
Distance-based calculations are intentionally avoided, as administrative boundaries are not defined by proximity.

---

## Shapefile Components and Their Roles

A shapefile consists of multiple files:

- `.shp` — geometry  
- `.dbf` — attribute data  
- `.shx` — spatial index  
- `.prj` — coordinate reference system  
- `.cpg` — character encoding  

All components must be present for correct operation.

---

## Data Quality and Transparency

At the end of execution, the pipeline prints a **data quality summary**, reporting:

- Number of missing values per output column
- Percentage of missing values relative to total rows

This provides transparency into data completeness without modifying results.

---

## Performance Considerations

- Spatial joins use R-tree indexing
- Efficient for thousands of input points
- For very large datasets, chunked processing is recommended

---

## Common Causes of Missing Output

- Points lying exactly on administrative boundaries  
- Newly created districts not present in HQ datasets  
- Administrative units without officially defined headquarters  
- Encoding artifacts in source files  

These reflect real-world data limitations rather than software errors.

---

## Licensing and Disclaimer

This repository contains **code only**.

All GIS datasets are subject to their respective licenses and terms of use.
Users are responsible for complying with Survey of India and data.gov.in policies.

---

## Intended Use Cases

- GIS and remote sensing projects  
- Census and demographic analysis  
- Disaster management and planning  
- Location intelligence pipelines  
- Academic theses and research  
- Government and PSU analytics  

---

## Final Notes

This project demonstrates a **fully offline, authoritative reverse geocoding workflow for India**.
It prioritizes correctness, transparency, and reproducibility over forced completeness.
