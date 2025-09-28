import { NextResponse } from "next/server"

export async function GET() {
  const hasGeminiKey = !!process.env.GEMINI_API_KEY

  return NextResponse.json({
    aiEnhanced: hasGeminiKey,
    provider: hasGeminiKey ? "Gemini" : "Demo Mode",
  })
}
