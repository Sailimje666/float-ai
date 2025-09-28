export interface ArgoFloat {
  id: string
  name: string
  lat: number
  lon: number
  status: "active" | "inactive"
  lastUpdate: string
  trajectory: TrajectoryPoint[]
  profiles: Profile[]
}

export interface TrajectoryPoint {
  lat: number
  lon: number
  date: string
}

export interface Profile {
  date: string
  depth: number[]
  temperature: number[]
  salinity: number[]
  pressure: number[]
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  data?: any
  visualizationType?: "profile" | "map" | "timeseries" | "comparison"
}

export interface QueryResponse {
  message: string
  data?: any
  visualizationType?: "profile" | "map" | "timeseries" | "comparison"
  suggestions?: string[]
}
