import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/system-status`, {
      cache: "no-store",
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] System status error:", error)
    
    // Return offline status if backend is unavailable
    return NextResponse.json({
      status: "offline",
      timestamp: new Date().toISOString(),
      services: {
        ollama: { status: "error", model: "unknown", version: "unknown" },
        vectorDb: { status: "disconnected", collections: 0 },
        whisper: { status: "unavailable", model: "unknown" },
        embeddings: { status: "unavailable", model: "unknown" }
      },
      resources: {
        cpuUsage: 0,
        memoryUsage: 0,
        diskSpace: 0
      }
    })
  }
}
