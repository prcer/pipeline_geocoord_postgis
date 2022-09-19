from sqlalchemy import create_engine, text
import logging as log

def connect(pg_url):
    try:
        return create_engine(pg_url)
    except Exception as e:
        log.error(f'Unable to create Postgres engine: {str(e)}')
        return None


def setup_table(pg_engine):
    try:
        with pg_engine.connect() as conn:
            with open('/opt/trips/utils/setup_table.sql') as sql_file:
                query = text(sql_file.read())
                conn.execute(query)
    except Exception as e:
        log.error(f'Unable to setup Postgres schema and table: {str(e)}')


def create_weekly_partition(pg_engine, schema, table, week_year):
    """
        Create weekly date partition based on week of the year (week_year), inclusively.
    """
    try:
        with pg_engine.connect() as conn:
            conn.execute(f"CREATE TABLE {schema}.{table}_{week_year} \
                    PARTITION OF {schema}.{table} \
                    FOR VALUES IN ('{week_year}');")
    except Exception as e:
        log.error(f'Unable to setup Postgres partition {week_year}: {str(e)}')


def insert_batch(pg_engine, schema, table, gdf, dtype):
    try:
        with pg_engine.connect() as conn:
            gdf.to_postgis(table, con=conn, schema=schema, if_exists='append', index=False, dtype=dtype)
        return True
    except Exception as e:
        log.error(f'Unable to insert into Postgres table {schema}.{table}: {str(e)}')
        return False


