"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ArgoFloat } from "@/types/argo"

interface ProfileChartProps {
  floats: ArgoFloat[]
  variable: "temperature" | "salinity"
  title?: string
}

export function ProfileChart({ floats, variable, title }: ProfileChartProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!chartRef.current || !floats.length) return

    setIsLoading(true)
    setError(null)

    const loadPlotly = () => {
      return new Promise((resolve, reject) => {
        if (typeof window !== "undefined" && (window as any).Plotly) {
          resolve((window as any).Plotly)
          return
        }

        const script = document.createElement("script")
        script.src = "https://cdn.plot.ly/plotly-2.26.0.min.js"
        script.onload = () => resolve((window as any).Plotly)
        script.onerror = () => reject(new Error("Failed to load Plotly"))
        document.head.appendChild(script)
      })
    }

    loadPlotly()
      .then((Plotly: any) => {
        const traces = floats.map((float, index) => {
          const profile = float.profiles[0] // Use latest profile
          const colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

          return {
            x: profile[variable],
            y: profile.depth.map((d) => -d), // Negative for depth (oceanographic convention)
            mode: "lines+markers",
            name: float.name,
            line: { color: colors[index % colors.length], width: 2 },
            marker: { size: 4 },
            hovertemplate:
              `<b>${float.name}</b><br>` +
              `Depth: %{y}m<br>` +
              `${variable === "temperature" ? "Temperature" : "Salinity"}: %{x}${variable === "temperature" ? "°C" : " PSU"}<br>` +
              `<extra></extra>`,
          }
        })

        const layout = {
          title: {
            text: title || `${variable === "temperature" ? "Temperature" : "Salinity"} Profiles`,
            font: { size: 16 },
          },
          xaxis: {
            title: variable === "temperature" ? "Temperature (°C)" : "Salinity (PSU)",
            gridcolor: "#374151",
          },
          yaxis: {
            title: "Depth (m)",
            gridcolor: "#374151",
            autorange: "reversed",
          },
          plot_bgcolor: "transparent",
          paper_bgcolor: "transparent",
          font: { color: "#9ca3af" },
          margin: { l: 60, r: 20, t: 40, b: 60 },
          showlegend: true,
          legend: {
            x: 1,
            y: 1,
            bgcolor: "rgba(0,0,0,0.1)",
          },
        }

        const config = {
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
          displaylogo: false,
        }

        Plotly.newPlot(chartRef.current, traces, layout, config)
        setIsLoading(false)
      })
      .catch((err) => {
        console.error("Failed to load Plotly:", err)
        setError("Failed to load chart library")
        setIsLoading(false)
      })

    return () => {
      if (chartRef.current && (window as any).Plotly) {
        ;(window as any).Plotly.purge(chartRef.current)
      }
    }
  }, [floats, variable, title])

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium">
          {title || `${variable === "temperature" ? "Temperature" : "Salinity"} Profiles`}
        </h3>
        <div className="flex gap-2">
          <Badge variant="secondary">Interactive</Badge>
          <Badge variant="outline">{floats.length} floats</Badge>
        </div>
      </div>
      <div ref={chartRef} className="h-80">
        {isLoading && (
          <div className="flex items-center justify-center h-full text-muted-foreground">Loading chart...</div>
        )}
        {error && <div className="flex items-center justify-center h-full text-red-500">{error}</div>}
      </div>
    </Card>
  )
}
