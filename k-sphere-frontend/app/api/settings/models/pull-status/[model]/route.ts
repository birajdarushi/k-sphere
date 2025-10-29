import { NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET(
  request: Request,
  { params }: { params: { model: string } }
) {
  try {
    const modelName = params.model

    const response = await fetch(
      `${BACKEND_URL}/api/settings/models/pull-status/${modelName}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        cache: "no-store",
      }
    )

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    console.error("Error checking pull status:", error)
    return NextResponse.json(
      { error: error.message || "Failed to check pull status" },
      { status: 500 }
    )
  }
}
