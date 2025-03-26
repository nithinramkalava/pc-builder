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
    v_cpu_socket text;
    v_cpu_memory_type text;
BEGIN
    -- Get the CPU socket type and memory type
    SELECT cs.socket, 
           CASE 
               WHEN cs.maximum_supported_memory LIKE '%DDR5%' THEN 'DDR5'
               WHEN cs.maximum_supported_memory LIKE '%DDR4%' THEN 'DDR4'
               ELSE NULL
           END INTO v_cpu_socket, v_cpu_memory_type
    FROM cpu_specs cs
    WHERE cs.id = cpu_id;

    IF v_cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU with ID % not found or socket information missing', cpu_id;
    END IF;

    RETURN QUERY
    SELECT m.id, m.name, m.price, m.form_factor, m.socket_cpu, 
           m.memory_max, m.memory_slots, m.memory_type, m.memory_speed,
           m.chipset, m.color, m.m2_slots, m.sata_ports
    FROM motherboard_specs m
    WHERE m.socket_cpu = v_cpu_socket;
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
    v_cpu_socket text;
BEGIN
    -- Get the CPU socket type
    SELECT cs.socket INTO v_cpu_socket
    FROM cpu_specs cs
    WHERE cs.id = cpu_id;

    IF v_cpu_socket IS NULL THEN
        RAISE EXCEPTION 'CPU socket not found for ID %', cpu_id;
    END IF;

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
    WHERE v_cpu_socket = ANY(string_to_array(c.cpu_socket, E'\n'));
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch video cards compatible with a given motherboard.
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
    v_mobo_exists boolean;
    v_mobo_pci_slots text;
    v_mobo_max_pcie_value int := 1;
BEGIN
    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs ms WHERE ms.id = mobo_id
    ), ms.pci_slots INTO v_mobo_exists, v_mobo_pci_slots
    FROM motherboard_specs ms
    WHERE ms.id = mobo_id;

    IF NOT v_mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Determine the maximum PCIe lanes supported by the motherboard
    IF v_mobo_pci_slots IS NOT NULL THEN
        IF v_mobo_pci_slots LIKE '%PCIe x16%' THEN
            v_mobo_max_pcie_value := 16;
        ELSIF v_mobo_pci_slots LIKE '%PCIe x8%' THEN
            v_mobo_max_pcie_value := 8;
        ELSIF v_mobo_pci_slots LIKE '%PCIe x4%' THEN
            v_mobo_max_pcie_value := 4;
        END IF;
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
        CASE 
            WHEN g.interface LIKE '%PCIe x16%' AND v_mobo_max_pcie_value >= 16 THEN true
            WHEN g.interface LIKE '%PCIe x8%' AND v_mobo_max_pcie_value >= 8 THEN true
            WHEN g.interface LIKE '%PCIe x4%' AND v_mobo_max_pcie_value >= 4 THEN true
            WHEN g.interface LIKE '%PCIe x1%' THEN true
            WHEN g.interface IS NULL OR g.interface = '' THEN true
            WHEN g.interface LIKE '%PCIe%' THEN true
            ELSE false
        END;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch cases compatible with a given GPU and motherboard.
CREATE OR REPLACE FUNCTION get_compatible_case(gpu_id int, mobo_id int)
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
    v_gpu_length_mm numeric;
    v_gpu_length_text text;
    v_gpu_exists boolean;
    v_mobo_exists boolean;
    v_mobo_form_factor text;
BEGIN
    -- Check if GPU exists
    SELECT EXISTS (
        SELECT 1 FROM gpu_specs gs WHERE gs.id = gpu_id
    ) INTO v_gpu_exists;

    IF NOT v_gpu_exists THEN
        RAISE EXCEPTION 'GPU with ID % does not exist', gpu_id;
    END IF;

    -- Check if motherboard exists and get its form factor
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs ms WHERE ms.id = mobo_id
    ), ms.form_factor INTO v_mobo_exists, v_mobo_form_factor
    FROM motherboard_specs ms
    WHERE ms.id = mobo_id;

    IF NOT v_mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Get GPU length
    SELECT gs.length INTO v_gpu_length_text
    FROM gpu_specs gs
    WHERE gs.id = gpu_id;

    -- Extract numeric length value with improved pattern matching
    IF v_gpu_length_text ~ '([0-9]+(\.[0-9]+)?).*mm' THEN
        v_gpu_length_mm := (regexp_match(v_gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric;
    ELSIF v_gpu_length_text ~ '([0-9]+(\.[0-9]+)?).*in' THEN
        v_gpu_length_mm := (regexp_match(v_gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric * 25.4;
    ELSIF v_gpu_length_text ~ '([0-9]+(\.[0-9]+)?)' THEN
        v_gpu_length_mm := (regexp_match(v_gpu_length_text, '([0-9]+(\.[0-9]+)?)'))[1]::numeric;
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
        -- Check GPU length compatibility
        CASE 
            WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?).*mm' THEN
                (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric >= v_gpu_length_mm
            WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?).*"' THEN
                (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric * 25.4 >= v_gpu_length_mm
            WHEN c.maximum_video_card_length ~ '([0-9]+(\.[0-9]+)?)' THEN
                (regexp_match(c.maximum_video_card_length, '([0-9]+(\.[0-9]+)?)'))[1]::numeric >= v_gpu_length_mm
            ELSE false
        END
        AND
        -- Check motherboard form factor compatibility
        v_mobo_form_factor = ANY(string_to_array(c.motherboard_form_factor, E'\n'));
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
    v_case_exists boolean;
    v_case_type text;
    v_compatible_psu_type text;
BEGIN
    -- Check if case exists and get its type
    SELECT 
        EXISTS (SELECT 1 FROM case_specs cs WHERE cs.id = case_id),
        cs.type
    INTO 
        v_case_exists,
        v_case_type
    FROM case_specs cs
    WHERE cs.id = case_id;

    IF NOT v_case_exists THEN
        RAISE EXCEPTION 'Case with ID % does not exist', case_id;
    END IF;

    -- Determine compatible PSU type based on case form factor
    IF v_case_type LIKE 'ATX%' THEN
        v_compatible_psu_type := 'ATX';
    ELSIF v_case_type LIKE 'Mini ITX%' THEN
        v_compatible_psu_type := 'SFX';
    ELSIF v_case_type LIKE 'MicroATX%' THEN
        v_compatible_psu_type := 'ATX';
    ELSIF v_case_type = 'HTPC' THEN
        v_compatible_psu_type := 'TFX';
    ELSE
        v_compatible_psu_type := 'ATX';
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
        CASE 
            WHEN v_compatible_psu_type = 'ATX' THEN
                p.type = 'ATX'
            WHEN v_compatible_psu_type = 'SFX' THEN
                p.type IN ('SFX', 'Mini ITX')
            WHEN v_compatible_psu_type = 'TFX' THEN
                p.type IN ('TFX', 'Flex ATX')
            ELSE 
                FALSE
        END
    )
    ORDER BY p.wattage ASC;
END;
$$ LANGUAGE plpgsql;

-- Stored function to fetch RAM compatible with both motherboard and CPU
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
    v_mobo_memory_type text;
    v_mobo_memory_speed text;
    v_cpu_exists boolean;
    v_mobo_exists boolean;
BEGIN
    -- Check if CPU exists
    SELECT EXISTS (
        SELECT 1 FROM cpu_specs cs WHERE cs.id = cpu_id
    ) INTO v_cpu_exists;

    IF NOT v_cpu_exists THEN
        RAISE EXCEPTION 'CPU with ID % does not exist', cpu_id;
    END IF;

    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs ms WHERE ms.id = mobo_id
    ) INTO v_mobo_exists;

    IF NOT v_mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    -- Get motherboard memory specifications
    SELECT ms.memory_type, ms.memory_speed
    INTO v_mobo_memory_type, v_mobo_memory_speed
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
        CASE 
            WHEN m.speed LIKE 'DDR5%' AND v_mobo_memory_type = 'DDR5' THEN true
            WHEN m.speed LIKE 'DDR4%' AND v_mobo_memory_type = 'DDR4' THEN true
            ELSE false
        END
        AND (
            CASE
                WHEN v_mobo_memory_speed LIKE '%' || m.speed || '%' THEN true
                WHEN m.speed ~ 'DDR[45]-([0-9]+)' THEN
                    v_mobo_memory_speed LIKE '%' || (regexp_match(m.speed, 'DDR[45]-([0-9]+)'))[1] || '%'
                ELSE false
            END
        );
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
    v_mobo_m2_slots text;
    v_mobo_sata_ports text;
    v_mobo_exists boolean;
BEGIN
    -- Check if motherboard exists
    SELECT EXISTS (
        SELECT 1 FROM motherboard_specs ms WHERE ms.id = mobo_id
    ), ms.m2_slots, ms.sata_ports INTO v_mobo_exists, v_mobo_m2_slots, v_mobo_sata_ports
    FROM motherboard_specs ms
    WHERE ms.id = mobo_id;

    IF NOT v_mobo_exists THEN
        RAISE EXCEPTION 'Motherboard with ID % does not exist', mobo_id;
    END IF;

    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.price,
        s.capacity,
        s.price_per_gb,
        s.type,
        s.cache,
        s.form_factor,
        s.interface
    FROM ssd_specs s
    WHERE 
        (s.form_factor = 'M.2-2280' AND v_mobo_m2_slots IS NOT NULL)
        OR (s.interface LIKE '%SATA%' AND v_mobo_sata_ports IS NOT NULL)
    ORDER BY s.price_per_gb ASC NULLS LAST;

END;
$$ LANGUAGE plpgsql;

