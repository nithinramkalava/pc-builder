-- db/compatibility.sql
-- Stored function to fetch motherboards compatible with a given CPU.
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
    RETURN QUERY
    SELECT m.*
    FROM cpu c
    JOIN motherboard m ON m.socket = c.socket_type
    WHERE c.id = cpu_id
      AND m.memory_type = c.memory_type_support;
END;
$$ LANGUAGE plpgsql;


-- Stored function to fetch CPU coolers compatible with a given CPU’s socket.
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
    -- Get the CPU socket type and TDP
    SELECT socket_type::text, tdp INTO cpu_socket, cpu_tdp 
    FROM cpu 
    WHERE cpu.id = cpu_id;

    IF cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU socket not found for ID %', cpu_id;
    END IF;

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
        SELECT 1
        FROM unnest(c.supported_sockets) socket
        WHERE socket = cpu_socket
    )
    AND (c.tdp_support >= cpu_tdp OR cpu_tdp IS NULL)
    ORDER BY c.price ASC NULLS LAST;

END;
$$ LANGUAGE plpgsql;


-- Stored function to fetch video cards compatible with a given motherboard.
-- This function uses the motherboard's PCIe version and maximum available lanes.
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
    RETURN QUERY
    SELECT v.*
    FROM video_card v
    JOIN motherboard m ON m.pcie_version = v.pcie_version
    WHERE m.id = mobo_id
      AND m.max_pcie_lanes >= v.pcie_lanes_required;
END;
$$ LANGUAGE plpgsql;



-- Stored function to fetch cases compatible with a given GPU (by checking physical length).
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
    -- Check if GPU exists
    SELECT EXISTS (
        SELECT 1 FROM video_card WHERE video_card.id = gpu_id
    ) INTO gpu_exists;

    IF NOT gpu_exists THEN
        RAISE EXCEPTION 'GPU with ID % does not exist', gpu_id;
    END IF;

    -- Get GPU length
    SELECT v.length INTO gpu_length 
    FROM video_card v 
    WHERE v.id = gpu_id;

    -- Handle null GPU length
    IF gpu_length IS NULL THEN
        RAISE EXCEPTION 'GPU length information is not available for GPU ID %', gpu_id;
    END IF;

    -- Return compatible cases
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



-- Stored function to fetch PSUs compatible based on a minimum required wattage.
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
    -- Check if case exists and get its type
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

    -- Determine compatible PSU type based on case form factor
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

    RETURN QUERY
    SELECT p.*
    FROM power_supply p
    WHERE p.wattage >= required_wattage
    AND (
        -- Check PSU compatibility based on mapped type
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
    -- Check if CPU exists
    SELECT EXISTS (
        SELECT 1 FROM cpu WHERE cpu.id = cpu_id
    ) INTO cpu_exists;

    IF NOT cpu_exists THEN
        RAISE EXCEPTION 'CPU with ID % does not exist', cpu_id;
    END IF;

    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard WHERE motherboard.id = mobo_id
    ) INTO mobo_exists;

    IF NOT mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Get CPU and motherboard memory specifications
    SELECT m.memory_type, m.supported_memory_speeds,
           c.memory_type_support, c.memory_speed_support
    INTO mobo_memory_type, mobo_supported_speeds,
         cpu_memory_type, cpu_memory_speed
    FROM motherboard m
    CROSS JOIN cpu c
    WHERE m.id = mobo_id AND c.id = cpu_id;

    RETURN QUERY
    SELECT m.*
    FROM memory m
    WHERE 
        -- Check DDR version compatibility with motherboard
        concat('DDR', m.ddr_version) = mobo_memory_type
        -- Check if memory speed is supported by motherboard (using string_to_array to convert comma-separated string)
        AND m.memory_speed::text = ANY(string_to_array(mobo_supported_speeds, ','))
        -- Check if memory type matches CPU's supported type
        AND concat('DDR', m.ddr_version) = cpu_memory_type
        -- Check if memory speed doesn't exceed CPU's max speed
        AND m.memory_speed <= cpu_memory_speed;

END;
$$ LANGUAGE plpgsql;
