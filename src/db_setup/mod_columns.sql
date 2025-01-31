-- Alter CPU table
ALTER TABLE cpu
ADD COLUMN socket_type VARCHAR(50),
ADD COLUMN memory_type_support VARCHAR(50),
ADD COLUMN memory_speed_support INTEGER,
ADD COLUMN chipset_support TEXT[], -- Array of compatible chipsets
ADD COLUMN max_memory_support INTEGER;

-- Alter Motherboard table
ALTER TABLE motherboard
ADD COLUMN memory_type VARCHAR(50),
ADD COLUMN supported_memory_speeds INTEGER[], -- Array of supported speeds
ADD COLUMN chipset VARCHAR(50),
ADD COLUMN pcie_version VARCHAR(20),
ADD COLUMN max_pcie_lanes INTEGER,
ADD COLUMN m2_slots INTEGER,
ADD COLUMN sata_ports INTEGER;

-- Alter Memory table
ALTER TABLE memory
ADD COLUMN memory_type VARCHAR(50),
ADD COLUMN voltage DECIMAL(4,2),
ADD COLUMN memory_format VARCHAR(50),
ADD COLUMN ecc_support BOOLEAN;

-- Alter Storage table
ALTER TABLE storage
ADD COLUMN power_consumption INTEGER,
ADD COLUMN nvme BOOLEAN,
ADD COLUMN pcie_version VARCHAR(20);

-- Alter Video Card (GPU) table
ALTER TABLE video_card
ADD COLUMN tdp INTEGER,
ADD COLUMN required_psu_wattage INTEGER,
ADD COLUMN pcie_version VARCHAR(20),
ADD COLUMN pcie_lanes_required INTEGER,
ADD COLUMN height DECIMAL(6,2),
ADD COLUMN power_connectors TEXT[]; -- Array of required connectors

-- Alter Case table
ALTER TABLE case_enclosure
ADD COLUMN max_gpu_length DECIMAL(6,2),
ADD COLUMN max_gpu_height DECIMAL(6,2),
ADD COLUMN max_cpu_cooler_height DECIMAL(6,2),
ADD COLUMN supported_motherboard_sizes TEXT[], -- Array of supported sizes
ADD COLUMN max_psu_length DECIMAL(6,2),
ADD COLUMN radiator_support TEXT[], -- Array of supported radiator sizes
ADD COLUMN included_fans INTEGER,
ADD COLUMN max_fan_slots INTEGER;

-- Alter Power Supply table
ALTER TABLE power_supply
ADD COLUMN available_connectors JSONB, -- JSON of connector types and counts
ADD COLUMN psu_length DECIMAL(6,2),
ADD COLUMN fan_size INTEGER,
ADD COLUMN protection_features TEXT[],
ADD COLUMN atx_version VARCHAR(20);

-- Alter CPU Cooler table
ALTER TABLE cpu_cooler
ADD COLUMN supported_sockets TEXT[], -- Array of supported socket types
ADD COLUMN height DECIMAL(6,2),
ADD COLUMN tdp_support INTEGER,
ADD COLUMN radiator_size VARCHAR(50),
ADD COLUMN clearance_required DECIMAL(6,2);

-- Create indexes for commonly queried compatibility fields
CREATE INDEX idx_cpu_socket ON cpu(socket_type);
CREATE INDEX idx_motherboard_socket ON motherboard(socket);
CREATE INDEX idx_memory_type ON memory(memory_type);
CREATE INDEX idx_gpu_length ON video_card(length);
CREATE INDEX idx_case_max_gpu ON case_enclosure(max_gpu_length);
CREATE INDEX idx_psu_wattage ON power_supply(wattage);

-- Create GIN indexes for array fields
CREATE INDEX idx_cpu_chipset_support ON cpu USING gin(chipset_support);
CREATE INDEX idx_motherboard_memory_speeds ON motherboard USING gin(supported_memory_speeds);
CREATE INDEX idx_gpu_power_connectors ON video_card USING gin(power_connectors);
CREATE INDEX idx_case_mobo_sizes ON case_enclosure USING gin(supported_motherboard_sizes);
CREATE INDEX idx_case_radiator ON case_enclosure USING gin(radiator_support);
CREATE INDEX idx_cooler_sockets ON cpu_cooler USING gin(supported_sockets);

-- Add some example compatibility check functions
CREATE OR REPLACE FUNCTION check_cpu_motherboard_compatibility(
    cpu_id INTEGER,
    motherboard_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    cpu_socket VARCHAR(50);
    mobo_socket VARCHAR(50);
BEGIN
    SELECT socket_type INTO cpu_socket FROM cpu WHERE id = cpu_id;
    SELECT socket INTO mobo_socket FROM motherboard WHERE id = motherboard_id;
    RETURN cpu_socket = mobo_socket;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_case_gpu_compatibility(
    case_id INTEGER,
    gpu_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    case_max_length DECIMAL(6,2);
    gpu_length DECIMAL(6,2);
BEGIN
    SELECT max_gpu_length INTO case_max_length FROM case_enclosure WHERE id = case_id;
    SELECT length INTO gpu_length FROM video_card WHERE id = gpu_id;
    RETURN case_max_length >= gpu_length;
END;
$$ LANGUAGE plpgsql;



