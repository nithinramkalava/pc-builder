import os
import pandas as pd
import json
import ollama
from data_connection import connect_to_db, get_sqlalchemy_engine, load_table_data

def get_table_schema(engine, table_name):
    """Get the schema information for a table"""
    query = f"""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = '{table_name}'
    """
    return pd.read_sql_query(query, engine)

def analyze_feature_with_gemma(feature_name, data_type, sample_values, table_name):
    """Use Gemma 3:12b to analyze a feature and provide a description"""
    prompt = f"""
    Analyze this database feature from a computer components database:
    Table: {table_name}
    Feature name: {feature_name}
    Data type: {data_type}
    Sample values: {sample_values}
    
    Provide a 2-3 sentence description of what this feature represents and how it could be used in a PC component recommendation system. Be concise and technical.
    """
    
    # Use ollama Python library
    try:
        response = ollama.chat(
            model='gemma3:12b',
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error calling Gemma: {e}")
        return f"Error analyzing feature {feature_name}: {e}"

def main():
    # List of tables to process from data_connection.py
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
    
    # Define output file path in the recommendation folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "data_desc.txt")
    
    # Connect to database
    try:
        conn = connect_to_db()
        print("Successfully connected to the PostgreSQL database")
        
        # Create SQLAlchemy engine
        engine = get_sqlalchemy_engine()
        
        with open(output_file, 'w') as f:
            f.write("# PC BUILDER DATABASE FEATURE ANALYSIS\n\n")
            f.write("This document contains descriptions of database features and how they can be used in a PC recommendation system.\n\n")
            
            # Process each table
            for table in tables:
                print(f"\nAnalyzing {table}...")
                f.write(f"\n## {table.upper()}\n\n")
                
                try:
                    # Get table data
                    df = load_table_data(table, engine)
                    print(f"Found {len(df)} records in {table}")
                    
                    # Get schema information
                    schema = get_table_schema(engine, table)
                    
                    # Analyze each feature
                    for _, row in schema.iterrows():
                        column_name = row['column_name']
                        data_type = row['data_type']
                        
                        # Get sample values (up to 5)
                        if column_name in df.columns:
                            sample_values = df[column_name].dropna().head(5).tolist()
                        else:
                            sample_values = ["No data available"]
                        
                        print(f"  Analyzing feature: {column_name}")
                        
                        # Get description from Gemma
                        description = analyze_feature_with_gemma(
                            column_name, 
                            data_type, 
                            sample_values, 
                            table
                        )
                        
                        # Write to file
                        f.write(f"### {column_name}\n")
                        f.write(f"**Data Type:** {data_type}\n\n")
                        f.write(f"**Description:** {description}\n\n")
                        f.write(f"**Sample Values:** {sample_values}\n\n")
                        
                except Exception as e:
                    error_msg = f"Error processing {table}: {e}"
                    print(error_msg)
                    f.write(f"Error: {error_msg}\n\n")
            
            # Close connection
            conn.close()
            print(f"\nAnalysis complete. Results written to {output_file}")
            
    except Exception as e:
        print(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    main() 