'use client'

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-primary-900 mb-4">
          P.U.L.S.E
        </h1>
        <p className="text-xl text-neutral-600 mb-8">
          Personal Unified Lifestyle & Sustenance Engine
        </p>
        <div className="space-x-4">
          <a
            href="/login"
            className="btn-primary px-6 py-3 inline-block"
          >
            Sign In
          </a>
          <a
            href="/register"
            className="btn-secondary px-6 py-3 inline-block"
          >
            Sign Up
          </a>
        </div>
      </div>
    </main>
  )
}
