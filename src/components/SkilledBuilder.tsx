// src/components/SkilledBuilder.tsx
"use client";

import { useState, useEffect } from "react";

type Part = {
  id: number;
  name: string;
  price: number;
};

export type PartType =
  | "cpu"
  | "motherboard"
  | "cpuCooler"
  | "gpu"
  | "case"
  | "psu"
  | "ram"
  | "storage";

type SelectedParts = { [K in PartType]?: Part };

// Build order is now in the preferred sequence.
const partOrder: PartType[] = [
  "cpu",
  "motherboard",
  "cpuCooler",
  "gpu",
  "case",
  "psu",
  "ram",
  "storage",
];

const SkilledBuilder = () => {
  const [currentPartIndex, setCurrentPartIndex] = useState(0);
  const [selectedParts, setSelectedParts] = useState<SelectedParts>({});
  const [partsData, setPartsData] = useState<Part[]>([]);
  const [loadingParts, setLoadingParts] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Convert stage key into a nicer label.
  const formatStageLabel = (stage: string) => {
    if (stage === "cpuCooler") return "CPU Cooler";
    return stage.charAt(0).toUpperCase() + stage.slice(1);
  };

  // Allow the user to click on a previously completed stage to go back.
  const handleStageClick = (stageIndex: number) => {
    if (stageIndex < currentPartIndex) {
      // Remove any selections for later stages.
      const newSelectedParts = { ...selectedParts };
      for (let i = stageIndex; i < partOrder.length; i++) {
        delete newSelectedParts[partOrder[i]];
      }
      setSelectedParts(newSelectedParts);
      setCurrentPartIndex(stageIndex);
    }
  };

  const currentPart = partOrder[currentPartIndex];
  const isComplete = currentPartIndex >= partOrder.length;

  // When a part is selected, record the selection and move to the next stage.
  const handlePartSelect = (part: Part) => {
    setSelectedParts((prev) => ({
      ...prev,
      [currentPart]: part,
    }));
    setCurrentPartIndex((prev) => prev + 1);
  };

  // Fetch the parts for the current stage from the API.
  useEffect(() => {
    const fetchParts = async () => {
      setLoadingParts(true);
      setError(null);
      try {
        const res = await fetch(`/api/parts/${currentPart}`);
        if (!res.ok) {
          throw new Error("Failed to fetch parts");
        }
        const data: Part[] = await res.json();
        setPartsData(data);
      } catch (err: unknown) {
        const errorMessage =
          err instanceof Error ? err.message : "An error occurred";
        setError(errorMessage);
      } finally {
        setLoadingParts(false);
      }
    };

    if (!isComplete) {
      fetchParts();
    }
    // Reset search term when the stage changes.
    setSearchTerm("");
  }, [currentPart, isComplete]);

  // Filter parts based on the search term (case-insensitive).
  const filteredParts = partsData.filter((part) =>
    part.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPrice = Object.values(selectedParts).reduce(
    (sum, part) => sum + (part?.price || 0),
    0
  );

  return (
    <div className="space-y-6">
      {/* Stage Navigation Bar */}
      <div className="flex items-center space-x-2">
        {partOrder.map((stage, index) => {
          const isCompleted = index < currentPartIndex;
          const isCurrent = index === currentPartIndex;
          const label = formatStageLabel(stage);

          let stageClasses = "px-3 py-1 rounded text-sm";
          if (isCompleted) {
            stageClasses += " bg-green-500 text-white cursor-pointer";
          } else if (isCurrent) {
            stageClasses += " bg-blue-500 text-white";
          } else {
            stageClasses += " bg-gray-300 text-gray-600";
          }

          return (
            <div key={stage} className="flex items-center">
              <div
                className={stageClasses}
                onClick={() => isCompleted && handleStageClick(index)}
              >
                {label} {isCompleted && <span>&#10003;</span>}
              </div>
              {index < partOrder.length - 1 && (
                <span className="text-gray-500">&#8594;</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Main Content: Either Build Summary or the Part Selection Pane */}
      {isComplete ? (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Your Build Summary</h2>
          {Object.entries(selectedParts).map(([type, part]) => (
            <div
              key={type}
              className="flex justify-between items-center bg-gray-100 p-4 rounded text-black shadow-sm"
            >
              <span className="font-medium capitalize">
                {formatStageLabel(type)}
              </span>
              <div className="text-right">
                <div>{part?.name}</div>
                <div className="text-black">
                  ₹{(part?.price * 83).toLocaleString("en-IN")}
                </div>
              </div>
            </div>
          ))}
          <div className="text-xl font-bold text-right">
            Total: ₹{(totalPrice * 83).toLocaleString("en-IN")}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">
            Select your {formatStageLabel(currentPart)}
          </h2>
          {/* Realtime Search Bar */}
          <input
            type="text"
            placeholder={`Search ${formatStageLabel(currentPart)}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="p-2 border rounded w-full text-black"
          />
          {loadingParts ? (
            <div>Loading...</div>
          ) : error ? (
            <div className="text-red-500">Error: {error}</div>
          ) : (
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {filteredParts.map((part) => (
                <button
                  key={part.id}
                  onClick={() => handlePartSelect(part)}
                  className="p-4 border rounded text-left space-y-2 text-white bg-gray-800 hover:bg-gray-700 transition-colors duration-200"
                >
                  <div className="font-medium">{part.name}</div>
                  <div className="text-white">
                    ₹{(part.price * 83).toLocaleString("en-IN")}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SkilledBuilder;
