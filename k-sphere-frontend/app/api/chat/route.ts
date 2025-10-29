import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { query, conversationId } = body

    if (!query) {
      return NextResponse.json({ error: "No query provided" }, { status: 400 })
    }

    console.log("[Frontend API] Chat query received:", query)

    // Forward to backend
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        conversationId: conversationId || "default",
        topK: 5
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[Frontend API] Backend error:", response.status, errorText)
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    
    // Transform backend response to frontend format
    return NextResponse.json({
      answer: data.answer,
      sources: data.sources,
      conversationId: data.conversationId,
      processingTime: data.processingTime
    })
  } catch (error) {
    console.error("[Frontend API] Chat error:", error)
    return NextResponse.json({ 
      message: {
        role: "assistant",
        content: "I'm sorry, I couldn't process your request. The backend service might be unavailable. Please make sure you've uploaded some documents to your knowledge base first.",
        sources: []
      },
      error: "Backend unavailable" 
    }, { status: 200 })
  }
}
