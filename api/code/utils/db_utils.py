from sqlalchemy import create_engine
from sqlalchemy.sql import text
import logging as log
import os

POSTGRES_DB_URL = os.environ['POSTGRES_DB_URL']
SCHEMA = os.environ['POSTGRES_SCHEMA']
TABLE = os.environ['POSTGRES_TABLE']

def connect(pg_url):
    try:
        return create_engine(pg_url)
    except Exception as e:
        log.error(f'Unable to create Postgres engine: {str(e)}')
        return None

def run_query(query, params):
    """
        Run generic, ready to execute query with params and single result tuple.
        Returns: results: tuples
                 status: True if query ran successfully (results might be None even if that happens) and False otherwise
    """
    try:
        pg_engine = connect(POSTGRES_DB_URL)
        with pg_engine.connect() as conn:
            results = conn.execute(text(query), params).fetchone()
        log.info(f'Query results: {results}')
        return results, True
    except Exception as e:
        log.error(f'Unable to run query: {str(e)}')
        return None, False
    finally:
        pg_engine.dispose()


