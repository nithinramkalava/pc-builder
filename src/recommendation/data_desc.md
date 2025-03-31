# PC BUILDER DATABASE FEATURE ANALYSIS

This document contains descriptions of database features and how they can be used in a PC recommendation system.


## CPU_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `cpu_specs` table is a primary key, uniquely identifying each CPU entry. This integer identifier is essential for relational database integrity and enables efficient joining of data from other tables (e.g., linking CPUs to motherboard compatibility). In a recommendation system, the `id` facilitates retrieval of specific CPU details and facilitates filtering/sorting based on linked data.

**Sample Values:** [356, 372, 373, 374, 404]

### name
**Data Type:** text

**Description:** The `name` feature stores the full, human-readable product name of each CPU. This string contains key identifiers like brand, model number, and clock speed, enabling filtering and sorting within the database. A recommendation system could leverage this name to match user search queries, display product titles, and categorize CPUs based on model series (e.g., identifying "i7" processors for high-performance builds).

**Sample Values:** ['Intel Core i7-7740X 4.3 GHz Quad-Core Processor', 'Intel Core i3-530 2.93 GHz Dual-Core Processor', 'Intel Core i3-2120 3.3 GHz Dual-Core Processor', 'Intel Core i3-540 3.06 GHz Dual-Core Processor', 'AMD EPYC 4364P 4.5 GHz 8-Core Processor']

### price
**Data Type:** text

**Description:** The "price" feature in `cpu_specs` represents the retail price of each CPU, stored as a text string including the dollar sign. This data is crucial for filtering CPUs based on budget constraints and implementing price-based sorting within a recommendation system, enabling users to find components within their desired price range. Further, it can be used in algorithms prioritizing cost-effectiveness alongside performance metrics.

**Sample Values:** ['$234.99', '$45.00', '$199.28', '$103.97', '$429.99']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores pricing and availability information for CPUs from various retailers, utilizing a JSONB data type for flexible storage. This allows for tracking price fluctuations and stock levels at different vendors. In a recommendation system, this data can be leveraged to prioritize CPUs with competitive pricing and high availability, improving user satisfaction and purchase likelihood.

**Sample Values:** [{'Amazon': {'price': '$234.99+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$45.00+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$199.28+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$103.97', 'availability': 'In Stock'}}, {'Newegg': {'price': '$429.99', 'availability': 'In Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The "manufacturer" feature in the `cpu_specs` table indicates the brand producing the CPU. This categorical data is crucial for filtering and recommending CPUs based on user preference (e.g., "Show me only Intel CPUs") or compatibility with other components, ensuring a cohesive system build. It's a fundamental attribute used for faceted search and targeted recommendations within the system.

**Sample Values:** ['Intel', 'Intel', 'Intel', 'Intel', 'AMD']

### part_number
**Data Type:** text

**Description:** The `part_number` feature represents a unique identifier assigned by the manufacturer to a specific CPU model. This alphanumeric string allows for precise identification and differentiation of CPU variants, crucial for accurate matching with product listings and compatibility checks. In a recommendation system, `part_number` is essential for filtering available CPUs based on user-specified motherboard compatibility or desired CPU features linked to that specific model.

**Sample Values:** ['BX80677I77740X', 'BX80616I3530', 'BX80623I32120', 'BX80616I3540', '100-100001477WOF']

### series
**Data Type:** text

**Description:** The "series" feature in `cpu_specs` denotes the product line or family a CPU belongs to (e.g., Intel Core i7, AMD EPYC). This attribute allows for filtering CPUs by brand and target market (consumer, workstation, server) and is crucial for recommending compatible motherboards or components based on the CPU's intended use case and architecture. It's a key discriminator for grouping CPUs with similar feature sets and performance characteristics.

**Sample Values:** ['Intel Core i7', 'Intel Core i3', 'Intel Core i3', 'Intel Core i3', 'AMD EPYC']

### microarchitecture
**Data Type:** text

**Description:** The 'microarchitecture' feature in `cpu_specs` defines the internal design and core technology of a CPU. It's a key differentiator between CPU generations from the same manufacturer, impacting performance characteristics like instruction set support and power efficiency. A recommendation system could leverage this to match users with CPUs offering specific architectural advancements needed for their workloads (e.g., Zen 4 for high-performance gaming).

**Sample Values:** ['Kaby Lake', 'Westmere', 'Sandy Bridge', 'Westmere', 'Zen 4']

### core_family
**Data Type:** text

**Description:** The `core_family` feature in `cpu_specs` denotes the architectural generation or microarchitecture of a CPU core, representing a specific design lineage (e.g., Intel's Kaby Lake-X). This allows for filtering CPUs based on architectural features and performance characteristics, enabling recommendations based on desired performance tiers or compatibility with specific workloads that benefit from a particular core family's optimizations. It can also be used to group CPUs for comparative analysis and performance benchmarking.

**Sample Values:** ['Kaby Lake-X', 'Clarkdale', 'Sandy Bridge', 'Clarkdale', 'Raphael']

### socket
**Data Type:** text

**Description:** The 'socket' feature in `cpu_specs` defines the physical interface on a motherboard that a CPU connects to. This alphanumeric string (e.g., LGA2066, AM5) dictates CPU compatibility – only CPUs designed for a specific socket can be used with a corresponding motherboard. A recommendation system would use this feature to ensure suggested motherboards are compatible with the selected CPU, preventing mismatched hardware combinations.

**Sample Values:** ['LGA2066', 'LGA1156', 'LGA1155', 'LGA1156', 'AM5']

### core_count
**Data Type:** integer

**Description:** The `core_count` feature in `cpu_specs` represents the number of independent processing units within a CPU. This integer value directly correlates with a CPU's potential for parallel processing and overall performance, particularly in multi-threaded workloads. A recommendation system could leverage `core_count` to match CPUs with user needs based on intended applications like video editing or gaming, favoring higher core counts for performance-intensive tasks.

**Sample Values:** [4, 2, 2, 2, 8]

### thread_count
**Data Type:** integer

**Description:** The `thread_count` feature in `cpu_specs` represents the number of independent threads a CPU can execute concurrently. This value directly impacts multitasking performance and is crucial for applications benefiting from parallel processing. A recommendation system could prioritize CPUs with higher thread counts for users indicating workloads like video editing or running virtual machines.

**Sample Values:** [8, 4, 4, 4, 16]

### performance_core_clock
**Data Type:** text

**Description:** The `performance_core_clock` feature represents the maximum clock speed (in GHz) at which a CPU core operates under typical load. This value is crucial for gauging processing speed and is frequently used in recommendation systems to prioritize CPUs with higher clock speeds for users seeking maximum single-core performance or for tasks like gaming where core clock significantly impacts frame rates. It should be considered alongside other metrics like core count and boost clock for a complete performance profile.

**Sample Values:** ['4.3 GHz', '2.93 GHz', '3.3 GHz', '3.06 GHz', '4.5 GHz']

### performance_core_boost_clock
**Data Type:** text

**Description:** The `performance_core_boost_clock` feature represents the maximum clock speed a CPU core can achieve under optimal conditions, typically expressed in GHz. This value indicates the potential for peak single-core performance and is crucial for tasks like gaming or demanding applications. In a recommendation system, it would be used to prioritize CPUs offering higher boost clocks for users seeking maximum responsiveness and performance.

**Sample Values:** ['4.5 GHz', 'NaN', 'NaN', 'NaN', '5.4 GHz']

### l2_cache
**Data Type:** text

**Description:** The `l2_cache` feature in the `cpu_specs` table represents the size of the CPU's Level 2 cache memory, typically expressed in megabytes (MB). This cache provides fast access to frequently used data, directly impacting CPU performance and responsiveness. A recommendation system could prioritize CPUs with larger L2 cache sizes for users emphasizing gaming or resource-intensive applications where low latency is critical.

**Sample Values:** ['1 MB', '0.5 MB', '0.5 MB', '0.5 MB', '8 MB']

### l3_cache
**Data Type:** text

**Description:** The `l3_cache` feature in `cpu_specs` represents the size of the CPU's Level 3 cache memory, typically expressed in megabytes (MB). This cache acts as a high-speed buffer for frequently accessed data, directly impacting performance, particularly in gaming and computationally intensive tasks. A recommendation system could prioritize CPUs with larger L3 cache sizes for users seeking optimal performance in those scenarios.

**Sample Values:** ['8 MB', '4 MB', '3 MB', '4 MB', '32 MB']

### tdp
**Data Type:** text

**Description:** The "tdp" feature in the `cpu_specs` table represents Thermal Design Power, indicating the maximum heat a CPU is expected to generate under normal operating conditions. This value is crucial for PC component recommendations as it informs the required cooling solution (CPU cooler) and power supply wattage to ensure stable and safe system operation. A recommendation system would use TDP to filter CPUs compatible with a user's existing or desired cooler and PSU.

**Sample Values:** ['112 W', '73 W', '65 W', '73 W', '105 W']

### integrated_graphics
**Data Type:** text

**Description:** The `integrated_graphics` feature in the `cpu_specs` table indicates whether a CPU includes an integrated graphics processing unit (GPU). This field stores the specific model or brand of the integrated GPU, allowing for filtering CPUs based on graphics capability. A recommendation system could leverage this to suggest CPUs with suitable integrated graphics for users prioritizing low-power or budget-friendly solutions, or to exclude CPUs without integrated graphics if a discrete GPU is already selected.

**Sample Values:** ['NaN', 'Intel HD Graphics', 'Intel HD Graphics 2000', 'Intel HD Graphics', 'Radeon']

### maximum_supported_memory
**Data Type:** text

**Description:** The `maximum_supported_memory` feature in `cpu_specs` indicates the maximum amount of RAM a given CPU model can handle. Its data type being text allows for values including units like "GB" and potentially "NaN" for unknown or unsupported values. This feature is crucial for PC component recommendation systems to ensure compatibility, filtering CPUs based on user-specified RAM configurations and preventing system instability.

**Sample Values:** ['64 GB', 'NaN', 'NaN', 'NaN', 'NaN']

### ecc_support
**Data Type:** boolean

**Description:** The `ecc_support` feature in the `cpu_specs` table indicates whether a CPU supports ECC (Error-Correcting Code) memory. This boolean value (True/False) is crucial for systems requiring high data integrity, such as servers or workstations handling sensitive data. A recommendation system should prioritize CPUs with `ecc_support=True` for users selecting components for such applications.

**Sample Values:** [False, False, False, False, True]

### includes_cooler
**Data Type:** boolean

**Description:** The `includes_cooler` feature in the `cpu_specs` table indicates whether a given CPU comes bundled with a CPU cooler. This boolean value (True/False) directly informs whether an additional cooler purchase is necessary for the user. A recommendation system can leverage this flag to suggest complementary coolers for CPUs where `includes_cooler` is False, or exclude cooler suggestions when it's True.

**Sample Values:** [False, True, True, True, False]

### packaging
**Data Type:** text

**Description:** The "packaging" feature in `cpu_specs` indicates the retail packaging format of the CPU (e.g., boxed, tray). This attribute signifies whether the CPU is sold in a retail box with accompanying documentation and potentially a cooler, versus a more basic tray package. A recommendation system could use this to filter results based on user preference for boxed products, or to prioritize boxed CPUs for users seeking a complete and readily usable component.

**Sample Values:** ['Boxed', 'Boxed', 'Boxed', 'Boxed', 'Boxed']

### lithography
**Data Type:** text

**Description:** The "lithography" feature in the `cpu_specs` table represents the manufacturing process node size used to fabricate a CPU, measured in nanometers. Smaller lithography values generally indicate more advanced fabrication, often correlating with higher transistor density and improved performance/efficiency. A recommendation system could prioritize CPUs with smaller lithography values for users seeking cutting-edge technology or maximizing performance within a power budget.

**Sample Values:** ['14 nm', '32 nm', '32 nm', '32 nm', '5 nm']

### includes_cpu_cooler
**Data Type:** boolean

**Description:** The `includes_cpu_cooler` feature in the `cpu_specs` table indicates whether a given CPU comes bundled with a CPU cooler. This boolean value allows the recommendation system to filter CPUs based on user preferences – for example, recommending CPUs *without* an included cooler if the user already has a compatible aftermarket cooler, or prioritizing those *with* a cooler for budget-conscious builds. This simplifies the selection process by factoring in a frequently needed accessory.

**Sample Values:** [False, True, True, True, False]

### simultaneous_multithreading
**Data Type:** boolean

**Description:** The `simultaneous_multithreading` feature indicates whether a CPU supports Intel's Hyper-Threading technology (or similar AMD implementation). This boolean value (True/False) signifies if the CPU can process multiple threads concurrently within a single physical core, effectively increasing the number of logical processors. A recommendation system could prioritize CPUs with `simultaneous_multithreading=True` for users needing increased multitasking performance or running heavily threaded applications like video editing or virtual machines.

**Sample Values:** [False, False, False, False, True]

### efficiency_core_clock
**Data Type:** text

**Description:** The `efficiency_core_clock` feature likely represents the clock speed (in MHz or GHz) used by a CPU's efficiency cores, designed for low-power operation. This value is valuable for estimating power consumption and performance in lightly threaded workloads, enabling a recommendation system to prioritize CPUs balancing performance and energy efficiency for users with specific power budgets or battery life concerns. The prevalence of "NaN" values suggests data quality issues or a limited number of CPUs with readily available efficiency core clock data.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### efficiency_core_boost_clock
**Data Type:** text

**Description:** The `efficiency_core_boost_clock` feature likely represents the maximum clock speed achievable by a CPU's efficiency cores during boost operation. This value indicates the processor's ability to handle lighter workloads efficiently, maximizing battery life or reducing power consumption. In a recommendation system, it could be prioritized for users seeking power-efficient builds or prioritizing mobile/laptop use cases.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### model
**Data Type:** text

**Description:** The "model" feature in the `cpu_specs` table represents the specific product name or identifier of a CPU. This string value is crucial for identifying individual CPU variants and is essential for filtering and matching CPUs based on user specifications or compatibility checks within a PC component recommendation system. The feature allows for precise identification and comparison of different CPU models, enabling accurate recommendations.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### url
**Data Type:** text

**Description:** The `url` feature stores the unique web address of a CPU product listing, typically on a retailer or product comparison site like PCPartPicker. This URL provides a direct link to detailed product information and can be used to fetch additional data (e.g., pricing, images, reviews) via web scraping or API integration to enrich the database and improve recommendation accuracy. Furthermore, it enables users to easily verify details and purchase components directly.

**Sample Values:** ['https://pcpartpicker.com/product/FJL7YJ/intel-core-i7-7740x-43ghz-quad-core-processor-bx80677i77740x', 'https://pcpartpicker.com/product/2Jdqqs/intel-cpu-bx80616i3530', 'https://pcpartpicker.com/product/2CXfrH/intel-cpu-bx80623i32120', 'https://pcpartpicker.com/product/WF6BD3/intel-cpu-bx80616i3540', 'https://pcpartpicker.com/product/vchv6h/amd-epyc-4364p-45-ghz-8-core-processor-100-100001477wof']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of a CPU in the database. This value is crucial for filtering and sorting CPUs based on budget constraints in a recommendation system, enabling users to find suitable options within a specified price range. Furthermore, it can be incorporated into a weighted scoring algorithm to balance performance and affordability in recommendations.

**Sample Values:** [234.99, 45.0, 199.28, 103.97, 429.99]

### score
**Data Type:** integer

**Description:** The "score" feature in the `cpu_specs` table likely represents a synthetic performance benchmark or aggregated rating reflecting overall CPU capability, possibly derived from a combination of factors like clock speed, core count, and benchmark results. This score can be used in a recommendation system to filter CPUs based on desired performance tiers, prioritize higher-scoring CPUs when suggesting upgrades, or rank options based on a user-defined performance expectation. Utilizing this score allows for a simplified performance comparison for users without requiring detailed technical understanding.

**Sample Values:** [75, 47, 43, 46, 98]


## GPU_SPECS

### id
**Data Type:** integer

**Description:** The "id" feature in the `gpu_specs` table is a primary key, representing a unique numerical identifier for each GPU entry. This ID allows for efficient referencing of GPU specifications within the database and is crucial for joining with other tables (e.g., pricing, reviews) in a recommendation system to link GPU features to user preferences or system requirements. It's a foundational element for querying and relating GPU data for accurate recommendations.

**Sample Values:** [2, 4, 761, 762, 262]

### name
**Data Type:** text

**Description:** The "name" feature represents the full, human-readable product name of the GPU. This string contains valuable information for filtering and displaying results, and can be parsed (using techniques like string splitting and regular expressions) to extract manufacturer, model, and potentially even performance tiers for more granular recommendations. It's crucial for user-facing presentation and enabling searches based on specific product names.

**Sample Values:** ['Zotac GAMING SOLID OC GeForce RTX 5090 32 GB Video Card', 'Asus ROG STRIX WHITE OC GeForce RTX 3090 24 GB Video Card', 'MSI GAMING X TRIO GeForce RTX 4090 24 GB Video Card', 'ASRock Radeon RX6700XT CLP 12GO Radeon RX 6700 XT 12 GB Video Card', 'EVGA XC3 ULTRA GAMING GeForce RTX 3070 Ti 8 GB Video Card']

### price
**Data Type:** text

**Description:** The "price" feature in the `gpu_specs` table represents the retail price of a specific GPU. As a text field, it requires parsing to extract the numerical value for comparison and filtering. This feature is crucial for recommending GPUs based on a user's budget constraints and for sorting GPUs by price within a given performance tier.

**Sample Values:** ['$2261.69', '$1999.99', '$3998.00', '$599.99', '$989.00']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores pricing and availability information for a GPU from various retailers in a JSONB format. This allows for flexible storage of retailer-specific details beyond just price. In a recommendation system, this data enables dynamic price comparisons, availability checks to filter viable options, and potentially personalized recommendations based on preferred retailers or budget constraints.

**Sample Values:** [{'Newegg': {'price': '$2261.69', 'availability': 'Out of Stock'}}, {'Amazon': {'price': '$1999.99+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$3998.00+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$599.99', 'availability': 'In Stock'}}, {'Amazon': {'price': '$989.00+', 'availability': 'In Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The `manufacturer` feature in `gpu_specs` identifies the company that produced the graphics card. This categorical data allows for filtering GPUs by brand preference, enabling users to specifically request components from a desired manufacturer. It's crucial for personalized recommendations catering to brand loyalty or perceived quality differences among GPU manufacturers.

**Sample Values:** ['Zotac', 'Asus', 'MSI', 'ASRock', 'EVGA']

### part_number
**Data Type:** text

**Description:** The `part_number` feature uniquely identifies a specific GPU model within the database. This alphanumeric string serves as a manufacturer's identifier and is crucial for distinguishing variations of the same GPU (e.g., different cooling solutions or clock speeds). In a recommendation system, it allows for precise matching of user selections to available components and facilitates filtering based on specific manufacturer models.

**Sample Values:** ['ZT-B50900J-10P', 'ROG-STRIX-RTX3090-O24G-WHITE\n90YV0F96-M0NM00', 'GeForce RTX 4090 GAMING X TRIO 24G\nRTX 4090 GAMING X TRIO 24G\nV510-006R\nG4090GXT24', 'RX6700XT CLP 12GO\n90-GA2LZZ-00UANF', '08G-P5-3785-KL']

### chipset
**Data Type:** text

**Description:** The "chipset" feature in `gpu_specs` identifies the specific GPU model, representing the core processing unit's architecture and generation. This feature is crucial for PC component recommendations, allowing for filtering by desired performance tier (e.g., recommending GPUs with "RTX 4090" for high-end gaming builds) and ensuring compatibility with other components like power supplies and motherboards. It also enables performance comparisons based on architectural similarities and benchmarks.

**Sample Values:** ['GeForce RTX 5090', 'GeForce RTX 3090', 'GeForce RTX 4090', 'Radeon RX 6700 XT', 'GeForce RTX 3070 Ti']

### memory
**Data Type:** text

**Description:** The "memory" feature in the `gpu_specs` table represents the dedicated video memory (VRAM) of a graphics card, quantified in gigabytes (GB). This attribute is crucial for determining a GPU's ability to handle large textures and complex scenes, impacting performance in demanding applications like gaming and video editing. A recommendation system would use this value to match GPUs to users based on their desired resolution, graphics settings, and workload requirements.

**Sample Values:** ['32 GB', '24 GB', '24 GB', '12 GB', '8 GB']

### core_clock
**Data Type:** text

**Description:** The `core_clock` feature represents the base operating frequency of a GPU's processing cores, expressed in megahertz (MHz). This value is a key performance indicator and can be used in a recommendation system to filter GPUs based on desired performance tiers or to compare relative processing power alongside other specifications like memory bandwidth. Higher core clock values generally correlate with increased performance in computationally intensive tasks like gaming and rendering.

**Sample Values:** ['2010 MHz', '1395 MHz', '2235 MHz', '2375 MHz', '1575 MHz']

### boost_clock
**Data Type:** text

**Description:** The `boost_clock` feature represents the maximum clock speed (in MHz) a GPU can achieve under optimized conditions, exceeding its base clock. This value is crucial for performance comparisons and can be used in a recommendation system to prioritize GPUs offering higher boost clocks for users seeking maximum frame rates in demanding applications or games. Analyzing `boost_clock` alongside other specifications allows for accurate performance tiering and targeted GPU suggestions.

**Sample Values:** ['2422 MHz', '1890 MHz', 'NaN', '2620 MHz', '1815 MHz']

### effective_memory_clock
**Data Type:** text

**Description:** The `effective_memory_clock` feature in `gpu_specs` represents the operational speed of the GPU's memory, typically measured in MHz. This value directly impacts memory bandwidth and overall GPU performance, especially in memory-bound workloads. A recommendation system could leverage this feature to prioritize GPUs with higher effective memory clocks for users prioritizing high frame rates in games or intensive data processing tasks.

**Sample Values:** ['NaN', '19500 MHz', '21000 MHz', '16000 MHz', '19000 MHz']

### interface
**Data Type:** text

**Description:** The "interface" feature in the `gpu_specs` table defines the physical connection type used by the GPU, specifically its bus interface. This value (typically PCIe x16) dictates compatibility with a motherboard's expansion slots. A recommendation system would use this feature to filter GPUs based on the user's motherboard's supported interface, ensuring compatibility and preventing purchase of incompatible components.

**Sample Values:** ['PCIe x16', 'PCIe x16', 'PCIe x16', 'PCIe x16', 'PCIe x16']

### color
**Data Type:** text

**Description:** The "color" feature in the `gpu_specs` table describes the aesthetic color scheme of the graphics card's cooler or shroud. This categorical data allows filtering for user preference (e.g., recommending black-themed GPUs for a dark build) and allows for visual search/sorting within the database. It's a low-priority attribute for performance but contributes to a more complete and visually-driven component selection experience.

**Sample Values:** ['Black / Copper', 'White / Black', 'Black', 'Black', 'Black']

### length
**Data Type:** text

**Description:** The "length" feature in the `gpu_specs` table represents the physical length of the GPU in millimeters. This measurement is crucial for ensuring compatibility with a PC case, as a GPU exceeding the available space will not fit. A recommendation system would utilize this data to filter GPUs based on the user's case dimensions, preventing incompatible selections and ensuring a successful build.

**Sample Values:** ['330 mm', '318 mm', '337 mm', '303 mm', '285 mm']

### tdp
**Data Type:** text

**Description:** The `tdp` (Thermal Design Power) feature represents the maximum sustained power a GPU is designed to dissipate, typically measured in watts. It's a crucial indicator of a GPU's heat output and power consumption, enabling the recommendation system to filter for compatible power supplies and cooling solutions.  Using `tdp` allows the system to suggest GPUs within a user's existing power budget and ensure adequate thermal headroom for optimal performance.

**Sample Values:** ['575 W', '350 W', '450 W', '230 W', '290 W']

### case_expansion_slot_width
**Data Type:** text

**Description:** The `case_expanion_slot_width` feature in `gpu_specs` represents the number of PCIe expansion slots required by a GPU, indicating its physical size. This data is crucial for compatibility checks; a recommendation system should filter GPUs based on the available slot width in the user's PC case to avoid physical fit issues. It enables accurate suggestions by ensuring the proposed GPU can be physically installed.

**Sample Values:** ['3', '2', '3', '2', '2']

### total_slot_width
**Data Type:** text

**Description:** The `total_slot_width` feature represents the physical space a GPU occupies within a computer's PCI-e slot, typically measured in slots (where 1 slot is roughly equivalent to 82mm). This is crucial for compatibility; a recommendation system should filter GPUs based on this value to ensure they fit within the available space in a user's case, preventing physical fitting issues. Utilizing this data ensures recommended GPUs are physically compatible with the user's existing system.

**Sample Values:** ['4', '3', '4', '3', '3']

### cooling
**Data Type:** text

**Description:** The "cooling" feature in the `gpu_specs` table describes the GPU's thermal management solution. It typically indicates the number and type of fans employed for heat dissipation. This data can be leveraged in a recommendation system to prioritize GPUs with adequate cooling solutions for users with high-performance CPUs or in environments with limited airflow.

**Sample Values:** ['3 Fans', '3 Fans', '3 Fans', '3 Fans', '3 Fans']

### external_power
**Data Type:** text

**Description:** The `external_power` feature in the `gpu_specs` table describes the power connectors required from the power supply unit (PSU) for a given GPU. This data represents the number and type of PCIe power connectors (e.g., 8-pin, 16-pin) needed for operation. A recommendation system can utilize this to filter GPUs based on user's existing PSU capabilities, ensuring compatibility and preventing power delivery issues.

**Sample Values:** ['1 PCIe 16-pin', '3 PCIe 8-pin', '1 PCIe 16-pin', '2 PCIe 8-pin', '2 PCIe 8-pin']

### hdmi
**Data Type:** text

**Description:** The "hdmi" feature in the `gpu_specs` table indicates the HDMI version supported by a graphics card, stored as text (e.g., "2.1", "2.0b"). This data allows the recommendation system to filter GPUs based on user display requirements, ensuring compatibility with high-resolution monitors and televisions utilizing HDMI connectivity. It enables precise matching of GPU HDMI versions to user-specified display capabilities for optimal performance.

**Sample Values:** []

### displayport
**Data Type:** text

**Description:** The "displayport" feature in the `gpu_specs` table indicates the number of DisplayPort outputs available on a GPU. This data type (text) likely stores the count of ports (e.g., "1", "2", "3"). A recommendation system can utilize this feature to filter GPUs based on user-specified display configurations or prioritize GPUs supporting the user's desired number of external monitors.

**Sample Values:** []

### dvi
**Data Type:** text

**Description:** The "dvi" feature in the `gpu_specs` table represents the Digital Visual Interface (DVI) version supported by a graphics card. It's a textual field indicating the DVI version (e.g., "DVI-I", "DVI-D", "DVI-SL"). A recommendation system could use this to filter GPUs based on user display connectivity requirements, ensuring compatibility with monitors utilizing DVI connections.

**Sample Values:** []

### vga
**Data Type:** text

**Description:** The "vga" feature in the `gpu_specs` table likely represents the VGA (Video Graphics Array) resolution supported by the GPU. This value, stored as text, indicates the maximum resolution the GPU can output using the older VGA standard. A recommendation system could use this to filter GPUs based on user-specified display resolution requirements or to indicate compatibility with legacy systems.

**Sample Values:** []

### url
**Data Type:** text

**Description:** The `url` feature in the `gpu_specs` table stores the unique web address of each GPU product listing, typically on a retailer or product comparison website. This URL serves as a stable identifier for the GPU, allowing retrieval of detailed product information (images, pricing history, user reviews) not directly stored within the database itself. A recommendation system could leverage this URL to dynamically enrich product details presented to users or to track price changes for accurate price-based recommendations.

**Sample Values:** ['https://pcpartpicker.com/product/qkdMnQ/zotac-gaming-solid-oc-geforce-rtx-5090-32-gb-video-card-zt-b50900j-10p', 'https://pcpartpicker.com/product/G32WGX/asus-geforce-rtx-3090-24-gb-rog-strix-white-oc-video-card-rog-strix-rtx3090-o24g-white', 'https://pcpartpicker.com/product/mVM48d/msi-gaming-x-trio-geforce-rtx-4090-24-gb-video-card-geforce-rtx-4090-gaming-x-trio-24g', 'https://pcpartpicker.com/product/x9Gbt6/asrock-radeon-rx-6700-xt-12-gb-challenger-pro-oc-video-card-rx6700xt-clp-12go', 'https://pcpartpicker.com/product/GtWzK8/evga-geforce-rtx-3070-ti-8-gb-xc3-ultra-gaming-video-card-08g-p5-3785-kl']

### model
**Data Type:** text

**Description:** The "model" feature in the `gpu_specs` table represents the specific branding and designation of a graphics card. This string value allows for granular differentiation between GPU variants and is crucial for accurate filtering and matching in a recommendation system, allowing users to specify a desired GPU model or enabling similarity-based recommendations based on model names. Handling the prevalence of "NaN" values (likely representing missing data) is a necessary data cleaning step for effective utilization.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'Radeon RX6700XT CLP 12GO', 'NaN']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of a GPU, likely in USD. This value can be used in recommendation systems to filter GPUs based on a user's budget, prioritize lower-cost options for budget-conscious users, or calculate price-performance ratios for optimized recommendations. It's a crucial input for price-sensitive filtering and value-based comparisons.

**Sample Values:** [2261.69, 1999.99, 3998.0, 599.99, 989.0]

### score
**Data Type:** integer

**Description:** The "score" feature in `gpu_specs` likely represents a composite performance metric, possibly derived from a weighted average of benchmark results or synthetic tests. This score allows for easy ranking and comparison of GPUs, enabling a recommendation system to prioritize higher-scoring cards based on user-defined performance targets or budget constraints. It simplifies filtering and sorting GPUs to provide relevant suggestions without requiring complex benchmark data analysis.

**Sample Values:** [100, 97, 80, 85, 79]


## MEMORY_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `memory_specs` table is a primary key, serving as a unique numerical identifier for each memory module entry. This integer ID facilitates efficient joins with other tables (like memory manufacturers or compatibility lists) and enables quick retrieval of specific memory specifications within the database. In a recommendation system, it's crucial for linking memory modules to user selections and generating accurate component pairings.

**Sample Values:** [165, 170, 171, 172, 173]

### name
**Data Type:** text

**Description:** The "name" feature stores the full product name of the memory module. This string provides crucial information about the manufacturer, capacity, configuration (e.g., 2x8GB), generation (DDR3/4/5), and speed/timings, which can be parsed and used to filter and recommend memory based on user-specified criteria like motherboard compatibility and desired performance levels.  Natural Language Processing (NLP) techniques could further extract these attributes for more granular matching and recommendations.

**Sample Values:** ['Corsair Vengeance RGB Pro 32 GB (2 x 16 GB) DDR4-3200 CL16 Memory', 'G.Skill Ripjaws V 16 GB (2 x 8 GB) DDR4-3600 CL18 Memory', 'G.Skill Ripjaws V 64 GB (2 x 32 GB) DDR4-3600 CL18 Memory', 'G.Skill Trident Z5 RGB 32 GB (2 x 16 GB) DDR5-8000 CL38 Memory', 'Corsair Vengeance 16 GB (2 x 8 GB) DDR3-1600 CL9 Memory']

### price
**Data Type:** text

**Description:** The "price" feature in the `memory_specs` table represents the retail price of a specific memory module. This data, stored as text to accommodate currency symbols, is crucial for filtering and sorting memory options based on budget constraints within a recommendation system. It allows the system to prioritize modules that fall within a user's defined price range or suggest the best value based on performance and cost.

**Sample Values:** ['$81.99', '$32.99', '$99.99', '$169.99', '$75.98']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores price and availability data for a memory component across various retailers in a JSONB format. This allows for flexible tracking of pricing fluctuations and stock levels from different vendors. In a recommendation system, it enables price-based filtering, identification of the cheapest options, and potentially predicting price trends to inform user suggestions.

**Sample Values:** [{'B&H': {'price': '$82.99', 'availability': 'In Stock'}, 'Amazon': {'price': '$81.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$81.99', 'availability': 'In Stock'}, 'Corsair': {'price': '$82.99', 'availability': 'In Stock'}, 'Best Buy': {'price': '$82.99', 'availability': 'Out of Stock'}}, {'Amazon': {'price': '$32.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$32.99', 'availability': 'In Stock'}, 'MemoryC': {'price': '$64.48', 'availability': 'In Stock'}}, {'Amazon': {'price': '$99.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$99.99', 'availability': 'In Stock'}}, {'Newegg': {'price': '$169.99', 'availability': 'In Stock'}}, {'Amazon': {'price': '$75.98', 'availability': 'In Stock'}, 'Newegg': {'price': '$75.99', 'availability': 'In Stock'}, 'Corsair': {'price': '$88.98', 'availability': 'In Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The "manufacturer" feature in the `memory_specs` table identifies the company that produced the RAM module. This attribute is crucial for filtering and sorting memory options based on user preference or brand reputation. A recommendation system can leverage this to prioritize modules from preferred manufacturers or suggest compatible options based on motherboard manufacturer compatibility lists.

**Sample Values:** ['Corsair', 'G.Skill', 'G.Skill', 'G.Skill', 'Corsair']

### part_number
**Data Type:** text

**Description:** The `part_number` feature uniquely identifies a specific memory module within a manufacturer's catalog. This alphanumeric string serves as a precise identifier for product variations (e.g., capacity, speed, timings) and is crucial for matching components and ensuring compatibility. In a recommendation system, it's used to filter available memory options, cross-reference with motherboard compatibility lists, and accurately represent available product choices.

**Sample Values:** ['CMW32GX4M2E3200C16', 'F4-3600C18D-16GVK', 'F4-3600C18D-64GVK', 'F5-8000J3848H16GX2-TZ5RK', 'CMZ16GX3M2A1600C10']

### speed
**Data Type:** text

**Description:** The "speed" feature in the `memory_specs` table represents the data transfer rate of the RAM, expressed in a standardized format (e.g., DDR4-3200). This value, measured in MT/s (MegaTransfers per second), directly impacts system performance and is crucial for compatibility matching during component recommendations, ensuring the selected RAM is supported by the motherboard and CPU. A recommendation system would prioritize RAM with speeds compatible with and beneficial to the user's existing hardware.

**Sample Values:** ['DDR4-3200', 'DDR4-3600', 'DDR4-3600', 'DDR5-8000', 'DDR3-1600']

### modules
**Data Type:** text

**Description:** The "modules" feature in the `memory_specs` table describes the memory module configuration, specifying the quantity and capacity of individual RAM sticks. This data allows a recommendation system to filter memory options based on desired total capacity and number of modules, ensuring compatibility with the motherboard and meeting user preferences for dual-channel or quad-channel configurations. Analyzing module counts also aids in identifying potential performance bottlenecks if mismatched configurations are selected.

**Sample Values:** ['2 x 16GB', '2 x 8GB', '2 x 32GB', '2 x 16GB', '2 x 8GB']

### price_per_gb
**Data Type:** text

**Description:** The `price_per_gb` feature represents the cost of memory (RAM) normalized to its capacity in gigabytes. This metric allows for direct price comparisons between different memory modules regardless of their total size, facilitating cost-effective recommendations. A recommendation system could utilize this feature to prioritize memory options offering the best price/performance ratio or to filter based on user-defined budget constraints.

**Sample Values:** ['$2.562', '$2.062', '$1.562', '$5.312', '$4.749']

### color
**Data Type:** text

**Description:** The "color" feature in `memory_specs` describes the visual appearance of the memory module, typically referring to the color of the heat spreader. This attribute can be used in a recommendation system to filter results based on user aesthetic preferences or to suggest memory kits that visually match other components in their system, enhancing overall build consistency. It's a purely cosmetic characteristic, so its relevance is dependent on user prioritization of aesthetics.

**Sample Values:** ['Black', 'Black', 'Black', 'Black', 'Black / Yellow']

### first_word_latency
**Data Type:** text

**Description:** The `first_word_latency` feature represents the time, in nanoseconds (ns), it takes for memory to output the first data word after a read request. This metric directly impacts system responsiveness and is crucial for applications sensitive to memory access delays. A recommendation system could prioritize memory modules with lower `first_word_latency` values to optimize performance for users emphasizing responsiveness, such as gamers or content creators.

**Sample Values:** ['10 ns', '10 ns', '10 ns', '9.5 ns', '11.25 ns']

### cas_latency
**Data Type:** text

**Description:** The `cas_latency` feature represents the CAS (Column Access Strobe) latency of RAM, a critical timing parameter indicating the delay between a command and data availability. Lower CAS latency values generally signify faster RAM performance. A recommendation system could prioritize memory modules with lower `cas_latency` values for users seeking maximum responsiveness and improved performance in memory-intensive applications.

**Sample Values:** ['16', '18', '18', '38', '9']

### voltage
**Data Type:** text

**Description:** The "voltage" feature in the `memory_specs` table represents the operating voltage required by the memory module, typically expressed in volts. This is a critical compatibility parameter; a recommendation system should prioritize memory modules with voltages compatible with the system's motherboard and CPU to avoid instability or damage. Matching voltage is essential for ensuring system stability and optimal performance.

**Sample Values:** ['1.35 V', '1.35 V', '1.35 V', '1.45 V', '1.5 V']

### timing
**Data Type:** text

**Description:** The "timing" feature in the `memory_specs` table represents the CAS latency timings (CL, tRCD, tRP, tRAS) of RAM modules, crucial for performance. These values, expressed in clock cycles, directly impact memory access speed and should be considered when recommending memory to ensure compatibility and optimal system performance, particularly for users prioritizing gaming or content creation. A recommendation system would favor timings that match or exceed the motherboard and CPU's supported speeds.

**Sample Values:** ['16-20-20-38', '18-22-22-42', '18-22-22-42', '38-38-48-128', '9-9-9-24']

### ecc
**Data Type:** boolean

**Description:** The "ecc" feature in the `memory_specs` table indicates whether the memory module supports Error-Correcting Code (ECC). This boolean flag signifies a critical feature for data integrity, particularly important for servers and workstations requiring high reliability. A recommendation system could prioritize ECC memory for users selecting builds intended for professional applications or those prioritizing data stability over cost.

**Sample Values:** []

### heat_spreader
**Data Type:** boolean

**Description:** The `heat_spreader` feature in the `memory_specs` table indicates whether a memory module utilizes a heat spreader to dissipate heat. This boolean value (True/False) signifies the presence of a metallic layer designed to improve thermal performance. A recommendation system could prioritize memory modules with `heat_spreader = True` for users building high-performance systems or those overclocking, as it suggests improved stability and longevity under load.

**Sample Values:** [True, True, True, True, True]

### url
**Data Type:** text

**Description:** The `url` feature stores a link to the product page on PCPartPicker, providing a standardized external reference for each memory module. This URL can be leveraged for fetching additional product details not stored in the `memory_specs` table (e.g., pricing, images, user reviews) and for providing users with direct links to purchase recommended memory. It serves as a valuable API endpoint for real-time data enrichment within a recommendation engine.

**Sample Values:** ['https://pcpartpicker.com/product/27TzK8/corsair-vengeance-rgb-pro-32-gb-2-x-16-gb-ddr4-3200-memory-cmw32gx4m2e3200c16', 'https://pcpartpicker.com/product/n6RgXL/gskill-ripjaws-v-16-gb-2-x-8-gb-ddr4-3600-memory-f4-3600c18d-16gvk', 'https://pcpartpicker.com/product/kmBhP6/gskill-ripjaws-v-64-gb-2-x-32-gb-ddr4-3600-memory-f4-3600c18d-64gvk', 'https://pcpartpicker.com/product/xQ8bt6/gskill-trident-z5-rgb-32-gb-2-x-16-gb-ddr5-8000-cl38-memory-f5-8000j3848h16gx2-tz5rk', 'https://pcpartpicker.com/product/qdkD4D/corsair-memory-cmz16gx3m2a1600c10']

### model
**Data Type:** text

**Description:** The "model" feature in the `memory_specs` table represents the specific model name or part number of a RAM module. This string identifier allows for precise differentiation between memory modules with potentially similar specifications and is crucial for matching components based on manufacturer and specific revision. A recommendation system can utilize this field to filter for compatible RAM based on motherboard compatibility lists or user preferences for specific brands/models.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of a memory module, likely in USD. This value is crucial for filtering and sorting memory options based on user budget constraints and can be integrated into a recommendation system to prioritize affordable alternatives or suggest optimal value-for-money configurations. It allows for price-based ranking and comparison within the memory selection process.

**Sample Values:** [81.99, 32.99, 99.99, 169.99, 75.98]

### score
**Data Type:** integer

**Description:** The "score" feature in the `memory_specs` table likely represents a composite performance rating assigned to each memory module, aggregating factors like timings, frequency, and capacity. This score can be used within a recommendation system to prioritize memory modules with higher values, effectively surfacing the best performing options for users seeking optimal system performance. It simplifies comparison across different memory configurations without requiring users to manually evaluate individual specifications.

**Sample Values:** [54, 53, 66, 63, 36]


## SSD_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `ssd_specs` table serves as a primary key, uniquely identifying each SSD record within the database. This integer identifier allows for efficient joins with other tables (like manufacturer or compatibility tables) and is essential for retrieving specific SSD data within the recommendation system. It ensures data integrity and facilitates precise referencing of SSD entries during matching and ranking processes.

**Sample Values:** [1, 2, 3, 4, 5]

### name
**Data Type:** text

**Description:** The "name" feature in the `ssd_specs` table represents the full, user-facing product name of the SSD. This string is crucial for displaying product information to users and is essential for matching user search queries with specific SSD models. In a recommendation system, it's used for filtering, sorting by popularity (based on search frequency), and presenting relevant product options.

**Sample Values:** ['Samsung 980 Pro', 'Kingston NV2', 'Samsung 970 Evo Plus', 'Samsung 990 Pro', 'Crucial P3 Plus']

### price
**Data Type:** numeric

**Description:** The "price" feature in the `ssd_specs` table represents the retail cost of a specific Solid State Drive (SSD). This numeric value allows for price-based filtering and sorting within the database, enabling the recommendation system to prioritize SSDs within a user-defined budget or suggest cost-effective alternatives. It’s crucial for algorithms aiming to optimize value alongside performance metrics.

**Sample Values:** [169.99, 60.99, 97.5, 318.35, 69.98]

### capacity
**Data Type:** integer

**Description:** The "capacity" feature in the `ssd_specs` table represents the storage volume of the SSD, measured in gigabytes (GB). This integer value directly impacts the amount of data the SSD can hold and is a crucial factor for users prioritizing storage space. A recommendation system would leverage this feature to filter and prioritize SSDs based on user-specified storage requirements or to suggest larger capacity drives for users with extensive data storage needs.

**Sample Values:** [2000, 1000, 1000, 4000, 1000]

### price_per_gb
**Data Type:** numeric

**Description:** The `price_per_gb` feature represents the cost of an SSD normalized by its storage capacity (in gigabytes). This metric allows for direct cost comparison between SSDs of varying sizes, facilitating recommendations based on value-for-money. A recommendation system could leverage this feature to suggest the most cost-effective SSD for a user's desired storage capacity.

**Sample Values:** [0.085, 0.061, 0.098, 0.08, 0.07]

### type
**Data Type:** text

**Description:** The `type` feature in the `ssd_specs` table designates the fundamental category of the SSD. It consistently indicates "SSD" for all entries, signifying this is a solid-state drive and not another storage medium. In a recommendation system, this feature confirms the component's category, enabling filtering for users specifically seeking SSDs and facilitating compatibility checks with other system components.

**Sample Values:** ['SSD', 'SSD', 'SSD', 'SSD', 'SSD']

### cache
**Data Type:** text

**Description:** The "cache" feature in the `ssd_specs` table represents the amount of DRAM cache present on the SSD, typically measured in megabytes. This value significantly impacts performance, particularly in handling small random reads and writes. A recommendation system could prioritize SSDs with larger cache values for users emphasizing responsiveness and general-purpose computing tasks.

**Sample Values:** ['2048.0', 'NaN', '1024.0', '4096.0', 'NaN']

### form_factor
**Data Type:** text

**Description:** The `form_factor` feature in the `ssd_specs` table specifies the physical dimensions and connector type of the SSD. It's a crucial attribute for compatibility, as motherboards have specific slots (e.g., M.2) and size requirements (e.g., 2280). A recommendation system would filter SSDs based on the user's motherboard's supported form factors to ensure a successful installation.

**Sample Values:** ['M.2-2280', 'M.2-2280', 'M.2-2280', 'M.2-2280', 'M.2-2280']

### interface
**Data Type:** text

**Description:** The "interface" feature in the `ssd_specs` table defines the physical connection type of the SSD, specifying the form factor (M.2) and the PCIe generation and lane configuration (e.g., PCIe 4.0 x4). This is crucial for compatibility checks; a recommendation system would filter SSDs based on the motherboard's supported interface to ensure the SSD can be physically connected and operate at its maximum speed. Incompatible interfaces would be excluded from recommendations.

**Sample Values:** ['M.2 PCIe 4.0 X4', 'M.2 PCIe 4.0 X4', 'M.2 PCIe 3.0 X4', 'M.2 PCIe 4.0 X4', 'M.2 PCIe 4.0 X4']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of an SSD in the database. This feature is crucial for filtering and sorting SSDs based on budget constraints and for calculating price-to-performance ratios within a PC component recommendation system, enabling suggestions tailored to user spending limits. It allows for prioritizing lower-cost options or identifying the best value within a specified price range.

**Sample Values:** [169.99, 60.99, 97.5, 318.35, 69.98]


## MOTHERBOARD_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `motherboard_specs` table serves as a primary key, uniquely identifying each motherboard entry. This integer value facilitates efficient data retrieval and linking to other related tables (e.g., compatibility lists) within the database. In a recommendation system, it's crucial for referencing specific motherboards when suggesting compatible components or filtering results based on user selections.

**Sample Values:** [304, 324, 412, 414, 415]

### name
**Data Type:** text

**Description:** The `name` feature stores the full product name of each motherboard. This string data is crucial for identifying specific models and can be used for filtering and sorting in a recommendation system, enabling users to find exact matches or similar products based on name patterns (e.g., brand, chipset). Furthermore, it's valuable for displaying user-facing product listings and search results.

**Sample Values:** ['Asus ROG MAXIMUS Z790 HERO BTF ATX LGA1700 Motherboard', 'ASRock B850 Pro-A ATX AM5 Motherboard', 'Asus TUF GAMING Z690-PLUS WIFI D4 ATX LGA1700 Motherboard', 'ASRock B550 Pro4 ATX AM4 Motherboard', 'MSI MPG Z790 CARBON WIFI II ATX LGA1700 Motherboard']

### price
**Data Type:** text

**Description:** The "price" feature in the `motherboard_specs` table represents the retail cost of each motherboard, stored as a text string including a dollar sign. This feature is crucial for filtering and ranking motherboards based on budget constraints within a recommendation system, allowing users to specify a maximum price threshold and prioritizing more affordable options when appropriate. It would require parsing to extract the numerical value for accurate comparisons and calculations.

**Sample Values:** ['$903.70', '$169.99', '$259.99', '$173.77', '$269.99']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores price and availability information for a motherboard from various retailers in a JSONB format. This allows for flexible storage of varying retailer data structures and enables queries to find the lowest price or identify retailers with stock. A recommendation system can utilize this data to prioritize motherboards based on price, availability, and preferred retailer for the user.

**Sample Values:** [{'Amazon': {'price': '$903.70+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$169.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$169.99', 'availability': 'In Stock'}}, {'GameStop': {'price': '$259.99', 'availability': 'Out of Stock'}}, {'Amazon': {'price': '$173.77+', 'availability': 'In Stock'}, 'MemoryC': {'price': '$174.92', 'availability': 'In Stock'}}, {'B&H': {'price': '$269.99', 'availability': 'Out of Stock'}, 'MSI': {'price': '$429.99', 'availability': 'In Stock'}, 'Amazon': {'price': '$333.71+', 'availability': 'In Stock'}, 'Newegg': {'price': '$429.99', 'availability': 'In Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The "manufacturer" feature in `motherboard_specs` identifies the company that produced the motherboard. This categorical data allows for filtering and sorting motherboards based on brand preference, enabling users to refine recommendations to only display products from their favored manufacturers. Furthermore, it can be incorporated into collaborative filtering or content-based filtering algorithms to suggest motherboards based on user affinity for specific brands.

**Sample Values:** ['Asus', 'ASRock', 'Asus', 'ASRock', 'MSI']

### part_number
**Data Type:** text

**Description:** The `part_number` feature represents the manufacturer's unique identifier for a specific motherboard model, often containing revision information. This field is critical for precise product identification and inventory management, allowing for differentiation between subtly different versions of the same motherboard. In a recommendation system, it enables accurate matching of user selections, compatibility checks with other components (e.g., CPU, RAM), and retrieval of detailed specifications associated with a specific motherboard revision.

**Sample Values:** ['ROG MAXIMUS Z790 HERO BTF\n90MB1H50-M0EAY0\n90MB1H50-M0AAY0', 'B850 Pro-A\n90-MXBQM0-A0UAYZ\n90-MXBQM-A0UAYZ', 'TUF GAMING Z690-PLUS WIFI D4\n90MB18V0-M0EAY0', 'B550 Pro4\n90-MXBCZ0-A0UAYZ', 'MPG Z790 CARBON WIFI II\n7D89-006R\n911-7D89-010']

### form_factor
**Data Type:** text

**Description:** The `form_factor` feature in the `motherboard_specs` table defines the physical size and shape of a motherboard. It's a crucial constraint for PC builds as it dictates case compatibility; a recommendation system would use this to filter motherboards based on the user's selected PC case's supported form factors, ensuring a proper fit. This prevents incompatible hardware selections and a failed build.

**Sample Values:** ['ATX', 'ATX', 'ATX', 'ATX', 'ATX']

### socket_cpu
**Data Type:** text

**Description:** The `socket_cpu` feature in `motherboard_specs` represents the physical interface type on the motherboard that connects to the CPU. This is a critical compatibility factor; a PC recommendation system must match `socket_cpu` with compatible CPU models to avoid incompatibility errors and ensure a functional build. The system can filter motherboards based on a user's selected CPU or vice-versa.

**Sample Values:** ['LGA1700', 'AM5', 'LGA1700', 'AM4', 'LGA1700']

### chipset
**Data Type:** text

**Description:** The "chipset" feature in the `motherboard_specs` table identifies the integrated logic controller on a motherboard, dictating supported CPU generations, memory speeds, and I/O capabilities. In a recommendation system, this is crucial for compatibility filtering – ensuring recommended motherboards support the selected CPU and desired RAM configuration. It also enables tiered recommendations based on chipset feature sets (e.g., recommending Z790 for overclocking enthusiasts).

**Sample Values:** ['Intel Z790', 'AMD B850', 'Intel Z690', 'AMD B550', 'Intel Z790']

### memory_max
**Data Type:** text

**Description:** The `memory_max` feature in the `motherboard_specs` table represents the maximum supported RAM capacity for a given motherboard. This value, stored as text, indicates the total amount of RAM (in GB) the motherboard can accommodate. In a recommendation system, it's crucial for matching motherboards to user-specified RAM capacity or desired future upgrade paths, ensuring compatibility and avoiding potential system instability.

**Sample Values:** ['192 GB', '256 GB', '128 GB', '128 GB', '192 GB']

### memory_slots
**Data Type:** integer

**Description:** The `memory_slots` feature in the `motherboard_specs` table represents the number of physical RAM slots available on a motherboard. This integer value dictates the maximum RAM capacity and flexibility for memory upgrades. In a recommendation system, it's a crucial constraint – ensuring recommended motherboards are compatible with user-specified RAM capacity and expansion needs.

**Sample Values:** [4, 4, 4, 4, 4]

### memory_type
**Data Type:** text

**Description:** The `memory_type` feature in the `motherboard_specs` table indicates the type of RAM supported by a specific motherboard. This data is crucial for compatibility checks; a recommendation system would use it to ensure suggested motherboards are paired with compatible RAM modules (e.g., suggesting DDR5 RAM for a DDR5-compatible motherboard).  Failure to match memory types would result in system instability or failure to boot.

**Sample Values:** ['DDR5', 'DDR5', 'DDR4', 'DDR4', 'DDR5']

### memory_speed
**Data Type:** text

**Description:** The `memory_speed` feature in the `motherboard_specs` table represents the supported RAM speeds the motherboard can handle, expressed in a text format listing multiple supported speeds. This data is crucial for a recommendation system to ensure compatibility and optimize performance by suggesting motherboards that support the user's desired RAM speed or a suitable range of speeds for their intended use case. The string format requires parsing to extract individual speed values for accurate comparisons and filtering.

**Sample Values:** ['DDR5-4800\nDDR5-5000\nDDR5-5200\nDDR5-5400\nDDR5-5600\nDDR5-5800\nDDR5-6000\nDDR5-6200\nDDR5-6400\nDDR5-6600\nDDR5-6800\nDDR5-7000\nDDR5-7200\nDDR5-7400\nDDR5-7600\nDDR5-7800\nDDR5-8000', 'DDR5-4400\nDDR5-4800\nDDR5-5200\nDDR5-5600\nDDR5-6000\nDDR5-6200\nDDR5-6400\nDDR5-6600\nDDR5-6800\nDDR5-7000\nDDR5-7200\nDDR5-7600\nDDR5-7800\nDDR5-8000', 'DDR4-2133\nDDR4-2400\nDDR4-2666\nDDR4-2800\nDDR4-2933\nDDR4-3000\nDDR4-3200\nDDR4-3333\nDDR4-3400\nDDR4-3466\nDDR4-3600\nDDR4-3733\nDDR4-3866\nDDR4-4000\nDDR4-4133\nDDR4-4266\nDDR4-4400\nDDR4-4600\nDDR4-4800\nDDR4-5000\nDDR4-5133\nDDR4-5333', 'DDR4-2133\nDDR4-2400\nDDR4-2666\nDDR4-2933\nDDR4-3200\nDDR4-3466\nDDR4-3600\nDDR4-3733\nDDR4-3800\nDDR4-3866\nDDR4-4000\nDDR4-4133\nDDR4-4200\nDDR4-4266\nDDR4-4333\nDDR4-4400\nDDR4-4533', 'DDR5-4800\nDDR5-5000\nDDR5-5200\nDDR5-5400\nDDR5-5600\nDDR5-5800\nDDR5-6000\nDDR5-6200\nDDR5-6400\nDDR5-6600\nDDR5-6800\nDDR5-7000\nDDR5-7200\nDDR5-7400\nDDR5-7600\nDDR5-7800']

### color
**Data Type:** text

**Description:** The "color" feature in the `motherboard_specs` table describes the aesthetic color scheme of the motherboard. This attribute can be used in a recommendation system to filter results based on user-specified preferences for visual style, allowing for personalized builds and enhancing user satisfaction by matching desired aesthetics. It’s a non-functional attribute, but contributes to overall system build cohesion.

**Sample Values:** ['Black', 'Black / Silver', 'Black / Silver', 'Silver / Black', 'Black']

### sli_crossfire
**Data Type:** text

**Description:** The `sli_crossfire` feature in the `motherboard_specs` table indicates whether a motherboard supports NVIDIA SLI or AMD CrossFire, multi-GPU configurations. Its value is text, with "NaN" signifying no support, while other values specify the supported version or capabilities. This feature can be utilized in a recommendation system to filter motherboards for users planning to use multiple GPUs for increased graphical performance.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'CrossFire Capable', 'NaN']

### pci_slots
**Data Type:** text

**Description:** The `pci_slots` feature in the `motherboard_specs` table represents the number and type (e.g., PCIe 3.0 x16, PCIe 4.0 x1) of PCI Express slots available on a motherboard. This data is crucial for recommending motherboards compatible with expansion cards like GPUs, sound cards, and network adapters, ensuring sufficient slots and appropriate bandwidth are available for the user's desired configuration. A recommendation system would filter motherboards based on the number and type of PCI slots required by the user's chosen expansion cards.

**Sample Values:** []

### onboard_video
**Data Type:** text

**Description:** The `onboard_video` feature in the `motherboard_specs` table indicates whether the motherboard includes integrated graphics processing. Its text value often reflects dependency on the installed CPU's integrated GPU capabilities. In a recommendation system, this feature is crucial for identifying motherboards suitable for builds where a discrete graphics card isn't desired or is unavailable, allowing for filtering based on integrated graphics needs.

**Sample Values:** ['Depends on CPU', 'Depends on CPU', 'Depends on CPU', 'Depends on CPU', 'Depends on CPU']

### wireless_networking
**Data Type:** text

**Description:** The `wireless_networking` feature in the `motherboard_specs` table indicates the supported Wi-Fi standard for a given motherboard. It's a text field storing values like 'Wi-Fi 7' or 'Wi-Fi 6', representing the wireless connectivity capabilities. In a recommendation system, this feature can be used to filter motherboards based on user-specified Wi-Fi standards or prioritize models supporting the latest wireless technologies.

**Sample Values:** ['Wi-Fi 7', 'NaN', 'Wi-Fi 6', 'NaN', 'Wi-Fi 7']

### raid_support
**Data Type:** text

**Description:** The `raid_support` feature in the `motherboard_specs` table indicates whether a motherboard supports RAID (Redundant Array of Independent Disks) functionality. This allows users to configure multiple storage drives for increased performance or data redundancy. A recommendation system could prioritize motherboards with RAID support for users explicitly seeking those features or targeting high-performance/data-critical builds.

**Sample Values:** ['Yes', 'Yes', 'Yes', 'Yes', 'Yes']

### onboard_ethernet
**Data Type:** text

**Description:** The `onboard_ethernet` feature details the integrated Ethernet controller on a motherboard, specifying the number of ports and supported data transfer speeds, often including the manufacturer (Intel, Realtek). In a recommendation system, this feature allows filtering for motherboards with specific Ethernet capabilities (e.g., 2.5GbE for faster network connections) or prioritizing models with a preferred controller manufacturer based on user preference or known reliability. This caters to users who require high-performance networking or have brand loyalty for Ethernet controllers.

**Sample Values:** ['1 x 2.5 Gb/s (Intel)', '1 x 2.5 Gb/s (Realtek Dragon RTL8125BG)', '1 x 2.5 Gb/s (Intel)', '1 x 1 Gb/s (Realtek RTL8111H)', '1 x 2.5 Gb/s (Intel)']

### sata_ports
**Data Type:** text

**Description:** The `sata_ports` feature in the `motherboard_specs` table represents the number of SATA (Serial ATA) ports available on a motherboard, stored as a text string (likely indicating an array or list of port counts). This data is crucial for determining storage compatibility; a recommendation system would use it to ensure suggested motherboards support the user's desired number of hard drives or SSDs. Filtering or sorting motherboards by `sata_ports` enables users to find options that meet their storage needs.

**Sample Values:** []

### m2_slots
**Data Type:** text

**Description:** The `m2_slots` feature describes the supported M.2 SSD form factors (e.g., 2280, 2242) and key types (M-key, E-key) available on a motherboard. This data is crucial for recommending motherboards compatible with specific M.2 SSDs based on their physical dimensions and protocol requirements. A recommendation system could filter for motherboards listing the user's desired M.2 form factor, ensuring compatibility and avoiding potential hardware conflicts.

**Sample Values:** ['2242/2260/2280/22110 M-key\n2242/2260/2280 M-key\n2242/2260/2280 M-key\n2280 M-key\n2280 M-key', '2280 M-key\n2280 M-key\n2230/2242/2260/2280 M-key\n2280 M-key\n2230 E-key', '2242/2260/2280/22110 M-key\n2242/2260/2280 M-key\n2242/2260/2280 M-key\n2242/2260/2280 M-key', '2260/2280/22110 M-key\n2242/2260/2280 M-key\n2230 E-key', '2260/2280 M-key\n2260/2280/22110 M-key\n2260/2280 M-key\n2260/2280 M-key\n2260/2280 M-key']

### usb_headers
**Data Type:** text

**Description:** The `usb_headers` feature in `motherboard_specs` describes the number and type (e.g., USB 2.0, USB 3.2 Gen 1) of internal USB headers available on a motherboard. This data is crucial for users planning to connect numerous USB devices through front panel connectors or internal peripherals, allowing a recommendation system to prioritize motherboards with sufficient headers based on user-defined device counts and required USB versions.  A lack of suitable headers can be a significant compatibility bottleneck.

**Sample Values:** []

### ecc_support
**Data Type:** text

**Description:** The `ecc_support` feature in the `motherboard_specs` table indicates whether a motherboard supports Error-Correcting Code (ECC) memory. This boolean-like text field (likely storing values like "Yes", "No", or potentially more granular details) signifies compatibility with ECC RAM, which enhances data integrity by detecting and correcting memory errors. A recommendation system would use this to filter motherboards for users building systems requiring high reliability, such as servers or scientific workstations.

**Sample Values:** []

### url
**Data Type:** text

**Description:** The `url` feature stores the direct link to a product page on PCPartPicker for a specific motherboard. This allows for easy redirection to detailed product information, user reviews, and pricing updates. Within a recommendation system, it serves as a critical link for displaying product details to the user and potentially fetching additional data via web scraping if needed.

**Sample Values:** ['https://pcpartpicker.com/product/rz4Zxr/asus-rog-maximus-z790-hero-btf-atx-lga1700-motherboard-rog-maximus-z790-hero-btf', 'https://pcpartpicker.com/product/tccBD3/asrock-b850-pro-a-atx-am5-motherboard-b850-pro-a', 'https://pcpartpicker.com/product/XQBG3C/asus-tuf-gaming-z690-plus-wifi-d4-atx-lga1700-motherboard-tuf-gaming-z690-plus-wifi-d4', 'https://pcpartpicker.com/product/T3XYcf/asrock-b550-pro4-atx-am4-motherboard-b550-pro4', 'https://pcpartpicker.com/product/Vqgrxr/msi-mpg-z790-carbon-wifi-ii-atx-lga1700-motherboard-mpg-z790-carbon-wifi-ii']

### model
**Data Type:** text

**Description:** The "model" feature in the `motherboard_specs` table represents the specific model name of a motherboard (e.g., "ASUS ROG Strix Z790-E Gaming WiFi"). Currently, the feature contains only "NaN" values, indicating missing data. Once populated, it would be crucial for filtering and matching motherboards based on user-specified models or compatibility requirements within a PC component recommendation system.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature in the `motherboard_specs` table represents the numerical price of each motherboard. This value is crucial for filtering motherboards based on budget constraints and for ranking recommendations based on price-performance ratio, allowing the system to suggest options aligned with a user's affordability and desired value. It enables both direct price-based filtering and more sophisticated optimization algorithms.

**Sample Values:** [903.7, 169.99, 259.99, 173.77, 269.99]

### score
**Data Type:** integer

**Description:** The "score" feature in the `motherboard_specs` table likely represents a composite rating or performance index calculated by aggregating various specifications and benchmark results. This score can be utilized in a recommendation system to rank motherboards based on overall suitability for a user's desired performance level, allowing for quick filtering and prioritized suggestions. Higher scores would indicate a generally more capable or feature-rich motherboard.

**Sample Values:** [77, 77, 88, 75, 90]


## PSU_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `psu_specs` table serves as a primary key, uniquely identifying each power supply unit entry in the database. It's an auto-incrementing integer, facilitating efficient data management and relationship building with other tables. In a recommendation system, this ID can be used to quickly retrieve specific PSU details when matching components based on compatibility and wattage requirements.

**Sample Values:** [842, 157, 5, 160, 186]

### name
**Data Type:** text

**Description:** The `name` feature stores the full product name of the power supply unit (PSU). This string provides a rich source of information, enabling keyword searches (e.g., "Corsair," "1000W," "Gold") and parsing for specific attributes like wattage, certification, and form factor. In a recommendation system, it's crucial for matching user search queries and providing detailed product identification.

**Sample Values:** ['Logisys PS480D 480 W ATX Power Supply', 'Corsair SF1000L 1000 W 80+ Gold Certified Fully Modular SFX Power Supply', 'MSI MAG A750GL PCIE5 750 W 80+ Gold Certified Fully Modular ATX Power Supply', 'SeaSonic Focus GX V4 ATX 3 (2024) 1000 W 80+ Gold Certified Fully Modular ATX Power Supply', 'EVGA SuperNOVA 1000 G6 1000 W 80+ Gold Certified Fully Modular ATX Power Supply']

### price
**Data Type:** text

**Description:** The "price" feature in the `psu_specs` table represents the retail price of a power supply unit, stored as a text string including a dollar sign. This feature is crucial for filtering and sorting PSUs based on budget constraints in a recommendation system, allowing users to find suitable options within a specified price range and enabling price-based ranking alongside performance metrics. It will require parsing to extract the numerical value for comparison and calculation.

**Sample Values:** ['$27.99', '$179.99', '$104.94', '$189.90', '$159.99']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores price and availability data from various retailers for a given PSU, using a JSONB data type to accommodate varying retailer sets. This allows for dynamic pricing comparisons and enables the recommendation system to prioritize PSUs with competitive prices and readily available stock, optimizing for user value and minimizing potential delays. Querying this field can also allow for displaying retailer-specific information directly to the user.

**Sample Values:** [{'Amazon': {'price': '$27.99', 'availability': 'In Stock'}}, {'Corsair': {'price': '$179.99', 'availability': 'Out of Stock'}}, {'B&H': {'price': '$91.25', 'availability': 'Out of Stock'}, 'MSI': {'price': '$99.99', 'availability': 'In Stock'}, 'Amazon': {'price': '$94.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$94.99', 'availability': 'In Stock'}, 'Adorama': {'price': '$104.94', 'availability': 'Unknown'}, 'Best Buy': {'price': '$94.99', 'availability': 'Out of Stock'}}, {'Amazon': {'price': '$189.90', 'availability': 'In Stock'}, 'Newegg': {'price': '$204.98', 'availability': 'Out of Stock'}}, {'Newegg': {'price': '$159.99', 'availability': 'Out of Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The `manufacturer` feature in the `psu_specs` table identifies the company that produced the power supply unit. This attribute is crucial for filtering and sorting PSUs based on brand preference, enabling users to select components from trusted or desired manufacturers. It can also be leveraged for compatibility checks and recommendations based on manufacturer-specific features or product lines.

**Sample Values:** ['Logisys', 'Corsair', 'MSI', 'SeaSonic', 'EVGA']

### part_number
**Data Type:** text

**Description:** The `part_number` feature in the `psu_specs` table represents the manufacturer's unique identifier for a specific power supply unit (PSU) model. It's crucial for accurate product identification and inventory management, allowing the recommendation system to match user selections with precise PSU models and ensuring compatibility checks with other components based on manufacturer specifications. This feature is essential for filtering and recommending PSUs based on user-selected brands and models.

**Sample Values:** ['PS480D', 'CP-9020246-NA\nCP-9020246-WW\nCP-9020246-AU\nCP-9020246-UK\nCP-9020246-EU', 'MAG A750GL PCIE5\n306-7ZP8B11-CE0', 'FOCUS-GX-1000-V4\nFocus V4 GX-1000', '220-G6-1000-X1']

### type
**Data Type:** text

**Description:** The "type" feature in the `psu_specs` table defines the physical form factor of the power supply unit. This categorization is crucial for compatibility, as it dictates the PSU's dimensions and connector placement, restricting it to specific case types. A recommendation system would use this feature to filter PSUs based on the user's chosen PC case form factor, ensuring a proper fit.

**Sample Values:** ['ATX', 'SFX', 'ATX', 'ATX', 'ATX']

### efficiency_rating
**Data Type:** text

**Description:** The `efficiency_rating` feature in the `psu_specs` table denotes the power supply unit's (PSU) efficiency certification level (e.g., 80+ Gold). This data represents the PSU's ability to deliver power efficiently, minimizing energy waste. A recommendation system could prioritize PSUs with higher efficiency ratings to reduce electricity costs and heat generation for users prioritizing energy-conscious builds.

**Sample Values:** ['NaN', '80+ Gold', '80+ Gold', '80+ Gold', '80+ Gold']

### wattage
**Data Type:** integer

**Description:** The "wattage" feature in the `psu_specs` table represents the maximum power output capacity of a power supply unit (PSU), measured in watts. This value is crucial for system compatibility and stability, as it dictates the total power draw of all connected components. A recommendation system would utilize wattage to ensure proposed PSUs are sufficiently powerful to support the user's selected CPU, GPU, and other peripherals, preventing instability or damage.

**Sample Values:** [480, 1000, 750, 1000, 1000]

### modular
**Data Type:** text

**Description:** The "modular" feature in the `psu_specs` table describes the level of modularity in a power supply unit (PSU). Values like "No," "Partial," or "Full" indicate whether all, some, or no cables are detachable, impacting cable management and airflow within a PC case. A recommendation system could prioritize PSUs with "Full" modularity for users seeking cleaner builds and improved cable routing.

**Sample Values:** ['No', 'Full', 'Full', 'Full', 'Full']

### color
**Data Type:** text

**Description:** The "color" feature in the `psu_specs` table represents the exterior color of the power supply unit (PSU). This categorical data allows filtering and sorting PSUs based on aesthetic preferences, enabling users to match PSU colors to their PC builds. The feature can be incorporated into recommendation systems by prioritizing PSUs that align with user-specified color schemes or overall build aesthetics.

**Sample Values:** ['NaN', 'Black', 'Black', 'Black', 'Black']

### fanless
**Data Type:** boolean

**Description:** The `fanless` feature in the `psu_specs` table indicates whether a power supply unit operates without an active cooling fan. This boolean value (True/False) signifies a passive cooling design, relying on heatsinks for heat dissipation. A recommendation system could leverage this to filter for quiet builds or prioritize PSUs suitable for noise-sensitive users, or those building in extremely compact cases with limited airflow.

**Sample Values:** [False, False, False, False, False]

### atx_connector
**Data Type:** text

**Description:** The `atx_connector` feature in the `psu_specs` table specifies the type and quantity of ATX power connectors (e.g., 24-pin, 4+4 pin) supported by a power supply unit. This data is crucial for compatibility checks during PC builds, as it directly informs whether a PSU can adequately power a motherboard and its connected components. A recommendation system can utilize this field to filter PSUs based on the motherboard's connector requirements, ensuring a valid and functional system.

**Sample Values:** []

### eps_connector
**Data Type:** text

**Description:** The `eps_connector` feature in the `psu_specs` table denotes the number and type (e.g., 8-pin, 12V) of EPS connectors provided by a power supply unit. This information is critical for compatibility with modern motherboards requiring EPS power for the CPU, and can be used in a recommendation system to ensure the PSU provides sufficient power delivery based on the user's chosen CPU and motherboard. A recommendation system should prioritize PSUs with appropriate EPS connector configurations based on these requirements.

**Sample Values:** []

### pcie_12v_connector
**Data Type:** text

**Description:** The `pcie_12v_connector` feature in the `psu_specs` table indicates the presence and quantity of dedicated 12V PCI Express power connectors available on a power supply unit (PSU). This is crucial for compatibility with high-end graphics cards that require supplemental power beyond the standard ATX connectors. A recommendation system could use this data to ensure a PSU is selected that provides sufficient 12V PCIe power for the user's intended GPU configuration.

**Sample Values:** []

### pcie_8pin_connector
**Data Type:** text

**Description:** The `pcie_8pin_connector` feature in the `psu_specs` table indicates whether a power supply unit (PSU) includes an 8-pin PCI Express connector. This connector provides power to graphics cards, and its presence/absence is crucial for compatibility checks during system builds. A recommendation system would utilize this feature to ensure suggested PSUs meet the power requirements of selected GPUs, preventing incompatibility errors.

**Sample Values:** []

### pcie_6plus2pin_connector
**Data Type:** text

**Description:** The `pcie_6plus2pin_connector` feature in the `psu_specs` table indicates the presence and number of 6+2 pin PCIe power connectors available on a power supply unit (PSU). This allows the recommendation system to filter PSUs based on the number of high-end graphics cards (GPUs) a user intends to install, ensuring compatibility with their power requirements. It's a crucial factor for systems demanding substantial GPU power.

**Sample Values:** []

### pcie_6pin_connector
**Data Type:** text

**Description:** The `pcie_6pin_connector` feature in the `psu_specs` table indicates the presence and quantity of PCI Express 6-pin connectors on a power supply unit (PSU). This data is crucial for determining PSU compatibility with graphics cards requiring auxiliary power via PCIe connectors, enabling the recommendation system to filter PSUs based on the power demands of a user's selected GPU. A recommendation system would use this value to ensure a suitable PSU is suggested, preventing potential compatibility issues and system instability.

**Sample Values:** []

### sata_connector
**Data Type:** text

**Description:** The `sata_connector` feature in the `psu_specs` table indicates the number of SATA power connectors present on a power supply unit (PSU). This value is crucial for determining compatibility with storage devices like HDDs and SSDs that require SATA power. A recommendation system would use this data to ensure the PSU has sufficient SATA connectors for the user's intended storage configuration.

**Sample Values:** []

### molex_4pin_connector
**Data Type:** text

**Description:** The `molex_4pin_connector` feature in the `psu_specs` table indicates the presence and quantity of Molex 4-pin connectors available on a power supply unit (PSU). This data is crucial for compatibility checks, particularly when recommending PSUs for builds utilizing older devices or peripherals that require this connector type. The system can filter or prioritize PSUs with this feature based on user-specified component requirements.

**Sample Values:** []

### length
**Data Type:** text

**Description:** The "length" feature in the `psu_specs` table represents the physical length of the power supply unit (PSU) in millimeters. This dimension is crucial for ensuring compatibility with PC cases; a recommendation system should filter PSUs based on this length to avoid fitment issues, preventing users from selecting units that are too long for their case. Accurate length data enhances the system's ability to provide functionally viable component suggestions.

**Sample Values:** ['150 mm', '130 mm', '140 mm', '140 mm', '140 mm']

### url
**Data Type:** text

**Description:** The `url` feature stores the direct web address of the corresponding power supply unit (PSU) listing, likely on a retailer or product comparison site like PCPartPicker. This URL can be leveraged to dynamically fetch up-to-date product details (pricing, availability, specifications) and display interactive links for users, enriching the recommendation system with real-time information and direct purchase pathways. It also enables automated scraping for feature enrichment if the database lacks certain details.

**Sample Values:** ['https://pcpartpicker.com/product/qnR48d/logisys-power-supply-ps480d', 'https://pcpartpicker.com/product/GMbRsY/corsair-sf1000l-1000-w-80-gold-certified-fully-modular-sfx-power-supply-cp-9020246-na', 'https://pcpartpicker.com/product/dbCZxr/msi-mag-a750gl-pcie5-750-w-80-gold-certified-fully-modular-atx-power-supply-mag-a750gl-pcie5', 'https://pcpartpicker.com/product/YkCZxr/seasonic-focus-gx-atx-30-v4-2024-1000-w-80-gold-certified-fully-modular-atx-power-supply-focus-gx-1000-v4', 'https://pcpartpicker.com/product/QdFbt6/evga-supernova-1000-g6-1000-w-80-gold-certified-fully-modular-atx-power-supply-220-g6-1000-x1']

### model
**Data Type:** text

**Description:** The "model" feature in the `psu_specs` table represents the specific product name or identifier of a power supply unit (PSU). This string data is crucial for differentiating PSU variations and allowing for precise matching against user selections or compatibility checks within a recommendation system; for example, ensuring a PSU's model is compatible with a specific motherboard or graphics card. Handling 'NaN' values appropriately (e.g., filtering or imputation) is necessary for accurate system building and recommendation.

**Sample Values:** ['NaN', 'SF1000L', 'NaN', 'NaN', 'SuperNOVA 1000 G6']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature in the `psu_specs` table represents the numerical price of a power supply unit. This value allows the recommendation system to filter and rank PSUs based on budget constraints, prioritize lower-cost options, or suggest alternatives within a defined price range for users. It's a crucial factor in price-sensitive component selection.

**Sample Values:** [27.99, 179.99, 104.94, 189.9, 159.99]

### score
**Data Type:** integer

**Description:** The "score" feature in the `psu_specs` table likely represents a composite performance rating or overall quality assessment of the power supply unit, calculated based on factors like efficiency, ripple suppression, and component quality. This numerical score can be directly incorporated into a recommendation system to prioritize higher-scoring PSUs based on user-defined preferences or to filter results, ensuring recommended PSUs meet a certain performance threshold. It provides a simplified, aggregated metric for evaluating PSU suitability.

**Sample Values:** [53, 84, 87, 84, 85]


## COOLER_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `cooler_specs` table is a primary key, uniquely identifying each individual cooler entry within the database. This integer identifier allows for efficient referencing and joining with other tables (like manufacturer or performance data) and is essential for accurate component matching and filtering within a PC component recommendation system. It ensures data integrity and facilitates the linking of cooler specifications to other related information.

**Sample Values:** [1, 79, 375, 374, 379]

### name
**Data Type:** text

**Description:** The `name` feature represents the full product identifier for a CPU cooler. It's a string containing the manufacturer and model name, crucial for uniquely identifying each cooler within the database. In a recommendation system, this feature enables precise matching to user selections, filtering by brand/model preference, and potentially extracting keywords for similarity-based recommendations (e.g., "RGB," "Liquid").

**Sample Values:** ['Thermalright Peerless Assassin 120 SE 66.17 CFM CPU Cooler', 'be quiet! Dark Rock Pro 4 50.5 CFM CPU Cooler', 'Corsair iCUE H150i RGB PRO XT 75 CFM Liquid CPU Cooler', 'Asus ROG Ryujin III 71.6 CFM Liquid CPU Cooler', 'Cooler Master Hyper 212 RGB Black Edition 59 CFM CPU Cooler']

### price
**Data Type:** text

**Description:** The "price" feature in `cooler_specs` represents the retail price of a cooler, stored as a text string including a currency symbol. This feature is crucial for budget-constrained PC builds; a recommendation system would leverage it to filter and rank coolers based on user-defined price limits or to suggest the best value options within a given price range. Further processing (e.g., extracting the numerical value) would be necessary for accurate comparisons and calculations.

**Sample Values:** ['$34.90', '$165.00', '$135.98', '$209.99', '$59.99']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores price and availability data for a cooler from various retailers in a JSONB format. This allows for querying the lowest price, identifying retailers with stock, or filtering recommendations based on budget and preferred vendor. It’s crucial for a recommendation system to dynamically offer components within a user’s price range and ensure availability for timely purchase.

**Sample Values:** [{'Amazon': {'price': '$34.90', 'availability': 'In Stock'}}, {'Amazon': {'price': '$165.00+', 'availability': 'In Stock'}}, {'GameStop': {'price': '$135.98', 'availability': 'Out of Stock'}}, {'B&H': {'price': '$209.99', 'availability': 'In Stock'}, 'ASUS': {'price': '$209.99', 'availability': 'In Stock'}, 'Amazon': {'price': '$209.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$209.99', 'availability': 'In Stock'}}, {'B&H': {'price': '$59.99', 'availability': 'In Stock'}, 'Amazon': {'price': '$95.44', 'availability': 'In Stock'}, 'Adorama': {'price': '$69.94', 'availability': 'Out of Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The "manufacturer" feature in the `cooler_specs` table identifies the company that produced the CPU cooler. This categorical data is crucial for filtering and sorting coolers based on user preference or brand loyalty. A recommendation system can leverage this to suggest coolers from a preferred manufacturer or compare performance across different brands.

**Sample Values:** ['Thermalright', 'be quiet!', 'Corsair', 'Asus', 'Cooler Master']

### part_number
**Data Type:** text

**Description:** The `part_number` feature represents a unique identifier assigned by the manufacturer to distinguish specific cooler models. This field is crucial for precisely identifying a component, enabling accurate matching with product listings, compatibility checks (e.g., socket type), and building a structured inventory for the recommendation system. It facilitates unambiguous component selection and allows for filtering and grouping coolers based on manufacturer and specific revision.

**Sample Values:** ['PA120 SE-D3\nPA120 SE\nPA120 SE D6-CAD\nPA120 SE 1700\nPA120 SE 1700-d6\n419043', 'BK022', 'CW-9060045-WW', '90RC00K0-M0UAY0\nROG RYUJIN III 240\n90RC00K0-M0AAY0', 'RR-212S-20PC-R2']

### fan_rpm
**Data Type:** text

**Description:** The `fan_rpm` feature in `cooler_specs` represents the rotational speed of the cooler's fan, expressed in revolutions per minute (RPM). This value, stored as text to accommodate ranges, directly impacts cooling performance and noise levels. A recommendation system could use `fan_rpm` to filter coolers based on desired noise profiles (lower RPM for quiet builds) or performance requirements (higher RPM for overclocking).

**Sample Values:** ['1550 RPM', '1500 RPM', '2400 RPM', '450 - 2000 RPM', '650 - 2000 RPM']

### noise_level
**Data Type:** text

**Description:** The `noise_level` feature in `cooler_specs` represents the acoustic output of a cooler, typically measured in decibels (dB). This data allows for filtering and ranking coolers based on user preference for quiet operation, and can be incorporated into a recommendation system to prioritize coolers with lower dB values for users prioritizing silent builds. Further analysis could involve parsing the string format to extract minimum and maximum noise levels for more granular comparisons.

**Sample Values:** ['25.6 dB', '12.8 - 24.3 dB', '37 dB', '29.7 dB', '8 - 30 dB']

### color
**Data Type:** text

**Description:** The "color" feature in the `cooler_specs` table describes the aesthetic coloration of the cooler, typically a combination of colors. This feature can be used in a recommendation system to filter coolers based on user-specified color preferences or to suggest complementary components based on a desired build theme. Representing color as text allows for nuanced descriptions beyond simple color names, accommodating multi-tone designs.

**Sample Values:** ['Black / Silver', 'Black', 'Black / White', 'Black', 'NaN']

### radiator_size
**Data Type:** text

**Description:** The `radiator_size` feature in the `cooler_specs` table specifies the dimensions of the radiator integrated into a liquid cooler. This data (e.g., "120mm x 240mm", "240mm x 280mm") is crucial for compatibility checks with PC cases and is essential for recommending coolers that fit within user-defined case constraints. The system can filter coolers based on this value to ensure a proper fit and avoid compatibility issues.

**Sample Values:** []

### bearing_type
**Data Type:** text

**Description:** The `bearing_type` feature in `cooler_specs` specifies the type of bearing used within a CPU cooler's fan (e.g., fluid dynamic bearing, ball bearing, sleeve bearing). This data point is crucial for assessing cooler longevity, noise levels, and overall performance, allowing a recommendation system to prioritize coolers with preferred bearing types based on user preferences (e.g., quiet operation, long lifespan). Filtering or ranking coolers based on `bearing_type` directly enhances the relevance of recommendations for users concerned with these specific characteristics.

**Sample Values:** []

### height
**Data Type:** text

**Description:** The "height" feature in `cooler_specs` represents the vertical dimension of a CPU cooler, typically measured in millimeters. This is a crucial constraint for PC builds as it dictates compatibility with available case space; a recommendation system should filter coolers based on this value to ensure proper fit and prevent clearance issues. Utilizing height allows for accurate recommendations aligned with user-specified case dimensions.

**Sample Values:** ['155 mm', '163 mm', 'NaN', '101 mm', '159 mm']

### cpu_socket
**Data Type:** text

**Description:** The `cpu_socket` feature indicates the compatible CPU socket type for a cooler. This allows for filtering coolers based on the user's CPU socket, ensuring compatibility and preventing incorrect purchases. In a recommendation system, it’s a critical attribute for matching coolers to specific CPU models and ensuring system functionality.

**Sample Values:** ['AM4\nAM5\nLGA1150\nLGA1151\nLGA1155\nLGA1156\nLGA1200\nLGA1700\nLGA1851', 'AM2\nAM2+\nAM3\nAM3+\nAM4\nAM5\nFM1\nFM2\nFM2+\nLGA1150\nLGA1151\nLGA1155\nLGA1156\nLGA1200\nLGA1366\nLGA1700\nLGA1851\nLGA2011\nLGA2011-3\nLGA2066', 'AM2\nAM2+\nAM3\nAM3+\nAM4\nAM5\nsTR4\nsTRX4\nFM1\nFM2\nFM2+\nLGA1150\nLGA1151\nLGA1155\nLGA1156\nLGA1200\nLGA1700\nLGA1851\nLGA2011\nLGA2011-3\nLGA2066', 'AM4\nAM5\nLGA1150\nLGA1151\nLGA1155\nLGA1156\nLGA1200\nLGA1700\nLGA1851', 'AM2\nAM2+\nAM3\nAM3+\nAM4\nAM5\nFM1\nFM2\nFM2+\nLGA1150\nLGA1151\nLGA1155\nLGA1156\nLGA1200\nLGA1366\nLGA1700\nLGA1851\nLGA2011\nLGA2011-3\nLGA2066']

### water_cooled
**Data Type:** boolean

**Description:** The `water_cooled` feature in `cooler_specs` indicates whether a cooler utilizes a liquid cooling system (True) or a traditional air cooling system (False). This boolean attribute allows the recommendation system to filter coolers based on user preferences for liquid cooling, ensuring compatibility with their desired build aesthetics and performance targets. It's a simple but crucial filter for building a PC with specific cooling requirements.

**Sample Values:** [False, False, False, False, False]

### fanless
**Data Type:** boolean

**Description:** The `fanless` feature in `cooler_specs` indicates whether a cooler operates without a fan, utilizing passive heat dissipation. This boolean value (True/False) allows the system to filter for coolers suited for silent builds or situations where fan noise is undesirable. The recommendation engine can prioritize fanless coolers when a user specifies a "silent" or "noise-free" build preference.

**Sample Values:** [False, False, False, False, False]

### url
**Data Type:** text

**Description:** The `url` feature in the `cooler_specs` table stores the direct link to the product page on PCPartPicker for each cooler. This allows for easy access to detailed product information, user reviews, and pricing updates directly from the source. In a recommendation system, it facilitates dynamic content retrieval and allows users to quickly verify specifications and purchase options.

**Sample Values:** ['https://pcpartpicker.com/product/hYxRsY/thermalright-peerless-assassin-120-se-6617-cfm-cpu-cooler-pa120-se-d3', 'https://pcpartpicker.com/product/F3gzK8/be-quiet-dark-rock-pro-4-505-cfm-cpu-cooler-bk022', 'https://pcpartpicker.com/product/Fnyqqs/corsair-icue-h150i-rgb-pro-xt-75-cfm-liquid-cpu-cooler-cw-9060045-ww', 'https://pcpartpicker.com/product/L74Zxr/asus-rog-ryujin-iii-716-cfm-liquid-cpu-cooler-90rc00k0-m0uay0', 'https://pcpartpicker.com/product/WHH7YJ/cooler-master-hyper-212-rgb-black-edition-59-cfm-cpu-cooler-rr-212s-20pc-r2']

### model
**Data Type:** text

**Description:** The 'model' feature in `cooler_specs` represents the specific product name or identifier for a CPU cooler. This string attribute is crucial for matching coolers to compatible CPUs and motherboards and is a primary key for linking to other related data (e.g., performance metrics, price). In a recommendation system, it allows for filtering based on user preference for specific brands or models and enables targeted suggestions based on compatibility and performance profiles.

**Sample Values:** ['Peerless Assassin 120 SE', 'Dark Rock Pro 4', 'iCUE H150i RGB PRO XT', 'NaN', 'Hyper 212 RGB Black Edition']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of a cooler, typically in USD. This value allows for price-based filtering and sorting within the database, and is crucial for recommending coolers based on a user's specified budget or preferred price range. It facilitates cost-effective recommendations and allows for price comparisons between different cooler models.

**Sample Values:** [34.9, 165.0, 135.98, 209.99, 59.99]

### score
**Data Type:** integer

**Description:** The "score" feature in the `cooler_specs` table likely represents a composite performance rating for a CPU cooler, aggregated from various factors like cooling capacity, noise levels, and ease of installation. This numerical value can be used in a recommendation system to rank coolers based on user-defined priorities (e.g., prioritize higher scores for optimal cooling or lower scores for quieter operation) or to filter results based on a minimum acceptable performance threshold. It offers a readily usable metric for comparative analysis without requiring individual component attribute weighting.

**Sample Values:** [53, 49, 46, 33, 62]


## CASE_SPECS

### id
**Data Type:** integer

**Description:** The `id` feature in the `case_specs` table serves as a unique primary key for each case entry, allowing for unambiguous identification. In a recommendation system, this ID can be used to efficiently join `case_specs` with other tables (e.g., user preferences, component compatibility) and retrieve related data for personalized case suggestions or filtering. Its integer data type enables fast indexing and joins, crucial for performance.

**Sample Values:** [992, 1057, 1342, 1054, 1055]

### name
**Data Type:** text

**Description:** The `name` feature in the `case_specs` table represents the full, human-readable product name of a computer case. This string data is crucial for displaying product details to users and can be used in a recommendation system by matching user search queries, enabling filtering by brand or model, and providing a clear product identifier for accurate results. It's also valuable for generating product titles and descriptions for display purposes.

**Sample Values:** ['Silverstone Sugo SG11 MicroATX Mini Tower Case', 'Okinos Aqua 3 MicroATX Mini Tower Case', 'GameMax F36 MicroATX Mini Tower Case', 'Corsair 4000D Airflow ATX Mid Tower Case', 'Fractal Design Terra Mini ITX Desktop Case']

### price
**Data Type:** text

**Description:** The "price" feature in the `case_specs` table represents the retail cost of a PC case, stored as a text string including the dollar sign. This feature is crucial for filtering and sorting case recommendations based on user budget constraints and can be used to calculate price ranges for bundle suggestions or to prioritize lower-cost alternatives within a given performance tier. Proper parsing and conversion to a numerical data type are necessary for accurate calculations and comparisons.

**Sample Values:** ['$118.42', '$66.98', '$44.17', '$104.00', '$179.99']

### retailer_prices
**Data Type:** jsonb

**Description:** The `retailer_prices` feature stores pricing and availability data from various retailers for a given PC case, utilizing a JSONB data type for flexibility. This allows for tracking price fluctuations and retailer-specific stock levels. In a recommendation system, it can be leveraged to prioritize cases with competitive pricing, real-time availability, and potentially predict price trends for informed purchasing decisions.

**Sample Values:** [{'Amazon': {'price': '$118.42+', 'availability': 'In Stock'}}, {'Amazon': {'price': '$66.98', 'availability': 'In Stock'}, 'Adorama': {'price': '$69.99', 'availability': 'Unknown'}}, {'Newegg': {'price': '$44.17', 'availability': 'In Stock'}}, {'B&H': {'price': '$104.00', 'availability': 'In Stock'}, 'Amazon': {'price': '$104.00', 'availability': 'In Stock'}, 'Newegg': {'price': '$104.00', 'availability': 'Out of Stock'}, 'Corsair': {'price': '$104.99', 'availability': 'Out of Stock'}}, {'B&H': {'price': '$179.99', 'availability': 'In Stock'}, 'Newegg': {'price': '$195.98', 'availability': 'In Stock'}, 'Adorama': {'price': '$209.99', 'availability': 'Unknown'}, 'Best Buy': {'price': '$179.99', 'availability': 'In Stock'}}]

### manufacturer
**Data Type:** text

**Description:** The `manufacturer` feature in the `case_specs` table identifies the company that produced the PC case. This attribute is crucial for filtering and recommending cases based on user preference for specific brands, enabling targeted suggestions based on brand loyalty or perceived quality associated with a manufacturer. It’s a categorical variable readily used in query filtering and collaborative filtering algorithms within a recommendation engine.

**Sample Values:** ['Silverstone', 'Okinos', 'GameMax', 'Corsair', 'Fractal Design']

### part_number
**Data Type:** text

**Description:** The `part_number` feature represents the manufacturer's unique identifier for a specific PC case model. It's crucial for inventory management and product differentiation, allowing for precise identification and matching of components. In a recommendation system, `part_number` is key for accurate product filtering, ensuring users receive recommendations for the exact case model they are seeking and preventing mismatched component compatibility.

**Sample Values:** ['SST-SG11B\nSG11B', 'OKICC-AQUA3-MATXB-H3BA', 'F36 BK', 'CC-9011201-WW', 'FD-C-TER1N-03']

### type
**Data Type:** text

**Description:** The "type" feature in the `case_specs` table describes the form factor and overall design of a computer case. This categorical data represents the physical size and shape constraints a PC build must adhere to, and is crucial for recommending compatible motherboards and other components. A recommendation system would use this field to filter cases based on the selected motherboard's form factor (e.g., recommending MicroATX cases for MicroATX motherboards).

**Sample Values:** ['MicroATX Mini Tower', 'MicroATX Mini Tower', 'MicroATX Mini Tower', 'ATX Mid Tower', 'Mini ITX Desktop']

### color
**Data Type:** text

**Description:** The "color" feature in the `case_specs` table defines the exterior color scheme of a PC case. This textual data allows for filtering and sorting case options based on user aesthetic preferences. Within a recommendation system, it can be used to prioritize cases matching a user's specified color preferences or to suggest complementary components based on a desired color palette.

**Sample Values:** ['Black', 'Black', 'Black', 'White', 'Green / Brown']

### power_supply
**Data Type:** text

**Description:** The `power_supply` feature in the `case_specs` table indicates whether the computer case includes a power supply unit (PSU) and, if so, potentially its wattage or model (though the current data is uniformly missing). In a recommendation system, this feature would be used to filter cases based on user preference for integrated or standalone PSUs, or to prioritize cases with sufficient wattage for a targeted build. The data's current state necessitates imputation or collection of specific PSU details for effective utilization.

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### side_panel
**Data Type:** text

**Description:** The `side_panel` feature in the `case_specs` table describes the material and construction of a computer case's side panels. This attribute is a text field allowing for varied descriptions like "Tempered Glass" or "Mesh." A recommendation system can leverage this data to filter cases based on user preferences (e.g., showcasing cases with tempered glass for aesthetics or mesh for improved airflow) or suggest compatible components considering side panel visibility/clearance.

**Sample Values:** ['NaN', 'Tempered Glass', 'Tempered Glass', 'Tinted Tempered Glass', 'Mesh']

### power_supply_shroud
**Data Type:** boolean

**Description:** The `power_supply_shroud` feature in `case_specs` indicates whether a PC case includes a dedicated shroud to conceal the power supply unit. This boolean value (True/False) helps users visually manage cable clutter and improve the aesthetics of their build. A recommendation system could prioritize cases with a shroud for users who value clean builds or specify a preference for improved cable management.

**Sample Values:** [False, True, True, True, False]

### front_panel_usb
**Data Type:** text

**Description:** The `front_panel_usb` feature in the `case_specs` table describes the USB ports available on the front panel of a computer case. This text field specifies the USB generation and connector type (e.g., Type-A, Type-C) for each port. A recommendation system could use this data to prioritize cases offering desired USB connectivity based on user preferences and peripherals.

**Sample Values:** ['USB 3.2 Gen 1 Type-A', 'USB 3.2 Gen 1 Type-A', 'USB 3.2 Gen 2 Type-C\nUSB 3.2 Gen 1 Type-A', 'USB 3.2 Gen 2 Type-C\nUSB 3.2 Gen 1 Type-A', 'USB 3.2 Gen 2x2 Type-C\nUSB 3.2 Gen 1 Type-A']

### motherboard_form_factor
**Data Type:** text

**Description:** The `motherboard_form_factor` feature stores the supported motherboard sizes a case can accommodate, represented as a comma-separated text string. This allows the recommendation system to filter cases based on the user's selected motherboard, ensuring compatibility and avoiding fitment issues. The system can also use this data to suggest motherboards that fit within a given case's supported form factors.

**Sample Values:** ['Micro ATX\nMini ITX\nMini DTX', 'Micro ATX\nMini ITX', 'Mini ITX', 'ATX\nEATX\nMicro ATX\nMini ITX', 'Mini ITX']

### maximum_video_card_length
**Data Type:** text

**Description:** The `maximum_video_card_length` feature in the `case_specs` table defines the longest graphics card (GPU) that can physically fit within a given computer case. This value, expressed in millimeters and inches, is crucial for compatibility checks and is a primary constraint in a PC component recommendation system to ensure the selected GPU doesn't exceed the case's physical limitations. It's a key attribute to filter case recommendations based on desired GPU size.

**Sample Values:** ['369 mm / 14.528"', '330 mm / 12.992"', '350 mm / 13.78"', '360 mm / 14.173"', '322 mm / 12.677"']

### drive_bays
**Data Type:** text

**Description:** The `drive_bays` feature in `case_specs` describes the number and type of drive bays available within a computer case, indicating storage device compatibility. This data allows a recommendation system to filter cases based on user-specified storage needs (e.g., recommending cases with sufficient 3.5" bays for HDDs or 2.5" bays for SSDs).  It's a crucial factor for ensuring compatibility and preventing user frustration with storage device installation.

**Sample Values:** ['1 x External 5.25"\n3 x Internal 3.5"\n9 x Internal 2.5"', '2 x Internal 3.5"\n1 x Internal 2.5"', '3 x Internal 2.5"\n2 x Internal 3.5"', '2 x Internal 3.5"\n2 x Internal 2.5"', '2 x Internal 2.5"']

### expansion_slots
**Data Type:** text

**Description:** The `expansion_slots` feature in the `case_specs` table details the number and type of expansion slots available within a PC case, typically referring to PCIe slots for graphics cards and other add-in cards. This data is crucial for compatibility checks within a recommendation system; it allows filtering cases based on the number of expansion cards a user intends to install and ensuring compatibility with their desired hardware configuration. It can also be used to highlight cases suitable for multi-GPU setups or specialized expansion cards.

**Sample Values:** ['4 x Full-Height', '4 x Full-Height', '4 x Full-Height', '7 x Full-Height\n2 x Full-Height via Riser', '3 x Full-Height via Riser']

### dimensions
**Data Type:** text

**Description:** The "dimensions" feature in the `case_specs` table represents the physical size of a PC case, recorded as a text string containing both millimeters and inches. This data is crucial for compatibility checks within a recommendation system, ensuring suggested components (motherboards, GPUs, etc.) fit physically within the selected case, preventing build failures and ensuring optimal airflow. The string format necessitates parsing logic for accurate comparison and filtering.

**Sample Values:** ['NaN', '350 mm x 210 mm x 392 mm\n13.78" x 8.268" x 15.433"', '419 mm x 216 mm x 388 mm\n16.496" x 8.504" x 15.276"', '453 mm x 230 mm x 466 mm\n17.835" x 9.055" x 18.346"', '343 mm x 153 mm x 218 mm\n13.504" x 6.024" x 8.583"']

### volume
**Data Type:** text

**Description:** The "volume" feature in the `case_specs` table represents the internal capacity of a PC case, typically expressed in liters (L) and cubic feet (ft³). This data is crucial for compatibility checks within a recommendation system, ensuring components like GPUs and radiators fit comfortably within the selected case, preventing physical constraints and promoting optimal system design. The system can filter cases based on component size requirements or suggest cases with ample volume for future upgrades.

**Sample Values:** ['NaN', '28.812 L\n1.017 ft³', '35.116 L\n1.24 ft³', '48.553 L\n1.715 ft³', '11.44 L\n0.404 ft³']

### url
**Data Type:** text

**Description:** The `url` feature stores the direct web address of the corresponding PC case listing on PCPartPicker. This allows for external referencing and provides a reliable link to detailed product information, specifications, and pricing not stored within the database itself. In a recommendation system, this URL can be used to display product pages for users, enable dynamic pricing updates, or facilitate affiliate marketing.

**Sample Values:** ['https://pcpartpicker.com/product/YLDzK8/silverstone-case-sstsg11b', 'https://pcpartpicker.com/product/FfQKHx/okinos-aqua-3-microatx-mini-tower-case-okicc-aqua3-matxb-h3ba', 'https://pcpartpicker.com/product/wwxxFT/gamemax-f36-microatx-mini-tower-case-f36-bk', 'https://pcpartpicker.com/product/WBVG3C/corsair-4000d-airflow-atx-mid-tower-case-cc-9011201-ww', 'https://pcpartpicker.com/product/rpKscf/fractal-design-terra-mini-itx-desktop-case-fd-c-ter1n-03']

### model
**Data Type:** text

**Description:** The 'model' feature in the `case_specs` table represents the specific model name of a PC case. Currently, it contains mostly missing values ("NaN"), indicating a data quality issue that needs addressing.  This feature is crucial for filtering and matching cases based on user preference or compatibility requirements (e.g., "I need a Fractal Design Meshify 2").

**Sample Values:** ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']

### price_num
**Data Type:** numeric

**Description:** The `price_num` feature represents the numerical price of a computer case, stored as a numeric data type. This value is crucial for filtering and sorting cases based on budget constraints and can be incorporated into recommendation algorithms to suggest cases that align with a user's specified price range or offer the best value for money. It allows for price-based comparisons and ranking within the component database.

**Sample Values:** [118.42, 66.98, 44.17, 104.0, 179.99]

### score
**Data Type:** integer

**Description:** The "score" feature in the `case_specs` table likely represents a composite rating or evaluation of the PC case, potentially derived from user reviews, expert opinions, or a weighted combination of various specifications. This numerical score can be utilized within a recommendation system to prioritize cases with higher scores, allowing for quick filtering and ranking based on overall desirability and user satisfaction. It provides a simplified metric for algorithmic comparison, supplementing individual specification data.

**Sample Values:** [69, 78, 83, 88, 45]

