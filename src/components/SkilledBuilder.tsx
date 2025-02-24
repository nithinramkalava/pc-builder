// src/components/SkilledBuilder.tsx
"use client";

import { useState, useEffect } from "react";

type Part = {
  id: number;
  name: string;
  price: number | string | null;
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

  const formatStageLabel = (stage: string) => {
    if (stage === "cpuCooler") return "CPU Cooler";
    return stage.charAt(0).toUpperCase() + stage.slice(1);
  };

  const handleStageClick = (stageIndex: number) => {
    if (stageIndex < currentPartIndex) {
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

  const handlePartSelect = (part: Part) => {
    console.log(`[Client] Selected ${currentPart}:`, {
      id: part.id,
      name: part.name,
      price: part.price,
      priceType: typeof part.price
    });
    setSelectedParts((prev) => ({
      ...prev,
      [currentPart]: part,
    }));
    setCurrentPartIndex((prev) => prev + 1);
  };

  useEffect(() => {
    const fetchParts = async () => {
      setLoadingParts(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams();
        
        switch (currentPart) {
          case "motherboard":
            if (selectedParts.cpu?.id) queryParams.set("cpu_id", selectedParts.cpu.id.toString());
            break;
          case "cpuCooler":
            if (selectedParts.cpu?.id) queryParams.set("cpu_id", selectedParts.cpu.id.toString());
            break;
          case "gpu":
            if (selectedParts.motherboard?.id) queryParams.set("mobo_id", selectedParts.motherboard.id.toString());
            break;
          case "case":
            if (selectedParts.gpu?.id) queryParams.set("gpu_id", selectedParts.gpu.id.toString());
            break;
          case "psu":
            if (selectedParts.case?.id) {
              queryParams.set("case_id", selectedParts.case.id.toString());
              const estimatedWattage = 
                (Number(selectedParts.cpu?.price) || 0) + 
                (Number(selectedParts.gpu?.price) || 0) + 
                100;
              queryParams.set("required_wattage", estimatedWattage.toString());
            }
            break;
          case "ram":
            if (selectedParts.motherboard?.id && selectedParts.cpu?.id) {
              queryParams.set("mobo_id", selectedParts.motherboard.id.toString());
              queryParams.set("cpu_id", selectedParts.cpu.id.toString());
            }
            break;
        }

        const url = `/api/parts/${currentPart}?${queryParams.toString()}`;
        console.log(`[Client] Fetching parts for ${currentPart} from: ${url}`);
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch parts");
        const data: Part[] = await res.json();
        console.log(`[Client] Received ${currentPart} data:`, data.map(part => ({
          id: part.id,
          name: part.name,
          price: part.price,
          priceType: typeof part.price
        })));
        setPartsData(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoadingParts(false);
      }
    };

    if (!isComplete) fetchParts();
    setSearchTerm("");
  }, [currentPart, isComplete, selectedParts]);

  const filteredParts = partsData.filter((part) =>
    part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false
  );

  const calculateTotal = () => {
    const parts = Object.values(selectedParts);
    console.log("[Client] All selected parts for total calculation:", parts.map(part => ({
      name: part?.name,
      price: part?.price,
      priceType: typeof part?.price
    })));
    let hasMissingPrice = false;
    const total = parts.reduce((sum, part) => {
      if (part) {
        const price = Number(part.price); // Convert to number here
        console.log(`[Client] Processing part: ${part.name}, raw price: ${part.price}, converted price: ${price}, type: ${typeof price}`);
        if (!isNaN(price) && price !== null && price !== undefined) {
          return sum + price; // Add the converted number
        }
        hasMissingPrice = true;
      }
      return sum;
    }, 0);

    console.log(`[Client] Calculated total before conversion: ${total}, hasMissingPrice: ${hasMissingPrice}`);
    const formattedTotal = (total * 83).toLocaleString("en-IN");
    return {
      totalText: hasMissingPrice ? `${formattedTotal} + extra` : formattedTotal,
      hasMissingPrice
    };
  };

  const { totalText, hasMissingPrice } = calculateTotal();

  return (
    <div className="space-y-6">
      <div className="border-b flex">
        {partOrder.map((stage, index) => {
          const isCurrent = index === currentPartIndex;
          const isCompleted = index < currentPartIndex;
          const label = formatStageLabel(stage);
          const tabClasses = `cursor-pointer px-4 py-2 border-b-2 ${
            isCurrent
              ? "border-white font-semibold text-white"
              : "border-transparent text-gray-500"
          }`;
          return (
            <div
              key={stage}
              onClick={() => isCompleted && handleStageClick(index)}
            >
              <div className={tabClasses}>
                {label} {isCompleted && <span>✓</span>}
              </div>
            </div>
          );
        })}
      </div>

      {isComplete ? (
        <div className="space-y-4 mt-4">
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
                <div>
                  {part && !isNaN(Number(part.price)) && part.price !== null && part.price !== undefined
                    ? `₹${(Number(part.price) * 83).toLocaleString("en-IN")}`
                    : "Price unavailable"}
                </div>
              </div>
            </div>
          ))}
          <div className="text-xl font-bold text-right">
            Total: ₹{totalText}
            {hasMissingPrice && (
              <span className="text-sm font-normal ml-2 text-gray-600">
                (Some parts missing price data)
              </span>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-4 mt-4">
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
                  <div>
                    {part && !isNaN(Number(part.price)) && part.price !== null && part.price !== undefined
                      ? `₹${(Number(part.price) * 83).toLocaleString("en-IN")}`
                      : "Price unavailable"}
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