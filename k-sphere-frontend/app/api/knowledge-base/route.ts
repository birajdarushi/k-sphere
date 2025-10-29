import { NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const params = new URLSearchParams()
    
    // Forward all query parameters to backend
    searchParams.forEach((value, key) => {
      params.append(key, value)
    })

    const response = await fetch(`${BACKEND_URL}/api/knowledge-base?${params}`, {
      cache: "no-store",
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] Knowledge base fetch error:", error)
    return NextResponse.json({ 
      files: [], 
      total: 0,
      error: "Backend unavailable" 
    }, { status: 200 }) // Return empty list instead of error
  }
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    const files = formData.getAll("files") as File[]

    if (!files || files.length === 0) {
      return NextResponse.json({ error: "No files provided" }, { status: 400 })
    }

    console.log("[Frontend API] File upload received:", files.map(f => f.name).join(", "))

    // Forward to backend
    const backendFormData = new FormData()
    files.forEach(file => {
      backendFormData.append("files", file)
    })

    const response = await fetch(`${BACKEND_URL}/api/knowledge-base`, {
      method: "POST",
      body: backendFormData,
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("[Frontend API] File upload error:", error)
    return NextResponse.json({ error: "Upload failed" }, { status: 500 })
  }
}
