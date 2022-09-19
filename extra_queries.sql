-- From the two most commonly appearing regions, which is the latest datasource?
WITH most_common_regions AS (
    SELECT region,
           COUNT(*) AS trips_count,
           MAX(trip_datetime) AS latest_trip_date
    FROM trips_data.trips
    GROUP BY region
    ORDER BY trips_count DESC
    LIMIT 2
) 
SELECT most_common_regions.region, 
       MAX(datasource) AS datasource
FROM most_common_regions, trips_data.trips AS trips
WHERE most_common_regions.region = trips.region
    AND latest_trip_date = trips.trip_datetime
GROUP BY most_common_regions.region;
 

-- What regions has the "cheap_mobile" datasource appeared in?
SELECT DISTINCT(region)
FROM trips_data.trips
WHERE datasource = 'cheap_mobile';