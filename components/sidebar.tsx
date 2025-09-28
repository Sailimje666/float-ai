"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ThemeToggle } from "@/components/theme-toggle"
import { AboutModal } from "@/components/about-modal"
import { MessageSquare, BarChart3, Info, Waves, Menu, X } from "lucide-react"
import { useEffect } from "react"

interface SidebarProps {
  onShowVisualizations?: () => void
}

export function Sidebar({ onShowVisualizations }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [showAbout, setShowAbout] = useState(false)
  const [showNews, setShowNews] = useState(false)

  const navigation = [
    {
      name: "Chat",
      href: "#chat",
      icon: MessageSquare,
      current: true,
    },
    {
      name: "About",
      href: "#about",
      icon: Info,
      current: false,
      onClick: () => setShowAbout(true),
    },
  ]

  // Demo mode removed

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <Waves className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-sidebar-foreground">Float AI</h2>
            <Badge variant="secondary" className="text-xs">
              MVP
            </Badge>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={item.onClick}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                item.current
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.name}
            </Link>
          )
        })}

        {/* Ocean News Toggle */}
        <div className="pt-2">
          <Button
            variant="outline"
            className="w-full justify-start gap-2"
            onClick={() => setShowNews(!showNews)}
          >
            📰 Ocean News
            <Badge variant="secondary" className="ml-auto text-xs">
              Daily
            </Badge>
          </Button>
        </div>

        {showNews && (
          <div className="mt-3">
            <div className="text-xs font-medium mb-2 text-sidebar-foreground px-1">
              Daily Ocean News
            </div>
            <div className="px-1">
              <NewsList />
            </div>
          </div>
        )}
      </nav>

      {/* Demo Mode Button removed */}

      {/* Theme Toggle */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center justify-between">
          <span className="text-sm text-sidebar-foreground">Theme</span>
          <ThemeToggle />
        </div>
      </div>

      {/* Status Card */}
      <div className="p-4">
        <Card className="p-3 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-blue-200 dark:border-blue-800">
          <div className="text-xs text-blue-700 dark:text-blue-300 mb-1">ARGO Floats</div>
          <div className="text-sm font-medium text-blue-900 dark:text-blue-100">5 Active</div>
          <div className="text-xs text-blue-600 dark:text-blue-400">Indian Ocean Region</div>
        </Card>
      </div>

      {/* News section now toggled above with a button */}

      <AboutModal open={showAbout} onOpenChange={setShowAbout} />
    </div>
  )

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="sm"
        className="lg:hidden fixed top-4 left-4 z-50 bg-background/80 backdrop-blur-sm"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
      </Button>

      {/* Mobile sidebar overlay */}
      {isOpen && <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setIsOpen(false)} />}

      {/* Sidebar */}
      <aside
        className={`
        fixed lg:static inset-y-0 left-0 z-40 w-64 bg-sidebar border-r border-sidebar-border
        transform transition-transform duration-200 ease-in-out
        ${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}
      >
        <SidebarContent />
      </aside>
    </>
  )
}

function NewsList() {
  const [items, setItems] = useState<{ title: string; link: string }[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    const run = async () => {
      setLoading(true)
      try {
        const res = await fetch("/api/ocean-news", { cache: "no-store" })
        const json = await res.json()
        if (!isMounted) return
        setItems(Array.isArray(json.items) ? json.items : [])
      } catch (e) {
        if (!isMounted) return
        setError("Failed to load news")
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    run()
    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return <div className="text-xs text-muted-foreground">Loading...</div>
  }
  if (error) {
    return <div className="text-xs text-red-600">{error}</div>
  }
  if (items.length === 0) {
    return <div className="text-xs text-muted-foreground">No items today.</div>
  }
  const isIndian = (title: string) => {
    const keywords = [
      "India",
      "Indian",
      "Bay of Bengal",
      "Arabian Sea",
      "Mumbai",
      "Chennai",
      "Goa",
      "Kerala",
      "Andaman",
      "Lakshadweep",
    ]
    return keywords.some((k) => title.toLowerCase().includes(k.toLowerCase()))
  }

  return (
    <ul className="space-y-2 max-h-64 overflow-auto pr-1">
      {items.map((item) => {
        const highlight = isIndian(item.title)
        return (
          <li key={item.link}>
            <a
              href={item.link}
              target="_blank"
              rel="noreferrer noopener"
              className={`block ${highlight ? "text-sm font-semibold" : "text-xs"} text-sidebar-foreground hover:underline`}
              title={item.title}
            >
              {highlight && <span className="mr-2 inline-block px-1 py-0.5 text-[10px] rounded bg-emerald-100 text-emerald-700">India</span>}
              {item.title}
            </a>
          </li>
        )
      })}
    </ul>
  )
}
