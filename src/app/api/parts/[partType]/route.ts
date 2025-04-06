// src/app/api/parts/[partType]/route.ts
import { NextResponse } from "next/server";
import { Pool } from "pg";

// Create a pool with error logging
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Log any pool errors
pool.on("error", (err) => {
  console.error("Unexpected error on idle client", err);
});

const TABLE_MAP: Record<string, string> = {
  cpu: "cpu_specs",
  motherboard: "motherboard_specs",
  cpuCooler: "cooler_specs",
  gpu: "gpu_specs",
  case: "case_specs",
  psu: "psu_specs",
  ram: "memory_specs",
  storage: "ssd_specs",
};

export async function GET(
  request: Request,
  { params }: { params: Promise<{ partType: string }> }
) {
  const resolvedParams = await params;
  const { partType } = resolvedParams;
  const tableName = TABLE_MAP[partType];
  const { searchParams } = new URL(request.url);

  if (!tableName) {
    return NextResponse.json({ error: "Invalid part type" }, { status: 400 });
  }

  try {
    console.log(
      `Connecting to database to fetch ${partType} from ${tableName}...`
    );
    const client = await pool.connect();
    try {
      let queryText: string;
      let params: unknown[] = [];

      switch (partType) {
        case "motherboard":
          const cpuId = searchParams.get("cpu_id");
          if (!cpuId) throw new Error("CPU ID required");
          queryText = "SELECT * FROM get_compatible_motherboards($1)";
          params = [cpuId];
          break;

        case "cpuCooler":
          const coolerCpuId = searchParams.get("cpu_id");
          if (!coolerCpuId) throw new Error("CPU ID required");
          queryText = "SELECT * FROM get_compatible_cpu_coolers($1)";
          params = [coolerCpuId];
          break;

        case "gpu":
          const moboId = searchParams.get("mobo_id");
          if (!moboId) throw new Error("Motherboard ID required");
          queryText = "SELECT * FROM get_compatible_video_cards($1)";
          params = [moboId];
          break;

        case "case":
          const gpuId = searchParams.get("gpu_id");
          const caseMotherboardId = searchParams.get("mobo_id");
          if (!gpuId || !caseMotherboardId)
            throw new Error("GPU ID and Motherboard ID required");
          queryText = "SELECT * FROM get_compatible_case($1, $2)";
          params = [gpuId, caseMotherboardId];
          break;

        case "psu":
          const caseId = searchParams.get("case_id");
          const cpuIdForPsu = searchParams.get("cpu_id");
          const gpuIdForPsu = searchParams.get("gpu_id");

          if (!caseId || !cpuIdForPsu || !gpuIdForPsu) {
            throw new Error(
              "Case ID, CPU ID, and GPU ID required for PSU compatibility"
            );
          }

          // Get CPU TDP
          const cpuResult = await client.query(
            "SELECT tdp FROM cpu_specs WHERE id = $1",
            [cpuIdForPsu]
          );

          // Get GPU TDP
          const gpuResult = await client.query(
            "SELECT tdp FROM gpu_specs WHERE id = $1",
            [gpuIdForPsu]
          );

          if (cpuResult.rows.length === 0 || gpuResult.rows.length === 0) {
            throw new Error("Could not find CPU or GPU TDP values");
          }

          // Extract TDP values and convert to numbers
          let cpuTdp = 0;
          let gpuTdp = 0;

          if (cpuResult.rows[0].tdp) {
            const cpuTdpMatch = cpuResult.rows[0].tdp.match(/(\d+)/);
            if (cpuTdpMatch) cpuTdp = parseInt(cpuTdpMatch[0], 10);
          }

          if (gpuResult.rows[0].tdp) {
            const gpuTdpMatch = gpuResult.rows[0].tdp.match(/(\d+)/);
            if (gpuTdpMatch) gpuTdp = parseInt(gpuTdpMatch[0], 10);
          }

          // Calculate total wattage with 50% headroom
          const totalTdp = cpuTdp + gpuTdp;
          const requiredWattage = Math.ceil(totalTdp * 1.5);

          queryText = "SELECT * FROM get_compatible_psu($1, $2)";
          params = [requiredWattage, caseId];
          break;

        case "ram":
          const ramMoboId = searchParams.get("mobo_id");
          const ramCpuId = searchParams.get("cpu_id");
          if (!ramMoboId || !ramCpuId)
            throw new Error("Motherboard and CPU IDs required");
          queryText = "SELECT * FROM get_compatible_ram($1, $2)";
          params = [ramMoboId, ramCpuId];
          break;

        case "storage":
          const storageMotherboardId = searchParams.get("mobo_id");
          if (!storageMotherboardId) throw new Error("Motherboard ID required");
          queryText = "SELECT * FROM get_compatible_ssd($1)";
          params = [storageMotherboardId];
          break;

        default:
          // For CPU and other simple part types, just select key fields
          queryText = `SELECT id, name, price FROM ${tableName} ORDER BY id ASC`;
          break;
      }

      console.log(`Executing query: ${queryText} with params:`, params);
      const result = await client.query(queryText, params);
      console.log(`Query returned ${result.rows.length} rows`);

      // Add debug logging for storage data
      if (partType === "storage" && result.rows.length > 0) {
        console.log("Storage API result sample:", {
          firstRow: result.rows[0],
          hasCapacityField: "capacity" in result.rows[0],
          capacityValue: result.rows[0].capacity,
          capacityType: typeof result.rows[0].capacity,
        });
      }

      return NextResponse.json(result.rows);
    } catch (queryError) {
      console.error("Database query error:", queryError);
      throw queryError;
    } finally {
      client.release();
    }
  } catch (error: unknown) {
    console.error("API error:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
