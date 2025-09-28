"use client"

import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

export function Header() {
  return (
    <header className="border-b border-border bg-card sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-card/80">
      <div className="px-6 py-4">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-foreground text-balance">
              Float AI MVP: AI for ARGO Data Exploration
            </h1>
            <Badge variant="outline" className="hidden sm:inline-flex">
              Beta
            </Badge>
          </div>
          <p className="text-muted-foreground text-sm text-pretty">Powered by AI – Query Ocean Data Naturally</p>
        </div>
      </div>
      <Separator />
    </header>
  )
}
