# Pipeline Trips Ingestion into Postgis with Geospatial Metrics API

# Functionality
- ...

# Instructions & Usage
- Just make sure you have docker and docker-compose installed in the local machine
- Navigate to root folder and run: `docker-compose up`
- To ingest data, just drop a CSV file with the same format as the sample provide into the folder ingestion/data_input
  - File will start ingestion and will be renamed with a _PROCESSING_ suffix.
  - Once ingestion is done, file will be moved to ingestion/data_output folder (with the same original name)
  - File process can also be monitored in details via logs from the ingestion container at: `/var/log/ingestion.log`
- API will be available at `http://localhost:5000`. From local machine or inside the api container, functionality can be tested with script: `api/code/test/test_api.py`. Sample output:
```
Endpoint: http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28
Status code: 400
Reason: BAD REQUEST
None
Endpoint: http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28&region=Hamburg
Status code: 200
Reason: OK
{
    "weekly_avg_trips_by_box": {},
    "weekly_avg_trips_by_region": {
        "avg_trips_area": "12.00",
        "compute_time_ms": 21.055,
        "region": "Hamburg",
        "total_trips_area": "60",
        "week_year": "22_2018"
    }
}
Endpoint: http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28&box=(-100 -100,-100 100,100 100,100 -100,-100 -100)
Status code: 200
Reason: OK
{
    "weekly_avg_trips_by_box": {
        "avg_trips_area": "12.00",
        "box_coords": "(-100 -100,-100 100,100 100,100 -100,-100 -100)",
        "compute_time_ms": 35.48,
        "total_trips_area": "144",
        "week_year": "22_2018"
    },
    "weekly_avg_trips_by_region": {}
}
Endpoint: http://localhost:5000/v1/weekly_avg_trips?date=2018-05-01&region=Turin&box=(-100 -100,-100 100,100 100,100 -100,-100 -100)
Status code: 200
Reason: OK
{
    "weekly_avg_trips_by_box": {
        "avg_trips_area": "12.55",
        "box_coords": "(-100 -100,-100 100,100 100,100 -100,-100 -100)",
        "compute_time_ms": 51.101,
        "total_trips_area": "276",
        "week_year": "18_2018"
    },
    "weekly_avg_trips_by_region": {
        "avg_trips_area": "13.71",
        "compute_time_ms": 51.101,
        "region": "Turin",
        "total_trips_area": "96",
        "week_year": "18_2018"
    }
}
```
- Ingested data can be verified in postgres container:
```
psql -U postgres_user trips_db
\d+ trips_data.trips;
SELECT * FROM trips_data.trips;
SELECT st_asgeojson(trunc_origin_coord) FROM trips_data.trips;
```
- To terminate application, run: `docker-compose down`

# Scalability
- ...

# Changes to host application in AWS
- ...

