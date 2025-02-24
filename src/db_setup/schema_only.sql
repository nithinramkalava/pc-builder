--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: check_case_gpu_compatibility(integer, integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.check_case_gpu_compatibility(case_id integer, gpu_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    case_max_length DECIMAL(6,2);
    gpu_length DECIMAL(6,2);
BEGIN
    SELECT max_gpu_length INTO case_max_length FROM case_enclosure WHERE id = case_id;
    SELECT length INTO gpu_length FROM video_card WHERE id = gpu_id;
    RETURN case_max_length >= gpu_length;
END;
$$;


ALTER FUNCTION public.check_case_gpu_compatibility(case_id integer, gpu_id integer) OWNER TO pc_builder_admin;

--
-- Name: check_cpu_motherboard_compatibility(integer, integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.check_cpu_motherboard_compatibility(cpu_id integer, motherboard_id integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    cpu_socket VARCHAR(50);
    mobo_socket VARCHAR(50);
BEGIN
    SELECT socket_type INTO cpu_socket FROM cpu WHERE id = cpu_id;
    SELECT socket INTO mobo_socket FROM motherboard WHERE id = motherboard_id;
    RETURN cpu_socket = mobo_socket;
END;
$$;


ALTER FUNCTION public.check_cpu_motherboard_compatibility(cpu_id integer, motherboard_id integer) OWNER TO pc_builder_admin;

--
-- Name: clean_chipset_support(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.clean_chipset_support(chipsets text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    cleaned_chipsets text[];
BEGIN
    IF chipsets IS NULL THEN
        RETURN NULL;
    END IF;

    -- Remove quotes, brackets, and clean up each chipset name
    cleaned_chipsets := ARRAY(
        SELECT TRIM(BOTH '"' FROM TRIM(BOTH ' ' FROM unnest))
        FROM unnest(chipsets)
        WHERE unnest IS NOT NULL AND LENGTH(unnest) > 0
        ORDER BY unnest
    );

    -- Join with commas
    RETURN array_to_string(cleaned_chipsets, ',');
END;
$$;


ALTER FUNCTION public.clean_chipset_support(chipsets text[]) OWNER TO postgres;

--
-- Name: extract_max_radiator_size(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.extract_max_radiator_size(radiator_array text[]) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    size_text text;
    size_number INTEGER := 0;
    temp_number text;
    num_value INTEGER;
BEGIN
    -- Loop through each element in the array
    FOREACH size_text IN ARRAY radiator_array LOOP
        -- Extract numbers from text
        temp_number := REGEXP_REPLACE(size_text, '[^0-9]', '', 'g');
        
        -- Convert to number if not empty
        IF temp_number IS NOT NULL AND temp_number != '' THEN
            -- Safe conversion to integer
            BEGIN
                num_value := temp_number::INTEGER;
                
                -- Handle special cases like multiple 120mm or 140mm
                IF num_value < 100 THEN
                    -- If it's likely a fan size (120 or 140), multiply by count if present
                    IF size_text ~* '(\dx|x\d)' THEN
                        DECLARE
                            multiplier INTEGER;
                            multiplier_text text;
                        BEGIN
                            multiplier_text := (regexp_matches(size_text, '(\d+)x|x(\d+)', 'i'))[1];
                            IF multiplier_text IS NOT NULL THEN
                                multiplier := multiplier_text::INTEGER;
                                num_value := num_value * multiplier;
                            END IF;
                        EXCEPTION WHEN OTHERS THEN
                            -- If conversion fails, keep original number
                            NULL;
                        END;
                    END IF;
                END IF;
                
                -- Update max size if this is larger
                IF num_value > size_number THEN
                    size_number := num_value;
                END IF;
            EXCEPTION WHEN OTHERS THEN
                -- If conversion fails, skip this value
                NULL;
            END;
        END IF;
    END LOOP;
    
    RETURN size_number;
END;
$$;


ALTER FUNCTION public.extract_max_radiator_size(radiator_array text[]) OWNER TO postgres;

--
-- Name: get_compatible_case(integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_case(gpu_id integer) RETURNS TABLE(case_id integer, case_name character varying, case_price numeric, case_type character varying, case_color character varying, case_psu numeric, case_side_panel character varying, case_external_volume numeric, case_internal_35_bays integer, case_max_gpu_length numeric, case_max_gpu_height numeric, case_max_cpu_cooler_height numeric, case_supported_motherboard_sizes text[], case_max_psu_length numeric, case_radiator_support text[], case_included_fans integer, case_max_fan_slots integer, case_max_radiator_size integer)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_compatible_case(gpu_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_cpu_coolers(integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_cpu_coolers(cpu_id integer) RETURNS TABLE(id integer, name character varying, price numeric, rpm text, noise_level text, color character varying, size numeric, supported_sockets text[], height numeric, tdp_support integer, radiator_size character varying, clearance_required numeric)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_compatible_cpu_coolers(cpu_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_motherboards(integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_motherboards(cpu_id integer) RETURNS TABLE(id integer, name character varying, price numeric, socket character varying, form_factor character varying, max_memory integer, memory_slots integer, color character varying, memory_type character varying, supported_memory_speeds integer[], chipset character varying, pcie_version character varying, max_pcie_lanes integer, m2_slots integer, sata_ports integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT m.*
    FROM cpu c
    JOIN motherboard m ON m.socket = c.socket_type
    WHERE c.id = cpu_id
      AND m.memory_type = c.memory_type_support;
END;
$$;


ALTER FUNCTION public.get_compatible_motherboards(cpu_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_psu(integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_psu(required_wattage integer) RETURNS TABLE(id integer, name character varying, price numeric, type character varying, efficiency character varying, wattage integer, modular character varying, color character varying, available_connectors jsonb, psu_length numeric, fan_size integer, protection_features text[], atx_version character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM power_supply
    WHERE wattage >= required_wattage;
END;
$$;


ALTER FUNCTION public.get_compatible_psu(required_wattage integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_psu(integer, integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_psu(required_wattage integer, case_id integer) RETURNS TABLE(id integer, name character varying, price numeric, type character varying, efficiency character varying, wattage integer, modular character varying, color character varying, available_connectors jsonb, psu_length numeric, fan_size integer, protection_features text[], atx_version character varying)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_compatible_psu(required_wattage integer, case_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_ram(integer, integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_ram(mobo_id integer, cpu_id integer) RETURNS TABLE(id integer, name character varying, price numeric, speed character varying, modules character varying, price_per_gb numeric, color character varying, first_word_latency numeric, cas_latency numeric, voltage numeric, memory_format character varying, ecc_support boolean, ddr_version integer, memory_speed integer)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_compatible_ram(mobo_id integer, cpu_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_compatible_video_cards(integer); Type: FUNCTION; Schema: public; Owner: pc_builder_admin
--

CREATE FUNCTION public.get_compatible_video_cards(mobo_id integer) RETURNS TABLE(id integer, name character varying, price numeric, chipset character varying, memory numeric, core_clock numeric, boost_clock numeric, color character varying, length numeric, tdp integer, required_psu_wattage integer, pcie_version character varying, pcie_lanes_required integer, height numeric, power_connectors text[])
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT v.*
    FROM video_card v
    JOIN motherboard m ON m.pcie_version = v.pcie_version
    WHERE m.id = mobo_id
      AND m.max_pcie_lanes >= v.pcie_lanes_required;
END;
$$;


ALTER FUNCTION public.get_compatible_video_cards(mobo_id integer) OWNER TO pc_builder_admin;

--
-- Name: get_highest_ddr(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_highest_ddr(memory_types text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    highest_version INTEGER := 0;
    current_version INTEGER;
    mem_type text;
BEGIN
    -- If the input is NULL, return NULL
    IF memory_types IS NULL THEN
        RETURN NULL;
    END IF;

    -- Remove curly braces and split string
    memory_types := REPLACE(REPLACE(memory_types, '{', ''), '}', '');
    
    -- Loop through each memory type
    FOR mem_type IN SELECT unnest(string_to_array(memory_types, ',')) LOOP
        -- Extract DDR version number
        current_version := (regexp_matches(mem_type, 'DDR(\d+)', 'i'))[1]::INTEGER;
        IF current_version > highest_version THEN
            highest_version := current_version;
        END IF;
    END LOOP;

    -- Return the highest DDR version found
    IF highest_version > 0 THEN
        RETURN 'DDR' || highest_version;
    END IF;

    RETURN NULL;
END;
$$;


ALTER FUNCTION public.get_highest_ddr(memory_types text) OWNER TO postgres;

--
-- Name: get_max_radiator_size(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_max_radiator_size(radiator_array text[]) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    size_text text;
    all_numbers INTEGER[];
    max_size INTEGER := 0;
BEGIN
    -- Loop through each element in the array
    FOREACH size_text IN ARRAY radiator_array LOOP
        -- Extract all numbers from the text
        SELECT ARRAY(
            SELECT NULLIF(REGEXP_REPLACE(m[1], '[^0-9]', '', 'g'), '')::INTEGER
            FROM REGEXP_MATCHES(size_text, '(\d+)', 'g') m
            WHERE NULLIF(REGEXP_REPLACE(m[1], '[^0-9]', '', 'g'), '') IS NOT NULL
        ) INTO all_numbers;
        
        -- Find the maximum number in this element
        IF array_length(all_numbers, 1) > 0 THEN
            SELECT GREATEST(max_size, MAX(num))
            INTO max_size
            FROM unnest(all_numbers) num;
        END IF;
    END LOOP;
    
    RETURN max_size;
END;
$$;


ALTER FUNCTION public.get_max_radiator_size(radiator_array text[]) OWNER TO postgres;

--
-- Name: standardize_atx_version(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_atx_version(version text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    clean_version text;
BEGIN
    -- If null, return null
    IF version IS NULL THEN
        RETURN NULL;
    END IF;

    -- Convert to uppercase and trim whitespace
    clean_version := UPPER(TRIM(version));
    
    -- Remove 'ATX' prefix if exists
    clean_version := REGEXP_REPLACE(clean_version, '^ATX\s*', '', 'i');
    
    -- Remove 'V' prefix if exists
    clean_version := REGEXP_REPLACE(clean_version, '^V', '', 'i');
    
    -- Replace underscores with dots
    clean_version := REPLACE(clean_version, '_', '.');
    
    -- Remove any letters after numbers (like 'a' or 'b' in v2.52a)
    clean_version := REGEXP_REPLACE(clean_version, '([0-9])[A-Z]', '\1', 'gi');
    
    -- Standardize format to X.XX
    RETURN CASE
        WHEN clean_version ~ '^2\.3$' THEN '2.30'
        WHEN clean_version ~ '^2\.4$' THEN '2.40'
        WHEN clean_version ~ '^2\.5$' THEN '2.50'
        WHEN clean_version ~ '^2\.51$' THEN '2.51'
        WHEN clean_version ~ '^2\.52$' THEN '2.52'
        WHEN clean_version ~ '^2\.32$' THEN '2.32'
        WHEN clean_version ~ '^2\.31$' THEN '2.31'
        WHEN clean_version ~ '^2\.0$' THEN '2.00'
        WHEN clean_version ~ '^3\.0$' THEN '3.00'
        ELSE REGEXP_REPLACE(clean_version, '^(\d+\.\d+).*$', '\1')
    END;
END;
$_$;


ALTER FUNCTION public.standardize_atx_version(version text) OWNER TO postgres;

--
-- Name: standardize_cooler_socket(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_cooler_socket(socket text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    normalized text;
BEGIN
    -- If null or invalid text, return null
    IF socket IS NULL OR socket IN ('list', 'of', 'socket', 'types', 'supported', 'A', 'F', 'H4') THEN
        RETURN NULL;
    END IF;

    -- Convert to uppercase and trim
    normalized := UPPER(TRIM(socket));
    
    -- Remove 'SOCKET' word if exists
    normalized := REGEXP_REPLACE(normalized, 'SOCKET\s+', '', 'i');
    
    -- Standardize the format
    RETURN CASE
        -- Intel LGA sockets
        WHEN normalized ~ '^(LGA)?1700$' THEN 'LGA1700'
        WHEN normalized ~ '^(LGA)?1200$' THEN 'LGA1200'
        WHEN normalized ~ '^(LGA)?1151(_VR)?$' THEN 'LGA1151'
        WHEN normalized ~ '^(LGA)?1150$' THEN 'LGA1150'
        WHEN normalized ~ '^(LGA)?1155$' THEN 'LGA1155'
        WHEN normalized ~ '^(LGA)?1156$' THEN 'LGA1156'
        WHEN normalized ~ '^(LGA)?775$' THEN 'LGA775'
        WHEN normalized ~ '^(LGA)?1366$' THEN 'LGA1366'
        WHEN normalized ~ 'LGA115[Xx]' THEN 'LGA1151'  -- Most common 115x socket
        WHEN normalized ~ '^(LGA)?2066$' THEN 'LGA2066'
        WHEN normalized ~ '^(LGA)?2011-3$' THEN 'LGA2011-3'
        WHEN normalized ~ '^(LGA)?2011$' THEN 'LGA2011'
        WHEN normalized = 'LGA20XX' THEN 'LGA2066'     -- Most recent 20xx socket
        
        -- AMD Mainstream sockets
        WHEN normalized ~ '^AM5$' THEN 'AM5'
        WHEN normalized ~ '^AM4$' THEN 'AM4'
        WHEN normalized ~ '^AM3\+$' THEN 'AM3+'
        WHEN normalized ~ '^AM3$' THEN 'AM3'
        WHEN normalized ~ '^AM2\+$' THEN 'AM2+'
        WHEN normalized ~ '^AM2(R2)?$' THEN 'AM2'
        WHEN normalized ~ '^AM1$' THEN 'AM1'
        
        -- AMD HEDT/Server sockets
        WHEN normalized IN ('STRX4', 'TRX4', 'AMD TRX4', 'AMD TRX40') THEN 'sTRX4'
        WHEN normalized IN ('TR4', 'AMD TR4') THEN 'TR4'
        WHEN normalized = 'SP3' THEN 'SP3'
        WHEN normalized = 'SP3R2' THEN 'SP3r2'
        
        -- AMD FM sockets
        WHEN normalized ~ '^FM2\+$' THEN 'FM2+'
        WHEN normalized ~ '^FM2$' THEN 'FM2'
        WHEN normalized ~ '^FM1$' THEN 'FM1'
        
        -- Remove chipset entries that were mistakenly added as sockets
        WHEN normalized IN ('B450', 'X570', 'B550', 'X470', 'X99') THEN NULL
        
        -- Return original if no match (for manual review)
        ELSE normalized
    END;
END;
$_$;


ALTER FUNCTION public.standardize_cooler_socket(socket text) OWNER TO postgres;

--
-- Name: standardize_cooler_sockets(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_cooler_sockets(sockets text[]) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF sockets IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN array(
        SELECT DISTINCT s
        FROM (
            SELECT standardize_cooler_socket(unnest) as s
            FROM unnest(sockets)
        ) t
        WHERE s IS NOT NULL
        ORDER BY s
    );
END;
$$;


ALTER FUNCTION public.standardize_cooler_sockets(sockets text[]) OWNER TO postgres;

--
-- Name: standardize_mobo_size(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_mobo_size(size text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    standardized text;
BEGIN
    -- Convert to uppercase and trim whitespace
    size := UPPER(TRIM(size));
    
    -- Remove all separators and spaces
    size := REGEXP_REPLACE(size, '[-_\s]', '', 'g');
    
    -- Standardize the format
    standardized := CASE
        -- ATX variations
        WHEN size = 'ATX' THEN 'ATX'
        
        -- Micro-ATX variations
        WHEN size IN ('MATX', 'MICROATX', 'MATX', 'MICATX') THEN 'Micro-ATX'
        
        -- Mini-ITX variations
        WHEN size IN ('MINIITX', 'MITX', 'ITX', 'MINITX') THEN 'Mini-ITX'
        
        -- Extended ATX
        WHEN size = 'EATX' THEN 'E-ATX'
        
        -- Mini-STX variations
        WHEN size IN ('MINISTX', 'MISTX') THEN 'Mini-STX'
        
        -- Return original if no match
        ELSE size
    END;
    
    RETURN standardized;
END;
$$;


ALTER FUNCTION public.standardize_mobo_size(size text) OWNER TO postgres;

--
-- Name: standardize_mobo_sizes(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_mobo_sizes(sizes text[]) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF sizes IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN array(
        SELECT DISTINCT standardize_mobo_size(unnest)
        FROM unnest(sizes)
        WHERE unnest IS NOT NULL
        ORDER BY standardize_mobo_size(unnest)
    );
END;
$$;


ALTER FUNCTION public.standardize_mobo_sizes(sizes text[]) OWNER TO postgres;

--
-- Name: standardize_pcie_version(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_pcie_version(version text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Convert to uppercase and trim whitespace
    version := UPPER(TRIM(version));
    
    -- Remove any text in parentheses
    version := REGEXP_REPLACE(version, '\s*\([^)]*\)', '', 'g');
    
    -- Remove 'X16' references
    version := REGEXP_REPLACE(version, '\s*X\s*16', '', 'gi');
    
    -- Remove 'GEN' references
    version := REGEXP_REPLACE(version, '\s*GEN\s*', '', 'gi');
    
    -- Remove 'VERSION' references
    version := REGEXP_REPLACE(version, '\s*VERSION\s*', '', 'gi');
    
    -- Remove 'PCIE' prefix and dot in version number
    version := REGEXP_REPLACE(version, 'PCIE\s*', '', 'gi');
    version := REGEXP_REPLACE(version, '\.0', '', 'gi');
    
    -- Standardize the version numbers
    RETURN CASE
        -- Version 1.x
        WHEN version ~ '1\.1|1' THEN 'PCIe 1.0'
        
        -- Version 2.x
        WHEN version ~ '2\.0|2|2\.5' THEN 'PCIe 2.0'
        
        -- Version 3.x
        WHEN version ~ '3\.0|3|3\.1' THEN 'PCIe 3.0'
        
        -- Version 4.x
        WHEN version ~ '4\.0|4' THEN 'PCIe 4.0'
        
        -- Version 5.x
        WHEN version ~ '5\.0|5' THEN 'PCIe 5.0'
        
        -- Return original if no match (for manual review)
        ELSE 'PCIe ' || version
    END;
END;
$$;


ALTER FUNCTION public.standardize_pcie_version(version text) OWNER TO postgres;

--
-- Name: standardize_power_connector(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_power_connector(connector text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    standardized text;
BEGIN
    -- Convert to uppercase and trim whitespace
    connector := UPPER(TRIM(connector));
    
    -- Remove variations of PCIe/PCI-E
    connector := REGEXP_REPLACE(connector, 'PCI-?E\s*X?16?_?', '', 'gi');
    
    -- Remove underscores
    connector := REPLACE(connector, '_', '-');
    
    -- Standardize spacing
    connector := REGEXP_REPLACE(connector, '\s+', ' ', 'g');
    
    -- Handle special cases first
    IF connector ~ '12V\s*HP\s*ERMS?' THEN
        RETURN '12VHPWR';
    END IF;

    -- Standardize pin format
    standardized := CASE
        -- Handle 6-pin variations
        WHEN connector ~ '6.?PIN' THEN '6-PIN'
        
        -- Handle 8-pin variations
        WHEN connector ~ '8.?PIN' THEN '8-PIN'
        
        -- Handle 12-pin variations
        WHEN connector ~ '12.?PIN' THEN '12VHPWR'
        
        -- Handle 16-pin variations
        WHEN connector ~ '16.?PIN' THEN '16-PIN'
        
        -- Handle multiple connector cases
        WHEN connector ~ '2X\s*16.?PIN' THEN '2x 16-PIN'
        WHEN connector ~ '2X\s*8.?PIN' THEN '2x 8-PIN'
        WHEN connector ~ '2X\s*12.?PIN' THEN '2x 12VHPWR'
        WHEN connector ~ '3X\s*16.?PIN' THEN '3x 16-PIN'
        
        -- Return original if no match
        ELSE connector
    END;
    
    RETURN standardized;
END;
$$;


ALTER FUNCTION public.standardize_power_connector(connector text) OWNER TO postgres;

--
-- Name: standardize_power_connectors(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_power_connectors(connectors text[]) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF connectors IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN array(
        SELECT DISTINCT standardize_power_connector(unnest)
        FROM unnest(connectors)
        WHERE unnest IS NOT NULL
    );
END;
$$;


ALTER FUNCTION public.standardize_power_connectors(connectors text[]) OWNER TO postgres;

--
-- Name: standardize_protection_feature(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_protection_feature(feature text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Convert to uppercase and trim whitespace
    feature := UPPER(TRIM(feature));
    
    -- Remove common separators and spaces
    feature := REGEXP_REPLACE(feature, '[-_\s]', '', 'g');
    
    -- Remove 'PROTECTION' word and its variants
    feature := REGEXP_REPLACE(feature, 'PROTECTION|PROTECT', '', 'g');
    
    RETURN CASE
        -- Over Voltage Protection
        WHEN feature IN ('OVP', 'OVERVOLTAGE', 'OVERVOLT', 'OVERVOLTAGEPROTECTION') THEN 'OVP'
        
        -- Under Voltage Protection
        WHEN feature IN ('UVP', 'UNDERVOLTAGE', 'UNDERVOLT', 'UNDERVOLTAGEPROTECTION') THEN 'UVP'
        
        -- Over Current Protection
        WHEN feature IN ('OCP', 'OVERCURRENT', 'OVERCURRENTPROTECTION') THEN 'OCP'
        
        -- Over Power Protection
        WHEN feature IN ('OPP', 'OVERPOWER', 'OVERPOWERPROTECTION', 'OVERLOAD', 'OVERLOADPROTECTION') THEN 'OPP'
        
        -- Over Temperature Protection
        WHEN feature IN ('OTP', 'OVERTEMP', 'OVERTEMPERATURE', 'THERMALPROTECTION') THEN 'OTP'
        
        -- Short Circuit Protection
        WHEN feature IN ('SCP', 'SHORTCIRCUIT', 'SHORTCIRCUITPROTECTION') THEN 'SCP'
        
        -- Return null for unrecognized features
        ELSE NULL
    END;
END;
$$;


ALTER FUNCTION public.standardize_protection_feature(feature text) OWNER TO postgres;

--
-- Name: standardize_protection_features(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_protection_features(features text[]) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF features IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN array(
        SELECT DISTINCT f
        FROM (
            SELECT standardize_protection_feature(unnest) as f
            FROM unnest(features)
        ) t
        WHERE f IS NOT NULL
        ORDER BY f
    );
END;
$$;


ALTER FUNCTION public.standardize_protection_features(features text[]) OWNER TO postgres;

--
-- Name: standardize_radiator_size(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_radiator_size(size text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    normalized text;
    numbers integer[];
BEGIN
    -- Handle null, empty, 'NaN', 'NA' cases
    IF size IS NULL OR size = '' OR size = 'NaN' OR size = 'NA' THEN
        RETURN NULL;
    END IF;

    -- Convert to uppercase and trim
    normalized := UPPER(TRIM(size));
    
    -- Remove 'MM', 'CM' suffixes and convert cm to mm
    IF normalized ~ 'CM' THEN
        normalized := REGEXP_REPLACE(normalized, 'CM', '', 'gi');
        -- Extract numbers and multiply by 10 to convert to mm
        numbers := ARRAY(
            SELECT NULLIF(REGEXP_REPLACE(m[1], '[^0-9]', '', 'g'), '')::INTEGER * 10
            FROM REGEXP_MATCHES(normalized, '(\d+)', 'g') m
        );
    ELSE
        normalized := REGEXP_REPLACE(normalized, 'MM', '', 'gi');
        -- Extract numbers
        numbers := ARRAY(
            SELECT NULLIF(REGEXP_REPLACE(m[1], '[^0-9]', '', 'g'), '')::INTEGER
            FROM REGEXP_MATCHES(normalized, '(\d+)', 'g') m
        );
    END IF;

    -- Handle special cases and find the largest number
    IF array_length(numbers, 1) > 0 THEN
        -- If we have multiple numbers (like 140x280), take the largest
        RETURN (SELECT MAX(n) FROM unnest(numbers) n);
    END IF;

    RETURN NULL;
END;
$$;


ALTER FUNCTION public.standardize_radiator_size(size text) OWNER TO postgres;

--
-- Name: standardize_socket_name(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.standardize_socket_name(socket_name text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Remove 'Socket ' prefix if exists
    socket_name := REPLACE(socket_name, 'Socket ', '');
    
    -- Standardize LGA format (remove space after LGA)
    socket_name := REGEXP_REPLACE(socket_name, 'LGA\s+', 'LGA');
    
    -- Standardize specific cases
    RETURN CASE
        -- AMD Sockets
        WHEN socket_name ILIKE '%am3+%' THEN 'AM3+'
        WHEN socket_name ILIKE '%am3%' THEN 'AM3'
        WHEN socket_name ILIKE '%am4%' THEN 'AM4'
        WHEN socket_name ILIKE '%am5%' THEN 'AM5'
        WHEN socket_name ILIKE '%fm2+%' OR socket_name ILIKE '%fm2/fm2+%' THEN 'FM2+'
        WHEN socket_name ILIKE '%fm2%' THEN 'FM2'
        WHEN socket_name ILIKE '%fm1%' THEN 'FM1'
        WHEN socket_name ILIKE '%str4%' THEN 'sTR4'
        WHEN socket_name ILIKE '%strx4%' THEN 'sTRX4'
        
        -- Intel LGA Sockets
        WHEN socket_name ILIKE '%lga775%' THEN 'LGA775'
        WHEN socket_name ILIKE '%lga1150%' THEN 'LGA1150'
        WHEN socket_name ILIKE '%lga1151%' THEN 'LGA1151'
        WHEN socket_name ILIKE '%lga1155%' THEN 'LGA1155'
        WHEN socket_name ILIKE '%lga1156%' THEN 'LGA1156'
        WHEN socket_name ILIKE '%lga1200%' THEN 'LGA1200'
        WHEN socket_name ILIKE '%lga1700%' THEN 'LGA1700'
        WHEN socket_name ILIKE '%lga1366%' THEN 'LGA1366'
        WHEN socket_name ILIKE '%lga2011-3%' OR socket_name ILIKE '%lga2011-v3%' THEN 'LGA2011-3'
        WHEN socket_name ILIKE '%lga2011%' THEN 'LGA2011'
        WHEN socket_name ILIKE '%lga2066%' THEN 'LGA2066'
        
        -- Return original if no match (for manual review)
        ELSE socket_name
    END;
END;
$$;


ALTER FUNCTION public.standardize_socket_name(socket_name text) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: case_enclosure; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.case_enclosure (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    type character varying(50),
    color character varying(50),
    psu numeric(6,2),
    side_panel character varying(50),
    external_volume numeric(10,2),
    internal_35_bays integer,
    max_gpu_length numeric(6,2),
    max_gpu_height numeric(6,2),
    max_cpu_cooler_height numeric(6,2),
    supported_motherboard_sizes text[],
    max_psu_length numeric(6,2),
    radiator_support text[],
    included_fans integer,
    max_fan_slots integer,
    max_radiator_size integer
);


ALTER TABLE public.case_enclosure OWNER TO pc_builder_admin;

--
-- Name: case_enclosure_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.case_enclosure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.case_enclosure_id_seq OWNER TO pc_builder_admin;

--
-- Name: case_enclosure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.case_enclosure_id_seq OWNED BY public.case_enclosure.id;


--
-- Name: cpu; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.cpu (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    core_count integer,
    core_clock numeric(4,2),
    boost_clock numeric(4,2),
    tdp integer,
    graphics character varying(255),
    smt boolean,
    socket_type character varying(50),
    memory_type_support text,
    memory_speed_support integer,
    chipset_support text,
    max_memory_support integer
);


ALTER TABLE public.cpu OWNER TO pc_builder_admin;

--
-- Name: cpu_cooler; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.cpu_cooler (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    rpm character varying(100),
    noise_level character varying(50),
    color character varying(50),
    size numeric(5,2),
    supported_sockets text[],
    height numeric(6,2),
    tdp_support integer,
    radiator_size character varying(50),
    clearance_required numeric(6,2),
    radiator_size_mm integer
);


ALTER TABLE public.cpu_cooler OWNER TO pc_builder_admin;

--
-- Name: cpu_cooler_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.cpu_cooler_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cpu_cooler_id_seq OWNER TO pc_builder_admin;

--
-- Name: cpu_cooler_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.cpu_cooler_id_seq OWNED BY public.cpu_cooler.id;


--
-- Name: cpu_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.cpu_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cpu_id_seq OWNER TO pc_builder_admin;

--
-- Name: cpu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.cpu_id_seq OWNED BY public.cpu.id;


--
-- Name: memory; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.memory (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    speed character varying(50),
    modules character varying(50),
    price_per_gb numeric(10,2),
    color character varying(50),
    first_word_latency numeric(5,2),
    cas_latency numeric(4,2),
    voltage numeric(4,2),
    memory_format character varying(50),
    ecc_support boolean,
    ddr_version integer,
    memory_speed integer
);


ALTER TABLE public.memory OWNER TO pc_builder_admin;

--
-- Name: memory_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.memory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.memory_id_seq OWNER TO pc_builder_admin;

--
-- Name: memory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.memory_id_seq OWNED BY public.memory.id;


--
-- Name: motherboard; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.motherboard (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    socket character varying(50),
    form_factor character varying(50),
    max_memory integer,
    memory_slots integer,
    color character varying(50),
    memory_type character varying(50),
    supported_memory_speeds integer[],
    chipset character varying(50),
    pcie_version character varying(20),
    max_pcie_lanes integer,
    m2_slots integer,
    sata_ports integer
);


ALTER TABLE public.motherboard OWNER TO pc_builder_admin;

--
-- Name: motherboard_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.motherboard_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.motherboard_id_seq OWNER TO pc_builder_admin;

--
-- Name: motherboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.motherboard_id_seq OWNED BY public.motherboard.id;


--
-- Name: motherboard_new; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.motherboard_new (
    id integer NOT NULL,
    name character varying(255),
    manufacturer character varying(100),
    part_number character varying(100),
    socket character varying(100),
    form_factor character varying(50),
    chipset character varying(100),
    memory_max character varying(50),
    memory_type character varying(50),
    memory_slots integer,
    memory_speed text[],
    color character varying(100),
    sli_crossfire character varying(100),
    pcie_x16_slots integer,
    pcie_x8_slots integer,
    pcie_x4_slots integer,
    pcie_x1_slots integer,
    pci_slots integer,
    m2_slots text[],
    mini_pcie_slots integer,
    half_mini_pcie_slots integer,
    mini_pcie_msata_slots integer,
    msata_slots integer,
    sata_6gb integer,
    onboard_ethernet character varying(255),
    onboard_video character varying(255),
    usb_2_headers integer,
    usb_2_headers_single integer,
    usb_32_gen1_headers integer,
    usb_32_gen2_headers integer,
    usb_32_gen2x2_headers integer,
    supports_ecc boolean,
    wireless_networking character varying(100),
    raid_support boolean,
    back_connect_connectors boolean,
    url text
);


ALTER TABLE public.motherboard_new OWNER TO pc_builder_admin;

--
-- Name: motherboard_new_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.motherboard_new_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.motherboard_new_id_seq OWNER TO pc_builder_admin;

--
-- Name: motherboard_new_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.motherboard_new_id_seq OWNED BY public.motherboard_new.id;


--
-- Name: motherboards; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.motherboards (
    id integer NOT NULL,
    name character varying(255),
    manufacturer character varying(100),
    part_number character varying(100),
    socket character varying(50),
    form_factor character varying(50),
    chipset character varying(50),
    memory_max character varying(50),
    memory_type character varying(20),
    memory_slots integer,
    memory_speeds text[],
    color character varying(100),
    sli_crossfire character varying(100),
    pcie_x16_slots integer,
    pcie_x8_slots integer,
    pcie_x4_slots integer,
    pcie_x1_slots integer,
    pci_slots integer,
    m2_slots text[],
    mini_pcie_slots integer,
    half_mini_pcie_slots integer,
    mini_pcie_msata_slots integer,
    msata_slots integer,
    sata_6_slots integer,
    onboard_ethernet character varying(255),
    onboard_video character varying(255),
    usb_2_headers integer,
    usb_2_headers_single integer,
    usb_3_gen1_headers integer,
    usb_3_gen2_headers integer,
    usb_3_gen2x2_headers integer,
    supports_ecc boolean,
    wireless_networking character varying(255),
    raid_support boolean,
    back_connect_connectors boolean,
    url text,
    model character varying(255)
);


ALTER TABLE public.motherboards OWNER TO pc_builder_admin;

--
-- Name: motherboards_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.motherboards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.motherboards_id_seq OWNER TO pc_builder_admin;

--
-- Name: motherboards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.motherboards_id_seq OWNED BY public.motherboards.id;


--
-- Name: power_supply; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.power_supply (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    type character varying(50),
    efficiency character varying(50),
    wattage integer,
    modular character varying(50),
    color character varying(50),
    available_connectors jsonb,
    psu_length numeric(6,2),
    fan_size integer,
    protection_features text[],
    atx_version character varying(20)
);


ALTER TABLE public.power_supply OWNER TO pc_builder_admin;

--
-- Name: power_supply_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.power_supply_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.power_supply_id_seq OWNER TO pc_builder_admin;

--
-- Name: power_supply_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.power_supply_id_seq OWNED BY public.power_supply.id;


--
-- Name: storage; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.storage (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    capacity numeric(10,2),
    price_per_gb numeric(10,3),
    type character varying(50),
    cache numeric(10,2),
    form_factor character varying(50),
    interface character varying(50),
    power_consumption integer,
    nvme boolean,
    pcie_version character varying(20)
);


ALTER TABLE public.storage OWNER TO pc_builder_admin;

--
-- Name: storage_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.storage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.storage_id_seq OWNER TO pc_builder_admin;

--
-- Name: storage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.storage_id_seq OWNED BY public.storage.id;


--
-- Name: test_motherboard; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.test_motherboard (
    id integer NOT NULL,
    name character varying(255),
    manufacturer character varying(100),
    part_number character varying(100),
    socket character varying(100),
    form_factor character varying(50),
    chipset character varying(100),
    memory_max character varying(50),
    memory_type character varying(50),
    memory_slots integer,
    memory_speed text[],
    color character varying(100),
    sli_crossfire character varying(100),
    pcie_x16_slots integer,
    pcie_x8_slots integer,
    pcie_x4_slots integer,
    pcie_x1_slots integer,
    pci_slots integer,
    m2_slots text[],
    mini_pcie_slots integer,
    half_mini_pcie_slots integer,
    mini_pcie_msata_slots integer,
    msata_slots integer,
    sata_6gb integer,
    onboard_ethernet character varying(255),
    onboard_video character varying(255),
    usb_2_headers integer,
    usb_2_headers_single integer,
    usb_32_gen1_headers integer,
    usb_32_gen2_headers integer,
    usb_32_gen2x2_headers integer,
    supports_ecc boolean,
    wireless_networking character varying(100),
    raid_support boolean,
    back_connect_connectors boolean,
    url text
);


ALTER TABLE public.test_motherboard OWNER TO pc_builder_admin;

--
-- Name: test_motherboard_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.test_motherboard_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_motherboard_id_seq OWNER TO pc_builder_admin;

--
-- Name: test_motherboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.test_motherboard_id_seq OWNED BY public.test_motherboard.id;


--
-- Name: video_card; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.video_card (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(10,2),
    chipset character varying(100),
    memory numeric(5,2),
    core_clock numeric(6,2),
    boost_clock numeric(6,2),
    color character varying(50),
    length numeric(6,2),
    tdp integer,
    required_psu_wattage integer,
    pcie_version character varying(20),
    pcie_lanes_required integer,
    height numeric(6,2),
    power_connectors text[]
);


ALTER TABLE public.video_card OWNER TO pc_builder_admin;

--
-- Name: video_card_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.video_card_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_card_id_seq OWNER TO pc_builder_admin;

--
-- Name: video_card_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.video_card_id_seq OWNED BY public.video_card.id;


--
-- Name: case_enclosure id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.case_enclosure ALTER COLUMN id SET DEFAULT nextval('public.case_enclosure_id_seq'::regclass);


--
-- Name: cpu id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu ALTER COLUMN id SET DEFAULT nextval('public.cpu_id_seq'::regclass);


--
-- Name: cpu_cooler id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu_cooler ALTER COLUMN id SET DEFAULT nextval('public.cpu_cooler_id_seq'::regclass);


--
-- Name: memory id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.memory ALTER COLUMN id SET DEFAULT nextval('public.memory_id_seq'::regclass);


--
-- Name: motherboard id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard ALTER COLUMN id SET DEFAULT nextval('public.motherboard_id_seq'::regclass);


--
-- Name: motherboard_new id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard_new ALTER COLUMN id SET DEFAULT nextval('public.motherboard_new_id_seq'::regclass);


--
-- Name: motherboards id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboards ALTER COLUMN id SET DEFAULT nextval('public.motherboards_id_seq'::regclass);


--
-- Name: power_supply id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.power_supply ALTER COLUMN id SET DEFAULT nextval('public.power_supply_id_seq'::regclass);


--
-- Name: storage id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.storage ALTER COLUMN id SET DEFAULT nextval('public.storage_id_seq'::regclass);


--
-- Name: test_motherboard id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.test_motherboard ALTER COLUMN id SET DEFAULT nextval('public.test_motherboard_id_seq'::regclass);


--
-- Name: video_card id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.video_card ALTER COLUMN id SET DEFAULT nextval('public.video_card_id_seq'::regclass);


--
-- Name: case_enclosure case_enclosure_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.case_enclosure
    ADD CONSTRAINT case_enclosure_name_key UNIQUE (name);


--
-- Name: case_enclosure case_enclosure_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.case_enclosure
    ADD CONSTRAINT case_enclosure_pkey PRIMARY KEY (id);


--
-- Name: cpu_cooler cpu_cooler_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu_cooler
    ADD CONSTRAINT cpu_cooler_name_key UNIQUE (name);


--
-- Name: cpu_cooler cpu_cooler_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu_cooler
    ADD CONSTRAINT cpu_cooler_pkey PRIMARY KEY (id);


--
-- Name: cpu cpu_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu
    ADD CONSTRAINT cpu_name_key UNIQUE (name);


--
-- Name: cpu cpu_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu
    ADD CONSTRAINT cpu_pkey PRIMARY KEY (id);


--
-- Name: memory memory_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_name_key UNIQUE (name);


--
-- Name: memory memory_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_pkey PRIMARY KEY (id);


--
-- Name: motherboard motherboard_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard
    ADD CONSTRAINT motherboard_name_key UNIQUE (name);


--
-- Name: motherboard_new motherboard_new_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard_new
    ADD CONSTRAINT motherboard_new_pkey PRIMARY KEY (id);


--
-- Name: motherboard motherboard_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard
    ADD CONSTRAINT motherboard_pkey PRIMARY KEY (id);


--
-- Name: motherboards motherboards_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboards
    ADD CONSTRAINT motherboards_pkey PRIMARY KEY (id);


--
-- Name: power_supply power_supply_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.power_supply
    ADD CONSTRAINT power_supply_name_key UNIQUE (name);


--
-- Name: power_supply power_supply_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.power_supply
    ADD CONSTRAINT power_supply_pkey PRIMARY KEY (id);


--
-- Name: storage storage_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_name_key UNIQUE (name);


--
-- Name: storage storage_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_pkey PRIMARY KEY (id);


--
-- Name: test_motherboard test_motherboard_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.test_motherboard
    ADD CONSTRAINT test_motherboard_pkey PRIMARY KEY (id);


--
-- Name: video_card video_card_name_key; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.video_card
    ADD CONSTRAINT video_card_name_key UNIQUE (name);


--
-- Name: video_card video_card_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.video_card
    ADD CONSTRAINT video_card_pkey PRIMARY KEY (id);


--
-- Name: idx_case_max_gpu; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_case_max_gpu ON public.case_enclosure USING btree (max_gpu_length);


--
-- Name: idx_case_mobo_sizes; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_case_mobo_sizes ON public.case_enclosure USING gin (supported_motherboard_sizes);


--
-- Name: idx_case_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_case_name ON public.case_enclosure USING btree (name);


--
-- Name: idx_case_radiator; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_case_radiator ON public.case_enclosure USING gin (radiator_support);


--
-- Name: idx_cooler_sockets; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_cooler_sockets ON public.cpu_cooler USING gin (supported_sockets);


--
-- Name: idx_cpu_chipset_support; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_cpu_chipset_support ON public.cpu USING btree (chipset_support);


--
-- Name: idx_cpu_cooler_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_cpu_cooler_name ON public.cpu_cooler USING btree (name);


--
-- Name: idx_cpu_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_cpu_name ON public.cpu USING btree (name);


--
-- Name: idx_cpu_socket; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_cpu_socket ON public.cpu USING btree (socket_type);


--
-- Name: idx_gpu_length; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_gpu_length ON public.video_card USING btree (length);


--
-- Name: idx_gpu_power_connectors; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_gpu_power_connectors ON public.video_card USING gin (power_connectors);


--
-- Name: idx_memory_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_memory_name ON public.memory USING btree (name);


--
-- Name: idx_motherboard_memory_speeds; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_motherboard_memory_speeds ON public.motherboard USING gin (supported_memory_speeds);


--
-- Name: idx_motherboard_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_motherboard_name ON public.motherboard USING btree (name);


--
-- Name: idx_motherboard_socket; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_motherboard_socket ON public.motherboard USING btree (socket);


--
-- Name: idx_power_supply_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_power_supply_name ON public.power_supply USING btree (name);


--
-- Name: idx_psu_wattage; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_psu_wattage ON public.power_supply USING btree (wattage);


--
-- Name: idx_storage_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_storage_name ON public.storage USING btree (name);


--
-- Name: idx_video_card_name; Type: INDEX; Schema: public; Owner: pc_builder_admin
--

CREATE INDEX idx_video_card_name ON public.video_card USING btree (name);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO pc_builder_admin;


--
-- Name: FUNCTION clean_chipset_support(chipsets text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.clean_chipset_support(chipsets text[]) TO pc_builder_admin;


--
-- Name: FUNCTION extract_max_radiator_size(radiator_array text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.extract_max_radiator_size(radiator_array text[]) TO pc_builder_admin;


--
-- Name: FUNCTION get_highest_ddr(memory_types text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.get_highest_ddr(memory_types text) TO pc_builder_admin;


--
-- Name: FUNCTION get_max_radiator_size(radiator_array text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.get_max_radiator_size(radiator_array text[]) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_atx_version(version text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_atx_version(version text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_cooler_socket(socket text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_cooler_socket(socket text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_cooler_sockets(sockets text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_cooler_sockets(sockets text[]) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_mobo_size(size text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_mobo_size(size text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_mobo_sizes(sizes text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_mobo_sizes(sizes text[]) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_pcie_version(version text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_pcie_version(version text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_power_connector(connector text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_power_connector(connector text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_power_connectors(connectors text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_power_connectors(connectors text[]) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_protection_feature(feature text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_protection_feature(feature text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_protection_features(features text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_protection_features(features text[]) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_radiator_size(size text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_radiator_size(size text) TO pc_builder_admin;


--
-- Name: FUNCTION standardize_socket_name(socket_name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.standardize_socket_name(socket_name text) TO pc_builder_admin;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO pc_builder_admin;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO pc_builder_admin;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO pc_builder_admin;


--
-- PostgreSQL database dump complete
--

