import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { searchParams } = new URL(request.url)
    const title = searchParams.get("title")

    if (!title) {
      return NextResponse.json({ error: "Title is required" }, { status: 400 })
    }

    const response = await fetch(
      `${BACKEND_URL}/api/conversations/${params.id}/title?title=${encodeURIComponent(title)}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
      }
    )

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[Frontend API] Backend error:", response.status, errorText)
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] Error updating conversation title:", error)
    return NextResponse.json({ 
      error: "Failed to update conversation title"
    }, { status: 500 })
  }
}
