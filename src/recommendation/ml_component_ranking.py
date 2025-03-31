import os
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import joblib

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'pc_builder_prod', 
    'user': 'pc_builder_admin',      
    'password': 'pc_builder'          
}

# Directory to save ML models
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ========== DATA PREPROCESSING FUNCTIONS ==========

def clean_numeric_value(value):
    """Clean and convert string values to numeric"""
    if value in [None, 'NULL', 'NaN']:
        return np.nan
    
    if isinstance(value, (int, float)):
        return value
        
    # Remove suffixes like 'GHz', 'MB', etc.
    for suffix in ['GHz', 'MHz', 'GB', 'MB', 'TB', 'W', 'mm', 'ns']:
        if isinstance(value, str) and suffix in value:
            return float(value.replace(suffix, '').strip())
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan

def extract_boolean_feature(value):
    """Extract boolean value from various formats"""
    if value in [None, 'NULL', 'NaN']:
        return np.nan
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, str) and value.lower() in ['yes', 'true', 'y']:
        return 1.0
    return 0.0

def extract_categorical_value(value, mapping=None):
    """Convert categorical values to numeric using provided mapping"""
    if value in [None, 'NULL', 'NaN']:
        return np.nan
    
    if mapping and value in mapping:
        return mapping[value]
    
    return value

# ========== COMPONENT DATA PREPARATION ==========

def prepare_cpu_data(cpu_data):
    """Prepare CPU data for ML model"""
    features = pd.DataFrame(cpu_data)
    
    # Extract numeric features
    numeric_cols = ['core_count', 'thread_count', 'l3_cache', 'price_num', 'tdp']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Extract clock speeds
    if 'performance_core_clock' in features.columns:
        features['core_clock'] = features['performance_core_clock'].apply(clean_numeric_value)
    
    if 'performance_core_boost_clock' in features.columns:
        features['boost_clock'] = features['performance_core_boost_clock'].apply(clean_numeric_value)
    
    # Extract architecture generation (e.g., 13th gen, 7000 series)
    if 'name' in features.columns:
        # Extract generation from name (Intel Core i7-13700K -> 13, AMD Ryzen 7 7700X -> 7)
        features['generation'] = features['name'].apply(lambda x: 
            int(x.split('-')[1][:2]) if '-' in str(x) and x.split('-')[1][:2].isdigit() 
            else int(str(x).split(' ')[-1][0]) if str(x).split(' ')[-1][0].isdigit() 
            else np.nan)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_gpu_data(gpu_data):
    """Prepare GPU data for ML model"""
    features = pd.DataFrame(gpu_data)
    
    # Extract numeric features
    numeric_cols = ['memory', 'price_num', 'length']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Extract clock speeds
    if 'core_clock' in features.columns:
        features['core_clock'] = features['core_clock'].apply(clean_numeric_value)
    
    if 'boost_clock' in features.columns:
        features['boost_clock'] = features['boost_clock'].apply(clean_numeric_value)
    
    # Extract memory bus width
    if 'memory_interface' in features.columns:
        features['memory_bus'] = features['memory_interface'].apply(
            lambda x: clean_numeric_value(x.split('-bit')[0]) if isinstance(x, str) and '-bit' in x else np.nan)
    
    # Extract generation based on chipset
    if 'chipset' in features.columns:
        # Use regex to extract generation number (RTX 4090, RX 7900 XT)
        features['generation'] = features['chipset'].apply(
            lambda x: int(str(x)[3]) if isinstance(x, str) and len(str(x)) > 3 and str(x)[3].isdigit() else np.nan)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_motherboard_data(mobo_data):
    """Prepare motherboard data for ML model"""
    features = pd.DataFrame(mobo_data)
    
    # Extract numeric features
    numeric_cols = ['memory_slots', 'memory_max', 'price_num']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Form factor mapping
    form_factor_map = {'ATX': 3, 'Micro ATX': 2, 'Mini ITX': 1}
    if 'form_factor' in features.columns:
        features['form_factor_score'] = features['form_factor'].apply(
            lambda x: extract_categorical_value(x, form_factor_map))
    
    # Extract M.2 slot count
    if 'm2_slots' in features.columns:
        features['m2_count'] = features['m2_slots'].apply(
            lambda x: len(str(x).split('\n')) if x not in [None, 'NULL', 'NaN'] else 0)
    
    # Extract WiFi capability
    if 'wireless_networking' in features.columns:
        features['has_wifi'] = features['wireless_networking'].apply(
            lambda x: 1.0 if x not in [None, 'NULL', 'NaN'] and 'Wi-Fi' in str(x) else 0.0)
    
    # Chipset tier based on letter (Z > B > H)
    chipset_map = {'Z': 3, 'B': 2, 'H': 1, 'X': 3, 'A': 2}
    if 'chipset' in features.columns:
        features['chipset_tier'] = features['chipset'].apply(
            lambda x: next((chipset_map[c] for c in str(x) if c in chipset_map), 0) 
            if x not in [None, 'NULL', 'NaN'] else np.nan)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_memory_data(memory_data):
    """Prepare memory data for ML model"""
    features = pd.DataFrame(memory_data)
    
    # Extract numeric features
    numeric_cols = ['price_num', 'first_word_latency']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Extract speed
    if 'speed' in features.columns:
        features['speed_num'] = features['speed'].apply(
            lambda x: int(str(x).split('-')[1]) if isinstance(x, str) and '-' in str(x) 
            else int(str(x)) if isinstance(x, str) and str(x).isdigit() 
            else np.nan)
    
    # Extract capacity
    if 'modules' in features.columns:
        features['total_capacity'] = features['modules'].apply(
            lambda x: int(str(x).split('x')[0]) * int(str(x).split('x')[1].replace('GB', '').strip())
            if isinstance(x, str) and 'x' in str(x) and 'GB' in str(x)
            else np.nan)
    
    # Heat spreader
    if 'heat_spreader' in features.columns:
        features['has_heat_spreader'] = features['heat_spreader'].apply(extract_boolean_feature)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_cooler_data(cooler_data):
    """Prepare cooler data for ML model"""
    features = pd.DataFrame(cooler_data)
    
    # Extract numeric features
    numeric_cols = ['price_num']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Fan RPM
    if 'fan_rpm' in features.columns:
        features['fan_rpm_max'] = features['fan_rpm'].apply(
            lambda x: float(str(x).split()[0]) if x not in [None, 'NULL', 'NaN'] else np.nan)
    
    # Noise level
    if 'noise_level' in features.columns:
        features['noise_db'] = features['noise_level'].apply(
            lambda x: float(str(x).split('-')[0].strip()) if isinstance(x, str) and '-' in str(x)
            else float(str(x).split()[0]) if isinstance(x, str) 
            else np.nan)
    
    # Socket compatibility count
    if 'cpu_socket' in features.columns:
        features['socket_count'] = features['cpu_socket'].apply(
            lambda x: len(str(x).split('\n')) if x not in [None, 'NULL', 'NaN'] else 0)
    
    # Water cooling
    if 'water_cooled' in features.columns:
        features['is_water_cooled'] = features['water_cooled'].apply(extract_boolean_feature)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_case_data(case_data):
    """Prepare case data for ML model"""
    features = pd.DataFrame(case_data)
    
    # Extract numeric features
    numeric_cols = ['price_num']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Form factor support count
    if 'motherboard_form_factor' in features.columns:
        features['form_factor_count'] = features['motherboard_form_factor'].apply(
            lambda x: len(str(x).split('\n')) if x not in [None, 'NULL', 'NaN'] else 0)
    
    # Glass panel
    if 'side_panel' in features.columns:
        features['has_glass'] = features['side_panel'].apply(
            lambda x: 1.0 if x not in [None, 'NULL', 'NaN'] and 'Glass' in str(x) else 0.0)
    
    # PSU shroud
    if 'power_supply_shroud' in features.columns:
        features['has_psu_shroud'] = features['power_supply_shroud'].apply(extract_boolean_feature)
    
    # USB Type-C
    if 'front_panel_usb' in features.columns:
        features['has_usb_c'] = features['front_panel_usb'].apply(
            lambda x: 1.0 if x not in [None, 'NULL', 'NaN'] and 'Type-C' in str(x) else 0.0)
    
    # GPU clearance
    if 'maximum_video_card_length' in features.columns:
        features['gpu_clearance'] = features['maximum_video_card_length'].apply(
            lambda x: float(str(x).split()[0]) if x not in [None, 'NULL', 'NaN'] else np.nan)
    
    # Drive bays
    if 'drive_bays' in features.columns:
        features['drive_bay_count'] = features['drive_bays'].apply(
            lambda x: sum(int(bay.split('x')[0].strip()) for bay in str(x).split('\n') if 'x' in bay)
            if x not in [None, 'NULL', 'NaN']
            else 0)
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

def prepare_psu_data(psu_data):
    """Prepare PSU data for ML model"""
    features = pd.DataFrame(psu_data)
    
    # Extract numeric features
    numeric_cols = ['price_num']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].apply(clean_numeric_value)
    
    # Wattage
    if 'wattage' in features.columns:
        features['wattage_num'] = features['wattage'].apply(clean_numeric_value)
    
    # Efficiency rating
    efficiency_map = {'80+ Titanium': 5, '80+ Platinum': 4, '80+ Gold': 3, '80+ Silver': 2, '80+ Bronze': 1, '80+': 0}
    if 'efficiency_rating' in features.columns:
        features['efficiency_score'] = features['efficiency_rating'].apply(
            lambda x: next((score for rating, score in efficiency_map.items() if rating in str(x)), 0)
            if x not in [None, 'NULL', 'NaN']
            else np.nan)
    
    # Modularity
    modularity_map = {'Full': 2, 'Semi': 1, 'No': 0}
    if 'modular' in features.columns:
        features['modularity_score'] = features['modular'].apply(
            lambda x: extract_categorical_value(x, modularity_map))
    
    # Keep only numeric columns and ID
    numeric_features = features.select_dtypes(include=['number']).columns
    return features[['id'] + [col for col in numeric_features if col != 'id']]

# ========== ML MODEL TRAINING AND RANKING ==========

def train_model(features, target_name, component_type):
    """Train a machine learning model on the given features"""
    # Split features and target
    X = features.drop(['id', target_name], axis=1, errors='ignore')
    y = features[target_name] if target_name in features.columns else None
    
    # If we don't have a target variable (e.g. price), use unsupervised learning
    if y is None or len(y) == 0:
        # Create a synthetic score based on PCA or other dimensionality reduction
        # For simplicity, we'll use a weighted sum of normalized features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # Higher values are better (except price)
        weights = np.ones(X.shape[1])
        price_cols = [i for i, col in enumerate(X.columns) if 'price' in col.lower()]
        for i in price_cols:
            weights[i] = -1  # Lower price is better
        
        # Simple weighted sum as synthetic score
        synthetic_score = np.sum(X_scaled * weights, axis=1)
        y = synthetic_score
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create a pipeline with imputation and model
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('model', GradientBoostingRegressor(n_estimators=100, random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error for {component_type}: {mae:.4f}")
    
    # Save the model
    model_path = os.path.join(MODEL_DIR, f"{component_type}_model.joblib")
    joblib.dump(pipeline, model_path)
    
    # Store the column names used for training
    feature_names = X.columns.tolist()
    
    return pipeline, feature_names

def predict_and_rank(model, features, component_type, feature_names=None, target_name='price_num'):
    """Use the trained model to predict scores and calculate rankings"""
    # Get features without ID and target column (which wasn't used in training)
    X = features.drop(['id', target_name], axis=1, errors='ignore')
    
    # If feature_names is provided, select only those columns in the correct order
    if feature_names:
        # Make sure we only select columns that exist in X
        valid_features = [col for col in feature_names if col in X.columns]
        X = X[valid_features]
    
    # Predict scores
    scores = model.predict(X)
    
    # Create DataFrame with ID and score
    result = pd.DataFrame({
        'id': features['id'],
        'ml_score': scores
    })
    
    # Calculate rankings (higher score = better rank)
    result['rank'] = result['ml_score'].rank(ascending=False, method='dense').astype(int)
    
    return result

def ensure_rank_columns_exist(conn):
    """Make sure all component tables have an ml_score and rank column"""
    try:
        with conn.cursor() as cursor:
            # Add columns to each table if they don't exist
            tables = [
                'cpu_specs', 'motherboard_specs', 'cooler_specs',
                'gpu_specs', 'case_specs', 'psu_specs', 'memory_specs'
            ]
            
            for table in tables:
                # Check for ml_score column
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'ml_score'
                """)
                if not cursor.fetchone():
                    print(f"Adding ml_score column to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN ml_score FLOAT")
                
                # Check for rank column
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'rank'
                """)
                if not cursor.fetchone():
                    print(f"Adding rank column to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN rank INTEGER")
        
        conn.commit()
        print("ML score and rank columns added where needed")
    
    except Exception as e:
        print(f"Error ensuring columns exist: {e}")
        conn.rollback()

def update_component_ranks(conn):
    """Train ML models and update ranks for all components in the database"""
    try:
        # Create a cursor
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            print("Processing CPU data...")
            cursor.execute("SELECT * FROM cpu_specs")
            cpus = cursor.fetchall()
            cpu_features = prepare_cpu_data(cpus)
            cpu_model, cpu_features_list = train_model(cpu_features, 'price_num', 'cpu')
            cpu_ranks = predict_and_rank(cpu_model, cpu_features, 'cpu', cpu_features_list)
            
            print("Processing motherboard data...")
            cursor.execute("SELECT * FROM motherboard_specs")
            mobos = cursor.fetchall()
            mobo_features = prepare_motherboard_data(mobos)
            mobo_model, mobo_features_list = train_model(mobo_features, 'price_num', 'motherboard')
            mobo_ranks = predict_and_rank(mobo_model, mobo_features, 'motherboard', mobo_features_list)
            
            print("Processing cooler data...")
            cursor.execute("SELECT * FROM cooler_specs")
            coolers = cursor.fetchall()
            cooler_features = prepare_cooler_data(coolers)
            cooler_model, cooler_features_list = train_model(cooler_features, 'price_num', 'cooler')
            cooler_ranks = predict_and_rank(cooler_model, cooler_features, 'cooler', cooler_features_list)
            
            print("Processing GPU data...")
            cursor.execute("SELECT * FROM gpu_specs")
            gpus = cursor.fetchall()
            gpu_features = prepare_gpu_data(gpus)
            gpu_model, gpu_features_list = train_model(gpu_features, 'price_num', 'gpu')
            gpu_ranks = predict_and_rank(gpu_model, gpu_features, 'gpu', gpu_features_list)
            
            print("Processing case data...")
            cursor.execute("SELECT * FROM case_specs")
            cases = cursor.fetchall()
            case_features = prepare_case_data(cases)
            case_model, case_features_list = train_model(case_features, 'price_num', 'case')
            case_ranks = predict_and_rank(case_model, case_features, 'case', case_features_list)
            
            print("Processing PSU data...")
            cursor.execute("SELECT * FROM psu_specs")
            psus = cursor.fetchall()
            psu_features = prepare_psu_data(psus)
            psu_model, psu_features_list = train_model(psu_features, 'price_num', 'psu')
            psu_ranks = predict_and_rank(psu_model, psu_features, 'psu', psu_features_list)
            
            print("Processing memory data...")
            cursor.execute("SELECT * FROM memory_specs")
            memories = cursor.fetchall()
            memory_features = prepare_memory_data(memories)
            memory_model, memory_features_list = train_model(memory_features, 'price_num', 'memory')
            memory_ranks = predict_and_rank(memory_model, memory_features, 'memory', memory_features_list)
            
            # Update database with ML scores and ranks
            print("Updating database with ML scores and ranks...")
            
            # Update CPUs
            for _, row in cpu_ranks.iterrows():
                cursor.execute(
                    "UPDATE cpu_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update motherboards
            for _, row in mobo_ranks.iterrows():
                cursor.execute(
                    "UPDATE motherboard_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update coolers
            for _, row in cooler_ranks.iterrows():
                cursor.execute(
                    "UPDATE cooler_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update GPUs
            for _, row in gpu_ranks.iterrows():
                cursor.execute(
                    "UPDATE gpu_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update cases
            for _, row in case_ranks.iterrows():
                cursor.execute(
                    "UPDATE case_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update PSUs
            for _, row in psu_ranks.iterrows():
                cursor.execute(
                    "UPDATE psu_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
            
            # Update memory
            for _, row in memory_ranks.iterrows():
                cursor.execute(
                    "UPDATE memory_specs SET ml_score = %s, rank = %s WHERE id = %s", 
                    (row['ml_score'], row['rank'], row['id'])
                )
        
        # Commit the changes
        conn.commit()
        print("All component ML scores and ranks updated successfully!")
    
    except Exception as e:
        print(f"Error updating component ranks: {e}")
        conn.rollback()

def main():
    """Main function to connect to database and update ranks using ML"""
    try:
        # Connect to database using config settings
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Make sure all tables have ml_score and rank columns
        ensure_rank_columns_exist(conn)
        
        # Update all component ranks
        update_component_ranks(conn)
        
        print("Database update complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 