import React from "react";

const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
      <div className="relative w-32 h-32 mb-8">
        <div className="absolute top-0 left-0 w-full h-full border-8 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <div className="absolute top-4 left-4 w-24 h-24 border-8 border-blue-300 border-t-transparent rounded-full animate-spin-slow"></div>
        <div className="absolute top-8 left-8 w-16 h-16 border-8 border-purple-400 border-t-transparent rounded-full animate-spin-reverse"></div>
      </div>

      <h2 className="text-3xl font-bold mb-4 text-blue-300 text-center">
        Building Your Custom PC
      </h2>
      <p className="text-gray-300 text-center max-w-lg mb-2">
        Analyzing components, checking compatibility, and optimizing for your
        specific requirements...
      </p>
      <p className="text-gray-400 text-center">This may take a moment</p>

      <style jsx>{`
        @keyframes spin-slow {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
        @keyframes spin-reverse {
          0% {
            transform: rotate(360deg);
          }
          100% {
            transform: rotate(0deg);
          }
        }
        .animate-spin-reverse {
          animation: spin-reverse 2s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen;
