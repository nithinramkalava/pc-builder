// src/components/SkilledBuilder.tsx
'use client';

import { useState } from 'react';
import { pcParts } from '@/lib/parts-data';

type PartType = keyof typeof pcParts;
type SelectedParts = { [K in PartType]?: typeof pcParts[K][0] };

const partOrder: PartType[] = ['cpu', 'motherboard', 'ram', 'storage', 'gpu', 'case', 'psu'];

const SkilledBuilder = () => {
  const [currentPartIndex, setCurrentPartIndex] = useState(0);
  const [selectedParts, setSelectedParts] = useState<SelectedParts>({});

  const currentPart = partOrder[currentPartIndex];
  const isComplete = currentPartIndex >= partOrder.length;

  const handlePartSelect = (part: typeof pcParts[PartType][0]) => {
    setSelectedParts(prev => ({
      ...prev,
      [currentPart]: part
    }));
    setCurrentPartIndex(prev => prev + 1);
  };

  const totalPrice = Object.values(selectedParts).reduce((sum, part) => sum + (part?.price || 0), 0);

  if (isComplete) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Your Build Summary</h2>
        {Object.entries(selectedParts).map(([type, part]) => (
          <div key={type} className="flex justify-between items-center bg-gray-100 p-4 rounded text-black shadow-sm">
            <span className="font-medium capitalize">{type}</span>
            <div className="text-right">
              <div>{part?.name}</div>
              <div className="text-black">₹{(part?.price * 83).toLocaleString('en-IN')}</div>
            </div>
          </div>
        ))}
        <div className="text-xl font-bold text-right">
          Total: ₹{(totalPrice * 83).toLocaleString('en-IN')}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Select your {currentPart.toUpperCase()}</h2>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {pcParts[currentPart].map((part) => (
          <button
            key={part.id}
            onClick={() => handlePartSelect(part)}
            className="p-4 border rounded text-left space-y-2 text-white bg-gray-800 hover:bg-gray-700 transition-colors duration-200"
          >
            <div className="font-medium">{part.name}</div>
            <div className="text-white">₹{(part.price * 83).toLocaleString('en-IN')}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SkilledBuilder;