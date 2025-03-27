// src/components/Navigation.tsx
import Link from "next/link";

const Navigation = () => {
  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-white text-xl font-bold">
          PC Builder
        </Link>
        <div className="space-x-4">
          <Link href="/skilled" className="text-white hover:text-gray-300">
            Skilled Builder
          </Link>
          <Link href="/beginner" className="text-white hover:text-gray-300">
            Beginner Builder
          </Link>
          <Link href="/recommend" className="text-white hover:text-gray-300">
             Reccomendation
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
