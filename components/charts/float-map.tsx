"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ArgoFloat } from "@/types/argo"

interface FloatMapProps {
  floats: ArgoFloat[]
  showTrajectories?: boolean
  title?: string
}

export function FloatMap({ floats, showTrajectories = false, title }: FloatMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mapRef.current || !floats.length) return

    setIsLoading(true)
    setError(null)

    const loadLeaflet = () => {
      return new Promise((resolve, reject) => {
        if (typeof window !== "undefined" && (window as any).L) {
          resolve((window as any).L)
          return
        }

        // Load CSS first
        const cssLink = document.createElement("link")
        cssLink.rel = "stylesheet"
        cssLink.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        document.head.appendChild(cssLink)

        // Then load JS
        const script = document.createElement("script")
        script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        script.onload = () => resolve((window as any).L)
        script.onerror = () => reject(new Error("Failed to load Leaflet"))
        document.head.appendChild(script)
      })
    }

    loadLeaflet()
      .then((L: any) => {
        // Clean up existing map
        if (mapInstanceRef.current) {
          mapInstanceRef.current.remove()
        }

        // Calculate bounds
        const lats = floats.map((f) => f.lat)
        const lons = floats.map((f) => f.lon)
        const bounds = [
          [Math.min(...lats) - 2, Math.min(...lons) - 2],
          [Math.max(...lats) + 2, Math.max(...lons) + 2],
        ] as [[number, number], [number, number]]

        // Create map
        const map = L.map(mapRef.current).fitBounds(bounds)
        mapInstanceRef.current = map

        // Add tile layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
        }).addTo(map)

        // Color palette for floats
        const colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

        floats.forEach((float, index) => {
          const color = colors[index % colors.length]

          // Add current position marker
          const marker = L.circleMarker([float.lat, float.lon], {
            radius: 8,
            fillColor: color,
            color: "#ffffff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
          }).addTo(map)

          // Add popup with float info
          const latestProfile = float.profiles[0]
          const popupContent = `
            <div class="p-2">
              <h4 class="font-semibold text-sm mb-1">${float.name}</h4>
              <p class="text-xs text-gray-600 mb-2">ID: ${float.id}</p>
              <div class="text-xs space-y-1">
                <div>Status: <span class="font-medium ${float.status === "active" ? "text-green-600" : "text-red-600"}">${float.status}</span></div>
                <div>Last Update: ${new Date(float.lastUpdate).toLocaleDateString()}</div>
                <div>Latest Temp: ${latestProfile.temperature[0]}°C</div>
                <div>Latest Salinity: ${latestProfile.salinity[0]} PSU</div>
              </div>
            </div>
          `
          marker.bindPopup(popupContent)

          // Add trajectory if requested
          if (showTrajectories && float.trajectory.length > 1) {
            const trajectoryPoints = float.trajectory.map((point) => [point.lat, point.lon] as [number, number])

            L.polyline(trajectoryPoints, {
              color: color,
              weight: 2,
              opacity: 0.7,
              dashArray: "5, 5",
            }).addTo(map)

            // Add trajectory markers
            float.trajectory.slice(1).forEach((point, trajIndex) => {
              L.circleMarker([point.lat, point.lon], {
                radius: 4,
                fillColor: color,
                color: "#ffffff",
                weight: 1,
                opacity: 0.7,
                fillOpacity: 0.5,
              })
                .addTo(map)
                .bindPopup(`
                <div class="p-2">
                  <h5 class="font-medium text-xs">${float.name}</h5>
                  <p class="text-xs">Date: ${new Date(point.date).toLocaleDateString()}</p>
                </div>
              `)
            })
          }
        })

        // Add scale control
        L.control.scale().addTo(map)
        setIsLoading(false)
      })
      .catch((err) => {
        console.error("Failed to load Leaflet:", err)
        setError("Failed to load map library")
        setIsLoading(false)
      })

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [floats, showTrajectories])

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium">{title || "ARGO Float Locations"}</h3>
        <div className="flex gap-2">
          <Badge variant="secondary">Geospatial</Badge>
          <Badge variant="outline">{floats.length} floats</Badge>
          {showTrajectories && <Badge variant="outline">Trajectories</Badge>}
        </div>
      </div>
      <div ref={mapRef} className="h-80 rounded-lg overflow-hidden bg-muted">
        {isLoading && (
          <div className="flex items-center justify-center h-full text-muted-foreground">Loading map...</div>
        )}
        {error && <div className="flex items-center justify-center h-full text-red-500">{error}</div>}
      </div>
    </Card>
  )
}
