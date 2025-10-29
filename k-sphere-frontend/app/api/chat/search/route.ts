import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { query, limit = 10, type = "all" } = body

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 })
    }

    // Forward search request to backend
    const params = new URLSearchParams({
      query,
      limit: String(limit),
      type,
    })

    const response = await fetch(`${BACKEND_URL}/api/search?${params}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] Search error:", error)
    return NextResponse.json(
      {
        results: [],
        total: 0,
        error: "Search failed",
      },
      { status: 200 }
    ) // Return empty results instead of error
  }
}
