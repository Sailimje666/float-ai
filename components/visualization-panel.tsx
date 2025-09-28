"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { BarChart3, Download, FileText } from "lucide-react"
import { ProfileChart } from "@/components/charts/profile-chart"
import { FloatMap } from "@/components/charts/float-map"
import { ComparisonChart } from "@/components/charts/comparison-chart"
import { OceanographicAnalysis } from "@/components/charts/oceanographic-analysis"

interface VisualizationPanelProps {
  data?: any
}

export function VisualizationPanel({ data }: VisualizationPanelProps) {
  const handleExportCSV = () => {
    if (!data?.floats) return

    const csvData = data.floats.flatMap((float: any) =>
      float.profiles[0].depth.map((depth: number, index: number) => ({
        float_id: float.id,
        float_name: float.name,
        latitude: float.lat,
        longitude: float.lon,
        depth: depth,
        temperature: float.profiles[0].temperature[index],
        salinity: float.profiles[0].salinity[index],
        pressure: float.profiles[0].pressure[index],
        date: float.profiles[0].date,
      })),
    )

    const csvContent = [Object.keys(csvData[0]).join(","), ...csvData.map((row) => Object.values(row).join(","))].join(
      "\n",
    )

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `argo_data_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleExportJSON = () => {
    if (!data?.floats) return

    const jsonContent = JSON.stringify(data.floats, null, 2)
    const blob = new Blob([jsonContent], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `argo_data_${new Date().toISOString().split("T")[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Panel Header */}
      <div className="p-4 border-b border-border bg-card/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="font-semibold">Visualizations</h2>
            {data && (
              <Badge variant="secondary" className="text-xs">
                Live Data
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
              disabled={!data?.floats}
              title="Export as CSV"
            >
              <Download className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportJSON}
              disabled={!data?.floats}
              title="Export as JSON"
            >
              <FileText className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Visualization Content */}
      <div className="flex-1 p-4 overflow-y-auto">
        {!data ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="font-medium mb-2">No Visualization Yet</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Start a conversation to see interactive charts and maps of ARGO oceanographic data
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Render based on visualization type */}
            {data.type === "profile" && data.floats && (
              <>
                <ProfileChart
                  floats={data.floats}
                  variable={data.variable || "temperature"}
                  title={`${data.variable === "salinity" ? "Salinity" : "Temperature"} Profiles`}
                />
                <FloatMap floats={data.floats} title="Float Locations" />
              </>
            )}

            {data.type === "map" && data.floats && (
              <>
                <FloatMap
                  floats={data.floats}
                  showTrajectories={data.showTrajectories}
                  title={data.showTrajectories ? "Float Trajectories" : "Float Locations"}
                />
                {data.floats.length > 1 && (
                  <ComparisonChart
                    floats={data.floats}
                    variable="temperature"
                    depth={100}
                    title="Temperature Comparison at 100m"
                  />
                )}
              </>
            )}

            {data.type === "comparison" && data.floats && (
              <>
                <ComparisonChart
                  floats={data.floats}
                  variable={data.variable || "temperature"}
                  depth={data.depth || 100}
                />
                <FloatMap floats={data.floats} title="Compared Float Locations" />
              </>
            )}

            {data.type === "analysis" && data.floats && <OceanographicAnalysis floats={data.floats} />}

            {data.floats && data.floats.length >= 3 && data.type !== "analysis" && (
              <Card className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-blue-200 dark:border-blue-800">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">Advanced Analysis Available</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      Explore thermocline depths, water masses, and regional comparisons
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-blue-300 text-blue-700 hover:bg-blue-100 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/20 bg-transparent"
                    onClick={() => {
                      console.log("[v0] Analysis view requested")
                    }}
                  >
                    View Analysis
                  </Button>
                </div>
              </Card>
            )}

            {/* Data summary card */}
            {data.floats && (
              <Card className="p-4 bg-muted/30 border-dashed">
                <h4 className="font-medium mb-2">Data Summary</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Active Floats:</span>
                    <span className="ml-2 font-medium">{data.floats.length}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Data Points:</span>
                    <span className="ml-2 font-medium">
                      {data.floats.reduce((acc: number, f: any) => acc + f.profiles[0].depth.length, 0)}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Depth Range:</span>
                    <span className="ml-2 font-medium">0-2000m</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Temp Range:</span>
                    <span className="ml-2 font-medium">
                      {Math.min(...data.floats.flatMap((f: any) => f.profiles[0].temperature)).toFixed(1)}°C -
                      {Math.max(...data.floats.flatMap((f: any) => f.profiles[0].temperature)).toFixed(1)}°C
                    </span>
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
