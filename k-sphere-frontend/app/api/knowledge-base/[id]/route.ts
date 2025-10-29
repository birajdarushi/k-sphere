import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params

    // TODO: Replace with actual database query
    const mockFile = {
      id: Number.parseInt(id),
      name: "machine_learning_fundamentals.pdf",
      type: "document",
      size: "2.4 MB",
      sizeBytes: 2516582,
      uploadedAt: "2024-01-15T10:30:00Z",
      status: "indexed",
      chunks: 45,
      metadata: {
        author: "John Doe",
        pages: 120,
        language: "en",
      },
    }

    return NextResponse.json(mockFile)
  } catch (error) {
    console.error("[v0] File fetch error:", error)
    return NextResponse.json({ error: "Failed to fetch file" }, { status: 500 })
  }
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params

    console.log("[Frontend API] Deleting file with id:", id)

    // Forward delete request to backend
    const response = await fetch(`http://localhost:8000/api/knowledge-base/${id}`, {
      method: "DELETE",
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[Frontend API] Backend delete error:", response.status, errorText)
      throw new Error(`Backend delete failed: ${response.statusText}`)
    }

    const data = await response.json()
    console.log("[Frontend API] File deleted successfully:", id)

    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] File deletion error:", error)
    return NextResponse.json(
      { error: "Failed to delete file", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    )
  }
}
