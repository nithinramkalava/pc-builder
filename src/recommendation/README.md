# PC Parts Recommendation System

This is a PC parts recommendation system that suggests compatible components based on user preferences, budget constraints, and performance requirements.

## Features

- Budget allocation based on user priorities and intended use cases
- Component selection in dependency order to ensure compatibility
- Use of PostgreSQL stored procedures for compatibility checks
- Adjusts recommendations based on technical preferences (AMD/Intel, form factor, etc.)
- Failover mechanisms to find alternatives when ideal components aren't available
- Currency conversion from INR to USD for price comparisons
- Component selection optimized for performance score within budget

## Requirements

- Python 3.7+
- PostgreSQL database with PC components data
- The following Python packages:
  - psycopg2
  - pandas
  - sqlalchemy
  - numpy

## Setup

1. Make sure your PostgreSQL database is running with the proper schema and data
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure the database connection parameters in `data_connection.py` are correct
4. Make sure the compatibility stored procedures from `new_compatibility.sql` are installed in your database

## Usage

1. Create an `input.json` file with user preferences (see example below)
2. Run the recommendation system:
   ```
   python recommendation_system.py
   ```
3. View the recommended components in the generated `recommendation_result.json` file
4. Alternatively, run the test script:
   ```
   python test_recommendation.py
   ```

## Input Format

The input.json file should have the following structure:

```json
{
  "budget": 120000,
  "useCases": {
    "gaming": { "needed": true, "intensity": 8 },
    "videoEditing": { "needed": false, "intensity": 0 },
    "rendering3D": { "needed": false, "intensity": 0 },
    "programming": { "needed": true, "intensity": 5 },
    "officeWork": { "needed": true, "intensity": 3 },
    "streaming": { "needed": false, "intensity": 0 }
  },
  "technicalPreferences": {
    "cpuPlatform": "AMD",
    "gpuPlatform": "NVIDIA",
    "formFactor": "Mid tower",
    "rgbImportance": 7,
    "noiseLevel": "Balanced",
    "upgradePathImportance": 8,
    "storage": {
      "ssdCapacity": "1TB",
      "hddCapacity": "2TB"
    },
    "connectivity": {
      "wifi": true,
      "bluetooth": true,
      "usbPorts": "Multiple USB 3.0 and USB-C"
    }
  },
  "performancePriorities": {
    "cpu": 7,
    "gpu": 9,
    "ram": 6,
    "storageSpeed": 5
  }
}
```

Note: The budget is in Indian Rupees (INR) and will be automatically converted to USD for database comparisons.

## How It Works

1. The system loads user preferences from the input.json file
2. Based on use cases and performance priorities, it allocates budget percentages to different components
3. Budget amounts are converted from INR to USD for database price comparisons
4. Components are selected in the following order to ensure compatibility:
   - CPU
   - Motherboard (compatible with CPU)
   - CPU Cooler (compatible with CPU socket)
   - Memory (compatible with motherboard and CPU)
   - GPU (compatible with motherboard)
   - Case (compatible with GPU size and motherboard form factor)
   - PSU (compatible with case and estimated power requirements)
   - Storage (compatible with motherboard)
5. Each component is selected based on:
   - Compatibility with previously selected components
   - Technical preferences specified by the user
   - Budget allocated for that component
   - Performance score (highest score first)
6. The final recommendation is output as a JSON file with detailed component information and total cost in both INR and USD

## Component Selection Logic

The system uses dedicated stored procedures in PostgreSQL to ensure compatibility:

- `get_compatible_motherboards(cpu_id)`: Finds motherboards compatible with a CPU
- `get_compatible_cpu_coolers(cpu_id)`: Finds coolers compatible with a CPU socket
- `get_compatible_video_cards(mobo_id)`: Finds GPUs compatible with a motherboard
- `get_compatible_case(gpu_id, mobo_id)`: Finds cases that fit both GPU and motherboard
- `get_compatible_psu(required_wattage, case_id)`: Finds PSUs with sufficient power and compatible with case
- `get_compatible_ram(mobo_id, cpu_id)`: Finds RAM compatible with both motherboard and CPU
- `get_compatible_ssd(mobo_id)`: Finds SSDs compatible with a motherboard

Each selection filters by budget and sorts by performance score to identify the best option.

## Currency Conversion

The system uses an approximate conversion rate (1 INR = 0.012 USD) to translate between currencies. This rate is defined in the `PCRecommendationSystem` class and can be updated as needed. The output includes prices in both currencies for clarity.
