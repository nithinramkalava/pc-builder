import { NextResponse } from "next/server";
import { Pool } from "pg";

// Create a new connection pool (adjust config as needed)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Map our part types (as used in the UI) to the underlying database table names.
const TABLE_MAP: Record<string, string> = {
  cpu: "cpu",
  motherboard: "motherboard",
  cpuCooler: "cpu_cooler", // note: use underscore for table name (if that's how it's stored)
  gpu: "video_card",
  case: "case_enclosure",
  psu: "power_supply",
  ram: "memory", // mapping "ram" to the "memory" table
  storage: "storage", // assume a table "storage" exists
};

export async function GET(
  request: Request,
  { params }: { params: { partType: string } }
) {
  // Await the params before using its properties
  const { partType } = await Promise.resolve(params);
  const tableName = TABLE_MAP[partType];

  if (!tableName) {
    return NextResponse.json({ error: "Invalid part type" }, { status: 400 });
  }

  try {
    const client = await pool.connect();
    try {
      // For simplicity, we are selecting id, name, and price.
      // Extend this query if you need additional fields.
      const queryText = `SELECT id, name, price FROM ${tableName}`;
      const result = await client.query(queryText);
      return NextResponse.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : "An unknown error occurred";
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
