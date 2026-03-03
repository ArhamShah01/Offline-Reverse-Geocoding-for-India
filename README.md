# Offline Reverse Geocoding for India

## Administrative Boundaries, Headquarters and PIN Codes (Fully Offline)

I built this project to create a fully offline reverse geocoding
pipeline for India using official Government of India GIS datasets.

The system runs entirely on local files. It does not use external APIs
or internet services. Every administrative attribute is derived through
spatial joins on authoritative boundary datasets.

------------------------------------------------------------------------

## Why This Project Exists

Most reverse geocoding tools fall into one of these categories:

-   Online APIs that require internet access and impose usage limits
-   Heavy self-hosted engines that require significant infrastructure
-   Lightweight libraries that stop at state or city level

I needed something:

-   India-specific
-   District and subdistrict aware
-   Fully offline
-   Transparent and reproducible

This project addresses that gap.

------------------------------------------------------------------------

## What This Project Does

For each latitude and longitude pair in `database.xlsx`, the pipeline
determines:

-   State
-   District
-   Subdistrict / Taluk
-   State Capital
-   District Headquarters
-   PIN Code

All assignments use strict polygon containment with EPSG:4326.

There is no distance-based approximation and no heuristic inference.
Every value originates directly from the underlying GIS datasets.

------------------------------------------------------------------------

## What This Project Intentionally Does Not Do

-   No Google Maps, Mapbox, OpenStreetMap, or other commercial APIs
-   No online geocoding services
-   No distance-based guessing
-   No inferred headquarters
-   No forced administrative attribution except explicitly defined
    shared capital overrides

If a value is not defined in the dataset, it remains blank or is marked
as DISPUTED.

------------------------------------------------------------------------

## Official Data Sources

### Administrative Boundaries and Headquarters

Survey of India -- Online Maps Portal\
https://onlinemaps.surveyofindia.gov.in/Digital_Product_Show.aspx

Product details:

-   Product Code: OVSF/1M/6
-   Format: Shapefile
-   Scale: 1:1 Million
-   Coverage: Entire India
-   Detail Level: State, District, Subdistrict boundaries with
    headquarters locations

### PIN Code Boundaries

Government of India Open Data Portal (data.gov.in)\
https://www.data.gov.in/resource/delivery-post-office-pincode-boundary

Provides polygon boundaries for Indian PIN codes.

These datasets must be downloaded separately and placed locally.

------------------------------------------------------------------------

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

All shapefile components (.shp, .shx, .dbf, .prj, .cpg) must be present
in the same directory.

------------------------------------------------------------------------

## Input Format

The file `database.xlsx` must contain:

`latitude | longitude`

Processing behavior:

-   Leading and trailing whitespace is removed
-   Text values are coerced to numeric
-   Coordinates outside valid geographic ranges are marked invalid
-   Invalid rows remain in the output but receive no spatial attributes

------------------------------------------------------------------------

## Spatial Logic Overview

Polygon containment using `within` is applied for:

-   State
-   District
-   Subdistrict
-   PIN Code

Points that fall exactly on administrative boundaries may return empty
values because `within` excludes boundary-touching geometries.

------------------------------------------------------------------------

## State Capital Assignment

State capital points are spatially linked to state polygons.

Manual overrides are applied only when spatial assignment is missing:

-   Haryana → Chandigarh
-   Punjab → Chandigarh

------------------------------------------------------------------------

## District Headquarters Assignment

District headquarters are assigned only when defined in the dataset.

HQ points are spatially linked to district polygons and merged strictly
by normalized district name.

If no headquarters is defined, the field remains empty.

No distance-based inference is used.

------------------------------------------------------------------------

## Disputed Region Handling

If a polygon's state attribute contains the word DISPUTED, the pipeline
explicitly sets:

-   state
-   district
-   subdistrict
-   district_hq
-   state_capital
-   pincode

to DISPUTED.

This prevents partial or misleading attribution.

------------------------------------------------------------------------

## Output

The file `reverse_geocoded_database.xlsx` contains:

latitude \| longitude \| state \| district \| subdistrict \|
state_capital \| district_hq \| Pincode

At completion, the pipeline prints:

-   Missing value count per column
-   Percentage of missing values

------------------------------------------------------------------------

## Known Limitations

-   Points on administrative boundaries may return null
-   No fallback for boundary-touching geometries
-   No deduplication after spatial joins
-   Performance depends on GeoPandas spatial index availability
-   Schema validation assumes correct column names

------------------------------------------------------------------------

## Intended Use Cases

-   GIS and remote sensing projects
-   Academic research
-   Government analytics workflows
-   Disaster management systems
-   Location intelligence pipelines

------------------------------------------------------------------------

## Licensing and Disclaimer

This repository contains code only.

All GIS datasets are subject to their respective licenses and terms of
use. Users are responsible for complying with Survey of India and
data.gov.in policies.

------------------------------------------------------------------------

## Final Note

This project demonstrates a fully offline, dataset-driven reverse
geocoding workflow for India.

It prioritizes administrative correctness, transparency, and
reproducibility.
