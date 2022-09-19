CREATE SCHEMA IF NOT EXISTS trips_data AUTHORIZATION postgres_user;

-- trunc_origin_coord, trunc_destination_coord, trip_hour and week_year simplify query processing at the cost of using more space.
CREATE TABLE IF NOT EXISTS trips_data.trips(
    region VARCHAR,
    origin_coord GEOMETRY(POINT, 4326),
    destination_coord GEOMETRY(POINT, 4326),
    trip_datetime TIMESTAMP,
    datasource VARCHAR,
    trunc_origin_coord GEOMETRY(POINT, 4326),
    trunc_destination_coord GEOMETRY(POINT, 4326),
    trip_hour INT,
    week_year VARCHAR 
) PARTITION BY LIST (week_year);

CREATE INDEX IF NOT EXISTS week_year_idx ON trips_data.trips (week_year);
CREATE INDEX IF NOT EXISTS region_idx ON trips_data.trips (region);