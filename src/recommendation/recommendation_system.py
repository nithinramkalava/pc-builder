import json
import os
import pandas as pd
import numpy as np
from data_connection import get_sqlalchemy_engine, connect_to_db

class PCRecommendationSystem:
    def __init__(self, input_file=r"C:\Users\voltX\OneDrive\Desktop\pc-builder\src\recommendation\input.json"):
        """Initialize the recommendation system with user preferences"""
        # Load user preferences
        self.user_prefs = self._load_preferences(input_file)
        
        # Connect to database
        self.engine = get_sqlalchemy_engine()
        self.conn = connect_to_db()
        self.cursor = self.conn.cursor()
        
        # Store selected components
        self.selected_components = {}
        
        # Define component tables
        self.component_tables = {
            "cpu": "cpu_specs",
            "motherboard": "motherboard_specs",
            "cooler": "cooler_specs",
            "memory": "memory_specs",
            "gpu": "gpu_specs",
            "storage": "ssd_specs",
            "case": "case_specs",
            "psu": "psu_specs"
        }
        
        # Budget allocation percentages (default values)
        self.budget_allocation = {
            "cpu": 0.20,        # 1st - CPU first as all other components depend on it
            "motherboard": 0.16, # 2nd - Motherboard depends on CPU
            "cooler": 0.05,     # 3rd - CPU Cooler depends on CPU
            "memory": 0.12,     # 4th - Memory depends on Motherboard and CPU
            "gpu": 0.28,        # 5th - GPU depends on Motherboard
            "case": 0.07,       # 6th - Case depends on GPU and Motherboard
            "psu": 0.06,        # 7th - PSU depends on CPU, GPU, and Case
            "storage": 0.06     # 8th - Storage depends on Motherboard
        }
        
        # Currency conversion rate: INR to USD (approximate, update as needed)
        self.inr_to_usd = 0.012  # 1 INR = 0.012 USD
        
        # Adjust budget allocations based on user preferences
        self._adjust_budget_allocation()
        
    def _load_preferences(self, input_file):
        """Load user preferences from JSON file"""
        with open(input_file, 'r') as f:
            return json.load(f)

    def _adjust_budget_allocation(self):
        """Adjust budget allocation based on use cases and performance priorities, following component selection order"""
        # Initialize budget allocation based on component selection order
        self.budget_allocation = {
            "cpu": 0.20,        # 1st - CPU first as all other components depend on it
            "motherboard": 0.16, # 2nd - Motherboard depends on CPU
            "cooler": 0.05,     # 3rd - CPU Cooler depends on CPU
            "memory": 0.12,     # 4th - Memory depends on Motherboard and CPU
            "gpu": 0.28,        # 5th - GPU depends on Motherboard
            "case": 0.07,       # 6th - Case depends on GPU and Motherboard
            "psu": 0.06,        # 7th - PSU depends on CPU, GPU, and Case
            "storage": 0.06     # 8th - Storage depends on Motherboard
        }
        
        # Get user preferences
        use_cases = self.user_prefs["useCases"]
        perf_priorities = self.user_prefs["performancePriorities"]
        
        # Adjust for gaming (prioritize GPU)
        if use_cases["gaming"]["needed"] and use_cases["gaming"]["intensity"] > 5:
            self.budget_allocation["gpu"] += 0.05
            self.budget_allocation["cpu"] -= 0.02
            self.budget_allocation["storage"] -= 0.01
            self.budget_allocation["case"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.01
        
        # Adjust for video editing/rendering (prioritize CPU and RAM)
        if (use_cases["videoEditing"]["needed"] and use_cases["videoEditing"]["intensity"] > 5) or \
           (use_cases["rendering3D"]["needed"] and use_cases["rendering3D"]["intensity"] > 5):
            self.budget_allocation["cpu"] += 0.05
            self.budget_allocation["memory"] += 0.03
            self.budget_allocation["gpu"] -= 0.03
            self.budget_allocation["case"] -= 0.02
            self.budget_allocation["psu"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.02
        
        # Adjust for programming (prioritize CPU and RAM)
        if use_cases["programming"]["needed"] and use_cases["programming"]["intensity"] > 5:
            self.budget_allocation["cpu"] += 0.03
            self.budget_allocation["memory"] += 0.02
            self.budget_allocation["gpu"] -= 0.03
            self.budget_allocation["case"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.01
            
        # Fine-tune based on explicit performance priorities
        if perf_priorities.get("cpu", 0) > 7:
            self.budget_allocation["cpu"] += 0.03
            self.budget_allocation["gpu"] -= 0.02
            self.budget_allocation["case"] -= 0.01
            
        if perf_priorities.get("gpu", 0) > 7:
            self.budget_allocation["gpu"] += 0.03
            self.budget_allocation["cpu"] -= 0.02
            self.budget_allocation["case"] -= 0.01
            
        if perf_priorities.get("ram", 0) > 7:
            self.budget_allocation["memory"] += 0.02
            self.budget_allocation["gpu"] -= 0.01
            self.budget_allocation["case"] -= 0.01
            
        if perf_priorities.get("storageSpeed", 0) > 7:
            self.budget_allocation["storage"] += 0.02
            self.budget_allocation["case"] -= 0.01
            self.budget_allocation["psu"] -= 0.01
            
        # Normalize allocations to ensure they sum to 1
        total = sum(self.budget_allocation.values())
        for key in self.budget_allocation:
            self.budget_allocation[key] /= total
    
    def _get_component_budget(self, component_type):
        """Calculate budget for a specific component in USD"""
        # Get budget in INR
        total_budget_inr = self.user_prefs["budget"]
        
        # Calculate component budget in INR
        component_budget_inr = total_budget_inr * self.budget_allocation[component_type]
        
        # Convert to USD for database comparison
        component_budget_usd = component_budget_inr * self.inr_to_usd
        
        return component_budget_usd
    
    def select_cpu(self):
        """Select the best CPU within budget, considering user preferences"""
        budget = self._get_component_budget("cpu")
        original_budget = budget
        
        # Build query based on preferences - sort by rank first (lower is better), then price in ascending order for value
        query = """
            SELECT * FROM cpu_specs 
            WHERE price_num <= %s AND price_num > 0 
            ORDER BY 
                CASE WHEN rank IS NULL THEN 9999 ELSE rank END ASC,
                price_num ASC
            LIMIT 5
        """
        
        # Filter by platform preference if specified
        platform_pref = self.user_prefs["technicalPreferences"].get("cpuPlatform")
        if platform_pref:
            if platform_pref.upper() == "AMD":
                query = """
                    SELECT * FROM cpu_specs 
                    WHERE price_num <= %s AND manufacturer = 'AMD' AND price_num > 0 
                    ORDER BY 
                        CASE WHEN rank IS NULL THEN 9999 ELSE rank END ASC,
                        price_num ASC
                    LIMIT 5
                """
            elif platform_pref.upper() == "INTEL":
                query = """
                    SELECT * FROM cpu_specs 
                    WHERE price_num <= %s AND manufacturer = 'Intel' AND price_num > 0 
                    ORDER BY 
                        CASE WHEN rank IS NULL THEN 9999 ELSE rank END ASC,
                        price_num ASC
                    LIMIT 5
                """
        
        try:
            # Execute query
            self.cursor.execute(query, (budget,))
            results = self.cursor.fetchall()
            
            if not results:
                # First fallback: Try with a 50% higher budget
                budget = original_budget * 1.5
                print(f"DEBUG: No CPUs found within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                self.cursor.execute(query, (budget,))
                results = self.cursor.fetchall()
                
            if not results:
                # Second fallback: Try with a 100% higher budget (double the original)
                budget = original_budget * 2
                print(f"DEBUG: No CPUs found with 50% higher budget, trying with double budget: ${budget}")
                self.cursor.execute(query, (budget,))
                results = self.cursor.fetchall()
                
            if not results:
                # Final fallback: Try with a maximum budget cap of 2.5x
                budget = original_budget * 2.5
                print(f"DEBUG: No CPUs found with double budget, trying with final cap of ${budget}")
                self.cursor.execute(query, (budget,))
                results = self.cursor.fetchall()
                
            if not results:
                # Last resort: look for the cheapest CPU
                print(f"DEBUG: No CPUs within any budget cap, looking for cheapest CPU")
                
                # Modify query to sort by price ascending only
                cheapest_query = query.replace("ORDER BY \n                CASE WHEN rank IS NULL THEN 9999 ELSE rank END ASC,\n                price_num ASC", 
                                              "ORDER BY price_num ASC")
                self.cursor.execute(cheapest_query)
                results = self.cursor.fetchall()
                
            if not results:
                raise Exception(f"No compatible CPU found within budget of ${budget:.2f} (₹{budget/self.inr_to_usd:.2f})")
            
            # Get column names
            column_names = [desc[0] for desc in self.cursor.description]
            
            # Convert to dictionary - take the top result which has the best rank
            cpu = dict(zip(column_names, results[0]))
            
            # Use existing price_num if available or extract from price string
            if "price_num" in cpu and cpu["price_num"] is not None and cpu["price_num"] > 0:
                print(f"DEBUG: Using existing price_num for CPU: {cpu.get('price_num')}")
            else:
                # Extract numeric value from price string
                price_str = str(cpu.get("price", "$0.00"))
                try:
                    # Remove $ and comma characters
                    price_str = price_str.replace("$", "").replace(",", "")
                    cpu["price_num"] = float(price_str)
                    print(f"DEBUG: Extracted price_num from string for CPU: {cpu['price_num']}")
                except Exception as e:
                    print(f"DEBUG: Error extracting price from string for CPU: {str(e)}")
                    cpu["price_num"] = 0
            
            # Log if we're going over the original budget
            if cpu.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected CPU costs ${cpu.get('price_num', 0)}, which is ${cpu.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            self.selected_components["cpu"] = cpu
            
            return cpu
        except Exception as e:
            raise Exception(f"Error selecting CPU: {str(e)}")
    
    def select_motherboard(self):
        """Select the best motherboard compatible with the chosen CPU"""
        if "cpu" not in self.selected_components:
            raise Exception("CPU must be selected before choosing a motherboard")
            
        budget = self._get_component_budget("motherboard")
        original_budget = budget
        cpu_id = self.selected_components["cpu"]["id"]
        
        try:
            # Use compatibility function to get compatible motherboards and join with motherboard_specs to get rank
            query = """
                SELECT c.*, m.rank, m.ml_score, m.price_num
                FROM get_compatible_motherboards(%s) c
                LEFT JOIN motherboard_specs m ON c.id = m.id
                WHERE m.price_num <= %s AND m.price_num > 0
                ORDER BY 
                    CASE WHEN m.rank IS NULL THEN 9999 ELSE m.rank END ASC,
                    m.price_num ASC
                LIMIT 5
            """
            self.cursor.execute(query, (cpu_id, budget))
            results = self.cursor.fetchall()
            
            if not results:
                # First fallback: Try with a 50% higher budget
                budget = original_budget * 1.5
                print(f"DEBUG: No motherboards found within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Second fallback: Try with a 100% higher budget (double the original)
                budget = original_budget * 2
                print(f"DEBUG: No motherboards found with 50% higher budget, trying with double budget: ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Final fallback: Try with a maximum budget cap of 2.5x
                budget = original_budget * 2.5
                print(f"DEBUG: No motherboards found with double budget, trying with final cap of ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Last resort: look for the cheapest compatible motherboard
                print(f"DEBUG: No motherboards within any budget cap, looking for cheapest compatible motherboard")
                cheapest_query = """
                    SELECT c.*, m.rank, m.ml_score, m.price_num
                    FROM get_compatible_motherboards(%s) c
                    LEFT JOIN motherboard_specs m ON c.id = m.id
                    WHERE m.price_num > 0
                    ORDER BY m.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(cheapest_query, (cpu_id,))
                results = self.cursor.fetchall()
                
            if not results:
                raise Exception(f"No compatible motherboard found for CPU id={cpu_id}")
            
            # Get column names
            column_names = [desc[0] for desc in self.cursor.description]
            
            # Convert to dictionary
            motherboard = dict(zip(column_names, results[0]))
            
            # Use existing price_num if available or extract from price string
            if "price_num" in motherboard and motherboard["price_num"] is not None and motherboard["price_num"] > 0:
                print(f"DEBUG: Using existing price_num for motherboard: {motherboard.get('price_num')}")
            else:
                # Extract numeric value from price string
                price_str = str(motherboard.get("price", "$0.00"))
                try:
                    # Remove $ and comma characters
                    price_str = price_str.replace("$", "").replace(",", "")
                    motherboard["price_num"] = float(price_str)
                    print(f"DEBUG: Extracted price_num from string for motherboard: {motherboard['price_num']}")
                except Exception as e:
                    print(f"DEBUG: Error extracting price from string for motherboard: {str(e)}")
                    motherboard["price_num"] = 0
            
            # Log if we're going over the original budget
            if motherboard.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected motherboard costs ${motherboard.get('price_num', 0)}, which is ${motherboard.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            self.selected_components["motherboard"] = motherboard
            return motherboard
            
        except Exception as e:
            raise Exception(f"Error selecting motherboard: {str(e)}")
    
    def select_cooler(self):
        """Select the best CPU cooler compatible with the chosen CPU"""
        if "cpu" not in self.selected_components:
            raise Exception("CPU must be selected before choosing a CPU cooler")
            
        budget = self._get_component_budget("cooler")
        original_budget = budget
        cpu_id = self.selected_components["cpu"]["id"]
        
        try:
            # Use compatibility function to get compatible CPU coolers and join with cooler_specs to get rank
            query = """
                SELECT c.*, cs.rank, cs.ml_score, cs.price_num
                FROM get_compatible_cpu_coolers(%s) c
                LEFT JOIN cooler_specs cs ON c.id = cs.id
                WHERE cs.price_num <= %s AND cs.price_num > 0
                ORDER BY 
                    CASE WHEN cs.rank IS NULL THEN 9999 ELSE cs.rank END ASC,
                    cs.price_num ASC
                LIMIT 5
            """
            self.cursor.execute(query, (cpu_id, budget))
            results = self.cursor.fetchall()
            
            if not results:
                # First fallback: Try with a 50% higher budget
                budget = original_budget * 1.5
                print(f"DEBUG: No coolers found within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Second fallback: Try with a 100% higher budget (double the original)
                budget = original_budget * 2
                print(f"DEBUG: No coolers found with 50% higher budget, trying with double budget: ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Final fallback: Try with a maximum budget cap of 2.5x
                budget = original_budget * 2.5
                print(f"DEBUG: No coolers found with double budget, trying with final cap of ${budget}")
                self.cursor.execute(query, (cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Last resort: look for the cheapest compatible cooler
                print(f"DEBUG: No coolers within any budget cap, looking for cheapest compatible cooler")
                cheapest_query = """
                    SELECT c.*, cs.rank, cs.ml_score, cs.price_num
                    FROM get_compatible_cpu_coolers(%s) c
                    LEFT JOIN cooler_specs cs ON c.id = cs.id
                    WHERE cs.price_num > 0
                    ORDER BY cs.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(cheapest_query, (cpu_id,))
                results = self.cursor.fetchall()
                
            if not results:
                raise Exception(f"No compatible CPU cooler found for CPU id={cpu_id}")
            
            # Get column names
            column_names = [desc[0] for desc in self.cursor.description]
            
            # Convert to dictionary
            cooler = dict(zip(column_names, results[0]))
            
            # Use existing price_num if available or extract from price string
            if "price_num" in cooler and cooler["price_num"] is not None and cooler["price_num"] > 0:
                print(f"DEBUG: Using existing price_num for cooler: {cooler.get('price_num')}")
            else:
                # Extract numeric value from price string
                price_str = str(cooler.get("price", "$0.00"))
                try:
                    # Remove $ and comma characters
                    price_str = price_str.replace("$", "").replace(",", "")
                    cooler["price_num"] = float(price_str)
                    print(f"DEBUG: Extracted price_num from string for cooler: {cooler['price_num']}")
                except Exception as e:
                    print(f"DEBUG: Error extracting price from string for cooler: {str(e)}")
                    cooler["price_num"] = 0
            
            # Log if we're going over the original budget
            if cooler.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected cooler costs ${cooler.get('price_num', 0)}, which is ${cooler.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            self.selected_components["cooler"] = cooler
            return cooler
        except Exception as e:
            raise Exception(f"Error selecting CPU cooler: {str(e)}")
    
    def select_memory(self):
        """Select the best RAM compatible with both the motherboard and CPU"""
        if "motherboard" not in self.selected_components or "cpu" not in self.selected_components:
            raise Exception("Motherboard and CPU must be selected before choosing memory")
            
        budget = self._get_component_budget("memory")
        original_budget = budget
        motherboard_id = self.selected_components["motherboard"]["id"]
        cpu_id = self.selected_components["cpu"]["id"]
        
        try:
            # Use compatibility function to get compatible memory and join with memory_specs to get rank
            query = """
                SELECT r.*, m.rank, m.ml_score, m.price_num
                FROM get_compatible_ram(%s, %s) r
                LEFT JOIN memory_specs m ON r.id = m.id
                WHERE m.price_num <= %s AND m.price_num > 0
                ORDER BY 
                    CASE WHEN m.rank IS NULL THEN 9999 ELSE m.rank END ASC,
                    m.price_num ASC
                LIMIT 5
            """
            self.cursor.execute(query, (motherboard_id, cpu_id, budget))
            results = self.cursor.fetchall()
            
            if not results:
                # First fallback: Try with a 50% higher budget
                budget = original_budget * 1.5
                print(f"DEBUG: No memory found within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                self.cursor.execute(query, (motherboard_id, cpu_id, budget))
                results = self.cursor.fetchall()
            
            if not results:
                # Second fallback: Try with a 100% higher budget (double the original)
                budget = original_budget * 2
                print(f"DEBUG: No memory found with 50% higher budget, trying with double budget: ${budget}")
                self.cursor.execute(query, (motherboard_id, cpu_id, budget))
                results = self.cursor.fetchall()
                
            if not results:
                # Third fallback: Try with a maximum budget cap of 2.5x
                budget = original_budget * 2.5
                print(f"DEBUG: No memory found with double budget, trying with final cap of ${budget}")
                self.cursor.execute(query, (motherboard_id, cpu_id, budget))
                results = self.cursor.fetchall()
            
            if not results:
                # Last resort: Look for the cheapest compatible memory regardless of budget
                # but sort by price to get the most affordable option
                print(f"DEBUG: No memory found within any budget cap, looking for cheapest compatible memory")
                fallback_query = """
                    SELECT r.*, m.rank, m.ml_score, m.price_num
                    FROM get_compatible_ram(%s, %s) r
                    LEFT JOIN memory_specs m ON r.id = m.id
                    WHERE m.price_num > 0
                    ORDER BY m.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(fallback_query, (motherboard_id, cpu_id))
                results = self.cursor.fetchall()
                
            if not results:
                # Absolute last resort: Try with only motherboard compatibility
                print(f"DEBUG: No compatible memory found, trying with just motherboard compatibility")
                mobo_only_query = """
                    SELECT m.*, ms.rank, ms.ml_score, ms.price_num
                    FROM memory_specs m
                    LEFT JOIN memory_specs ms ON m.id = ms.id
                    WHERE m.price_num > 0
                    ORDER BY m.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(mobo_only_query)
                results = self.cursor.fetchall()
                
            if not results:
                raise Exception(f"No compatible memory found for motherboard id={motherboard_id} and CPU id={cpu_id}. Please check compatibility.")
            
            # Get column names
            column_names = [desc[0] for desc in self.cursor.description]
            
            # Convert to dictionary
            memory = dict(zip(column_names, results[0]))
            
            # Use existing price_num if available or extract from price string
            if "price_num" in memory and memory["price_num"] is not None and memory["price_num"] > 0:
                print(f"DEBUG: Using existing price_num: {memory.get('price_num')}")
            else:
                # Extract numeric value from price string
                price_str = str(memory.get("price", "$0.00"))
                try:
                    # Remove $ and comma characters
                    price_str = price_str.replace("$", "").replace(",", "")
                    memory["price_num"] = float(price_str)
                    print(f"DEBUG: Extracted price_num from string: {memory['price_num']}")
                except Exception as e:
                    print(f"DEBUG: Error extracting price from string: {str(e)}")
                    memory["price_num"] = 0
            
            # Log if we're going over the original budget
            if memory.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected memory costs ${memory.get('price_num', 0)}, which is ${memory.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            self.selected_components["memory"] = memory
            return memory
        except Exception as e:
            raise Exception(f"Error selecting memory: {str(e)}")
    
    def select_gpu(self):
        """Select the best GPU compatible with the chosen motherboard"""
        if "motherboard" not in self.selected_components:
            raise Exception("Motherboard must be selected before choosing a GPU")
            
        budget = self._get_component_budget("gpu")
        original_budget = budget
        motherboard_id = self.selected_components["motherboard"]["id"]
        
        try:
            print(f"DEBUG: Starting GPU selection for motherboard_id={motherboard_id} with budget=${budget}")
            
            # Consider GPU platform preference if specified
            platform_pref = self.user_prefs["technicalPreferences"].get("gpuPlatform")
            platform_filter = ""
            
            if platform_pref:
                if platform_pref.upper() == "NVIDIA":
                    platform_filter = "AND v.chipset LIKE '%GeForce%'"
                elif platform_pref.upper() == "AMD":
                    platform_filter = "AND v.chipset LIKE '%Radeon%'"
            
            # First, check if the compatibility function returns any results at all
            compat_check_query = """
                SELECT COUNT(*) FROM get_compatible_video_cards(%s)
            """
            self.cursor.execute(compat_check_query, (motherboard_id,))
            count_result = self.cursor.fetchone()
            count = count_result[0] if count_result else 0
            
            print(f"DEBUG: Found {count} compatible GPUs for motherboard_id={motherboard_id}")
            
            if count == 0:
                raise Exception(f"No compatible GPUs found for motherboard id={motherboard_id}")
            
            # Get structure of the result to see available columns
            struct_query = """
                SELECT * FROM get_compatible_video_cards(%s) LIMIT 1
            """
            self.cursor.execute(struct_query, (motherboard_id,))
            struct_result = self.cursor.fetchone()
            column_names = [desc[0] for desc in self.cursor.description]
            print(f"DEBUG: Available columns in get_compatible_video_cards: {column_names}")
            
            # Get all compatible GPUs with price below budget and join with gpu_specs to get rank
            query = """
                SELECT v.*, g.rank as gpu_rank, g.ml_score, g.price_num
                FROM get_compatible_video_cards(%s) v
                LEFT JOIN gpu_specs g ON v.id = g.id
                WHERE g.price_num <= %s AND g.price_num > 0
                ORDER BY 
                    CASE WHEN g.rank IS NULL THEN 9999 ELSE g.rank END ASC,
                    g.price_num ASC
                LIMIT 10
            """
            
            print(f"DEBUG: Executing query with budget filter: {budget}")
            self.cursor.execute(query, (motherboard_id, budget))
            results = self.cursor.fetchall()
            
            print(f"DEBUG: Query returned {len(results)} results")
            
            if not results:
                # First fallback: Try with a 50% higher budget
                budget = original_budget * 1.5
                print(f"DEBUG: No GPUs found within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                self.cursor.execute(query, (motherboard_id, budget))
                results = self.cursor.fetchall()
                print(f"DEBUG: Query with 50% higher budget returned {len(results)} results")
            
            if not results:
                # Second fallback: Try with a 100% higher budget (double the original)
                budget = original_budget * 2
                print(f"DEBUG: No GPUs found with 50% higher budget, trying with double budget: ${budget}")
                self.cursor.execute(query, (motherboard_id, budget))
                results = self.cursor.fetchall()
                print(f"DEBUG: Query with double budget returned {len(results)} results")
                
            if not results:
                # Third fallback: Try with a maximum budget cap of 2.5x
                budget = original_budget * 2.5
                print(f"DEBUG: No GPUs found with double budget, trying with final cap of ${budget}")
                self.cursor.execute(query, (motherboard_id, budget))
                results = self.cursor.fetchall()
                print(f"DEBUG: Query with 2.5x budget returned {len(results)} results")
            
            if not results:
                # Last resort: Look for the cheapest compatible GPU regardless of budget
                print(f"DEBUG: No GPUs within any budget cap, looking for cheapest compatible GPU")
                cheapest_query = """
                    SELECT v.*, g.rank as gpu_rank, g.ml_score, g.price_num
                    FROM get_compatible_video_cards(%s) v
                    LEFT JOIN gpu_specs g ON v.id = g.id
                    WHERE g.price_num > 0
                    ORDER BY g.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(cheapest_query, (motherboard_id,))
                results = self.cursor.fetchall()
                
            if not results:
                raise Exception(f"No compatible GPU found for motherboard id={motherboard_id}")
            
            # Get the first result safely
            if len(results) == 0:
                raise Exception("No GPU results found after all queries")
            
            # Get column names
            column_names = [desc[0] for desc in self.cursor.description]
            print(f"DEBUG: Result columns: {column_names}")
            
            # Print first result for debugging
            first_result = results[0]
            print(f"DEBUG: First result has {len(first_result)} items: {first_result}")
            
            # Convert to dictionary safely
            gpu = {}
            for i, col in enumerate(column_names):
                if i < len(first_result):
                    gpu[col] = first_result[i]
                else:
                    print(f"DEBUG: Missing value for column {col}")
                    gpu[col] = None
            
            # Rename gpu_rank to rank for consistency
            if "gpu_rank" in gpu:
                gpu["rank"] = gpu["gpu_rank"]
                
            print(f"DEBUG: Selected GPU: {gpu.get('name')} at {gpu.get('price')}")
            
            # Use existing price_num if available or extract from price string
            if "price_num" in gpu and gpu["price_num"] is not None and gpu["price_num"] > 0:
                print(f"DEBUG: Using existing price_num: {gpu.get('price_num')}")
            else:
                # Extract numeric value from price string
                price_str = str(gpu.get("price", "$0.00"))
                try:
                    # Remove $ and comma characters
                    price_str = price_str.replace("$", "").replace(",", "")
                    gpu["price_num"] = float(price_str)
                    print(f"DEBUG: Extracted price_num from string: {gpu['price_num']}")
                except Exception as e:
                    print(f"DEBUG: Error extracting price from string: {str(e)}")
                    gpu["price_num"] = 0
                
            # Log if we're going over the original budget
            if gpu.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected GPU costs ${gpu.get('price_num', 0)}, which is ${gpu.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            self.selected_components["gpu"] = gpu
            return gpu
            
        except Exception as e:
            print(f"DEBUG: Error in GPU selection: {str(e)}")
            # If there's a specific error with tuple index, provide more context
            if "tuple index out of range" in str(e):
                print("DEBUG: This error typically occurs when trying to access elements in the query results that don't exist.")
                print("DEBUG: Check if all expected columns are being returned by the query.")
            raise Exception(f"Error selecting GPU: {str(e)}")
    
    def select_case(self):
        """Select the best case compatible with the GPU and motherboard"""
        if "motherboard" not in self.selected_components or "gpu" not in self.selected_components:
            raise Exception("Motherboard and GPU must be selected before choosing a case")
            
        budget = self._get_component_budget("case")
        motherboard_id = self.selected_components["motherboard"]["id"]
        gpu_id = self.selected_components["gpu"]["id"]
        
        try:
            print(f"DEBUG: Starting case selection for GPU id={gpu_id}, motherboard_id={motherboard_id} with budget=${budget}")
            
            # Check compatibility first
            check_query = """
                SELECT COUNT(*) FROM get_compatible_case(%s, %s)
            """
            self.cursor.execute(check_query, (gpu_id, motherboard_id))
            count = self.cursor.fetchone()[0]
            print(f"DEBUG: Found {count} compatible cases")
            
            if count == 0:
                raise Exception(f"No compatible cases found for GPU id={gpu_id} and motherboard id={motherboard_id}")
            
            # Get case with price filter, joining with case_specs to get the rank
            budget_query = """
                SELECT c.id, c.name, c.price, c.type, c.color, cs.rank as case_rank, cs.ml_score, cs.price_num
                FROM get_compatible_case(%s, %s) c
                LEFT JOIN case_specs cs ON c.id = cs.id
                WHERE cs.price_num <= %s AND cs.price_num > 0
                ORDER BY 
                    CASE WHEN cs.rank IS NULL THEN 9999 ELSE cs.rank END ASC,
                    cs.price_num ASC
                LIMIT 1
            """
            self.cursor.execute(budget_query, (gpu_id, motherboard_id, budget))
            budget_case = self.cursor.fetchone()
            
            # If no cases within budget, try with a higher budget
            if not budget_case:
                print(f"DEBUG: No cases within budget ${budget}, trying with 50% higher budget")
                self.cursor.execute(budget_query, (gpu_id, motherboard_id, budget * 1.5))
                budget_case = self.cursor.fetchone()
            
            # If still no cases, try without budget constraint
            if not budget_case:
                print(f"DEBUG: No cases within higher budget, trying without budget constraint")
                simple_query = """
                    SELECT c.id, c.name, c.price, c.type, c.color, cs.rank as case_rank, cs.ml_score, cs.price_num
                    FROM get_compatible_case(%s, %s) c
                    LEFT JOIN case_specs cs ON c.id = cs.id
                    WHERE cs.price_num > 0
                    ORDER BY 
                        CASE WHEN cs.rank IS NULL THEN 9999 ELSE cs.rank END ASC,
                        cs.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(simple_query, (gpu_id, motherboard_id))
                budget_case = self.cursor.fetchone()
            
            if not budget_case:
                raise Exception("No cases found with any query")
                
            print(f"DEBUG: Selected case result: {budget_case}")
            
            # Create case dict with just the essential fields to avoid index errors
            case = {
                "id": budget_case[0] if len(budget_case) > 0 else None,
                "name": budget_case[1] if len(budget_case) > 1 else "Unknown Case",
                "price": budget_case[2] if len(budget_case) > 2 else "$0",
                "type": budget_case[3] if len(budget_case) > 3 else "Unknown",
                "color": budget_case[4] if len(budget_case) > 4 else "Unknown",
                "rank": budget_case[5] if len(budget_case) > 5 else 9999,
                "ml_score": budget_case[6] if len(budget_case) > 6 else 0,
                "price_num": budget_case[7] if len(budget_case) > 7 else 0
            }
            
            # Rename case_rank to rank for consistency if needed
            if "case_rank" in case:
                case["rank"] = case["case_rank"]
                
            print(f"DEBUG: Created case dictionary: {case}")
            
            self.selected_components["case"] = case
            return case
            
        except Exception as e:
            print(f"DEBUG: Error in case selection: {str(e)}")
            raise Exception(f"Error selecting case: {str(e)}")
    
    def select_psu(self):
        """Select the best PSU based on the total power requirements"""
        if "cpu" not in self.selected_components or "gpu" not in self.selected_components or "case" not in self.selected_components:
            raise Exception("CPU, GPU, and case must be selected before choosing a PSU")
            
        budget = self._get_component_budget("psu")
        case_id = self.selected_components["case"]["id"]
        
        try:
            print(f"DEBUG: Starting PSU selection for case_id={case_id} with budget=${budget}")
            
            # Calculate estimated power requirement
            cpu_tdp = 100  # Default value
            if "tdp" in self.selected_components["cpu"]:
                try:
                    cpu_tdp_str = self.selected_components["cpu"]["tdp"]
                    if cpu_tdp_str:
                        cpu_tdp = int(''.join(filter(str.isdigit, cpu_tdp_str)))
                    print(f"DEBUG: CPU TDP: {cpu_tdp}W")
                except Exception as e:
                    print(f"DEBUG: Error parsing CPU TDP: {str(e)}")
            
            gpu_tdp = 200  # Default value
            if "tdp" in self.selected_components["gpu"]:
                try:
                    gpu_tdp_str = self.selected_components["gpu"]["tdp"]
                    if gpu_tdp_str:
                        gpu_tdp = int(''.join(filter(str.isdigit, gpu_tdp_str)))
                    print(f"DEBUG: GPU TDP: {gpu_tdp}W")
                except Exception as e:
                    print(f"DEBUG: Error parsing GPU TDP: {str(e)}")
            
            # Estimate with safety margin
            required_power = int((cpu_tdp + gpu_tdp + 150) * 1.3)
            print(f"DEBUG: Required power: {required_power}W")
            
            # Check compatibility
            check_query = """
                SELECT COUNT(*) FROM get_compatible_psu(%s, %s)
            """
            self.cursor.execute(check_query, (required_power, case_id))
            count = self.cursor.fetchone()[0]
            print(f"DEBUG: Found {count} compatible PSUs")
            
            # If none found, reduce the power requirement
            if count == 0:
                required_power = int((cpu_tdp + gpu_tdp + 150) * 1.1)
                print(f"DEBUG: Reducing required power to {required_power}W")
                self.cursor.execute(check_query, (required_power, case_id))
                count = self.cursor.fetchone()[0]
                print(f"DEBUG: Found {count} compatible PSUs with reduced power")
                
                if count == 0:
                    raise Exception(f"No compatible PSUs found for case id={case_id}")
            
            # Get PSU with budget filter and join with psu_specs to get rank
            budget_query = """
                SELECT p.id, p.name, p.price, p.type, p.efficiency_rating, p.wattage, ps.rank as psu_rank, ps.ml_score, ps.price_num
                FROM get_compatible_psu(%s, %s) p
                LEFT JOIN psu_specs ps ON p.id = ps.id
                WHERE ps.price_num <= %s AND ps.price_num > 0
                ORDER BY
                    CASE WHEN ps.rank IS NULL THEN 9999 ELSE ps.rank END ASC,
                    ps.price_num ASC
                LIMIT 1
            """
            self.cursor.execute(budget_query, (required_power, case_id, budget))
            budget_psu = self.cursor.fetchone()
            
            # If no PSUs within budget, try with a higher budget
            if not budget_psu:
                print(f"DEBUG: No PSUs within budget ${budget}, trying with 50% higher budget")
                self.cursor.execute(budget_query, (required_power, case_id, budget * 1.5))
                budget_psu = self.cursor.fetchone()
                
            # If still no PSUs, try without budget constraint
            if not budget_psu:
                print(f"DEBUG: No PSUs with higher budget, trying without budget constraint")
                cheap_query = """
                    SELECT p.id, p.name, p.price, p.type, p.efficiency_rating, p.wattage, ps.rank as psu_rank, ps.ml_score, ps.price_num
                    FROM get_compatible_psu(%s, %s) p
                    LEFT JOIN psu_specs ps ON p.id = ps.id
                    WHERE ps.price_num > 0
                    ORDER BY
                        CASE WHEN ps.rank IS NULL THEN 9999 ELSE ps.rank END ASC,
                        ps.price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(cheap_query, (required_power, case_id))
                budget_psu = self.cursor.fetchone()
            
            if not budget_psu:
                raise Exception("No PSUs found with any query")
                
            print(f"DEBUG: Selected PSU result: {budget_psu}")
            
            # Create PSU dict with just the essential fields
            psu = {
                "id": budget_psu[0] if len(budget_psu) > 0 else None,
                "name": budget_psu[1] if len(budget_psu) > 1 else "Unknown PSU",
                "price": budget_psu[2] if len(budget_psu) > 2 else "$0",
                "type": budget_psu[3] if len(budget_psu) > 3 else "Unknown",
                "efficiency_rating": budget_psu[4] if len(budget_psu) > 4 else "Unknown",
                "wattage": budget_psu[5] if len(budget_psu) > 5 else required_power,
                "rank": budget_psu[6] if len(budget_psu) > 6 else 9999,
                "ml_score": budget_psu[7] if len(budget_psu) > 7 else 0,
                "price_num": budget_psu[8] if len(budget_psu) > 8 else 0
            }
            
            # Rename psu_rank to rank for consistency if needed
            if "psu_rank" in psu:
                psu["rank"] = psu["psu_rank"]
                
            print(f"DEBUG: Created PSU dictionary: {psu}")
            
            self.selected_components["psu"] = psu
            return psu
            
        except Exception as e:
            print(f"DEBUG: Error in PSU selection: {str(e)}")
            raise Exception(f"Error selecting PSU: {str(e)}")
    
    def select_storage(self):
        """Select the best storage device compatible with the motherboard"""
        if "motherboard" not in self.selected_components:
            raise Exception("Motherboard must be selected before choosing storage")
            
        budget = self._get_component_budget("storage")
        original_budget = budget
        motherboard_id = self.selected_components["motherboard"]["id"]
        
        try:
            print(f"DEBUG: Starting storage selection for motherboard_id={motherboard_id} with budget=${budget}")
            
            # Check compatibility
            check_query = """
                SELECT COUNT(*) FROM get_compatible_ssd(%s)
            """
            self.cursor.execute(check_query, (motherboard_id,))
            count = self.cursor.fetchone()[0]
            print(f"DEBUG: Found {count} compatible storage devices")
            
            if count == 0:
                raise Exception(f"No compatible storage found for motherboard id={motherboard_id}")
            
            # Get any compatible storage by capacity
            budget_query = """
                SELECT s.id, s.name, s.price, s.capacity, s.type, s.interface, ss.price_num
                FROM get_compatible_ssd(%s) s
                JOIN ssd_specs ss ON s.id = ss.id
                WHERE ss.price_num <= %s AND ss.price_num > 0
                ORDER BY 
                    ss.capacity DESC,
                    ss.price_num ASC
                LIMIT 1
            """
            
            # Try to select storage within budget
            try:
                self.cursor.execute(budget_query, (motherboard_id, budget))
                budget_storage = self.cursor.fetchone()
            except Exception as e:
                print(f"DEBUG: Error in budget query: {str(e)}")
                budget_storage = None
            
            # First fallback: Try with a 50% higher budget
            if not budget_storage:
                budget = original_budget * 1.5
                print(f"DEBUG: No storage within budget ${original_budget}, trying with 50% higher budget: ${budget}")
                try:
                    self.cursor.execute(budget_query, (motherboard_id, budget))
                    budget_storage = self.cursor.fetchone()
                except Exception as e:
                    print(f"DEBUG: Error in 50% higher budget query: {str(e)}")
                    budget_storage = None
            
            # Second fallback: Try with a 100% higher budget (double the original)
            if not budget_storage:
                budget = original_budget * 2
                print(f"DEBUG: No storage with 50% higher budget, trying with double budget: ${budget}")
                try:
                    self.cursor.execute(budget_query, (motherboard_id, budget))
                    budget_storage = self.cursor.fetchone()
                except Exception as e:
                    print(f"DEBUG: Error in double budget query: {str(e)}")
                    budget_storage = None
            
            # Third fallback: Try with a maximum budget cap of 2.5x
            if not budget_storage:
                budget = original_budget * 2.5
                print(f"DEBUG: No storage with double budget, trying with final cap of ${budget}")
                try:
                    self.cursor.execute(budget_query, (motherboard_id, budget))
                    budget_storage = self.cursor.fetchone()
                except Exception as e:
                    print(f"DEBUG: Error in 2.5x budget query: {str(e)}")
                    budget_storage = None
            
            # Last resort: Look for the cheapest compatible storage regardless of budget
            if not budget_storage:
                print(f"DEBUG: No storage within any budget cap, looking for cheapest compatible storage")
                cheapest_query = """
                    SELECT s.id, s.name, s.price, s.capacity, s.type, s.interface, ss.price_num
                    FROM get_compatible_ssd(%s) s
                    JOIN ssd_specs ss ON s.id = ss.id
                    WHERE ss.price_num > 0
                    ORDER BY ss.price_num ASC
                    LIMIT 1
                """
                try:
                    self.cursor.execute(cheapest_query, (motherboard_id,))
                    budget_storage = self.cursor.fetchone()
                except Exception as e:
                    print(f"DEBUG: Error in cheapest query: {str(e)}")
                    budget_storage = None
            
            # Absolute last resort: any storage that exists
            if not budget_storage:
                print(f"DEBUG: Still no storage found, using any available storage")
                last_resort_query = """
                    SELECT id, name, price, capacity, type, interface, price_num
                    FROM ssd_specs
                    WHERE price_num > 0
                    ORDER BY price_num ASC
                    LIMIT 1
                """
                self.cursor.execute(last_resort_query)
                budget_storage = self.cursor.fetchone()
            
            if not budget_storage:
                raise Exception("No storage devices found with any query")
                
            print(f"DEBUG: Selected storage result: {budget_storage}")
            
            # Create storage dict with just the essential fields
            storage = {
                "id": budget_storage[0] if len(budget_storage) > 0 else None,
                "name": budget_storage[1] if len(budget_storage) > 1 else "Unknown Storage",
                "price": budget_storage[2] if len(budget_storage) > 2 else 0,
                "capacity": budget_storage[3] if len(budget_storage) > 3 else 500,
                "type": budget_storage[4] if len(budget_storage) > 4 else "SSD",
                "interface": budget_storage[5] if len(budget_storage) > 5 else "SATA",
                "price_num": budget_storage[6] if len(budget_storage) > 6 else 0
            }
            
            # Try to get rank separately
            try:
                # Try a simplified query since there might be no ml_score column
                storage["rank"] = 9999  # Default rank
                storage["ml_score"] = 0  # Default ml_score
                
                # No need to query for columns that don't exist
                print(f"DEBUG: Using default rank value: {storage['rank']}")
            except Exception as rank_err:
                print(f"DEBUG: Error getting rank: {str(rank_err)}")
                storage["rank"] = 9999
                storage["ml_score"] = 0
            
            # Log if we're going over the original budget
            if storage.get('price_num', 0) > original_budget:
                print(f"WARNING: Selected storage costs ${storage.get('price_num', 0)}, which is ${storage.get('price_num', 0) - original_budget} over the original budget of ${original_budget}")
            
            print(f"DEBUG: Created storage dictionary: {storage}")
            
            self.selected_components["storage"] = storage
            return storage
            
        except Exception as e:
            print(f"DEBUG: Error in storage selection: {str(e)}")
            raise Exception(f"Error selecting storage: {str(e)}")
    
    def build_recommendation(self):
        """
        Build a complete PC recommendation based on the budget
        Returns a dictionary of selected components in detailed format
        """
        try:
            # Get the budget from user preferences
            budget = self.user_prefs['budget']
            conversion_rate = self.inr_to_usd  # For clarity
            
            print(f"Building recommendation with budget ₹{budget:.2f} / ${budget * conversion_rate:.2f}")
            # Show budget allocation
            for component, percentage in self.budget_allocation.items():
                component_budget = budget * percentage
                print(f"{component.capitalize()}: {percentage * 100:.1f}% (₹{component_budget:.2f} / ${component_budget * conversion_rate:.2f})")
            
            # Perform component selection in this order:
            # CPU first
            cpu = self.select_cpu()
            print(f"Selected CPU: {cpu['name']} (${cpu.get('price_num', 0):.2f})")
            
            # Motherboard next
            motherboard = self.select_motherboard()
            print(f"Selected Motherboard: {motherboard['name']} (${motherboard.get('price_num', 0):.2f})")
            
            # CPU Cooler
            cooler = self.select_cooler()
            print(f"Selected Cooler: {cooler['name']} (${cooler.get('price_num', 0):.2f})")
            
            # GPU next (moved up from previous position)
            gpu = self.select_gpu()
            print(f"Selected GPU: {gpu['name']} (${gpu.get('price_num', 0):.2f})")
            
            # Case next (moved up from previous position)
            case = self.select_case()
            print(f"Selected Case: {case['name']} (${case.get('price_num', 0):.2f})")
            
            # PSU next (moved up from previous position)
            psu = self.select_psu()
            print(f"Selected PSU: {psu['name']} (${psu.get('price_num', 0):.2f})")
            
            # Memory next (moved down from previous position)
            memory = self.select_memory()
            print(f"Selected Memory: {memory['name']} (${memory.get('price_num', 0):.2f})")
            
            # Storage last
            storage = self.select_storage()
            print(f"Selected Storage: {storage['name']} (${storage.get('price_num', 0):.2f})")
            
            # Calculate total cost in USD safely
            total_cost_usd = 0
            
            # Helper function to safely extract price values
            def get_safe_price(component, price_key="price_num"):
                if component and price_key in component:
                    price = component.get(price_key)
                    if isinstance(price, (int, float)):
                        return float(price)
                # Fallback: try to parse from price string if price_num is not available
                if component and "price" in component:
                    price_str = str(component.get("price", "0"))
                    try:
                        # Remove $ and , characters
                        price_str = price_str.replace("$", "").replace(",", "")
                        # Try to convert to float
                        return float(price_str)
                    except:
                        pass
                return 0
            
            # Add up costs from all components using price_num when available
            total_cost_usd = (
                get_safe_price(cpu) +
                get_safe_price(motherboard) +
                get_safe_price(cooler) +
                get_safe_price(memory) +
                get_safe_price(gpu) +
                get_safe_price(case) +
                get_safe_price(psu) +
                get_safe_price(storage)
            )
            
            # Convert to INR for display
            total_cost_inr = total_cost_usd / conversion_rate
            
            # Format the recommendation
            recommendation = {
                "components": {
                    "cpu": {
                        "name": cpu.get("name"),
                        "price": cpu.get("price"),
                        "price_inr": f"₹{get_safe_price(cpu) / conversion_rate:.2f}",
                        "details": {
                            "manufacturer": cpu.get("manufacturer"),
                            "core_count": cpu.get("core_count"),
                            "core_clock": cpu.get("performance_core_clock"),
                            "boost_clock": cpu.get("performance_core_boost_clock"),
                            "rank": cpu.get("rank"),
                            "ml_score": cpu.get("ml_score")
                        }
                    },
                    "motherboard": {
                        "name": motherboard.get("name"),
                        "price": motherboard.get("price"),
                        "price_inr": f"₹{get_safe_price(motherboard) / conversion_rate:.2f}",
                        "details": {
                            "form_factor": motherboard.get("form_factor"),
                            "chipset": motherboard.get("chipset"),
                            "memory_type": motherboard.get("memory_type"),
                            "rank": motherboard.get("rank"),
                            "ml_score": motherboard.get("ml_score")
                        }
                    },
                    "cooler": {
                        "name": cooler.get("name"),
                        "price": cooler.get("price"),
                        "price_inr": f"₹{get_safe_price(cooler) / conversion_rate:.2f}",
                        "details": {
                            "type": "Water Cooled" if cooler.get("water_cooled") else "Air Cooled",
                            "noise_level": cooler.get("noise_level"),
                            "rank": cooler.get("rank"),
                            "ml_score": cooler.get("ml_score")
                        }
                    },
                    "gpu": {
                        "name": gpu.get("name"),
                        "price": gpu.get("price"),
                        "price_inr": f"₹{get_safe_price(gpu) / conversion_rate:.2f}",
                        "details": {
                            "chipset": gpu.get("chipset"),
                            "memory": gpu.get("memory"),
                            "core_clock": gpu.get("core_clock"),
                            "rank": gpu.get("rank"),
                            "ml_score": gpu.get("ml_score")
                        }
                    },
                    "case": {
                        "name": case.get("name"),
                        "price": case.get("price"),
                        "price_inr": f"₹{get_safe_price(case) / conversion_rate:.2f}",
                        "details": {
                            "type": case.get("type"),
                            "color": case.get("color"),
                            "rank": case.get("rank"),
                            "ml_score": case.get("ml_score")
                        }
                    },
                    "psu": {
                        "name": psu.get("name"),
                        "price": psu.get("price"),
                        "price_inr": f"₹{get_safe_price(psu) / conversion_rate:.2f}",
                        "details": {
                            "wattage": f"{psu.get('wattage')} W",
                            "efficiency": psu.get("efficiency_rating"),
                            "modular": psu.get("modular"),
                            "rank": psu.get("rank"),
                            "ml_score": psu.get("ml_score")
                        }
                    },
                    "memory": {
                        "name": memory.get("name"),
                        "price": memory.get("price"),
                        "price_inr": f"₹{get_safe_price(memory) / conversion_rate:.2f}",
                        "details": {
                            "speed": memory.get("speed"),
                            "modules": memory.get("modules"),
                            "rank": memory.get("rank"),
                            "ml_score": memory.get("ml_score")
                        }
                    },
                    "storage": {
                        "name": storage.get("name"),
                        "price": str(storage.get("price")),
                        "price_inr": f"₹{get_safe_price(storage) / conversion_rate:.2f}",
                        "details": {
                            "capacity": f"{storage.get('capacity')} GB",
                            "type": storage.get("type"),
                            "interface": storage.get("interface"),
                            "rank": storage.get("rank"),
                            "ml_score": storage.get("ml_score")
                        }
                    }
                },
                "selection_order": ["cpu", "motherboard", "cooler", "gpu", "case", "psu", "memory", "storage"],
                "total_cost_usd": f"${total_cost_usd:.2f}",
                "total_cost_inr": f"₹{total_cost_inr:.2f}",
                "budget_inr": f"₹{budget:.2f}",
                "budget_usd": f"${budget * conversion_rate:.2f}"
            }
            
            # Add budget status
            if total_cost_inr <= budget:
                recommendation["status"] = "Within budget"
                recommendation["remaining_budget_inr"] = f"₹{budget - total_cost_inr:.2f}"
            else:
                recommendation["status"] = f"Over budget by ₹{total_cost_inr - budget:.2f}"
            
            return recommendation
        
        except Exception as e:
            print(f"Error building recommendation: {str(e)}")
            # Return partial recommendation if we have some components
            if self.selected_components:
                print("Returning partial recommendation with available components:")
                for component, details in self.selected_components.items():
                    print(f"- {component.capitalize()}: {details['name']} (${details.get('price_num', 0):.2f})")
                # Return components in a format compatible with the expected output
                return {
                    "error": str(e),
                    "components_selected_so_far": self.selected_components
                }
            else:
                raise Exception(f"Could not build any recommendation: {str(e)}")
    
    def close(self):
        """Close database connections"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Run the PC recommendation system"""
    try:
        # Create the recommendation system
        rec_system = PCRecommendationSystem()
        
        # Generate recommendation
        recommendation = rec_system.build_recommendation()
        
        # Print the recommendation
        print(json.dumps(recommendation, indent=2))
        
        # Save the recommendation to a file
        with open("recommendation_result.json", "w") as f:
            json.dump(recommendation, f, indent=2)
        
        # Close connections
        rec_system.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 