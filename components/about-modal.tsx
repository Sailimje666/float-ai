"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Waves, Database, Brain, Map, BarChart3, Globe } from "lucide-react"

interface AboutModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AboutModal({ open, onOpenChange }: AboutModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <Waves className="w-5 h-5 text-white" />
            </div>
            About Float AI MVP
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Overview */}
          <div>
            <h3 className="font-semibold mb-3">Overview</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Float AI MVP is an AI-powered conversational system that democratizes access to ARGO float oceanographic
              data. Using natural language processing, researchers and decision-makers can explore complex ocean data
              without requiring technical expertise in databases or programming.
            </p>
          </div>

          {/* Key Features */}
          <div>
            <h3 className="font-semibold mb-3">Key Features</h3>
            <div className="grid gap-3">
              <Card className="p-3">
                <div className="flex items-start gap-3">
                  <Brain className="w-5 h-5 text-blue-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-sm">Natural Language to Visualization</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Convert plain English queries into instant, interactive ocean data visualizations
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-3">
                <div className="flex items-start gap-3">
                  <BarChart3 className="w-5 h-5 text-cyan-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-sm">Interactive Dashboards</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Real-time charts and maps with hover tooltips, zoom, and pan capabilities
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-3">
                <div className="flex items-start gap-3">
                  <Map className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-sm">AI-Guided Discovery</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Proactive suggestions and follow-up queries to help uncover hidden patterns
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Current Data */}
          <div>
            <h3 className="font-semibold mb-3">Current Dataset</h3>
            <Card className="p-4 bg-muted/30">
              <div className="flex items-center gap-2 mb-3">
                <Database className="w-4 h-4 text-primary" />
                <span className="font-medium text-sm">Indian Ocean ARGO Floats</span>
                <Badge variant="secondary" className="text-xs">
                  MVP Dataset
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Active Floats:</span>
                  <span className="ml-2 font-medium">5</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Regions:</span>
                  <span className="ml-2 font-medium">4</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Variables:</span>
                  <span className="ml-2 font-medium">Temperature, Salinity</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Depth Range:</span>
                  <span className="ml-2 font-medium">5-2000m</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Future Extensions */}
          <div>
            <h3 className="font-semibold mb-3">Future Extensions</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                <span>Global ARGO float network integration</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                <span>BGC (Biogeochemical) parameters</span>
              </div>
              <div className="flex items-center gap-2">
                <Waves className="w-4 h-4" />
                <span>Glider and satellite data fusion</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                <span>Advanced analytics and anomaly detection</span>
              </div>
            </div>
          </div>

          {/* Technical Stack */}
          <div>
            <h3 className="font-semibold mb-3">Technical Stack</h3>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Next.js</Badge>
              <Badge variant="outline">React</Badge>
              <Badge variant="outline">TypeScript</Badge>
              <Badge variant="outline">Tailwind CSS</Badge>
              <Badge variant="outline">Shadcn UI</Badge>
              <Badge variant="outline">Plotly.js</Badge>
              <Badge variant="outline">Leaflet.js</Badge>
              <Badge variant="outline">OpenAI API</Badge>
            </div>
          </div>

          {/* Version Info */}
          <div className="pt-4 border-t border-border">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Built for Oceanographers</span>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs">
                  MVP Version 1.0
                </Badge>
                <span>© 2024</span>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
