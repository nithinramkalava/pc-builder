import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration - Update these values to match your database
DB_CONFIG = {
    'host': 'localhost',
    'database': 'pc_builder_prod', 
    'user': 'pc_builder_admin',      
    'password': 'pc_builder'          
}

# ========== COMPONENT SCORING FUNCTIONS ==========

def score_cpu(cpu):
    """
    Score a CPU based on its specifications.
    Returns a score out of 100.
    """
    try:
        # Parse numeric values and handle potential NULL values
        core_count = int(cpu['core_count']) if cpu['core_count'] not in ['NaN', 'NULL'] else 0
        thread_count = int(cpu['thread_count']) if cpu['thread_count'] not in ['NaN', 'NULL'] else 0
        
        # Parse clock speeds
        base_clock = 0
        if cpu['performance_core_clock'] not in ['NaN', 'NULL']:
            base_clock = float(cpu['performance_core_clock'].replace('GHz', '').strip())
        
        boost_clock = 0
        if cpu['performance_core_boost_clock'] not in ['NaN', 'NULL']:
            boost_clock = float(cpu['performance_core_boost_clock'].replace('GHz', '').strip())
        
        # Parse cache
        l3_cache = 0
        if cpu['l3_cache'] not in ['NaN', 'NULL']:
            l3_cache = float(cpu['l3_cache'].replace('MB', '').strip())
        
        # Get price
        price = float(cpu['price_num']) if cpu['price_num'] not in ['NaN', 'NULL'] else 1000
        
        # Calculate scores
        core_score = min(core_count * 5, 40)  # Cap at 40 points
        thread_score = min((thread_count - core_count) * 2.5, 10)  # Value for SMT/HT
        base_clock_score = min(base_clock * 2, 10)
        boost_clock_score = min(boost_clock * 3, 15)
        cache_score = min(l3_cache / 2, 10)  # 1 point per 2MB of L3 cache
        value_score = max(25 - (price / 40), 0)
        
        total_score = core_score + thread_score + base_clock_score + boost_clock_score + cache_score + value_score
        return min(round(total_score), 100)  # Cap at 100
    except Exception as e:
        print(f"Error scoring CPU: {e}")
        return 0


def score_motherboard(mobo):
    """
    Score a motherboard based on its specifications.
    Returns a score out of 100.
    """
    try:
        # Parse memory specs
        memory_max = 0
        if mobo['memory_max'] not in ['NaN', 'NULL']:
            memory_max = int(mobo['memory_max'].replace('GB', '').strip())
        
        memory_slots = int(mobo['memory_slots']) if mobo['memory_slots'] not in ['NaN', 'NULL'] else 0
        price = float(mobo['price_num']) if mobo['price_num'] not in ['NaN', 'NULL'] else 1000
        
        # Memory support
        memory_max_score = min(memory_max / 16, 10)
        memory_slots_score = min(memory_slots * 2.5, 10)
        
        # Form factor (ATX better than mATX better than ITX)
        form_factor_score = {"ATX": 10, "Micro ATX": 8, "Mini ITX": 6}.get(mobo['form_factor'], 5)
        
        # Expansion and storage
        m2_slots_score = 0
        if mobo['m2_slots'] not in ['NULL', 'NaN']:
            m2_slots = str(mobo['m2_slots']).split('\n')
            m2_slots_score = min(len(m2_slots) * 5, 15)
        
        # Features
        wifi_score = 0
        if mobo['wireless_networking'] not in ['NULL', 'NaN', None]:
            wifi_score = 10 if "Wi-Fi" in str(mobo['wireless_networking']) else 0
        
        # Modern chipset - extract series number from chipset
        chipset_score = 0
        if mobo['chipset'] not in ['NULL', 'NaN', None]:
            if "Z" in str(mobo['chipset']):
                chipset_score = 20  # High-end
            elif "B" in str(mobo['chipset']):
                chipset_score = 15  # Mid-range
            elif "H" in str(mobo['chipset']):
                chipset_score = 10  # Budget
        
        # Value factor
        value_score = max(20 - (price / 50), 0)
        
        total_score = memory_max_score + memory_slots_score + form_factor_score + m2_slots_score + wifi_score + chipset_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring motherboard: {e}")
        return 0


def score_cooler(cooler):
    """
    Score a CPU cooler based on its specifications.
    Returns a score out of 100.
    """
    try:
        price = float(cooler['price_num']) if cooler['price_num'] not in ['NaN', 'NULL'] else 1000
        
        # Performance metrics
        rpm_score = 0
        if cooler['fan_rpm'] not in ['NULL', 'NaN', None]:
            rpm = float(cooler['fan_rpm'].split()[0])
            rpm_score = min(rpm / 500, 10)
        
        # Noise (lower is better)
        noise_score = 0
        if cooler['noise_level'] not in ['NULL', 'NaN', None]:
            noise_text = cooler['noise_level']
            if "-" in noise_text:
                noise_level = float(noise_text.split("-")[0].strip())
            else:
                noise_level = float(noise_text.split()[0])
            noise_score = max(20 - noise_level, 0)
        
        # Socket compatibility (more is better)
        socket_score = 0
        if cooler['cpu_socket'] not in ['NULL', 'NaN', None]:
            socket_score = min(len(str(cooler['cpu_socket']).split('\n')) * 2, 20)
        
        # Water cooling premium
        cooling_type_score = 15 if cooler['water_cooled'] else 0
        
        # Value factor
        value_score = max(35 - (price / 10), 0)
        
        total_score = rpm_score + noise_score + socket_score + cooling_type_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring cooler: {e}")
        return 0


def score_gpu(gpu):
    """
    Score a GPU based on its specifications.
    Returns a score out of 100.
    """
    try:
        # Parse memory
        memory = 0
        if gpu['memory'] not in ['NaN', 'NULL', None]:
            memory = int(gpu['memory'].split()[0])
        
        # Parse clock speeds
        core_clock = 0
        if gpu['core_clock'] not in ['NaN', 'NULL', None]:
            core_clock = float(gpu['core_clock'].replace('MHz', '').strip())
        
        boost_clock = 0
        if gpu['boost_clock'] not in ['NaN', 'NULL', None]:
            boost_clock = float(gpu['boost_clock'].replace('MHz', '').strip())
        
        price = float(gpu['price_num']) if gpu['price_num'] not in ['NaN', 'NULL'] else 2000
        
        # GPU memory
        memory_score = min(memory * 2, 30)
        
        # Clock speeds
        core_clock_score = min(core_clock / 100, 10)
        boost_clock_score = min(boost_clock / 100, 15)
        
        # Performance tier based on chipset
        chipset_score = 0
        if gpu['chipset'] not in ['NaN', 'NULL', None]:
            chipset = str(gpu['chipset'])
            if "5090" in chipset or "4090" in chipset:
                chipset_score = 25
            elif "5080" in chipset or "4080" in chipset or "3090" in chipset:
                chipset_score = 20
            elif "5070" in chipset or "4070" in chipset or "3080" in chipset:
                chipset_score = 15
            elif "5060" in chipset or "4060" in chipset or "3070" in chipset:
                chipset_score = 10
            else:
                chipset_score = 5
        
        # Cooling
        cooling_score = 0
        if gpu['cooling'] not in ['NaN', 'NULL', None]:
            fans = int(gpu['cooling'].split()[0])
            cooling_score = fans * 5
        
        # Value factor (price per performance)
        value_score = max(20 - (price / 150), 0)
        
        total_score = memory_score + core_clock_score + boost_clock_score + chipset_score + cooling_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring GPU: {e}")
        return 0


def score_case(case):
    """
    Score a PC case based on its specifications.
    Returns a score out of 100.
    """
    try:
        price = float(case['price_num']) if case['price_num'] not in ['NaN', 'NULL'] else 200
        
        # Form factor support
        form_factor_score = 0
        if case['motherboard_form_factor'] not in ['NaN', 'NULL', None]:
            form_factor_support = len(str(case['motherboard_form_factor']).split('\n'))
            form_factor_score = min(form_factor_support * 5, 15)
        
        # Premium features
        glass_panel_score = 0
        if case['side_panel'] not in ['NaN', 'NULL', None]:
            glass_panel_score = 10 if "Glass" in str(case['side_panel']) else 0
        
        shroud_score = 10 if case['power_supply_shroud'] else 0
        
        # USB connectivity
        usb_score = 0
        if case['front_panel_usb'] not in ['NaN', 'NULL', None]:
            if "USB 3.2 Gen 2 Type-C" in str(case['front_panel_usb']):
                usb_score += 15
            elif "USB 3.2 Gen 1" in str(case['front_panel_usb']):
                usb_score += 10
        
        # GPU clearance
        gpu_length_score = 0
        if case['maximum_video_card_length'] not in ['NaN', 'NULL', None]:
            gpu_length = float(case['maximum_video_card_length'].split()[0])
            gpu_length_score = min(gpu_length / 30, 10)
        
        # Storage options
        drive_count = 0
        if case['drive_bays'] not in ['NaN', 'NULL', None]:
            drive_bays = str(case['drive_bays']).split('\n')
            for bay in drive_bays:
                if "x" in bay:
                    count = int(bay.split('x')[0].strip())
                    drive_count += count
        drive_score = min(drive_count * 2, 15)
        
        # Value factor
        value_score = max(25 - (price / 20), 0)
        
        total_score = form_factor_score + glass_panel_score + shroud_score + usb_score + gpu_length_score + drive_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring case: {e}")
        return 0


def score_psu(psu):
    """
    Score a power supply unit based on its specifications.
    Returns a score out of 100.
    """
    try:
        wattage = 0
        if psu['wattage'] not in ['NaN', 'NULL', None]:
            wattage = int(psu['wattage'])
        
        price = float(psu['price_num']) if psu['price_num'] not in ['NaN', 'NULL'] else 200
        
        # Wattage (higher is better)
        wattage_score = min(wattage / 20, 30)
        
        # Efficiency rating
        efficiency_score = 0
        if psu['efficiency_rating'] not in ['NaN', 'NULL', None]:
            if "Titanium" in str(psu['efficiency_rating']):
                efficiency_score = 25
            elif "Platinum" in str(psu['efficiency_rating']):
                efficiency_score = 20
            elif "Gold" in str(psu['efficiency_rating']):
                efficiency_score = 15
            elif "Silver" in str(psu['efficiency_rating']):
                efficiency_score = 10
            elif "Bronze" in str(psu['efficiency_rating']):
                efficiency_score = 5
            elif "80+" in str(psu['efficiency_rating']):
                efficiency_score = 3
        
        # Modularity bonus
        modularity_score = 0
        if psu['modular'] not in ['NaN', 'NULL', None]:
            if psu['modular'] == "Full":
                modularity_score = 15
            elif psu['modular'] == "Semi":
                modularity_score = 10
        
        # Value factor
        value_score = max(30 - (price / 30), 0)
        
        total_score = wattage_score + efficiency_score + modularity_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring PSU: {e}")
        return 0


def score_memory(mem):
    """
    Score memory (RAM) based on its specifications.
    Returns a score out of 100.
    """
    try:
        price = float(mem['price_num']) if mem['price_num'] not in ['NaN', 'NULL'] else 200
        
        # Speed - higher is better
        speed = 0
        if mem['speed'] not in ['NaN', 'NULL', None]:
            speed_text = mem['speed']
            if "DDR" in speed_text:
                speed = int(speed_text.split('-')[1])
            else:
                speed = int(speed_text)
        speed_score = min(speed / 200, 30)
        
        # Capacity - total GB
        total_capacity = 0
        if mem['modules'] not in ['NaN', 'NULL', None]:
            modules = mem['modules'].split('x')
            if len(modules) == 2:
                count = int(modules[0].strip())
                size = int(modules[1].strip().replace('GB', ''))
                total_capacity = count * size
        capacity_score = min(total_capacity / 4, 25)
        
        # Latency - lower is better
        latency_score = 0
        if mem['first_word_latency'] not in ['NaN', 'NULL', None]:
            latency = float(mem['first_word_latency'].replace('ns', '').strip())
            latency_score = max(15 - latency, 0)
        
        # Features
        heat_spreader_score = 10 if mem['heat_spreader'] else 0
        
        # Value factor - price per GB
        value_score = max(20 - (price / total_capacity * 2), 0) if total_capacity > 0 else 0
        
        total_score = speed_score + capacity_score + latency_score + heat_spreader_score + value_score
        return min(round(total_score), 100)
    except Exception as e:
        print(f"Error scoring memory: {e}")
        return 0


# ========== DATABASE UPDATE FUNCTIONS ==========

def update_component_scores(conn):
    """Update scores for all components in the database"""
    try:
        # Create a cursor
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            print("Updating CPU scores...")
            # Get all components and calculate their scores
            cursor.execute("SELECT * FROM cpu_specs")
            cpus = cursor.fetchall()
            for cpu in cpus:
                score = score_cpu(cpu)
                cursor.execute("UPDATE cpu_specs SET score = %s WHERE id = %s", (score, cpu['id']))
            
            print("Updating motherboard scores...")
            cursor.execute("SELECT * FROM motherboard_specs")
            motherboards = cursor.fetchall()
            for mobo in motherboards:
                score = score_motherboard(mobo)
                cursor.execute("UPDATE motherboard_specs SET score = %s WHERE id = %s", (score, mobo['id']))
            
            print("Updating cooler scores...")
            cursor.execute("SELECT * FROM cooler_specs")
            coolers = cursor.fetchall()
            for cooler in coolers:
                score = score_cooler(cooler)
                cursor.execute("UPDATE cooler_specs SET score = %s WHERE id = %s", (score, cooler['id']))
            
            print("Updating GPU scores...")
            cursor.execute("SELECT * FROM gpu_specs")
            gpus = cursor.fetchall()
            for gpu in gpus:
                score = score_gpu(gpu)
                cursor.execute("UPDATE gpu_specs SET score = %s WHERE id = %s", (score, gpu['id']))
            
            print("Updating case scores...")
            cursor.execute("SELECT * FROM case_specs")
            cases = cursor.fetchall()
            for case in cases:
                score = score_case(case)
                cursor.execute("UPDATE case_specs SET score = %s WHERE id = %s", (score, case['id']))
            
            print("Updating PSU scores...")
            cursor.execute("SELECT * FROM psu_specs")
            psus = cursor.fetchall()
            for psu in psus:
                score = score_psu(psu)
                cursor.execute("UPDATE psu_specs SET score = %s WHERE id = %s", (score, psu['id']))
            
            print("Updating memory scores...")
            cursor.execute("SELECT * FROM memory_specs")
            memories = cursor.fetchall()
            for memory in memories:
                score = score_memory(memory)
                cursor.execute("UPDATE memory_specs SET score = %s WHERE id = %s", (score, memory['id']))
        
        # Commit the changes
        conn.commit()
        print("All component scores updated successfully!")
    
    except Exception as e:
        print(f"Error updating component scores: {e}")
        conn.rollback()


def ensure_score_columns_exist(conn):
    """Make sure all component tables have a score column"""
    try:
        with conn.cursor() as cursor:
            # Add score column to each table if it doesn't exist
            tables = [
                'cpu_specs', 'motherboard_specs', 'cooler_specs',
                'gpu_specs', 'case_specs', 'psu_specs', 'memory_specs'
            ]
            
            for table in tables:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'score'
                """)
                if not cursor.fetchone():
                    print(f"Adding score column to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN score INTEGER")
        
        conn.commit()
        print("Score columns added where needed")
    
    except Exception as e:
        print(f"Error ensuring score columns exist: {e}")
        conn.rollback()


def main():
    """Main function to connect to database and update scores"""
    try:
        # Connect to database using config settings
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Make sure all tables have a score column
        ensure_score_columns_exist(conn)
        
        # Update all component scores
        update_component_scores(conn)
        
        print("Database update complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main() 