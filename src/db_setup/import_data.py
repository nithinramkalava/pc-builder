import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, List
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

class PCPartsDBImporter:
    def __init__(self, db_params: Dict[str, str]):
        self.db_params = db_params
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cursor = self.conn.cursor()
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def clean_dataframe(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Clean and prepare DataFrame for import"""
        # Select only the required columns
        df = df[columns].copy()
        
        # Remove duplicates based on 'name' column
        df = df.drop_duplicates(subset=['name'], keep='first')
        
        # Replace NaN values with None for SQL compatibility
        df = df.where(pd.notnull(df), None)
        
        return df

    def import_csv_to_table(self, csv_path: Path, table_name: str, columns: List[str]):
        try:
            logger.info(f"Reading CSV file: {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Clean and prepare data
            df = self.clean_dataframe(df, columns)
            logger.info(f"Found {len(df)} unique entries after cleaning")
            
            # Clear existing data from the table
            self.cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            self.conn.commit()
            
            # Convert DataFrame to list of tuples
            data = [tuple(row) for row in df.values]
            
            # Create the INSERT query
            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(columns)}) 
                VALUES %s
            """
            
            # Execute the insert
            execute_values(self.cursor, insert_query, data)
            self.conn.commit()
            
            logger.info(f"Successfully imported {len(data)} rows into {table_name}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error importing data to {table_name}: {e}")
            raise

    def process_all_files(self):
        file_mappings = {
            'cpu.csv': ('cpu', ['name', 'price', 'core_count', 'core_clock', 'boost_clock', 'tdp', 'graphics', 'smt']),
            'motherboard.csv': ('motherboard', ['name', 'price', 'socket', 'form_factor', 'max_memory', 'memory_slots', 'color']),
            'memory.csv': ('memory', ['name', 'price', 'speed', 'modules', 'price_per_gb', 'color', 'first_word_latency', 'cas_latency']),
            'internal-hard-drive.csv': ('storage', ['name', 'price', 'capacity', 'price_per_gb', 'type', 'cache', 'form_factor', 'interface']),
            'video-card.csv': ('video_card', ['name', 'price', 'chipset', 'memory', 'core_clock', 'boost_clock', 'color', 'length']),
            'case.csv': ('case_enclosure', ['name', 'price', 'type', 'color', 'psu', 'side_panel', 'external_volume', 'internal_35_bays']),
            'power-supply.csv': ('power_supply', ['name', 'price', 'type', 'efficiency', 'wattage', 'modular', 'color']),
            'cpu-cooler.csv': ('cpu_cooler', ['name', 'price', 'rpm', 'noise_level', 'color', 'size'])
        }

        for csv_file, (table_name, columns) in file_mappings.items():
            try:
                csv_path = DATA_DIR / csv_file
                if not csv_path.exists():
                    logger.warning(f"CSV file not found: {csv_path}")
                    continue
                    
                logger.info(f"Processing {csv_file}...")
                self.import_csv_to_table(csv_path, table_name, columns)
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
                continue  # Continue with next file even if current one fails

def main():
    # Database connection parameters
    db_params = {
        'dbname': 'pc_builder',
        'user': 'pc_builder_admin',
        'password': 'pc_builder',  # Replace with your actual password
        'host': 'localhost',
        'port': '5432'
    }

    importer = PCPartsDBImporter(db_params)
    
    try:
        importer.connect()
        importer.process_all_files()
    except Exception as e:
        logger.error(f"Import process failed: {e}")
    finally:
        importer.close()

if __name__ == "__main__":
    main()