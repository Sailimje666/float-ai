import { type NextRequest, NextResponse } from "next/server"
import { processNaturalLanguageQuery } from "@/lib/mock-data"

// Local helper to fetch Argovis and transform to our ArgoFloat shape
function transformArgovisToArgoFloats(argovisProfiles: any[]) {
  const byPlatform: Record<string, any[]> = {}
  for (const p of argovisProfiles) {
    const platformId = String(p?.platform_number || p?._id || p?.wmo || "unknown")
    if (!byPlatform[platformId]) byPlatform[platformId] = []
    byPlatform[platformId].push(p)
  }
  return Object.entries(byPlatform).map(([platformId, profiles]) => {
    const latest: any = profiles[0] || {}
    const lat = Number(latest?.lat ?? latest?.latitude ?? 0)
    const lon = Number(latest?.lon ?? latest?.longitude ?? 0)
    const date = String(latest?.date || latest?.time || latest?.timestamp || new Date().toISOString())
    const depth: number[] = Array.isArray(latest?.pres)
      ? latest.pres
      : Array.isArray(latest?.pressure)
      ? latest.pressure
      : []
    const temperature: number[] = Array.isArray(latest?.temp)
      ? latest.temp
      : Array.isArray(latest?.temperature)
      ? latest.temperature
      : []
    const salinity: number[] = Array.isArray(latest?.psal)
      ? latest.psal
      : Array.isArray(latest?.salinity)
      ? latest.salinity
      : []
    const pressure: number[] = depth
    return {
      id: platformId,
      name: `Float ${platformId}`,
      lat,
      lon,
      status: "active",
      lastUpdate: date,
      trajectory: [
        { lat, lon, date },
      ],
      profiles: [
        { date, depth, temperature, salinity, pressure },
      ],
    }
  })
}

function getRegionParams(region?: string) {
  const r = (region || "indian ocean").toLowerCase()
  switch (r) {
    case "arabian sea":
      return { lat: 18, lon: 64, radius: 800 }
    case "bay of bengal":
      return { lat: 15, lon: 88, radius: 800 }
    case "equatorial":
    case "equator":
      return { lat: 0, lon: 80, radius: 1000 }
    case "southern ocean":
      return { lat: -50, lon: 60, radius: 1500 }
    case "indian ocean":
    default:
      return { lat: -10, lon: 80, radius: 1800 }
  }
}

async function fetchArgovisFloatsByRegion(region?: string) {
  const { lat, lon, radius } = getRegionParams(region)
  const url = `https://argovis.colorado.edu/catalog/profiles?lat=${lat}&lon=${lon}&radius=${radius}`
  const resp = await fetch(url, {
    headers: { Authorization: `Bearer ${process.env.ARGOVIS_API_KEY ?? ""}` },
    cache: "no-store",
  })
  if (!resp.ok) return []
  const json = await resp.json()
  return Array.isArray(json) ? transformArgovisToArgoFloats(json) : []
}

export async function POST(request: NextRequest) {
  try {
    const { query, netcdfSummary } = await request.json()

    if (!query || typeof query !== "string") {
      return NextResponse.json({ error: "Query is required" }, { status: 400 })
    }

    const geminiApiKey = process.env.GEMINI_API_KEY

    let enhancedResponse: any

    if (geminiApiKey) {
      // Use Gemini to enhance query processing
      enhancedResponse = await processWithGemini(query, geminiApiKey)
    } else {
      // Fallback to mock processing
      enhancedResponse = processNaturalLanguageQuery(query)
    }

    // Attach live floats from Argovis based on inferred region
    try {
      const floats = await fetchArgovisFloatsByRegion(enhancedResponse?.region)
      enhancedResponse = {
        ...enhancedResponse,
        floats,
      }
    } catch (e) {
      console.error("Failed to fetch Argovis floats for query:", e)
    }

    // If a NetCDF summary was uploaded, include it to tailor responses client-side
    if (netcdfSummary) {
      enhancedResponse = {
        ...enhancedResponse,
        netcdf: netcdfSummary,
      }
    }

    return NextResponse.json({ success: true, data: enhancedResponse })
  } catch (error) {
    console.error("Query processing error:", error)
    return NextResponse.json({ error: "Failed to process query" }, { status: 500 })
  }
}

async function processWithGemini(query: string, apiKey: string) {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `You are an AI assistant specialized in oceanographic data analysis. Your task is to interpret natural language queries about ARGO float data and return structured responses.\n\nAvailable data regions: Arabian Sea, Bay of Bengal, Equatorial, Southern Ocean, Indian Ocean\nAvailable variables: temperature, salinity, pressure\nAvailable visualization types: profile, map, comparison, timeseries\n\nReturn strictly a JSON object with keys:\n- message: string\n- type: \"profile\" | \"map\" | \"comparison\" | \"timeseries\"\n- variable?: \"temperature\" | \"salinity\" | \"pressure\"\n- region?: \"arabian sea\" | \"bay of bengal\" | \"equatorial\" | \"southern ocean\" | \"indian ocean\"\n- suggestions?: string[]\n\nUser query: ${query}\n\nIMPORTANT:\n- Respond with ONLY the JSON object (no markdown, no explanation, no backticks).\n- If unsure, infer sensible defaults (type/map, variable/temperature).`,
                },
              ],
            },
          ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 300,
          },
        }),
      },
    )

    if (!response.ok) {
      const errorBody = await response.text()
      console.error(`[v0] Gemini API non-OK response: Status ${response.status}, Body: ${errorBody}`)
      // Graceful fallback for quota/auth errors so user can continue chatting in demo mode
      if (response.status === 429 || response.status === 401 || response.status === 403) {
        return processNaturalLanguageQuery(query)
      }
      throw new Error(`Gemini API error: ${response.status}`)
    }

    const geminiResponse = await response.json()
    const geminiContent = geminiResponse?.candidates?.[0]?.content?.parts?.[0]?.text

    if (!geminiContent) {
      throw new Error("No content in Gemini response")
    }

    try {
      const jsonMatch = geminiContent.match(/\{[\s\S]*\}/)
      const jsonText = jsonMatch ? jsonMatch[0] : geminiContent
      const parsedResponse = JSON.parse(jsonText)

      const mockResult = processNaturalLanguageQuery(query)

      return {
        ...mockResult,
        message: parsedResponse.message ?? mockResult.message,
        type: parsedResponse.type ?? mockResult.type,
        variable: parsedResponse.variable ?? mockResult.variable,
        region: parsedResponse.region ?? mockResult.region,
        suggestions: parsedResponse.suggestions ?? mockResult.suggestions,
        aiEnhanced: true,
      }
    } catch (parseError) {
      console.warn(
        "[v0] Failed to parse Gemini response as JSON, using fallback. Raw response:",
        geminiContent,
        "Parse error:",
        parseError,
      )
      return processNaturalLanguageQuery(query)
    }
  } catch (error) {
    console.error("Gemini processing error:", error)
    return processNaturalLanguageQuery(query)
  }
}
