-- db/new_compatibility.sql
-- Stored function to fetch motherboards compatible with a given CPU.
CREATE OR REPLACE FUNCTION get_compatible_motherboards(cpu_id int)

RETURNS TABLE (
    id int,
    name text,
    price text,
    form_factor text,
    socket_cpu text,
    memory_max text,
    memory_slots int,
    memory_type text,
    memory_speed text,
    chipset text,
    color text,
    m2_slots text,
    sata_ports text
) AS $$
DECLARE
    cpu_socket text;
    cpu_memory_type text;
BEGIN
    -- Get the CPU socket type and memory type
    SELECT socket, 
           CASE 
               WHEN maximum_supported_memory LIKE '%DDR5%' THEN 'DDR5'
               WHEN maximum_supported_memory LIKE '%DDR4%' THEN 'DDR4'
               ELSE 
                  CASE 
                      WHEN tdp LIKE '%DDR5%' THEN 'DDR5'  -- Try to find in other fields
                      WHEN tdp LIKE '%DDR4%' THEN 'DDR4'
                      ELSE 'DDR5'  -- Default to latest memory type
                  END
           END INTO cpu_socket, cpu_memory_type
    FROM cpu_specs
    WHERE cpu_specs.id = cpu_id;

    IF cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU with ID % not found or socket information missing', cpu_id;
    END IF;

    RETURN QUERY
    SELECT m.id, m.name, m.price, m.form_factor, m.socket_cpu, 
           m.memory_max, m.memory_slots, m.memory_type, m.memory_speed,
           m.chipset, m.color, m.m2_slots, m.sata_ports
    FROM motherboard_specs m
    WHERE m.socket_cpu = cpu_socket;
    --   AND (m.memory_type = cpu_memory_type OR 
    --       (cpu_memory_type = 'DDR5' AND m.memory_type LIKE '%DDR5%') OR
    --       (cpu_memory_type = 'DDR4' AND m.memory_type LIKE '%DDR4%'));
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch CPU coolers compatible with a given CPU's socket.
CREATE OR REPLACE FUNCTION get_compatible_cpu_coolers(cpu_id int)
RETURNS TABLE (
    id int,
    name text,
    price text,
    fan_rpm text,
    noise_level text,
    color text,
    radiator_size text,
    height text,
    cpu_socket text,
    water_cooled boolean,
    fanless boolean
) AS $$
DECLARE
    cpu_socket text;
    cpu_tdp numeric;
    socket_pattern text;
BEGIN
    -- Get the CPU socket type and TDP
    SELECT cs.socket, 
           CASE 
               WHEN cs.tdp ~ '^[0-9]+(\.[0-9]+)?$' THEN cs.tdp::numeric
               WHEN cs.tdp ~ '^[0-9]+' THEN (regexp_match(cs.tdp, '^[0-9]+'))[1]::numeric
               ELSE NULL
           END INTO cpu_socket, cpu_tdp
    FROM cpu_specs cs
    WHERE cs.id = cpu_id;

    IF cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU socket not found for ID %', cpu_id;
    END IF;
    
    -- Normalize socket name for pattern matching
    -- For example, AM5 should match 'AM5' exactly or as part of a list
    socket_pattern := '(^|[^A-Za-z0-9])' || cpu_socket || '([^A-Za-z0-9]|$)';

    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.price,
        c.fan_rpm,
        c.noise_level,
        c.color,
        c.radiator_size,
        c.height,
        c.cpu_socket,
        c.water_cooled,
        c.fanless
    FROM cooler_specs c
    WHERE c.cpu_socket ~ socket_pattern
    ORDER BY 
        CASE 
            WHEN c.price ~ '^\\$?[0-9]+(\.[0-9]+)?$' THEN 
                (regexp_replace(c.price, '\\$', ''))::numeric 
            ELSE NULL 
        END ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch video cards compatible with a given motherboard.
-- This function considers PCIe interface compatibility where PCIe x16 supports x8, x4, x1 but not vice versa
CREATE OR REPLACE FUNCTION get_compatible_video_cards(mobo_id int)
RETURNS TABLE (
    id int,
    name text,
    price text,
    chipset text,
    memory text,
    core_clock text,
    boost_clock text,
    color text,
    length text,
    tdp text,
    interface text
) AS $$
DECLARE
    mobo_exists boolean;
    mobo_pci_slots text;
    mobo_max_pcie_value int := 1; -- Default to lowest PCIe value
BEGIN
    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs WHERE motherboard_specs.id = mobo_id
    ), pci_slots INTO mobo_exists, mobo_pci_slots
    FROM motherboard_specs
    WHERE id = mobo_id;

    IF NOT mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Determine the maximum PCIe lanes supported by the motherboard
    -- First check in pci_slots field
    IF mobo_pci_slots IS NOT NULL THEN
        IF mobo_pci_slots LIKE '%PCIe x16%' THEN
            mobo_max_pcie_value := 16;
        ELSIF mobo_pci_slots LIKE '%PCIe x8%' THEN
            mobo_max_pcie_value := 8;
        ELSIF mobo_pci_slots LIKE '%PCIe x4%' THEN
            mobo_max_pcie_value := 4;
        END IF;
    ELSE
        -- If not found, assume most motherboards support x16
        mobo_max_pcie_value := 16;
    END IF;

    RETURN QUERY
    SELECT 
        g.id,
        g.name,
        g.price,
        g.chipset,
        g.memory,
        g.core_clock,
        g.boost_clock,
        g.color,
        g.length,
        g.tdp,
        g.interface
    FROM gpu_specs g
    WHERE 
        -- Filter GPUs based on PCIe compatibility
        CASE 
            -- If GPU requires PCIe x16, motherboard must support x16
            WHEN g.interface LIKE '%PCIe x16%' AND mobo_max_pcie_value >= 16 THEN true
            -- If GPU requires PCIe x8, motherboard must support at least x8
            WHEN g.interface LIKE '%PCIe x8%' AND mobo_max_pcie_value >= 8 THEN true
            -- If GPU requires PCIe x4, motherboard must support at least x4
            WHEN g.interface LIKE '%PCIe x4%' AND mobo_max_pcie_value >= 4 THEN true
            -- If GPU requires PCIe x1, almost all motherboards support it
            WHEN g.interface LIKE '%PCIe x1%' THEN true
            -- For other cases or when interface is not specified, include them
            WHEN g.interface IS NULL OR g.interface = '' THEN true
            -- Default case to handle variations in PCIe formatting
            WHEN g.interface LIKE '%PCIe%' THEN true
            ELSE false
        END
    ORDER BY 
        CASE 
            WHEN g.price ~ '^\\$?[0-9]+(\.[0-9]+)?$' THEN 
                (regexp_replace(g.price, '\\$', ''))::numeric 
            ELSE NULL 
        END ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch cases compatible with a given GPU (by checking physical length).
-- Updated to handle more variations in length formatting
CREATE OR REPLACE FUNCTION get_compatible_case(gpu_id int)
RETURNS TABLE (
    id int,
    name text,
    price text,
    type text,
    color text,
    power_supply text,
    side_panel text,
    motherboard_form_factor text,
    maximum_video_card_length text
) AS $$
DECLARE
    gpu_length_mm numeric;
    gpu_length_text text;
    gpu_exists boolean;
BEGIN
    -- Check if GPU exists
    SELECT EXISTS (
        SELECT 1 FROM gpu_specs WHERE gpu_specs.id = gpu_id
    ) INTO gpu_exists;

    IF NOT gpu_exists THEN
        RAISE EXCEPTION 'GPU with ID % does not exist', gpu_id;
    END IF;

    -- Get GPU length
    SELECT g.length INTO gpu_length_text
    FROM gpu_specs g
    WHERE g.id = gpu_id;

    -- Extract numeric length value with improved pattern matching
    IF gpu_length_text ~ '([0-9]+(\.[0-9]+)?).*mm' THEN
        gpu_length_mm := (regexp_match(gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric;
    ELSIF gpu_length_text ~ '([0-9]+(\.[0-9]+)?).*in' THEN
        -- Convert inches to mm (1 inch = 25.4 mm)
        gpu_length_mm := (regexp_match(gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric * 25.4;
    ELSIF gpu_length_text ~ '([0-9]+(\.[0-9]+)?)' THEN
        gpu_length_mm := (regexp_match(gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric;
    ELSE
        RAISE EXCEPTION 'GPU length information is not available or not in expected format for GPU ID %', gpu_id;
    END IF;

    -- Return compatible cases
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.price,
        c.type,
        c.color,
        c.power_supply,
        c.side_panel,
        c.motherboard_form_factor,
        c.maximum_video_card_length
    FROM case_specs c
    WHERE 
        -- Extract case GPU length limit and compare with improved pattern matching
        (
            CASE 
                -- Pattern for "360 mm" format
                WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?).*mm' THEN
                    (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric >= gpu_length_mm
                -- Pattern for "14.173"" format (convert to mm)
                WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?).*"' THEN
                    (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric * 25.4 >= gpu_length_mm
                -- Basic numeric pattern
                WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?)' THEN
                    (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric >= gpu_length_mm
                ELSE false
            END
        )
    ORDER BY 
        CASE 
            WHEN c.price ~ '^\\$?[0-9]+(\.[0-9]+)?$' THEN 
                (regexp_replace(c.price, '\\$', ''))::numeric 
            ELSE NULL 
        END ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch PSUs compatible based on a minimum required wattage.
CREATE OR REPLACE FUNCTION get_compatible_psu(required_wattage int, case_id int)
RETURNS TABLE (
    id int,
    name text,
    price text,
    type text,
    efficiency_rating text,
    wattage int,
    modular text,
    color text
) AS $$
DECLARE
    case_exists boolean;
    case_type text;
    compatible_psu_type text;
BEGIN
    -- Check if case exists and get its type
    SELECT 
        EXISTS (SELECT 1 FROM case_specs c WHERE c.id = case_id),
        c.type
    INTO 
        case_exists,
        case_type
    FROM case_specs c
    WHERE c.id = case_id;

    IF NOT case_exists THEN
        RAISE EXCEPTION 'Case with ID % does not exist', case_id;
    END IF;

    -- Determine compatible PSU type based on case form factor
    IF case_type LIKE 'ATX%' THEN
        compatible_psu_type := 'ATX';
    ELSIF case_type LIKE 'Mini ITX%' THEN
        compatible_psu_type := 'SFX';
    ELSIF case_type LIKE 'MicroATX%' THEN
        compatible_psu_type := 'ATX';
    ELSIF case_type = 'HTPC' THEN
        compatible_psu_type := 'TFX';
    ELSE
        compatible_psu_type := 'ATX'; -- Default to ATX for unknown types
    END IF;

    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.price,
        p.type,
        p.efficiency_rating,
        p.wattage,
        p.modular,
        p.color
    FROM psu_specs p
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
    )
    ORDER BY p.wattage ASC;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch RAM compatible with both motherboard and CPU
-- Updated to improve memory speed matching
CREATE OR REPLACE FUNCTION get_compatible_ram(mobo_id int, cpu_id int)
RETURNS TABLE (
    id int,
    name text,
    price text,
    speed text,
    modules text,
    price_per_gb text,
    color text,
    first_word_latency text,
    cas_latency text,
    voltage text,
    timing text,
    ecc boolean,
    heat_spreader boolean
) AS $$
DECLARE
    mobo_memory_type text;
    mobo_memory_speed text;
    cpu_memory_type text;
    cpu_exists boolean;
    mobo_exists boolean;
BEGIN
    -- Check if CPU exists
    SELECT EXISTS (
        SELECT 1 FROM cpu_specs WHERE cpu_specs.id = cpu_id
    ), 
    CASE 
        WHEN maximum_supported_memory LIKE '%DDR5%' THEN 'DDR5'
        WHEN maximum_supported_memory LIKE '%DDR4%' THEN 'DDR4'
        ELSE 'DDR5' -- Default to latest memory type
    END INTO cpu_exists, cpu_memory_type
    FROM cpu_specs
    WHERE id = cpu_id;

    IF NOT cpu_exists THEN
        RAISE EXCEPTION 'CPU with ID % does not exist', cpu_id;
    END IF;

    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs WHERE motherboard_specs.id = mobo_id
    ) INTO mobo_exists;

    IF NOT mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Get motherboard memory specifications
    SELECT ms.memory_type, ms.memory_speed
    INTO mobo_memory_type, mobo_memory_speed
    FROM motherboard_specs ms
    WHERE ms.id = mobo_id;

    RETURN QUERY
    SELECT 
        m.id,
        m.name,
        m.price,
        m.speed,
        m.modules,
        m.price_per_gb,
        m.color,
        m.first_word_latency,
        m.cas_latency,
        m.voltage,
        m.timing,
        m.ecc,
        m.heat_spreader
    FROM memory_specs m
    WHERE 
        -- Check if memory type matches both CPU and motherboard supported type
        (
            CASE 
                WHEN m.speed LIKE 'DDR5%' AND mobo_memory_type = 'DDR5' AND cpu_memory_type = 'DDR5' THEN true
                WHEN m.speed LIKE 'DDR4%' AND mobo_memory_type = 'DDR4' AND cpu_memory_type = 'DDR4' THEN true
                ELSE false
            END
        )
        -- Check if memory speed is in motherboard's supported speeds
        AND (
            CASE
                -- Direct match
                WHEN mobo_memory_speed LIKE '%' || m.speed || '%' THEN true
                -- Extract the numeric part for broader matching
                WHEN m.speed ~ 'DDR[45]-([0-9]+)' THEN
                    mobo_memory_speed LIKE '%' || (regexp_match(m.speed, 'DDR[45]-([0-9]+)'))[1] || '%'
                ELSE false
            END
        )
    ORDER BY 
        CASE 
            WHEN m.price ~ '^\\$?[0-9]+(\.[0-9]+)?$' THEN 
                (regexp_replace(m.price, '\\$', ''))::numeric 
            ELSE NULL 
        END ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch SSDs compatible with a motherboard
CREATE OR REPLACE FUNCTION get_compatible_ssd(mobo_id int)
RETURNS TABLE (
    id int,
    name text,
    price numeric,
    capacity int,
    price_per_gb numeric,
    type text,
    cache text,
    form_factor text,
    interface text
) AS $$
DECLARE
    mobo_m2_slots text;
    mobo_sata_ports text;
    mobo_exists boolean;
BEGIN
    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs WHERE motherboard_specs.id = mobo_id
    ), m2_slots, sata_ports INTO mobo_exists, mobo_m2_slots, mobo_sata_ports
    FROM motherboard_specs
    WHERE id = mobo_id;

    IF NOT mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    RETURN QUERY
    SELECT 
        s.*
    FROM ssd_specs s
    WHERE 
        -- For M.2 SSDs, check if motherboard has M.2 slots
        (s.form_factor = 'M.2-2280' AND mobo_m2_slots IS NOT NULL)
        -- For SATA SSDs, check if motherboard has SATA ports
        OR (s.interface LIKE '%SATA%' AND mobo_sata_ports IS NOT NULL)
    ORDER BY s.price_per_gb ASC NULLS LAST;
END;
$$ LANGUAGE plpgsql;
