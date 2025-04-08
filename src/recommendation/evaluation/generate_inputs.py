# filename: generate_inputs.py
import json
import random

def generate_input_data(output_file="input_data.json"):
    """Generates varied input preference files for budget ranges."""
    all_inputs = []
    budgets = range(80000, 300001, 10000) # 80k to 300k INR

    for i, budget in enumerate(budgets):
        prefs = {
            "budget": budget,
            "useCases": {
                "gaming": {"needed": False, "intensity": 0},
                "videoEditing": {"needed": False, "intensity": 0},
                "rendering3D": {"needed": False, "intensity": 0},
                "programming": {"needed": False, "intensity": 0},
                "officeWork": {"needed": False, "intensity": 0},
                "streaming": {"needed": False, "intensity": 0}
            },
            "technicalPreferences": {
                "cpuPlatform": random.choice(["AMD", "Intel", "Any"]),
                "gpuPlatform": random.choice(["NVIDIA", "AMD", "Any"]),
                "marketSegment": "Consumer",
                "formFactor": "Mid tower",
                "rgbImportance": 5,
                "noiseLevel": "Balanced",
                "upgradePathImportance": 5,
                "storage": {
                    "ssdCapacity": "1TB",
                    "hddCapacity": "None"
                },
                "connectivity": {
                    "wifi": True,
                    "bluetooth": False,
                    "usbPorts": "Multiple USB 3.0"
                }
            },
            "performancePriorities": {
                "cpu": 5,
                "gpu": 5,
                "ram": 5,
                "storageSpeed": 5
            }
        }

        # --- Customize based on budget ---
        if budget <= 120000:
            # Low Budget: Value Gaming / Office / Light Programming
            prefs["useCases"]["gaming"]["needed"] = True
            prefs["useCases"]["gaming"]["intensity"] = random.randint(5, 7)
            prefs["useCases"]["officeWork"]["needed"] = True
            prefs["useCases"]["officeWork"]["intensity"] = random.randint(4, 6)
            if random.random() > 0.5:
                 prefs["useCases"]["programming"]["needed"] = True
                 prefs["useCases"]["programming"]["intensity"] = random.randint(3, 5)

            prefs["technicalPreferences"]["rgbImportance"] = random.randint(2, 5)
            prefs["technicalPreferences"]["upgradePathImportance"] = random.randint(4, 6)
            prefs["technicalPreferences"]["storage"]["ssdCapacity"] = random.choice(["500GB", "1TB"])
            prefs["performancePriorities"]["gpu"] = random.randint(6, 8)
            prefs["performancePriorities"]["cpu"] = random.randint(5, 7)

        elif budget <= 200000:
            # Mid Budget: Good Gaming / Productivity / Streaming
            prefs["useCases"]["gaming"]["needed"] = True
            prefs["useCases"]["gaming"]["intensity"] = random.randint(7, 9)
            if random.random() > 0.3:
                prefs["useCases"]["programming"]["needed"] = True
                prefs["useCases"]["programming"]["intensity"] = random.randint(5, 7)
            if random.random() > 0.6:
                prefs["useCases"]["videoEditing"]["needed"] = True
                prefs["useCases"]["videoEditing"]["intensity"] = random.randint(4, 6)
            if random.random() > 0.5:
                prefs["useCases"]["streaming"]["needed"] = True
                prefs["useCases"]["streaming"]["intensity"] = random.randint(6, 8)

            prefs["technicalPreferences"]["rgbImportance"] = random.randint(4, 7)
            prefs["technicalPreferences"]["upgradePathImportance"] = random.randint(6, 8)
            prefs["technicalPreferences"]["storage"]["ssdCapacity"] = random.choice(["1TB", "2TB"])
            if random.random() > 0.5:
                 prefs["technicalPreferences"]["storage"]["hddCapacity"] = random.choice(["1TB", "2TB"])
            prefs["technicalPreferences"]["connectivity"]["usbPorts"] = "Multiple USB 3.0 and USB-C"
            prefs["performancePriorities"]["gpu"] = random.randint(7, 9)
            prefs["performancePriorities"]["cpu"] = random.randint(6, 8)
            prefs["performancePriorities"]["ram"] = random.randint(6, 7)
            prefs["performancePriorities"]["storageSpeed"] = random.randint(5, 7)

        else:
            # High Budget: High-End Gaming / Heavy Creative / Workstation
            if random.random() > 0.4: # More chance of workstation focus
                 prefs["technicalPreferences"]["marketSegment"] = random.choice(["Consumer", "Workstation"])
                 prefs["useCases"]["videoEditing"]["needed"] = True
                 prefs["useCases"]["videoEditing"]["intensity"] = random.randint(7, 9)
                 prefs["useCases"]["rendering3D"]["needed"] = True
                 prefs["useCases"]["rendering3D"]["intensity"] = random.randint(7, 9)
                 prefs["useCases"]["programming"]["needed"] = True
                 prefs["useCases"]["programming"]["intensity"] = random.randint(7, 9)
                 prefs["performancePriorities"]["cpu"] = random.randint(8, 10)
                 prefs["performancePriorities"]["ram"] = random.randint(8, 10)
                 prefs["performancePriorities"]["storageSpeed"] = random.randint(7, 9)
                 prefs["performancePriorities"]["gpu"] = random.randint(6, 8) # GPU less dominant in pure workstation
            else: # High end gaming focus
                 prefs["useCases"]["gaming"]["needed"] = True
                 prefs["useCases"]["gaming"]["intensity"] = random.randint(9, 10)
                 prefs["useCases"]["streaming"]["needed"] = True
                 prefs["useCases"]["streaming"]["intensity"] = random.randint(8, 9)
                 prefs["performancePriorities"]["gpu"] = random.randint(9, 10)
                 prefs["performancePriorities"]["cpu"] = random.randint(8, 9)
                 prefs["performancePriorities"]["ram"] = random.randint(7, 8)

            prefs["technicalPreferences"]["formFactor"] = random.choice(["Mid tower", "Full tower"])
            prefs["technicalPreferences"]["rgbImportance"] = random.randint(5, 9)
            prefs["technicalPreferences"]["noiseLevel"] = random.choice(["Balanced", "Quiet", "Performance"])
            prefs["technicalPreferences"]["upgradePathImportance"] = random.randint(7, 9)
            prefs["technicalPreferences"]["storage"]["ssdCapacity"] = random.choice(["2TB", "4TB"])
            if random.random() > 0.3:
                prefs["technicalPreferences"]["storage"]["hddCapacity"] = random.choice(["2TB", "4TB", "None"]) # High end might skip HDD
            prefs["technicalPreferences"]["connectivity"]["wifi"] = True
            prefs["technicalPreferences"]["connectivity"]["bluetooth"] = True
            prefs["technicalPreferences"]["connectivity"]["usbPorts"] = "Multiple USB 3.2 and USB-C"

        # Clean up 'Any' preference
        if prefs["technicalPreferences"]["cpuPlatform"] == "Any":
             prefs["technicalPreferences"]["cpuPlatform"] = None
        if prefs["technicalPreferences"]["gpuPlatform"] == "Any":
             prefs["technicalPreferences"]["gpuPlatform"] = None

        all_inputs.append(prefs)

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(all_inputs, f, indent=2)

    print(f"Generated {len(all_inputs)} input configurations in {output_file}")

if __name__ == "__main__":
    generate_input_data()