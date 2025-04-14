import React from "react";

// Define types for the build recommendation results
interface ComponentDetails {
  [key: string]: string | number | boolean | null;
}

interface ComponentInfo {
  name: string;
  price: string;
  price_inr: string;
  details: ComponentDetails;
}

export interface BuildRecommendation {
  components: {
    [key: string]: ComponentInfo;
  };
  selection_order: string[];
  total_cost_usd: string;
  total_cost_inr: string;
  budget_inr: string;
  budget_usd: string;
  status: string;
  remaining_budget_inr?: string;
  selection_errors?: {
    [key: string]: string;
  };
  error?: string;
}

interface BuildResultDisplayProps {
  pcBuild: BuildRecommendation;
  onRestart: () => void;
}

const BuildResultDisplay: React.FC<BuildResultDisplayProps> = ({
  pcBuild,
  onRestart,
}) => {
  // Format price for display
  const formatPrice = (price: string): string => {
    if (!price) return "N/A";
    return price;
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div className="mb-6 text-center">
            <h2 className="text-3xl font-bold mb-2 text-white">
              Your Custom PC Build
            </h2>
            <p className="text-gray-300 mb-6">
              Based on your requirements, here&apos;s the optimized build
              recommendation
            </p>

            <div className="flex flex-col md:flex-row justify-between gap-4 bg-gray-950 bg-opacity-60 p-4 rounded-lg mb-4 border border-gray-800">
              <div className="text-center">
                <span className="text-gray-400 block text-sm mb-1">
                  Budget:
                </span>
                <div className="text-xl font-semibold text-white">
                  {pcBuild.budget_inr}
                </div>
              </div>
              <div className="text-center">
                <span className="text-gray-400 block text-sm mb-1">
                  Total Cost:
                </span>
                <div className="text-xl font-semibold text-white">
                  {pcBuild.total_cost_inr}
                </div>
              </div>
              <div className="text-center">
                <span className="text-gray-400 block text-sm mb-1">
                  Status:
                </span>
                <div
                  className={`text-xl font-semibold ${
                    pcBuild.status.includes("Over budget")
                      ? "text-red-400"
                      : "text-emerald-400"
                  }`}
                >
                  {pcBuild.status}
                </div>
              </div>
            </div>

            {pcBuild.remaining_budget_inr && (
              <div className="text-emerald-400 mb-4">
                Remaining Budget: {pcBuild.remaining_budget_inr}
              </div>
            )}
          </div>

          <div className="space-y-4">
            {pcBuild.selection_order.map((type) => {
              const component = pcBuild.components[type];
              if (!component) return null;

              return (
                <div
                  key={type}
                  className="bg-gray-950 bg-opacity-40 p-4 rounded-lg transition-all hover:bg-opacity-60 border border-gray-800"
                >
                  <div className="flex flex-col md:flex-row md:justify-between md:items-start">
                    <div className="md:w-1/4 mb-2 md:mb-0">
                      <h3 className="font-semibold text-gray-300 capitalize">
                        {type}
                      </h3>
                    </div>
                    <div className="md:w-3/4">
                      <div className="font-semibold text-white text-lg mb-1">
                        {component.name}
                      </div>
                      <div className="text-blue-300 mb-3">
                        {formatPrice(component.price_inr)}
                      </div>

                      {component.details &&
                        Object.keys(component.details).length > 0 && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            {Object.entries(component.details).map(
                              ([key, value]) => {
                                // Format the key for better display
                                const formattedKey = key
                                  .replace(/([A-Z])/g, " $1")
                                  .replace(/^./, (str) => str.toUpperCase())
                                  .replace(/_/g, " ");

                                return (
                                  <div key={key} className="flex">
                                    <span className="text-gray-500 mr-1">
                                      {formattedKey}:
                                    </span>
                                    <span className="text-gray-300">
                                      {value}
                                    </span>
                                  </div>
                                );
                              }
                            )}
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 text-center">
            <button
              onClick={onRestart}
              className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200 font-semibold border border-gray-700"
            >
              Start a New Build
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuildResultDisplay;
