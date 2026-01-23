# Offline Reverse Geocoding for India
## Administrative Boundaries, Headquarters & PIN Codes (Fully Offline)

> An offline, authoritative reverse geocoding system for India using official Government of India GIS datasets.

---

## Why This Project Exists

Most reverse geocoding solutions fall into one of the following categories:

- **Online APIs** (Google Maps, Mapbox, OpenCage, etc.)  
  → Require internet access, impose usage limits, and operate as black boxes.

- **Large self-hosted engines** (e.g., Nominatim, Pelias)  
  → Require heavy infrastructure, complex setup, and are not tailored for
    India-specific administrative requirements such as district headquarters.

- **Lightweight offline libraries**  
  → Typically limited to country/state/city lookups and unsuitable for
    district- or subdistrict-level analysis.

This project was built to address a **specific gap**:
a **fully offline, India-focused reverse geocoding pipeline** that produces
administratively correct results using **authoritative Government of India
datasets**, without heuristics or external services.

To the best of our knowledge, no existing open-source tool provides fully offline
reverse geocoding for India with reliable district-, subdistrict-, headquarters-,
and PIN code–level attribution.

---

This repository provides a **fully offline reverse geocoding pipeline for India**.
Given latitude and longitude coordinates, the system derives administrative attributes using official Government of India GIS datasets, **without using any external APIs or internet services**.

The project is designed for **correctness, transparency, and reproducibility**, and is suitable for academic work, government workflows, and restricted environments.

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

## What This Project Intentionally Does Not Do

- No Google Maps, Mapbox, OpenStreetMap, or other commercial APIs  
- No online geocoding services  
- No forced or guessed administrative values  

If an administrative attribute is not defined in the source data, it is intentionally left blank or explicitly marked as `DISPUTED`.

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
├── All_India_pincode_Boundary.geojson
└── database.xlsx
```

All shapefile components (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`) must be present in the same directory.

---

## Input Format

`database.xlsx` must contain:

```
latitude | longitude
```

- Leading and trailing whitespaces are handled automatically  
- Text values are safely coerced to numeric  
- Invalid coordinates are ignored  

---

## Output Format

`reverse_geocoded_database.xlsx` contains:

```
latitude | longitude | state | district | subdistrict | state_capital | district_hq | pincode
```

---

## Spatial Logic Overview

### Polygon-Based Administrative Assignment

The following attributes are derived using **polygon containment (`within`)**:

- State  
- District  
- Subdistrict  
- PIN Code  

Polygon containment reflects true administrative ownership rather than geographic proximity.

---

### State Capital Assignment

State capitals are assigned by spatially associating capital point locations with state polygons.
Certain states share a capital city (for example, Chandigarh for Haryana and Punjab); these cases are handled explicitly to ensure correctness.

---

### District Headquarters Assignment

District headquarters are assigned **only when administratively defined**:

- District HQ points are spatially linked to district polygons  
- A strict district-to-HQ relationship is applied  
- No distance-based approximation is used  

If a district does not have a defined headquarters in the source dataset, the `district_hq` field is left blank.

---

## Handling of Disputed Regions

Some administrative polygons in the Survey of India dataset are explicitly labeled as disputed, for example:

- `DISPUTED (MADHYA PRADESH & GUJARAT)`  
- `DISPUTED (MADHYA PRADESH & RAJASTHAN)`  
- `DISPUTED (RAJATHAN & GUJARAT)`  
- `DISPUTED (WEST BENGAL , BIHAR & JHARKHAND)`  

For any input point that falls inside such a polygon:

- All administrative columns (`state`, `district`, `subdistrict`, `district_hq`, `state_capital`, `pincode`) are explicitly set to `DISPUTED`  
- This avoids partial or misleading attribution  

The project includes a dedicated validation file, `disputed_test_points.xlsx`, containing coordinates guaranteed to lie inside each disputed polygon.
These points are also merged into `sample_latlongs_merged_with_disputed.xlsx` for end-to-end testing.

---

## Why Some District HQ Values Are Empty

Empty `district_hq` values are **expected and correct** in several cases:

- **New or reorganized districts** not present in the headquarters dataset  
- **Gramin / Rural districts**, where HQs are recorded under the parent district name  
- **Delhi districts**, which do not have separate district headquarters in official administrative data  
- **Disputed regions**, which are explicitly marked as `DISPUTED`  

The pipeline intentionally avoids guessing or inferring headquarters where no authoritative definition exists.

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

At the end of execution, the pipeline prints a **data quality summary** showing:

- Number of missing values per output column  
- Percentage of missing values relative to total rows  

This provides transparency into data completeness without modifying results.

---

## Performance Considerations

- Spatial joins use R-tree indexing  
- Suitable for thousands of points  
- For very large datasets, chunked processing is recommended  

---

## Common Causes of Missing Output

- Points lying exactly on administrative boundaries  
- Newly created districts not present in HQ datasets  
- Administrative units without officially defined headquarters  
- Encoding artifacts in source data  

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
It prioritizes administrative correctness, transparency, and reproducibility over forced completeness.
