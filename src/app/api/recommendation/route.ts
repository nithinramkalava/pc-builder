import { NextResponse } from "next/server";
import { writeFile } from "fs/promises";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import fs from "fs/promises";

const execAsync = promisify(exec);

export async function POST(request: Request) {
  try {
    const { preferences } = await request.json();

    // Generate a unique ID for this request
    const requestId = uuidv4();

    // Create temp directory if it doesn't exist
    const tempDir = path.join(process.cwd(), "temp");
    try {
      await fs.mkdir(tempDir, { recursive: true });
    } catch (err) {
      console.error("Error creating temp directory:", err);
    }

    // Create input file path
    const inputFilePath = path.join(tempDir, `input_${requestId}.json`);

    // Write preferences to input file
    await writeFile(inputFilePath, JSON.stringify(preferences, null, 2));

    console.log(`Created input file: ${inputFilePath}`);

    // Path to Python script
    const pythonScriptPath = path.join(
      process.cwd(),
      "src",
      "recommendation",
      "recommendation_system.py"
    );

    // Path for output results
    const outputFilePath = path.join(tempDir, `output_${requestId}.json`);

    // Execute the Python script with the input file
    const command = `python "${pythonScriptPath}" --input "${inputFilePath}" --output "${outputFilePath}"`;

    console.log(`Executing command: ${command}`);

    const { stdout, stderr } = await execAsync(command);

    if (stderr) {
      console.error("Python script error:", stderr);
    }

    console.log("Python script output:", stdout);

    // Read the output file
    let recommendationResult;
    try {
      const outputContent = await fs.readFile(outputFilePath, "utf-8");
      recommendationResult = JSON.parse(outputContent);
      console.log("Recommendation result loaded");
    } catch (readErr) {
      console.error("Error reading output file:", readErr);
      throw new Error("Failed to read recommendation results");
    }

    // Clean up temporary files
    try {
      await fs.unlink(inputFilePath);
      await fs.unlink(outputFilePath);
    } catch (cleanupErr) {
      console.error("Error cleaning up temporary files:", cleanupErr);
    }

    return NextResponse.json(recommendationResult);
  } catch (error) {
    console.error("Recommendation API error:", error);
    return NextResponse.json(
      {
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}
