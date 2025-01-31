import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from typing import Dict, List, Any, Optional
import asyncio
from ollama import AsyncClient
import re

# Configuration
CONTINUE_FROM_LAST = False  # Set to False to start fresh, True to continue from last position
BATCH_SIZE: Optional[int] = None  # Set to None for processing all records at once

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMDataEnricher:
    def __init__(self, db_params: Dict[str, str]):
        self.db_params = db_params
        self.conn = None
        self.cursor = None
        self.ollama_client = AsyncClient()

    async def connect(self):
        self.conn = psycopg2.connect(**self.db_params)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        logger.info("Connected to database")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_last_processed_id(self, table_name: str, column_name: str) -> int:
        """Get the last processed ID for a given table and column"""
        query = f"""
            SELECT MAX(id) FROM {table_name} 
            WHERE {column_name} IS NOT NULL
        """
        self.cursor.execute(query)
        return self.cursor.fetchone()['max'] or 0

    def build_select_query(self, table_name: str, last_id: int) -> str:
        """Build SELECT query based on BATCH_SIZE configuration"""
        query = f"""
            SELECT * FROM {table_name}
            WHERE id > {last_id}
            ORDER BY id
        """
        if BATCH_SIZE is not None:
            query += f"\nLIMIT {BATCH_SIZE}"
        return query

    def clean_llm_response(self, response: str) -> str:
        """Remove thinking part and extract just the JSON"""
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json_match.group(0)
        return None

    async def get_llm_completion(self, prompt: str) -> Dict:
        """Get completion from Ollama and process response"""
        try:
            response = await self.ollama_client.chat(
                model="qwen2.5:14b",
                messages=[{
                    "role": "system",
                    "content": """You are a PC hardware expert. Analyze the component specifications and provide 
                    detailed technical specifications in JSON format. Do not include explanations or thinking process in your response.
                    And your responses should be consistent throughout - for a field example: (PCIe4 or 4) choose one format and stick with it throughout the column
                    Provide only valid JSON with actual values, not placeholder values and nothing else. The output should only be json."""
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            
            json_str = self.clean_llm_response(response.message.content)
            if json_str:
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in response: {json_str}")
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Error getting LLM completion: {e}")
            return None

    async def enrich_cpu_data(self):
        """Enrich CPU data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('cpu', 'socket_type')
        
        query = self.build_select_query('cpu', last_id)
        self.cursor.execute(query)
        cpus = self.cursor.fetchall()

        if not cpus:
            logger.info("No new CPUs to process")
            return

        total = len(cpus)
        logger.info(f"Processing {total} CPUs...")

        for i, cpu in enumerate(cpus, 1):
            prompt = f"""
            Based on these CPU specifications:
            Name: {cpu['name']}
            Core Count: {cpu['core_count']}
            Core Clock: {cpu['core_clock']} GHz
            Boost Clock: {cpu['boost_clock']} GHz
            TDP: {cpu['tdp']}W
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "socket_type": "The actual socket type (e.g. AM4, LGA1700)",
                "memory_type_support": ["The actual supported memory types"],
                "memory_speed_support": actual_max_speed_in_mhz,
                "chipset_support": ["list", "of", "compatible", "chipsets"],
                "max_memory_support": max_memory_in_gb
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE cpu 
                        SET socket_type = %(socket_type)s,
                            memory_type_support = %(memory_type_support)s,
                            memory_speed_support = %(memory_speed_support)s,
                            chipset_support = %(chipset_support)s,
                            max_memory_support = %(max_memory_support)s
                        WHERE id = %(id)s
                    """
                    data['id'] = cpu['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated CPU {i}/{total}: {cpu['name']} (ID: {cpu['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating CPU {cpu['name']}: {e}")

    async def enrich_gpu_data(self):
        """Enrich GPU data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('video_card', 'tdp')
        
        query = self.build_select_query('video_card', last_id)
        self.cursor.execute(query)
        gpus = self.cursor.fetchall()

        if not gpus:
            logger.info("No new GPUs to process")
            return

        total = len(gpus)
        logger.info(f"Processing {total} GPUs...")

        for i, gpu in enumerate(gpus, 1):
            prompt = f"""
            Based on these GPU specifications:
            Name: {gpu['name']}
            Chipset: {gpu['chipset']}
            Memory: {gpu['memory']} GB
            Core Clock: {gpu['core_clock']} MHz
            Boost Clock: {gpu['boost_clock']} MHz
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "tdp": power_consumption_in_watts,
                "required_psu_wattage": recommended_psu_watts,
                "pcie_version": "actual_pcie_version",
                "pcie_lanes_required": number_of_lanes,
                "height": height_in_mm,
                "power_connectors": ["list", "of", "required", "connectors"]
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE video_card 
                        SET tdp = %(tdp)s,
                            required_psu_wattage = %(required_psu_wattage)s,
                            pcie_version = %(pcie_version)s,
                            pcie_lanes_required = %(pcie_lanes_required)s,
                            height = %(height)s,
                            power_connectors = %(power_connectors)s
                        WHERE id = %(id)s
                    """
                    data['id'] = gpu['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated GPU {i}/{total}: {gpu['name']} (ID: {gpu['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating GPU {gpu['name']}: {e}")

    async def enrich_motherboard_data(self):
        """Enrich motherboard data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('motherboard', 'chipset')
        query = self.build_select_query('motherboard', last_id)
        self.cursor.execute(query)
        motherboards = self.cursor.fetchall()

        if not motherboards:
            logger.info("No new motherboards to process")
            return

        total = len(motherboards)
        logger.info(f"Processing {total} motherboards...")

        for i, mobo in enumerate(motherboards, 1):
            prompt = f"""
            Based on these motherboard specifications:
            Name: {mobo['name']}
            Socket: {mobo['socket']}
            Form Factor: {mobo['form_factor']}
            Max Memory: {mobo['max_memory']}
            Memory Slots: {mobo['memory_slots']}
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "memory_type": "The memory type (DDR4/DDR5)",
                "supported_memory_speeds": [list_of_supported_speeds_in_mhz],
                "chipset": "actual_chipset_model",
                "pcie_version": "pcie_version_number",
                "max_pcie_lanes": number_of_lanes,
                "m2_slots": number_of_m2_slots,
                "sata_ports": number_of_sata_ports
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE motherboard 
                        SET memory_type = %(memory_type)s,
                            supported_memory_speeds = %(supported_memory_speeds)s,
                            chipset = %(chipset)s,
                            pcie_version = %(pcie_version)s,
                            max_pcie_lanes = %(max_pcie_lanes)s,
                            m2_slots = %(m2_slots)s,
                            sata_ports = %(sata_ports)s
                        WHERE id = %(id)s
                    """
                    data['id'] = mobo['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated Motherboard {i}/{total}: {mobo['name']} (ID: {mobo['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating motherboard {mobo['name']}: {e}")

    async def enrich_memory_data(self):
        """Enrich memory data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('memory', 'memory_type')
        query = self.build_select_query('memory', last_id)
        self.cursor.execute(query)
        memories = self.cursor.fetchall()

        if not memories:
            logger.info("No new memory modules to process")
            return

        total = len(memories)
        logger.info(f"Processing {total} memory modules...")

        for i, mem in enumerate(memories, 1):
            prompt = f"""
            Based on these memory specifications:
            Name: {mem['name']}
            Speed: {mem['speed']}
            Modules: {mem['modules']}
            CAS Latency: {mem['cas_latency']}
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "memory_type": "actual_memory_type",
                "voltage": voltage_in_volts,
                "memory_format": "DIMM_or_SODIMM",
                "ecc_support": boolean_true_or_false
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE memory 
                        SET memory_type = %(memory_type)s,
                            voltage = %(voltage)s,
                            memory_format = %(memory_format)s,
                            ecc_support = %(ecc_support)s
                        WHERE id = %(id)s
                    """
                    data['id'] = mem['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated Memory {i}/{total}: {mem['name']} (ID: {mem['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating memory {mem['name']}: {e}")

    async def enrich_storage_data(self):
        """Enrich storage data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('storage', 'nvme')
        query = self.build_select_query('storage', last_id)
        self.cursor.execute(query)
        storages = self.cursor.fetchall()

        if not storages:
            logger.info("No new storage devices to process")
            return

        total = len(storages)
        logger.info(f"Processing {total} storage devices...")

        for i, storage in enumerate(storages, 1):
            prompt = f"""
            Based on these storage specifications:
            Name: {storage['name']}
            Type: {storage['type']}
            Form Factor: {storage['form_factor']}
            Interface: {storage['interface']}
            Capacity: {storage['capacity']} GB
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "power_consumption": power_consumption_in_watts,
                "nvme": is_nvme_drive_boolean,
                "pcie_version": "pcie_version_if_nvme"
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE storage 
                        SET power_consumption = %(power_consumption)s,
                            nvme = %(nvme)s,
                            pcie_version = %(pcie_version)s
                        WHERE id = %(id)s
                    """
                    data['id'] = storage['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated Storage {i}/{total}: {storage['name']} (ID: {storage['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating storage {storage['name']}: {e}")

    async def enrich_case_data(self):
        """Enrich case data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('case_enclosure', 'max_gpu_length')
        query = self.build_select_query('case_enclosure', last_id)
        self.cursor.execute(query)
        cases = self.cursor.fetchall()

        if not cases:
            logger.info("No new cases to process")
            return

        total = len(cases)
        logger.info(f"Processing {total} cases...")

        for i, case in enumerate(cases, 1):
            prompt = f"""
            Based on these case specifications:
            Name: {case['name']}
            Type: {case['type']}
            External Volume: {case['external_volume']}
            Internal 3.5" Bays: {case['internal_35_bays']}
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "max_gpu_length": max_gpu_length_in_mm,
                "max_gpu_height": max_gpu_height_in_mm,
                "max_cpu_cooler_height": max_cpu_cooler_height_in_mm,
                "supported_motherboard_sizes": ["list", "of", "supported", "sizes"],
                "max_psu_length": max_psu_length_in_mm,
                "radiator_support": ["list", "of", "supported", "radiator", "sizes"],
                "included_fans": number_of_included_fans,
                "max_fan_slots": total_number_of_fan_slots
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE case_enclosure 
                        SET max_gpu_length = %(max_gpu_length)s,
                            max_gpu_height = %(max_gpu_height)s,
                            max_cpu_cooler_height = %(max_cpu_cooler_height)s,
                            supported_motherboard_sizes = %(supported_motherboard_sizes)s,
                            max_psu_length = %(max_psu_length)s,
                            radiator_support = %(radiator_support)s,
                            included_fans = %(included_fans)s,
                            max_fan_slots = %(max_fan_slots)s
                        WHERE id = %(id)s
                    """
                    data['id'] = case['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated Case {i}/{total}: {case['name']} (ID: {case['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating case {case['name']}: {e}")

    async def enrich_psu_data(self):
        """Enrich power supply data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('power_supply', 'psu_length')
        query = self.build_select_query('power_supply', last_id)
        self.cursor.execute(query)
        psus = self.cursor.fetchall()

        if not psus:
            logger.info("No new power supplies to process")
            return

        total = len(psus)
        logger.info(f"Processing {total} power supplies...")

        for i, psu in enumerate(psus, 1):
            prompt = f"""
            Based on these power supply specifications:
            Name: {psu['name']}
            Type: {psu['type']}
            Efficiency: {psu['efficiency']}
            Wattage: {psu['wattage']}
            Modular: {psu['modular']}
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "available_connectors": {{"cpu": number_of_cpu_connectors, "pcie": number_of_pcie_connectors, "sata": number_of_sata_connectors}},
                "psu_length": length_in_mm,
                "fan_size": fan_size_in_mm,
                "protection_features": ["list", "of", "protection", "features"],
                "atx_version": "atx_version_number"
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    # Convert the connectors dictionary to JSON string
                    if isinstance(data.get('available_connectors'), dict):
                        data['available_connectors'] = json.dumps(data['available_connectors'])

                    update_query = """
                        UPDATE power_supply 
                        SET available_connectors = %(available_connectors)s::jsonb,
                            psu_length = %(psu_length)s,
                            fan_size = %(fan_size)s,
                            protection_features = %(protection_features)s,
                            atx_version = %(atx_version)s
                        WHERE id = %(id)s
                    """
                    data['id'] = psu['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated PSU {i}/{total}: {psu['name']} (ID: {psu['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating PSU {psu['name']}: {e}")
                    logger.error(f"Data that caused error: {data}")  # Add this for debugging

    async def enrich_cooler_data(self):
        """Enrich CPU cooler data using LLM"""
        last_id = 0 if not CONTINUE_FROM_LAST else self.get_last_processed_id('cpu_cooler', 'height')
        query = self.build_select_query('cpu_cooler', last_id)
        self.cursor.execute(query)
        coolers = self.cursor.fetchall()

        if not coolers:
            logger.info("No new CPU coolers to process")
            return

        total = len(coolers)
        logger.info(f"Processing {total} CPU coolers...")

        for i, cooler in enumerate(coolers, 1):
            prompt = f"""
            Based on these CPU cooler specifications:
            Name: {cooler['name']}
            RPM: {cooler['rpm']}
            Noise Level: {cooler['noise_level']}
            Size: {cooler['size']}
            
            Return a JSON object with ONLY these fields and actual values (not placeholders):
            {{
                "supported_sockets": ["list", "of", "supported", "socket", "types"],
                "height": height_in_mm,
                "tdp_support": max_tdp_support_in_watts,
                "radiator_size": "radiator_size_if_liquid_cooler",
                "clearance_required": clearance_required_in_mm
            }}
            """

            data = await self.get_llm_completion(prompt)
            if data:
                try:
                    update_query = """
                        UPDATE cpu_cooler 
                        SET supported_sockets = %(supported_sockets)s,
                            height = %(height)s,
                            tdp_support = %(tdp_support)s,
                            radiator_size = %(radiator_size)s,
                            clearance_required = %(clearance_required)s
                        WHERE id = %(id)s
                    """
                    data['id'] = cooler['id']
                    self.cursor.execute(update_query, data)
                    self.conn.commit()
                    logger.info(f"Updated CPU Cooler {i}/{total}: {cooler['name']} (ID: {cooler['id']})")
                except Exception as e:
                    self.conn.rollback()
                    logger.error(f"Error updating CPU Cooler {cooler['name']}: {e}")
                    logger.error(f"Data that caused error: {data}")  # Add this for debugging

    async def run_enrichment(self):
        """Run all enrichment tasks"""
        await self.connect()
        try:
            logger.info("Starting enrichment process...")
            
            # Process all component types
            await self.enrich_cpu_data()
            await self.enrich_motherboard_data()
            await self.enrich_memory_data()
            await self.enrich_storage_data()
            await self.enrich_gpu_data()
            await self.enrich_case_data()
            await self.enrich_psu_data()
            await self.enrich_cooler_data()
            
            logger.info("Completed enrichment process")
        except Exception as e:
            logger.error(f"Error during enrichment process: {e}")
        finally:
            self.close()

async def main():
    # Configuration for the database connection
    db_params = {
        'dbname': 'pc_builder',
        'user': 'pc_builder_admin',
        'password': 'pc_builder',
        'host': 'localhost',
        'port': '5432'
    }

    # Create and run the enricher
    enricher = LLMDataEnricher(db_params)
    await enricher.run_enrichment()

if __name__ == "__main__":
    asyncio.run(main())