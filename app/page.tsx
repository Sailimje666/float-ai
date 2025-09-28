"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ChatInterface } from "@/components/chat-interface"
import { VisualizationPanel } from "@/components/visualization-panel"
import type { ChatMessage } from "@/types/argo"
import { getSampleQueries } from "@/lib/mock-data"

// 👇 Argovis + New Components
import ArgovisData from "@/components/ArgovisData"
import dynamic from "next/dynamic"
const OceanMap = dynamic(() => import("@/components/OceanMap"), { ssr: false })
import AnomalyChart from "@/components/AnomalyChart"

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentVisualization, setCurrentVisualization] = useState<any>(null)

  // --- Mock sample data aur extra states for map/chart/kid-mode ---
  const sampleData = [
    { year: 2010, temp: 14.1 },
    { year: 2011, temp: 14.2 },
    { year: 2012, temp: 14.3 },
    { year: 2013, temp: 14.4 },
    { year: 2014, temp: 14.6 },
    { year: 2015, temp: 15.0 },
    { year: 2016, temp: 16.1, anomaly: true }, // anomaly example
    { year: 2017, temp: 15.2 },
    { year: 2018, temp: 15.0 },
    { year: 2019, temp: 15.1 },
    { year: 2020, temp: 15.3 },
  ]

  const [insight, setInsight] = useState<any>(null)
  const [chartData, setChartData] = useState<any[]>(sampleData)
  // Removed kid mode UI

  // Mock backend call — abhi sirf demo ke liye
  function mockFetchInsights(coords: any) {
    return new Promise((res) => {
      setTimeout(() => {
        res({
          text: `Detected a big temp spike in 2016 near (${coords.lat.toFixed(
            2
          )}, ${coords.lng.toFixed(2)}) — likely El Niño.`,
          kidText: `Ocean ko 2016 me bukhar aaya tha near (${coords.lat.toFixed(
            2
          )}, ${coords.lng.toFixed(2)}) — isko El Niño bolte hai.`,
          data: sampleData,
        })
      }, 700)
    })
  }

  async function handleRegionSelect(coords: any) {
    setInsight({ text: "Loading..." })
    const res: any = await mockFetchInsights(coords)
    setInsight(res)
    setChartData(res.data)

    setCurrentVisualization({
      type: "map",
      floats: [],
      message: res.text,
    })
  }

  const handleNewMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message])
    if (message.data) {
      setCurrentVisualization(message.data)
    }
  }

  // Demo mode removed

  const handleShowVisualizations = async () => {
    let floats: any[] = []
    try {
      const res = await fetch('/api/argovis?lat=10&lon=-45&radius=200', { cache: 'no-store' })
      const json = await res.json()
      floats = json?.floats || []
    } catch (e) {
      console.error('Failed to load Argovis floats:', e)
    }
    const defaultViz = {
      type: "map",
      floats,
      message: "Showing ARGO float locations.",
      suggestions: [
        "Show temperature profiles from these floats",
        "Compare salinity between regions",
        "Display float trajectories",
      ],
    }
    setCurrentVisualization(defaultViz)
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "assistant",
        content: "Opened the Visualizations panel with the float map.",
        timestamp: new Date(),
        data: defaultViz,
        visualizationType: "map",
      },
    ])
    if (typeof window !== "undefined") {
      const el = document.getElementById("visualizations")
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 overflow-hidden">
          <div className="w-full max-w-7xl mx-auto h-full min-w-0 px-3 md:px-4 flex gap-6">
            <div className="flex-1 min-w-0 h-full">
              <ChatInterface
                messages={messages}
                onNewMessage={handleNewMessage}
              />
            </div>

            <div
              id="visualizations"
              className="hidden md:flex md:w-[42%] min-w-0 h-full items-stretch"
            >
              <div className="w-full self-stretch overflow-y-auto py-4 space-y-4">
                <ArgovisData />

                <div className="space-y-4">
                  <OceanMap onRegionSelect={handleRegionSelect} />

                  {/* Kid mode controls removed */}

                  <div className="px-1">
                    <h2 className="font-semibold">Anomaly Chart</h2>
                    <AnomalyChart data={chartData} />
                  </div>

                  <div className="p-4 bg-gray-50 rounded">
                    <h3 className="font-medium">AI Insight</h3>
                    <p className="mt-2">{insight ? insight.text : "Map pe click karo to insight dikhai dega."}</p>
                  </div>

                  {currentVisualization ? (
                    <div className="w-full self-stretch">
                      <VisualizationPanel data={currentVisualization} />
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground border border-dashed rounded-md p-4 w-full self-stretch">
                      Visualizations will appear here after you run a query.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </div>
  )
}
