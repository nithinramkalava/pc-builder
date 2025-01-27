// src/app/beginner/page.tsx
import BeginnerBuilder from '@/components/BeginnerBuilder'

export default function BeginnerPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">PC Building Assistant</h1>
      <BeginnerBuilder />
    </div>
  )
}