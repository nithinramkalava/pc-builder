# filename: recommendation_system.py
import json
import os
import pandas as pd
import numpy as np
from data_connection import get_sqlalchemy_engine, connect_to_db
import traceback # Added for detailed error logging
import logging # Use logging
import argparse # For command-line arguments

# Assuming logging is configured elsewhere (like in run_evaluation.py)
# If running this file directly, uncomment the next few lines:
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PCRecommendationSystem:
    # Add flags for evaluation modes
    def __init__(self, input_file=r"C:\Users\voltX\OneDrive\Desktop\pc-builder\src\recommendation\input.json",
                 use_ml_ranking=True, use_dynamic_budget=True):
        """Initialize the recommendation system with user preferences and evaluation flags"""
        self.use_ml_ranking = use_ml_ranking
        self.use_dynamic_budget = use_dynamic_budget
        logging.info(f"Initializing RecommendationSystem with ml_ranking={self.use_ml_ranking}, dynamic_budget={self.use_dynamic_budget}")

        # Load user preferences
        self.user_prefs = self._load_preferences(input_file)

        # Connect to database
        self.engine = get_sqlalchemy_engine()
        self.conn = connect_to_db()
        # Ensure autocommit is OFF for potentially rolling back during build process if needed
        self.conn.autocommit = False
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

        # Budget allocation percentages (STATIC default values)
        self.default_budget_allocation = {
            "cpu": 0.20,
            "motherboard": 0.16,
            "cooler": 0.05,
            "memory": 0.12,
            "gpu": 0.28,
            "case": 0.07,
            "psu": 0.06,
            "storage": 0.06
        }
        # Initialize budget allocation with defaults
        self.budget_allocation = self.default_budget_allocation.copy()

        # Currency conversion rate: INR to USD (approximate, update as needed)
        self.inr_to_usd = 0.012  # 1 INR = 0.012 USD

        # Adjust budget allocations based on user preferences IF dynamic budget is enabled
        if self.use_dynamic_budget:
            self._adjust_budget_allocation()
        else:
            logging.info("Dynamic budget allocation is OFF. Using static defaults.")

    def _load_preferences(self, input_file):
        """Load user preferences from JSON file"""
        try:
            with open(input_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Input file not found at {input_file}")
            raise
        except json.JSONDecodeError:
            logging.error(f"Could not decode JSON from {input_file}")
            raise


    def _adjust_budget_allocation(self):
        """Adjust budget allocation based on use cases and performance priorities"""
        logging.debug("Adjusting budget allocation dynamically.")
        self.budget_allocation = self.default_budget_allocation.copy()
        use_cases = self.user_prefs["useCases"]
        perf_priorities = self.user_prefs["performancePriorities"]

        # --- Adjustments Logic ---
        if use_cases.get("gaming", {}).get("needed") and use_cases["gaming"]["intensity"] > 5:
            self.budget_allocation["gpu"] += 0.05
            self.budget_allocation["cpu"] -= 0.02
            self.budget_allocation["storage"] -= 0.01
            self.budget_allocation["case"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.01

        if (use_cases.get("videoEditing", {}).get("needed") and use_cases["videoEditing"]["intensity"] > 5) or \
           (use_cases.get("rendering3D", {}).get("needed") and use_cases["rendering3D"]["intensity"] > 5):
            self.budget_allocation["cpu"] += 0.05
            self.budget_allocation["memory"] += 0.03
            self.budget_allocation["gpu"] -= 0.03
            self.budget_allocation["case"] -= 0.02
            self.budget_allocation["psu"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.02

        if use_cases.get("programming", {}).get("needed") and use_cases["programming"]["intensity"] > 5:
            self.budget_allocation["cpu"] += 0.03
            self.budget_allocation["memory"] += 0.02
            self.budget_allocation["gpu"] -= 0.03
            self.budget_allocation["case"] -= 0.01
            self.budget_allocation["motherboard"] -= 0.01

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
        # --- End Adjustments ---

        # --- Normalization ---
        total = sum(self.budget_allocation.values())
        if total <= 0:
            logging.warning("Budget allocations summed to zero or less. Resetting to defaults.")
            self.budget_allocation = self.default_budget_allocation.copy()
            total = 1.0
        for key in self.budget_allocation:
            self.budget_allocation[key] /= total
            if self.budget_allocation[key] < 0:
                logging.warning(f"Negative allocation for {key} after normalization. Setting to 0.")
                self.budget_allocation[key] = 0
        final_total = sum(self.budget_allocation.values())
        if final_total > 0 and abs(final_total - 1.0) > 1e-6:
             logging.debug("Re-normalizing after clipping negative allocations.")
             for key in self.budget_allocation:
                 self.budget_allocation[key] /= final_total
        # --- End Normalization ---

    def _get_component_budget(self, component_type):
        """Calculate budget for a specific component in USD"""
        total_budget_inr = self.user_prefs["budget"]
        component_budget_inr = total_budget_inr * self.budget_allocation[component_type]
        component_budget_usd = component_budget_inr * self.inr_to_usd
        return component_budget_usd

    def _get_market_segment(self):
        """Get the preferred market segment from user preferences"""
        return self.user_prefs["technicalPreferences"].get("marketSegment", "Consumer")

    # MODIFIED: Quote "rank" column
    def _get_order_by_clause(self, table_alias):
        """Generate the ORDER BY clause based on the evaluation mode, quoting 'rank'"""
        if self.use_ml_ranking:
            # Use double quotes for the "rank" column name
            return f"""
            ORDER BY
                CASE WHEN {table_alias}."rank" IS NULL THEN 9999 ELSE {table_alias}."rank" END ASC,
                {table_alias}.price_num ASC
            """
        else:
             logging.debug(f"ML Ranking OFF. Ordering by price only for {table_alias}.")
             return f"""
            ORDER BY
                {table_alias}.price_num ASC
            """

    def _get_params(self, params_template, budget_val, segment_val):
        new_params = []
        # Ensure template is iterable (tuple or list)
        template = params_template if isinstance(params_template, (list, tuple)) else (params_template,)
        for p in template:
            if p == -1: # Budget placeholder
                new_params.append(budget_val)
            elif p == 'SEGMENT_PLACEHOLDER' and segment_val is not None: # Segment placeholder
                new_params.append(segment_val)
            else: # Keep other parameters (like IDs) as they are
                new_params.append(p)
        return tuple(new_params)

    def _execute_query_with_fallbacks(self, base_query, cheapest_query, last_resort_query,
                                      base_params_template, cheapest_params_template, last_resort_params,
                                      original_budget, component_type, market_segment=None, brand_filter=""):
        """
        Helper to execute queries with budget and market segment fallbacks.
        Returns (results, description) on success, or (None, None) on failure.
        """
        budget = original_budget
        current_market_segment = market_segment
        results = None
        description = None
        query_description = f"{component_type} ({'Market: '+str(market_segment) if market_segment else ''}{', Brand: '+brand_filter if brand_filter else ''})"

        query_attempts = [
            ("Initial Budget", base_query, base_params_template, budget, current_market_segment),
            ("1.5x Budget", base_query, base_params_template, original_budget * 1.5, current_market_segment),
            ("2.0x Budget", base_query, base_params_template, original_budget * 2.0, current_market_segment),
            ("2.5x Budget", base_query, base_params_template, original_budget * 2.5, current_market_segment),
        ]

        # Add Consumer segment fallback if applicable
        if market_segment == "Workstation":
            query_attempts.append(
                ("Consumer Segment Fallback", base_query, base_params_template, original_budget * 2.5, "Consumer")
            )

        # Add cheapest query (still respecting segment if possible)
        query_attempts.append(
             ("Cheapest in Segment", cheapest_query, cheapest_params_template, None, current_market_segment if market_segment else "Consumer") # Default to Consumer if no segment initially
        )

        # Add absolute last resort
        query_attempts.append(
             ("Absolute Last Resort", last_resort_query, last_resort_params, None, None)
        )


        for attempt_name, query, params_template, budget_val, segment_val in query_attempts:
            try:
                # Special handling for last resort params which might not be a template
                if attempt_name == "Absolute Last Resort":
                     current_params = last_resort_params
                else:
                     current_params = self._get_params(params_template, budget_val, segment_val)

                logging.debug(f"Attempt: {attempt_name} for {query_description}")
                logging.debug(f"Executing Query: {query.strip()} | Params: {current_params}")

                self.cursor.execute(query, current_params)
                results = self.cursor.fetchall()
                if results:
                    description = self.cursor.description # Fetch description immediately
                    logging.debug(f"Success on attempt: {attempt_name}")
                    return results, description # Return successful result and description
                else:
                    logging.debug(f"No results on attempt: {attempt_name}")

            except Exception as e:
                logging.error(f"ERROR during query attempt '{attempt_name}' for {component_type}: {e}")
                # Log the failing query and params for easier debugging
                logging.error(f"Failed Query: {query.strip()} | Params: {current_params}")
                # logging.error(traceback.format_exc()) # Optional full traceback
                # Continue to the next fallback attempt
                continue

        logging.warning(f"All query attempts failed for {component_type}.")
        return None, None # Indicate failure


    def _process_and_store_component(self, results, description, component_type, original_budget):
        """Processes query results, handles pricing, and stores the component."""
        if not results:
            # This check might be redundant if _execute_query_with_fallbacks handles it, but keep for safety
            raise Exception(f"No compatible {component_type} found after all fallbacks (processing stage).")
        if not description:
             raise Exception(f"Missing database cursor description for {component_type} results.")

        try:
            column_names = [desc[0] for desc in description]
            logging.debug(f"{component_type} - Result Columns: {column_names}")
            component_data = dict(zip(column_names, results[0]))
        except IndexError:
             logging.error(f"IndexError processing {component_type}. Results: {results}, Columns: {column_names}")
             raise Exception(f"Error processing results for {component_type} - likely mismatch between columns and data.")


        # --- Price Handling ---
        price_num = component_data.get("price_num")
        if not isinstance(price_num, (int, float)) or price_num <= 0:
            price_str = str(component_data.get("price", "$0.00")).replace("$", "").replace(",", "")
            try:
                component_data["price_num"] = float(price_str) if price_str else 0.0
            except ValueError:
                component_data["price_num"] = 0.0
            logging.debug(f"{component_type} - Parsed/defaulted price_num: {component_data['price_num']:.2f}")
        else:
             logging.debug(f"{component_type} - Using existing price_num: {price_num:.2f}")


        # --- Rank Handling (Add defaults if columns expected but missing) ---
        # Check if rank was expected (i.e., not storage)
        if component_type != "storage":
            rank_key_specific = f"{component_type}_rank"
            if rank_key_specific in component_data:
                component_data["rank"] = component_data.pop(rank_key_specific)
            component_data["rank"] = component_data.get("rank", 9999)
            component_data["ml_score"] = component_data.get("ml_score", 0)
        else: # Add defaults for storage
            component_data["rank"] = 9999
            component_data["ml_score"] = 0

        # --- Over Budget Warning ---
        current_price = component_data.get('price_num', 0)
        if current_price > original_budget:
            logging.warning(f"Selected {component_type} price ${current_price:.2f} exceeds original budget ${original_budget:.2f}")

        # --- Store Component ---
        self.selected_components[component_type] = component_data
        logging.info(f"Selected {component_type.upper()}: {component_data.get('name', 'N/A')} (${component_data.get('price_num', 0):.2f})")
        return component_data


    def select_cpu(self):
        budget = self._get_component_budget("cpu")
        market_segment = self._get_market_segment()
        platform_pref = self.user_prefs["technicalPreferences"].get("cpuPlatform")
        logging.info(f"Starting CPU Selection - Budget: ${budget:.2f}, Segment: {market_segment}, Platform: {platform_pref}")

        platform_filter = ""
        if platform_pref:
            if platform_pref.upper() == "AMD": platform_filter = " AND manufacturer = 'AMD'"
            elif platform_pref.upper() == "INTEL": platform_filter = " AND manufacturer = 'Intel'"

        # Ensure "rank" and ml_score are selected
        base_query = f"""
            SELECT *, "rank", ml_score FROM cpu_specs
            WHERE price_num <= %s AND price_num > 0 AND market_segment = %s {platform_filter}
            {self._get_order_by_clause('cpu_specs')}
            LIMIT 5
        """
        cheapest_query = f"""
            SELECT *, "rank", ml_score FROM cpu_specs
            WHERE price_num > 0 AND market_segment = %s {platform_filter}
            ORDER BY price_num ASC
            LIMIT 1
        """
        last_resort_query = f"""
            SELECT *, "rank", ml_score FROM cpu_specs WHERE price_num > 0 {platform_filter} ORDER BY price_num ASC LIMIT 1
        """
        absolute_last_resort_query = """
             SELECT *, "rank", ml_score FROM cpu_specs WHERE price_num > 0 ORDER BY price_num ASC LIMIT 1
        """

        try:
            results, description = self._execute_query_with_fallbacks(
                base_query=base_query,
                cheapest_query=cheapest_query,
                last_resort_query=last_resort_query,
                base_params_template=(-1, 'SEGMENT_PLACEHOLDER'),
                cheapest_params_template=('SEGMENT_PLACEHOLDER',),
                last_resort_params=(),
                original_budget=budget,
                component_type="CPU",
                market_segment=market_segment,
                brand_filter=platform_filter
            )

            if not results:
                 logging.warning("CPU - Fallback queries failed, trying absolute last resort (any platform)")
                 self.cursor.execute(absolute_last_resort_query)
                 results = self.cursor.fetchall()
                 description = self.cursor.description

            return self._process_and_store_component(results, description, "cpu", budget)

        except Exception as e:
            logging.error(f"Error selecting CPU: {str(e)}")
            raise # Re-raise critical error


    def select_motherboard(self):
        if "cpu" not in self.selected_components:
            raise Exception("CPU must be selected before choosing a motherboard")

        budget = self._get_component_budget("motherboard")
        cpu_id = self.selected_components["cpu"]["id"]
        logging.info(f"Starting Motherboard Selection - Budget: ${budget:.2f}, CPU ID: {cpu_id}")

        # Compatibility check added
        try:
             check_query = "SELECT COUNT(*) FROM get_compatible_motherboards(%s)"
             self.cursor.execute(check_query, (cpu_id,))
             count = self.cursor.fetchone()[0]
             logging.info(f"Motherboard - Found {count} compatible parts via function.")
             if count == 0:
                 raise Exception(f"No compatible motherboards found via function for CPU ID {cpu_id}")
        except Exception as check_err:
             logging.error(f"Motherboard - Error checking compatibility: {check_err}. Trying last resort query directly.")
             # If check fails, only the last resort query makes sense
             last_resort_query = """
                  SELECT *, "rank", ml_score FROM motherboard_specs WHERE price_num > 0 ORDER BY price_num ASC LIMIT 1
             """
             try:
                  self.cursor.execute(last_resort_query)
                  results = self.cursor.fetchall()
                  description = self.cursor.description
                  if not results: raise Exception("No motherboards found even in last resort.")
                  return self._process_and_store_component(results, description, "motherboard", budget)
             except Exception as lr_err:
                  logging.error(f"Motherboard - Last resort query failed: {lr_err}")
                  raise Exception(f"No compatible motherboard found for CPU id={cpu_id} (check/last resort failed)")


        # Proceed if compatibility check passed
        base_query = f"""
            SELECT c.*, m."rank", m.ml_score, m.price_num
            FROM get_compatible_motherboards(%s) c
            LEFT JOIN motherboard_specs m ON c.id = m.id
            WHERE m.price_num <= %s AND m.price_num > 0
            {self._get_order_by_clause('m')}
            LIMIT 5
        """
        cheapest_query = """
             SELECT c.*, m."rank", m.ml_score, m.price_num
             FROM get_compatible_motherboards(%s) c
             LEFT JOIN motherboard_specs m ON c.id = m.id
             WHERE m.price_num > 0
             ORDER BY m.price_num ASC
             LIMIT 1
        """
        last_resort_query = """
             SELECT *, "rank", ml_score FROM motherboard_specs WHERE price_num > 0 ORDER BY price_num ASC LIMIT 1
        """

        try:
            results, description = self._execute_query_with_fallbacks(
                base_query=base_query,
                cheapest_query=cheapest_query,
                last_resort_query=last_resort_query,
                base_params_template=(cpu_id, -1),
                cheapest_params_template=(cpu_id,),
                last_resort_params=(),
                original_budget=budget,
                component_type="Motherboard"
            )
            return self._process_and_store_component(results, description, "motherboard", budget)

        except Exception as e:
            logging.error(f"Error selecting motherboard: {str(e)}")
            raise # Re-raise critical error


    def select_cooler(self):
        if "cpu" not in self.selected_components:
            raise Exception("CPU must be selected before choosing a CPU cooler")

        budget = self._get_component_budget("cooler")
        cpu_id = self.selected_components["cpu"]["id"]
        logging.info(f"Starting Cooler Selection - Budget: ${budget:.2f}, CPU ID: {cpu_id}")

        try:
             check_query = "SELECT COUNT(*) FROM get_compatible_cpu_coolers(%s)"
             self.cursor.execute(check_query, (cpu_id,))
             count = self.cursor.fetchone()[0]
             logging.info(f"Cooler - Found {count} compatible parts via function.")
             # Don't raise error if count is 0, handle with stock cooler logic later
        except Exception as check_err:
             logging.warning(f"Cooler - Error checking compatibility: {check_err}. Will attempt queries anyway.")


        base_query = f"""
            SELECT c.*, cs."rank", cs.ml_score, cs.price_num
            FROM get_compatible_cpu_coolers(%s) c
            LEFT JOIN cooler_specs cs ON c.id = cs.id
            WHERE cs.price_num <= %s AND cs.price_num > 0
            {self._get_order_by_clause('cs')}
            LIMIT 5
        """
        cheapest_query = """
            SELECT c.*, cs."rank", cs.ml_score, cs.price_num
            FROM get_compatible_cpu_coolers(%s) c
            LEFT JOIN cooler_specs cs ON c.id = cs.id
            WHERE cs.price_num > 0
            ORDER BY cs.price_num ASC
            LIMIT 1
        """
        last_resort_query = """
             SELECT *, "rank", ml_score FROM cooler_specs WHERE price_num > 0 ORDER BY price_num ASC LIMIT 1
        """

        try:
            results, description = self._execute_query_with_fallbacks(
                base_query=base_query,
                cheapest_query=cheapest_query,
                last_resort_query=last_resort_query,
                base_params_template=(cpu_id, -1),
                cheapest_params_template=(cpu_id,),
                last_resort_params=(),
                original_budget=budget,
                component_type="Cooler"
            )

            if not results:
                 cpu_name = self.selected_components["cpu"].get("name", "").lower()
                 is_stock_possible = ("ryzen 5" in cpu_name or "ryzen 3" in cpu_name or
                                     ("core i5" in cpu_name and "k" not in cpu_name) or "core i3" in cpu_name or
                                     "pentium" in cpu_name or "athlon" in cpu_name)

                 if is_stock_possible:
                     logging.warning("No specific compatible cooler found, assuming stock cooler is sufficient/used.")
                     cooler = {"id": None, "name": "Stock Cooler (Assumed)", "price": "$0.00", "price_num": 0.0, "rank": 9999, "ml_score": 0}
                     self.selected_components["cooler"] = cooler
                     return cooler
                 else:
                     logging.error(f"No compatible CPU cooler found for CPU id={cpu_id}, and stock cooler unlikely.")
                     # Allow build to continue but log the issue
                     # Return a placeholder to indicate failure but allow process to potentially finish
                     cooler = {"id": None, "name": "ERROR - No Cooler Found", "price": "$0.00", "price_num": 0.0, "rank": 9999, "ml_score": 0}
                     self.selected_components["cooler"] = cooler
                     # Raise an exception that can be caught later if needed, or just return None/placeholder
                     raise Exception("Failed to select suitable Cooler") # Raise to signify partial failure

            return self._process_and_store_component(results, description, "cooler", budget)

        except Exception as e:
            # Handle case where stock cooler assumption was made but error still occurred
             logging.error(f"Error selecting CPU cooler: {str(e)}")
             raise # Re-raise error


    def select_memory(self):
        if "motherboard" not in self.selected_components or "cpu" not in self.selected_components:
            raise Exception("Motherboard and CPU must be selected before choosing memory")

        budget = self._get_component_budget("memory")
        motherboard_id = self.selected_components["motherboard"]["id"]
        cpu_id = self.selected_components["cpu"]["id"]
        logging.info(f"Starting Memory Selection - Budget: ${budget:.2f}, Mobo ID: {motherboard_id}, CPU ID: {cpu_id}")

        try:
             check_query = "SELECT COUNT(*) FROM get_compatible_ram(%s, %s)"
             self.cursor.execute(check_query, (motherboard_id, cpu_id))
             count = self.cursor.fetchone()[0]
             logging.info(f"Memory - Found {count} compatible parts via function.")
             if count == 0:
                  logging.warning("Memory - Compatibility function returned 0 results. Will try last resort.")
        except Exception as check_err:
             logging.warning(f"Memory - Error checking compatibility: {check_err}. Will try queries anyway.")


        base_query = f"""
            SELECT r.*, m."rank", m.ml_score, m.price_num
            FROM get_compatible_ram(%s, %s) r
            LEFT JOIN memory_specs m ON r.id = m.id
            WHERE m.price_num <= %s AND m.price_num > 0
            {self._get_order_by_clause('m')}
            LIMIT 5
        """
        cheapest_query = """
            SELECT r.*, m."rank", m.ml_score, m.price_num
            FROM get_compatible_ram(%s, %s) r
            LEFT JOIN memory_specs m ON r.id = m.id
            WHERE m.price_num > 0
            ORDER BY m.price_num ASC
            LIMIT 1
        """
        mobo_mem_type = self.selected_components["motherboard"].get("memory_type")
        type_filter = f"AND type = '{mobo_mem_type}'" if mobo_mem_type else ""
        last_resort_query = f"""
            SELECT *, "rank", ml_score FROM memory_specs
            WHERE price_num > 0 {type_filter}
            ORDER BY price_num ASC LIMIT 1
        """

        try:
            results, description = self._execute_query_with_fallbacks(
                base_query=base_query,
                cheapest_query=cheapest_query,
                last_resort_query=last_resort_query,
                base_params_template=(motherboard_id, cpu_id, -1),
                cheapest_params_template=(motherboard_id, cpu_id),
                last_resort_params=(),
                original_budget=budget,
                component_type="Memory"
            )
            return self._process_and_store_component(results, description, "memory", budget)

        except Exception as e:
            logging.error(f"Error selecting memory: {str(e)}")
            raise # Re-raise error

    def select_gpu(self):
        if "motherboard" not in self.selected_components:
            raise Exception("Motherboard must be selected before choosing a GPU")

        budget = self._get_component_budget("gpu")
        motherboard_id = self.selected_components["motherboard"]["id"]
        market_segment = self._get_market_segment()
        platform_pref = self.user_prefs["technicalPreferences"].get("gpuPlatform")
        logging.info(f"Starting GPU Selection - Budget: ${budget:.2f}, Mobo ID: {motherboard_id}, Segment: {market_segment}, Platform: {platform_pref}")

        brand_filter = ""
        if platform_pref:
            if platform_pref.upper() == "NVIDIA": brand_filter = " AND g.brand = 'NVIDIA'"
            elif platform_pref.upper() == "AMD": brand_filter = " AND g.brand = 'AMD'"
            elif platform_pref.upper() == "INTEL": brand_filter = " AND g.brand = 'Intel'"
            logging.debug(f"GPU Brand filter: {brand_filter}")

        # --- Integrated Graphics Check ---
        cpu_name = self.selected_components["cpu"].get("name", "").lower()
        cpu_manu = self.selected_components["cpu"].get("manufacturer", "").lower()
        has_igpu = ("g" in cpu_name.split('-')[-1] or "apu" in cpu_name or
                   (cpu_manu == "intel" and not any(flag in cpu_name.split('-')[-1] for flag in ["f", "kf", "ks"])) or
                    self.selected_components["cpu"].get("integrated_graphics") not in [None, 'NaN', 'No', False])

        # --- Compatibility Check ---
        compat_count = 0
        try:
            compat_check_query = "SELECT COUNT(*) FROM get_compatible_video_cards(%s)"
            self.cursor.execute(compat_check_query, (motherboard_id,))
            compat_count = self.cursor.fetchone()[0]
            logging.info(f"GPU - Found {compat_count} compatible parts via function.")
            if compat_count == 0 and not has_igpu:
                 # Don't raise yet, let fallbacks try direct query
                 logging.warning(f"GPU - Compatibility function returned 0 results for Mobo ID {motherboard_id}, and no iGPU detected. Will proceed to fallbacks.")
            elif compat_count == 0 and has_igpu:
                 logging.warning("GPU - Compatibility function returned 0 results, but CPU has iGPU. Assuming integrated graphics.")
                 gpu = {"id": None, "name": "Integrated Graphics (Assumed)", "price": "$0.00", "price_num": 0.0, "rank": 9999, "ml_score": 0, "brand": "Integrated", "market_segment": "Integrated"}
                 self.selected_components["gpu"] = gpu
                 return gpu
        except Exception as func_err:
             logging.warning(f"GPU - Error executing get_compatible_video_cards({motherboard_id}): {func_err}. Will attempt direct queries.")
             compat_count = -1 # Indicate function failure

        # --- Define Queries ---
        # Base/Cheapest use function if it worked (compat_count >= 0)
        if compat_count >= 0:
            base_query_template = f"""
                SELECT v.*, g.rank as gpu_rank, g.ml_score, g.price_num, g.market_segment, g.brand
                FROM get_compatible_video_cards(%s) v
                LEFT JOIN gpu_specs g ON v.id = g.id
                WHERE g.price_num <= %s AND g.price_num > 0 AND g.market_segment = %s {{brand_filter_placeholder}}
                {self._get_order_by_clause('g')}
                LIMIT 10
            """
            cheapest_query_template = f"""
                 SELECT v.*, g.rank as gpu_rank, g.ml_score, g.price_num, g.market_segment, g.brand
                 FROM get_compatible_video_cards(%s) v
                 LEFT JOIN gpu_specs g ON v.id = g.id
                 WHERE g.price_num > 0 AND g.market_segment = %s {{brand_filter_placeholder}}
                 ORDER BY g.price_num ASC
                 LIMIT 1
            """
            base_params_template = (motherboard_id, -1, 'SEGMENT_PLACEHOLDER')
            cheapest_params_template = (motherboard_id, 'SEGMENT_PLACEHOLDER')
        else: # Function failed or returned 0 - use direct query on gpu_specs
             logging.warning("GPU - Using direct queries on gpu_specs table.")
             base_query_template = f"""
                 SELECT *, "rank" as gpu_rank /* Assuming rank exists on gpu_specs */
                 FROM gpu_specs g
                 WHERE g.price_num <= %s AND g.price_num > 0 AND g.market_segment = %s {{brand_filter_placeholder}}
                 {self._get_order_by_clause('g')}
                 LIMIT 10
             """
             cheapest_query_template = f"""
                  SELECT *, "rank" as gpu_rank
                  FROM gpu_specs g
                  WHERE g.price_num > 0 AND g.market_segment = %s {{brand_filter_placeholder}}
                  ORDER BY g.price_num ASC
                  LIMIT 1
             """
             base_params_template = (-1, 'SEGMENT_PLACEHOLDER')
             cheapest_params_template = ('SEGMENT_PLACEHOLDER',)


        # Last resort query is always direct
        last_resort_query = """
             SELECT *, "rank" as gpu_rank FROM gpu_specs g
             WHERE g.price_num > 0 ORDER BY g.price_num ASC LIMIT 1
        """
        last_resort_params = ()

        try:
            results = None
            description = None
            current_brand_filter_sql = brand_filter # SQL part like " AND g.brand = 'NVIDIA'"

            # --- Try initial budget with brand filter ---
            if current_brand_filter_sql:
                 logging.debug(f"GPU - Trying query with brand filter: {current_brand_filter_sql}")
                 query = base_query_template.format(brand_filter_placeholder=current_brand_filter_sql)
                 current_params = self._get_params(base_params_template, budget, market_segment)
                 self.cursor.execute(query, current_params)
                 results = self.cursor.fetchall()
                 if results: description = self.cursor.description

            # --- Try initial budget without brand filter (if needed) ---
            if not results:
                 if current_brand_filter_sql: logging.debug("GPU - No results with brand filter, trying without.")
                 query = base_query_template.format(brand_filter_placeholder="")
                 current_params = self._get_params(base_params_template, budget, market_segment)
                 self.cursor.execute(query, current_params)
                 results = self.cursor.fetchall()
                 if results: description = self.cursor.description
                 current_brand_filter_sql = "" # Clear for subsequent fallbacks

            # --- Use helper for budget/segment fallbacks ---
            if not results:
                results, description = self._execute_query_with_fallbacks(
                    base_query=base_query_template.format(brand_filter_placeholder=current_brand_filter_sql),
                    cheapest_query=cheapest_query_template.format(brand_filter_placeholder=current_brand_filter_sql),
                    last_resort_query=last_resort_query,
                    base_params_template=base_params_template,
                    cheapest_params_template=cheapest_params_template,
                    last_resort_params=last_resort_params,
                    original_budget=budget, # Pass original budget for fallbacks
                    component_type="GPU",
                    market_segment=market_segment,
                    brand_filter=brand_filter # Original preference for logging
                )

            # --- Final iGPU Check ---
            if not results:
                 if has_igpu:
                     logging.warning("GPU - No dedicated GPU found after all fallbacks. Assuming integrated graphics.")
                     gpu = {"id": None, "name": "Integrated Graphics (Assumed)", "price": "$0.00", "price_num": 0.0, "rank": 9999, "ml_score": 0, "brand": "Integrated", "market_segment": "Integrated"}
                     self.selected_components["gpu"] = gpu
                     return gpu
                 else:
                      raise Exception(f"No compatible GPU found for motherboard id={motherboard_id} after all fallbacks, and no integrated graphics detected.")

            return self._process_and_store_component(results, description, "gpu", budget)

        except Exception as e:
            logging.error(f"Error selecting GPU: {str(e)}")
            raise # Re-raise error


    def select_case(self):
        if "motherboard" not in self.selected_components:
             raise Exception("Motherboard must be selected before choosing a case")

        gpu_id = self.selected_components.get("gpu", {}).get("id")
        motherboard_id = self.selected_components["motherboard"]["id"]
        budget = self._get_component_budget("case")
        logging.info(f"Starting Case Selection - Budget: ${budget:.2f}, Mobo ID: {motherboard_id}, GPU ID: {gpu_id}")

        compat_count = -1
        compat_params = None
        use_direct_query_logic = False

        # --- Define Queries based on GPU presence ---
        if gpu_id is not None:
            try:
                compat_check_query = "SELECT COUNT(*) FROM get_compatible_case(%s, %s)"
                compat_params = (gpu_id, motherboard_id)
                self.cursor.execute(compat_check_query, compat_params)
                compat_count = self.cursor.fetchone()[0]
                logging.info(f"Case - Found {compat_count} compatible parts via function (GPU specific).")
                if compat_count == 0:
                     logging.warning("Case - Compatibility function returned 0 with GPU ID. Will try direct queries.")
                     use_direct_query_logic = True
            except Exception as check_err:
                 logging.warning(f"Case - Error checking compatibility function with GPU: {check_err}. Will try direct queries.")
                 use_direct_query_logic = True

            if not use_direct_query_logic:
                base_query = f"""
                    SELECT c.id, c.name, c.price, c.type, c.color, cs."rank" as case_rank, cs.ml_score, cs.price_num
                    FROM get_compatible_case(%s, %s) c
                    LEFT JOIN case_specs cs ON c.id = cs.id
                    WHERE cs.price_num <= %s AND cs.price_num > 0
                    {self._get_order_by_clause('cs')}
                    LIMIT 1
                """
                cheapest_query = """
                    SELECT c.id, c.name, c.price, c.type, c.color, cs."rank" as case_rank, cs.ml_score, cs.price_num
                    FROM get_compatible_case(%s, %s) c
                    LEFT JOIN case_specs cs ON c.id = cs.id
                    WHERE cs.price_num > 0
                    ORDER BY cs.price_num ASC
                    LIMIT 1
                """
                base_params_template = (gpu_id, motherboard_id, -1)
                cheapest_params_template = (gpu_id, motherboard_id)

        # If no GPU or GPU compat check failed/returned 0
        if gpu_id is None or use_direct_query_logic:
            if not use_direct_query_logic: # Log only if we haven't logged failure already
                logging.info("Case - No dedicated GPU or initial compat check failed. Using motherboard form factor.")
            mobo_form_factor = self.selected_components["motherboard"].get("form_factor", "ATX")
            form_factor_like = f"%{mobo_form_factor}%"
            try:
                 compat_check_query = "SELECT COUNT(*) FROM case_specs WHERE motherboard_form_factor LIKE %s AND price_num > 0"
                 compat_params = (form_factor_like,)
                 self.cursor.execute(compat_check_query, compat_params)
                 compat_count = self.cursor.fetchone()[0]
                 logging.info(f"Case - Found {compat_count} compatible parts via form factor '{mobo_form_factor}'.")
            except Exception as ff_check_err:
                 logging.warning(f"Case - Error checking compatibility by form factor: {ff_check_err}. Will proceed to last resort if needed.")
                 compat_count = -1 # Indicate check failed

            base_query = f"""
                SELECT cs.id, cs.name, cs.price, cs.type, cs.color, cs."rank" as case_rank, cs.ml_score, cs.price_num
                FROM case_specs cs
                WHERE cs.motherboard_form_factor LIKE %s
                  AND cs.price_num <= %s AND cs.price_num > 0
                {self._get_order_by_clause('cs')}
                LIMIT 1
            """
            cheapest_query = """
                 SELECT cs.id, cs.name, cs.price, cs.type, cs.color, cs."rank" as case_rank, cs.ml_score, cs.price_num
                 FROM case_specs cs
                 WHERE cs.motherboard_form_factor LIKE %s
                   AND cs.price_num > 0
                 ORDER BY cs.price_num ASC
                 LIMIT 1
            """
            base_params_template = (form_factor_like, -1)
            cheapest_params_template = (form_factor_like,)

        # Last resort query is always direct, ignoring compatibility checks
        last_resort_query = """
             SELECT cs.id, cs.name, cs.price, cs.type, cs.color, cs."rank", cs.ml_score, cs.price_num
             FROM case_specs cs WHERE cs.price_num > 0 ORDER BY cs.price_num ASC LIMIT 1
        """
        last_resort_params = ()

        try:
             if compat_count == 0:
                 logging.warning("Case - Compatibility check found 0 results. Trying last resort directly.")
                 self.cursor.execute(last_resort_query, last_resort_params)
                 results = self.cursor.fetchall()
                 description = self.cursor.description
             else: # compat_count > 0 or check failed (compat_count == -1)
                 results, description = self._execute_query_with_fallbacks(
                     base_query=base_query,
                     cheapest_query=cheapest_query,
                     last_resort_query=last_resort_query,
                     base_params_template=base_params_template,
                     cheapest_params_template=cheapest_params_template,
                     last_resort_params=last_resort_params,
                     original_budget=budget,
                     component_type="Case"
                 )

             return self._process_and_store_component(results, description, "case", budget)

        except Exception as e:
            logging.error(f"Error selecting case: {str(e)}")
            raise # Re-raise error

    def select_psu(self):
        if "cpu" not in self.selected_components or "case" not in self.selected_components:
            raise Exception("CPU and Case must be selected before choosing a PSU")
        # Handle case where case selection failed/placeholder
        case_id = self.selected_components["case"].get("id")
        if not case_id:
             logging.warning("PSU - Valid Case ID missing. Attempting selection without case compatibility.")
             # Modify queries or use a very broad last resort
             # For now, let's proceed, but get_compatible_psu might fail

        budget = self._get_component_budget("psu")
        original_budget = budget

        # --- Calculate Power Requirement ---
        cpu_tdp, gpu_tdp = 100, 0 # Defaults
        try: # CPU TDP
            cpu_tdp_str = str(self.selected_components["cpu"].get("tdp", "100W"))
            if cpu_tdp_str and cpu_tdp_str not in ['N/A', 'NaN', '']:
                 cpu_tdp = int(''.join(filter(str.isdigit, cpu_tdp_str))) if any(char.isdigit() for char in cpu_tdp_str) else 100
        except Exception as cpu_tdp_err: logging.warning(f"PSU - Could not parse CPU TDP: {cpu_tdp_err}")

        try: # GPU TDP
            if "gpu" in self.selected_components and self.selected_components["gpu"].get("id") is not None:
                gpu_tdp_str = str(self.selected_components["gpu"].get("tdp", "0W"))
                if gpu_tdp_str and gpu_tdp_str not in ['N/A', 'NaN', '']:
                     gpu_tdp = int(''.join(filter(str.isdigit, gpu_tdp_str))) if any(char.isdigit() for char in gpu_tdp_str) else 200 # Assume 200W if dedicated GPU TDP missing
                else: gpu_tdp = 200
            elif "gpu" not in self.selected_components: gpu_tdp = 250 # Estimate higher if GPU selection failed
        except Exception as gpu_tdp_err:
                 logging.warning(f"PSU - Could not parse GPU TDP: {gpu_tdp_err}, using default {gpu_tdp}W.")

        required_power_high = int((cpu_tdp + gpu_tdp + 150) * 1.3)
        required_power_med = int((cpu_tdp + gpu_tdp + 150) * 1.1)
        required_power_low = int(cpu_tdp + gpu_tdp + 100)
        power_levels_to_try = [required_power_high, required_power_med, required_power_low]
        current_power_req = required_power_high # Start high
        logging.info(f"Starting PSU Selection - Budget: ${budget:.2f}, Case ID: {case_id}, Req Power Est: ~{current_power_req}W")

        # --- Check Compatibility & Adjust Power Req ---
        compat_count = 0
        if case_id: # Only check if we have a case ID
             try:
                 check_query = "SELECT COUNT(*) FROM get_compatible_psu(%s, %s)"
                 for power_level in power_levels_to_try:
                     self.cursor.execute(check_query, (power_level, case_id))
                     count = self.cursor.fetchone()[0]
                     if count > 0:
                         current_power_req = power_level
                         compat_count = count
                         logging.info(f"PSU - Found {compat_count} compatible parts via function at {current_power_req}W.")
                         break
                     else:
                         logging.warning(f"PSU - Compatibility function returned 0 for {power_level}W.")
                 if compat_count == 0:
                     logging.warning("PSU - No compatible PSUs found for any calculated power requirement via function. Will try last resort.")
             except Exception as check_err:
                 logging.warning(f"PSU - Error checking compatibility function: {check_err}. Will try last resort.")
                 compat_count = -1 # Indicate function error
        else: # No case_id
             compat_count = -1 # Skip function check

        # --- Define Queries ---
        use_compat_function = (case_id is not None and compat_count > 0)

        if use_compat_function:
            base_query = f"""
                SELECT p.id, p.name, p.price, p.type, p.efficiency_rating, p.wattage, ps."rank" as psu_rank, ps.ml_score, ps.price_num
                FROM get_compatible_psu(%s, %s) p
                LEFT JOIN psu_specs ps ON p.id = ps.id
                WHERE ps.price_num <= %s AND ps.price_num > 0
                {self._get_order_by_clause('ps')}
                LIMIT 1
            """
            cheapest_query = """
                SELECT p.id, p.name, p.price, p.type, p.efficiency_rating, p.wattage, ps."rank" as psu_rank, ps.ml_score, ps.price_num
                FROM get_compatible_psu(%s, %s) p
                LEFT JOIN psu_specs ps ON p.id = ps.id
                WHERE ps.price_num > 0
                ORDER BY ps.price_num ASC
                LIMIT 1
            """
            base_params_template = (current_power_req, case_id, -1)
            cheapest_params_template = (current_power_req, case_id)
        else: # Direct query on psu_specs (no reliable compatibility)
             logging.warning("PSU - Using direct queries on psu_specs (no/failed compatibility check).")
             base_query = f"""
                 SELECT *, "rank" as psu_rank /* Assume rank exists */
                 FROM psu_specs ps
                 WHERE ps.wattage >= %s /* Filter by minimum power */
                   AND ps.price_num <= %s AND ps.price_num > 0
                 {self._get_order_by_clause('ps')}
                 LIMIT 1
             """
             cheapest_query = """
                 SELECT *, "rank" as psu_rank
                 FROM psu_specs ps
                 WHERE ps.wattage >= %s AND ps.price_num > 0
                 ORDER BY ps.price_num ASC
                 LIMIT 1
             """
             base_params_template = (current_power_req, -1) # Use lowest power req for direct query minimum
             cheapest_params_template = (current_power_req,)


        # Last resort: Cheapest PSU above minimum power (ignore case compat)
        last_resort_query = """
             SELECT *, "rank" as psu_rank FROM psu_specs ps
             WHERE ps.wattage >= %s AND ps.price_num > 0
             ORDER BY ps.price_num ASC LIMIT 1
        """
        last_resort_params = (required_power_low,) # Use lowest calculated power

        try:
            results, description = self._execute_query_with_fallbacks(
                base_query=base_query,
                cheapest_query=cheapest_query,
                last_resort_query=last_resort_query,
                base_params_template=base_params_template,
                cheapest_params_template=cheapest_params_template,
                last_resort_params=last_resort_params,
                original_budget=budget,
                component_type="PSU"
            )
            return self._process_and_store_component(results, description, "psu", budget)

        except Exception as e:
            logging.error(f"Error selecting PSU: {str(e)}")
            raise # Re-raise error

    def select_storage(self):
        """Select the best storage device compatible with the motherboard, prioritizing capacity then price."""
        if "motherboard" not in self.selected_components:
            raise Exception("Motherboard must be selected before choosing storage")

        budget = self._get_component_budget("storage")
        original_budget = budget
        motherboard_id = self.selected_components["motherboard"]["id"]
        logging.info(f"Starting Storage Selection - Budget: ${budget:.2f}, Mobo ID: {motherboard_id}")

        use_direct_query = False
        
        # --- Check Compatibility Function ---
        try:
            check_query = "SELECT COUNT(*) FROM get_compatible_ssd(%s)"
            self.cursor.execute(check_query, (motherboard_id,))
            count = self.cursor.fetchone()[0]
            logging.info(f"Storage - Found {count} compatible parts via function.")
            if count == 0:
                 logging.warning("get_compatible_ssd returned 0 results. Trying direct query on ssd_specs.")
                 use_direct_query = True
                 # Verify ssd_specs table isn't empty
                 check_query_direct = "SELECT COUNT(*) FROM ssd_specs WHERE price_num > 0"
                 self.cursor.execute(check_query_direct)
                 if self.cursor.fetchone()[0] == 0:
                     raise Exception("No SSDs found in ssd_specs table.")
        except Exception as check_err:
             logging.warning(f"Storage - Error checking compatibility function ({check_err}). Will use direct query.")
             use_direct_query = True

        # --- Define Order By Logic (Capacity Desc, Price Asc) ---
        # FIXED: Handling numeric capacities properly
        capacity_order_by = """
            ORDER BY
                capacity DESC, 
                price ASC
        """

        # --- Define Queries ---
        # FIXED: Matching the exact columns returned by get_compatible_ssd function
        if not use_direct_query:
            base_query = f"""
                SELECT 
                    s.id, s.name, s.price, s.capacity, s.price_per_gb, 
                    s.type, s.cache, s.form_factor, s.interface
                FROM get_compatible_ssd(%s) s
                WHERE s.price <= %s AND s.price > 0
                {capacity_order_by}
                LIMIT 1
            """
            cheapest_query = """
                SELECT 
                    s.id, s.name, s.price, s.capacity, s.price_per_gb, 
                    s.type, s.cache, s.form_factor, s.interface
                FROM get_compatible_ssd(%s) s
                WHERE s.price > 0
                ORDER BY s.capacity DESC, s.price ASC
                LIMIT 1
            """
        else:
             # Direct queries on ssd_specs
             base_query = f"""
                 SELECT 
                    ss.id, ss.name, ss.price, ss.capacity, ss.price_per_gb, 
                    ss.type, ss.cache, ss.form_factor, ss.interface
                 FROM ssd_specs ss
                 WHERE ss.price_num <= %s AND ss.price_num > 0
                 ORDER BY 
                    CASE
                        WHEN ss.capacity LIKE '%TB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'TB', ''), ' ', '') AS FLOAT) * 1000
                        WHEN ss.capacity LIKE '%GB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'GB', ''), ' ', '') AS FLOAT)
                        ELSE 0
                    END DESC,
                    ss.price_num ASC
                 LIMIT 1
             """
             cheapest_query = """
                 SELECT 
                    ss.id, ss.name, ss.price, ss.capacity, ss.price_per_gb, 
                    ss.type, ss.cache, ss.form_factor, ss.interface
                 FROM ssd_specs ss
                 WHERE ss.price_num > 0
                 ORDER BY 
                    CASE
                        WHEN ss.capacity LIKE '%TB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'TB', ''), ' ', '') AS FLOAT) * 1000
                        WHEN ss.capacity LIKE '%GB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'GB', ''), ' ', '') AS FLOAT)
                        ELSE 0
                    END DESC,
                    ss.price_num ASC
                 LIMIT 1
             """

        # Last resort is always the same: best capacity-to-price ratio overall SSD
        last_resort_query = """
             SELECT 
                ss.id, ss.name, ss.price, ss.capacity, ss.price_per_gb, 
                ss.type, ss.cache, ss.form_factor, ss.interface
             FROM ssd_specs ss 
             WHERE ss.price_num > 0 
             ORDER BY 
                CASE
                    WHEN ss.capacity LIKE '%TB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'TB', ''), ' ', '') AS FLOAT) * 1000
                    WHEN ss.capacity LIKE '%GB' THEN CAST(REPLACE(REPLACE(ss.capacity, 'GB', ''), ' ', '') AS FLOAT)
                    ELSE 0
                END DESC,
                ss.price_num ASC
             LIMIT 1
        """

        try:
            # Progressive budget increment strategy
            current_budget = budget
            max_attempts = 10  # Try up to 10 budget increments
            increment_factor = 0.10  # 10% budget increment each try
            results = None
            description = None
            
            for attempt in range(max_attempts + 1):  # +1 for the initial attempt at original budget
                logging.info(f"Storage - Attempt {attempt}: trying with budget ${current_budget:.2f}")
                
                # Try to find compatible SSD within current budget
                try:
                    if not use_direct_query:
                        # Using compatibility function
                        self.cursor.execute(base_query, (motherboard_id, current_budget))
                    else:
                        # Using direct query
                        self.cursor.execute(base_query, (current_budget,))
                    
                    results = self.cursor.fetchall()
                    if results:
                        description = self.cursor.description
                        logging.info(f"Storage - Found suitable drive within budget on attempt {attempt}")
                        break
                except Exception as query_err:
                    logging.error(f"Storage - Error in query execution: {str(query_err)}")
                    # Continue to next attempt
                
                # If we've tried all increments and still nothing, fallback to cheapest options
                if attempt == max_attempts:
                    logging.warning(f"Storage - No suitable drive found after {max_attempts} budget increments. Trying fallback.")
                    try:
                        # First try the compatible cheapest query
                        if not use_direct_query:
                            self.cursor.execute(cheapest_query, (motherboard_id,))
                        else:
                            self.cursor.execute(cheapest_query)
                            
                        results = self.cursor.fetchall()
                        if results:
                            description = self.cursor.description
                            logging.info(f"Storage - Found drive with cheapest query fallback")
                            break
                            
                        # If that fails, try absolute last resort
                        logging.warning(f"Storage - Cheapest query failed. Trying last resort.")
                        self.cursor.execute(last_resort_query)
                        results = self.cursor.fetchall()
                        description = self.cursor.description
                        
                        if results:
                            logging.info(f"Storage - Found drive with last resort query")
                            break
                        else:
                            raise Exception("No storage device found after all fallback attempts")
                            
                    except Exception as fallback_err:
                        logging.error(f"Storage - Fallback queries failed: {fallback_err}")
                        raise Exception(f"All storage queries failed: {fallback_err}")
                    
                    break
                
                # Increment budget for next attempt
                current_budget = current_budget * (1 + increment_factor)
                logging.info(f"Storage - Increasing budget to ${current_budget:.2f} for attempt {attempt+1}")
            
            if not results:
                raise Exception("No storage device found after all attempts")
                
            # Process the selected component
            # Convert the results to the format expected by _process_and_store_component
            component_data = dict(zip([d[0] for d in description], results[0]))
            
            # Add price_num field if using compatibility function (which returns price as numeric)
            if not use_direct_query:
                component_data['price_num'] = float(component_data.get('price', 0))
                # Ensure price is formatted as string with $ for consistency
                if isinstance(component_data['price'], (int, float)):
                    component_data['price'] = f"${component_data['price']:.2f}"
            
            logging.info(f"Selected storage: {component_data.get('name')} - {component_data.get('capacity')} - ${component_data.get('price_num', 0):.2f}")
            
            # Store in selected_components
            self.selected_components['storage'] = component_data
            return component_data

        except Exception as e:
            logging.error(f"Error selecting storage: {str(e)}", exc_info=True)
            
            # Last attempt - try to get ANY storage device
            try:
                logging.warning("Storage - Attempting emergency last resort query")
                self.cursor.execute("SELECT * FROM ssd_specs WHERE price_num > 0 ORDER BY price_num ASC LIMIT 1")
                results = self.cursor.fetchall()
                description = self.cursor.description
                if results:
                    component_data = dict(zip([d[0] for d in description], results[0]))
                    self.selected_components['storage'] = component_data
                    return component_data
            except Exception as final_err:
                logging.error(f"Storage - Emergency query also failed: {final_err}")
                
            raise # Re-raise original error


    def build_recommendation(self):
        """
        Build a complete PC recommendation based on the budget.
        Returns a dictionary containing the build or error information.
        """
        budget = self.user_prefs['budget']
        conversion_rate = self.inr_to_usd
        logging.info("-" * 20)
        logging.info(f"Building recommendation for budget ₹{budget:.2f} / ${budget * conversion_rate:.2f}")
        logging.info(f"Mode: ML Ranking={self.use_ml_ranking}, Dynamic Budget={self.use_dynamic_budget}")
        for component, percentage in self.budget_allocation.items():
            component_budget = budget * percentage
            logging.info(f"  {component.capitalize()}: {percentage * 100:.1f}% (₹{component_budget:.2f} / ${component_budget * conversion_rate:.2f})")
        logging.info("-" * 20)

        component_order = ["cpu", "motherboard", "cooler", "memory", "gpu", "case", "psu", "storage"]
        errors = {} # Store non-critical errors encountered

        # --- Component Selection Phase ---
        try:
            # Use explicit calls and store results directly
            cpu = self.select_cpu()
            motherboard = self.select_motherboard()
            cooler = self.select_cooler() # Might return placeholder
            memory = self.select_memory()
            gpu = self.select_gpu()    # Might return placeholder
            case = self.select_case()
            psu = self.select_psu()
            storage = self.select_storage()

        except Exception as build_exc:
             logging.error(f"CRITICAL ERROR during build process: {build_exc}", exc_info=True)
             try: self.conn.rollback()
             except Exception as rb_err: logging.error(f"Rollback failed after critical error: {rb_err}")
             return {
                 "error": f"Critical failure during build: {str(build_exc)}",
                 "components_selected_so_far": self.selected_components
             }

        # --- Assemble Final Recommendation ---
        if not self.selected_components:
             return {"error": "Failed to select any components."}

        total_cost_usd = 0
        final_components = {}

        def get_safe_price(component_dict, price_key="price_num"):
             if not component_dict: return 0.0
             price = component_dict.get(price_key)
             if isinstance(price, (int, float)) and price > 0: return float(price)
             price_str = str(component_dict.get("price", "0")).replace("$", "").replace(",", "")
             try: return float(price_str) if price_str else 0.0
             except ValueError: return 0.0

        for comp_type in component_order:
            comp_data = self.selected_components.get(comp_type)
            if comp_data and comp_data.get("id") is not None and "ERROR" not in comp_data.get("name", ""): # Check for actual components, ignore placeholders/errors
                 price_usd = get_safe_price(comp_data)
                 total_cost_usd += price_usd
                 details = { # Auto-populate common/useful fields
                     "manufacturer": comp_data.get("manufacturer"), "chipset": comp_data.get("chipset"),
                     "core_count": comp_data.get("core_count"),
                     "core_clock": comp_data.get("performance_core_clock") or comp_data.get("core_clock"),
                     "boost_clock": comp_data.get("performance_core_boost_clock") or comp_data.get("boost_clock"),
                     "form_factor": comp_data.get("form_factor"), "memory_type": comp_data.get("memory_type"),
                     "type": comp_data.get("type"), "color": comp_data.get("color"),
                     "noise_level": comp_data.get("noise_level"), "memory": comp_data.get("memory"),
                     "modules": comp_data.get("modules"), "speed": comp_data.get("speed"),
                     "capacity": comp_data.get("capacity"), "interface": comp_data.get("interface"),
                     "wattage": comp_data.get("wattage"), "efficiency": comp_data.get("efficiency_rating"),
                     "modular": comp_data.get("modular"), "rank": comp_data.get("rank"),
                     "ml_score": comp_data.get("ml_score")
                 }
                 final_components[comp_type] = {
                     "name": comp_data.get("name"),
                     "price": str(comp_data.get("price", "$0.00")),
                     "price_inr": f"₹{price_usd / conversion_rate:.2f}",
                     "details": {k: v for k, v in details.items() if v is not None and v != 'NaN'} # Clean details
                 }
            elif comp_data: # Log placeholders or errors encountered earlier
                 if "ERROR" in comp_data.get("name", ""):
                      errors[comp_type] = comp_data["name"] # Store the error message
                 elif comp_data.get("id") is None: # Log placeholders like stock cooler/iGPU
                      logging.info(f"Using placeholder for {comp_type}: {comp_data.get('name')}")
                      # Optionally include placeholder in output if desired
                      # final_components[comp_type] = { "name": comp_data.get("name"), ... }


        total_cost_inr = total_cost_usd / conversion_rate

        recommendation = {
            "components": final_components,
            "selection_order": component_order,
            "total_cost_usd": f"${total_cost_usd:.2f}",
            "total_cost_inr": f"₹{total_cost_inr:.2f}",
            "budget_inr": f"₹{budget:.2f}",
            "budget_usd": f"${budget * conversion_rate:.2f}",
            "selection_errors": errors if errors else None # Include errors if any occurred
        }
        if recommendation.get("selection_errors") is None:
             recommendation.pop("selection_errors", None)

        if total_cost_inr <= budget:
            recommendation["status"] = "Within budget"
            recommendation["remaining_budget_inr"] = f"₹{budget - total_cost_inr:.2f}"
        else:
            recommendation["status"] = f"Over budget by ₹{total_cost_inr - budget:.2f}"

        try:
            self.conn.commit()
            logging.debug("Recommendation built successfully. Committed transaction.")
        except Exception as commit_err:
            logging.error(f"Failed to commit transaction: {commit_err}")
            recommendation["commit_error"] = str(commit_err)

        return recommendation


    def close(self):
        """Close database connections"""
        logging.debug("Closing database connection.")
        if self.cursor:
            try: self.cursor.close()
            except: pass
        if self.conn:
            try:
                if not self.conn.closed and not self.conn.autocommit:
                    self.conn.rollback()
                    logging.debug("Rolled back any pending changes on close.")
            except Exception as rb_err:
                 logging.warning(f"Error during rollback on close: {rb_err}")
            try: self.conn.close()
            except: pass
        self.cursor = None
        self.conn = None


# Keep main for direct testing if needed
def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='PC Parts Recommendation System')
    parser.add_argument('--input', type=str, help='Path to input JSON file with user preferences')
    parser.add_argument('--output', type=str, help='Path to output JSON file for recommendations')
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    
    try:
        print(f"Using input file: {input_file}")
        
        # Create recommendation system with specified input file
        rec_system = PCRecommendationSystem(input_file=input_file) if input_file else PCRecommendationSystem()
        
        # Generate recommendation
        recommendation = rec_system.build_recommendation()
        
        # Write to output file if specified
        if output_file:
            print(f"Writing recommendation to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(recommendation, f, indent=2)
        else:
            # Print to console if no output file
            print(json.dumps(recommendation, indent=2))
            
        rec_system.close()
        
    except Exception as e:
        error_message = f"Error in recommendation system: {str(e)}"
        print(error_message)
        print(traceback.format_exc())
        
        # If output file is specified, write error to it
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({"error": error_message}, f)
        
        # Exit with error code
        exit(1)

if __name__ == "__main__":
    main()