"use client"

import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"

export function Footer() {
  return (
    <>
      <Separator />
      <footer className="bg-card border-t border-border">
        <div className="px-6 py-3">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Built for Oceanographers</span>
              <span className="hidden sm:inline">•</span>
              <Badge variant="secondary" className="text-xs">
                MVP Version
              </Badge>
            </div>
            <div className="text-xs text-muted-foreground">Last updated: {new Date().toLocaleDateString()}</div>
          </div>
        </div>
      </footer>
    </>
  )
}
