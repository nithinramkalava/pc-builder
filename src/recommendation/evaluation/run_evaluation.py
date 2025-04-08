# filename: run_evaluation.py
import json
import os
import shutil
import traceback
import time
import logging # Use logging module
import sys

# Add the parent directory (src/) to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recommendation_system import PCRecommendationSystem
from recommendation_system import PCRecommendationSystem

# --- Configuration ---
INPUT_DATA_FILE = "input_data.json"
OUTPUT_DIR_BASE = "Evaluation_Results"
TEMP_INPUT_FILE = "temp_current_input.json" # Kept for individual runs
LOG_FILE = os.path.join(OUTPUT_DIR_BASE, "evaluation_run.log") # Central log file

TEST_CONFIGS = {
    "A": {"ml_ranking": True,  "dynamic_budget": True,  "desc": "Full IntelliBuild (ML Rank ON, Dynamic Budget ON)"},
    "B": {"ml_ranking": False, "dynamic_budget": True,  "desc": "No ML Rank (ML Rank OFF, Dynamic Budget ON)"},
    "C": {"ml_ranking": True,  "dynamic_budget": False, "desc": "No Dynamic Budget (ML Rank ON, Dynamic Budget OFF)"}
}
# --- End Configuration ---

# --- Setup Logging ---
def setup_logging():
    # Ensure base directory exists for the log file
    os.makedirs(OUTPUT_DIR_BASE, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w'), # Overwrite log each run
            logging.StreamHandler() # Also print to console
        ]
    )
setup_logging()
# --- End Logging Setup ---


def run_single_test(test_id, config, input_prefs_list, output_dir):
    """Runs recommendations, separating successful and failed builds."""
    successful_builds = {}
    failed_builds_log = [] # List to store detailed failure info
    success_output_file = os.path.join(output_dir, f"builds_{test_id}.json")
    failure_log_file = os.path.join(output_dir, f"failed_builds_{test_id}.json") # Log failures as JSON

    logging.info(f"--- Running Test {test_id}: {config['desc']} ---")
    logging.info(f"Success Output: {success_output_file}")
    logging.info(f"Failure Log: {failure_log_file}")

    for i, prefs in enumerate(input_prefs_list):
        build_id = f"{i+1}{test_id.lower()}"
        logging.info(f"  Processing Build ID: {build_id} (Budget: ₹{prefs.get('budget', 'N/A')})")

        # Write temp input
        try:
            with open(TEMP_INPUT_FILE, 'w') as f_temp:
                json.dump(prefs, f_temp, indent=2)
        except Exception as e:
            logging.error(f"    ERROR (Build {build_id}): Failed to write temporary input file: {e}")
            failure_info = {
                "build_id": build_id,
                "budget": prefs.get('budget'),
                "status": "ERROR",
                "stage": "InputSetup",
                "error_message": f"Failed to write temp input: {e}",
                "traceback": traceback.format_exc()
            }
            failed_builds_log.append(failure_info)
            continue

        rec_system = None
        recommendation = None
        try:
            start_time = time.time()
            rec_system = PCRecommendationSystem(
                input_file=TEMP_INPUT_FILE,
                use_ml_ranking=config["ml_ranking"],
                use_dynamic_budget=config["dynamic_budget"]
            )
            recommendation = rec_system.build_recommendation()
            end_time = time.time()
            duration = end_time - start_time

            # --- Check for errors IN the recommendation result ---
            if recommendation and isinstance(recommendation, dict):
                # Case 1: Critical error during build (returned specific error structure)
                if "error" in recommendation:
                    logging.error(f"    ERROR (Build {build_id}): Critical build failure: {recommendation['error']}")
                    failure_info = {
                        "build_id": build_id,
                        "budget": prefs.get('budget'),
                        "status": "ERROR",
                        "stage": "BuildRecommendation",
                        "error_message": recommendation['error'],
                        "traceback": None, # No exception traceback in this case
                        "components_selected_so_far": recommendation.get("components_selected_so_far", {})
                    }
                    failed_builds_log.append(failure_info)
                # Case 2: Non-critical errors during component selection (selection_errors present)
                elif "selection_errors" in recommendation and recommendation["selection_errors"]:
                    logging.warning(f"    PARTIAL SUCCESS (Build {build_id}): Completed with selection errors: {recommendation['selection_errors']}")
                    # Treat as failure for logging, but save the partial build info
                    failure_info = {
                        "build_id": build_id,
                        "budget": prefs.get('budget'),
                        "status": "PARTIAL_ERROR",
                        "stage": "ComponentSelection",
                        "error_message": "One or more components failed selection.",
                        "selection_errors": recommendation["selection_errors"],
                        "partial_build": recommendation # Log the whole thing
                    }
                    failed_builds_log.append(failure_info)
                     # Optionally, you could also put these in the success file if a partial build is useful
                    # recommendation["build_id"] = build_id
                    # recommendation["test_config"] = { ... }
                    # successful_builds[build_id] = recommendation
                    # logging.info(f"    Build {build_id} partially generated in {duration:.2f}s (logged as failure due to errors).")
                # Case 3: Full Success
                else:
                    recommendation["build_id"] = build_id
                    recommendation["test_config"] = {
                        "test_id": test_id,
                        "ml_ranking": config["ml_ranking"],
                        "dynamic_budget": config["dynamic_budget"]
                    }
                    successful_builds[build_id] = recommendation
                    logging.info(f"    Build {build_id} generated successfully in {duration:.2f}s.")
            else:
                 # Should not happen if build_recommendation always returns a dict
                 logging.error(f"    ERROR (Build {build_id}): Unexpected result from build_recommendation: {recommendation}")
                 failure_info = { ... } # Log as failure
                 failed_builds_log.append(failure_info)

        except Exception as e:
            # Catch exceptions raised *during* instantiation or build_recommendation call
            logging.error(f"    ERROR (Build {build_id}): Exception during processing: {str(e)}")
            failure_info = {
                "build_id": build_id,
                "budget": prefs.get('budget'),
                "status": "ERROR",
                "stage": "Instantiation or Build",
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "components_selected_so_far": rec_system.selected_components if rec_system else {}
            }
            failed_builds_log.append(failure_info)
        finally:
            if rec_system:
                try: rec_system.close()
                except Exception as close_err: logging.warning(f"    WARN (Build {build_id}): Error closing DB connection: {close_err}")
            if os.path.exists(TEMP_INPUT_FILE):
                try: os.remove(TEMP_INPUT_FILE)
                except Exception as rm_err: logging.warning(f"    WARN: Could not remove temporary file {TEMP_INPUT_FILE}: {rm_err}")

    # --- Save Successful Builds ---
    if successful_builds:
        try:
            with open(success_output_file, 'w') as f_out:
                json.dump(successful_builds, f_out, indent=2)
            logging.info(f"--- Test {test_id}: Saved {len(successful_builds)} successful builds to {success_output_file} ---")
        except Exception as e:
            logging.error(f"FATAL ERROR: Could not write success results for Test {test_id} to {success_output_file}: {e}")
    else:
         logging.warning(f"--- Test {test_id}: No successful builds were generated. ---")


    # --- Save Failed Builds Log ---
    if failed_builds_log:
        try:
            with open(failure_log_file, 'w') as f_fail:
                json.dump(failed_builds_log, f_fail, indent=2)
            logging.info(f"--- Test {test_id}: Saved {len(failed_builds_log)} failed build logs to {failure_log_file} ---")
        except Exception as e:
            logging.error(f"FATAL ERROR: Could not write failure log for Test {test_id} to {failure_log_file}: {e}")
    else:
         logging.info(f"--- Test {test_id}: No build failures were logged. ---")


def main():
    logging.info("="*30)
    logging.info("Starting PC Recommendation System Evaluation")
    logging.info("="*30)

    # 1. Load Input Data
    if not os.path.exists(INPUT_DATA_FILE):
        logging.error(f"Input data file '{INPUT_DATA_FILE}' not found. Run generate_inputs.py.")
        return
    try:
        with open(INPUT_DATA_FILE, 'r') as f:
            input_preferences = json.load(f)
        logging.info(f"Loaded {len(input_preferences)} input preferences from {INPUT_DATA_FILE}")
    except Exception as e:
        logging.error(f"Failed to load or parse {INPUT_DATA_FILE}: {e}")
        return

    # 2. Setup Output Directories
    if os.path.exists(OUTPUT_DIR_BASE):
        logging.warning(f"Output directory '{OUTPUT_DIR_BASE}' already exists. Removing old results.")
        try:
            shutil.rmtree(OUTPUT_DIR_BASE)
        except Exception as e:
            logging.error(f"Could not remove old output directory '{OUTPUT_DIR_BASE}': {e}")
            # Attempt to continue, maybe just subdirs failed
    try:
        os.makedirs(OUTPUT_DIR_BASE, exist_ok=True) # Base dir for log file
        for test_id in TEST_CONFIGS:
            test_dir = os.path.join(OUTPUT_DIR_BASE, f"Test_{test_id}")
            os.makedirs(test_dir, exist_ok=True)
            logging.info(f"Ensured output directory exists: {test_dir}")
    except Exception as e:
        logging.error(f"Could not create output directories under {OUTPUT_DIR_BASE}: {e}")
        return

    # --- Re-Setup logging after directory creation/clearing ---
    setup_logging()
    logging.info("Log file setup complete.")
    # ---

    # 3. Run Tests
    total_start_time = time.time()
    for test_id, config in TEST_CONFIGS.items():
        output_dir = os.path.join(OUTPUT_DIR_BASE, f"Test_{test_id}")
        run_single_test(test_id, config, input_preferences, output_dir)

    total_end_time = time.time()
    logging.info("--- Evaluation Complete ---")
    logging.info(f"Total execution time: {total_end_time - total_start_time:.2f} seconds.")
    logging.info(f"Results saved in: {OUTPUT_DIR_BASE}")
    logging.info(f"Overall log saved in: {LOG_FILE}")

if __name__ == "__main__":
    main()