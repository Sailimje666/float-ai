import { NextResponse } from "next/server"

// Simple RSS fetcher and naive parser for titles and links
async function fetchRss(url: string): Promise<{ title: string; link: string }[]> {
  try {
    const res = await fetch(url, { cache: "no-store" })
    const xml = await res.text()
    const items: { title: string; link: string }[] = []
    const itemRegex = /<item[\s\S]*?<\/item>/g
    const titleRegex = /<title>([\s\S]*?)<\/title>/
    const linkRegex = /<link>([\s\S]*?)<\/link>/
    const matches = xml.match(itemRegex) || []
    for (const item of matches) {
      const titleMatch = item.match(titleRegex)
      const linkMatch = item.match(linkRegex)
      const title = titleMatch ? titleMatch[1].trim() : ""
      const link = linkMatch ? linkMatch[1].trim() : ""
      if (title && link) {
        items.push({ title, link })
      }
    }
    return items
  } catch {
    return []
  }
}

export async function GET() {
  const sources = [
    // NOAA News (general; many ocean-related stories)
    "https://www.noaa.gov/news.rss",
    // ScienceDaily Oceans
    "https://www.sciencedaily.com/rss/earth_climate/oceans.xml",
    // Nature Ocean sciences
    "https://www.nature.com/subjects/ocean-sciences.rss",
  ]

  const results = await Promise.all(sources.map((s) => fetchRss(s)))
  const combined = results.flat()
  // Deduplicate by link
  const seen = new Set<string>()
  const deduped: { title: string; link: string }[] = []
  for (const item of combined) {
    if (!seen.has(item.link)) {
      seen.add(item.link)
      deduped.push(item)
    }
  }

  // Return top 12 items
  return NextResponse.json({ items: deduped.slice(0, 12) })
}


