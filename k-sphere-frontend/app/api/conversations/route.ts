import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[Frontend API] Backend error:", response.status, errorText)
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] Error fetching conversations:", error)
    return NextResponse.json({ 
      error: "Failed to fetch conversations",
      conversations: []
    }, { status: 500 })
  }
}
