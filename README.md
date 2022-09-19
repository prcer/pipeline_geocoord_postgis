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


```http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28
400
BAD REQUEST


http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28&region=Hamburg

200
{'weekly_avg_trips_by_box': {}, 'weekly_avg_trips_by_region': {'avg_trips_area': '8.00', 'compute_time_ms': 21.266, 'region': 'Hamburg', 'total_trips_area': '40', 'week_year': '22_2018'}}


http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28&box=(-100 -100,-100 100,100 100,100 -100,-100 -100)

200
{'weekly_avg_trips_by_box': {'avg_trips_area': '8.00', 'box_coords': '(-100 -100,-100 100,100 100,100 -100,-100 -100)', 'compute_time_ms': 19.742, 'total_trips_area': '96', 'week_year': '22_2018'}, 'weekly_avg_trips_by_region': {}}


http://localhost:5000/v1/weekly_avg_trips?date=2018-05-28&region=Hamburg&box=(-100 -100,-100 100,100 100,100 -100,-100 -100)

200
{'weekly_avg_trips_by_box': {'avg_trips_area': '8.00', 'box_coords': '(-100 -100,-100 100,100 100,100 -100,-100 -100)', 'compute_time_ms': 38.007, 'total_trips_area': '96', 'week_year': '22_2018'}, 'weekly_avg_trips_by_region': {'avg_trips_area': '8.00', 'compute_time_ms': 38.007, 'region': 'Hamburg', 'total_trips_area': '40', 'week_year': '22_2018'}}```

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

