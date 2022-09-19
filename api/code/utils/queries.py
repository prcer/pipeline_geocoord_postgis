QUERIES = {
    "WEEKLY_AVG_BY_REGION": "WITH area_trips_count AS ( \
                                SELECT COUNT(*) AS trips_count \
                                FROM trips_data.trips \
                                WHERE week_year = :week_year AND region = :region \
                                GROUP BY trip_hour, trunc_origin_coord, trunc_destination_coord \
                             ) \
                             SELECT ROUND(AVG(trips_count), 2) AS weekly_avg, \
                                SUM(trips_count) AS count_trips \
                             FROM area_trips_count",
    "WEEKLY_AVG_BY_BOX": "WITH area_trips_count AS ( \
                            SELECT COUNT(*) AS trips_count \
                            FROM trips_data.trips \
                            WHERE week_year = :week_year \
                                AND ST_Contains(ST_GeomFromText(:box, 4326), \
                                        ST_Collect(trunc_origin_coord, trunc_destination_coord)) \
                            GROUP BY trip_hour, trunc_origin_coord, trunc_destination_coord \
                            ) \
                            SELECT ROUND(AVG(trips_count), 2) AS weekly_avg, \
                                SUM(trips_count) AS count_trips \
                            FROM area_trips_count"
}