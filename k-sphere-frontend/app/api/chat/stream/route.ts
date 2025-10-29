import { NextRequest } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query, conversationId } = body

    if (!query) {
      return new Response("No query provided", { status: 400 })
    }

    console.log("[Frontend API] Streaming chat query received:", query)

    // Forward to backend streaming endpoint
    const response = await fetch(`${BACKEND_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        conversationId: conversationId || "default",
        topK: 10
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[Frontend API] Backend error:", response.status, errorText)
      throw new Error(`Backend returned ${response.status}`)
    }

    // Stream the response back to the client
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    })
  } catch (error) {
    console.error("[Frontend API] Streaming error:", error)
    return new Response(
      `data: ${JSON.stringify({ type: "error", error: String(error) })}\n\n`,
      {
        headers: {
          "Content-Type": "text/event-stream",
        },
      }
    )
  }
}
