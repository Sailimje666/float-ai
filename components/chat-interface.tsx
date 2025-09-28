"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Loader2, Lightbulb, Waves, AlertCircle, Upload } from "lucide-react"
import type { ChatMessage } from "@/types/argo"
import { getSampleQueries } from "@/lib/mock-data"
import { sendQuery } from "@/lib/api-client"
// Visualizations are now rendered in a separate section on the page

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onNewMessage: (message: ChatMessage) => void
}

export function ChatInterface({ messages, onNewMessage }: ChatInterfaceProps) {
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const [sampleQueries] = useState(getSampleQueries())
  const [aiStatus, setAiStatus] = useState<{ aiEnhanced: boolean; provider: string } | null>(null)
  const [netcdfSummary, setNetcdfSummary] = useState<any | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Prefer sentinel scroll to handle dynamic heights and images
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth", block: "end" })
      return
    }
    const viewport = containerRef.current?.querySelector(
      '[data-slot="scroll-area-viewport"]',
    ) as HTMLDivElement | null
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight
    }
  }, [messages])

  useEffect(() => {
    const fetchAiStatus = async () => {
      try {
        const response = await fetch("/api/status")
        const status = await response.json()
        setAiStatus(status)
      } catch (error) {
        console.error("Failed to fetch AI status:", error)
        setAiStatus({ aiEnhanced: false, provider: "Demo Mode" })
      }
    }

    fetchAiStatus()
  }, [])

  const runQuery = async (text: string) => {
    const queryText = text.trim()
    if (!queryText || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: queryText,
      timestamp: new Date(),
    }

    onNewMessage(userMessage)
    setInput("")
    setIsLoading(true)

    try {
      const response = await sendQuery(queryText, netcdfSummary ?? undefined)

      if (response.success && response.data) {
        const aiResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.data.message,
          timestamp: new Date(),
          data: response.data,
          visualizationType: response.data.type,
        }
        onNewMessage(aiResponse)
      } else {
        const errorResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.error || "I'm having trouble processing your query. Please try rephrasing it.",
          timestamp: new Date(),
        }
        onNewMessage(errorResponse)
      }
    } catch (error) {
      console.error("Query failed:", error)
      const errorResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm experiencing technical difficulties. Please try again in a moment.",
        timestamp: new Date(),
      }
      onNewMessage(errorResponse)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await runQuery(input)
  }

  const handleSampleQuery = (query: string) => {
    void runQuery(query)
  }

  const handleSuggestionClick = (suggestion: string) => {
    void runQuery(suggestion)
  }

  return (
    <div ref={containerRef} className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b border-border bg-card/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
            <Waves className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="font-semibold">Ocean Data Assistant</h2>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                AI Powered
              </Badge>
              <Badge variant="outline" className="text-xs">
                ARGO Data
              </Badge>
              {aiStatus?.aiEnhanced ? (
                <Badge variant="default" className="text-xs bg-green-500">
                  Enhanced AI
                </Badge>
              ) : (
                <Badge variant="outline" className="text-xs">
                  Demo Mode
                </Badge>
              )}
            </div>
          </div>
        </div>
        <p className="text-sm text-muted-foreground mt-2">
          Ask me anything about ARGO float data in natural language. I can show profiles, maps, and comparisons.
        </p>
        <div className="mt-2 flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".nc,application/x-netcdf,application/netcdf"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0]
              if (!file) return
              try {
                const arrayBuffer = await file.arrayBuffer()
                const { NetCDFReader } = await import("netcdfjs")
                const reader = new NetCDFReader(new DataView(arrayBuffer))
                const variables = reader.variables.map((v: any) => ({
                  name: v.name,
                  dimensions: Array.isArray(v.dimensions)
                    ? v.dimensions.map((d: any) => (typeof d === "object" && d !== null ? d.name ?? String(d) : String(d)))
                    : v.dimensions,
                  type: v.type,
                }))
                const dimensions = Array.isArray((reader as any).dimensions)
                  ? (reader as any).dimensions.map((d: any) => ({ name: d.name, size: d.size }))
                  : []
                const globalAttributes = Array.isArray((reader as any).globalAttributes)
                  ? (reader as any).globalAttributes.map((a: any) => ({ name: a.name, value: String(a.value).slice(0, 200) }))
                  : []
                setNetcdfSummary({ filename: file.name, variables, dimensions, globalAttributes })
              } catch (err) {
                console.error("Failed to parse NetCDF:", err)
                setNetcdfSummary({ filename: file.name, error: "Could not parse .nc file" })
              }
            }}
          />
          <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()} className="gap-2">
            <Upload className="w-4 h-4" />
            Upload .nc
          </Button>
          {netcdfSummary && (
            <span className="text-xs text-muted-foreground">
              Loaded: {netcdfSummary.filename} ({netcdfSummary.variables?.length ?? 0} vars)
            </span>
          )}
        </div>
        {aiStatus && !aiStatus.aiEnhanced && (
          <div className="mt-2 p-2 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <div className="flex items-center gap-2 text-xs text-amber-700 dark:text-amber-300">
              <AlertCircle className="w-3 h-3" />
              <span>Add GEMINI_API_KEY environment variable for enhanced AI responses</span>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 min-h-0 p-4 pb-4">
        <div className="space-y-4">
          {/* Extra padding so content never hides behind the sticky input */}
          <div className="pb-32">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Waves className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-medium mb-2">Welcome to Float AI!</h3>
              <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                I'm your AI assistant for exploring ARGO oceanographic data. Ask me about temperature, salinity, float
                locations, or regional comparisons in plain English.
              </p>

              <div className="space-y-3">
                <div className="flex items-center gap-2 justify-center text-xs text-muted-foreground mb-3">
                  <Lightbulb className="w-3 h-3" />
                  <span>Try these sample queries:</span>
                </div>
                <div className="grid gap-2 max-w-lg mx-auto">
                  {sampleQueries.slice(0, 4).map((query, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs bg-transparent hover:bg-accent text-left justify-start h-auto py-2 px-3"
                      onClick={() => handleSampleQuery(query)}
                    >
                      <span className="text-muted-foreground mr-2">→</span>
                      {query}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" && (
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}

              <div className="max-w-[85%] space-y-2">
                <Card
                  className={`p-3 ${
                    message.role === "user" ? "bg-primary text-primary-foreground ml-auto" : "bg-card border-border"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <div
                    className={`text-xs mt-2 flex items-center gap-2 ${
                      message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"
                    }`}
                  >
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                    {message.role === "assistant" && message.data?.aiEnhanced && (
                      <Badge variant="secondary" className="text-xs">
                        AI Enhanced
                      </Badge>
                    )}
                  </div>
                </Card>

                {message.role === "assistant" && message.data?.suggestions && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Lightbulb className="w-3 h-3" />
                      <span>You might also ask:</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {message.data.suggestions.map((suggestion: string, index: number) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="text-xs h-7 bg-transparent hover:bg-accent"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {message.role === "assistant" && message.data?.floats && (
                  <Card className="p-3 bg-muted/50 border-dashed">
                    <div className="text-xs text-muted-foreground mb-1">Data Summary</div>
                    <div className="flex items-center gap-4 text-sm">
                      <span>
                        <strong>{message.data.floats.length}</strong> floats
                      </span>
                      {message.data.variable && (
                        <span>
                          Variable: <strong>{message.data.variable}</strong>
                        </span>
                      )}
                      {message.data.type && (
                        <Badge variant="secondary" className="text-xs">
                          {message.data.type}
                        </Badge>
                      )}
                    </div>
                  </Card>
                )}

                {/* Visualization rendering moved to dedicated section on main page */}
              </div>

              {message.role === "user" && (
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <Card className="p-3 bg-card">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-sm">Analyzing oceanographic data...</span>
                </div>
              </Card>
            </div>
          )}
          <div ref={bottomRef} />
          </div>
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-border bg-card">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about ocean data... (e.g., 'Show salinity near equator' or 'Compare Arabian Sea temperatures')"
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>

        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Show me all float locations")}
          >
            📍 Float Map
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Compare temperature profiles")}
          >
            🌡️ Temperature
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Show salinity data")}
          >
            🧂 Salinity
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Arabian Sea analysis")}
          >
            🌊 Arabian Sea
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Show comprehensive oceanographic analysis")}
          >
            📊 Advanced Analysis
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs whitespace-nowrap bg-transparent"
            onClick={() => handleSampleQuery("Display thermocline depths and water masses")}
          >
            🔬 Water Masses
          </Button>
        </div>
      </div>
    </div>
  )
}
