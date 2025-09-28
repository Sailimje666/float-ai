import { NextResponse, type NextRequest } from "next/server"

// Transforms a subset of Argovis profile fields into our app's ArgoFloat shape
function transformArgovisToArgoFloats(argovisProfiles: any[]) {
  // Group by platform_number (float id)
  const platformToProfiles: Record<string, any[]> = {}
  for (const p of argovisProfiles) {
    const platformId = String(p?.platform_number || p?._id || p?.wmo || "unknown")
    if (!platformToProfiles[platformId]) platformToProfiles[platformId] = []
    platformToProfiles[platformId].push(p)
  }

  // Build minimal ArgoFloat objects expected by visualizations
  const argoFloats = Object.entries(platformToProfiles).map(([platformId, profiles]) => {
    const latest = profiles[0] || {}
    const lat = Number(latest?.lat ?? latest?.latitude ?? 0)
    const lon = Number(latest?.lon ?? latest?.longitude ?? 0)
    const date = String(latest?.date || latest?.time || latest?.timestamp || new Date().toISOString())

    // Many Argovis records expose arrays as: pres/pressure, temp/temperature, psal/salinity
    // Fallback to empty arrays if not present
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
        {
          lat,
          lon,
          date,
        },
      ],
      profiles: [
        {
          date,
          depth,
          temperature,
          salinity,
          pressure,
        },
      ],
    }
  })

  return argoFloats
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const lat = searchParams.get("lat") ?? "10"
  const lon = searchParams.get("lon") ?? "-45"
  const radius = searchParams.get("radius") ?? "200"

  const url = `https://argovis.colorado.edu/catalog/profiles?lat=${encodeURIComponent(
    lat,
  )}&lon=${encodeURIComponent(lon)}&radius=${encodeURIComponent(radius)}`

  try {
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${process.env.ARGOVIS_API_KEY ?? ""}`,
      },
      // App router fetch defaults to dynamic; ensure we bypass any caches for live data
      cache: "no-store",
    })

    if (!response.ok) {
      const text = await response.text()
      return NextResponse.json({ error: `Upstream error ${response.status}: ${text}` }, { status: 502 })
    }

    const argovisData = await response.json()
    const floats = Array.isArray(argovisData) ? transformArgovisToArgoFloats(argovisData) : []

    return NextResponse.json({ floats })
  } catch (error: any) {
    return NextResponse.json({ error: error?.message || "Failed to fetch Argovis data" }, { status: 500 })
  }
}


