import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/knowledge-base/stats`, {
      cache: "no-store",
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] Stats fetch error:", error)
    // Return empty stats if backend is unavailable
    return NextResponse.json({
      totalFiles: 0,
      totalChunks: 0,
      byType: {
        documents: 0,
        images: 0,
        audio: 0
      },
      storageUsed: 0,
      lastUpdated: new Date().toISOString()
    })
  }
}
