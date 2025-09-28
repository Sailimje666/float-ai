export interface QueryRequest {
  query: string
  netcdfSummary?: any
}

export interface QueryResponse {
  success: boolean
  data?: any
  error?: string
}

export async function sendQuery(query: string, netcdfSummary?: any): Promise<QueryResponse> {
  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, netcdfSummary }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error("API request failed:", error)
    return {
      success: false,
      error: "Failed to process your query. Please try again.",
    }
  }
}
