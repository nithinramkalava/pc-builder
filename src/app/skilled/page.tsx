// src/app/skilled/page.tsx
import SkilledBuilder from '@/components/SkilledBuilder'

export default function SkilledPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Build Your PC</h1>
      <SkilledBuilder />
    </div>
  )
}