import time
import logging as log
import os
import pandas as pd
import shutil
from utils.db_utils import connect, insert_batch, setup_table,  create_weekly_partition
import geopandas as gpd
from shapely import wkt
from geoalchemy2 import Geometry

log.basicConfig(filename = "/var/log/ingestion.log",
                filemode = "w",
                format='%(asctime)s - %(levelname)s: %(message)s',
                level = log.DEBUG)

CHUNK_SIZE = int(os.environ['CHUNK_SIZE'])
PROCESSING_FILE_SUFFIX = '_PROCESSING_'


class FileProcessor:
    def __init__(self):
        log.info('Starting constructor setup')

        # Create data folders if they do not exist
        self.input_dir = 'data_input'
        self.output_dir = 'data_output'
        self.create_dir(self.input_dir)
        self.create_dir(self.output_dir)

        # Maintain engine to create postgres connections
        self.pg_engine = connect(os.environ['POSTGRES_DB_URL'])
        setup_table(self.pg_engine)
        self.schema = os.environ['POSTGRES_SCHEMA']
        self.table = os.environ['POSTGRES_TABLE']

        # Keep track of weekly partitions already created to save on unnecessary calls to create table
        self.created_parts = set()

        self.db_column_names = ['region', 'origin_coord', 'destination_coord', 'trip_datetime', 'datasource', 
                                'trunc_origin_coord', 'trunc_destination_coord', 'trip_hour', 'week_year']
        
        self.db_dtype_conv = {'origin_coord': Geometry('POINT', srid=4326),
            'destination_coord': Geometry('POINT', srid=4326),
            'trunc_origin_coord': Geometry('POINT', srid=4326),
            'trunc_destination_coord': Geometry('POINT', srid=4326)
        }

        log.info('Finished constructor setup')
    

    def monitor_loop(self):
        """
            Only handling CSV files for now that are located inside the data_input dir.
            Process 1 file at a time for simplicity.
            This could be enhanced to prioritize oldest file.
        """

        while True:
            file_names = os.listdir(self.input_dir)
            if file_names:
                self.process_file(file_names[0])
            else:
                time.sleep(1)
        self.pg_engine.dispose()


    def process_file(self, file_name):
        orig_file_path = os.path.join(self.input_dir, file_name)
        file_path = os.path.join(self.input_dir, file_name + PROCESSING_FILE_SUFFIX)

        # Rename file and add a suffix, so that user knows file is being processed.
        os.rename(orig_file_path, file_path)

        log.info(f'Processing file {file_name}')
        chunk_num = 1
        num_proc_rows = 0
        # File could potentially be big, thus processing it in chunks
        for df_chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
            num_rows = len(df_chunk)
            log.info(f'Processing chunk #{chunk_num} of {num_rows} rows from {file_name}')
            df_trans = self.transform_df(df_chunk)
            self.store_df(df_trans)
            num_proc_rows += num_rows
            log.info(f'Processed chunk #{chunk_num} from {file_name} - Total file rows processed so far: {num_proc_rows}')
            chunk_num += 1

        # Once file is completely processed, move it to output dir with its original name 
        # (avoid creating files with the same name, since they will be overwritten in data_output dir)
        shutil.move(file_path, os.path.join(self.output_dir, file_name))
        log.info(f'Fully processed file {file_name}')


    def transform_df(self, df):
        # Handle date columns 
        df['datetime'] =  pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
        df = df.rename(columns={'datetime': 'trip_datetime'})
        # Create new column for the hour of trip
        df['trip_hour'] = df['trip_datetime'].dt.hour
        # Create partition by week number and year
        df['week_year'] = df['trip_datetime'].dt.strftime('%W_%Y')

        # Handle point coordinates. Create new columns for the truncate coordinates (i.e. no decimal points)
        df['destination_coord'] = df['destination_coord'].apply(wkt.loads)
        df['trunc_destination_coord'] = df['destination_coord'].apply(wkt.dumps, rounding_precision=0)
        df['origin_coord'] = df['origin_coord'].apply(wkt.loads)
        df['trunc_origin_coord'] = df['origin_coord'].apply(wkt.dumps, rounding_precision=0)

        df = df.reindex(columns=self.db_column_names)
        #gdf = gpd.GeoDataFrame(df)
        gdf = gpd.GeoDataFrame(df, geometry='origin_coord')
        gdf.set_crs(epsg=4326, inplace=True)
        return gdf


    def store_df(self, gdf):
        # Create weekly partitions
        parts_to_create = set(gdf['week_year'].unique()) - self.created_parts
        for part in parts_to_create:
            create_weekly_partition(self.pg_engine, self.schema, self.table, part)
            self.created_parts.add(part)
        # Store entire batch / file chunk in Postgres
        insert_batch(self.pg_engine, self.schema, self.table, gdf, self.db_dtype_conv)


    def create_dir(self, dir_name):
        try:
            os.makedirs(dir_name)
        except OSError:
            pass


if __name__ == '__main__':
    log.info(f'Waiting for postgres to be available')
    # Add a 30s delay on startup just to be completely sure postgres container is up and running.
    time.sleep(30)

    file_proc = FileProcessor()
    file_proc.monitor_loop()
        
            
                 

    