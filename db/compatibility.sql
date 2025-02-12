-- db/compatibility.sql

/**
 * Function: get_compatible_motherboards
 * Purpose: Returns all motherboards that are compatible with a given CPU
 * Compatibility checks:
 * - CPU socket type matches motherboard socket
 * - Memory type support matches between CPU and motherboard
 * Parameters:
 * @param cpu_id - The ID of the CPU to find compatible motherboards for
 * Returns: Table of compatible motherboards with their specifications
 */
CREATE OR REPLACE FUNCTION get_compatible_motherboards(cpu_id int)
RETURNS TABLE (
    id int,
    name varchar,
    price numeric,
    socket varchar,
    form_factor varchar,
    max_memory int,
    memory_slots int,
    color varchar,
    memory_type varchar,
    supported_memory_speeds int[],
    chipset varchar,
    pcie_version varchar,
    max_pcie_lanes int,
    m2_slots int,
    sata_ports int
) AS $$
BEGIN
    -- Join CPU and motherboard tables on socket type
    -- Filter for matching memory type support
    RETURN QUERY
    SELECT m.*
    FROM cpu c
    JOIN motherboard m ON m.socket = c.socket_type
    WHERE c.id = cpu_id
      AND m.memory_type = c.memory_type_support;
END;
$$ LANGUAGE plpgsql;


/**
 * Function: get_compatible_cpu_coolers
 * Purpose: Finds CPU coolers that are compatible with a given CPU
 * Compatibility checks:
 * - Socket type compatibility
 * - TDP (Thermal Design Power) support
 * Parameters:
 * @param cpu_id - The ID of the CPU to find compatible coolers for
 * Returns: Table of compatible CPU coolers with their specifications
 * Error handling: Raises exception if CPU socket information is not found
 */
CREATE OR REPLACE FUNCTION get_compatible_cpu_coolers(cpu_id int)
RETURNS TABLE (
    id int,
    name varchar,
    price numeric,
    rpm text,
    noise_level text,
    color varchar,
    size numeric,
    supported_sockets text[],
    height numeric,
    tdp_support int,
    radiator_size varchar,
    clearance_required numeric
) AS $$
DECLARE
    cpu_socket text;
    cpu_tdp int;
BEGIN
    -- Retrieve CPU socket type and TDP requirements
    SELECT socket_type::text, tdp INTO cpu_socket, cpu_tdp 
    FROM cpu 
    WHERE cpu.id = cpu_id;

    -- Validate CPU exists
    IF cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU socket not found for ID %', cpu_id;
    END IF;

    -- Return compatible coolers based on socket and TDP requirements
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.price,
        c.rpm::text,
        c.noise_level::text,
        c.color,
        c.size,
        c.supported_sockets,
        c.height,
        c.tdp_support,
        c.radiator_size,
        c.clearance_required
    FROM cpu_cooler c
    WHERE EXISTS (
        -- Check if CPU socket is in cooler's supported sockets array
        SELECT 1
        FROM unnest(c.supported_sockets) socket
        WHERE socket = cpu_socket
    )
    -- Ensure cooler can handle CPU's TDP (if specified)
    AND (c.tdp_support >= cpu_tdp OR cpu_tdp IS NULL)
    ORDER BY c.price ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;


/**
 * Function: get_compatible_video_cards
 * Purpose: Finds graphics cards compatible with a given motherboard
 * Compatibility checks:
 * - PCIe version compatibility
 * - Available PCIe lanes
 * Parameters:
 * @param mobo_id - The ID of the motherboard to find compatible GPUs for
 * Returns: Table of compatible graphics cards with their specifications
 */
CREATE OR REPLACE FUNCTION get_compatible_video_cards(mobo_id int)
RETURNS TABLE (
    id int,
    name varchar,
    price numeric,
    chipset varchar,
    memory numeric,
    core_clock numeric,
    boost_clock numeric,
    color varchar,
    length numeric,
    tdp int,
    required_psu_wattage int,
    pcie_version varchar,
    pcie_lanes_required int,
    height numeric,
    power_connectors text[]
) AS $$
BEGIN
    -- Join video cards with motherboard on PCIe version
    -- Ensure motherboard has enough PCIe lanes
    RETURN QUERY
    SELECT v.*
    FROM video_card v
    JOIN motherboard m ON m.pcie_version = v.pcie_version
    WHERE m.id = mobo_id
      AND m.max_pcie_lanes >= v.pcie_lanes_required;
END;
$$ LANGUAGE plpgsql;


/**
 * Function: get_compatible_case
 * Purpose: Finds PC cases that can physically accommodate a given GPU
 * Compatibility checks:
 * - GPU length vs case maximum GPU length
 * Parameters:
 * @param gpu_id - The ID of the GPU to find compatible cases for
 * Returns: Table of compatible cases with their specifications
 * Error handling: 
 * - Validates GPU exists
 * - Checks for required GPU length information
 */
CREATE OR REPLACE FUNCTION get_compatible_case(gpu_id int)
RETURNS TABLE (
    case_id int,
    case_name varchar,
    case_price numeric,
    case_type varchar,
    case_color varchar,
    case_psu numeric,
    case_side_panel varchar,
    case_external_volume numeric,
    case_internal_35_bays int,
    case_max_gpu_length numeric,
    case_max_gpu_height numeric,
    case_max_cpu_cooler_height numeric,
    case_supported_motherboard_sizes text[],
    case_max_psu_length numeric,
    case_radiator_support text[],
    case_included_fans int,
    case_max_fan_slots int,
    case_max_radiator_size int
) AS $$
DECLARE
    gpu_length numeric;
    gpu_exists boolean;
BEGIN
    -- Validate GPU exists in database
    SELECT EXISTS (
        SELECT 1 FROM video_card WHERE video_card.id = gpu_id
    ) INTO gpu_exists;

    IF NOT gpu_exists THEN
        RAISE EXCEPTION 'GPU with ID % does not exist', gpu_id;
    END IF;

    -- Get GPU length for compatibility check
    SELECT v.length INTO gpu_length 
    FROM video_card v 
    WHERE v.id = gpu_id;

    -- Ensure GPU length information is available
    IF gpu_length IS NULL THEN
        RAISE EXCEPTION 'GPU length information is not available for GPU ID %', gpu_id;
    END IF;

    -- Return cases that can fit the GPU
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.price,
        c.type,
        c.color,
        c.psu,
        c.side_panel,
        c.external_volume,
        c.internal_35_bays,
        c.max_gpu_length,
        c.max_gpu_height,
        c.max_cpu_cooler_height,
        c.supported_motherboard_sizes,
        c.max_psu_length,
        c.radiator_support,
        c.included_fans,
        c.max_fan_slots,
        c.max_radiator_size
    FROM case_enclosure c
    WHERE c.max_gpu_length >= gpu_length
        AND c.max_gpu_length IS NOT NULL
    ORDER BY c.price ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;


/**
 * Function: get_compatible_psu
 * Purpose: Finds power supplies that meet system requirements and fit in the case
 * Compatibility checks:
 * - Minimum required wattage
 * - Form factor compatibility with case
 * - Physical size constraints
 * Parameters:
 * @param required_wattage - The minimum wattage needed for the system
 * @param case_id - The ID of the case to check PSU compatibility with
 * Returns: Table of compatible power supplies with their specifications
 * Error handling: Validates case exists
 */
CREATE OR REPLACE FUNCTION get_compatible_psu(required_wattage int, case_id int)
RETURNS TABLE (
    id int,
    name varchar,
    price numeric,
    type varchar,
    efficiency varchar,
    wattage int,
    modular varchar,
    color varchar,
    available_connectors jsonb,
    psu_length numeric,
    fan_size int,
    protection_features text[],
    atx_version varchar
) AS $$
DECLARE
    case_exists boolean;
    case_form_factor varchar;
    case_max_psu_length numeric;
    compatible_psu_type varchar;
BEGIN
    -- Get case information and validate it exists
    SELECT 
        EXISTS (SELECT 1 FROM case_enclosure c WHERE c.id = case_id),
        c.type,
        c.max_psu_length
    INTO 
        case_exists,
        case_form_factor,
        case_max_psu_length
    FROM case_enclosure c
    WHERE c.id = case_id;

    IF NOT case_exists THEN
        RAISE EXCEPTION 'Case with ID % does not exist', case_id;
    END IF;

    -- Map case form factor to compatible PSU type
    IF case_form_factor LIKE 'ATX%' THEN
        compatible_psu_type := 'ATX';
    ELSIF case_form_factor LIKE 'Mini ITX%' THEN
        compatible_psu_type := 'SFX';
    ELSIF case_form_factor LIKE 'MicroATX%' THEN
        compatible_psu_type := 'ATX';
    ELSIF case_form_factor = 'HTPC' THEN
        compatible_psu_type := 'TFX';
    ELSE
        compatible_psu_type := 'ATX'; -- Default to ATX for unknown types
    END IF;

    -- Return compatible PSUs based on wattage and form factor
    RETURN QUERY
    SELECT p.*
    FROM power_supply p
    WHERE p.wattage >= required_wattage
    AND (
        -- Check PSU compatibility based on form factor mapping
        CASE 
            WHEN compatible_psu_type = 'ATX' THEN
                p.type = 'ATX'
            WHEN compatible_psu_type = 'SFX' THEN
                p.type IN ('SFX', 'Mini ITX')
            WHEN compatible_psu_type = 'TFX' THEN
                p.type IN ('TFX', 'Flex ATX')
            ELSE 
                FALSE
        END
    );
END;
$$ LANGUAGE plpgsql;


/**
 * Function: get_compatible_ram
 * Purpose: Finds RAM modules compatible with both motherboard and CPU
 * Compatibility checks:
 * - DDR version compatibility
 * - Memory speed support
 * - Memory type matching
 * Parameters:
 * @param mobo_id - The ID of the motherboard
 * @param cpu_id - The ID of the CPU
 * Returns: Table of compatible RAM modules with their specifications
 * Error handling: 
 * - Validates both CPU and motherboard exist
 * - Checks memory specifications are available
 */
CREATE OR REPLACE FUNCTION get_compatible_ram(mobo_id int, cpu_id int)
RETURNS TABLE (
    id int,
    name varchar,
    price numeric,
    speed varchar,
    modules varchar,
    price_per_gb numeric,
    color varchar,
    first_word_latency numeric,
    cas_latency numeric,
    voltage numeric,
    memory_format varchar,
    ecc_support boolean,
    ddr_version int,
    memory_speed int
) AS $$
DECLARE
    mobo_memory_type varchar;
    mobo_supported_speeds varchar;
    cpu_memory_type varchar;
    cpu_memory_speed float;
    cpu_exists boolean;
    mobo_exists boolean;
BEGIN
    -- Validate CPU exists
    SELECT EXISTS (
        SELECT 1 FROM cpu WHERE cpu.id = cpu_id
    ) INTO cpu_exists;

    IF NOT cpu_exists THEN
        RAISE EXCEPTION 'CPU with ID % does not exist', cpu_id;
    END IF;

    -- Validate motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard WHERE motherboard.id = mobo_id
    ) INTO mobo_exists;

    IF NOT mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Get memory specifications from both CPU and motherboard
    SELECT m.memory_type, m.supported_memory_speeds,
           c.memory_type_support, c.memory_speed_support
    INTO mobo_memory_type, mobo_supported_speeds,
         cpu_memory_type, cpu_memory_speed
    FROM motherboard m
    CROSS JOIN cpu c
    WHERE m.id = mobo_id AND c.id = cpu_id;

    -- Return compatible RAM modules based on all constraints
    RETURN QUERY
    SELECT m.*
    FROM memory m
    WHERE 
        -- Match DDR version with motherboard
        concat('DDR', m.ddr_version) = mobo_memory_type
        -- Ensure memory speed is supported by motherboard
        AND m.memory_speed::text = ANY(string_to_array(mobo_supported_speeds, ','))
        -- Match memory type with CPU support
        AND concat('DDR', m.ddr_version) = cpu_memory_type
        -- Ensure memory speed doesn't exceed CPU's maximum supported speed
        AND m.memory_speed <= cpu_memory_speed;
END;
$$ LANGUAGE plpgsql;