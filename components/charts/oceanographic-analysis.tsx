"use client"
import { useEffect, useRef, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ArgoFloat } from "@/types/argo"

interface OceanographicAnalysisProps {
  floats: ArgoFloat[]
}

export function OceanographicAnalysis({ floats }: OceanographicAnalysisProps) {
  const tsChartRef = useRef<HTMLDivElement>(null)
  const regionalChartRef = useRef<HTMLDivElement>(null)
  const [plotlyLoaded, setPlotlyLoaded] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadPlotly = () => {
      if (window.Plotly) {
        setPlotlyLoaded(true)
        setLoading(false)
        return
      }

      const script = document.createElement("script")
      script.src = "https://cdn.plot.ly/plotly-2.26.0.min.js"
      script.onload = () => {
        setPlotlyLoaded(true)
        setLoading(false)
      }
      script.onerror = () => {
        console.error("Failed to load Plotly")
        setLoading(false)
      }
      document.head.appendChild(script)
    }

    loadPlotly()
  }, [])

  useEffect(() => {
    if (!plotlyLoaded || !window.Plotly) return

    // Create T-S diagram
    if (tsChartRef.current) {
      const tsData = createTSData()
      window.Plotly.newPlot(
        tsChartRef.current,
        tsData,
        {
          title: "Temperature-Salinity-Depth Relationship",
          scene: {
            xaxis: { title: "Salinity (PSU)" },
            yaxis: { title: "Temperature (°C)" },
            zaxis: { title: "Depth (m)", autorange: "reversed" },
          },
          height: 600,
          showlegend: true,
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { color: "#374151" },
        },
        { responsive: true, displayModeBar: false },
      )
    }

    // Create regional comparison
    if (regionalChartRef.current) {
      const regionalData = createRegionalComparison()
      window.Plotly.newPlot(
        regionalChartRef.current,
        regionalData,
        {
          title: "Temperature vs Depth by Region",
          xaxis: { title: "Temperature (°C)" },
          yaxis: { title: "Depth (m)", autorange: "reversed" },
          height: 500,
          showlegend: true,
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { color: "#374151" },
        },
        { responsive: true, displayModeBar: false },
      )
    }
  }, [plotlyLoaded, floats])

  const calculateThermocline = (temperature: number[], depth: number[]) => {
    let maxGradient = 0
    let thermoclineDepth = 0

    for (let i = 1; i < temperature.length - 1; i++) {
      const gradient = Math.abs((temperature[i - 1] - temperature[i + 1]) / (depth[i + 1] - depth[i - 1]))
      if (gradient > maxGradient) {
        maxGradient = gradient
        thermoclineDepth = depth[i]
      }
    }
    return thermoclineDepth
  }

  const calculateMixedLayerDepth = (temperature: number[], depth: number[]) => {
    const surfaceTemp = temperature[0]
    for (let i = 1; i < temperature.length; i++) {
      if (surfaceTemp - temperature[i] >= 0.2) {
        return depth[i]
      }
    }
    return depth[depth.length - 1]
  }

  const createTSData = () => {
    return floats.map((float) => {
      const profile = float.profiles[0]
      return {
        x: profile.salinity,
        y: profile.temperature,
        z: profile.depth,
        mode: "markers+lines",
        type: "scatter3d",
        name: float.name,
        marker: {
          size: 4,
          color: profile.depth,
          colorscale: "Viridis",
          showscale: true,
        },
        line: { width: 2 },
      }
    })
  }

  const createRegionalComparison = () => {
    const regions = {
      Tropical: floats.filter((f) => Math.abs(f.lat) < 10),
      Subtropical: floats.filter((f) => Math.abs(f.lat) >= 10 && Math.abs(f.lat) < 30),
      Temperate: floats.filter((f) => Math.abs(f.lat) >= 30),
    }

    return Object.entries(regions)
      .map(([region, regionFloats]) => {
        if (regionFloats.length === 0) return null

        // Average temperature profile for region
        const avgProfile = regionFloats[0].profiles[0].depth.map((depth, i) => {
          const avgTemp =
            regionFloats.reduce((sum, float) => sum + float.profiles[0].temperature[i], 0) / regionFloats.length
          return { depth, temperature: avgTemp }
        })

        return {
          x: avgProfile.map((p) => p.temperature),
          y: avgProfile.map((p) => -p.depth),
          mode: "lines+markers",
          type: "scatter",
          name: `${region} (${regionFloats.length} floats)`,
          line: { width: 3 },
          marker: { size: 6 },
        }
      })
      .filter(Boolean)
  }

  const analysisData = floats.map((float) => {
    const profile = float.profiles[0]
    return {
      name: float.name,
      thermoclineDepth: calculateThermocline(profile.temperature, profile.depth),
      mixedLayerDepth: calculateMixedLayerDepth(profile.temperature, profile.depth),
      surfaceTemp: profile.temperature[0],
      surfaceSalinity: profile.salinity[0],
      deepTemp: profile.temperature[profile.temperature.length - 1],
      lat: float.lat,
      lon: float.lon,
    }
  })

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-center h-32">
              <div className="text-muted-foreground">Loading oceanographic analysis...</div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Regional Temperature Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Regional Temperature Profiles
            <Badge variant="secondary">Comparative Analysis</Badge>
          </CardTitle>
          <CardDescription>
            Average temperature profiles by latitude zones showing thermocline variations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div ref={regionalChartRef} className="w-full h-[500px]" />
        </CardContent>
      </Card>

      {/* Temperature-Salinity Diagram */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Temperature-Salinity Analysis
            <Badge variant="secondary">Water Mass ID</Badge>
          </CardTitle>
          <CardDescription>3D T-S diagram colored by depth for water mass identification</CardDescription>
        </CardHeader>
        <CardContent>
          <div ref={tsChartRef} className="w-full h-[600px]" />
        </CardContent>
      </Card>

      {/* Analysis Summary Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Oceanographic Metrics
            <Badge variant="secondary">Summary</Badge>
          </CardTitle>
          <CardDescription>Key oceanographic parameters extracted from ARGO profiles</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Float</th>
                  <th className="text-left p-2">Location</th>
                  <th className="text-left p-2">Surface T (°C)</th>
                  <th className="text-left p-2">Surface S (PSU)</th>
                  <th className="text-left p-2">MLD (m)</th>
                  <th className="text-left p-2">Thermocline (m)</th>
                  <th className="text-left p-2">Deep T (°C)</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.map((data, i) => (
                  <tr key={i} className="border-b hover:bg-muted/50">
                    <td className="p-2 font-medium">{data.name}</td>
                    <td className="p-2">
                      {data.lat.toFixed(1)}°, {data.lon.toFixed(1)}°
                    </td>
                    <td className="p-2">{data.surfaceTemp.toFixed(1)}</td>
                    <td className="p-2">{data.surfaceSalinity.toFixed(1)}</td>
                    <td className="p-2">{data.mixedLayerDepth.toFixed(0)}</td>
                    <td className="p-2">{data.thermoclineDepth.toFixed(0)}</td>
                    <td className="p-2">{data.deepTemp.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
