import type { ArgoFloat } from "@/types/argo"
import mockData from "@/data/mock-argo-data.json"

export const getArgoFloats = (): ArgoFloat[] => {
  return mockData.floats as ArgoFloat[]
}

export const getFloatById = (id: string): ArgoFloat | undefined => {
  return mockData.floats.find((float) => float.id === id) as ArgoFloat | undefined
}

export const getFloatsByRegion = (region: string): ArgoFloat[] => {
  const floats = mockData.floats as ArgoFloat[]

  switch (region.toLowerCase()) {
    case "arabian sea":
      return floats.filter((f) => f.lat > 10 && f.lat < 25 && f.lon > 60 && f.lon < 75)
    case "bay of bengal":
      return floats.filter((f) => f.lat > 5 && f.lat < 20 && f.lon > 80 && f.lon < 95)
    case "equator":
    case "equatorial":
      return floats.filter((f) => Math.abs(f.lat) < 5)
    case "southern ocean":
      return floats.filter((f) => f.lat < -20)
    case "tropical":
      return floats.filter((f) => Math.abs(f.lat) < 10)
    case "subtropical":
      return floats.filter((f) => Math.abs(f.lat) >= 10 && Math.abs(f.lat) < 30)
    default:
      return floats
  }
}

export const getSampleQueries = (): string[] => {
  return mockData.sampleQueries
}

export const processNaturalLanguageQuery = (query: string): any => {
  const lowerQuery = query.toLowerCase()

  // Friendly greeting handling so the bot can chat naturally
  const greetingRegex = /^(hi+|hello+|hey+|yo+|hiya|hola|namaste|good\s*(morning|afternoon|evening))\b|(how\s*are\s*you\??)$/i
  if (greetingRegex.test(query)) {
    return {
      type: "greeting",
      message:
        "Hi! I'm your Ocean Data Assistant. Ask me about ARGO float locations, temperature/salinity, or comparisons.",
      suggestions: [
        "Show me all float locations",
        "Compare temperature at 100m",
        "Show salinity near equator",
      ],
    }
  }

  // Advanced oceanographic analysis queries
  if (
    lowerQuery.includes("thermocline") ||
    lowerQuery.includes("water mass") ||
    lowerQuery.includes("analysis") ||
    lowerQuery.includes("t-s diagram") ||
    lowerQuery.includes("mixed layer") ||
    lowerQuery.includes("density")
  ) {
    return {
      type: "analysis",
      floats: getArgoFloats(),
      message:
        "Here's a comprehensive oceanographic analysis including thermocline depths, water mass identification, and regional comparisons.",
      suggestions: [
        "Show me temperature profiles by region",
        "Compare salinity stratification between regions",
        "Display float trajectories with temperature data",
      ],
    }
  }

  // Regional comparison queries
  if (
    (lowerQuery.includes("compare") || lowerQuery.includes("comparison")) &&
    (lowerQuery.includes("region") || lowerQuery.includes("tropical") || lowerQuery.includes("subtropical"))
  ) {
    return {
      type: "analysis",
      floats: getArgoFloats(),
      message: "Comparing oceanographic data across different latitude zones and regions.",
      suggestions: [
        "Show me thermocline variations by region",
        "Display water mass properties",
        "Compare mixed layer depths",
      ],
    }
  }

  // Salinity-specific queries
  if (lowerQuery.includes("salinity")) {
    if (lowerQuery.includes("equator")) {
      return {
        type: "profile",
        variable: "salinity",
        floats: getFloatsByRegion("equatorial"),
        message:
          "Here are the salinity profiles near the equator from our ARGO floats. Notice the lower salinity values typical of equatorial regions.",
        suggestions: [
          "Compare with Arabian Sea salinity",
          "Show temperature-salinity relationship",
          "Display salinity at different depths",
        ],
      }
    }
    if (lowerQuery.includes("arabian") || lowerQuery.includes("bay of bengal")) {
      const region = lowerQuery.includes("arabian") ? "arabian sea" : "bay of bengal"
      return {
        type: "profile",
        variable: "salinity",
        floats: getFloatsByRegion(region),
        message: `Salinity profiles from ${region.charAt(0).toUpperCase() + region.slice(1)} showing ${region === "arabian sea" ? "higher salinity due to evaporation" : "lower salinity from freshwater input"}.`,
        suggestions: ["Compare with other regions", "Show temperature profiles", "Display water mass analysis"],
      }
    }
    return {
      type: "comparison",
      variable: "salinity",
      floats: getArgoFloats(),
      message: "Comparing salinity profiles across all available ARGO floats.",
      suggestions: [
        "Focus on specific regions",
        "Show salinity at specific depths",
        "Display temperature-salinity diagrams",
      ],
    }
  }

  // Temperature-specific queries
  if (lowerQuery.includes("temperature")) {
    if (lowerQuery.includes("arabian")) {
      return {
        type: "profile",
        variable: "temperature",
        floats: getFloatsByRegion("arabian sea"),
        message:
          "Temperature data from Arabian Sea floats showing warm surface waters and strong thermocline development.",
        suggestions: ["Compare with Bay of Bengal", "Show thermocline depth analysis", "Display seasonal variations"],
      }
    }
    if (lowerQuery.includes("depth") || lowerQuery.match(/\d+\s*m/)) {
      const depthMatch = lowerQuery.match(/(\d+)\s*m/)
      const depth = depthMatch ? Number.parseInt(depthMatch[1]) : 100
      return {
        type: "comparison",
        variable: "temperature",
        depth: depth,
        floats: getArgoFloats(),
        message: `Temperature comparison at ${depth}m depth across all floats, showing regional variations.`,
        suggestions: ["Try different depths", "Show vertical profiles", "Compare with salinity at same depth"],
      }
    }
  }

  // Location and mapping queries
  if (lowerQuery.includes("location") || lowerQuery.includes("map") || lowerQuery.includes("where")) {
    return {
      type: "map",
      floats: getArgoFloats(),
      message: "ARGO float locations across the Indian Ocean region, showing active monitoring network.",
      suggestions: ["Show float trajectories", "Display temperature at locations", "Focus on specific regions"],
    }
  }

  if (lowerQuery.includes("trajectory") || lowerQuery.includes("path") || lowerQuery.includes("movement")) {
    return {
      type: "map",
      floats: getArgoFloats(),
      showTrajectories: true,
      message: "Float trajectories showing drift patterns influenced by ocean currents.",
      suggestions: ["Analyze current patterns", "Show temperature along trajectories", "Compare drift speeds"],
    }
  }

  // Depth-specific queries
  if (lowerQuery.includes("deep") || lowerQuery.includes("1000") || lowerQuery.includes("2000")) {
    return {
      type: "profile",
      variable: "temperature",
      floats: getArgoFloats(),
      message: "Deep ocean temperature profiles showing the cold, stable deep water masses.",
      suggestions: ["Compare with surface temperatures", "Show salinity at depth", "Analyze water mass properties"],
    }
  }

  // Default enhanced response
  return {
    type: "profile",
    variable: "temperature",
    floats: getArgoFloats().slice(0, 3),
    message:
      "Here's oceanographic data from our ARGO float network. These autonomous instruments provide crucial data for understanding ocean dynamics and climate.",
    suggestions: [
      "Show me comprehensive oceanographic analysis",
      "Compare temperature profiles by region",
      "Display thermocline and water mass analysis",
      "Show float trajectories and current patterns",
    ],
  }
}

export const getFloatData = () => {
  return {
    floats: mockData.floats as ArgoFloat[],
  }
}
