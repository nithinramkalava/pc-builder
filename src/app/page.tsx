// src/app/page.tsx
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-8 bg-gray-900">
      <h1 className="text-4xl font-bold text-center text-white">Welcome to PC Builder</h1>
      <p className="text-xl text-center text-gray-300 max-w-2xl">
        Choose your experience level and start building your perfect PC
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        <Link 
          href="/skilled"
          className="p-8 border border-gray-600 rounded-lg text-center space-y-4 bg-transparent text-white hover:bg-white hover:text-gray-900 transition-all duration-200"
        >
          <h2 className="text-2xl font-bold">Skilled Builder</h2>
          <p className="text-inherit">
            Choose your parts directly with our streamlined interface
          </p>
        </Link>

        <Link 
          href="/recommend"
          className="p-8 border border-gray-600 rounded-lg text-center space-y-4 bg-transparent text-white hover:bg-white hover:text-gray-900 transition-all duration-200"
        >
          <h2 className="text-2xl font-bold">Beginner Builder</h2>
          <p className="text-inherit">
            Get personalized recommendations through an interactive chat
          </p>
        </Link>
      </div>
    </div>
  )
}