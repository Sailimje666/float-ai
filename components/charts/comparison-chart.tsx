"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ArgoFloat } from "@/types/argo"

interface ComparisonChartProps {
  floats: ArgoFloat[]
  variable: "temperature" | "salinity"
  depth?: number
  title?: string
}

export function ComparisonChart({ floats, variable, depth = 100, title }: ComparisonChartProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [plotlyLoaded, setPlotlyLoaded] = useState(false)

  useEffect(() => {
    const loadPlotly = () => {
      if (window.Plotly) {
        setPlotlyLoaded(true)
        setIsLoading(false)
        return
      }

      const script = document.createElement("script")
      script.src = "https://cdn.plot.ly/plotly-2.26.0.min.js"
      script.onload = () => {
        setPlotlyLoaded(true)
        setIsLoading(false)
      }
      script.onerror = () => {
        console.error("Failed to load Plotly")
        setIsLoading(false)
      }
      document.head.appendChild(script)
    }

    loadPlotly()
  }, [])

  useEffect(() => {
    if (!chartRef.current || !floats.length || !plotlyLoaded || !window.Plotly) return

    const data = floats.map((float) => {
      const profile = float.profiles[0]
      const depthIndex = profile.depth.findIndex((d) => d >= depth) || 0
      return {
        name: float.name,
        value: profile[variable][depthIndex],
        lat: float.lat,
        lon: float.lon,
      }
    })

    const trace = {
      x: data.map((d) => d.name),
      y: data.map((d) => d.value),
      type: "bar",
      marker: {
        color: data.map((_, i) => {
          const colors = ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
          return colors[i % colors.length]
        }),
        opacity: 0.8,
      },
      hovertemplate:
        `<b>%{x}</b><br>` +
        `${variable === "temperature" ? "Temperature" : "Salinity"}: %{y}${variable === "temperature" ? "°C" : " PSU"}<br>` +
        `Depth: ${depth}m<br>` +
        `<extra></extra>`,
    }

    const layout = {
      title: {
        text: title || `${variable === "temperature" ? "Temperature" : "Salinity"} Comparison at ${depth}m`,
        font: { size: 16 },
      },
      xaxis: {
        title: "ARGO Floats",
        tickangle: -45,
      },
      yaxis: {
        title: variable === "temperature" ? "Temperature (°C)" : "Salinity (PSU)",
      },
      plot_bgcolor: "transparent",
      paper_bgcolor: "transparent",
      font: { color: "#9ca3af" },
      margin: { l: 60, r: 20, t: 60, b: 100 },
    }

    const config = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
      displaylogo: false,
    }

    window.Plotly.newPlot(chartRef.current, [trace], layout, config)

    return () => {
      if (chartRef.current && window.Plotly) {
        window.Plotly.purge(chartRef.current)
      }
    }
  }, [floats, variable, depth, title, plotlyLoaded])

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium">
          {title || `${variable === "temperature" ? "Temperature" : "Salinity"} Comparison`}
        </h3>
        <div className="flex gap-2">
          <Badge variant="secondary">Comparison</Badge>
          <Badge variant="outline">{depth}m depth</Badge>
        </div>
      </div>
      {isLoading ? (
        <div className="h-64 flex items-center justify-center text-muted-foreground">Loading chart...</div>
      ) : (
        <div ref={chartRef} className="h-64" />
      )}
    </Card>
  )
}
