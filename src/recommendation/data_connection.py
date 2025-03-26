# connect to the postgres databse and load the data in pandas dataframe, and print first 5 rows of the dataframe for each table
# db - pc_builder_prod, user - pc_builder_admin, password - pc_builder
# tables: cpu_specs, gpu_specs, memory_specs, ssd_specs, motherboard_specs, psu_specs, cooler_specs, case_specs

import psycopg2
import pandas as pd
from sqlalchemy import create_engine

def connect_to_db():
    """Connect to PostgreSQL database and return connection"""
    conn = psycopg2.connect(
        dbname="pc_builder_prod",
        user="pc_builder_admin",
        password="pc_builder",
        host="localhost",  
        port="5432"        
    )
    return conn

def get_sqlalchemy_engine():
    """Create SQLAlchemy engine for pandas operations"""
    connection_string = "postgresql://pc_builder_admin:pc_builder@localhost:5432/pc_builder_prod"
    return create_engine(connection_string)

def load_table_data(table_name, engine):
    """Load data from table into pandas DataFrame"""
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)
    return df

def main():
    # List of tables to process
    tables = [
        "cpu_specs",
        "gpu_specs",
        "memory_specs",
        "ssd_specs", 
        "motherboard_specs",
        "psu_specs",
        "cooler_specs",
        "case_specs"
    ]
    
    # Connect to database
    try:
        conn = connect_to_db()
        print("Successfully connected to the PostgreSQL database")
        
        # Create SQLAlchemy engine
        engine = get_sqlalchemy_engine()
        
        # Load data from each table and print first 5 rows
        for table in tables:
            print(f"\n--- {table} ---")
            try:
                df = load_table_data(table, engine)
                print(f"Found {len(df)} records in {table}")
                print(df.head(5))
            except Exception as e:
                print(f"Error loading data from {table}: {e}")
                
        # Close connection
        conn.close()
        print("\nDatabase connection closed")
        
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    main()
