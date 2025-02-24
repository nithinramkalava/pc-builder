// src/app/api/parts/[partType]/route.ts
import { NextResponse } from "next/server";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const TABLE_MAP: Record<string, string> = {
  cpu: "cpu",
  motherboard: "motherboard",
  cpuCooler: "cpu_cooler",
  gpu: "video_card",
  case: "case_enclosure",
  psu: "power_supply",
  ram: "memory",
  storage: "storage",
};

export async function GET(
  request: Request,
  { params }: { params: Promise<{ partType: string }> } // Change to Promise
) {
  const resolvedParams = await params; // Await the params
  const { partType } = resolvedParams;
  const tableName = TABLE_MAP[partType];
  const { searchParams } = new URL(request.url);

  if (!tableName) {
    return NextResponse.json({ error: "Invalid part type" }, { status: 400 });
  }

  try {
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
          if (!gpuId) throw new Error("GPU ID required");
          queryText = "SELECT * FROM case_enclosure"; // "SELECT * FROM get_compatible_case($1)";
          // params = [gpuId];
          break;

        case "psu":
          const caseId = searchParams.get("case_id");
          const requiredWattage = "500" // searchParams.get("required_wattage") ||;
          if (!caseId) throw new Error("Case ID required");
          queryText = "SELECT * FROM get_compatible_psu($1, $2)";
          params = [requiredWattage, caseId];
          break;

        case "ram":
          const ramMoboId = searchParams.get("mobo_id");
          const ramCpuId = searchParams.get("cpu_id");
          if (!ramMoboId || !ramCpuId) throw new Error("Motherboard and CPU IDs required");
          queryText = "SELECT * FROM get_compatible_ram($1, $2)";
          params = [ramMoboId, ramCpuId];
          break;

        default:
          queryText = `SELECT id, name, price FROM ${tableName}`;
          break;
      }

      const result = await client.query(queryText, params);
      return NextResponse.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}