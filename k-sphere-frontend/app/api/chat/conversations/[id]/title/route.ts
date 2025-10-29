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
      return NextResponse.json(
        { error: "Title is required" },
        { status: 400 }
      )
    }

    const response = await fetch(
      `${BACKEND_URL}/api/chat/conversations/${params.id}/title?title=${encodeURIComponent(title)}`,
      { method: "PATCH" }
    )
    
    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json(
        { error: error || "Failed to update conversation title" },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    console.error("Update conversation title error:", error)
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    )
  }
}
